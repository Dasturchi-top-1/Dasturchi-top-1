# ============================================================
# 📚 BLIP STUDY BOT
# Fayl: blip_study_bot.py
# Telegram Bot (raw HTTP) + OpenRouter AI
# English → Gemini | Python → DeepSeek
# ============================================================
import os
import json
import time
import datetime
import urllib.request
import urllib.parse
import urllib.error

# ============================================================
# ⚠️ SOZLAMALAR — config.py yoki environment orqali
# ============================================================
try:
    from config import BOT_TOKEN, OPENROUTER_KEY
except ImportError:
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
    OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "YOUR_OPENROUTER_KEY")

DATA_FILE = "/storage/emulated/0/Ai/Ustox_x/blip_study_users.json"
LOG_FILE = "/storage/emulated/0/Ai/Ustoz_x/blip_study.log"
POLL_TIMEOUT = 30

# ============================================================
# 🤖 AI MODELLAR (fallback bilan)
# ============================================================
ENGLISH_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "google/gemini-flash-1.5",
    "nex-agi/nex-n2.5-mini:free",
]
PYTHON_MODELS = [
    "deepseek/deepseek-chat-v3.1:free",
    "deepseek/deepseek-chat:free",
    "nex-agi/nex-n2.5-pro:free",
]
FALLBACK_MODELS = [
    "nex-agi/nex-n2.5-mini:free",
    "qwen/qwen3.8-27b:free",
]
AI_URL = "https://openrouter.ai/api/v1/chat/completions"

# ============================================================
# 📝 SYSTEM PROMPTLAR
# ============================================================
ENGLISH_PROMPT = (
    "Sen BLIP STUDY BOT ning ingliz tili o'qituvchisisan. "
    "Isming: Blip English Teacher. "
    "Vazifang: o'quvchiga ingliz tilini o'rgatish. "
    "QOIDALAR:\n"
    "1. Har doim O'ZBEK TILIDA tushuntir, inglizcha misollar ber.\n"
    "2. Grammatika, vocabulary, tarjima, gap tuzishga yordam ber.\n"
    "3. Xato qilsa, sababini tushuntir va to'g'ri variantni ko'rsat.\n"
    "4. Qisqa, aniq va tushunarli yoz (max 5-6 gap).\n"
    "5. Misollar keltir.\n"
    "6. O'quvchini rag'batlantir."
)

PYTHON_PROMPT = (
    "Sen BLIP STUDY BOT ning Python o'qituvchisisan. "
    "Isming: Blip Python Teacher. "
    "Vazifang: o'quvchiga Python dasturlashni o'rgatish. "
    "QOIDALAR:\n"
    "1. Har doim O'ZBEK TILIDA tushuntir.\n"
    "2. Kod bloklarini ```python ... ``` shaklida yoz.\n"
    "3. Boshlang'ichdan bosqichma-bosqich o'rgat.\n"
    "4. Xatolarni tahlil qil va yechim ko'rsat.\n"
    "5. O'quvchini o'zi kod yozishga unda.\n"
    "6. Topshiriq va hint ber.\n"
    "7. Xavfsiz dasturlashni o'rgat.\n"
    "8. Qisqa va aniq yoz (max 8-10 gap)."
)

# ============================================================
# 📁 JSON STORAGE
# ============================================================
def load_data():
    """JSON faylni yuklaydi. Buzilgan bo'lsa, xavfsiz tiklaydi."""
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "last_update_id": 0}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Noto'g'ri format")
        data.setdefault("users", {})
        data.setdefault("last_update_id", 0)
        return data
    except Exception as e:
        log(f"⚠️ JSON buzilgan: {e}")
        try:
            backup = DATA_FILE + ".bak"
            os.rename(DATA_FILE, backup)
            log(f"💾 Zaxira: {backup}")
        except Exception:
            pass
        return {"users": {}, "last_update_id": 0}


def save_data(data):
    """JSON faylni atomik saqlaydi."""
    try:
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DATA_FILE)
        return True
    except Exception as e:
        log(f"⚠️ Saqlash xatosi: {e}")
        return False


def get_user(user_id):
    """Foydalanuvchini oladi yoki yaratadi."""
    data = load_data()
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "id": user_id,
            "name": "",
            "mode": "english",
            "english_count": 0,
            "python_count": 0,
            "quiz_count": 0,
            "auto": True,
            "last_english": "",
            "last_python": "",
            "quiz_active": False,
            "quiz_question": "",
            "quiz_answer": "",
            "joined": str(datetime.date.today()),
        }
        save_data(data)
    return data["users"][uid]


def update_user(user_id, **kwargs):
    """Foydalanuvchi ma'lumotlarini yangilaydi."""
    data = load_data()
    uid = str(user_id)
    if uid not in data["users"]:
        get_user(user_id)
        data = load_data()
    for k, v in kwargs.items():
        data["users"][uid][k] = v
    save_data(data)


def all_users():
    """Barcha foydalanuvchilar (dict)."""
    return load_data().get("users", {})


def get_last_update_id():
    """Oxirgi ko'rilgan update ID."""
    return load_data().get("last_update_id", 0)


def set_last_update_id(uid):
    """Oxirgi update ID ni saqlaydi."""
    data = load_data()
    data["last_update_id"] = uid
    save_data(data)


# ============================================================
# 📝 LOG (maxfiy ma'lumotsiz)
# ============================================================
def log(matn):
    """Log yozadi — token/keylarni tozalab."""
    try:
        if BOT_TOKEN:
            matn = matn.replace(BOT_TOKEN, "[TOKEN]")
        if OPENROUTER_KEY:
            matn = matn.replace(OPENROUTER_KEY, "[KEY]")
        vaqt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{vaqt}] {matn}\n")
    except Exception:
        pass
    print(matn)
# ============================================================
# 🌐 HTTP HELPERS — Telegram API (raw)
# ============================================================
def tg_request(method, params=None, timeout=35):
    """Telegram API ga so'rov yuboradi."""
    if not BOT_TOKEN:
        log("❌ BOT_TOKEN yo'q")
        return None
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        if params:
            data = urllib.parse.urlencode(params).encode("utf-8")
            req = urllib.request.Request(url, data=data, method="POST")
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        log(f"⚠️ TG HTTP {e.code}: {method}")
        return None
    except urllib.error.URLError as e:
        log(f"⚠️ TG URL xato: {e.reason}")
        return None
    except Exception as e:
        log(f"⚠️ TG xato: {e}")
        return None


def tg_send(chat_id, text, reply_to=None):
    """Xabar yuboradi. Uzun bo'lsa bo'lib yuboradi."""
    if not text:
        return False
    # Telegram 4096 belgi limiti
    if len(text) <= 4000:
        p = {"chat_id": chat_id, "text": text}
        if reply_to:
            p["reply_to_message_id"] = reply_to
        r = tg_request("sendMessage", p)
        return bool(r and r.get("ok"))
    # Bo'lib yuborish
    ok = True
    for i in range(0, len(text), 4000):
        p = {"chat_id": chat_id, "text": text[i:i+4000]}
        r = tg_request("sendMessage", p)
        if not (r and r.get("ok")):
            ok = False
        time.sleep(0.5)
    return ok


def tg_get_updates(offset, timeout=POLL_TIMEOUT):
    """Yangilanishlarni oladi (long polling)."""
    p = {
        "timeout": timeout,
        "offset": offset,
        "allowed_updates": json.dumps(["message"]),
    }
    return tg_request("getUpdates", p, timeout=timeout + 10)


def tg_set_commands():
    """Bot buyruqlarini o'rnatadi."""
    cmds = [
        {"command": "start", "description": "Boshlash"},
        {"command": "english", "description": "Ingliz tili rejimi"},
        {"command": "python", "description": "Python rejimi"},
        {"command": "auto", "description": "Avtomatik dars yoqish/o'chirish"},
        {"command": "quiz", "description": "Test savoli"},
        {"command": "progress", "description": "Statistika"},
    ]
    p = {"commands": json.dumps(cmds)}
    return tg_request("setMyCommands", p)


# ============================================================
# 🤖 OPENROUTER — AI so'rov
# ============================================================
def ai_request(model, system_prompt, user_text, timeout=40):
    """OpenRouter API ga so'rov yuboradi."""
    if not OPENROUTER_KEY:
        return None
    if not user_text or not user_text.strip():
        return None
    # Maxfiy himoya
    user_text = _sanitize(user_text)
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://blip.local",
        "X-Title": "Blip Study Bot",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(AI_URL, data=data,
                                     headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            result = json.loads(r.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        log(f"⚠️ AI HTTP {e.code} ({model.split('/')[-1][:20]})")
        return None
    except urllib.error.URLError as e:
        log(f"⚠️ AI URL xato: {e.reason}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        log(f"⚠️ AI javob formati: {e}")
        return None
    except Exception as e:
        log(f"⚠️ AI xato: {e}")
        return None


def ai_ask(models, system_prompt, user_text):
    """Bir nechta modelni sinab ko'radi (fallback)."""
    for model in models:
        natija = ai_request(model, system_prompt, user_text)
        if natija:
            return natija
        time.sleep(0.5)
    # Fallback modellar
    for model in FALLBACK_MODELS:
        natija = ai_request(model, system_prompt, user_text)
        if natija:
            return natija
        time.sleep(0.5)
    return None


def ask_english(text):
    """English o'qituvchi."""
    return ai_ask(ENGLISH_MODELS, ENGLISH_PROMPT, text)


def ask_python(text):
    """Python o'qituvchi."""
    return ai_ask(PYTHON_MODELS, PYTHON_PROMPT, text)


# ============================================================
# 🛡 MAXFIY HIMOYA
# ============================================================
import re

XAVFLI = [
    (r"ghp_[A-Za-z0-9]{20,}", "[TOKEN]"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "[TOKEN]"),
    (r"sk-or-v1-[A-Za-z0-9-]{20,}", "[KEY]"),
    (r"sk-[A-Za-z0-9]{20,}", "[KEY]"),
    (r"AIza[A-Za-z0-9_-]{20,}", "[KEY]"),
    (r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b", "[BOT]"),
    (r"(?i)(password|parol|pwd)\s*[:=]\s*\S+", "PAROL: [YASHIRIN]"),
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[KARTA]"),
    (r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL]"),
]


def _sanitize(matn):
    """Maxfiy ma'lumotlarni AI ga yuborishdan oldin yashiradi."""
    if not matn:
        return ""
    for p, r in XAVFLI:
        matn = re.sub(p, r, matn)
    return matn
# ============================================================
# 🧠 MODE ANIQLASH — oddiy matn qaysi o'qituvchiga?
# ============================================================
PYTHON_KALIT = [
    "python", "питон", "пайтон", "код", "kod", "code",
    "while", "for", "if ", "else", "def ", "class ",
    "list", "dict", "tuple", "set", "loop", "sikl",
    "function", "funksiya", "variable", "o'zgaruvchi",
    "import", "print", "input", "return", "xato", "error",
    "dastur", "programma", "программа", "скрипт", "script",
    "django", "flask", "pandas", "numpy", "tkinter",
    "aiogram", "телеграм бот", "telegram bot",
]

ENGLISH_KALIT = [
    "english", "ingliz", "англий", "grammar", "grammatika",
    "vocabulary", "tarjima", "translate", "translation",
    "book", "apple", "word", "so'z", "слово",
    "what is", "what's", "how to say", "to'g'ri",
    "correct", "i am", "you are", "he is", "she is",
    "past", "present", "future", "tense", "zamon",
    "noun", "verb", "adjective", "article", "preposition",
    "i am go", "i goes", "she go", "he go",
]


def aniqla_mode(text):
    """Matndan rejimni aniqlaydi."""
    if not text:
        return None
    t = text.lower()
    py_score = sum(1 for k in PYTHON_KALIT if k in t)
    en_score = sum(1 for k in ENGLISH_KALIT if k in t)
    # Inglizcha so'zlar lotin harflarida bo'lsa
    if re.search(r"[a-zA-Z]{3,}", text):
        en_score += 1
    # Kod bloki
    if "```" in text or "def " in t or "print(" in t:
        py_score += 3
    if py_score > en_score:
        return "python"
    elif en_score > py_score:
        return "english"
    return None


# ============================================================
# 💬 XABAR HANDLERLARI
# ============================================================
def cmd_start(chat_id, user):
    name = user.get("name") or "do'stim"
    matn = (
        f"📚 Salom, {name}!\n\n"
        f"Men — Blip Study Bot. Sizga 2 ta yo'nalishda yordam beraman:\n\n"
        f"🇬🇧 Ingliz tili — Gemini o'qituvchi\n"
        f"🐍 Python — DeepSeek o'qituvchi\n\n"
        f"📋 BUYRUQLAR:\n"
        f"/english — Ingliz tili rejimi\n"
        f"/python — Python rejimi\n"
        f"/auto — Avtomatik dars (yoq/o'chir)\n"
        f"/quiz — Test savoli\n"
        f"/progress — Statistika\n\n"
        f"💡 Shunchaki savol yozing — men tushunib javob beraman!\n"
        f"Masalan: \"while nima?\" yoki \"What is a book?\""
    )
    tg_send(chat_id, matn)


def cmd_english(chat_id, user):
    update_user(user["id"], mode="english")
    tg_send(chat_id,
        "🇬🇧 English rejimi yoqildi!\n\n"
        "Endi savollaringiz ingliz tili o'qituvchisiga boradi.\n"
        "Misol: \"Past simple nima?\" yoki \"Correct: I am go school\"")


def cmd_python(chat_id, user):
    update_user(user["id"], mode="python")
    tg_send(chat_id,
        "🐍 Python rejimi yoqildi!\n\n"
        "Endi savollaringiz Python o'qituvchisiga boradi.\n"
        "Misol: \"while nima?\" yoki \"Kodimda xato bor\"")


def cmd_auto(chat_id, user):
    yangi = not user.get("auto", True)
    update_user(user["id"], auto=yangi)
    if yangi:
        tg_send(chat_id, "🔔 Avtomatik darslar YOQILDI!\n\n"
                         "Har kuni:\n"
                         "🌅 09:00 — English darsi\n"
                         "🌆 18:00 — Python darsi")
    else:
        tg_send(chat_id, "🔕 Avtomatik darslar O'CHIRILDI.")


def cmd_progress(chat_id, user):
    mode = user.get("mode", "english")
    mode_emoji = "🇬🇧" if mode == "english" else "🐍"
    matn = (
        f"📊 SIZNING STATISTIKANGIZ\n\n"
        f"👤 Ism: {user.get('name') or '—'}\n"
        f"🎯 Rejim: {mode_emoji} {mode.upper()}\n"
        f"🇬🇧 English darslar: {user.get('english_count', 0)}\n"
        f"🐍 Python darslar: {user.get('python_count', 0)}\n"
        f"🎯 Quizlar: {user.get('quiz_count', 0)}\n"
        f"🔔 Avtomatik: {'✅ Yoniq' if user.get('auto', True) else '❌ O\'chiq'}\n"
        f"📅 Boshlangan: {user.get('joined', '—')}"
    )
    tg_send(chat_id, matn)


def cmd_quiz(chat_id, user):
    """Quiz savolini yaratadi."""
    mode = user.get("mode", "english")
    if mode == "english":
        savol_prompt = (
            "Bitta ingliz tili test savolini tuz. "
            "Format: savol + 4 variant (A, B, C, D). "
            "Javobni savol ostida yozma! Faqat savolni yoz."
        )
        system = ENGLISH_PROMPT
        models = ENGLISH_MODELS
    else:
        savol_prompt = (
            "Bitta Python test savolini tuz. "
            "Format: savol + 4 variant (A, B, C, D). "
            "Javobni savol ostida yozma! Faqat savolni yoz."
        )
        system = PYTHON_PROMPT
        models = PYTHON_MODELS

    tg_send(chat_id, "⏳ Savol tayyorlanmoqda...")
    savol = ai_ask(models, system, savol_prompt)
    if not savol:
        tg_send(chat_id, "❌ Savol tayyorlanmadi. Keyinroq urinib ko'ring.")
        return
    # Javobni olish (alohida so'rov)
    javob = ai_ask(models, system,
                   f"Quyidagi savolga to'g'ri javobni faqat harf bilan yoz "
                   f"(A/B/C/D):\n\n{savol}")
    update_user(user["id"],
                quiz_active=True,
                quiz_question=savol,
                quiz_answer=(javob or "").strip().upper()[:1])
    tg_send(chat_id,
        f"🎯 QUIZ ({mode.upper()})\n\n{savol}\n\n"
        f"✍️ Javobingizni yozing (A/B/C/D)")
# ============================================================
# 🔔 AVTOMATIK DARSLAR
# ============================================================
def yubor_avto_darslar():
    """Belgilangan vaqtda avtomatik dars yuboradi."""
    hozir = datetime.datetime.now()
    bugun = str(hozir.date())
    soat = hozir.hour
    users = all_users()
    if not users:
        return
    for uid, user in users.items():
        try:
            if not user.get("auto", True):
                continue
            chat_id = user.get("id")
            if not chat_id:
                continue
            # 🌅 English — 9:00
            if soat == 9 and user.get("last_english") != bugun:
                savol = (
                    "Bugungi English darsingizni boshla. "
                    "5 ta yangi so'z + 1 ta grammatik qoida. "
                    "Qisqa va qiziqarli qilib yoz (10 gap)."
                )
                javob = ai_ask(ENGLISH_MODELS, ENGLISH_PROMPT, savol)
                if javob:
                    tg_send(chat_id, f"🌅 BUGUNGI ENGLISH DARSI\n\n{javob}")
                    update_user(chat_id,
                                last_english=bugun,
                                english_count=user.get("english_count", 0) + 1)
                    time.sleep(1)
            # 🌆 Python — 18:00
            if soat == 18 and user.get("last_python") != bugun:
                savol = (
                    "Bugungi Python darsingizni boshla. "
                    "1 ta tushuncha + 1 ta misol kod. "
                    "Qisqa va qiziqarli qilib yoz (10 gap)."
                )
                javob = ai_ask(PYTHON_MODELS, PYTHON_PROMPT, savol)
                if javob:
                    tg_send(chat_id, f"🌆 BUGUNGI PYTHON DARSI\n\n{javob}")
                    update_user(chat_id,
                                last_python=bugun,
                                python_count=user.get("python_count", 0) + 1)
                    time.sleep(1)
        except Exception as e:
            log(f"⚠️ Avto dars xato ({uid}): {e}")


# ============================================================
# 📩 XABARLARNI QAYTA ISHLASH
# ============================================================
def handle_command(chat_id, user, text):
    """Buyruqni bajaradi."""
    cmd = text.split()[0].lower().lstrip("/").split("@")[0]
    if cmd == "start":
        cmd_start(chat_id, user)
    elif cmd == "english":
        cmd_english(chat_id, user)
    elif cmd == "python":
        cmd_python(chat_id, user)
    elif cmd == "auto":
        cmd_auto(chat_id, user)
    elif cmd == "quiz":
        cmd_quiz(chat_id, user)
    elif cmd == "progress":
        cmd_progress(chat_id, user)
    else:
        tg_send(chat_id, "❓ Buyruq topilmadi. /start bosing.")


def handle_message(chat_id, user, text):
    """Oddiy matnli xabarni qayta ishlaydi."""
    if not text or not text.strip():
        return
    # Quiz javobi
    if user.get("quiz_active"):
        javob = text.strip().upper()[:1]
        togri = (user.get("quiz_answer") or "").upper()[:1]
        if javob in ("A", "B", "C", "D"):
            if javob == togri:
                update_user(user["id"], quiz_active=False,
                            quiz_count=user.get("quiz_count", 0) + 1)
                tg_send(chat_id,
                    f"✅ TO'G'RI! ({javob})\n\n"
                    f"🎉 Barakalla! Davom etamiz.")
            else:
                update_user(user["id"], quiz_active=False)
                tg_send(chat_id,
                    f"❌ Xato. To'g'ri javob: {togri}\n\n"
                    f"Keyingi safar yaxshiroq urinib ko'ring!")
            # Tushuntirish
            izoh_prompt = (
                f"Foydalanuvchi quizga {javob} deb javob berdi. "
                f"To'g'ri javob: {togri}. "
                f"Qisqa tushuntirish ber (2-3 gap): {user.get('quiz_question')}"
            )
            mode = user.get("mode", "english")
            izoh = ai_ask(ENGLISH_MODELS if mode == "english" else PYTHON_MODELS,
                          ENGLISH_PROMPT if mode == "english" else PYTHON_PROMPT,
                          izoh_prompt)
            if izoh:
                tg_send(chat_id, f"💡 {izoh}")
            return
        else:
            tg_send(chat_id, "❌ Iltimos, A/B/C/D dan birini yozing.")
            return

    # Rejimni aniqlash
    aniqlangan = aniqla_mode(text)
    user_mode = user.get("mode", "english")
    mode = aniqlangan or user_mode

    # 🐍 Python
    if mode == "python":
        tg_send(chat_id, "🐍 O'ylayapman...")
        javob = ask_python(text)
        if javob:
            tg_send(chat_id, javob)
        else:
            tg_send(chat_id, "❌ AI javob bermadi. Keyinroq urinib ko'ring.")
    # 🇬🇧 English
    else:
        tg_send(chat_id, "🇬🇧 O'ylayapman...")
        javob = ask_english(text)
        if javob:
            tg_send(chat_id, javob)
        else:
            tg_send(chat_id, "❌ AI javob bermadi. Keyinroq urinib ko'ring.")


def handle_update(update):
    """Bitta update ni qayta ishlaydi."""
    try:
        msg = update.get("message")
        if not msg:
            return
        chat_id = msg.get("chat", {}).get("id")
        if not chat_id:
            return
        text = msg.get("text", "")
        if not text:
            return
        # Foydalanuvchi
        user = get_user(chat_id)
        # Ism yangilash
        fname = msg.get("from", {}).get("first_name", "")
        if fname and user.get("name") != fname:
            update_user(chat_id, name=fname)
            user["name"] = fname
        # Buyruq
        if text.startswith("/"):
            handle_command(chat_id, user, text)
        else:
            handle_message(chat_id, user, text)
    except Exception as e:
        log(f"⚠️ Update xato: {e}")


# ============================================================
# 🔄 ASOSIY LOOP — LONG POLLING (TUZATILGAN)
# ============================================================
def main():
    """Asosiy loop — botni ishga tushiradi."""
    if not BOT_TOKEN:
        log("❌ BOT_TOKEN yo'q! config.py yoki environment kerak.")
        return
    if not OPENROUTER_KEY:
        log("⚠️ OPENROUTER_KEY yo'q — AI ishlamaydi!")

    log("🚀 Blip Study Bot ishga tushdi!")
    log(f"📁 Users: {DATA_FILE}")
    log(f"📝 Log: {LOG_FILE}")

    # Buyruqlarni o'rnatish
    tg_set_commands()

    # Bot ma'lumotlarini olish
    me = tg_request("getMe")
    if me and me.get("ok"):
        bot_name = me["result"].get("username", "?")
        log(f"🤖 Bot: @{bot_name}")
    else:
        log("⚠️ Bot ma'lumotlarini olishda xato!")

    last_id = get_last_update_id()

    # 🆕 Eski pending xabarlarni o'tkazib yuborish
    if last_id == 0:
        log("🧹 Eski xabarlar tozalanmoqda...")
        init_updates = tg_get_updates(0, timeout=1)
        if init_updates and init_updates.get("ok"):
            ups = init_updates.get("result", [])
            if ups:
                last_id = max(u.get("update_id", 0) for u in ups)
                set_last_update_id(last_id)
                log(f"✅ {len(ups)} ta eski xabar o'tkazib yuborildi")

    last_auto_check = 0
    xato_soni = 0

    log("🔄 Long polling boshlandi...\n")

    # Cheksiz loop
    while True:
        try:
            # 🎯 TUZATILGAN: last_id + 1
            updates = tg_get_updates(last_id + 1, timeout=POLL_TIMEOUT)

            if updates and updates.get("ok"):
                for up in updates.get("result", []):
                    handle_update(up)
                    uid = up.get("update_id", 0)
                    if uid > last_id:
                        last_id = uid

                # Yangi update bo'lsa, saqlash
                if updates.get("result"):
                    set_last_update_id(last_id)

                # Muvaffaqiyat — xatoni reset
                xato_soni = 0

            # 🔔 Avtomatik darslarni tekshirish (har 5 daqiqada)
            hozir = time.time()
            if hozir - last_auto_check > 300:
                try:
                    yubor_avto_darslar()
                except Exception as e:
                    log(f"⚠️ Avto: {e}")
                last_auto_check = hozir

        except KeyboardInterrupt:
            log("👋 To'xtatildi (Ctrl+C)")
            break
        except Exception as e:
            xato_soni += 1
            log(f"⚠️ Loop xato #{xato_soni}: {e}")
            # Ketma-ket xatolar — ko'proq kutish
            kutish = min(xato_soni * 2, 30)
            time.sleep(kutish)


# ============================================================
# 🏁 ENTRY POINT
# ============================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("👋 Xayr!")
    except Exception as e:
        log(f"❌ Kutilmagan xato: {e}")