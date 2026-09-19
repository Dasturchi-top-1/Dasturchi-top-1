# ==========================================================
# LOYIHA: MATNDAN QR KOD YARATUVCHI
# PLATFORMA: Android (Pydroid 3)
# ==========================================================

import os
import subprocess
import tkinter as tk

try:
    import qrcode
    from PIL import ImageTk
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False

SAVE_FOLDER = "AI/qr_codes"  # zaxira (agar umumiy papka topilmasa)

# Telefonning umumiy Rasmlar papkasi - shu yerga saqlansa, Galereya/Telegram/
# WhatsApp orqali osongina "Share" qilish mumkin bo'ladi
PUBLIC_PICTURES = "/storage/emulated/0/Pictures/QR_Codes"

# Rang sxemasi
BG_COLOR = "#0e1621"
PANEL_BG = "#1c2733"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#8a9aa9"
BTN_COLOR = "#4ea1f3"
INPUT_BG = "#242f3d"


def get_save_folder():
    """Imkon bo'lsa umumiy Rasmlar papkasini, bo'lmasa ilova papkasini qaytaradi"""
    try:
        os.makedirs(PUBLIC_PICTURES, exist_ok=True)
        return PUBLIC_PICTURES
    except Exception:
        os.makedirs(SAVE_FOLDER, exist_ok=True)
        return SAVE_FOLDER


class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Kod Yaratuvchi")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("380x550")
        self.root.minsize(300, 450)

        self.last_saved_path = None
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#17212b", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📱 QR Kod Yaratuvchi", bg="#17212b", fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=13)

        if not LIBS_AVAILABLE:
            tk.Label(
                self.root, text="⚠️  Kerakli kutubxonalar o'rnatilmagan.\n\n"
                                 "Pydroid 3 Terminal'ida ishga tushiring:\n\n"
                                 "pip install qrcode[pil]\npip install Pillow",
                bg=BG_COLOR, fg="#e0245e", font=("Arial", 11), justify="left",
            ).pack(pady=30, padx=20)
            return

        tk.Label(
            self.root, text="QR kodga aylantirmoqchi bo'lgan matningizni yozing:",
            bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 10), wraplength=340,
        ).pack(pady=(20, 8), padx=15)

        self.text_entry = tk.Text(
            self.root, height=4, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 12),
            insertbackground=TEXT_COLOR, relief="flat", wrap="word",
        )
        self.text_entry.pack(fill="x", padx=15, pady=6)

        tk.Button(
            self.root, text="✨ QR kod yaratish", command=self._generate,
            bg=BTN_COLOR, fg="white", font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2",
        ).pack(pady=10)

        self.qr_preview = tk.Label(self.root, bg=PANEL_BG)
        self.qr_preview.pack(pady=10)

        self.share_btn = tk.Button(
            self.root, text="📤 Ulashish (Share)", command=self._share,
            bg="#2ea043", fg="white", font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2",
        )
        # Faqat QR kod yaratilgandan keyin pack() qilinadi (_generate ichida)

        self.status = tk.Label(self.root, text="", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                                 font=("Arial", 9), wraplength=340)
        self.status.pack(pady=6)

    def _generate(self):
        text = self.text_entry.get("1.0", tk.END).strip()

        if not text:
            self.status.config(text="⚠️  Avval matn kiriting!")
            return

        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=3)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            filename = f"qr_{abs(hash(text)) % 100000}.png"
            save_folder = get_save_folder()
            path = os.path.join(save_folder, filename)
            img.save(path)
            self.last_saved_path = path

            preview = img.copy()
            preview.thumbnail((240, 240))
            photo = ImageTk.PhotoImage(preview)
            self.qr_preview.config(image=photo)
            self.qr_preview.image = photo  # referensni saqlab qolish - aks holda rasm yo'qoladi

            self.share_btn.pack(pady=6)

            if save_folder == PUBLIC_PICTURES:
                self.status.config(
                    text="✅ Saqlandi! Pastdagi 'Ulashish' tugmasini bosing,\n"
                         "yoki Galereya/Fayl menejeridan 'QR_Codes' papkasini\n"
                         "ochib, rasmni istalgan ilovaga yuboring."
                )
            else:
                self.status.config(text=f"✅ QR kod yaratildi va saqlandi:\n{path}")

        except Exception as e:
            self.status.config(text=f"❌ Xato: {e}")

    def _share(self):
        """Termux'da bo'lsa, Android ulashish oynasini ochadi.
        Pydroid'da bu ishlamasligi mumkin - shunda qo'lda ulashish kerak bo'ladi."""
        if not self.last_saved_path:
            return
        try:
            subprocess.run(
                ['termux-share', self.last_saved_path],
                timeout=5, capture_output=True,
            )
        except Exception:
            self.status.config(
                text="ℹ️  Avtomatik ulashish shu qurilmada ishlamadi.\n"
                     "Galereya yoki Fayl menejeridan 'QR_Codes'\n"
                     "papkasini ochib, rasmni qo'lda ulashing."
            )


# --- DASTUR ISHGA TUSHIRISH ---
if __name__ == '__main__':
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()
