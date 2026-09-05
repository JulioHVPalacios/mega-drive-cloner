/**
 * OMNICLOUD CORE - TELEGRAM BOT SERVERLESS WORKER (CLOUDFLARE EDGE)
 * 100% Gratuito - Siempre Activo - Cero PC Encendida - Latencia ultrabaja
 */

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response('OmniCloud Telegram Worker activo.', { status: 200 });
    }

    try {
      const update = await request.json();
      const botToken = env.TELEGRAM_BOT_TOKEN;
      const authChatId = String(env.AUTHORIZED_CHAT_ID || '');
      const repo = env.GITHUB_REPO || 'JulioHVPalacios/mega-drive-cloner';
      const pat = env.GITHUB_PAT;

      if (!botToken) {
        return new Response('Missing TELEGRAM_BOT_TOKEN', { status: 200 });
      }

      // 1. Manejo de Mensajes de Texto
      if (update.message) {
        const msg = update.message;
        const chatId = String(msg.chat.id);
        const text = msg.text ? msg.text.trim() : '';

        // Filtro de Seguridad: Solo permitir tu cuenta si AUTHORIZED_CHAT_ID esta configurado
        if (authChatId && chatId !== authChatId) {
          await sendTG(botToken, chatId, '⛔ Acceso no autorizado. Este bot es de uso privado.');
          return new Response('OK', { status: 200 });
        }

        // Comando /start o /help
        if (text === '/start' || text === '/help') {
          const welcome = '👑 <b>Bienvenido al Centro OmniCloud Core</b>\n\n' +
            'Puedo descargar cualquier archivo a maxima velocidad (1.5 - 2.0 Gbps) directo a tus nubes con tu PC 100% apagada.\n\n' +
            '👉 <b>Simplemente enviame o comparte cualquier enlace:</b>\n' +
            '• Torrents o Magnets\n' +
            '• ISOs gigantes de foros o HTTP\n' +
            '• MEGA.nz o TeraBox\n' +
            '• Videos de YouTube / HLS / m3u8\n' +
            '• Carpetas de Google Drive ajenas';

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
          const reply = '📦 <b>Enlace Detectado:</b>\n<code>' + escapeHtml(text) + '</code>\n\n' +
            '🎯 <b>Selecciona a que nube deseas enviarlo:</b>';

          const keyboard = {
            inline_keyboard: [
              [{ text: '🚀 Google Drive (Rotacion Julio + Vexor 10TB)', callback_data: 'd:rot' }],
              [
                { text: '📁 Julio (5TB)', callback_data: 'd:jul' },
                { text: '📁 Vexor (5TB)', callback_data: 'd:vex' }
              ],
              [
                { text: '☁️ OneDrive', callback_data: 'd:one' },
                { text: '🔴 MEGA.nz', callback_data: 'd:meg' }
              ]
            ]
          };
          await sendTG(botToken, chatId, reply, keyboard);
          return new Response('OK', { status: 200 });
        }

        await sendTG(botToken, chatId, 'ℹ️ Enviame un enlace (HTTP/Magnet/Drive/Mega) o pulsa /start para ver el menu.');
      }

      // 2. Manejo de Botones Tactiles (Callback Queries)
      if (update.callback_query) {
        const cq = update.callback_query;
        const chatId = String(cq.message.chat.id);
        const data = cq.data;

        if (authChatId && chatId !== authChatId) {
          await sendTG(botToken, chatId, '⛔ Acceso no autorizado.');
          return new Response('OK', { status: 200 });
        }

        if (data === 'cmd:status') {
          await handleStatus(botToken, chatId, repo, pat);
        } else if (data === 'cmd:sync') {
          await triggerSync(botToken, chatId, repo, pat);
        } else if (data.startsWith('d:')) {
          let target = 'Google Drive (Rotacion Inteligente: Julio + Vexor 10TB)';
          if (data === 'd:jul') target = 'Google Drive (Mi Unidad Principal - Julio)';
          if (data === 'd:vex') target = 'Google Drive (Unidad Auxiliar - Vexor)';
          if (data === 'd:one') target = 'Microsoft OneDrive (Aviso: Throttling 429)';
          if (data === 'd:meg') target = 'MEGA.nz';

          const origText = cq.message.text || '';
          const match = origText.match(/Enlace Detectado:\s*([\s\S]+?)(?:\n\n🎯|$)/);
          const fullUrl = match ? match[1].trim() : '';

          if (fullUrl) {
            await triggerDownload(botToken, chatId, repo, pat, fullUrl, target);
          } else {
            await sendTG(botToken, chatId, '⚠️ No se pudo extraer la URL. Por favor vuelve a enviarla por texto.');
          }
        }

        // Apagar el relojito del boton en la app de Telegram
        await fetch(`https://api.telegram.org/bot${botToken}/answerCallbackQuery?callback_query_id=${cq.id}`).catch(() => {});
      }

      return new Response('OK', { status: 200 });
    } catch (err) {
      return new Response('Error: ' + err.message, { status: 200 });
    }
  }
};

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

async function sendTG(token, chatId, text, keyboard = null) {
  const body = {
    chat_id: chatId,
    text: text,
    parse_mode: 'HTML'
  };
  if (keyboard) body.reply_markup = keyboard;
  return fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}

async function handleStatus(token, chatId, repo, pat) {
  try {
    if (!pat) {
      await sendTG(token, chatId, '⚠️ GITHUB_PAT no configurado en Cloudflare Workers.');
      return;
    }
    const res = await fetch(`https://api.github.com/repos/${repo}/actions/runs?per_page=3`, {
      headers: {
        'Authorization': `Bearer ${pat}`,
        'User-Agent': 'OmniCloud-Telegram-Bot',
        'Accept': 'application/vnd.github+json'
      }
    });
    const data = await res.json();
    const runs = data.workflow_runs || [];
    if (runs.length === 0) {
      await sendTG(token, chatId, 'ℹ️ No hay ejecuciones recientes en GitHub Actions.');
      return;
    }
    let msg = '📊 <b>ESTADO DE DESCARGAS EN VIVO (AZURE CLOUD):</b>\n\n';
    for (const r of runs) {
      const icon = r.status === 'completed' ? (r.conclusion === 'success' ? '✅' : '❌') : '🔄';
      msg += `${icon} <b>${escapeHtml(r.name || 'Tarea')}</b>\nEstado: ${r.status} (${r.conclusion || 'en curso'})\nID: ${r.id}\n\n`;
    }
    await sendTG(token, chatId, msg);
  } catch (e) {
    await sendTG(token, chatId, '❌ Error al consultar GitHub: ' + e.message);
  }
}

async function triggerSync(token, chatId, repo, pat) {
  try {
    if (!pat) {
      await sendTG(token, chatId, '⚠️ GITHUB_PAT no configurado en Cloudflare Workers.');
      return;
    }
    await sendTG(token, chatId, '🔄 Disparando verificacion del Megapack en Azure...');
    const res = await fetch(`https://api.github.com/repos/${repo}/actions/workflows/sincronizador_automatico_megapack.yml/dispatches`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${pat}`,
        'User-Agent': 'OmniCloud-Telegram-Bot',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ref: 'main' })
    });
    if (res.status === 204) {
      await sendTG(token, chatId, '✅ ¡Auto-sincronizador lanzado en la nube! Te avisare si encuentra cursos nuevos.');
    } else {
      await sendTG(token, chatId, `⚠️ Respuesta de GitHub (Status ${res.status})`);
    }
  } catch (e) {
    await sendTG(token, chatId, '❌ Error al disparar sync: ' + e.message);
  }
}

async function triggerDownload(token, chatId, repo, pat, url, target) {
  try {
    if (!pat) {
      await sendTG(token, chatId, '⚠️ GITHUB_PAT no configurado en Cloudflare Workers.');
      return;
    }
    await sendTG(token, chatId, `🚀 <b>Transmitiendo orden a Azure...</b>\n🎯 Destino: <i>${target}</i>\nTu PC puede seguir apagada.`);
    const res = await fetch(`https://api.github.com/repos/${repo}/actions/workflows/descargador_universal.yml/dispatches`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${pat}`,
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
      await sendTG(token, chatId, '🎉 <b>¡Descarga en marcha a 1.5 Gbps!</b>\nLos servidores de Azure estan transfiriendo tus archivos. Sonara una notificacion cuando finalice.');
    } else {
      await sendTG(token, chatId, `⚠️ Error al iniciar descarga en GitHub (Status ${res.status}).`);
    }
  } catch (e) {
    await sendTG(token, chatId, '❌ Error al conectar con GitHub: ' + e.message);
  }
}
