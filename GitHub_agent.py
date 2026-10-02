# ============================================================
# 🚀 BLIP GITHUB AGENT v6.0 — Flask + Webhook (Render)
# ============================================================
import os, json, time, base64, re, datetime
import urllib.request, urllib.parse, urllib.error
from flask import Flask, request

# ============================================================
# ⚙️ SOZLAMALAR
# ============================================================
BOT_TOKEN = os.environ.get("GH_BOT_TOKEN", "")
GITHUB_TOKEN = os.environ.get("GH_TOKEN", "")
GITHUB_USER = os.environ.get("GH_USER", "Dasturchi-top-1")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "")
MAXFIY_PAROL = os.environ.get("GH_PAROL", "Blipzor921324")

MAX_URINISH = 3
SESSIYA_VAQTI = 30 * 24 * 3600
STATE_FILE = "gh_state.json"
SESS_FILE = "gh_sessions.json"
LOG_FILE = "gh_agent.log"
PROMPT_FILE = "readme_prompt.txt"

AI_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODELS = [
    "google/gemini-2.5-flash-lite",
    "openai/gpt-4o-mini",
]

app = Flask(__name__)
ADMIN_ID = [0]

# ============================================================
# 📝 PROMPTLAR
# ============================================================
DEFAULT_PROMPT = """Sen professional README.md yozuvchisan.
Har bir loyihaga MOS, chiroyli va professional README yozasan.

QOIDALAR:
1. Har doim O'ZBEK TILIDA (lotin alifbosida) yoz
2. Markdown formatida yoz
3. Emoji ishlat
4. Kod bloklarini ``` bilan o'ra
5. Muallif: Salohiddin (Blip), 13 yosh, Tojikiston

MAJBURIY BO'LIMLAR:
- # [Loyiha nomi] (sarlavha + emoji)
- Qisqa tavsif (2 gap)
- ## ✨ Xususiyatlar
- ## 🛠 Texnologiyalar
- ## 🚀 O'rnatish (kod blok)
- ## 🎯 Foydalanish
- ## 👤 Muallif — Salohiddin (Blip)
- ## 📜 Litsenziya — MIT

FAQAT README matnini qaytar."""

INTENT_PROMPT = """Sen intent parser. Foydalanuvchi xabaridan niyatni JSON da aniqlaysan.

MUMKIN: readme_create, stats, repos, prompt_set, prompt_show, prompt_reset, help, chat

QOIDALAR:
- "barcha","hammasi" → readme_create, repo: "barcha"
- "promptni o'zgartir","yangi prompt" → prompt_set, prompt: <matn>
- "prompt qanday","promptni ko'rsat" → prompt_show
- "standart prompt" → prompt_reset
- aniq repo nomi → readme_create, repo: <nom>
- "stat","statistika" → stats
- "repolar","loyihalar" → repos
- boshqa → chat

FAQAT JSON. Internet haqida gapirma.

MISOLLAR:
"Barcha loyihalar uchun README" → {"intent":"readme_create","repo":"barcha"}
"RasmAI uchun README" → {"intent":"readme_create","repo":"RasmAI"}
"Prompt qanday?" → {"intent":"prompt_show"}
"Salom" → {"intent":"chat","javob":"Salom! Men Blip GitHub Agent."}
"""

SYSTEM_PROMPT = (
    "Sen BLIP GITHUB AGENT yordamchisisan. "
    "Har doim O'ZBEK TILIDA (lotin) qisqa javob ber. "
    "Internet haqida gapirma."
)

# ============================================================
# 🛡 MAXFIY TOZALASH
# ============================================================
XAVFLI = [
    (r"(?i)(password|parol|pwd)\s*[:=]\s*\S+", "[PAROL]"),
    (r"ghp_[A-Za-z0-9]{20,}", "[GH_TOKEN]"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "[GH_TOKEN]"),
    (r"sk-or-v1-[A-Za-z0-9-]{20,}", "[OR_KEY]"),
    (r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b", "[BOT]"),
]

def maxfiy_tozala(m):
    if not m: return ""
    for p, a in XAVFLI: m = re.sub(p, a, m)
    return m

# ============================================================
# 📝 LOG
# ============================================================
def log(m):
    try:
        if BOT_TOKEN: m = m.replace(BOT_TOKEN, "[T]")
        if GITHUB_TOKEN: m = m.replace(GITHUB_TOKEN, "[G]")
        if OPENROUTER_KEY: m = m.replace(OPENROUTER_KEY, "[K]")
        v = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{v}] {m}\n")
    except: pass
    print(m)

# ============================================================
# 📝 PROMPT FAYL
# ============================================================
def prompt_oqi():
    if not os.path.exists(PROMPT_FILE):
        try:
            with open(PROMPT_FILE, "w", encoding="utf-8") as f:
                f.write(DEFAULT_PROMPT)
        except: pass
        return DEFAULT_PROMPT
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            m = f.read().strip()
        return m if m else DEFAULT_PROMPT
    except: return DEFAULT_PROMPT

def prompt_yoz(m):
    try:
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write(m)
        return True
    except: return False

# ============================================================
# 🔐 SESSIYA
# ============================================================
_SESS = {}

def load_sess():
    if not os.path.exists(SESS_FILE): return {}
    try:
        with open(SESS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_sess(s):
    try:
        with open(SESS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False)
    except: pass

def sess_bor(cid):
    k = str(cid); h = time.time()
    if k in _SESS and h - _SESS[k].get("v", 0) < SESSIYA_VAQTI:
        _SESS[k]["v"] = h; return True
    s = load_sess()
    if k in s and h - s[k].get("v", 0) < SESSIYA_VAQTI:
        _SESS[k] = s[k]; _SESS[k]["v"] = h; return True
    return False

def sess_yarat(cid):
    k = str(cid); _SESS[k] = {"v": time.time(), "u": 0}
    s = load_sess(); s[k] = _SESS[k]; save_sess(s)

def sess_ochir(cid):
    k = str(cid); _SESS.pop(k, None)
    s = load_sess(); s.pop(k, None); save_sess(s)

def urinsh(cid):
    k = str(cid)
    if k not in _SESS: _SESS[k] = {"v": time.time(), "u": 0}
    _SESS[k]["u"] = _SESS[k].get("u", 0) + 1
    s = load_sess(); s[k] = _SESS[k]; save_sess(s)
    return _SESS[k]["u"]

# ============================================================
# 📤 TELEGRAM
# ============================================================
def tg(method, params=None, timeout=35):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        if params:
            d = urllib.parse.urlencode(params).encode()
            req = urllib.request.Request(url, data=d, method="POST")
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        log(f"⚠️ TG: {e}"); return None

def send(cid, text):
    if not text or not cid: return
    for i in range(0, len(text), 4000):
        tg("sendMessage", {"chat_id": cid, "text": text[i:i+4000]})
        if len(text) > 4000: time.sleep(0.3)

def typing(cid):
    tg("sendChatAction", {"chat_id": cid, "action": "typing"})

# ============================================================
# 🤖 AI
# ============================================================
def ai_req(model, sys_p, user, timeout=60):
    if not OPENROUTER_KEY: return None
    payload = {"model": model, "messages": [
        {"role": "system", "content": sys_p},
        {"role": "user", "content": user}],
        "temperature": 0.7, "max_tokens": 2000}
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(AI_URL, data=data, headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"⚠️ AI: {e}"); return None

def ai_ask(sys_p, user):
    for m in AI_MODELS:
        n = ai_req(m, sys_p, user)
        if n: return n
        time.sleep(0.3)
    return None

def intent_aniqla(text):
    j = ai_ask(INTENT_PROMPT, text)
    if not j: return None
    try:
        if "```" in j:
            j = j.split("```")[1]
            if j.startswith("json"): j = j[4:]
        s, e = j.find("{"), j.rfind("}") + 1
        if s >= 0 and e > s: return json.loads(j[s:e])
    except: pass
    return None

# ============================================================
# 🐙 GITHUB API
# ============================================================
def gh_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "BlipGitHubAgent",
    }

def gh_get(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers=gh_headers())
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code != 404: log(f"⚠️ GH {e.code}")
        return None
    except Exception as e:
        log(f"⚠️ GH: {e}"); return None

def gh_put(url, data, timeout=30):
    try:
        req = urllib.request.Request(
            url, data=json.dumps(data).encode(),
            headers={**gh_headers(), "Content-Type": "application/json"},
            method="PUT")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        log(f"⚠️ PUT {e.code}: {e.read().decode()[:100]}")
        return None
    except Exception as e:
        log(f"⚠️ PUT: {e}"); return None

def gh_user_info():
    return gh_get(f"https://api.github.com/users/{GITHUB_USER}")

def gh_repos():
    return gh_get(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100")

def gh_repo_exists(repo):
    return gh_get(f"https://api.github.com/repos/{GITHUB_USER}/{repo}") is not None

def gh_get_file(repo, path):
    return gh_get(f"https://api.github.com/repos/{GITHUB_USER}/{repo}/contents/{path}")

def gh_create_file(repo, path, content, message):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/contents/{path}"
    sha = None
    ex = gh_get_file(repo, path)
    if ex and "sha" in ex: sha = ex["sha"]
    data = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }
    if sha: data["sha"] = sha
    return gh_put(url, data)

# ============================================================
# 📝 README YARATISH
# ============================================================
def readme_yarat_ai(repo, desc, til):
    custom = prompt_oqi()
    user_prompt = (
        f"Loyiha uchun README.md yoz:\n\n"
        f"📦 REPO: {repo}\n"
        f"📄 TAVSIF: {desc}\n"
        f"🛠 TIL: {til}\n\n"
        f"Markdown formatida, emoji bilan. "
        f"FAQAT README matnini qaytar."
    )
    return ai_ask(custom, user_prompt)

def barcha_readme(cid):
    send(cid, "⏳ Repolar olinmoqda...")
    repos = gh_repos() or []
    if not repos:
        send(cid, "❌ Repolar topilmadi"); return

    kerakli = []
    send(cid, f"🔍 {len(repos)} repo tekshirilmoqda...")
    for r in repos:
        nomi = r.get("name", "")
        if not nomi: continue
        if not gh_get_file(nomi, "README.md"):
            kerakli.append({
                "nom": nomi,
                "til": r.get("language") or "Python",
                "desc": r.get("description") or f"{nomi} loyihasi"
            })

    send(cid, f"✅ Tekshirildi: {len(repos)}\n❌ README yo'q: {len(kerakli)}")

    if not kerakli:
        send(cid, f"🎉 Barcha {len(repos)} repoda README bor!")
        return

    send(cid, f"\n📦 Hozir: {len(kerakli[:10])} ta\n🚀 Boshlanmoqda...")

    muvaffaqiyat = 0
    xato = []
    for i, info in enumerate(kerakli[:10], 1):
        repo = info["nom"]
        typing(cid)
        send(cid, f"📝 [{i}/{len(kerakli[:10])}] {repo}...")

        readme = readme_yarat_ai(repo, info["desc"], info["til"])
        if not readme:
            send(cid, "  ❌ AI xato")
            xato.append(repo)
            continue

        natija = gh_create_file(repo, "README.md", readme,
                                 f"📝 Add README.md — Blip auto")
        if natija:
            muvaffaqiyat += 1
            url = f"https://github.com/{GITHUB_USER}/{repo}"
            send(cid, f"  ✅ Saqlandi\n  🔗 {url}")
        else:
            xato.append(repo)
            send(cid, "  ❌ GitHub xato")
        time.sleep(1)

    send(cid,
        f"\n{'='*30}\n✅ TUGADI!\n{'='*30}\n\n"
        f"✅ Saqlandi: {muvaffaqiyat}\n"
        f"❌ Xato: {len(xato)}\n"
        f"⏳ Qoldi: {len(kerakli) - len(kerakli[:10])}\n\n"
        f"🌐 https://github.com/{GITHUB_USER}")

def bitta_readme(cid, repo):
    if repo.lower() in ("barcha", "hammasi", "all", "hamma"):
        barcha_readme(cid); return

    send(cid, f"⏳ {repo} tekshirilmoqda...")
    if not gh_repo_exists(repo):
        repos = gh_repos() or []
        nomlar = [r.get("name", "") for r in repos]
        m = f"❌ Repo topilmadi: {repo}\n\n"
        if nomlar:
            m += "📚 Sizning repolaringiz:\n"
            for n in nomlar[:10]: m += f"   • {n}\n"
        send(cid, m); return

    send(cid, "🤖 README yaratilmoqda...")
    readme = readme_yarat_ai(repo, f"{repo} loyihasi", "Python")
    if not readme:
        send(cid, "❌ AI README yarata olmadi"); return

    send(cid, "📤 GitHub'ga yuborilmoqda...")
    natija = gh_create_file(repo, "README.md", readme, f"📝 Add README — {repo}")
    if not natija:
        send(cid, "❌ GitHub'ga yuborilmadi"); return

    url = f"https://github.com/{GITHUB_USER}/{repo}"
    send(cid, f"✅ README YARATILDI!\n\n📦 {repo}\n🌐 {url}\n\n"
              f"📖 README:\n\n{readme[:2500]}")

# ============================================================
# 📊 STATISTIKA
# ============================================================
def stats_yubor(cid):
    user = gh_user_info()
    if not user:
        send(cid, "❌ GitHub ulanmadi"); return
    repos = gh_repos() or []
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)
    m = (f"📊 GITHUB STATISTIKA\n{'='*30}\n\n"
         f"👤 @{GITHUB_USER}\n\n"
         f"⭐ Yulduzlar: {stars}\n"
         f"🍴 Forklar: {forks}\n"
         f"👥 Followers: {user.get('followers', 0)}\n"
         f"📚 Repolar: {len(repos)}\n")
    top = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:5]
    if top:
        m += f"\n🏆 TOP 5:\n"
        for i, r in enumerate(top, 1):
            m += f"{i}. {r.get('name')}\n   ⭐ {r.get('stargazers_count', 0)}\n"
    send(cid, m)

def repos_yubor(cid):
    repos = gh_repos() or []
    if not repos:
        send(cid, "📭 Repolar yo'q"); return
    m = f"📚 REPOLAR ({len(repos)} ta)\n{'='*30}\n\n"
    top = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)
    for i, r in enumerate(top[:20], 1):
        m += (f"{i}. {r.get('name')}\n"
              f"   ⭐ {r.get('stargazers_count', 0)} "
              f"💻 {r.get('language') or '—'}\n")
    send(cid, m)

# ============================================================
# 💬 XABAR
# ============================================================
def xabar(cid, text):
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lstrip("/").split("@")[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""
        if cmd == "start": cmd_start(cid)
        elif cmd == "help": cmd_help(cid)
        elif cmd == "prompt": cmd_prompt(cid)
        elif cmd == "setprompt":
            if args: cmd_setprompt(cid, args)
            else: send(cid, "❌ /setprompt <matn>")
        elif cmd == "resetprompt": cmd_resetprompt(cid)
        elif cmd == "stat": stats_yubor(cid)
        elif cmd == "repos": repos_yubor(cid)
        elif cmd == "logout": logout(cid)
        else: send(cid, "❓ /help bosing.")
        return

    typing(cid)
    it = intent_aniqla(text)
    if not it:
        j = ai_ask(SYSTEM_PROMPT, text)
        send(cid, j or "Tushunmadim. /help"); return
    t = it.get("intent", "chat")

    if t == "prompt_set":
        y = it.get("prompt", "")
        if y and len(y) >= 30:
            prompt_yoz(y)
            send(cid, f"✅ PROMPT SAQLANDI!\n\n📝 {len(y)} belgi\n\n"
                      f"💡 Tekshirish: 'barcha readme'")
        else:
            send(cid, "❌ Prompt juda qisqa (30+ belgi)")
    elif t == "prompt_show":
        p = prompt_oqi()
        send(cid, f"📝 JORIY PROMPT\n{'─'*35}\n\n{p[:3500]}\n\n"
                  f"{'─'*35}\n📊 {len(p)} belgi")
    elif t == "prompt_reset":
        prompt_yoz(DEFAULT_PROMPT)
        send(cid, "✅ Standart prompt tiklandi!")
    elif t == "readme_create":
        repo = it.get("repo", "")
        if repo: bitta_readme(cid, repo)
        else: send(cid, "❌ Repo nomi yo'q")
    elif t == "stats": stats_yubor(cid)
    elif t == "repos": repos_yubor(cid)
    elif t == "help": cmd_help(cid)
    else:
        j = it.get("javob", "") or ai_ask(SYSTEM_PROMPT, text)
        send(cid, j or "Tushunmadim")

# ============================================================
# 💬 BUYRUQLAR
# ============================================================
def cmd_start(cid):
    send(cid, "🚀 BLIP GITHUB AGENT v6.0\n\n"
              "Men buyruqsiz ishlayman!\n\n"
              "📝 \"RasmAI uchun README\"\n"
              "📦 \"barcha readme\"\n"
              "📊 \"statistika\"\n"
              "📚 \"repolar\"\n\n"
              "/prompt — Prompt ko'rish\n"
              "/help — Yordam")

def cmd_help(cid):
    send(cid, "📖 YORDAM\n\n"
              "ODDIY MATN:\n"
              "• \"barcha readme\"\n"
              "• \"RasmAI uchun README\"\n"
              "• \"statistika\"\n"
              "• \"repolar\"\n\n"
              "BUYRUQLAR:\n"
              "/prompt — Prompt\n"
              "/setprompt <matn> — Yangilash\n"
              "/resetprompt — Reset\n"
              "/stat — Statistika\n"
              "/repos — Repolar\n"
              "/logout — Chiqish")

def cmd_prompt(cid):
    p = prompt_oqi()
    send(cid, f"📝 JORIY README PROMPT\n{'─'*35}\n\n{p[:3500]}\n\n"
              f"{'─'*35}\n📊 {len(p)} belgi\n\n"
              f"💡 Yangilash: /setprompt <matn>")

def cmd_setprompt(cid, matn):
    if len(matn) < 30:
        send(cid, "❌ Prompt juda qisqa (30+ belgi)"); return
    if prompt_yoz(matn):
        send(cid, f"✅ PROMPT YANGILANDI!\n\n📝 {len(matn)} belgi")
    else:
        send(cid, "❌ Saqlashda xato")

def cmd_resetprompt(cid):
    if prompt_yoz(DEFAULT_PROMPT):
        send(cid, "✅ Standart prompt tiklandi!")

def logout(cid):
    sess_ochir(cid)
    send(cid, "👋 Chiqdingiz!\n\nQayta: /start")

def parol_ol(cid, matn):
    if matn.strip() == MAXFIY_PAROL:
        sess_yarat(cid)
        send(cid, "✅ PAROL TO'G'RI!\n\nXush kelibsiz, Blip! 🚀\n\n"
                  "/help — Yordam\n\n"
                  "💡 Yoki yozing:\n"
                  "\"barcha readme\"\n"
                  "\"RasmAI uchun README\"")
        return True
    u = urinsh(cid); q = MAX_URINISH - u
    send(cid, f"❌ Parol xato! Qolgan: {q}" if q > 0 else "🚫 Bloklandi! 1 daqiqa")
    if q <= 0:
        time.sleep(60)
        _SESS[str(cid)] = {"v": time.time(), "u": 0}
    return False

# ============================================================
# 🌐 FLASK
# ============================================================
@app.route("/")
def index():
    return "Blip GitHub Agent v6.0 ishlayapti ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        up = request.get_json()
        msg = up.get("message") or up.get("edited_message")
        if not msg or "text" not in msg: return "ok"

        cid = msg["chat"]["id"]
        text = msg["text"].strip()
        ism = msg.get("from", {}).get("first_name", "?")

        if text == "/start":
            sess_ochir(cid)
            send(cid, f"🔐 BLIP GITHUB AGENT v6.0\n\n"
                      f"Salom, {ism}!\nParolni yuboring:\n❌ 3 urinish")
            return "ok"
        if text == "/logout":
            logout(cid); return "ok"
        if text == "/id":
            send(cid, f"🆔 {cid}"); return "ok"

        if not sess_bor(cid):
            parol_ol(cid, text); return "ok"

        if not ADMIN_ID[0]: ADMIN_ID[0] = cid

        try: xabar(cid, text)
        except Exception as e:
            log(f"⚠️ {e}"); send(cid, f"❌ {str(e)[:100]}")
        return "ok"
    except Exception as e:
        log(f"❌ Webhook: {e}"); return "ok"

# ============================================================
# 🏁
# ============================================================
if __name__ == "__main__":
    log("🚀 Blip GitHub Agent v6.0 (Webhook)")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)