# ==========================================================
# LOYIHA: GAME OF LIFE + ZARRACHALAR FIZIKASI
# PLATFORMA: Android (Pydroid 3) - tkinter tayyor keladi
# ==========================================================

import random
import tkinter as tk
from tkinter import ttk

# Rang sxemasi
BG_COLOR = "#0e1621"
PANEL_BG = "#1c2733"
TEXT_COLOR = "#ffffff"
BTN_COLOR = "#4ea1f3"
BTN_GREEN = "#2ea043"
BTN_RED = "#e0245e"
CELL_ALIVE = "#00ffcc"
GRID_BG = "#0a0a15"


def styled_button(parent, text, command, color=BTN_COLOR, **kwargs):
    return tk.Button(
        parent, text=text, command=command, bg=color, fg="white",
        font=("Arial", 10, "bold"), relief="flat", cursor="hand2", **kwargs
    )


# ==========================================================
# 1-BO'LIM: CONWAY'S GAME OF LIFE
# ==========================================================

class GameOfLifeTab(tk.Frame):
    CELL_SIZE = 12
    COLS = 26
    ROWS = 28

    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self.grid = [[0] * self.COLS for _ in range(self.ROWS)]
        self.running = False
        self.generation = 0
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="🧬 Conway's Game of Life", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 13, "bold")).pack(pady=8)

        self.info_label = tk.Label(self, text="Avlod: 0 | Hujayralar: 0", bg=BG_COLOR,
                                     fg=CELL_ALIVE, font=("Arial", 10))
        self.info_label.pack(pady=2)

        self.canvas = tk.Canvas(
            self, width=self.COLS * self.CELL_SIZE, height=self.ROWS * self.CELL_SIZE,
            bg=GRID_BG, highlightthickness=1, highlightbackground=BTN_COLOR,
        )
        self.canvas.pack(pady=8)
        self.canvas.bind("<Button-1>", self._toggle_cell)
        self.canvas.bind("<B1-Motion>", self._toggle_cell)

        control_frame = tk.Frame(self, bg=BG_COLOR)
        control_frame.pack(pady=6)

        self.play_btn = styled_button(control_frame, "▶️ Boshlash", self._toggle_run, color=BTN_GREEN)
        self.play_btn.grid(row=0, column=0, padx=3)
        styled_button(control_frame, "🎲 Tasodifiy", self._randomize).grid(row=0, column=1, padx=3)
        styled_button(control_frame, "🗑️ Tozalash", self._clear, color=BTN_RED).grid(row=0, column=2, padx=3)

        tk.Label(self, text="👆 Katakchalarni bosib/tortib hujayra qo'ying",
                  bg=BG_COLOR, fg="#8a9aa9", font=("Arial", 8)).pack(pady=4)

        self._draw()

    def _toggle_cell(self, event):
        if self.running:
            return
        col = event.x // self.CELL_SIZE
        row = event.y // self.CELL_SIZE
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            self.grid[row][col] = 1
            self._draw()

    def _randomize(self):
        self.grid = [[random.choice([0, 0, 1]) for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.generation = 0
        self._draw()

    def _clear(self):
        self.running = False
        self.play_btn.config(text="▶️ Boshlash", bg=BTN_GREEN)
        self.grid = [[0] * self.COLS for _ in range(self.ROWS)]
        self.generation = 0
        self._draw()

    def _toggle_run(self):
        self.running = not self.running
        if self.running:
            self.play_btn.config(text="⏸️ To'xtatish", bg=BTN_RED)
            self._step_loop()
        else:
            self.play_btn.config(text="▶️ Boshlash", bg=BTN_GREEN)

    def _count_neighbors(self, row, col):
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.ROWS and 0 <= c < self.COLS:
                    count += self.grid[r][c]
        return count

    def _next_generation(self):
        new_grid = [[0] * self.COLS for _ in range(self.ROWS)]
        for r in range(self.ROWS):
            for c in range(self.COLS):
                alive = self.grid[r][c]
                neighbors = self._count_neighbors(r, c)
                if alive and neighbors in (2, 3):
                    new_grid[r][c] = 1
                elif not alive and neighbors == 3:
                    new_grid[r][c] = 1
        self.grid = new_grid
        self.generation += 1

    def _step_loop(self):
        if not self.running:
            return
        self._next_generation()
        self._draw()
        self.after(150, self._step_loop)

    def _draw(self):
        self.canvas.delete("all")
        alive_count = 0
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if self.grid[r][c]:
                    alive_count += 1
                    x1, y1 = c * self.CELL_SIZE, r * self.CELL_SIZE
                    x2, y2 = x1 + self.CELL_SIZE - 1, y1 + self.CELL_SIZE - 1
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=CELL_ALIVE, outline="")
        self.info_label.config(text=f"Avlod: {self.generation} | Hujayralar: {alive_count}")


# ==========================================================
# 2-BO'LIM: ZARRACHALAR FIZIKASI
# ==========================================================

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-6, -2)
        self.radius = random.uniform(3, 6)
        self.life = 1.0
        colors = ["#ff2e63", "#00ffcc", "#b967ff", "#f0a500", "#4ea1f3"]
        self.color = random.choice(colors)

    def update(self, width, height, gravity):
        self.vy += gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.012

        # Devor va poldan qaytish (bounce)
        if self.x - self.radius < 0 or self.x + self.radius > width:
            self.vx *= -0.7
            self.x = max(self.radius, min(width - self.radius, self.x))
        if self.y + self.radius > height:
            self.y = height - self.radius
            self.vy *= -0.6

    def is_alive(self):
        return self.life > 0


class ParticleTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        self.particles = []
        self.gravity = 0.25
        self.running = True
        self._build_ui()
        self._animate()

    def _build_ui(self):
        tk.Label(self, text="✨ Zarrachalar Fizikasi", bg=BG_COLOR, fg=TEXT_COLOR,
                  font=("Arial", 13, "bold")).pack(pady=8)

        self.count_label = tk.Label(self, text="Zarrachalar: 0", bg=BG_COLOR, fg="#b967ff",
                                      font=("Arial", 10))
        self.count_label.pack(pady=2)

        self.canvas = tk.Canvas(
            self, width=320, height=400, bg=GRID_BG,
            highlightthickness=1, highlightbackground=BTN_COLOR,
        )
        self.canvas.pack(pady=8)
        self.canvas.bind("<Button-1>", self._spawn_burst)
        self.canvas.bind("<B1-Motion>", self._spawn_burst)

        control_frame = tk.Frame(self, bg=BG_COLOR)
        control_frame.pack(pady=6)
        styled_button(control_frame, "🗑️ Tozalash", self._clear, color=BTN_RED).grid(row=0, column=0, padx=4)

        gravity_frame = tk.Frame(self, bg=BG_COLOR)
        gravity_frame.pack(pady=4)
        tk.Label(gravity_frame, text="Tortishish kuchi:", bg=BG_COLOR, fg="#8a9aa9",
                  font=("Arial", 8)).pack(side="left", padx=4)
        self.gravity_slider = tk.Scale(
            gravity_frame, from_=0, to=1, resolution=0.05, orient="horizontal",
            bg=BG_COLOR, fg=TEXT_COLOR, highlightthickness=0, length=150,
            command=self._update_gravity,
        )
        self.gravity_slider.set(0.25)
        self.gravity_slider.pack(side="left")

        tk.Label(self, text="👆 Ekranga teging - zarrachalar 'portlaydi'!",
                  bg=BG_COLOR, fg="#8a9aa9", font=("Arial", 8)).pack(pady=4)

    def _update_gravity(self, value):
        self.gravity = float(value)

    def _spawn_burst(self, event):
        for _ in range(8):
            if len(self.particles) < 300:  # cheklov - telefon sekinlashib qolmasligi uchun
                self.particles.append(Particle(event.x, event.y))

    def _clear(self):
        self.particles = []

    def _animate(self):
        width = self.canvas.winfo_width() or 320
        height = self.canvas.winfo_height() or 400

        for p in self.particles:
            p.update(width, height, self.gravity)
        self.particles = [p for p in self.particles if p.is_alive()]

        self.canvas.delete("all")
        for p in self.particles:
            alpha_size = p.radius * p.life
            self.canvas.create_oval(
                p.x - alpha_size, p.y - alpha_size, p.x + alpha_size, p.y + alpha_size,
                fill=p.color, outline="",
            )

        self.count_label.config(text=f"Zarrachalar: {len(self.particles)}")
        self.after(30, self._animate)


# ==========================================================
# ASOSIY ILOVA
# ==========================================================

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game of Life + Zarrachalar")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("360x680")
        self.root.minsize(320, 500)

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=BG_COLOR, borderwidth=0)
        style.configure('TNotebook.Tab', background=PANEL_BG, foreground=TEXT_COLOR,
                          padding=[12, 8], font=("Arial", 10))
        style.map('TNotebook.Tab', background=[('selected', BTN_COLOR)])

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#17212b", height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🔬 Simulyatsiyalar", bg="#17212b", fg=TEXT_COLOR,
                  font=("Arial", 12, "bold")).pack(pady=8)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        notebook.add(GameOfLifeTab(notebook), text="🧬 Game of Life")
        notebook.add(ParticleTab(notebook), text="✨ Zarrachalar")


# --- DASTUR ISHGA TUSHIRISH ---
if __name__ == '__main__':
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
