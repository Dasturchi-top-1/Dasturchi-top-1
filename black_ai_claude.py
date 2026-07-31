# ============================================================
#  BLIP PLATFORM :: QISM 1 / 4
#  Import + Sozlamalar + Baza + Autentifikatsiya
#  Project Code: 921324
# ============================================================
from flask import Flask,request,session,redirect,url_for,render_template_string,jsonify
from flask_socketio import SocketIO,emit,join_room,leave_room
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
import sqlite3,os,time,random,string

# ── SOZLAMALAR ──────────────────────────────────────────────
BAZA  = "/storage/emulated/0/AI/blip_platform.db"
KALIT = "blip-921324-secret"
PORT  = 8080
MAXFIY_KOD = "921324"          # Platformaga kirish uchun taklif kodi
ONLAYN = set()                 # Xotirada saqlanadigan onlayn IDlar

app = Flask(__name__)
app.config["SECRET_KEY"] = KALIT
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

import logging
logging.getLogger("werkzeug").setLevel(logging.ERROR)

# ── BAZA ────────────────────────────────────────────────────
def db():
    os.makedirs(os.path.dirname(BAZA), exist_ok=True)
    u = sqlite3.connect(BAZA)
    u.row_factory = sqlite3.Row
    return u

def db_init():
    u = db()
    u.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created TEXT NOT NULL,
            online_share INTEGER DEFAULT 0,
            last_seen TEXT,
            battery TEXT,
            bio TEXT DEFAULT '',
            score INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS friends(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_id INTEGER NOT NULL,
            to_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created TEXT NOT NULL,
            UNIQUE(from_id,to_id)
        );
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_id INTEGER NOT NULL,
            to_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            time TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS quiz_scores(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            time TEXT NOT NULL
        );
    """)
    u.commit(); u.close()

# ── YORDAMCHILAR ────────────────────────────────────────────
def require_login(f):
    @wraps(f)
    def wrapper(*a,**kw):
        if "uid" not in session:
            return redirect(url_for("login"))
        return f(*a,**kw)
    return wrapper

def get_user(uid):
    u = db()
    r = u.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone()
    u.close(); return r

def are_friends(a,b):
    u = db()
    r = u.execute(
        "SELECT 1 FROM friends WHERE status='accepted' AND "
        "((from_id=? AND to_id=?) OR (from_id=? AND to_id=?))",
        (a,b,b,a)
    ).fetchone()
    u.close(); return r is not None

def friend_list(uid):
    u = db()
    r = u.execute("""
        SELECT u.id,u.username,u.online_share,u.last_seen,u.battery
        FROM friends f JOIN users u ON
            (f.from_id=? AND u.id=f.to_id) OR
            (f.to_id=? AND u.id=f.from_id)
        WHERE f.status='accepted' ORDER BY u.username
    """,(uid,uid)).fetchall()
    u.close(); return r

# ── ASOSIY STIL ─────────────────────────────────────────────
CSS = """
*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,monospace}
body{background:#0d0d0d;color:#39ff14;min-height:100vh}
.wrap{max-width:420px;margin:0 auto;padding:16px}
h1{color:#39ff14;font-size:17px;text-align:center;margin-bottom:3px}
.sub{color:#00c8ff;font-size:10px;text-align:center;margin-bottom:18px}
input,select,textarea{width:100%;background:#111a24;color:#39ff14;
border:1px solid #00c8ff;border-radius:4px;padding:10px;font-size:13px;
margin-bottom:10px}
.btn{display:block;width:100%;padding:11px;border:none;border-radius:4px;
font-size:13px;font-weight:bold;cursor:pointer;margin-bottom:8px;text-align:center;
text-decoration:none}
.btn-g{background:#39ff14;color:#0d0d0d}
.btn-b{background:#111a24;color:#00c8ff;border:1px solid #00c8ff}
.btn-r{background:#1a0000;color:#ff4444;border:1px solid #ff4444}
.err{color:#ff4444;font-size:12px;text-align:center;margin-bottom:10px}
.nav{display:flex;justify-content:space-between;align-items:center;
background:#111a24;border-bottom:1px solid #1a1a1a;padding:10px 16px;
position:sticky;top:0;z-index:99}
.nav a{color:#00c8ff;font-size:11px;text-decoration:none}
.nav h2{color:#39ff14;font-size:13px}
.karta{background:#111a24;border:1px solid #1a1a1a;border-radius:6px;
padding:12px;margin-bottom:10px}
.qator{display:flex;justify-content:space-between;align-items:center;
padding:9px;border-bottom:1px solid #1a1a1a}
.qator:last-child{border-bottom:none}
.chip{font-size:10px;padding:3px 7px;border-radius:10px;margin-left:4px}
.chip-g{background:#0d3d16;color:#39ff14}
.chip-b{background:#0d1a3d;color:#00c8ff}
.chip-r{background:#1a0000;color:#ff4444}
"""

# ── AUTH HTML ────────────────────────────────────────────────
AUTH_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Blip :: {{t}}</title><style>"""+CSS+"""
.auth-box{max-width:340px;margin:60px auto;padding:28px;
background:#111a24;border:1px solid #39ff14;border-radius:8px;
box-shadow:0 0 20px rgba(57,255,20,.1)}
</style></head><body>
<div class=auth-box>
<h1>>> BLIP PLATFORM <<</h1>
<div class=sub>[ PROJECT CODE: 921324 ]</div>
<form method=POST>
<input name=username placeholder="Ismingiz" required autofocus minlength=3>
<input name=code type=password placeholder="Maxfiy kod" required>
<button class="btn btn-g" type=submit>KIRISH</button>
</form>
{% if err %}<div class=err>{{err}}</div>{% endif %}
</div></body></html>"""

# ── BOSH MENYU HTML ──────────────────────────────────────────
MENU_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Blip :: Menyu</title><style>"""+CSS+"""
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
.modul{background:#111a24;border:1px solid #1a1a1a;border-radius:8px;
padding:16px 10px;text-align:center;text-decoration:none;display:block}
.modul .icon{font-size:24px;margin-bottom:6px}
.modul .nom{color:#39ff14;font-size:12px;font-weight:bold}
.modul .tavsif{color:#555;font-size:9px;margin-top:3px}
</style></head><body>
<div class=nav>
<span style=color:#39ff14;font-size:12px>👤 {{u}}</span>
<h2>>> BLIP <<</h2>
<a href="{{url_for('logout')}}">Chiqish</a>
</div>
<div class=wrap>
<div class=grid>
<a class=modul href="{{url_for('hub')}}">
<div class=icon>🔗</div><div class=nom>Blip Hub</div>
<div class=tavsif>Do'stlar & Chat</div></a>
<a class=modul href="{{url_for('art')}}">
<div class=icon>🎨</div><div class=nom>AI Art</div>
<div class=tavsif>Rasm yaratish</div></a>
<a class=modul href="{{url_for('anon')}}">
<div class=icon>👤</div><div class=nom>Anonim Chat</div>
<div class=tavsif>Begona bilan gaplash</div></a>
<a class=modul href="{{url_for('beat')}}">
<div class=icon>🎵</div><div class=nom>Beat Hub</div>
<div class=tavsif>Musiqa & Pleylist</div></a>
<a class=modul href="{{url_for('crypto')}}">
<div class=icon>💰</div><div class=nom>Crypto</div>
<div class=tavsif>Kurs & Konvertor</div></a>
<a class=modul href="{{url_for('quiz')}}">
<div class=icon>🎯</div><div class=nom>Quiz Master</div>
<div class=tavsif>Viktorina & Reyting</div></a>
<a class=modul href="{{url_for('meme')}}">
<div class=icon>😂</div><div class=nom>Meme</div>
<div class=tavsif>Kulgili rasm</div></a>
</div></div></body></html>"""

# ── AUTH ROUTE'LAR ───────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("menu") if "uid" in session else url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    err = None
    if request.method == "POST":
        un = request.form.get("username","").strip()
        code = request.form.get("code","").strip()

        if code != MAXFIY_KOD:
            err = "Maxfiy kod noto'g'ri."
        elif len(un) < 3:
            err = "Ism kamida 3 belgi bo'lsin."
        else:
            u = db()
            row = u.execute("SELECT * FROM users WHERE username=?",(un,)).fetchone()
            if row is None:
                # Bu ism bilan birinchi marta kirilyapti - avtomatik yaratamiz
                u.execute("INSERT INTO users(username,password,created) VALUES(?,?,?)",
                          (un, "", time.strftime("%Y-%m-%d %H:%M")))
                u.commit()
                row = u.execute("SELECT * FROM users WHERE username=?",(un,)).fetchone()
            u.close()
            session["uid"] = row["id"]
            session["username"] = row["username"]
            return redirect(url_for("menu"))

    return render_template_string(AUTH_H, err=err)

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/menu")
@require_login
def menu():
    return render_template_string(MENU_H, u=session["username"])

# ── QISM 1 TUGADI. Keyin QISM 2 ni davom ettiring ───────────
# ============================================================
#  BLIP PLATFORM :: QISM 2 / 4
#  Modul 1: BLIP HUB - Do'stlar, 1ga1 Chat, Status, Kod Generatori
#  Bu qismni QISM 1 dan keyin, xuddi shu faylga qo'shing.
# ============================================================

# ── HUB DASHBOARD HTML ───────────────────────────────────────
HUB_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Blip Hub</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
<style>"""+CSS+"""
.kod-panel{background:#111a24;border:2px solid #00c8ff;border-radius:8px;
padding:24px 12px;text-align:center;margin:14px 0;box-shadow:0 0 20px rgba(0,200,255,.15)}
.kod{font-size:30px;font-weight:bold;color:#39ff14;letter-spacing:2px}
.kod.blink{animation:bl .6s}
@keyframes bl{0%{color:#fff;text-shadow:0 0 20px #fff}100%{color:#39ff14}}
.kod-lbl{color:#00c8ff;font-size:10px;margin-bottom:8px}
</style></head><body>
<div class=nav>
<a href="{{url_for('menu')}}">&larr; Menyu</a>
<h2>BLIP HUB</h2>
<a href="{{url_for('hub_friends')}}">Do'stlar</a>
</div>
<div class=wrap>
<div class=kod-panel>
<div class=kod-lbl>JORIY KIBER-KOD:</div>
<div class=kod id=kod>------</div>
</div>

<div class=karta>
<form method=POST action="{{url_for('hub_status_toggle')}}">
{% if me.online_share %}
<button class="btn btn-g" type=submit>● ULASHISH YOQIQ (bosib o'chirish)</button>
{% else %}
<button class="btn btn-b" type=submit>○ ULASHISH O'CHIQ (bosib yoqish)</button>
{% endif %}
</form>
</div>

<div class=karta>
<div style="color:#00c8ff;font-size:12px;margin-bottom:8px">DO'STLARIM ({{friends|length}})</div>
{% for f in friends %}
<div class=qator>
<span>{{f.username}}</span>
<div>
{% if f.online_share %}
  {% if f.id in onlayn %}<span class="chip chip-g">● ONLAYN</span>
  {% else %}<span class="chip chip-b">○ {{f.last_seen or ''}}</span>{% endif %}
{% endif %}
<a class="btn btn-b" style="display:inline;padding:5px 10px;margin-left:6px"
href="{{url_for('hub_chat',username=f.username)}}">CHAT</a>
</div>
</div>
{% else %}<div style="color:#555;font-size:11px;padding:10px">Hali do'st yo'q.</div>
{% endfor %}
</div>
</div>
<script>
const socket=io();
socket.on("hub_code",(d)=>{
  const k=document.getElementById("kod");
  k.textContent=d.kod; k.classList.remove("blink"); void k.offsetWidth; k.classList.add("blink");
});
socket.on("hub_refresh",()=>location.reload());
</script>
</body></html>"""

# ── DO'STLAR SAHIFASI HTML ───────────────────────────────────
FRIENDS_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Do'stlar</title><style>"""+CSS+"""</style></head><body>
<div class=nav><a href="{{url_for('hub')}}">&larr; Hub</a><h2>DO'STLAR</h2><span></span></div>
<div class=wrap>
<div class=karta>
<form method=GET>
<input name=q placeholder="Username qidirish..." value="{{q or ''}}">
</form>
{% if results is not none %}
{% for r in results %}
<div class=qator><span>{{r.username}}</span>
<form method=POST action="{{url_for('hub_friend_add',uid=r.id)}}">
<button class="btn btn-g" style="width:auto;padding:6px 12px" type=submit>+ Qo'shish</button>
</form></div>
{% else %}<div style="color:#555;font-size:11px;padding:8px">Topilmadi.</div>{% endfor %}
</div>
{% endif %}

<div class=karta>
<div style="color:#00c8ff;font-size:12px;margin-bottom:8px">SO'ROVLAR</div>
{% for s in requests %}
<div class=qator><span>{{s.username}}</span>
<div>
<a class="btn btn-g" style="display:inline;padding:5px 10px" href="{{url_for('hub_friend_accept',rid=s.rid)}}">✓</a>
<a class="btn btn-r" style="display:inline;padding:5px 10px" href="{{url_for('hub_friend_reject',rid=s.rid)}}">✕</a>
</div></div>
{% else %}<div style="color:#555;font-size:11px;padding:8px">So'rov yo'q.</div>{% endfor %}
</div>

<div class=karta>
<div style="color:#00c8ff;font-size:12px;margin-bottom:8px">DO'STLARIM ({{friends|length}})</div>
{% for f in friends %}<div class=qator><span>{{f.username}}</span></div>
{% else %}<div style="color:#555;font-size:11px;padding:8px">Hali yo'q.</div>{% endfor %}
</div>
</div></body></html>"""

# ── CHAT HTML ─────────────────────────────────────────────────
HUB_CHAT_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Chat :: {{other}}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,monospace}
body{background:#0d0d0d;color:#39ff14;display:flex;flex-direction:column;height:100vh}
.nav{background:#111a24;border-bottom:1px solid #00c8ff;padding:12px 16px;
display:flex;justify-content:space-between}
.nav a{color:#00c8ff;text-decoration:none;font-size:12px}
#box{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:7px}
.b{max-width:75%;padding:8px 12px;border-radius:10px;font-size:13px}
.me{align-self:flex-end;background:#0d3d16;color:#39ff14;border:1px solid #39ff14}
.ot{align-self:flex-start;background:#111a24;color:#00c8ff;border:1px solid #00c8ff}
.t{font-size:9px;color:#666;margin-top:3px}
.ip{display:flex;gap:8px;padding:10px;background:#111a24}
#m{flex:1;background:#0d0d0d;color:#39ff14;border:1px solid #39ff14;
border-radius:18px;padding:9px 14px;font-size:13px}
#s{background:#39ff14;color:#0d0d0d;border:none;border-radius:18px;padding:9px 16px;font-weight:bold}
</style></head><body>
<div class=nav><a href="{{url_for('hub_friends')}}">&larr; Orqaga</a><b>{{other}}</b><span></span></div>
<div id=box>
{% for m in history %}
<div class="b {{'me' if m.from_id==myid else 'ot'}}">{{m.text}}<div class=t>{{m.time}}</div></div>
{% endfor %}
</div>
<div class=ip><input id=m placeholder="Xabar..." autocomplete=off><button id=s>YUBOR</button></div>
<script>
const socket=io(); const otherId={{other_id}}; const myId={{myid}};
const box=document.getElementById("box"); const inp=document.getElementById("m");
function scr(){box.scrollTop=box.scrollHeight} scr();
function add(text,t,fid){
  const d=document.createElement("div");
  d.className="b "+(fid===myId?"me":"ot");
  d.innerHTML=text.replace(/</g,"&lt;")+'<div class="t">'+t+"</div>";
  box.appendChild(d); scr();
}
function send(){
  const v=inp.value.trim(); if(!v)return;
  socket.emit("hub_msg",{to_id:otherId,text:v}); inp.value="";
}
document.getElementById("s").onclick=send;
inp.addEventListener("keydown",e=>{if(e.key==="Enter")send()});
socket.on("hub_msg_in",(d)=>{
  if(d.from_id===otherId||d.to_id===otherId) add(d.text,d.time,d.from_id);
});
</script></body></html>"""

# ── HUB ROUTE'LAR ─────────────────────────────────────────────
@app.route("/hub")
@require_login
def hub():
    me = get_user(session["uid"])
    return render_template_string(HUB_H, me=me, friends=friend_list(session["uid"]), onlayn=ONLAYN)

@app.route("/hub/status/toggle", methods=["POST"])
@require_login
def hub_status_toggle():
    bat = None
    for p in ("/sys/class/power_supply/battery/capacity","/sys/class/power_supply/BAT0/capacity"):
        try:
            with open(p) as f: bat = f.read().strip()+"%"; break
        except Exception: continue
    u = db()
    u.execute("UPDATE users SET online_share=1-COALESCE(online_share,0),battery=? WHERE id=?",
              (bat, session["uid"]))
    u.commit(); u.close()
    return redirect(url_for("hub"))

@app.route("/hub/friends")
@require_login
def hub_friends():
    q = request.args.get("q","").strip()
    results = None
    if q:
        u = db()
        rows = u.execute("SELECT id,username FROM users WHERE username LIKE ? AND id!=? LIMIT 20",
                          (f"%{q}%", session["uid"])).fetchall()
        u.close()
        results = [r for r in rows if not are_friends(session["uid"],r["id"])]
    u = db()
    reqs = u.execute("""
        SELECT f.id AS rid,u.username FROM friends f JOIN users u ON u.id=f.from_id
        WHERE f.to_id=? AND f.status='pending' ORDER BY f.created DESC
    """,(session["uid"],)).fetchall()
    u.close()
    return render_template_string(FRIENDS_H, q=q, results=results, requests=reqs,
                                   friends=friend_list(session["uid"]))

@app.route("/hub/friend/add/<int:uid>", methods=["POST"])
@require_login
def hub_friend_add(uid):
    if uid == session["uid"]: return redirect(url_for("hub_friends"))
    u = db()
    try:
        u.execute("INSERT INTO friends(from_id,to_id,status,created) VALUES(?,?,'pending',?)",
                  (session["uid"], uid, time.strftime("%Y-%m-%d %H:%M")))
        u.commit()
    except sqlite3.IntegrityError: pass
    u.close()
    return redirect(url_for("hub_friends"))

@app.route("/hub/friend/accept/<int:rid>")
@require_login
def hub_friend_accept(rid):
    u = db()
    u.execute("UPDATE friends SET status='accepted' WHERE id=? AND to_id=?",(rid, session["uid"]))
    u.commit(); u.close()
    return redirect(url_for("hub_friends"))

@app.route("/hub/friend/reject/<int:rid>")
@require_login
def hub_friend_reject(rid):
    u = db()
    u.execute("DELETE FROM friends WHERE id=? AND to_id=?",(rid, session["uid"]))
    u.commit(); u.close()
    return redirect(url_for("hub_friends"))

@app.route("/hub/chat/<username>")
@require_login
def hub_chat(username):
    u = db()
    other = u.execute("SELECT * FROM users WHERE username=?",(username,)).fetchone()
    u.close()
    if other is None or not are_friends(session["uid"], other["id"]):
        return redirect(url_for("hub_friends"))
    u = db()
    hist = u.execute("""
        SELECT from_id,to_id,text,time FROM messages
        WHERE (from_id=? AND to_id=?) OR (from_id=? AND to_id=?)
        ORDER BY id ASC LIMIT 300
    """,(session["uid"],other["id"],other["id"],session["uid"])).fetchall()
    u.close()
    return render_template_string(HUB_CHAT_H, other=other["username"], other_id=other["id"],
                                   myid=session["uid"], history=hist)

# ── HUB SOCKETIO HODISALARI ────────────────────────────────────
@socketio.on("connect")
def sio_connect():
    if "uid" not in session:
        return False
    ONLAYN.add(session["uid"])
    join_room(str(session["uid"]))
    socketio.emit("hub_refresh")

@socketio.on("disconnect")
def sio_disconnect():
    uid = session.get("uid")
    if uid:
        ONLAYN.discard(uid)
        u = db()
        u.execute("UPDATE users SET last_seen=? WHERE id=?", (time.strftime("%d.%m %H:%M"), uid))
        u.commit(); u.close()
        socketio.emit("hub_refresh")

@socketio.on("hub_msg")
def sio_hub_msg(data):
    if "uid" not in session: return False
    to_id = data.get("to_id")
    text = (data.get("text") or "").strip()
    if not text or not to_id or len(text) > 2000: return
    if not are_friends(session["uid"], to_id): return
    t = time.strftime("%H:%M")
    u = db()
    u.execute("INSERT INTO messages(from_id,to_id,text,time) VALUES(?,?,?,?)",
              (session["uid"], to_id, text, t))
    u.commit(); u.close()
    pkt = {"from_id":session["uid"],"to_id":to_id,"text":text,"time":t}
    emit("hub_msg_in", pkt, room=str(to_id))
    emit("hub_msg_in", pkt, room=str(session["uid"]))

def hub_code_generator():
    """Har 5 soniyada tasodifiy kod yaratib, barcha ulanganlarga yuboradi."""
    while True:
        socketio.sleep(5)
        kod = f"BLIP-{random.randint(100000,999999)}"
        socketio.emit("hub_code", {"kod": kod})

# ── QISM 2 TUGADI. Keyin QISM 3 ni davom ettiring ─────────────
# ============================================================
#  BLIP PLATFORM :: QISM 3 / 4
#  Modul 2: AI ART GENERATOR (generativ san'at, matn asosida)
#  Modul 3: ANONIM CHAT (tasodifiy juftlashtirish)
#  Modul 4: BEAT HUB (musiqa qidirish - iTunes ochiq API)
#  Bu qismni QISM 2 dan keyin, xuddi shu faylga qo'shing.
# ============================================================
import hashlib
import random as _random
import io
import base64

try:
    from PIL import Image, ImageDraw
    PIL_BOR = True
except ImportError:
    PIL_BOR = False

try:
    import requests as _requests
    REQUESTS_BOR = True
except ImportError:
    REQUESTS_BOR = False

ART_PAPKA = "/storage/emulated/0/AI/art_gallery"

# ── QO'SHIMCHA BAZA JADVALLARI (QISM 3 uchun) ─────────────────
def db_init_qism3():
    u = db()
    u.executescript("""
        CREATE TABLE IF NOT EXISTS art_images(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            filename TEXT NOT NULL,
            created TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS playlist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            track TEXT NOT NULL,
            artist TEXT NOT NULL,
            preview_url TEXT NOT NULL,
            artwork TEXT,
            added TEXT NOT NULL
        );
    """)
    u.commit(); u.close()


# ============================================================
#  MODUL 2: AI ART GENERATOR
#  (Matn asosida deterministik, rangli GENERATIV san'at.
#   Haqiqiy AI rasm-chizish emas - buni foydalanuvchiga ochiq
#   aytamiz, chunki bu halollik talabi.)
# ============================================================
def matndan_rasm_yarat(matn, olcham=420):
    """Matnni hash qilib, shu asosda rangli generativ rasm chizadi."""
    seed = int(hashlib.md5(matn.encode("utf-8")).hexdigest(), 16)
    rnd = _random.Random(seed)

    img = Image.new("RGB", (olcham, olcham), (13, 13, 13))
    draw = ImageDraw.Draw(img)

    def tasodifiy_rang():
        return (rnd.randint(40,255), rnd.randint(40,255), rnd.randint(40,255))

    # Fon gradienti
    rang1, rang2 = tasodifiy_rang(), tasodifiy_rang()
    for y in range(olcham):
        nisbat = y / olcham
        r = int(rang1[0]*(1-nisbat) + rang2[0]*nisbat)
        g = int(rang1[1]*(1-nisbat) + rang2[1]*nisbat)
        b = int(rang1[2]*(1-nisbat) + rang2[2]*nisbat)
        draw.line([(0,y),(olcham,y)], fill=(r,g,b))

    # Tasodifiy shakllar (matn harflari soniga qarab)
    shakllar_soni = min(len(matn) + 5, 40)
    for _ in range(shakllar_soni):
        x1,y1 = rnd.randint(0,olcham), rnd.randint(0,olcham)
        r = rnd.randint(15,80)
        rang = tasodifiy_rang()
        shakl_turi = rnd.choice(["doira","chiziq","uchburchak"])
        if shakl_turi == "doira":
            draw.ellipse([x1-r,y1-r,x1+r,y1+r], outline=rang, width=2)
        elif shakl_turi == "chiziq":
            x2,y2 = rnd.randint(0,olcham), rnd.randint(0,olcham)
            draw.line([(x1,y1),(x2,y2)], fill=rang, width=2)
        else:
            x2,y2 = x1+rnd.randint(-r,r), y1+rnd.randint(-r,r)
            x3,y3 = x1+rnd.randint(-r,r), y1+rnd.randint(-r,r)
            draw.polygon([(x1,y1),(x2,y2),(x3,y3)], outline=rang)

    return img


ART_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>AI Art</title><style>"""+CSS+"""
.galereya{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.galereya img{width:100%;border-radius:6px;border:1px solid #1a1a1a}
.galereya .prompt{font-size:9px;color:#666;margin-top:3px}
</style></head><body>
<div class=nav><a href="{{url_for('menu')}}">&larr; Menyu</a><h2>AI ART</h2><span></span></div>
<div class=wrap>
<div class=karta>
<div style="color:#00c8ff;font-size:11px;margin-bottom:8px">
Matn yozing, generativ san'at yarataylik (deterministik, matningizga xos rang/shakl):
</div>
<form method=POST action="{{url_for('art_generate')}}">
<input name=prompt placeholder="Masalan: kiber-samuray tong" required maxlength=100>
<button class="btn btn-g" type=submit>🎨 YARATISH</button>
</form>
</div>
<div class=karta>
<div style="color:#00c8ff;font-size:12px;margin-bottom:8px">GALEREYA</div>
<div class=galereya>
{% for a in gallery %}
<div>
<img src="{{url_for('art_image',filename=a.filename)}}">
<div class=prompt>"{{a.prompt}}" — {{a.username}}</div>
</div>
{% else %}<div style="color:#555;font-size:11px">Hali rasm yo'q.</div>{% endfor %}
</div></div>
</div></body></html>"""


@app.route("/art")
@require_login
def art():
    u = db()
    gallery = u.execute("""
        SELECT a.filename,a.prompt,u.username FROM art_images a
        JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT 20
    """).fetchall()
    u.close()
    return render_template_string(ART_H, gallery=gallery)


@app.route("/art/generate", methods=["POST"])
@require_login
def art_generate():
    prompt = request.form.get("prompt","").strip()[:100]
    if not prompt or not PIL_BOR:
        return redirect(url_for("art"))

    os.makedirs(ART_PAPKA, exist_ok=True)
    img = matndan_rasm_yarat(prompt)
    fname = f"{session['uid']}_{int(time.time())}.png"
    img.save(os.path.join(ART_PAPKA, fname))

    u = db()
    u.execute("INSERT INTO art_images(user_id,prompt,filename,created) VALUES(?,?,?,?)",
              (session["uid"], prompt, fname, time.strftime("%Y-%m-%d %H:%M")))
    u.commit(); u.close()
    return redirect(url_for("art"))


@app.route("/art/image/<filename>")
@require_login
def art_image(filename):
    from flask import send_from_directory
    return send_from_directory(ART_PAPKA, filename)


# ============================================================
#  MODUL 3: ANONIM CHAT
# ============================================================
ANON_QUEUE = []          # kutayotgan uid lar
ANON_PAIRS = {}          # uid -> partner_uid
ANON_LABELS = {}         # uid -> "Anonim #1234"

ANON_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Anonim Chat</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,monospace}
body{background:#0d0d0d;color:#39ff14;display:flex;flex-direction:column;height:100vh}
.nav{background:#111a24;border-bottom:1px solid #00c8ff;padding:12px 16px;
display:flex;justify-content:space-between}
.nav a{color:#00c8ff;text-decoration:none;font-size:12px}
#status{text-align:center;color:#00c8ff;font-size:11px;padding:8px}
#box{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:7px}
.b{max-width:75%;padding:8px 12px;border-radius:10px;font-size:13px}
.me{align-self:flex-end;background:#0d3d16;color:#39ff14;border:1px solid #39ff14}
.ot{align-self:flex-start;background:#111a24;color:#00c8ff;border:1px solid #00c8ff}
.ip{display:flex;gap:6px;padding:10px;background:#111a24}
#m{flex:1;background:#0d0d0d;color:#39ff14;border:1px solid #39ff14;
border-radius:18px;padding:9px 14px;font-size:13px}
button{background:#39ff14;color:#0d0d0d;border:none;border-radius:18px;
padding:9px 14px;font-weight:bold;font-size:11px}
.next{background:#ff4444}
</style></head><body>
<div class=nav><a href="{{url_for('menu')}}">&larr; Menyu</a><b>ANONIM CHAT</b><span></span></div>
<div id=status>Ulanmoqda...</div>
<div id=box></div>
<div class=ip>
<input id=m placeholder="Xabar..." autocomplete=off disabled>
<button id=s disabled>YUBOR</button>
<button id=n class=next>KEYINGI</button>
</div>
<script>
const socket=io();
const box=document.getElementById("box"), st=document.getElementById("status");
const inp=document.getElementById("m"), sb=document.getElementById("s");
function scr(){box.scrollTop=box.scrollHeight}
function add(t,cls){const d=document.createElement("div");d.className="b "+cls;
d.textContent=t;box.appendChild(d);scr();}
function baglan(){ box.innerHTML=""; st.textContent="Qidirilmoqda..."; socket.emit("anon_join"); }
socket.on("connect", baglan);
socket.on("anon_waiting", ()=>{ st.textContent="Suhbatdosh kutilmoqda..."; inp.disabled=true; sb.disabled=true;});
socket.on("anon_paired", (d)=>{
  st.textContent="Ulandingiz: "+d.label; inp.disabled=false; sb.disabled=false;
  add("--- Suhbat boshlandi ("+d.label+") ---","ot");
});
socket.on("anon_message", (d)=>{ add(d.text,"ot"); });
socket.on("anon_partner_left", ()=>{
  add("--- Suhbatdosh chiqib ketdi ---","ot");
  st.textContent="Suhbatdosh chiqdi. KEYINGI bosing."; inp.disabled=true; sb.disabled=true;
});
function send(){ const v=inp.value.trim(); if(!v)return; socket.emit("anon_message",{text:v}); add(v,"me"); inp.value="";}
document.getElementById("s").onclick=send;
inp.addEventListener("keydown",e=>{if(e.key==="Enter")send()});
document.getElementById("n").onclick=()=>{ socket.emit("anon_next"); baglan(); };
window.addEventListener("beforeunload",()=>{socket.emit("anon_leave");});
</script></body></html>"""


@app.route("/anon")
@require_login
def anon():
    return render_template_string(ANON_H)


def _anon_yangi_label():
    return f"Anonim #{_random.randint(1000,9999)}"


def _anon_unpair(uid, xabar_ber=True):
    partner = ANON_PAIRS.pop(uid, None)
    if partner is not None:
        ANON_PAIRS.pop(partner, None)
        if xabar_ber:
            socketio.emit("anon_partner_left", room=str(partner))
    if uid in ANON_QUEUE:
        ANON_QUEUE.remove(uid)


@socketio.on("anon_join")
def sio_anon_join():
    if "uid" not in session: return False
    uid = session["uid"]
    _anon_unpair(uid, xabar_ber=True)

    if ANON_QUEUE:
        partner = ANON_QUEUE.pop(0)
        ANON_PAIRS[uid] = partner
        ANON_PAIRS[partner] = uid
        ANON_LABELS[uid] = _anon_yangi_label()
        ANON_LABELS[partner] = _anon_yangi_label()
        emit("anon_paired", {"label": ANON_LABELS[partner]}, room=str(uid))
        emit("anon_paired", {"label": ANON_LABELS[uid]}, room=str(partner))
    else:
        if uid not in ANON_QUEUE:
            ANON_QUEUE.append(uid)
        emit("anon_waiting")


@socketio.on("anon_message")
def sio_anon_message(data):
    if "uid" not in session: return False
    uid = session["uid"]
    partner = ANON_PAIRS.get(uid)
    text = (data.get("text") or "").strip()
    if partner and text:
        emit("anon_message", {"text": text[:1000]}, room=str(partner))


@socketio.on("anon_next")
def sio_anon_next():
    if "uid" not in session: return False
    _anon_unpair(session["uid"])


@socketio.on("anon_leave")
def sio_anon_leave():
    if "uid" not in session: return False
    _anon_unpair(session["uid"])


# ============================================================
#  MODUL 4: BEAT HUB (musiqa qidirish - iTunes ochiq API)
#  Eslatma: bu FAQAT 30 soniyalik rasmiy PREVIEW beradi -
#  to'liq qo'shiq yuklab olish HUQUQIY emas, shuning uchun
#  bu funksiya qasddan qo'shilmagan.
# ============================================================
BEAT_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Beat Hub</title><style>"""+CSS+"""
.trek{display:flex;gap:10px;align-items:center;padding:8px;
border-bottom:1px solid #1a1a1a}
.trek img{width:44px;height:44px;border-radius:4px}
.trek .info{flex:1;min-width:0}
.trek .nom{font-size:12px;color:#39ff14;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.trek .art{font-size:10px;color:#666}
audio{width:100%;height:28px;margin-top:4px}
</style></head><body>
<div class=nav><a href="{{url_for('menu')}}">&larr; Menyu</a><h2>BEAT HUB</h2>
<a href="{{url_for('beat_playlist')}}">Pleylist</a></div>
<div class=wrap>
<div class=karta>
<form method=GET action="{{url_for('beat')}}">
<input name=q placeholder="Qo'shiq yoki ijrochi qidirish..." value="{{q or ''}}">
</form>
{% if q %}
{% for t in results %}
<div class=trek>
<img src="{{t.artwork}}">
<div class=info>
<div class=nom>{{t.track}}</div>
<div class=art>{{t.artist}}</div>
<audio controls src="{{t.preview}}"></audio>
</div>
<form method=POST action="{{url_for('beat_add')}}">
<input type=hidden name=track value="{{t.track}}">
<input type=hidden name=artist value="{{t.artist}}">
<input type=hidden name=preview value="{{t.preview}}">
<input type=hidden name=artwork value="{{t.artwork}}">
<button style="padding:6px 10px;font-size:10px" type=submit>+</button>
</form>
</div>
{% else %}<div style="color:#555;font-size:11px;padding:8px">Natija topilmadi.</div>{% endfor %}
{% endif %}
</div></div></body></html>"""

PLAYLIST_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Pleylistim</title><style>"""+CSS+"""
.trek{display:flex;gap:10px;align-items:center;padding:8px;border-bottom:1px solid #1a1a1a}
.trek img{width:44px;height:44px;border-radius:4px}
.trek .info{flex:1}.trek .nom{font-size:12px;color:#39ff14}.trek .art{font-size:10px;color:#666}
audio{width:100%;height:28px;margin-top:4px}
</style></head><body>
<div class=nav><a href="{{url_for('beat')}}">&larr; Beat Hub</a><h2>PLEYLISTIM</h2><span></span></div>
<div class=wrap><div class=karta>
{% for t in items %}
<div class=trek><img src="{{t.artwork}}">
<div class=info><div class=nom>{{t.track}}</div><div class=art>{{t.artist}}</div>
<audio controls src="{{t.preview_url}}"></audio></div></div>
{% else %}<div style="color:#555;font-size:11px">Pleylist bo'sh.</div>{% endfor %}
</div></div></body></html>"""


@app.route("/beat")
@require_login
def beat():
    q = request.args.get("q","").strip()
    results = []
    if q and REQUESTS_BOR:
        try:
            r = _requests.get("https://itunes.apple.com/search",
                               params={"term": q, "media": "music", "limit": 15}, timeout=8)
            data = r.json()
            for item in data.get("results", []):
                results.append({
                    "track": item.get("trackName","?"),
                    "artist": item.get("artistName","?"),
                    "preview": item.get("previewUrl",""),
                    "artwork": item.get("artworkUrl60",""),
                })
        except Exception:
            results = []
    return render_template_string(BEAT_H, q=q, results=results)


@app.route("/beat/add", methods=["POST"])
@require_login
def beat_add():
    u = db()
    u.execute("INSERT INTO playlist(user_id,track,artist,preview_url,artwork,added) VALUES(?,?,?,?,?,?)",
              (session["uid"], request.form.get("track",""), request.form.get("artist",""),
               request.form.get("preview",""), request.form.get("artwork",""),
               time.strftime("%Y-%m-%d %H:%M")))
    u.commit(); u.close()
    return redirect(url_for("beat"))


@app.route("/beat/playlist")
@require_login
def beat_playlist():
    u = db()
    items = u.execute("SELECT * FROM playlist WHERE user_id=? ORDER BY id DESC",
                       (session["uid"],)).fetchall()
    u.close()
    return render_template_string(PLAYLIST_H, items=items)

# ── QISM 3 TUGADI. Keyin QISM 4 ni davom ettiring ─────────────
# ============================================================
#  BLIP PLATFORM :: QISM 4 / 4 (YAKUNIY)
#  Modul 5: CRYPTO TRACKER
#  Modul 6: QUIZ MASTER
#  Modul 7: MEME GENERATOR
#  + Ishga tushirish (main runner)
#  Bu qismni QISM 3 dan keyin, xuddi shu faylga qo'shing.
# ============================================================
from flask import send_from_directory

MEME_PAPKA = "/storage/emulated/0/AI/meme_gallery"

def db_init_qism4():
    u = db()
    u.executescript("""
        CREATE TABLE IF NOT EXISTS memes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            created TEXT NOT NULL
        );
    """)
    u.commit(); u.close()


# ============================================================
#  MODUL 5: CRYPTO TRACKER
# ============================================================
CRYPTO_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Crypto Tracker</title><style>"""+CSS+"""
.narx-qator{display:flex;justify-content:space-between;padding:8px;
border-bottom:1px solid #1a1a1a;font-size:12px}
.narx-qator b{color:#39ff14}
.up{color:#39ff14}.down{color:#ff4444}
</style></head><body>
<div class=nav><a href="{{url_for('menu')}}">&larr; Menyu</a><h2>CRYPTO</h2><span></span></div>
<div class=wrap>
{% if xato %}<div class=karta style="color:#ff4444;font-size:12px">{{xato}}</div>{% endif %}

<div class=karta>
<div style="color:#00c8ff;font-size:12px;margin-bottom:8px">KRIPTOVALYUTALAR (USD)</div>
{% for k,v in crypto.items() %}
<div class=narx-qator><span>{{k}}</span><b>${{v}}</b></div>
{% endfor %}
</div>

<div class=karta>
<div style="color:#00c8ff;font-size:12px;margin-bottom:8px">VALYUTA KURSLARI (1 USD =)</div>
{% for k,v in fiat.items() %}
<div class=narx-qator><span>{{k}}</span><b>{{v}}</b></div>
{% endfor %}
</div>

<div class=karta>
<div style="color:#00c8ff;font-size:12px;margin-bottom:8px">KONVERTOR</div>
<form method=GET action="{{url_for('crypto')}}">
<input name=amount type=number step=any placeholder="Miqdor" value="{{amount or ''}}">
<select name=from_c>
{% for c in barcha_valyutalar %}<option value="{{c}}" {{'selected' if c==from_c}}>{{c}}</option>{% endfor %}
</select>
<select name=to_c>
{% for c in barcha_valyutalar %}<option value="{{c}}" {{'selected' if c==to_c}}>{{c}}</option>{% endfor %}
</select>
<button class="btn btn-g" type=submit>HISOBLASH</button>
</form>
{% if natija is not none %}
<div style="text-align:center;color:#39ff14;font-size:15px;margin-top:8px;font-weight:bold">
{{amount}} {{from_c}} = {{natija}} {{to_c}}
</div>
{% endif %}
</div>
</div></body></html>"""


@app.route("/crypto")
@require_login
def crypto():
    xato = None
    crypto_narx = {}
    fiat_narx = {}
    barcha = ["USD","UZS","TJS","RUB","EUR","BTC","ETH"]

    if not REQUESTS_BOR:
        xato = "requests kutubxonasi o'rnatilmagan."
    else:
        try:
            r1 = _requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids":"bitcoin,ethereum","vs_currencies":"usd"}, timeout=8
            ).json()
            crypto_narx = {
                "Bitcoin (BTC)": r1.get("bitcoin",{}).get("usd","?"),
                "Ethereum (ETH)": r1.get("ethereum",{}).get("usd","?"),
            }
        except Exception:
            xato = "Kripto narxlarni olishda xato (internetni tekshiring)."

        try:
            r2 = _requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=8).json()
            kurslar = r2.get("rates", {})
            fiat_narx = {
                "UZS": kurslar.get("UZS","?"),
                "TJS": kurslar.get("TJS","?"),
                "RUB": kurslar.get("RUB","?"),
                "EUR": kurslar.get("EUR","?"),
            }
        except Exception:
            if not xato:
                xato = "Valyuta kurslarini olishda xato (internetni tekshiring)."

    amount = request.args.get("amount")
    from_c = request.args.get("from_c","USD")
    to_c = request.args.get("to_c","UZS")
    natija = None

    if amount and not xato:
        try:
            amount_f = float(amount)
            barcha_kurs = {"USD": 1.0}
            barcha_kurs.update({k:float(v) for k,v in fiat_narx.items() if v != "?"})
            if crypto_narx.get("Bitcoin (BTC)","?") != "?":
                barcha_kurs["BTC"] = 1.0/float(crypto_narx["Bitcoin (BTC)"])
            if crypto_narx.get("Ethereum (ETH)","?") != "?":
                barcha_kurs["ETH"] = 1.0/float(crypto_narx["Ethereum (ETH)"])

            if from_c in barcha_kurs and to_c in barcha_kurs:
                usd_qiymat = amount_f / barcha_kurs[from_c]
                natija = round(usd_qiymat * barcha_kurs[to_c], 4)
        except Exception:
            natija = None

    return render_template_string(CRYPTO_H, crypto=crypto_narx, fiat=fiat_narx, xato=xato,
                                   amount=amount, from_c=from_c, to_c=to_c, natija=natija,
                                   barcha_valyutalar=barcha)


# ============================================================
#  MODUL 6: QUIZ MASTER
# ============================================================
SAVOLLAR = {
    "Dasturlash": [
        {"s":"Python'da ro'yxat (list) qanday belgilanadi?","v":["[]","{}","()","<>"],"j":0},
        {"s":"'for' sikli nima uchun ishlatiladi?","v":["Shart tekshirish","Takrorlash","Funksiya yaratish","Import qilish"],"j":1},
        {"s":"HTML nima uchun ishlatiladi?","v":["Dizayn","Server mantiqi","Sahifa tuzilishi","Baza"],"j":2},
        {"s":"SQL nima?","v":["Dasturlash tili","Baza so'rov tili","Server","Brauzer"],"j":1},
    ],
    "Kiber-xavfsizlik": [
        {"s":"Kuchli parolda nima bo'lishi kerak?","v":["Faqat harflar","Faqat raqamlar","Harf+raqam+belgi","Ism"],"j":2},
        {"s":"Parolni saqlashda nima ishlatiladi?","v":["Ochiq matn","Xeshlash","Base64","Hech narsa"],"j":1},
        {"s":"Phishing nima?","v":["Virus turi","Firibgarlik usuli","Dastur tili","Baza"],"j":1},
    ],
    "Turnik": [
        {"s":"Chempion darajasi necha marta turnik?","v":["10","20","32","50"],"j":2},
        {"s":"Turnikda asosiy mushak guruhi?","v":["Oyoq","Orqa/qo'l","Bo'yin","Yuz"],"j":1},
    ],
    "Umumiy bilim": [
        {"s":"Yerning yo'ldoshi nima?","v":["Mars","Oy","Quyosh","Venera"],"j":1},
        {"s":"Suvning kimyoviy formulasi?","v":["CO2","H2O","O2","NaCl"],"j":1},
        {"s":"Bir yilda necha oy bor?","v":["10","11","12","13"],"j":2},
    ],
    "Tojikiston": [
        {"s":"Tojikiston poytaxti?","v":["Xo'jand","Dushanbe","Buxoro","Panjakent"],"j":1},
        {"s":"Tojikiston qaysi qit'ada?","v":["Yevropa","Osiyo","Afrika","Amerika"],"j":1},
    ],
}

QUIZ_MENU_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Quiz Master</title><style>"""+CSS+"""
.mavzu{display:block;background:#111a24;border:1px solid #1a1a1a;border-radius:6px;
padding:14px;margin-bottom:8px;text-decoration:none;color:#39ff14;font-size:13px}
</style></head><body>
<div class=nav><a href="{{url_for('menu')}}">&larr; Menyu</a><h2>QUIZ MASTER</h2><span></span></div>
<div class=wrap>
{% for mavzu in mavzular %}
<a class=mavzu href="{{url_for('quiz_start',topic=mavzu)}}">🎯 {{mavzu}}</a>
{% endfor %}
</div></body></html>"""

QUIZ_Q_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Quiz</title><style>"""+CSS+"""
.savol{font-size:15px;color:#39ff14;margin-bottom:14px;text-align:center}
.variant{display:block;width:100%;text-align:left;margin-bottom:8px;
padding:12px;background:#111a24;border:1px solid #00c8ff;border-radius:6px;
color:#00c8ff;font-size:13px}
.progress{text-align:center;color:#666;font-size:11px;margin-bottom:14px}
</style></head><body>
<div class=nav><a href="{{url_for('quiz')}}">&larr; Mavzular</a><h2>{{topic}}</h2><span></span></div>
<div class=wrap>
<div class=progress>Savol {{idx1}}/{{total}} | Ball: {{score}}</div>
<div class=karta>
<div class=savol>{{q.s}}</div>
<form method=POST action="{{url_for('quiz_answer')}}">
{% for v in q.v %}
<button class=variant name=answer value="{{loop.index0}}" type=submit>{{v}}</button>
{% endfor %}
</form>
</div></div></body></html>"""

QUIZ_RESULT_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Natija</title><style>"""+CSS+"""
.natija{text-align:center;font-size:32px;color:#39ff14;margin:20px 0}
.lb-qator{display:flex;justify-content:space-between;padding:8px;border-bottom:1px solid #1a1a1a;font-size:12px}
</style></head><body>
<div class=nav><a href="{{url_for('quiz')}}">&larr; Mavzular</a><h2>NATIJA</h2><span></span></div>
<div class=wrap>
<div class=karta>
<div class=natija>{{score}}/{{total}}</div>
<a class="btn btn-g" href="{{url_for('quiz_start',topic=topic)}}">QAYTA URINISH</a>
</div>
<div class=karta>
<div style="color:#00c8ff;font-size:12px;margin-bottom:8px">TOP-10 :: {{topic}}</div>
{% for l in leaderboard %}
<div class=lb-qator><span>{{loop.index}}. {{l.username}}</span><b>{{l.score}}/{{l.total}}</b></div>
{% else %}<div style="color:#555;font-size:11px">Hali natija yo'q.</div>{% endfor %}
</div></div></body></html>"""


@app.route("/quiz")
@require_login
def quiz():
    return render_template_string(QUIZ_MENU_H, mavzular=list(SAVOLLAR.keys()))


@app.route("/quiz/start/<topic>")
@require_login
def quiz_start(topic):
    if topic not in SAVOLLAR:
        return redirect(url_for("quiz"))
    session["quiz_topic"] = topic
    session["quiz_idx"] = 0
    session["quiz_score"] = 0
    return _quiz_savol_korsat()


def _quiz_savol_korsat():
    topic = session.get("quiz_topic")
    idx = session.get("quiz_idx", 0)
    savollar = SAVOLLAR.get(topic, [])
    if idx >= len(savollar):
        return _quiz_yakunla()
    q = savollar[idx]
    return render_template_string(QUIZ_Q_H, topic=topic, q=q, idx1=idx+1,
                                   total=len(savollar), score=session.get("quiz_score",0))


def _quiz_yakunla():
    topic = session.get("quiz_topic")
    score = session.get("quiz_score", 0)
    total = len(SAVOLLAR.get(topic, []))

    u = db()
    u.execute("INSERT INTO quiz_scores(user_id,topic,score,total,time) VALUES(?,?,?,?,?)",
              (session["uid"], topic, score, total, time.strftime("%Y-%m-%d %H:%M")))
    u.commit()
    leaderboard = u.execute("""
        SELECT us.username, qs.score, qs.total FROM quiz_scores qs
        JOIN users us ON us.id = qs.user_id
        WHERE qs.topic=? ORDER BY qs.score DESC, qs.total ASC LIMIT 10
    """,(topic,)).fetchall()
    u.close()

    return render_template_string(QUIZ_RESULT_H, topic=topic, score=score, total=total,
                                   leaderboard=leaderboard)


@app.route("/quiz/answer", methods=["POST"])
@require_login
def quiz_answer():
    topic = session.get("quiz_topic")
    idx = session.get("quiz_idx", 0)
    savollar = SAVOLLAR.get(topic, [])

    try:
        tanlov = int(request.form.get("answer", -1))
    except ValueError:
        tanlov = -1

    if 0 <= idx < len(savollar) and tanlov == savollar[idx]["j"]:
        session["quiz_score"] = session.get("quiz_score", 0) + 1

    session["quiz_idx"] = idx + 1
    return _quiz_savol_korsat()


# ============================================================
#  MODUL 7: MEME GENERATOR
# ============================================================
from PIL import ImageFont

MEME_H = """<!DOCTYPE html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Meme Generator</title><style>"""+CSS+"""
.galereya{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.galereya img{width:100%;border-radius:6px;border:1px solid #1a1a1a}
</style></head><body>
<div class=nav><a href="{{url_for('menu')}}">&larr; Menyu</a><h2>MEME GENERATOR</h2><span></span></div>
<div class=wrap>
<div class=karta>
<form method=POST action="{{url_for('meme_generate')}}" enctype="multipart/form-data">
<input type=file name=rasm accept="image/*" required>
<input name=top placeholder="Yuqori matn (ixtiyoriy)" maxlength=60>
<input name=bottom placeholder="Pastki matn (ixtiyoriy)" maxlength=60>
<button class="btn btn-g" type=submit>😂 YARATISH</button>
</form>
</div>
<div class=karta>
<div style="color:#00c8ff;font-size:12px;margin-bottom:8px">GALEREYA</div>
<div class=galereya>
{% for m in gallery %}
<img src="{{url_for('meme_image',filename=m.filename)}}">
{% else %}<div style="color:#555;font-size:11px">Hali meme yo'q.</div>{% endfor %}
</div></div>
</div></body></html>"""


def _meme_matn_chiz(draw, matn, olcham, y, rasm_kengligi):
    try:
        shrift = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 34)
    except Exception:
        shrift = ImageFont.load_default()

    matn = matn.upper()
    bbox = draw.textbbox((0,0), matn, font=shrift)
    matn_kengligi = bbox[2]-bbox[0]
    x = max((rasm_kengligi - matn_kengligi)//2, 5)

    # Qora hoshiya + oq matn (klassik meme uslubi)
    for dx,dy in [(-2,-2),(-2,2),(2,-2),(2,2),(0,2),(0,-2),(2,0),(-2,0)]:
        draw.text((x+dx,y+dy), matn, font=shrift, fill="black")
    draw.text((x,y), matn, font=shrift, fill="white")


@app.route("/meme")
@require_login
def meme():
    u = db()
    gallery = u.execute("SELECT filename FROM memes ORDER BY id DESC LIMIT 20").fetchall()
    u.close()
    return render_template_string(MEME_H, gallery=gallery)


@app.route("/meme/generate", methods=["POST"])
@require_login
def meme_generate():
    fayl = request.files.get("rasm")
    if not fayl or fayl.filename == "":
        return redirect(url_for("meme"))

    try:
        img = Image.open(fayl.stream).convert("RGB")
    except Exception:
        return redirect(url_for("meme"))

    img.thumbnail((600,600))
    draw = ImageDraw.Draw(img)
    top = request.form.get("top","").strip()
    bottom = request.form.get("bottom","").strip()

    if top:
        _meme_matn_chiz(draw, top, img.size, 10, img.size[0])
    if bottom:
        _meme_matn_chiz(draw, bottom, img.size, img.size[1]-50, img.size[0])

    os.makedirs(MEME_PAPKA, exist_ok=True)
    fname = f"{session['uid']}_{int(time.time())}.png"
    img.save(os.path.join(MEME_PAPKA, fname))

    u = db()
    u.execute("INSERT INTO memes(user_id,filename,created) VALUES(?,?,?)",
              (session["uid"], fname, time.strftime("%Y-%m-%d %H:%M")))
    u.commit(); u.close()
    return redirect(url_for("meme"))


@app.route("/meme/image/<filename>")
@require_login
def meme_image(filename):
    return send_from_directory(MEME_PAPKA, filename)


# ============================================================
#  ISHGA TUSHIRISH (MAIN RUNNER)
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  BLIP PLATFORM :: PROJECT CODE 921324")
    print("  7 MODUL: Hub, Art, Anonim, Beat, Crypto, Quiz, Meme")
    print("=" * 50)

    db_init()
    db_init_qism3()
    db_init_qism4()
    print("[TIZIM] Barcha bazalar tayyor.")

    socketio.start_background_task(hub_code_generator)
    print("[TIZIM] Kod generatori ishga tushdi.")

    print(f"[TIZIM] Server: http://0.0.0.0:{PORT}")
    print(f"[TIZIM] Kirish uchun taklif kodi: {MAXFIY_KOD}")

    socketio.run(app, host="0.0.0.0", port=PORT, debug=False,
                 allow_unsafe_werkzeug=True)
