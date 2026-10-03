// ============================================================
// ⚡ BLIP AI WORKER v3.2 — Til qo'llab-quvvatlash
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
Buyruq kutma — oddiy xabarga ham javob ber.`;

// ============================================================
// 🌐 TILGA MOS COUNCIL PROMPTLAR
// ============================================================
const COUNCIL_SYSTEM = {
  uz: `Sen aqlli va dono yordamchisan.
O'zbek tilida (lotin) qisqa va aniq javob ber (3-5 gap).
Faqat savolga javob ber, ortiqcha gapirma.`,
  
  ru: `Ты умный и мудрый помощник.
Отвечай на русском языке кратко и точно (3-5 предложений).
Отвечай только на вопрос, не говори лишнего.`,
  
  en: `You are a smart and wise assistant.
Answer in English briefly and accurately (3-5 sentences).
Answer only the question, don't say extra.`
};

const JUDGE_SYSTEM = {
  uz: `Sen AI Kengashning dono raisisisan.
5 ta AI javobini tahlil qilib, O'ZBEK TILIDA qisqa umumiy xulosa yoz (5-7 gap).
Eng yaxshi fikrlarni birlashtir, qarama-qarshiliklarni ajrat.`,
  
  ru: `Ты мудрый председатель AI Совета.
Проанализируй ответы 5 AI и напиши краткий общий вывод на РУССКОМ языке (5-7 предложений).
Объедини лучшие идеи, выдели противоречия.`,
  
  en: `You are the wise chairman of the AI Council.
Analyze 5 AI answers and write a brief general conclusion in ENGLISH (5-7 sentences).
Combine best ideas, highlight contradictions.`
};

const COUNCIL_PAROL = "Blipzor921324";

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
    parameters: { type: "object", properties: {} } } }
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
      if (![...args.expr].every(c => allowed.includes(c))) return "Xato";
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
    return "Noma'lum";
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
    // 🏛 AI COUNCIL
    // ============================================================
    if (path === "/council" && request.method === "POST") {
      try {
        const body = await request.json();
        const question = (body.question || "").trim();
        const parol = (body.parol || "").trim();
        const lang = (body.lang || "uz").toLowerCase();

        if (parol !== COUNCIL_PAROL) {
          return json({ error: "🔐 Parol xato! Faqat Blip uchun." }, 403);
        }

        if (!question) return json({ error: "Savol yo'q" }, 400);
        if (question.length > 2000) return json({ error: "Savol juda uzun" }, 400);

        const sysMsg = COUNCIL_SYSTEM[lang] || COUNCIL_SYSTEM.uz;
        const judgeSys = JUDGE_SYSTEM[lang] || JUDGE_SYSTEM.uz;

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
                { role: "system", content: sysMsg },
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
            answer: "❌ Xato"
          }))
        );

        const answers = await Promise.all(promises);

        let judgePrompt;
        if (lang === "ru") {
          judgePrompt = `Вопрос: "${question}"\n\n5 AI ответили:\n\n${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}\n\nТы председатель. Напиши общий вывод на РУССКОМ (5-7 предложений).`;
        } else if (lang === "en") {
          judgePrompt = `Question: "${question}"\n\n5 AIs answered:\n\n${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}\n\nYou are chairman. Write general conclusion in ENGLISH (5-7 sentences).`;
        } else {
          judgePrompt = `Savol: "${question}"\n\n5 ta AI javob berdi:\n\n${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}\n\nSen rais. Umumiy xulosa yoz O'ZBEK TILIDA (5-7 gap).`;
        }

        const judgeRes = await fetch("https://openrouter.ai/api/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + env.OPENROUTER_API_KEY,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "qwen/qwen3.6-plus-preview:free",
            messages: [
              { role: "system", content: judgeSys },
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
          `Salom ${name}! 👋\n\nMen Blip Agent — AI yordamching.\n\n/reset — tozalash\n/help — yordam`, env);
        return new Response("ok");
      }
      if (text === "/reset") {
        await env.AGENT_KV.delete("hist:" + chatId);
        await sendTg(chatId, "🧹 Tozalandi.", env);
        return new Response("ok");
      }
      if (text === "/help") {
        await sendTg(chatId, `🤖 Blip Agent\n\n/reset — tozalash\n/help — yordam`, env);
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
    return new Response("Blip AI v3.2 ishlayapti ✅\n\nEndpoints:\n/api\n/council 🔐 (uz/ru/en)\n/webhook", {
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
};
