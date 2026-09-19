# ============================================================
#  BLIP AI HUB v1.0 – 1/3
#  Fayl: blip_ai_hub.py
# ============================================================
import os, requests, datetime, json
from flask import Flask, request, session, redirect, url_for, render_template_string

# Terminalni jim qilish
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
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "blip-ai-hub-921324")

TIZIM_PAROLI = "921324"
PORT = 8080
OPENROUTER_API_KEY = os.getenv("YOUR_OPENROUTER_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Modellar ro'yxati
MODELLAR = {
    "deepseek/deepseek-chat": "DeepSeek Chat",
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
    if not OPENROUTER_API_KEY:
        return "OpenRouter API kaliti topilmadi. .env fayliga OPENROUTER_API_KEY qo'shing."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8080",
        "X-Title": "Blip AI Hub"
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
        return f"So'rovda xatolik: {e}"

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
.tab{display:flex;gap:5px;margin:15px 0;flex-wrap:wrap}
.tab a{flex:1;text-align:center;padding:8px;background:#111;border:1px solid #39ff14;border-radius:5px;color:#39ff14}
"""

LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Blip AI Hub</title><style>""" + STYLE + """ body{display:flex;align-items:center;justify-content:center}</style></head><body>
<div class=karta><h1>Blip AI Hub</h1><div class=sub>Kirish</div>
<form method=POST>
<input name=username placeholder='Username' required autofocus>
<input type=password name=parol placeholder='Parol' required>
<button>KIRISH</button>
</form>
{% if xato %}<p class=xato>{{ xato }}</p>{% endif %}
</div></body></html>"""

ASOSIY_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Blip AI Hub</title><style>""" + STYLE + """</style></head><body>
<div class=karta>
<h1>Blip AI Hub</h1>
<div class=sub>Xush kelibsiz, {{ username }}!</div>
<div class=tab>
<a href='/chat'>💬 Chat</a>
<a href='/kod'>📝 Kod</a>
<a href='/tarjima'>🌐 Tarjima</a>
<a href='/xulosa'>📄 Xulosa</a>
<a href='/ertak'>🧚 Ertak</a>
<a href='/pdfsavol'>📚 PDF Savol</a>
</div>
<div style=text-align:center;color:#666;margin-top:20px>Menyudan bo'lim tanlang</div>
<a href='/logout' style=color:#ff4444;text-align:center;display:block;margin-top:20px'>Chiqish</a>
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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
    # ============================================================
#  BLIP AI HUB v1.0 – 2/3
#  Bo'limlar: Chat, Kod Generator, Tarjimon
# ============================================================

CHAT_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Chat</title><style>""" + STYLE + """</style></head><body>
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
<a href='/asosiy'>← Bosh sahifa</a>
</div></body></html>"""

KOD_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Kod Generator</title><style>""" + STYLE + """</style></head><body>
<div class=karta>
<h1>📝 Kod Generator</h1>
<div class=sub>Dasturlash tilini va vazifani yozing</div>
<form method=POST action='/kod'>
<select name=model>
{% for slug, nom in modellar.items() %}<option value='{{ slug }}' {% if tanlangan_model==slug %}selected{% endif %}>{{ nom }}</option>{% endfor %}
</select>
<textarea name=talab rows=4 placeholder='Masalan: Python da Flask server kodi...' required>{{ old_talab }}</textarea>
<button>Kod yozish</button>
</form>
{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}
<a href='/asosiy'>← Bosh sahifa</a>
</div></body></html>"""

TARJIMA_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Tarjimon</title><style>""" + STYLE + """</style></head><body>
<div class=karta>
<h1>🌐 Tarjimon</h1>
<div class=sub>Matnni boshqa tilga o'giring</div>
<form method=POST action='/tarjima'>
<select name=til>
<option value='ingliz'>Ingliz</option>
<option value='rus'>Rus</option>
<option value='ozbek'>O'zbek</option>
</select>
<textarea name=matn rows=4 placeholder='Matn kiriting...' required>{{ old_matn }}</textarea>
<button>Tarjima qilish</button>
</form>
{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}
<a href='/asosiy'>← Bosh sahifa</a>
</div></body></html>"""

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
            system = "Siz tajribali dasturchisiz. Foydalanuvchi talabiga mos to'liq, ishlaydigan kod yozing. Izohlar kerak bo'lsa qo'shing. Faqat kodni qaytaring."
            javob = openrouter_sorash(talab, model=model, system=system)
    return render_template_string(KOD_HTML, modellar=MODELLAR, javob=javob, old_talab=old_talab, tanlangan_model=tanlangan_model)

@app.route("/tarjima", methods=["GET","POST"])
@login_talab
def tarjima():
    javob = None
    old_matn = ""
    til = "ingliz"
    if request.method == "POST":
        til = request.form.get("til","ingliz")
        matn = request.form.get("matn","").strip()
        old_matn = matn
        if matn:
            system = f"Siz professional tarjimonsiz. Foydalanuvchi matnini {til} tiliga tarjima qiling."
            javob = openrouter_sorash(matn, model="deepseek/deepseek-chat", system=system)
    return render_template_string(TARJIMA_HTML, til=til, javob=javob, old_matn=old_matn)
# ============================================================
#  BLIP AI HUB v1.0 – 3/3
#  Bo'limlar: Xulosa, Ertak, PDF Savol va ishga tushirish
# ============================================================

XULOSA_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Xulosa</title><style>""" + STYLE + """</style></head><body>
<div class=karta>
<h1>📄 Matn Xulosalovchi</h1>
<div class=sub>Uzoq matnni qisqartirib beradi</div>
<form method=POST action='/xulosa'>
<textarea name=matn rows=6 placeholder='Matn kiriting...' required>{{ old_matn }}</textarea>
<button>Xulosa olish</button>
</form>
{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}
<a href='/asosiy'>← Bosh sahifa</a>
</div></body></html>"""

ERTAK_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Ertak Yozuvchi</title><style>""" + STYLE + """</style></head><body>
<div class=karta>
<h1>🧚 Ertak Yozuvchi</h1>
<div class=sub>Mavzu kiriting, ertak yozib beradi</div>
<form method=POST action='/ertak'>
<select name=model>
{% for slug, nom in modellar.items() %}<option value='{{ slug }}' {% if tanlangan_model==slug %}selected{% endif %}>{{ nom }}</option>{% endfor %}
</select>
<textarea name=mavzu rows=3 placeholder='Masalan: Kiber-shahar va robot bola...' required>{{ old_mavzu }}</textarea>
<button>Ertak yozish</button>
</form>
{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}
<a href='/asosiy'>← Bosh sahifa</a>
</div></body></html>"""

PDFSAVOL_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>PDF Savol-Javob</title><style>""" + STYLE + """</style></head><body>
<div class=karta>
<h1>📚 PDF Savol-Javob</h1>
<div class=sub>PDF yuklang, savol bering</div>
<form method=POST action='/pdfsavol' enctype=multipart/form-data>
<input type=file name=pdf accept='.pdf' required>
<textarea name=savol rows=3 placeholder='PDF haqida savolingiz...' required></textarea>
<button>Yuborish</button>
</form>
{% if xato %}<p class=xato>{{ xato }}</p>{% endif %}
{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}
<a href='/asosiy'>← Bosh sahifa</a>
</div></body></html>"""

@app.route("/xulosa", methods=["GET","POST"])
@login_talab
def xulosa():
    javob = None
    old_matn = ""
    if request.method == "POST":
        matn = request.form.get("matn","").strip()
        old_matn = matn
        if matn:
            system = "Siz matnni qisqartirib, asosiy fikrlarni ajratib beradigan yordamchisiz. Matn xulosasini 3-5 qatorda yozing."
            javob = openrouter_sorash(matn, model="deepseek/deepseek-chat", system=system)
    return render_template_string(XULOSA_HTML, javob=javob, old_matn=old_matn)

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

@app.route("/pdfsavol", methods=["GET","POST"])
@login_talab
def pdfsavol():
    javob = None
    xato = None
    if request.method == "POST":
        fayl = request.files.get("pdf")
        savol = request.form.get("savol","").strip()
        if not fayl or not savol:
            xato = "PDF fayl va savol kiriting."
        else:
            try:
                from PyPDF2 import PdfReader
                import io
                pdf_content = fayl.read()
                pdf_reader = PdfReader(io.BytesIO(pdf_content))
                matn = ""
                for sahifa in pdf_reader.pages:
                    matn += sahifa.extract_text() or ""
                matn = matn.strip()
                if len(matn) < 10:
                    xato = "PDF dan matn olish imkoni bo'lmadi."
                else:
                    prompt = f"PDF matni:\n{matn[:5000]}\n\nSavol: {savol}"
                    javob = openrouter_sorash(prompt, model="deepseek/deepseek-chat", system="Siz hujjat bo'yicha savollarga javob berasiz. Faqat hujjatdan foydalaning.")
            except Exception as e:
                xato = f"Xatolik: {e}"
    return render_template_string(PDFSAVOL_HTML, javob=javob, xato=xato)

if __name__ == "__main__":
    print("Blip AI Hub ishga tushdi (port {})".format(PORT))
    app.run(host="0.0.0.0", port=PORT, debug=False)