# ==========================================================
# LOYIHA: AI CODE GENERATOR
# PLATFORMA: Android (Pydroid 3)
# FUNKSIYA: Vazifa tavsifi -> AI kod yozadi -> Saqlaydi -> Ishga tushiradi
# ==========================================================

import os
import re
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import requests

# ==========================================================
# SOZLAMALAR - BU YERGA O'Z API KALITINGIZNI QO'YING
# ==========================================================
OPENROUTER_API_KEY = "YOUR_OPENROUTER_KEY"  # openrouter.ai'dan oling
AI_MODEL = "deepseek/deepseek-v4-flash"
SAVE_FOLDER = "AI/generated_code"  # kod shu papkaga saqlanadi

# Rang sxemasi (dark mode, kod muharriri uslubi)
BG_COLOR = "#0e1621"
PANEL_BG = "#1c2733"
CODE_BG = "#0d1117"
TEXT_COLOR = "#ffffff"
CODE_TEXT_COLOR = "#c9d1d9"
BTN_COLOR = "#4ea1f3"
BTN_RUN_COLOR = "#2ea043"
SUBTEXT_COLOR = "#8a9aa9"
HEADER_BG = "#17212b"


class CodeGeneratorAI:
    """AI orqali kod generatsiya qiluvchi modul"""

    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def generate_code(self, task_description):
        system_prompt = (
            "Sen professional Python dasturchisan. Foydalanuvchi vazifasini o'qib, "
            "TO'LIQ ISHLAYDIGAN Python kodini yoz. Faqat kod bloki qaytar (```python ... ``` ichida), "
            "qo'shimcha tushuntirish yozma. Kod xatosiz, standart kutubxonalar bilan ishlashi kerak."
        )

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": task_description},
                    ],
                },
                timeout=60,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._extract_code(content), None

        except requests.exceptions.RequestException as e:
            return None, f"API xatosi: {e}"
        except (KeyError, IndexError):
            return None, "Javobni o'qib bo'lmadi."

    def _extract_code(self, text):
        """AI javobidan faqat kod qismini ajratib oladi"""
        match = re.search(r'```python\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        return text  # agar kod bloki topilmasa, to'liq javobni qaytaradi


class CodeFileManager:
    """Kodni faylga saqlovchi va ishga tushiruvchi modul"""

    def __init__(self, folder):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    def save_code(self, code):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"code_{timestamp}.py"
        path = os.path.join(self.folder, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        return path

    def run_code(self, path, timeout=30):
        """Kodni alohida jarayonda ishga tushiradi, natijani qaytaradi"""
        try:
            result = subprocess.run(
                [sys.executable, path],
                capture_output=True, text=True, timeout=timeout,
            )
            output = result.stdout
            if result.returncode != 0:
                output += f"\n--- XATO ---\n{result.stderr}"
            return output if output.strip() else "(Dastur hech narsa chiqarmadi)"
        except subprocess.TimeoutExpired:
            return f"⏱️ Vaqt tugadi ({timeout} soniyadan oshdi) - dastur to'xtatildi."
        except Exception as e:
            return f"❌ Ishga tushirishda xato: {e}"


class CodeGenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Code Generator")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("420x750")
        self.root.minsize(320, 500)

        self.ai = CodeGeneratorAI(OPENROUTER_API_KEY, AI_MODEL)
        self.file_manager = CodeFileManager(SAVE_FOLDER)
        self.current_code_path = None

        self._build_ui()

    def _build_ui(self):
        # --- Sarlavha ---
        header = tk.Frame(self.root, bg=HEADER_BG, height=50)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(
            header, text="🤖 AI Code Generator", bg=HEADER_BG, fg=TEXT_COLOR,
            font=("Arial", 13, "bold"),
        ).pack(pady=13)

        # --- Vazifa kiritish maydoni ---
        task_panel = tk.Frame(self.root, bg=PANEL_BG)
        task_panel.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(
            task_panel, text="Vazifani yozing:", bg=PANEL_BG, fg=SUBTEXT_COLOR,
            font=("Arial", 9), anchor="w",
        ).pack(fill="x", padx=8, pady=(6, 2))

        self.task_entry = tk.Text(
            task_panel, height=3, bg="#242f3d", fg=TEXT_COLOR, font=("Arial", 11),
            insertbackground=TEXT_COLOR, relief="flat", wrap="word",
        )
        self.task_entry.pack(fill="x", padx=8, pady=(0, 8))

        self.generate_btn = tk.Button(
            task_panel, text="✨ Kod yaratish", bg=BTN_COLOR, fg="white",
            font=("Arial", 11, "bold"), relief="flat", cursor="hand2",
            command=self._on_generate_clicked,
        )
        self.generate_btn.pack(pady=(0, 8))

        # --- Status ---
        self.status_label = tk.Label(
            self.root, text="Vazifa yozib, 'Kod yaratish' tugmasini bosing", bg=BG_COLOR,
            fg=SUBTEXT_COLOR, font=("Arial", 9),
        )
        self.status_label.pack(pady=2)

        # --- Kod ko'rsatish maydoni ---
        tk.Label(
            self.root, text="📄 Yaratilgan kod:", bg=BG_COLOR, fg=SUBTEXT_COLOR,
            font=("Arial", 9), anchor="w",
        ).pack(fill="x", padx=10)

        self.code_display = scrolledtext.ScrolledText(
            self.root, bg=CODE_BG, fg=CODE_TEXT_COLOR, font=("Courier New", 10),
            insertbackground=TEXT_COLOR, relief="flat", height=14, wrap="none",
        )
        self.code_display.pack(fill="both", expand=True, padx=8, pady=4)

        # --- Amal tugmalari ---
        action_row = tk.Frame(self.root, bg=BG_COLOR)
        action_row.pack(fill="x", padx=8, pady=4)

        self.run_btn = tk.Button(
            action_row, text="▶️ Ishga tushirish", bg=BTN_RUN_COLOR, fg="white",
            font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
            command=self._on_run_clicked, state="disabled",
        )
        self.run_btn.pack(side="left", padx=(0, 6))

        self.copy_btn = tk.Button(
            action_row, text="📋 Nusxalash", bg=BTN_COLOR, fg="white",
            font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
            command=self._on_copy_clicked, state="disabled",
        )
        self.copy_btn.pack(side="left")

        # --- Natija (output) maydoni ---
        tk.Label(
            self.root, text="📤 Natija:", bg=BG_COLOR, fg=SUBTEXT_COLOR,
            font=("Arial", 9), anchor="w",
        ).pack(fill="x", padx=10)

        self.output_display = scrolledtext.ScrolledText(
            self.root, bg=PANEL_BG, fg=TEXT_COLOR, font=("Courier New", 9),
            relief="flat", height=8, wrap="word", state="disabled",
        )
        self.output_display.pack(fill="both", expand=False, padx=8, pady=(4, 8))

    def _on_generate_clicked(self):
        task = self.task_entry.get("1.0", tk.END).strip()
        if not task:
            self.status_label.config(text="⚠️  Avval vazifani yozing!")
            return

        self.generate_btn.config(state="disabled")
        self.run_btn.config(state="disabled")
        self.status_label.config(text="⏳ AI kod yozmoqda...")
        self.code_display.delete("1.0", tk.END)

        threading.Thread(target=self._generate_thread, args=(task,), daemon=True).start()

    def _generate_thread(self, task):
        code, error = self.ai.generate_code(task)
        self.root.after(0, lambda: self._on_code_ready(code, error))

    def _on_code_ready(self, code, error):
        self.generate_btn.config(state="normal")

        if error:
            self.status_label.config(text=f"❌ {error}")
            return

        self.code_display.insert("1.0", code)

        # Avtomatik saqlash
        saved_path = self.file_manager.save_code(code)
        self.current_code_path = saved_path

        # Avtomatik nusxalash - kod yaratilgan zahoti clipboard'ga tushadi
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        self.root.update()

        self.status_label.config(text=f"✅ Kod tayyor, saqlandi va nusxalandi! ({os.path.basename(saved_path)})")
        self.run_btn.config(state="normal")
        self.copy_btn.config(state="normal")

    def _on_run_clicked(self):
        if not self.current_code_path:
            return

        self.status_label.config(text="⏳ Kod ishga tushmoqda...")
        self.output_display.config(state="normal")
        self.output_display.delete("1.0", tk.END)
        self.output_display.insert("1.0", "Kutilmoqda...")
        self.output_display.config(state="disabled")

        threading.Thread(target=self._run_thread, daemon=True).start()

    def _run_thread(self):
        output = self.file_manager.run_code(self.current_code_path)
        self.root.after(0, lambda: self._on_run_done(output))

    def _on_run_done(self, output):
        self.output_display.config(state="normal")
        self.output_display.delete("1.0", tk.END)
        self.output_display.insert("1.0", output)
        self.output_display.config(state="disabled")
        self.status_label.config(text="✅ Ishga tushirish tugadi")

    def _on_copy_clicked(self):
        code = self.code_display.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        self.root.update()
        self.status_label.config(text="📋 Kod nusxalandi!")


# --- DASTUR ISHGA TUSHIRISH ---
if __name__ == '__main__':
    if OPENROUTER_API_KEY == "SIZNING_API_KALITINGIZ":
        print("⚠️  DIQQAT: Avval kod ichidagi OPENROUTER_API_KEY qismiga")
        print("    o'z API kalitingizni qo'ying (openrouter.ai saytidan oling)!")

    root = tk.Tk()
    app = CodeGenApp(root)
    root.mainloop()
