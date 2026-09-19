# ==========================================================
# LOYIHA: CYBER SNAKE - CYBERPUNK USLUBIDAGI ILON O'YINI
# PLATFORMA: Android (Pydroid 3) - tkinter tayyor keladi
# ==========================================================

import random
import tkinter as tk

# O'yin sozlamalari
GRID_SIZE = 20
GRID_WIDTH = 16
GRID_HEIGHT = 20
GAME_SPEED = 130  # millisekund (kichikroq = tezroq)

# Cyberpunk rang sxemasi
BG_COLOR = "#0a0014"
GRID_COLOR = "#1a0a2e"
SNAKE_HEAD = "#00ffcc"
SNAKE_BODY = "#00b894"
FOOD_COLOR = "#ff2e63"
NEON_PINK = "#ff2e63"
NEON_CYAN = "#00ffcc"
NEON_PURPLE = "#b967ff"
TEXT_COLOR = "#e0e0ff"
BTN_BG = "#1a0a2e"


class CyberSnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CYBER SNAKE")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self._build_ui()
        self._reset_game()

    def _build_ui(self):
        # Sarlavha - neon effekt uchun ikki qatlamli matn
        title_frame = tk.Frame(self.root, bg=BG_COLOR)
        title_frame.pack(pady=(15, 5))
        tk.Label(
            title_frame, text="⚡ CYBER SNAKE ⚡", bg=BG_COLOR, fg=NEON_CYAN,
            font=("Courier New", 20, "bold"),
        ).pack()

        # Ball ko'rsatkichi
        self.score_label = tk.Label(
            self.root, text="SCORE: 0", bg=BG_COLOR, fg=NEON_PINK,
            font=("Courier New", 14, "bold"),
        )
        self.score_label.pack(pady=4)

        # O'yin maydoni (Canvas)
        canvas_width = GRID_WIDTH * GRID_SIZE
        canvas_height = GRID_HEIGHT * GRID_SIZE
        self.canvas = tk.Canvas(
            self.root, width=canvas_width, height=canvas_height,
            bg=GRID_COLOR, highlightthickness=2, highlightbackground=NEON_PURPLE,
        )
        self.canvas.pack(pady=8)

        # Boshqaruv tugmalari (teginish uchun - D-pad uslubida)
        control_frame = tk.Frame(self.root, bg=BG_COLOR)
        control_frame.pack(pady=10)

        btn_style = {
            'bg': BTN_BG, 'fg': NEON_CYAN, 'font': ("Arial", 16, "bold"),
            'width': 4, 'height': 1, 'relief': 'flat', 'cursor': 'hand2',
            'activebackground': NEON_PURPLE,
        }

        tk.Button(control_frame, text="↑", command=lambda: self._change_direction(0, -1),
                   **btn_style).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(control_frame, text="←", command=lambda: self._change_direction(-1, 0),
                   **btn_style).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(control_frame, text="↓", command=lambda: self._change_direction(0, 1),
                   **btn_style).grid(row=1, column=1, padx=3, pady=3)
        tk.Button(control_frame, text="→", command=lambda: self._change_direction(1, 0),
                   **btn_style).grid(row=1, column=2, padx=3, pady=3)

        # Qayta boshlash tugmasi
        self.restart_btn = tk.Button(
            self.root, text="🔄 QAYTA BOSHLASH", command=self._reset_game,
            bg=NEON_PINK, fg="white", font=("Courier New", 11, "bold"),
            relief="flat", cursor="hand2",
        )
        self.restart_btn.pack(pady=8)

        # Klaviatura orqali ham boshqarish (agar tashqi klaviatura ulangan bo'lsa)
        self.root.bind("<Up>", lambda e: self._change_direction(0, -1))
        self.root.bind("<Down>", lambda e: self._change_direction(0, 1))
        self.root.bind("<Left>", lambda e: self._change_direction(-1, 0))
        self.root.bind("<Right>", lambda e: self._change_direction(1, 0))

    def _reset_game(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.game_over = False
        self._spawn_food()
        self.score_label.config(text="SCORE: 0")
        self._game_loop()

    def _spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                self.food = pos
                break

    def _change_direction(self, dx, dy):
        # Ilon o'ziga qarshi yo'nalishga burila olmaydi
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_direction = (dx, dy)

    def _game_loop(self):
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Devorga yoki o'ziga urilishni tekshirish
        if (
            new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in self.snake
        ):
            self._show_game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.score_label.config(text=f"SCORE: {self.score}")
            self._spawn_food()
        else:
            self.snake.pop()

        self._draw()
        self.root.after(GAME_SPEED, self._game_loop)

    def _draw(self):
        self.canvas.delete("all")

        # Grid chiziqlari (nozik, cyberpunk fon effekti uchun)
        for x in range(0, GRID_WIDTH * GRID_SIZE, GRID_SIZE):
            self.canvas.create_line(x, 0, x, GRID_HEIGHT * GRID_SIZE, fill="#150a28")
        for y in range(0, GRID_HEIGHT * GRID_SIZE, GRID_SIZE):
            self.canvas.create_line(0, y, GRID_WIDTH * GRID_SIZE, y, fill="#150a28")

        # Ilonni chizish (bosh - yorqinroq, tana - xiraroq neon)
        for i, (x, y) in enumerate(self.snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            self.canvas.create_rectangle(
                x * GRID_SIZE + 1, y * GRID_SIZE + 1,
                (x + 1) * GRID_SIZE - 1, (y + 1) * GRID_SIZE - 1,
                fill=color, outline=NEON_CYAN if i == 0 else "",
            )

        # Ovqatni chizish (aylana, neon pushti)
        fx, fy = self.food
        self.canvas.create_oval(
            fx * GRID_SIZE + 3, fy * GRID_SIZE + 3,
            (fx + 1) * GRID_SIZE - 3, (fy + 1) * GRID_SIZE - 3,
            fill=FOOD_COLOR, outline=NEON_PINK,
        )

    def _show_game_over(self):
        self.game_over = True
        self.canvas.create_rectangle(
            0, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE,
            fill=BG_COLOR, stipple="gray50",
        )
        self.canvas.create_text(
            GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2 - 20,
            text="GAME OVER", fill=NEON_PINK, font=("Courier New", 22, "bold"),
        )
        self.canvas.create_text(
            GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2 + 15,
            text=f"Yakuniy ball: {self.score}", fill=NEON_CYAN, font=("Courier New", 13),
        )


# --- DASTUR ISHGA TUSHIRISH ---
if __name__ == '__main__':
    root = tk.Tk()
    game = CyberSnakeGame(root)
    root.mainloop()
