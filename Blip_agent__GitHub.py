# ============================================================
# 🚀 BLIP GITHUB AGENT v5.0 — 1-QISM
# Fayl: blip_github_agent.py
# Papka: /storage/emulated/0/Ai/GitHubAgent/
# Parol + Prompt via Telegram
# ⚠️ Bu faylni GitHub'ga YUKLAMANG!
# ============================================================
import os, sys, json, time, base64, re, datetime
import urllib.request, urllib.parse, urllib.error

# ============================================================
# ⚠️ TOKENLAR — SHU YERNI TO'LDIRING!
# ============================================================
BOT_TOKEN = "YOUR_TOKEN"
GITHUB_TOKEN = "YOUR_TOKEN"
GITHUB_USER = "Dasturchi-top-1"
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY"

# ============================================================
# 🔐 PAROL
# ============================================================
MAXFIY_PAROL = "Blipzor921324"
MAX_URINISH = 3
SESSIYA_VAQTI = 30 * 24 * 3600

# ============================================================
# SOZLAMALAR
# ============================================================
LOYIHA_PAPKA = "/storage/emulated/0/Ai/GitHubAgent"
os.makedirs(LOYIHA_PAPKA, exist_ok=True)

STATE_FILE = f"{LOYIHA_PAPKA}/agent_state.json"
SESS_FILE = f"{LOYIHA_PAPKA}/sessions.json"
LOG_FILE = f"{LOYIHA_PAPKA}/github_agent.log"
PROMPT_FILE = f"{LOYIHA_PAPKA}/readme_prompt.txt"

CHECK_INTERVAL = 300
DAILY_REPORT_HOUR = 9
MAX_README_BATCH = 10

AI_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODELS = [
    "nex-agi/nex-n2.5-pro:free",
    "nex-agi/nex-n2.5-mini:free",
    "qwen/qwen3.8-27b:free",
]

# ============================================================
# 📝 STANDART PROMPT
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

LOYIHA TURIGA QARAB QO'SHIMCHA:
- Bot → Buyruqlar
- AI → API sozlash
- O'yin → Qoidalar
- Diniy → Manba

FAQAT README matnini qaytar."""

# ============================================================
# 📝 PROMPT BOSHQARUVI
# ============================================================
def prompt_oqi():
    """Promptni fayldan o'qiydi."""
    if not os.path.exists(PROMPT_FILE):
        try:
            with open(PROMPT_FILE, "w", encoding="utf-8") as f:
                f.write(DEFAULT_PROMPT)
        except: pass
        return DEFAULT_PROMPT
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            matn = f.read().strip()
        return matn if matn else DEFAULT_PROMPT
    except:
        return DEFAULT_PROMPT

def prompt_yoz(matn):
    """Promptni saqlaydi."""
    try:
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write(matn)
        return True
    except Exception as e:
        log(f"⚠️ Prompt saqlash: {e}")
        return False

# ============================================================
# 🤖 INTENT PROMPT
# ============================================================
INTENT_PROMPT = """Sen intent parser. Foydalanuvchi xabaridan niyatini JSON formatda aniqlaysan.

MUMKIN NIYATLAR:
1. readme_create — README yaratish (repo yoki 'barcha')
2. readme_update — README yangilash
3. stats — statistika
4. repos — repolar ro'yxati
5. prompt_set — promptni o'zgartirish
6. prompt_show — promptni ko'rsatish
7. prompt_reset — promptni standartga qaytarish
8. help — yordam
9. chat — oddiy suhbat

QOIDALAR:
- "barcha", "hammasi", "hamma" → repo: "barcha"
- "promptni o'zgartir", "yangi prompt", "prompt yangila" → prompt_set
- Agar prompt matni bo'lsa → "prompt" maydoniga yoz
- "prompt qanday", "promptni ko'rsat" → prompt_show
- "standart prompt", "prompt reset" → prompt_reset
- Aniq repo nomi → readme_create
- "stat", "statistika" → stats
- "repolar", "loyihalar" → repos
- Boshqa → chat

FAQAT JSON qaytar.

MISOLLAR:
User: "Barcha loyihalar uchun README yarat"
→ {"intent": "readme_create", "repo": "barcha"}

User: "RasmAI uchun README"
→ {"intent": "readme_create", "repo": "RasmAI"}

User: "Promptni o'zgartir: Sen professional README yozuvchisan. 100+ qator yoz."
→ {"intent": "prompt_set", "prompt": "Sen professional README yozuvchisan. 100+ qator yoz."}

User: "Prompt qanday?"
→ {"intent": "prompt_show"}

User: "Statistikam qanday?"
→ {"intent": "stats"}

User: "Salom"
→ {"intent": "chat", "javob": "Salom! Men Blip GitHub Agent."}
"""

SYSTEM_PROMPT = (
    "Sen BLIP GITHUB AGENT yordamchisisan. "
    "Har doim O'ZBEK TILIDA (lotin) javob ber. Qisqa yoz."
)

# ============================================================
# LOG
# ============================================================
def log(matn):
    try:
        if BOT_TOKEN: matn = matn.replace(BOT_TOKEN, "[TOKEN]")
        if OPENROUTER_KEY: matn = matn.replace(OPENROUTER_KEY, "[KEY]")
        if GITHUB_TOKEN: matn = matn.replace(GITHUB_TOKEN, "[GH_TOKEN]")
        if MAXFIY_PAROL: matn = matn.replace(MAXFIY_PAROL, "[PAROL]")
        vaqt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{vaqt}] {matn}\n")
    except: pass
    print(matn)

def tokenlarni_tekshir():
    xato = []
    if not BOT_TOKEN or BOT_TOKEN.startswith("BU_"): xato.append("BOT_TOKEN")
    if not GITHUB_TOKEN or GITHUB_TOKEN.startswith("BU_"): xato.append("GITHUB_TOKEN")
    if not OPENROUTER_KEY or OPENROUTER_KEY.startswith("BU_"): xato.append("OPENROUTER_KEY")
    if not MAXFIY_PAROL or len(MAXFIY_PAROL) < 6: xato.append("MAXFIY_PAROL")
    if xato:
        print("\n❌ To'ldirilmagan:")
        for x in xato: print(f"   • {x}")
        sys.exit(1)
    print("  ✅ Tokenlar va parol to'ldirilgan")

# ============================================================
# 🔐 SESSIYA
# ============================================================
_SESSIONS_MEM = {}

def load_sessions():
    if not os.path.exists(SESS_FILE): return {}
    try:
        with open(SESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_sessions(s):
    try:
        tmp = SESS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
        os.replace(tmp, SESS_FILE)
        return True
    except: return False

def sessiya_bor(chat_id):
    key = str(chat_id); hozir = time.time()
    if key in _SESSIONS_MEM:
        if hozir - _SESSIONS_MEM[key].get("vaqt", 0) < SESSIYA_VAQTI:
            _SESSIONS_MEM[key]["vaqt"] = hozir
            s = load_sessions(); s[key] = _SESSIONS_MEM[key]; save_sessions(s)
            return True
        del _SESSIONS_MEM[key]
    s = load_sessions()
    if key in s:
        if hozir - s[key].get("vaqt", 0) < SESSIYA_VAQTI:
            _SESSIONS_MEM[key] = s[key]
            _SESSIONS_MEM[key]["vaqt"] = hozir
            s[key]["vaqt"] = hozir; save_sessions(s)
            return True
        del s[key]; save_sessions(s)
    return False

def sessiya_yarat(chat_id):
    key = str(chat_id); hozir = time.time()
    ma = {"vaqt": hozir, "urinsh": 0}
    _SESSIONS_MEM[key] = ma
    s = load_sessions(); s[key] = ma; save_sessions(s)

def sessiya_ochir(chat_id):
    key = str(chat_id)
    _SESSIONS_MEM.pop(key, None)
    s = load_sessions(); s.pop(key, None); save_sessions(s)

def urinsh_oshir(chat_id):
    key = str(chat_id)
    if key not in _SESSIONS_MEM:
        _SESSIONS_MEM[key] = {"vaqt": time.time(), "urinsh": 0}
    _SESSIONS_MEM[key]["urinsh"] = _SESSIONS_MEM[key].get("urinsh", 0) + 1
    s = load_sessions(); s[key] = _SESSIONS_MEM[key]; save_sessions(s)
    return _SESSIONS_MEM[key]["urinsh"]

def parol_tekshir(matn):
    return matn.strip() == MAXFIY_PAROL

# ============================================================
# TELEGRAM API
# ============================================================
def tg_request(method, params=None, timeout=35):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        if params:
            data = urllib.parse.urlencode(params).encode("utf-8")
            req = urllib.request.Request(url, data=data, method="POST")
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        log(f"⚠️ TG: {e}"); return None

def tg_send(chat_id, text, reply_to=None):
    if not text or not chat_id: return False
    if len(text) <= 4000:
        p = {"chat_id": chat_id, "text": text}
        if reply_to: p["reply_to_message_id"] = reply_to
        r = tg_request("sendMessage", p)
        return bool(r and r.get("ok"))
    ok = True
    for i in range(0, len(text), 4000):
        p = {"chat_id": chat_id, "text": text[i:i+4000]}
        r = tg_request("sendMessage", p)
        if not (r and r.get("ok")): ok = False
        time.sleep(0.3)
    return ok

def tg_typing(chat_id):
    tg_request("sendChatAction", {"chat_id": chat_id, "action": "typing"})

def tg_get_updates(offset, timeout=30):
    return tg_request("getUpdates", {
        "timeout": timeout, "offset": offset,
        "allowed_updates": json.dumps(["message"]),
    }, timeout=timeout + 10)
# ============================================================
# 🤖 AI
# ============================================================
def ai_request(model, system, user_text, timeout=60):
    if not OPENROUTER_KEY: return None
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_text}],
        "temperature": 0.7, "max_tokens": 2000,
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            AI_URL, data=data,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://blip.local",
                "X-Title": "Blip GitHub Agent",
            }, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            result = json.loads(r.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"⚠️ AI: {e}"); return None

def ai_ask(system, user_text):
    for model in AI_MODELS:
        natija = ai_request(model, system, user_text)
        if natija: return natija
        time.sleep(0.3)
    return None

def intent_aniqla(text):
    javob = ai_ask(INTENT_PROMPT, text)
    if not javob: return None
    try:
        if "```" in javob:
            javob = javob.split("```")[1]
            if javob.startswith("json"): javob = javob[4:]
            javob = javob.strip()
        start = javob.find("{"); end = javob.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(javob[start:end])
    except Exception as e:
        log(f"⚠️ Intent JSON: {e}")
    return None

# ============================================================
# GITHUB API
# ============================================================
def gh_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "BlipGitHubAgent",
    }

def http_get(url, headers=None, timeout=20):
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code != 404: log(f"⚠️ HTTP {e.code}")
        return None
    except Exception as e:
        log(f"⚠️ GET: {e}"); return None

def http_put(url, data, headers=None, timeout=30):
    try:
        req = urllib.request.Request(
            url, data=json.dumps(data).encode(),
            headers={**(headers or {}), "Content-Type": "application/json"},
            method="PUT")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        log(f"⚠️ PUT {e.code}: {e.read().decode()[:100]}")
        return None
    except Exception as e:
        log(f"⚠️ PUT: {e}"); return None

def gh_user_info():
    return http_get(f"https://api.github.com/users/{GITHUB_USER}",
                    headers=gh_headers())

def gh_repos():
    return http_get(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100",
                    headers=gh_headers())

def gh_repo_exists(repo):
    r = http_get(f"https://api.github.com/repos/{GITHUB_USER}/{repo}",
                 headers=gh_headers())
    return r is not None

def gh_get_file(repo, path):
    return http_get(f"https://api.github.com/repos/{GITHUB_USER}/{repo}/contents/{path}",
                    headers=gh_headers())

def gh_create_file(repo, path, content, message):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/contents/{path}"
    sha = None
    existing = gh_get_file(repo, path)
    if existing and "sha" in existing:
        sha = existing["sha"]
    data = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }
    if sha: data["sha"] = sha
    return http_put(url, data, headers=gh_headers())

# ============================================================
# 📝 README YARATISH
# ============================================================
def readme_matn_yarat(repo, title, description, tech, features):
    """AI orqali loyihaga MOS README yaratadi.
    Prompt fayldan o'qiladi."""
    tech_str = ", ".join(tech) if tech else "Python"
    feat_str = "\n- ".join(features) if features else "Asosiy funksiyalar"
    
    # 🎯 CUSTOM PROMPT — fayldan
    custom_prompt = prompt_oqi()
    
    user_prompt = (
        f"Loyiha uchun README.md yoz:\n\n"
        f"📦 REPO: {repo}\n"
        f"📝 SARLAVHA: {title}\n"
        f"📄 TAVSIF: {description or 'Loyiha haqida'}\n"
        f"🛠 TEXNOLOGIYALAR: {tech_str}\n"
        f"✨ XUSUSIYATLAR:\n- {feat_str}\n\n"
        f"Markdown formatida, emoji bilan yoz. "
        f"FAQAT README matnini qaytar."
    )
    
    return ai_ask(custom_prompt, user_prompt)

def barcha_uchun_readme(chat_id):
    """Barcha repolar uchun README yaratadi."""
    tg_send(chat_id, "⏳ Repolar olinmoqda...")
    repos = gh_repos() or []
    if not repos:
        tg_send(chat_id, "❌ Repolar topilmadi"); return

    kerakli = []
    tg_send(chat_id, f"🔍 {len(repos)} repo tekshirilmoqda...")
    
    for r in repos:
        nomi = r.get("name", "")
        if not nomi: continue
        existing = gh_get_file(nomi, "README.md")
        if not existing:
            kerakli.append({
                "nom": nomi,
                "til": r.get("language") or "Python",
                "desc": r.get("description") or f"{nomi} loyihasi"
            })
    
    tg_send(chat_id,
        f"✅ Tekshirildi: {len(repos)} repo\n"
        f"❌ README yo'q: {len(kerakli)} ta")
    
    if not kerakli:
        tg_send(chat_id, f"🎉 Barcha {len(repos)} repoda README bor!")
        return

    barcha = len(kerakli)
    birinchi = kerakli[:MAX_README_BATCH]

    tg_send(chat_id,
        f"\n📦 Hozir: {len(birinchi)} ta\n"
        f"⏳ Qoldi: {barcha - len(birinchi)} ta\n\n"
        f"🚀 Boshlanmoqda...\n")

    muvaffaqiyat = 0
    xato_repos = []
    
    for i, info in enumerate(birinchi, 1):
        repo = info["nom"]
        til = info["til"]
        desc = info["desc"]
        
        tg_typing(chat_id)
        tg_send(chat_id, f"📝 [{i}/{len(birinchi)}] {repo}...")

        readme = readme_matn_yarat(
            repo,
            repo.replace("_", " ").replace("-", " "),
            desc,
            [til, "Python", "GitHub"],
            ["Dasturlash", "Ochiq kod"])
        
        if not readme:
            tg_send(chat_id, "  ❌ AI xato")
            xato_repos.append(repo)
            continue

        natija = gh_create_file(
            repo, "README.md", readme,
            f"📝 Add README.md — Blip auto")

        if natija:
            muvaffaqiyat += 1
            url = f"https://github.com/{GITHUB_USER}/{repo}"
            tg_send(chat_id, f"  ✅ Saqlandi\n  🔗 {url}")
        else:
            xato_repos.append(repo)
            tg_send(chat_id, "  ❌ GitHub xato")

        time.sleep(2)

    matn = (
        f"\n{'=' * 30}\n"
        f"✅ TUGADI!\n"
        f"{'=' * 30}\n\n"
        f"📊 Natija:\n"
        f"   ✅ Saqlandi: {muvaffaqiyat}\n"
        f"   ❌ Xato: {len(xato_repos)}\n"
        f"   ⏳ Qoldi: {barcha - len(birinchi)}\n\n"
    )
    
    if barcha > len(birinchi):
        matn += f'💡 Yana {barcha - len(birinchi)} ta qoldi.\n'
        matn += f'Qayta yozing: "barcha readme"\n\n'
    
    matn += f"🌐 https://github.com/{GITHUB_USER}"
    tg_send(chat_id, matn)

def readme_yarat(chat_id, repo):
    """Bitta repo uchun README yaratadi."""
    repo_lower = repo.lower().strip()
    if repo_lower in ("barcha", "hammasi", "all", "barchasi",
                      "barcha loyihalar", "barcha repolar", "hamma"):
        barcha_uchun_readme(chat_id)
        return True

    tg_send(chat_id, f"⏳ {repo} tekshirilmoqda...")
    if not gh_repo_exists(repo):
        repos = gh_repos() or []
        nomlar = [r.get("name", "") for r in repos]
        matn = f"❌ Repo topilmadi: {repo}\n\n"
        if nomlar:
            matn += "📚 Sizning repolaringiz:\n"
            for n in nomlar[:10]:
                matn += f"   • {n}\n"
        tg_send(chat_id, matn)
        return False

    tg_send(chat_id, "🤖 README yaratilmoqda...")
    readme = readme_matn_yarat(repo, repo, f"{repo} loyihasi",
                               ["Python"], ["Dasturlash"])
    if not readme:
        tg_send(chat_id, "❌ AI README yarata olmadi")
        return False

    tg_send(chat_id, "📤 GitHub'ga yuborilmoqda...")
    natija = gh_create_file(repo, "README.md", readme,
                            f"📝 Add README.md — {repo}")
    if not natija:
        tg_send(chat_id, "❌ GitHub'ga yuborilmadi")
        return False

    url = f"https://github.com/{GITHUB_USER}/{repo}"
    tg_send(chat_id,
        f"✅ README YARATILDI!\n\n"
        f"📦 Repo: {repo}\n"
        f"🌐 Ko'rish: {url}\n\n"
        f"📖 README:\n\n{readme[:2500]}")
    return True

# ============================================================
# 📊 STATISTIKA
# ============================================================
def stats_yubor(chat_id):
    user = gh_user_info()
    if not user:
        tg_send(chat_id, "❌ GitHub ulanmadi"); return
    repos = gh_repos() or []
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    matn = (f"📊 GITHUB STATISTIKA\n{'=' * 30}\n\n"
            f"👤 @{GITHUB_USER}\n\n"
            f"⭐ Yulduzlar: {total_stars}\n"
            f"🍴 Forklar: {total_forks}\n"
            f"👥 Followers: {user.get('followers', 0)}\n"
            f"📚 Repolar: {len(repos)}\n")
    top = sorted(repos, key=lambda x: x.get("stargazers_count", 0),
                 reverse=True)[:5]
    if top:
        matn += f"\n🏆 TOP 5:\n"
        for i, r in enumerate(top, 1):
            matn += (f"{i}. {r.get('name')}\n"
                     f"   ⭐ {r.get('stargazers_count', 0)} "
                     f"🍴 {r.get('forks_count', 0)}\n")
    tg_send(chat_id, matn)

def repos_yubor(chat_id):
    repos = gh_repos() or []
    if not repos:
        tg_send(chat_id, "📭 Repolar yo'q"); return
    matn = f"📚 REPOLAR ({len(repos)} ta)\n{'=' * 30}\n\n"
    top = sorted(repos, key=lambda x: x.get("stargazers_count", 0),
                 reverse=True)
    for i, r in enumerate(top[:20], 1):
        matn += (f"{i}. {r.get('name')}\n"
                 f"   ⭐ {r.get('stargazers_count', 0)} "
                 f"🍴 {r.get('forks_count', 0)} "
                 f"💻 {r.get('language') or '—'}\n")
    tg_send(chat_id, matn)
# ============================================================
# 💬 XABARNI QAYTA ISHLASH
# ============================================================
def xabar_qayta_ishla(chat_id, text):
    """Buyruq YOKI oddiy matnni qayta ishlaydi."""
    
    # 1. BUYRUQ bo'lsa
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lstrip("/").split("@")[0].lower()
        args_text = parts[1].strip() if len(parts) > 1 else ""
        
        if cmd == "start": cmd_start(chat_id)
        elif cmd == "help": cmd_help(chat_id)
        elif cmd == "prompt": cmd_prompt(chat_id)
        elif cmd == "setprompt":
            if args_text: cmd_setprompt(chat_id, args_text)
            else: tg_send(chat_id, "❌ /setprompt <matn>")
        elif cmd == "resetprompt": cmd_resetprompt(chat_id)
        elif cmd == "stat": stats_yubor(chat_id)
        elif cmd == "repos": repos_yubor(chat_id)
        elif cmd == "logout": logout(chat_id)
        else: tg_send(chat_id, "❓ Buyruq yo'q. /help bosing.")
        return
    
    # 2. ODDIY MATN — AI intent
    tg_typing(chat_id)
    intent = intent_aniqla(text)
    if not intent:
        javob = ai_ask(SYSTEM_PROMPT, text)
        tg_send(chat_id, javob or "Tushunmadim. /help bosing.")
        return
    
    tur = intent.get("intent", "chat")
    
    # 🎯 PROMPT HANDLERLARI
    if tur == "prompt_set":
        yangi = intent.get("prompt", "")
        if yangi and len(yangi) >= 30:
            prompt_yoz(yangi)
            tg_send(chat_id,
                f"✅ PROMPT SAQLANDI!\n\n"
                f"📝 {len(yangi)} belgi\n\n"
                f"Endi README shu prompt bilan yaratiladi.\n\n"
                f"💡 Tekshirish: 'barcha readme'")
            log(f"✅ Prompt: {len(yangi)} belgi")
        else:
            tg_send(chat_id,
                "❌ Prompt juda qisqa (30+ belgi)\n"
                "Yoki matn ko'rsatilmagan.")
        return
    
    elif tur == "prompt_show":
        p = prompt_oqi()
        tg_send(chat_id,
            f"📝 JORIY PROMPT\n{'─' * 35}\n\n"
            f"{p[:3500]}\n\n"
            f"{'─' * 35}\n"
            f"📊 Uzunlik: {len(p)} belgi")
        return
    
    elif tur == "prompt_reset":
        prompt_yoz(DEFAULT_PROMPT)
        tg_send(chat_id, "✅ Standart prompt tiklandi!")
        log("✅ Prompt reset")
        return
    
    elif tur == "readme_create":
        repo = intent.get("repo", "")
        if not repo:
            tg_send(chat_id, "❌ Repo nomi yo'q"); return
        readme_yarat(chat_id, repo)
    
    elif tur == "stats":
        stats_yubor(chat_id)
    
    elif tur == "repos":
        repos_yubor(chat_id)
    
    elif tur == "help":
        cmd_help(chat_id)
    
    elif tur == "chat":
        javob = intent.get("javob", "")
        if not javob:
            javob = ai_ask(SYSTEM_PROMPT, text)
        tg_send(chat_id, javob or "Tushunmadim")
    
    else:
        javob = ai_ask(SYSTEM_PROMPT, text)
        tg_send(chat_id, javob or "Tushunmadim")

# ============================================================
# 💬 BUYRUQLAR
# ============================================================
def cmd_start(chat_id):
    tg_send(chat_id,
        "🚀 BLIP GITHUB AGENT v5.0\n\n"
        "Men buyruqsiz ishlayman! Yozing:\n\n"
        "📝 README yaratish:\n"
        "\"RasmAI uchun README yarat\"\n\n"
        "📦 Barcha repolar:\n"
        "\"barcha readme\"\n\n"
        "📊 Statistika:\n"
        "\"statistika\"\n\n"
        "📚 Repolar:\n"
        "\"repolar\"\n\n"
        "📝 Prompt boshqarish:\n"
        "/prompt — ko'rish\n"
        "/setprompt — yangilash\n"
        "/resetprompt — standart\n\n"
        "/help — To'liq yordam")

def cmd_help(chat_id):
    tg_send(chat_id,
        "📖 YORDAM\n\n"
        "ODDIY MATN:\n"
        "• \"barcha readme\"\n"
        "• \"RasmAI uchun README\"\n"
        "• \"statistika\"\n"
        "• \"repolar\"\n\n"
        "BUYRUQLAR:\n"
        "/prompt — Prompt ko'rish\n"
        "/setprompt <matn> — Yangilash\n"
        "/resetprompt — Reset\n"
        "/stat — Statistika\n"
        "/repos — Repolar\n"
        "/logout — Chiqish\n\n"
        "💡 Prompt yangilash:\n"
        "\"Promptni o'zgartir: [yangi matn]\"")

def cmd_prompt(chat_id):
    p = prompt_oqi()
    tg_send(chat_id,
        f"📝 JORIY README PROMPT\n"
        f"{'─' * 35}\n\n"
        f"{p[:3500]}\n\n"
        f"{'─' * 35}\n"
        f"📊 Uzunlik: {len(p)} belgi\n\n"
        f"💡 Yangilash:\n"
        f"/setprompt <yangi matn>\n"
        f"Yoki: \"Promptni o'zgartir: ...\"")

def cmd_setprompt(chat_id, matn):
    if len(matn) < 30:
        tg_send(chat_id, "❌ Prompt juda qisqa (30+ belgi)")
        return
    if prompt_yoz(matn):
        tg_send(chat_id,
            f"✅ PROMPT YANGILANDI!\n\n"
            f"📝 {len(matn)} belgi\n\n"
            f"Endi README shu prompt bilan yaratiladi.\n\n"
            f"💡 Tekshirish: 'barcha readme'")
        log(f"✅ Prompt: {len(matn)}")
    else:
        tg_send(chat_id, "❌ Saqlashda xato")

def cmd_resetprompt(chat_id):
    if prompt_yoz(DEFAULT_PROMPT):
        tg_send(chat_id, "✅ Standart prompt tiklandi!")
    else:
        tg_send(chat_id, "❌ Xato")

# ============================================================
# 🔐 PAROL
# ============================================================
def start_salom(chat_id, ism):
    tg_send(chat_id,
        f"🔐 BLIP GITHUB AGENT v5.0\n\n"
        f"Salom, {ism}!\n\n"
        f"Bu bot faqat egasi uchun.\n"
        f"Parolni yuboring:\n\n"
        f"❌ 3 urinish\n⏱ Sessiya: 30 kun")

def parol_ol(chat_id, matn):
    if parol_tekshir(matn):
        sessiya_yarat(chat_id)
        s = load_sessions()
        if str(chat_id) in s:
            s[str(chat_id)]["urinsh"] = 0
            save_sessions(s)
        tg_send(chat_id,
            "✅ PAROL TO'G'RI!\n\n"
            "Xush kelibsiz, Blip! 🚀\n\n"
            "📋 Buyruqlar:\n"
            "/prompt — Prompt\n"
            "/stat — Statistika\n"
            "/repos — Repolar\n"
            "/help — Yordam\n\n"
            "💡 Yoki yozing:\n"
            "\"barcha readme\"\n"
            "\"RasmAI uchun README\"\n"
            "\"Promptni o'zgartir: ...\"")
        log(f"✅ Parol: {chat_id}")
        return True
    else:
        urinsh = urinsh_oshir(chat_id)
        qoldi = MAX_URINISH - urinsh
        if qoldi <= 0:
            tg_send(chat_id, "🚫 BLOKLANDI! 1 daqiqa kuting.")
            log(f"🚫 Blok: {chat_id}")
            time.sleep(60)
            s = load_sessions()
            if str(chat_id) in s:
                s[str(chat_id)]["urinsh"] = 0
                save_sessions(s)
        else:
            tg_send(chat_id, f"❌ Parol xato! Qolgan: {qoldi}")
        log(f"❌ Xato parol: {chat_id}")
        return False

def logout(chat_id):
    sessiya_ochir(chat_id)
    tg_send(chat_id, "👋 Chiqdingiz!\n\nQayta: /start")

# ============================================================
# 🔄 ASOSIY LOOP
# ============================================================
def main():
    log("🚀 BLIP GITHUB AGENT v5.0 ishga tushdi!")
    log(f"👤 GitHub: @{GITHUB_USER}")
    log(f"🔐 Parol: ✅")
    log(f"📁 {LOYIHA_PAPKA}")
    log(f"📝 Prompt: {len(prompt_oqi())} belgi")

    me = tg_request("getMe")
    if me and me.get("ok"):
        log(f"🤖 Bot: @{me['result'].get('username', '?')}")

    init = tg_get_updates(0, timeout=1)
    last_id = 0
    if init and init.get("ok"):
        ups = init.get("result", [])
        if ups: last_id = max(u.get("update_id", 0) for u in ups)

    log("🔄 Kuzatish boshlandi...\n")
    xato_soni = 0

    while True:
        try:
            updates = tg_get_updates(last_id + 1, timeout=25)
            if updates and updates.get("ok"):
                for up in updates.get("result", []):
                    msg = up.get("message")
                    if not msg: continue
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "").strip()
                    ism = msg.get("from", {}).get("first_name", "?")
                    if not chat_id or not text: continue

                    if text == "/start":
                        sessiya_ochir(chat_id)
                        start_salom(chat_id, ism)
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue
                    if text == "/logout":
                        logout(chat_id)
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue
                    if text == "/id":
                        tg_send(chat_id, f"🆔 ID: `{chat_id}`")
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue

                    if not sessiya_bor(chat_id):
                        parol_ol(chat_id, text)
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue

                    try:
                        xabar_qayta_ishla(chat_id, text)
                    except Exception as e:
                        log(f"⚠️ Xabar: {e}")
                        tg_send(chat_id, f"❌ Xato: {str(e)[:100]}")

                    uid = up.get("update_id", 0)
                    if uid > last_id: last_id = uid
                xato_soni = 0
            time.sleep(1)
        except KeyboardInterrupt:
            log("👋 To'xtatildi"); break
        except Exception as e:
            xato_soni += 1
            log(f"⚠️ Loop #{xato_soni}: {e}")
            time.sleep(min(xato_soni * 2, 30))

# ============================================================
# 🏁 ENTRY
# ============================================================
if __name__ == "__main__":
    os.system("clear" if os.name != "nt" else "cls")
    print("\n" + "=" * 55)
    print("  🚀 BLIP GITHUB AGENT v5.0")
    print("  Parol + Prompt via Telegram")
    print("=" * 55)
    print(f"  📁 {LOYIHA_PAPKA}")
    print(f"  👤 @{GITHUB_USER}")
    print(f"  🔐 Parol: ✅")
    print("=" * 55)
    tokenlarni_tekshir()
    try:
        main()
    except KeyboardInterrupt:
        log("\n👋 Xayr!")
    except Exception as e:
        log(f"❌ {e}")