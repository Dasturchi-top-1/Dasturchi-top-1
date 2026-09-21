# ============================================================
# 🎓 BLIP LESSON PRO v7.0 — AI to'liq
# Fayl: blip_lesson_pro.py
# ============================================================
import os, json, sqlite3, datetime, hashlib, secrets, urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

# ⚠️ SHU YERNI TO'LDIRING!
BOT_TOKEN = "YOUR_TOKEN"
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY"
ADMIN_TG_ID = 0

DB = "/storage/emulated/0/Ai/lesson_pro.db"
PORT = 8080

ADMIN_USER = "BLIP_KIBER_XAFSIZLIK"
ADMIN_PASS = "YOUR_PASS"
ADMIN_NAME = "ADMIN BLIP"

AI_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODELS = [
    "nex-agi/nex-n2.5-pro:free",
    "nex-agi/nex-n2.5-mini:free",
    "qwen/qwen3.8-27b:free",
    "z-ai/glm-5.2:free",
    "google/gemma-4-31b-it:free",
]

SYSTEM_PROMPT = (
    "Sen BLIP LESSON PRO platformasining aqlli yordamchisisan. "
    "Sen quyidagi sohalarda CHUQUR bilimga egasan:\n"
    "1. Python dasturlash\n"
    "2. Ingliz tili\n"
    "3. Arab tili va Qur'on\n"
    "4. Kiber xavfsizlik\n"
    "5. Matematika, fizika, kimyo, biologiya\n"
    "6. Tojikiston tarixi va madaniyati\n"
    "7. Sun'iy intellekt va texnologiya\n"
    "8. Umumiy bilim\n\n"
    "QOIDALAR:\n"
    "- Har doim O'ZBEK TILIDA (lotin) javob ber\n"
    "- Aniq, tushunarli va qisqa yoz\n"
    "- Misollar keltir\n"
    "- Bilmasang: 'Bu haqda aniq malumotim yoq' deb ayt"
)

# ============================================================
# 🤖 AI FUNKSIYALARI
# ============================================================
def ai_sorov(savol):
    if not OPENROUTER_KEY or OPENROUTER_KEY.startswith("BU_"):
        return None
    for model in AI_MODELS:
        data = {"model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": savol}],
                "temperature": 0.9, "max_tokens": 800}
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

def ai_hisobot():
    us, ls, qs, rs = stat_all()
    r = res_top(5)
    n = "TOP 5:\n"
    for i, x in enumerate(r, 1):
        n += f"{i}. {x[0]}: {x[1]}% ({x[2]} ta)\n"
    savol = (f"Malumot: {us} user, {ls} dars, {rs} natija\n{n}\n"
             f"3 gap bilan ustoz uchun tahlil yoz.")
    return ai_sorov(savol)

def ai_test_tahlil(uname, foiz):
    if foiz >= 90: holat = "Ajoyib!"
    elif foiz >= 70: holat = "Yaxshi!"
    elif foiz >= 50: holat = "O'rtacha."
    else: holat = "Qiyin."
    savol = (f"Oquvchi: {uname}\nTest: {foiz}%\nHolat: {holat}\n\n"
             f"1-2 gapda ustozga maslahat yoz.")
    return ai_sorov(savol)

def ai_darsdan_sorov(lesson_title, lesson_content, savol):
    prompt = (f"DARS:\n{lesson_title}\n{lesson_content[:1000]}\n\n"
              f"SAVOL: {savol}\n\nFaqat shu dars asosida javob ber.")
    return ai_sorov(prompt)

def ai_admin_xabar(matn):
    if not ADMIN_TG_ID or not BOT_TOKEN or BOT_TOKEN.startswith("BU_"):
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": ADMIN_TG_ID, "text": matn, "parse_mode": "Markdown"
        }).encode()
        urllib.request.urlopen(
            urllib.request.Request(url, data=data, method="POST"), timeout=10)
    except: pass

# ============================================================
# BAZA
# ============================================================
def db_init():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, password TEXT, role TEXT,
        full_name TEXT, tg_id INTEGER, sana TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, content TEXT, video TEXT,
        teacher TEXT, sana TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_id INTEGER, q TEXT, a TEXT, b TEXT,
        c TEXT, d TEXT, correct TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, lesson_id INTEGER, correct INTEGER,
        total INTEGER, percent INTEGER, sana TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, msg TEXT, vaqt TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, lesson_id INTEGER, stars INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY, username TEXT, vaqt TEXT)""")
    c.execute("SELECT COUNT(*) FROM users WHERE username=?", (ADMIN_USER,))
    if c.fetchone()[0] == 0:
        h = hashlib.sha256(ADMIN_PASS.encode()).hexdigest()
        c.execute("INSERT INTO users (username,password,role,full_name,tg_id,sana) "
                  "VALUES (?,?,?,?,?,?)",
                  (ADMIN_USER, h, "admin", ADMIN_NAME, ADMIN_TG_ID,
                   str(datetime.date.today())))
    conn.commit(); conn.close()

def hp(p): return hashlib.sha256(p.encode()).hexdigest()

def user_reg(u, p, role, fn, tg=None):
    conn = sqlite3.connect(DB); c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username,password,role,full_name,tg_id,sana) "
                  "VALUES (?,?,?,?,?,?)",
                  (u, hp(p), role, fn, tg, str(datetime.date.today())))
        conn.commit(); conn.close(); return True
    except: conn.close(); return False

def user_login(u, p):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT username,role,full_name FROM users "
              "WHERE username=? AND password=?", (u, hp(p)))
    r = c.fetchone(); conn.close(); return r

def user_info(u):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT username,role,full_name,tg_id FROM users WHERE username=?",
              (u,))
    r = c.fetchone(); conn.close(); return r

def user_tg(tg):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT username,role,full_name FROM users WHERE tg_id=?", (tg,))
    r = c.fetchone(); conn.close(); return r

def user_set_role(u, r):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("UPDATE users SET role=? WHERE username=?", (r, u))
    conn.commit(); conn.close()

def users_all():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT username,role,full_name,sana FROM users ORDER BY id")
    r = c.fetchall(); conn.close(); return r

def sess_new(u):
    t = secrets.token_hex(16)
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO sessions (token,username,vaqt) VALUES (?,?,?)",
              (t, u, datetime.datetime.now().isoformat()))
    conn.commit(); conn.close(); return t

def sess_get(t):
    if not t: return None
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT username FROM sessions WHERE token=?", (t,))
    r = c.fetchone(); conn.close(); return r[0] if r else None

def sess_del(t):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE token=?", (t,))
    conn.commit(); conn.close()

def lsn_add(title, content, video, teacher):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO lessons (title,content,video,teacher,sana) "
              "VALUES (?,?,?,?,?)",
              (title, content, video, teacher, str(datetime.date.today())))
    i = c.lastrowid; conn.commit(); conn.close(); return i

def lsn_list():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT id,title,teacher,sana,video FROM lessons ORDER BY id DESC")
    r = c.fetchall(); conn.close(); return r

def lsn_get(lid):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT id,title,content,video,teacher FROM lessons WHERE id=?",
              (lid,))
    l = c.fetchone()
    c.execute("SELECT id,q,a,b,c,d,correct FROM questions WHERE lesson_id=?",
              (lid,))
    q = c.fetchall(); conn.close(); return l, q

def lsn_del(lid):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("DELETE FROM lessons WHERE id=?", (lid,))
    c.execute("DELETE FROM questions WHERE lesson_id=?", (lid,))
    conn.commit(); conn.close()

def q_add(lid, q, a, b, cc, d, cor):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO questions (lesson_id,q,a,b,c,d,correct) "
              "VALUES (?,?,?,?,?,?,?)", (lid, q, a, b, cc, d, cor))
    conn.commit(); conn.close()

def res_add(u, lid, cor, tot):
    p = int(cor/tot*100) if tot else 0
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO results (username,lesson_id,correct,total,percent,sana) "
              "VALUES (?,?,?,?,?,?)",
              (u, lid, cor, tot, p, str(datetime.date.today())))
    conn.commit(); conn.close(); return p

def res_top(limit=10):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("""SELECT username, MAX(percent), COUNT(*), AVG(percent)
        FROM results GROUP BY username
        ORDER BY MAX(percent) DESC, AVG(percent) DESC LIMIT ?""", (limit,))
    r = c.fetchall(); conn.close(); return r

def res_user(u):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("""SELECT l.title, r.correct, r.total, r.percent, r.sana
        FROM results r JOIN lessons l ON l.id=r.lesson_id
        WHERE r.username=? ORDER BY r.id DESC""", (u,))
    r = c.fetchall(); conn.close(); return r

def stat_all():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users"); u = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM lessons"); l = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM questions"); q = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM results"); r = c.fetchone()[0]
    conn.close(); return u, l, q, r

def chat_add(u, m):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO chat (username,msg,vaqt) VALUES (?,?,?)",
              (u, m, datetime.datetime.now().strftime("%H:%M")))
    conn.commit(); conn.close()

def chat_list(n=30):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT username,msg,vaqt FROM chat ORDER BY id DESC LIMIT ?", (n,))
    r = c.fetchall(); conn.close(); return list(reversed(r))

def rat_add(u, lid, s):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("DELETE FROM ratings WHERE username=? AND lesson_id=?", (u, lid))
    c.execute("INSERT INTO ratings (username,lesson_id,stars) VALUES (?,?,?)",
              (u, lid, s))
    conn.commit(); conn.close()

def rat_avg(lid):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT AVG(stars), COUNT(*) FROM ratings WHERE lesson_id=?", (lid,))
    r = c.fetchone(); conn.close()
    return round(r[0], 1) if r[0] else 0, r[1]
# ============================================================
# TERMINAL REJIMI
# ============================================================
def term():
    G="\033[92m";Y="\033[93m";R="\033[91m";C="\033[96m";W="\033[97m";X="\033[0m"
    print(f"\n{W}{'='*50}{X}\n  🎓 BLIP LESSON PRO v7.0\n{W}{'='*50}{X}")
    u = input(f"{C}Username: {X}").strip()
    p = input(f"{C}Password: {X}").strip()
    info = user_login(u, p)
    if not info:
        print(f"{R}❌ Login xato!{X}"); return
    uname, role, fname = info
    print(f"{G}✅ Salom, {fname} ({role})!{X}")
    while True:
        us, ls, qs, rs = stat_all()
        print(f"\n{'='*50}\n  🎓 {fname} | {role.upper()}\n{'='*50}")
        print(f"  👥 {us} | 📚 {ls} | ❓ {qs} | 📊 {rs}")
        print("  [1] 📖 Darslar")
        if role in ("admin","teacher"): print("  [2] ➕ Dars qo'shish")
        print("  [3] 🎯 Test       [4] 🏆 Reyting")
        print("  [5] 💬 Chat       [6] ⭐ Baho")
        print("  [7] 📊 Mening natijalarim")
        print("  [12] 🤖 AI savol-javob")
        if role == "admin":
            print("  [8] 👥 Userlar   [9] 🗑 Dars o'chirish")
            print("  [10] 🎭 Rol     [11] 🤖 AI hisobot")
        print("  [0] 🚪 Chiqish")
        t = input(f"{Y}Tanla: {X}").strip()
        if t == "0": print(f"\n{G}👋{X}\n"); break
        elif t == "1":
            ds = lsn_list()
            if not ds: print("📭"); continue
            for x in ds:
                v = "🎬" if x[4] else "📝"
                b, cnt = rat_avg(x[0])
                print(f"  {v} {x[0]}. {x[1]} — {x[2]} {b}⭐({cnt})")
        elif t == "2" and role in ("admin","teacher"):
            title = input("Nomi: ").strip()
            if not title: continue
            content = input("Matn: ").strip()
            video = input("Video URL: ").strip()
            lid = lsn_add(title, content, video, uname)
            print(f"{G}✅ ID: {lid}{X}")
            while True:
                q = input("Savol (Enter=tugat): ").strip()
                if not q: break
                a = input("  A: ").strip(); b = input("  B: ").strip()
                cc = input("  C: ").strip(); d = input("  D: ").strip()
                cor = input("To'g'ri (A/B/C/D): ").strip().upper()
                q_add(lid, q, a, b, cc, d, cor)
        elif t == "3":
            ds = lsn_list()
            if not ds: continue
            for x in ds: print(f"  {x[0]}. {x[1]}")
            try: lid = int(input("ID: "))
            except: continue
            l, qs2 = lsn_get(lid)
            if not l or not qs2: print("📭"); continue
            print(f"\n{W}📖 {l[1]}{X}\n{l[2]}")
            if l[3]: print(f"{C}🎬 {l[3]}{X}")
            cor = 0
            for i, q in enumerate(qs2, 1):
                print(f"\n{C}{i}. {q[1]}{X}\n  A) {q[2]}\n  B) {q[3]}\n  C) {q[4]}\n  D) {q[5]}")
                a = input("Javob: ").strip().upper()
                if a == q[6]: print(f"{G}✅{X}"); cor += 1
                else: print(f"{R}❌ {q[6]}{X}")
            p = res_add(uname, lid, cor, len(qs2))
            print(f"\n{G}🎯 {cor}/{len(qs2)} ({p}%){X}")
            print(f"{Y}🤖 AI tahlil...{X}")
            tahlil = ai_test_tahlil(uname, p)
            if tahlil:
                print(f"\n{C}🤖 AI: {tahlil}{X}")
                ai_admin_xabar(f"📊 *Yangi natija*\n\n👤 {uname}\n"
                    f"🎯 {cor}/{len(qs2)} ({p}%)\n\n🤖 AI: {tahlil}")
        elif t == "4":
            r = res_top()
            if not r: print("📭"); continue
            print("\n🏆 TOP 10:")
            for i, x in enumerate(r, 1):
                m = ["🥇","🥈","🥉"][i-1] if i <= 3 else f"{i}."
                print(f"  {m} {x[0]}: {x[1]}% ({x[2]})")
        elif t == "5":
            for u2, m, v in chat_list(20): print(f"  [{v}] {u2}: {m}")
            msg = input("Xabar: ").strip()
            if msg: chat_add(uname, msg)
        elif t == "6":
            for x in lsn_list():
                b, cnt = rat_avg(x[0])
                print(f"  {x[0]}. {x[1]}: {b}⭐({cnt})")
            try: lid = int(input("ID: "))
            except: continue
            y = int(input("Yulduz (1-5): "))
            rat_add(uname, lid, y); print(f"{G}✅{X}")
        elif t == "7":
            ru = res_user(uname)
            if not ru: print("📭"); continue
            print(f"\n{W}📊 Mening natijalarim:{X}")
            for title, c, tot, p, s in ru:
                print(f"  {s} {title}: {c}/{tot} ({p}%)")
        elif t == "8" and role == "admin":
            for u2, r2, f2, s2 in users_all():
                print(f"  {u2} | {r2} | {f2} | {s2}")
        elif t == "9" and role == "admin":
            for x in lsn_list(): print(f"  {x[0]}. {x[1]}")
            try: lid = int(input("O'chirish ID: "))
            except: continue
            lsn_del(lid); print(f"{G}✅{X}")
        elif t == "10" and role == "admin":
            for u2, r2, f2, s2 in users_all(): print(f"  {u2} | {r2}")
            u2 = input("Username: ").strip()
            r2 = input("Yangi rol: ").strip()
            user_set_role(u2, r2); print(f"{G}✅{X}")
        elif t == "11" and role == "admin":
            print(f"{Y}🤖 AI hisobot...{X}")
            h = ai_hisobot()
            print(f"\n{W}🤖 AI:{X}\n{h}\n" if h else f"{R}❌{X}")
        elif t == "12":
            print(f"{Y}🤖 AI savol-javob (chiqish: exit){X}")
            while True:
                savol = input(f"{C}Savol: {X}").strip()
                if not savol or savol.lower() == "exit": break
                print(f"{Y}⏳...{X}")
                javob = ai_sorov(savol)
                print(f"\n{W}🤖 {javob or 'Javob yoq'}{X}\n")
        else: print(f"{R}❌{X}")
# ============================================================
# HTML — LOGIN
# ============================================================
LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Login</title><style>
body{font-family:sans-serif;background:#0a0e27;color:#eee;padding:20px;max-width:500px;margin:auto}
h1{color:#00BCD4;text-align:center;margin-top:60px}
.card{background:#1a1f3a;padding:30px;border-radius:14px;margin:20px 0;border-left:5px solid #00BCD4}
input{width:100%;padding:14px;border-radius:10px;border:1px solid #333;background:#0a0e27;color:#fff;font-size:16px;margin:8px 0;box-sizing:border-box}
.btn{background:#00BCD4;color:#000;border:none;padding:14px;border-radius:10px;font-size:16px;cursor:pointer;width:100%;font-weight:bold;margin-top:10px}
.btn2{background:#FF9800}
</style></head><body>
<h1>🎓 Blip Lesson PRO</h1>
<div class="card">
<form method="POST" action="/login">
<input name="u" placeholder="Username" required>
<input name="p" type="password" placeholder="Password" required>
<button class="btn" type="submit">🔐 Kirish</button>
</form>
<form method="POST" action="/register" style="margin-top:20px">
<input name="u" placeholder="Yangi username" required>
<input name="p" type="password" placeholder="Parol" required>
<input name="fn" placeholder="Toliq ism" required>
<button class="btn btn2" type="submit">📝 Ro'yxatdan o'tish</button>
</form></div></body></html>"""

# ============================================================
# HTML — ASOSIY
# ============================================================
MAIN_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Blip Lesson</title><style>
*{box-sizing:border-box}
body{font-family:sans-serif;background:#0a0e27;color:#eee;padding:20px;max-width:900px;margin:auto}
.hdr{display:flex;justify-content:space-between;align-items:center;background:#1a1f3a;padding:12px 20px;border-radius:10px;margin-bottom:15px;flex-wrap:wrap;gap:10px}
.hdr b{color:#00BCD4}
.btn{background:#00BCD4;color:#000;border:none;padding:10px 16px;border-radius:8px;font-size:15px;cursor:pointer;font-weight:bold;margin:3px}
.btn2{background:#FF9800}.btn3{background:#f44336;color:#fff}
.card{background:#1a1f3a;padding:20px;border-radius:14px;margin:12px 0;border-left:5px solid #00BCD4}
input,textarea{width:100%;padding:12px;border-radius:8px;border:1px solid #333;background:#0a0e27;color:#fff;font-size:15px;margin:5px 0;box-sizing:border-box;font-family:inherit}
.dars{background:#0a0e27;padding:15px;border-radius:10px;margin:8px 0;cursor:pointer;border-left:3px solid #00BCD4}
.stat{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.stat div{background:#1a1f3a;padding:15px;border-radius:10px;text-align:center}
.stat b{display:block;font-size:24px;color:#00BCD4}
.rey{background:#0a0e27;padding:10px;border-radius:8px;margin:5px 0}
.chat{background:#0a0e27;padding:10px;border-radius:8px;max-height:300px;overflow-y:auto}
.msg{padding:8px;margin:4px 0;background:#1a1f3a;border-radius:8px}
.msg b{color:#00BCD4}
.star{color:#FFD700}
.tabs{display:flex;gap:5px;margin-bottom:10px;flex-wrap:wrap}
.tabs button{flex:1;padding:10px;border:none;border-radius:8px;background:#1a1f3a;color:#eee;cursor:pointer;font-weight:bold;min-width:90px}
.tabs button.on{background:#00BCD4;color:#000}
.ai{background:#0f1a3a;border-left:5px solid #FF9800;padding:15px;border-radius:10px;margin:10px 0}
</style></head><body>
<div class="hdr">
<div>🎓 <b>Blip Lesson PRO</b></div>
<div id="user">...</div>
<button class="btn btn3" onclick="lo()">Chiqish</button>
</div>
<div class="tabs">
<button class="on" onclick="tb('darslar',this)">📚 Darslar</button>
<button onclick="tb('rey',this)">🏆 TOP</button>
<button onclick="tb('chat',this)">💬 Chat</button>
<button onclick="tb('mstat',this)">📊 Mening</button>
<button onclick="tb('aiTab',this)">🤖 AI</button>
<button id="tbadm" onclick="tb('adm',this)" style="display:none">👑 Admin</button>
</div>
<div id="darslar" class="tab">
<div class="stat" id="st">...</div>
<div class="card"><h3>📚 Darslar</h3><div id="dl">...</div></div>
<div class="card" id="dqc" style="display:none"><h3>➕ Yangi dars</h3>
<input id="dt" placeholder="Nomi">
<textarea id="dc" placeholder="Matn" rows="3"></textarea>
<input id="dv" placeholder="Video URL">
<button class="btn" onclick="dq()">Saqlash</button></div>
</div>
<div id="rey" class="tab" style="display:none">
<div class="card"><h3>🏆 TOP 10</h3><div id="rt">...</div></div>
</div>
<div id="chat" class="tab" style="display:none">
<div class="card"><h3>💬 Chat</h3>
<div class="chat" id="ch"></div>
<input id="cm" placeholder="Xabar...">
<button class="btn" onclick="cs()">📤 Yuborish</button></div>
</div>
<div id="mstat" class="tab" style="display:none">
<div class="card"><h3>📊 Mening natijalarim</h3><div id="ms">...</div></div>
</div>
<div id="aiTab" class="tab" style="display:none">
<div class="card"><h3>🤖 AI Yordamchi</h3>
<p>Savol bering — AI o'zbek tilida javob beradi!</p>
<textarea id="aiQ" placeholder="Savolingizni yozing..." rows="3"></textarea>
<button class="btn" onclick="aiAsk()">🤖 So'rash</button>
<div id="aiA" class="ai" style="display:none"></div></div>
</div>
<div id="adm" class="tab" style="display:none">
<div class="card"><h3>👑 Admin panel</h3>
<button class="btn btn2" onclick="aiH()">🤖 AI hisobot</button>
<div id="aiR" class="ai" style="display:none"></div></div>
</div>
<script>
function tb(id,btn){
 document.querySelectorAll('.tab').forEach(e=>e.style.display='none');
 document.getElementById(id).style.display='block';
 document.querySelectorAll('.tabs button').forEach(e=>e.classList.remove('on'));
 btn.classList.add('on');
}
function lo(){fetch('/api/logout').then(()=>location.href='/');}
function yk(){
 fetch('/api/me').then(r=>r.json()).then(d=>{
  if(d.err){location.href='/';return;}
  document.getElementById('user').innerHTML='👤 <b>'+d.fname+'</b> ('+d.role+')';
  if(d.role==='admin'||d.role==='teacher'){document.getElementById('dqc').style.display='block';}
  if(d.role==='admin'){document.getElementById('tbadm').style.display='block';}
 });
 fetch('/api/stat').then(r=>r.json()).then(d=>{
  document.getElementById('st').innerHTML='<div><b>'+d.u+'</b>👥</div><div><b>'+d.l+'</b>📚</div><div><b>'+d.q+'</b>❓</div><div><b>'+d.r+'</b>📊</div>';
 });
 fetch('/api/lessons').then(r=>r.json()).then(d=>{
  let h='';d.forEach(x=>{let v=x.video?'🎬':'📝';
   let st='';for(let i=0;i<5;i++)st+=i<x.baho?'⭐':'☆';
   h+='<div class="dars" onclick="och('+x.id+')">'+v+' <b>'+x.title+'</b> <span class="star">'+st+'</span><br><small>👨‍🏫 '+x.teacher+' • '+x.sana+'</small></div>'});
  if(!d.length)h='📭';document.getElementById('dl').innerHTML=h;});
 fetch('/api/top').then(r=>r.json()).then(d=>{
  let h='';d.forEach((x,i)=>{let m=['🥇','🥈','🥉'][i]||(i+1)+'.';
   h+='<div class="rey">'+m+' <b>'+x.username+'</b> — '+x.mx+'% ('+x.cnt+')</div>'});
  if(!d.length)h='📭';document.getElementById('rt').innerHTML=h;});
 fetch('/api/chat').then(r=>r.json()).then(d=>{
  let h='';d.forEach(x=>{h+='<div class="msg"><b>'+x.username+'</b> <small>'+x.vaqt+'</small><br>'+x.msg+'</div>'});
  let c=document.getElementById('ch');c.innerHTML=h;c.scrollTop=c.scrollHeight;});
 fetch('/api/my').then(r=>r.json()).then(d=>{
  let h='';d.forEach(x=>{h+='<div class="rey">'+x.title+': '+x.correct+'/'+x.total+' ('+x.percent+'%)</div>'});
  if(!d.length)h='📭';document.getElementById('ms').innerHTML=h;});
}
function och(id){location.href='/lesson/'+id;}
function dq(){
 let t=document.getElementById('dt').value;
 let c=document.getElementById('dc').value;
 let v=document.getElementById('dv').value;
 if(!t)return alert('Nom kerak!');
 fetch('/api/lesson_add',{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({title:t,content:c,video:v})}).then(r=>r.json()).then(d=>{
   if(d.id){alert('✅ Dars ID: '+d.id);location.reload();}
   else alert('❌');
  });
}
function cs(){
 let m=document.getElementById('cm').value;if(!m)return;
 fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({msg:m})}).then(r=>r.text()).then(t=>{
   document.getElementById('cm').value='';yk();});
}
function aiAsk(){
 let q=document.getElementById('aiQ').value;if(!q)return;
 let a=document.getElementById('aiA');a.style.display='block';
 a.innerHTML='⏳ AI o\\'ylayapti...';
 fetch('/api/ai_ask?q='+encodeURIComponent(q)).then(r=>r.json()).then(d=>{
  a.innerHTML='<b>🤖 AI:</b><br>'+d.matn.replace(/\\n/g,'<br>');
 });
}
function aiH(){
 let r=document.getElementById('aiR');
 r.style.display='block';r.innerHTML='⏳ AI tahlil...';
 fetch('/api/ai_report').then(r=>r.json()).then(d=>{
  r.innerHTML='<b>🤖 AI HISOBOT:</b><br>'+d.matn.replace(/\\n/g,'<br>');
 });
}
yk();setInterval(yk,8000);
</script></body></html>"""
# ============================================================
# HTML — DARS
# ============================================================
LESSON_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dars</title><style>
body{font-family:sans-serif;background:#0a0e27;color:#eee;padding:20px;max-width:800px;margin:auto}
h1{color:#00BCD4}
.card{background:#1a1f3a;padding:22px;border-radius:14px;margin:12px 0;border-left:5px solid #00BCD4}
.btn{background:#00BCD4;color:#000;border:none;padding:14px;border-radius:10px;font-size:16px;cursor:pointer;width:100%;font-weight:bold;margin:5px 0}
input,textarea{width:100%;padding:12px;border-radius:8px;border:1px solid #333;background:#0a0e27;color:#fff;font-size:15px;margin:5px 0;box-sizing:border-box}
.savol{margin:15px 0;padding:15px;background:#0a0e27;border-radius:10px}
.v{display:block;padding:10px;margin:5px 0;background:#1a1f3a;border-radius:8px;cursor:pointer}
.v input{margin-right:8px;width:auto}
iframe,video{width:100%;border-radius:10px;margin:10px 0}
.star{font-size:36px;cursor:pointer;color:#444}
.star.on{color:#FFD700}
a{color:#4DD0E1}
.ai{background:#0f1a3a;border-left:5px solid #FF9800;padding:15px;border-radius:10px;margin:10px 0}
</style></head><body>
<a href="/">← Orqaga</a>
<h1 id="nm">...</h1>
<div id="vd"></div>
<div class="card"><div id="mt">...</div></div>
<div class="card"><h3>⭐ Baholang:</h3>
<span class="star" onclick="bh(1)">★</span>
<span class="star" onclick="bh(2)">★</span>
<span class="star" onclick="bh(3)">★</span>
<span class="star" onclick="bh(4)">★</span>
<span class="star" onclick="bh(5)">★</span>
<span id="bm"></span></div>
<div class="card"><h3>🤖 AI dan so'rash</h3>
<textarea id="aiQ" placeholder="Shu dars bo'yicha savol..." rows="2"></textarea>
<button class="btn" onclick="aiAsk()">🤖 So'rash</button>
<div id="aiA" class="ai" style="display:none"></div></div>
<form id="f">
<div id="sv"></div>
<button type="submit" class="btn">🎯 Yuborish</button></form>
<script>
const id=location.pathname.split('/').pop();
function bh(y){
 fetch('/api/rate?id='+id+'&y='+y).then(r=>r.text()).then(t=>{
  document.querySelectorAll('.star').forEach((el,i)=>el.classList.toggle('on',i<y));
  document.getElementById('bm').innerText=' ✅';
 });
}
function aiAsk(){
 let q=document.getElementById('aiQ').value;if(!q)return;
 let a=document.getElementById('aiA');a.style.display='block';
 a.innerHTML='⏳ AI...';
 fetch('/api/ai_ask?lid='+id+'&q='+encodeURIComponent(q)).then(r=>r.json()).then(d=>{
  a.innerHTML='<b>🤖 AI:</b><br>'+d.matn.replace(/\\n/g,'<br>');
 });
}
fetch('/api/lesson/'+id).then(r=>r.json()).then(d=>{
 document.getElementById('nm').innerText='📖 '+d.title;
 document.getElementById('mt').innerText=d.content;
 if(d.video){
  let v='';
  if(d.video.includes('youtu')){
   let vid=d.video.split('v=').pop().split('&')[0].split('/').pop();
   v='<iframe height="400" src="https://www.youtube.com/embed/'+vid+'" allowfullscreen></iframe>';
  } else v='<video controls src="'+d.video+'"></video>';
  document.getElementById('vd').innerHTML=v;
 }
 let h='';
 d.questions.forEach((s,i)=>{
  h+='<div class="savol"><p><b>'+(i+1)+'. '+s.q+'</b></p>';
  ['a','b','c','d'].forEach(k=>{
   h+='<label class="v"><input type="radio" name="s'+i+'" value="'+k+'" required> '+s[k]+'</label>';
  });h+='</div>';
 });
 document.getElementById('sv').innerHTML=h;
 document.getElementById('f').onsubmit=e=>{
  e.preventDefault();
  let j=[];d.questions.forEach((s,i)=>{
   let v=document.querySelector('input[name="s'+i+'"]:checked');
   j.push(v?v.value:'');
  });
  fetch('/api/submit?id='+id+'&j='+j.join(',')).then(r=>r.json()).then(d=>{
   let s=d.percent>=70?'\\n\\n🎓 SERTIFIKAT!':'';
   let ai=d.ai?'\\n\\n🤖 AI: '+d.ai:'';
   alert('🎯 '+d.correct+'/'+d.total+' ('+d.percent+'%)'+s+ai);
   location.href='/';
  });
 };
});
</script></body></html>"""

# ============================================================
# HTTP HANDLER
# ============================================================
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _cookie(self):
        c = self.headers.get("Cookie","")
        for p in c.split(";"):
            if "=" in p:
                k,v = p.strip().split("=",1)
                if k == "sess": return v
        return None
    def _me(self): return sess_get(self._cookie())
    def do_GET(self):
        p = self.path.split("?")[0]
        tok = self._cookie(); uname = sess_get(tok)
        if p in ("/","/index.html"):
            self._h(LOGIN_HTML if not uname else MAIN_HTML); return
        if p == "/logout":
            sess_del(tok); self.send_response(302)
            self.send_header("Location","/"); self.end_headers(); return
        if not uname:
            self.send_response(302)
            self.send_header("Location","/"); self.end_headers(); return
        if p.startswith("/lesson/"): self._h(LESSON_HTML); return
        if p == "/api/me":
            i = user_info(uname)
            self._j({"username":i[0],"role":i[1],"fname":i[2]})
        elif p == "/api/stat":
            u,l,q,r = stat_all(); self._j({"u":u,"l":l,"q":q,"r":r})
        elif p == "/api/lessons":
            ds = []
            for x in lsn_list():
                b,_ = rat_avg(x[0])
                ds.append({"id":x[0],"title":x[1],"teacher":x[2],
                           "sana":x[3],"video":x[4],"baho":int(b)})
            self._j(ds)
        elif p == "/api/top":
            self._j([{"username":x[0],"mx":x[1],"cnt":x[2]} for x in res_top()])
        elif p == "/api/chat":
            self._j([{"username":x[0],"msg":x[1],"vaqt":x[2]} for x in chat_list(30)])
        elif p == "/api/my":
            self._j([{"title":x[0],"correct":x[1],"total":x[2],"percent":x[3]}
                     for x in res_user(uname)])
        elif p == "/api/ai_report":
            i = user_info(uname)
            if i[1] != "admin": self._j({"matn":"Ruxsat yo'q"}); return
            h = ai_hisobot(); self._j({"matn": h if h else "AI javob bermadi"})
        elif p.startswith("/api/ai_ask"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            savol = q.get("q",[""])[0]
            lid = int(q.get("lid",[0])[0])
            if lid:
                l, _ = lsn_get(lid)
                javob = ai_darsdan_sorov(l[1], l[2], savol) if l else None
            else:
                javob = ai_sorov(savol)
            self._j({"matn": javob or "AI javob bermadi"})
        elif p.startswith("/api/lesson/"):
            lid = int(p.split("/")[-1])
            l, qs = lsn_get(lid)
            if not l: self._j({}); return
            self._j({"title":l[1],"content":l[2],"video":l[3],
                     "questions":[{"q":x[1],"a":x[2],"b":x[3],"c":x[4],"d":x[5]}
                                  for x in qs]})
        elif p.startswith("/api/rate"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            rat_add(uname, int(q.get("id",[0])[0]), int(q.get("y",[5])[0]))
            self._t("OK")
        elif p.startswith("/api/submit"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            lid = int(q.get("id",[0])[0])
            jv = q.get("j",[""])[0].split(",")
            l, qs = lsn_get(lid)
            cor = 0
            for i, qu in enumerate(qs):
                if i < len(jv) and jv[i].upper() == qu[6]: cor += 1
            pc = res_add(uname, lid, cor, len(qs))
            tahlil = ai_test_tahlil(uname, pc)
            ai_admin_xabar(f"📊 *Yangi natija*\n\n👤 {uname}\n"
                f"🎯 {cor}/{len(qs)} ({pc}%)\n\n🤖 AI: {tahlil or '—'}")
            self._j({"correct":cor,"total":len(qs),"percent":pc,"ai":tahlil or ""})
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length",0))
        body = self.rfile.read(n).decode()
        if self.path == "/login":
            q = urllib.parse.parse_qs(body)
            info = user_login(q.get("u",[""])[0], q.get("p",[""])[0])
            if info:
                t = sess_new(info[0])
                self.send_response(302)
                self.send_header("Set-Cookie", f"sess={t}; Path=/")
                self.send_header("Location","/"); self.end_headers()
            else:
                self.send_response(302); self.send_header("Location","/")
                self.end_headers()
        elif self.path == "/register":
            q = urllib.parse.parse_qs(body)
            u = q.get("u",[""])[0]; p = q.get("p",[""])[0]
            fn = q.get("fn",[""])[0]
            if user_reg(u, p, "student", fn):
                t = sess_new(u)
                self.send_response(302)
                self.send_header("Set-Cookie", f"sess={t}; Path=/")
                self.send_header("Location","/"); self.end_headers()
            else:
                self.send_response(302); self.send_header("Location","/")
                self.end_headers()
        elif self.path == "/api/chat":
            uname = self._me()
            if not uname: self._t(""); return
            d = json.loads(body); chat_add(uname, d.get("msg","")); self._t("OK")
        elif self.path == "/api/lesson_add":
            uname = self._me()
            info = user_info(uname) if uname else None
            if not info or info[1] not in ("admin","teacher"):
                self._t(""); return
            d = json.loads(body)
            lid = lsn_add(d.get("title",""), d.get("content",""),
                          d.get("video",""), uname)
            self._j({"id":lid})
        else: self.send_response(404); self.end_headers()
    def _j(self,m):
        self.send_response(200)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(m,ensure_ascii=False).encode())
    def _h(self,m):
        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.end_headers(); self.wfile.write(m.encode())
    def _t(self,m):
        self.send_response(200)
        self.send_header("Content-Type","text/plain; charset=utf-8")
        self.end_headers(); self.wfile.write(m.encode())

def web():
    print(f"\n🌐 http://127.0.0.1:{PORT}")
    print(f"🔐 Admin: {ADMIN_USER} / {ADMIN_PASS}")
    print(f"📁 {DB}\n⛔ Ctrl+C\n")
    try: HTTPServer(("0.0.0.0",PORT),H).serve_forever()
    except KeyboardInterrupt: print("\n👋")
    except Exception as e: print(f"❌ {e}")
# ============================================================
# TELEGRAM BOT
# ============================================================
def tg_mode():
    try:
        import telebot
        from telebot import types
    except ImportError:
        print("❌ pip install pyTelegramBotAPI")
        return
    if BOT_TOKEN.startswith("BU_"):
        print("❌ BOT_TOKEN!")
        return
    bot = telebot.TeleBot(BOT_TOKEN)
    k = {}

    def reg_check(m):
        u = user_tg(m.from_user.id)
        if not u:
            bot.send_message(m.chat.id, "❌ /reg username parol ism")
            return None
        return u

    @bot.message_handler(commands=["start"])
    def s(m):
        bot.send_message(m.chat.id,
            "🎓 Blip Lesson PRO v7.0\n\n"
            "📋 BUYRUQLAR:\n"
            "/reg - Royxatdan otish\n"
            "/login - Kirish\n"
            "/darslar - Darslar\n"
            "/test - Test\n"
            "/top - Reyting\n"
            "/chat - Chat\n"
            "/profil - Profil\n"
            "/mening - Natijalarim\n"
            "/ai savol - AI savol\n"
            "/test_yarat mavzu - AI test\n"
            "/qosh - Dars qoshish\n"
            "/tugat - Tugatish\n"
            "/help - Yordam\n\n"
            "🤖 Shunchaki yozing - AI javob beradi!")

    @bot.message_handler(commands=["help"])
    def h(m):
        bot.send_message(m.chat.id,
            "📖 Yordam\n\n"
            "1. /reg ism parol Ism\n"
            "2. /login ism parol\n"
            "3. /darslar - darslar\n"
            "4. /test - test\n"
            "5. /test_yarat mavzu\n"
            "6. /qosh - dars qoshish\n"
            "7. /ai savol - AI savol\n"
            "8. Yozing - AI javob beradi!")

    @bot.message_handler(commands=["reg"])
    def rg(m):
        p = m.text.split()
        if len(p) < 4:
            bot.send_message(m.chat.id, "❌ /reg ism parol Ism")
            return
        if user_reg(p[1], p[2], "student", " ".join(p[3:]), m.from_user.id):
            bot.send_message(m.chat.id, f"✅ {p[1]} royxatdan otdi")
        else:
            bot.send_message(m.chat.id, "❌ Band username!")

    @bot.message_handler(commands=["login"])
    def lg(m):
        p = m.text.split()
        if len(p) < 3:
            bot.send_message(m.chat.id, "❌ /login ism parol")
            return
        info = user_login(p[1], p[2])
        if info:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("UPDATE users SET tg_id=? WHERE username=?",
                      (m.from_user.id, p[1]))
            conn.commit()
            conn.close()
            bot.send_message(m.chat.id, f"✅ {info[2]} ({info[1]})")
        else:
            bot.send_message(m.chat.id, "❌ Login xato!")

    @bot.message_handler(commands=["darslar"])
    def d(m):
        if not reg_check(m):
            return
        ds = lsn_list()
        if not ds:
            bot.send_message(m.chat.id, "📭 Darslar yoq")
            return
        kb = types.InlineKeyboardMarkup()
        for x in ds:
            v = "🎬" if x[4] else "📝"
            b, _ = rat_avg(x[0])
            kb.add(types.InlineKeyboardButton(
                text=f"{v} {x[1]} {'⭐'*int(b)}", callback_data=f"d:{x[0]}"))
        bot.send_message(m.chat.id, "📚 Darslar:", reply_markup=kb)

    @bot.message_handler(commands=["top"])
    def tp(m):
        r = res_top()
        if not r:
            bot.send_message(m.chat.id, "📭")
            return
        t = "🏆 TOP 10:\n\n"
        for i, x in enumerate(r, 1):
            me = ["🥇","🥈","🥉"][i-1] if i <= 3 else f"{i}."
            t += f"{me} {x[0]}: {x[1]}% ({x[2]})\n"
        bot.send_message(m.chat.id, t)

    @bot.message_handler(commands=["mening"])
    def mn(m):
        u = reg_check(m)
        if not u:
            return
        ru = res_user(u[0])
        if not ru:
            bot.send_message(m.chat.id, "📭")
            return
        t = "📊 Natijalarim:\n\n"
        for title, c, tot, p, s in ru[:10]:
            t += f"• {title}: {c}/{tot} ({p}%)\n"
        bot.send_message(m.chat.id, t)

    @bot.message_handler(commands=["profil"])
    def pf(m):
        u = reg_check(m)
        if not u:
            return
        bot.send_message(m.chat.id,
            f"👤 Profil\n\nUsername: {u[0]}\nIsm: {u[2]}\nRol: {u[1]}")

    @bot.message_handler(commands=["chat"])
    def ch(m):
        u = reg_check(m)
        if not u:
            return
        t = "💬 Chat:\n\n"
        for u2, mm, v in chat_list(15):
            t += f"[{v}] {u2}: {mm}\n"
        bot.send_message(m.chat.id, t)
        k[m.chat.id] = {"h": "chat"}
        bot.send_message(m.chat.id, "✍️ Xabar:")

    @bot.message_handler(commands=["test"])
    def ts(m):
        u = reg_check(m)
        if not u:
            return
        ds = lsn_list()
        if not ds:
            bot.send_message(m.chat.id, "📭")
            return
        kb = types.InlineKeyboardMarkup()
        for x in ds:
            kb.add(types.InlineKeyboardButton(text=f"🎯 {x[1]}",
                                              callback_data=f"t:{x[0]}"))
        bot.send_message(m.chat.id, "Test uchun dars:", reply_markup=kb)

    @bot.message_handler(commands=["ai"])
    def ai_cmd(m):
        u = reg_check(m)
        if not u:
            return
        savol = m.text.replace("/ai", "").strip()
        if not savol:
            bot.send_message(m.chat.id, "❌ /ai savol...")
            return
        bot.send_message(m.chat.id, "⏳ AI...")
        javob = ai_sorov(savol)
        bot.send_message(m.chat.id, f"🤖 {javob or 'Javob yoq'}")

    @bot.message_handler(commands=["test_yarat"])
    def test_yarat(m):
        u = user_tg(m.from_user.id)
        if not u or u[1] not in ("admin", "teacher"):
            bot.send_message(m.chat.id, "❌ Faqat admin/ustoz!")
            return
        mavzu = m.text.replace("/test_yarat", "").strip()
        if not mavzu:
            bot.send_message(m.chat.id, "❌ /test_yarat mavzu")
            return
        bot.send_message(m.chat.id, f"⏳ AI {mavzu} savollar tayyorlayapti...")
        prompt = (
            f"'{mavzu}' mavzusida 3 ta test savoli tayyorla.\n\n"
            f"HAR BIR SAVOL FORMATI:\n\n"
            f"SAVOL: savol matni?\n"
            f"A) birinchi variant\n"
            f"B) ikkinchi variant\n"
            f"C) uchinchi variant\n"
            f"D) tortinchi variant\n"
            f"JAVOB: A\n"
            f"---\n\n"
            f"Faqat shu formatda yoz."
        )
        javob = ai_sorov(prompt)
        if not javob:
            bot.send_message(m.chat.id, "❌ AI javob bermadi")
            return
        k[m.chat.id] = {"h": "ai_test", "mavzu": mavzu, "ai_matn": javob}
        if len(javob) > 4000:
            for i in range(0, len(javob), 4000):
                bot.send_message(m.chat.id, javob[i:i+4000])
        else:
            bot.send_message(m.chat.id, f"🤖 AI tayyorladi:\n\n{javob}")
        bot.send_message(m.chat.id, f"\n📝 Saqlash: /saqla {mavzu}")

    @bot.message_handler(commands=["saqla"])
    def saqla(m):
        u = user_tg(m.from_user.id)
        if not u or u[1] not in ("admin", "teacher"):
            bot.send_message(m.chat.id, "❌ Faqat admin/ustoz!")
            return
        st = k.get(m.chat.id, {})
        if st.get("h") != "ai_test":
            bot.send_message(m.chat.id, "❌ Avval /test_yarat")
            return
        nomi = m.text.replace("/saqla", "").strip() or st.get("mavzu", "AI test")
        lid = lsn_add(nomi, f"AI yaratgan test: {st['mavzu']}", "", u[0])
        savollar = st["ai_matn"].split("---")
        q_soni = 0
        for sv in savollar:
            sv = sv.strip()
            if not sv:
                continue
            lines = [l.strip() for l in sv.split("\n") if l.strip()]
            savol = ""
            a = b_ = cc = d = ""
            cor = ""
            for l in lines:
                lu = l.upper()
                if lu.startswith("SAVOL:"):
                    savol = l.split(":", 1)[1].strip()
                elif l.startswith("A)") or l.startswith("A."):
                    a = l[2:].strip()
                elif l.startswith("B)") or l.startswith("B."):
                    b_ = l[2:].strip()
                elif l.startswith("C)") or l.startswith("C."):
                    cc = l[2:].strip()
                elif l.startswith("D)") or l.startswith("D."):
                    d = l[2:].strip()
                elif lu.startswith("JAVOB"):
                    cor = l.split(":", 1)[1].strip().upper()
            if savol and a and b_ and cc and d and cor in ("A", "B", "C", "D"):
                q_add(lid, savol, a, b_, cc, d, cor)
                q_soni += 1
        k.pop(m.chat.id, None)
        bot.send_message(m.chat.id,
            f"✅ Dars saqlandi!\n\n📖 {nomi}\n🆔 ID: {lid}\n❓ Savollar: {q_soni} ta")

    @bot.message_handler(commands=["qosh"])
    def cmd_qosh(m):
        u = user_tg(m.from_user.id)
        if not u or u[1] not in ("admin", "teacher"):
            bot.send_message(m.chat.id, "❌ Faqat admin/ustoz!")
            return
        k[m.chat.id] = {"h": "q_nomi"}
        bot.send_message(m.chat.id, "📖 Dars nomini yozing:\n(Bekor: /cancel)")

    @bot.message_handler(commands=["cancel"])
    def cmd_cancel(m):
        if m.chat.id in k:
            k.pop(m.chat.id, None)
            bot.send_message(m.chat.id, "⏹ Bekor qilindi.")

    @bot.message_handler(commands=["tugat"])
    def cmd_tugat(m):
        st = k.get(m.chat.id, {})
        if st.get("h") == "q_savol":
            bot.send_message(m.chat.id,
                f"✅ Dars tayyor! ID: {st.get('lid')}\n"
                f"Savollar: {st.get('savol', 0)} ta")
            k.pop(m.chat.id, None)
        else:
            bot.send_message(m.chat.id, "❌ Savol kutilmayapti")

    @bot.callback_query_handler(func=lambda c: True)
    def cb(c):
        u = user_tg(c.from_user.id)
        if not u:
            bot.answer_callback_query(c.id, "❌ /reg qiling!")
            return
        if c.data.startswith("d:"):
            lid = int(c.data.split(":")[1])
            l, qs = lsn_get(lid)
            if not l:
                return
            t = f"📖 {l[1]}\n\n{l[2]}"
            if l[3]:
                t += f"\n\n🎬 {l[3]}"
            bot.send_message(c.message.chat.id, t)
        elif c.data.startswith("t:"):
            lid = int(c.data.split(":")[1])
            l, qs = lsn_get(lid)
            if not qs:
                bot.send_message(c.message.chat.id, "📭")
                return
            k[c.message.chat.id] = {"h": "test", "lid": lid, "i": 0, "c": 0, "u": u[0]}
            sy(bot, c.message.chat.id, qs, 0, k)
        elif c.data.startswith("j:"):
            _, cor, tv = c.data.split(":")
            st = k.get(c.message.chat.id)
            if not st:
                return
            if tv == cor:
                st["c"] = st.get("c", 0) + 1
                bot.answer_callback_query(c.id, "✅")
            else:
                bot.answer_callback_query(c.id, f"❌ {cor}")
            st["i"] += 1
            l, qs = lsn_get(st["lid"])
            sy(bot, c.message.chat.id, qs, st["i"], k)

    def sy(bot, chat, qs, i, k):
        if i >= len(qs):
            st = k.get(chat, {})
            c = st.get("c", 0)
            tot = len(qs)
            p = res_add(st.get("u", "A"), st.get("lid", 0), c, tot)
            sf = "\n\n🎓 SERTIFIKAT!" if p >= 70 else ""
            tahlil = ai_test_tahlil(st.get("u", "A"), p)
            ai_admin_xabar(f"📊 Natija\n\n👤 {st.get('u', 'A')}\n"
                f"🎯 {c}/{tot} ({p}%)\n\n🤖 AI: {tahlil or '-'}")
            msg = f"🎯 {c}/{tot} ({p}%){sf}"
            if tahlil:
                msg += f"\n\n🤖 AI: {tahlil}"
            bot.send_message(chat, msg)
            k.pop(chat, None)
            return
        q = qs[i]
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("A) " + q[2], callback_data=f"j:{q[6]}:A"))
        kb.add(types.InlineKeyboardButton("B) " + q[3], callback_data=f"j:{q[6]}:B"))
        kb.add(types.InlineKeyboardButton("C) " + q[4], callback_data=f"j:{q[6]}:C"))
        kb.add(types.InlineKeyboardButton("D) " + q[5], callback_data=f"j:{q[6]}:D"))
        bot.send_message(chat, f"❓ {i+1}/{len(qs)}\n\n{q[1]}",
                         reply_markup=kb)

    @bot.message_handler(func=lambda m: m.chat.id in k, content_types=["text"])
    def mt(m):
        st = k.get(m.chat.id, {})
        h = st.get("h")
        if h == "chat":
            u = user_tg(m.from_user.id)
            if u:
                chat_add(u[0], m.text)
            k.pop(m.chat.id, None)
            bot.send_message(m.chat.id, "✅")
        elif h == "q_nomi":
            st["nomi"] = m.text
            st["h"] = "q_matn"
            bot.send_message(m.chat.id, "📝 Dars matnini yozing:")
        elif h == "q_matn":
            st["matn"] = m.text
            st["h"] = "q_video"
            bot.send_message(m.chat.id, "🎬 Video URL (Enter=yoq):")
        elif h == "q_video":
            video = m.text.strip()
            if video in ("yoq", "-", ""):
                video = ""
            u = user_tg(m.from_user.id)
            lid = lsn_add(st["nomi"], st["matn"], video, u[0])
            st["lid"] = lid
            st["h"] = "q_savol"
            st["savol"] = 0
            bot.send_message(m.chat.id,
                f"✅ Dars ID: {lid}\n\n"
                f"Endi savollarni yozing:\n\n"
                f"Savol?\nA) ...\nB) ...\nC) ...\nD) ...\nJavob: A\n\n"
                f"Tugatish: /tugat")
        elif h == "q_savol":
            lines = [l.strip() for l in m.text.strip().split("\n") if l.strip()]
            try:
                savol = lines[0]
                a = b_ = cc = d = ""
                cor = ""
                for l in lines[1:]:
                    if l.startswith("A)") or l.startswith("A."):
                        a = l[2:].strip()
                    elif l.startswith("B)") or l.startswith("B."):
                        b_ = l[2:].strip()
                    elif l.startswith("C)") or l.startswith("C."):
                        cc = l[2:].strip()
                    elif l.startswith("D)") or l.startswith("D."):
                        d = l[2:].strip()
                    elif l.lower().startswith("javob"):
                        cor = l.split(":", 1)[1].strip().upper()
                if not (a and b_ and cc and d and cor in ("A", "B", "C", "D")):
                    bot.send_message(m.chat.id,
                        "❌ Format xato! Togri:\n"
                        "Savol?\nA) ...\nB) ...\nC) ...\nD) ...\nJavob: A")
                    return
                q_add(st["lid"], savol, a, b_, cc, d, cor)
                st["savol"] = st.get("savol", 0) + 1
                bot.send_message(m.chat.id,
                    f"✅ Savol {st['savol']} qoshildi!\n\nYana savol yoki /tugat")
            except Exception as e:
                bot.send_message(m.chat.id, f"❌ Xato: {e}")

    @bot.message_handler(content_types=["text"],
                         func=lambda m: m.chat.id not in k
                                       and not m.text.startswith("/"))
    def ai_auto(m):
        u = user_tg(m.from_user.id)
        if not u:
            return
        bot.send_chat_action(m.chat.id, "typing")
        javob = ai_sorov(m.text)
        if javob:
            if len(javob) > 4000:
                for i in range(0, len(javob), 4000):
                    bot.send_message(m.chat.id, javob[i:i+4000])
            else:
                bot.send_message(m.chat.id, f"🤖 {javob}")

    print("\n🤖 /start\n⛔ Ctrl+C\n")
    try:
        bot.infinity_polling(timeout=30)
    except KeyboardInterrupt:
        print("\n👋")


# ============================================================
# MENYU + ASOSIY
# ============================================================
def menyu():
    while True:
        us, ls, qs, rs = stat_all()
        ai_h = "✅" if OPENROUTER_KEY and not OPENROUTER_KEY.startswith("BU_") else "❌"
        print(f"\n{'='*45}\n  🎓 BLIP LESSON PRO v7.0\n{'='*45}")
        print(f"  👥 {us} | 📚 {ls} | ❓ {qs} | 📊 {rs}")
        print(f"  🔐 Admin: {ADMIN_USER}")
        print(f"  🤖 AI: {ai_h} | TG ID: {ADMIN_TG_ID}")
        print(f"  [1] 💻 Terminal")
        print(f"  [2] 🌐 Brauzer (port {PORT})")
        print(f"  [3] 🤖 Telegram")
        print(f"  [0] 🚪 Chiqish")
        print(f"{'='*45}")
        t = input("Tanlang: ").strip()
        if t == "1":
            term()
        elif t == "2":
            web()
        elif t == "3":
            tg_mode()
        elif t == "0":
            print("\n👋\n")
            break


if __name__ == "__main__":
    db_init()
    os.system("clear" if os.name != "nt" else "cls")
    print("\n🎓 BLIP LESSON PRO v7.0")
    print(f"🌐 Port: {PORT}")
    print(f"🔐 Admin: {ADMIN_USER}")
    ai_h = "✅" if OPENROUTER_KEY and not OPENROUTER_KEY.startswith("BU_") else "❌"
    print(f"🤖 AI: {ai_h}")
    us, ls, qs, rs = stat_all()
    print(f"👥 {us} | 📚 {ls} | ❓ {qs} | 📊 {rs}")
    input("\n▶️ Enter...")
    menyu()