# ============================================================
# BLIP ZEROCLOUD v1.0 – Shaxsiy bulut
# Fayl: blip_zerocloud.py
# ============================================================
import os, sqlite3, datetime, secrets, string, hashlib, shutil
from flask import Flask, request, session, redirect, url_for, render_template_string, send_file, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = "blip-zerocloud-921324"
PAROL = "921324"  # kirish paroli

ASOSIY_PAPKA = "/storage/emulated/0/BlipCloud"
VERSIYALAR_PAPKA = os.path.join(ASOSIY_PAPKA, "versiyalar")
BAZA_YOLI = os.path.join(ASOSIY_PAPKA, "cloud.db")

os.makedirs(ASOSIY_PAPKA, exist_ok=True)
os.makedirs(VERSIYALAR_PAPKA, exist_ok=True)

def baza_ulanish():
    ulanish = sqlite3.connect(BAZA_YOLI)
    ulanish.row_factory = sqlite3.Row
    return ulanish

def baza_ishga_tushir():
    ulanish = baza_ulanish()
    ulanish.executescript("""
        CREATE TABLE IF NOT EXISTS fayllar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomi TEXT NOT NULL,
            asl_joy TEXT NOT NULL,
            hajmi INTEGER,
            yuklangan TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS versiyalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fayl_id INTEGER NOT NULL,
            joy TEXT NOT NULL,
            vaqt TEXT NOT NULL,
            FOREIGN KEY(fayl_id) REFERENCES fayllar(id)
        );
        CREATE TABLE IF NOT EXISTS havolalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fayl_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            yaratilgan TEXT NOT NULL,
            amal_qilish TEXT,
            bir_marta INTEGER DEFAULT 0,
            parol TEXT,
            FOREIGN KEY(fayl_id) REFERENCES fayllar(id)
        );
    """)
    ulanish.commit()
    ulanish.close()

baza_ishga_tushir()

def login_talab(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("auth"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

STYLE = "*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,monospace}body{background:#0a0a0a;color:#39ff14;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:10px}.karta{background:#111;border:1px solid #39ff14;border-radius:10px;padding:25px;width:100%;max-width:700px}h1{color:#39ff14;text-align:center;margin-bottom:15px}input,button{width:100%;padding:10px;margin:8px 0;background:#000;border:1px solid #39ff14;color:#39ff14;border-radius:5px}button{background:#39ff14;color:#000;font-weight:bold}a{color:#00c8ff;text-decoration:none}.jadval{width:100%;border-collapse:collapse;margin:15px 0}.jadval th,.jadval td{border:1px solid #333;padding:8px;text-align:left;font-size:12px}.jadval th{background:#1a1a1a;color:#39ff14}"

LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><title>Blip ZeroCloud</title><style>""" + STYLE + """</style></head><body><div class=karta>
<h1>Blip ZeroCloud</h1><form method=POST action='/login'>
<input type=password name=parol placeholder='Parol' required>
<button>KIRISH</button></form>
{% if xato %}<p style=color:red>{{ xato }}</p>{% endif %}</div></body></html>"""

BOSH_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><title>Bulut</title><style>""" + STYLE + """</style></head><body><div class=karta>
<h1>Blip ZeroCloud</h1>
<form method=POST action='/yuklash' enctype=multipart/form-data>
<input type=file name=fayl required>
<button>Yuklash</button></form>
<h3>Fayllar:</h3>
<table class=jadval><tr><th>Nomi</th><th>Hajmi</th><th>Amallar</th></tr>
{% for f in fayllar %}<tr>
<td>{{ f.nomi }}</td><td>{{ f.hajmi }} KB</td>
<td><a href='/yuklab_olish/{{ f.id }}'>Yuklab olish</a> | <a href='/versiyalar/{{ f.id }}'>Versiyalar</a> | <a href='/ulashish/{{ f.id }}'>Ulashish</a> | <a href='/ochirish/{{ f.id }}' style=color:red>O'chirish</a></td>
</tr>{% endfor %}</table>
<a href='/logout'>Chiqish</a></div></body></html>"""

VERSIYALAR_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><title>Versiyalar</title><style>""" + STYLE + """</style></head><body><div class=karta>
<h1>Versiyalar - {{ fayl.nomi }}</h1>
<table class=jadval><tr><th>Vaqt</th><th>Amal</th></tr>
{% for v in versiyalar %}<tr><td>{{ v.vaqt }}</td><td><a href='/versiyani_yuklab_olish/{{ v.id }}'>Yuklab olish</a></td></tr>{% endfor %}</table>
<a href='/'>← Orqaga</a></div></body></html>"""

ULASHISH_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><title>Ulashish</title><style>""" + STYLE + """</style></head><body><div class=karta>
<h1>Faylni ulashish</h1>
<form method=POST action='/ulashish/{{ fayl.id }}'>
<label>Havola amal qilish muddati (daqiqada, bo'sh = cheksiz):</label>
<input type=number name=muddat placeholder='Masalan: 60'>
<label>Bir martalik havola:</label>
<input type=checkbox name=bir_marta value='1'>
<label>Parol (ixtiyoriy):</label>
<input type=text name=parol placeholder='Parol'>
<button>HAVOLA YARATISH</button></form>
{% if havola %}<p class=yaxshi>Havola: <a href='{{ havola }}' target='_blank'>{{ havola }}</a></p>{% endif %}
<a href='/'>← Orqaga</a></div></body></html>"""

@app.route("/")
def bosh():
    if session.get("auth"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        parol = request.form.get("parol", "")
        if parol == PAROL:
            session["auth"] = True
            return redirect(url_for("dashboard"))
        return render_template_string(LOGIN_HTML, xato="Noto'g'ri parol")
    return render_template_string(LOGIN_HTML, xato=None)

@app.route("/dashboard")
@login_talab
def dashboard():
    ulanish = baza_ulanish()
    fayllar = ulanish.execute("SELECT * FROM fayllar ORDER BY id DESC").fetchall()
    ulanish.close()
    return render_template_string(BOSH_HTML, fayllar=fayllar)

@app.route("/yuklash", methods=["POST"])
@login_talab
def yuklash():
    fayl = request.files.get("fayl")
    if not fayl or not fayl.filename:
        return "Fayl tanlanmagan", 400
    nomi = fayl.filename
    # Xavfsiz nom
    nomi = nomi.replace("/", "_").replace("\\", "_")
    asl_joy = os.path.join(ASOSIY_PAPKA, nomi)

    # Agar shu nomdagi fayl mavjud bo'lsa, eski faylni versiyaga saqlaymiz
    ulanish = baza_ulanish()
    mavjud = ulanish.execute("SELECT * FROM fayllar WHERE nomi=?", (nomi,)).fetchone()
    if mavjud:
        # Eski faylni versiyalar papkasiga ko'chiramiz
        versiya_nomi = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{nomi}"
        versiya_joy = os.path.join(VERSIYALAR_PAPKA, versiya_nomi)
        if os.path.exists(mavjud["asl_joy"]):
            shutil.copy2(mavjud["asl_joy"], versiya_joy)
            ulanish.execute("INSERT INTO versiyalar (fayl_id, joy, vaqt) VALUES (?,?,?)",
                            (mavjud["id"], versiya_joy, str(datetime.datetime.now())[:19]))
        # Yangi faylni asosiy joyga saqlaymiz
        fayl.save(asl_joy)
        ulanish.execute("UPDATE fayllar SET asl_joy=?, hajmi=?, yuklangan=? WHERE id=?",
                        (asl_joy, os.path.getsize(asl_joy)//1024, str(datetime.datetime.now())[:19], mavjud["id"]))
    else:
        # Yangi fayl
        fayl.save(asl_joy)
        ulanish.execute("INSERT INTO fayllar (nomi, asl_joy, hajmi, yuklangan) VALUES (?,?,?,?)",
                        (nomi, asl_joy, os.path.getsize(asl_joy)//1024, str(datetime.datetime.now())[:19]))
    ulanish.commit()
    ulanish.close()
    return redirect(url_for("dashboard"))

@app.route("/yuklab_olish/<int:fayl_id>")
@login_talab
def yuklab_olish(fayl_id):
    ulanish = baza_ulanish()
    fayl = ulanish.execute("SELECT * FROM fayllar WHERE id=?", (fayl_id,)).fetchone()
    ulanish.close()
    if fayl and os.path.exists(fayl["asl_joy"]):
        return send_file(fayl["asl_joy"], as_attachment=True, download_name=fayl["nomi"])
    return "Fayl topilmadi", 404

@app.route("/versiyalar/<int:fayl_id>")
@login_talab
def versiyalar(fayl_id):
    ulanish = baza_ulanish()
    fayl = ulanish.execute("SELECT * FROM fayllar WHERE id=?", (fayl_id,)).fetchone()
    versiyalar = ulanish.execute("SELECT * FROM versiyalar WHERE fayl_id=? ORDER BY id DESC", (fayl_id,)).fetchall()
    ulanish.close()
    return render_template_string(VERSIYALAR_HTML, fayl=fayl, versiyalar=versiyalar)

@app.route("/versiyani_yuklab_olish/<int:versiya_id>")
@login_talab
def versiyani_yuklab_olish(versiya_id):
    ulanish = baza_ulanish()
    versiya = ulanish.execute("SELECT * FROM versiyalar WHERE id=?", (versiya_id,)).fetchone()
    ulanish.close()
    if versiya and os.path.exists(versiya["joy"]):
        return send_file(versiya["joy"], as_attachment=True)
    return "Versiya topilmadi", 404

@app.route("/ulashish/<int:fayl_id>", methods=["GET", "POST"])
@login_talab
def ulashish(fayl_id):
    ulanish = baza_ulanish()
    fayl = ulanish.execute("SELECT * FROM fayllar WHERE id=?", (fayl_id,)).fetchone()
    havola = None
    if request.method == "POST":
        token = secrets.token_urlsafe(16)
        muddat = request.form.get("muddat")
        bir_marta = 1 if request.form.get("bir_marta") else 0
        parol = request.form.get("parol")
        amal_qilish = None
        if muddat:
            amal_qilish = str(datetime.datetime.now() + datetime.timedelta(minutes=int(muddat)))
        ulanish.execute("INSERT INTO havolalar (fayl_id, token, yaratilgan, amal_qilish, bir_marta, parol) VALUES (?,?,?,?,?,?)",
                        (fayl_id, token, str(datetime.datetime.now())[:19], amal_qilish, bir_marta, parol))
        ulanish.commit()
        havola = url_for("havola_orqali", token=token, _external=True)
    ulanish.close()
    return render_template_string(ULASHISH_HTML, fayl=fayl, havola=havola)

@app.route("/s/<token>")
def havola_orqali(token):
    ulanish = baza_ulanish()
    havola = ulanish.execute("SELECT * FROM havolalar WHERE token=?", (token,)).fetchone()
    if not havola:
        ulanish.close()
        return "Havola topilmadi", 404
    if havola["amal_qilish"] and datetime.datetime.now() > datetime.datetime.fromisoformat(havola["amal_qilish"]):
        ulanish.close()
        return "Havola muddati tugagan", 410
    if havola["parol"]:
        # Parol tekshirish
        if request.args.get("parol") != havola["parol"]:
            return """<form method=GET><input type=password name=parol placeholder='Parol'><button>OK</button></form>"""
    fayl = ulanish.execute("SELECT * FROM fayllar WHERE id=?", (havola["fayl_id"],)).fetchone()
    ulanish.close()
    if not fayl or not os.path.exists(fayl["asl_joy"]):
        return "Fayl topilmadi", 404

    if havola["bir_marta"]:
        # Bir martalik havolani o'chiramiz
        ulanish = baza_ulanish()
        ulanish.execute("DELETE FROM havolalar WHERE id=?", (havola["id"],))
        ulanish.commit()
        ulanish.close()

    return send_file(fayl["asl_joy"], as_attachment=True, download_name=fayl["nomi"])

@app.route("/ochirish/<int:fayl_id>")
@login_talab
def ochirish(fayl_id):
    ulanish = baza_ulanish()
    fayl = ulanish.execute("SELECT * FROM fayllar WHERE id=?", (fayl_id,)).fetchone()
    if fayl:
        # Faylning asosiy joyini o'chirish
        if os.path.exists(fayl["asl_joy"]):
            os.remove(fayl["asl_joy"])
        # Bog'liq versiyalarni o'chirish
        versiyalar = ulanish.execute("SELECT * FROM versiyalar WHERE fayl_id=?", (fayl_id,)).fetchall()
        for v in versiyalar:
            if os.path.exists(v["joy"]):
                os.remove(v["joy"])
        # Havolalarni o'chirish
        ulanish.execute("DELETE FROM havolalar WHERE fayl_id=?", (fayl_id,))
        # Faylni bazadan o'chirish
        ulanish.execute("DELETE FROM fayllar WHERE id=?", (fayl_id,))
        ulanish.commit()
    ulanish.close()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    print("Blip ZeroCloud ishga tushdi (port 8080)")
    app.run(host="0.0.0.0", port=8080, debug=False)