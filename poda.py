import tkinter as tk
from datetime import datetime, timedelta

# 📋 QISHLOQDA NAVBAT BILAN PODA BOQADIGAN ODAMLAR RO'YXATI
# Navbat mana shu tartibda aylanadi. Odamlarni xohlagancha qo'shishing mumkin!
PODACHILAR = [
    "Musobek",
    "Habib",
    "Oraz pshak",
    "Robiya",
    "Hasan",
    "Hoji",
    "Muhammad>",
    "Ahliddin",
    "Fotima",
    "Jasur",
    "Parvina",
    "Biz",
    "Rasul",
    "Ayjamol",
    "Mullo",
    "Muhammad ali",
    "Orif",
    ">>>",
    "Umar",
    "Ayub",
    "DNX Malim",
    "Zafar",
    "Fozil",
    "Muso",
    "Iso",
    "Orzubek",
    "APQ",
    "Dilshod",
    "Husniddin"
]
()
# 📅 NAVBAT BOSHLANISH SANASI (Tizim adashmasligi uchun poydevor)
# 2026-yil 6-iyul kuni ro'yxatdagi birinchi odam (Alijon aka)dan boshlanadi deb hisoblaymiz
BOSH_SANA = datetime(2026, 7, 6)

def navbatni_hisobla(kun_ofseti=0):
    # Bugungi yoki tanlangan kundagi podachini aniqlash algoritmi
    maqsadli_sana = datetime.now() + timedelta(days=kun_ofseti)
    farq = (maqsadli_sana - BOSH_SANA).days
    
    # Matematik kiber-tryuk: Kunlar farqini odamlar soniga bo'lgandagi qoldiq
    indeks = farq % len(PODACHILAR)
    return maqsadli_sana.strftime("%d-%m-%Y"), PODACHILAR[indeks]

# --- EKRAN INTERFEYSI (TKINTER) ---
root = tk.Tk()
root.title("Kiber-Poda v1.0")
root.geometry("400x500")
root.configure(bg="#1e1e2e") # To'q rangli kiber-fon

current_offset = 0

def yangila_ekran():
    sana_matn, odam = navbatni_hisobla(current_offset)
    lbl_sana.config(text=f"📅 Sana: {sana_matn}")
    lbl_odam.config(text=odam)
    
    # Bugun, ertaga yoki kechagi kun ekanligini bildirish
    if current_offset == 0:
        lbl_kun_status.config(text="🔴 BUGUNGI NAVBAT", fg="#ff5555")
    elif current_offset == 1:
        lbl_kun_status.config(text="🟡 ERTAGA", fg="#ffb86c")
    elif current_offset == -1:
        lbl_kun_status.config(text="⚪ KECHA", fg="#8be9fd")
    else:
        lbl_kun_status.config(text="🌐 KIBER-PROGNOZ", fg="#50fa7b")

def keyingi_kun():
    global current_offset
    current_offset += 1
    yangila_ekran()

def oldingi_kun():
    global current_offset
    current_offset -= 1
    yangila_ekran()

# Sarlavha
lbl_title = tk.Label(root, text="KUN TARTIBI NAVBATI TIZIMI", font=("Arial", 13, "bold"), bg="#1e1e2e", fg="#50fa7b")
lbl_title.pack(pady=20)

# Kun statusi (Bugun/Ertaga)
lbl_kun_status = tk.Label(root, text="", font=("Arial", 14, "bold"), bg="#1e1e2e")
lbl_kun_status.pack()

# Sana ko'rsatgichi
lbl_sana = tk.Label(root, text="", font=("Arial", 12), bg="#1e1e2e", fg="#a9b1d6")
lbl_sana.pack(pady=5)

# Poda boquvchining ismi (Katta va qalin shriftda)
lbl_odam = tk.Label(root, text="", font=("Arial", 26, "bold"), bg="#1e1e2e", fg="#f1fa8c")
lbl_odam.pack(pady=30)

# Tugmalar paneli (Kunlarni oldinga-orqaga varoqlash uchun)
btn_frame = tk.Frame(root, bg="#1e1e2e")
btn_frame.pack(pady=20)

btn_oldingi = tk.Button(btn_frame, text="◀ Kechagi kun", font=("Arial", 11), command=oldingi_kun, bg="#ff5555", fg="white", width=12)
btn_oldingi.grid(row=0, column=0, padx=10)

btn_keyingi = tk.Button(btn_frame, text="Ertangi kun ▶", font=("Arial", 11), command=keyingi_kun, bg="#50fa7b", fg="black", width=12)
btn_keyingi.grid(row=0, column=1, padx=10)

# Dasturni ilk bor yangilab ishga tushirish
yangila_ekran()
root.mainloop()
