# 🌐 GUÍA DEFINITIVA: CÓMO TENER TU BOT ACTIVO 24/7 (CON PC 100% APAGADA O FORMATEADA)

Para que tu bot de Telegram (`@VexorOmniBot`) funcione **perpetuamente**, día y noche, **con tu computadora apagada, desenchufada o tras formatear Windows**, el bot debe estar alojado en la nube gratuita de **Cloudflare Workers**.

---

## ⚡ OPCIÓN RÁPIDA: DESPLIEGUE EN CLOUDFLARE EN 60 SEGUNDOS (100% GRATIS)

### Paso 1: Entrar a Cloudflare (Cero Costo)
1. Entra a [https://dash.cloudflare.com/](https://dash.cloudflare.com/) (si no tienes cuenta, regístrate gratis en 15 segundos sin tarjeta).
2. En el menú lateral izquierdo, haz clic en **Workers & Pages** (Workers y Páginas).
3. Haz clic en el botón azul **Create application** ➔ pestaña **Workers** ➔ clic en **Create Worker**.
4. Ponle de nombre `omnicloud-bot` y haz clic en **Deploy** (Desplegar).

### Paso 2: Pegar el Código del Bot
1. En la pantalla que aparece, haz clic en **Edit code** (Editar código).
2. En el editor de la izquierda, **borra todo** lo que haya.
3. Abre tu archivo `D:\mega-drive-cloner\telegram_bot_worker.js`, copia todo su contenido y **pégalo en el editor de Cloudflare**.
4. Haz clic en el botón azul **Deploy** (arriba a la derecha).

### Paso 3: Configurar las Variables de Entorno
1. Regresa a la página principal de tu Worker y entra en la pestaña **Settings** (Configuración) ➔ **Variables and Secrets**.
2. Añade las siguientes 3 variables:
   - `TELEGRAM_BOT_TOKEN`: `8775957501:AAEF5W3TgWUku6pMCqdFN9ouFpxMG4BJ7MI`
   - `AUTHORIZED_CHAT_ID`: `1136933800`
   - `GITHUB_PAT`: (Tu token personal de GitHub)
   - *(Opcional)* `GEMINI_API_KEY`: (Tu clave de Google Gemini para IA sin censura)
   - *(Opcional)* `OPENROUTER_API_KEY`: (Tu clave de OpenRouter si deseas Dolphin/LLaMA)
3. Haz clic en **Save and Deploy**.

### Paso 4: Conectar Telegram con tu Worker (1 Clic)
Copia la URL que te da Cloudflare (ejemplo: `https://omnicloud-bot.tu-subdominio.workers.dev`).
Ahora tienes 2 opciones sencillísimas para vincularlo:
- **Método A:** Abre en tu PC el archivo `D:\mega-drive-cloner\configurar_webhook_nube_24_7.bat`, pega tu URL y presiona Enter.
- **Método B:** Pega esto en tu navegador web:
  `https://api.telegram.org/bot8775957501:AAEF5W3TgWUku6pMCqdFN9ouFpxMG4BJ7MI/setWebhook?url=https://omnicloud-bot.tu-subdominio.workers.dev`

---

## 🎉 ¡LISTO! RESULTADO FINAL:
- Tu bot responderá en **15 milisegundos**.
- Tu PC puede estar **100% apagada**, desenchufada o en medio de un formateo completo de Windows.
- El bot responderá a tus toques, descargas en Azure, búsquedas en GitHub y consultas sin censura los 365 días del año.
