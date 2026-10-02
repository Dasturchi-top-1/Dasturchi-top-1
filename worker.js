// ============================================================
// ⚡ BLIP AI WORKER v3.0 — Telegram + Sayt + AI Council
// ============================================================

const SYSTEM = `Sen Blip Agent — Telegram bot orqali ishlovchi AI yordamchisan.

FOYDALANUVCHI HAQIDA:
- Ism: Blip (Salohiddin)
- Joy: Tojikiston, Dushanbe
- Yosh: 13
- Til: O'zbek (lotin)
- Muhit: Pydroid 3, Termux, Cloudflare
- Loyihalar: Blip Order Bot, DeepSeek Agent, CyberHub, Blip AI
- Telegram: @BLIP_KIBER_XAFSIZLIK
- GitHub: Dasturchi-top-1

VAZIFA:
O'zbek tilida (lotin) qisqa va aniq javob ber.
Buyruq kutma — oddiy xabarga ham javob ber.
Kerak bo'lsa tool ishlat (vaqt, hisoblash, eslatma).

XARAKTER:
Do'stona, samimiy, yoshga mos. Blip deb chaqir.`;

const COUNCIL_SYSTEM = `Sen aqlli va dono yordamchisan.
O'zbek tilida (lotin) qisqa va aniq javob ber (3-5 gap).
Faqat savolga javob ber, ortiqcha gapirma.`;

const JUDGE_SYSTEM = `Sen AI Kengashning dono raisisisan.
5 ta AI javobini tahlil qilib, O'ZBEK TILIDA qisqa umumiy xulosa yoz (5-7 gap).
Eng yaxshi fikrlarni birlashtir, qarama-qarshiliklarni ajrat.`;

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
    name: "del_note", description: "Eslatmani o'chiradi (raqami bilan)",
    parameters: { type: "object", properties: { num: { type: "number" } }, required: ["num"] } } }
];

const COUNCIL_MODELS = [
  { id: "openai/gpt-4o-mini", name: "GPT-4o Mini", emoji: "🤖" },
  { id: "google/gemini-2.5-flash-lite", name: "Gemini Flash", emoji: "🧠" },
  { id: "anthropic/claude-3-haiku", name: "Claude Haiku", emoji: "🎭" },
  { id: "deepseek/deepseek-chat", name: "DeepSeek", emoji: "⚡" },
  { id: "meta-llama/llama-3.3-70b-instruct", name: "Llama 3.3", emoji: "🦙" }
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
      if (![...args.expr].every(c => allowed.includes(c))) return "Xato: faqat raqam va belgilar";
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
    model: "openai/gpt-4o-mini",
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

  const statKey = "stats:" + chatId;
  const s = JSON.parse(await env.AGENT_KV.get(statKey) || '{"msgs":0,"start":0}');
  s.msgs = (s.msgs || 0) + 1;
  if (!s.start) s.start = Date.now();
  await env.AGENT_KV.put(statKey, JSON.stringify(s));

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
    // 🏛 AI COUNCIL — 5 ta AI birga javob beradi
    // ============================================================
    if (path === "/council" && request.method === "POST") {
      try {
        const body = await request.json();
        const question = (body.question || "").trim();
        if (!question) return json({ error: "Savol yo'q" }, 400);
        if (question.length > 2000) return json({ error: "Savol juda uzun" }, 400);

        // 5 ta AI parallel javob beradi
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

        // Rais — umumiy xulosa
        const judgePrompt = `Savol: "${question}"

5 ta AI quyidagicha javob berdi:

${answers.map((a, i) => `${i+1}. ${a.name} ${a.emoji}:\n${a.answer}`).join("\n\n")}

Sen AI Kengash raisisan. Yuqoridagi javoblarni tahlil qilib:
- Umumiy fikrlarni ajrat
- Muhim nuqtalarni ko'rsat
- Yakuniy xulosa yoz (5-7 gap)

Faqat xulosani yoz.`;

        const judgeRes = await fetch("https://openrouter.ai/api/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + env.OPENROUTER_API_KEY,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "openai/gpt-4o-mini",
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
    // 💬 SAYT UCHUN API (chat)
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
          `Salom ${name}! 👋\n\nMen Blip Agent — AI yordamching.\n\n📋 Buyruqlar:\n/reset — suhbatni tozalash\n/notes — eslatmalar\n/stats — statistika\n/help — yordam\n\nYoki oddiy savol yoz!`, env);
        return new Response("ok");
      }

      if (text === "/reset") {
        await env.AGENT_KV.delete("hist:" + chatId);
        await sendTg(chatId, "🧹 Suhbat tarixi tozalandi.", env);
        return new Response("ok");
      }

      if (text === "/notes") {
        const list = JSON.parse(await env.AGENT_KV.get("notes:" + chatId) || "[]");
        const out = list.length
          ? list.map((n, i) => (i+1) + ". " + n.text).join("\n")
          : "Eslatmalar yo'q. 'Eslatma: ...' deb yoz.";
        await sendTg(chatId, "📝 Eslatmalar:\n\n" + out, env);
        return new Response("ok");
      }

      if (text === "/stats") {
        const s = JSON.parse(await env.AGENT_KV.get("stats:" + chatId) || '{"msgs":0,"start":0}');
        const days = s.start ? Math.ceil((Date.now() - s.start) / 86400000) : 0;
        await sendTg(chatId, `📊 Statistika:\n\nXabarlar: ${s.msgs || 0}\nKun: ${days}`, env);
        return new Response("ok");
      }

      if (text === "/help") {
        await sendTg(chatId,
          `🤖 Blip Agent — yordam\n\n/reset — tarixni tozalash\n/notes — eslatmalar ro'yxati\n/stats — statistika\n/help — bu yordam\n\n💡 Tool'lar:\n• "Soat necha?" — vaqt\n• "5*8 hisobla" — matematika\n• "Eslatma: sut olish" — saqlash`, env);
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
    return new Response("Blip AI v3.0 ishlayapti ✅\n\nEndpoints:\n/api — Sayt chat\n/council — AI Kengash\n/webhook — Telegram", {
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
};
