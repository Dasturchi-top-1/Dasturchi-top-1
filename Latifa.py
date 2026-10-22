# ============================================================
# 😂 BLIP KULGILI BOT — Final v3.0
# Terminal + Brauzer + Telegram + AI (o'zbek lotin) + Fayl
# Fayl: blip_meme_ai.py
# ============================================================
import os, json, random, logging, datetime
import urllib.request, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "YOUR_TOKEN"
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY"
AI_URL = "https://openrouter.ai/api/v1/chat/completions"
PORT = 8000
LATIFA_FAYL = "/storage/emulated/0/Ai/Latifa/latifa.txt"

# Fallback modellar (o'zbek tilida yaxshi ishlaydiganlar)
MODELLAR = [
    "nex-agi/nex-n2.5-mini:free",
    "nex-agi/nex-n2.5-pro:free",
    "qwen/qwen3.8-27b:free",
    "z-ai/glm-5.2:free",
    "google/gemma-4-31b-it:free",
]

logging.basicConfig(level=logging.INFO)
KESH = []
SEVIMLILAR = {}

MAVZULAR = [
    "dasturchilar hayoti", "Python programming", "sun'iy intellekt",
    "kundalik hayot", "maktab hayoti", "oila va do'stlar",
    "sport va mashq", "turnik va fitness", "internet va tarmoq",
    "kompyuter o'yinlari", "telefon va gadgetlar", "ovqat va taomlar",
    "hayvonlar", "kosmos va sayyoralar", "ob-havo",
    "Tojikiston va vatan", "kiber xavfsizlik", "matematika",
    "ingliz tili o'rganish", "kitob o'qish",
]

KUTISH = [
    "🤔 AI boshini qashlayapti...", "☕ AI qahva ichyapti...",
    "🧠 AI xotirasini qidiryapti...", "😂 AI kulib yubordi...",
    "🎭 AI hazil o'ylayapti...", "🤡 AI niqobini kiydi...",
    "💡 AI lampochkasi yondi!...", "🍿 Popkorn tayyorlanmoqda...",
]
KULGILI_XATO = [
    "😂 AI hazildan charchadi!", "🤖 AI robot bo'lib qoldi!",
    "🙈 AI uyalib qoldi!", "🐌 AI sekinlashdi!",
    "💤 AI uxlab qoldi!", "🌪 AI shamolga uchdi!",
]
TABRIK = [
    "🎉 Zo'r! Sen hazilni tushunding!", "😂 Kulgili!",
    "🏆 Sen hazil ustasisan!", "🌟 Ajoyib!",
    "🎭 Sahna seniki!", "😎 Zo'r, sen kulgichisan!",
]
BAYROQLAR = ["😂", "🤣", "😆", "😁", "😅", "🤭", "😹", "😸"]

# ============================================================
# TILNI TEKSHIRISH (o'zbek lotin)
# ============================================================
def til_tekshir(matn):
    """O'zbek lotin alifbosida yozilganligini tekshiradi."""
    if not matn or len(matn) < 10:
        return False
    
    matn_l = matn.lower()
    
    # Kirill belgilari
    kirill = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    if sum(1 for b in matn_l if b in kirill) > 3:
        return False
    
    # Inglizcha umumiy so'zlar
    ingliz = {"the", "and", "is", "are", "you", "with", "this", "that",
              "have", "from", "joke", "about", "what", "why", "for"}
    sozlar = matn_l.split()
    if sum(1 for s in sozlar if s in ingliz) > 2:
        return False
    
    # O'zbek lotin belgilari bor-yo'qligi
    oz_lotin = "o'g'"
    if not any(b in matn_l for b in "abcdeghijklmnopqrstuvxyz"):
        return False
    
    return True

# ============================================================
# FAYLGA SAQLASH
# ============================================================
def faylga_saqla(matn, mavzu=""):
    try:
        os.makedirs(os.path.dirname(LATIFA_FAYL), exist_ok=True)
        vaqt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(LATIFA_FAYL, "a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 50}\n")
            f.write(f"📅 {vaqt}")
            if mavzu:
                f.write(f"  |  🎯 {mavzu}")
            f.write(f"\n{'=' * 50}\n😂 {matn}\n")
        return True
    except Exception as e:
        print(f"⚠️ Fayl: {e}")
        return False

def fayldagi_soni():
    if not os.path.exists(LATIFA_FAYL): return 0
    try:
        with open(LATIFA_FAYL, "r", encoding="utf-8") as f:
            return f.read().count("😂")
    except: return 0

def fayldan_oqi(oxirgi=10):
    if not os.path.exists(LATIFA_FAYL): return []
    try:
        with open(LATIFA_FAYL, "r", encoding="utf-8") as f:
            matn = f.read()
        latifalar = []
        for blok in matn.split("=" * 50):
            if "😂" in blok:
                q = blok.split("😂", 1)
                if len(q) > 1: latifalar.append(q[1].strip())
        return latifalar[-oxirgi:]
    except: return []

# ============================================================
# AI LATIFA (O'ZBEK LOTIN + FALLBACK)
# ============================================================
def ai_latifa(mavzu=None):
    if not OPENROUTER_KEY or OPENROUTER_KEY.startswith("BU_"):
        return None, None
    if not mavzu:
        mavzu = random.choice(MAVZULAR)
    
    prompt = (
        f"O'ZBEK TILIDA (LOTIN ALIFBOSIDA) juda kulgili latifa yoz.\n\n"
        f"Mavzu: {mavzu}\n\n"
        f"QAT'IY QOIDALAR:\n"
        f"1. FAQAT O'ZBEK LOTIN alifbosida yoz\n"
        f"2. RUS, INGLIZ, ARAB, KIRILL yozuvida YOZMA!\n"
        f"3. 3 gapdan oshmasin\n"
        f"4. Juda kulgili bo'lsin\n"
        f"5. Kirish so'zsiz, to'g'ridan-to'g'ri latifa\n\n"
        f"NAMUNALAR:\n"
        f"- Onam: 'Dars qildingmi?' Men: 'Ha' Onam: 'Nega daftar bo'sh?'\n"
        f"- Programmist: 'Kodim ishlayapti!' Do'stim: 'Nega xato yoq?'\n"
        f"- Turnikda 32 marta tortilaman. Do'stim: 'Qanday?' Men: 'Odatlandim!'"
    )
    
    sys_prompt = (
        "Sen o'zbek hazil ustasisan. "
        "FAQAT o'zbek lotin alifbosida yozasan. "
        "Rus, ingliz, arab yozuvida yozish TAQIQLANGAN. "
        "Kirill alifbosi ham TAQIQLANGAN. "
        "Har bir javob faqat o'zbek lotinchada bo'lishi shart."
    )
    
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}",
               "Content-Type": "application/json",
               "HTTP-Referer": "https://blip.local",
               "X-Title": "Blip Funny Bot"}
    
    for model in MODELLAR:
        data = {"model": model,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}],
                "temperature": 1.3, "max_tokens": 250}
        try:
            req = urllib.request.Request(AI_URL,
                data=json.dumps(data).encode(),
                headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=25) as r:
                j = json.loads(r.read().decode())
            matn = j["choices"][0]["message"]["content"]
            if not matn: continue
            matn = matn.strip().replace("```", "").strip().strip('"').strip("'")
            
            # Tilni tekshirish
            if not til_tekshir(matn):
                print(f"⚠️ {model}: noto'g'ri til, keyingisi...")
                continue
            
            KESH.append({"mavzu": mavzu, "matn": matn})
            if len(KESH) > 50: KESH.pop(0)
            return matn, mavzu
        except Exception as e:
            print(f"⚠️ {model}: {e}")
            continue
    
    if KESH:
        item = random.choice(KESH)
        return item["matn"], item["mavzu"]
    return None, None

def sevimli_qosh(uid, matn, mavzu=""):
    u = str(uid)
    SEVIMLILAR.setdefault(u, [])
    if matn not in SEVIMLILAR[u]:
        SEVIMLILAR[u].append(matn)
        if len(SEVIMLILAR[u]) > 30: SEVIMLILAR[u].pop(0)
    return faylga_saqla(matn, mavzu)

def sevimli_ol(uid):
    return SEVIMLILAR.get(str(uid), [])

# ============================================================
# 1) TERMINAL
# ============================================================
def terminal_rejim():
    G="\033[92m"; Y="\033[93m"; R="\033[91m"; B="\033[94m"
    C="\033[96m"; W="\033[97m"; RST="\033[0m"
    print(f"\n{B}{'='*55}{RST}")
    print(f"{W}  😂 BLIP KULGILI BOT — TERMINAL{RST}")
    print(f"{B}{'='*55}{RST}")
    while True:
        print(f"\n  [1] 😂 Latifa         [2] 🎯 Mavzu bilan")
        print(f"  [3] ❤️  Fayldan o'qish [4] 📊 Statistika")
        print(f"  [0] 🚪 Chiqish")
        t = input(f"{Y}Tanlang: {RST}").strip()
        if t == "0":
            print(f"\n{G}👋 Xayr, kulgichi!{RST}\n"); break
        elif t == "1":
            print(f"{Y}{random.choice(KUTISH)}{RST}")
            n, m = ai_latifa()
            if n:
                print(f"\n{W}{random.choice(BAYROQLAR)} [{m}]\n\n{n}{RST}")
                s = input(f"\n{C}❤️ Saqlash? (h/y): {RST}").strip().lower()
                if s == "h":
                    if sevimli_qosh("terminal", n, m):
                        print(f"{G}❤️ Saqlandi: {LATIFA_FAYL}{RST}")
                        print(f"{G}{random.choice(TABRIK)}{RST}")
                    else:
                        print(f"{R}❌ Saqlashda xato!{RST}")
            else:
                print(f"{R}{random.choice(KULGILI_XATO)}{RST}")
        elif t == "2":
            for i, m in enumerate(MAVZULAR, 1):
                print(f"  {i:>2}. {m}")
            try:
                idx = int(input(f"{Y}Raqam: {RST}").strip()) - 1
                if not (0 <= idx < len(MAVZULAR)):
                    print(f"{R}❌ Bunday raqam yo'q!{RST}"); continue
                mavzu = MAVZULAR[idx]
            except:
                print(f"{R}❌ Raqam kiriting! 😅{RST}"); continue
            print(f"{Y}{random.choice(KUTISH)}{RST}")
            n, m = ai_latifa(mavzu)
            if n:
                print(f"\n{W}{random.choice(BAYROQLAR)} [{m}]\n\n{n}{RST}")
                s = input(f"\n{C}❤️ Saqlash? (h/y): {RST}").strip().lower()
                if s == "h":
                    if sevimli_qosh("terminal", n, m):
                        print(f"{G}❤️ Saqlandi!{RST}")
            else:
                print(f"{R}{random.choice(KULGILI_XATO)}{RST}")
        elif t == "3":
            items = fayldan_oqi(10)
            if not items:
                print(f"{Y}📭 Fayl bo'sh: {LATIFA_FAYL}{RST}")
            else:
                print(f"\n{W}❤️ Fayldagi latifalar ({fayldagi_soni()} ta):{RST}")
                for i, m in enumerate(items, 1):
                    print(f"\n  {i}. {m}")
        elif t == "4":
            print(f"\n{W}📊 Statistika:{RST}")
            print(f"  💾 Faylda:  {fayldagi_soni()} ta latifa")
            print(f"  🧠 RAM da:  {len(KESH)} ta latifa")
            print(f"  📁 Fayl:    {LATIFA_FAYL}")
        else:
            print(f"{R}❌ Nima dediz? 😅{RST}")

# ============================================================
# 2) BRAUZER
# ============================================================
HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>😂 Blip Kulgili Bot</title>
<style>
body{font-family:sans-serif;background:#111;color:#eee;padding:20px;max-width:600px;margin:auto}
h1{color:#FF9800;text-align:center}
.card{background:#222;padding:25px;border-radius:15px;margin:15px 0;border-left:5px solid #FF9800}
.btn{background:#FF9800;color:#fff;border:none;padding:16px;border-radius:10px;font-size:18px;cursor:pointer;margin:5px;width:100%;font-weight:bold}
.btn2{background:#2196F3}
.btn3{background:#E91E63}
.joke{font-size:20px;line-height:1.7;white-space:pre-wrap;min-height:80px}
.loading{color:#FF9800}
</style></head><body>
<h1>😂 Kulgili Bot</h1>
<div class="card"><div class="joke" id="j">Tugmani bos! AI seni kuldiradi! 😂</div></div>
<button class="btn" onclick="f('/api/latifa')">😂 KULDIR MENI!</button>
<button class="btn btn3" onclick="saqla()">💾 FAYLGA SAQLA</button>
<button class="btn btn2" onclick="f('/api/sevimli')">❤️ Saqlanganlar</button>
<script>
let ox='';
function f(u){let j=document.getElementById('j');j.className='joke loading';j.innerText='⏳ AI o\\'ylayapti...';fetch(u).then(r=>r.text()).then(t=>{j.className='joke';j.innerText=t;if(u=='/api/latifa')ox=t})}
function saqla(){if(!ox){alert('Avval latifa oling!');return}fetch('/api/saqla?m='+encodeURIComponent(ox)).then(r=>r.text()).then(t=>alert(t))}
</script></body></html>"""

class WebHandler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path in ("/", "/index.html"): self.html(HTML)
        elif self.path == "/api/latifa":
            n, m = ai_latifa()
            b = random.choice(BAYROQLAR)
            self.txt(f"{b} [{m}]\n\n{n}" if n else random.choice(KULGILI_XATO))
        elif self.path.startswith("/api/saqla"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            m = q.get("m", [""])[0]
            if m and faylga_saqla(m):
                self.txt(f"✅ Faylga saqlandi!\n📁 {LATIFA_FAYL}")
            else:
                self.txt("❌ Saqlashda xato!")
        elif self.path == "/api/sevimli":
            items = fayldan_oqi(10)
            if not items: self.txt("📭 Fayl bo'sh!")
            else:
                t = f"❤️ Fayldagi latifalar ({fayldagi_soni()} ta):\n\n"
                for i, m in enumerate(items, 1): t += f"{i}. {m}\n\n"
                self.txt(t)
        else:
            self.send_response(404); self.end_headers()
    def txt(self, m):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers(); self.wfile.write(m.encode())
    def html(self, m):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers(); self.wfile.write(m.encode())

def brauzer_rejim():
    print(f"\n🌐 BRAUZER: http://127.0.0.1:{PORT}")
    print(f"📁 Fayl: {LATIFA_FAYL}")
    print(f"⛔ Ctrl+C\n")
    try:
        HTTPServer(("0.0.0.0", PORT), WebHandler).serve_forever()
    except KeyboardInterrupt: print("\n👋 To'xtatildi")
    except Exception as e: print(f"❌ {e}")

# ============================================================
# 3) TELEGRAM
# ============================================================
def telegram_rejim():
    try:
        import telebot
        from telebot import types
    except ImportError:
        print("❌ pip install pyTelegramBotAPI"); return
    if BOT_TOKEN.startswith("BU_"):
        print("❌ BOT_TOKEN!"); return
    bot = telebot.TeleBot(BOT_TOKEN)

    def yubor(chat_id, matn, mavzu):
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("🔁 Yana", callback_data="y"),
            types.InlineKeyboardButton("🎯 Mavzu", callback_data="m"),
            types.InlineKeyboardButton("💾 Saqlash", callback_data=f"s:{matn[:80]}|{mavzu}")
        )
        bot.send_message(chat_id,
            f"{random.choice(BAYROQLAR)} *[{mavzu}]*\n\n{matn}",
            reply_markup=kb, parse_mode="Markdown")

    @bot.message_handler(commands=["start"])
    def s(msg):
        bot.send_message(msg.chat.id,
            "😂 *Blip Kulgili Bot*\n\n"
            "AI o'zbek tilida latifa to'qiydi!\n\n"
            "📋 /latifa /mavzu /sevimli /kesh /help",
            parse_mode="Markdown")

    @bot.message_handler(commands=["help"])
    def h(msg):
        bot.send_message(msg.chat.id,
            "📖 *Yordam*\n\n"
            "/latifa — tasodifiy hazil\n"
            "/mavzu — mavzu tanlash\n"
            "/sevimli — fayldagi latifalar\n"
            "/kesh — statistika\n\n"
            f"💾 Fayl: `{LATIFA_FAYL}`",
            parse_mode="Markdown")

    @bot.message_handler(commands=["latifa"])
    def l(msg):
        bot.send_message(msg.chat.id, random.choice(KUTISH))
        n, m = ai_latifa()
        if n: yubor(msg.chat.id, n, m)
        else: bot.send_message(msg.chat.id, random.choice(KULGILI_XATO))

    @bot.message_handler(commands=["mavzu"])
    def mv(msg):
        kb = types.InlineKeyboardMarkup(row_width=2)
        t = [types.InlineKeyboardButton(text=m, callback_data=f"m:{i}")
             for i, m in enumerate(MAVZULAR)]
        kb.add(*t)
        bot.send_message(msg.chat.id, "🎯 *Mavzuni tanlang:*",
                         reply_markup=kb, parse_mode="Markdown")

    @bot.message_handler(commands=["sevimli"])
    def sv(msg):
        items = fayldan_oqi(10)
        if not items:
            bot.send_message(msg.chat.id, "📭 Fayl bo'sh!"); return
        t = f"❤️ *Fayldagi latifalar ({fayldagi_soni()} ta):*\n\n"
        for i, m in enumerate(items, 1): t += f"{i}. {m}\n\n"
        bot.send_message(msg.chat.id, t, parse_mode="Markdown")

    @bot.message_handler(commands=["kesh"])
    def ksh(msg):
        bot.send_message(msg.chat.id,
            f"📊 Faylda: *{fayldagi_soni()}*\nRAM: *{len(KESH)}*\n📁 `{LATIFA_FAYL}`",
            parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda c: True)
    def cb(call):
        if call.data == "y":
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            bot.send_message(call.message.chat.id, random.choice(KUTISH))
            n, m = ai_latifa()
            if n: yubor(call.message.chat.id, n, m)
            else: bot.send_message(call.message.chat.id, random.choice(KULGILI_XATO))
        elif call.data == "m":
            kb = types.InlineKeyboardMarkup(row_width=2)
            t = [types.InlineKeyboardButton(text=m, callback_data=f"m:{i}")
                 for i, m in enumerate(MAVZULAR)]
            kb.add(*t)
            bot.send_message(call.message.chat.id, "🎯 *Mavzuni tanlang:*",
                             reply_markup=kb, parse_mode="Markdown")
        elif call.data.startswith("m:"):
            idx = int(call.data.split(":")[1])
            mavzu = MAVZULAR[idx]
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            bot.send_message(call.message.chat.id,
                f"⏳ AI *{mavzu}* haqida o'ylayapti... 😂",
                parse_mode="Markdown")
            n, m = ai_latifa(mavzu)
            if n: yubor(call.message.chat.id, n, m)
            else: bot.send_message(call.message.chat.id, random.choice(KULGILI_XATO))
        elif call.data.startswith("s:"):
            qism = call.data[2:].split("|", 1)
            matn = qism[0]
            mavzu = qism[1] if len(qism) > 1 else ""
            if faylga_saqla(matn, mavzu):
                bot.answer_callback_query(call.id, "💾 Faylga saqlandi!")
            else:
                bot.answer_callback_query(call.id, "❌ Xato!")

    print(f"\n🤖 TELEGRAM tayyor! /start bosing")
    print(f"📁 Fayl: {LATIFA_FAYL}")
    print(f"⛔ Ctrl+C\n")
    try: bot.infinity_polling(timeout=30)
    except KeyboardInterrupt: print("\n👋 To'xtatildi")

# ============================================================
# LAUNCHER
# ============================================================
def menyu():
    while True:
        print(f"""
╔════════════════════════════════════╗
║  😂 BLIP KULGILI BOT v3.0          ║
║  🇺🇿 Faqat o'zbek lotin            ║
║  💾 Saqlash: latifa.txt            ║
╠════════════════════════════════════╣
║  [1] 💻 Terminal rejimi            ║
║  [2] 🌐 Brauzer rejimi             ║
║  [3] 🤖 Telegram bot               ║
║  [0] 🚪 Chiqish                    ║
╚════════════════════════════════════╝""")
        t = input("Tanlang: ").strip()
        if t == "1": terminal_rejim()
        elif t == "2": brauzer_rejim()
        elif t == "3": telegram_rejim()
        elif t == "0":
            print("\n👋 Xayr, kulgichi! 😂\n"); break
        else: print("❌ Nima dediz? 😅")

if __name__ == "__main__":
    os.system("clear" if os.name != "nt" else "cls")
    print("\n😂 BLIP KULGILI BOT v3.0")
    print(f"🇺🇿 Til: Faqat o'zbek lotin")
    print(f"🤖 {len(MODELLAR)} ta fallback model")
    print(f"📚 {len(MAVZULAR)} ta mavzu")
    print(f"💾 Fayl: {LATIFA_FAYL}")
    print(f"📊 Fayldagi latifalar: {fayldagi_soni()} ta")
    ai_h = "✅" if OPENROUTER_KEY and not OPENROUTER_KEY.startswith("BU_") else "❌"
    print(f"🧠 AI: {ai_h}")
    if ai_h == "❌": print("\n⚠️  OPENROUTER_KEY ni to'ldiring!")
    input("\n▶️  Enter...")
    menyu()