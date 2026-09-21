# ============================================================
# 📧 BLIP MAIL BOT v5.0 — Tarjima + AI hisobot
# Fayl: blip_mail_bot.py
# 2 qism • Har biri 460 qatordan kam
# ============================================================
import os, json, sqlite3, datetime, urllib.parse
import urllib.request, imaplib, email, re
from email.header import decode_header

# ⚠️ SHU YERNI TO'LDIRING!
BOT_TOKEN = "YOUR_TOKEN"
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY"
ADMIN_TG_ID = 0

GMAIL_USER = "YOUR_GMAIL"
GMAIL_PASS = "YOUR_PASS"

DB = "/storage/emulated/0/Ai/mail_bot.db"
IMAP_SERVER = "imap.gmail.com"
AI_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODELS = [
    "nex-agi/nex-n2.5-pro:free",
    "nex-agi/nex-n2.5-mini:free",
    "qwen/qwen3.8-27b:free",
]

# ============================================================
# 🛡 MAXFIY HIMOYA — faqat ID va PAROL yashiriladi
# ============================================================
XAVFLI = [
    (r"(?i)(password|parol|pwd)\s*[:=]\s*\S+", "[PAROL YASHIRIN]"),
    (r"(?i)(kod|code|pin|otp)\s*[:=]\s*\d{4,8}", "[KOD YASHIRIN]"),
    (r"(?i)(passport|pasport|id)\s*[:=]?\s*[A-Z0-9]{8,15}", "[ID YASHIRIN]"),
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[KARTA YASHIRIN]"),
    (r"ghp_[A-Za-z0-9]{20,}", "[GITHUB_TOKEN]"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "[GITHUB_PAT]"),
    (r"sk-or-v1-[A-Za-z0-9-]{20,}", "[OPENROUTER_KEY]"),
    (r"sk-[A-Za-z0-9]{20,}", "[OPENAI_KEY]"),
    (r"AIza[A-Za-z0-9_-]{20,}", "[GOOGLE_KEY]"),
    (r"AKIA[A-Z0-9]{16}", "[AWS_KEY]"),
    (r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b", "[BOT_TOKEN]"),
    (r"(?i)(secret[_-]?key|api[_-]?key)\s*[:=]\s*\S+", "[SECRET]"),
]

def maxfiy_tozala(matn):
    if not matn:
        return ""
    toza = matn
    for pattern, almashtir in XAVFLI:
        toza = re.sub(pattern, almashtir, toza)
    return toza

def til_aniqla(matn):
    """Matn qaysi tilda ekanligini aniqlaydi."""
    if not matn:
        return "uz"
    # Rus tili (kirill)
    kirill = len(re.findall(r"[а-яА-ЯёЁ]", matn))
    # Ingliz tili
    ingliz = len(re.findall(r"[a-zA-Z]", matn))
    # O'zbek lotin belgilari
    oz = len(re.findall(r"[oʻgʻ']", matn.lower()))
    
    if kirill > ingliz and kirill > 10:
        return "ru"
    elif ingliz > kirill and ingliz > 10:
        return "en"
    else:
        return "uz"

# ============================================================
# 🤖 AI FUNKSIYALARI
# ============================================================
SYSTEM_PROMPT = (
    "Sen BLIP MAIL BOT yordamchisisan. "
    "Har doim O'ZBEK TILIDA (lotin alifbosida) javob ber. "
    "Qisqa va aniq yoz."
)

def ai_sorov(savol):
    if not OPENROUTER_KEY or OPENROUTER_KEY.startswith("BU_"):
        return None
    for model in AI_MODELS:
        data = {"model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": savol}],
                "temperature": 0.5, "max_tokens": 700}
        try:
            req = urllib.request.Request(AI_URL,
                data=json.dumps(data).encode(),
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}",
                         "Content-Type": "application/json"},
                method="POST")
            with urllib.request.urlopen(req, timeout=30) as r:
                j = json.loads(r.read().decode())
            return j["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"⚠️ AI {model}: {e}")
            continue
    return None

def ai_tarjima(matn, til="ru"):
    """Matnni o'zbek tiliga tarjima qiladi."""
    if not matn or not matn.strip():
        return ""
    matn_x = maxfiy_tozala(matn)
    til_nomi = "rus" if til == "ru" else "ingliz"
    prompt = (
        f"Quyidagi {til_nomi} tilidagi matnni O'ZBEK TILIGA "
        f"(lotin alifbosida) tarjima qil. Faqat tarjimani yoz, "
        f"boshqa hech narsa qo'shma:\n\n{matn_x[:1500]}"
    )
    return ai_sorov(prompt) or ""

def ai_hisobot(mavzu, kimdan, matn, til):
    """Email haqida qisqa hisobot beradi."""
    matn_x = maxfiy_tozala(matn)
    mavzu_x = maxfiy_tozala(mavzu)
    prompt = (
        f"Email haqida qisqa hisobot ber (3-4 gap):\n\n"
        f"Kimdan: {kimdan}\n"
        f"Mavzu: {mavzu_x}\n"
        f"Til: {til}\n"
        f"Matn: {matn_x[:1200]}\n\n"
        f"Hisobotda yoz:\n"
        f"1. Kim yozgan (ism)\n"
        f"2. Nima haqida\n"
        f"3. Muhimmi?\n"
        f"4. Javob kerakmi?"
    )
    return ai_sorov(prompt) or ""

# ============================================================
# BAZA
# ============================================================
def db_init():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msg_id TEXT UNIQUE, kimdan TEXT, mavzu TEXT, matn TEXT,
        sana TEXT, til TEXT, tarjima TEXT, hisobot TEXT,
        yaratilgan TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY, auto_check INTEGER DEFAULT 1,
        oxirgi_tekshiruv TEXT)""")
    c.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
    conn.commit()
    conn.close()

# ============================================================
# 📧 GMAIL
# ============================================================
def gmail_ulan():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USER, GMAIL_PASS)
        return mail
    except Exception as e:
        print(f"❌ Gmail: {e}")
        return None

def email_matn_ol(msg):
    matn = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    matn = part.get_payload(decode=True).decode("utf-8", "ignore")
                    break
                except:
                    pass
            elif ctype == "text/html" and not matn:
                try:
                    html = part.get_payload(decode=True).decode("utf-8", "ignore")
                    matn = re.sub(r"<[^>]+>", "", html)
                except:
                    pass
    else:
        try:
            matn = msg.get_payload(decode=True).decode("utf-8", "ignore")
        except:
            pass
    return matn.strip()[:3000]

def email_ol(limit=10, faqat_yangi=True):
    mail = gmail_ulan()
    if not mail:
        return []
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
                    "matn": matn, "sana": sana
                })
            except Exception as e:
                print(f"⚠️ {eid}: {e}")
        mail.logout()
        return natijalar
    except Exception as e:
        print(f"❌: {e}")
        return []

def email_saqlash(em, til, tarjima, hisobot):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO emails
            (msg_id, kimdan, mavzu, matn, sana, til, tarjima,
             hisobot, yaratilgan)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (em["msg_id"], em["kimdan"], em["mavzu"], em["matn"],
             em["sana"], til, tarjima, hisobot,
             str(datetime.date.today())))
        conn.commit()
        eid = c.lastrowid
        conn.close()
        return eid
    except sqlite3.IntegrityError:
        conn.close()
        return None

def email_royxat(limit=20):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT id, kimdan, mavzu, sana, til
        FROM emails ORDER BY id DESC LIMIT ?""", (limit,))
    r = c.fetchall()
    conn.close()
    return r

def email_ol_id(eid):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT id, kimdan, mavzu, matn, sana, til,
        tarjima, hisobot FROM emails WHERE id=?""", (eid,))
    r = c.fetchone()
    conn.close()
    return r

def email_stat():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM emails")
    jami = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM emails WHERE tarjima != ''")
    tarjima = c.fetchone()[0]
    conn.close()
    return jami, tarjima

# ============================================================
# 📱 TELEGRAM XABAR
# ============================================================
def tg_xabar(matn):
    if not ADMIN_TG_ID or not BOT_TOKEN or BOT_TOKEN.startswith("BU_"):
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": ADMIN_TG_ID, "text": matn
        }).encode()
        urllib.request.urlopen(
            urllib.request.Request(url, data=data, method="POST"), timeout=10)
    except Exception as e:
        print(f"⚠️ TG: {e}")

def yangi_emaillarni_tekshir():
    print("📧 Gmail tekshirilmoqda...")
    emaillar = email_ol(10, faqat_yangi=True)
    if not emaillar:
        print("📭 Yangi email yo'q")
        return 0
    yangi = 0
    for em in emaillar:
        yangi += 1
        # Til aniqlash
        til = til_aniqla(em["matn"] + " " + em["mavzu"])
        print(f"📩 {em['mavzu'][:40]} | Til: {til}")
        
        # AI tarjima (faqat ru yoki en)
        tarjima = ""
        if til in ("ru", "en"):
            print(f"  🌐 Tarjima qilinmoqda...")
            tarjima = ai_tarjima(em["matn"], til)
        
        # AI hisobot
        print(f"  🤖 Hisobot tayyorlanmoqda...")
        hisobot = ai_hisobot(em["mavzu"], em["kimdan"], em["matn"], til)
        
        # Bazaga saqlash
        eid = email_saqlash(em, til, tarjima, hisobot)
        if not eid:
            continue
        
        # Telegram xabar
        til_emoji = {"ru": "🇷🇺", "en": "🇬🇧", "uz": "🇺🇿"}
        matn_telegram = maxfiy_tozala(em["matn"])
        
        xabar = (
            f"📧 YANGI EMAIL\n\n"
            f"👤 Kimdan: {em['kimdan']}\n"
            f"📌 Mavzu: {em['mavzu']}\n"
            f"📅 {em['sana'][:25]}\n"
            f"🌐 Til: {til_emoji.get(til,'❓')} {til.upper()}\n\n"
            f"📝 Matn:\n{matn_telegram[:400]}\n"
        )
        if tarjima:
            xabar += f"\n\n🌐 TARJIMA:\n{tarjima[:800]}\n"
        if hisobot:
            xabar += f"\n\n🤖 HISOBOT:\n{hisobot}"
        tg_xabar(xabar)
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE settings SET oxirgi_tekshiruv=? WHERE id=1",
              (datetime.datetime.now().isoformat(),))
    conn.commit()
    conn.close()
    print(f"✅ {yangi} ta yangi email")
    return yangi

def auto_tekshir():
    import time
    while True:
        try:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("SELECT auto_check FROM settings WHERE id=1")
            yoqilgan = c.fetchone()[0]
            conn.close()
            if yoqilgan:
                yangi_emaillarni_tekshir()
            time.sleep(300)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️ Auto: {e}")
            time.sleep(60)
# ============================================================
# TELEGRAM BOT
# ============================================================
def tg_mode():
    try:
        import telebot
        from telebot import types
        import threading
    except ImportError:
        print("❌ pip install pyTelegramBotAPI")
        return
    if BOT_TOKEN.startswith("BU_"):
        print("❌ BOT_TOKEN!")
        return
    bot = telebot.TeleBot(BOT_TOKEN)

    t = threading.Thread(target=auto_tekshir, daemon=True)
    t.start()

    @bot.message_handler(commands=["start"])
    def s(m):
        j, tt = email_stat()
        bot.send_message(m.chat.id,
            f"📧 Blip Mail Bot v5.0\n\n"
            f"📊 Jami: {j} | 🌐 Tarjima: {tt}\n\n"
            f"📋 BUYRUQLAR:\n"
            f"/check — Yangi emaillar\n"
            f"/list — Email ro'yxati\n"
            f"/read <id> — To'liq o'qish\n"
            f"/hisobot <id> — AI hisobot\n"
            f"/ai savol — AI savol\n"
            f"/stat — Statistika\n"
            f"/auto on/off — Avtomatik\n"
            f"/help — Yordam\n\n"
            f"🌐 Rus/Ingliz → O'zbek tarjima\n"
            f"🤖 AI qisqa hisobot\n"
            f"🔒 ID va PAROL yashiriladi!")

    @bot.message_handler(commands=["help"])
    def h(m):
        bot.send_message(m.chat.id,
            "📖 Yordam\n\n"
            "/check — yangi emaillar\n"
            "/list — ro'yxat\n"
            "/read 1 — o'qish (tarjima bilan)\n"
            "/hisobot 1 — AI hisobot\n"
            "/ai savol — AI savol\n"
            "/stat — statistika\n"
            "/auto on/off\n\n"
            "🌐 TIL ANIQLASH:\n"
            "🇷🇺 Rus → O'zbek tarjima\n"
            "🇬🇧 Ingliz → O'zbek tarjima\n"
            "🇺🇿 O'zbek → tarjima kerak emas\n\n"
            "🔒 ID/parol → [YASHIRIN]")

    @bot.message_handler(commands=["check"])
    def chk(m):
        bot.send_message(m.chat.id, "⏳ Tekshirilmoqda...\n"
                                    "🌐 Tarjima + 🤖 Hisobot tayyorlanadi")
        n = yangi_emaillarni_tekshir()
        bot.send_message(m.chat.id, f"✅ {n} ta yangi email")

    @bot.message_handler(commands=["list"])
    def lst(m):
        r = email_royxat(15)
        if not r:
            bot.send_message(m.chat.id, "📭 Email yo'q")
            return
        t = "📋 Emails:\n\n"
        til_emoji = {"ru": "🇷🇺", "en": "🇬🇧", "uz": "🇺🇿"}
        for x in r:
            til = til_emoji.get(x[4], "❓")
            t += f"{til} {x[0]}. {x[2][:40]}\n   👤 {x[1][:25]}\n\n"
        bot.send_message(m.chat.id, t)

    @bot.message_handler(commands=["read"])
    def rd(m):
        p = m.text.split()
        if len(p) < 2:
            bot.send_message(m.chat.id, "❌ /read id")
            return
        try:
            eid = int(p[1])
        except:
            bot.send_message(m.chat.id, "❌ Raqam")
            return
        em = email_ol_id(eid)
        if not em:
            bot.send_message(m.chat.id, "❌ Topilmadi")
            return
        til_emoji = {"ru": "🇷🇺", "en": "🇬🇧", "uz": "🇺🇿"}
        matn_x = maxfiy_tozala(em[3])
        
        t = (f"📧 {em[2]}\n\n"
             f"👤 {em[1]}\n"
             f"📅 {em[4]}\n"
             f"🌐 {til_emoji.get(em[5],'❓')} {em[5].upper()}\n\n"
             f"📝 Asl matn:\n{matn_x[:1500]}\n")
        
        if em[6]:
            t += f"\n\n🌐 TARJIMA:\n{em[6][:1500]}\n"
        if em[7]:
            t += f"\n\n🤖 HISOBOT:\n{em[7]}"
        
        # Uzun bo'lsa bo'lib yuborish
        if len(t) > 4000:
            for i in range(0, len(t), 4000):
                bot.send_message(m.chat.id, t[i:i+4000])
        else:
            bot.send_message(m.chat.id, t)

    @bot.message_handler(commands=["hisobot"])
    def hs(m):
        p = m.text.split()
        if len(p) < 2:
            bot.send_message(m.chat.id, "❌ /hisobot id")
            return
        try:
            eid = int(p[1])
        except:
            bot.send_message(m.chat.id, "❌ Raqam")
            return
        em = email_ol_id(eid)
        if not em:
            bot.send_message(m.chat.id, "❌ Topilmadi")
            return
        if em[7]:
            bot.send_message(m.chat.id, f"🤖 AI hisobot:\n\n{em[7]}")
        else:
            bot.send_message(m.chat.id, "⏳ Yangi hisobot tayyorlanadi...")
            h = ai_hisobot(em[2], em[1], em[3], em[5])
            if h:
                # Yangilash
                conn = sqlite3.connect(DB)
                c = conn.cursor()
                c.execute("UPDATE emails SET hisobot=? WHERE id=?", (h, eid))
                conn.commit()
                conn.close()
                bot.send_message(m.chat.id, f"🤖 AI hisobot:\n\n{h}")
            else:
                bot.send_message(m.chat.id, "❌ AI javob bermadi")

    @bot.message_handler(commands=["ai"])
    def ai_cmd(m):
        savol = m.text.replace("/ai", "").strip()
        if not savol:
            bot.send_message(m.chat.id, "❌ /ai savol...")
            return
        bot.send_message(m.chat.id, "⏳ AI...")
        javob = ai_sorov(savol)
        bot.send_message(m.chat.id, f"🤖 {javob or 'Javob yoq'}")

    @bot.message_handler(commands=["stat"])
    def st(m):
        j, t = email_stat()
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT auto_check FROM settings WHERE id=1")
        avto = c.fetchone()[0]
        conn.close()
        bot.send_message(m.chat.id,
            f"📊 Statistika\n\n"
            f"📧 Jami: {j}\n"
            f"🌐 Tarjima: {t}\n"
            f"⚙️ Avtomatik: {'✅ Yoniq' if avto else '❌ Ochiq'}\n"
            f"👤 Gmail: {GMAIL_USER[:3]}***@***")

    @bot.message_handler(commands=["auto"])
    def au(m):
        p = m.text.split()
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        if len(p) < 2:
            c.execute("SELECT auto_check FROM settings WHERE id=1")
            hozir = c.fetchone()[0]
            conn.close()
            bot.send_message(m.chat.id,
                f"⚙️ Avtomatik: {'✅ Yoniq' if hozir else '❌ Ochiq'}\n"
                f"/auto on — yoqish\n/auto off — o'chirish")
            return
        v = 1 if p[1].lower() in ("on", "yoq", "1") else 0
        c.execute("UPDATE settings SET auto_check=? WHERE id=1", (v,))
        conn.commit()
        conn.close()
        bot.send_message(m.chat.id,
            f"✅ Avtomatik: {'YONIQ' if v else 'OCHIQ'}")

    @bot.message_handler(content_types=["text"],
                         func=lambda m: not m.text.startswith("/"))
    def ai_auto(m):
        bot.send_chat_action(m.chat.id, "typing")
        javob = ai_sorov(m.text)
        if javob:
            if len(javob) > 4000:
                for i in range(0, len(javob), 4000):
                    bot.send_message(m.chat.id, javob[i:i+4000])
            else:
                bot.send_message(m.chat.id, f"🤖 {javob}")

    print("\n🤖 Blip Mail Bot v5.0 ishga tushdi!")
    print(f"📧 Gmail: {GMAIL_USER}")
    print(f"🌐 Tarjima: ✅ | 🤖 Hisobot: ✅")
    print(f"🔒 ID va PAROL yashiriladi: ✅")
    print(f"⛔ Ctrl+C\n")
    try:
        bot.infinity_polling(timeout=30)
    except KeyboardInterrupt:
        print("\n👋 To'xtatildi")

# ============================================================
# ASOSIY
# ============================================================
if __name__ == "__main__":
    db_init()
    os.system("clear" if os.name != "nt" else "cls")
    print("\n📧 BLIP MAIL BOT v5.0")
    print(f"👤 Gmail: {GMAIL_USER}")
    print(f"🌐 Tarjima: ✅ (Rus/Ingliz → O'zbek)")
    print(f"🤖 AI hisobot: ✅")
    print(f"🔒 ID va PAROL yashiriladi: ✅")
    j, t = email_stat()
    print(f"📧 {j} email | 🌐 {t} tarjima")
    input("\n▶️ Enter...")
    tg_mode()