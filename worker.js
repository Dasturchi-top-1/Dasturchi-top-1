// ============================================================
// ⚡ BLIP AI WORKER v5.0 — Gemini 3, parolsiz
// ============================================================

const SYSTEM = `Sen Blip Agent — Telegram bot orqali ishlovchi AI yordamchisan.
Foydalanuvchi: Blip (Salohiddin), Tojikiston, Dushanbe, 13 yosh.
O'zbek tilida (lotin) qisqa va aniq javob ber.
Buyruq kutma — oddiy xabarga ham javob ber.`;

// ============================================================
// 🌐 TILLAR
// ============================================================
const COUNCIL_SYSTEM = {
  uz: `Sen aqlli va dono yordamchisan. O'zbek tilida (lotin) qisqa va aniq javob ber (3-5 gap). Faqat savolga javob ber.`,
  ru: `Ты умный и мудрый помощник. Отвечай на русском кратко и точно (3-5 предложений).`,
  en: `You are a smart and wise assistant. Answer in English briefly and accurately (3-5 sentences).`,
  tg: `Ту ёвари оқил ва доно ҳастӣ. Ба забони тоҷикӣ кӯтоҳ ва дақиқ ҷавоб деҳ (3-5 ҷумла).`
};

const JUDGE_SYSTEM = {
  uz: `Sen AI Kengashning dono raisisisan. Javoblarni tahlil qilib, O'ZBEK TILIDA qisqa xulosa yoz (5-7 gap).`,
  ru: `Ты мудрый председатель AI Совета. Проанализируй ответы и напиши краткий вывод на РУССКОМ (5-7 предложений).`,
  en: `You are the wise chairman of the AI Council. Analyze answers and write brief conclusion in ENGLISH (5-7 sentences).`,
  tg: `Ту раиси донои Шӯрои AI ҳастӣ. Ҷавобҳоро таҳлил кун ва хулосаи кӯтоҳ ба ЗАБОНИ ТОҶИКӢ нависед (5-7 ҷумла).`
};

const TIME_SYSTEM = `Sen vaqt sayohatchisisan. Foydalanuvchi yil va joyni aytadi. Sen o'sha davrdagi voqeani tasvirlab berasan.
FAQAT JSON qaytar:
{"story":"O'sha davr haqida qisqa hikoya (4-6 gap)","fact":"Qiziqarli tarixiy fakt","imagePrompt":"English prompt for image"}`;

const WORLD_SYSTEM = `Sen dunyo yaratuvchisisan. Har safar yangi fantastik dunyo o'ylab topasan.
FAQAT JSON qaytar:
{"name":"Dunyo nomi","story":"Dunyo haqida qisqa tavsif (4-6 gap)","fact":"Qiziqarli fakt","imagePrompt":"English prompt for image"}`;

const DEBATE_FOR_SYSTEM = `Sen FOR tomoni vakilisan. Berilgan mavzuni HIMOYA qilasan. Kuchli argumentlar yoz (3-4 gap).`;
const DEBATE_AGAINST_SYSTEM = `Sen AGAINST tomoni vakilisan. Berilgan mavzuga QARSHI chiqasan. Kuchli argumentlar yoz (3-4 gap).`;
const DEBATE_JUDGE_SYSTEM = `Sen munozara hakamisan. Ikki tomon argumentini o'qib, xolis qaror chiqarasan (2-3 gap).`;

const DREAM_SYSTEM = `Sen professional tush tahlilchisisan. Tushni o'qib, JSON formatda javob ber:
{"analysis":"Tushning ma'nosi (3-5 gap)","symbols":["ramz1","ramz2"],"mood":"xursand/qo'rqinchli/g'alati/sokin/xafa","imagePrompt":"English prompt for image"}
FAQAT JSON qaytar.`;

const COUNCIL_PAROL = "SALOXIDDINJON UMARJON ENEM VA OILA";

const TURING_TOPICS = [
  "Hayotning ma'nosi nima?", "Eng yaxshi dasturlash tili qaysi?",
  "Kelajakda AI odamlarni almashtiradimi?", "Pul baxt keltiradimi?",
  "Maktab kerakmi yoki o'z-o'zini o'qitish yaxshimi?", "Ijtimoiy tarmoqlar foydalimi?",
  "Eng katta ixtiro nima?", "Kosmik sayohat muhimmi?",
  "Sun'iy intellekt xavflimi?", "Kitob o'qish yoki film ko'rish?"
];

const GEMINI_MODELS = [
  { id: "gemini-3.8-flash", name: "Gemini 3.8", emoji: "🧠" },
  { id: "gemini-3.5-flash", name: "Gemini 3.5", emoji: "⚡" },
  { id: "gemini-3.5-flash-lite", name: "Gemini 3.5 Lite", emoji: "🌟" },
  { id: "gemini-3.1-flash-lite", name: "Gemini 3.1 Lite", emoji: "💎" },
  { id: "gemini-3.8-flash", name: "Gemini Flash", emoji: "🚀" }
];

const FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"];

// ============================================================
// 🌟 GEMINI API
// ============================================================
async function geminiRaw(model, sysMsg, userMsg, env, maxTokens) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${env.GEMINI_API_KEY}`;
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: userMsg }] }],
        systemInstruction: { parts: [{ text: sysMsg }] },
        generationConfig: { temperature: 0.7, maxOutputTokens: maxTokens }
      })
    });
    const d = await r.json();
    if (d.error) return { error: d.error.message || "Xato" };
    const text = d.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!text) return { error: "Javob bo'sh" };
    return { text: text };
  } catch (e) {
    return { error: e.message };
  }
}

async function geminiCall(model, sysMsg, userMsg, env, maxTokens = 800) {
  let result = await geminiRaw(model, sysMsg, userMsg, env, maxTokens);
  if (result.text) return result;
  for (const fb of FALLBACK_MODELS) {
    if (fb === model) continue;
    result = await geminiRaw(fb, sysMsg, userMsg, env, maxTokens);
    if (result.text) return result;
  }
  return { error: result.error || "Barcha modellar ishlamadi" };
}

// ============================================================
// 📤 TELEGRAM
// ============================================================
async function sendTg(chatId, text, env) {
  for (let i = 0; i < text.length; i += 4000) {
    await fetch("https://api.telegram.org/bot" + env.TELEGRAM_TOKEN + "/sendMessage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, text: text.slice(i, i + 4000) })
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
// 🤖 AGENT LOOP (Telegram)
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
        const lang = (body.lang || "uz").toLowerCase();

        if (!question) return json({ error: "Savol yo'q" }, 400);
        if (question.length > 2000) return json({ error: "Savol juda uzun" }, 400);

        const sysMsg = COUNCIL_SYSTEM[lang] || COUNCIL_SYSTEM.uz;
        const judgeSys = JUDGE_SYSTEM[lang] || JUDGE_SYSTEM.uz;

        const promises = GEMINI_MODELS.map(m =>
          geminiCall(m.id, sysMsg, question, env, 500)
            .then(r => ({
              emoji: m.emoji,
              name: m.name,
              answer: r.error ? ("❌ " + r.error) : r.text
            }))
        );

        const answers = await Promise.all(promises);

        let judgePrompt;
        if (lang === "ru") {
          judgePrompt = `Вопрос: "${question}"\n\nОтветы:\n\n${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}\n\nНапиши общий вывод на РУССКОМ (5-7 предложений).`;
        } else if (lang === "en") {
          judgePrompt = `Question: "${question}"\n\nAnswers:\n\n${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}\n\nWrite general conclusion in ENGLISH (5-7 sentences).`;
        } else if (lang === "tg") {
          judgePrompt = `Савол: "${question}"\n\nҶавобҳо:\n\n${answers.map((a, i) => `${i+1}. ${a.name}:\n${a.answer}`).join("\n\n")}\n\nХулосаи умумӣ ба ЗАБОНИ ТОҶИКӢ нависед (5-7 ҷумла).`;
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
    // 🌙 DREAM JOURNAL
    // ============================================================
    if (path === "/dream" && request.method === "POST") {
      try {
        const body = await request.json();
        const dream = (body.dream || "").trim();

        if (!dream) return json({ error: "Tush matni yo'q" }, 400);
        if (dream.length > 2000) return json({ error: "Tush juda uzun" }, 400);

        const result = await geminiCall("gemini-3.8-flash", DREAM_SYSTEM, dream, env, 600);
        if (result.error) return json({ error: "AI xatosi: " + result.error }, 500);

        let data = { analysis: "Tahlil qilinmadi", symbols: [], mood: "g'alati", imagePrompt: "mystical dream, surreal" };
        try {
          const text = result.text;
          const s = text.indexOf('{');
          const e = text.lastIndexOf('}') + 1;
          if (s >= 0 && e > s) data = { ...data, ...JSON.parse(text.slice(s, e)) };
        } catch {}

        const imageUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(data.imagePrompt || 'dream')}?width=768&height=768&nologo=true&seed=${Date.now()}`;

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
    // ⏰ TIME MACHINE
    // ============================================================
    if (path === "/time" && request.method === "POST") {
      try {
        const body = await request.json();
        const year = (body.year || "").toString().trim();
        const place = (body.place || "").trim();

        if (!year) return json({ error: "Yil yo'q" }, 400);

        const prompt = `Yil: ${year}${place ? '\nJoy: ' + place : ''}\n\nO'sha davr haqida hikoya yoz.`;
        const result = await geminiCall("gemini-3.8-flash", TIME_SYSTEM, prompt, env, 600);
        if (result.error) return json({ error: "AI xatosi: " + result.error }, 500);

        let data = { story: "Hikoya yaratilmadi", fact: "", imagePrompt: `year ${year} historical scene` };
        try {
          const text = result.text;
          const s = text.indexOf('{');
          const e = text.lastIndexOf('}') + 1;
          if (s >= 0 && e > s) data = { ...data, ...JSON.parse(text.slice(s, e)) };
        } catch {}

        const imageUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(data.imagePrompt || year)}?width=768&height=768&nologo=true&seed=${Date.now()}`;

        return json({ story: data.story, fact: data.fact || "", imageUrl });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 🎲 ONE-BUTTON WORLD
    // ============================================================
    if (path === "/world" && request.method === "POST") {
      try {
        const body = await request.json();

        const prompt = `Yangi fantastik dunyo yarat. Tasodifiy mavzu tanla (kosmos, okean, sehr, texnologiya, o'rmon, cho'l).`;
        const result = await geminiCall("gemini-3.8-flash", WORLD_SYSTEM, prompt, env, 600);
        if (result.error) return json({ error: "AI xatosi: " + result.error }, 500);

        let data = { name: "Yangi dunyo", story: "Dunyo yaratilmadi", fact: "", imagePrompt: "fantasy world, surreal" };
        try {
          const text = result.text;
          const s = text.indexOf('{');
          const e = text.lastIndexOf('}') + 1;
          if (s >= 0 && e > s) data = { ...data, ...JSON.parse(text.slice(s, e)) };
        } catch {}

        const imageUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(data.imagePrompt || 'fantasy world')}?width=768&height=768&nologo=true&seed=${Date.now()}`;

        return json({ name: data.name, story: data.story, fact: data.fact || "", imageUrl });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // ⚔️ AI DEBATE ARENA
    // ============================================================
    if (path === "/debate" && request.method === "POST") {
      try {
        const body = await request.json();
        const topic = (body.topic || "").trim();

        if (!topic) return json({ error: "Mavzu yo'q" }, 400);

        const [forResult, againstResult] = await Promise.all([
          geminiCall("gemini-3.8-flash", DEBATE_FOR_SYSTEM, topic, env, 400),
          geminiCall("gemini-3.8-flash", DEBATE_AGAINST_SYSTEM, topic, env, 400)
        ]);

        const forArg = forResult.error ? "FOR argumenti olinmadi" : forResult.text;
        const againstArg = againstResult.error ? "AGAINST argumenti olinmadi" : againstResult.text;

        const judgePrompt = `Mavzu: "${topic}"\n\nFOR:\n${forArg}\n\nAGAINST:\n${againstArg}\n\nKim yaxshiroq argument keltirdi? Xolis qaror chiqar.`;
        const judgeResult = await geminiCall("gemini-3.8-flash", DEBATE_JUDGE_SYSTEM, judgePrompt, env, 400);
        const verdict = judgeResult.error ? "Hakam qaror qila olmadi" : judgeResult.text;

        return json({ forArg, againstArg, verdict });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 🎭 REVERSE TURING TEST
    // ============================================================
    if (path === "/turing" && request.method === "POST") {
      try {
        const body = await request.json();

        if (body.action === "topic") {
          const topic = TURING_TOPICS[Math.floor(Math.random() * TURING_TOPICS.length)];
          return json({ topic });
        }

        if (body.action === "judge") {
          const topic = (body.topic || "").trim();
          const userAnswer = (body.userAnswer || "").trim();
          if (!topic || !userAnswer) return json({ error: "Mavzu yoki javob yo'q" }, 400);

          const aiHumanPrompt = `Sen oddiy 14 yoshli o'smir odamsan. Quyidagi savolga ODDIY, SODDA, his-tuyg'uli javob yoz (2-4 gap). FAQAT javob yoz.\n\nSavol: ${topic}`;
          const aiResult = await geminiCall("gemini-3.8-flash", "Sen oddiy o'smir odamsan.", aiHumanPrompt, env, 400);
          const aiAnswer = aiResult.error ? "Javob yo'q" : aiResult.text;

          const userFirst = Math.random() < 0.5;
          const answer1 = userFirst ? userAnswer : aiAnswer;
          const answer2 = userFirst ? aiAnswer : userAnswer;

          const judgePrompt = `Sen Turing Test hakamisan.\nSAVOL: ${topic}\n\nJAVOB 1:\n${answer1}\n\nJAVOB 2:\n${answer2}\n\nQaysi biri odam? Faqat JSON qaytar: {"human":1,"reason":"sabab"}`;
          const judgeResult = await geminiCall("gemini-3.8-flash", "Sen Turing Test hakamisan.", judgePrompt, env, 300);

          let judgeData = { human: 1, reason: "Aniqlanmadi" };
          if (!judgeResult.error) {
            try {
              const text = judgeResult.text;
              const s = text.indexOf('{');
              const e = text.lastIndexOf('}') + 1;
              if (s >= 0 && e > s) judgeData = JSON.parse(text.slice(s, e));
            } catch {}
          }

          const actualHuman = userFirst ? 1 : 2;
          const judgeCorrect = (judgeData.human === actualHuman);

          return json({
            answer1: answer1,
            answer2: answer2,
            judgeVerdict: `Hakam ${judgeData.human}-javobni odam deb topdi`,
            humanIsUser: userFirst,
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
        await sendTg(chatId, `Salom ${name}! 👋\n\nMen Blip Agent.\n\n/reset — tozalash\n/help — yordam`, env);
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
    return new Response("Blip AI v5.0 ishlayapti ✅\n\nEndpoints:\n/council\n/dream\n/turing\n/time\n/world\n/debate\n/api\n/webhook", {
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
};
