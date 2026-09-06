/**
 * OMNICLOUD CORE 2.0 - TELEGRAM BOT SERVERLESS WORKER (CLOUDFLARE EDGE)
 * 100% Gratuito - Siempre Activo 24/7 - Cero PC Encendida - Latencia Ultrabaja
 * Incluye Teclado Táctil Persistente, Búsqueda de Proyectos en Vivo, IA y Gestión Remota
 */

const MAIN_KEYBOARD = {
  keyboard: [
    [{ text: "🚀 Enviar Enlace / Descargar" }, { text: "🤝 Compartir Carpeta" }],
    [{ text: "📊 Estado de Descargas" }, { text: "👥 Ver Permisos" }],
    [{ text: "🧠 Asistente IA" }, { text: "🔄 Sincronizar Megapack" }]
  ],
  resize_keyboard: true,
  is_persistent: true
};

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
      const geminiKey = env.GEMINI_API_KEY || '';

      if (!botToken) {
        return new Response('Missing TELEGRAM_BOT_TOKEN', { status: 200 });
      }

      // 1. Mensajes de Texto
      if (update.message) {
        const msg = update.message;
        const chatId = String(msg.chat.id);
        const text = msg.text ? msg.text.trim() : '';

        if (authChatId && chatId !== authChatId) {
          await sendTG(botToken, chatId, '⛔ Acceso no autorizado. Este bot es de uso privado.');
          return new Response('OK', { status: 200 });
        }

        const norm = text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();

        // Botones del teclado persistente o comandos
        if (text === '🚀 Enviar Enlace / Descargar' || norm === 'descargar') {
          const dlPrompt = '📥 <b>PEGA AQUÍ CUALQUIER ENLACE PARA DESCARGAR</b>\n\n' +
            '• 🌐 <b>Archivos Directos:</b> ISO, RAR, ZIP, EXE, MKV...\n' +
            '• 📦 <b>Google Drive:</b> Carpetas o archivos compartidos por terceros\n' +
            '• 🧲 <b>Torrents / Magnets:</b> Enlaces <code>magnet:?xt=...</code>\n' +
            '• 🔴 <b>MEGA.nz / TeraBox:</b> Descargas a máxima velocidad\n\n' +
            '⚡ <i>Azure transferirá los archivos a 1.5 - 2.0 Gbps directo a tu Google Drive sin que tu PC esté encendida.</i>';
          await sendTG(botToken, chatId, dlPrompt);
          return new Response('OK', { status: 200 });
        }

        if (text === '🤝 Compartir Carpeta' || norm === '/compartir' || norm === 'compartir') {
          const sharePrompt = '🤝 <b>COMPARTIR CARPETAS DE GOOGLE DRIVE AL INSTANTE</b>\n\n' +
            'Comparte con cualquier amigo o cliente <b>solo con su correo Gmail</b>.\n' +
            '• No necesitan Rclone ni contraseñas.\n' +
            '• Les aparece en 1.5 segundos en <b>Compartido conmigo</b>.\n' +
            '• Consumo de cuota cero para ellos.\n\n' +
            '📁 <i>Para compartir desde aquí, escribe: <code>/compartir amigo@gmail.com</code></i>';
          await sendTG(botToken, chatId, sharePrompt);
          return new Response('OK', { status: 200 });
        }

        if (text === '📊 Estado de Descargas' || norm === '/status' || norm.includes('como va') || norm.includes('estado')) {
          await handleStatus(botToken, chatId, repo, pat);
          return new Response('OK', { status: 200 });
        }

        if (text === '👥 Ver Permisos' || norm === '/permisos' || norm.includes('permiso')) {
          await sendTG(botToken, chatId, '👥 <b>Consulta de Permisos:</b>\nPara ver permisos en tiempo real o revocar accesos por API directa, abre <code>iniciar_bot_telegram_pc.bat</code> en tu PC o usa el bot local.');
          return new Response('OK', { status: 200 });
        }

        if (text === '🔄 Sincronizar Megapack' || norm === '/sync' || norm.includes('sincroniz')) {
          await triggerSync(botToken, chatId, repo, pat);
          return new Response('OK', { status: 200 });
        }

        if (text === '🧠 Asistente IA' || norm === '/ia' || norm === 'ayuda') {
          const aiPrompt = '🧠 <b>ASISTENTE INTELIGENTE OMNICLOUD (SUPER-IA)</b>\n\n' +
            '🔥 <b>¿Qué puedo hacer por ti?</b>\n' +
            '• <b>Buscar los mejores proyectos:</b> Escribe <i>"busca los mejores proyectos de IA"</i> o <i>"proyectos de Python"</i>.\n' +
            '• <b>Investigar conceptos:</b> Pregúntame qué es cualquier tecnología o arquitectura.\n' +
            '• <b>Dudas de tu sistema:</b> Velocidades, formateo o uso de archivos.\n\n' +
            '👇 <b>Toca una opción rápida o escribe lo que desees en el chat:</b>';
          const kbd = {
            inline_keyboard: [
              [{ text: '🔍 Buscar Proyectos de IA en GitHub', callback_data: 'ai:search:artificial intelligence agents' }],
              [{ text: '🔍 Buscar Proyectos de Python en GitHub', callback_data: 'ai:search:python tools automation' }],
              [{ text: '⏱️ ¿Cuánto tardan 300GB, 500GB o 1TB?', callback_data: 'ai:faq:TIMING' }],
              [{ text: '🛡️ ¿Qué pasa si formateo mi PC?', callback_data: 'ai:faq:FORMATTING' }],
              [{ text: '📦 ¿Cómo se usa el auto-unidor .bat?', callback_data: 'ai:faq:JOINING' }]
            ]
          };
          await sendTG(botToken, chatId, aiPrompt, kbd);
          return new Response('OK', { status: 200 });
        }

        // Búsqueda de proyectos en GitHub (Live Search)
        if (norm.match(/\b(busca|buscar|encuentra|mejores|top)\b.*\b(proyectos|repositorios|github|herramientas|librerias)\b|\b(proyectos de|repos de)\b/)) {
          await sendTG(botToken, chatId, '🔍 <b>Consultando la base global de GitHub en tiempo real...</b>');
          const ghRes = await searchGitHub(text, pat);
          await sendTG(botToken, chatId, ghRes);
          return new Response('OK', { status: 200 });
        }

        // Preguntas Conceptuales / Wikipedia
        if (norm.match(/\b(que es|quien es|definicion de|concepto de|explica que es)\b/)) {
          const wikiRes = await searchWiki(text);
          if (wikiRes) {
            await sendTG(botToken, chatId, wikiRes);
            return new Response('OK', { status: 200 });
          }
        }

        // Bienvenida
        if (text === '/start' || text === '/help' || norm === 'hola' || norm === 'menu') {
          const welcome = '👑 <b>Centro de Control OmniCloud Core 2.0 (Cloudflare Edge 24/7)</b>\n\n' +
            'Descargas ultrarrápidas a 1.5 - 2.0 Gbps en la nube Azure con tu <b>PC 100% apagada</b>, Inteligencia Artificial y gestión de Google Drive.\n\n' +
            '👇 <b>Toca cualquiera de los botones grandes de abajo para empezar:</b>';
          await sendTG(botToken, chatId, welcome);
          return new Response('OK', { status: 200 });
        }

        // Preguntas Frecuentes por Lenguaje Natural
        if (norm.includes('cuanto tarda') || norm.includes('500 gb') || norm.includes('1 tb')) {
          await sendTG(botToken, chatId, getFaqAnswer('TIMING'));
          return new Response('OK', { status: 200 });
        }
        if (norm.includes('formate') || norm.includes('borra mi pc')) {
          await sendTG(botToken, chatId, getFaqAnswer('FORMATTING'));
          return new Response('OK', { status: 200 });
        }
        if (norm.includes('como un') || norm.includes('abrir') || norm.includes('bat') || norm.includes('001')) {
          await sendTG(botToken, chatId, getFaqAnswer('JOINING'));
          return new Response('OK', { status: 200 });
        }

        // Detección de Enlaces (HTTP, HTTPS, Magnet, Drive)
        if (text.startsWith('http://') || text.startsWith('https://') || text.startsWith('magnet:') || text.endsWith('.torrent')) {
          const isBig = text.match(/\.(iso|rar|zip|tar|7z|img|mkv)($|\?)/i);
          const isDrive = text.includes('drive.google.com');

          let reply = '📦 <b>Enlace Detectado:</b>\n<code>' + escapeHtml(text.slice(0, 100)) + '</code>\n\n';
          if (isDrive) {
            reply += '📁 <b>Google Drive detectado:</b> Puedes clonarlo directamente de nube a nube sin que pase por tu PC.\n\n';
          }
          reply += '🎯 <b>Selecciona el destino:</b>';

          const buttons = [
            [{ text: '🚀 Google Drive (Rotación Julio + Vexor 10TB)', callback_data: 'd:rot' }]
          ];
          if (isBig) {
            buttons.push([{ text: '⚡ Modo Swarm Multi-Nodo (30GB en <4m)', callback_data: 'd:swarm' }]);
          }
          buttons.push(
            [
              { text: '📁 Julio (5TB)', callback_data: 'd:jul' },
              { text: '📁 Vexor (5TB)', callback_data: 'd:vex' }
            ],
            [
              { text: '☁️ OneDrive', callback_data: 'd:one' },
              { text: '🔴 MEGA.nz', callback_data: 'd:meg' }
            ]
          );

          await sendTG(botToken, chatId, reply, { inline_keyboard: buttons });
          return new Response('OK', { status: 200 });
        }

        // Consulta a Gemini AI si hay clave configurada
        if (geminiKey) {
          const geminiResp = await callGemini(geminiKey, text);
          if (geminiResp) {
            await sendTG(botToken, chatId, `🤖 <b>OmniCloud AI:</b>\n\n${geminiResp}`);
            return new Response('OK', { status: 200 });
          }
        }

        // Si parece tema de programación, buscar automáticamente en GitHub
        if (norm.match(/\b(python|javascript|react|flutter|ia|ai|scraping|docker|api|cloud)\b/)) {
          const ghAuto = await searchGitHub(text, pat);
          if (ghAuto && ghAuto.includes('🏆')) {
            await sendTG(botToken, chatId, ghAuto);
            return new Response('OK', { status: 200 });
          }
        }

        await sendTG(botToken, chatId, 'ℹ️ Envíame un enlace para descargar, o escribe por ejemplo: <i>"busca los mejores proyectos de IA"</i>.');
      }

      // 2. Callback Queries (Botones Táctiles)
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
        } else if (data.startsWith('ai:search:')) {
          const q = data.split('ai:search:')[1];
          await sendTG(botToken, chatId, `🔍 <b>Buscando proyectos de '${q}' en GitHub...</b>`);
          const ghRes = await searchGitHub(q, pat);
          await sendTG(botToken, chatId, ghRes);
        } else if (data.startsWith('ai:faq:')) {
          const topic = data.split('ai:faq:')[1];
          await sendTG(botToken, chatId, getFaqAnswer(topic));
        } else if (data.startsWith('d:')) {
          let target = 'Google Drive (Rotación Inteligente: Julio + Vexor 10TB)';
          if (data === 'd:jul') target = 'Google Drive (Mi Unidad Principal - Julio)';
          if (data === 'd:vex') target = 'Google Drive (Unidad Auxiliar - Vexor)';
          if (data === 'd:one') target = 'Microsoft OneDrive (Aviso: Throttling 429)';
          if (data === 'd:meg') target = 'MEGA.nz';

          const origText = cq.message.text || '';
          const match = origText.match(/Enlace Detectado:\s*([\s\S]+?)(?:\n\n🎯|$)/);
          const fullUrl = match ? match[1].trim() : '';

          if (data === 'd:swarm') {
            await triggerSwarm(botToken, chatId, repo, pat);
          } else if (fullUrl) {
            await triggerDownload(botToken, chatId, repo, pat, fullUrl, target);
          } else {
            await sendTG(botToken, chatId, '⚠️ No se pudo extraer la URL. Por favor vuelve a enviarla por texto.');
          }
        }

        await fetch(`https://api.telegram.org/bot${botToken}/answerCallbackQuery?callback_query_id=${cq.id}`).catch(() => {});
      }

      return new Response('OK', { status: 200 });
    } catch (err) {
      return new Response('Error: ' + err.message, { status: 200 });
    }
  }
};

async function searchGitHub(query, pat = null) {
  try {
    const cleanQ = query.replace(/\b(busca|buscar|encuentra|mejores|los|de|para|proyectos|repositorios|github|top|herramientas|librerias|frameworks)\b/gi, '').trim() || query;
    const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(cleanQ)}&sort=stars&order=desc&per_page=5`;
    const headers = { 'User-Agent': 'OmniCloud-AI-Bot', 'Accept': 'application/vnd.github+json' };
    if (pat) headers['Authorization'] = `Bearer ${pat}`;

    const res = await fetch(url, { headers });
    const data = await res.json();
    const items = data.items || [];
    if (items.length === 0) return 'ℹ️ No se encontraron repositorios para esa búsqueda.';

    let msg = `🏆 <b>LOS MEJORES PROYECTOS EN GITHUB (${cleanQ.toUpperCase()}):</b>\n\n`;
    items.forEach((it, idx) => {
      const desc = it.description || 'Sin descripción disponible';
      msg += `<b>${idx + 1}. <a href='${it.html_url}'>${it.full_name}</a></b>\n`;
      msg += `⭐ <b>${it.stargazers_count.toLocaleString()} estrellas</b> | 🍴 ${it.forks_count.toLocaleString()} forks | 💻 <code>${it.language || 'General'}</code>\n`;
      msg += `📝 <i>${escapeHtml(desc.slice(0, 160))}...</i>\n\n`;
    });
    msg += '💡 <i>Toca cualquier enlace para abrir el repositorio directamente en GitHub.</i>';
    return msg;
  } catch (e) {
    return '❌ Error al consultar GitHub: ' + e.message;
  }
}

async function searchWiki(query) {
  try {
    const cleanQ = query.replace(/\b(que es|quien es|definicion de|concepto de|explica que es)\b/gi, '').trim() || query;
    const url = `https://es.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(cleanQ.replace(/ /g, '_'))}`;
    const res = await fetch(url, { headers: { 'User-Agent': 'OmniCloudBot/2.0' } });
    if (!res.ok) return null;
    const data = await res.json();
    if (data.extract) {
      return `📖 <b>${escapeHtml(data.title)}</b>\n\n${escapeHtml(data.extract)}\n\n🔗 <a href='${data.content_urls?.desktop?.page || ''}'>Leer artículo en Wikipedia</a>`;
    }
    return null;
  } catch {
    return null;
  }
}

function getFaqAnswer(topic) {
  if (topic === 'TIMING') {
    return '⏱️ <b>TIEMPOS CERTIFICADOS DE TRANSFERENCIA</b>\n\n' +
      '<b>1. Drive a Drive (Server-Side):</b>\n• 300 GB: ~30s\n• 500 GB: ~45s\n• 1 TB: ~1.5m\n\n' +
      '<b>2. Compartir Carpeta (/compartir):</b> <b>1.5 segundos</b> para cualquier tamaño.\n\n' +
      '<b>3. Azure Swarm (Internet a Drive):</b>\n• 300 GB: ~16 min\n• 500 GB: ~27 min\n• 1 TB: ~55 min\n\n' +
      '💡 <i>Tu PC puede estar 100% apagada.</i>';
  } else if (topic === 'FORMATTING') {
    return '🛡️ <b>PROTECCIÓN CONTRA FORMATEO</b>\n\n' +
      '¡Nada se borra ni se detiene!\n' +
      '1. Azure y GitHub funcionan en internet 24/7 con tu PC apagada.\n' +
      '2. Tu disco D: no se borra al formatear C:.\n' +
      '3. Con doble clic en <code>restaurar_tras_formateo.bat</code> todo se restaura en 60 segundos.';
  } else if (topic === 'JOINING') {
    return '📦 <b>¿CÓMO UNEN LOS ARCHIVOS TUS AMIGOS?</b>\n\n' +
      'OmniCloud deposita automáticamente en su carpeta:\n' +
      '👉 <b>DOBLE_CLIC_AQUI_PARA_UNIR.bat</b>\n\n' +
      'Ellos solo hacen doble clic en Windows y en 5 segundos se ensambla y se monta como disco virtual sin saber de comandos.';
  }
  return 'ℹ️ Escribe lo que necesites y te orientaré.';
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function sendTG(token, chatId, text, keyboard = null) {
  const body = {
    chat_id: chatId,
    text: text,
    parse_mode: 'HTML'
  };
  body.reply_markup = keyboard || MAIN_KEYBOARD;
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
      msg += `${icon} <b>${escapeHtml(r.name || 'Tarea')}</b>\nEstado: <code>${r.status} (${r.conclusion || 'en curso'})</code>\nID: <code>${r.id}</code>\n\n`;
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
    await sendTG(token, chatId, '🔄 Disparando verificación del Megapack en Azure...');
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
      await sendTG(token, chatId, '✅ ¡Auto-sincronizador lanzado en la nube! Te avisaré si encuentra archivos nuevos.');
    } else {
      await sendTG(token, chatId, `⚠️ Respuesta de GitHub (Status ${res.status})`);
    }
  } catch (e) {
    await sendTG(token, chatId, '❌ Error al disparar sync: ' + e.message);
  }
}

async function triggerSwarm(token, chatId, repo, pat) {
  try {
    if (!pat) {
      await sendTG(token, chatId, '⚠️ GITHUB_PAT no configurado en Cloudflare Workers.');
      return;
    }
    await sendTG(token, chatId, '⚡ <b>Desplegando Enjambre Swarm Multi-Nodo en Azure Cloud...</b>\n4 nodos concurrentes descargarán a máxima velocidad.');
    const res = await fetch(`https://api.github.com/repos/${repo}/actions/workflows/omniengine_universal.yml/dispatches`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${pat}`,
        'User-Agent': 'OmniCloud-Telegram-Bot',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ref: 'main',
        inputs: { mode: 'external_monolithic_range_swarm' }
      })
    });
    if (res.status === 204) {
      await sendTG(token, chatId, '🎉 <b>¡Enjambre Swarm Lanzado!</b>\nLos 4 nodos de Azure están trabajando en paralelo.');
    } else {
      await sendTG(token, chatId, `⚠️ Error al lanzar enjambre (Status ${res.status}).`);
    }
  } catch (e) {
    await sendTG(token, chatId, '❌ Error: ' + e.message);
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
      await sendTG(token, chatId, '🎉 <b>¡Descarga en marcha a 1.5 Gbps!</b>\nLos servidores de Azure están transfiriendo tus archivos. Sonará una notificación push cuando finalice.');
    } else {
      await sendTG(token, chatId, `⚠️ Error al iniciar descarga en GitHub (Status ${res.status}).`);
    }
  } catch (e) {
    await sendTG(token, chatId, '❌ Error al conectar con GitHub: ' + e.message);
  }
}

async function callGemini(apiKey, prompt) {
  try {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
    const payload = {
      contents: [{ role: 'user', parts: [{ text: prompt }] }]
    };
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text?.replace(/\*\*/g, '<b>') || null;
  } catch {
    return null;
  }
}
