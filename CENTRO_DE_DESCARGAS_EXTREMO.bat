@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title 🚀 CENTRO DE DESCARGAS Y TRANSFERENCIA EXTREMA (Universal Multi-Nube / 32 Hilos)

:MENU
cls
echo =====================================================================
echo  👑 CENTRO DE TRANSFERENCIA Y DESCARGAS EXTREMAS
echo     (Aceleración 32 Hilos / Detección de Discos / 20 Nodos Azure)
echo =====================================================================
echo.
echo  [1] ⚡ Descargar CUALQUIER Enlace de Internet a tu PC (Torrents/ISOs/Mega/Web)
echo  [2] 📥 Descargar Carpeta Completa de Google Drive a tu PC/Disco Externo
echo  [3] 📂 Montar Google Drive como Disco Virtual (Z:) en Windows
echo  [4] 🚀 Descargador Universal a la Nube (Cualquier Link a Cualquier Nube - PC Apagada)
echo  [5] 🐉 Enviar al Enjambre Hydra en la Nube (20 Servidores Azure)
echo  [6] 🔄 Verificar Estado del Auto-Sincronizador Megapack (Watchdog)
echo  [7] 🛠️ Restaurar / Reparar Herramientas (Post-Formateo en 30s)
echo  [0] ❌ Salir
echo.
echo =====================================================================
set /p OPCION="Selecciona una opción [0-7]: "

if "%OPCION%"=="1" goto DESCARGA_UNIVERSAL_LOCAL
if "%OPCION%"=="2" goto CLONAR_DRIVE_A_LOCAL
if "%OPCION%"=="3" goto MONTAR_DRIVE
if "%OPCION%"=="4" goto DESCARGADOR_UNIVERSAL_CLOUD
if "%OPCION%"=="5" goto LANZAR_ENJAMBRE
if "%OPCION%"=="6" goto VERIFICAR_WATCHDOG
if "%OPCION%"=="7" goto RESTAURAR_SISTEMA
if "%OPCION%"=="0" exit /b
goto MENU

:DESCARGA_UNIVERSAL_LOCAL
cls
echo =====================================================================
echo  ⚡ [1] DESCARGA UNIVERSAL A MÁXIMA VELOCIDAD (A TU DISCO O LAPTOP)
echo =====================================================================
echo  Soporta: Torrents, Magnets, ISOs gigantes, Enlaces directos, Videos, etc.
echo.
echo 📊 Estado actual de tus discos:
powershell -Command "Get-PSDrive -PSProvider FileSystem | ForEach-Object { [PSCustomObject]@{ 'Unidad' = $_.Name + ':'; 'Libre (GB)' = [math]::Round($_.Free / 1GB, 2); 'Total (GB)' = [math]::Round(($_.Used + $_.Free) / 1GB, 2) } } | Format-Table -AutoSize"
echo.

set /p URL_ORIGEN="Pega aquí tu enlace (URL, Magnet o arrastra el archivo .torrent): "
if "%URL_ORIGEN%"=="" goto MENU

echo.
echo ¿En qué disco deseas guardarlo?
echo   - Puedes usar tu laptop (ej. C:\Descargas o D:\Descargas)
echo   - O conectar tu disco externo (ej. E:\ o F:\)
set /p RUTA_DESTINO="Escribe la ruta o letra de disco (Default: D:\Descargas): "
if "%RUTA_DESTINO%"=="" set RUTA_DESTINO=D:\Descargas

if not exist "%RUTA_DESTINO%" (
    echo Creando carpeta: %RUTA_DESTINO%
    mkdir "%RUTA_DESTINO%" 2>nul
)

where aria2c >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando motor acelerador Aria2c (Cero lag, 32 hilos)...
    winget install aria2.aria2 --accept-source-agreements --accept-package-agreements >nul 2>nul
)

echo.
echo =====================================================================
echo 🚀 DESCARGANDO A MÁXIMA POTENCIA DE LÍNEA:
echo  • Conexiones concurrentes: 16 a 32 hilos en paralelo.
echo  • Preasignación 'falloc': Reserva espacio en 1 segundo (Cero fragmentación).
echo  • Memoria DMA (mmap): Escribe directo a disco sin calentar procesador.
echo  • Reanudación inteligente: Si se corta la red, continúa donde se quedó.
echo =====================================================================
echo.

aria2c "%URL_ORIGEN%" --dir="%RUTA_DESTINO%" --continue=true --file-allocation=falloc --enable-mmap=true --max-connection-per-server=16 --split=32 --min-split-size=5M --summary-interval=2 --max-overall-upload-limit=10K --bt-max-peers=100 --enable-dht=true --check-integrity=true --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

echo.
echo =====================================================================
echo ✅ ¡DESCARGA COMPLETADA CON ÉXITO TOTAL!
echo Guardado en: %RUTA_DESTINO%
echo =====================================================================
pause
goto MENU

:CLONAR_DRIVE_A_LOCAL
cls
echo =====================================================================
echo  📥 [2] CLONAR CARPETA DE GOOGLE DRIVE A DISCO LOCAL / EXTERNO
echo =====================================================================
echo.
echo Carpetas en tu Google Drive:
rclone lsd "midrive:"
echo.
set /p CARPETA_DRIVE="Escribe el nombre de la carpeta en Drive a descargar: "
if "%CARPETA_DRIVE%"=="" goto MENU

echo.
echo Discos disponibles:
powershell -Command "Get-PSDrive -PSProvider FileSystem | ForEach-Object { [PSCustomObject]@{ 'Unidad' = $_.Name + ':'; 'Libre (GB)' = [math]::Round($_.Free / 1GB, 2); 'Total (GB)' = [math]::Round(($_.Used + $_.Free) / 1GB, 2) } } | Format-Table -AutoSize"
echo.
set /p RUTA_LOCAL="Escribe la ruta local o disco destino (ej. E:\Cursos, D:\Backup): "
if "%RUTA_LOCAL%"=="" set RUTA_LOCAL=D:\Descargas\%CARPETA_DRIVE%

echo.
echo 🚀 Descargando con 16 transferencias paralelas y 32 checkers...
rclone copy "midrive:%CARPETA_DRIVE%" "%RUTA_LOCAL%" --transfers=16 --checkers=32 --buffer-size=256M --use-mmap --fast-list -P -v
echo.
echo ✅ Copia completada y verificada en: %RUTA_LOCAL%
pause
goto MENU

:MONTAR_DRIVE
cls
echo =====================================================================
echo  📂 [3] MONTAR GOOGLE DRIVE COMO DISCO VIRTUAL (Z:) EN WINDOWS
echo =====================================================================
echo.
echo Verificando controlador WinFsp...
sc query WinFsp.Launcher >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando WinFsp para soporte de disco virtual en Windows...
    winget install WinFsp.WinFsp --accept-source-agreements --accept-package-agreements
)

echo.
echo Montando Google Drive en Z:...
start /b rclone mount midrive: Z: --vfs-cache-mode full --buffer-size=256M --dir-cache-time 72h --network-mode
timeout /t 3 >nul
explorer Z:
echo ✅ Unidad Z: montada con éxito. Podrás ver tus archivos en 'Este equipo'.
pause
goto MENU

:DESCARGADOR_UNIVERSAL_CLOUD
cls
echo =====================================================================
echo  🚀 [4] DESCARGADOR UNIVERSAL A LA NUBE (PC APAGADA)
echo =====================================================================
echo  Soporta: Torrents, Magnets, ISOs gigantes, Enlaces directos,
echo           MEGA.nz, TeraBox, YouTube/Streams, Drive-to-Drive.
echo.
set /p ENLACE_URL="Pega aquí el enlace de origen: "
if "%ENLACE_URL%"=="" goto MENU

echo.
echo ¿A qué nube deseas mandarlo?
echo  [1] Google Drive (Rotación Inteligente: Julio + Vexor 10TB)
echo  [2] Google Drive (Mi Unidad Principal - Julio)
echo  [3] Google Drive (Unidad Auxiliar - Vexor)
echo  [4] Microsoft OneDrive
echo  [5] MEGA.nz personal
echo  [6] Nube Desconocida / WebDAV / S3
set /p DEST_SEL="Selecciona [1-6] (Default: 1): "
set DEST_TARGET=Google Drive (Rotación Inteligente: Julio + Vexor 10TB)
if "%DEST_SEL%"=="2" set DEST_TARGET=Google Drive (Mi Unidad Principal - Julio)
if "%DEST_SEL%"=="3" set DEST_TARGET=Google Drive (Unidad Auxiliar - Vexor)
if "%DEST_SEL%"=="4" set DEST_TARGET=Microsoft OneDrive (Aviso: Throttling 429)
if "%DEST_SEL%"=="5" set DEST_TARGET=MEGA.nz
if "%DEST_SEL%"=="6" set DEST_TARGET=Nube Desconocida / Genérica (WebDAV / AList / PikPak)

echo.
set /p CARPETA_DEST="Nombre de la carpeta de destino (Default: DESCARGAS_UNIVERSALES): "
if "%CARPETA_DEST%"=="" set CARPETA_DEST=DESCARGAS_UNIVERSALES

echo.
echo 🚀 Transmitiendo orden a los servidores en la nube de Microsoft Azure...
gh workflow run descargador_universal.yml --repo JulioHVPalacios/mega-drive-cloner -f source_url="%ENLACE_URL%" -f destination_target="%DEST_TARGET%" -f dest_folder="%CARPETA_DEST%" -f transfer_mode="Auto Streaming RAM Turbo (Zero Disco - Soporta 500GB/1TB/2TB)"
echo.
echo =====================================================================
echo ✅ ¡ORDEN ENVIADA CON ÉXITO A LA NUBE!
echo Ya puedes apagar tu PC por completo.
echo El servidor en la nube transferirá los archivos a máxima velocidad.
echo =====================================================================
pause
goto MENU

:LANZAR_ENJAMBRE
cls
echo =====================================================================
echo  🐉 [5] LANZAR ENJAMBRE HYDRA EN LA NUBE (20 SERVIDORES AZURE)
echo =====================================================================
echo.
set /p ENLACE_NUBE="Pega el enlace (Drive, OneDrive, TeraBox o Torrent): "
if "%ENLACE_NUBE%"=="" goto MENU

echo.
echo ¿A qué destino deseas enviarlo?
echo [1] Google Drive (Mi Unidad)
echo [2] Microsoft OneDrive
echo [3] Ambas Nubes (Google Drive + OneDrive)
set /p DEST_NUBE="Selecciona [1-3] (Default: 1): "
set DESTINO_FINAL=Google Drive (Mi Unidad)
if "%DEST_NUBE%"=="2" set DESTINO_FINAL=Microsoft OneDrive
if "%DEST_NUBE%"=="3" set DESTINO_FINAL=Ambas Nubes (Google Drive + Microsoft OneDrive)

set /p CARPETA_NUBE="Nombre de la carpeta de destino en la nube: "
if "%CARPETA_NUBE%"=="" set CARPETA_NUBE=DESCARGAS_HYDRA

echo.
echo 🚀 Transmitiendo orden a los 20 servidores en Azure...
gh workflow run descargador_hydra_enjambre.yml --repo JulioHVPalacios/mega-drive-cloner -f source_url="%ENLACE_NUBE%" -f destination_target="%DESTINO_FINAL%" -f dest_folder="%CARPETA_NUBE%" -f swarm_nodes="20"
echo.
echo =====================================================================
echo ✅ ¡ENJAMBRE HYDRA ACTIVADO CON ÉXITO!
echo Ya puedes apagar tu PC o cerrar esta ventana si lo deseas.
echo Los 20 servidores continuarán transfiriendo 24/7 en la nube.
echo =====================================================================
pause
goto MENU

:VERIFICAR_WATCHDOG
cls
echo =====================================================================
echo  🔄 [6] ESTADO DEL AUTO-SINCRONIZADOR MEGAPACK (WATCHDOG 24/7)
echo =====================================================================
echo  Horarios programados: 04:00 AM y 12:00 PM (Hora local Perú/Col/Ecu)
echo.
echo 📊 Consultando últimas ejecuciones en GitHub Actions...
gh run list --workflow=sincronizador_automatico_megapack.yml --repo JulioHVPalacios/mega-drive-cloner --limit 5
echo.
echo =====================================================================
echo [1] Disparar verificación y sincronización AHORA en la nube
echo [2] Volver al menú principal
set /p WATCH_OP="Selecciona [1-2]: "
if "%WATCH_OP%"=="1" (
    echo.
    echo 🚀 Lanzando verificación inmediata en la nube...
    gh workflow run sincronizador_automatico_megapack.yml --repo JulioHVPalacios/mega-drive-cloner
    echo ✅ ¡Disparado! Puedes revisar el avance con la opción 6 en unos segundos.
    pause
)
goto MENU

:RESTAURAR_SISTEMA
cls
call "%~dp0restaurar_tras_formateo.bat"
goto MENU
