@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title CENTRO DE DESCARGAS Y TRANSFERENCIA EXTREMA - OMNICLOUD CORE

:MENU
cls
echo =====================================================================
echo   CENTRO DE TRANSFERENCIA Y DESCARGAS EXTREMAS
echo   (Aceleracion 32 Hilos - Discos Locales - Nube de Azure 24/7)
echo =====================================================================
echo.
echo  [1] Descargar CUALQUIER Enlace de Internet a tu PC (Aria2c 16 Hilos)
echo  [2] Descargar Carpeta Completa de Google Drive a tu PC o Disco Externo
echo  [3] Montar Google Drive como Disco Virtual Z: en Windows
echo  [4] Descargador Universal a la Nube (Cualquier Link - PC Apagada)
echo  [5] Enjambre Hydra en la Nube (20 Servidores Azure para Carpetas Gigantes)
echo  [6] Consultar Estado del Auto-Sincronizador Megapack (Watchdog 24/7)
echo  [7] Hacer Copia de Seguridad Segura (Antes de Formatear)
echo  [8] Restaurar Todo el Sistema tras Formateo (1 Clic en 30s)
echo  [0] Salir
echo.
echo =====================================================================
set "OPCION="
set /p "OPCION=Selecciona una opcion [0-8]: "

if not defined OPCION exit /b
if "%OPCION%"=="0" exit /b
if "%OPCION%"=="1" goto DESCARGA_UNIVERSAL_LOCAL
if "%OPCION%"=="2" goto CLONAR_DRIVE_A_LOCAL
if "%OPCION%"=="3" goto MONTAR_DRIVE
if "%OPCION%"=="4" goto DESCARGADOR_UNIVERSAL_CLOUD
if "%OPCION%"=="5" goto LANZAR_ENJAMBRE
if "%OPCION%"=="6" goto VERIFICAR_WATCHDOG
if "%OPCION%"=="7" goto BACKUP_SISTEMA
if "%OPCION%"=="8" goto RESTAURAR_SISTEMA
goto MENU

:DESCARGA_UNIVERSAL_LOCAL
cls
echo =====================================================================
echo  [1] DESCARGA UNIVERSAL A MAXIMA VELOCIDAD A TU DISCO LOCAL
echo =====================================================================
echo  Soporta: Torrents, Magnets, ISOs gigantes, Enlaces directos, Videos.
echo.
echo Estado actual de tus discos:
powershell -NoProfile -Command "Get-PSDrive -PSProvider FileSystem | ForEach-Object { [PSCustomObject]@{ 'Unidad' = $_.Name + ':'; 'Libre (GB)' = [math]::Round($_.Free / 1GB, 2); 'Total (GB)' = [math]::Round(($_.Used + $_.Free) / 1GB, 2) } } | Format-Table -AutoSize"
echo.

set /p "URL_ORIGEN=Pega aqui tu enlace (URL, Magnet o archivo .torrent): "
if "%URL_ORIGEN%"=="" goto MENU

echo.
echo En que disco deseas guardarlo? (Default: D:\Descargas)
set /p "RUTA_DESTINO=Escribe la ruta o letra de disco: "
if "%RUTA_DESTINO%"=="" set "RUTA_DESTINO=D:\Descargas"

if not exist "%RUTA_DESTINO%" mkdir "%RUTA_DESTINO%" 2>nul

where aria2c >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando acelerador Aria2c...
    winget install aria2.aria2 --accept-source-agreements --accept-package-agreements >nul 2>nul
)

echo.
echo Descargando a maxima velocidad con Aria2c...
aria2c "%URL_ORIGEN%" --dir="%RUTA_DESTINO%" --continue=true --file-allocation=falloc --enable-mmap=true --max-connection-per-server=16 --split=16 --min-split-size=1M --summary-interval=2 --max-overall-upload-limit=10K --bt-max-peers=100 --enable-dht=true --check-integrity=true --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

echo.
echo [OK] Descarga completada en: %RUTA_DESTINO%
pause
goto MENU

:CLONAR_DRIVE_A_LOCAL
cls
echo =====================================================================
echo  [2] CLONAR CARPETA DE GOOGLE DRIVE A DISCO LOCAL O EXTERNO
echo =====================================================================
echo.
echo Carpetas en tu Google Drive:
rclone lsd "midrive:"
echo.
set /p "CARPETA_DRIVE=Escribe el nombre exacto de la carpeta en Drive: "
if "%CARPETA_DRIVE%"=="" goto MENU

echo.
set /p "RUTA_LOCAL=Escribe la ruta local destino (ej: E:\Backup o D:\Descargas): "
if "%RUTA_LOCAL%"=="" set "RUTA_LOCAL=D:\Descargas\%CARPETA_DRIVE%"

echo.
echo Descargando con 16 hilos en paralelo...
rclone copy "midrive:%CARPETA_DRIVE%" "%RUTA_LOCAL%" --transfers=16 --checkers=32 --buffer-size=64M --use-mmap --fast-list -P -v
echo.
echo [OK] Copia completada en: %RUTA_LOCAL%
pause
goto MENU

:MONTAR_DRIVE
cls
echo =====================================================================
echo  [3] MONTAR GOOGLE DRIVE COMO DISCO VIRTUAL Z: EN WINDOWS
echo =====================================================================
echo.
sc query WinFsp.Launcher >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando WinFsp...
    winget install WinFsp.WinFsp --accept-source-agreements --accept-package-agreements >nul 2>nul
)

echo Montando Google Drive en unidad Z:...
start /b rclone mount midrive: Z: --vfs-cache-mode full --buffer-size=64M --dir-cache-time 72h --network-mode
timeout /t 3 >nul
explorer Z:
echo [OK] Unidad Z: montada con exito.
pause
goto MENU

:DESCARGADOR_UNIVERSAL_CLOUD
cls
echo =====================================================================
echo  [4] DESCARGADOR UNIVERSAL A LA NUBE (PC APAGADA)
echo =====================================================================
echo  Soporta: Torrents, Magnets, ISOs de foros, MEGA, YouTube/Streams, Drive.
echo.
set /p "ENLACE_URL=Pega aqui el enlace de origen: "
if "%ENLACE_URL%"=="" goto MENU

echo.
echo A que nube deseas mandarlo?
echo  [1] Google Drive (Rotacion Inteligente: Julio + Vexor 10TB)
echo  [2] Google Drive (Mi Unidad Principal - Julio)
echo  [3] Google Drive (Unidad Auxiliar - Vexor)
echo  [4] Microsoft OneDrive
echo  [5] MEGA.nz personal
echo  [6] Nube Desconocida / WebDAV / S3
set /p "DEST_SEL=Selecciona [1-6] (Default: 1): "
set "DEST_TARGET=Google Drive (Rotación Inteligente: Julio + Vexor 10TB)"
if "%DEST_SEL%"=="2" set "DEST_TARGET=Google Drive (Mi Unidad Principal - Julio)"
if "%DEST_SEL%"=="3" set "DEST_TARGET=Google Drive (Unidad Auxiliar - Vexor)"
if "%DEST_SEL%"=="4" set "DEST_TARGET=Microsoft OneDrive (Aviso: Throttling 429)"
if "%DEST_SEL%"=="5" set "DEST_TARGET=MEGA.nz"
if "%DEST_SEL%"=="6" set "DEST_TARGET=Nube Desconocida / Genérica (WebDAV / AList / PikPak)"

echo.
set /p "CARPETA_DEST=Carpeta destino en tu nube (Default: DESCARGAS_UNIVERSALES): "
if "%CARPETA_DEST%"=="" set "CARPETA_DEST=DESCARGAS_UNIVERSALES"

echo.
echo Transmitiendo orden a los servidores en la nube de Microsoft Azure...
gh workflow run descargador_universal.yml --repo JulioHVPalacios/mega-drive-cloner -f source_url="%ENLACE_URL%" -f destination_target="%DEST_TARGET%" -f dest_folder="%CARPETA_DEST%" -f transfer_mode="Auto Streaming RAM Turbo (Zero Disco - Soporta 500GB/1TB/2TB)"
echo.
echo =====================================================================
echo  [OK] ORDEN ENVIADA CON EXITO A LA NUBE!
echo  Ya puedes apagar tu PC por completo.
echo  El servidor transferira los archivos a maxima velocidad de linea.
echo =====================================================================
pause
goto MENU

:LANZAR_ENJAMBRE
cls
echo =====================================================================
echo  [5] LANZAR ENJAMBRE HYDRA EN LA NUBE (20 SERVIDORES AZURE)
echo =====================================================================
echo.
set /p "ENLACE_NUBE=Pega el enlace de la carpeta gigantesca: "
if "%ENLACE_NUBE%"=="" goto MENU

echo.
set /p "CARPETA_NUBE=Nombre de la carpeta de destino en la nube: "
if "%CARPETA_NUBE%"=="" set "CARPETA_NUBE=DESCARGAS_HYDRA"

echo.
echo Transmitiendo orden al enjambre de 20 servidores...
gh workflow run descargador_hydra_enjambre.yml --repo JulioHVPalacios/mega-drive-cloner -f source_url="%ENLACE_NUBE%" -f destination_target="Google Drive (Mi Unidad)" -f dest_folder="%CARPETA_NUBE%" -f swarm_nodes="20"
echo.
echo [OK] Enjambre Hydra activado con exito. Ya puedes apagar tu PC.
pause
goto MENU

:VERIFICAR_WATCHDOG
cls
echo =====================================================================
echo  [6] ESTADO DEL AUTO-SINCRONIZADOR MEGAPACK (WATCHDOG 24/7)
echo =====================================================================
echo  Horarios programados: 04:00 AM y 12:00 PM (Hora local)
echo.
echo Consultando ultimas ejecuciones en GitHub Actions...
gh run list --workflow=sincronizador_automatico_megapack.yml --repo JulioHVPalacios/mega-drive-cloner --limit 5
echo.
echo [1] Disparar verificacion y sincronizacion AHORA en la nube
echo [2] Volver al menu
set /p "WATCH_OP=Selecciona [1-2]: "
if "%WATCH_OP%"=="1" (
    echo.
    echo Lanzando verificacion inmediata en la nube...
    gh workflow run sincronizador_automatico_megapack.yml --repo JulioHVPalacios/mega-drive-cloner
    echo [OK] Disparado con exito!
    pause
)
goto MENU

:BACKUP_SISTEMA
cls
call "%~dp0hacer_backup_seguro_pc.bat"
goto MENU

:RESTAURAR_SISTEMA
cls
call "%~dp0restaurar_tras_formateo.bat"
goto MENU
