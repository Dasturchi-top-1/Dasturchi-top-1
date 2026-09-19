# ==========================================================
# LOYIHA: MUSIQA + KUNDALIK + FITNESS TRACKER
# PLATFORMA: Android (Pydroid 3)
# BO'LIMLAR: Qo'shiq havolasi qidirish, Kundalik/kayfiyat, Mashq tracker
# ==========================================================

import os
import json
import urllib.parse
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import date, datetime

DATA_FOLDER = "AI/data"
os.makedirs(DATA_FOLDER, exist_ok=True)
DIARY_FILE = os.path.join(DATA_FOLDER, "diary.json")
WORKOUTS_FILE = os.path.join(DATA_FOLDER, "workouts.json")

# Rang sxemasi
BG_COLOR = "#0e1621"
PANEL_BG = "#1c2733"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#8a9aa9"
BTN_COLOR = "#4ea1f3"
BTN_GREEN = "#2ea043"
BTN_RED = "#e0245e"
INPUT_BG = "#242f3d"

MOODS = ["😄 Ajoyib", "🙂 Yaxshi", "😐 O'rtacha", "😔 Yomon", "😢 Juda yomon"]


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def styled_button(parent, text, command, color=BTN_COLOR, **kwargs):
    return tk.Button(
        parent, text=text, command=command, bg=color, fg="white",
        font=("Arial", 10, "bold"), relief="flat", cursor="hand2", **kwargs
    )


# ==========================================================
# 1-BO'LIM: QO'SHIQ MATNI HAVOLASI QIDIRUVCHI
# ==========================================================

class MusicTab(tk.Frame):
    """Qo'shiq nomi bo'yicha Genius va YouTube havolalarini yaratadi.
    ESLATMA: haqiqiy matnni (lyrics) ko'rsatmaydi - mualliflik huquqi
    sababli faqat rasmiy manbalarga havola beradi."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="🎵 Qo'shiq Havolasi Qidiruvchi", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Qo'shiq nomi va ijrochisini kiriting:", bg=BG_COLOR,
                  fg=SUBTEXT_COLOR, font=("Arial", 9)).pack(anchor="w", padx=15)

        self.song_entry = tk.Entry(self, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 11))
        self.song_entry.pack(fill="x", padx=15, pady=6)
        self.song_entry.bind("<Return>", lambda e: self._search())

        styled_button(self, "🔍 Havolalarni topish", self._search, color=BTN_GREEN).pack(pady=6)

        self.result_frame = tk.Frame(self, bg=BG_COLOR)
        self.result_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.status = tk.Label(self, text="", bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9))
        self.status.pack()

    def _search(self):
        query = self.song_entry.get().strip()
        if not query:
            return

        for widget in self.result_frame.winfo_children():
            widget.destroy()

        encoded = urllib.parse.quote(query)
        links = {
            "📝 Genius (matn/lyrics)": f"https://genius.com/search?q={encoded}",
            "🎥 YouTube (video/audio)": f"https://www.youtube.com/results?search_query={encoded}",
            "🎧 Spotify (tinglash)": f"https://open.spotify.com/search/{encoded}",
        }

        for label, url in links.items():
            card = tk.Frame(self.result_frame, bg=PANEL_BG)
            card.pack(fill="x", pady=4)

            tk.Label(card, text=label, bg=PANEL_BG, fg=TEXT_COLOR,
                      font=("Arial", 10, "bold"), anchor="w").pack(fill="x", padx=10, pady=(8, 2))

            styled_button(
                card, "📋 Havolani nusxalash", lambda u=url, l=label: self._copy(u, l),
            ).pack(anchor="w", padx=10, pady=(0, 8))

        self.status.config(text=f"✅ '{query}' uchun havolalar tayyor")

    def _copy(self, url, label):
        self.clipboard_clear()
        self.clipboard_append(url)
        self.update()
        self.status.config(text=f"📋 {label} havolasi nusxalandi!")


# ==========================================================
# 2-BO'LIM: KUNDALIK / KAYFIYAT TRACKER
# ==========================================================

class DiaryTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self.entries = load_json(DIARY_FILE, [])
        self.selected_mood = tk.StringVar(value=MOODS[1])
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        tk.Label(self, text="📖 Kundalik", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Bugungi kayfiyat:", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                  font=("Arial", 9)).pack(anchor="w", padx=15)

        mood_menu = tk.OptionMenu(self, self.selected_mood, *MOODS)
        mood_menu.config(bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 10), relief="flat")
        mood_menu.pack(fill="x", padx=15, pady=4)

        self.entry_text = scrolledtext.ScrolledText(
            self, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 10), wrap="word", height=5
        )
        self.entry_text.pack(fill="x", padx=15, pady=6)

        styled_button(self, "💾 Kundalikka yozish", self._save_entry, color=BTN_GREEN).pack(pady=6)

        self.stats_label = tk.Label(self, text="", bg=BG_COLOR, fg=BTN_COLOR, font=("Arial", 10, "bold"))
        self.stats_label.pack(pady=4)

        list_frame = tk.Frame(self, bg=BG_COLOR)
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.entry_list = tk.Listbox(
            list_frame, bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9),
            relief="flat", selectbackground=BTN_COLOR,
        )
        self.entry_list.pack(fill="both", expand=True, side="left")

        scrollbar = tk.Scrollbar(list_frame, command=self.entry_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.entry_list.config(yscrollcommand=scrollbar.set)

    def _save_entry(self):
        text = self.entry_text.get("1.0", tk.END).strip()
        if not text:
            return

        self.entries.append({
            'date': date.today().strftime('%Y-%m-%d'),
            'mood': self.selected_mood.get(),
            'text': text,
        })
        save_json(DIARY_FILE, self.entries)
        self.entry_text.delete("1.0", tk.END)
        self._refresh_list()

    def _refresh_list(self):
        self.entry_list.delete(0, tk.END)
        for entry in reversed(self.entries):
            preview = entry['text'][:40] + ("..." if len(entry['text']) > 40 else "")
            self.entry_list.insert(tk.END, f"{entry['date']} {entry['mood']} — {preview}")

        # Oylik statistika (joriy oy)
        current_month = date.today().strftime('%Y-%m')
        month_entries = [e for e in self.entries if e['date'].startswith(current_month)]

        if month_entries:
            mood_counts = {}
            for e in month_entries:
                mood_counts[e['mood']] = mood_counts.get(e['mood'], 0) + 1
            most_common = max(mood_counts, key=mood_counts.get)
            self.stats_label.config(
                text=f"Bu oy: {len(month_entries)} ta yozuv | Ko'p uchragan kayfiyat: {most_common}"
            )
        else:
            self.stats_label.config(text="Bu oy hali yozuv yo'q")


# ==========================================================
# 3-BO'LIM: FITNESS / MASHQ TRACKER
# ==========================================================

class FitnessTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self.workouts = load_json(WORKOUTS_FILE, [])
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        tk.Label(self, text="🏋️ Fitness Tracker", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=10)

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(fill="x", padx=15)

        self.exercise_entry = tk.Entry(form, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 10))
        self.exercise_entry.insert(0, "Mashq nomi (masalan: Squat)")
        self.exercise_entry.pack(fill="x", pady=3)

        row = tk.Frame(form, bg=BG_COLOR)
        row.pack(fill="x", pady=3)

        self.sets_entry = tk.Entry(row, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 10), width=8)
        self.sets_entry.insert(0, "Setlar")
        self.sets_entry.pack(side="left", padx=(0, 4))

        self.reps_entry = tk.Entry(row, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 10), width=8)
        self.reps_entry.insert(0, "Takror")
        self.reps_entry.pack(side="left", padx=4)

        self.weight_entry = tk.Entry(row, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 10), width=8)
        self.weight_entry.insert(0, "Kg")
        self.weight_entry.pack(side="left", padx=4)

        styled_button(form, "➕ Qo'shish", self._add_workout, color=BTN_GREEN).pack(pady=6)

        self.streak_label = tk.Label(self, text="", bg=BG_COLOR, fg=BTN_COLOR, font=("Arial", 11, "bold"))
        self.streak_label.pack(pady=4)

        list_frame = tk.Frame(self, bg=BG_COLOR)
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.workout_list = tk.Listbox(
            list_frame, bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9),
            relief="flat", selectbackground=BTN_COLOR,
        )
        self.workout_list.pack(fill="both", expand=True, side="left")

        scrollbar = tk.Scrollbar(list_frame, command=self.workout_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.workout_list.config(yscrollcommand=scrollbar.set)

        styled_button(self, "🗑️ Tanlanganni o'chirish", self._delete_selected, color=BTN_RED).pack(pady=5)

    def _add_workout(self):
        exercise = self.exercise_entry.get().strip()
        if not exercise or exercise == "Mashq nomi (masalan: Squat)":
            return

        def safe_int(entry, default=0):
            val = entry.get().strip()
            return int(val) if val.isdigit() else default

        sets = safe_int(self.sets_entry)
        reps = safe_int(self.reps_entry)
        weight_str = self.weight_entry.get().strip()
        weight = weight_str if weight_str and weight_str != "Kg" else "0"

        self.workouts.append({
            'date': date.today().strftime('%Y-%m-%d'),
            'exercise': exercise, 'sets': sets, 'reps': reps, 'weight': weight,
        })
        save_json(WORKOUTS_FILE, self.workouts)

        self.exercise_entry.delete(0, tk.END)
        self.sets_entry.delete(0, tk.END)
        self.reps_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self._refresh_list()

    def _delete_selected(self):
        selection = self.workout_list.curselection()
        if not selection:
            return
        del self.workouts[selection[0]]
        save_json(WORKOUTS_FILE, self.workouts)
        self._refresh_list()

    def _refresh_list(self):
        self.workout_list.delete(0, tk.END)
        for w in reversed(self.workouts):
            self.workout_list.insert(
                tk.END,
                f"{w['date']} | {w['exercise']} | {w['sets']}x{w['reps']} | {w['weight']}kg"
            )
        self._calculate_streak()

    def _calculate_streak(self):
        """Ketma-ket necha kun mashq qilinganini hisoblaydi"""
        if not self.workouts:
            self.streak_label.config(text="Hali mashq yo'q - boshlaymiz! 💪")
            return

        unique_dates = sorted(set(w['date'] for w in self.workouts), reverse=True)
        streak = 1
        today = date.today()

        try:
            last_date = datetime.strptime(unique_dates[0], '%Y-%m-%d').date()
            if (today - last_date).days > 1:
                self.streak_label.config(text=f"Jami mashq kunlari: {len(unique_dates)} | Streak uzilgan")
                return

            for i in range(len(unique_dates) - 1):
                d1 = datetime.strptime(unique_dates[i], '%Y-%m-%d').date()
                d2 = datetime.strptime(unique_dates[i + 1], '%Y-%m-%d').date()
                if (d1 - d2).days == 1:
                    streak += 1
                else:
                    break

            self.streak_label.config(text=f"🔥 {streak} kunlik streak! Jami: {len(unique_dates)} kun")
        except Exception:
            self.streak_label.config(text=f"Jami mashq kunlari: {len(unique_dates)}")


# ==========================================================
# ASOSIY ILOVA
# ==========================================================

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Musiqa + Kundalik + Fitness")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("420x750")
        self.root.minsize(320, 500)

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=BG_COLOR, borderwidth=0)
        style.configure('TNotebook.Tab', background=PANEL_BG, foreground=TEXT_COLOR,
                          padding=[10, 8], font=("Arial", 10))
        style.map('TNotebook.Tab', background=[('selected', BTN_COLOR)])

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#17212b", height=45)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🎵 📖 🏋️ Yordamchi", bg="#17212b", fg=TEXT_COLOR,
                  font=("Arial", 13, "bold")).pack(pady=10)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        notebook.add(MusicTab(notebook), text="🎵 Musiqa")
        notebook.add(DiaryTab(notebook), text="📖 Kundalik")
        notebook.add(FitnessTab(notebook), text="🏋️ Fitness")


# --- DASTUR ISHGA TUSHIRISH ---
if __name__ == '__main__':
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
