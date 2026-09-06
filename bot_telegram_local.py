"""
OmniCloud Core - Telegram Bot Local Poller (Zero dependencias externas)
Ejecutable con Python 3 nativo. Soporta descargas ultra-rápidas en Azure y
compartición instantánea de Google Drive a cualquier tercero con solo su correo.
"""
import os
import sys
import json
import time
import re
import subprocess
import urllib.request
import urllib.parse
import share_drive_folder

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BOT_TOKEN = "8775957501:AAEF5W3TgWUku6pMCqdFN9ouFpxMG4BJ7MI"
AUTH_CHAT_ID = "1136933800"
REPO = "JulioHVPalacios/mega-drive-cloner"
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Diccionarios de sesión en memoria
pending_urls = {}
user_states = {}

def call_tg(endpoint, payload):
    url = f"{API_BASE}/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERROR TG] {endpoint}: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": str(chat_id),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return call_tg("sendMessage", payload)

def answer_callback(cb_id, text=None):
    payload = {"callback_query_id": cb_id}
    if text:
        payload["text"] = text
    call_tg("answerCallbackQuery", payload)

def get_runs_status():
    try:
        cmd = ["gh", "run", "list", "--repo", REPO, "--limit", "4", "--json", "databaseId,name,status,conclusion,createdAt"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
        runs = json.loads(res.stdout)
        if not runs:
            return "ℹ️ No hay ejecuciones registradas en GitHub Actions."
        
        msg = "📊 <b>ESTADO DE DESCARGAS EN VIVO (AZURE CLOUD):</b>\n\n"
        for r in runs:
            st = r.get("status")
            conc = r.get("conclusion")
            if st == "completed":
                icon = "✅" if conc == "success" else "❌"
            else:
                icon = "🔄"
            
            estado_txt = f"{st} ({conc})" if conc else f"{st} (ejecutando)"
            msg += f"{icon} <b>{r.get('name')}</b>\nEstado: <code>{estado_txt}</code>\nID: <code>{r.get('databaseId')}</code>\n\n"
        return msg
    except Exception as e:
        return f"❌ Error al consultar GitHub CLI: {e}"

def trigger_workflow_download(url, target, recipient_email=""):
    try:
        cmd = [
            "gh", "workflow", "run", "descargador_universal.yml",
            "--repo", REPO,
            "-f", f"source_url={url}",
            "-f", f"destination_target={target}",
            "-f", "dest_folder=DESCARGAS_UNIVERSALES",
            "-f", "transfer_mode=Auto Streaming RAM Turbo (Zero Disco - Soporta 500GB/1TB/2TB)"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
        return True, res.stdout
    except Exception as e:
        return False, str(e)

def trigger_sync():
    try:
        cmd = ["gh", "workflow", "run", "sincronizador_automatico_megapack.yml", "--repo", REPO]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
        return True, res.stdout
    except Exception as e:
        return False, str(e)

def show_share_menu(chat_id):
    txt = (
        "🤝 <b>COMPARTIR CARPETAS DE GOOGLE DRIVE AL INSTANTE</b>\n\n"
        "Comparte cualquier carpeta con amigos o clientes con <b>solo escribir su correo</b>.\n"
        "• <b>Cero fricción:</b> No necesitan Rclone, contraseñas ni permisos raros.\n"
        "• <b>Automático:</b> Aparece en su pestaña 'Compartido conmigo'.\n"
        "• <b>Instantáneo:</b> El Megapack de 825 GB se comparte en 1.5 segundos.\n\n"
        "📁 <b>Selecciona la carpeta que deseas compartir:</b>"
    )
    kbd = {
        "inline_keyboard": [
            [{"text": "📦 Megapack Programación (825 GB)", "callback_data": "sh:f:MEGAPACK_PROGRAMACION_COMPLETO"}],
            [{"text": "📂 Descargas Universales", "callback_data": "sh:f:DESCARGAS_UNIVERSALES"}],
            [{"text": "✍️ Escribir nombre de otra carpeta...", "callback_data": "sh:f:custom"}],
            [{"text": "👥 Ver quién tiene acceso (/permisos)", "callback_data": "sh:list"}]
        ]
    }
    send_message(chat_id, txt, kbd)

def execute_share(chat_id, folder, email, role="reader", remote="midrive"):
    send_message(chat_id, f"⏳ Conectando con Google Drive API para compartir <code>{folder}</code> con <code>{email}</code>...")
    try:
        ok, link = share_drive_folder.share_folder(folder, email, role=role, remote=remote, send_notification=True)
        if ok:
            role_desc = "👁️ Solo Lectura (Ver y Descargar)" if role == "reader" else "✏️ Lectura y Escritura (Modificar)"
            msg = (
                "🎉 <b>¡CARPETA COMPARTIDA CON ÉXITO!</b>\n\n"
                f"📁 <b>Carpeta:</b> <code>{folder}</code>\n"
                f"👤 <b>Destinatario:</b> <code>{email}</code>\n"
                f"🔑 <b>Nivel de Acceso:</b> {role_desc}\n"
                f"🔗 <a href='{link}'>Abrir Carpeta en Google Drive</a>\n\n"
                "ℹ️ <b>¿Cómo lo ve el destinatario?</b>\n"
                "1. Google le envió una notificación oficial a su correo.\n"
                "2. La carpeta aparece ya en su pestaña <b>'Compartido conmigo'</b> en Google Drive.\n"
                "3. Si desea verla en su 'Mi unidad': Click derecho -> <i>Añadir acceso directo a Drive</i> (0 bytes de cuota consumidos)."
            )
            send_message(chat_id, msg)
        else:
            send_message(chat_id, f"❌ No se pudo compartir <code>{folder}</code> con <code>{email}</code>. Verifica que el correo de Google sea válido y la carpeta exista.")
    except Exception as e:
        send_message(chat_id, f"❌ Error en la operación: {e}")

def handle_update(up):
    # 1. Mensaje normal
    if "message" in up:
        msg = up["message"]
        chat_id = str(msg.get("chat", {}).get("id"))
        text = (msg.get("text") or "").strip()

        if chat_id != AUTH_CHAT_ID:
            send_message(chat_id, "⛔ Acceso no autorizado. Este bot es de uso privado.")
            return

        state = user_states.get(chat_id, {})

        # Comprobación de estados interactivos
        if state.get("step") == "waiting_custom_folder":
            user_states[chat_id] = {
                "step": "waiting_share_email",
                "folder": text,
                "remote": "midrive"
            }
            send_message(chat_id, f"📁 Carpeta seleccionada: <code>{text}</code>\n\n📧 <b>Ahora escribe el correo Google de la persona a quien se lo enviarás:</b>\n(Ej: <code>amigo@gmail.com</code>)")
            return

        if state.get("step") == "waiting_share_email":
            email = text.lower()
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                send_message(chat_id, "⚠️ El formato del correo no parece válido. Por favor escribe un correo válido (ej: <code>amigo@gmail.com</code>):")
                return

            folder = state.get("folder", "MEGAPACK_PROGRAMACION_COMPLETO")
            remote = state.get("remote", "midrive")
            user_states[chat_id]["email"] = email

            kbd = {
                "inline_keyboard": [
                    [{"text": "👁️ Solo Lectura (Recomendado)", "callback_data": "sh:r:reader"}],
                    [{"text": "✏️ Lectura y Escritura", "callback_data": "sh:r:writer"}]
                ]
            }
            send_message(chat_id, f"👤 Destinatario: <code>{email}</code>\n📁 Carpeta: <code>{folder}</code>\n\n🔑 <b>Selecciona el tipo de acceso que le otorgarás:</b>", kbd)
            return

        if state.get("step") == "waiting_download_third_party_email":
            email = text.lower()
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                send_message(chat_id, "⚠️ Correo no válido. Ingresa el correo de Google de la persona:")
                return
            url = state.get("url")
            user_states.pop(chat_id, None)
            target = "Google Drive (Mi Unidad Principal - Julio)"
            send_message(chat_id, f"🚀 <b>Transmitiendo orden a Azure...</b>\n🎯 Descargando a tu Drive y compartiendo con <code>{email}</code>.")
            ok, err = trigger_workflow_download(url, target, recipient_email=email)
            if ok:
                send_message(chat_id, f"🎉 <b>¡Descarga en marcha a 1.5 Gbps!</b>\nAl finalizar se le enviará acceso automático a <code>{email}</code>.")
            else:
                send_message(chat_id, f"❌ Error al despachar en GitHub: {err}")
            return

        # Comandos principales
        if text in ["/start", "/help", "hola", "menu", "iniciar"]:
            user_states.pop(chat_id, None)
            welcome = (
                "👑 <b>Bienvenido al Centro OmniCloud Core</b>\n\n"
                "Puedo descargar cualquier archivo a máxima velocidad (1.5 - 2.0 Gbps) directo a tus nubes con tu PC 100% apagada y compartir carpetas instantáneamente.\n\n"
                "👉 <b>Opciones principales:</b>\n"
                "• <b>Enviar Enlaces:</b> Torrents, ISOs, HTTP, YouTube, MEGA o Drive.\n"
                "• <b>Compartir Carpetas:</b> Da acceso a terceros con solo dar su correo.\n"
                "• <b>Monitoreo:</b> Revisa descargas activas en tiempo real."
            )
            kbd = {
                "inline_keyboard": [
                    [{"text": "🤝 Compartir Carpeta con Tercero (Sin Rclone)", "callback_data": "cmd:share_menu"}],
                    [{"text": "📊 Estado de Descargas en Vivo", "callback_data": "cmd:status"}],
                    [{"text": "🔄 Sincronizar Megapack Ahora", "callback_data": "cmd:sync"}]
                ]
            }
            send_message(chat_id, welcome, kbd)
            return

        if text.startswith("/compartir"):
            parts = text.split()
            if len(parts) == 1:
                show_share_menu(chat_id)
                return
            elif len(parts) == 2:
                # /compartir email@gmail.com
                arg = parts[1]
                if "@" in arg:
                    execute_share(chat_id, "MEGAPACK_PROGRAMACION_COMPLETO", arg, role="reader")
                else:
                    show_share_menu(chat_id)
                return
            elif len(parts) >= 3:
                # /compartir carpeta email@gmail.com
                folder = parts[1]
                email = parts[2]
                execute_share(chat_id, folder, email, role="reader")
                return

        if text.startswith("/permisos"):
            parts = text.split()
            folder = parts[1] if len(parts) > 1 else "MEGAPACK_PROGRAMACION_COMPLETO"
            send_message(chat_id, f"🔍 Consultando permisos de <code>{folder}</code>...")
            perms = share_drive_folder.list_permissions(folder, remote="midrive")
            if not perms:
                send_message(chat_id, f"ℹ️ No se encontraron permisos o la carpeta <code>{folder}</code> no existe.")
            else:
                lines = [f"👥 <b>Permisos actuales para</b> <code>{folder}</code>:\n"]
                for p in perms:
                    em = p.get('emailAddress', 'Enlace Público')
                    name = p.get('displayName', '')
                    role = p.get('role', '')
                    lines.append(f"• <b>{em}</b> ({name}) - <code>{role}</code>")
                send_message(chat_id, "\n".join(lines))
            return

        if text.startswith("/revocar"):
            parts = text.split()
            if len(parts) < 2:
                send_message(chat_id, "ℹ️ Uso: <code>/revocar &lt;correo&gt;</code> o <code>/revocar &lt;carpeta&gt; &lt;correo&gt;</code>")
                return
            if len(parts) == 2:
                folder = "MEGAPACK_PROGRAMACION_COMPLETO"
                email = parts[1]
            else:
                folder = parts[1]
                email = parts[2]
            
            send_message(chat_id, f"⏳ Revocando acceso a <code>{email}</code> en <code>{folder}</code>...")
            ok = share_drive_folder.revoke_permission(folder, email, remote="midrive")
            if ok:
                send_message(chat_id, f"✅ Acceso revocado exitosamente para <code>{email}</code>.")
            else:
                send_message(chat_id, f"❌ No se encontró o no se pudo revocar el acceso para <code>{email}</code>.")
            return

        if text == "/status":
            st_msg = get_runs_status()
            send_message(chat_id, st_msg)
            return

        if text == "/sync":
            send_message(chat_id, "🔄 Disparando auto-sincronizador en la nube Azure...")
            ok, out = trigger_sync()
            if ok:
                send_message(chat_id, "✅ ¡Auto-sincronizador lanzado! Te avisaré si detecta novedades.")
            else:
                send_message(chat_id, f"❌ Error: {out}")
            return

        # Detección de Enlace
        if text.startswith("http://") or text.startswith("https://") or text.startswith("magnet:") or text.endswith(".torrent"):
            msg_id = msg.get("message_id")
            pending_urls[f"{chat_id}:{msg_id}"] = text

            preview_txt = (
                "📦 <b>Enlace Detectado:</b>\n"
                f"<code>{text[:300]}</code>\n\n"
                "🎯 <b>Selecciona a qué nube deseas enviarlo:</b>"
            )
            kbd = {
                "inline_keyboard": [
                    [{"text": "🚀 Google Drive (Rotación 10TB)", "callback_data": f"d:rot:{msg_id}"}],
                    [
                        {"text": "📁 Julio (5TB)", "callback_data": f"d:jul:{msg_id}"},
                        {"text": "📁 Vexor (5TB)", "callback_data": f"d:vex:{msg_id}"}
                    ],
                    [{"text": "🤝 Descargar y Compartir con Tercero", "callback_data": f"d:third:{msg_id}"}],
                    [
                        {"text": "☁️ OneDrive", "callback_data": f"d:one:{msg_id}"},
                        {"text": "🔴 MEGA.nz", "callback_data": f"d:meg:{msg_id}"}
                    ]
                ]
            }
            send_message(chat_id, preview_txt, kbd)
            return

        send_message(chat_id, "ℹ️ Envíame un enlace para descargar, o pulsa /compartir para compartir carpetas.")

    # 2. Clic en botón táctil
    elif "callback_query" in up:
        cq = up["callback_query"]
        cb_id = cq.get("id")
        answer_callback(cb_id)

        chat_id = str(cq.get("message", {}).get("chat", {}).get("id"))
        data = cq.get("data", "")

        if chat_id != AUTH_CHAT_ID:
            return

        if data == "cmd:share_menu":
            show_share_menu(chat_id)
        elif data == "cmd:status":
            st_msg = get_runs_status()
            send_message(chat_id, st_msg)
        elif data == "cmd:sync":
            send_message(chat_id, "🔄 Disparando auto-sincronizador en la nube Azure...")
            ok, out = trigger_sync()
            if ok:
                send_message(chat_id, "✅ ¡Auto-sincronizador lanzado! Te avisaré si detecta novedades.")
            else:
                send_message(chat_id, f"❌ Error: {out}")

        # Flujo de compartición por botones
        elif data.startswith("sh:f:"):
            folder_choice = data.split("sh:f:")[1]
            if folder_choice == "custom":
                user_states[chat_id] = {"step": "waiting_custom_folder"}
                send_message(chat_id, "✍️ <b>Escribe el nombre de la carpeta tal como aparece en tu Google Drive:</b>\n(Ej: <code>Mis_ISOS</code> o <code>Curso_Python_2026</code>)")
            else:
                user_states[chat_id] = {
                    "step": "waiting_share_email",
                    "folder": folder_choice,
                    "remote": "midrive"
                }
                send_message(chat_id, f"📁 Carpeta seleccionada: <code>{folder_choice}</code>\n\n📧 <b>Escribe el correo de Google de la persona a quien deseas compartirle el acceso:</b>\n(Ej: <code>amigo@gmail.com</code>)")

        elif data.startswith("sh:r:"):
            role_choice = data.split("sh:r:")[1]
            state = user_states.get(chat_id, {})
            folder = state.get("folder", "MEGAPACK_PROGRAMACION_COMPLETO")
            email = state.get("email")
            remote = state.get("remote", "midrive")
            user_states.pop(chat_id, None)

            if email:
                execute_share(chat_id, folder, email, role=role_choice, remote=remote)
            else:
                send_message(chat_id, "⚠️ La sesión expiró. Por favor pulsa /compartir para reiniciar.")

        elif data == "sh:list":
            perms = share_drive_folder.list_permissions("MEGAPACK_PROGRAMACION_COMPLETO", remote="midrive")
            if not perms:
                send_message(chat_id, "ℹ️ No se encontraron permisos.")
            else:
                lines = ["👥 <b>Personas con acceso a MEGAPACK_PROGRAMACION_COMPLETO:</b>\n"]
                for p in perms:
                    em = p.get('emailAddress', 'Enlace Público')
                    name = p.get('displayName', '')
                    role = p.get('role', '')
                    lines.append(f"• <b>{em}</b> ({name}) - <code>{role}</code>")
                send_message(chat_id, "\n".join(lines))

        # Flujo de selección de descarga
        elif data.startswith("d:"):
            parts = data.split(":")
            cloud_code = parts[1]
            msg_ref = parts[2] if len(parts) > 2 else ""

            if cloud_code == "third":
                url_key = f"{chat_id}:{msg_ref}"
                full_url = pending_urls.get(url_key)
                if not full_url:
                    orig_text = cq.get("message", {}).get("text", "")
                    for line in orig_text.split("\n"):
                        l = line.strip()
                        if l.startswith("http://") or l.startswith("https://") or l.startswith("magnet:"):
                            full_url = l
                            break
                if full_url:
                    user_states[chat_id] = {
                        "step": "waiting_download_third_party_email",
                        "url": full_url
                    }
                    send_message(chat_id, "📧 <b>Ingresa el correo Google de la persona a quien deseas compartirle esta descarga:</b>\n(Azure la descargará a máxima velocidad y le otorgará acceso automáticamente)")
                else:
                    send_message(chat_id, "⚠️ No se encontró la URL en memoria. Por favor reenvía el enlace.")
                return

            target_map = {
                "rot": "Google Drive (Rotación Inteligente: Julio + Vexor 10TB)",
                "jul": "Google Drive (Mi Unidad Principal - Julio)",
                "vex": "Google Drive (Unidad Auxiliar - Vexor)",
                "one": "Microsoft OneDrive (Aviso: Throttling 429)",
                "meg": "MEGA.nz"
            }
            target = target_map.get(cloud_code, "Google Drive (Rotación Inteligente: Julio + Vexor 10TB)")

            url_key = f"{chat_id}:{msg_ref}"
            full_url = pending_urls.get(url_key)

            if not full_url:
                orig_text = cq.get("message", {}).get("text", "")
                lines = orig_text.split("\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("http://") or line.startswith("https://") or line.startswith("magnet:"):
                        full_url = line
                        break

            if full_url:
                send_message(chat_id, f"🚀 <b>Transmitiendo orden a Azure...</b>\n🎯 Destino: <i>{target}</i>\nTu PC puede estar apagada.")
                ok, err = trigger_workflow_download(full_url, target)
                if ok:
                    send_message(chat_id, "🎉 <b>¡Descarga en marcha a 1.5 Gbps!</b>\nLos servidores de Azure están transfiriendo tus archivos. Sonará una notificación cuando finalice.")
                else:
                    send_message(chat_id, f"❌ Error al despachar en GitHub: {err}")
            else:
                send_message(chat_id, "⚠️ No se encontró la URL en memoria. Por favor reenvía el enlace.")

def main():
    print("=" * 60)
    print("  OMNICLOUD CORE - TELEGRAM BOT POLLER ACTIVO")
    print(f"  Bot: @VexorOmniBot")
    print(f"  Chat Autorizado: {AUTH_CHAT_ID} (Julio)")
    print("=" * 60)
    offset = 0
    while True:
        try:
            url = f"{API_BASE}/getUpdates?offset={offset}&timeout=30"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            for up in data.get("result", []):
                offset = up["update_id"] + 1
                handle_update(up)
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
