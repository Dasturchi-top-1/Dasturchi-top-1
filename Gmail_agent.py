# ============================================================
# 📧 BLIP MAIL BOT v7.1 — Flask + Webhook (Render uchun)
# ============================================================
import os, json, time, sqlite3, re, datetime
import urllib.request, urllib.parse
import imaplib, email
from email.header import decode_header
from flask import Flask, request

# ============================================================
# ⚙️ SOZLAMALAR — Render Environment Variables dan olinadi
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
MAXFIY_PAROL = os.environ.get("MAXFIY_PAROL", "Blipzor921324")

MAX_URINISH = 3
SESSIYA_VAQTI = 30 * 24 * 3600
IMAP_SERVER = "imap.gmail.com"
AI_URL = "https://openrouter.ai/api/v1/chat/completions"

AI_MODELS = [
    "google/gemini-2.5-flash-lite",
    "openai/gpt-4o-mini",
    "anthropic/claude-3-haiku",
]

LOYIHA_PAPKA = "."
DB_FILE = os.path.join(LOYIHA_PAPKA, "mail_bot.db")
SESS_FILE = os.path.join(LOYIHA_PAPKA, "sessions.json")
LOG_FILE = os.path.join(LOYIHA_PAPKA, "mail_bot.log")

app = Flask(__name__)
ADMIN_ID = [0]

# ============================================================
# 📝 AI PROMPTLAR
# ============================================================
INTENT_P = """Sen intent parser. Foydalanuvchi xabaridan niyatni JSON da aniqlaysan.

MUMKIN NIYATLAR:
check, list, read, stat, auto_on, auto_off, help, chat

QOIDALAR:
- "tekshir","yangi","email bormi" → check
- "royxat","list","ko'rsat" → list
- "o'qi","read","N-email" → read (id bilan)
- "stat","statistika" → stat
- "avtomatik yoq" → auto_on
- "avtomatik ochir" → auto_off
- "yordam","help" → help
- Boshqa → chat

FAQAT JSON qaytar. Internet haqida gapirma.

MISOLLAR:
"Yangi email bormi?" → {"intent":"check"}
"Emaillarni ko'rsat" → {"intent":"list"}
"5-emailni o'qi" → {"intent":"read","id":5}
"Salom" → {"intent":"chat","javob":"Salom! Men Blip Mail Bot."}
"""

SYSTEM_PROMPT = (
    "Sen BLIP MAIL BOT yordamchisisan. "
    "Har doim O'ZBEK TILIDA (lotin) javob ber. Qisqa yoz. "
    "Faqat foydalanuvchi so'ragan narsani bajar. "
    "Internetga ulanishing haqida gapirma."
)

# ============================================================
# 🛡 MAXFIY HIMOYA
# ============================================================
XAVFLI = [
    (r"(?i)(password|parol|pwd)\s*[:=]\s*\S+", "[PAROL]"),
    (r"(?i)(kod|code|pin|otp)\s*[:=]\s*\d{4,8}", "[KOD]"),
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[KARTA]"),
    (r"ghp_[A-Za-z0-9]{20,}", "[GH_TOKEN]"),
    (r"sk-or-v1-[A-Za-z0-9-]{20,}", "[OR_KEY]"),
    (r"sk-[A-Za-z0-9]{20,}", "[KEY]"),
    (r"AIza[A-Za-z0-9_-]{20,}", "[GOOGLE_KEY]"),
    (r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b", "[BOT]"),
]

def maxfiy_tozala(matn):
    if not matn: return ""
    for p, a in XAVFLI: matn = re.sub(p, a, matn)
    return matn

# ============================================================
# 📝 LOG
# ============================================================
def log(matn):
    try:
        if BOT_TOKEN: matn = matn.replace(BOT_TOKEN, "[TOKEN]")
        if OPENROUTER_KEY: matn = matn.replace(OPENROUTER_KEY, "[KEY]")
        if GMAIL_PASS: matn = matn.replace(GMAIL_PASS, "[PASS]")
        v = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{v}] {matn}\n")
    except: pass
    print(matn)

# ============================================================
# 🔐 SESSIYA
# ============================================================
_SESS = {}

def load_sess():
    if not os.path.exists(SESS_FILE): return {}
    try:
        with open(SESS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_sess(s):
    try:
        with open(SESS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False)
    except: pass

def sess_bor(cid):
    k = str(cid); h = time.time()
    if k in _SESS and h - _SESS[k].get("v", 0) < SESSIYA_VAQTI:
        _SESS[k]["v"] = h; return True
    s = load_sess()
    if k in s and h - s[k].get("v", 0) < SESSIYA_VAQTI:
        _SESS[k] = s[k]; _SESS[k]["v"] = h; return True
    return False

def sess_yarat(cid):
    k = str(cid); _SESS[k] = {"v": time.time(), "u": 0}
    s = load_sess(); s[k] = _SESS[k]; save_sess(s)

def sess_ochir(cid):
    k = str(cid); _SESS.pop(k, None)
    s = load_sess(); s.pop(k, None); save_sess(s)

def urinsh(cid):
    k = str(cid)
    if k not in _SESS: _SESS[k] = {"v": time.time(), "u": 0}
    _SESS[k]["u"] = _SESS[k].get("u", 0) + 1
    s = load_sess(); s[k] = _SESS[k]; save_sess(s)
    return _SESS[k]["u"]

# ============================================================
# 📤 TELEGRAM
# ============================================================
def tg(method, params=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        if params:
            d = urllib.parse.urlencode(params).encode()
            req = urllib.request.Request(url, data=d, method="POST")
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=35) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        log(f"⚠️ TG: {e}"); return None

def send(cid, text):
    if not text or not cid: return
    for i in range(0, len(text), 4000):
        tg("sendMessage", {"chat_id": cid, "text": text[i:i+4000]})
        if len(text) > 4000: time.sleep(0.3)

def typing(cid):
    tg("sendChatAction", {"chat_id": cid, "action": "typing"})

# ============================================================
# 🗄 BAZA
# ============================================================
def db_init():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT, msg_id TEXT UNIQUE,
        kimdan TEXT, mavzu TEXT, matn TEXT, sana TEXT,
        tarjima TEXT, hisobot TEXT, yaratilgan TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY, auto_check INTEGER DEFAULT 1)""")
    c.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
    conn.commit(); conn.close()

def em_saqlash(em, t="", h=""):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    try:
        c.execute("""INSERT INTO emails
            (msg_id,kimdan,mavzu,matn,sana,tarjima,hisobot,yaratilgan)
            VALUES (?,?,?,?,?,?,?,?)""",
            (em["msg_id"], em["kimdan"], em["mavzu"], em["matn"],
             em["sana"], t, h, str(datetime.date.today())))
        conn.commit(); i = c.lastrowid; conn.close(); return i
    except sqlite3.IntegrityError:
        conn.close(); return None

def em_royxat(n=15):
    c = sqlite3.connect(DB_FILE).cursor()
    c.execute("SELECT id,kimdan,mavzu,sana FROM emails ORDER BY id DESC LIMIT ?", (n,))
    r = c.fetchall(); c.connection.close(); return r

def em_ol(eid):
    c = sqlite3.connect(DB_FILE).cursor()
    c.execute("SELECT id,kimdan,mavzu,matn,sana,tarjima,hisobot FROM emails WHERE id=?", (eid,))
    r = c.fetchone(); c.connection.close(); return r

def em_stat():
    c = sqlite3.connect(DB_FILE).cursor()
    c.execute("SELECT COUNT(*) FROM emails"); j = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM emails WHERE tarjima != ''"); t = c.fetchone()[0]
    c.connection.close(); return j, t

def auto_holat():
    c = sqlite3.connect(DB_FILE).cursor()
    c.execute("SELECT auto_check FROM settings WHERE id=1")
    r = c.fetchone(); c.connection.close(); return r[0] if r else 1

def auto_set(v):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE settings SET auto_check=? WHERE id=1", (v,))
    conn.commit(); conn.close()

# ============================================================
# 🤖 AI
# ============================================================
def ai_req(model, sys_p, user):
    if not OPENROUTER_KEY: return None
    payload = {"model": model, "messages": [
        {"role": "system", "content": sys_p},
        {"role": "user", "content": user}],
        "temperature": 0.7, "max_tokens": 800}
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(AI_URL, data=data, headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode())["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"⚠️ AI: {e}"); return None

def ai_ask(sys_p, user):
    for m in AI_MODELS:
        n = ai_req(m, sys_p, user)
        if n: return n
        time.sleep(0.3)
    return None

def intent(text):
    j = ai_ask(INTENT_P, text)
    if not j: return None
    try:
        if "```" in j:
            j = j.split("```")[1]
            if j.startswith("json"): j = j[4:]
        s, e = j.find("{"), j.rfind("}") + 1
        if s >= 0 and e > s: return json.loads(j[s:e])
    except: pass
    return None

def til_aniq(m):
    if not m: return "uz"
    k = len(re.findall(r"[а-яА-ЯёЁ]", m))
    i = len(re.findall(r"[a-zA-Z]", m))
    if k > i and k > 10: return "ru"
    if i > k and i > 10: return "en"
    return "uz"

def tarjima(m, t):
    if not m: return ""
    tn = "rus" if t == "ru" else "ingliz"
    return ai_ask("Sen tarjimonsan. O'zbek tilida.",
        f"{tn} tilidagi matnni O'ZBEK TILIGA tarjima qil:\n\n{maxfiy_tozala(m)[:1500]}") or ""

def hisobot(mavzu, kimdan, matn, til):
    return ai_ask("Sen email tahlilchisisan. O'zbek tilida.",
        f"Email haqida qisqa hisobot:\nKimdan: {kimdan}\nMavzu: {maxfiy_tozala(mavzu)}\n"
        f"Til: {til}\nMatn: {maxfiy_tozala(matn)[:1200]}") or ""

# ============================================================
# 📧 GMAIL
# ============================================================
def gmail():
    try:
        m = imaplib.IMAP4_SSL(IMAP_SERVER)
        m.login(GMAIL_USER, GMAIL_PASS); return m
    except Exception as e:
        log(f"❌ Gmail: {e}"); return None

def matn_ol(msg):
    matn = ""
    if msg.is_multipart():
        for p in msg.walk():
            ct = p.get_content_type()
            if ct == "text/plain":
                try: matn = p.get_payload(decode=True).decode("utf-8", "ignore"); break
                except: pass
            elif ct == "text/html" and not matn:
                try:
                    h = p.get_payload(decode=True).decode("utf-8", "ignore")
                    matn = re.sub(r"<[^>]+>", "", h)
                except: pass
    else:
        try: matn = msg.get_payload(decode=True).decode("utf-8", "ignore")
        except: pass
    return matn.strip()[:3000]

def email_ol(limit=10):
    m = gmail()
    if not m: return []
    try:
        m.select("INBOX")
        t, d = m.search(None, "UNSEEN")
        ids = d[0].split()[-limit:]
        natija = []
        for eid in reversed(ids):
            try:
                t, md = m.fetch(eid, "(RFC822)")
                msg = email.message_from_bytes(md[0][1])
                kimdan = msg.get("From", "")
                kimdan = decode_header(kimdan)[0][0]
                if isinstance(kimdan, bytes): kimdan = kimdan.decode("utf-8", "ignore")
                mavzu = ""
                for p, e in decode_header(msg.get("Subject", "")):
                    mavzu += p.decode(e or "utf-8", "ignore") if isinstance(p, bytes) else p
                natija.append({"msg_id": msg.get("Message-ID", str(eid)),
                    "kimdan": kimdan, "mavzu": mavzu or "(mavzusiz)",
                    "matn": matn_ol(msg), "sana": msg.get("Date", "")})
            except Exception as e: log(f"⚠️ {eid}: {e}")
        m.logout(); return natija
    except Exception as e:
        log(f"❌: {e}"); return []

# ============================================================
# 📥 YANGI EMAILLAR
# ============================================================
def yangi_tekshir(admin):
    emlar = email_ol(10)
    if not emlar: return 0
    n = 0
    for em in emlar:
        n += 1
        til = til_aniq(em["matn"] + " " + em["mavzu"])
        tarj = tarjima(em["matn"], til) if til in ("ru", "en") else ""
        his = hisobot(em["mavzu"], em["kimdan"], em["matn"], til)
        if not em_saqlash(em, tarj, his): continue
        t_em = {"ru": "🇷🇺", "en": "🇬🇧", "uz": "🇺🇿"}
        x = (f"📧 YANGI EMAIL\n\n👤 {em['kimdan']}\n📌 {em['mavzu']}\n"
             f"📅 {em['sana'][:25]}\n🌐 {t_em.get(til,'❓')} {til.upper()}\n\n"
             f"📝 {maxfiy_tozala(em['matn'])[:400]}\n")
        if tarj: x += f"\n🌐 TARJIMA:\n{tarj[:800]}\n"
        if his: x += f"\n🤖 HISOBOT:\n{his}"
        if admin: send(admin, x)
    return n

# ============================================================
# 💬 BUYRUQLAR
# ============================================================
def cmd_start(cid):
    send(cid, "📧 BLIP MAIL BOT v7.1\n\n/check /list /read /stat\n/auto /help /logout\n\n"
        "💡 Yoki yozing:\n• \"yangi email bormi?\"\n• \"emaillarni ko'rsat\"")

def cmd_help(cid):
    send(cid, "📖 YORDAM\n\n/check — Yangi\n/list — Ro'yxat\n/read id — O'qish\n"
        "/stat — Statistika\n/auto on/off — Avtomatik\n/logout — Chiqish")

def cmd_check(cid):
    send(cid, "⏳ Tekshirilmoqda...")
    n = yangi_tekshir(cid)
    if n == 0: send(cid, "📭 Yangi email yo'q")

def cmd_list(cid):
    r = em_royxat()
    if not r: send(cid, "📭 Email yo'q"); return
    t = "📋 EMAILLAR:\n\n"
    for x in r: t += f"📝 {x[0]}. {x[2][:40]}\n   👤 {x[1][:25]}\n\n"
    send(cid, t)

def cmd_read(cid, args):
    if not args: send(cid, "❌ /read id"); return
    try: eid = int(args[0])
    except: send(cid, "❌ Raqam"); return
    em = em_ol(eid)
    if not em: send(cid, "❌ Topilmadi"); return
    t = f"📧 {em[2]}\n\n👤 {em[1]}\n📅 {em[4]}\n\n📝 {maxfiy_tozala(em[3])[:2000]}"
    if em[5]: t += f"\n\n🌐 TARJIMA:\n{em[5][:1500]}"
    if em[6]: t += f"\n\n🤖 HISOBOT:\n{em[6]}"
    send(cid, t)

def cmd_stat(cid):
    j, t = em_stat(); a = auto_holat()
    send(cid, f"📊 STATISTIKA\n\n📧 Jami: {j}\n🌐 Tarjima: {t}\n"
        f"⚙️ Avtomatik: {'✅' if a else '❌'}\n🔐 Sessiya: ✅")

def cmd_auto(cid, args):
    if not args:
        send(cid, f"⚙️ Avtomatik: {'✅' if auto_holat() else '❌'}\n/auto on | /auto off"); return
    v = 1 if args[0].lower() in ("on", "yoq", "1") else 0
    auto_set(v); send(cid, f"✅ Avtomatik: {'YONIQ' if v else 'OCHIQ'}")

# ============================================================
# 💬 XABAR
# ============================================================
def xabar(cid, text):
    if text.startswith("/"):
        p = text.split(); c = p[0].lstrip("/").split("@")[0].lower(); a = p[1:]
        if c == "start": cmd_start(cid)
        elif c == "help": cmd_help(cid)
        elif c == "check": cmd_check(cid)
        elif c == "list": cmd_list(cid)
        elif c == "read": cmd_read(cid, a)
        elif c == "stat": cmd_stat(cid)
        elif c == "auto": cmd_auto(cid, a)
        else: send(cid, "❓ /help bosing.")
        return
    typing(cid)
    it = intent(text)
    if not it:
        j = ai_ask(SYSTEM_PROMPT, text)
        send(cid, j or "Tushunmadim. /help"); return
    t = it.get("intent", "chat")
    if t == "check": cmd_check(cid)
    elif t == "list": cmd_list(cid)
    elif t == "read": cmd_read(cid, [str(it.get("id", 0))])
    elif t == "stat": cmd_stat(cid)
    elif t == "auto_on": cmd_auto(cid, ["on"])
    elif t == "auto_off": cmd_auto(cid, ["off"])
    elif t == "help": cmd_help(cid)
    else:
        j = it.get("javob", "") or ai_ask(SYSTEM_PROMPT, text)
        send(cid, j or "Tushunmadim")

def parol_ol(cid, matn):
    if matn.strip() == MAXFIY_PAROL:
        sess_yarat(cid)
        send(cid, "✅ PAROL TO'G'RI!\n\nXush kelibsiz, Blip! 🚀\n\n/help — Yordam")
        return True
    u = urinsh(cid); q = MAX_URINISH - u
    send(cid, f"❌ Parol xato! Qolgan: {q}" if q > 0 else "🚫 Bloklandi! 1 daqiqa")
    if q <= 0:
        time.sleep(60)
        _SESS[str(cid)] = {"v": time.time(), "u": 0}
    return False

# ============================================================
# 🌐 FLASK
# ============================================================
@app.route("/")
def index():
    return "Blip Mail Bot v7.1 ishlayapti ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        up = request.get_json()
        msg = up.get("message") or up.get("edited_message")
        if not msg or "text" not in msg: return "ok"
        cid = msg["chat"]["id"]; text = msg["text"].strip()
        ism = msg.get("from", {}).get("first_name", "?")

        if text == "/start":
            sess_ochir(cid)
            send(cid, f"🔐 BLIP MAIL BOT v7.1\n\nSalom, {ism}!\nParolni yuboring:\n❌ 3 urinish")
            return "ok"
        if text == "/logout":
            sess_ochir(cid); send(cid, "👋 Chiqdingiz"); return "ok"
        if text == "/id":
            send(cid, f"🆔 {cid}"); return "ok"

        if not sess_bor(cid):
            parol_ol(cid, text); return "ok"

        if not ADMIN_ID[0]: ADMIN_ID[0] = cid

        try: xabar(cid, text)
        except Exception as e:
            log(f"⚠️ {e}"); send(cid, f"❌ {str(e)[:100]}")
        return "ok"
    except Exception as e:
        log(f"❌ Webhook: {e}"); return "ok"

@app.route("/auto_check")
def auto_check():
    try:
        if auto_holat() and ADMIN_ID[0]:
            yangi_tekshir(ADMIN_ID[0])
        return "ok"
    except Exception as e:
        log(f"⚠️ {e}"); return "error"

# ============================================================
# 🏁
# ============================================================
if __name__ == "__main__":
    log("🚀 Blip Mail Bot v7.1 (Webhook)")
    db_init()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
