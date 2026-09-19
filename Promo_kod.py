# ==========================================================
# LOYIHA: BARCODE / SHTRIX-KOD QIDIRUVChI APPLIKATSIYA
# PLATFORMA: Android (Pydroid 3 / Tkinter)
# ==========================================================

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

# Ranglar
BG_COLOR = "#0e1621"
INPUT_BG = "#17212b"
TEXT_COLOR = "#ffffff"
BTN_COLOR = "#4ea1f3"
CARD_BG = "#1c2733"

class BarcodeLookupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shtrix-kod Qidiruvchi")
        self.root.geometry("380x600")
        self.root.configure(bg=BG_COLOR)

        self._build_ui()

    def _build_ui(self):
        # Sarlavha
        header = tk.Label(
            self.root, 
            text="📦 Mahsulot Qidiruvchi", 
            font=("Arial", 16, "bold"), 
            bg=BG_COLOR, 
            fg=TEXT_COLOR
        )
        header.pack(pady=15)

        # Qidiruv ramkasi
        input_frame = tk.Frame(self.root, bg=BG_COLOR)
        input_frame.pack(fill="x", padx=15, pady=5)

        self.entry = tk.Entry(
            input_frame, 
            bg=INPUT_BG, 
            fg=TEXT_COLOR, 
            font=("Arial", 12), 
            insertbackground=TEXT_COLOR,
            bd=1,
            relief="solid"
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 5))
        self.entry.insert(0, "8906150490727")  # Rasmdagi shtrix-kod misol tariqasida

        search_btn = tk.Button(
            input_frame, 
            text="Qidirish 🔍", 
            bg=BTN_COLOR, 
            fg="white", 
            font=("Arial", 10, "bold"), 
            bd=0, 
            command=self._start_search,
            padx=10
        )
        search_btn.pack(side="right")

        # Status yorlig'i
        self.status_lbl = tk.Label(self.root, text="", font=("Arial", 10), bg=BG_COLOR, fg=BTN_COLOR)
        self.status_lbl.pack(pady=5)

        # Natija ko'rsatish oynasi
        self.result_frame = tk.Frame(self.root, bg=CARD_BG, bd=1, relief="solid")
        self.result_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.result_text = tk.Text(
            self.result_frame, 
            bg=CARD_BG, 
            fg=TEXT_COLOR, 
            font=("Arial", 11), 
            wrap="word", 
            bd=0,
            padx=10,
            pady=10
        )
        self.result_text.pack(fill="both", expand=True)

    def _start_search(self):
        barcode = self.entry.get().strip()
        if not barcode:
            messagebox.showwarning("Xatolik", "Iltimos, shtrix-kodni kiriting!")
            return

        self.status_lbl.config(text="Qidirilmoqda...")
        self.result_text.delete("1.0", tk.END)
        
        # UI qotib qolmasligi uchun alohida oqimda ishga tushiramiz
        threading.Thread(target=self._fetch_data, args=(barcode,), daemon=True).start()

    def _fetch_data(self, barcode):
        # Open Food Facts API (Oziq-ovqat va farmatsevtika/kosmetika uchun ochiq bazalardan biri)
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if response.status_code == 200 and data.get("status") == 1:
                product = data.get("product", {})
                
                name = product.get("product_name", "Noma'lum mahsulot")
                brands = product.get("brands", "Noma'lum brend")
                quantity = product.get("quantity", "Ko'rsatilmagan")
                categories = product.get("categories", "Kiritilmagan")
                countries = product.get("countries", "Noma'lum")

                result_msg = (
                    f"✅ MAHSULOT TOPILDI!\n\n"
                    f"📌 Nomi: {name}\n"
                    f"🏷️ Brend/Ilab chiqaruvchi: {brands}\n"
                    f"⚖️ Hajmi/O'lchami: {quantity}\n"
                    f"🌐 Davlatlar: {countries}\n"
                    f"📂 Kategoriya: {categories}\n"
                )
            else:
                result_msg = (
                    f"⚠️ Shtrix-kod: {barcode}\n\n"
                    f"Mahsulot xalqaro ochiq bazadan topilmadi.\n"
                    f"(Eslatma: Spey Medical kabi dori-darmonlar va maxsus vositalar xususiy farmatsevtika bazalarida saqlanishi mumkin)."
                )

        except Exception as e:
            result_msg = f"❌ Tarmoq xatosi yuz berdi:\n{str(e)}"

        self.root.after(0, lambda: self._update_ui(result_msg))

    def _update_ui(self, msg):
        self.status_lbl.config(text="")
        self.result_text.insert(tk.END, msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeLookupApp(root)
    root.mainloop()