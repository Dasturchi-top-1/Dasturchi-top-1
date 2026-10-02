// ============================================================
// ⚡ BLIP AI WORKER v3.1 — Parol bilan himoyalangan
// ============================================================

const SYSTEM = `Sen Blip Agent — Telegram bot orqali ishlovchi AI yordamchisan.

FOYDALANUVCHI HAQIDA:
- Ism: Blip (Salohiddin)
- Joy: Tojikiston, Dushanbe
- Yosh: 13
- Til: O'zbek (lotin)
- Loyihalar: Blip Order Bot, DeepSeek Agent, CyberHub, Blip AI
- GitHub: Dasturchi-top-1

VAZIFA:
O'zbek tilida (lotin) qisqa va aniq javob ber.
Buyruq kutma — oddiy xabarga ham javob ber.
Kerak bo'lsa tool ishlat (vaqt, hisoblash, eslatma).`;

const COUNCIL_SYSTEM = `Sen aqlli va dono yordamchisan.
O'zbek tilida (lotin) qisqa va aniq javob ber (3-5 gap).
Faqat savolga javob ber, ortiqcha gapirma.`;

const JUDGE_SYSTEM = `Sen AI Kengashning dono raisisisan.
5 ta AI javobini tahlil qilib, O'ZBEK TILIDA qisqa umumiy xulosa yoz (5-7 gap).
Eng yaxshi fikrlarni birlashtir, qarama-qarshiliklarni ajrat.`;

// 🔐 KENGASH PAROLI
const COUNCIL_PAROL = "SALOXIDDINJON UMARJON ENEM VA OILA";

const TOOLS = [
  { type: "function", function: {
    name: "get_time", description: "Hozirgi vaqtni oladi",
    parameters: { type: "object", properties: {} } } },
  { type: "function", function: {
    name: "calc", description: "Matematik ifodani hisoblaydi",
    parameters: { type: "object", properties: { expr: { type: "string" } }, required: ["expr"] } } },
  { type: "function", function: {
    name: "save_note", description: "Eslatma saqlaydi",
    parameters: { type: "object", properties: { text: { type: "string" } }, required: ["text"] } } },
  { type: "function", function: {
    name: "get_notes", description: "Eslatmalarni oladi",
    parameters: { type: "object", properties: {} } } },
  { type: "function", function: {
    name: "del_note", description: "Eslatmani o'chiradi",
    parameters: { type: "object", properties: { num: { type: "number" } }, required: ["num"] } } }
];

const COUNCIL_MODELS = [
  { id: "qwen/qwen3.6-plus-preview:free", name: "Qwen3.6", emoji: "🌟" },
  { id: "nvidia/nemotron-3-ultra-550b-a55b:free", name: "Nemotron", emoji: "🧠" },
  { id: "stepfun/step-3.5-flash:free", name: "StepFun", emoji: "⚡" },
  { id: "liquid/lfm-2.5-2.6b:free", name: "LFM", emoji: "🌪" },
  { id: "meta-llama/llama-3.3-70b-instruct:free", name: "Llama 3.3", emoji: "🦙" }
];

// ============================================================
// 🛠 TOOL'LAR
// ============================================================
async function runTool(name, args, env, chatId) {
  try {
    if (name === "get_time")
      return new Date().toLocaleString("uz-UZ", { timeZone: "Asia/Dushanbe" });
    if (name === "calc") {
      const allowed = "0123456789+-*/(). ";
      if (![...args.expr].every(c => allowed.includes(c))) return "Xato: faqat raqam";
      return String(new Function("return (" + args.expr + ")")());
    }
    if (name === "save_note") {
      const k = "notes:" + chatId;
      const list = JSON.parse(await env.AGENT_KV.get(k) || "[]");
      list.push({ text: args.text, at: Date.now() });
      await env.AGENT_KV.put(k, JSON.stringify(list));
      return "Saqlandi. Jami: " + list.length;
    }
    if (name === "get_notes") {
      const list = JSON.parse(await env.AGENT_KV.get("notes:" + chatId) || "[]");
      return list.length ? list.map((n, i) => (i+1) + ". " + n.text).join("\n") : "Bo'sh.";
    }
    if (name === "del_note") {
      const k = "notes:" + chatId;
      const list = JSON.parse(await env.AGENT_KV.get(k) || "[]");
      if (args.num < 1 || args.num > list.length) return "Bunday raqam yo'q";
      const removed = list.splice(args.num - 1, 1);
      await env.AGENT_KV.put(k, JSON.stringify(list));
      return "O'chirildi: " + removed[0].text;
    }
    return "Noma'lum tool";
  } catch (e) { return "Xato: " + e.message; }
}

// ============================================================
// 🤖 AI
// ============================================================
async function callAI(messages, env, useTools = true) {
  const payload = {
    model: "qwen/qwen3.6-plus-preview:free",
    messages: messages
  };
  if (useTools) {
    payload.tools = TOOLS;
    payload.tool_choice = "auto";
  }
  const r = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + env.OPENROUTER_API_KEY,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
  return await r.json();
}

async function agentLoop(userMsg, chatId, env) {
  const key = "hist:" + chatId;
  let history = JSON.parse(await env.AGENT_KV.get(key) || "[]");
  if (!history.length) history.push({ role: "system", content: SYSTEM });
  history.push({ role: "user", content: userMsg });

  let reply = "", steps = 0;
  while (steps < 5) {
    steps++;
    const data = await callAI(history, env, true);
    const msg = data.choices?.[0]?.message;
    if (!msg) { reply = "AI javob bermadi."; break; }

    if (msg.tool_calls?.length) {
      history.push(msg);
      for (const tc of msg.tool_calls) {
        const args = JSON.parse(tc.function.arguments || "{}");
        const out = await runTool(tc.function.name, args, env, chatId);
        history.push({ role: "tool", tool_call_id: tc.id, content: String(out) });
      }
      continue;
    }
    reply = msg.content || "";
    history.push({ role: "assistant", content: reply });
    break;
  }

  if (history.length > 40) history = [history[0], ...history.slice(-39)];
  await env.AGENT_KV.put(key, JSON.stringify(history));
  return reply || "Javob bo'sh.";
}

// ============================================================
// 📤 TELEGRAM
// ============================================================
async function sendTg(chatId, text, env) {
  for (let i = 0; i < text.length; i += 4000) {
    await fetch("https://api.telegram.org/bot" + env.TELEGRAM_TOKEN + "/sendMessage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, text: text.slice(i, i+4000) })
    });
  }
}

async function sendTyping(chatId, env) {
  try {
    await fetch("https://api.telegram.org/bot" + env.TELEGRAM_TOKEN + "/sendChatAction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, action: "typing" })
    });
  } catch {}
}

// ============================================================
// 🌐 CORS
// ============================================================
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type"
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { ...CORS, "Content-Type": "application/json" }
  });
}

// ============================================================
// 🚀 MAIN
// ============================================================
export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // ============================================================
    // 🏛 AI COUNCIL (parol bilan)
    // ============================================================
    if (path === "/council" && request.method === "POST") {
      try {
        const body = await request.json();
        const question = (body.question || "").trim();
        const parol = (body.parol || "").trim();

        // 🔐 Parol tekshirish
        if (parol !== COUNCIL_PAROL) {
          return json({ error: "🔐 Parol xato! Faqat Blip uchun." }, 403);
        }

        if (!question) return json({ error: "Savol yo'q" }, 400);
        if (question.length > 2000) return json({ error: "Savol juda uzun" }, 400);

        // 5 ta AI parallel
        const promises = COUNCIL_MODELS.map(m =>
          fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": "Bearer " + env.OPENROUTER_API_KEY,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: m.id,
              messages: [
                { role: "system", content: COUNCIL_SYSTEM },
                { role: "user", content: question }
              ],
              max_tokens: 500,
              temperature: 0.7
            })
          })
          .then(r => r.json())
          .then(d => ({
            emoji: m.emoji,
            name: m.name,
            answer: d.choices?.[0]?.message?.content || "Javob olinmadi"
          }))
          .catch(e => ({
            emoji: m.emoji,
            name: m.name,
            answer: "❌ Xato: " + e.message
          }))
        );

        const answers = await Promise.all(promises);

        // Rais xulosasi
        const judgePrompt = `Savol: "${question}"

5 ta AI javob berdi:

${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}

Sen AI Kengash raisisan. Yuqoridagi javoblarni tahlil qilib, umumiy xulosa yoz (5-7 gap).`;

        const judgeRes = await fetch("https://openrouter.ai/api/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + env.OPENROUTER_API_KEY,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "qwen/qwen3.6-plus-preview:free",
            messages: [
              { role: "system", content: JUDGE_SYSTEM },
              { role: "user", content: judgePrompt }
            ],
            max_tokens: 700,
            temperature: 0.7
          })
        });
        const jd = await judgeRes.json();
        const conclusion = jd.choices?.[0]?.message?.content || "Xulosa olinmadi";

        return json({ answers, conclusion });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 💬 SAYT UCHUN API
    // ============================================================
    if (path === "/api" && request.method === "POST") {
      try {
        const body = await request.json();
        if (!body.message) return json({ error: "message yo'q" }, 400);
        const reply = await agentLoop(body.message, body.sid || "web", env);
        return json({ reply });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 🤖 TELEGRAM WEBHOOK
    // ============================================================
    if (path === "/webhook" && request.method === "POST") {
      let update;
      try { update = await request.json(); } catch { return new Response("ok"); }

      const msg = update.message || update.edited_message;
      if (!msg || !msg.text) return new Response("ok");

      const chatId = msg.chat.id;
      const text = msg.text.trim();
      const name = msg.chat.first_name || "Blip";

      if (text === "/start") {
        await sendTg(chatId,
          `Salom ${name}! 👋\n\nMen Blip Agent — AI yordamching.\n\n/reset — tozalash\n/notes — eslatmalar\n/help — yordam`, env);
        return new Response("ok");
      }
      if (text === "/reset") {
        await env.AGENT_KV.delete("hist:" + chatId);
        await sendTg(chatId, "🧹 Tozalandi.", env);
        return new Response("ok");
      }
      if (text === "/help") {
        await sendTg(chatId, `🤖 Blip Agent\n\n/reset — tozalash\n/notes — eslatmalar\n/help — yordam`, env);
        return new Response("ok");
      }

      try {
        await sendTyping(chatId, env);
        const reply = await agentLoop(text, chatId, env);
        await sendTg(chatId, reply, env);
      } catch (e) {
        await sendTg(chatId, "❌ Xato: " + e.message, env);
      }
      return new Response("ok");
    }

    // ============================================================
    // 🏠 HEALTH CHECK
    // ============================================================
    return new Response("Blip AI v3.1 ishlayapti ✅\n\nEndpoints:\n/api\n/council 🔐\n/webhook", {
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
};
<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Council — Blip</title>
<style>
  :root{
    --bg:#0a0a1a;--card:#141428;--text:#e6e6f0;--muted:#8888aa;
    --accent:#6366f1;--accent2:#a855f7;--border:#2a2a44;
    --gold:#fbbf24;--red:#ef4444;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  body{
    font-family:system-ui,sans-serif;background:var(--bg);color:var(--text);
    min-height:100vh;padding:20px;
    background-image:radial-gradient(circle at 20% 10%,rgba(99,102,241,.15),transparent 50%),
                     radial-gradient(circle at 80% 90%,rgba(168,85,247,.15),transparent 50%);
  }
  .container{max-width:900px;margin:auto}
  header{text-align:center;padding:40px 0 30px}
  h1{
    font-size:42px;font-weight:900;
    background:linear-gradient(90deg,#6366f1,#a855f7,#6366f1);
    background-size:200% 200%;-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;animation:grad 4s ease infinite;
  }
  @keyframes grad{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
  .sub{color:var(--muted);margin-top:8px;font-size:15px}
  .badges{display:flex;gap:8px;justify-content:center;margin-top:16px;flex-wrap:wrap}
  .badge{font-size:12px;padding:4px 10px;border:1px solid var(--border);
         border-radius:999px;color:var(--muted)}
  .ask{background:var(--card);border:1px solid var(--border);border-radius:16px;
       padding:16px;margin-bottom:24px}
  input[type="password"]{
    width:100%;padding:12px;border-radius:10px;border:1px solid var(--border);
    background:var(--bg);color:var(--text);font-size:15px;margin-bottom:10px;outline:none
  }
  input[type="password"]:focus{border-color:var(--accent)}
  textarea{
    width:100%;padding:14px;border-radius:10px;border:1px solid var(--border);
    background:var(--bg);color:var(--text);font-size:15px;font-family:inherit;
    resize:vertical;min-height:80px;outline:none
  }
  textarea:focus{border-color:var(--accent)}
  .row{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}
  .examples{display:flex;gap:6px;flex-wrap:wrap;flex:1}
  .ex{font-size:12px;padding:6px 12px;border-radius:999px;background:var(--bg);
      border:1px solid var(--border);color:var(--muted);cursor:pointer}
  .ex:hover{border-color:var(--accent);color:var(--accent)}
  #askBtn{
    padding:12px 28px;border:none;border-radius:10px;cursor:pointer;
    background:linear-gradient(90deg,var(--accent),var(--accent2));
    color:#fff;font-weight:700;font-size:15px
  }
  #askBtn:disabled{opacity:.5;cursor:wait}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
        gap:12px;margin-bottom:24px}
  .ai-card{
    background:var(--card);border:1px solid var(--border);border-radius:14px;
    padding:16px;animation:fade .4s ease
  }
  .ai-head{display:flex;align-items:center;gap:8px;margin-bottom:10px}
  .ai-emoji{font-size:22px}
  .ai-name{font-weight:700;font-size:14px}
  .ai-text{font-size:13px;line-height:1.6;color:#c8c8dc;white-space:pre-wrap}
  .council{
    background:linear-gradient(135deg,rgba(251,191,36,.1),rgba(168,85,247,.1));
    border:2px solid var(--gold);border-radius:16px;padding:24px;
    animation:fade .6s ease
  }
  .council-head{display:flex;align-items:center;gap:10px;margin-bottom:14px}
  .council-title{font-size:18px;font-weight:800;color:var(--gold)}
  .council-text{font-size:15px;line-height:1.7;white-space:pre-wrap}
  @keyframes fade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  .loading{text-align:center;padding:40px;color:var(--muted)}
  .error{text-align:center;padding:20px;color:var(--red)}
  .dots::after{content:'...';animation:dots 1.5s steps(4) infinite}
  @keyframes dots{0%{content:'.'}33%{content:'..'}66%{content:'...'}}
  footer{text-align:center;padding:30px;color:var(--muted);font-size:12px;margin-top:20px}
  footer a{color:var(--accent);text-decoration:none}
  @media(max-width:600px){h1{font-size:30px}header{padding:20px 0}}
</style>
</head>
<body>
<div class="container">

<header>
  <h1>🏛 AI KENGASH</h1>
  <p class="sub">Bitta savol — 5 ta AI javob — 1 ta dono xulosa</p>
  <div class="badges">
    <span class="badge">🌟 Qwen3.6</span>
    <span class="badge">🧠 Nemotron</span>
    <span class="badge">⚡ StepFun</span>
    <span class="badge">🌪 LFM</span>
    <span class="badge">🦙 Llama 3.3</span>
  </div>
</header>

<div class="ask">
  <input type="password" id="parol" placeholder="🔐 Parol..." autocomplete="off">
  <textarea id="q" placeholder="Savolingizni yozing... Masalan: 'Kelajakda AI qanday bo'ladi?'"></textarea>
  <div class="row">
    <div class="examples">
      <span class="ex" onclick="fill('Hayotning ma\'nosi nima?')">Hayot ma'nosi</span>
      <span class="ex" onclick="fill('Eng yaxshi dasturlash tili?')">Dasturlash tili</span>
      <span class="ex" onclick="fill('Kelajakda AI qanday bo\'ladi?')">AI kelajagi</span>
      <span class="ex" onclick="fill('13 yoshda qanday dasturchi bo\'lish mumkin?')">Dasturchi bo'lish</span>
    </div>
    <button id="askBtn" onclick="ask()">Kengashni chaqirish</button>
  </div>
</div>

<div id="out"></div>

<footer>
  ⚡ <a href="https://dasturchi-top-1.github.io/Dasturchi-top-1/">Blip AI</a> tomonidan yaratildi · 2026
</footer>

</div>

<script>
const API = "https://dasturchi-ai-proxy.sulhiyahasanova1.workers.dev/council";

// Parolni eslab qolish
window.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('council_parol');
  if (saved) document.getElementById('parol').value = saved;
  document.getElementById('parol').addEventListener('change', (e) => {
    localStorage.setItem('council_parol', e.target.value);
  });
});

function fill(t){ document.getElementById('q').value = t; }

async function ask(){
  const q = document.getElementById('q').value.trim();
  const parol = document.getElementById('parol').value.trim();
  const btn = document.getElementById('askBtn');
  const out = document.getElementById('out');

  if(!parol){
    out.innerHTML = '<div class="error">🔐 Parolni kiriting!</div>';
    return;
  }
  if(!q){
    out.innerHTML = '<div class="error">❓ Savolni yozing!</div>';
    return;
  }

  // Parolni saqlash
  localStorage.setItem('council_parol', parol);

  btn.disabled = true;
  btn.textContent = '⏳ Kengash yig\'ilmoqda...';
  out.innerHTML = '<div class="loading">🤖 5 ta AI o\'ylayapti<span class="dots"></span></div>';

  try{
    const r = await fetch(API, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ question: q, parol: parol })
    });
    const d = await r.json();

    if(!r.ok || d.error){
      out.innerHTML = '<div class="error">' + (d.error || 'Xato') + '</div>';
      return;
    }

    let html = '<div class="grid">';
    d.answers.forEach(a => {
      html += `<div class="ai-card">
        <div class="ai-head">
          <span class="ai-emoji">${a.emoji}</span>
          <span class="ai-name">${a.name}</span>
        </div>
        <div class="ai-text">${esc(a.answer)}</div>
      </div>`;
    });
    html += '</div>';

    html += `<div class="council">
      <div class="council-head">
        <span style="font-size:28px">🏛</span>
        <span class="council-title">KENGASH XULOSASI</span>
      </div>
      <div class="council-text">${esc(d.conclusion)}</div>
    </div>`;

    out.innerHTML = html;
  } catch(e){
    out.innerHTML = '<div class="error">❌ Xato: ' + e.message + '</div>';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Kengashni chaqirish';
  }
}

function esc(s){
  return (s || '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}
</script>
</body>
</html>
