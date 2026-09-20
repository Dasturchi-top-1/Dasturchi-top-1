# ============================================================
# BLIP GITHUB YUKLOVCHI v7.0
# Fayl: blip_github.py
# O'zgarmagan fayllarni O'TKAZIB YUBORADI (SHA solishtirish)
# ============================================================
import os
import re
import base64
import hashlib
import requests
from urllib.parse import quote

# ============================================================
# ⚠️ SOZLAMALAR — SHU YERNI TO'LDIRING!
# ============================================================
TOKEN = "YOUR_TOKEN"
USERNAME = "Dasturchi-top-1"
REPO = "Dasturchi-top-1"
PAPKA = "/storage/emulated/0/.kivy"

SKIP = {"blip_github.py", "yuklangan.json", ".token", ".gitignore"}

# Xavfli patternlar — (regex, o'rinbosar)
XAVFLI = [
    (r"ghp_[A-Za-z0-9]{20,}",              "YOUR_GITHUB_TOKEN"),
    (r"github_pat_[A-Za-z0-9_]{20,}",      "YOUR_GITHUB_PAT"),
    (r"sk-or-[A-Za-z0-9-]{20,}",           "YOUR_OPENROUTER_KEY"),
    (r"sk-[A-Za-z0-9]{20,}",               "YOUR_OPENAI_KEY"),
    (r"AIza[A-Za-z0-9_-]{20,}",            "YOUR_GOOGLE_API_KEY"),
    (r"xoxb-[A-Za-z0-9-]{20,}",            "YOUR_SLACK_TOKEN"),
    (r"AKIA[A-Z0-9]{16}",                  "YOUR_AWS_KEY"),
    (r"(api[_-]?key\s*[=:]\s*['\"])[^'\"]+(['\"])",   r"\1YOUR_API_KEY\2"),
    (r"(secret[_-]?key\s*[=:]\s*['\"])[^'\"]+(['\"])", r"\1YOUR_SECRET_KEY\2"),
    (r"(password\s*[=:]\s*['\"])[^'\"]+(['\"])",      r"\1YOUR_PASSWORD\2"),
    (r"(TOKEN\s*=\s*['\"])[^'\"]+(['\"])",            r"\1YOUR_TOKEN\2"),
]

# ============================================================
# YORDAMCHI FUNKSIYALAR
# ============================================================
def git_sha(matn):
    """Git blob SHA-1 hisoblaydi."""
    data = matn.encode("utf-8")
    sha = hashlib.sha1()
    sha.update(f"blob {len(data)}\0".encode("utf-8"))
    sha.update(data)
    return sha.hexdigest()

def token_tekshir():
    if not TOKEN or TOKEN.startswith("ghp_sizning"):
        print("\n❌ XATO: Token kiritilmagan!")
        print("💡 Kodda TOKEN = 'YOUR_TOKEN' qatoriga yozing!\n")
        exit()
    print(f"  ✅ Token: {TOKEN[:8]}...{TOKEN[-4:]}")
    return TOKEN.strip()

def faylni_tekshir(matn):
    """Token bor-yo'qligini tekshiradi va tozalaydi."""
    topilgan = []
    toza = matn
    for pattern, almashtir in XAVFLI:
        moslar = re.findall(pattern, matn)
        if moslar:
            nom = pattern[:25].replace("\\", "")
            topilgan.append(f"{nom}... ({len(moslar)} ta)")
            if "\\1" in almashtir:
                toza = re.sub(pattern, almashtir, toza, flags=re.IGNORECASE)
            else:
                toza = re.sub(pattern, almashtir, toza, flags=re.IGNORECASE)
    return toza, topilgan

def faylni_oqi(yol):
    try:
        with open(yol, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return None

# ============================================================
# GITHUB
# ============================================================
def github_royxat(token):
    """GitHub'dagi fayllar: {nom: sha}"""
    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/"
    headers = {"Authorization": f"token {token}"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return {i["name"]: i["sha"] for i in r.json()
                    if i["type"] == "file"}
        elif r.status_code == 401:
            print(f"\n❌ Token yaroqsiz (401).")
            return None
        elif r.status_code == 404:
            print(f"\n❌ Repo topilmadi: {USERNAME}/{REPO}")
            return None
        else:
            print(f"\n❌ GitHub xatosi: HTTP {r.status_code}")
            return None
    except Exception as e:
        print(f"\n❌ Ulanish xatosi: {e}")
        return None

def github_yukla(token, matn, fayl_nomi, mavjud_sha=None):
    try:
        content = base64.b64encode(matn.encode("utf-8")).decode("utf-8")
    except Exception as e:
        print(f"(encode: {e})", end=" ")
        return False
    
    xavfsiz_nom = quote(fayl_nomi, safe="")
    url = (f"https://api.github.com/repos/"
           f"{USERNAME}/{REPO}/contents/{xavfsiz_nom}")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    amal = "Yangilandi" if mavjud_sha else "Qo'shildi"
    data = {"message": f"{amal}: {fayl_nomi}", "content": content}
    if mavjud_sha:
        data["sha"] = mavjud_sha
    try:
        r = requests.put(url, headers=headers, json=data, timeout=30)
        if r.status_code in [200, 201]:
            return True
        print(f"(HTTP {r.status_code})", end=" ")
        return False
    except Exception as e:
        print(f"(PUT: {e})", end=" ")
        return False

# ============================================================
# ASOSIY DASTUR
# ============================================================
def main():
    os.system("clear" if os.name != "nt" else "cls")
    
    print(f"\n{'=' * 62}")
    print(f"  🚀 BLIP GITHUB YUKLOVCHI v7.0")
    print(f"  🔒 Token olib tashlanadi • ⏭  O'zgarmaganlar o'tkaziladi")
    print(f"{'=' * 62}\n")
    
    token = token_tekshir()
    print(f"  📦 Repo:  {USERNAME}/{REPO}")
    print(f"  📁 Papka: {PAPKA}\n")
    
    # GitHub'dagi fayllar
    print(f"  ⏳ GitHub'dagi fayllar olinmoqda...")
    github_fayllar = github_royxat(token)
    if github_fayllar is None:
        return
    print(f"  ✅ GitHub'da: {len(github_fayllar)} ta fayl\n")
    
    # Mahalliy fayllar
    if not os.path.exists(PAPKA):
        print(f"\n❌ Papka topilmadi: {PAPKA}")
        return
    fayllar = sorted([f for f in os.listdir(PAPKA)
                      if f.endswith(".py") and f not in SKIP])
    print(f"  ✅ Papkada:   {len(fayllar)} ta .py fayl")
    
    # Har bir faylni tahlil qilish
    print(f"\n  🔍 Fayllar tahlil qilinmoqda...")
    
    yangi = []        # GitHub'da yo'q
    ozgargan = []     # GitHub'da bor, lekin o'zgargan
    ozgarmagan = []   # GitHub'da bor va bir xil (O'TKAZILADI)
    tokenli = []      # Token bor fayllar
    
    for f in fayllar:
        yol = f"{PAPKA}/{f}"
        matn = faylni_oqi(yol)
        if matn is None:
            continue
        
        toza, sabablar = faylni_tekshir(matn)
        mahalliy_sha = git_sha(toza)
        github_sha = github_fayllar.get(f)
        
        malumot = {"nom": f, "matn": toza, "sha": github_sha}
        if sabablar:
            malumot["sabablar"] = sabablar
            tokenli.append(malumot)
        
        if github_sha is None:
            yangi.append(malumot)
        elif github_sha == mahalliy_sha:
            ozgarmagan.append(malumot)
        else:
            ozgargan.append(malumot)
    
    # HOLAT
    print(f"\n{'=' * 62}")
    print(f"  📊 HOLAT:")
    print(f"     🆕 Yangi (GitHub'da yo'q):      {len(yangi)}")
    print(f"     🔄 O'zgargan (yangilanadi):     {len(ozgargan)}")
    print(f"     ⏭  O'zgarmagan (o'tkaziladi):   {len(ozgarmagan)}")
    print(f"     🔒 Token topilgan:               {len(tokenli)}")
    print(f"{'=' * 62}")
    
    # Tokenli fayllar
    if tokenli:
        print(f"\n  🔒 TOKEN/API TOPILGAN ({len(tokenli)} ta):")
        print(f"  {'─' * 58}")
        for x in tokenli:
            print(f"     ⚠️  {x['nom']}")
            for s in x["sabablar"]:
                print(f"        └─ {s}")
        print(f"\n  💡 Nusxadan token olib tashlanadi (asl fayl tegmaydi)")
    
    # Yuklanadiganlar
    yuklanadi = yangi + ozgargan
    if not yuklanadi:
        print(f"\n  🎉 Hammasi joyida! Yuklanadigan narsa yo'q.")
        print(f"  ⏭  {len(ozgarmagan)} ta fayl allaqachon GitHub'da.\n")
        return
    
    # Ko'rsatish
    if yangi:
        print(f"\n  🆕 YANGI ({len(yangi)} ta):")
        for i, x in enumerate(yangi[:10], 1):
            print(f"     {i}. {x['nom']}")
        if len(yangi) > 10:
            print(f"     ... va yana {len(yangi) - 10} ta")
    
    if ozgargan:
        print(f"\n  🔄 O'ZGARGAN ({len(ozgargan)} ta):")
        for i, x in enumerate(ozgargan[:10], 1):
            print(f"     {i}. {x['nom']}")
        if len(ozgargan) > 10:
            print(f"     ... va yana {len(ozgargan) - 10} ta")
    
    # TASDIQLASH
    javob = input(f"\n  Yuklaymizmi? (h/y): ").strip().lower()
    if javob != "h":
        print(f"\n  ⏹  Bekor qilindi.\n")
        return
    
    # YUKLASH
    print(f"\n{'=' * 62}")
    print(f"  ⏳ Yuklash boshlandi ({len(yuklanadi)} ta fayl)...")
    print(f"{'=' * 62}\n")
    
    m_ok = 0
    xato = 0
    xato_royxat = []
    
    for i, x in enumerate(yuklanadi, 1):
        token_belgi = "🔒" if "sabablar" in x else "  "
        amal = "U" if x["sha"] else "Y"
        print(f"  [{amal}{i}/{len(yuklanadi)}] {token_belgi} {x['nom']}... ",
              end="", flush=True)
        
        if github_yukla(token, x["matn"], x["nom"], x["sha"]):
            print("✅")
            m_ok += 1
        else:
            print("❌")
            xato += 1
            xato_royxat.append(x["nom"])
    
    # HISOBOT
    print(f"\n{'=' * 62}")
    print(f"  📊 NATIJA")
    print(f"{'=' * 62}")
    print(f"     ✅ Yuklandi:              {m_ok}")
    print(f"     ❌ Xato:                   {xato}")
    print(f"     ⏭  O'tkazildi:             {len(ozgarmagan)} (o'zgarmagan)")
    print(f"     🔒 Token olib tashlandi:  {len(tokenli)} faylda")
    print(f"     💾 Asl fayllar:           O'ZGARMADI")
    
    if xato_royxat:
        print(f"\n  ⚠️  Xato bo'lganlar:")
        for f in xato_royxat[:10]:
            print(f"     - {f}")
    
    print(f"\n  🌐 https://github.com/{USERNAME}/{REPO}")
    print(f"{'=' * 62}\n")

# ============================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  ⏹  To'xtatildi (Ctrl+C)\n")
    except Exception as e:
        print(f"\n\n  ❌ Kutilmagan xato: {e}\n")