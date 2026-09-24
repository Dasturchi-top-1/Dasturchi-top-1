# ============================================================
# 🎬 BLIP YOUTUBE AGENT v2.0 — 1-QISM
# Fayl: blip_youtube_agent.py
# Papka: /storage/emulated/0/Ai/YouTubeAgent/
# Parol + Buyruqsiz AI
# ⚠️ Bu faylni GitHub'ga YUKLAMANG!
# ============================================================
import os, sys, json, time, re, datetime
import urllib.request, urllib.parse, urllib.error

# ============================================================
# ⚠️ TOKENLAR — SHU YERNI TO'LDIRING!
# ============================================================
BOT_TOKEN = "YOUR_TOKEN"
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY"

# ============================================================
# 🔐 PAROL
# ============================================================
MAXFIY_PAROL = "Blipzor921324"
MAX_URINISH = 3
SESSIYA_VAQTI = 30 * 24 * 3600

# ============================================================
# SOZLAMALAR
# ============================================================
LOYIHA_PAPKA = "/storage/emulated/0/Ai/YouTubeAgent"
os.makedirs(LOYIHA_PAPKA, exist_ok=True)

STATE_FILE = f"{LOYIHA_PAPKA}/youtube_state.json"
SESS_FILE = f"{LOYIHA_PAPKA}/sessions.json"
LOG_FILE = f"{LOYIHA_PAPKA}/youtube_agent.log"

# Kanal ma'lumotlari
KANAL_NOMI = "Blip"
KANAL_TILI = "O'zbek"
KANAL_YOSHI = 13
KANAL_MAVZULARI = [
    "Python dasturlash", "Sun'iy intellekt",
    "Dasturlash darslari", "Kiber-atletika", "Ingliz tili"
]

AI_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODELS = [
    "nex-agi/nex-n2.5-pro:free",
    "nex-agi/nex-n2.5-mini:free",
    "qwen/qwen3.8-27b:free",
]

SYSTEM_PROMPT = (
    "Sen BLIP YouTube Agent — professional YouTube "
    "kontent yaratuvchi yordamchisisan. "
    "Foydalanuvchi 13 yoshli Python dasturchi Blip. "
    "Uning kanali: Python, AI, dasturlash haqida. "
    "Har doim O'ZBEK TILIDA (lotin) javob ber. "
    "Amaliy va qo'llaniladigan maslahat ber."
)

INTENT_PROMPT = """Sen intent parser. Foydalanuvchi xabaridan niyatini JSON formatda aniqlaysan.

MUMKIN NIYATLAR:
1. reja — kanal boshlash rejasi
2. goya — video g'oyalar (mavzu kerak)
3. sarlavha — sarlavha yaratish (mavzu kerak)
4. tavsif — tavsif yozish (mavzu kerak)
5. teglar — teglar (mavzu kerak)
6. skript — video skript (mavzu kerak)
7. muqova — muqova g'oyasi (mavzu kerak)
8. kontent — 30 kunlik reja
9. trend — trend mavzular
10. stat — statistika
11. help — yordam
12. chat — oddiy suhbat

QOIDALAR:
- "reja", "boshla", "qanday boshlayman" → reja
- "goya", "g'oya", "fikr" → goya
- "sarlavha", "title" → sarlavha
- "tavsif", "description" → tavsif
- "teg", "tag", "hashtag" → teglar
- "skript", "script", "yoz" → skript
- "muqova", "thumbnail", "rasm" → muqova
- "kontent", "kalendar", "30 kun" → kontent
- "trend", "mashhur" → trend
- "stat", "statistika" → stat
- Boshqa → chat

FAQAT JSON qaytar.

MISOLLAR:
User: "Kanalni qanday boshlayman?"
→ {"intent": "reja"}

User: "Python uchun sarlavha"
→ {"intent": "sarlavha", "mavzu": "Python"}

User: "Salom"
→ {"intent": "chat", "javob": "Salom! Men Blip YouTube Agent. /reja bilan boshlang."}
"""

# ============================================================
# LOG
# ============================================================
def log(matn):
    try:
        if BOT_TOKEN: matn = matn.replace(BOT_TOKEN, "[TOKEN]")
        if OPENROUTER_KEY: matn = matn.replace(OPENROUTER_KEY, "[KEY]")
        if MAXFIY_PAROL: matn = matn.replace(MAXFIY_PAROL, "[PAROL]")
        vaqt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{vaqt}] {matn}\n")
    except: pass
    print(matn)

def tokenlarni_tekshir():
    xato = []
    if not BOT_TOKEN or BOT_TOKEN.startswith("BU_"): xato.append("BOT_TOKEN")
    if not OPENROUTER_KEY or OPENROUTER_KEY.startswith("BU_"): xato.append("OPENROUTER_KEY")
    if not MAXFIY_PAROL or len(MAXFIY_PAROL) < 6: xato.append("MAXFIY_PAROL")
    if xato:
        print("\n❌ To'ldirilmagan:")
        for x in xato: print(f"   • {x}")
        sys.exit(1)
    print("  ✅ Tokenlar va parol to'ldirilgan")

# ============================================================
# 🔐 SESSIYA
# ============================================================
_SESSIONS_MEM = {}

def load_sessions():
    if not os.path.exists(SESS_FILE): return {}
    try:
        with open(SESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_sessions(s):
    try:
        tmp = SESS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
        os.replace(tmp, SESS_FILE)
        return True
    except: return False

def sessiya_bor(chat_id):
    key = str(chat_id); hozir = time.time()
    if key in _SESSIONS_MEM:
        if hozir - _SESSIONS_MEM[key].get("vaqt", 0) < SESSIYA_VAQTI:
            _SESSIONS_MEM[key]["vaqt"] = hozir
            s = load_sessions(); s[key] = _SESSIONS_MEM[key]; save_sessions(s)
            return True
        del _SESSIONS_MEM[key]
    s = load_sessions()
    if key in s:
        if hozir - s[key].get("vaqt", 0) < SESSIYA_VAQTI:
            _SESSIONS_MEM[key] = s[key]
            _SESSIONS_MEM[key]["vaqt"] = hozir
            s[key]["vaqt"] = hozir; save_sessions(s)
            return True
        del s[key]; save_sessions(s)
    return False

def sessiya_yarat(chat_id):
    key = str(chat_id); hozir = time.time()
    ma = {"vaqt": hozir, "urinsh": 0}
    _SESSIONS_MEM[key] = ma
    s = load_sessions(); s[key] = ma; save_sessions(s)

def sessiya_ochir(chat_id):
    key = str(chat_id)
    _SESSIONS_MEM.pop(key, None)
    s = load_sessions(); s.pop(key, None); save_sessions(s)

def urinsh_oshir(chat_id):
    key = str(chat_id)
    if key not in _SESSIONS_MEM:
        _SESSIONS_MEM[key] = {"vaqt": time.time(), "urinsh": 0}
    _SESSIONS_MEM[key]["urinsh"] = _SESSIONS_MEM[key].get("urinsh", 0) + 1
    s = load_sessions(); s[key] = _SESSIONS_MEM[key]; save_sessions(s)
    return _SESSIONS_MEM[key]["urinsh"]

def parol_tekshir(matn):
    return matn.strip() == MAXFIY_PAROL

# ============================================================
# STORAGE
# ============================================================
def load_state():
    default = {
        "jami_sarlavha": 0, "jami_tavsif": 0,
        "jami_script": 0, "jami_goya": 0, "jami_reja": 0,
    }
    if not os.path.exists(STATE_FILE): return default
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default.items(): data.setdefault(k, v)
        return data
    except: return default

def save_state(state):
    try:
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, STATE_FILE)
        return True
    except: return False

# ============================================================
# TELEGRAM API
# ============================================================
def tg_request(method, params=None, timeout=35):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        if params:
            data = urllib.parse.urlencode(params).encode("utf-8")
            req = urllib.request.Request(url, data=data, method="POST")
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        log(f"⚠️ TG: {e}"); return None

def tg_send(chat_id, text, reply_to=None):
    if not text or not chat_id: return False
    if len(text) <= 4000:
        p = {"chat_id": chat_id, "text": text}
        if reply_to: p["reply_to_message_id"] = reply_to
        r = tg_request("sendMessage", p)
        return bool(r and r.get("ok"))
    ok = True
    for i in range(0, len(text), 4000):
        p = {"chat_id": chat_id, "text": text[i:i+4000]}
        r = tg_request("sendMessage", p)
        if not (r and r.get("ok")): ok = False
        time.sleep(0.3)
    return ok

def tg_typing(chat_id):
    tg_request("sendChatAction", {"chat_id": chat_id, "action": "typing"})

def tg_get_updates(offset, timeout=30):
    return tg_request("getUpdates", {
        "timeout": timeout, "offset": offset,
        "allowed_updates": json.dumps(["message"]),
    }, timeout=timeout + 10)
# ============================================================
# 🤖 AI FUNKSIYALAR
# ============================================================
def ai_request(model, system, user_text, timeout=60):
    if not OPENROUTER_KEY: return None
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_text}],
        "temperature": 0.8, "max_tokens": 1500,
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            AI_URL, data=data,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://blip.local",
                "X-Title": "Blip YouTube Agent",
            }, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            result = json.loads(r.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"⚠️ AI: {e}"); return None

def ai_ask(system, user_text):
    for model in AI_MODELS:
        natija = ai_request(model, system, user_text)
        if natija: return natija
        time.sleep(0.3)
    return None

def intent_aniqla(text):
    javob = ai_ask(INTENT_PROMPT, text)
    if not javob: return None
    try:
        if "```" in javob:
            javob = javob.split("```")[1]
            if javob.startswith("json"): javob = javob[4:]
            javob = javob.strip()
        start = javob.find("{"); end = javob.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(javob[start:end])
    except Exception as e:
        log(f"⚠️ Intent JSON: {e}")
    return None

# ============================================================
# 🎬 YOUTUBE FUNKSIYALAR
# ============================================================
def yt_reja():
    prompt = (
        f"13 yoshli Python dasturchi YouTube kanalini "
        f"noldan boshlamoqchi.\n\n"
        f"Ism: {KANAL_NOMI}\nYosh: {KANAL_YOSHI}\n"
        f"Til: {KANAL_TILI}\n"
        f"Mavzular: {', '.join(KANAL_MAVZULARI)}\n\n"
        f"BOSQICHMA-BOSQICH REJA yoz:\n"
        f"1. Kanal ochish (nomi, logotip, tavsif)\n"
        f"2. Birinchi 3 video nima haqida\n"
        f"3. Uskuna (telefon, mikrofon, yozish)\n"
        f"4. Dasturlar (montaj, ovoz)\n"
        f"5. Yuklash jadvali\n"
        f"6. SEO (sarlavha, tavsif, teglar)\n"
        f"7. O'sish strategiyasi (100 obunachi)\n"
        f"8. Monetizatsiya\n\n"
        f"Amaliy, aniq yoz. Emoji ishlat."
    )
    return ai_ask(SYSTEM_PROMPT, prompt)

def yt_sarlavha(mavzu):
    prompt = (
        f"'{mavzu}' mavzusida YouTube uchun 5 ta sarlavha yoz.\n\n"
        f"QOIDALAR:\n- 60 belgidan kam\n"
        f"- Qiziqarli va clickbait\n"
        f"- SEO kalit so'zlar\n- O'zbek tilida\n"
        f"- Raqamlar ishlat\n\n"
        f"Format:\n1. [Sarlavha]\n   💡 [Nega ishlaydi]\n2. ..."
    )
    return ai_ask(SYSTEM_PROMPT, prompt)

def yt_tavsif(mavzu):
    prompt = (
        f"'{mavzu}' mavzusida YouTube video uchun tavsif yoz.\n\n"
        f"FORMAT:\n1. Hook (2-3 gap)\n"
        f"2. Vaqt belgilari\n3. Asosiy ma'lumot (5-7 gap)\n"
        f"4. Call to action\n5. Hashtaglar (15-20)\n"
        f"6. Ijtimoiy tarmoq\n\nO'zbek tilida."
    )
    return ai_ask(SYSTEM_PROMPT, prompt)

def yt_teglar(mavzu):
    prompt = (
        f"'{mavzu}' mavzusida YouTube uchun 30 ta teg yoz.\n\n"
        f"- O'zbek + ingliz\n- Aralash (qisqa + uzun)\n"
        f"- Faqat vergul bilan ajratilgan ro'yxat\n\n"
        f"Format: python, dasturlash, ai, ..."
    )
    return ai_ask(SYSTEM_PROMPT, prompt)

def yt_skript(mavzu):
    prompt = (
        f"'{mavzu}' mavzusida YouTube video uchun skript yoz.\n\n"
        f"FORMAT:\n🎬 INTRO (0:00-0:30)\n   [Matn]\n"
        f"📚 ASOSIY QISM (0:30-5:00)\n   1. ...\n   2. ...\n"
        f"🎯 XULOSA (5:00-6:00)\n   [Matn]\n"
        f"📢 CALL TO ACTION\n\n"
        f"Har bir qismda aynan nima aytilishini yoz. O'zbek tilida."
    )
    return ai_ask(SYSTEM_PROMPT, prompt)

def yt_muqova(mavzu):
    prompt = (
        f"'{mavzu}' mavzusida YouTube video uchun muqova "
        f"(thumbnail) g'oyasi ber.\n\n"
        f"FORMAT:\n🎨 ASOSIY G'OYA: [1 gap]\n\n"
        f"📝 MATN (muqovadagi):\n   - Asosiy: [2-3 so'z]\n"
        f"   - Rang: [#hex]\n   - Font: [qanday]\n\n"
        f"🖼 TASVIR:\n   - Nima ko'rsatiladi\n"
        f"   - Rang palitrasi\n   - Emoji\n\n"
        f"🛠 QANDAY:\n   - Canva (bepul)\n   - Photopea (bepul)\n\n"
        f"O'zbek tilida."
    )
    return ai_ask(SYSTEM_PROMPT, prompt)

def yt_kontent():
    prompt = (
        f"13 yoshli Python dasturchi uchun 30 kunlik "
        f"YouTube kontent reja yoz.\n\n"
        f"Mavzular: {', '.join(KANAL_MAVZULARI)}\n"
        f"Haftada: 2-3 video\n\n"
        f"FORMAT:\n📅 1-hafta:\n"
        f"   Dushanba: [Mavzu] — [Nega]\n"
        f"   Chorshanba: ...\n   Juma: ...\n\n"
        f"📅 2-hafta: ...\n...\n\n"
        f"Har bir video uchun 1 gap tavsif. O'zbek tilida."
    )
    return ai_ask(SYSTEM_PROMPT, prompt)

def yt_trend():
    prompt = (
        f"2026-yilda YouTube'da O'zbek tilida trend bo'layotgan "
        f"5 ta texnologiya mavzusi ayt.\n\n"
        f"Har biri:\n- Mavzu\n- Nega trend\n"
        f"- Qanday video qilish\n- Qancha vaqt trend\n\n"
        f"O'zbek tilida."
    )
    return ai_ask(SYSTEM_PROMPT, prompt)

def yt_goya(mavzu):
    prompt = (
        f"'{mavzu}' mavzusida 10 ta video g'oyasi ber.\n\n"
        f"Har biri:\n1. [Sarlavha]\n   📝 [Qisqa tavsif]\n"
        f"   ⏱ [Taxminiy davomiylik]\n"
        f"   🎯 [Nima o'rganadi]\n\nO'zbek tilida."
    )
    return ai_ask(SYSTEM_PROMPT, prompt)
# ============================================================
# 💬 BUYRUQLAR
# ============================================================
def cmd_start(chat_id):
    tg_send(chat_id,
        "🎬 BLIP YOUTUBE AGENT v2.0\n\n"
        "YouTube kanal boshlashga yordam beraman!\n\n"
        "📋 BUYRUQLAR:\n"
        "/reja — Kanalni boshlash rejasi\n"
        "/goya mavzu — 10 ta video g'oya\n"
        "/sarlavha mavzu — 5 ta sarlavha\n"
        "/tavsif mavzu — Tavsif yozish\n"
        "/teglar mavzu — 30 ta teg\n"
        "/skript mavzu — Video skript\n"
        "/muqova mavzu — Muqova g'oyasi\n"
        "/kontent — 30 kunlik reja\n"
        "/trend — Trend mavzular\n"
        "/stat — Statistika\n"
        "/help — Yordam\n"
        "/logout — Chiqish\n\n"
        "💡 Yoki shunchaki yozing:\n"
        "\"sarlavha Python uchun\"")

def cmd_help(chat_id):
    tg_send(chat_id,
        "📖 YORDAM\n\n"
        "KANALNI BOSHLASH:\n"
        "1. /reja — batafsil reja\n"
        "2. /trend — trend mavzular\n"
        "3. /goya Python — g'oyalar\n"
        "4. /kontent — 30 kunlik reja\n\n"
        "VIDEO YARATISH:\n"
        "/sarlavha python nima\n"
        "/tavsif python nima\n"
        "/skript python nima\n"
        "/muqova python nima\n"
        "/teglar python nima\n\n"
        "💡 Yoki oddiy matn:\n"
        "\"Python uchun sarlavha yoz\"")

def cmd_reja(chat_id, state):
    tg_typing(chat_id)
    tg_send(chat_id, "⏳ Kanal rejasi tayyorlanmoqda...")
    javob = yt_reja()
    if javob:
        tg_send(chat_id, f"🎬 KANALNI BOSHLASH REJASI\n\n{javob}")
        state["jami_reja"] = state.get("jami_reja", 0) + 1
        save_state(state)
    else:
        tg_send(chat_id, "❌ AI javob bermadi")

def cmd_goya(chat_id, mavzu, state):
    if not mavzu:
        tg_send(chat_id, "❌ /goya <mavzu>\nMisol: /goya Python")
        return
    tg_typing(chat_id)
    tg_send(chat_id, f"⏳ '{mavzu}' uchun g'oyalar...")
    javob = yt_goya(mavzu)
    if javob:
        tg_send(chat_id, f"💡 VIDEO G'OYALAR\n\n{javob}")
        state["jami_goya"] = state.get("jami_goya", 0) + 1
        save_state(state)
    else:
        tg_send(chat_id, "❌ AI javob bermadi")

def cmd_sarlavha(chat_id, mavzu, state):
    if not mavzu:
        tg_send(chat_id, "❌ /sarlavha <mavzu>")
        return
    tg_typing(chat_id)
    tg_send(chat_id, f"⏳ '{mavzu}' uchun sarlavhalar...")
    javob = yt_sarlavha(mavzu)
    if javob:
        tg_send(chat_id, f"📝 SARLAVHALAR\n\n{javob}")
        state["jami_sarlavha"] = state.get("jami_sarlavha", 0) + 1
        save_state(state)
    else:
        tg_send(chat_id, "❌ AI javob bermadi")

def cmd_tavsif(chat_id, mavzu, state):
    if not mavzu:
        tg_send(chat_id, "❌ /tavsif <mavzu>")
        return
    tg_typing(chat_id)
    tg_send(chat_id, f"⏳ '{mavzu}' uchun tavsif...")
    javob = yt_tavsif(mavzu)
    if javob:
        tg_send(chat_id, f"📄 TAVSIF\n\n{javob}")
        state["jami_tavsif"] = state.get("jami_tavsif", 0) + 1
        save_state(state)
    else:
        tg_send(chat_id, "❌ AI javob bermadi")

def cmd_teglar(chat_id, mavzu):
    if not mavzu:
        tg_send(chat_id, "❌ /teglar <mavzu>")
        return
    tg_typing(chat_id)
    tg_send(chat_id, f"⏳ '{mavzu}' uchun teglar...")
    javob = yt_teglar(mavzu)
    if javob:
        tg_send(chat_id, f"🏷 TEGLAR\n\n{javob}")
    else:
        tg_send(chat_id, "❌ AI javob bermadi")

def cmd_skript(chat_id, mavzu, state):
    if not mavzu:
        tg_send(chat_id, "❌ /skript <mavzu>")
        return
    tg_typing(chat_id)
    tg_send(chat_id, f"⏳ '{mavzu}' uchun skript...")
    javob = yt_skript(mavzu)
    if javob:
        tg_send(chat_id, f"🎬 VIDEO SKRIPT\n\n{javob}")
        state["jami_script"] = state.get("jami_script", 0) + 1
        save_state(state)
    else:
        tg_send(chat_id, "❌ AI javob bermadi")

def cmd_muqova(chat_id, mavzu):
    if not mavzu:
        tg_send(chat_id, "❌ /muqova <mavzu>")
        return
    tg_typing(chat_id)
    tg_send(chat_id, f"⏳ '{mavzu}' uchun muqova...")
    javob = yt_muqova(mavzu)
    if javob:
        tg_send(chat_id, f"🎨 MUQOVA G'OYASI\n\n{javob}")
    else:
        tg_send(chat_id, "❌ AI javob bermadi")

def cmd_kontent(chat_id):
    tg_typing(chat_id)
    tg_send(chat_id, "⏳ 30 kunlik reja...")
    javob = yt_kontent()
    if javob:
        tg_send(chat_id, f"📅 30 KUNLIK REJA\n\n{javob}")
    else:
        tg_send(chat_id, "❌ AI javob bermadi")

def cmd_trend(chat_id):
    tg_typing(chat_id)
    tg_send(chat_id, "⏳ Trend mavzular...")
    javob = yt_trend()
    if javob:
        tg_send(chat_id, f"🔥 TREND MAVZULAR\n\n{javob}")
    else:
        tg_send(chat_id, "❌ AI javob bermadi")

def cmd_stat(chat_id, state):
    tg_send(chat_id,
        f"📊 STATISTIKA\n\n"
        f"📝 Sarlavhalar: {state.get('jami_sarlavha', 0)}\n"
        f"📄 Tavsiflar: {state.get('jami_tavsif', 0)}\n"
        f"🎬 Skriptlar: {state.get('jami_script', 0)}\n"
        f"💡 G'oyalar: {state.get('jami_goya', 0)}\n"
        f"📋 Rejalar: {state.get('jami_reja', 0)}\n\n"
        f"👤 Kanal: {KANAL_NOMI}\n"
        f"🌐 Til: {KANAL_TILI}")

# ============================================================
# 💬 XABARNI QAYTA ISHLASH
# ============================================================
def xabar_qayta_ishla(chat_id, text, state):
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lstrip("/").split("@")[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""
        if cmd == "start": cmd_start(chat_id)
        elif cmd == "help": cmd_help(chat_id)
        elif cmd == "reja": cmd_reja(chat_id, state)
        elif cmd == "goya": cmd_goya(chat_id, args, state)
        elif cmd == "sarlavha": cmd_sarlavha(chat_id, args, state)
        elif cmd == "tavsif": cmd_tavsif(chat_id, args, state)
        elif cmd == "teglar": cmd_teglar(chat_id, args)
        elif cmd == "skript": cmd_skript(chat_id, args, state)
        elif cmd == "muqova": cmd_muqova(chat_id, args)
        elif cmd == "kontent": cmd_kontent(chat_id)
        elif cmd == "trend": cmd_trend(chat_id)
        elif cmd == "stat": cmd_stat(chat_id, state)
        else: tg_send(chat_id, "❓ Buyruq yo'q. /help bosing.")
        return

    # Oddiy matn — AI intent
    tg_typing(chat_id)
    intent = intent_aniqla(text)
    if not intent:
        javob = ai_ask(SYSTEM_PROMPT, text)
        tg_send(chat_id, javob or "Tushunmadim. /help bosing.")
        return
    tur = intent.get("intent", "chat")
    mavzu = intent.get("mavzu", "")
    if tur == "reja": cmd_reja(chat_id, state)
    elif tur == "goya": cmd_goya(chat_id, mavzu, state)
    elif tur == "sarlavha": cmd_sarlavha(chat_id, mavzu, state)
    elif tur == "tavsif": cmd_tavsif(chat_id, mavzu, state)
    elif tur == "teglar": cmd_teglar(chat_id, mavzu)
    elif tur == "skript": cmd_skript(chat_id, mavzu, state)
    elif tur == "muqova": cmd_muqova(chat_id, mavzu)
    elif tur == "kontent": cmd_kontent(chat_id)
    elif tur == "trend": cmd_trend(chat_id)
    elif tur == "stat": cmd_stat(chat_id, state)
    elif tur == "help": cmd_help(chat_id)
    elif tur == "chat":
        javob = intent.get("javob", "")
        if not javob: javob = ai_ask(SYSTEM_PROMPT, text)
        tg_send(chat_id, javob or "Tushunmadim")
    else:
        javob = ai_ask(SYSTEM_PROMPT, text)
        tg_send(chat_id, javob or "Tushunmadim")

# ============================================================
# 🔐 PAROL
# ============================================================
def start_salom(chat_id, ism):
    tg_send(chat_id,
        f"🔐 BLIP YOUTUBE AGENT v2.0\n\n"
        f"Salom, {ism}!\n\n"
        f"Bu bot faqat egasi uchun.\n"
        f"Parolni yuboring:\n\n"
        f"❌ 3 urinish\n⏱ Sessiya: 30 kun")

def parol_ol(chat_id, matn):
    if parol_tekshir(matn):
        sessiya_yarat(chat_id)
        s = load_sessions()
        if str(chat_id) in s:
            s[str(chat_id)]["urinsh"] = 0
            save_sessions(s)
        tg_send(chat_id,
            "✅ PAROL TO'G'RI!\n\n"
            "Xush kelibsiz, Blip! 🎬\n\n"
            "📋 Buyruqlar:\n"
            "/reja — Kanal boshlash\n"
            "/trend — Trend mavzular\n"
            "/goya Python — G'oyalar\n"
            "/sarlavha Python — Sarlavha\n"
            "/skript Python — Skript\n"
            "/help — Yordam")
        log(f"✅ Parol: {chat_id}"); return True
    else:
        urinsh = urinsh_oshir(chat_id)
        qoldi = MAX_URINISH - urinsh
        if qoldi <= 0:
            tg_send(chat_id, "🚫 BLOKLANDI! 1 daqiqa kuting.")
            log(f"🚫 Blok: {chat_id}")
            time.sleep(60)
            s = load_sessions()
            if str(chat_id) in s:
                s[str(chat_id)]["urinsh"] = 0
                save_sessions(s)
        else:
            tg_send(chat_id, f"❌ Parol xato! Qolgan: {qoldi}")
        log(f"❌ Xato parol: {chat_id}")
        return False

def logout(chat_id):
    sessiya_ochir(chat_id)
    tg_send(chat_id, "👋 Chiqdingiz!\n\nQayta: /start")

# ============================================================
# 🔄 ASOSIY LOOP
# ============================================================
def main():
    log("🚀 BLIP YOUTUBE AGENT v2.0 ishga tushdi!")
    log(f"👤 Kanal: {KANAL_NOMI}")
    log(f"🔐 Parol: ✅")
    log(f"📁 {LOYIHA_PAPKA}")

    me = tg_request("getMe")
    if me and me.get("ok"):
        log(f"🤖 Bot: @{me['result'].get('username', '?')}")

    init = tg_get_updates(0, timeout=1)
    last_id = 0
    if init and init.get("ok"):
        ups = init.get("result", [])
        if ups: last_id = max(u.get("update_id", 0) for u in ups)

    log("🔄 Kuzatish boshlandi...\n")
    state = load_state()
    xato_soni = 0

    while True:
        try:
            updates = tg_get_updates(last_id + 1, timeout=25)
            if updates and updates.get("ok"):
                for up in updates.get("result", []):
                    msg = up.get("message")
                    if not msg: continue
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "").strip()
                    ism = msg.get("from", {}).get("first_name", "?")
                    if not chat_id or not text: continue

                    if text == "/start":
                        sessiya_ochir(chat_id)
                        start_salom(chat_id, ism)
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue
                    if text == "/logout":
                        logout(chat_id)
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue
                    if text == "/id":
                        tg_send(chat_id, f"🆔 ID: `{chat_id}`")
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue

                    if not sessiya_bor(chat_id):
                        parol_ol(chat_id, text)
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue

                    try:
                        xabar_qayta_ishla(chat_id, text, state)
                    except Exception as e:
                        log(f"⚠️ Xabar: {e}")
                        tg_send(chat_id, f"❌ Xato: {str(e)[:100]}")

                    uid = up.get("update_id", 0)
                    if uid > last_id: last_id = uid
                xato_soni = 0
            time.sleep(1)
        except KeyboardInterrupt:
            log("👋 To'xtatildi"); break
        except Exception as e:
            xato_soni += 1
            log(f"⚠️ Loop #{xato_soni}: {e}")
            time.sleep(min(xato_soni * 2, 30))

# ============================================================
# 🏁 ENTRY
# ============================================================
if __name__ == "__main__":
    os.system("clear" if os.name != "nt" else "cls")
    print("\n" + "=" * 55)
    print("  🎬 BLIP YOUTUBE AGENT v2.0")
    print("  Parol + Buyruqsiz AI")
    print("=" * 55)
    print(f"  📁 {LOYIHA_PAPKA}")
    print(f"  👤 {KANAL_NOMI} | {KANAL_TILI}")
    print(f"  🔐 Parol: ✅")
    print("=" * 55)
    tokenlarni_tekshir()
    try:
        main()
    except KeyboardInterrupt:
        log("\n👋 Xayr!")
    except Exception as e:
        log(f"❌ {e}")