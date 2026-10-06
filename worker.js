// ============================================================
// ⚡ BLIP WORKER v6.0 — Auth + Chat + Image + AI
// ============================================================

const SYSTEM = `Sen Blip Agent — AI yordamchisan. O'zbek tilida qisqa javob ber.`;

const COUNCIL_SYSTEM = {
  uz: `Sen aqlli yordamchisan. O'zbek tilida (lotin) qisqa javob ber (3-5 gap).`,
  ru: `Ты умный помощник. Отвечай на русском кратко (3-5 предложений).`,
  en: `You are a smart assistant. Answer briefly in English (3-5 sentences).`,
  tg: `Ту ёвари оқил ҳастӣ. Ба забони тоҷикӣ кӯтоҳ ҷавоб деҳ.`
};

const JUDGE_SYSTEM = {
  uz: `Sen AI Kengashning raisi. O'ZBEK TILIDA qisqa xulosa yoz (5-7 gap).`,
  ru: `Ты председатель AI Совета. Напиши краткий вывод на РУССКОМ.`,
  en: `You are the chairman. Write brief conclusion in ENGLISH.`,
  tg: `Ту раиси Шӯро ҳастӣ. Ба забони ТОҶИКӢ хулоса нависед.`
};

const TIME_SYSTEM = `Sen vaqt sayohatchisisan. FAQAT JSON qaytar:
{"story":"hikoya (4-6 gap)","fact":"fakt","imagePrompt":"English prompt"}`;

const WORLD_SYSTEM = `Sen dunyo yaratuvchisisan. FAQAT JSON:
{"name":"nom","story":"tavsif","fact":"fakt","imagePrompt":"English prompt"}`;

const DEBATE_FOR = `Sen FOR tomon. Mavzuni HIMOYA qil (3-4 gap).`;
const DEBATE_AGAINST = `Sen AGAINST tomon. QARSHI chiq (3-4 gap).`;
const DEBATE_JUDGE = `Sen hakam. Xolis qaror chiqar (2-3 gap).`;

const DREAM_SYSTEM = `Sen tush tahlilchisi. FAQAT JSON:
{"analysis":"ma'no","symbols":["r1","r2"],"mood":"xursand/g'alati/sokin","imagePrompt":"English prompt"}`;

const TURING_TOPICS = [
  "Hayotning ma'nosi nima?","Eng yaxshi dasturlash tili?",
  "Kelajakda AI odamlarni almashtiradimi?","Pul baxt keltiradimi?",
  "Maktab kerakmi?","Ijtimoiy tarmoqlar foydalimi?",
  "Eng katta ixtiro nima?","Kosmik sayohat muhimmi?",
  "Sun'iy intellekt xavflimi?","Kitob yoki film?"
];

const GEMINI_MODELS = [
  { id: "gemini-3.8-flash", name: "Gemini 3.8", emoji: "🧠" },
  { id: "gemini-3.5-flash", name: "Gemini 3.5", emoji: "⚡" },
  { id: "gemini-3.5-flash-lite", name: "Gemini 3.5 Lite", emoji: "🌟" },
  { id: "gemini-3.1-flash-lite", name: "Gemini 3.1 Lite", emoji: "💎" },
  { id: "gemini-3.8-flash", name: "Gemini Flash", emoji: "🚀" }
];

const FALLBACKS = ["gemini-3.5-flash-lite","gemini-3.1-flash-lite","gemini-3.5-flash"];

// ============================================================
// 🔐 PAROL HASH (SHA-256)
// ============================================================
async function hashPass(pass, salt) {
  const data = new TextEncoder().encode(pass + ":" + salt);
  const buf = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
}

function genToken() {
  const arr = new Uint8Array(24);
  crypto.getRandomValues(arr);
  return Array.from(arr).map(b => b.toString(16).padStart(2, "0")).join("");
}

function genSalt() {
  const arr = new Uint8Array(16);
  crypto.getRandomValues(arr);
  return Array.from(arr).map(b => b.toString(16).padStart(2, "0")).join("");
}

// ============================================================
// 📊 KV FUNKSIYALAR
// ============================================================
async function getUser(name, env) {
  const d = await env.AGENT_KV.get("user:" + name.toLowerCase());
  return d ? JSON.parse(d) : null;
}

async function getUserById(id, env) {
  const d = await env.AGENT_KV.get("uid:" + id);
  return d ? JSON.parse(d) : null;
}

async function saveUser(user, env) {
  await env.AGENT_KV.put("user:" + user.name, JSON.stringify(user));
  await env.AGENT_KV.put("uid:" + user.id, JSON.stringify(user));
}

async function getSession(token, env) {
  if (!token) return null;
  const d = await env.AGENT_KV.get("session:" + token);
  return d ? JSON.parse(d) : null;
}

async function saveSession(token, session, env) {
  await env.AGENT_KV.put("session:" + token, JSON.stringify(session), {
    expirationTtl: 30 * 24 * 3600
  });
}

async function delSession(token, env) {
  await env.AGENT_KV.delete("session:" + token);
}

async function getNextId(env) {
  const cur = await env.AGENT_KV.get("nextId");
  const next = cur ? parseInt(cur) + 1 : 1001;
  await env.AGENT_KV.put("nextId", String(next));
  return next;
}

// ============================================================
// 📊 FAOLLIK
// ============================================================
async function addActivity(ism, action, page, env) {
  let list = [];
  try {
    const d = await env.AGENT_KV.get("activity");
    list = d ? JSON.parse(d) : [];
  } catch(e) {}
  list.push({ ism: ism, action: action, page: page || "-", time: Date.now() });
  if (list.length > 500) list = list.slice(-500);
  await env.AGENT_KV.put("activity", JSON.stringify(list));
}

async function getActivity(env) {
  try {
    const d = await env.AGENT_KV.get("activity");
    return d ? JSON.parse(d) : [];
  } catch(e) { return []; }
}

// ============================================================
// 💬 CHAT
// ============================================================
function chatKey(id1, id2) {
  const a = Math.min(id1, id2);
  const b = Math.max(id1, id2);
  return "chat:" + a + "-" + b;
}

async function getChat(fromId, toId, env) {
  try {
    const d = await env.AGENT_KV.get(chatKey(fromId, toId));
    return d ? JSON.parse(d) : [];
  } catch(e) { return []; }
}

async function saveChat(fromId, toId, msgs, env) {
  if (msgs.length > 200) msgs = msgs.slice(-200);
  await env.AGENT_KV.put(chatKey(fromId, toId), JSON.stringify(msgs));
}

async function addMessage(fromUser, toId, text, env) {
  const msgs = await getChat(fromUser.id, toId, env);
  msgs.push({
    fromId: fromUser.id,
    fromName: fromUser.name,
    toId: toId,
    text: text,
    time: Date.now()
  });
  await saveChat(fromUser.id, toId, msgs, env);
  return msgs.length;
}

// Foydalanuvchilar ro'yxati
async function listUsers(env) {
  const list = await env.AGENT_KV.list({ prefix: "user:" });
  const users = [];
  for (const k of list.keys) {
    const d = await env.AGENT_KV.get(k.name);
    if (d) users.push(JSON.parse(d));
  }
  return users;
}

// ============================================================
// 🌟 GEMINI AI
// ============================================================
async function geminiRaw(model, sysMsg, userMsg, env, maxTok) {
  const url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + env.GEMINI_API_KEY;
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: userMsg }] }],
        systemInstruction: { parts: [{ text: sysMsg }] },
        generationConfig: { temperature: 0.7, maxOutputTokens: maxTok || 800 }
      })
    });
    const d = await r.json();
    if (d.error) return { error: d.error.message };
    const text = d.candidates?.[0]?.content?.parts?.[0]?.text;
    return text ? { text: text } : { error: "Bo'sh" };
  } catch(e) { return { error: e.message }; }
}

async function geminiCall(model, sysMsg, userMsg, env, maxTok) {
  let r = await geminiRaw(model, sysMsg, userMsg, env, maxTok);
  if (r.text) return r;
  for (const fb of FALLBACKS) {
    if (fb === model) continue;
    r = await geminiRaw(fb, sysMsg, userMsg, env, maxTok);
    if (r.text) return r;
  }
  return { error: r.error || "Xato" };
}

// ============================================================
// 🖼 RASM (Pollinations)
// ============================================================
function imageUrl(prompt, w, h) {
  w = w || 768;
  h = h || 768;
  return "https://image.pollinations.ai/prompt/" + encodeURIComponent(prompt) + "?width=" + w + "&height=" + h + "&nologo=true&seed=" + Date.now();
}

// ============================================================
// 🌐 CORS + JSON
// ============================================================
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization"
};

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: Object.assign({}, CORS, { "Content-Type": "application/json" })
  });
}

function getToken(request) {
  const auth = request.headers.get("Authorization") || "";
  return auth.replace("Bearer ", "").trim();
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
  } catch(e) {}
}

// Telegram agent loop
async function agentLoop(userMsg, chatId, env) {
  const key = "hist:" + chatId;
  let history = JSON.parse(await env.AGENT_KV.get(key) || "[]");
  if (!history.length) history.push({ role: "system", content: SYSTEM });
  history.push({ role: "user", content: userMsg });

  const context = history.slice(-10).map(h => (h.role === "user" ? "F:" : "AI:") + h.content).join("\n");
  const result = await geminiCall("gemini-3.8-flash", SYSTEM, context, env, 800);
  const reply = result.error ? ("❌ " + result.error) : result.text;

  history.push({ role: "assistant", content: reply });
  if (history.length > 40) history = [history[0], ...history.slice(-39)];
  await env.AGENT_KV.put(key, JSON.stringify(history));
  return reply;
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
    // 📝 REGISTER
    // ============================================================
    if (path === "/register" && request.method === "POST") {
      try {
        const body = await request.json();
        const name = (body.name || "").trim().toLowerCase();
        const pass = (body.pass || "").trim();

        if (!name || !pass) return json({ error: "Ism va parol kerak" }, 400);
        if (name.length < 2) return json({ error: "Ism kamida 2 belgi" }, 400);
        if (pass.length < 4) return json({ error: "Parol kamida 4 belgi" }, 400);
        if (name === "blip") return json({ error: "Bu ism band!" }, 403);

        const existing = await getUser(name, env);
        if (existing) return json({ error: "Bu ism allaqachon band!" }, 403);

        const id = await getNextId(env);
        const salt = genSalt();
        const hash = await hashPass(pass, salt);

        const user = {
          id: id,
          name: name,
          displayName: (body.displayName || name).trim(),
          salt: salt,
          passHash: hash,
          rol: "user",
          joined: Date.now(),
          lastSeen: Date.now(),
          visits: 1
        };
        await saveUser(user, env);
        await addActivity(name, "register", "index", env);

        const token = genToken();
        await saveSession(token, { id: id, name: name, rol: "user" }, env);

        return json({
          ok: true,
          token: token,
          user: { id: id, name: name, displayName: user.displayName, rol: "user" }
        });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 🔐 LOGIN
    // ============================================================
    if (path === "/login" && request.method === "POST") {
      try {
        const body = await request.json();
        const name = (body.name || "").trim().toLowerCase();
        const pass = (body.pass || "").trim();

        if (!name || !pass) return json({ error: "Ism va parol kerak" }, 400);

        const user = await getUser(name, env);
        if (!user) return json({ error: "Bunday ism topilmadi" }, 404);

        const hash = await hashPass(pass, user.salt);
        if (hash !== user.passHash) return json({ error: "Parol xato!" }, 403);

        user.lastSeen = Date.now();
        user.visits = (user.visits || 0) + 1;
        await saveUser(user, env);
        await addActivity(name, "login", "index", env);

        const token = genToken();
        await saveSession(token, { id: user.id, name: user.name, rol: user.rol }, env);

        return json({
          ok: true,
          token: token,
          user: { id: user.id, name: user.name, displayName: user.displayName, rol: user.rol }
        });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 🚪 LOGOUT
    // ============================================================
    if (path === "/logout" && request.method === "POST") {
      const token = getToken(request);
      if (token) {
        const sess = await getSession(token, env);
        if (sess) await addActivity(sess.name, "logout", "-", env);
        await delSession(token, env);
      }
      return json({ ok: true });
    }

    // ============================================================
    // 👤 ME
    // ============================================================
    if (path === "/me" && request.method === "GET") {
      const token = getToken(request);
      const sess = await getSession(token, env);
      if (!sess) return json({ error: "Token yo'q" }, 401);
      const user = await getUserById(sess.id, env);
      if (!user) return json({ error: "Topilmadi" }, 404);
      return json({
        id: user.id,
        name: user.name,
        displayName: user.displayName,
        rol: user.rol,
        joined: user.joined,
        visits: user.visits
      });
    }

    // ============================================================
    // 👥 USERS
    // ============================================================
    if (path === "/users" && request.method === "GET") {
      const token = getToken(request);
      const sess = await getSession(token, env);
      if (!sess) return json({ error: "Token yo'q" }, 401);

      const all = await listUsers(env);
      const list = all.map(u => ({
        id: u.id,
        name: u.name,
        displayName: u.displayName,
        rol: u.rol,
        lastSeen: u.lastSeen
      }));
      return json({ users: list, total: list.length });
    }

    // ============================================================
    // 🔍 FIND (ID orqali)
    // ============================================================
    if (path === "/find" && request.method === "GET") {
      const token = getToken(request);
      const sess = await getSession(token, env);
      if (!sess) return json({ error: "Token yo'q" }, 401);

      const id = parseInt(url.searchParams.get("id") || "0");
      if (!id) return json({ error: "ID kerak" }, 400);

      const user = await getUserById(id, env);
      if (!user) return json({ error: "Topilmadi" }, 404);

      return json({
        user: {
          id: user.id,
          name: user.name,
          displayName: user.displayName,
          lastSeen: user.lastSeen
        }
      });
    }

    // ============================================================
    // 💬 CHAT SEND
    // ============================================================
    if (path === "/chat/send" && request.method === "POST") {
      const token = getToken(request);
      const sess = await getSession(token, env);
      if (!sess) return json({ error: "Token yo'q" }, 401);

      try {
        const body = await request.json();
        const toId = parseInt(body.toId || "0");
        const text = (body.text || "").trim();
        if (!toId || !text) return json({ error: "toId va text kerak" }, 400);
        if (toId === sess.id) return json({ error: "O'zingizga yozib bo'lmaydi" }, 400);

        const me = await getUserById(sess.id, env);
        const target = await getUserById(toId, env);
        if (!target) return json({ error: "Foydalanuvchi topilmadi" }, 404);

        await addMessage(me, toId, text, env);
        await addActivity(sess.name, "chat", "to:" + target.name, env);

        return json({ ok: true });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 💬 CHAT GET
    // ============================================================
    if (path === "/chat/get" && request.method === "GET") {
      const token = getToken(request);
      const sess = await getSession(token, env);
      if (!sess) return json({ error: "Token yo'q" }, 401);

      const withId = parseInt(url.searchParams.get("with") || "0");
      if (!withId) return json({ error: "with kerak" }, 400);

      const msgs = await getChat(sess.id, withId, env);
      return json({ messages: msgs });
    }

    // ============================================================
    // 💬 CHAT LIST
    // ============================================================
    if (path === "/chat/list" && request.method === "GET") {
      const token = getToken(request);
      const sess = await getSession(token, env);
      if (!sess) return json({ error: "Token yo'q" }, 401);

      const list = await env.AGENT_KV.list({ prefix: "chat:" });
      const chats = [];
      for (const k of list.keys) {
        const parts = k.name.replace("chat:", "").split("-");
        const a = parseInt(parts[0]);
        const b = parseInt(parts[1]);
        if (a === sess.id || b === sess.id) {
          const other = a === sess.id ? b : a;
          const otherUser = await getUserById(other, env);
          if (otherUser) {
            const msgs = await getChat(sess.id, other, env);
            chats.push({
              withId: other,
              withName: otherUser.displayName || otherUser.name,
              lastMsg: msgs.length ? msgs[msgs.length - 1].text : "",
              lastTime: msgs.length ? msgs[msgs.length - 1].time : 0
            });
          }
        }
      }
      chats.sort((a, b) => b.lastTime - a.lastTime);
      return json({ chats: chats });
      }
        // ============================================================
    // 🎨 RASM GENERATSIYA
    // ============================================================
    if (path === "/image" && request.method === "POST") {
      try {
        const body = await request.json();
        const prompt = (body.prompt || "").trim();
        const w = parseInt(body.w || "768");
        const h = parseInt(body.h || "768");
        if (!prompt) return json({ error: "Prompt kerak" }, 400);
        if (prompt.length > 500) return json({ error: "Prompt juda uzun" }, 400);

        const url = imageUrl(prompt, w, h);
        return json({ imageUrl: url, prompt: prompt });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 📊 ADMIN: ACTIVITY
    // ============================================================
    if (path === "/admin/activity" && request.method === "GET") {
      const token = getToken(request);
      const sess = await getSession(token, env);
      if (!sess || sess.rol !== "admin") return json({ error: "Faqat admin" }, 403);

      const activity = await getActivity(env);
      const last24 = activity.filter(a => Date.now() - a.time < 86400000);
      return json({ activity: last24 });
    }

    // ============================================================
    // 📊 ADMIN: STATS
    // ============================================================
    if (path === "/admin/stats" && request.method === "GET") {
      const token = getToken(request);
      const sess = await getSession(token, env);
      if (!sess || sess.rol !== "admin") return json({ error: "Faqat admin" }, 403);

      const users = await listUsers(env);
      const activity = await getActivity(env);
      const online = users.filter(u => Date.now() - (u.lastSeen || 0) < 5 * 60 * 1000).length;

      return json({
        users: users.length,
        online: online,
        last24h: activity.filter(a => Date.now() - a.time < 86400000).length,
        list: users.map(u => ({
          id: u.id,
          name: u.name,
          displayName: u.displayName,
          rol: u.rol,
          lastSeen: u.lastSeen,
          visits: u.visits,
          joined: u.joined
        }))
      });
    }

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
          geminiCall(m.id, sysMsg, question, env, 500).then(r => ({
            emoji: m.emoji,
            name: m.name,
            answer: r.error ? ("❌ " + r.error) : r.text
          }))
        );
        const answers = await Promise.all(promises);

        let judgePrompt = 'Savol: "' + question + '"\n\n';
        answers.forEach((a, i) => { judgePrompt += (i+1) + ". " + a.name + ":\n" + a.answer + "\n\n"; });
        judgePrompt += "Umumiy xulosa yoz.";

        const jr = await geminiCall("gemini-3.8-flash", judgeSys, judgePrompt, env, 700);
        const conclusion = jr.error ? ("❌ " + jr.error) : jr.text;

        return json({ answers: answers, conclusion: conclusion });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 🌙 DREAM
    // ============================================================
    if (path === "/dream" && request.method === "POST") {
      try {
        const body = await request.json();
        const dream = (body.dream || "").trim();
        if (!dream) return json({ error: "Tush matni yo'q" }, 400);

        const r = await geminiCall("gemini-3.8-flash", DREAM_SYSTEM, dream, env, 600);
        if (r.error) return json({ error: "AI: " + r.error }, 500);

        let data = { analysis: "?", symbols: [], mood: "g'alati", imagePrompt: "dream" };
        try {
          const s = r.text.indexOf("{");
          const e = r.text.lastIndexOf("}") + 1;
          if (s >= 0 && e > s) data = Object.assign(data, JSON.parse(r.text.slice(s, e)));
        } catch(e) {}

        return json({
          analysis: data.analysis,
          symbols: data.symbols || [],
          mood: data.mood || "g'alati",
          imageUrl: imageUrl(data.imagePrompt || "dream")
        });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // ⏰ TIME
    // ============================================================
    if (path === "/time" && request.method === "POST") {
      try {
        const body = await request.json();
        const year = String(body.year || "").trim();
        const place = (body.place || "").trim();
        if (!year) return json({ error: "Yil kerak" }, 400);

        const p = "Yil: " + year + (place ? " Joy: " + place : "");
        const r = await geminiCall("gemini-3.8-flash", TIME_SYSTEM, p, env, 600);
        if (r.error) return json({ error: r.error }, 500);

        let data = { story: "?", fact: "", imagePrompt: year };
        try {
          const s = r.text.indexOf("{");
          const e = r.text.lastIndexOf("}") + 1;
          if (s >= 0 && e > s) data = Object.assign(data, JSON.parse(r.text.slice(s, e)));
        } catch(e) {}

        return json({
          story: data.story,
          fact: data.fact || "",
          imageUrl: imageUrl(data.imagePrompt || year)
        });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 🎲 WORLD
    // ============================================================
    if (path === "/world" && request.method === "POST") {
      try {
        const r = await geminiCall("gemini-3.8-flash", WORLD_SYSTEM, "Yangi fantastik dunyo yarat", env, 600);
        if (r.error) return json({ error: r.error }, 500);

        let data = { name: "?", story: "?", fact: "", imagePrompt: "fantasy world" };
        try {
          const s = r.text.indexOf("{");
          const e = r.text.lastIndexOf("}") + 1;
          if (s >= 0 && e > s) data = Object.assign(data, JSON.parse(r.text.slice(s, e)));
        } catch(e) {}

        return json({
          name: data.name,
          story: data.story,
          fact: data.fact || "",
          imageUrl: imageUrl(data.imagePrompt || "fantasy world")
        });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // ⚔️ DEBATE
    // ============================================================
    if (path === "/debate" && request.method === "POST") {
      try {
        const body = await request.json();
        const topic = (body.topic || "").trim();
        if (!topic) return json({ error: "Mavzu kerak" }, 400);

        const [f, a] = await Promise.all([
          geminiCall("gemini-3.8-flash", DEBATE_FOR, topic, env, 400),
          geminiCall("gemini-3.8-flash", DEBATE_AGAINST, topic, env, 400)
        ]);

        const forArg = f.error ? "?" : f.text;
        const againstArg = a.error ? "?" : a.text;

        const jp = "Mavzu: " + topic + "\n\nFOR:\n" + forArg + "\n\nAGAINST:\n" + againstArg + "\n\nKim yaxshiroq?";
        const jr = await geminiCall("gemini-3.8-flash", DEBATE_JUDGE, jp, env, 400);

        return json({
          forArg: forArg,
          againstArg: againstArg,
          verdict: jr.error ? "?" : jr.text
        });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 🎭 TURING
    // ============================================================
    if (path === "/turing" && request.method === "POST") {
      try {
        const body = await request.json();

        if (body.action === "topic") {
          const topic = TURING_TOPICS[Math.floor(Math.random() * TURING_TOPICS.length)];
          return json({ topic: topic });
        }

        if (body.action === "judge") {
          const topic = (body.topic || "").trim();
          const userAnswer = (body.userAnswer || "").trim();
          if (!topic || !userAnswer) return json({ error: "Kerak" }, 400);

          const aiHuman = "Sen 14 yoshli o'smirsan. Oddiy, sodda javob yoz (2-4 gap).\n\nSavol: " + topic;
          const aiR = await geminiCall("gemini-3.8-flash", "Sen o'smirsan.", aiHuman, env, 400);
          const aiAnswer = aiR.error ? "?" : aiR.text;

          const userFirst = Math.random() < 0.5;
          const a1 = userFirst ? userAnswer : aiAnswer;
          const a2 = userFirst ? aiAnswer : userAnswer;

          const jp = "SAVOL: " + topic + "\n\nJAVOB 1:\n" + a1 + "\n\nJAVOB 2:\n" + a2 + '\n\nQaysi biri odam? FAQAT JSON: {"human":1,"reason":"sabab"}';
          const jr = await geminiCall("gemini-3.8-flash", "Sen hakamsan.", jp, env, 300);

          let jd = { human: 1, reason: "?" };
          if (!jr.error) {
            try {
              const s = jr.text.indexOf("{");
              const e = jr.text.lastIndexOf("}") + 1;
              if (s >= 0 && e > s) jd = JSON.parse(jr.text.slice(s, e));
            } catch(e) {}
          }

          const actual = userFirst ? 1 : 2;
          return json({
            answer1: a1,
            answer2: a2,
            judgeVerdict: "Hakam " + jd.human + "-javobni odam deb topdi",
            humanIsUser: userFirst,
            userWins: jd.human !== actual,
            reasoning: jd.reason || ""
          });
        }

        return json({ error: "Noma'lum action" }, 400);
      } catch(e) {
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
        return json({ reply: reply });
      } catch(e) {
        return json({ error: e.message }, 500);
      }
    }

    // ============================================================
    // 🤖 TELEGRAM WEBHOOK
    // ============================================================
    if (path === "/webhook" && request.method === "POST") {
      let update;
      try { update = await request.json(); } catch(e) { return new Response("ok"); }
      const msg = update.message || update.edited_message;
      if (!msg || !msg.text) return new Response("ok");

      const chatId = msg.chat.id;
      const text = msg.text.trim();
      const name = msg.chat.first_name || "Blip";

      if (text === "/start") {
        await sendTg(chatId, "Salom " + name + "! 👋 Men Blip Agent.", env);
        return new Response("ok");
      }
      if (text === "/reset") {
        await env.AGENT_KV.delete("hist:" + chatId);
        await sendTg(chatId, "🧹 Tozalandi.", env);
        return new Response("ok");
      }

      try {
        await sendTyping(chatId, env);
        const reply = await agentLoop(text, chatId, env);
        await sendTg(chatId, reply, env);
      } catch(e) {
        await sendTg(chatId, "❌ " + e.message, env);
      }
      return new Response("ok");
    }

    // ============================================================
    // 🏠 HEALTH
    // ============================================================
    return new Response("Blip Core v6.0 ishlayapti ✅\n\nAuth + Chat + Image + AI", {
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
};
