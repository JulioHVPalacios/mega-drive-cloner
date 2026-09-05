import os
import sys
import subprocess
import shutil

def find_rclone_conf():
    appdata = os.environ.get("APPDATA", "")
    conf_path = os.path.join(appdata, "rclone", "rclone.conf")
    if os.path.exists(conf_path):
        return conf_path
    home = os.path.expanduser("~")
    alt_path = os.path.join(home, ".config", "rclone", "rclone.conf")
    if os.path.exists(alt_path):
        return alt_path
    return conf_path

def sync_to_github():
    conf_path = find_rclone_conf()
    if not os.path.exists(conf_path):
        print(f"❌ No se encontró el archivo rclone.conf en: {conf_path}")
        return False
    
    print("\n📤 Subiendo configuración actualizada a GitHub Secrets (RCLONE_CONFIG)...")
    try:
        with open(conf_path, "r", encoding="utf-8") as f:
            content = f.read()
        p = subprocess.Popen(["gh", "secret", "set", "RCLONE_CONFIG"], stdin=subprocess.PIPE, text=True)
        p.communicate(input=content)
        if p.returncode == 0:
            print("🎉 ¡ÉXITO TOTAL! Las credenciales están sincronizadas con tu cuenta de GitHub.")
            print("🚀 Ya puedes usar tus nubes directamente desde el Descargador Universal.")
            return True
        else:
            print("⚠️ Hubo un detalle al subir con GitHub CLI. Asegúrate de tener conexión.")
            return False
    except Exception as e:
        print(f"❌ Error al sincronizar con GitHub: {e}")
        return False

def main():
    while True:
        print("\n" + "="*65)
        print("   🌐 ASISTENTE UNIVERSAL: CONECTAR CUALQUIER NUBE A GITHUB")
        print("="*65)
        print("  [1] 📁 Google Drive (Conectar cuenta adicional de Google)")
        print("  [2] ☁️ Microsoft OneDrive (Conectar cuenta Microsoft Personal/Trabajo)")
        print("  [3] 🔴 MEGA.nz (Conectar cuenta de MEGA con usuario y contraseña)")
        print("  [4] 🌐 Nube Desconocida / WebDAV (InfiniCLOUD, TeraBox, pCloud, etc.)")
        print("  [5] 🪣 Almacenamiento S3 (Cloudflare R2, Wasabi, Backblaze B2, Minio)")
        print("  [6] 🖥️ Servidor Remoto (FTP / SFTP)")
        print("  [7] 🔄 Sincronizar mis nubes actuales a GitHub Secrets AHORA")
        print("  [0] ❌ Salir")
        print("="*65)
        
        op = input("👉 Selecciona una opción (0-7): ").strip()
        
        if op == "0":
            print("\n👋 ¡Hasta luego!")
            break
            
        elif op == "1":
            print("\n--- Conectando Google Drive ---")
            nombre = input("Escribe un nombre para este Drive (ej: drive2): ").strip() or "drive2"
            print("🌐 Abriendo navegador para autorizar con Google...")
            subprocess.run(f'rclone config create "{nombre}" drive scope="drive"', shell=True)
            sync_to_github()
            
        elif op == "2":
            print("\n--- Conectando Microsoft OneDrive ---")
            print("🌐 Se abrirá tu navegador para iniciar sesión en Microsoft...")
            subprocess.run('rclone config create onedrive onedrive', shell=True)
            sync_to_github()
            
        elif op == "3":
            print("\n--- Conectando MEGA.nz ---")
            user = input("Correo de tu cuenta de MEGA: ").strip()
            pwd = input("Contraseña de tu cuenta de MEGA: ").strip()
            if user and pwd:
                obs = subprocess.check_output(f'rclone obscure "{pwd}"', shell=True, text=True).strip()
                subprocess.run(f'rclone config create mega mega user="{user}" pass="{obs}"', shell=True)
                sync_to_github()
            else:
                print("⚠️ Datos incompletos.")
                
        elif op == "4":
            print("\n--- Conectando Nube Desconocida / WebDAV ---")
            print("Ejemplo: Si usas InfiniCLOUD, TeraBox WebDAV, pCloud, 4shared o Nextcloud.")
            nombre = input("Nombre identificador (ej: mi_nube): ").strip() or "mi_nube"
            url = input("URL WebDAV (ej: https://dav.ejemplo.com/): ").strip()
            user = input("Usuario o correo: ").strip()
            pwd = input("Contraseña o App Password: ").strip()
            if url and user:
                obs = subprocess.check_output(f'rclone obscure "{pwd}"', shell=True, text=True).strip() if pwd else ""
                cmd = f'rclone config create "{nombre}" webdav url="{url}" vendor="other" user="{user}" pass="{obs}"'
                subprocess.run(cmd, shell=True)
                sync_to_github()
            else:
                print("⚠️ Se requiere al menos la URL y el usuario.")
                
        elif op == "5":
            print("\n--- Conectando S3 Compatible (Wasabi, R2, B2) ---")
            nombre = input("Nombre identificador (ej: mis3): ").strip() or "mis3"
            endpoint = input("Endpoint URL (ej: https://s3.wasabisys.com): ").strip()
            ak = input("Access Key ID: ").strip()
            sk = input("Secret Access Key: ").strip()
            if endpoint and ak and sk:
                cmd = f'rclone config create "{nombre}" s3 provider="Other" endpoint="{endpoint}" access_key_id="{ak}" secret_access_key="{sk}"'
                subprocess.run(cmd, shell=True)
                sync_to_github()
            else:
                print("⚠️ Faltan datos de S3.")
                
        elif op == "6":
            print("\n--- Conectando Servidor Remoto (FTP / SFTP) ---")
            nombre = input("Nombre identificador (ej: miservidor): ").strip() or "miservidor"
            tipo = input("Tipo (ftp o sftp, por defecto sftp): ").strip().lower() or "sftp"
            host = input("Host o IP del servidor: ").strip()
            user = input("Usuario: ").strip()
            pwd = input("Contraseña: ").strip()
            obs = subprocess.check_output(f'rclone obscure "{pwd}"', shell=True, text=True).strip() if pwd else ""
            cmd = f'rclone config create "{nombre}" {tipo} host="{host}" user="{user}" pass="{obs}"'
            subprocess.run(cmd, shell=True)
            sync_to_github()
            
        elif op == "7":
            sync_to_github()
            
        input("\n[Presiona Enter para continuar...]")

if __name__ == "__main__":
    main()
