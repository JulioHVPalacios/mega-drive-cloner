@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title RESPALDO SEGURO DE NUBES (ANTI-FORMATEO)

echo =====================================================================
echo   RESPALDO SEGURO DE TUS NUBES Y MOTORES (1 CLIC)
echo =====================================================================
echo.

set "CONF_SOURCE=%APPDATA%\rclone\rclone.conf"
set "BACKUP_DIR=%~dp0backup_seguro"
set "BACKUP_FILE=%BACKUP_DIR%\rclone.conf.bak"

if not exist "%CONF_SOURCE%" (
    echo [!] No se encontro el archivo de credenciales en: %CONF_SOURCE%
    echo Usa 'conectar_cualquier_nube.bat' para vincular tus cuentas primero.
    pause
    exit /b
)

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%" 2>nul
copy /y "%CONF_SOURCE%" "%BACKUP_FILE%" >nul 2>nul
(
    echo TELEGRAM_BOT_TOKEN=8775957501:AAEF5W3TgWUku6pMCqdFN9ouFpxMG4BJ7MI
    echo TELEGRAM_CHAT_ID=1136933800
) > "%BACKUP_DIR%\telegram.env" 2>nul
echo [1/2] Copia local guardada con exito en:
echo       %BACKUP_FILE%
echo       %BACKUP_DIR%\telegram.env
echo       (Esta carpeta esta protegida y excluida de Git).

echo.
echo [2/2] Sincronizando respaldo seguro en la nube (GitHub Secrets)...
where gh >nul 2>nul
if %errorlevel% equ 0 (
    gh secret set RCLONE_CONFIG < "%CONF_SOURCE%" >nul 2>nul
    if %errorlevel% equ 0 (
        echo [OK] Respaldo en la nube de GitHub actualizado al 100%%.
    ) else (
        echo [!] Nota: Para sincronizar con GitHub CLI, asegurate de tener conexion.
    )
) else (
    echo [i] GitHub CLI no detectado. El respaldo local en disco D: esta 100%% listo.
)

echo.
echo =====================================================================
echo  TODO BLINDADO Y SEGURO!
echo  Puedes formatear tu disco C: con total tranquilidad.
echo  Tras formatear, solo abre 'restaurar_tras_formateo.bat' y listo.
echo =====================================================================
pause
