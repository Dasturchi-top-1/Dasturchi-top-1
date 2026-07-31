import tkinter as tk
from tkinter import messagebox
import random

# ============================================================
# BLACK AI Core v9.0 // GUIDO EDITION
# OFFLINE CYBER-ENCYCLOPEDIA FOR PYDROID 3
# ============================================================

BG_MAIN = "#111318"
BG_PANEL = "#1a1c22"
BG_WIDGET = "#0d0e12"

COLOR_PURPLE = "#bd93f9"
COLOR_GREEN = "#50fa7b"
COLOR_CYAN = "#8be9fd"
COLOR_WHITE = "#f8f8f2"
COLOR_GRAY = "#6272a4"

FONT_TITLE = ("Consolas", 11, "bold")
FONT_CODE = ("Consolas", 10)
FONT_INTERFACE = ("Consolas", 9, "bold")

# ============================================================
# EXPERT CYBER AI ENGINE (MATN TAHLIL QILUVCHI KLASS)
# ============================================================

class ExpertCyberAI:
    def __init__(self):
        # Ulkan oflayn darsliklar va andozalar arxivi
        self.archive = {
            "python_nima": (
                "# === [MODULE-BUILDER] :: PYTHON INTRODUCTION ===\n"
                "# Python — 1991-yilda niderlandiyalik dasturchi Guido van Rossum tomonidan yaratilgan.\n"
                "# Bu yuqori darajali, universal va o'qilishi oson bo'lgan dasturlash tilidir.\n"
                "# Guido van Rossum tilni BBC'ning 'Monty Python's Flying Circus' shousi sharafiga nomlagan.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: FIRST CODE ===\n"
                "print('Salom, Kiber-Dunyo!')\n"
            ),
            "print_funksiyasi": (
                "# === [MODULE-BUILDER] :: PRINT FUNCTION ===\n"
                "# print() — ma'lumotlarni konsolga (ekranga) chiqarish uchun asosiy funksiyadir.\n"
                "# U har xil turdagi ma'lumotlarni (matn, son, ro'yxat) qabul qila oladi.\n"
                "# 'sep' argumenti elementlar orasiga belgi qo'yadi, 'end' esa qator oxirini belgilaydi.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: PRINT EXAMPLES ===\n"
                "print('Kiber', 'Tizim', sep='-', end=' // ONLINE \\n')\n"
                "print('Natija:', 45 + 55)\n"
            ),
            "input_olish": (
                "# === [MODULE-BUILDER] :: INPUT OLISH ===\n"
                "# input() — foydalanuvchidan klaviatura orqali ma'lumot qabul qilish funksiyasi.\n"
                "# Diqqat: input() har doim matn (string) ko'rinishida ma'lumot qaytaradi.\n"
                "# Agar son qabul qilmoqchi bo'lsak, uni int() yoki float() bilan o'girish shart.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: INPUT ANDOZA ===\n"
                "ism = input('Foydalanuvchi nomini kiriting: ')\n"
                "yosh = int(input('Yoshingizni kiriting: '))\n"
                "print('Tizim foydalanuvchisi:', ism, '| Tug\'ilgan yil:', 2026 - yosh)\n"
            ),
            "shartlar": (
                "# === [MODULE-BUILDER] :: IF-ELIF-ELSE SCHEME ===\n"
                "# Mantiqiy shartlarni tekshirish uchun if, elif va else operatorlari ishlatiladi.\n"
                "# Python-da shartlar bloklari to'rtta joy tashlash (indentation) orqali ajratiladi.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: CONDITIONAL CODE ===\n"
                "tezlik = 120\n"
                "if tezlik > 110:\n"
                "    print('[SYSTEM-INFO] Tezlik o\'ta yuqori! Jarima!')\n"
                "elif tezlik < 40:\n"
                "    print('[SYSTEM-INFO] Tezlik juda past!')\n"
                "else:\n"
                "    print('[SYSTEM-INFO] Tezlik me\'yorda.')\n"
            ),
            "while_sikli": (
                "# === [MODULE-BUILDER] :: WHILE LOOP CORE ===\n"
                "# While sikli berilgan shart to'g'ri (True) bo'lgan muddatda tinmay aylanadi.\n"
                "# Agar shart hech qachon False bo'lmasa, cheksiz sikl (infinite loop) yuzaga keladi.\n"
                "# Cheksiz sikldan zudlik bilan chiqish uchun 'break' operatori qo'llaniladi.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: WHILE BREAK LOOP ===\n"
                "counter = 1\n"
                "while True:\n"
                "    print('[LOOP-CORE] Sikl raqami:', counter)\n"
                "    if counter >= 5:\n"
                "        print('[LOOP-CORE] Shart bajarildi. Sikl to\'xtatildi.')\n"
                "        break\n"
                "    counter += 1\n"
            ),
            "range_funksiyasi": (
                "# === [MODULE-BUILDER] :: RANGE & FOR LOOP ===\n"
                "# range(start, stop, step) funksiyasi ma'lum bir orliqdagi sonlar ketma-ketligini beradi.\n"
                "# range(5) -> 0 dan 4 gacha sonlarni qaytaradi (5 kirmaydi).\n"
                "# Uni odatda 'for' takrorlash operatori bilan birga ishlatishadi.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: FOR RANGE STEP ===\n"
                "print('1 dan 10 gacha toq sonlar:')\n"
                "for i in range(1, 11, 2):\n"
                "    print('Toq son:', i)\n"
            ),
            "royxatlar": (
                "# === [MODULE-BUILDER] :: PYTHON LISTS ===\n"
                "# Ro'yxat (list) — bir nechta elementlarni bitta o'zgaruvchida saqlash imkonini beradi.\n"
                "# Ro'yxat elementlari tartiblangan, o'zgartirilishi mumkin va indekslanadi (0 dan boshlanadi).\n"
                "# Element qo'shish uchun .append(), o'chirish uchun esa .remove() ishlatiladi.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: LIST MANIPULATION ===\n"
                "kiber_tizimlar = ['Firewall', 'Proxy', 'Mainframe']\n"
                "kiber_tizimlar.append('Database')\n"
                "print('Birinchi element:', kiber_tizimlar[0])\n"
                "print('To\'liq ro\'yxat:', kiber_tizimlar)\n"
            ),
            "funksiyalar": (
                "# === [MODULE-BUILDER] :: FUNCTIONS (DEF) ===\n"
                "# Funksiya — faqat chaqirilgandagina ishlaydigan kod blokidir.\n"
                "# U 'def' kalit so'zi orqali e'lon qilinadi va qiymat qaytarishi uchun 'return' ishlatiladi.\n"
                "# Funksiya ichidagi o'zgaruvchilar lokal (tashqarida ko'rinmaydi) hisoblanadi.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: FUNCTION WITH RETURN ===\n"
                "def hisobla_kvadrat(son):\n"
                "    natija = son * son\n"
                "    return natija\n"
                "\n"
                "kod_chiqishi = hisobla_kvadrat(12)\n"
                "print('12 ning kvadrati:', kod_chiqishi)\n"
            ),
            "kalkulyator_oddiy": (
                "# === [MODULE-BUILDER] :: OFFLINE COMPACT CALCULATOR ===\n"
                "# Bu hech qanday xatolarsiz ishlaydigan to'liq kalkulyator andozasidir.\n"
                "# ZeroDivisionError (nolga bo'lish) xatoligi try/except orqali ushlangan.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: EXECUTABLE CALCULATOR ===\n"
                "def kalkulyator():\n"
                "    print('--- KIBER KALKULYATOR v1.0 ---')\n"
                "    try:\n"
                "        a = float(input('Birinchi sonni kiriting: '))\n"
                "        amal = input('Amalni kiriting (+, -, *, /): ')\n"
                "        b = float(input('Ikkinchi sonni kiriting: '))\n"
                "        \n"
                "        if amal == '+': print('Natija:', a + b)\n"
                "        elif amal == '-': print('Natija:', a - b)\n"
                "        elif amal == '*': print('Natija:', a * b)\n"
                "        elif amal == '/':\n"
                "            if b == 0: print('[ERROR] Nolga bo\'lish mumkin emas!')\n"
                "            else: print('Natija:', a / b)\n"
                "        else: print('[ERROR] Noto\'g\'ri amal!')\n"
                "    except ValueError:\n"
                "        print('[ERROR] Faqat son kiritish lozim!')\n"
                "\n"
                "kalkulyator()\n"
            ),
            "son_topish_oyini": (
                "# === [MODULE-BUILDER] :: RANDOM NUMBER GAME ===\n"
                "# Kompyuter 1 dan 50 gacha bo'lgan tasodifiy son o'ylaydi.\n"
                "# While sikli va shartlar yordamida foydalanuvchi sonni topguncha o'yin davom etadi.\n"
                "# \n"
                "# === [CODE-TEMPLATE] :: RANDOM GAME CODE ===\n"
                "def son_topish():\n"
                "    print('--- SON TOPISH O\'YINI ---')\n"
                "    yashirin_son = random.randint(1, 50)\n"
                "    urinishlar = 0\n"
                "    while True:\n"
                "        taxmin = int(input('1 dan 50 gacha son kiriting: '))\n"
                "        urinishlar += 1\n"
                "        if taxmin < yashirin_son:\n"
                "            print('Yashirin son kattaroq!')\n"
                "        elif taxmin > yashirin_son:\n"
                "            print('Yashirin son kichikroq!')\n"
                "        else:\n"
                "            print(f'Tabriklaymiz! {urinishlar} urinishda topdingiz!')\n"
                "            break\n"
                "\n"
                "# Ishga tushirish uchun pastdagi qatorni sharhdan oching:\n"
                "# son_topish()\n"
            )
        }

    def analyze(self, query):
        query = query.lower().strip()
        
        if query == "all" or query == "barchasi":
            full_text = ""
            for key, val in self.archive.items():
                full_text += val + "\n" + "# " + "="*45 + "\n\n"
            return full_text
            
        # Matn ichidan kalit so'zlarni aqlli skanerlash (Fuzzy scan)
        if "python" in query or "tarix" in query or "ros" in query:
            return self.archive["python_nima"]
        elif "while" in query or "sikl" in query or "break" in query:
            return self.archive["while_sikli"]
        elif "funksiy" in query or "def" in query or "return" in query:
            return self.archive["funksiyalar"]
        elif "range" in query or "for" in query:
            return self.archive["range_funksiyasi"]
        elif "print" in query or "chiqar" in query:
            return self.archive["print_funksiyasi"]
        elif "ro'yxat" in query or "royxat" in query or "list" in query:
            return self.archive["royxatlar"]
        elif "input" in query or "qabul" in query:
            return self.archive["input_olish"]
        elif "if" in query or "else" in query or "shart" in query:
            return self.archive["shartlar"]
        elif "kalkulyator" in query or "hisob" in query:
            return self.archive["kalkulyator_oddiy"]
        elif "o'yin" in query or "oyin" in query or "son" in query:
            return self.archive["son_topish_oyini"]
        else:
            return (
                "# === [SYSTEM-INFO] :: KALIT SO'Z TOPILMADI ===\n"
                "# Qidiruv muvaffaqiyatsiz tugadi.\n"
                "# Quyidagi kalit so'zlardan foydalaning:\n"
                "# -> python, print, input, shartlar, while, range, royxat, funksiyalar\n"
                "# -> kalkulyator, oyin, all\n"
            )

# ============================================================
# INTERFEYS ARXITEKTURASI VA LOYIHA INTEGRATSIYASI
# ============================================================

ai_engine = ExpertCyberAI()

root = tk.Tk()
root.title("BLACK AI v9.0")
root.geometry("380x660")
root.configure(bg=BG_MAIN)
root.resizable(False, False)

# INTERFEYS FUNKSIYALARI
def run_search():
    user_input = search_entry.get()
    if user_input.strip() == "":
        log_box.delete("1.0", "end")
        log_box.insert("1.0", "# === [SYSTEM-INFO] :: QIDIRUV MAYDONI BO'SH ===\n")
        return
    
    result = ai_engine.analyze(user_input)
    log_box.delete("1.0", "end")
    log_box.insert("1.0", result)
    status_var.set("[ANALYSIS-COMPLETED]")

def clear_all():
    search_entry.delete(0, "end")
    log_box.delete("1.0", "end")
    log_box.insert("1.0", "# === [SYSTEM-INFO] :: ARXIV HOLATI TOZALANDI ===\n")
    status_var.set("[SYSTEM-CLEARED]")

def copy_to_clipboard():
    code_text = log_box.get("1.0", "end-1c")
    if code_text.strip() == "" or ("[SYSTEM-INFO]" in code_text and "KALIT" in code_text):
        status_var.set("[COPY-FAILED] EMPTY BUFFER")
        return
    root.clipboard_clear()
    root.clipboard_append(code_text)
    root.update()
    status_var.set("[COPIED-TO-CLIPBOARD]")

# SARLAVHA (TITLE PANEL)
title_frame = tk.Frame(root, bg=BG_PANEL)
title_frame.pack(fill="x", padx=8, pady=(8, 4))

title_label = tk.Label(
    title_frame, 
    text="BLACK AI Core v9.0 // GUIDO EDITION", 
    font=FONT_TITLE, 
    bg=BG_PANEL, 
    fg=COLOR_PURPLE
)
title_label.pack(pady=6)

# QIDIRUV PANELI (ENTRY)
search_frame = tk.Frame(root, bg=BG_PANEL)
search_frame.pack(fill="x", padx=8, pady=4)

search_entry = tk.Entry(
    search_frame, 
    bg=BG_WIDGET, 
    fg=COLOR_GREEN, 
    insertbackground=COLOR_GREEN,
    relief="flat", 
    font=FONT_CODE
)
search_entry.pack(fill="x", ipady=6, padx=6, pady=6)
search_entry.insert(0, "all") # Dastlab hammasini ko'rish uchun andoza

# TUGMALAR PANELI
button_frame = tk.Frame(root, bg=BG_MAIN)
button_frame.pack(fill="x", padx=8, pady=4)

search_btn = tk.Button(
    button_frame, 
    text="Kiber-Qidiruv & Analiz", 
    command=run_search,
    bg=BG_PANEL, 
    fg=COLOR_GREEN, 
    activebackground=BG_PANEL, 
    activeforeground=COLOR_GREEN,
    relief="flat", 
    font=FONT_INTERFACE
)
search_btn.pack(side="left", expand=True, fill="x", padx=(0, 2), ipady=4)

clear_btn = tk.Button(
    button_frame, 
    text="Tozala", 
    command=clear_all,
    bg=BG_PANEL, 
    fg=COLOR_PURPLE, 
    activebackground=BG_PANEL, 
    activeforeground=COLOR_PURPLE,
    relief="flat", 
    font=FONT_INTERFACE
)
clear_btn.pack(side="right", expand=True, fill="x", padx=(2, 0), ipady=4)

# MATN VA NUSXA OLISH PANELI
editor_frame = tk.Frame(root, bg=BG_PANEL)
editor_frame.pack(fill="both", expand=True, padx=8, pady=4)

top_editor_bar = tk.Frame(editor_frame, bg=BG_PANEL)
top_editor_bar.pack(fill="x", padx=4, pady=2)

copy_btn = tk.Button(
    top_editor_bar, 
    text="[ NUSXA OLISH ]", 
    command=copy_to_clipboard,
    bg=BG_WIDGET, 
    fg=COLOR_CYAN, 
    activebackground=BG_WIDGET, 
    activeforeground=COLOR_CYAN,
    relief="flat", 
    font=FONT_INTERFACE
)
copy_btn.pack(side="right", padx=2, pady=2)

# TEXT WIDGET VA SCROLLBAR
scroll_bar = tk.Scrollbar(editor_frame)
scroll_bar.pack(side="right", fill="y")

log_box = tk.Text(
    editor_frame, 
    bg=BG_WIDGET, 
    fg=COLOR_WHITE, 
    insertbackground=COLOR_WHITE,
    relief="flat", 
    font=FONT_CODE, 
    yscrollcommand=scroll_bar.set,
    wrap="word"
)
log_box.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
scroll_bar.config(command=log_box.yview)

# STATUS BAR (PASTKI CHIZIQ)
status_var = tk.StringVar()
status_var.set("[LOOP-CORE ACTIVE]")

status_bar = tk.Label(
    root, 
    textvariable=status_var, 
    anchor="w", 
    bg=BG_PANEL, 
    fg=COLOR_GRAY, 
    font=("Consolas", 8)
)
status_bar.pack(fill="x", pady=(4, 0))

# DASTURNI BOSH_LANG'ICH ISHGA TUSHIRISH LOGI
log_box.insert("1.0", "# === [LOOP-CORE] :: SYSTEM INITIALIZED ===\n# Kalit so'zni kiriting va tahlilni boshlang.\n")
run_search() # Dastur ochilishi bilan 'all' buyrug'ini ishga tushiradi

root.mainloop()
