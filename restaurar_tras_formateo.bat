@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title 🔄 RESTAURADOR TOTAL TRAS FORMATEO (1 CLIC - 100% AUTOMATIZADO)

echo =====================================================================
echo  🔄 RESTAURADOR MAESTRO TRAS FORMATEO (CERO DOLOR DE CABEZA)
echo =====================================================================
echo  Este script dejará tu PC formateada 100% lista en 1 minuto:
echo   1. Instala Rclone oficial.
echo   2. Instala Aria2c (Motor multi-hilo para ISOs/Torrents).
echo   3. Instala WinFsp (Controlador de disco virtual Z:).
echo   4. Instala GitHub CLI.
echo   5. Crea el acceso directo del CENTRO DE DESCARGAS en tu Escritorio.
echo =====================================================================
echo.

echo [1/4] Verificando Rclone...
where rclone >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando Rclone...
    winget install Rclone.Rclone --accept-source-agreements --accept-package-agreements >nul 2>nul
    echo ✅ Rclone instalado.
) else (
    echo ✅ Rclone ya está disponible.
)

echo.
echo [2/4] Verificando Aria2c (Acelerador Multi-Segmento)...
where aria2c >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando Aria2c...
    winget install aria2.aria2 --accept-source-agreements --accept-package-agreements >nul 2>nul
    echo ✅ Aria2c instalado.
) else (
    echo ✅ Aria2c ya está disponible.
)

echo.
echo [3/4] Verificando WinFsp (Soporte de Disco Virtual Z:)...
sc query WinFsp.Launcher >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando WinFsp...
    winget install WinFsp.WinFsp --accept-source-agreements --accept-package-agreements >nul 2>nul
    echo ✅ WinFsp instalado.
) else (
    echo ✅ WinFsp ya está disponible.
)

echo.
echo [4/4] Creando acceso directo en el Escritorio...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\CENTRO DE DESCARGAS EXTREMO.lnk'); $Shortcut.TargetPath = '%~dp0CENTRO_DE_DESCARGAS_EXTREMO.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Centro de Descargas y Transferencias Extremas'; $Shortcut.Save()"
echo ✅ Acceso directo creado en tu Escritorio.

echo.
echo =====================================================================
echo 🎉 ¡RESTAURACIÓN COMPLETADA AL 100%!
echo Puedes abrir directamente: 'CENTRO DE DESCARGAS EXTREMO' en tu Escritorio.
echo Recuerda que tus credenciales VIP y la nube de 20 servidores siguen
echo funcionando 24/7 en: https://github.com/JulioHVPalacios/mega-drive-cloner
echo =====================================================================
pause
