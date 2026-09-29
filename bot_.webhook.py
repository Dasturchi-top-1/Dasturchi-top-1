from flask import Flask, request, jsonify
import requests, sqlite3, time, os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "BU_YERGA_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "sk-or-v1-...")
MODEL = "openai/gpt-4o-mini"
DB = "blip_bot.db"
SECRET = os.environ.get("WEBHOOK_SECRET", "blip_webhook_secret")

SYSTEM = """Sen Blip Agent — Telegram bot orqali ishlovchi AI yordamchisan.
Foydalanuvchi: Blip (Salohiddin), Tojikiston, Dushanbe, 13 yosh.
O'zbek tilida (lotin) qisqa va aniq javob ber. Buyruq kutma — oddiy xabarga ham javob ber."""

# ===== BAZA =====
def db_init():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS hist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER, role TEXT, content TEXT, created REAL
    )""")
    con.commit(); con.close()

def db_add(cid, role, content):
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO hist (chat_id,role,content,created) VALUES (?,?,?,?)",
                (cid, role, content, time.time()))
    con.commit(); con.close()

def db_get(cid, limit=20):
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT role,content FROM hist WHERE chat_id=? ORDER BY id DESC LIMIT ?",
                       (cid, limit)).fetchall()
    con.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def db_clear(cid):
    con = sqlite3.connect(DB)
    con.execute("DELETE FROM hist WHERE chat_id=?", (cid,))
    con.commit(); con.close()

db_init()

# ===== AI =====
def call_ai(cid, msg):
    hist = db_get(cid, 20)
    messages = [{"role": "system", "content": SYSTEM}] + hist
    messages.append({"role": "user", "content": msg})

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": "Bearer " + OPENROUTER_KEY,
                 "Content-Type": "application/json"},
        json={"model": MODEL, "messages": messages}, timeout=60
    )
    data = r.json()
    if "choices" not in data:
        return "Xato: " + str(data)[:200]
    reply = data["choices"][0]["message"]["content"]
    db_add(cid, "user", msg)
    db_add(cid, "assistant", reply)
    return reply

# ===== TELEGRAM =====
API = "https://api.telegram.org/bot" + TELEGRAM_TOKEN

def send(cid, text):
    for i in range(0, len(text), 4000):
        try:
            requests.post(API + "/sendMessage",
                json={"chat_id": cid, "text": text[i:i+4000]}, timeout=30)
        except Exception as e:
            print("Send xato:", e)

# ===== WEBHOOK =====
@app.route("/webhook", methods=["POST"])
def webhook():
    # Xavfsizlik tekshiruvi
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET:
        return "Forbidden", 403

    update = request.get_json()
    msg = update.get("message") or update.get("edited_message")
    if not msg or "text" not in msg:
        return "ok", 200

    cid = msg["chat"]["id"]
    text = msg["text"].strip()
    name = msg["chat"].get("first_name", "Blip")

    if text == "/start":
        send(cid, f"Salom {name}! 👋\nMen Blip Agent.\nBuyruq kutma — oddiy yozsang ham tushunaman!")
        return "ok", 200
    if text == "/reset":
        db_clear(cid)
        send(cid, "🧹 Suhbat tarixi tozalandi.")
        return "ok", 200
    if text == "/help":
        send(cid, "/start — salom\n/reset — tozalash\n/help — yordam")
        return "ok", 200

    try:
        reply = call_ai(cid, text)
    except Exception as e:
        reply = "❌ Xato: " + str(e)
    send(cid, reply)
    return "ok", 200

# ===== HEALTH =====
@app.route("/")
def index():
    return "Blip Bot ishlayapti ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))