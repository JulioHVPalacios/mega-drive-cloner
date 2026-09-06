import configparser
import json
import os
import sys
import urllib.request
import urllib.parse
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def find_rclone_conf():
    paths = [
        os.path.expanduser("~/.config/rclone/rclone.conf"),
        os.path.expandvars(r"%APPDATA%\rclone\rclone.conf"),
        "/root/.config/rclone/rclone.conf",
        "/home/runner/.config/rclone/rclone.conf"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def get_drive_credentials(remote='midrive'):
    conf_path = find_rclone_conf()
    if not conf_path:
        raise FileNotFoundError("No se encontró rclone.conf en las rutas estándar.")

    config = configparser.ConfigParser()
    config.read(conf_path, encoding='utf-8')

    if not config.has_section(remote):
        raise ValueError(f"El remoto '{remote}' no existe en rclone.conf.")

    client_id = config.get(remote, 'client_id', fallback=None)
    client_secret = config.get(remote, 'client_secret', fallback=None)
    token_raw = config.get(remote, 'token', fallback=None)

    if not token_raw:
        raise ValueError(f"No hay token para '{remote}' en rclone.conf.")

    token_json = json.loads(token_raw)
    refresh_token = token_json.get('refresh_token')
    if not refresh_token:
        raise ValueError(f"No hay refresh_token para '{remote}'.")

    return client_id, client_secret, refresh_token

def get_access_token(remote='midrive'):
    client_id, client_secret, refresh_token = get_drive_credentials(remote)
    token_url = "https://oauth2.googleapis.com/token"
    params = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode('utf-8')

    req = urllib.request.Request(token_url, data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        return res['access_token']

def get_folder_id(folder_path, remote='midrive', access_token=None):
    if not access_token:
        access_token = get_access_token(remote)

    clean_name = os.path.basename(folder_path.replace('\\', '/').rstrip('/'))
    safe_name = clean_name.replace("'", "\\'")
    query = f"name = '{safe_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    search_url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(query)}&fields=files(id,name,webViewLink)&supportsAllDrives=true&includeItemsFromAllDrives=true&pageSize=5"
    req = urllib.request.Request(search_url, headers={'Authorization': f'Bearer {access_token}'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            files = data.get('files', [])
            if files:
                fid = files[0]['id']
                link = files[0].get('webViewLink', f"https://drive.google.com/drive/folders/{fid}")
                return fid, link
    except Exception as e:
        print(f"[-] Error buscando carpeta por nombre: {e}", flush=True)

    # Fallback: Comprobar si folder_path era directamente un ID de archivo en Drive
    try:
        direct_url = f"https://www.googleapis.com/drive/v3/files/{folder_path}?fields=id,name,webViewLink&supportsAllDrives=true"
        req_direct = urllib.request.Request(direct_url, headers={'Authorization': f'Bearer {access_token}'})
        with urllib.request.urlopen(req_direct, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'id' in data:
                return data['id'], data.get('webViewLink', f"https://drive.google.com/drive/folders/{data['id']}")
    except Exception:
        pass

    return None, None

def share_folder(folder_path, recipient_email, role='reader', remote='midrive', send_notification=True):
    access_token = get_access_token(remote)
    folder_id, folder_link = get_folder_id(folder_path, remote=remote, access_token=access_token)

    if not folder_id:
        print(f"[-] Error: No se pudo localizar la carpeta '{folder_path}' en '{remote}:'", flush=True)
        return False, None

    notify_param = 'true' if send_notification else 'false'
    url = f"https://www.googleapis.com/drive/v3/files/{folder_id}/permissions?sendNotificationEmail={notify_param}&supportsAllDrives=true"
    body = json.dumps({
        'role': role,
        'type': 'user',
        'emailAddress': recipient_email
    }).encode('utf-8')

    req = urllib.request.Request(url, data=body, headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            perm_data = json.loads(resp.read().decode('utf-8'))
            role_desc = "Lectura (Ver y Descargar)" if role == 'reader' else "Escritura (Editar y Subir)"
            print("=" * 65, flush=True)
            print("🚀 ¡CARPETA COMPARTIDA CON ÉXITO EN GOOGLE DRIVE!", flush=True)
            print(f"📁 Carpeta: {folder_path} (ID: {folder_id})", flush=True)
            print(f"👤 Destinatario: {recipient_email}", flush=True)
            print(f"🔑 Nivel de Acceso: {role} ({role_desc})", flush=True)
            print(f"🆔 ID de Permiso: {perm_data.get('id')}", flush=True)
            print(f"🔗 Enlace Oficial: {folder_link}", flush=True)
            print(f"📧 Notificación: {'Enviada por Google' if send_notification else 'Silenciosa'}", flush=True)
            print("=" * 65, flush=True)
            print("ℹ️ Instrucciones para el destinatario:", flush=True)
            print("   1. La persona NO necesita Rclone ni configurar nada.", flush=True)
            print("   2. Aparece directamente en su pestaña 'Compartido conmigo'.", flush=True)
            print("   3. Si desea verla en 'Mi unidad': Click derecho -> 'Añadir acceso directo a Drive' (0 bytes ocupados en su cuota).", flush=True)
            print("=" * 65, flush=True)
            return True, folder_link
    except Exception as e:
        print(f"[-] Error al otorgar permisos en Google Drive: {e}", flush=True)
        return False, None

def list_permissions(folder_path, remote='midrive'):
    access_token = get_access_token(remote)
    folder_id, folder_link = get_folder_id(folder_path, remote=remote, access_token=access_token)

    if not folder_id:
        print(f"[-] Error: No se encontro la carpeta '{folder_path}'", flush=True)
        return []

    url = f"https://www.googleapis.com/drive/v3/files/{folder_id}/permissions?fields=permissions(id,displayName,emailAddress,role,type)&supportsAllDrives=true"
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            perms = data.get('permissions', [])
            print(f"👥 Permisos actuales para '{folder_path}':", flush=True)
            for p in perms:
                print(f"  • {p.get('emailAddress', 'N/A')} ({p.get('displayName', 'Anónimo')}) - Rol: {p.get('role')} (ID: {p.get('id')})", flush=True)
            return perms
    except Exception as e:
        print(f"[-] Error al listar permisos: {e}", flush=True)
        return []

def revoke_permission(folder_path, email_or_id, remote='midrive'):
    access_token = get_access_token(remote)
    folder_id, folder_link = get_folder_id(folder_path, remote=remote, access_token=access_token)

    if not folder_id:
        print(f"[-] Error: No se encontro la carpeta '{folder_path}'", flush=True)
        return False

    url_list = f"https://www.googleapis.com/drive/v3/files/{folder_id}/permissions?fields=permissions(id,emailAddress)&supportsAllDrives=true"
    req_list = urllib.request.Request(url_list, headers={'Authorization': f'Bearer {access_token}'})
    target_id = None
    try:
        with urllib.request.urlopen(req_list, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            perms = data.get('permissions', [])
            for p in perms:
                if p.get('id') == email_or_id or p.get('emailAddress', '').lower() == email_or_id.lower():
                    target_id = p.get('id')
                    break
    except Exception as e:
        print(f"[-] Error al consultar lista de permisos: {e}", flush=True)
        return False

    if not target_id:
        print(f"[-] No se encontro permiso asignado a '{email_or_id}'.", flush=True)
        return False

    url_del = f"https://www.googleapis.com/drive/v3/files/{folder_id}/permissions/{target_id}?supportsAllDrives=true"
    req_del = urllib.request.Request(url_del, headers={'Authorization': f'Bearer {access_token}', 'Content-Length': '0'}, method='DELETE')
    try:
        with urllib.request.urlopen(req_del, timeout=30) as resp:
            print(f"[OK] Permiso revocado correctamente para '{email_or_id}'.", flush=True)
            return True
    except Exception as e:
        print(f"[-] Error al revocar permiso: {e}", flush=True)
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compartir carpetas de Google Drive instantáneamente por email sin configuraciones para terceros")
    parser.add_argument("--folder", required=True, help="Ruta o nombre de la carpeta (ej: MEGAPACK_PROGRAMACION_COMPLETO)")
    parser.add_argument("--email", default="", help="Correo de Google del destinatario")
    parser.add_argument("--role", default="reader", choices=["reader", "writer"], help="Rol: reader (lectura) o writer (escritura)")
    parser.add_argument("--remote", default="midrive", choices=["midrive", "midrive2"], help="Cuenta de origen")
    parser.add_argument("--action", default="share", choices=["share", "list", "revoke"], help="Acción a realizar")
    parser.add_argument("--no-notify", action="store_true", help="No enviar correo de notificación oficial de Google")

    args = parser.parse_args()

    if args.action == 'share':
        if not args.email:
            print("[-] Error: Debe especificar --email para la acción 'share'", flush=True)
            sys.exit(1)
        share_folder(args.folder, args.email, args.role, args.remote, not args.no_notify)
    elif args.action == 'list':
        list_permissions(args.folder, args.remote)
    elif args.action == 'revoke':
        if not args.email:
            print("[-] Error: Debe especificar --email o el ID de permiso para 'revoke'", flush=True)
            sys.exit(1)
        revoke_permission(args.folder, args.email, args.remote)
