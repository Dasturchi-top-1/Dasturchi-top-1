# ============================================================
#  BLIP SUPER APP v1.0 – Ko'p funksiyali platforma
#  Fayl: blip_super_app.py
#  1/5: Importlar, sozlamalar, baza, login, bosh menyu
# ============================================================
import os, sqlite3, datetime, requests, base64, io, json
from flask import Flask, request, session, redirect, url_for, render_template_string, send_file, jsonify
from werkzeug.utils import secure_filename

# Terminal jim bo'lishi uchun
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
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "blip-super-app-921324")

TIZIM_PAROLI = "921324"
PORT = 8080
BAZA_YOLI = "/storage/emulated/0/AI/blip_super_app.db"
YUKLASH_PAPKA = "/storage/emulated/0/Download/BlipCloud/"
os.makedirs(YUKLASH_PAPKA, exist_ok=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def baza_ulanish():
    os.makedirs(os.path.dirname(BAZA_YOLI), exist_ok=True)
    ulanish = sqlite3.connect(BAZA_YOLI)
    ulanish.row_factory = sqlite3.Row
    return ulanish

def baza_ishga_tushir():
    ulanish = baza_ulanish()
    ulanish.executescript("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            yaratilgan TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS xarajatlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            foydalanuvchi_id INTEGER NOT NULL,
            summa REAL NOT NULL,
            kategoriya TEXT NOT NULL,
            izoh TEXT,
            vaqt TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS eslatmalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            foydalanuvchi_id INTEGER NOT NULL,
            matn TEXT NOT NULL,
            bajarilgan INTEGER DEFAULT 0,
            vaqt TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fayllar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            foydalanuvchi_id INTEGER NOT NULL,
            fayl_nomi TEXT NOT NULL,
            fayl_yoli TEXT NOT NULL,
            hajmi INTEGER,
            yuklangan TEXT NOT NULL
        );
    """)
    ulanish.commit()
    ulanish.close()

baza_ishga_tushir()

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
        "X-Title": "Blip Super App"
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    data = {"model": model, "messages": messages, "temperature": 0.7, "max_tokens": 2000}
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Xatolik: {r.status_code} - {r.text[:200]}"
    except Exception as e:
        return f"So'rovda xatolik: {e}"

# HTML uslubi
STYLE = "*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,sans-serif}body{background:#0a0a0a;color:#fff;min-height:100vh;padding:10px}.karta{background:#111;border:1px solid #39ff14;border-radius:10px;padding:20px;max-width:650px;margin:0 auto}h1{color:#39ff14;text-align:center;margin-bottom:10px}.sub{color:#00c8ff;text-align:center;font-size:12px;margin-bottom:20px}input,select,textarea,button{width:100%;padding:10px;margin:8px 0;background:#000;border:1px solid #39ff14;color:#fff;border-radius:5px}button{background:#39ff14;color:#000;font-weight:bold;cursor:pointer}a{color:#00c8ff;text-decoration:none}.xato{color:red;text-align:center}.natija{background:#1a1a1a;padding:15px;border-radius:8px;margin:10px 0;white-space:pre-wrap}.menyu{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:15px 0}.menyu a{padding:12px;background:#111;border:1px solid #39ff14;border-radius:5px;text-align:center;color:#39ff14}"

LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Blip Super App</title><style>"""+STYLE+""" body{display:flex;align-items:center;justify-content:center}</style></head><body><div class=karta><h1>Blip Super App</h1><div class=sub>Kirish</div><form method=POST><input name=username placeholder='Username' required autofocus><input type=password name=parol placeholder='Parol' required><button>KIRISH</button></form>{% if xato %}<p class=xato>{{ xato }}</p>{% endif %}</div></body></html>"""

MENYU_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Menyu</title><style>"""+STYLE+"""</style></head><body><div class=karta><h1>Blip Super App</h1><div class=sub>Xush kelibsiz, {{ username }}!</div><div class=menyu><a href='/ai'>🤖 AI Chat</a><a href='/pdf'>📄 PDF Studio</a><a href='/valyuta'>💱 Valyuta</a><a href='/obhavo'>🌤 Ob-havo</a><a href='/tarjima'>🌐 Tarjimon</a><a href='/xarajat'>💰 Xarajatlar</a><a href='/eslatma'>📝 Eslatmalar</a><a href='/bulut'>📁 Bulut</a></div><a href='/logout' style=color:#ff4444;text-align:center;display:block;margin-top:15px'>Chiqish</a></div></body></html>"""

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        parol = request.form.get("parol","").strip()
        if parol == TIZIM_PAROLI and username:
            ulanish = baza_ulanish()
            foydalanuvchi = ulanish.execute("SELECT * FROM foydalanuvchilar WHERE username=?", (username,)).fetchone()
            if not foydalanuvchi:
                ulanish.execute("INSERT INTO foydalanuvchilar (username, yaratilgan) VALUES (?,?)", (username, hozirgi_vaqt()))
                foydalanuvchi = ulanish.execute("SELECT * FROM foydalanuvchilar WHERE username=?", (username,)).fetchone()
            ulanish.commit()
            ulanish.close()
            session["user_id"] = foydalanuvchi["id"]
            session["username"] = username
            return redirect(url_for("menyu"))
        return render_template_string(LOGIN_HTML, xato="Noto'g'ri parol yoki ism!")
    return render_template_string(LOGIN_HTML, xato=None)

@app.route("/menyu")
@login_talab
def menyu():
    return render_template_string(MENYU_HTML, username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
# ============================================================
#  BLIP SUPER APP v1.0 – 2/5
#  AI Chat va PDF Studio
# ============================================================

AI_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>AI Chat</title><style>"""+STYLE+"""</style></head><body><div class=karta><h1>🤖 AI Chat</h1><div class=sub>OpenRouter bilan suhbat</div><form method=POST action='/ai'><select name=model>{% for slug, nom in modellar.items() %}<option value='{{ slug }}' {% if tanlangan==slug %}selected{% endif %}>{{ nom }}</option>{% endfor %}</select><textarea name=savol rows=4 placeholder='Savolingiz...' required>{{ old_savol }}</textarea><button>Yuborish</button></form>{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}<a href='/menyu'>← Menyu</a></div></body></html>"""

PDF_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>PDF Studio</title><style>"""+STYLE+"""</style></head><body><div class=karta><h1>📄 PDF Studio</h1><div class=sub>PDF bilan ishlash</div><form method=POST action='/pdf_yaratish'><textarea name=matn rows=5 placeholder='PDF uchun matn kiriting...' required></textarea><input name=nomi placeholder='Fayl nomi (masalan: hujjat)' required><button>PDF yaratish</button></form><form method=POST action='/pdf_oqish' enctype=multipart/form-data><input type=file name=pdf accept='.pdf' required><button>PDF o'qish</button></form>{% if natija %}<div class=natija>{{ natija }}</div>{% endif %}<a href='/menyu'>← Menyu</a></div></body></html>"""

@app.route("/ai", methods=["GET","POST"])
@login_talab
def ai():
    modellar = {
        "deepseek/deepseek-chat": "DeepSeek Chat",
        "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet",
        "google/gemini-flash-1.5": "Gemini Flash 1.5",
        "openai/gpt-4o-mini": "GPT-4o Mini",
        "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
    }
    javob = None
    old_savol = ""
    tanlangan = "deepseek/deepseek-chat"
    if request.method == "POST":
        model = request.form.get("model","deepseek/deepseek-chat")
        savol = request.form.get("savol","").strip()
        old_savol = savol
        tanlangan = model
        if savol:
            javob = openrouter_sorash(savol, model=model)
    return render_template_string(AI_HTML, modellar=modellar, javob=javob, old_savol=old_savol, tanlangan=tanlangan)

@app.route("/pdf_yaratish", methods=["POST"])
@login_talab
def pdf_yaratish():
    matn = request.form.get("matn","").strip()
    nomi = request.form.get("nomi","hujjat").strip()
    if not matn:
        return redirect(url_for("pdf"))
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for qator in matn.split('\n'):
            pdf.multi_cell(0, 10, qator)
        fayl_nomi = secure_filename(nomi) + ".pdf"
        fayl_yoli = os.path.join(YUKLASH_PAPKA, fayl_nomi)
        pdf.output(fayl_yoli)
        natija = f"PDF yaratildi: {fayl_yoli}"
    except Exception as e:
        natija = f"Xatolik: {e}"
    return render_template_string(PDF_HTML, natija=natija)

@app.route("/pdf_oqish", methods=["POST"])
@login_talab
def pdf_oqish():
    fayl = request.files.get("pdf")
    if not fayl:
        return redirect(url_for("pdf"))
    try:
        from PyPDF2 import PdfReader
        import io
        pdf_content = fayl.read()
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        matn = ""
        for sahifa in pdf_reader.pages:
            matn += sahifa.extract_text() or ""
        natija = matn[:2000] if matn else "Matn topilmadi."
    except Exception as e:
        natija = f"Xatolik: {e}"
    return render_template_string(PDF_HTML, natija=natija)

@app.route("/pdf")
@login_talab
def pdf():
    return render_template_string(PDF_HTML, natija=None)
# ============================================================
#  BLIP SUPER APP v1.0 – 3/5
#  Valyuta, Ob-havo, Tarjimon
# ============================================================

VALYUTA_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Valyuta</title><style>"""+STYLE+"""</style></head><body><div class=karta><h1>💱 Valyuta Kurslari</h1><div class=sub>Real-vaqt ma'lumot</div>{% if kurslar %}<div class=natija>1 USD = {{ kurslar.usd_uzs }} UZS<br>1 USD = {{ kurslar.usd_tjs }} TJS<br>1 USD = {{ kurslar.usd_rub }} RUB<br>1 USD = {{ kurslar.usd_eur }} EUR</div>{% else %}<p class=xato>Ma'lumot olinmadi</p>{% endif %}<a href='/menyu'>← Menyu</a></div></body></html>"""

OBHAVO_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Ob-havo</title><style>"""+STYLE+"""</style></head><body><div class=karta><h1>🌤 Ob-havo</h1><div class=sub>Shahar bo'yicha</div><form method=POST action='/obhavo'><input name=shahar placeholder='Shahar nomi (masalan: Dushanbe)' required><button>Ko'rish</button></form>{% if natija %}<div class=natija>{{ natija }}</div>{% endif %}<a href='/menyu'>← Menyu</a></div></body></html>"""

TARJIMA_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Tarjimon</title><style>"""+STYLE+"""</style></head><body><div class=karta><h1>🌐 Tarjimon</h1><div class=sub>Matn tarjimasi</div><form method=POST action='/tarjima'><select name=til><option value='ingliz'>Ingliz</option><option value='rus'>Rus</option><option value='ozbek'>O'zbek</option></select><textarea name=matn rows=4 placeholder='Matn kiriting...' required>{{ old_matn }}</textarea><button>Tarjima qilish</button></form>{% if javob %}<div class=natija>{{ javob }}</div>{% endif %}<a href='/menyu'>← Menyu</a></div></body></html>"""

@app.route("/valyuta")
@login_talab
def valyuta():
    kurslar = None
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
        if r.status_code == 200:
            rates = r.json().get("rates", {})
            kurslar = {
                "usd_uzs": round(rates.get("UZS", 0), 2),
                "usd_tjs": round(rates.get("TJS", 0), 2),
                "usd_rub": round(rates.get("RUB", 0), 2),
                "usd_eur": round(rates.get("EUR", 0), 4),
            }
    except:
        pass
    return render_template_string(VALYUTA_HTML, kurslar=kurslar)

@app.route("/obhavo", methods=["GET","POST"])
@login_talab
def obhavo():
    natija = None
    if request.method == "POST":
        shahar = request.form.get("shahar","").strip()
        if shahar:
            try:
                url = f"https://wttr.in/{shahar}?format=%C+%t+%h+%w"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    natija = r.text.strip()
                else:
                    natija = "Ob-havo ma'lumoti olinmadi."
            except Exception as e:
                natija = f"Xatolik: {e}"
    return render_template_string(OBHAVO_HTML, natija=natija)

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
#  BLIP SUPER APP v1.0 – 4/5
#  Xarajat hisoblagich va Eslatmalar
# ============================================================

XARAJAT_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Xarajatlar</title><style>"""+STYLE+""" .xarajat-qator{display:flex;justify-content:space-between;padding:8px;border-bottom:1px solid #222}.summa{color:#39ff14;font-weight:bold}.kategoriya{color:#00c8ff}</style></head><body><div class=karta><h1>💰 Xarajatlar</h1><div class=sub>Kundalik xarajatlarni kuzating</div><form method=POST action='/xarajat_qoshish'><input type=number step=0.01 name=summa placeholder='Summa' required><select name=kategoriya><option value='Ovqat'>Ovqat</option><option value='Yo\'l'>Yo'l</option><option value='Aloqa'>Aloqa</option><option value='Kiyim'>Kiyim</option><option value='Boshqa'>Boshqa</option></select><input name=izoh placeholder='Izoh (ixtiyoriy)'><button>Qo'shish</button></form><h3 style=color:#39ff14;margin:15px 0>Jami: {{ jami }} so'm</h3>{% for x in xarajatlar %}<div class=xarajat-qator><span class=kategoriya>{{ x.kategoriya }}</span><span>{{ x.izoh or '' }}</span><span class=summa>{{ x.summa }}</span><a href='/xarajat_ochirish/{{ x.id }}' style=color:red>✕</a></div>{% endfor %}<a href='/menyu'>← Menyu</a></div></body></html>"""

ESLATMA_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Eslatmalar</title><style>"""+STYLE+""" .eslatma-qator{display:flex;justify-content:space-between;padding:8px;border-bottom:1px solid #222}.bajarilgan{text-decoration:line-through;color:#666}</style></head><body><div class=karta><h1>📝 Eslatmalar</h1><div class=sub>Vazifalaringiz</div><form method=POST action='/eslatma_qoshish'><input name=matn placeholder='Yangi eslatma...' required><button>Qo'shish</button></form>{% for e in eslatmalar %}<div class=eslatma-qator><span class={% if e.bajarilgan %}bajarilgan{% endif %}>{{ e.matn }}</span><div><a href='/eslatma_bajarish/{{ e.id }}'>{% if not e.bajarilgan %}✓{% else %}↩{% endif %}</a> <a href='/eslatma_ochirish/{{ e.id }}' style=color:red>✕</a></div></div>{% endfor %}<a href='/menyu'>← Menyu</a></div></body></html>"""

@app.route("/xarajat")
@login_talab
def xarajat():
    ulanish = baza_ulanish()
    xarajatlar = ulanish.execute("SELECT * FROM xarajatlar WHERE foydalanuvchi_id=? ORDER BY id DESC LIMIT 100", (session["user_id"],)).fetchall()
    jami = ulanish.execute("SELECT SUM(summa) as jami FROM xarajatlar WHERE foydalanuvchi_id=?", (session["user_id"],)).fetchone()["jami"] or 0
    ulanish.close()
    return render_template_string(XARAJAT_HTML, xarajatlar=xarajatlar, jami=jami)

@app.route("/xarajat_qoshish", methods=["POST"])
@login_talab
def xarajat_qoshish():
    summa = float(request.form.get("summa", 0))
    kategoriya = request.form.get("kategoriya", "Boshqa")
    izoh = request.form.get("izoh", "").strip()
    if summa > 0:
        ulanish = baza_ulanish()
        ulanish.execute("INSERT INTO xarajatlar (foydalanuvchi_id, summa, kategoriya, izoh, vaqt) VALUES (?,?,?,?,?)",
                        (session["user_id"], summa, kategoriya, izoh, hozirgi_vaqt()))
        ulanish.commit()
        ulanish.close()
    return redirect(url_for("xarajat"))

@app.route("/xarajat_ochirish/<int:xarajat_id>")
@login_talab
def xarajat_ochirish(xarajat_id):
    ulanish = baza_ulanish()
    ulanish.execute("DELETE FROM xarajatlar WHERE id=? AND foydalanuvchi_id=?", (xarajat_id, session["user_id"]))
    ulanish.commit()
    ulanish.close()
    return redirect(url_for("xarajat"))

@app.route("/eslatma")
@login_talab
def eslatma():
    ulanish = baza_ulanish()
    eslatmalar = ulanish.execute("SELECT * FROM eslatmalar WHERE foydalanuvchi_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    ulanish.close()
    return render_template_string(ESLATMA_HTML, eslatmalar=eslatmalar)

@app.route("/eslatma_qoshish", methods=["POST"])
@login_talab
def eslatma_qoshish():
    matn = request.form.get("matn", "").strip()
    if matn:
        ulanish = baza_ulanish()
        ulanish.execute("INSERT INTO eslatmalar (foydalanuvchi_id, matn, vaqt) VALUES (?,?,?)",
                        (session["user_id"], matn, hozirgi_vaqt()))
        ulanish.commit()
        ulanish.close()
    return redirect(url_for("eslatma"))

@app.route("/eslatma_bajarish/<int:eslatma_id>")
@login_talab
def eslatma_bajarish(eslatma_id):
    ulanish = baza_ulanish()
    eslatma = ulanish.execute("SELECT bajarilgan FROM eslatmalar WHERE id=? AND foydalanuvchi_id=?", (eslatma_id, session["user_id"])).fetchone()
    if eslatma:
        yangi = 0 if eslatma["bajarilgan"] else 1
        ulanish.execute("UPDATE eslatmalar SET bajarilgan=? WHERE id=?", (yangi, eslatma_id))
        ulanish.commit()
    ulanish.close()
    return redirect(url_for("eslatma"))

@app.route("/eslatma_ochirish/<int:eslatma_id>")
@login_talab
def eslatma_ochirish(eslatma_id):
    ulanish = baza_ulanish()
    ulanish.execute("DELETE FROM eslatmalar WHERE id=? AND foydalanuvchi_id=?", (eslatma_id, session["user_id"]))
    ulanish.commit()
    ulanish.close()
    return redirect(url_for("eslatma"))
# ============================================================
#  BLIP SUPER APP v1.0 – 5/5
#  Bulutli saqlash va ishga tushirish
# ============================================================

BULUT_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Bulut</title><style>"""+STYLE+""" .fayl-qator{display:flex;justify-content:space-between;padding:8px;border-bottom:1px solid #222}</style></head><body><div class=karta><h1>📁 Bulutli saqlash</h1><div class=sub>Fayllaringizni yuklang va ulashing</div><form method=POST action='/bulut_yuklash' enctype=multipart/form-data><input type=file name=fayl required><button>Yuklash</button></form>{% for f in fayllar %}<div class=fayl-qator><span>{{ f.fayl_nomi }} ({{ f.hajmi }} KB)</span><div><a href='/bulut_yuklab_olish/{{ f.id }}'>⬇</a> <a href='/bulut_ochirish/{{ f.id }}' style=color:red>✕</a></div></div>{% endfor %}<a href='/menyu'>← Menyu</a></div></body></html>"""

@app.route("/bulut")
@login_talab
def bulut():
    ulanish = baza_ulanish()
    fayllar = ulanish.execute("SELECT * FROM fayllar WHERE foydalanuvchi_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    ulanish.close()
    return render_template_string(BULUT_HTML, fayllar=fayllar)

@app.route("/bulut_yuklash", methods=["POST"])
@login_talab
def bulut_yuklash():
    fayl = request.files.get("fayl")
    if fayl and fayl.filename:
        fayl_nomi = secure_filename(fayl.filename)
        fayl_yoli = os.path.join(YUKLASH_PAPKA, f"{session['user_id']}_{fayl_nomi}")
        fayl.save(fayl_yoli)
        hajmi = os.path.getsize(fayl_yoli) // 1024
        ulanish = baza_ulanish()
        ulanish.execute("INSERT INTO fayllar (foydalanuvchi_id, fayl_nomi, fayl_yoli, hajmi, yuklangan) VALUES (?,?,?,?,?)",
                        (session["user_id"], fayl_nomi, fayl_yoli, hajmi, hozirgi_vaqt()))
        ulanish.commit()
        ulanish.close()
    return redirect(url_for("bulut"))

@app.route("/bulut_yuklab_olish/<int:fayl_id>")
@login_talab
def bulut_yuklab_olish(fayl_id):
    ulanish = baza_ulanish()
    fayl = ulanish.execute("SELECT * FROM fayllar WHERE id=? AND foydalanuvchi_id=?", (fayl_id, session["user_id"])).fetchone()
    ulanish.close()
    if fayl and os.path.exists(fayl["fayl_yoli"]):
        return send_file(fayl["fayl_yoli"], as_attachment=True)
    return "Fayl topilmadi", 404

@app.route("/bulut_ochirish/<int:fayl_id>")
@login_talab
def bulut_ochirish(fayl_id):
    ulanish = baza_ulanish()
    fayl = ulanish.execute("SELECT * FROM fayllar WHERE id=? AND foydalanuvchi_id=?", (fayl_id, session["user_id"])).fetchone()
    if fayl:
        if os.path.exists(fayl["fayl_yoli"]):
            os.remove(fayl["fayl_yoli"])
        ulanish.execute("DELETE FROM fayllar WHERE id=?", (fayl_id,))
        ulanish.commit()
    ulanish.close()
    return redirect(url_for("bulut"))

if __name__ == "__main__":
    print("Blip Super App ishga tushdi (port {})".format(PORT))
    app.run(host="0.0.0.0", port=PORT, debug=False)    
    