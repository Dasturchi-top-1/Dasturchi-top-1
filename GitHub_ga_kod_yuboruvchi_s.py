# ============================================================
# 🚀 BLIP GITHUB YUKLOVCHI v9.1 (INTERAKTIV + "HAMMASI" REJIMI)
# Fayl: blip_github.py
# Xususiyatlari:
# 1. Maxfiy kalitlarni yashiradi va tamg'a qo'shadi.
# 2. Raqam orqali yoki "h" (hammasi) orqali yuklash/o'chirish.
# 3. Xato bo'lsa ham dastur to'xtab qolmaydi.
# ============================================================
import os
import re
import base64
import hashlib
import requests
import subprocess
from urllib.parse import quote

# ============================================================
# ⚠️ SOZLAMALAR — SHU YERNI TO'LDIRING!
# ============================================================
TOKEN = "YOUR_TOKEN" 
USERNAME = "Dasturchi-top-1"
REPO = "Dasturchi-top-1"
PAPKA = "/storage/emulated/0/.kivy" 

MARKER = "Ishlab chiqaruvchi: Blip"
SKIP = {"GitHub_ga_kod_yuboruvchi.py", "yuklangan.json", ".token", ".gitignore", "config.py", "blip_github.py"}

# Xavfli patternlar (Sizning kodingizdan)
XAVFLI = [
    (r"ghp_[A-Za-z0-9]{20,}", "YOUR_GITHUB_TOKEN"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "YOUR_GITHUB_PAT"),
    (r"sk-[A-Za-z0-9]{20,}", "YOUR_OPENAI_KEY"),
    (r"AIza[A-Za-z0-9_-]{20,}", "YOUR_GOOGLE_API_KEY"),
    (r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b", "YOUR_BOT_TOKEN"),
    (r"(PASS\w*\s*=\s*['\"])[^'\"]+(['\"])", r"\1YOUR_PASS\2"),
    (r"(TOKEN\s*=\s*['\"])[^'\"]+(['\"])", r"\1YOUR_TOKEN\2"),
    (r"(API_KEY\s*=\s*['\"])[^'\"]+(['\"])", r"\1YOUR_API_KEY\2"),
    (r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "YOUR_EMAIL"),
]

# ============================================================
# YORDAMCHI FUNKSIYALAR
# ============================================================
def git_sha(matn):
    data = matn.encode("utf-8")
    sha = hashlib.sha1()
    sha.update(f"blob {len(data)}\0".encode("utf-8"))
    sha.update(data)
    return sha.hexdigest()

def faylni_tekshir(matn):
    toza = matn
    for pattern, almashtir in XAVFLI:
        try:
            if re.search(pattern, toza):
                toza = re.sub(pattern, almashtir, toza, flags=re.IGNORECASE)
        except Exception:
            pass
    return toza

def tamga_qosh(matn):
    if MARKER in matn:
        return matn
    return matn + (f"\n\n# {MARKER}\n" if not matn.endswith("\n") else f"\n# {MARKER}\n")

def raqamlarni_ajrat(matn):
    """1, 3, 5 kabi matnni raqamlar ro'yxatiga aylantiradi. 'h' bo'lsa -1 qaytaradi."""
    matn = matn.strip().lower()
    if matn in ["h", "hammasi", "all"]:
        return "ALL"
    try:
        return [int(x.strip()) for x in re.split(r'[,\s]+', matn) if x.strip().isdigit()]
    except Exception:
        return []

# ============================================================
# GITHUB API
# ============================================================
def github_royxat():
    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/"
    headers = {"Authorization": f"token {TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return {i["name"]: i["sha"] for i in r.json() if i["type"] == "file"}
        return {}
    except Exception:
        return {}

def github_yukla(matn, fayl_nomi, mavjud_sha=None):
    content = base64.b64encode(matn.encode("utf-8")).decode("utf-8")
    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{quote(fayl_nomi)}"
    headers = {"Authorization": f"token {TOKEN}"}
    data = {"message": f"Yangilandi: {fayl_nomi}", "content": content}
    if mavjud_sha: data["sha"] = mavjud_sha
    try:
        r = requests.put(url, headers=headers, json=data, timeout=30)
        return r.status_code in [200, 201]
    except Exception:
        return False

def github_ochir(fayl_nomi, mavjud_sha):
    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{quote(fayl_nomi)}"
    headers = {"Authorization": f"token {TOKEN}"}
    data = {"message": f"O'chirildi: {fayl_nomi}", "sha": mavjud_sha}
    try:
        r = requests.delete(url, headers=headers, json=data, timeout=15)
        return r.status_code == 200
    except Exception:
        return False

# ============================================================
# ASOSIY DASTUR (INTERAKTIV)
# ============================================================
def asosiy_menyu():
    if not os.path.exists(PAPKA):
        print(f"\n❌ Papka topilmadi: {PAPKA}")
        return
    mahalliy_fayllar = sorted([f for f in os.listdir(PAPKA) if f.endswith(".py") and f not in SKIP])
    
    while True:
        os.system("clear" if os.name != "nt" else "cls")
        print(f"\n{'=' * 55}")
        print(f"  🚀 BLIP GITHUB BOSHQARUV PANELI v9.1")
        print(f"{'=' * 55}")
        
        github_fayllar = github_royxat()
        if not github_fayllar:
            print("  ⚠️ GitHub bilan ulanib bo'lmadi (Token yoki Internetni tekshiring).")
            input("\n  Davom etish uchun Enter bosing...")
            continue

        yangi = [f for f in mahalliy_fayllar if f not in github_fayllar]
        ozgargan = []
        for f in mahalliy_fayllar:
            if f in github_fayllar:
                try:
                    with open(f"{PAPKA}/{f}", "r", encoding="utf-8", errors="ignore") as file:
                        matn = file.read()
                    yakuniy = tamga_qosh(faylni_tekshir(matn))
                    if git_sha(yakuniy) != github_fayllar[f]:
                        ozgargan.append(f)
                except Exception:
                    pass
        
        ochiriladigan = [f for f in github_fayllar.keys() if f.endswith(".py") and f not in mahalliy_fayllar and f not in SKIP]

        print(f"  📊 Holat: 🆕 Yangi: {len(yangi)} | 🔄 O'zgargan: {len(ozgargan)} | 🗑️ O'chirilishi kerak: {len(ochiriladigan)}")
        print(f"  GitHub'da: {len(github_fayllar)} ta | Telefonda: {len(mahalliy_fayllar)} ta")
        print(f"{'-' * 55}")
        print("  1. 📤 Yuklash (Raqamlar yoki 'h' - hammasi)")
        print("  2. 🗑️  O'chirish (Raqamlar yoki 'h' - hammasi)")
        print("  3. ✏️  Tahrirlash")
        print("  4. 🚪 Chiqish")
        print(f"{'=' * 55}")
        
        tanlov = input("  Tanlang (1-4): ").strip()
        
        if tanlov == "1":
            # ================= YUKLASH =================
            yuklashga = yangi + ozgargan
            if not yuklashga:
                print("\n  ✅ Yuklanadigan yangi/o'zgargan fayl yo'q.")
                input("  Enter bosing...")
                continue
                
            print(f"\n  Yuklanadigan fayllar:")
            for i, f in enumerate(yuklashga, 1):
                belgi = "🔄" if f in ozgargan else "🆕"
                print(f"    {i}. {belgi} {f}")
            
            kiritma = input("\n  Raqamlarni yoki 'h' (hammasini yuborish) ni kiriting: ")
            tanlangan = raqamlarni_ajrat(kiritma)
            
            if tanlangan == "ALL":
                yuboriladigan_fayllar = yuklashga
                print(f"\n  ⏳ Hammasi ({len(yuboriladigan_fayllar)} ta) yuklanmoqda...")
            else:
                yuboriladigan_fayllar = []
                for r in tanlangan:
                    if 0 < r <= len(yuklashga):
                        yuboriladigan_fayllar.append(yuklashga[r-1])
                print(f"\n  ⏳ Tanlangan ({len(yuboriladigan_fayllar)} ta) yuklanmoqda...")
            
            for f_nomi in yuboriladigan_fayllar:
                try:
                    print(f"  📤 {f_nomi}...", end=" ", flush=True)
                    with open(f"{PAPKA}/{f_nomi}", "r", encoding="utf-8", errors="ignore") as file:
                        matn = file.read()
                    yakuniy = tamga_qosh(faylni_tekshir(matn))
                    if github_yukla(yakuniy, f_nomi, github_fayllar.get(f_nomi)):
                        print("✅")
                    else:
                        print("❌ (O'tkazib yuborildi)")
                except Exception as e:
                    print(f"❌ (Xato: {e})")
            input("\n  Enter bosing...")

        elif tanlov == "2":
            # ================= O'CHIRISH =================
            barcha_git = sorted(list(github_fayllar.keys()))
            if not barcha_git:
                print("\n  GitHub'da fayl yo'q.")
                input("  Enter bosing...")
                continue
                
            print(f"\n  GitHub'dagi barcha fayllar:")
            for i, f in enumerate(barcha_git, 1):
                print(f"    {i}. {f}")
                
            kiritma = input("\n  Raqamlarni yoki 'h' (hammasini o'chirish) ni kiriting: ")
            tanlangan = raqamlarni_ajrat(kiritma)
            
            if not tanlangan:
                print("\n  ⚠️ Raqam kiritilmadi.")
                input("  Enter bosing...")
                continue

            if tanlangan == "ALL":
                ochiriladigan_fayllar = barcha_git
                print(f"\n  🗑️ Hammasi ({len(ochiriladigan_fayllar)} ta) o'chirilmoqda...")
            else:
                ochiriladigan_fayllar = []
                for r in tanlangan:
                    if 0 < r <= len(barcha_git):
                        ochiriladigan_fayllar.append(barcha_git[r-1])
                print(f"\n  🗑️ Tanlangan ({len(ochiriladigan_fayllar)} ta) o'chirilmoqda...")

            for f_nomi in ochiriladigan_fayllar:
                try:
                    print(f"  🗑️ {f_nomi}...", end=" ", flush=True)
                    if github_ochir(f_nomi, github_fayllar[f_nomi]):
                        print("✅")
                    else:
                        print("❌ (O'tkazib yuborildi)")
                except Exception as e:
                    print(f"❌ (Xato: {e})")
            input("\n  Enter bosing...")

        elif tanlov == "3":
            # ================= TAHRIRLASH =================
            if not mahalliy_fayllar:
                print("\n  Telefonda .py fayllar yo'q.")
                input("  Enter bosing...")
                continue
            
            print(f"\n  Telefondagi fayllar:")
            for i, f in enumerate(mahalliy_fayllar, 1):
                print(f"    {i}. {f}")
                
            try:
                r = int(input("\n  Tahrirlash uchun fayl raqamini kiriting: "))
                if 0 < r <= len(mahalliy_fayllar):
                    f_nomi = mahalliy_fayllar[r-1]
                    yol = f"{PAPKA}/{f_nomi}"
                    print(f"  ✏️ {f_nomi} tahrirlash uchun ochilmoqda...")
                    subprocess.run(["am", "start", "-a", "android.intent.action.EDIT", "-d", f"file://{yol}"], stderr=subprocess.DEVNULL)
                else:
                    print("\n  ⚠️ Bunday raqamdagi fayl yo'q.")
            except ValueError:
                print("\n  ⚠️ Iltimos, faqat raqam kiriting.")
            except Exception as e:
                print(f"\n  ❌ Xatolik: {e}")
            input("\n  Enter bosing...")

        elif tanlov == "4":
            print("\n  👋 Dastur tugadi. Xayr!")
            break
        else:
            print("\n  ⚠️ Noto'g'ri buyruq. Faqat 1, 2, 3 yoki 4 ni kiriting.")
            input("  Enter bosing...")

# ============================================================
if __name__ == "__main__":
    try:
        asosiy_menyu()
    except KeyboardInterrupt:
        print("\n\n  ⏹ Dastur to'xtatildi (Ctrl+C)\n")