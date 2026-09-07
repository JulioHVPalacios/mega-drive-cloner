# -*- coding: utf-8 -*-
"""
UNIVERSAL WATCHDOG & SYNCHRONIZER (Desatendido 24/7 en Azure)
Monitorea todas las carpetas compartidas registradas en sync_registry.json,
detecta novedades subidas por los creadores originales y las descarga
en modo estrictamente ADITIVO (CERO BORRADOS) a tu Google Drive.
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import time
import argparse
import subprocess
import urllib.request
import urllib.parse

TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8775957501:AAGPitEyFmfa1aeFGZtKcCwsfbFSyDxQ35A")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1136933800")

def notify_telegram(message_html):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("ℹ️ Telegram credentials no configuradas. Omitiendo notificación.")
        return False
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TG_CHAT_ID,
        "text": message_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"⚠️ Error al enviar alerta a Telegram: {e}")
        return False

def run_watchdog(registry_path="sync_registry.json", target_id="all", dry_run=False, dest_override=None):
    if not os.path.exists(registry_path):
        print(f"❌ Error: No se encontró el registro en {registry_path}")
        sys.exit(1)

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    folders = registry.get("monitored_folders", [])
    if not folders:
        print("ℹ️ No hay carpetas registradas en el watchdog.")
        return

    diffs_dir = "/tmp/diffs" if os.name != "nt" else os.path.join(os.environ.get("TEMP", "C:\\Temp"), "diffs")
    os.makedirs(diffs_dir, exist_ok=True)

    results = []
    total_new_files = 0

    print("=" * 70)
    print("🛰️ INICIANDO UNIVERSAL WATCHDOG & SYNCHRONIZER 24/7")
    print(f"📁 Registro: {registry_path} | Objetivo: {target_id} | Dry-run: {dry_run}")
    print("=" * 70)

    for item in folders:
        f_id = item.get("id")
        f_name = item.get("name", f_id)
        source_id = item.get("source_id", "").strip()
        dest_folder = item.get("dest_folder", "").strip()
        dest_remote = dest_override or item.get("dest_remote", "midrive")
        is_active = item.get("active", True)

        if target_id != "all" and f_id != target_id:
            continue

        if not is_active:
            print(f"\n⏸️ Omitiendo carpeta inactiva: {f_name}")
            results.append({"name": f_name, "status": "⏸️ Inactiva", "new": 0})
            continue

        if not source_id:
            print(f"\n⚠️ Falta source_id para: {f_name}")
            results.append({"name": f_name, "status": "⚠️ Sin ID origen", "new": 0})
            continue

        src = f"midrive,root_folder_id={source_id}:"
        dst = f"{dest_remote}:{dest_folder}"
        diff_file = os.path.join(diffs_dir, f"{f_id}_nuevos.txt")

        if os.path.exists(diff_file):
            try:
                os.remove(diff_file)
            except Exception:
                pass

        print(f"\n🔍 [1/2] Verificando novedades en: {f_name}")
        print(f"   Origen:  {src}")
        print(f"   Destino: {dst}")

        check_cmd = [
            "rclone", "check",
            src, dst,
            "--one-way",
            "--missing-on-dst", diff_file,
            "--fast-list"
        ]

        try:
            # rclone check retorna exit code 1 si hay diferencias, no es un error de ejecución
            subprocess.run(check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"   ❌ Error al ejecutar rclone check: {e}")
            results.append({"name": f_name, "status": "❌ Error check", "new": 0})
            continue

        new_count = 0
        if os.path.exists(diff_file) and os.path.getsize(diff_file) > 0:
            with open(diff_file, "r", encoding="utf-8", errors="ignore") as df:
                lines = [l.strip() for l in df.readlines() if l.strip()]
                new_count = len(lines)

        if new_count == 0:
            print(f"   ✅ 100% al día. No hay archivos nuevos subidos por el creador.")
            results.append({"name": f_name, "status": "✅ 100% al día", "new": 0})
            continue

        total_new_files += new_count
        print(f"   ⚡ ¡Se detectaron {new_count} archivos/carpetas NUEVOS en el origen!")
        with open(diff_file, "r", encoding="utf-8", errors="ignore") as df:
            for idx, line in enumerate(df):
                if idx < 10:
                    print(f"      + {line.strip()}")
                elif idx == 10:
                    print(f"      ... y {new_count - 10} archivos más.")
                    break

        if dry_run:
            print("   ℹ️ Modo dry-run activo. No se copiarán archivos.")
            results.append({"name": f_name, "status": f"🔍 {new_count} detectados (Dry-Run)", "new": new_count})
            continue

        print(f"   🚀 [2/2] Sincronizando en modo ESTRICTAMENTE ADITIVO (Cero borrados)...")
        copy_cmd = [
            "rclone", "copy",
            src, dst,
            "--fast-list",
            "--update",
            "--checksum",
            "--transfers=12",
            "--checkers=24",
            "--buffer-size=64M",
            "--use-mmap",
            "--drive-chunk-size=128M",
            "--drive-server-side-across-configs=true",
            "--retries=10",
            "--low-level-retries=20",
            "-v", "-P",
            "--stats", "15s"
        ]

        t_start = time.time()
        try:
            res = subprocess.run(copy_cmd, check=True)
            elapsed = time.time() - t_start
            print(f"   🎉 ¡Sincronizado con éxito en {elapsed:.1f}s! ({new_count} archivos transferidos)")
            results.append({"name": f_name, "status": f"🎉 +{new_count} nuevos sincronizados", "new": new_count})
        except subprocess.CalledProcessError as cpe:
            print(f"   ❌ Fallo durante la copia: {cpe}")
            results.append({"name": f_name, "status": "❌ Error en copia", "new": 0})

    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL DEL WATCHDOG:")
    print("=" * 70)
    for r in results:
        print(f"• {r['name']}: {r['status']}")
    print("=" * 70)

    # Notificación inteligente a Telegram
    # Solo envía push si hubo novedades o si se ejecutó manualmente para una carpeta específica
    if total_new_files > 0 or target_id != "all":
        lines = [
            "🛰️ <b>UNIVERSAL WATCHDOG &amp; SYNC - REPORTE 24/7</b>\n",
            f"🎯 <b>Novedades detectadas:</b> {total_new_files} archivos.\n",
            "📋 <b>Detalle por carpeta monitoreada:</b>"
        ]
        for r in results:
            lines.append(f"• <b>{r['name']}</b>: {r['status']}")

        lines.append("\n🛡️ <i>Modo estrictamente aditivo: CERO borrados en tu Google Drive.</i>")
        lines.append("⚡ <i>Monitoreo continuo en Azure con tu PC apagada.</i>")

        msg = "\n".join(lines)
        notify_telegram(msg)
        print("🔔 Notificación enviada a Telegram.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Watchdog & Synchronizer")
    parser.add_argument("--registry", default="sync_registry.json", help="Ruta al archivo sync_registry.json")
    parser.add_argument("--target", default="all", help="ID de la carpeta específica a sincronizar o 'all'")
    parser.add_argument("--dry-run", action="store_true", help="Solo auditar diferencias sin copiar")
    parser.add_argument("--dest", default=None, help="Sobrescribir unidad de destino (ej. midrive o midrive2)")
    args = parser.parse_args()

    run_watchdog(
        registry_path=args.registry,
        target_id=args.target,
        dry_run=args.dry_run,
        dest_override=args.dest
    )
