# 🌐 GUÍA MAESTRA: CÓMO CONECTAR CUALQUIER NUBE (CONOCIDA O DESCONOCIDA)

Esta guía te explica de forma extremadamente simple cómo conectar cualquier página de almacenamiento en la nube a tu **Descargador Universal de GitHub Actions**, para que siempre seas 100% independiente aunque no tengas asistencia técnica a mano.

---

## 🧭 ¿Cómo funciona el almacenamiento en internet?

El 99% de las páginas en el mundo que te regalan o venden almacenamiento (TeraBox, InfiniCLOUD, pCloud, Degoo, 4shared, Nextcloud, servidores de universidades) usan un estándar abierto llamado **WebDAV**.

**WebDAV** es como un "enchufe universal": permite que cualquier programa (como GitHub Actions o Rclone) meta o saque archivos de tu cuenta sin entrar a la página web.

---

## 📋 ¿Qué datos pide una nube para conectarse?

Solo necesitas **3 datos sencillos**:
1. **URL de conexión**: La dirección del servidor (siempre empieza con `https://...`).
2. **Usuario**: Tu correo electrónico o tu nombre de usuario en esa página.
3. **Contraseña**: Tu contraseña o una "Contraseña de aplicación" (*App Password*) que generas en los ajustes de esa página.

---

## 🔍 ¿Dónde encontrar esos 3 datos en las nubes más populares?

### 1. InfiniCLOUD (20 GB - 1 TB gratuitos)
* Entras a tu cuenta en `infinicloud.com`.
* Vas a **My Page** (Mi Página).
* Verás una sección llamada **Apps Connection** (Conexión de Aplicaciones).
* Haces clic en **Turn on Connection Password** (Activar contraseña de conexión).
* Te mostrará:
  * **URL:** `https://xxxx.infinicloud.jp/dav/`
  * **User ID:** Tu ID de usuario
  * **Password:** Tu contraseña de conexión generada

---

### 2. pCloud (Hasta 2 TB)
* **URL:**  
  * Si tu cuenta es de Estados Unidos: `https://webdav.pcloud.com/`  
  * Si tu cuenta es de Europa: `https://ewebdav.pcloud.com/`
* **Usuario:** Tu correo de pCloud
* **Contraseña:** Tu contraseña de pCloud

---

### 3. TeraBox / Degoo / 4shared
* En los ajustes de tu cuenta, busca la pestaña **Seguridad**, **Acceso Remoto** o **Avanzado**.
* Activa la opción **WebDAV** o **FTP**.
* Copia el enlace que te muestra en pantalla.

---

### 4. Nextcloud / ownCloud (Nubes Privadas o de Universidades)
* Entra a tu Nextcloud en el navegador.
* En la esquina inferior izquierda, haz clic en **Archivos** > **Ajustes de archivos**.
* Verás un enlace que dice **WebDAV**:  
  `https://tu-servidor.com/remote.php/dav/files/tu_usuario/`
* Ese enlace es tu URL. Tu usuario y clave son los mismos con los que inicias sesión.

---

## 🚀 Las 2 Formas de Usarlo en tu Descargador Universal

### Forma 1: Directo en la página de GitHub Actions (Sin configurar nada en tu PC)
1. Abres el **Descargador Universal** en GitHub Actions.
2. En **`🎯 Nube de Destino`** seleccionas: `Nube Desconocida / Genérica (WebDAV)`.
3. En la casilla **`🔑 Credenciales Nube Externa`** pegas los 3 datos en este formato simple:
   ```text
   url=https://la-direccion-que-te-dio-la-pagina/; user=tu_correo@gmail.com; pass=tu_contraseña
   ```
4. Clic en **`Run workflow`** y ¡listo! Los 500 GB se transferirán directamente hacia allá.

---

### Forma 2: Con el Asistente Automático de tu Computadora (1 Clic)
En tu carpeta `D:\mega-drive-cloner`:
1. Haces doble clic en el archivo: **`conectar_cualquier_nube.bat`**.
2. Te saldrá un menú en pantalla con números:
   * Presionas `[4]` para Nube Desconocida / WebDAV.
   * Presionas `[2]` para OneDrive.
   * Presionas `[3]` para MEGA.
3. El asistente te pide los datos, los prueba, y los **sube automáticamente a tu GitHub**.
4. A partir de ese momento, esa nube queda guardada para siempre y ya no tienes que escribir contraseñas nunca más.
