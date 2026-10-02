# ============================================================
# 📧 BLIP MAIL BOT v6.0 — 1-QISM
# Fayl: blip_mail_bot.py
# Papka: /storage/emulated/0/Ai/MailBot/
# ⚠️ Bu faylni GitHub'ga YUKLAMANG!
# ============================================================
import os, sys, json, time, sqlite3, re
import datetime, urllib.request, urllib.parse, urllib.error
import imaplib, email
from email.header import decode_header

# ============================================================
# ⚠️ TOKENLAR — SHU YERNI TO'LDIRING!
# ============================================================
BOT_TOKEN = "YOUR_TOKEN"
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY"
GMAIL_USER = "YOUR_GMAIL"
GMAIL_PASS = "YOUR_PASS"

# ============================================================
# 🔐 PAROL
# ============================================================
MAXFIY_PAROL = "Blipzor921324"
MAX_URINISH = 3
SESSIYA_VAQTI = 30 * 24 * 3600

# ============================================================
# SOZLAMALAR
# ============================================================
LOYIHA_PAPKA = "/storage/emulated/0/Ai/MailBot"
os.makedirs(LOYIHA_PAPKA, exist_ok=True)
DB_FILE = f"{LOYIHA_PAPKA}/mail_bot.db"
SESS_FILE = f"{LOYIHA_PAPKA}/sessions.json"
LOG_FILE = f"{LOYIHA_PAPKA}/mail_bot.log"
IMAP_SERVER = "imap.gmail.com"
CHECK_INTERVAL = 300

AI_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODELS = [
    "nex-agi/nex-n2.5-pro:free",
    "nex-agi/nex-n2.5-mini:free",
    "qwen/qwen3.8-27b:free",
]

# ============================================================
# 🛡 MAXFIY HIMOYA
# ============================================================
XAVFLI = [
    (r"(?i)(password|parol|pwd)\s*[:=]\s*\S+", "[PAROL]"),
    (r"(?i)(kod|code|pin|otp)\s*[:=]\s*\d{4,8}", "[KOD]"),
    (r"(?i)(passport|pasport|id)\s*[:=]?\s*[A-Z0-9]{8,15}", "[ID]"),
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[KARTA]"),
    (r"ghp_[A-Za-z0-9]{20,}", "[GH_TOKEN]"),
    (r"sk-or-v1-[A-Za-z0-9-]{20,}", "[OR_KEY]"),
    (r"sk-[A-Za-z0-9]{20,}", "[KEY]"),
    (r"AIza[A-Za-z0-9_-]{20,}", "[GOOGLE_KEY]"),
    (r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b", "[BOT]"),
    (r"(?i)(secret[_-]?key|api[_-]?key)\s*[:=]\s*\S+", "[SECRET]"),
]

def maxfiy_tozala(matn):
    if not matn: return ""
    toza = matn
    for p, a in XAVFLI:
        toza = re.sub(p, a, toza)
    return toza

# ============================================================
# 🤖 AI PROMPTLAR
# ============================================================
INTENT_PROMPT = """Sen intent parser. Foydalanuvchi xabaridan niyatini JSON formatda aniqlaysan.

MUMKIN NIYATLAR:
1. check — yangi emaillarni tekshirish
2. list — email ro'yxati
3. read — email o'qish (id kerak)
4. stat — statistika
5. auto_on — avtomatik yoqish
6. auto_off — avtomatik o'chirish
7. help — yordam
8. chat — oddiy suhbat

QOIDALAR:
- "tekshir", "yangi", "email bormi", "check" → check
- "royxat", "list", "ko'rsat", "qaysi" → list
- "o'qi", "read", "N-email" → read (id bilan)
- "stat", "statistika", "ahvol" → stat
- "avtomatik yoq", "auto on" → auto_on
- "avtomatik ochir", "auto off" → auto_off
- "yordam", "help" → help
- Boshqa → chat

FAQAT JSON qaytar.

MISOLLAR:
User: "Yangi email bormi?"
→ {"intent": "check"}

User: "Emaillarni ko'rsat"
→ {"intent": "list"}

User: "Statistikam qanday?"
→ {"intent": "stat"}

User: "5-emailni o'qi"
→ {"intent": "read", "id": 5}

User: "Salom"
→ {"intent": "chat", "javob": "Salom! Men Blip Mail Bot."}
"""

SYSTEM_PROMPT = (
    "Sen BLIP MAIL BOT yordamchisisan. "
    "Har doim O'ZBEK TILIDA (lotin) javob ber. Qisqa yoz."
)

# ============================================================
# LOG
# ============================================================
def log(matn):
    try:
        if BOT_TOKEN: matn = matn.replace(BOT_TOKEN, "[TOKEN]")
        if OPENROUTER_KEY: matn = matn.replace(OPENROUTER_KEY, "[KEY]")
        if GMAIL_PASS: matn = matn.replace(GMAIL_PASS, "[GMAIL_PASS]")
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
    if not GMAIL_USER or "sizning" in GMAIL_USER: xato.append("GMAIL_USER")
    if not GMAIL_PASS or "16_xonali" in GMAIL_PASS: xato.append("GMAIL_PASS")
    if not MAXFIY_PAROL or len(MAXFIY_PAROL) < 6: xato.append("MAXFIY_PAROL")
    if xato:
        print("\n❌ To'ldirilmagan:")
        for x in xato: print(f"   • {x}")
        sys.exit(1)
    print("  ✅ Tokenlar va parol to'ldirilgan")

# ============================================================
# 🔐 SESSIYA (XOTIRA + FAYL)
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
# BAZA
# ============================================================
def db_init():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msg_id TEXT UNIQUE, kimdan TEXT, mavzu TEXT, matn TEXT,
        sana TEXT, tarjima TEXT, hisobot TEXT, yaratilgan TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY, auto_check INTEGER DEFAULT 1,
        oxirgi_tekshiruv TEXT)""")
    c.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
    conn.commit(); conn.close()

def email_saqlash(em, tarjima="", hisobot=""):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    try:
        c.execute("""INSERT INTO emails
            (msg_id, kimdan, mavzu, matn, sana, tarjima, hisobot, yaratilgan)
            VALUES (?,?,?,?,?,?,?,?)""",
            (em["msg_id"], em["kimdan"], em["mavzu"], em["matn"],
             em["sana"], tarjima, hisobot, str(datetime.date.today())))
        conn.commit(); eid = c.lastrowid; conn.close(); return eid
    except sqlite3.IntegrityError:
        conn.close(); return None

def email_royxat(limit=20):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT id, kimdan, mavzu, sana FROM emails
        ORDER BY id DESC LIMIT ?""", (limit,))
    r = c.fetchall(); conn.close(); return r

def email_ol_id(eid):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""SELECT id, kimdan, mavzu, matn, sana, tarjima, hisobot
        FROM emails WHERE id=?""", (eid,))
    r = c.fetchone(); conn.close(); return r

def email_stat():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM emails"); jami = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM emails WHERE tarjima != ''")
    tarjima = c.fetchone()[0]; conn.close()
    return jami, tarjima

def auto_holat():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT auto_check FROM settings WHERE id=1")
    r = c.fetchone(); conn.close()
    return r[0] if r else 1

def auto_ozgartir(v):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE settings SET auto_check=? WHERE id=1", (v,))
    conn.commit(); conn.close()

# ============================================================
# 🤖 AI FUNKSIYALAR
# ============================================================
def ai_request(model, system, user_text, timeout=45):
    if not OPENROUTER_KEY: return None
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_text}],
        "temperature": 0.7, "max_tokens": 800,
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            AI_URL, data=data,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://blip.local",
                "X-Title": "Blip Mail Bot",
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

def til_aniqla(matn):
    if not matn: return "uz"
    kirill = len(re.findall(r"[а-яА-ЯёЁ]", matn))
    ingliz = len(re.findall(r"[a-zA-Z]", matn))
    if kirill > ingliz and kirill > 10: return "ru"
    elif ingliz > kirill and ingliz > 10: return "en"
    return "uz"

def ai_tarjima(matn, til="ru"):
    if not matn: return ""
    matn_x = maxfiy_tozala(matn)
    til_nomi = "rus" if til == "ru" else "ingliz"
    prompt = (f"Quyidagi {til_nomi} tilidagi matnni O'ZBEK TILIGA "
              f"(lotin) tarjima qil:\n\n{matn_x[:1500]}")
    return ai_ask("Sen tarjimonsan. O'zbek tilida.", prompt) or ""

def ai_hisobot(mavzu, kimdan, matn, til):
    matn_x = maxfiy_tozala(matn); mavzu_x = maxfiy_tozala(mavzu)
    prompt = (f"Email haqida qisqa hisobot (3-4 gap):\n\n"
              f"Kimdan: {kimdan}\nMavzu: {mavzu_x}\n"
              f"Til: {til}\nMatn: {matn_x[:1200]}\n\n"
              f"Kim yozgan, nima haqida, muhimmi, javob kerakmi?")
    return ai_ask("Sen email tahlilchisisan. O'zbek tilida.", prompt) or ""

# ============================================================
# 📧 GMAIL
# ============================================================
def gmail_ulan():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USER, GMAIL_PASS)
        return mail
    except Exception as e:
        log(f"❌ Gmail: {e}"); return None

def email_matn_ol(msg):
    matn = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    matn = part.get_payload(decode=True).decode("utf-8", "ignore")
                    break
                except: pass
            elif ctype == "text/html" and not matn:
                try:
                    html = part.get_payload(decode=True).decode("utf-8", "ignore")
                    matn = re.sub(r"<[^>]+>", "", html)
                except: pass
    else:
        try:
            matn = msg.get_payload(decode=True).decode("utf-8", "ignore")
        except: pass
    return matn.strip()[:3000]

def email_ol(limit=10, faqat_yangi=True):
    mail = gmail_ulan()
    if not mail: return []
    try:
        mail.select("INBOX")
        typ, data = mail.search(None, "UNSEEN" if faqat_yangi else "ALL")
        ids = data[0].split()
        ids = ids[-limit:] if len(ids) > limit else ids
        natijalar = []
        for eid in reversed(ids):
            try:
                typ, msg_data = mail.fetch(eid, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                msg_id = msg.get("Message-ID", str(eid))
                sana = msg.get("Date", "")
                kimdan = msg.get("From", "")
                kimdan = decode_header(kimdan)[0][0]
                if isinstance(kimdan, bytes):
                    kimdan = kimdan.decode("utf-8", "ignore")
                mavzu = msg.get("Subject", "")
                decoded = decode_header(mavzu)
                mavzu = ""
                for part, enc in decoded:
                    if isinstance(part, bytes):
                        mavzu += part.decode(enc or "utf-8", "ignore")
                    else:
                        mavzu += part
                matn = email_matn_ol(msg)
                natijalar.append({
                    "msg_id": msg_id, "kimdan": kimdan,
                    "mavzu": mavzu or "(mavzusiz)",
                    "matn": matn, "sana": sana})
            except Exception as e:
                log(f"⚠️ {eid}: {e}")
        mail.logout(); return natijalar
    except Exception as e:
        log(f"❌: {e}"); return []

# ============================================================
# 📥 YANGI EMAILLAR
# ============================================================
def yangi_emaillarni_tekshir(admin_id):
    log("📧 Gmail tekshirilmoqda...")
    emaillar = email_ol(10, faqat_yangi=True)
    if not emaillar:
        log("📭 Yangi email yo'q"); return 0
    yangi = 0
    for em in emaillar:
        yangi += 1
        til = til_aniqla(em["matn"] + " " + em["mavzu"])
        log(f"📩 {em['mavzu'][:40]} | {til}")
        tarjima = ""
        if til in ("ru", "en"):
            log(f"  🌐 Tarjima...")
            tarjima = ai_tarjima(em["matn"], til)
        log(f"  🤖 Hisobot...")
        hisobot = ai_hisobot(em["mavzu"], em["kimdan"], em["matn"], til)
        eid = email_saqlash(em, tarjima, hisobot)
        if not eid: continue
        til_emoji = {"ru": "🇷🇺", "en": "🇬🇧", "uz": "🇺🇿"}
        matn_x = maxfiy_tozala(em["matn"])
        xabar = (f"📧 YANGI EMAIL\n\n"
                 f"👤 Kimdan: {em['kimdan']}\n"
                 f"📌 Mavzu: {em['mavzu']}\n"
                 f"📅 {em['sana'][:25]}\n"
                 f"🌐 {til_emoji.get(til,'❓')} {til.upper()}\n\n"
                 f"📝 {matn_x[:400]}\n")
        if tarjima: xabar += f"\n🌐 TARJIMA:\n{tarjima[:800]}\n"
        if hisobot: xabar += f"\n🤖 HISOBOT:\n{hisobot}"
        if admin_id: tg_send(admin_id, xabar)
    log(f"✅ {yangi} ta yangi email")
    return yangi
# ============================================================
# 💬 BUYRUQLAR
# ============================================================
def cmd_start(chat_id):
    tg_send(chat_id,
        "📧 BLIP MAIL BOT v6.0\n\n"
        "BUYRUQLAR:\n"
        "/check /list /read /stat\n"
        "/auto /help /logout\n\n"
        "💡 Yoki shunchaki yozing:\n"
        "• \"yangi email bormi?\"\n"
        "• \"emaillarni ko'rsat\"\n"
        "• \"statistikam qanday?\"\n"
        "• \"5-emailni o'qi\"")

def cmd_help(chat_id):
    tg_send(chat_id,
        "📖 YORDAM\n\n"
        "BUYRUQLAR:\n"
        "/check — Yangi emaillar\n"
        "/list — Ro'yxat\n"
        "/read id — O'qish\n"
        "/stat — Statistika\n"
        "/auto on/off — Avtomatik\n"
        "/logout — Chiqish\n\n"
        "ODDIY MATN:\n"
        "• \"yangi email bormi?\"\n"
        "• \"emaillarni ko'rsat\"\n"
        "• \"statistika\"\n"
        "• \"5-emailni o'qi\"\n\n"
        "🛡 Maxfiy: parol, karta, ID → yashiriladi")

def cmd_check(chat_id):
    tg_send(chat_id, "⏳ Tekshirilmoqda...\n🌐 Tarjima + 🤖 Hisobot")
    n = yangi_emaillarni_tekshir(chat_id)
    if n == 0:
        tg_send(chat_id, "📭 Yangi email yo'q")

def cmd_list(chat_id):
    r = email_royxat(15)
    if not r:
        tg_send(chat_id, "📭 Email yo'q"); return
    t = "📋 EMAILLAR:\n\n"
    for x in r:
        t += f"📝 {x[0]}. {x[2][:40]}\n   👤 {x[1][:25]}\n\n"
    tg_send(chat_id, t)

def cmd_read(chat_id, args):
    if not args:
        tg_send(chat_id, "❌ /read id"); return
    try: eid = int(args[0])
    except: tg_send(chat_id, "❌ Raqam"); return
    em = email_ol_id(eid)
    if not em:
        tg_send(chat_id, "❌ Topilmadi"); return
    matn_x = maxfiy_tozala(em[3])
    t = (f"📧 {em[2]}\n\n👤 {em[1]}\n📅 {em[4]}\n\n"
         f"📝 {matn_x[:2000]}")
    if em[5]: t += f"\n\n🌐 TARJIMA:\n{em[5][:1500]}"
    if em[6]: t += f"\n\n🤖 HISOBOT:\n{em[6]}"
    if len(t) > 4000:
        for i in range(0, len(t), 4000):
            tg_send(chat_id, t[i:i+4000])
    else:
        tg_send(chat_id, t)

def cmd_stat(chat_id):
    j, t = email_stat(); avto = auto_holat()
    tg_send(chat_id,
        f"📊 STATISTIKA\n\n"
        f"📧 Jami: {j}\n"
        f"🌐 Tarjima: {t}\n"
        f"⚙️ Avtomatik: {'✅ Yoniq' if avto else '❌ Ochiq'}\n"
        f"🔐 Sessiya: ✅ Faol")

def cmd_auto(chat_id, args):
    if not args:
        avto = auto_holat()
        tg_send(chat_id,
            f"⚙️ Avtomatik: {'✅ Yoniq' if avto else '❌ Ochiq'}\n"
            f"/auto on | /auto off")
        return
    v = 1 if args[0].lower() in ("on", "yoq", "1") else 0
    auto_ozgartir(v)
    tg_send(chat_id, f"✅ Avtomatik: {'YONIQ' if v else 'OCHIQ'}")

# ============================================================
# 💬 XABARNI QAYTA ISHLASH
# ============================================================
def xabar_qayta_ishla(chat_id, text):
    if text.startswith("/"):
        parts = text.split()
        cmd = parts[0].lstrip("/").split("@")[0].lower()
        args = parts[1:]
        if cmd == "start": cmd_start(chat_id)
        elif cmd == "help": cmd_help(chat_id)
        elif cmd == "check": cmd_check(chat_id)
        elif cmd == "list": cmd_list(chat_id)
        elif cmd == "read": cmd_read(chat_id, args)
        elif cmd == "stat": cmd_stat(chat_id)
        elif cmd == "auto": cmd_auto(chat_id, args)
        else: tg_send(chat_id, "❓ Buyruq yo'q. /help bosing.")
        return

    tg_typing(chat_id)
    intent = intent_aniqla(text)
    if not intent:
        javob = ai_ask(SYSTEM_PROMPT, text)
        tg_send(chat_id, javob or "Tushunmadim. /help bosing.")
        return
    tur = intent.get("intent", "chat")
    if tur == "check": cmd_check(chat_id)
    elif tur == "list": cmd_list(chat_id)
    elif tur == "read":
        eid = intent.get("id", 0)
        cmd_read(chat_id, [str(eid)])
    elif tur == "stat": cmd_stat(chat_id)
    elif tur == "auto_on": cmd_auto(chat_id, ["on"])
    elif tur == "auto_off": cmd_auto(chat_id, ["off"])
    elif tur == "help": cmd_help(chat_id)
    elif tur == "chat":
        javob = intent.get("javob", "")
        if not javob: javob = ai_ask(SYSTEM_PROMPT, text)
        tg_send(chat_id, javob or "Tushunmadim")
    else:
        javob = ai_ask(SYSTEM_PROMPT, text)
        tg_send(chat_id, javob or "Tushunmadim")

# ============================================================
# 🔐 PAROL HANDLERLARI
# ============================================================
def start_salom(chat_id, ism):
    tg_send(chat_id,
        f"🔐 BLIP MAIL BOT v6.0\n\n"
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
            "Xush kelibsiz, Blip! 🚀\n\n"
            "📋 Buyruqlar:\n"
            "/check — Yangi emaillar\n"
            "/list — Ro'yxat\n"
            "/stat — Statistika\n"
            "/help — Yordam\n\n"
            "💡 Yoki shunchaki yozing:\n"
            "\"yangi email bormi?\"")
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
# 🔄 AUTO LOOP
# ============================================================
def auto_tekshir_loop(get_admin):
    while True:
        try:
            if auto_holat():
                aid = get_admin()
                if aid: yangi_emaillarni_tekshir(aid)
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"⚠️ Auto: {e}"); time.sleep(60)

# ============================================================
# 🔄 ASOSIY LOOP
# ============================================================
def main():
    log("🚀 BLIP MAIL BOT v6.0 ishga tushdi!")
    log(f"👤 Gmail: {GMAIL_USER[:5]}***")
    log(f"🔐 Parol: ✅")
    log(f"📁 {LOYIHA_PAPKA}")

    db_init()
    me = tg_request("getMe")
    if me and me.get("ok"):
        log(f"🤖 Bot: @{me['result'].get('username', '?')}")

    init = tg_get_updates(0, timeout=1)
    last_id = 0
    if init and init.get("ok"):
        ups = init.get("result", [])
        if ups: last_id = max(u.get("update_id", 0) for u in ups)

    admin_id = [0]
    def get_admin(): return admin_id[0]

    import threading
    t = threading.Thread(target=auto_tekshir_loop,
                         args=(get_admin,), daemon=True)
    t.start()

    log("🔄 Kuzatish boshlandi...\n")
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

                    if not admin_id[0]:
                        admin_id[0] = chat_id
                        log(f"✅ Admin ID: {admin_id[0]}")

                    try:
                        xabar_qayta_ishla(chat_id, text)
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
    print("  📧 BLIP MAIL BOT v6.0")
    print("  Parol + Buyruqsiz AI")
    print("=" * 55)
    print(f"  📁 {LOYIHA_PAPKA}")
    print(f"  👤 {GMAIL_USER[:5]}***")
    print(f"  🔐 Parol: ✅")
    print("=" * 55)
    tokenlarni_tekshir()
    try:
        main()
    except KeyboardInterrupt:
        log("\n👋 Xayr!")
    except Exception as e:
        log(f"❌ {e}")