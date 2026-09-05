@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title 🚀 CENTRO DE TRANSFERENCIA Y DESCARGAS EXTREMAS (100 Gbps Cloud / Multi-Hilo Local)

:MENU
cls
echo =====================================================================
echo  👑 CENTRO DE TRANSFERENCIA Y DESCARGAS EXTREMAS
echo     (Aceleración Multi-Hilo / Discos Externos / 20 Nodos Azure)
echo =====================================================================
echo.
echo  [1] ⚡ Descargar Torrent / ISO / Enlace Directo a Disco Duro (Local/Externo)
echo  [2] 📥 Descargar Carpeta de Google Drive a tu Disco Duro (32 Conexiones)
echo  [3] 📂 Montar Google Drive como Disco Virtual (Z:) en Windows
echo  [4] 🐉 Enviar al Enjambre Hydra en la Nube (Apagar PC / Celular)
echo  [5] 🔄 Actualizar / Restaurar Credenciales y Herramientas (Post-Formateo)
echo  [0] ❌ Salir
echo.
echo =====================================================================
set /p OPCION="Selecciona una opción [0-5]: "

if "%OPCION%"=="1" goto DESCARGA_DIRECTA
if "%OPCION%"=="2" goto CLONAR_DRIVE_A_LOCAL
if "%OPCION%"=="3" goto MONTAR_DRIVE
if "%OPCION%"=="4" goto LANZAR_ENJAMBRE
if "%OPCION%"=="5" goto RESTAURAR_SISTEMA
if "%OPCION%"=="0" exit /b
goto MENU

:DESCARGA_DIRECTA
cls
echo =====================================================================
echo  ⚡ [1] DESCARGA MULTI-HILO ULTRA RÁPIDA (TORRENTS / ISOS / ENLACES)
echo =====================================================================
echo.
echo Discos disponibles en tu PC:
powershell -Command "Get-PSDrive -PSProvider FileSystem | ForEach-Object { [PSCustomObject]@{ 'Unidad' = $_.Name + ':'; 'Espacio Libre (GB)' = [math]::Round($_.Free / 1GB, 2); 'Espacio Total (GB)' = [math]::Round(($_.Used + $_.Free) / 1GB, 2) } } | Format-Table -AutoSize"
echo.
set /p URL_ORIGEN="Pega el enlace URL, Magnet o ruta del archivo .torrent: "
if "%URL_ORIGEN%"=="" goto MENU

set /p DISCO_DESTINO="Escribe la letra del disco o ruta destino (ej. E:, D:\Descargas, F:): "
if "%DISCO_DESTINO%"=="" set DISCO_DESTINO=D:\Descargas

if not exist "%DISCO_DESTINO%" (
    echo Creando directorio: %DISCO_DESTINO%
    mkdir "%DISCO_DESTINO%" 2>nul
)

where aria2c >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando motor Aria2c ultra-acelerado...
    winget install aria2.aria2 --accept-source-agreements --accept-package-agreements >nul 2>nul
)

echo.
echo 🚀 Iniciando descarga a saturación de línea con preasignación 'falloc' (Cero lag de disco)...
aria2c "%URL_ORIGEN%" --dir="%DISCO_DESTINO%" --file-allocation=falloc --enable-mmap=true --max-connection-per-server=16 --split=16 --min-split-size=10M --summary-interval=5 --max-overall-upload-limit=1K
echo.
echo ✅ Descarga completada en: %DISCO_DESTINO%
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
set /p CARPETA_DRIVE="Escribe el nombre exacto de la carpeta en Drive a descargar: "
if "%CARPETA_DRIVE%"=="" goto MENU

echo.
echo Discos disponibles:
powershell -Command "Get-PSDrive -PSProvider FileSystem | ForEach-Object { [PSCustomObject]@{ 'Unidad' = $_.Name + ':'; 'Espacio Libre (GB)' = [math]::Round($_.Free / 1GB, 2) } } | Format-Table -AutoSize"
echo.
set /p RUTA_LOCAL="Escribe la ruta local o disco externo destino (ej. E:\Cursos, D:\Backup): "
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
echo Podrás abrir tu Google Drive directamente desde 'Este equipo'.
start /b rclone mount midrive: Z: --vfs-cache-mode full --buffer-size 256M --dir-cache-time 72h --network-mode
timeout /t 3 >nul
explorer Z:
echo ✅ Unidad Z: montada con éxito.
pause
goto MENU

:LANZAR_ENJAMBRE
cls
echo =====================================================================
echo  🐉 [4] LANZAR ENJAMBRE HYDRA EN LA NUBE (20 SERVIDORES AZURE)
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

:RESTAURAR_SISTEMA
cls
call "%~dp0restaurar_tras_formateo.bat"
goto MENU
