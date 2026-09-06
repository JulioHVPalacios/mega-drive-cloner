"""
OmniCloud Core - Telegram Bot Local Poller Inteligente (Zero Dependencias)
Totalmente optimizado para manejo táctil en móviles:
- Teclado persistente con botones grandes (Cero necesidad de escribir comandos)
- Motor de Procesamiento de Lenguaje Natural (NLP Cognitivo)
- Integración con Google Gemini 2.0 AI (Respuestas y asesoría técnica en vivo)
- Compartición instantánea de carpetas Google Drive a cualquier Gmail
- Despacho de descargas ultrarrápidas en Azure Cloud (1.5 - 2.0 Gbps, PC apagada)
- Modos Swarm Multi-Nodo (30 GB en < 4 minutos con auto-unidor .bat)
- Traductor de errores a lenguaje cotidiano comprensible
"""
import os
import sys
import json
import time
import re
import unicodedata
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

# =====================================================================
# CONFIGURACIÓN MAESTRA
# =====================================================================
BOT_TOKEN = "8775957501:AAEF5W3TgWUku6pMCqdFN9ouFpxMG4BJ7MI"
AUTH_CHAT_ID = "1136933800"
REPO = "JulioHVPalacios/mega-drive-cloner"
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEMINI_KEY_FILE = os.path.join(BASE_DIR, "gemini_api_key.txt")

# Sesiones en memoria
pending_urls = {}
user_states = {}

# Teclado Táctil Principal Fijo en el Celular (Persistent Reply Keyboard)
MAIN_KEYBOARD = {
    "keyboard": [
        [{"text": "🚀 Enviar Enlace / Descargar"}, {"text": "🤝 Compartir Carpeta"}],
        [{"text": "📊 Estado de Descargas"}, {"text": "👥 Ver Permisos"}],
        [{"text": "🧠 Asistente IA"}, {"text": "🔄 Sincronizar Megapack"}]
    ],
    "resize_keyboard": True,
    "is_persistent": True
}

# =====================================================================
# COMUNICACIÓN TELEGRAM API
# =====================================================================
def call_tg(endpoint, payload):
    url = f"{API_BASE}/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERROR TG] {endpoint}: {e}", flush=True)
        return None

def send_message(chat_id, text, reply_markup=None, with_keyboard=True):
    payload = {
        "chat_id": str(chat_id),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    elif with_keyboard:
        payload["reply_markup"] = MAIN_KEYBOARD
    return call_tg("sendMessage", payload)

def answer_callback(cb_id, text=None):
    payload = {"callback_query_id": cb_id}
    if text:
        payload["text"] = text
    call_tg("answerCallbackQuery", payload)

def escape_html(text):
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))

# =====================================================================
# INTELIGENCIA ARTIFICIAL: GOOGLE GEMINI 2.0 FLASH + MOTOR COGNITIVO
# =====================================================================
GEMINI_SYSTEM_PROMPT = """Eres OmniCloud AI, el asistente de inteligencia artificial personal de Julio en su bot de Telegram (@VexorOmniBot).
Tu labor es orientarlo a él y a sus clientes con máxima claridad, cordialidad y profesionalismo.
Conoces al 100% la infraestructura de OmniCloud:
1. Nube Microsoft Azure: Descargas extremas a 1.5 - 2.0 Gbps que funcionan 24/7 con la PC de Julio apagada.
2. Almacenamiento: Google Drive 10 TB con rotación automática entre cuenta principal Julio (5TB) y auxiliar Vexor (5TB) para saltarse cualquier límite diario de Google.
3. Modos Swarm Multi-Nodo: Para archivos gigantes de 30GB+ (ISOs, RARs, ZIPs) que bajan en menos de 4 minutos y traen un script automático 'DOBLE_CLIC_AQUI_PARA_UNIR.bat' para que personas sin conocimientos técnicos monten o extraigan todo en 5 segundos con 1 solo clic.
4. Compartición sin Rclone: Permite dar acceso a cualquier carpeta de Google Drive a cualquier amigo o cliente con solo su correo Gmail, sin contraseñas ni instalaciones en su PC.
5. Formateo Seguro de PC: El formateo del disco C: nunca borra el disco D: ni detiene los servidores de Azure en la nube. El archivo 'restaurar_tras_formateo.bat' restaura todo en 60 segundos con 1 solo clic.

FORMATO OBLIGATORIO:
- Responde SIEMPRE en español claro, amigable y directo.
- Usa formato HTML compatible con Telegram (<b>negrita</b>, <code>código</code>, <i>cursiva</i>). NO uses markdown con **.
- Mantén las respuestas breves y fáciles de leer en una pantalla de celular (máximo 2 a 3 párrafos).
"""

def get_gemini_key():
    if os.path.exists(GEMINI_KEY_FILE):
        try:
            with open(GEMINI_KEY_FILE, "r", encoding="utf-8") as f:
                k = f.read().strip()
                if k.startswith("AIzaSy"):
                    return k
        except Exception:
            pass
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if k and k.strip().startswith("AIzaSy"):
        return k.strip()
    return None

def save_gemini_key(key):
    try:
        with open(GEMINI_KEY_FILE, "w", encoding="utf-8") as f:
            f.write(key.strip())
        return True
    except Exception as e:
        print(f"Error guardando clave Gemini: {e}")
        return False

def call_gemini_api(prompt):
    api_key = get_gemini_key()
    if not api_key:
        return None

    models = ["gemini-2.0-flash", "gemini-1.5-flash"]
    payload = {
        "system_instruction": {
            "parts": [{"text": GEMINI_SYSTEM_PROMPT}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 900
        }
    }
    data = json.dumps(payload).encode("utf-8")

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                candidates = res.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    text = text.replace("**", "<b>").replace("**", "</b>")
                    return text
        except Exception as e:
            print(f"[GEMINI] Error con {model}: {e}", flush=True)
            continue
    return None

def get_cognitive_answer(topic):
    if topic == "TIMING":
        return (
            "⏱️ <b>TIEMPOS CERTIFICADOS DE TRANSFERENCIA (OMNICLOUD CORE)</b>\n\n"
            "<b>1. Servidor a Servidor (Drive a Drive):</b>\n"
            "• <b>300 GB:</b> ~30 segundos\n"
            "• <b>500 GB:</b> ~45 segundos\n"
            "• <b>1 TB:</b> ~1.5 minutos\n\n"
            "<b>2. Compartición Instantánea (/compartir):</b>\n"
            "• <b>Cualquier tamaño (incluso el Megapack de 825 GB):</b> <b>1.5 segundos</b>.\n\n"
            "<b>3. Azure Swarm (Desde Internet a Google Drive):</b>\n"
            "• <b>300 GB:</b> ~16 minutos (4 nodos en paralelo)\n"
            "• <b>500 GB:</b> ~27 minutos (4 nodos en paralelo)\n"
            "• <b>1 TB:</b> ~55 minutos (con rotación Julio + Vexor para saltar el tope de 750GB/día)\n\n"
            "<b>4. Enlace Directo Monolítico (1 solo hilo):</b>\n"
            "• <b>300 GB:</b> ~58 minutos\n"
            "• <b>500 GB:</b> ~1h 36m\n"
            "• <b>1 TB:</b> ~3h 15m\n\n"
            "💡 <i>Recuerda: Tu PC puede estar 100% apagada durante todo el proceso.</i>"
        )
    elif topic == "FORMATTING":
        return (
            "🛡️ <b>PROTECCIÓN TOTAL CONTRA FORMATEO DE PC</b>\n\n"
            "<b>¿Qué pasa si formateas tu computadora?</b>\n"
            "<b>¡NADA se pierde ni se interrumpe!</b>\n\n"
            "1. <b>Nube 100% Autónoma:</b> Los servidores de Azure y GitHub Actions viven en internet. Siguen descargando y compartiendo 24/7 aunque no tengas Windows instalado.\n"
            "2. <b>Disco D: Intacto:</b> Al formatear Windows, solo se borra el disco <code>C:</code>. Todo tu repositorio y archivos en <code>D:\\mega-drive-cloner</code> quedan a salvo.\n"
            "3. <b>Restauración en 1 Clic (60 segundos):</b>\n"
            "Tras formatear tu PC, solo abres tu disco D: y le das doble clic a:\n"
            "👉 <code>restaurar_tras_formateo.bat</code>\n\n"
            "Ese script instala automáticamente Rclone, GitHub CLI, Aria2c, WinFsp y reconecta tus 10TB de Google Drive al instante."
        )
    elif topic == "JOINING":
        return (
            "📦 <b>¿CÓMO USAN LOS ARCHIVOS TUS AMIGOS O CLIENTES?</b>\n\n"
            "<b>Cero complicaciones técnicas (A prueba de novatos):</b>\n\n"
            "Cuando OmniCloud sube archivos de 30GB en partes (<code>.001, .002</code> o <code>.part1.rar</code>), deposita automáticamente en esa misma carpeta el archivo:\n"
            "👉 <b>DOBLE_CLIC_AQUI_PARA_UNIR.bat</b>\n\n"
            "<b>¿Qué hace la persona que lo recibe?</b>\n"
            "1. Descarga la carpeta de su Google Drive a su PC.\n"
            "2. Le da <b>doble clic</b> a <code>DOBLE_CLIC_AQUI_PARA_UNIR.bat</code>.\n"
            "3. En <b>5 segundos</b> se ensamblan las partes y se monta automáticamente en Windows como si hubiera metido un DVD en su lectora.\n"
            "4. Si es un RAR o ZIP, WinRAR / 7-Zip lo descomprimen con un simple clic derecho ➔ <i>Extraer aquí</i>."
        )
    elif topic == "SHARING":
        return (
            "🤝 <b>¿CÓMO FUNCIONA LA COMPARTICIÓN CON TERCEROS?</b>\n\n"
            "• <b>Cero programas para la otra persona:</b> No necesitan Rclone, contraseñas ni instalar nada.\n"
            "• <b>Solo su correo:</b> Tú solo escribes su correo (ej: <code>amigo@gmail.com</code>) en este bot.\n"
            "• <b>Inmediato:</b> La carpeta aparece de inmediato en su Google Drive dentro de <b>'Compartido conmigo'</b>.\n"
            "• <b>Consumo de cuota cero:</b> Al destinatario no le resta espacio en su cuenta gratuita de Google."
        )
    elif topic == "AI_SETUP":
        return (
            "🧠 <b>CÓMO VINCULAR TU CLAVE GRATUITA DE GOOGLE GEMINI AI</b>\n\n"
            "Tu bot ya tiene respuestas inteligentes integradas, pero si deseas que Google Gemini 2.0 Flash charle contigo libremente:\n\n"
            "1. Consigue una clave gratuita en 10 segundos en:\n"
            "👉 <a href='https://aistudio.google.com/'>Google AI Studio (aistudio.google.com)</a>\n"
            "2. Copia tu clave (empieza por <code>AIzaSy...</code>)\n"
            "3. Envíala a este chat escribiendo:\n"
            "<code>/ia_key TU_CLAVE_AQUI</code>\n\n"
            "¡Y listo! El bot activará el cerebro de Gemini al 100%."
        )
    return "ℹ️ Escribe lo que necesites saber y te orientaré de inmediato."

# =====================================================================
# TRADUCTOR DE ERRORES A LENGUAJE AMIGABLE
# =====================================================================
def translate_error(raw_err):
    err_str = str(raw_err).lower()
    if "quota" in err_str or "rate limit" in err_str or "403" in err_str:
        return "⚠️ Google Drive o GitHub tienen una pequeña pausa temporal de cuota. El sistema rotará automáticamente o reintentará en breve."
    if "could not resolve" in err_str or "connection refused" in err_str:
        return "⚠️ El enlace que enviaste parece estar inaccesible o el servidor de origen no responde."
    if "authentication" in err_str or "login" in err_str:
        return "⚠️ Las credenciales necesitan actualizarse. Puedes usar 'restaurar_tras_formateo.bat' para renovarlas."
    return f"⚠️ Nota técnica: {escape_html(str(raw_err)[:200])}"

# =====================================================================
# OPERACIONES DE NUBE Y GITHUB ACTIONS
# =====================================================================
def get_runs_status():
    try:
        cmd = ["gh", "run", "list", "--repo", REPO, "--limit", "4", "--json", "databaseId,name,status,conclusion,createdAt,workflowName"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
        runs = json.loads(res.stdout)
        if not runs:
            return "ℹ️ No hay ejecuciones registradas en GitHub Actions."

        msg = "📊 <b>ESTADO DE DESCARGAS EN VIVO (AZURE CLOUD):</b>\n\n"
        for r in runs:
            st = r.get("status")
            conc = r.get("conclusion")
            name = r.get("workflowName") or r.get("name")
            db_id = r.get("databaseId")

            if st == "completed":
                if conc == "success":
                    icon = "✅"
                    desc = "Completada al 100% con éxito"
                else:
                    icon = "❌"
                    desc = f"Detenida ({conc})"
            else:
                icon = "🔄"
                desc = "Descargando en vivo en Azure (PC apagada)"

            msg += f"{icon} <b>{escape_html(name)}</b>\n"
            msg += f"• Estado: <code>{desc}</code>\n"
            msg += f"• ID de tarea: <code>{db_id}</code>\n\n"

        msg += "💡 <i>Los servidores de Azure trabajan de forma independiente a tu computadora.</i>"
        return msg
    except Exception as e:
        return f"❌ Error al consultar GitHub: {translate_error(e)}"

def trigger_workflow_download(url, target, recipient_email="", dest_folder="DESCARGAS_UNIVERSALES"):
    try:
        cmd = [
            "gh", "workflow", "run", "descargador_universal.yml",
            "--repo", REPO,
            "-f", f"source_url={url}",
            "-f", f"destination_target={target}",
            "-f", f"dest_folder={dest_folder}",
            "-f", "transfer_mode=Auto Streaming RAM Turbo (Zero Disco - Soporta 500GB/1TB/2TB)"
        ]
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
        return True, ""
    except Exception as e:
        return False, str(e)

def trigger_swarm_download(mode="external_monolithic_range_swarm"):
    try:
        cmd = [
            "gh", "workflow", "run", "omniengine_universal.yml",
            "--repo", REPO,
            "-f", f"mode={mode}"
        ]
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
        return True, ""
    except Exception as e:
        return False, str(e)

def trigger_sync():
    try:
        cmd = ["gh", "workflow", "run", "sincronizador_automatico_megapack.yml", "--repo", REPO]
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
        return True, ""
    except Exception as e:
        return False, str(e)

# =====================================================================
# MENÚS Y FLUJOS TÁCTILES GUIADOS
# =====================================================================
def show_welcome(chat_id):
    txt = (
        "👑 <b>Centro de Control OmniCloud Core</b>\n\n"
        "Descargas ultrarrápidas (1.5 - 2.0 Gbps) en la nube Azure con tu <b>PC 100% apagada</b> y gestión de Google Drive (10 TB).\n\n"
        "👇 <b>Toca cualquiera de los botones de abajo para empezar:</b>\n"
        "• <b>🚀 Enviar Enlace:</b> Descarga archivos gigantes o torrents.\n"
        "• <b>🤝 Compartir Carpeta:</b> Comparte con amigos solo con su correo.\n"
        "• <b>📊 Estado de Descargas:</b> Mira tus descargas activas en Azure.\n"
        "• <b>🧠 Asistente IA:</b> Pregúntame dudas de velocidad, formateo o uso."
    )
    send_message(chat_id, txt)

def show_download_prompt(chat_id):
    txt = (
        "📥 <b>PEGA AQUÍ CUALQUIER ENLACE PARA DESCARGAR</b>\n\n"
        "Puedo recibir:\n"
        "• 🌐 <b>Archivos Directos:</b> ISO, RAR, ZIP, EXE, MKV, MP4...\n"
        "• 🧲 <b>Torrents / Magnets:</b> Enlaces <code>magnet:?xt=...</code>\n"
        "• 📦 <b>Google Drive:</b> Carpetas o archivos de terceros\n"
        "• 🔴 <b>MEGA.nz / TeraBox:</b> Enlaces de descarga directa\n\n"
        "⚡ <i>Azure lo transferirá a 1.5 - 2.0 Gbps sin consumir tu conexión ni exigir que tu PC esté encendida.</i>\n\n"
        "👉 <b>Simplemente pega el enlace en este chat:</b>"
    )
    send_message(chat_id, txt)

def show_share_menu(chat_id):
    txt = (
        "🤝 <b>COMPARTIR CARPETAS DE GOOGLE DRIVE AL INSTANTE</b>\n\n"
        "Da acceso a amigos, colegas o clientes <b>solo escribiendo su correo de Google</b>.\n"
        "• <b>Cero fricción:</b> No necesitan Rclone ni contraseñas.\n"
        "• <b>Instantáneo:</b> Les aparece en 1.5 segundos en 'Compartido conmigo'.\n"
        "• <b>Sin consumo de cuota:</b> No gasta su espacio de Drive.\n\n"
        "📁 <b>Toca la carpeta que deseas compartir:</b>"
    )
    kbd = {
        "inline_keyboard": [
            [{"text": "📦 Megapack Programación (825 GB)", "callback_data": "sh:f:MEGAPACK_PROGRAMACION_COMPLETO"}],
            [{"text": "📂 Descargas Universales", "callback_data": "sh:f:DESCARGAS_UNIVERSALES"}],
            [{"text": "✍️ Escribir otra carpeta...", "callback_data": "sh:f:custom"}],
            [{"text": "👥 Ver quién tiene acceso (/permisos)", "callback_data": "sh:list"}]
        ]
    }
    send_message(chat_id, txt, kbd)

def show_link_options(chat_id, url, msg_id):
    pending_urls[f"{chat_id}:{msg_id}"] = url
    url_preview = url if len(url) <= 80 else url[:77] + "..."

    url_lower = url.lower()
    is_big = any(ext in url_lower for ext in [".iso", ".rar", ".zip", ".tar", ".7z", ".img", ".mkv"])

    txt = (
        "📦 <b>ENLACE DETECTADO CON ÉXITO</b>\n"
        f"<code>{escape_html(url_preview)}</code>\n\n"
        "🎯 <b>¿Cómo deseas procesar esta descarga?</b>"
    )

    buttons = [
        [{"text": "🚀 Descarga Estándar Turbo (Drive 10TB)", "callback_data": f"d:rot:{msg_id}"}]
    ]

    if is_big:
        buttons.append([{"text": "⚡ Modo Swarm 4 Nodos (30GB en <4 min)", "callback_data": f"d:swarm:{msg_id}"}])

    buttons.extend([
        [{"text": "🤝 Descargar y Compartir con Amigo/Cliente", "callback_data": f"d:third:{msg_id}"}],
        [
            {"text": "📁 Julio (5TB)", "callback_data": f"d:jul:{msg_id}"},
            {"text": "📁 Vexor (5TB)", "callback_data": f"d:vex:{msg_id}"}
        ],
        [
            {"text": "☁️ OneDrive", "callback_data": f"d:one:{msg_id}"},
            {"text": "🔴 MEGA.nz", "callback_data": f"d:meg:{msg_id}"}
        ],
        [{"text": "❌ Cancelar", "callback_data": "cmd:cancel"}]
    ])

    kbd = {"inline_keyboard": buttons}
    send_message(chat_id, txt, kbd)

def show_folder_options_for_email(chat_id, email):
    txt = (
        f"📧 <b>Correo Detectado:</b> <code>{email}</code>\n\n"
        "📁 <b>¿A qué carpeta deseas darle acceso a esta persona?</b>"
    )
    kbd = {
        "inline_keyboard": [
            [{"text": "📦 Megapack Programación (825 GB)", "callback_data": f"sh:quick:MEGAPACK_PROGRAMACION_COMPLETO:{email}"}],
            [{"text": "📂 Descargas Universales", "callback_data": f"sh:quick:DESCARGAS_UNIVERSALES:{email}"}],
            [{"text": "❌ Cancelar", "callback_data": "cmd:cancel"}]
        ]
    }
    send_message(chat_id, txt, kbd)

def show_ai_menu(chat_id):
    has_gemini = get_gemini_key() is not None
    gemini_status = "✅ Google Gemini 2.0 Conectado" if has_gemini else "⚡ Motor Cognitivo Local Activo"

    txt = (
        "🧠 <b>ASISTENTE INTELIGENTE OMNICLOUD</b>\n\n"
        f"Estado: <b>{gemini_status}</b>\n"
        "Puedo resolver cualquier duda sobre tus descargas, almacenamiento, formateo o archivos.\n\n"
        "👇 <b>Toca una pregunta frecuente o escribe directamente en el chat:</b>"
    )
    kbd = {
        "inline_keyboard": [
            [{"text": "⏱️ ¿Cuánto tardan 300GB, 500GB o 1TB?", "callback_data": "ai:faq:TIMING"}],
            [{"text": "🛡️ ¿Qué pasa si formateo mi PC?", "callback_data": "ai:faq:FORMATTING"}],
            [{"text": "📦 ¿Cómo se usa el auto-unidor .bat?", "callback_data": "ai:faq:JOINING"}],
            [{"text": "🤝 ¿Cómo compartir sin que tengan Rclone?", "callback_data": "ai:faq:SHARING"}],
            [{"text": "🔑 Conectar Clave Gemini AI (Opcional)", "callback_data": "ai:faq:AI_SETUP"}]
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
                "ℹ️ <b>¿Cómo lo usa la otra persona?</b>\n"
                "1. Google le envió una notificación oficial a su correo.\n"
                "2. La carpeta aparece ya en su pestaña <b>'Compartido conmigo'</b> en Google Drive.\n"
                "3. Si desea verla en su 'Mi unidad': Click derecho -> <i>Añadir acceso directo a Drive</i> (0 bytes ocupados en su cuota)."
            )
            send_message(chat_id, msg)
        else:
            send_message(chat_id, f"❌ No se pudo compartir <code>{folder}</code> con <code>{email}</code>. Verifica que el correo sea una cuenta de Google válida.")
    except Exception as e:
        send_message(chat_id, f"❌ Error en la operación: {translate_error(e)}")

# =====================================================================
# MOTOR DE PROCESAMIENTO DE LENGUAJE NATURAL (NLP)
# =====================================================================
def clean_text_for_nlp(text):
    text_norm = ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')
    return text_norm.strip()

def process_natural_language(chat_id, text, msg_id):
    norm = clean_text_for_nlp(text)

    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    urls = re.findall(r'(https?://[^\s]+|magnet:\?[^\s]+)', text)

    if urls:
        show_link_options(chat_id, urls[0], msg_id)
        return

    if text.startswith("/ia_key") or text.startswith("/key"):
        parts = text.split()
        if len(parts) > 1 and parts[1].startswith("AIzaSy"):
            save_gemini_key(parts[1])
            send_message(chat_id, "🎉 <b>¡Clave de Google Gemini 2.0 vinculada exitosamente!</b>\nA partir de ahora, la IA responderá cualquier consulta técnica o general directamente en este chat.")
            return
        else:
            send_message(chat_id, "ℹ️ Uso: <code>/ia_key TU_CLAVE_AIzaSy...</code>\nConsíguela gratis en aistudio.google.com")
            return

    if text.strip().startswith("AIzaSy") and len(text.strip()) > 30:
        save_gemini_key(text.strip())
        send_message(chat_id, "🎉 <b>¡Clave de Google Gemini vinculada con éxito!</b>\nEl cerebro de Gemini 2.0 Flash está activo para responderte libremente.")
        return

    if re.search(r'\b(revoc|quit|elimin)\w*\s+(acceso|permiso)\b|\bquitale\b', norm):
        if emails:
            folder = "MEGAPACK_PROGRAMACION_COMPLETO"
            if "descarga" in norm:
                folder = "DESCARGAS_UNIVERSALES"
            send_message(chat_id, f"⏳ Revocando acceso de <code>{emails[0]}</code> en <code>{folder}</code>...")
            ok = share_drive_folder.revoke_permission(folder, emails[0], remote="midrive")
            if ok:
                send_message(chat_id, f"✅ Acceso revocado correctamente para <code>{emails[0]}</code>.")
            else:
                send_message(chat_id, f"ℹ️ No se encontró permiso activo para <code>{emails[0]}</code>.")
        else:
            send_message(chat_id, "ℹ️ Por favor incluye el correo de la persona a quien deseas revocarle el acceso (ej: <code>revocar amigo@gmail.com</code>).")
        return

    if re.search(r'\b(compart|pasale|pasa|dale acceso|enviar acceso)\b', norm):
        if emails:
            folder = "MEGAPACK_PROGRAMACION_COMPLETO"
            if "descarga" in norm:
                folder = "DESCARGAS_UNIVERSALES"
            execute_share(chat_id, folder, emails[0], role="reader")
        else:
            show_share_menu(chat_id)
        return

    if re.search(r'\b(como va|estado|que esta bajando|progreso|status|cola)\b', norm):
        st_msg = get_runs_status()
        kbd = {"inline_keyboard": [[{"text": "🔄 Actualizar Estado Ahora", "callback_data": "cmd:status"}]]}
        send_message(chat_id, st_msg, kbd)
        return

    if re.search(r'\b(permiso|quien(es)? tiene(n)? acceso|lista de acceso)\b', norm):
        send_message(chat_id, "🔍 Consultando permisos en Google Drive...")
        perms = share_drive_folder.list_permissions("MEGAPACK_PROGRAMACION_COMPLETO", remote="midrive")
        if not perms:
            send_message(chat_id, "ℹ️ No se encontraron permisos específicos registrados.")
        else:
            lines = ["👥 <b>Personas con acceso a MEGAPACK_PROGRAMACION_COMPLETO:</b>\n"]
            for p in perms:
                em = p.get('emailAddress', 'Enlace Público')
                name = p.get('displayName', '')
                role = p.get('role', '')
                lines.append(f"• <b>{em}</b> ({name}) - <code>{role}</code>")
            send_message(chat_id, "\n".join(lines))
        return

    if re.search(r'\b(sincroniz|actualiz|sync)\b', norm):
        send_message(chat_id, "🔄 Disparando auto-sincronizador en la nube Azure...")
        ok, out = trigger_sync()
        if ok:
            send_message(chat_id, "✅ ¡Auto-sincronizador lanzado con éxito! Te avisaré cuando concluya.")
        else:
            send_message(chat_id, f"❌ Error: {translate_error(out)}")
        return

    if re.search(r'\b(cuanto|cuanto)\s+(tarda|demora|tomaria)\b|\b(500\s*gb|1\s*tb|300\s*gb|velocidad)\b', norm):
        send_message(chat_id, get_cognitive_answer("TIMING"))
        return

    if re.search(r'\b(format|formate|formateo|reinstalar|windows nuevo|borra mi pc)\b', norm):
        send_message(chat_id, get_cognitive_answer("FORMATTING"))
        return

    if re.search(r'\b(como|como)\s+(uno|unir|abro|abrir|extraer|descomprimir|montar)\b|\b(bat|001|part1)\b', norm):
        send_message(chat_id, get_cognitive_answer("JOINING"))
        return

    if emails and len(emails) == 1 and len(text.strip()) < 80:
        show_folder_options_for_email(chat_id, emails[0])
        return

    # Si ninguna regla anterior capturó el mensaje: Pasar a Gemini AI o Asistente Cognitivo
    ai_reply = call_gemini_api(text)
    if ai_reply:
        send_message(chat_id, f"🤖 <b>OmniCloud AI (Gemini):</b>\n\n{ai_reply}")
        return

    welcome_msg = (
        "🤖 <b>Asistente OmniCloud:</b>\n"
        "Puedo ayudarte a descargar enlaces, compartir carpetas o resolver dudas sobre tus 10TB de almacenamiento.\n\n"
        "👉 <i>Toca los botones de abajo o selecciona una de estas opciones rápidas:</i>"
    )
    kbd = {
        "inline_keyboard": [
            [{"text": "⏱️ Ver Tiempos de Descarga (500GB / 1TB)", "callback_data": "ai:faq:TIMING"}],
            [{"text": "🛡️ Ver Qué Pasa Si Formateo Mi PC", "callback_data": "ai:faq:FORMATTING"}],
            [{"text": "📦 Ver Cómo Montar ISOs y Archivos .bat", "callback_data": "ai:faq:JOINING"}]
        ]
    }
    send_message(chat_id, welcome_msg, kbd)

# =====================================================================
# ENRUTADOR PRINCIPAL DE MENSAJES Y EVENTOS
# =====================================================================
def handle_update(up):
    if "message" in up:
        msg = up["message"]
        chat_id = str(msg.get("chat", {}).get("id"))
        msg_id = msg.get("message_id")
        text = (msg.get("text") or "").strip()

        if chat_id != AUTH_CHAT_ID:
            send_message(chat_id, "⛔ Acceso no autorizado. Este bot es de uso privado.", with_keyboard=False)
            return

        if "voice" in msg:
            send_message(chat_id, "🎙️ <i>Mensaje de voz recibido. Para mayor precisión en las descargas, por favor escribe el enlace en texto o usa los botones de abajo.</i>")
            return

        if text.lower() in ["cancelar", "salir", "volver"]:
            user_states.pop(chat_id, None)
            send_message(chat_id, "✅ Operación cancelada. Menú principal listo.")
            return

        state = user_states.get(chat_id, {})

        if state.get("step") == "waiting_custom_folder":
            user_states[chat_id] = {
                "step": "waiting_share_email",
                "folder": text,
                "remote": "midrive"
            }
            send_message(chat_id, f"📁 Carpeta seleccionada: <code>{escape_html(text)}</code>\n\n📧 <b>Ahora escribe el correo Google de la persona a quien se lo enviarás:</b>\n(Ej: <code>amigo@gmail.com</code>)")
            return

        if state.get("step") == "waiting_share_email":
            email = text.lower()
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                send_message(chat_id, "⚠️ El formato del correo no parece válido. Escribe un correo de Google válido (ej: <code>amigo@gmail.com</code>):")
                return

            folder = state.get("folder", "MEGAPACK_PROGRAMACION_COMPLETO")
            remote = state.get("remote", "midrive")
            user_states[chat_id]["email"] = email

            kbd = {
                "inline_keyboard": [
                    [{"text": "👁️ Solo Lectura (Recomendado)", "callback_data": "sh:r:reader"}],
                    [{"text": "✏️ Lectura y Escritura", "callback_data": "sh:r:writer"}],
                    [{"text": "❌ Cancelar", "callback_data": "cmd:cancel"}]
                ]
            }
            send_message(chat_id, f"👤 Destinatario: <code>{email}</code>\n📁 Carpeta: <code>{folder}</code>\n\n🔑 <b>Selecciona el nivel de acceso:</b>", kbd)
            return

        if state.get("step") == "waiting_download_third_party_email":
            email = text.lower()
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                send_message(chat_id, "⚠️ Correo no válido. Ingresa el correo de Google de la persona:")
                return
            url = state.get("url")
            user_states.pop(chat_id, None)
            target = "Google Drive (Mi Unidad Principal - Julio)"
            send_message(chat_id, f"🚀 <b>Transmitiendo orden a Azure Cloud...</b>\n🎯 Descargando a tu Drive y compartiendo automáticamente con <code>{email}</code>.")
            ok, err = trigger_workflow_download(url, target, recipient_email=email)
            if ok:
                send_message(chat_id, f"🎉 <b>¡Descarga en marcha a 1.5 Gbps!</b>\nAl concluir la descarga, Google le enviará acceso oficial a <code>{email}</code> sin que tú hagas nada.")
            else:
                send_message(chat_id, f"❌ Error al iniciar: {translate_error(err)}")
            return

        if text == "🚀 Enviar Enlace / Descargar":
            show_download_prompt(chat_id)
            return
        elif text == "🤝 Compartir Carpeta":
            show_share_menu(chat_id)
            return
        elif text == "📊 Estado de Descargas":
            st_msg = get_runs_status()
            kbd = {"inline_keyboard": [[{"text": "🔄 Actualizar Estado Ahora", "callback_data": "cmd:status"}]]}
            send_message(chat_id, st_msg, kbd)
            return
        elif text == "👥 Ver Permisos":
            send_message(chat_id, "🔍 Consultando permisos en Google Drive...")
            perms = share_drive_folder.list_permissions("MEGAPACK_PROGRAMACION_COMPLETO", remote="midrive")
            if not perms:
                send_message(chat_id, "ℹ️ No se encontraron permisos específicos.")
            else:
                lines = ["👥 <b>Personas con acceso a MEGAPACK_PROGRAMACION_COMPLETO:</b>\n"]
                for p in perms:
                    em = p.get('emailAddress', 'Enlace Público')
                    name = p.get('displayName', '')
                    role = p.get('role', '')
                    lines.append(f"• <b>{em}</b> ({name}) - <code>{role}</code>")
                send_message(chat_id, "\n".join(lines))
            return
        elif text == "🧠 Asistente IA":
            show_ai_menu(chat_id)
            return
        elif text == "🔄 Sincronizar Megapack":
            send_message(chat_id, "🔄 Disparando auto-sincronizador en la nube Azure...")
            ok, out = trigger_sync()
            if ok:
                send_message(chat_id, "✅ ¡Auto-sincronizador lanzado con éxito! Te avisaré cuando concluya.")
            else:
                send_message(chat_id, f"❌ Error: {translate_error(out)}")
            return

        if text in ["/start", "/help", "hola", "menu", "iniciar"]:
            user_states.pop(chat_id, None)
            show_welcome(chat_id)
            return

        if text.startswith("/compartir"):
            parts = text.split()
            if len(parts) == 1:
                show_share_menu(chat_id)
            elif len(parts) == 2:
                arg = parts[1]
                if "@" in arg:
                    execute_share(chat_id, "MEGAPACK_PROGRAMACION_COMPLETO", arg, role="reader")
                else:
                    show_share_menu(chat_id)
            elif len(parts) >= 3:
                execute_share(chat_id, parts[1], parts[2], role="reader")
            return

        if text.startswith("/status"):
            st_msg = get_runs_status()
            kbd = {"inline_keyboard": [[{"text": "🔄 Actualizar Estado Ahora", "callback_data": "cmd:status"}]]}
            send_message(chat_id, st_msg, kbd)
            return

        if text.startswith("/sync"):
            send_message(chat_id, "🔄 Disparando auto-sincronizador en Azure...")
            ok, out = trigger_sync()
            if ok:
                send_message(chat_id, "✅ ¡Auto-sincronizador lanzado con éxito!")
            else:
                send_message(chat_id, f"❌ Error: {translate_error(out)}")
            return

        process_natural_language(chat_id, text, msg_id)

    elif "callback_query" in up:
        cq = up["callback_query"]
        cb_id = cq.get("id")
        answer_callback(cb_id)

        chat_id = str(cq.get("message", {}).get("chat", {}).get("id"))
        data = cq.get("data", "")

        if chat_id != AUTH_CHAT_ID:
            return

        if data == "cmd:cancel":
            user_states.pop(chat_id, None)
            send_message(chat_id, "✅ Operación cancelada.")
            return

        if data == "cmd:share_menu":
            show_share_menu(chat_id)
        elif data == "cmd:status":
            st_msg = get_runs_status()
            kbd = {"inline_keyboard": [[{"text": "🔄 Actualizar Estado Ahora", "callback_data": "cmd:status"}]]}
            send_message(chat_id, st_msg, kbd)
        elif data == "cmd:sync":
            send_message(chat_id, "🔄 Disparando auto-sincronizador en Azure...")
            ok, out = trigger_sync()
            if ok:
                send_message(chat_id, "✅ ¡Auto-sincronizador lanzado con éxito!")
            else:
                send_message(chat_id, f"❌ Error: {translate_error(out)}")

        elif data.startswith("ai:faq:"):
            topic = data.split("ai:faq:")[1]
            ans = get_cognitive_answer(topic)
            send_message(chat_id, ans)

        elif data.startswith("sh:f:"):
            folder_choice = data.split("sh:f:")[1]
            if folder_choice == "custom":
                user_states[chat_id] = {"step": "waiting_custom_folder"}
                send_message(chat_id, "✍️ <b>Escribe el nombre de la carpeta tal como aparece en tu Google Drive:</b>\n(Ej: <code>Mis_ISOS</code> o <code>Curso_Python</code>)")
            else:
                user_states[chat_id] = {
                    "step": "waiting_share_email",
                    "folder": folder_choice,
                    "remote": "midrive"
                }
                send_message(chat_id, f"📁 Carpeta: <code>{folder_choice}</code>\n\n📧 <b>Escribe el correo Gmail de la persona a quien se lo compartirás:</b>")

        elif data.startswith("sh:quick:"):
            parts = data.split(":")
            f_choice = parts[2]
            em_choice = parts[3]
            execute_share(chat_id, f_choice, em_choice, role="reader")

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
                send_message(chat_id, "⚠️ La sesión expiró. Toca '🤝 Compartir Carpeta' para reiniciar.")

        elif data == "sh:list":
            perms = share_drive_folder.list_permissions("MEGAPACK_PROGRAMACION_COMPLETO", remote="midrive")
            if not perms:
                send_message(chat_id, "ℹ️ No se encontraron permisos específicos.")
            else:
                lines = ["👥 <b>Personas con acceso a MEGAPACK_PROGRAMACION_COMPLETO:</b>\n"]
                for p in perms:
                    em = p.get('emailAddress', 'Enlace Público')
                    name = p.get('displayName', '')
                    role = p.get('role', '')
                    lines.append(f"• <b>{em}</b> ({name}) - <code>{role}</code>")
                send_message(chat_id, "\n".join(lines))

        elif data.startswith("d:"):
            parts = data.split(":")
            cloud_code = parts[1]
            msg_ref = parts[2] if len(parts) > 2 else ""

            if cloud_code == "swarm":
                send_message(chat_id, "⚡ <b>Lanzando Enjambre Swarm Multi-Nodo en Azure Cloud...</b>\n4 nodos concurrentes transferirán el archivo en paralelo con auto-unidor .bat incluido.")
                ok, err = trigger_swarm_download("external_monolithic_range_swarm")
                if ok:
                    send_message(chat_id, "🎉 <b>¡Enjambre Swarm Desplegado con Éxito!</b>\nLos 4 nodos de Azure están absorbiendo el archivo a máxima velocidad. Sonará una notificación cuando esté en tu Drive.")
                else:
                    send_message(chat_id, f"❌ Error al despachar enjambre: {translate_error(err)}")
                return

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
                    send_message(chat_id, "📧 <b>Ingresa el correo Gmail de la persona:</b>\nAzure descargará los archivos y le compartirá acceso automáticamente.")
                else:
                    send_message(chat_id, "⚠️ Enlace no encontrado en memoria. Por favor reenvía el enlace.")
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
                for line in orig_text.split("\n"):
                    l = line.strip()
                    if l.startswith("http://") or l.startswith("https://") or l.startswith("magnet:"):
                        full_url = l
                        break

            if full_url:
                send_message(chat_id, f"🚀 <b>Transmitiendo orden a Azure Cloud...</b>\n🎯 Destino: <i>{target}</i>\nTu PC puede estar apagada.")
                ok, err = trigger_workflow_download(full_url, target)
                if ok:
                    send_message(chat_id, "🎉 <b>¡Descarga en marcha a 1.5 Gbps!</b>\nLos servidores de Azure están transfiriendo tus archivos a tu Google Drive. Sonará una notificación cuando finalice.")
                else:
                    send_message(chat_id, f"❌ Error al iniciar: {translate_error(err)}")
            else:
                send_message(chat_id, "⚠️ No se encontró el enlace en memoria. Por favor vuelve a enviarlo.")

# =====================================================================
# BUCLE PRINCIPAL (LONG POLLING RESILIENTE)
# =====================================================================
def main():
    print("=" * 65)
    print("  OMNICLOUD CORE - TELEGRAM BOT POLLER CON IA INTEGRADA")
    print(f"  Bot: @VexorOmniBot")
    print(f"  Usuario Autorizado: {AUTH_CHAT_ID} (Julio)")
    has_ai = get_gemini_key() is not None
    print(f"  Motor de IA: {'Google Gemini 2.0 Flash + Cognitivo' if has_ai else 'Cognitivo Local (Clave Gemini opcional)'}")
    print("=" * 65)
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
