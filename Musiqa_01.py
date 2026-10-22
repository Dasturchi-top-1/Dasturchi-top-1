# ==========================================================
# LOYIHA: TARMOQ + AUDIO + ASCII-ART + GRAFIK/STATISTIKA
# PLATFORMA: Android (Pydroid 3 / Termux)
# ==========================================================

import os
import math
import wave
import socket
import subprocess
import threading
import statistics
import concurrent.futures
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Rang sxemasi
BG_COLOR = "#0e1621"
PANEL_BG = "#1c2733"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#8a9aa9"
BTN_COLOR = "#4ea1f3"
BTN_GREEN = "#2ea043"
BTN_RED = "#e0245e"
INPUT_BG = "#242f3d"

OUTPUT_FOLDER = "AI/outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def styled_button(parent, text, command, color=BTN_COLOR, **kwargs):
    return tk.Button(
        parent, text=text, command=command, bg=color, fg="white",
        font=("Arial", 10, "bold"), relief="flat", cursor="hand2", **kwargs
    )


# ==========================================================
# 1-BO'LIM: TARMOQDAGI QURILMALARNI SKANERLASH
# ==========================================================

class NetworkScannerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="🔌 Tarmoq Qurilmalari Skaneri", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(
            self, text="Wi-Fi tarmog'ingizdagi faol qurilmalarni topadi\n(faqat shu Wi-Fi'ga ulangan bo'lishingiz kerak)",
            bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9), justify="center",
        ).pack(pady=4)

        styled_button(self, "🔍 Skanerlashni boshlash", self._start_scan, color=BTN_GREEN).pack(pady=8)

        self.status = tk.Label(self, text="", bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9))
        self.status.pack(pady=2)

        self.progress = ttk.Progressbar(self, mode='determinate', length=300)
        self.progress.pack(pady=6)

        self.result_box = scrolledtext.ScrolledText(
            self, bg=PANEL_BG, fg=TEXT_COLOR, font=("Courier New", 10), wrap="word", height=14
        )
        self.result_box.pack(fill="both", expand=True, padx=15, pady=8)

    def _get_local_subnet(self):
        """O'zining lokal IP manzilini aniqlab, tarmoq prefiksini qaytaradi"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            prefix = '.'.join(local_ip.split('.')[:3])
            return prefix, local_ip
        except Exception:
            return None, None

    def _start_scan(self):
        self.result_box.delete("1.0", tk.END)
        self.status.config(text="⏳ Tarmoq aniqlanmoqda...")
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _ping_host(self, ip):
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                capture_output=True, text=True, timeout=2,
            )
            if result.returncode == 0:
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except Exception:
                    hostname = "Noma'lum"
                return (ip, hostname)
        except Exception:
            pass
        return None

    def _scan_thread(self):
        prefix, local_ip = self._get_local_subnet()
        if not prefix:
            self.after(0, lambda: self.status.config(text="❌ Tarmoq aniqlanmadi. Wi-Fi'ga ulanganingizni tekshiring."))
            return

        self.after(0, lambda: self.status.config(text=f"🔍 {prefix}.0/24 tarmog'i skanerlanmoqda..."))
        self.after(0, lambda: self.result_box.insert(tk.END, f"Sizning IP: {local_ip}\nTarmoq: {prefix}.0/24\n\n"))

        found_devices = []
        total = 254

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(self._ping_host, f"{prefix}.{i}"): i for i in range(1, 255)}
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                self.after(0, lambda c=completed: self.progress.config(value=(c / total) * 100))
                result = future.result()
                if result:
                    found_devices.append(result)
                    ip, hostname = result
                    self.after(0, lambda i=ip, h=hostname: self.result_box.insert(
                        tk.END, f"🟢 {i:15s} -> {h}\n"
                    ))

        self.after(0, lambda: self.status.config(
            text=f"✅ Tugadi! {len(found_devices)} ta faol qurilma topildi."
        ))


# ==========================================================
# 2-BO'LIM: AUDIO SHOVQIN TOZALOVCHI
# ==========================================================

class AudioNoiseTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self.selected_file = None
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="🔇 Audio Shovqin Tozalovchi", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=10)

        if not NUMPY_AVAILABLE:
            tk.Label(
                self, text="⚠️  numpy o'rnatilmagan.\nTerminal'da: pip install numpy",
                bg=BG_COLOR, fg="#e0245e", font=("Arial", 10),
            ).pack(pady=20)
            return

        tk.Label(
            self, text="Faqat .wav formatidagi fayllar qo'llab-quvvatlanadi.\n"
                        "Past chastotali doimiy shovqin (gum/hum)ni kamaytiradi.",
            bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9), justify="center",
        ).pack(pady=6)

        styled_button(self, "🎵 Audio fayl tanlash (.wav)", self._pick_file, color=BTN_GREEN).pack(pady=6)

        self.file_label = tk.Label(self, text="Fayl tanlanmagan", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                                     font=("Arial", 9))
        self.file_label.pack(pady=2)

        styled_button(self, "🧹 Shovqinni tozalash", self._process, color=BTN_COLOR).pack(pady=10)

        self.status = tk.Label(self, text="", bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9),
                                 wraplength=340)
        self.status.pack(pady=6)

    def _pick_file(self):
        path = filedialog.askopenfilename(filetypes=[("WAV fayllari", "*.wav")])
        if path:
            self.selected_file = path
            self.file_label.config(text=os.path.basename(path))

    def _process(self):
        if not self.selected_file:
            self.status.config(text="⚠️  Avval audio fayl tanlang!")
            return
        self.status.config(text="⏳ Qayta ishlanmoqda...")
        threading.Thread(target=self._process_thread, daemon=True).start()

    def _process_thread(self):
        try:
            with wave.open(self.selected_file, 'rb') as wf:
                n_channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                raw_data = wf.readframes(n_frames)

            audio = np.frombuffer(raw_data, dtype=np.int16).astype(np.float64)

            # Oddiy yuqori-o'tkazuvchi filtr (high-pass) - past chastotali gum/shovqinni kamaytiradi
            fft_data = np.fft.rfft(audio)
            freqs = np.fft.rfftfreq(len(audio), d=1.0 / framerate)
            cutoff_hz = 100  # 100 Hz dan pastini kamaytiramiz
            fft_data[freqs < cutoff_hz] *= 0.1

            cleaned = np.fft.irfft(fft_data).astype(np.int16)

            output_path = os.path.join(OUTPUT_FOLDER, "cleaned_audio.wav")
            with wave.open(output_path, 'wb') as out_wf:
                out_wf.setnchannels(n_channels)
                out_wf.setsampwidth(sampwidth)
                out_wf.setframerate(framerate)
                out_wf.writeframes(cleaned.tobytes())

            self.after(0, lambda: self.status.config(
                text=f"✅ Tayyor! Saqlandi:\n{output_path}"
            ))
        except Exception as e:
            self.after(0, lambda: self.status.config(text=f"❌ Xato: {e}"))


# ==========================================================
# 3-BO'LIM: ASCII-ART GENERATOR
# ==========================================================

class AsciiArtTab(tk.Frame):
    ASCII_CHARS = "@%#*+=-:. "

    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="🖌️ ASCII-Art Generator", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=10)

        if not PIL_AVAILABLE:
            tk.Label(
                self, text="⚠️  Pillow o'rnatilmagan.\nTerminal'da: pip install Pillow",
                bg=BG_COLOR, fg="#e0245e", font=("Arial", 10),
            ).pack(pady=20)
            return

        width_frame = tk.Frame(self, bg=BG_COLOR)
        width_frame.pack(pady=4)
        tk.Label(width_frame, text="Kenglik (belgi):", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                  font=("Arial", 9)).pack(side="left", padx=4)
        self.width_entry = tk.Entry(width_frame, bg=INPUT_BG, fg=TEXT_COLOR, width=6)
        self.width_entry.insert(0, "80")
        self.width_entry.pack(side="left")

        styled_button(self, "🖼️ Rasm tanlash va aylantirish", self._pick_and_convert,
                       color=BTN_GREEN).pack(pady=8)

        self.status = tk.Label(self, text="", bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9))
        self.status.pack(pady=2)

        self.ascii_output = scrolledtext.ScrolledText(
            self, bg="#000000", fg="#00ff00", font=("Courier New", 4), wrap="none", height=20
        )
        self.ascii_output.pack(fill="both", expand=True, padx=10, pady=6)

        styled_button(self, "💾 Matn sifatida saqlash", self._save_ascii).pack(pady=6)

    def _pick_and_convert(self):
        path = filedialog.askopenfilename(filetypes=[("Rasm fayllari", "*.jpg *.jpeg *.png *.webp")])
        if not path:
            return

        try:
            width = int(self.width_entry.get().strip() or "80")
        except ValueError:
            width = 80

        try:
            image = Image.open(path).convert('L')  # kulrang shkalaga aylantirish
            aspect_ratio = image.height / image.width
            height = int(width * aspect_ratio * 0.55)  # belgilar bo'yi kengroq, tuzatamiz
            image = image.resize((width, height))

            pixels = image.getdata()
            ascii_str = ''.join(
                self.ASCII_CHARS[pixel * (len(self.ASCII_CHARS) - 1) // 255] for pixel in pixels
            )

            lines = [ascii_str[i:i + width] for i in range(0, len(ascii_str), width)]
            result = '\n'.join(lines)

            self.ascii_output.delete("1.0", tk.END)
            self.ascii_output.insert("1.0", result)
            self.last_ascii = result
            self.status.config(text="✅ ASCII-art yaratildi!")

        except Exception as e:
            self.status.config(text=f"❌ Xato: {e}")

    def _save_ascii(self):
        if not hasattr(self, 'last_ascii'):
            self.status.config(text="⚠️  Avval rasm aylantiring!")
            return
        path = os.path.join(OUTPUT_FOLDER, "ascii_art.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.last_ascii)
        self.status.config(text=f"💾 Saqlandi: {path}")


# ==========================================================
# 4-BO'LIM: GRAFIK KALKULYATOR + STATISTIKA
# ==========================================================

SAFE_MATH = {name: getattr(math, name) for name in dir(math) if not name.startswith('_')}
SAFE_MATH.update({'abs': abs})


class GraphStatsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        graph_frame = tk.Frame(notebook, bg=BG_COLOR)
        stats_frame = tk.Frame(notebook, bg=BG_COLOR)
        notebook.add(graph_frame, text="📈 Grafik")
        notebook.add(stats_frame, text="🔢 Statistika")

        self._build_graph_ui(graph_frame)
        self._build_stats_ui(stats_frame)

    # --- GRAFIK QISM ---
    def _build_graph_ui(self, parent):
        tk.Label(parent, text="Funksiya kiriting (masalan: x**2, sin(x), x**2 - 3*x + 2):",
                  bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9), wraplength=340).pack(pady=(10, 4))

        self.func_entry = tk.Entry(parent, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 12))
        self.func_entry.insert(0, "x**2")
        self.func_entry.pack(fill="x", padx=15, pady=4)

        styled_button(parent, "📈 Chizish", self._plot_function, color=BTN_GREEN).pack(pady=6)

        self.graph_status = tk.Label(parent, text="", bg=BG_COLOR, fg="#e0245e", font=("Arial", 9))
        self.graph_status.pack()

        self.graph_canvas = tk.Canvas(parent, bg=PANEL_BG, height=300, highlightthickness=0)
        self.graph_canvas.pack(fill="both", expand=True, padx=10, pady=8)

    def _plot_function(self):
        expr = self.func_entry.get().strip()
        self.graph_canvas.delete("all")
        self.graph_status.config(text="")

        w = self.graph_canvas.winfo_width() or 340
        h = self.graph_canvas.winfo_height() or 300
        x_min, x_max = -10, 10

        points = []
        try:
            for px in range(0, w):
                x_val = x_min + (px / w) * (x_max - x_min)
                context = dict(SAFE_MATH)
                context['x'] = x_val
                y_val = eval(expr, {"__builtins__": {}}, context)
                points.append((px, x_val, y_val))
        except Exception as e:
            self.graph_status.config(text=f"❌ Xato funksiyada: {e}")
            return

        y_values = [p[2] for p in points if isinstance(p[2], (int, float)) and not math.isnan(p[2]) and not math.isinf(p[2])]
        if not y_values:
            self.graph_status.config(text="❌ Chizish uchun mos qiymatlar topilmadi")
            return

        y_min, y_max = min(y_values), max(y_values)
        if y_min == y_max:
            y_min -= 1
            y_max += 1
        y_range = y_max - y_min

        # O'q chizig'i (y=0)
        if y_min <= 0 <= y_max:
            zero_y = h - ((0 - y_min) / y_range) * h
            self.graph_canvas.create_line(0, zero_y, w, zero_y, fill="#4a5568", dash=(3, 3))

        prev_point = None
        for px, x_val, y_val in points:
            if not isinstance(y_val, (int, float)) or math.isnan(y_val) or math.isinf(y_val):
                prev_point = None
                continue
            py = h - ((y_val - y_min) / y_range) * h
            if prev_point:
                self.graph_canvas.create_line(prev_point[0], prev_point[1], px, py, fill="#00ffcc", width=2)
            prev_point = (px, py)

        self.graph_status.config(text=f"✅ y_min={y_min:.2f}, y_max={y_max:.2f}", fg=BTN_GREEN)

    # --- STATISTIKA QISM ---
    def _build_stats_ui(self, parent):
        tk.Label(parent, text="Raqamlarni vergul bilan ajratib kiriting:\n(masalan: 5, 8, 3, 9, 2, 7)",
                  bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9), justify="center").pack(pady=(15, 6))

        self.stats_entry = tk.Text(parent, height=3, bg=INPUT_BG, fg=TEXT_COLOR, font=("Arial", 11), wrap="word")
        self.stats_entry.pack(fill="x", padx=15, pady=4)

        styled_button(parent, "🔢 Hisoblash", self._calculate_stats, color=BTN_GREEN).pack(pady=8)

        self.stats_result = scrolledtext.ScrolledText(
            parent, bg=PANEL_BG, fg=TEXT_COLOR, font=("Courier New", 11), wrap="word", height=10
        )
        self.stats_result.pack(fill="both", expand=True, padx=15, pady=8)

    def _calculate_stats(self):
        raw = self.stats_entry.get("1.0", tk.END).strip()
        self.stats_result.delete("1.0", tk.END)

        try:
            numbers = [float(n.strip()) for n in raw.split(',') if n.strip()]
        except ValueError:
            self.stats_result.insert("1.0", "❌ Xato: faqat raqamlarni vergul bilan ajratib kiriting")
            return

        if not numbers:
            self.stats_result.insert("1.0", "⚠️  Avval raqamlar kiriting")
            return

        lines = [
            f"Sonlar soni:        {len(numbers)}",
            f"Yig'indi:            {sum(numbers):.4f}",
            f"O'rtacha (mean):     {statistics.mean(numbers):.4f}",
            f"Median:              {statistics.median(numbers):.4f}",
            f"Minimum:             {min(numbers):.4f}",
            f"Maksimum:            {max(numbers):.4f}",
        ]

        if len(numbers) > 1:
            lines.append(f"Standart chetlanish: {statistics.stdev(numbers):.4f}")
            lines.append(f"Dispersiya:          {statistics.variance(numbers):.4f}")

        try:
            mode_val = statistics.mode(numbers)
            lines.append(f"Moda:                {mode_val}")
        except statistics.StatisticsError:
            lines.append("Moda:                Aniq moda yo'q")

        self.stats_result.insert("1.0", "\n".join(lines))


# ==========================================================
# ASOSIY ILOVA
# ==========================================================

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarmoq + Audio + ASCII + Grafik")
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
                          padding=[6, 6], font=("Arial", 8))
        style.map('TNotebook.Tab', background=[('selected', BTN_COLOR)])

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#17212b", height=45)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🛠️ Ko'p Funksiyali Vosita", bg="#17212b", fg=TEXT_COLOR,
                  font=("Arial", 12, "bold")).pack(pady=10)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        notebook.add(NetworkScannerTab(notebook), text="🔌 Tarmoq")
        notebook.add(AudioNoiseTab(notebook), text="🔇 Audio")
        notebook.add(AsciiArtTab(notebook), text="🖌️ ASCII")
        notebook.add(GraphStatsTab(notebook), text="📊 Grafik")


# --- DASTUR ISHGA TUSHIRISH ---
if __name__ == '__main__':
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
