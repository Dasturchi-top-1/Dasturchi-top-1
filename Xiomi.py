# ==========================================
# LOYIHA: Cyber Toolbox v3.2 (Tkinter GUI)
# PLATFORMA: Python (Pydroid 3)
# ==========================================

import base64
import os
import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


# --- 1. SHIFRLASH VA OCHISH FUNKSIYALARI ---
def encrypt_text(plain_text, secret_key):
  enc = []
  for i in range(len(plain_text)):
    key_c = secret_key[i % len(secret_key)]
    enc_c = chr(ord(plain_text[i]) + ord(key_c))
    enc.append(enc_c)
  return base64.urlsafe_b64encode("".join(enc).encode("utf-8")).decode("utf-8")


def decrypt_text(cipher_text, secret_key):
  try:
    decoded = (
        base64.urlsafe_b64decode(cipher_text.encode("utf-8"))
        .decode("utf-8")
        .strip()
    )
    dec = []
    for i in range(len(decoded)):
      key_c = secret_key[i % len(secret_key)]
      dec_c = chr(ord(decoded[i]) - ord(key_c))
      dec.append(dec_c)
    return "".join(dec)
  except Exception:
    return (
        "❌ XATOLIK: Kalit so'z xato yoki shifrlangan matn noto'g'ri kiritildi!"
    )


# --- 2. WI-FI SCANNER ---
def scan_network(output_box):
  output_box.delete("1.0", tk.END)
  output_box.insert(tk.END, "🔍 Tarmoq skanerlanmoqda, iltimos kuting...\n")

  def run():
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8", 80))
      local_ip = s.getsockname()[0]
      s.close()

      output_box.insert(tk.END, f"💻 Sizning IP: {local_ip}\n")
      base_ip = ".".join(local_ip.split(".")[:-1]) + "."
      output_box.insert(tk.END, f"🌐 Tarmoq diapazoni: {base_ip}1 - 254\n\n")

      active_count = 0
      for i in range(1, 30):
        target_ip = base_ip + str(i)
        try:
          sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          sock.settimeout(0.1)
          result = sock.connect_ex((target_ip, 80))
          if result == 0 or target_ip == local_ip:
            output_box.insert(tk.END, f"🟢 Faol qurilma topildi: {target_ip}\n")
            active_count += 1
          sock.close()
        except:
          pass

      output_box.insert(
          tk.END, f"\n✅ Skanerlash yakunlandi! Jami faol: {active_count} ta\n"
      )
    except Exception as e:
      output_box.insert(
          tk.END, f"❌ Tarmoqni skanerlashda xatolik: {e}\n(Wi-Fi yoqilganmi?)\n"
      )

  threading.Thread(target=run).start()


# --- 3. SMART FILE FINDER ---
def search_files(keyword, output_box):
  output_box.delete("1.0", tk.END)
  if not keyword:
    output_box.insert(tk.END, "❌ Qidirish uchun so'z kiritilmadi!")
    return

  output_box.insert(tk.END, f"📂 '{keyword}' 📁 Telefonda qidirilmoqda...\n\n")

  def run():
    found_count = 0
    search_path = "/sdcard/"

    try:
      for root_dir, dirs, files in os.walk(search_path):
        if "Android" in root_dir and "data" in root_dir:
          continue
        for file in files:
          if keyword.lower() in file.lower():
            full_path = os.path.join(root_dir, file)
            output_box.insert(tk.END, f"🎯 {full_path}\n")
            found_count += 1
            if found_count >= 25:
              output_box.insert(
                  tk.END, "\n... (Natijalar ko'p, bir qismi ko'rsatildi)"
              )
              break
        if found_count >= 25:
          break
    except Exception as e:
      output_box.insert(tk.END, f"❌ Xatolik: {e}\n")

    output_box.insert(
        tk.END, f"\n✅ Qidiruv tugadi! Topildi: {found_count} ta fayl.\n"
    )

  threading.Thread(target=run).start()


# --- TKINTER GUI OYNASI ---
root = tk.Tk()
root.title("Cyber Toolbox v3.2")
root.geometry("400x600")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# 1-BO'LIM: SEYF (RAQAMLI QUTI)
tab_vault = ttk.Frame(notebook)
notebook.add(tab_vault, text="🔐 Seyf")

tk.Label(
    tab_vault,
    text="Maxfiy matn (Yoki 1 yildan keyin Shifrni yozing):",
    font=("Arial", 10, "bold"),
).pack(anchor="w", padx=10, pady=5)
entry_text = tk.Entry(tab_vault, width=35, font=("Arial", 11))
entry_text.pack(padx=10, fill="x")

tk.Label(
    tab_vault, text="Maxfiy kalit so'z (Master Key):", font=("Arial", 10, "bold")
).pack(anchor="w", padx=10, pady=5)
entry_key = tk.Entry(tab_vault, width=35, font=("Arial", 11), show="*")
entry_key.pack(padx=10, fill="x")


def do_encrypt():
  txt = entry_text.get()
  key = entry_key.get()
  if txt and key:
    res = encrypt_text(txt, key)
    text_result.delete("1.0", tk.END)
    text_result.insert(tk.END, res)
  else:
    messagebox.showerror("Xato", "Maydonlar bo'sh bo'lmasligi kerak!")


def do_decrypt():
  txt = entry_text.get()
  key = entry_key.get()
  if txt and key:
    res = decrypt_text(txt, key)
    text_result.delete("1.0", tk.END)
    text_result.insert(tk.END, res)
  else:
    messagebox.showerror("Xato", "Maydonlar bo'sh bo'lmasligi kerak!")


def copy_to_clipboard():
  root.clipboard_clear()
  root.clipboard_append(text_result.get("1.0", tk.END).strip())
  messagebox.showinfo(
      "Nusxalandi",
      "Natija xotiraga olindi! Uni Qaydlarga (Notes) borib saqlang.",
  )


btn_frame = tk.Frame(tab_vault)
btn_frame.pack(pady=10)

tk.Button(
    btn_frame,
    text="🔒 Shifrlash",
    command=do_encrypt,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
).pack(side="left", padx=5)
tk.Button(
    btn_frame,
    text="🔓 Ochish",
    command=do_decrypt,
    bg="#2196F3",
    fg="white",
    font=("Arial", 10, "bold"),
).pack(side="left", padx=5)
tk.Button(
    btn_frame,
    text="📋 Nusxalash",
    command=copy_to_clipboard,
    bg="#FF9800",
    fg="white",
    font=("Arial", 10, "bold"),
).pack(side="left", padx=5)

tk.Label(tab_vault, text="Natija (Shifr yoki Asl matn):", font=("Arial", 9, "bold")).pack(
    anchor="w", padx=10
)
text_result = scrolledtext.ScrolledText(tab_vault, height=8, width=30)
text_result.pack(padx=10, fill="both", expand=True, pady=5)


# 2-BO'LIM: WI-FI
tab_wifi = ttk.Frame(notebook)
notebook.add(tab_wifi, text="🌐 Wi-Fi")

tk.Button(
    tab_wifi,
    text="🔍 Tarmoqni Skanerlash",
    command=lambda: scan_network(wifi_output),
    bg="#9C27B0",
    fg="white",
    font=("Arial", 11, "bold"),
).pack(pady=10, fill="x", padx=10)
wifi_output = scrolledtext.ScrolledText(tab_wifi, height=20, width=30)
wifi_output.pack(padx=10, fill="both", expand=True, pady=5)


# 3-BO'LIM: FAYL QIDIRUVCHI
tab_file = ttk.Frame(notebook)
notebook.add(tab_file, text="📂 Fayl Topuvchi")

tk.Label(tab_file, text="Qidirilayotgan fayl nomi:", font=("Arial", 10, "bold")).pack(
    anchor="w", padx=10, pady=5
)
entry_file = tk.Entry(tab_file, width=30, font=("Arial", 11))
entry_file.pack(padx=10, fill="x")

tk.Button(
    tab_file,
    text="🔍 Faylni Qidirish",
    command=lambda: search_files(entry_file.get(), file_output),
    bg="#E91E63",
    fg="white",
    font=("Arial", 11, "bold"),
).pack(pady=10, fill="x", padx=10)
file_output = scrolledtext.ScrolledText(tab_file, height=15, width=30)
file_output.pack(padx=10, fill="both", expand=True, pady=5)

root.mainloop()
