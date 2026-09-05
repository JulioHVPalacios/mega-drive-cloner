@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title OmniCloud Core - Telegram Bot Local Poller

cls
echo =====================================================================
echo   OMNICLOUD CORE - TELEGRAM BOT POLING (MODO LOCAL)
echo =====================================================================
echo.
echo   Bot Oficial: @VexorOmniBot
echo   Usuario Vinculado: Julio (ID: 1136933800)
echo   Servidores: Azure Cloud (PC Apagada) + Google Drive 10TB
echo.
echo   El bot esta escuchando en tiempo real.
echo   Puedes enviar enlaces o usar botones desde tu celular.
echo.
echo   [Para detener el bot, presiona Ctrl + C]
echo =====================================================================
echo.

python bot_telegram_local.py
pause
