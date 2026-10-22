import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

FON = "#0d0d0d"
YASHIL = "#39ff14"
KOK = "#00c8ff"
PANEL = "#111a24"
XATO = "#ff4444"

MALUMOT_FAYLI = "/storage/emulated/0/AI/turnik_kundaligi.json"


def yozuvlarni_yukla():
    if not os.path.isfile(MALUMOT_FAYLI):
        return []
    try:
        with open(MALUMOT_FAYLI, "r", encoding="utf-8") as f:
            yozuvlar = json.load(f)
    except Exception:
        return []

    # Xato/tasodifiy kiritilgan juda katta sonlarni avtomatik tozalaymiz
    toza = [y for y in yozuvlar if y.get("natija", 0) <= 500]
    if len(toza) != len(yozuvlar):
        yozuvlarni_saqla(toza)
    return toza


def yozuvlarni_saqla(yozuvlar):
    try:
        os.makedirs(os.path.dirname(MALUMOT_FAYLI), exist_ok=True)
        with open(MALUMOT_FAYLI, "w", encoding="utf-8") as f:
            json.dump(yozuvlar, f, ensure_ascii=False, indent=2)
    except Exception as xato:
        print(f"[XATOLIK] Saqlashda muammo: {xato}")


class TurnikKundaligi:
    def __init__(self, oyna):
        self.oyna = oyna
        oyna.title("TURNIK KUNDALIGI :: 921324")
        oyna.geometry("380x640")
        oyna.configure(bg=FON)

        self.yozuvlar = yozuvlarni_yukla()

        tk.Label(oyna, text=">> TURNIK KUNDALIGI <<", font=("Courier", 14, "bold"),
                 bg=FON, fg=YASHIL).pack(pady=(15, 0))
        tk.Label(oyna, text="[ KIBER-ATLET :: 921324 ]", font=("Courier", 9),
                 bg=FON, fg=KOK).pack(pady=(0, 12))

        kirish_freym = tk.Frame(oyna, bg=FON)
        kirish_freym.pack(pady=6)

        tk.Label(kirish_freym, text="Bugungi natija (marta):", font=("Courier", 10),
                 bg=FON, fg=YASHIL).pack()
        self.natija_input = tk.Entry(kirish_freym, font=("Courier", 16), bg=PANEL,
                                      fg=YASHIL, insertbackground=YASHIL,
                                      justify="center", width=8)
        self.natija_input.pack(pady=6)
        self.natija_input.bind("<Return>", lambda e: self.natija_qoshish())

        tk.Button(oyna, text="[ + KIRITISH ]", font=("Courier", 11, "bold"),
                  bg=PANEL, fg=YASHIL, activebackground=YASHIL, activeforeground=FON,
                  command=self.natija_qoshish).pack(pady=8)

        self.stat_label = tk.Label(oyna, text="", font=("Courier", 10, "bold"),
                                    bg=PANEL, fg=YASHIL, justify="left", anchor="w")
        self.stat_label.pack(padx=15, pady=10, fill="x", ipady=8, ipadx=8)

        tk.Label(oyna, text="── PROGRESS (oxirgi 10 kun) ──", font=("Courier", 9, "bold"),
                 bg=FON, fg=KOK).pack(pady=(5, 0))

        self.grafik_label = tk.Label(oyna, text="", font=("Courier", 9), bg=FON,
                                      fg=YASHIL, justify="left")
        self.grafik_label.pack(padx=15, pady=8, fill="x")

        tk.Label(oyna, text="── TARIX ──", font=("Courier", 9, "bold"),
                 bg=FON, fg=KOK).pack(pady=(5, 0))

        tashqi_freym = tk.Frame(oyna, bg=FON)
        tashqi_freym.pack(fill="both", expand=True, padx=15, pady=6)

        self.canvas = tk.Canvas(tashqi_freym, bg=FON, highlightthickness=0)
        scrollbar = tk.Scrollbar(tashqi_freym, orient="vertical", command=self.canvas.yview)
        self.royxat_freym = tk.Frame(self.canvas, bg=FON)

        self.royxat_freym.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.royxat_freym, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.hammasini_yangila()

    def natija_qoshish(self):
        matn = self.natija_input.get().strip()
        if not matn.isdigit():
            messagebox.showwarning("Xatolik", "Faqat butun son kiriting!")
            return

        son = int(matn)
        if son > 500:
            messagebox.showwarning(
                "Xatolik",
                "Natija 500 dan katta bo'lishi mumkin emas.\n"
                "Ehtimol tasodifan uzun raqam kiritdingiz?"
            )
            return
        yangi_yozuv = {
            "sana": datetime.now().strftime("%Y-%m-%d"),
            "natija": son,
        }
        self.yozuvlar.append(yangi_yozuv)
        yozuvlarni_saqla(self.yozuvlar)

        self.natija_input.delete(0, tk.END)
        self.hammasini_yangila()

    def yozuvni_ochirish(self, indeks):
        tasdiq = messagebox.askyesno("O'chirish", "Bu yozuvni o'chirishni tasdiqlaysizmi?")
        if tasdiq:
            self.yozuvlar.pop(indeks)
            yozuvlarni_saqla(self.yozuvlar)
            self.hammasini_yangila()

    def hammasini_yangila(self):
        self._statistikani_yangila()
        self._grafikni_yangila()
        self._tarixni_yangila()

    def _statistikani_yangila(self):
        if not self.yozuvlar:
            self.stat_label.config(text="Hozircha ma'lumot yo'q.\nBirinchi natijangni kiritib bosla!")
            return

        natijalar = [y["natija"] for y in self.yozuvlar]
        eng_yaxshi = max(natijalar)
        ortacha = sum(natijalar) / len(natijalar)
        jami_mashq = len(natijalar)
        oxirgi = natijalar[-1]

        chempion_belgi = " \U0001F3C6 REKORD DARAJASIGA YETDI!" if eng_yaxshi >= 32 else ""

        matn = (
            f"ENG YAXSHI REKORD: {eng_yaxshi} marta{chempion_belgi}\n"
            f"O'RTACHA NATIJA: {ortacha:.1f} marta\n"
            f"JAMI MASHQLAR: {jami_mashq} kun\n"
            f"OXIRGI NATIJA: {oxirgi} marta"
        )
        self.stat_label.config(text=matn)

    def _grafikni_yangila(self):
        if not self.yozuvlar:
            self.grafik_label.config(text="(grafik uchun ma'lumot yo'q)")
            return

        oxirgi_10 = self.yozuvlar[-10:]
        maksimum = max(y["natija"] for y in oxirgi_10)
        maksimum = max(maksimum, 1)

        qatorlar = []
        for yozuv in oxirgi_10:
            uzunlik = int((yozuv["natija"] / maksimum) * 20)
            ustun = "#" * uzunlik
            sana_qisqa = yozuv["sana"][5:]
            qatorlar.append(f"{sana_qisqa} |{ustun} {yozuv['natija']}")

        self.grafik_label.config(text="\n".join(qatorlar))

    def _tarixni_yangila(self):
        for widget in self.royxat_freym.winfo_children():
            widget.destroy()

        if not self.yozuvlar:
            tk.Label(self.royxat_freym, text="Tarix bo'sh.", font=("Courier", 10),
                     bg=FON, fg="#666666").pack(pady=15)
            return

        for i, yozuv in enumerate(reversed(self.yozuvlar)):
            haqiqiy_indeks = len(self.yozuvlar) - 1 - i
            qator = tk.Frame(self.royxat_freym, bg=PANEL)
            qator.pack(fill="x", pady=2, padx=2)

            matn_freym = tk.Frame(qator, bg=PANEL)
            matn_freym.pack(side="left", fill="x", expand=True, padx=8, pady=5)

            tk.Label(matn_freym, text=f"{yozuv['sana']}  ->  {yozuv['natija']} marta",
                     font=("Courier", 10), bg=PANEL, fg=YASHIL, anchor="w",
                     wraplength=260, justify="left"
                     ).pack(anchor="w", fill="x")

            tk.Button(qator, text="X", font=("Courier", 9, "bold"), width=2,
                      bg=FON, fg=XATO,
                      command=lambda idx=haqiqiy_indeks: self.yozuvni_ochirish(idx)
                      ).pack(side="right", padx=6)


asosiy = tk.Tk()
ilova = TurnikKundaligi(asosiy)
asosiy.mainloop()
