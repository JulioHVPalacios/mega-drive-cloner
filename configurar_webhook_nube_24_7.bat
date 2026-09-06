@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Configurar Webhook 24/7 en Cloudflare (PC Apagada)

cls
echo =====================================================================
echo   CONFIGURADOR DE WEBHOOK CLOUD 24/7 (OMNICLOUD BOT)
echo =====================================================================
echo  Este script vincula tu bot de Telegram a tu Cloudflare Worker
echo  para que funcione PERPETUAMENTE con tu PC 100%% APAGADA.
echo =====================================================================
echo.

set "BOT_TOKEN=8775957501:AAEF5W3TgWUku6pMCqdFN9ouFpxMG4BJ7MI"

set /p WORKER_URL="Pega aqui la URL de tu Cloudflare Worker (ej: https://omnicloud-bot.tu-subdominio.workers.dev): "

if "!WORKER_URL!"=="" (
    echo [!] No ingresaste ninguna URL. Operacion cancelada.
    pause
    exit /b 1
)

echo.
echo Vinculando Webhook con Telegram...
powershell -Command "$resp = Invoke-RestMethod -Uri 'https://api.telegram.org/bot%BOT_TOKEN%/setWebhook?url=%WORKER_URL%'; Write-Host 'Respuesta de Telegram:' ($resp | ConvertTo-Json)"

echo.
echo =====================================================================
echo  ¡WEBHOOK ACTIVADO CON EXITO!
echo  A partir de ahora, tu bot responde desde la nube de Cloudflare
echo  las 24 horas del dia, aunque tu PC este completamente apagada.
echo =====================================================================
pause
