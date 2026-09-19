# ==========================================================
# LOYIHA: MINI FAYL-SERVER + DASTURCHI VOSITALARI
# PLATFORMA: Android (Pydroid 3 / Termux)
# BO'LIMLAR: Wi-Fi fayl server, JSON/XML formatlovchi, Regex sinovchisi
# ==========================================================

import os
import re
import json
import socket
import threading
import xml.dom.minidom
import http.server
import socketserver
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

# Rang sxemasi
BG_COLOR = "#0e1621"
PANEL_BG = "#1c2733"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#8a9aa9"
BTN_COLOR = "#4ea1f3"
BTN_GREEN = "#2ea043"
BTN_RED = "#e0245e"
INPUT_BG = "#242f3d"


def styled_button(parent, text, command, color=BTN_COLOR, **kwargs):
    return tk.Button(
        parent, text=text, command=command, bg=color, fg="white",
        font=("Arial", 10, "bold"), relief="flat", cursor="hand2", **kwargs
    )


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    """allow_reuse_address ni SERVER YARATILISHIDAN OLDIN sozlaydi -
    shunda 'Address already in use' xatosi chiqmaydi, chunki portni
    band qilish (bind) paytida SO_REUSEADDR allaqachon yoqilgan bo'ladi"""
    allow_reuse_address = True


# ==========================================================
# 1-BO'LIM: MINI FAYL-SERVER (Wi-Fi orqali)
# ==========================================================

class FileServerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self.server = None
        self.server_thread = None
        self.selected_folder = os.path.expanduser("~")
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="📡 Mini Fayl-Server", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(
            self, text="Telefon fayllaringizni Wi-Fi orqali\nkompyuter/boshqa qurilmadan ko'rish",
            bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9), justify="center",
        ).pack(pady=4)

        styled_button(self, "📁 Papka tanlash", self._pick_folder).pack(pady=6)

        self.folder_label = tk.Label(self, text=self.selected_folder, bg=BG_COLOR, fg=SUBTEXT_COLOR,
                                       font=("Arial", 8), wraplength=340)
        self.folder_label.pack(pady=2)

        self.toggle_btn = styled_button(self, "▶️ Serverni ishga tushirish", self._toggle_server, color=BTN_GREEN)
        self.toggle_btn.pack(pady=10)

        self.status_label = tk.Label(self, text="⚪ Server o'chirilgan", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                                       font=("Arial", 10, "bold"))
        self.status_label.pack(pady=4)

        self.address_box = tk.Text(
            self, height=2, bg=PANEL_BG, fg=BTN_COLOR, font=("Courier New", 12, "bold"),
            relief="flat", wrap="word",
        )
        self.address_box.pack(fill="x", padx=15, pady=8)
        self.address_box.config(state="disabled")

        tk.Label(
            self, text="⚠️ Shu manzilni kompyuter/telefon brauzerida oching\n"
                        "(faqat bir xil Wi-Fi tarmog'ida bo'lganlar kira oladi)",
            bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 8), justify="center",
        ).pack(pady=6)

    def _pick_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=folder)

    def _toggle_server(self):
        if self.server is None:
            self._start_server()
        else:
            self._stop_server()

    def _start_server(self):
        try:
            handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
                *args, directory=self.selected_folder, **kwargs
            )
            self.server = ReusableTCPServer(("0.0.0.0", 8000), handler)

            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()

            local_ip = get_local_ip()
            address = f"http://{local_ip}:8000"

            self.address_box.config(state="normal")
            self.address_box.delete("1.0", tk.END)
            self.address_box.insert("1.0", address)
            self.address_box.config(state="disabled")

            self.status_label.config(text="🟢 Server ishlamoqda", fg=BTN_GREEN)
            self.toggle_btn.config(text="⏹️ Serverni to'xtatish", bg=BTN_RED)

        except Exception as e:
            self.status_label.config(text=f"❌ Xato: {e}", fg=BTN_RED)

    def _stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

        self.status_label.config(text="⚪ Server o'chirilgan", fg=SUBTEXT_COLOR)
        self.toggle_btn.config(text="▶️ Serverni ishga tushirish", bg=BTN_GREEN)
        self.address_box.config(state="normal")
        self.address_box.delete("1.0", tk.END)
        self.address_box.config(state="disabled")


# ==========================================================
# 2-BO'LIM: JSON/XML FORMATLOVCHI
# ==========================================================

class FormatterTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="🔧 JSON/XML Formatlovchi", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=10)

        format_frame = tk.Frame(self, bg=BG_COLOR)
        format_frame.pack(pady=4)

        self.format_type = tk.StringVar(value="JSON")
        tk.Radiobutton(format_frame, text="JSON", variable=self.format_type, value="JSON",
                        bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=PANEL_BG,
                        activebackground=BG_COLOR, activeforeground=TEXT_COLOR).pack(side="left", padx=8)
        tk.Radiobutton(format_frame, text="XML", variable=self.format_type, value="XML",
                        bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=PANEL_BG,
                        activebackground=BG_COLOR, activeforeground=TEXT_COLOR).pack(side="left", padx=8)

        tk.Label(self, text="Chalkash kodni bu yerga joylashtiring:", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                  font=("Arial", 9)).pack(anchor="w", padx=15)

        self.input_box = scrolledtext.ScrolledText(
            self, bg=INPUT_BG, fg=TEXT_COLOR, font=("Courier New", 10), wrap="word", height=8
        )
        self.input_box.pack(fill="both", expand=True, padx=15, pady=4)

        styled_button(self, "✨ Formatlash", self._format, color=BTN_GREEN).pack(pady=6)

        self.status = tk.Label(self, text="", bg=BG_COLOR, fg=BTN_RED, font=("Arial", 9))
        self.status.pack()

        tk.Label(self, text="Natija:", bg=BG_COLOR, fg=SUBTEXT_COLOR, font=("Arial", 9)).pack(anchor="w", padx=15)

        self.output_box = scrolledtext.ScrolledText(
            self, bg=PANEL_BG, fg=TEXT_COLOR, font=("Courier New", 10), wrap="word", height=8
        )
        self.output_box.pack(fill="both", expand=True, padx=15, pady=4)

        styled_button(self, "📋 Natijani nusxalash", self._copy).pack(pady=6)

    def _format(self):
        raw = self.input_box.get("1.0", tk.END).strip()
        self.output_box.delete("1.0", tk.END)
        self.status.config(text="")

        if not raw:
            self.status.config(text="⚠️  Avval kod joylashtiring!")
            return

        try:
            if self.format_type.get() == "JSON":
                parsed = json.loads(raw)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            else:
                dom = xml.dom.minidom.parseString(raw)
                formatted = dom.toprettyxml(indent="  ")
                # Bo'sh qatorlarni tozalaymiz
                formatted = '\n'.join(line for line in formatted.split('\n') if line.strip())

            self.output_box.insert("1.0", formatted)
            self.status.config(text="✅ To'g'ri formatlangan!", fg=BTN_GREEN)

        except Exception as e:
            self.status.config(text=f"❌ Xato: {e}", fg=BTN_RED)

    def _copy(self):
        text = self.output_box.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
            self.status.config(text="📋 Nusxalandi!", fg=BTN_GREEN)


# ==========================================================
# 3-BO'LIM: REGEX SINOVCHISI
# ==========================================================

class RegexTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="🔍 Regex Sinovchisi", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Regex naqshi (pattern):", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                  font=("Arial", 9)).pack(anchor="w", padx=15)

        self.pattern_entry = tk.Entry(self, bg=INPUT_BG, fg=TEXT_COLOR, font=("Courier New", 11))
        self.pattern_entry.insert(0, r"\d+")
        self.pattern_entry.pack(fill="x", padx=15, pady=4)
        self.pattern_entry.bind("<KeyRelease>", lambda e: self._test())

        tk.Label(self, text="Sinov matni:", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                  font=("Arial", 9)).pack(anchor="w", padx=15, pady=(8, 0))

        self.test_text = scrolledtext.ScrolledText(
            self, bg=INPUT_BG, fg=TEXT_COLOR, font=("Courier New", 10), wrap="word", height=6
        )
        self.test_text.pack(fill="both", expand=True, padx=15, pady=4)
        self.test_text.insert("1.0", "Mening telefon raqamim: 998901234567, yoshim 25.")
        self.test_text.bind("<KeyRelease>", lambda e: self._test())

        styled_button(self, "🔍 Tekshirish", self._test, color=BTN_GREEN).pack(pady=6)

        self.match_count_label = tk.Label(self, text="", bg=BG_COLOR, fg=BTN_COLOR,
                                            font=("Arial", 10, "bold"))
        self.match_count_label.pack()

        tk.Label(self, text="Topilgan mosliklar:", bg=BG_COLOR, fg=SUBTEXT_COLOR,
                  font=("Arial", 9)).pack(anchor="w", padx=15, pady=(6, 0))

        self.results_box = scrolledtext.ScrolledText(
            self, bg=PANEL_BG, fg=TEXT_COLOR, font=("Courier New", 10), wrap="word", height=6
        )
        self.results_box.pack(fill="both", expand=True, padx=15, pady=4)

    def _test(self, event=None):
        pattern = self.pattern_entry.get()
        text = self.test_text.get("1.0", tk.END)
        self.results_box.delete("1.0", tk.END)

        if not pattern:
            self.match_count_label.config(text="")
            return

        try:
            matches = list(re.finditer(pattern, text))
            self.match_count_label.config(text=f"✅ {len(matches)} ta moslik topildi", fg=BTN_GREEN)

            for i, m in enumerate(matches, 1):
                self.results_box.insert(
                    tk.END, f"[{i}] '{m.group()}'  (pozitsiya: {m.start()}-{m.end()})\n"
                )
        except re.error as e:
            self.match_count_label.config(text=f"❌ Regex xatosi: {e}", fg=BTN_RED)


# ==========================================================
# ASOSIY ILOVA
# ==========================================================

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fayl-server + Dasturchi vositalari")
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
                          padding=[8, 6], font=("Arial", 9))
        style.map('TNotebook.Tab', background=[('selected', BTN_COLOR)])

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#17212b", height=45)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🛠️ Fayl-server + Dev Vositalari", bg="#17212b", fg=TEXT_COLOR,
                  font=("Arial", 12, "bold")).pack(pady=10)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        notebook.add(FileServerTab(notebook), text="📡 Server")
        notebook.add(FormatterTab(notebook), text="🔧 Formatlash")
        notebook.add(RegexTab(notebook), text="🔍 Regex")


# --- DASTUR ISHGA TUSHIRISH ---
if __name__ == '__main__':
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
