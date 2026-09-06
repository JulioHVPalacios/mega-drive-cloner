@echo off
chcp 65001 > nul
title Desactivar Webhook y Regresar a Modo Local (PC Encendida)

cls
echo =====================================================================
echo   DESACTIVADOR DE WEBHOOK (MODO LOCAL)
echo =====================================================================
echo  Este script elimina el webhook de la nube para permitir que el
echo  bot corra directamente desde tu computadora (bot_telegram_local.py).
echo =====================================================================
echo.

set "BOT_TOKEN=8775957501:AAEF5W3TgWUku6pMCqdFN9ouFpxMG4BJ7MI"

echo Eliminando Webhook de Telegram...
powershell -Command "$resp = Invoke-RestMethod -Uri 'https://api.telegram.org/bot%BOT_TOKEN%/deleteWebhook'; Write-Host 'Respuesta de Telegram:' ($resp | ConvertTo-Json)"

echo.
echo =====================================================================
echo  ¡MODO LOCAL HABILITADO!
echo  Ahora puedes ejecutar 'iniciar_bot_telegram_pc.bat'.
echo =====================================================================
pause
