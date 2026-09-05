/**
 * OMNICLOUD CORE - TELEGRAM BOT SERVERLESS WORKER (CLOUDFLARE EDGE)
 * 100% Gratuito - Siempre Activo - Cero PC Encendida - Respuesta en 10ms
 */

// Variables que se configuran en el panel de Cloudflare (Environment Variables):
// - TELEGRAM_BOT_TOKEN: El token que te da @BotFather
// - AUTHORIZED_CHAT_ID: Tu ID numerico de Telegram (solo tu puedes usarlo)
// - GITHUB_PAT: Tu Personal Access Token de GitHub (con permisos de workflow)
// - GITHUB_REPO: 'JulioHVPalacios/mega-drive-cloner'

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response('OmniCloud Telegram Worker activo.', { status: 200 });
    }

    try {
      const update = await request.json();
      const botToken = env.TELEGRAM_BOT_TOKEN;
      const authChatId = String(env.AUTHORIZED_CHAT_ID);
      const repo = env.GITHUB_REPO || 'JulioHVPalacios/mega-drive-cloner';
      const pat = env.GITHUB_PAT;

      // 1. Manejo de Mensajes de Texto
      if (update.message) {
        const msg = update.message;
        const chatId = String(msg.chat.id);
        const text = msg.text ? msg.text.trim() : '';

        // Filtro de Seguridad: Solo permitir mensajes de tu cuenta
        if (chatId !== authChatId) {
          await sendTG(botToken, chatId, '⛔ Acceso no autorizado. Este bot es privado.');
          return new Response('OK', { status: 200 });
        }

        // Comando /start o /help
        if (text === '/start' || text === '/help') {
          const welcome = 👑 <b>Bienvenido al Centro OmniCloud Core</b>\n\n +
            Puedo descargar cualquier archivo a maxima velocidad (1.5 Gbps) directo a tus nubes con tu PC 100% apagada.\n\n +
            👉 <b>Simplemente enviame o comparte cualquier enlace:</b>\n +
            • Torrents o Magnets\n +
            • ISOs gigantes de foros o HTTP\n +
            • MEGA.nz o TeraBox\n +
            • Videos de YouTube / HLS / m3u8\n +
            • Carpetas de Google Drive ajenas;
          
          const keyboard = {
            inline_keyboard: [
              [{ text: '📊 Estado de Descargas en Vivo', callback_data: 'cmd:status' }],
              [{ text: '🔄 Sincronizar Megapack Ahora', callback_data: 'cmd:sync' }]
            ]
          };
          await sendTG(botToken, chatId, welcome, keyboard);
          return new Response('OK', { status: 200 });
        }

        // Comando /status
        if (text === '/status') {
          await handleStatus(botToken, chatId, repo, pat);
          return new Response('OK', { status: 200 });
        }

        // Comando /sync
        if (text === '/sync') {
          await triggerSync(botToken, chatId, repo, pat);
          return new Response('OK', { status: 200 });
        }

        // Deteccion de Enlaces (HTTP, HTTPS, Magnet)
        if (text.startsWith('http://') || text.startsWith('https://') || text.startsWith('magnet:') || text.endsWith('.torrent')) {
          const reply = 📦 <b>Enlace Detectado:</b>\n<code></code>\n\n +
            🎯 <b>Selecciona a que nube deseas enviarlo:</b>;
          
          // Guardar link codificado en base64 en callback o session
          // Como callback_data tiene limite de 64 bytes, guardamos el comando abreviado
          // y pasamos el URL via parametro temporal
          const keyboard = {
            inline_keyboard: [
              [{ text: '🚀 Google Drive (Rotacion Julio + Vexor 10TB)', callback_data: d:rot| }],
              [
                { text: '📁 Julio (5TB)', callback_data: d:jul| },
                { text: '📁 Vexor (5TB)', callback_data: d:vex| }
              ],
              [
                { text: '☁️ OneDrive', callback_data: d:one| },
                { text: '🔴 MEGA.nz', callback_data: d:meg| }
              ]
            ]
          };
          await sendTG(botToken, chatId, reply, keyboard);
          return new Response('OK', { status: 200 });
        }

        await sendTG(botToken, chatId, 'ℹ️ Por favor enviame un enlace valido o usa /start para ver las opciones.');
      }

      // 2. Manejo de Clics en Botones Táctiles (Callback Queries)
      if (update.callback_query) {
        const cq = update.callback_query;
        const chatId = String(cq.message.chat.id);
        const data = cq.data;

        if (chatId !== authChatId) return new Response('OK', { status: 200 });

        if (data === 'cmd:status') {
          await handleStatus(botToken, chatId, repo, pat);
        } else if (data === 'cmd:sync') {
          await triggerSync(botToken, chatId, repo, pat);
        } else if (data.startsWith('d:')) {
          // Extraer destino del boton
          const parts = data.split('|');
          const code = parts[0];
          
          let target = 'Google Drive (Rotación Inteligente: Julio + Vexor 10TB)';
          if (code === 'd:jul') target = 'Google Drive (Mi Unidad Principal - Julio)';
          if (code === 'd:vex') target = 'Google Drive (Unidad Auxiliar - Vexor)';
          if (code === 'd:one') target = 'Microsoft OneDrive (Aviso: Throttling 429)';
          if (code === 'd:meg') target = 'MEGA.nz';

          // Extraer URL del texto del mensaje original
          const origText = cq.message.text || '';
          const match = origText.match(/Enlace Detectado:\s*([^\n]+)/);
          const fullUrl = match ? match[1].trim() : '';

          if (fullUrl) {
            await triggerDownload(botToken, chatId, repo, pat, fullUrl, target);
          } else {
            await sendTG(botToken, chatId, '⚠️ No se pudo extraer la URL. Por favor vuelve a enviarla.');
          }
        }

        // Responder a Telegram para apagar el indicador de carga del boton
        await fetch(https://api.telegram.org/bot/answerCallbackQuery?callback_query_id=);
      }

      return new Response('OK', { status: 200 });
    } catch (err) {
      return new Response('Error: ' + err.message, { status: 200 });
    }
  }
};

async function sendTG(token, chatId, text, keyboard = null) {
  const body = {
    chat_id: chatId,
    text: text,
    parse_mode: 'HTML'
  };
  if (keyboard) body.reply_markup = keyboard;
  return fetch(https://api.telegram.org/bot/sendMessage, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}

async function handleStatus(token, chatId, repo, pat) {
  try {
    const res = await fetch(https://api.github.com/repos//actions/runs?per_page=3, {
      headers: {
        'Authorization': Bearer ,
        'User-Agent': 'OmniCloud-Telegram-Bot',
        'Accept': 'application/vnd.github+json'
      }
    });
    const data = await res.json();
    const runs = data.workflow_runs || [];
    if (runs.length === 0) {
      await sendTG(token, chatId, 'ℹ️ No hay descargas recientes registradas en GitHub Actions.');
      return;
    }
    let msg = '📊 <b>ESTADO DE DESCARGAS EN VIVO (AZURE CLOUD):</b>\n\n';
    for (const r of runs) {
      const icon = r.status === 'completed' ? (r.conclusion === 'success' ? '✅' : '❌') : '🔄';
      msg += ${icon} <b></b>\nEstado:  ()\nInicio: \n\n;
    }
    await sendTG(token, chatId, msg);
  } catch (e) {
    await sendTG(token, chatId, '❌ Error al consultar GitHub: ' + e.message);
  }
}

async function triggerSync(token, chatId, repo, pat) {
  try {
    await sendTG(token, chatId, '🔄 Disparando verificacion del Megapack en Azure...');
    const res = await fetch(https://api.github.com/repos//actions/workflows/sincronizador_automatico_megapack.yml/dispatches, {
      method: 'POST',
      headers: {
        'Authorization': Bearer ,
        'User-Agent': 'OmniCloud-Telegram-Bot',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ref: 'main' })
    });
    if (res.status === 204) {
      await sendTG(token, chatId, '✅ ¡Auto-sincronizador lanzado en la nube! Te avisare si encuentra cursos nuevos.');
    } else {
      await sendTG(token, chatId, ⚠️ Respuesta de GitHub: );
    }
  } catch (e) {
    await sendTG(token, chatId, '❌ Error al disparar sync: ' + e.message);
  }
}

async function triggerDownload(token, chatId, repo, pat, url, target) {
  try {
    await sendTG(token, chatId, 🚀 <b>Transmitiendo orden a Azure...</b>\n🎯 Destino: <i></i>\nTu PC puede seguir apagada.);
    const res = await fetch(https://api.github.com/repos//actions/workflows/descargador_universal.yml/dispatches, {
      method: 'POST',
      headers: {
        'Authorization': Bearer ,
        'User-Agent': 'OmniCloud-Telegram-Bot',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ref: 'main',
        inputs: {
          source_url: url,
          destination_target: target,
          dest_folder: 'DESCARGAS_UNIVERSALES',
          transfer_mode: 'Auto Streaming RAM Turbo (Zero Disco - Soporta 500GB/1TB/2TB)'
        }
      })
    });
    if (res.status === 204) {
      await sendTG(token, chatId, 🎉 <b>¡Descarga en marcha a 1.5 Gbps!</b>\nLos servidores de Azure estan transfiriendo tus archivos. Sonara un 'ding' cuando finalice.);
    } else {
      await sendTG(token, chatId, ⚠️ Error al iniciar descarga en GitHub (Status ).);
    }
  } catch (e) {
    await sendTG(token, chatId, '❌ Error al conectar con GitHub: ' + e.message);
  }
}
