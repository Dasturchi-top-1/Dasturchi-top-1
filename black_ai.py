from flask import Flask, jsonify, request
import platform
import os
import time
import random
import threading
import logging
from functools import wraps

app = Flask(__name__)

# Flask/Werkzeug har bir so'rovni ("GET /poll HTTP/1.1" 200 kabi)
# avtomatik konsolga chiqarib, jurnalni to'ldirib yuboradi.
# Buni o'chiramiz - faqat o'zimiz yozgan [TIZIM]/[SAYTDAN] xabarlari qolsin.
logging.getLogger("werkzeug").setLevel(logging.ERROR)

# ============================================================
#  PAROL HIMOYASI
#  <<< SHU QATORDA PAROLNI O'ZGARTIRING (17-qator) >>>
# ============================================================
PAROL = "921324"


def parol_kerak(funksiya):
    @wraps(funksiya)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.password != PAROL:
            return ("Kirish taqiqlangan. Parol kerak.", 401,
                    {"WWW-Authenticate": 'Basic realm="Black AI Kiber-Panel"'})
        return funksiya(*args, **kwargs)
    return wrapper

# ============================================================
#  XAVFSIZ BUYRUQLAR RO'YXATI (whitelist)
#  Cheksiz shell buyruq emas - faqat shu funksiyalar ishlaydi.
# ============================================================
def _cmd_vaqt():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def _cmd_python_versiya():
    return platform.python_version()

def _cmd_tizim():
    return f"{platform.system()} {platform.release()} ({platform.machine()})"

def _cmd_fayllar():
    try:
        yol = os.getcwd()
        fayllar = os.listdir(yol)[:15]
        return f"{yol}:\n" + "\n".join(fayllar) if fayllar else "Papka bo'sh."
    except Exception as xato:
        return f"Xatolik: {xato}"

def _cmd_random_kod():
    return f"BLACK-AI-{random.randint(100000, 999999)}"

def _cmd_batareya():
    yollar = [
        "/sys/class/power_supply/battery/capacity",
        "/sys/class/power_supply/BAT0/capacity",
    ]
    for yol in yollar:
        try:
            with open(yol, "r") as f:
                foiz = f.read().strip()
            return f"Batareya: {foiz}%"
        except Exception:
            continue
    return "Batareya ma'lumoti topilmadi (qurilma qo'llab-quvvatlamaydi)."

def _cmd_xotira():
    try:
        with open("/proc/meminfo", "r") as f:
            qatorlar = f.readlines()[:3]
        natija = []
        for q in qatorlar:
            nom, qiymat = q.split(":")
            kb = int(qiymat.strip().split()[0])
            natija.append(f"{nom}: {kb // 1024} MB")
        return "\n".join(natija)
    except Exception as xato:
        return f"Xotira ma'lumoti olinmadi: {xato}"

def _cmd_ip_manzil():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"Lokal IP: {ip}"
    except Exception as xato:
        return f"IP aniqlanmadi: {xato}"

BUYRUQLAR = {
    "vaqt": _cmd_vaqt,
    "python": _cmd_python_versiya,
    "tizim": _cmd_tizim,
    "fayllar": _cmd_fayllar,
    "kod": _cmd_random_kod,
    "batareya": _cmd_batareya,
    "xotira": _cmd_xotira,
    "ip": _cmd_ip_manzil,
}

# ============================================================
#  KONSOL <-> SAYT ALOQA KANALI
# ============================================================
konsol_jurnali = []          # Pydroid konsolida yozilgan xabarlar
konsol_qulf = threading.Lock()


def konsol_tinglovchi():
    """Alohida oqimda ishlaydi: Pydroid konsolidan xabar o'qiydi
    va uni sayt ko'ra oladigan umumiy jurnalga qo'shadi."""
    while True:
        try:
            matn = input()
        except EOFError:
            break
        if not matn.strip():
            continue
        with konsol_qulf:
            yangi_id = len(konsol_jurnali) + 1
            konsol_jurnali.append({"id": yangi_id, "matn": matn})
        print(f"[TIZIM] Saytga yuborildi: {matn}")

# ============================================================
#  DASHBOARD (minified HTML/CSS/JS)
# ============================================================
DASHBOARD_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BLACK AI :: 921324</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Consolas,monospace}
body{background:#0d0d0d;color:#39ff14;padding:16px}
h1{color:#39ff14;font-size:20px;text-align:center;margin-bottom:2px}
.sub{color:#00c8ff;text-align:center;font-size:11px;margin-bottom:20px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px}
button{background:#111a24;color:#39ff14;border:1px solid #39ff14;padding:12px 6px;
font-size:12px;border-radius:4px;cursor:pointer}
button:active{background:#39ff14;color:#0d0d0d}
#term{background:#000;border:1px solid #00c8ff;border-radius:4px;padding:10px;
height:220px;overflow-y:auto;font-size:12px;white-space:pre-wrap}
.line{margin-bottom:4px}
.ok{color:#39ff14}.err{color:#ff4444}.web{color:#ffcc00}.pyd{color:#00c8ff}
.sendrow{display:flex;gap:6px;margin-top:10px}
#msg{flex:1;background:#111a24;color:#39ff14;border:1px solid #39ff14;
border-radius:4px;padding:8px;font-size:13px}
#sendbtn{background:#39ff14;color:#0d0d0d;border:none;border-radius:4px;
padding:8px 14px;font-weight:bold}
</style></head><body>
<h1>&gt;&gt; BLACK AI KIBER-PANEL &lt;&lt;</h1>
<div class="sub">[ NODE: 921324 | STATUS: ONLINE ]</div>
<div class="grid" id="btns"></div>
<div id="term"></div>
<div class="sendrow">
<input id="msg" placeholder="Pydroid'ga xabar yoz..." onkeydown="if(event.key==='Enter')yubor()">
<button id="sendbtn" onclick="yubor()">YUBOR</button>
</div>
<script>
const buyruqlar=["vaqt","python","tizim","fayllar","kod","batareya","xotira","ip"];
const grid=document.getElementById("btns");
const term=document.getElementById("term");
let oxirgiId=0;
buyruqlar.forEach(b=>{
  const el=document.createElement("button");
  el.textContent="["+b.toUpperCase()+"]";
  el.onclick=()=>bajar(b);
  grid.appendChild(el);
});
function yoz(matn,klass){
  const d=document.createElement("div");
  d.className="line "+(klass||"");
  d.textContent=matn;
  term.appendChild(d);
  term.scrollTop=term.scrollHeight;
}
async function bajar(nomi){
  yoz("> "+nomi+" bajarilmoqda...","");
  try{
    const r=await fetch("/run/"+nomi);
    const d=await r.json();
    if(d.ok){yoz(d.natija,"ok");}else{yoz("XATOLIK: "+d.xato,"err");}
  }catch(e){yoz("Ulanish xatosi: "+e,"err");}
}
async function yubor(){
  const kirish=document.getElementById("msg");
  const matn=kirish.value.trim();
  if(!matn)return;
  yoz("[SAYT -> PYDROID]: "+matn,"web");
  kirish.value="";
  try{
    await fetch("/send",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({matn:matn})});
  }catch(e){yoz("Yuborishda xato: "+e,"err");}
}
async function tinglash(){
  try{
    const r=await fetch("/poll?since="+oxirgiId);
    const d=await r.json();
    if(d.ok && d.xabarlar.length){
      d.xabarlar.forEach(x=>{
        yoz("[PYDROID -> SAYT]: "+x.matn,"pyd");
        oxirgiId=x.id;
      });
    }
  }catch(e){}
  setTimeout(tinglash,1500);
}
yoz("Tizim tayyor. Buyruq tanlang yoki xabar yozing.","ok");
tinglash();
</script></body></html>"""


# ============================================================
#  MARSHRUTLAR (ROUTES)
# ============================================================
@app.route("/")
@parol_kerak
def bosh_sahifa():
    return DASHBOARD_HTML


@app.route("/run/<buyruq_nomi>")
@parol_kerak
def buyruq_bajar(buyruq_nomi):
    funksiya = BUYRUQLAR.get(buyruq_nomi)
    if funksiya is None:
        return jsonify(ok=False, xato="Bunday buyruq ro'yxatda yo'q."), 404
    try:
        natija = funksiya()
        return jsonify(ok=True, natija=natija)
    except Exception as xato:
        return jsonify(ok=False, xato=str(xato)), 500


@app.route("/poll")
@parol_kerak
def poll():
    """Sayt shu yerga har 1.5 soniyada so'rov yuborib, Pydroid
    konsolida yozilgan yangi xabarlarni oladi."""
    try:
        since = int(request.args.get("since", 0))
    except ValueError:
        since = 0
    with konsol_qulf:
        yangilari = [x for x in konsol_jurnali if x["id"] > since]
    return jsonify(ok=True, xabarlar=yangilari)


@app.route("/send", methods=["POST"])
@parol_kerak
def send():
    """Sayt orqali yuborilgan xabarni Pydroid konsoliga chop etadi."""
    try:
        malumot = request.get_json(force=True)
        matn = (malumot.get("matn") or "").strip()
    except Exception:
        matn = ""
    if matn:
        print(f"[SAYTDAN]: {matn}")
        return jsonify(ok=True)
    return jsonify(ok=False, xato="Bo'sh xabar."), 400


# ============================================================
#  ISHGA TUSHIRISH
# ============================================================
if __name__ == "__main__":
    print("=" * 40)
    print("  BLACK AI KIBER-PANEL v5.0 :: 921324")
    print("=" * 40)
    print("[TIZIM] Server ishga tushmoqda...")
    print("[TIZIM] Brauzerda oching: http://10.241.232.39:8080")
    print("[TIZIM] Shu konsolga yozgan xabaringiz saytga boradi.\n")

    tinglovchi_oqim = threading.Thread(target=konsol_tinglovchi, daemon=True)
    tinglovchi_oqim.start()

    app.run(host="0.0.0.0", port=8080, debug=False)
