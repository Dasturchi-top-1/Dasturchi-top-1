import sqlite3
import os
import random
import time
import threading
from functools import wraps

from flask import Flask, request, session, redirect, url_for, render_template_string
from flask_socketio import SocketIO, emit, disconnect
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================
#  SOZLAMALAR
# ============================================================
BAZA_YOLI = "/storage/emulated/0/AI/blip_master_hub.db"
MAXFIY_KALIT = "921324-blip-master-hub-maxfiy-kalit"
PORT = 8080

app = Flask(__name__)
app.config["SECRET_KEY"] = MAXFIY_KALIT
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")


# ============================================================
#  MA'LUMOTLAR BAZASI (SQLite)
# ============================================================
def baza_ulanish():
    os.makedirs(os.path.dirname(BAZA_YOLI), exist_ok=True)
    ulanish = sqlite3.connect(BAZA_YOLI)
    ulanish.row_factory = sqlite3.Row
    return ulanish


def baza_ishga_tushir():
    ulanish = baza_ulanish()
    ulanish.execute("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            parol_xesh TEXT NOT NULL,
            yaratilgan TEXT NOT NULL
        )
    """)
    ulanish.commit()
    ulanish.close()


# ============================================================
#  AUTENTIFIKATSIYA YORDAMCHI FUNKSIYALARI
# ============================================================
def login_talab(funksiya):
    @wraps(funksiya)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_sahifa"))
        return funksiya(*args, **kwargs)
    return wrapper


# ============================================================
#  HTML SHABLONLARI (kiber-pank uslubi)
# ============================================================
ASOSIY_STIL = """
*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,monospace}
body{background:#0d0d0d;color:#39ff14;min-height:100vh;display:flex;
align-items:center;justify-content:center;padding:16px}
.karta{background:#111a24;border:1px solid #39ff14;border-radius:8px;
padding:24px;width:100%;max-width:340px;box-shadow:0 0 20px rgba(57,255,20,0.15)}
h1{color:#39ff14;font-size:18px;text-align:center;margin-bottom:4px}
.sub{color:#00c8ff;text-align:center;font-size:10px;margin-bottom:20px}
label{display:block;color:#00c8ff;font-size:11px;margin:10px 0 4px}
input{width:100%;background:#0d0d0d;color:#39ff14;border:1px solid #00c8ff;
border-radius:4px;padding:10px;font-size:14px}
button{width:100%;margin-top:18px;background:#39ff14;color:#0d0d0d;border:none;
border-radius:4px;padding:12px;font-weight:bold;font-size:14px;cursor:pointer}
.xato{color:#ff4444;font-size:12px;text-align:center;margin-top:10px}
.link{display:block;text-align:center;margin-top:16px;color:#00c8ff;
font-size:12px;text-decoration:none}
"""

LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Blip Master Hub :: Kirish</title><style>""" + ASOSIY_STIL + """</style></head>
<body><div class="karta">
<h1>&gt;&gt; BLIP MASTER HUB 2.0 &lt;&lt;</h1>
<div class="sub">[ TIZIMGA KIRISH :: 921324 ]</div>
<form method="POST">
<label>Foydalanuvchi nomi</label>
<input type="text" name="username" required autofocus>
<label>Parol</label>
<input type="password" name="parol" required>
<button type="submit">KIRISH</button>
</form>
{% if xato %}<div class="xato">{{ xato }}</div>{% endif %}
<a class="link" href="{{ url_for('royxat_sahifa') }}">Hisobingiz yo'qmi? Ro'yxatdan o'ting</a>
</div></body></html>"""

ROYXAT_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Blip Master Hub :: Ro'yxat</title><style>""" + ASOSIY_STIL + """</style></head>
<body><div class="karta">
<h1>&gt;&gt; BLIP MASTER HUB 2.0 &lt;&lt;</h1>
<div class="sub">[ RO'YXATDAN O'TISH :: 921324 ]</div>
<form method="POST">
<label>Foydalanuvchi nomi</label>
<input type="text" name="username" required autofocus minlength="3">
<label>Parol (kamida 6 belgi)</label>
<input type="password" name="parol" required minlength="6">
<button type="submit">RO'YXATDAN O'TISH</button>
</form>
{% if xato %}<div class="xato">{{ xato }}</div>{% endif %}
<a class="link" href="{{ url_for('login_sahifa') }}">Hisobingiz bormi? Kirish</a>
</div></body></html>"""

DASHBOARD_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Blip Master Hub :: Panel</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,monospace}
body{background:#0d0d0d;color:#39ff14;padding:16px}
h1{color:#39ff14;font-size:18px;text-align:center;margin-bottom:2px}
.sub{color:#00c8ff;text-align:center;font-size:11px;margin-bottom:6px}
.holat{text-align:center;font-size:11px;margin-bottom:20px}
.holat.ulangan{color:#39ff14}
.holat.uzilgan{color:#ff4444}
.kod-panel{background:#111a24;border:2px solid #00c8ff;border-radius:8px;
padding:30px 16px;text-align:center;margin-bottom:20px;box-shadow:0 0 25px rgba(0,200,255,0.2)}
.kod-yorlik{color:#00c8ff;font-size:11px;margin-bottom:10px}
.kod{font-size:34px;font-weight:bold;color:#39ff14;letter-spacing:2px}
.kod.miltillash{animation:miltilla 0.6s}
@keyframes miltilla{0%{color:#ffffff;text-shadow:0 0 20px #ffffff}
100%{color:#39ff14;text-shadow:0 0 10px #39ff14}}
.vaqt{color:#666;font-size:10px;margin-top:8px}
.chiqish{display:block;width:100%;background:#330000;color:#ff4444;
border:1px solid #ff4444;border-radius:4px;padding:10px;text-align:center;
text-decoration:none;font-size:13px;font-weight:bold}
.foydalanuvchi{text-align:center;color:#39ff14;font-size:12px;margin-bottom:16px}
</style></head>
<body>
<h1>&gt;&gt; BLIP MASTER HUB 2.0 &lt;&lt;</h1>
<div class="sub">[ NODE: 921324 | MASOFAVIY HAMKORLIK PLATFORMASI ]</div>
<div class="foydalanuvchi">Xush kelibsiz, {{ username }}!</div>
<div class="holat uzilgan" id="holat">● Ulanmoqda...</div>

<div class="kod-panel">
<div class="kod-yorlik">JORIY KIBER-KOD:</div>
<div class="kod" id="kod">------</div>
<div class="vaqt" id="vaqt">Kutilmoqda...</div>
</div>

<a class="chiqish" href="{{ url_for('logout_sahifa') }}">[ TIZIMDAN CHIQISH ]</a>

<script>
const socket = io();
const holatEl = document.getElementById("holat");
const kodEl = document.getElementById("kod");
const vaqtEl = document.getElementById("vaqt");

socket.on("connect", () => {
  holatEl.textContent = "● ULANDI";
  holatEl.className = "holat ulangan";
});

socket.on("disconnect", () => {
  holatEl.textContent = "● UZILDI";
  holatEl.className = "holat uzilgan";
});

socket.on("kod_yangilandi", (malumot) => {
  kodEl.textContent = malumot.kod;
  vaqtEl.textContent = "Yangilangan: " + malumot.vaqt;
  kodEl.classList.remove("miltillash");
  void kodEl.offsetWidth;
  kodEl.classList.add("miltillash");
});
</script>
</body></html>"""


# ============================================================
#  ROUTE'LAR (Sahifalar)
# ============================================================
@app.route("/")
def bosh_sahifa():
    if "user_id" in session:
        return redirect(url_for("dashboard_sahifa"))
    return redirect(url_for("login_sahifa"))


@app.route("/royxat", methods=["GET", "POST"])
def royxat_sahifa():
    if request.method == "GET":
        return render_template_string(ROYXAT_HTML, xato=None)

    username = request.form.get("username", "").strip()
    parol = request.form.get("parol", "")

    if len(username) < 3 or len(parol) < 6:
        return render_template_string(
            ROYXAT_HTML, xato="Username kamida 3, parol kamida 6 belgidan iborat bo'lsin."
        )

    parol_xesh = generate_password_hash(parol)
    ulanish = baza_ulanish()
    try:
        ulanish.execute(
            "INSERT INTO foydalanuvchilar (username, parol_xesh, yaratilgan) VALUES (?, ?, ?)",
            (username, parol_xesh, time.strftime("%Y-%m-%d %H:%M:%S")),
        )
        ulanish.commit()
    except sqlite3.IntegrityError:
        return render_template_string(
            ROYXAT_HTML, xato="Bu foydalanuvchi nomi allaqachon band."
        )
    finally:
        ulanish.close()

    return redirect(url_for("login_sahifa"))


@app.route("/login", methods=["GET", "POST"])
def login_sahifa():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML, xato=None)

    username = request.form.get("username", "").strip()
    parol = request.form.get("parol", "")

    ulanish = baza_ulanish()
    foydalanuvchi = ulanish.execute(
        "SELECT * FROM foydalanuvchilar WHERE username = ?", (username,)
    ).fetchone()
    ulanish.close()

    if foydalanuvchi is None or not check_password_hash(foydalanuvchi["parol_xesh"], parol):
        return render_template_string(
            LOGIN_HTML, xato="Username yoki parol noto'g'ri."
        )

    session["user_id"] = foydalanuvchi["id"]
    session["username"] = foydalanuvchi["username"]
    return redirect(url_for("dashboard_sahifa"))


@app.route("/logout")
def logout_sahifa():
    session.clear()
    return redirect(url_for("login_sahifa"))


@app.route("/dashboard")
@login_talab
def dashboard_sahifa():
    return render_template_string(DASHBOARD_HTML, username=session.get("username"))


# ============================================================
#  SOCKETIO HODISALARI (real-vaqt aloqa)
# ============================================================
@socketio.on("connect")
def socketio_ulanish():
    if "user_id" not in session:
        # Avtorizatsiyadan o'tmagan ulanish darhol rad etiladi.
        return False
    emit("xush_kelibsiz", {"xabar": f"Xush kelibsiz, {session.get('username')}!"})


@socketio.on("disconnect")
def socketio_uzilish():
    pass


# ============================================================
#  DINAMIK TASODIFIY KOD GENERATORI (orqa fon oqimi)
# ============================================================
def kod_generatori_oqimi():
    while True:
        socketio.sleep(5)
        kod = f"BLIP-{random.randint(100000, 999999)}"
        vaqt = time.strftime("%H:%M:%S")
        socketio.emit("kod_yangilandi", {"kod": kod, "vaqt": vaqt})


# ============================================================
#  ISHGA TUSHIRISH
# ============================================================
if __name__ == "__main__":
    print("=" * 45)
    print("  BLIP MASTER HUB 2.0 :: 921324")
    print("=" * 45)

    baza_ishga_tushir()
    print("[TIZIM] Ma'lumotlar bazasi tayyor.")

    socketio.start_background_task(kod_generatori_oqimi)
    print("[TIZIM] Kod generatori oqimi ishga tushdi.")

    print("[TIZIM] Server ishga tushmoqda: http://0.0.0.0:8080")
    socketio.run(app, host="0.0.0.0", port=PORT, debug=False,
                 allow_unsafe_werkzeug=True)
