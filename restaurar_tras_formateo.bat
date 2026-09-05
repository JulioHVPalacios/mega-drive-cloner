@echo off
chcp 65001 > nul
title Restaurador Post-Formateo - Mega Drive Cloner
echo =====================================================================
echo 🔄 RESTAURADOR RÁPIDO TRAS FORMATEO (1 CLIC)
echo =====================================================================
echo Este instalador deja tu PC lista en 30 segundos si acabas de formatear.
echo.

where rclone >nul 2>nul
if %errorlevel% neq 0 (
    echo [1/2] Rclone no detectado. Descargando e instalando versión oficial...
    winget install Rclone.Rclone --accept-source-agreements --accept-package-agreements >nul 2>nul
    if %errorlevel% neq 0 (
        echo Intentando instalación directa portátil...
        powershell -Command "Invoke-WebRequest -Uri 'https://downloads.rclone.org/rclone-current-windows-amd64.zip' -OutFile '%TEMP%\rclone.zip'; Expand-Archive -Path '%TEMP%\rclone.zip' -DestinationPath '%TEMP%\rclone_extracted' -Force; Move-Item (Get-ChildItem '%TEMP%\rclone_extracted\rclone*' | Select-Object -First 1).FullName '%~dp0rclone_portable' -Force"
    )
    echo ✅ Rclone instalado correctamente.
) else (
    echo ✅ Rclone ya está instalado en tu sistema.
)

where gh >nul 2>nul
if %errorlevel% neq 0 (
    echo [2/2] GitHub CLI no detectado. Instalando...
    winget install GitHub.cli --accept-source-agreements --accept-package-agreements >nul 2>nul
    echo ✅ GitHub CLI instalado. Abre una nueva consola y ejecuta: gh auth login
) else (
    echo ✅ GitHub CLI ya está disponible.
)

echo.
echo =====================================================================
echo 🎉 ¡TODO RESTAURADO Y LISTO!
echo Recuerda: Tu Descargador Universal sigue funcionando 24/7 en la nube
echo entrando a: https://github.com/JulioHVPalacios/mega-drive-cloner/actions
echo =====================================================================
pause
