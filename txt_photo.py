# ==========================================================
# LOYIHA: AI TERMINAL - ASCII-ART CHIZUVCHI
# PLATFORMA: Android (Pydroid 3)
# FUNKSIYA: Terminal ko'rinishidagi oyna + OpenRouter AI
#           "Chiz" desangiz, AI ASCII-art yasaydi, keyin
#           xotiraga saqlashni so'raydi
# ==========================================================

import os
import threading
from datetime import datetime
import tkinter as tk
import requests

# ==========================================================
# SOZLAMALAR - BU YERGA O'Z API KALITINGIZNI QO'YING
# ==========================================================
OPENROUTER_API_KEY = "YOUR_API_KEY"
AI_MODEL = "deepseek/deepseek-v4-flash"

SAVE_FOLDER = "AI/outputs/ascii_art"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Terminal uslubidagi rang sxemasi
TERM_BG = "#0c0c0c"
TERM_TEXT = "#00ff41"       # klassik terminal-yashil
TERM_PROMPT = "#4ea1f3"
TERM_ERROR = "#ff5555"
INPUT_BG = "#1a1a1a"

SYSTEM_PROMPT = (
    "Sen terminal ichida ishlaydigan AI yordamchisan. Agar foydalanuvchi biror narsani "
    "'chiz' desa, uni ASCII-art (belgilardan yasalgan rasm) sifatida, monospace shriftga "
    "mos formatda chiz - faqat oddiy klaviatura belgilaridan (masalan # * . / \\ | - + = @) "
    "foydalan, kod bloki ichida bermay, to'g'ridan-to'g'ri matn sifatida yoz. "
    "Boshqa savollarga oddiy, qisqa javob ber."
)


class AITerminal:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Terminal")
        self.root.configure(bg=TERM_BG)
        self.root.geometry("420x700")
        self.root.minsize(320, 480)

        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.last_ai_response = None
        self.awaiting_save_confirmation = False

        self._build_ui()
        self._print_line("AI Terminal v1.0 ishga tushdi.", TERM_PROMPT)
        self._print_line("Buyruq yozing (masalan: 'Creeper chiz')\n", TERM_PROMPT)

    def _build_ui(self):
        self.output = tk.Text(
            self.root, bg=TERM_BG, fg=TERM_TEXT, font=("Courier New", 10),
            wrap="word", relief="flat", state="disabled", padx=8, pady=8,
        )
        self.output.pack(fill="both", expand=True, padx=6, pady=(6, 0))

        input_frame = tk.Frame(self.root, bg=TERM_BG)
        input_frame.pack(fill="x", padx=6, pady=6)

        self.prompt_label = tk.Label(
            input_frame, text=">", bg=TERM_BG, fg=TERM_PROMPT, font=("Courier New", 12, "bold"),
        )
        self.prompt_label.pack(side="left", padx=(0, 4))

        self.entry = tk.Entry(
            input_frame, bg=INPUT_BG, fg=TERM_TEXT, font=("Courier New", 11),
            insertbackground=TERM_TEXT, relief="flat",
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.entry.bind("<Return>", lambda e: self._on_submit())
        self.entry.focus()

    def _print_line(self, text, color=TERM_TEXT):
        self.output.config(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.tag_add(color, "end-2l", "end-1l")
        self.output.tag_config(color, foreground=color)
        self.output.config(state="disabled")
        self.output.see(tk.END)

    def _on_submit(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.entry.delete(0, tk.END)
        self._print_line(f"> {user_text}", TERM_PROMPT)

        # Agar saqlashni tasdiqlash kutilayotgan bo'lsa
        if self.awaiting_save_confirmation:
            self._handle_save_confirmation(user_text)
            return

        self._print_line("⏳ AI javob bermoqda...", TERM_PROMPT)
        threading.Thread(target=self._ask_ai, args=(user_text,), daemon=True).start()

    def _ask_ai(self, user_text):
        self.history.append({"role": "user", "content": user_text})
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                json={"model": AI_MODEL, "messages": self.history},
                timeout=40,
            )
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})
            self.root.after(0, lambda: self._show_ai_response(reply))
        except Exception as e:
            self.root.after(0, lambda: self._print_line(f"❌ Xato: {e}", TERM_ERROR))

    def _show_ai_response(self, reply):
        self._print_line(reply, TERM_TEXT)
        self.last_ai_response = reply

        # ASCII-art chizilganini taxminiy aniqlaymiz (ko'p qatorli, maxsus belgilar bor)
        looks_like_art = reply.count('\n') >= 3

        if looks_like_art:
            self._print_line("\n💾 Buni xotiraga saqlaymi? (ha/yo'q)", TERM_PROMPT)
            self.awaiting_save_confirmation = True

    def _handle_save_confirmation(self, answer):
        self.awaiting_save_confirmation = False
        lower = answer.strip().lower()

        if lower in ("ha", "h", "yes", "y"):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"art_{timestamp}.txt"
            path = os.path.join(SAVE_FOLDER, filename)
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.last_ai_response)
                self._print_line(f"✅ Saqlandi: {path}\n", TERM_PROMPT)
            except Exception as e:
                self._print_line(f"❌ Saqlashda xato: {e}\n", TERM_ERROR)
        else:
            self._print_line("➖ Saqlanmadi.\n", TERM_PROMPT)


# --- DASTUR ISHGA TUSHIRISH ---
if __name__ == '__main__':
    if OPENROUTER_API_KEY == "SIZNING_API_KALITINGIZ":
        print("⚠️  DIQQAT: OPENROUTER_API_KEY qismiga o'z API kalitingizni qo'ying!")

    root = tk.Tk()
    app = AITerminal(root)
    root.mainloop()
