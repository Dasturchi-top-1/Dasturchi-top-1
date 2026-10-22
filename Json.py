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

MALUMOT_FAYLI = "/storage/emulated/0/AI/vazifalar.json"


def vazifalarni_yukla():
    if not os.path.isfile(MALUMOT_FAYLI):
        return []
    try:
        with open(MALUMOT_FAYLI, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def vazifalarni_saqla(vazifalar):
    try:
        os.makedirs(os.path.dirname(MALUMOT_FAYLI), exist_ok=True)
        with open(MALUMOT_FAYLI, "w", encoding="utf-8") as f:
            json.dump(vazifalar, f, ensure_ascii=False, indent=2)
        return True
    except Exception as xato:
        print(f"[XATOLIK] Saqlashda muammo: {xato}")
        return False


class VazifaBoshqaruvchisi:
    def __init__(self, oyna):
        self.oyna = oyna
        oyna.title("VAZIFA BOSHQARUVCHISI :: 921324")
        oyna.geometry("380x600")
        oyna.configure(bg=FON)

        self.vazifalar = vazifalarni_yukla()

        tk.Label(oyna, text=">> VAZIFA BOSHQARUVCHISI <<", font=("Courier", 14, "bold"),
                 bg=FON, fg=YASHIL).pack(pady=(15, 0))
        tk.Label(oyna, text="[ NODE: 921324 ]", font=("Courier", 9),
                 bg=FON, fg=KOK).pack(pady=(0, 12))

        # --- Kirish qismi ---
        self.vazifa_input = tk.Entry(oyna, font=("Courier", 12), bg=PANEL, fg=YASHIL,
                                      insertbackground=YASHIL)
        self.vazifa_input.pack(padx=15, pady=6, fill="x")
        self.vazifa_input.insert(0, "Yangi vazifa yozing...")
        self.vazifa_input.bind("<Return>", lambda e: self.vazifa_qoshish())

        muddat_freym = tk.Frame(oyna, bg=FON)
        muddat_freym.pack(pady=4)
        tk.Label(muddat_freym, text="Muddat (ixtiyoriy, masalan 20.07):",
                 font=("Courier", 9), bg=FON, fg=KOK).pack(side="left", padx=(0, 6))
        self.muddat_input = tk.Entry(muddat_freym, font=("Courier", 10), bg=PANEL,
                                      fg=YASHIL, insertbackground=YASHIL, width=10)
        self.muddat_input.pack(side="left")

        tk.Button(oyna, text="[ + QO'SHISH ]", font=("Courier", 11, "bold"),
                  bg=PANEL, fg=YASHIL, activebackground=YASHIL, activeforeground=FON,
                  command=self.vazifa_qoshish).pack(pady=8)

        # --- Vazifalar ro'yxati (Canvas + Scrollbar) ---
        tashqi_freym = tk.Frame(oyna, bg=FON)
        tashqi_freym.pack(fill="both", expand=True, padx=15, pady=10)

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

        # --- Status ---
        self.status_label = tk.Label(oyna, text="", font=("Courier", 9),
                                      bg=FON, fg=KOK)
        self.status_label.pack(pady=(0, 10))

        self.royxatni_yangila()

    def vazifa_qoshish(self):
        matn = self.vazifa_input.get().strip()
        if not matn or matn == "Yangi vazifa yozing...":
            messagebox.showwarning("Xatolik", "Vazifa matni kiritilmadi!")
            return

        muddat = self.muddat_input.get().strip()

        yangi_vazifa = {
            "matn": matn,
            "muddat": muddat if muddat else None,
            "bajarildi": False,
            "yaratilgan": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.vazifalar.append(yangi_vazifa)
        vazifalarni_saqla(self.vazifalar)

        self.vazifa_input.delete(0, tk.END)
        self.muddat_input.delete(0, tk.END)
        self.royxatni_yangila()

    def bajarildi_belgila(self, indeks):
        self.vazifalar[indeks]["bajarildi"] = not self.vazifalar[indeks]["bajarildi"]
        vazifalarni_saqla(self.vazifalar)
        self.royxatni_yangila()

    def vazifani_ochirish(self, indeks):
        tasdiq = messagebox.askyesno("O'chirish", "Bu vazifani o'chirishni tasdiqlaysizmi?")
        if tasdiq:
            self.vazifalar.pop(indeks)
            vazifalarni_saqla(self.vazifalar)
            self.royxatni_yangila()

    def royxatni_yangila(self):
        for widget in self.royxat_freym.winfo_children():
            widget.destroy()

        if not self.vazifalar:
            tk.Label(self.royxat_freym, text="Hozircha vazifa yo'q.",
                     font=("Courier", 10), bg=FON, fg="#666666").pack(pady=20)
        else:
            for i, vazifa in enumerate(self.vazifalar):
                self._vazifa_qatorini_chiz(i, vazifa)

        bajarilgan = sum(1 for v in self.vazifalar if v["bajarildi"])
        jami = len(self.vazifalar)
        self.status_label.config(text=f"Jami: {jami} | Bajarilgan: {bajarilgan}")

    def _vazifa_qatorini_chiz(self, indeks, vazifa):
        qator = tk.Frame(self.royxat_freym, bg=PANEL)
        qator.pack(fill="x", pady=3, padx=2)

        rang = "#666666" if vazifa["bajarildi"] else YASHIL
        chizib_matn = vazifa["matn"]
        if vazifa["bajarildi"]:
            chizib_matn = f"✓ {chizib_matn}"

        matn_freym = tk.Frame(qator, bg=PANEL)
        matn_freym.pack(side="left", fill="x", expand=True, padx=8, pady=6)

        tk.Label(matn_freym, text=chizib_matn, font=("Courier", 11), bg=PANEL,
                 fg=rang, anchor="w", justify="left", wraplength=200).pack(anchor="w")

        if vazifa.get("muddat"):
            tk.Label(matn_freym, text=f"Muddat: {vazifa['muddat']}", font=("Courier", 8),
                     bg=PANEL, fg=KOK, anchor="w").pack(anchor="w")

        tugmalar_freym = tk.Frame(qator, bg=PANEL)
        tugmalar_freym.pack(side="right", padx=6)

        tk.Button(tugmalar_freym, text="✓", font=("Courier", 10, "bold"), width=2,
                  bg=FON, fg=YASHIL, command=lambda: self.bajarildi_belgila(indeks)
                  ).pack(side="left", padx=2)
        tk.Button(tugmalar_freym, text="✕", font=("Courier", 10, "bold"), width=2,
                  bg=FON, fg=XATO, command=lambda: self.vazifani_ochirish(indeks)
                  ).pack(side="left", padx=2)


asosiy = tk.Tk()
ilova = VazifaBoshqaruvchisi(asosiy)
asosiy.mainloop()
