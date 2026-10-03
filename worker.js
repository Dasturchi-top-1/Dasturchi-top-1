// ============================================================
// ⚡ BLIP AI WORKER v4.2 — Google Gemini 3 (yangi modellar)
// ============================================================

const SYSTEM = `Sen Blip Agent — Telegram bot orqali ishlovchi AI yordamchisan.
Foydalanuvchi: Blip (Salohiddin), Tojikiston, Dushanbe, 13 yosh.
O'zbek tilida (lotin) qisqa va aniq javob ber.
Buyruq kutma — oddiy xabarga ham javob ber.`;

const COUNCIL_SYSTEM = {
  uz: `Sen aqlli va dono yordamchisan. O'zbek tilida (lotin) qisqa va aniq javob ber (3-5 gap). Faqat savolga javob ber.`,
  ru: `Ты умный и мудрый помощник. Отвечай на русском кратко и точно (3-5 предложений).`,
  en: `You are a smart and wise assistant. Answer in English briefly and accurately (3-5 sentences).`
};

const JUDGE_SYSTEM = {
  uz: `Sen AI Kengashning dono raisisisan. Javoblarni tahlil qilib, O'ZBEK TILIDA qisqa xulosa yoz (5-7 gap).`,
  ru: `Ты мудрый председатель AI Совета. Проанализируй ответы и напиши краткий вывод на РУССКОМ (5-7 предложений).`,
  en: `You are the wise chairman of the AI Council. Analyze answers and write brief conclusion in ENGLISH (5-7 sentences).`
};

const COUNCIL_PAROL = "SALOXIDDINJON UMARJON ENEM VA OILA";

// ============================================================
// 🌟 GEMINI 3 MODELLARI (YANGI)
// ============================================================
const GEMINI_MODELS = [
  { id: "gemini-3.8-flash", name: "Gemini 3.8", emoji: "🧠" },
  { id: "gemini-3.5-flash", name: "Gemini 3.5", emoji: "⚡" },
  { id: "gemini-3.5-flash-lite", name: "Gemini 3.5 Lite", emoji: "🌟" },
  { id: "gemini-3.1-flash-lite", name: "Gemini 3.1 Lite", emoji: "💎" },
  { id: "gemini-3.1-pro-preview", name: "Gemini 3.1 Pro", emoji: "🚀" }
];

// ============================================================
// 🌟 GEMINI API CHAQIRUV
// ============================================================
async function geminiCall(model, sysMsg, userMsg, env, maxTokens = 800) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${env.GEMINI_API_KEY}`;
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [
          { role: "user", parts: [{ text: userMsg }] }
        ],
        systemInstruction: { parts: [{ text: sysMsg }] },
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: maxTokens
        }
      })
    });
    const d = await r.json();
    if (d.error) return { error: d.error.message || "Xato" };
    const text = d.candidates?.[0]?.content?.parts?.[0]?.text;
    return { text: text || "Javob yo'q" };
  } catch (e) {
    return { error: e.message };
  }
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
// 🤖 AGENT LOOP (Telegram uchun)
// ============================================================
async function agentLoop(userMsg, chatId, env) {
  const key = "hist:" + chatId;
  let history = JSON.parse(await env.AGENT_KV.get(key) || "[]");
  if (!history.length) history.push({ role: "system", content: SYSTEM });

  const context = history.slice(-10).map(h =>
    (h.role === "user" ? "Foydalanuvchi: " : "AI: ") + h.content
  ).join("\n") + "\nFoydalanuvchi: " + userMsg;

  const result = await geminiCall("gemini-3.8-flash", SYSTEM, context, env, 800);
  const reply = result.error ? ("❌ " + result.error) : result.text;

  history.push({ role: "user", content: userMsg });
  history.push({ role: "assistant", content: reply });
  if (history.length > 40) history = [history[0], ...history.slice(-39)];
  await env.AGENT_KV.put(key, JSON.stringify(history));

  return reply;
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

        // 5 ta Gemini parallel
        const promises = GEMINI_MODELS.map(m =>
          geminiCall(m.id, sysMsg, question, env, 500)
            .then(r => ({
              emoji: m.emoji,
              name: m.name,
              answer: r.error ? ("❌ " + r.error) : r.text
            }))
        );

        const answers = await Promise.all(promises);

        // Rais xulosasi
        let judgePrompt;
        if (lang === "ru") {
          judgePrompt = `Вопрос: "${question}"\n\nОтветы:\n\n${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}\n\nНапиши общий вывод на РУССКОМ (5-7 предложений).`;
        } else if (lang === "en") {
          judgePrompt = `Question: "${question}"\n\nAnswers:\n\n${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}\n\nWrite general conclusion in ENGLISH (5-7 sentences).`;
        } else {
          judgePrompt = `Savol: "${question}"\n\nJavoblar:\n\n${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}\n\nUmumiy xulosa yoz O'ZBEK TILIDA (5-7 gap).`;
        }

        const judgeResult = await geminiCall("gemini-3.8-flash", judgeSys, judgePrompt, env, 700);
        const conclusion = judgeResult.error ? ("❌ " + judgeResult.error) : judgeResult.text;

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
        await sendTg(chatId, `Salom ${name}! 👋\n\nMen Blip Agent — AI yordamching.\n\n/reset — tozalash\n/help — yordam`, env);
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
    return new Response("Blip AI v4.2 (Gemini 3) ishlayapti ✅\n\nEndpoints:\n/api\n/council 🔐\n/webhook", {
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
};
