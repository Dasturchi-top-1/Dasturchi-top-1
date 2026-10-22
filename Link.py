# ==========================================================
# BLIP LINK QISQARTIRGICH
# Flask + SQLite + QR kod - bitta faylda, to'liq ishlaydigan versiya
# PLATFORMA: Pydroid 3 (Android)
# ==========================================================
#
# O'RNATISH:
#   pip install flask qrcode pillow requests
#
# ISHGA TUSHIRISH:
#   python blip_links.py
#
# ==========================================================

import os
import re
import io
import random
import string
import sqlite3
import requests
from datetime import datetime
from flask import (
    Flask, request, session, redirect, url_for,
    render_template_string, send_file, g, abort
)
import qrcode

# ==========================================================
# SOZLAMALAR
# ==========================================================
APP_PASSWORD = "YOUR_PASSWORD"
DB_FOLDER = "/storage/emulated/0/AI"
DB_PATH = os.path.join(DB_FOLDER, "blip_links.db")
PORT = 8080

os.makedirs(DB_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"


# ==========================================================
# BAZA BILAN ISHLASH
# ==========================================================

def get_db():
    """Har bir so'rov uchun bitta ulanish (Flask 'g' obyekti orqali)"""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            yaratilgan TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS havolalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            foydalanuvchi_id INTEGER NOT NULL,
            uzun_url TEXT NOT NULL,
            qisqa_kod TEXT UNIQUE NOT NULL,
            yaratilgan TEXT NOT NULL,
            FOREIGN KEY (foydalanuvchi_id) REFERENCES foydalanuvchilar (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bosishlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            havola_id INTEGER NOT NULL,
            ip TEXT,
            mamlakat TEXT DEFAULT 'Nomalum',
            vaqt TEXT NOT NULL,
            FOREIGN KEY (havola_id) REFERENCES havolalar (id)
        )
    """)

    conn.commit()
    conn.close()


def get_or_create_user(username):
    """Foydalanuvchini topadi, mavjud bo'lmasa yaratadi. PARAMETRLASHTIRILGAN so'rov."""
    db = get_db()
    row = db.execute(
        "SELECT id FROM foydalanuvchilar WHERE username = ?", (username,)
    ).fetchone()

    if row:
        return row["id"]

    cursor = db.execute(
        "INSERT INTO foydalanuvchilar (username, yaratilgan) VALUES (?, ?)",
        (username, datetime.now().isoformat())
    )
    db.commit()
    return cursor.lastrowid


# ==========================================================
# YORDAMCHI FUNKSIYALAR
# ==========================================================

def generate_random_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def is_valid_custom_code(code):
    return bool(re.match(r'^[A-Za-z0-9_-]+$', code))


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def get_country_from_ip(ip):
    """IP orqali mamlakatni aniqlashga urinadi - xato bo'lsa 'Nomalum' qaytaradi"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        if data.get("status") == "success":
            return data.get("country", "Nomalum")
    except Exception:
        pass
    return "Nomalum"


def login_required(func):
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ==========================================================
# DIZAYN - CYBERPUNK USLUBI (barcha sahifalar uchun umumiy CSS)
# ==========================================================

BASE_STYLE = """
<style>
  * { box-sizing: border-box; font-family: Consolas, monospace; }
  body { background:#0a0a0a; color:#39ff14; margin:0; padding:20px; }
  h1, h2 { color:#00c8ff; text-shadow: 0 0 8px #00c8ff44; }
  a { color:#00c8ff; text-decoration:none; }
  .card { background:#111; border:1px solid #39ff14; border-radius:10px;
          padding:18px; margin:14px 0; box-shadow: 0 0 12px #39ff1422; }
  input[type=text], input[type=password] {
      width:100%; padding:10px; margin:6px 0; background:#0a0a0a;
      border:1px solid #00c8ff; border-radius:6px; color:#39ff14; font-family:Consolas;
  }
  button, .btn {
      background:#39ff14; color:#0a0a0a; border:none; padding:10px 16px;
      border-radius:6px; font-weight:bold; cursor:pointer; font-family:Consolas;
  }
  button.danger { background:#ff3355; color:white; }
  table { width:100%; border-collapse:collapse; margin-top:10px; }
  th, td { border:1px solid #222; padding:8px; text-align:left; font-size:13px; }
  th { color:#00c8ff; }
  .error { color:#ff3355; }
  .short-link { font-size:18px; color:#39ff14; word-break:break-all; }
  img.qr { background:white; padding:6px; border-radius:6px; }
</style>
"""

# ==========================================================
# HTML SAHIFALAR
# ==========================================================

LOGIN_PAGE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Blip Link - Kirish</title>""" + BASE_STYLE + """</head>
<body>
<div class="card" style="max-width:340px; margin:60px auto;">
  <h1>BLIP LINK</h1>
  <form method="POST">
    <input type="text" name="username" placeholder="Foydalanuvchi nomi" required>
    <input type="password" name="password" placeholder="Parol" required>
    <button type="submit" style="width:100%;">KIRISH</button>
  </form>
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
</div>
</body></html>
"""

DASHBOARD_PAGE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Blip Link - Panel</title>""" + BASE_STYLE + """</head>
<body>
<h1>BLIP LINK PANEL</h1>
<p>Xush kelibsiz, <b>{{ username }}</b>!
   {% if username == 'admin' %}<a href="/admin">[ADMIN PANEL]</a>{% endif %}
   &nbsp;|&nbsp; <a href="/logout">Chiqish</a>
</p>

<div class="card">
  <h2>Yangi havola yaratish</h2>
  <form method="POST" action="/qisqartirish">
    <input type="text" name="uzun_url" placeholder="https://misol.com/juda-uzun-manzil" required>
    <input type="text" name="maxsus_kod" placeholder="Maxsus kod (ixtiyoriy, masalan: google)">
    <button type="submit">QISQARTIRISH</button>
  </form>

  {% if error %}<p class="error">{{ error }}</p>{% endif %}

  {% if new_link %}
  <div style="margin-top:14px; padding-top:14px; border-top:1px solid #222;">
    <p class="short-link">{{ new_link }}</p>
    <img class="qr" src="/qr/{{ new_code }}" width="140">
  </div>
  {% endif %}
</div>

<div class="card">
  <h2>Sizning havolalaringiz</h2>
  <table>
    <tr><th>Kod</th><th>Asl URL</th><th>Bosishlar</th><th>Yangi manzil</th><th>Amal</th></tr>
    {% for link in links %}
    <tr>
      <td><a href="/{{ link.qisqa_kod }}" target="_blank">{{ link.qisqa_kod }}</a></td>
      <td>{{ link.uzun_url[:40] }}{% if link.uzun_url|length > 40 %}...{% endif %}</td>
      <td>{{ link.bosishlar_soni }}</td>
      <td>
        <form method="POST" action="/yangilash/{{ link.id }}" style="display:flex; gap:4px;">
          <input type="text" name="yangi_url" placeholder="Yangi URL"
                 style="margin:0; font-size:12px; padding:6px;">
          <button type="submit" style="padding:6px 10px; font-size:12px;">Yangilash</button>
        </form>
      </td>
      <td>
        <form method="POST" action="/ochirish/{{ link.id }}" style="display:inline;"
              onsubmit="return confirm('Ochirishni tasdiqlaysizmi?');">
          <button type="submit" class="danger">O'chirish</button>
        </form>
      </td>
    </tr>
    {% endfor %}
  </table>
</div>
</body></html>
"""

ADMIN_PAGE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Blip Link - Admin</title>""" + BASE_STYLE + """</head>
<body>
<h1>ADMIN PANEL</h1>
<p><a href="/dashboard">Panelga qaytish</a> | <a href="/logout">Chiqish</a></p>

<div class="card">
  <h2>Umumiy statistika</h2>
  <p>Jami foydalanuvchilar: <b>{{ stats.users }}</b></p>
  <p>Jami havolalar: <b>{{ stats.links }}</b></p>
  <p>Jami bosishlar: <b>{{ stats.clicks }}</b></p>
</div>

<div class="card">
  <h2>Barcha havolalar</h2>
  <table>
    <tr><th>ID</th><th>Kod</th><th>URL</th><th>Bosishlar</th></tr>
    {% for link in all_links %}
    <tr>
      <td>{{ link.id }}</td>
      <td>{{ link.qisqa_kod }}</td>
      <td>{{ link.uzun_url[:50] }}</td>
      <td>{{ link.bosishlar_soni }}</td>
    </tr>
    {% endfor %}
  </table>
</div>
</body></html>
"""


# ==========================================================
# YO'NALISHLAR (ROUTES)
# ==========================================================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username:
            return render_template_string(LOGIN_PAGE, error="Foydalanuvchi nomini kiriting!")

        if password != APP_PASSWORD:
            return render_template_string(LOGIN_PAGE, error="Parol noto'g'ri!")

        session["username"] = username
        return redirect(url_for("dashboard"))

    return render_template_string(LOGIN_PAGE, error=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    username = session["username"]
    db = get_db()
    user_id = get_or_create_user(username)

    links = db.execute("""
        SELECT h.id, h.uzun_url, h.qisqa_kod,
               (SELECT COUNT(*) FROM bosishlar b WHERE b.havola_id = h.id) AS bosishlar_soni
        FROM havolalar h
        WHERE h.foydalanuvchi_id = ?
        ORDER BY h.id DESC
    """, (user_id,)).fetchall()

    return render_template_string(
        DASHBOARD_PAGE, username=username, links=links,
        error=None, new_link=None, new_code=None
    )


@app.route("/qisqartirish", methods=["POST"])
@login_required
def qisqartirish():
    username = session["username"]
    db = get_db()
    user_id = get_or_create_user(username)

    uzun_url = request.form.get("uzun_url", "").strip()
    maxsus_kod = request.form.get("maxsus_kod", "").strip()

    error = None
    new_link = None
    new_code = None

    if not uzun_url:
        error = "URL kiritish shart!"
    else:
        uzun_url = normalize_url(uzun_url)

        if maxsus_kod:
            if not is_valid_custom_code(maxsus_kod):
                error = "Kod faqat lotin harflari, raqamlar, - va _ dan iborat bo'lishi kerak!"
            else:
                existing = db.execute(
                    "SELECT id FROM havolalar WHERE qisqa_kod = ?", (maxsus_kod,)
                ).fetchone()
                if existing:
                    error = "Bu kod allaqachon band!"
                else:
                    new_code = maxsus_kod
        else:
            for _ in range(10):
                candidate = generate_random_code()
                existing = db.execute(
                    "SELECT id FROM havolalar WHERE qisqa_kod = ?", (candidate,)
                ).fetchone()
                if not existing:
                    new_code = candidate
                    break

            if not new_code:
                error = "Kod yaratishda xato, qayta urinib ko'ring."

        if new_code and not error:
            db.execute(
                "INSERT INTO havolalar (foydalanuvchi_id, uzun_url, qisqa_kod, yaratilgan) "
                "VALUES (?, ?, ?, ?)",
                (user_id, uzun_url, new_code, datetime.now().isoformat())
            )
            db.commit()
            new_link = request.host_url.replace("http://", "https://") + new_code

    links = db.execute("""
        SELECT h.id, h.uzun_url, h.qisqa_kod,
               (SELECT COUNT(*) FROM bosishlar b WHERE b.havola_id = h.id) AS bosishlar_soni
        FROM havolalar h
        WHERE h.foydalanuvchi_id = ?
        ORDER BY h.id DESC
    """, (user_id,)).fetchall()

    return render_template_string(
        DASHBOARD_PAGE, username=username, links=links,
        error=error, new_link=new_link, new_code=new_code
    )


@app.route("/<qisqa_kod>")
def redirect_link(qisqa_kod):
    if qisqa_kod in ("dashboard", "qisqartirish", "admin", "logout", "favicon.ico"):
        abort(404)

    db = get_db()
    link = db.execute(
        "SELECT id, uzun_url FROM havolalar WHERE qisqa_kod = ?", (qisqa_kod,)
    ).fetchone()

    if not link:
        return "Havola topilmadi.", 404

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    country = get_country_from_ip(ip)

    db.execute(
        "INSERT INTO bosishlar (havola_id, ip, mamlakat, vaqt) VALUES (?, ?, ?, ?)",
        (link["id"], ip, country, datetime.now().isoformat())
    )
    db.commit()

    return redirect(link["uzun_url"])


@app.route("/qr/<kod>")
def qr_code(kod):
    db = get_db()
    link = db.execute(
        "SELECT qisqa_kod FROM havolalar WHERE qisqa_kod = ?", (kod,)
    ).fetchone()

    if not link:
        abort(404)

    full_url = request.host_url.replace("http://", "https://") + kod

    img = qrcode.make(full_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")


@app.route("/ochirish/<int:havola_id>", methods=["POST"])
@login_required
def ochirish(havola_id):
    username = session["username"]
    db = get_db()
    user_id = get_or_create_user(username)

    link = db.execute(
        "SELECT id FROM havolalar WHERE id = ? AND foydalanuvchi_id = ?",
        (havola_id, user_id)
    ).fetchone()

    if link:
        db.execute("DELETE FROM bosishlar WHERE havola_id = ?", (havola_id,))
        db.execute("DELETE FROM havolalar WHERE id = ?", (havola_id,))
        db.commit()

    return redirect(url_for("dashboard"))


@app.route("/yangilash/<int:havola_id>", methods=["POST"])
@login_required
def yangilash(havola_id):
    """Qisqa kod O'ZGARMAYDI, lekin u yo'naltiradigan uzun URL yangilanadi -
    istalgan vaqt, xohlagancha marta o'zgartirish mumkin"""
    username = session["username"]
    db = get_db()
    user_id = get_or_create_user(username)

    yangi_url = request.form.get("yangi_url", "").strip()

    if yangi_url:
        yangi_url = normalize_url(yangi_url)

        # Faqat O'ZINING havolasini yangilay oladi (boshqa foydalanuvchining emas)
        link = db.execute(
            "SELECT id FROM havolalar WHERE id = ? AND foydalanuvchi_id = ?",
            (havola_id, user_id)
        ).fetchone()

        if link:
            db.execute(
                "UPDATE havolalar SET uzun_url = ? WHERE id = ?",
                (yangi_url, havola_id)
            )
            db.commit()

    return redirect(url_for("dashboard"))


@app.route("/admin")
@login_required
def admin():
    if session.get("username") != "admin":
        abort(403)

    db = get_db()

    users_count = db.execute("SELECT COUNT(*) AS c FROM foydalanuvchilar").fetchone()["c"]
    links_count = db.execute("SELECT COUNT(*) AS c FROM havolalar").fetchone()["c"]
    clicks_count = db.execute("SELECT COUNT(*) AS c FROM bosishlar").fetchone()["c"]

    all_links = db.execute("""
        SELECT h.id, h.qisqa_kod, h.uzun_url,
               (SELECT COUNT(*) FROM bosishlar b WHERE b.havola_id = h.id) AS bosishlar_soni
        FROM havolalar h
        ORDER BY h.id DESC
    """).fetchall()

    stats = {"users": users_count, "links": links_count, "clicks": clicks_count}

    return render_template_string(ADMIN_PAGE, stats=stats, all_links=all_links)


# ==========================================================
# DASTUR ISHGA TUSHIRISH
# ==========================================================

if __name__ == "__main__":
    init_db()
    print("=" * 55)
    print("BLIP LINK QISQARTIRGICH ishga tushmoqda...")
    print(f"Barcha foydalanuvchilar uchun parol: {APP_PASSWORD}")
    print("Admin panel uchun username: admin")
    print(f"Brauzerda oching: http://<telefon-IP>:{PORT}")
    print("=" * 55)

    app.run(host="0.0.0.0", port=PORT, debug=False)
