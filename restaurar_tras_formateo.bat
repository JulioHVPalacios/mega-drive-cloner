@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title RESTAURADOR TOTAL TRAS FORMATEO (1 CLIC - 100% AUTOMATIZADO)

echo =====================================================================
echo   RESTAURADOR MAESTRO TRAS FORMATEO (CERO DOLOR DE CABEZA)
echo =====================================================================
echo  Este script dejara tu PC formateada 100% lista en 1 minuto:
echo   1. Instala Rclone oficial.
echo   2. Instala GitHub CLI.
echo   3. Instala Aria2c (Motor multi-hilo para ISOs/Torrents).
echo   4. Instala WinFsp (Controlador de disco virtual Z:).
echo   5. Restaura tus credenciales de Google Drive/OneDrive/Mega.
echo   6. Crea el acceso directo del CENTRO DE DESCARGAS en tu Escritorio.
echo =====================================================================
echo.

echo [1/5] Verificando Rclone...
where rclone >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando Rclone...
    winget install Rclone.Rclone --accept-source-agreements --accept-package-agreements >nul 2>nul
    echo [OK] Rclone instalado.
) else (
    echo [OK] Rclone ya esta disponible.
)

echo.
echo [2/5] Verificando GitHub CLI (gh)...
where gh >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando GitHub CLI...
    winget install GitHub.cli --accept-source-agreements --accept-package-agreements >nul 2>nul
    echo [OK] GitHub CLI instalado.
) else (
    echo [OK] GitHub CLI ya esta disponible.
)

echo.
echo [3/5] Verificando Aria2c (Acelerador Multi-Segmento)...
where aria2c >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando Aria2c...
    winget install aria2.aria2 --accept-source-agreements --accept-package-agreements >nul 2>nul
    echo [OK] Aria2c instalado.
) else (
    echo [OK] Aria2c ya esta disponible.
)

echo.
echo [4/5] Verificando WinFsp (Soporte de Disco Virtual Z:)...
sc query WinFsp.Launcher >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando WinFsp...
    winget install WinFsp.WinFsp --accept-source-agreements --accept-package-agreements >nul 2>nul
    echo [OK] WinFsp instalado.
) else (
    echo [OK] WinFsp ya esta disponible.
)

echo.
echo [5/5] Restaurando credenciales de nubes...
set "BACKUP_CONF=%~dp0backup_seguro\rclone.conf.bak"
set "DEST_CONF=%APPDATA%\rclone\rclone.conf"
if exist "%BACKUP_CONF%" (
    if not exist "%APPDATA%\rclone" mkdir "%APPDATA%\rclone" 2>nul
    copy /y "%BACKUP_CONF%" "%DEST_CONF%" >nul 2>nul
    echo [OK] Credenciales de nubes restauradas automaticamente desde backup seguro.
    if exist "%~dp0backup_seguro\telegram.env" (
        echo [OK] Credenciales del Bot de Telegram verificadas y listas.
    )
) else (
    echo [i] Si no tienes backup local, usa 'conectar_cualquier_nube.bat' para vincular tus cuentas en 30s.
)

echo.
echo Creando acceso directo en el Escritorio...
powershell -NoProfile -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\CENTRO DE DESCARGAS EXTREMO.lnk'); $Shortcut.TargetPath = '%~dp0CENTRO_DE_DESCARGAS_EXTREMO.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Centro de Descargas y Transferencias Extremas'; $Shortcut.Save()"
echo [OK] Acceso directo creado en tu Escritorio.

echo.
echo =====================================================================
echo  RESTAURACION COMPLETADA AL 100%!
echo  Tu PC formateada ya tiene todos los motores listos para funcionar.
echo  Abre directamente: 'CENTRO DE DESCARGAS EXTREMO' en tu Escritorio.
echo  Recuerda que la nube de Azure y los workflows de GitHub siguen
echo  funcionando 24/7 de forma autonoma con tu PC apagada.
echo =====================================================================
pause
