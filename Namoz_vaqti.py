# ============================================================
# BLIP NAMOZ VAQTLARI v4.0 — Tojikiston
# Fayl: blip_namoz.py
# Koordinata usuli • 12-soatlik format • Qolgan vaqt
# ============================================================
import os
import json
import time
import datetime
import urllib.request
import urllib.error

# ---------- TOJIKISTON JOYLARI ----------
JOYLAR = {
    "1":  ("Dushanbe (poytaxt)",   38.5598, 68.7870),
    "2":  ("Khujand",              40.2833, 69.6333),
    "3":  ("Kulob",                37.9094, 69.7844),
    "4":  ("Bokhtar",              37.8366, 68.7800),
    "5":  ("Istaravshan",          39.9142, 69.0033),
    "6":  ("Panjakent",            39.4950, 67.6100),
    "7":  ("Tursunzoda",           38.5100, 68.2300),
    "8":  ("Vahdat",               38.5500, 69.0200),
    "9":  ("Konibodom",            40.2900, 70.4200),
    "10": ("Isfara",               40.1200, 70.6300),
    "11": ("Hisor",                38.5200, 68.5500),
    "12": ("Nurek",                38.3900, 69.3200),
    "13": ("Danghara",             37.9400, 69.1000),
    "14": ("Farkhor",              37.4900, 69.3900),
    "15": ("Qurgonteppa",          37.8300, 68.7800),
    "16": ("Sultonobod (Rudakiy)", 38.4787, 68.8067),
    "17": ("Shahraki Somoniyon",   38.5000, 68.7500),
    "18": ("Rudakiy tumani",       38.4787, 68.8067),
    "19": ("Yovon",                38.3100, 69.0400),
    "20": ("Varzob",               38.7700, 68.8200),
    "21": ("Shahrinav",            38.5700, 68.3300),
    "22": ("Hisor (tuman)",        38.5200, 68.5500),
    "23": ("Ayni",                 39.3900, 68.5400),
    "24": ("Zafarobod",            40.1800, 68.8300),
    "25": ("Asht",                 40.6700, 70.3400),
    "26": ("Devastich",            40.1900, 69.6800),
    "27": ("Kuhistoni Mastchoh",   39.5000, 69.5000),
    "28": ("Bobojon Ghafurov",     40.2200, 69.7300),
    "29": ("Jabbor Rasulov",       40.2000, 69.1000),
    "30": ("Jaloliddin Rumiy",     37.5000, 68.5000),
    "31": ("Vakhsh",               37.7000, 68.8300),
    "32": ("Jayhun",               37.4800, 68.5900),
    "33": ("Qubodiyon",            37.4100, 68.1900),
    "34": ("Shahritus",            37.2600, 68.1400),
    "35": ("Nosiri Khusrav",       37.2200, 68.1400),
}

# ---------- NAMOZLAR ----------
NAMOZLAR = [
    ("Fajr",    "🌙 Bomdod"),
    ("Sunrise", "🌅 Quyosh chiqishi"),
    ("Dhuhr",   "☀️  Peshin"),
    ("Asr",     "🌤  Asr"),
    ("Maghrib", "🌆 Shom"),
    ("Isha",    "🌃 Xufton"),
]

# ============================================================
# VAQTNI O'GIRISH
# ============================================================
def vaqt_ozbek(vaqt):
    """04:40 → 04:40  |  15:49 → 3:49"""
    try:
        soat, daqiqa = vaqt[:5].split(":")
        soat = int(soat)
        daqiqa = int(daqiqa)
    except:
        return vaqt
    if soat < 12:
        return f"{soat:02d}:{daqiqa:02d}"
    if soat == 12:
        return f"12:{daqiqa:02d}"
    return f"{soat - 12}:{daqiqa:02d}"

# ============================================================
# QOLGAN VAQTNI HISOBLASH
# ============================================================
def qolgan_vaqt(vaqt_str):
    """(matn, holat) qaytaradi. holat: qoldi/hozir/otdi"""
    try:
        soat, daqiqa = map(int, vaqt_str[:5].split(":"))
    except:
        return ("—", "xato")
    
    hozir = datetime.datetime.now()
    namoz = hozir.replace(hour=soat, minute=daqiqa,
                          second=0, microsecond=0)
    farq = (namoz - hozir).total_seconds()
    
    if -60 <= farq <= 60:
        return ("🟢 HOZIR!", "hozir")
    elif farq > 0:
        s = int(farq // 3600)
        d = int((farq % 3600) // 60)
        if s > 0:
            return (f"⏳ {s} soat {d} daq qoldi", "qoldi")
        return (f"⏳ {d} daqiqa qoldi", "qoldi")
    else:
        s = int(abs(farq) // 3600)
        d = int((abs(farq) % 3600) // 60)
        if s > 0:
            return (f"✅ {s} soat {d} daq oldin", "otdi")
        return (f"✅ {d} daqiqa oldin", "otdi")

# ============================================================
# API SO'ROVI (QAYTA URINISH BILAN)
# ============================================================
def namoz_vaqtlari(lat, lon, urinish=3):
    url = (f"https://api.aladhan.com/v1/timings"
           f"?latitude={lat}&longitude={lon}&method=3")
    for i in range(1, urinish + 1):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "BlipNamoz/4.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode("utf-8"))
            return data["data"]
        except urllib.error.HTTPError as e:
            if i < urinish:
                print(f"  ⚠️  Server band ({e.code}). "
                      f"{i}/{urinish}... 3 sek kutish")
                time.sleep(3)
            else:
                return {"xato": f"Server xatosi ({e.code}). "
                                f"Keyinroq urinib ko'ring."}
        except Exception as e:
            if i < urinish:
                print(f"  ⚠️  {e}. {i}/{urinish}... qayta urinish")
                time.sleep(3)
            else:
                return {"xato": str(e)}
    return {"xato": "Noma'lum xato"}

# ============================================================
# CHIQARISH
# ============================================================
def chiqar(data, nom):
    if "xato" in data:
        print(f"\n  ❌ Xato: {data['xato']}")
        print(f"  💡 Internetni tekshiring yoki keyinroq urinib ko'ring.")
        return

    t = data["timings"]
    s = data["date"]

    print(f"\n{'=' * 60}")
    print(f"  🕌 NAMOZ VAQTLARI — {nom}")
    print(f"  📅 {s['readable']}  |  🌙 {s['hijri']['date']}")
    print(f"  🕋 Usul: Muslim World League")
    print(f"{'=' * 60}\n")

    # Keyingi namozni topish
    keyingi = None
    for kalit, nom_oz in NAMOZLAR:
        if kalit == "Sunrise":
            continue
        _, holat = qolgan_vaqt(t.get(kalit, ""))
        if holat == "qoldi":
            keyingi = nom_oz
            break

    for kalit, nom_oz in NAMOZLAR:
        vaqt = t.get(kalit, "—")
        vaqt_k = vaqt_ozbek(vaqt)
        matn, holat = qolgan_vaqt(vaqt)
        
        belgi = " ⬅️ KEYINGI" if (keyingi == nom_oz and holat == "qoldi") else ""
        
        if holat == "hozir":
            print(f"  🔔 {nom_oz:<22} {vaqt_k:<7} {matn}{belgi}")
        elif holat == "otdi":
            print(f"     {nom_oz:<22} {vaqt_k:<7} {matn}")
        else:
            print(f"     {nom_oz:<22} {vaqt_k:<7} {matn}{belgi}")

    print(f"\n{'=' * 60}\n")

# ============================================================
# AVTOMATIK YANGILASH
# ============================================================
def avtomatik(nom, lat, lon):
    """Har 60 sekundda vaqtni yangilab turadi."""
    print(f"\n  🔄 Avtomatik rejim (har 60 sekund)")
    print(f"  ⛔ To'xtatish: Ctrl+C\n")
    try:
        while True:
            os.system("clear" if os.name != "nt" else "cls")
            data = namoz_vaqtlari(lat, lon)
            chiqar(data, nom)
            print(f"  🔄 Keyingi yangilanish: 60 sekund...")
            time.sleep(60)
    except KeyboardInterrupt:
        print(f"\n  👋 To'xtatildi.\n")

# ============================================================
# MENYU
# ============================================================
def menyu():
    while True:
        print(f"""
{'=' * 60}
  🕌 BLIP NAMOZ VAQTLARI v4.0 — Tojikiston
{'=' * 60}""")
        joylar = list(JOYLAR.items())
        for i in range(0, len(joylar), 3):
            qator = "  "
            for j in range(3):
                if i + j < len(joylar):
                    k, (nom, _, _) = joylar[i + j]
                    qator += f"[{k:>2}] {nom:<22}"
            print(qator)
        print(f"""
  [0] 🚪 Chiqish
{'=' * 60}""")

        tanlov = input("  Tanlang: ").strip()

        if tanlov == "0":
            print(f"\n  👋 Xayr, Blip!\n")
            break
        elif tanlov in JOYLAR:
            nom, lat, lon = JOYLAR[tanlov]
            print(f"\n  ⏳ {nom} uchun yuklanmoqda...")
            data = namoz_vaqtlari(lat, lon)
            chiqar(data, nom)
            
            javob = input("  🔄 Avtomatik yangilash? (h/y): ").strip().lower()
            if javob == "h":
                avtomatik(nom, lat, lon)
        else:
            print("  ❌ Noto'g'ri tanlov.")

# ============================================================
# ASOSIY
# ============================================================
if __name__ == "__main__":
    os.system("clear" if os.name != "nt" else "cls")
    print(f"\n{'=' * 60}")
    print(f"  🕌 BLIP NAMOZ VAQTLARI v4.0")
    print(f"  Koordinata • 12-soat • Qolgan vaqt • Avto")
    print(f"{'=' * 60}")
    input(f"\n  ▶️  Boshlash uchun Enter bosing...")
    menyu()