"""
OmniCloud Core - Telegram Bot Local Poller (Zero dependencias externas)
Ejecutable con Python 3 nativo.
"""
import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.parse

BOT_TOKEN = "8775957501:AAEF5W3TgWUku6pMCqdFN9ouFpxMG4BJ7MI"
AUTH_CHAT_ID = "1136933800"
REPO = "JulioHVPalacios/mega-drive-cloner"
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Diccionario en memoria para URLs pendientes de selección de destino
pending_urls = {}

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
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return call_tg("sendMessage", payload)

def answer_callback(cb_id):
    payload = {"callback_query_id": cb_id}
    call_tg("answerCallbackQuery", payload)

def get_runs_status():
    try:
        cmd = ["gh", "run", "list", "--repo", REPO, "--limit", "4", "--json", "databaseId,name,status,conclusion,createdAt"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
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

def trigger_workflow_download(url, target):
    try:
        cmd = [
            "gh", "workflow", "run", "descargador_universal.yml",
            "--repo", REPO,
            "-f", f"source_url={url}",
            "-f", f"destination_target={target}",
            "-f", "dest_folder=DESCARGAS_UNIVERSALES",
            "-f", "transfer_mode=Auto Streaming RAM Turbo (Zero Disco - Soporta 500GB/1TB/2TB)"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, res.stdout
    except Exception as e:
        return False, str(e)

def trigger_sync():
    try:
        cmd = ["gh", "workflow", "run", "sincronizador_automatico_megapack.yml", "--repo", REPO]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, res.stdout
    except Exception as e:
        return False, str(e)

def handle_update(up):
    # 1. Mensaje normal
    if "message" in up:
        msg = up["message"]
        chat_id = str(msg.get("chat", {}).get("id"))
        text = (msg.get("text") or "").strip()

        if chat_id != AUTH_CHAT_ID:
            send_message(chat_id, "⛔ Acceso no autorizado. Este bot es de uso privado.")
            return

        if text in ["/start", "/help", "hola", "menu", "iniciar"]:
            welcome = (
                "👑 <b>Bienvenido al Centro OmniCloud Core</b>\n\n"
                "Puedo descargar cualquier archivo a máxima velocidad (1.5 - 2.0 Gbps) directo a tus nubes con tu PC 100% apagada.\n\n"
                "👉 <b>Simplemente envíame o comparte cualquier enlace:</b>\n"
                "• Torrents o Magnets\n"
                "• ISOs gigantes de foros o HTTP\n"
                "• MEGA.nz o TeraBox\n"
                "• Videos de YouTube / HLS / m3u8\n"
                "• Carpetas de Google Drive ajenas"
            )
            kbd = {
                "inline_keyboard": [
                    [{"text": "📊 Estado de Descargas en Vivo", "callback_data": "cmd:status"}],
                    [{"text": "🔄 Sincronizar Megapack Ahora", "callback_data": "cmd:sync"}]
                ]
            }
            send_message(chat_id, welcome, kbd)
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
            # Generar clave de sesión
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
                    [
                        {"text": "☁️ OneDrive", "callback_data": f"d:one:{msg_id}"},
                        {"text": "🔴 MEGA.nz", "callback_data": f"d:meg:{msg_id}"}
                    ]
                ]
            }
            send_message(chat_id, preview_txt, kbd)
            return

        send_message(chat_id, "ℹ️ Envíame un enlace (HTTP/Magnet/Drive/Mega) o pulsa /start para ver las opciones.")

    # 2. Clic en botón táctil
    elif "callback_query" in up:
        cq = up["callback_query"]
        cb_id = cq.get("id")
        answer_callback(cb_id)

        chat_id = str(cq.get("message", {}).get("chat", {}).get("id"))
        data = cq.get("data", "")

        if chat_id != AUTH_CHAT_ID:
            return

        if data == "cmd:status":
            st_msg = get_runs_status()
            send_message(chat_id, st_msg)
        elif data == "cmd:sync":
            send_message(chat_id, "🔄 Disparando auto-sincronizador en la nube Azure...")
            ok, out = trigger_sync()
            if ok:
                send_message(chat_id, "✅ ¡Auto-sincronizador lanzado! Te avisaré si detecta novedades.")
            else:
                send_message(chat_id, f"❌ Error: {out}")
        elif data.startswith("d:"):
            parts = data.split(":")
            cloud_code = parts[1]
            msg_ref = parts[2] if len(parts) > 2 else ""

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
                # Intentar buscar en el texto del mensaje
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
            # Reintentar con backoff suave
            time.sleep(2)

if __name__ == "__main__":
    main()
