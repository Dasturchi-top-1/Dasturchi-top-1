import tkinter as tk
from tkinter import messagebox
import random

# ============================================================
#  1. GLOBAL PARAMETRLAR VA SO'ZLAR BAZASI
# ============================================================
FON = "#0d0d0d"
KOK = "#00c8ff"
YASHIL = "#39ff14"
PANEL = "#111a24"

SOZLAR_BAZASI = [
    {"soz": "gidir", "tafsif": "Gapga usta, chaqqon, pishiq odam."},
    {"soz": "kalaka", "tafsif": "Soyabon yoki soya joy, dam olish uchun ko'lanka."},
    {"soz": "chumkak", "tafsif": "Kichkina, past bo'yli, mitti narsa yoki odam."},
    {"soz": "g'irt", "tafsif": "Sof, xolis, aralashmagan narsa (masalan, g'irt yolg'on)."},
    {"soz": "loqma", "tafsif": "Tez tayyorlanadigan, sodda ovqat yoki taom."},
    {"soz": "pakana", "tafsif": "Bo'yi past, kichkina qomatli odam."},
    {"soz": "shalpang", "tafsif": "Osilib turgan, tartibsiz, salpaygan narsa."},
    {"soz": "qaqir", "tafsif": "Qattiq, quruq, o'ta toliqqan yoki charchagan holat."},
    {"soz": "milt", "tafsif": "Juda oz miqdor, bir zumgina narsa."},
    {"soz": "chalajon", "tafsif": "Yarim jonli, zaif, holdan toygan odam."},
    {"soz": "dodillamoq", "tafsif": "Baqirib-chaqirib shikoyat qilmoq, dod solmoq."},
    {"soz": "cho'chqora", "tafsif": "Qo'rqoq, cho'chib yuruvchi odam."},
    {"soz": "jag'illamoq", "tafsif": "Ko'p va tez gapirmoq, valdiramoq."},
    {"soz": "qumaloq", "tafsif": "Yumaloq, kichik va dumaloq shakldagi narsa."},
    {"soz": "lo'killamoq", "tafsif": "Sekin va noqulay yurmoq, cho'chib-cho'chib yurish."},
    {"soz": "targ'il", "tafsif": "Chiziqli yoki rang-barang, ola-bula naqshli narsa."},
    {"soz": "qaltirab", "tafsif": "Titrab, qo'rqinch yoki sovuqdan qaltirash holati."},
    {"soz": "mishiq", "tafsif": "Tumshug'i cho'zilgan yoki injiqroq, injiq odam/hayvon."},
    {"soz": "duduq", "tafsif": "Gapirganda tili tutiladigan, kekech odam."},
    {"soz": "avaylamoq", "tafsif": "Ehtiyot qilmoq, asrab-avaylab saqlamoq."},
    {"soz": "chuvillamoq", "tafsif": "Bolalar yoki qushlarning baland ovozda shovqin qilishi."},
    {"soz": "qoq suyak", "tafsif": "Juda ozg'in, faqat suyagi qolgandek horg'in odam."}
]

# ============================================================
#  2. O'YIN MANTIQI
# ============================================================
class SozOyin:
    def __init__(self, oyna):
        self.oyna = oyna
        self.oyna.title("Blip Game v9.2")
        self.oyna.geometry("280x420")  # Oyna o'lchami ixchamlashtirildi
        self.oyna.configure(bg=FON)
        
        self.ochko = 0
        self.asliy_soz = ""
        
        # Sarlavha shrifti 14 dan 10 ga tushirildi
        tk.Label(oyna, text="🧠 LAQAYCHA SO'Z TOP!", font=("Courier", 10, "bold"), bg=FON, fg=YASHIL).pack(pady=8)
        
        # Tafsif qutisi kichraytirildi
        self.tafsif_label = tk.Label(oyna, text="", font=("Courier", 9), bg=PANEL, fg=KOK, wraplength=240, height=4, relief="solid")
        self.tafsif_label.pack(pady=5, padx=15, fill="x")
        
        # Yashirin xizmat chiziqlari 18 dan 13 ga tushirildi
        self.shifr_label = tk.Label(oyna, text="", font=("Courier", 13, "bold"), bg=FON, fg=YASHIL)
        self.shifr_label.pack(pady=10)
        
        # Kiritish maydoni
        self.kirish_input = tk.Entry(oyna, font=("Courier", 11), bg=PANEL, fg=YASHIL, justify="center", insertbackground=YASHIL)
        self.kirish_input.pack(pady=5, padx=30, fill="x")
        
        # Tekshirish tugmasi
        tk.Button(oyna, text="[ TEKSHIRISH ]", font=("Courier", 10, "bold"), bg=PANEL, fg=KOK, command=self.tekshir).pack(pady=8)
        
        # Ochko labeli
        self.ochko_label = tk.Label(oyna, text="Ochko: 0", font=("Courier", 10, "bold"), bg=FON, fg=YASHIL)
        self.ochko_label.pack(pady=5)
        
        self.yangi_soz_tanla()

    def yangi_soz_tanla(self):
        tanlangan = random.choice(SOZLAR_BAZASI)
        self.asliy_soz = tanlangan["soz"]
        self.tafsif_label.config(text=f"Ma'nosi:\n{tanlangan['tafsif']}")
        
        # Telefon ekranida chiziqlar juda uzoq ketib qolmasligi uchun " _ " formatda chiqadi
        shifr = self.asliy_soz[0] + (" _" * (len(self.asliy_soz) - 1))
        self.shifr_label.config(text=shifr)
        self.kirish_input.delete(0, tk.END)

    def tekshir(self):
        taxmin = self.kirish_input.get().strip().lower()
        if taxmin == self.asliy_soz:
            self.ochko += 10
            self.ochko_label.config(text=f"Ochko: {self.ochko}")
            messagebox.showinfo("To'g'ri!", "Daxshat! Topdingiz, bro! +10 Ochko!")
            self.yangi_soz_tanla()
        else:
            messagebox.showerror("Xato", "Yo'q, adashdingiz. Yana urinib ko'ring!")

if __name__ == "__main__":
    root = tk.Tk()
    oyin = SozOyin(root)
    root.mainloop()
