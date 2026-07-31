import os
import random
import tkinter as tk
from tkinter import messagebox

# ============================================================
#  1. GLOBAL RANG KODLARI
# ============================================================
FON = "#0d0d0d"
KOK = "#00c8ff"
YASHIL = "#39ff14"
PANEL = "#111a24"

FON_RANGLARI = {
    "qora": "#0d0d0d",
    "oq": "#f5f5f5",
}

TUGMA_RANGLARI = {
    "yashil": "#39ff14",
    "kok": "#00c8ff",
    "qizil": "#ff4444",
}

# ============================================================
#  2. KOD GENERATORI UCHUN SHABLONLAR
# ============================================================
SHABLON_KALKULYATOR = '''import tkinter as tk

oyna = tk.Tk()
oyna.title("{SARLAVHA}")
oyna.geometry("280x380")
oyna.configure(bg="{FON_RANG}")

natija = tk.Entry(oyna, font=("Courier", 14), justify="right",
                   bg="{FON_RANG}", fg="{TUGMA_RANG}", insertbackground="{TUGMA_RANG}")
natija.pack(fill="x", padx=5, pady=5, ipady=5)

ifoda = ""

def tugma_bosildi(qiymat):
    global ifoda
    ifoda += str(qiymat)
    natija.delete(0, tk.END)
    natija.insert(0, ifoda)

def hisobla():
    global ifoda
    try:
        natija.delete(0, tk.END)
        natija.insert(0, str(eval(ifoda)))
        ifoda = ""
    except Exception:
        natija.delete(0, tk.END)
        natija.insert(0, "XATOLIK")
        ifoda = ""

def tozala():
    global ifoda
    ifoda = ""
    natija.delete(0, tk.END)

tugmalar = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
]

freym = tk.Frame(oyna, bg="{FON_RANG}")
freym.pack(expand=True, fill="both")

for qator in tugmalar:
    qator_freym = tk.Frame(freym, bg="{FON_RANG}")
    qator_freym.pack(expand=True, fill="both")
    for belgi in qator:
        if belgi == "=":
            komanda = hisobla
        else:
            komanda = lambda b=belgi: tugma_bosildi(b)
        tk.Button(qator_freym, text=belgi, font=("Courier", 11, "bold"),
                  bg="#111a24", fg="{TUGMA_RANG}", activebackground="{TUGMA_RANG}",
                  activeforeground="{FON_RANG}", command=komanda).pack(side="left", expand=True, fill="both")

tk.Button(oyna, text="TOZALASH", font=("Courier", 10, "bold"),
          bg="#330000", fg="{TUGMA_RANG}", command=tozala).pack(fill="x", padx=5, pady=5)

oyna.mainloop()
'''

SHABLON_TODO = '''import tkinter as tk

oyna = tk.Tk()
oyna.title("{SARLAVHA}")
oyna.geometry("300x400")
oyna.configure(bg="{FON_RANG}")

kirish = tk.Entry(oyna, font=("Courier", 10), bg="#111a24", fg="{TUGMA_RANG}",
                   insertbackground="{TUGMA_RANG}")
kirish.pack(fill="x", padx=5, pady=5)

royxat = tk.Listbox(oyna, font=("Courier", 10), bg="#000000", fg="{TUGMA_RANG}",
                     selectbackground="{TUGMA_RANG}", selectforeground="{FON_RANG}")
royxat.pack(expand=True, fill="both", padx=5, pady=2)

def qoshish():
    matn = kirish.get().strip()
    if matn:
        royxat.insert(tk.END, matn)
        kirish.delete(0, tk.END)

def ochirish():
    tanlangan = royxat.curselection()
    if tanlangan:
        royxat.delete(tanlangan[0])

tugmalar_freym = tk.Frame(oyna, bg="{FON_RANG}")
tugmalar_freym.pack(fill="x", padx=5, pady=5)

tk.Button(tugmalar_freym, text="QO'SHISH", font=("Courier", 9, "bold"),
          bg="#111a24", fg="{TUGMA_RANG}", command=qoshish).pack(side="left", expand=True, fill="x")
tk.Button(tugmalar_freym, text="O'CHIRISH", font=("Courier", 9, "bold"),
          bg="#330000", fg="{TUGMA_RANG}", command=ochirish).pack(side="left", expand=True, fill="x")

oyna.mainloop()
'''

SHABLON_GUESS_NUMBER = '''import tkinter as tk
import random

MAXFIY_SON = random.randint(1, 100)
urinishlar = 0

oyna = tk.Tk()
oyna.title("{SARLAVHA}")
oyna.geometry("280x320")
oyna.configure(bg="{FON_RANG}")

tk.Label(oyna, text="1 dan 100 gacha sonni top!", font=("Courier", 10, "bold"),
         bg="{FON_RANG}", fg="{TUGMA_RANG}").pack(pady=10)

kirish = tk.Entry(oyna, font=("Courier", 12), justify="center",
                   bg="#111a24", fg="{TUGMA_RANG}", insertbackground="{TUGMA_RANG}")
kirish.pack(pady=5)

natija_label = tk.Label(oyna, text="", font=("Courier", 10, "bold"),
                         bg="{FON_RANG}", fg="{TUGMA_RANG}", wraplength=240)
natija_label.pack(pady=10)

def tekshir():
    global urinishlar
    try:
        taxmin = int(kirish.get())
    except ValueError:
        natija_label.config(text="Faqat son kiriting!")
        return

    urinishlar += 1
    if taxmin < MAXFIY_SON:
        natija_label.config(text="Ko'proq! (" + str(urinishlar) + "-urinish)")
    elif taxmin > MAXFIY_SON:
        natija_label.config(text="Kamroq! (" + str(urinishlar) + "-urinish)")
    else:
        natija_label.config(text="TOPDING! " + str(urinishlar) + " ta urinishda!")

tk.Button(oyna, text="TEKSHIRISH", font=("Courier", 10, "bold"),
          bg="#111a24", fg="{TUGMA_RANG}", activebackground="{TUGMA_RANG}",
          activeforeground="{FON_RANG}", command=tekshir).pack(pady=5)

oyna.mainloop()
'''

SHABLONLAR = {
    "kalkulyator": SHABLON_KALKULYATOR,
    "todo": SHABLON_TODO,
    "guess_number": SHABLON_GUESS_NUMBER,
}

def kod_generatsiya_qil(tur, sarlavha="Blip Production", fon="qora", tugma="yashil", chiqish_papka="."):
    if tur not in SHABLONLAR:
        return None
    fon_rang = FON_RANGLARI.get(fon, FON_RANGLARI["qora"])
    tugma_rang = TUGMA_RANGLARI.get(tugma, TUGMA_RANGLARI["yashil"])
    shablon = SHABLONLAR[tur]
    tayyor_kod = shablon.replace("{SARLAVHA}", sarlavha).replace("{FON_RANG}", fon_rang).replace("{TUGMA_RANG}", tugma_rang)
    fayl_nomi = f"generatsiya_{tur}.py"
    fayl_yoli = os.path.join(chiqish_papka, fayl_nomi)
    with open(fayl_yoli, "w", encoding="utf-8") as f:
        f.write(tayyor_kod)
    return fayl_yoli

# ============================================================
#  3. MODULLAR KODLARI (TOPLEVEL OYNALAR)
# ============================================================

# --- MODUL 1: AVTO-EKSPERT ---
class AvtoEkspertOyna(tk.Toplevel):
    def __init__(self, ustoz):
        super().__init__(ustoz)
        self.title("AVTO-EKSPERT PRO")
        self.geometry("320x400")
        self.configure(bg=FON)
        
        tk.Label(self, text="🚗 AVTO-EKSPERT MATRIX", font=("Courier", 11, "bold"), bg=FON, fg=YASHIL).pack(pady=10)
        tk.Label(self, text="Muammoni yozing (motor, tormoz, elektr):", font=("Courier", 8), bg=FON, fg=KOK).pack(pady=2)
        
        self.muammo_input = tk.Entry(self, font=("Courier", 10), bg=PANEL, fg=YASHIL, insertbackground=YASHIL)
        self.muammo_input.pack(pady=5, padx=15, fill="x")
        
        tk.Button(self, text="[ DIAGNOSTIKA ]", font=("Courier", 9, "bold"), bg=PANEL, fg=YASHIL, command=self.tashxis).pack(pady=5)
        
        self.natija_box = tk.Label(self, text="Tizim tayyor...", font=("Courier", 8), bg=PANEL, fg=KOK, justify="left", wraplength=280, height=8, relief="solid")
        self.natija_box.pack(pady=10, padx=15, fill="both", expand=True)

    def tashxis(self):
        matn = self.muammo_input.get().lower()
        if "motor" in matn or "dvigatel" in matn:
            res = ">> TASHXIS: Motor qizishi yoki moy bosimi past.\n>> YECHIM: Moy darajasini tekshiring, antifriz quying."
        elif "tormoz" in matn:
            res = ">> TASHXIS: Tormoz kolodkalari yeyilgan yoki suyuqlik kam.\n>> YECHIM: Kolodkani almashtiring, suyuqlik darajasini ko'ring."
        elif "elektr" in matn or "akkumulyator" in matn:
            res = ">> TASHXIS: Akkumulyator quvvati past.\n>> YECHIM: Generator kuchlanishini multimetrda o'lchang."
        else:
            res = ">> TASHXIS: Umumiy nosozlik aniqlanmadi.\n>> YECHIM: Filtrlarni tekshirish tavsiya etiladi."
        self.natija_box.config(text=res, fg=YASHIL)

# --- MODUL 2: MINING TERMINAL ---
class MiningOyna(tk.Toplevel):
    def __init__(self, ustoz):
        super().__init__(ustoz)
        self.title("MINING TERMINAL")
        self.geometry("320x400")
        self.configure(bg=FON)
        self.balans = 0.0
        self.mining_ishlayapti = False

        tk.Label(self, text="⛏️ BLIP CRYPTO MINER v1.0", font=("Courier", 11, "bold"), bg=FON, fg=KOK).pack(pady=10)
        self.balans_label = tk.Label(self, text="Balans: 0.00000000 BTC", font=("Courier", 10, "bold"), bg=FON, fg=YASHIL).pack(pady=5)
        
        self.log_box = tk.Label(self, text="[Kiber-kon tayyor]", font=("Courier", 8), bg=PANEL, fg=KOK, justify="left", wraplength=280, height=10, relief="solid")
        self.log_box.pack(pady=5, padx=15, fill="both", expand=True)

        self.start_btn = tk.Button(self, text="[ START MINING ]", font=("Courier", 9, "bold"), bg=PANEL, fg=YASHIL, command=self.start_toggle)
        self.start_btn.pack(pady=10)

    def start_toggle(self):
        if not self.mining_ishlayapti:
            self.mining_ishlayapti = True
            self.start_btn.config(text="[ STOP MINING ]", fg="#ff4444")
            self.looptik()
        else:
            self.mining_ishlayapti = False
            self.start_btn.config(text="[ START MINING ]", fg=YASHIL)

    def looptik(self):
        if self.mining_ishlayapti:
            topildi = random.choice([True, False, False])
            hash_rate = random.randint(400, 500)
            if topildi:
                ulush = random.uniform(0.000001, 0.000005)
                self.balans += ulush
                for child in self.winfo_children():
                    if isinstance(child, tk.Label) and "Balans:" in child.cget("text"):
                        child.config(text=f"Balans: {self.balans:.8f} BTC")
                self.log_box.config(text=f">> Blok topildi!\n>> Hash: {hash_rate} MH/s\n>> +{ulush:.8f} BTC qo'shildi.", fg=YASHIL)
            else:
                self.log_box.config(text=f">> Kon qazilmoqda...\n>> Hash: {hash_rate} MH/s\n>> Yangi blok qidirilmoqda...", fg=KOK)
            self.after(1500, self.looptik)

# --- MODUL 3: XAVFSIZLIK TERMINALI ---
class XavfsizlikOyna(tk.Toplevel):
    def __init__(self, ustoz):
        super().__init__(ustoz)
        self.title("XAVFSIZLIK TERMINALI")
        self.geometry("320x400")
        self.configure(bg=FON)

        tk.Label(self, text="🔐 SECURITY SHIELD", font=("Courier", 11, "bold"), bg=FON, fg=YASHIL).pack(pady=10)
        
        tk.Button(self, text="[ SHIFRLASH (AES) ]", font=("Courier", 9, "bold"), bg=PANEL, fg=KOK, width=20, command=self.shifrlash_oyna).pack(pady=10)
        tk.Button(self, text="[ ANTIVIRUS SKANER ]", font=("Courier", 9, "bold"), bg=PANEL, fg=YASHIL, width=20, command=self.skaner_boshla).pack(pady=10)
        
        self.status_box = tk.Label(self, text="Kiber-mudofaa faol.", font=("Courier", 8), bg=PANEL, fg=YASHIL, height=5, width=30, relief="solid")
        self.status_box.pack(pady=15)

    def shifrlash_oyna(self):
        messagebox.showinfo("Kiber-Shifr", "Matnlarni kiber-kodga shifrlash faol!")

    def skaner_boshla(self):
        self.status_box.config(text=">> Skanerlash boshlandi...\n>> Fayllar tekshirilmoqda...\n>> Pydroid 3: TOZA! ✅", fg=YASHIL)

# --- MODUL 4: KOD GENERATORI ---
class KodGeneratoriOyna(tk.Toplevel):
    def __init__(self, ustoz):
        super().__init__(ustoz)
        self.title("KOD GENERATORI")
        self.geometry("340x480")
        self.configure(bg=FON)

        tk.Label(self, text=">> KOD GENERATORI <<", font=("Courier", 11, "bold"), bg=FON, fg=YASHIL).pack(pady=(10, 0))
        tk.Label(self, text="[ PARAMETR TIZIMI ]", font=("Courier", 8), bg=FON, fg=KOK).pack(pady=(0, 10))

        tk.Label(self, text="Dastur sarlavhasi:", font=("Courier", 9), bg=FON, fg=YASHIL).pack()
        self.sarlavha_input = tk.Entry(self, font=("Courier", 10), bg=PANEL, fg=YASHIL, insertbackground=YASHIL, justify="center")
        self.sarlavha_input.pack(pady=4, padx=15, fill="x")
        self.sarlavha_input.insert(0, "Blip Production")

        tk.Label(self, text="Dastur turi:", font=("Courier", 9), bg=FON, fg=YASHIL).pack(pady=(5, 0))
        self.tur_tanlov = tk.StringVar(value="kalkulyator")
        self._menyu_yasa(self.tur_tanlov, ["kalkulyator", "todo", "guess_number"])

        tk.Label(self, text="Fon rangi:", font=("Courier", 9), bg=FON, fg=YASHIL).pack(pady=(5, 0))
        self.fon_tanlov = tk.StringVar(value="qora")
        self._menyu_yasa(self.fon_tanlov, ["qora", "oq"])

        tk.Label(self, text="Tugma rangi:", font=("Courier", 9), bg=FON, fg=YASHIL).pack(pady=(5, 0))
        self.tugma_tanlov = tk.StringVar(value="yashil")
        self._menyu_yasa(self.tugma_tanlov, ["yashil", "kok", "qizil"])

        tk.Button(self, text="[ GENERATSIYA ]", font=("Courier", 10, "bold"), bg=PANEL, fg=YASHIL, activebackground=YASHIL, activeforeground=FON, command=self.generatsiya_qil).pack(pady=15)

        self.natija_label = tk.Label(self, text="", font=("Courier", 8, "bold"), bg=FON, fg=YASHIL, wraplength=300, justify="left")
        self.natija_label.pack(pady=5, padx=15)

    def _menyu_yasa(self, ozgaruvchi, variantlar):
        menyu = tk.OptionMenu(self, ozgaruvchi, *variantlar)
        menyu.config(font=("Courier", 9), bg=PANEL, fg=YASHIL, activebackground=YASHIL, activeforeground=FON, highlightthickness=0, width=15)
        menyu["menu"].config(font=("Courier", 9), bg=PANEL, fg=YASHIL)
        menyu.pack(pady=3)

    def generatsiya_qil(self):
        sarlavha = self.sarlavha_input.get().strip() or "Blip Production"
        tur = self.tur_tanlov.get()
        fon = self.fon_tanlov.get()
        tugma = self.tugma_tanlov.get()
        try:
            fayl_yoli = kod_generatsiya_qil(tur, sarlavha, fon, tugma)
            self.natija_label.config(text=f">> TO'G'RI TUGALLANDI!\nFayl: {fayl_yoli}", fg=YASHIL)
            messagebox.showinfo("Blip AI", f"Kod generatsiya qilindi:\n{fayl_yoli}")
        except Exception as xato:
            self.natija_label.config(text=f">> XATOLIK: {xato}", fg="#ff4444")

# ============================================================
#  4. ASOSIY BOSHMENYU KLASSI (BLIP HUB)
# ============================================================
class BlipHub:
    def __init__(self, oyna):
        self.oyna = oyna
        oyna.title("BLIP HUB")
        oyna.geometry("340x500") # Bosh oyna ixchamroq qilindi
        oyna.configure(bg=FON)

        tk.Label(oyna, text=">> BLIP PRODUCTION <<", font=("Courier", 14, "bold"), bg=FON, fg=YASHIL).pack(pady=(20, 0))
        tk.Label(oyna, text="[ PROJECT CODE: 921324 ]", font=("Courier", 9), bg=FON, fg=KOK).pack(pady=(2, 4))
        tk.Label(oyna, text="Kiber-atlet darajasi: 32/32 ✅", font=("Courier", 9, "bold"), bg=FON, fg=YASHIL).pack(pady=(0, 20))

        modullar = [
            ("🚗 AVTO-EKSPERT PRO", YASHIL, lambda: AvtoEkspertOyna(oyna)),
            ("⛏️ MINING TERMINAL", KOK, lambda: MiningOyna(oyna)),
            ("🔐 XAVFSIZLIK TERMINALI", YASHIL, lambda: XavfsizlikOyna(oyna)),
            ("⚙️ KOD GENERATORI", KOK, lambda: KodGeneratoriOyna(oyna)),
        ]

        for matn, rang, komanda in modullar:
            tk.Button(oyna, text=matn, font=("Courier", 10, "bold"), bg=PANEL, fg=rang, activebackground=rang, activeforeground=FON, width=22, height=1, command=komanda).pack(pady=5)

        tk.Button(oyna, text="[ SISTEMANI YOPISH ]", font=("Courier", 9, "bold"), bg="#330000", fg="#ff4444", activebackground="#ff4444", activeforeground=FON, command=self.chiqish).pack(pady=20)

    def chiqish(self):
        if messagebox.askyesno("Chiqish", "Hub'dan chiqasiizmi?"):
            self.oyna.destroy()

# ============================================================
#  5. ISHGA TUSHIRISH
# ============================================================
if __name__ == "__main__":
    asosiy = tk.Tk()
    hub = BlipHub(asosiy)
    asosiy.mainloop()
