# ==========================================
# LOYIHA: Cyber Ghost & Monitor v1.0
# PLATFORMA: Python (Pydroid 3 / Android)
# VAZIFASI: Tizim monitori + Rasm ichiga sir yashirish
# ==========================================

import os
import platform
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


# --- 1. STEGANOGRAFIYA (Rasm ichiga yashirish) ---
DELIMITER = b"====CYBER_GHOST===="

def hide_secret(image_path, secret_text):
    try:
        # Rasmni binar (byte) formatda o'qiymiz
        with open(image_path, "ab") as img_file:
            img_file.write(DELIMITER)
            img_file.write(secret_text.encode('utf-8'))
        return True, "✅ Sirli matn rasm ichiga muvaffaqiyatli yashirildi!\nEndi bu rasmni birov ko'rsa ham, ichida sir borligini bilmaydi."
    except Exception as e:
        return False, f"❌ Xatolik yuz berdi: {e}"

def extract_secret(image_path):
    try:
        with open(image_path, "rb") as img_file:
            content = img_file.read()
            if DELIMITER in content:
                # Delimiter orqali ajratib olamiz
                secret_bytes = content.split(DELIMITER)[-1]
                return True, secret_bytes.decode('utf-8')
            else:
                return False, "⚠️ Bu rasm ichida hech qanday yashirin sir topilmadi."
    except Exception as e:
        return False, f"❌ Xatolik yuz berdi: {e}"


# --- 2. SYSTEM MONITOR ---
def get_system_info():
    info = []
    info.append(f"🤖 Operatsion tizim: {platform.system()} {platform.release()}")
    info.append(f"📱 Qurilma arxitekturasi: {platform.machine()}")
    
    # Android/Linux uchun xotira holati (oddiy usulda)
    try:
        mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        mem_gb = mem_bytes / (1024.**3)
        info.append(f"🧠 Umumiy RAM (taxminiy): {mem_gb:.2f} GB")
    except:
        info.append("🧠 RAM ma'lumotini o'qib bo'lmadi.")
        
    return "\n".join(info)


# --- TKINTER GUI OYNASI ---
root = tk.Tk()
root.title("Cyber Ghost & Monitor")
root.geometry("450x650")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use('clam')

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# ==========================================
# TAB 1: STEGANOGRAFIYA
# ==========================================
tab_stego = tk.Frame(notebook, bg="#2d2d2d")
notebook.add(tab_stego, text="👻 Ghost (Stego)")

tk.Label(tab_stego, text="Rasm fayli manzili (masalan: /sdcard/Download/rasm.jpg):", bg="#2d2d2d", fg="white", font=("Arial", 9, "bold")).pack(anchor="w", padx=10, pady=(10, 2))
entry_img_path = tk.Entry(tab_stego, width=40, font=("Arial", 11))
entry_img_path.pack(padx=10, fill="x")

tk.Label(tab_stego, text="Yashirin matn (Sir):", bg="#2d2d2d", fg="white", font=("Arial", 9, "bold")).pack(anchor="w", padx=10, pady=(10, 2))
entry_secret = tk.Entry(tab_stego, width=40, font=("Arial", 11))
entry_secret.pack(padx=10, fill="x")

# AI Yordamchi log oynasi
tk.Label(tab_stego, text="🤖 AI Yordamchi (Natijalar):", bg="#2d2d2d", fg="#4CAF50", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(15, 2))
ai_log = scrolledtext.ScrolledText(tab_stego, height=8, width=30, bg="black", fg="#00FF00", font=("Courier", 10))
ai_log.pack(padx=10, fill="both", expand=True, pady=5)
ai_log.insert(tk.END, "[AI] Assalomu alaykum, Xo'jayin! Men ishga tayyorman.\nRasmni tanlang va sirni kiriting.\n")

def ai_speak(text):
    ai_log.insert(tk.END, f"\n[AI] {text}\n")
    ai_log.see(tk.END)

def btn_hide():
    img = entry_img_path.get().strip()
    sec = entry_secret.get()
    if not img or not sec:
        ai_speak("Xato! Rasm manzili va sirli matnni to'liq kiriting.")
        return
    if not os.path.exists(img):
        ai_speak(f"Xato! Rasm topilmadi: {img}\nManzil to'g'riligini tekshiring.")
        return
    
    ai_speak("Jarayon boshlandi... Fayl kodlari o'zgartirilmoqda...")
    success, msg = hide_secret(img, sec)
    ai_speak(msg)

def btn_extract():
    img = entry_img_path.get().strip()
    if not img:
        ai_speak("Xato! Rasm manzilini kiriting.")
        return
    if not os.path.exists(img):
        ai_speak("Xato! Rasm topilmadi. Qidiruv bekor qilindi.")
        return
        
    ai_speak("Rasm chuqur analiz qilinmoqda...")
    success, msg = extract_secret(img)
    if success:
        ai_speak(f"DIQQAT! SIR TOPILDI:\n>>> {msg} <<<")
    else:
        ai_speak(msg)

btn_frame = tk.Frame(tab_stego, bg="#2d2d2d")
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="🔒 Ichiga Yashirish", command=btn_hide, bg="#E91E63", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
tk.Button(btn_frame, text="👁️ Sirni O'qish", command=btn_extract, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

# ==========================================
# TAB 2: SYSTEM MONITOR
# ==========================================
tab_monitor = tk.Frame(notebook, bg="#1a1a2e")
notebook.add(tab_monitor, text="📊 Tizim Monitori")

tk.Label(tab_monitor, text="Tizim haqida ma'lumot (Real-time emas, Info):", bg="#1a1a2e", fg="#E91E63", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=10)

sys_output = scrolledtext.ScrolledText(tab_monitor, height=15, width=30, bg="black", fg="#00FFFF", font=("Courier", 11))
sys_output.pack(padx=10, fill="both", expand=True, pady=5)

def refresh_sys_info():
    sys_output.delete("1.0", tk.END)
    sys_output.insert(tk.END, "Tizim skanerlanmoqda...\n" + "-"*30 + "\n")
    sys_data = get_system_info()
    sys_output.insert(tk.END, sys_data + "\n" + "-"*30 + "\n✅ Barcha qismlar joyida!")

tk.Button(tab_monitor, text="🔄 Yangilash", command=refresh_sys_info, bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(pady=10)

# Boshlang'ich holatda info chiqarish
refresh_sys_info()

root.mainloop()
