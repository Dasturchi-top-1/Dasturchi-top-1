# ============================================================
#  BLIP AI STUDIO v1.0 – Ko‘p modelli AI markaz
#  Fayl: blip_ai_studio.py
# ============================================================
import os, sqlite3, datetime, requests, base64, json
from flask import Flask, request, session, redirect, url_for, render_template_string, send_file
from werkzeug.utils import secure_filename

# Terminal jim bo‘lishi uchun
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# .env yuklash
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "blip-ai-studio-921324")

TIZIM_PAROLI = "921324"
PORT = 8080
RASMLAR_PAPKA = "/storage/emulated/0/Pictures/BlipAI/"
os.makedirs(RASMLAR_PAPKA, exist_ok=True)

# OpenRouter sozlamalari
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Modellar ro‘yxati (OpenRouter slug)
MODELLAR = {
    "deepseek": "DeepSeek Chat",
    "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet",
    "google/gemini-flash-1.5": "Gemini Flash 1.5",
    "openai/gpt-4o-mini": "GPT-4o Mini",
    "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
}

def login_talab(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def hozirgi_vaqt():
    return str(datetime.datetime.now())[:19]

def openrouter_sorash(prompt, model="deepseek/deepseek-chat", system=None):
    """OpenRouter orqali matn olish"""
    if not OPENROUTER_API_KEY:
        return "OpenRouter API kaliti topilmadi. .env fayliga OPENROUTER_API_KEY qo'shing."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8080",
        "X-Title": "Blip AI Studio"
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            return f"Xatolik: {r.status_code} - {r.text[:200]}"
    except Exception as e:
        return f"So‘rovda xatolik: {e}"

def rasm_yaratish(tavsif):
    """Pollinations orqali rasm yaratish va saqlash"""
    url = f"https://image.pollinations.ai/prompt/{tavsif.replace(' ', '%20')}?width=512&height=512&nologo=true"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            fayl_nomi = f"ai_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            fayl_yol = os.path.join(RASMLAR_PAPKA, fayl_nomi)
            with open(fayl_yol, "wb") as f:
                f.write(r.content)
            return fayl_nomi, None
        else:
            return None, f"Rasm yaratishda xatolik: {r.status_code}"
    except Exception as e:
        return None, f"Rasm yaratishda xatolik: {e}"

# HTML uslubi
STYLE = """*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,sans-serif}
body{background:#0a0a0a;color:#fff;min-height:100vh;padding:10px}
.karta{background:#111;border:1px solid #39ff14;border-radius:10px;padding:20px;max-width:600px;margin:0 auto}
h1{color:#39ff14;text-align:center;margin-bottom:10px}
.sub{color:#00c8ff;text-align:center;font-size:12px;margin-bottom:20px}
input,select,textarea,button{width:100%;padding:10px;margin:8px 0;background:#000;border:1px solid #39ff14;color:#fff;border-radius:5px}
button{background:#39ff14;color:#000;font-weight:bold;cursor:pointer}
a{color:#00c8ff;text-decoration:none}
.xato{color:red;text-align:center}
.natija{background:#1a1a1a;padding:15px;border-radius:8px;margin:10px 0;white-space:pre-wrap}
.tab{display:flex;gap:5px;margin:15px 0}
.tab a{flex:1;text-align:center;padding:8px;background:#111;border:1px solid #39ff14;border-radius:5px;color:#39ff14}
img{max-width:100%;border-radius:8px;margin:10px 0;border:2px solid #39ff14}"""

LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Blip AI Studio</title><style>"""+STYLE+""" body{display:flex;align-items:center;justify-content:center}</style></head><body>
<div class=karta><h1>Blip AI Studio</h1><div class=sub>Kirish</div>
<form method=POST>
<input name=username placeholder='Username' required autofocus>
<input type=password name=parol placeholder='Parol' required>
<button>KIRISH</button>
</form>
{% if xato %}<p class=xato>{{ xato }}</p>{% endif %}
</div></body></html>"""
# ============================================================
#  BLIP AI STUDIO v1.0 – 2/3
#  Asosiy panel HTML, marshrutlar
# ============================================================

ASOSIY_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Blip AI Studio</title><style>"""+STYLE+"""</style></head><body>
<div class=karta>
<h1>Blip AI Studio</h1>
<div class=sub>Xush kelibsiz, {{ username }}!</div>

<div class=tab>
<a href='/chat'>💬 Chat</a>
<a href='/kod'>📝 Kod</a>
<a href='/ertak'>🧚 Ertak</a>
<a href='/rasm'>🎨 Rasm</a>
</div>

<div style=text-align:center;color:#666;margin-top:20px>
Menyudan bo'lim tanlang
</div>
<a href='/logout' style=color:#ff4444;text-align:center;display:block;margin-top:20px'>Chiqish</a>
</div></body></html>"""

CHAT_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Chat</title><style>"""+STYLE+"""</style></head><body>
<div class=karta>
<h1>💬 AI Chat</h1>
<div class=sub>Model tanlang va savol bering</div>
<form method=POST action='/chat'>
<select name=model>
{% for slug, nom in modellar.items() %}<option value='{{ slug }}' {% if tanlangan_model==slug %}selected{% endif %}>{{ nom }}</option>{% endfor %}
</select>
<textarea name=savol rows=4 placeholder='Savolingiz...' required>{{ old_savol }}</textarea>
<button>Yuborish</button>
</form>
{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}
<a href='/'>← Bosh sahifa</a>
</div></body></html>"""

KOD_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Kod yozish</title><style>"""+STYLE+"""</style></head><body>
<div class=karta>
<h1>📝 Kod Yozish</h1>
<div class=sub>Dasturlash tilini va vazifani yozing</div>
<form method=POST action='/kod'>
<select name=model>
{% for slug, nom in modellar.items() %}<option value='{{ slug }}' {% if tanlangan_model==slug %}selected{% endif %}>{{ nom }}</option>{% endfor %}
</select>
<textarea name=talab rows=4 placeholder='Masalan: Python da Flask server kodi...' required>{{ old_talab }}</textarea>
<button>Kod yozish</button>
</form>
{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}
<a href='/'>← Bosh sahifa</a>
</div></body></html>"""

ERTAK_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Ertak to'qish</title><style>"""+STYLE+"""</style></head><body>
<div class=karta>
<h1>🧚 Ertak To'qish</h1>
<div class=sub>Mavzu kiriting</div>
<form method=POST action='/ertak'>
<select name=model>
{% for slug, nom in modellar.items() %}<option value='{{ slug }}' {% if tanlangan_model==slug %}selected{% endif %}>{{ nom }}</option>{% endfor %}
</select>
<textarea name=mavzu rows=3 placeholder='Masalan: Kiber-shahar va robot bola...' required>{{ old_mavzu }}</textarea>
<button>Ertak yozish</button>
</form>
{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}
<a href='/'>← Bosh sahifa</a>
</div></body></html>"""

RASM_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Rasm yaratish</title><style>"""+STYLE+"""</style></head><body>
<div class=karta>
<h1>🎨 Rasm Yaratish</h1>
<div class=sub>Tavsif yozing, bepul Pollinations yaratadi</div>
<form method=POST action='/rasm'>
<textarea name=tavsif rows=4 placeholder='Masalan: Kiber-shahar, neon chiroqlar...' required>{{ old_tavsif }}</textarea>
<button>Rasm chizish</button>
</form>
{% if rasm_nomi %}<img src='/rasm_fayl/{{ rasm_nomi }}' alt='AI rasm'>{% endif %}
{% if xato %}<p class=xato>{{ xato }}</p>{% endif %}
<a href='/'>← Bosh sahifa</a>
</div></body></html>"""

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        parol = request.form.get("parol","").strip()
        if parol == TIZIM_PAROLI and username:
            session["user_id"] = username
            session["username"] = username
            return redirect(url_for("asosiy"))
        return render_template_string(LOGIN_HTML, xato="Noto'g'ri parol yoki ism!")
    return render_template_string(LOGIN_HTML, xato=None)

@app.route("/asosiy")
@login_talab
def asosiy():
    return render_template_string(ASOSIY_HTML, username=session["username"])

@app.route("/chat", methods=["GET","POST"])
@login_talab
def chat():
    javob = None
    old_savol = ""
    tanlangan_model = "deepseek/deepseek-chat"
    if request.method == "POST":
        model = request.form.get("model","deepseek/deepseek-chat")
        savol = request.form.get("savol","").strip()
        old_savol = savol
        tanlangan_model = model
        if savol:
            javob = openrouter_sorash(savol, model=model)
    return render_template_string(CHAT_HTML, modellar=MODELLAR, javob=javob, old_savol=old_savol, tanlangan_model=tanlangan_model)

@app.route("/kod", methods=["GET","POST"])
@login_talab
def kod():
    javob = None
    old_talab = ""
    tanlangan_model = "deepseek/deepseek-chat"
    if request.method == "POST":
        model = request.form.get("model","deepseek/deepseek-chat")
        talab = request.form.get("talab","").strip()
        old_talab = talab
        tanlangan_model = model
        if talab:
            system = "Siz tajribali dasturchisiz. Foydalanuvchi talabiga mos to'liq, ishlaydigan kod yozing. Izohlar kerak bo'lsa qo'shing."
            javob = openrouter_sorash(talab, model=model, system=system)
    return render_template_string(KOD_HTML, modellar=MODELLAR, javob=javob, old_talab=old_talab, tanlangan_model=tanlangan_model)

@app.route("/ertak", methods=["GET","POST"])
@login_talab
def ertak():
    javob = None
    old_mavzu = ""
    tanlangan_model = "meta-llama/llama-3.3-70b-instruct"
    if request.method == "POST":
        model = request.form.get("model","meta-llama/llama-3.3-70b-instruct")
        mavzu = request.form.get("mavzu","").strip()
        old_mavzu = mavzu
        tanlangan_model = model
        if mavzu:
            system = "Siz ijodkor yozuvchisiz. Foydalanuvchi mavzusiga qiziqarli, bolalarga mos ertak yozing."
            javob = openrouter_sorash(mavzu, model=model, system=system)
    return render_template_string(ERTAK_HTML, modellar=MODELLAR, javob=javob, old_mavzu=old_mavzu, tanlangan_model=tanlangan_model)

@app.route("/rasm", methods=["GET","POST"])
@login_talab
def rasm():
    rasm_nomi = None
    xato = None
    old_tavsif = ""
    if request.method == "POST":
        tavsif = request.form.get("tavsif","").strip()
        old_tavsif = tavsif
        if tavsif:
            rasm_nomi, xato = rasm_yaratish(tavsif)
    return render_template_string(RASM_HTML, rasm_nomi=rasm_nomi, xato=xato, old_tavsif=old_tavsif)

@app.route("/rasm_fayl/<fayl_nomi>")
@login_talab
def rasm_fayl(fayl_nomi):
    fayl_yol = os.path.join(RASMLAR_PAPKA, fayl_nomi)
    if os.path.exists(fayl_yol):
        return send_file(fayl_yol, mimetype="image/jpeg")
    return "Rasm topilmadi", 404

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
# ============================================================
#  BLIP AI STUDIO v1.0 – 3/3
#  Ishga tushirish
# ============================================================

if __name__ == "__main__":
    print("Blip AI Studio ishga tushdi (port {})".format(PORT))
    app.run(host="0.0.0.0", port=PORT, debug=False)