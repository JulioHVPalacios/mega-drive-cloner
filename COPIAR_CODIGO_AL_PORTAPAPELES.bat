@echo off
chcp 65001 > nul
type %~dp0telegram_bot_worker.js | clip
echo [OK] Codigo copiado al portapapeles. Pega con Ctrl + V en Cloudflare.
timeout /t 3 > nul
