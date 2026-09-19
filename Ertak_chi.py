# ==========================================================
# LOYIHA: AI ERTAK/HIKOYA GENERATOR
# PLATFORMA: Android (Pydroid 3)
# FUNKSIYA: Qahramon, mavzu, janr kiritasiz - AI original hikoya to'qiydi
# ==========================================================

import os
import threading
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import requests

# ==========================================================
# SOZLAMALAR - BU YERGA O'Z API KALITINGIZNI QO'YING
# ==========================================================
OPENROUTER_API_KEY = "YOUR_OPENROUTER_KEY"
AI_MODEL = "deepseek/deepseek-v4-flash"

SAVE_FOLDER = "/storage/emulated/0/Ertaklar"


def get_save_folder():
    """Imkon bo'lsa umumiy xotiraga, bo'lmasa ilova papkasiga saqlaydi"""
    try:
        os.makedirs(SAVE_FOLDER, exist_ok=True)
        return SAVE_FOLDER
    except Exception:
        fallback = "AI/stories"
        os.makedirs(fallback, exist_ok=True)
        return fallback

# Rang sxemasi - issiq, ertak kitobi uslubi
BG_COLOR = "#1a1625"
PANEL_BG = "#2d2438"
TEXT_COLOR = "#f5e6d3"
SUBTEXT_COLOR = "#a89bb5"
BTN_COLOR = "#e07a5f"
BTN_GREEN = "#81b29a"
INPUT_BG = "#3d3350"
ACCENT = "#f2cc8f"

GENRES = ["Bolalar ertagi", "Sarguzasht", "Fantastika", "Detektiv", "Hazil-mutoyiba", "Sirli/qo'rqinchli"]


def styled_button(parent, text, command, color=BTN_COLOR, **kwargs):
    return tk.Button(
        parent, text=text, command=command, bg=color, fg="white",
        font=("Georgia", 10, "bold"), relief="flat", cursor="hand2", **kwargs
    )


class StoryGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ertak Generator")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("400x750")
        self.root.minsize(320, 500)

        self.last_story = None
        self.selected_genre = tk.StringVar(value=GENRES[0])

        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.root, bg=PANEL_BG, height=55)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📖 Ertak Generator", bg=PANEL_BG, fg=ACCENT,
                  font=("Georgia", 15, "bold")).pack(pady=14)

        form = tk.Frame(self.root, bg=BG_COLOR)
        form.pack(fill="x", padx=15, pady=8)

        tk.Label(form, text="Janr:", bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9)).pack(anchor="w")
        genre_menu = tk.OptionMenu(form, self.selected_genre, *GENRES)
        genre_menu.config(bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 10), relief="flat")
        genre_menu.pack(fill="x", pady=(2, 8))

        tk.Label(form, text="Bosh qahramon (ixtiyoriy):", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                  font=("Arial", 9)).pack(anchor="w")
        self.character_entry = tk.Entry(form, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 11))
        self.character_entry.insert(0, "masalan: jasur quyon")
        self.character_entry.pack(fill="x", pady=(2, 8))

        tk.Label(form, text="Mavzu/joylashuv (ixtiyoriy):", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                  font=("Arial", 9)).pack(anchor="w")
        self.theme_entry = tk.Entry(form, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 11))
        self.theme_entry.insert(0, "masalan: sehrli o'rmon")
        self.theme_entry.pack(fill="x", pady=(2, 8))

        tk.Label(form, text="Hikoya uzunligi:", bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9)).pack(anchor="w")
        self.length_var = tk.StringVar(value="O'rtacha")
        length_frame = tk.Frame(form, bg=BG_COLOR)
        length_frame.pack(fill="x", pady=(2, 4))
        for length in ["Qisqa", "O'rtacha", "Uzun"]:
            tk.Radiobutton(
                length_frame, text=length, variable=self.length_var, value=length,
                bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=INPUT_BG,
                activebackground=BG_COLOR, activeforeground=TEXT_COLOR, font=("Arial", 9),
            ).pack(side="left", padx=(0, 10))

        styled_button(self.root, "✨ Ertak to'qish", self._generate, color=BTN_GREEN).pack(pady=10)

        self.status = tk.Label(self.root, text="", bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9))
        self.status.pack()

        self.story_box = scrolledtext.ScrolledText(
            self.root, bg=PANEL_BG, fg=TEXT_COLOR, font=("Georgia", 11), wrap="word", height=16,
            padx=10, pady=10,
        )
        self.story_box.pack(fill="both", expand=True, padx=15, pady=8)

        # --- Saqlashni tasdiqlash paneli (ertak tayyor bo'lganda ko'rinadi) ---
        self.save_prompt_frame = tk.Frame(self.root, bg=PANEL_BG)

        self.save_question_label = tk.Label(
            self.save_prompt_frame, text="💾 Ertakni xotiraga saqlaymizmi?",
            bg=PANEL_BG, fg=ACCENT, font=("Arial", 10, "bold"),
        )
        self.save_question_label.pack(side="left", padx=10, pady=8)

        styled_button(self.save_prompt_frame, "✅ Ha", self._confirm_save, color=BTN_GREEN,
                       width=6).pack(side="left", padx=4)
        styled_button(self.save_prompt_frame, "❌ Yo'q", self._decline_save, color="#6b5b73",
                       width=6).pack(side="left", padx=4)

        btn_row = tk.Frame(self.root, bg=BG_COLOR)
        btn_row.pack(pady=8)
        styled_button(btn_row, "📋 Nusxalash", self._copy).pack(side="left", padx=4)

    def _generate(self):
        if OPENROUTER_API_KEY == "SIZNING_API_KALITINGIZ":
            self.status.config(text="⚠️  Avval API kalitni sozlang!")
            return

        genre = self.selected_genre.get()
        character = self.character_entry.get().strip()
        theme = self.theme_entry.get().strip()
        length = self.length_var.get()

        if character.startswith("masalan"):
            character = ""
        if theme.startswith("masalan"):
            theme = ""

        length_map = {"Qisqa": "150-200 so'z", "O'rtacha": "300-400 so'z", "Uzun": "500-700 so'z"}

        prompt_parts = [f"Janr: {genre}."]
        if character:
            prompt_parts.append(f"Bosh qahramon: {character}.")
        if theme:
            prompt_parts.append(f"Mavzu/joylashuv: {theme}.")
        prompt_parts.append(f"Uzunlik: taxminan {length_map[length]}.")
        prompt_parts.append("O'zbek tilida, original, qiziqarli hikoya yoz. Sarlavha bilan boshla.")

        prompt = " ".join(prompt_parts)

        self.status.config(text="⏳ Ertak to'qilmoqda...")
        self.story_box.delete("1.0", tk.END)
        self.save_prompt_frame.pack_forget()
        threading.Thread(target=self._generate_thread, args=(prompt,), daemon=True).start()

    def _generate_thread(self, prompt):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "Sen ijodkor ertak/hikoyachisan. Faqat original, o'zing to'qigan hikoyalar yoz."},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=60,
            )
            response.raise_for_status()
            story = response.json()["choices"][0]["message"]["content"]
            self.root.after(0, lambda: self._show_story(story))
        except Exception as e:
            self.root.after(0, lambda: self.status.config(text=f"❌ Xato: {e}"))

    def _show_story(self, story):
        self.story_box.insert("1.0", story)
        self.last_story = story
        self.status.config(text="✅ Tayyor!")

        # Saqlashni so'raymiz
        self.save_prompt_frame.pack(fill="x", padx=15, pady=(0, 8))

    def _confirm_save(self):
        if not self.last_story:
            return

        folder = get_save_folder()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(folder, f"ertak_{timestamp}.txt")

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.last_story)
            self.status.config(text=f"✅ Saqlandi: {path}")
        except Exception as e:
            self.status.config(text=f"❌ Saqlashda xato: {e}")

        self.save_prompt_frame.pack_forget()

    def _decline_save(self):
        self.status.config(text="➖ Saqlanmadi.")
        self.save_prompt_frame.pack_forget()

    def _copy(self):
        if not self.last_story:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_story)
        self.root.update()
        self.status.config(text="📋 Nusxalandi!")


# --- DASTUR ISHGA TUSHIRISH ---
if __name__ == '__main__':
    root = tk.Tk()
    app = StoryGeneratorApp(root)
    root.mainloop()
