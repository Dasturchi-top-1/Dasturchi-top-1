# ============================================================
# BLIP QURAN v2.0 — Tanlab yuklovchi (MP3 + Arabcha TXT)
# Fayl: blip_quran.py
# Qori: Mishary Rashid Alafasy
# ============================================================
import os
import json
import urllib.request

# ---------- SOZLAMALAR ----------
FOLDER = "/storage/emulated/0/Ai/Quran"
MP3_SERVER = "https://server8.mp3quran.net/afs"
API_BASE = "https://api.alquran.cloud/v1/surah"

# ---------- 114 SURA RO'YXATI ----------
SURALAR_DATA = """1|Al-Fatiha
2|Al-Baqarah
3|Aal-Imran
4|An-Nisa
5|Al-Maidah
6|Al-Anam
7|Al-Araf
8|Al-Anfal
9|At-Tawbah
10|Yunus
11|Hud
12|Yusuf
13|Ar-Rad
14|Ibrahim
15|Al-Hijr
16|An-Nahl
17|Al-Isra
18|Al-Kahf
19|Maryam
20|Ta-Ha
21|Al-Anbiya
22|Al-Hajj
23|Al-Muminun
24|An-Nur
25|Al-Furqan
26|Ash-Shuara
27|An-Naml
28|Al-Qasas
29|Al-Ankabut
30|Ar-Rum
31|Luqman
32|As-Sajdah
33|Al-Ahzab
34|Saba
35|Fatir
36|Ya-Sin
37|As-Saffat
38|Sad
39|Az-Zumar
40|Ghafir
41|Fussilat
42|Ash-Shura
43|Az-Zukhruf
44|Ad-Dukhan
45|Al-Jathiyah
46|Al-Ahqaf
47|Muhammad
48|Al-Fath
49|Al-Hujurat
50|Qaf
51|Adh-Dhariyat
52|At-Tur
53|An-Najm
54|Al-Qamar
55|Ar-Rahman
56|Al-Waqiah
57|Al-Hadid
58|Al-Mujadila
59|Al-Hashr
60|Al-Mumtahanah
61|As-Saff
62|Al-Jumuah
63|Al-Munafiqun
64|At-Taghabun
65|At-Talaq
66|At-Tahrim
67|Al-Mulk
68|Al-Qalam
69|Al-Haqqah
70|Al-Maarij
71|Nuh
72|Al-Jinn
73|Al-Muzzammil
74|Al-Muddaththir
75|Al-Qiyamah
76|Al-Insan
77|Al-Mursalat
78|An-Naba
79|An-Naziat
80|Abasa
81|At-Takwir
82|Al-Infitar
83|Al-Mutaffifin
84|Al-Inshiqaq
85|Al-Buruj
86|At-Tariq
87|Al-Ala
88|Al-Ghashiyah
89|Al-Fajr
90|Al-Balad
91|Ash-Shams
92|Al-Layl
93|Ad-Duha
94|Ash-Sharh
95|At-Tin
96|Al-Alaq
97|Al-Qadr
98|Al-Bayyinah
99|Az-Zalzalah
100|Al-Adiyat
101|Al-Qariah
102|At-Takathur
103|Al-Asr
104|Al-Humazah
105|Al-Fil
106|Quraysh
107|Al-Maun
108|Al-Kawthar
109|Al-Kafirun
110|An-Nasr
111|Al-Masad
112|Al-Ikhlas
113|Al-Falaq
114|An-Nas"""

# Parse qilish
SURALAR = {}
for qator in SURALAR_DATA.strip().split("\n"):
    r, nom = qator.split("|")
    SURALAR[int(r)] = nom.strip()

# ---------- TAYYOR TO'PLAMLAR ----------
NAMOZ_UCHUN = [1, 103, 108, 109, 110, 112, 113, 114]
JUZ_AMMA = list(range(78, 115))

# ---------- PAPKA ----------
def papka_yarat():
    try:
        os.makedirs(FOLDER, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Papka yaratilmadi: {e}")
        print("💡 Pydroid 3 da 'Storage' ruxsatini bering!")
        return False

# ---------- YUKLASH FUNKSIYALARI ----------
def fayl_nomi(raqam):
    return f"{raqam:03d}_{SURALAR.get(raqam, f'Sura-{raqam}')}"

def mp3_yukla(raqam):
    fayl = f"{FOLDER}/{fayl_nomi(raqam)}.mp3"
    if os.path.exists(fayl):
        return "bor"
    url = f"{MP3_SERVER}/{raqam:03d}.mp3"
    try:
        urllib.request.urlretrieve(url, fayl)
        return "yuklandi"
    except Exception as e:
        return f"xato: {e}"

def txt_yukla(raqam):
    fayl = f"{FOLDER}/{fayl_nomi(raqam)}.txt"
    if os.path.exists(fayl):
        return "bor"
    url = f"{API_BASE}/{raqam}/quran-uthmani"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
        s = data["data"]
        matn = f"سورة {s['name']}\n"
        matn += f"{s['englishName']} — {s['numberOfAyahs']} oyat\n"
        matn += "─" * 40 + "\n\n"
        for oyat in s["ayahs"]:
            matn += f"{oyat['text']} ﴿{oyat['numberInSurah']}﴾\n\n"
        with open(fayl, "w", encoding="utf-8") as f:
            f.write(matn)
        return "yuklandi"
    except Exception as e:
        return f"xato: {e}"

def yukla(raqamlar):
    if not raqamlar:
        print("\n⚠️  Hech narsa tanlanmadi.")
        return
    print(f"\n{'=' * 55}")
    print(f"  📥 {len(raqamlar)} ta sura yuklanmoqda...")
    print(f"{'=' * 55}")
    
    s = {"m_ok": 0, "m_bor": 0, "m_x": 0, "t_ok": 0, "t_bor": 0, "t_x": 0}
    
    for i, r in enumerate(raqamlar, 1):
        nom = SURALAR.get(r, f"Sura-{r}")
        print(f"\n[{i}/{len(raqamlar)}] 📖 {r}. {nom}")
        
        natija = mp3_yukla(r)
        if natija == "yuklandi":
            print(f"   🎧 MP3: ✅")
            s["m_ok"] += 1
        elif natija == "bor":
            print(f"   🎧 MP3: ⏭️  mavjud")
            s["m_bor"] += 1
        else:
            print(f"   🎧 MP3: ❌ {natija}")
            s["m_x"] += 1
        
        natija = txt_yukla(r)
        if natija == "yuklandi":
            print(f"   📝 TXT: ✅")
            s["t_ok"] += 1
        elif natija == "bor":
            print(f"   📝 TXT: ⏭️  mavjud")
            s["t_bor"] += 1
        else:
            print(f"   📝 TXT: ❌ {natija}")
            s["t_x"] += 1
    
    print(f"\n{'=' * 55}")
    print(f"  📊 NATIJA")
    print(f"{'=' * 55}")
    print(f"  🎧 MP3: ✅ {s['m_ok']} | ⏭️  {s['m_bor']} | ❌ {s['m_x']}")
    print(f"  📝 TXT: ✅ {s['t_ok']} | ⏭️  {s['t_bor']} | ❌ {s['t_x']}")
    print(f"  📁 {FOLDER}")
    print(f"{'=' * 55}")

# ---------- PARSE QILISH ----------
def raqamlarni_parse(matn):
    """'1,5,78-85' -> [1,5,78,79,...,85]"""
    natija = []
    for qism in matn.split(","):
        qism = qism.strip()
        if "-" in qism:
            try:
                a, b = qism.split("-")
                natija.extend(range(int(a), int(b) + 1))
            except:
                pass
        else:
            try:
                natija.append(int(qism))
            except:
                pass
    return sorted(set(r for r in natija if 1 <= r <= 114))

# ---------- MENYU FUNKSIYALARI ----------
def sura_royxati():
    print(f"\n{'=' * 55}")
    print(f"  📚 114 SURA RO'YXATI")
    print(f"{'=' * 55}")
    for r in range(1, 115):
        nom = SURALAR[r]
        # 3 ustunda chiqarish
        if r % 3 == 1 and r != 1:
            print()
        print(f"  {r:>3}. {nom:<18}", end="")
    print(f"\n{'=' * 55}")

def menyu():
    while True:
        print(f"""
{'=' * 55}
  🕌 BLIP QURAN — Tanlab yuklovchi
{'=' * 55}
  [1] 📚 Sura ro'yxatini ko'rish (1-114)
  [2] 🕌 Namoz uchun (1, 103, 108-110, 112-114)
  [3] 📖 Juz Amma (78-114)
  [4] ✏️  Raqam bilan tanlash
  [5] 🌍 Barcha 114 sura
  [0] 🚪 Chiqish
{'=' * 55}""")
        tanlov = input("  Tanlang: ").strip()
        
        if tanlov == "1":
            sura_royxati()
        
        elif tanlov == "2":
            print(f"\n  🕌 Namoz uchun: {', '.join(map(str, NAMOZ_UCHUN))}")
            if input("  Yuklaymizmi? (h/y): ").strip().lower() == "h":
                yukla(NAMOZ_UCHUN)
        
        elif tanlov == "3":
            print(f"\n  📖 Juz Amma: 78-114 ({len(JUZ_AMMA)} ta sura)")
            if input("  Yuklaymizmi? (h/y): ").strip().lower() == "h":
                yukla(JUZ_AMMA)
        
        elif tanlov == "4":
            print(f"\n  ✏️  Misol: 1,112,113,114 yoki 78-90 yoki 1,5,10-15")
            matn = input("  Raqamlar: ").strip()
            raqamlar = raqamlarni_parse(matn)
            if raqamlar:
                print(f"\n  Tanlandi: {', '.join(map(str, raqamlar))}")
                if input("  Yuklaymizmi? (h/y): ").strip().lower() == "h":
                    yukla(raqamlar)
            else:
                print("  ❌ Noto'g'ri format.")
        
        elif tanlov == "5":
            print(f"\n  🌍 Barcha 114 sura (~500 MB, uzoq vaqt)")
            if input("  Ishonchingiz komilmi? (h/y): ").strip().lower() == "h":
                yukla(list(range(1, 115)))
        
        elif tanlov == "0":
            print(f"\n  👋 Xayr, Blip!\n")
            break
        else:
            print("  ❌ Noto'g'ri tanlov.")

# ---------- ASOSIY ----------
if __name__ == "__main__":
    os.system("clear" if os.name != "nt" else "cls")
    print(f"\n{'=' * 55}")
    print(f"  🕌 BLIP QURAN v2.0")
    print(f"  Qori: Mishary Rashid Alafasy")
    print(f"  MP3 + Arabcha TXT yuklovchi")
    print(f"{'=' * 55}")
    
    if papka_yarat():
        print(f"  📁 Papka tayyor: {FOLDER}")
        print(f"  🎧 Jami suralar: 114")
        input(f"\n  ▶️  Boshlash uchun Enter bosing...")
        menyu()