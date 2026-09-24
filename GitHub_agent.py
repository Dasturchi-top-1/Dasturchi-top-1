# ============================================================
# 🚀 BLIP GITHUB AGENT v4.0 — Parol himoyasi bilan
# Fayl: blip_github_agent.py
# Papka: /storage/emulated/0/Ai/GitHubAgent/
# ⚠️ Bu faylni GitHub'ga YUKLAMANG!
# ============================================================
import os, sys, json, time, base64, hashlib, datetime
import urllib.request, urllib.parse, urllib.error

# ============================================================
# ⚠️ TOKENLAR — SHU YERNI TO'LDIRING!
# ============================================================
BOT_TOKEN = "YOUR_TOKEN"
GITHUB_TOKEN = "YOUR_TOKEN"
GITHUB_USER = "Dasturchi-top-1"
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY"

# ============================================================
# 🔐 PAROL — o'zingiz o'ylab toping!
# ============================================================
MAXFIY_PAROL = "Blipzor921324"
MAX_URINISH = 3
SESSIYA_VAQTI = 365 * 24 * 3600  # 1 yil!  # 1 soat

# ============================================================
# SOZLAMALAR
# ============================================================
LOYIHA_PAPKA = "/storage/emulated/0/Ai/GitHubAgent"
os.makedirs(LOYIHA_PAPKA, exist_ok=True)

DB_FILE = f"{LOYIHA_PAPKA}/agent_state.json"
SESS_FILE = f"{LOYIHA_PAPKA}/sessions.json"
LOG_FILE = f"{LOYIHA_PAPKA}/github_agent.log"

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
# 🤖 AI INTENT PROMPT
# ============================================================
INTENT_PROMPT = """Sen intent parser. Foydalanuvchi xabaridan niyatini JSON formatda aniqlaysan.

MUMKIN NIYATLAR:
1. readme_create — README yaratish
   → repo (aniq nom yoki 'barcha'), title, description, tech, features
2. readme_update — README yangilash
   → repo, instructions
3. stats — statistika
4. repos — repolar ro'yxati
5. traffic — klon statistikasi
6. chat — oddiy suhbat

QOIDALAR:
- "barcha", "hammasi", "hamma" → repo: "barcha"
- "statistika", "stat", "ahvol" → stats
- "repolar", "loyihalar" → repos
- "klon", "traffic" → traffic
- Aniq repo nomi → readme_create
- Boshqa → chat

FAQAT JSON qaytar.

MISOLLAR:
User: "barcha readme"
→ {"intent": "readme_create", "repo": "barcha", "title": "Blip loyihalari", "description": "Barcha loyihalar", "tech": ["Python"], "features": ["AI"]}

User: "RasmAI uchun README"
→ {"intent": "readme_create", "repo": "RasmAI", "title": "RasmAI", "description": "Rasm tahlil", "tech": ["Python"], "features": ["AI"]}

User: "statistika"
→ {"intent": "stats"}

User: "Salom"
→ {"intent": "chat", "javob": "Salom! Men Blip GitHub Agent."}
"""

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
    if not MAXFIY_PAROL or len(MAXFIY_PAROL) < 6:
        xato.append("MAXFIY_PAROL (kamida 6 belgi)")
    if xato:
        print("\n❌ To'ldirilmagan:")
        for x in xato: print(f"   • {x}")
        sys.exit(1)
    print("  ✅ Tokenlar va parol to'ldirilgan")

# ============================================================
# STORAGE
# ============================================================
def load_state():
    default = {
        "last_check": 0, "last_daily": "",
        "repos": {}, "total_stars": 0, "total_forks": 0,
        "followers": 0, "events_seen": [], "first_run": True,
    }
    if not os.path.exists(DB_FILE): return default
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default.items(): data.setdefault(k, v)
        return data
    except: return default

def save_state(state):
    try:
        tmp = DB_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DB_FILE)
        return True
    except: return False

# ============================================================
# 🔐 SESSIYA BOSHQARUVI (XOTIRA + FAYL)
# ============================================================
# Xotiradagi sessiyalar (tez ishlaydi)
_SESSIONS_MEM = {}

def load_sessions():
    """Fayldan sessiyalarni oladi."""
    if not os.path.exists(SESS_FILE):
        return {}
    try:
        with open(SESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_sessions(s):
    """Faylga saqlaydi."""
    try:
        tmp = SESS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
        os.replace(tmp, SESS_FILE)
        return True
    except Exception as e:
        log(f"⚠️ Sessiya saqlash: {e}")
        return False

def sessiya_bor(chat_id):
    """XOTIRADA + faylda tekshiradi."""
    key = str(chat_id)
    hozir = time.time()
    
    # 1. XOTIRADA tekshirish (asosiy)
    if key in _SESSIONS_MEM:
        vaqt = _SESSIONS_MEM[key].get("vaqt", 0)
        if hozir - vaqt < SESSIYA_VAQTI:
            # Vaqtni yangilash
            _SESSIONS_MEM[key]["vaqt"] = hozir
            # Faylga ham yozish (background)
            s = load_sessions()
            s[key] = _SESSIONS_MEM[key]
            save_sessions(s)
            return True
        else:
            # Muddati o'tgan
            del _SESSIONS_MEM[key]
    
    # 2. FAYLDAN tekshirish (agar xotirada yo'q bo'lsa)
    s = load_sessions()
    if key in s:
        vaqt = s[key].get("vaqt", 0)
        if hozir - vaqt < SESSIYA_VAQTI:
            # Xotiraga ko'chirish
            _SESSIONS_MEM[key] = s[key]
            _SESSIONS_MEM[key]["vaqt"] = hozir
            s[key]["vaqt"] = hozir
            save_sessions(s)
            return True
        else:
            # Muddati o'tgan — tozalash
            del s[key]
            save_sessions(s)
    
    return False

def sessiya_yarat(chat_id):
    """Yangi sessiya — xotira + fayl."""
    key = str(chat_id)
    hozir = time.time()
    ma = {"vaqt": hozir, "urinsh": 0}
    
    # Xotiraga
    _SESSIONS_MEM[key] = ma
    
    # Faylga
    s = load_sessions()
    s[key] = ma
    save_sessions(s)
    
    log(f"✅ Sessiya yaratildi: {key}")

def sessiya_ochir(chat_id):
    """Sessiyani o'chiradi."""
    key = str(chat_id)
    _SESSIONS_MEM.pop(key, None)
    s = load_sessions()
    s.pop(key, None)
    save_sessions(s)

def urinsh_oshir(chat_id):
    """Xato urinish soni."""
    key = str(chat_id)
    if key not in _SESSIONS_MEM:
        _SESSIONS_MEM[key] = {"vaqt": time.time(), "urinsh": 0}
    _SESSIONS_MEM[key]["urinsh"] = _SESSIONS_MEM[key].get("urinsh", 0) + 1
    s = load_sessions()
    s[key] = _SESSIONS_MEM[key]
    save_sessions(s)
    return _SESSIONS_MEM[key]["urinsh"]

def urinsh_ol(chat_id):
    key = str(chat_id)
    return _SESSIONS_MEM.get(key, {}).get("urinsh", 0)

def parol_tekshir(matn):
    return matn.strip() == MAXFIY_PAROL

# ============================================================
# HTTP HELPERS
# ============================================================
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

# ============================================================
# GITHUB API
# ============================================================
def gh_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "BlipGitHubAgent",
    }

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
# 🤖 AI FUNKSIYALAR
# ============================================================
def ai_request(model, system, user_text, timeout=60):
    if not OPENROUTER_KEY: return None
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.7, "max_tokens": 1500,
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
        start = javob.find("{")
        end = javob.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(javob[start:end])
    except Exception as e:
        log(f"⚠️ Intent JSON: {e}")
    return None

# ============================================================
# 📝 README YARATISH
# ============================================================
def readme_matn_yarat(repo, title, description, tech, features):
    tech_str = ", ".join(tech) if tech else "Python"
    feat_str = ", ".join(features) if features else "Yangi loyiha"
    prompt = (
        f"Quyidagi loyiha uchun chiroyli README.md yoz:\n\n"
        f"Repo: {repo}\n"
        f"Sarlavha: {title}\n"
        f"Tavsif: {description}\n"
        f"Texnologiyalar: {tech_str}\n"
        f"Xususiyatlar: {feat_str}\n\n"
        f"FORMAT (Markdown):\n"
        f"# {title}\n\n"
        f"Qisqa tavsif\n\n"
        f"## ✨ Xususiyatlar\n- ...\n\n"
        f"## 🛠 Texnologiyalar\n- ...\n\n"
        f"## 🚀 O'rnatish\n1. ...\n\n"
        f"## 🎯 Foydalanish\n...\n\n"
        f"## 👤 Muallif\nSalohiddin (Blip), 13 yosh\n\n"
        f"## 📜 Litsenziya\nMIT\n\n"
        f"Emoji ishlat, chiroyli va tushunarli yoz. "
        f"FAQAT README matnini yoz."
    )
    return ai_ask(
        "Sen README.md yozuvchi mutaxassissan. "
        "Chiroyli Markdown yozasan. O'zbek tilida.",
        prompt)

def barcha_uchun_readme(chat_id, title, description, tech, features):
    """Barcha repolar uchun README yaratadi."""
    tg_send(chat_id, "⏳ Repolar olinmoqda...")
    repos = gh_repos() or []
    if not repos:
        tg_send(chat_id, "❌ Repolar topilmadi"); return

    # README kerak bo'lganlarni topish
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
            tech or [til, "GitHub", "Python"],
            features or ["Dasturlash", "Ochiq kod"])
        
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

def readme_yarat(chat_id, repo, title, description, tech, features):
    repo_lower = repo.lower().strip()
    if repo_lower in ("barcha", "hammasi", "all", "barchasi",
                      "barcha loyihalar", "barcha repolar", "hamma"):
        barcha_uchun_readme(chat_id, title, description, tech, features)
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
    readme = readme_matn_yarat(repo, title, description, tech, features)
    if not readme:
        tg_send(chat_id, "❌ AI README yarata olmadi")
        return False

    tg_send(chat_id, "📤 GitHub'ga yuborilmoqda...")
    natija = gh_create_file(repo, "README.md", readme,
                            f"📝 Add README.md — {title}")
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

def readme_yangila(chat_id, repo, instructions):
    existing = gh_get_file(repo, "README.md")
    if not existing:
        tg_send(chat_id, f"❌ README topilmadi: {repo}")
        return False
    try:
        matn_eski = base64.b64decode(existing["content"]).decode("utf-8")
    except:
        tg_send(chat_id, "❌ README o'qilmadi"); return False

    tg_send(chat_id, "🤖 README yangilanmoqda...")
    prompt = (
        f"Mavjud README:\n\n{matn_eski}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"SO'ROV: {instructions}\n\n"
        f"README'ni yangila. Format saqlansin."
    )
    readme_yangi = ai_ask(
        "Sen README tahrirlovchisisan. O'zbek tilida.", prompt)
    if not readme_yangi:
        tg_send(chat_id, "❌ AI yangilay olmadi"); return False

    natija = gh_create_file(repo, "README.md", readme_yangi,
                            f"📝 Update README — {instructions[:50]}")
    if not natija:
        tg_send(chat_id, "❌ GitHub xato"); return False

    tg_send(chat_id, f"✅ README YANGILANDI! ({repo})")
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

    matn = (
        f"📊 GITHUB STATISTIKA\n"
        f"{'=' * 30}\n\n"
        f"👤 @{GITHUB_USER}\n\n"
        f"⭐ Yulduzlar: {total_stars}\n"
        f"🍴 Forklar: {total_forks}\n"
        f"👥 Followers: {user.get('followers', 0)}\n"
        f"📚 Repolar: {len(repos)}\n"
    )
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
# 💬 XABARLARNI QAYTA ISHLASH
# ============================================================
def xabar_qayta_ishla(chat_id, text, state):
    tg_typing(chat_id)
    
    # Kodda "barcha" ni tekshirish
    t_lower = text.lower()
    barcha_kalit = ["barcha loyiha", "barcha repo", "barcha repolar",
                    "hammasi", "barchasi", "hamma loyiha", "hamma repo"]
    readme_kalit = ["readme", "reamde", "reamd", "rdme"]
    
    barcha_sozi = any(k in t_lower for k in barcha_kalit)
    readme_sozi = any(k in t_lower for k in readme_kalit)
    
    if barcha_sozi and readme_sozi:
        barcha_uchun_readme(
            chat_id, "Blip loyihalari",
            "Salohiddin (Blip) loyihalari",
            ["Python", "AI", "Telegram Bot"],
            ["Dasturlash", "AI", "Ochiq kod"])
        return
    
    # AI intent
    intent = intent_aniqla(text)
    if not intent:
        tg_send(chat_id, "❌ Tushunmadim. Qaytadan yozing.")
        return

    tur = intent.get("intent", "chat")
    if tur == "readme_create":
        repo = intent.get("repo", "")
        if not repo:
            tg_send(chat_id, "❌ Repo nomi yo'q"); return
        readme_yarat(chat_id, repo, intent.get("title", repo),
                     intent.get("description", ""),
                     intent.get("tech", ["Python"]),
                     intent.get("features", []))
    elif tur == "readme_update":
        repo = intent.get("repo", "")
        if not repo:
            tg_send(chat_id, "❌ Repo yo'q"); return
        readme_yangila(chat_id, repo,
                       intent.get("instructions", "Yaxshila"))
    elif tur == "stats":
        stats_yubor(chat_id)
    elif tur == "repos":
        repos_yubor(chat_id)
    elif tur == "traffic":
        tg_send(chat_id, "📈 Traffic tez kunda!")
    elif tur == "chat":
        javob = intent.get("javob", "")
        if not javob:
            javob = ai_ask(
                "Sen BLIP GITHUB AGENT. O'zbek tilida javob ber.",
                text) or "Tushunmadim"
        tg_send(chat_id, javob)
    else:
        javob = ai_ask("O'zbek tilida javob ber.", text)
        tg_send(chat_id, javob or "Tushunmadim")
# ============================================================
# 🔐 PAROL HANDLERLARI
# ============================================================
def start_salom(chat_id, ism):
    """Boshlang'ich xabar — parol so'raydi."""
    tg_send(chat_id,
        f"🔐 *BLIP GITHUB AGENT*\n\n"
        f"Salom, {ism}!\n\n"
        f"Bu bot faqat *egasi* uchun.\n"
        f"Davom etish uchun *parolni* yuboring:\n\n"
        f"❌ Xato qilsangiz — 3 urinish\n"
        f"⏱ Sessiya: 1 soat")

def parol_ol(chat_id, matn):
    """Parolni tekshiradi."""
    if parol_tekshir(matn):
        # Muvaffaqiyat
        sessiya_yarat(chat_id)
        # Urinshni reset
        s = load_sessions()
        if str(chat_id) in s:
            s[str(chat_id)]["urinsh"] = 0
            save_sessions(s)
        tg_send(chat_id,
            "✅ *PAROL TO'G'RI!*\n\n"
            "Xush kelibsiz, Blip! 🚀\n\n"
            "📋 *Buyruqlar:*\n"
            "• Barcha README: `barcha readme`\n"
            "• Bitta repo: `RasmAI uchun README yarat`\n"
            "• Statistika: `statistika`\n"
            "• Repolar: `repolar`\n"
            "• Chiqish: `/logout`")
        log(f"✅ Parol to'g'ri: chat_id={chat_id}")
        return True
    else:
        # Xato
        urinsh = urinsh_oshir(chat_id)
        qoldi = MAX_URINISH - urinsh
        if qoldi <= 0:
            tg_send(chat_id,
                "🚫 *BLOKLANDI!*\n\n"
                "3 marta xato parol.\n"
                "1 daqiqa kuting.")
            log(f"🚫 Bloklangan: chat_id={chat_id}")
            time.sleep(60)
            # Reset
            s = load_sessions()
            if str(chat_id) in s:
                s[str(chat_id)]["urinsh"] = 0
                save_sessions(s)
        else:
            tg_send(chat_id,
                f"❌ *Parol xato!*\n\n"
                f"Qolgan urinish: {qoldi} ta")
        log(f"❌ Xato parol: chat_id={chat_id}")
        return False

def logout(chat_id):
    sessiya_ochir(chat_id)
    tg_send(chat_id, "👋 *Chiqdingiz!*\n\nQayta kirish: /start")

# ============================================================
# 🔄 ASOSIY LOOP
# ============================================================
def main():
    log("🚀 BLIP GITHUB AGENT v4.0 ishga tushdi!")
    log(f"👤 GitHub: @{GITHUB_USER}")
    log(f"📁 Papka: {LOYIHA_PAPKA}")
    log(f"🔐 Parol: ✅ Yoniq")

    me = tg_request("getMe")
    if me and me.get("ok"):
        log(f"🤖 Bot: @{me['result'].get('username', '?')}")

    init = tg_get_updates(0, timeout=1)
    last_id = 0
    if init and init.get("ok"):
        ups = init.get("result", [])
        if ups: last_id = max(u.get("update_id", 0) for u in ups)

    log("🔄 Kuzatish boshlandi...\n")
    state = load_state()
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

                    # ===== /start =====
                    if text == "/start":
                        sessiya_ochir(chat_id)
                        start_salom(chat_id, ism)
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue

                    # ===== /logout =====
                    if text == "/logout":
                        logout(chat_id)
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue

                    # ===== /id =====
                    if text == "/id":
                        tg_send(chat_id, f"🆔 Sizning ID: `{chat_id}`")
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue

                    # ===== SESSIYA TEKSHIRUVI =====
                    if not sessiya_bor(chat_id):
                        # Parolni tekshirish
                        parol_ol(chat_id, text)
                        uid = up.get("update_id", 0)
                        if uid > last_id: last_id = uid
                        continue

                    # ===== SESSIYA BOR — ISHLA =====
                    try:
                        xabar_qayta_ishla(chat_id, text, state)
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
    print("  🚀 BLIP GITHUB AGENT v4.0")
    print("  🔐 Parol himoyasi bilan")
    print("=" * 55)
    print(f"  📁 {LOYIHA_PAPKA}")
    print(f"  👤 @{GITHUB_USER}")
    print(f"  🔐 Parol: ✅ Yoniq")
    print("=" * 55)
    tokenlarni_tekshir()
    try:
        main()
    except KeyboardInterrupt:
        log("\n👋 Xayr!")
    except Exception as e:
        log(f"❌ {e}")