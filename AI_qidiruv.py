# ============================================================
#  BLIP AI SEARCH ASSISTANT v1.0 – 1/3
#  Fayl: blip_ai_search.py
# ============================================================
import os, datetime, logging
from flask import Flask, request, session, redirect, url_for, render_template_string

# Terminalni jim qilish
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# g4f va qidiruv kutubxonalarini tekshirish
try:
    from g4f.client import Client
    G4F_OK = True
except:
    G4F_OK = False

try:
    from googlesearch import search
    SEARCH_OK = True
except:
    SEARCH_OK = False

try:
    import requests
    REQUESTS_OK = True
except:
    REQUESTS_OK = False

app = Flask(__name__)
app.config["SECRET_KEY"] = "blip-ai-search-921324"

TIZIM_PAROLI = "921324"
PORT = 8080

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

def ai_chat(savol):
    """g4f orqali AI javob"""
    if not G4F_OK:
        return "g4f kutubxonasi topilmadi. Iltimos, pip install g4f"
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # yoki boshqa model
            messages=[{"role": "user", "content": savol}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI xatolik: {e}"

def internet_qidiruv(savol, natijalar_soni=5):
    """Google qidiruv va natijalarni matn qilib qaytarish"""
    if not SEARCH_OK:
        return None, "googlesearch kutubxonasi topilmadi. pip install googlesearch-python"
    try:
        natijalar = []
        for url in search(savol, num_results=natijalar_soni):
            natijalar.append(url)
        if not natijalar:
            return None, "Hech narsa topilmadi."
        return natijalar, None
    except Exception as e:
        return None, f"Qidiruv xatolik: {e}"

def sayt_matni(url):
    """Saytdan matn olish"""
    if not REQUESTS_OK:
        return ""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            # Oddiy matn ajratish (beautifulsoup ishlatmasdan)
            import re
            matn = re.sub(r'<[^>]+>', ' ', r.text)
            matn = re.sub(r'\s+', ' ', matn).strip()
            return matn[:500]
    except:
        pass
    return ""

def qidiruv_va_xulosa(savol):
    """Internet qidiruv natijalarini yig'ib, AI bilan xulosa qilish"""
    natijalar, xato = internet_qidiruv(savol)
    if xato:
        return None, xato

    matnlar = []
    for url in natijalar:
        matn = sayt_matni(url)
        if matn:
            matnlar.append(f"URL: {url}\n{matn}\n")

    if not matnlar:
        return natijalar, "Saytlardan matn olish imkoni bo'lmadi."

    birlashgan = "\n".join(matnlar)
    prompt = f"Quyidagi internet natijalariga asoslanib, savolga qisqacha javob bering.\n\nSavol: {savol}\n\nNatijalar:\n{birlashgan[:3000]}"
    xulosa = ai_chat(prompt)
    return natijalar, xulosa

# HTML uslubi
STYLE = """*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,sans-serif}
body{background:#0a0a0a;color:#fff;min-height:100vh;padding:10px}
.karta{background:#111;border:1px solid #39ff14;border-radius:10px;padding:20px;max-width:700px;margin:0 auto}
h1{color:#39ff14;text-align:center;margin-bottom:10px}
.sub{color:#00c8ff;text-align:center;font-size:12px;margin-bottom:20px}
input,textarea,select,button{width:100%;padding:12px;margin:8px 0;background:#000;border:1px solid #39ff14;color:#fff;border-radius:5px;font-size:14px}
button{background:#39ff14;color:#000;font-weight:bold;cursor:pointer}
a{color:#00c8ff;text-decoration:none}
.xato{color:#ff4444;text-align:center}
.natija{background:#1a1a1a;padding:15px;border-radius:8px;margin:10px 0;white-space:pre-wrap}
.tab{display:flex;gap:5px;margin:15px 0;flex-wrap:wrap}
.tab a{flex:1;text-align:center;padding:8px;background:#111;border:1px solid #39ff14;border-radius:5px;color:#39ff14}
"""

LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Blip AI Search</title><style>""" + STYLE + """ body{display:flex;align-items:center;justify-content:center}</style></head><body>
<div class=karta><h1>Blip AI Search</h1><div class=sub>Kirish</div>
<form method=POST>
<input name=username placeholder='Username' required autofocus>
<input type=password name=parol placeholder='Parol' required>
<button>KIRISH</button>
</form>
{% if xato %}<p class=xato>{{ xato }}</p>{% endif %}
</div></body></html>"""
ASOSIY_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Blip AI Search</title><style>""" + STYLE + """</style></head><body>
<div class=karta>
<h1>Blip AI Search</h1>
<div class=sub>Xush kelibsiz, {{ username }}!</div>
<div class=tab>
<a href='/chat'>🤖 AI Chat</a>
<a href='/qidiruv'>🔎 Internet Qidiruv</a>
</div>
<div style=text-align:center;color:#666;margin-top:20px>Menyudan bo'lim tanlang</div>
<a href='/logout' style=color:#ff4444;text-align:center;display:block;margin-top:20px'>Chiqish</a>
</div></body></html>"""

CHAT_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>AI Chat</title><style>""" + STYLE + """</style></head><body>
<div class=karta>
<h1>🤖 AI Chat</h1>
<div class=sub>Bepul g4f orqali suhbat</div>
<form method=POST action='/chat'>
<textarea name=savol rows=4 placeholder='Savolingiz...' required>{{ old_savol }}</textarea>
<button>Yuborish</button>
</form>
{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}
<a href='/asosiy'>← Bosh sahifa</a>
</div></body></html>"""

QIDIRUV_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Internet Qidiruv</title><style>""" + STYLE + """</style></head><body>
<div class=karta>
<h1>🔎 Internet Qidiruv + AI Xulosa</h1>
<div class=sub>Savol yozing, u internetdan topib xulosa qiladi</div>
<form method=POST action='/qidiruv'>
<textarea name=savol rows=4 placeholder='Masalan: Python nima?' required>{{ old_savol }}</textarea>
<button>Qidirish</button>
</form>
{% if xato %}<p class=xato>{{ xato }}</p>{% endif %}
{% if natijalar %}
<h3 style=color:#39ff14>Topilgan manbalar:</h3>
<ul style=color:#00c8ff>
{% for url in natijalar %}<li><a href='{{ url }}' target=_blank style=color:#00c8ff>{{ url }}</a></li>{% endfor %}
</ul>
{% endif %}
{% if xulosa %}<div class=natija>{{ xulosa }}</div>{% endif %}
<a href='/asosiy'>← Bosh sahifa</a>
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
    if request.method == "POST":
        savol = request.form.get("savol","").strip()
        old_savol = savol
        if savol:
            javob = ai_chat(savol)
    return render_template_string(CHAT_HTML, javob=javob, old_savol=old_savol)

@app.route("/qidiruv", methods=["GET","POST"])
@login_talab
def qidiruv():
    old_savol = ""
    natijalar = None
    xulosa = None
    xato = None
    if request.method == "POST":
        savol = request.form.get("savol","").strip()
        old_savol = savol
        if savol:
            natijalar, xulosa_or_xato = qidiruv_va_xulosa(savol)
            if isinstance(xulosa_or_xato, str) and xulosa_or_xato.startswith(("Qidiruv xatolik", "Saytlardan matn", "googlesearch")):
                xato = xulosa_or_xato
                natijalar = None
                xulosa = None
            else:
                xulosa = xulosa_or_xato
    return render_template_string(QIDIRUV_HTML, old_savol=old_savol, natijalar=natijalar, xulosa=xulosa, xato=xato)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    print("Blip AI Search ishga tushdi (port {})".format(PORT))
    app.run(host="0.0.0.0", port=PORT, debug=False)