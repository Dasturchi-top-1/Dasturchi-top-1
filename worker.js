    // ============================================================
    // 🎭 REVERSE TURING TEST
    // ============================================================
    if (path === "/turing" && request.method === "POST") {
      try {
        const body = await request.json();
        const parol = (body.parol || "").trim();
        if (parol !== COUNCIL_PAROL) {
          return json({ error: "🔐 Parol xato!" }, 403);
        }

        // Yangi mavzu
        if (body.action === "topic") {
          const topic = TURING_TOPICS[Math.floor(Math.random() * TURING_TOPICS.length)];
          return json({ topic });
        }

        // Hakam qarori
        if (body.action === "judge") {
          const topic = (body.topic || "").trim();
          const userAnswer = (body.userAnswer || "").trim();
          if (!topic || !userAnswer) return json({ error: "Mavzu yoki javob yo'q" }, 400);

          // 1. AI odam bo'lib yozadi
          const aiHumanPrompt = `Sen oddiy 14 yoshli o'smir odamsan. Quyidagi savolga ODDIY, SODDA, his-tuyg'uli javob yoz. Xuddi odam kabi — xato bilan, norasmiy, qisqa (2-4 gap). FAQAT javob yoz.

Savol: ${topic}`;

          const aiResult = await geminiCall("gemini-3.8-flash",
            "Sen oddiy o'smir odamsan. Odam kabi yoz.",
            aiHumanPrompt, env, 400);
          const aiAnswer = aiResult.error ? "Javob yo'q" : aiResult.text;

          // 2. Tasodifiy tartib
          const userFirst = Math.random() < 0.5;
          const answer1 = userFirst ? userAnswer : aiAnswer;
          const answer2 = userFirst ? aiAnswer : userAnswer;

          // 3. Hakam qaror qabul qiladi
          const judgePrompt = `Sen Turing Test hakamisan. Ikki javobni o'qi.
Biri ODAM tomonidan yozilgan, biri AI tomonidan.
Qaysi biri ODAM ekanini aniqlashing kerak.

SAVOL: ${topic}

JAVOB 1:
${answer1}

JAVOB 2:
${answer2}

Qaysi biri odam? Faqat JSON qaytar:
{"human": 1 yoki 2, "reason": "qisqa sabab"}`;

          const judgeResult = await geminiCall("gemini-3.8-flash",
            "Sen Turing Test hakamisan. Faqat JSON qaytar.",
            judgePrompt, env, 300);

          let judgeData = { human: 1, reason: "Aniqlanmadi" };
          if(!judgeResult.error){
            try {
              const text = judgeResult.text;
              const s = text.indexOf('{');
              const e = text.lastIndexOf('}') + 1;
              if(s >= 0 && e > s){
                judgeData = JSON.parse(text.slice(s, e));
              }
            } catch(e){}
          }

          // Hakam to'g'ri topdimi?
          const judgeSaysHuman = judgeData.human; // 1 yoki 2
          const actualHuman = userFirst ? 1 : 2;
          const judgeCorrect = (judgeSaysHuman === actualHuman);

          return json({
            answer1: answer1,
            answer2: answer2,
            judgeVerdict: `Hakam ${judgeSaysHuman}-javobni odam deb topdi`,
            humanIsUser: userFirst ? true : false,
            userWins: !judgeCorrect,
            reasoning: judgeData.reason || ""
          });
        }

        return json({ error: "Noma'lum action" }, 400);
      } catch (e) {
        return json({ error: e.message }, 500);
      }
            }
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

const COUNCIL_PAROL = "921324";
const TURING_TOPICS = [
  "Hayotning ma'nosi nima?",
  "Eng yaxshi dasturlash tili qaysi?",
  "Kelajakda AI odamlarni almashtiradimi?",
  "Pul baxt keltiradimi?",
  "Maktab kerakmi yoki o'z-o'zini o'qitish yaxshimi?",
  "Ijtimoiy tarmoqlar foydalimi yoki zararlimi?",
  "Eng katta ixtiro nima?",
  "Kosmik sayohat muhimmi?",
  "Ta'lim tizimi qanday bo'lishi kerak?",
  "Sun'iy intellekt xavflimi?",
  "Kitob o'qish yoki film ko'rish?",
  "Yolg'izlik yaxshimi yoki yomonmi?",
  "Sport sog'liq uchun foydalimi?",
  "Musiqa kayfiyatga ta'sir qiladimi?",
  "Do'stlik puldan qimmatmi?"
];
const DREAM_SYSTEM = `Sen professional tush tahlilchisisan. Foydalanuvchi tushini o'qib, quyidagi JSON formatda javob ber:

{
  "analysis": "Tushning ma'nosi va psixologik tahlili (3-5 gap, o'zbek tilida)",
  "symbols": ["ramz1", "ramz2", "ramz3"],
  "mood": "xursand/qo'rqinchli/g'alati/sokin/xafa/hayajonli",
  "imagePrompt": "Tushni tasvirlovchi inglizcha prompt (rasm chizish uchun)"
}

FAQAT JSON qaytar. Boshqa hech narsa yozma.`;

// ============================================================
// 🌟 GEMINI 3 MODELLARI (YANGI)
// ============================================================
const GEMINI_MODELS = [
  { id: "gemini-3.8-flash", name: "Gemini 3.8", emoji: "🧠" },
  { id: "gemini-3.5-flash", name: "Gemini 3.5", emoji: "⚡" },
  { id: "gemini-3.5-flash-lite", name: "Gemini 3.5 Lite", emoji: "🌟" },
  { id: "gemini-3.1-flash-lite", name: "Gemini 3.1 Lite", emoji: "💎" },
  { id: "gemini-3.8-flash", name: "Gemini 3.8 Flash", emoji: "🚀" }
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
// 🌙 DREAM JOURNAL
// ============================================================
if (path === "/dream" && request.method === "POST") {
  try {
    const body = await request.json();
    const parol = (body.parol || "").trim();
    const dream = (body.dream || "").trim();

    //if (parol !== COUNCIL_PAROL) {
     // return json({ error: "🔐 Parol xato!" }, 403);
   // }
    if (!dream) return json({ error: "Tush matni yo'q" }, 400);
    if (dream.length > 2000) return json({ error: "Tush juda uzun" }, 400);

    const result = await geminiCall("gemini-3.8-flash", DREAM_SYSTEM, dream, env, 600);

    if (result.error) {
      return json({ error: "AI tahlil xatosi: " + result.error }, 500);
    }

    let data = {
      analysis: "Tahlil qilinmadi",
      symbols: [],
      mood: "g'alati",
      imagePrompt: "mystical dream scene, surreal, ethereal"
    };

    try {
      const text = result.text;
      const s = text.indexOf('{');
      const e = text.lastIndexOf('}') + 1;
      if (s >= 0 && e > s) {
        data = { ...data, ...JSON.parse(text.slice(s, e)) };
      }
    } catch (e) {}

    const imagePrompt = data.imagePrompt || dream.slice(0, 100);
    const encodedPrompt = encodeURIComponent(imagePrompt);
    const imageUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=768&height=768&nologo=true&seed=${Date.now()}`;

    return json({
      analysis: data.analysis,
      symbols: data.symbols || [],
      mood: data.mood || "g'alati",
      imageUrl: imageUrl
    });
  } catch (e) {
    return json({ error: e.message }, 500);
  }
    }
                   
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
