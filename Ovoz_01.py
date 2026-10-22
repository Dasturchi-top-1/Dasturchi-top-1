import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import os
import re

FON = "#0d0d0d"
YASHIL = "#39ff14"
KOK = "#00c8ff"
PANEL = "#111a24"

AI_PAPKA = "/storage/emulated/0/AI/musiqa"

TILLAR = {
    "Ingliz tili": "en",
    "Rus tili": "ru",
    "Turk tili": "tr",
}

def fayl_nomini_tozala(soz):
    soz = re.sub(r'[^\w\-]', '', soz, flags=re.UNICODE)
    return soz if soz else "ovoz"

def yagona_fayl_nomi_top(papka, asosiy_nom):
    fayl_yoli = os.path.join(papka, f"{asosiy_nom}.mp3")
    if not os.path.exists(fayl_yoli):
        return fayl_yoli
    hisob = 2
    while True:
        yangi = os.path.join(papka, f"{asosiy_nom}_{hisob}.mp3")
        if not os.path.exists(yangi):
            return yangi
        hisob += 1

class MatnOvozIlovasi:
    def __init__(self, oyna):
        self.oyna = oyna
        oyna.title("MATN -> OVOZ :: 921324")
        oyna.geometry("380x500")
        oyna.configure(bg=FON)

        tk.Label(oyna, text=">> MATN -> OVOZ KONVERTORI <<", font=("Courier", 13, "bold"),
                 bg=FON, fg=YASHIL).pack(pady=(15, 0))
        tk.Label(oyna, text="[ NODE: 921324 ]", font=("Courier", 9),
                 bg=FON, fg=KOK).pack(pady=(0, 12))

        # --- MATN -> OVOZ QISMI ---
        self.matn_input = scrolledtext.ScrolledText(
            oyna, height=12, font=("Courier", 10), bg=PANEL, fg=YASHIL,
            insertbackground=YASHIL, wrap=tk.WORD
        )
        self.matn_input.pack(padx=15, pady=6, fill="x")

        til_freym = tk.Frame(oyna, bg=FON)
        til_freym.pack(pady=4)
        tk.Label(til_freym, text="Til:", font=("Courier", 10), bg=FON, fg=YASHIL).pack(side="left", padx=4)
        self.til_tanlov = tk.StringVar(value="Ingliz tili")
        til_menyu = tk.OptionMenu(til_freym, self.til_tanlov, *TILLAR.keys())
        til_menyu.config(font=("Courier", 10), bg=PANEL, fg=YASHIL,
                          activebackground=YASHIL, activeforeground=FON, highlightthickness=0)
        til_menyu.pack(side="left")

        tk.Button(oyna, text="[ OVOZGA AYLANTIRISH ]", font=("Courier", 11, "bold"),
                  bg=PANEL, fg=YASHIL, activebackground=YASHIL, activeforeground=FON,
                  command=self.ovozga_aylantir_bosildi).pack(pady=8)

        # --- ESHITISH / O'CHIRISH TUGMALARI ---
        self.amal_freym = tk.Frame(oyna, bg=FON)
        self.eshitish_tugma = tk.Button(
            self.amal_freym, text="[ ▶ ESHITISH ]", font=("Courier", 10, "bold"),
            bg=PANEL, fg=YASHIL, activebackground=YASHIL, activeforeground=FON,
            command=self.eshitish_bosildi
        )
        self.ochirish_tugma = tk.Button(
            self.amal_freym, text="[ 🗑 O'CHIRISH ]", font=("Courier", 10, "bold"),
            bg="#330000", fg="#ff4444", activebackground="#ff4444", activeforeground=FON,
            command=self.ochirish_bosildi
        )
        self.eshitish_tugma.pack(side="left", padx=6)
        self.ochirish_tugma.pack(side="left", padx=6)
        self.oxirgi_fayl = None

        # --- LOG PANELI ---
        tk.Label(oyna, text="── TIZIM JURNALI ──", font=("Courier", 10, "bold"),
                 bg=FON, fg=KOK).pack(pady=(10, 0))
        self.log = scrolledtext.ScrolledText(
            oyna, height=6, font=("Courier", 9), bg="#000000", fg=YASHIL,
            wrap=tk.WORD, state=tk.DISABLED
        )
        self.log.pack(padx=15, pady=8, fill="both", expand=True)

    def logga_yoz(self, matn):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, matn + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def ovozga_aylantir_bosildi(self):
        matn = self.matn_input.get("1.0", tk.END).strip()
        if not matn:
            self.logga_yoz("[XATOLIK] Matn kiritilmadi.")
            return
        til_nomi = self.til_tanlov.get()
        til_kodi = TILLAR[til_nomi]
        self.amal_freym.pack_forget()
        self.logga_yoz(f"[TIZIM] Ovoz tayyorlanmoqda ({til_nomi})...")
        threading.Thread(target=self._ovozga_aylantir_ishla, args=(matn, til_kodi), daemon=True).start()

    def _ovozga_aylantir_ishla(self, matn, til_kodi):
        try:
            from gtts import gTTS
            os.makedirs(AI_PAPKA, exist_ok=True)
            birinchi_soz = fayl_nomini_tozala(matn.split()[0])
            fayl_yoli = yagona_fayl_nomi_top(AI_PAPKA, birinchi_soz)
            silliq_matn = re.sub(r'\s*\n\s*', ', ', matn)
            silliq_matn = re.sub(r'\s+', ' ', silliq_matn).strip()
            tts = gTTS(text=silliq_matn, lang=til_kodi)
            tts.save(fayl_yoli)
            self.oxirgi_fayl = fayl_yoli
            self.oyna.after(0, self.logga_yoz, f"[TIZIM] >> Fayl saqlandi: {fayl_yoli}")
            self.oyna.after(0, lambda: self.amal_freym.pack(pady=(0, 8)))
        except Exception as xato:
            self.oyna.after(0, self.logga_yoz, f"[XATOLIK] {xato}")

    def eshitish_bosildi(self):
        if not self.oxirgi_fayl or not os.path.isfile(self.oxirgi_fayl):
            self.logga_yoz("[XATOLIK] Eshitish uchun fayl topilmadi.")
            return
        buyruq = f'am start -a android.intent.action.VIEW -d "file://{self.oxirgi_fayl}" -t audio/mp3 -f 0x10000000'
        os.system(buyruq)

    def ochirish_bosildi(self):
        if self.oxirgi_fayl and os.path.isfile(self.oxirgi_fayl):
            os.remove(self.oxirgi_fayl)
            self.logga_yoz(f"[TIZIM] Fayl o'chirildi.")
            self.oxirgi_fayl = None
            self.amal_freym.pack_forget()

asosiy = tk.Tk()
ilova = MatnOvozIlovasi(asosiy)
asosiy.mainloop()
