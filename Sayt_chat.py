# ============================================================
#  BLIP SECURE HUB v1.0 – SQL himoyali, parol tekshiruvli
#  Fayl: blip_secure_hub.py
# ============================================================
import os, sqlite3, random, string, datetime
from flask import Flask, request, session, redirect, url_for, render_template_string, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "blip-secure-hub-921324"
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

TIZIM_PAROLI = "921324"
PORT = 8080
BAZA_YOLI = "/storage/emulated/0/AI/blip_secure_hub.db"
YUKLASH_PAPKA = "/storage/emulated/0/Download/BlipSecure/"

os.makedirs(YUKLASH_PAPKA, exist_ok=True)

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
            parol TEXT NOT NULL,
            oxirgi_faollik TEXT,
            yaratilgan TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS xabarlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            yuboruvchi_id INTEGER NOT NULL,
            qabul_qiluvchi_id INTEGER NOT NULL,
            matn TEXT NOT NULL,
            vaqt TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS dostlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            foydalanuvchi_id INTEGER NOT NULL,
            dost_id INTEGER NOT NULL,
            UNIQUE(foydalanuvchi_id, dost_id)
        );
    """)
    ulanish.commit()
    ulanish.close()

baza_ishga_tushir()

onlayn_sid = {}
onlayn_foydalanuvchilar = set()

def login_talab(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_sahifa"))
        return f(*args, **kwargs)
    return wrapper

def hozirgi_vaqt():
    return str(datetime.datetime.now())[:19]

# HTML uslubi
STYLE = "*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,sans-serif}body{background:#0a0a0a;color:#fff;display:flex;height:100vh}.yon-panel{width:35%;background:#111;border-right:1px solid #333;display:flex;flex-direction:column}.asosiy{flex:1;display:flex;flex-direction:column}.bosh{background:#1a1a1a;padding:15px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333}.bosh h2{color:#39ff14;font-size:18px}a{color:#00c8ff;text-decoration:none}.chat-qator{display:flex;align-items:center;padding:15px;border-bottom:1px solid #222;color:#fff;text-decoration:none}.chat-qator:hover{background:#1a1a1a}.avatar{width:45px;height:45px;background:#39ff14;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#000;font-weight:bold;margin-right:12px}.chat-info{flex:1}.onlayn-nuqta{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:5px}.onlayn{background:#39ff14}.offline{background:#666}input,button{background:#000;color:#fff;border:1px solid #39ff14;padding:10px;border-radius:5px}button{background:#39ff14;color:#000;font-weight:bold;cursor:pointer}.xabar{max-width:70%;padding:8px 12px;border-radius:8px;margin:5px;font-size:14px}.men{align-self:flex-end;background:#005c4b}.ular{align-self:flex-start;background:#1a1a1a}.vaqt{font-size:10px;color:#999;text-align:right;margin-top:3px}"

LOGIN_HTML = "<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Blip Secure Hub</title><style>"+STYLE+" body{display:flex;align-items:center;justify-content:center}</style></head><body><div style=background:#111;padding:30px;border-radius:10px;width:340px;text-align:center><h2 style=color:#39ff14>BLIP SECURE HUB</h2><form method=POST><input name=username placeholder='Username' required autofocus><input type=password name=parol placeholder='Parol' required><button>KIRISH</button></form>{% if xato %}<p style=color:red>{{ xato }}</p>{% endif %}</div></body></html>"

PANEL_HTML = "<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Panel</title><script src='https://cdn.socket.io/4.7.5/socket.io.min.js'></script><style>"+STYLE+"</style></head><body><div class=yon-panel><div class=bosh><h2>Secure Hub</h2></div><div style=flex:1;overflow-y:auto>{% for d in dostlar %}<a href='/chat/{{ d.username }}' class=chat-qator><div class=avatar>{{ d.username[0].upper() }}</div><div class=chat-info><span class='onlayn-nuqta {% if d.online %}onlayn{% else %}offline{% endif %}'></span>{{ d.username }}</div></a>{% endfor %}</div></div><div class=asosiy><div class=bosh><span style=color:#39ff14>👋 {{ username }}</span><a href='/logout' style=color:#ff4444>Chiqish</a></div><div style=flex:1;display:flex;align-items:center;justify-content:center;color:#666>Suhbatni tanlang</div></div></body></html>"
CHAT_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Chat</title>
<script src='https://cdn.socket.io/4.7.5/socket.io.min.js'></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,sans-serif}
body{background:#0a0a0a;color:#fff;display:flex;flex-direction:column;height:100vh}
.bosh{background:#1a1a1a;padding:12px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #333}
.bosh a{color:#00c8ff;text-decoration:none;font-size:18px}
.xabarlar{flex:1;overflow-y:auto;padding:15px;display:flex;flex-direction:column}
.xabar{max-width:70%;padding:8px 12px;border-radius:8px;font-size:14px;position:relative}
.men{align-self:flex-end;background:#005c4b}
.ular{align-self:flex-start;background:#1a1a1a}
.vaqt{font-size:10px;color:#999;text-align:right;margin-top:3px}
.kiritish{display:flex;gap:5px;padding:10px;background:#1a1a1a}
#msgInput{flex:1;background:#000;color:#fff;border:none;border-radius:20px;padding:10px 15px}
button{background:#39ff14;color:#000;border:none;border-radius:20px;padding:10px 20px;font-weight:bold}
</style></head><body>
<div class=bosh><a href='/dashboard'>←</a><b>{{ target }}</b></div>
<div class=xabarlar id=xabarlar>
{% for x in tarix %}
<div class='xabar {% if x.yuboruvchi_id == mening_id %}men{% else %}ular{% endif %}'>{{ x.matn }}<div class=vaqt>{{ x.vaqt[:16] }}</div></div>
{% endfor %}
</div>
<div class=kiritish><input id=msgInput placeholder='Xabar...' autofocus><button onclick=yubor()>Yubor</button></div>
<script>
const s=io();
const target='{{ target }}';
const meningId={{ mening_id }};
s.emit('join_chat',{target:target});
s.on('yangi_xabar',d=>{
    if(d.yuboruvchi_id==meningId||d.qabul_qiluvchi_id==meningId){
        let e=document.createElement('div');
        e.className='xabar '+(d.yuboruvchi_id==meningId?'men':'ular');
        e.innerHTML=d.matn+'<div class=vaqt>'+d.vaqt.slice(0,16)+'</div>';
        document.getElementById('xabarlar').appendChild(e);
        e.scrollIntoView();
    }
});
function yubor(){
    let i=document.getElementById('msgInput');
    let m=i.value.trim();
    if(m){s.emit('xabar_yuborish',{target:target,matn:m});i.value=''}
}
document.getElementById('msgInput').addEventListener('keypress',e=>{if(e.key=='Enter')yubor()})
</script></body></html>"""

@app.route("/", methods=["GET","POST"])
def login_sahifa():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        parol = request.form.get("parol","").strip()
        if parol == TIZIM_PAROLI and username:
            ulanish = baza_ulanish()
            foydalanuvchi = ulanish.execute("SELECT * FROM foydalanuvchilar WHERE username=?", (username,)).fetchone()
            if not foydalanuvchi:
                ulanish.execute("INSERT INTO foydalanuvchilar (username, parol, yaratilgan) VALUES (?,?,?)", (username, parol, hozirgi_vaqt()))
                foydalanuvchi = ulanish.execute("SELECT * FROM foydalanuvchilar WHERE username=?", (username,)).fetchone()
            ulanish.commit()
            ulanish.close()
            session["user_id"] = foydalanuvchi["id"]
            session["username"] = username
            return redirect(url_for("dashboard"))
        return render_template_string(LOGIN_HTML, xato="Noto'g'ri parol yoki ism!")
    return render_template_string(LOGIN_HTML, xato=None)

@app.route("/dashboard")
@login_talab
def dashboard():
    ulanish = baza_ulanish()
    dostlar = ulanish.execute("""
        SELECT u.id, u.username FROM dostlar d
        JOIN foydalanuvchilar u ON d.dost_id = u.id
        WHERE d.foydalanuvchi_id = ?
    """, (session["user_id"],)).fetchall()
    dost_list = []
    for d in dostlar:
        dost_list.append({"username": d["username"], "online": d["id"] in onlayn_foydalanuvchilar})
    ulanish.close()
    return render_template_string(PANEL_HTML, username=session["username"], dostlar=dost_list)

@app.route("/chat/<username>")
@login_talab
def chat_sahifa(username):
    ulanish = baza_ulanish()
    target = ulanish.execute("SELECT * FROM foydalanuvchilar WHERE username=?", (username,)).fetchone()
    if not target:
        ulanish.close()
        return "Topilmadi", 404
    tarix = ulanish.execute("SELECT * FROM xabarlar WHERE (yuboruvchi_id=? AND qabul_qiluvchi_id=?) OR (yuboruvchi_id=? AND qabul_qiluvchi_id=?) ORDER BY id LIMIT 100",
                            (session["user_id"], target["id"], target["id"], session["user_id"])).fetchall()
    ulanish.close()
    return render_template_string(CHAT_HTML, target=username, mening_id=session["user_id"], tarix=tarix)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_sahifa"))

# Socket.IO
@socketio.on("connect")
def ulanish():
    uid = session.get("user_id")
    if uid:
        onlayn_foydalanuvchilar.add(uid)
        onlayn_sid[request.sid] = uid

@socketio.on("disconnect")
def uzilish():
    uid = onlayn_sid.pop(request.sid, None)
    if uid:
        onlayn_foydalanuvchilar.discard(uid)

@socketio.on("join_chat")
def join_chat(data):
    target = data.get("target")
    if target:
        join_room(f"chat_{min(session['user_id'], target)}_{max(session['user_id'], target)}")

@socketio.on("xabar_yuborish")
def xabar_yuborish(data):
    yuboruvchi_id = session.get("user_id")
    target_name = data.get("target")
    matn = data.get("matn","").strip()
    if not yuboruvchi_id or not target_name or not matn:
        return
    ulanish = baza_ulanish()
    target = ulanish.execute("SELECT id FROM foydalanuvchilar WHERE username=?", (target_name,)).fetchone()
    if target:
        ulanish.execute("INSERT INTO xabarlar (yuboruvchi_id, qabul_qiluvchi_id, matn, vaqt) VALUES (?,?,?,?)",
                        (yuboruvchi_id, target["id"], matn, hozirgi_vaqt()))
        ulanish.commit()
        emit("yangi_xabar", {"yuboruvchi_id": yuboruvchi_id, "qabul_qiluvchi_id": target["id"], "matn": matn, "vaqt": hozirgi_vaqt()},
             room=f"chat_{min(yuboruvchi_id, target['id'])}_{max(yuboruvchi_id, target['id'])}")
    ulanish.close()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=PORT, debug=False, allow_unsafe_werkzeug=True)