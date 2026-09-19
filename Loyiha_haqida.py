import os, ast, re, requests

OPENROUTER_API_KEY = "YOUR_OPENROUTER_KEY"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def rang(matn, kod=GREEN):
    return kod + matn + RESET

def faylni_oqish(fayl_yoli):
    try:
        with open(fayl_yoli, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(fayl_yoli, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            return f"[O'QIB BO'LMADI: {e}]"
    except Exception as e:
        return f"[XATO: {e}]"

def tahlil_qilish(matn):
    natija = {
        "importlar": [],
        "funksiyalar": [],
        "sinflar": [],
        "dekoratorlar": [],
        "satriar": len(matn.splitlines()),
        "belgilar": len(matn),
    }
    try:
        daraxt = ast.parse(matn)
    except SyntaxError as e:
        natija["xato"] = str(e)
        return natija

    for tugun in ast.walk(daraxt):
        if isinstance(tugun, ast.Import):
            for alias in tugun.names:
                natija["importlar"].append(alias.name)
        elif isinstance(tugun, ast.ImportFrom):
            modul = tugun.module or ""
            for alias in tugun.names:
                natija["importlar"].append(f"{modul}.{alias.name}" if modul else alias.name)
        elif isinstance(tugun, ast.FunctionDef):
            natija["funksiyalar"].append(tugun.name)
            for dec in tugun.decorator_list:
                if isinstance(dec, ast.Name):
                    natija["dekoratorlar"].append(dec.id)
                elif isinstance(dec, ast.Call):
                    func = dec.func
                    if isinstance(func, ast.Name):
                        natija["dekoratorlar"].append(func.id)
                    elif isinstance(func, ast.Attribute):
                        natija["dekoratorlar"].append(func.attr)
        elif isinstance(tugun, ast.ClassDef):
            natija["sinflar"].append(tugun.name)

    return natija

def kod_turini_aniqlash(tahlil):
    importlar = " ".join(tahlil.get("importlar", [])).lower()
    if "flask" in importlar or "socketio" in importlar:
        return "🌐 Veb-server (Flask yoki SocketIO)"
    if "telebot" in importlar or "aiogram" in importlar:
        return "🤖 Telegram bot"
    if "kivy" in importlar or "kivymd" in importlar:
        return "📱 Kivy ilovasi"
    if "requests" in importlar and "beautifulsoup" in importlar:
        return "🕷 Veb-scraping"
    if "sqlite3" in importlar and "flask" not in importlar:
        return "🗄 Ma'lumotlar bazasi"
    if "numpy" in importlar or "pandas" in importlar:
        return "📊 Ma'lumotlar tahlili"
    if "pygame" in importlar:
        return "🎮 O'yin"
    if "os" in importlar and "subprocess" in importlar:
        return "⚙️ Tizim boshqaruvi"
    if not tahlil.get("funksiyalar") and not tahlil.get("sinflar"):
        return "📄 Oddiy skript"
    return "🐍 Python dastur"

def ai_tushuntirish(matn):
    if OPENROUTER_API_KEY == "SIZNING_OPENROUTER_KALITINGIZ":
        return None
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Blip Kivy Analyzer"
    }
    prompt = (
        "Quyidagi Python kodini ko'rib chiqing va uning nima qilishini "
        "2-3 ta oddiy gapda o'zbek tilida tushuntiring.\n\n"
        f"```python\n{matn[:1500]}\n```"
    )
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 300
    }
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return None
    except:
        return None

def fayl_tahlili(fayl_yoli, indeks=None):
    nomi = os.path.basename(fayl_yoli)
    if indeks:
        print(rang(f"--- {indeks}. {nomi} ---", GREEN))
    else:
        print(rang(f"--- {nomi} ---", GREEN))
    print(f"📍 Joylashuv: {fayl_yoli}")

    matn = faylni_oqish(fayl_yoli)
    tahlil = tahlil_qilish(matn)

    if "xato" in tahlil:
        print(rang(f"❌ Sintaksis xatosi: {tahlil['xato']}", RED))
    else:
        tur = kod_turini_aniqlash(tahlil)
        print(f"🔹 Kod turi: {rang(tur, YELLOW)}")
        print(f"📏 Satrlar: {tahlil['satriar']} | Belgilar: {tahlil['belgilar']}")

        if tahlil["importlar"]:
            unikal = list(dict.fromkeys(tahlil["importlar"]))[:10]
            print(f"📦 Importlar: {', '.join(unikal)}")

        if tahlil["funksiyalar"]:
            print(f"⚙️ Funksiyalar ({len(tahlil['funksiyalar'])}): {', '.join(tahlil['funksiyalar'][:8])}")

        if tahlil["sinflar"]:
            print(f"🏛 Sinflar ({len(tahlil['sinflar'])}): {', '.join(tahlil['sinflar'][:8])}")

        if tahlil["dekoratorlar"]:
            unikal_deko = list(dict.fromkeys(tahlil["dekoratorlar"]))[:5]
            print(f"🎯 Dekoratorlar: {', '.join(unikal_deko)}")

        ai_mavjud = OPENROUTER_API_KEY != "SIZNING_OPENROUTER_KALITINGIZ"
        if ai_mavjud:
            print("⏳ AI tahlil qilmoqda...")
            izoh = ai_tushuntirish(matn)
            if izoh:
                print(rang(f"🤖 AI: {izoh}"))
            else:
                print(rang("⚠️ AI javob bermadi.", YELLOW))
        else:
            print(rang("💡 AI tushuntirish uchun OPENROUTER_API_KEY ni qo'shing.", YELLOW))
    print()

def asosiy():
    print(rang("=" * 60))
    print(rang("  BLIP KIVY AI CODE ANALYZER", GREEN))
    print(rang("=" * 60))

    yol = input(rang("Fayl yoki papka yo'lini kiriting\n(bo'sh qoldirsangiz: /storage/emulated/0/.kivy): ", YELLOW)).strip()
    if not yol:
        yol = "/storage/emulated/0/.kivy"

    if os.path.isfile(yol):
        fayl_tahlili(yol)
    elif os.path.isdir(yol):
        py_fayllar = []
        for ildiz, papkalar, fayllar in os.walk(yol):
            for f in fayllar:
                if f.endswith(".py"):
                    py_fayllar.append(os.path.join(ildiz, f))
        if not py_fayllar:
            print(rang("📄 Bu papkada .py fayl topilmadi.", YELLOW))
            return
        print(rang(f"\n📁 Jami {len(py_fayllar)} ta Python fayl topildi.\n", BLUE))
        for idx, f in enumerate(py_fayllar, 1):
            fayl_tahlili(f, idx)
    else:
        print(rang("❌ Bunday fayl yoki papka mavjud emas!", RED))
        return

    print(rang("=" * 60))
    print(rang("Tahlil yakunlandi!", GREEN))

if __name__ == "__main__":
    asosiy()