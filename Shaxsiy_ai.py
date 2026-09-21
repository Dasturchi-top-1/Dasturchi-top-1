#!/usr/bin/env python3
# ==========================================================
# AI CONTEXTUAL CLI SHELL - Intellektual Terminal Yordamchisi
# PLATFORMA: Termux / Pydroid 3
# REJIMLAR: 1) Terminal  2) Brauzer (Flask)
# ==========================================================
#
# O'RNATISH:
#   pip install requests flask
#
# API KALIT (muhit o'zgaruvchisi orqali, kodda emas):
#   export OPENROUTER_API_KEY="YOUR_API_KEY"
#
# ==========================================================

import os
import re
import subprocess
import requests

OPENROUTER_API_KEY = "YOUR_API_KEY"  # bu yerga openrouter.ai'dan olgan kalitingizni qo'ying
AI_MODEL = "deepseek/deepseek-v4-flash"
BROWSER_PASSWORD = "YOUR_PASSWORD"

# ==========================================================
# XAVFLI BUYRUQLAR FILTRI
# MUHIM: bu ro'yxat TO'LIQ emas va 100% himoya BERMAYDI -
# u faqat eng keng tarqalgan halokatli naqshlarni ushlaydi.
# Asosiy himoya - HAR DOIM tasdiqlashdan oldin buyruqni o'qish.
# ==========================================================

DANGEROUS_PATTERNS = [
    r'rm\s+-rf\s+/(\s|$)',
    r'rm\s+-rf\s+/\*',
    r'rm\s+-rf\s+~',
    r':\(\)\s*\{\s*:\|\s*:&\s*\}\s*;\s*:',   # fork bomb
    r'mkfs',
    r'dd\s+if=.*of=\s*/dev/',
    r'>\s*/dev/sd[a-z]',
    r'chmod\s+-R\s+777\s+/(\s|$)',
    r'wget\s+.*\|\s*(sh|bash)',
    r'curl\s+.*\|\s*(sh|bash)',
    r'>\s*/etc/passwd',
    r'\bshutdown\b',
    r'\breboot\b',
]


def is_dangerous(cmd):
    """Buyruqni ma'lum xavfli naqshlarga solishtiradi"""
    lower = cmd.lower()
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, lower):
            return True, pattern
    return False, None


# ==========================================================
# AI ORQALI BUYRUQ SHAKLLANTIRISH
# ==========================================================

SYSTEM_PROMPT = (
    "Sen Termux/Linux uchun buyruq generatorisan. Foydalanuvchi so'roviga mos "
    "ANIQ BITTA bash buyrug'ini qaytar. FAQAT buyruqning o'zini yoz - hech qanday "
    "tushuntirish, hech qanday markdown belgisi (```), hech qanday qo'shimcha matn."
)


def extract_command(text):
    """Agar AI kodni ```...``` ichida qaytarsa, tozalab oladi"""
    match = re.search(r'```(?:bash|sh)?\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip().split('\n')[0].strip()


def ask_ai_for_command(user_request):
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "SIZNING_API_KALITINGIZ":
        return None, "Avval kod ichida OPENROUTER_API_KEY ni o'z kalitingizga almashtiring."

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_request},
                ],
            },
            timeout=40,
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        return extract_command(raw), None
    except Exception as e:
        return None, str(e)


def run_command(cmd):
    """Buyruqni bajaradi - faqat tasdiqlangandan keyin chaqiriladi"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        output = result.stdout
        if result.returncode != 0:
            output += f"\n--- XATO (kod {result.returncode}) ---\n{result.stderr}"
        return output if output.strip() else "(Chiqish bo'sh)"
    except subprocess.TimeoutExpired:
        return "Vaqt tugadi (60 soniyadan oshdi) - buyruq to'xtatildi."
    except Exception as e:
        return f"Bajarishda xato: {e}"


# ==========================================================
# 1-REJIM: TERMINAL
# ==========================================================

def terminal_mode():
    print("=" * 55)
    print("  AI CONTEXTUAL CLI SHELL (TERMINAL REJIM)")
    print("=" * 55)
    print("So'rovingizni yozing (masalan: 'joriy papkadagi eng katta")
    print("5 ta faylni ko'rsat'). Chiqish uchun 'exit'.\n")

    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "SIZNING_API_KALITINGIZ":
        print("DIQQAT: Kod ichida OPENROUTER_API_KEY hali sozlanmagan!\n")

    while True:
        try:
            user_input = input("So'rov> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Xayr, jigarim!")
            break

        print("[AI buyruq yozmoqda...]")
        cmd, error = ask_ai_for_command(user_input)

        if error:
            print(f"Xato: {error}\n")
            continue

        dangerous, pattern = is_dangerous(cmd)

        print(f"\nTaklif qilingan buyruq:\n  {cmd}\n")
        if dangerous:
            print(f"OGOHLANTIRISH: bu buyruq xavfli naqshga mos keldi ({pattern})!")
            print("Juda ehtiyot bo'ling - bu HALOKATLI bo'lishi mumkin.\n")

        confirm = input("Ushbu buyruq bajarilsinmi? (y/n): ").strip().lower()

        if confirm == "y":
            print("\n[Bajarilmoqda...]\n")
            output = run_command(cmd)
            print(output)
        else:
            print("Bekor qilindi.")

        print()


# ==========================================================
# 2-REJIM: BRAUZER (Flask)
# ==========================================================

def browser_mode():
    from flask import Flask, request, session, redirect, url_for, render_template_string
    import hmac

    app = Flask(__name__)
    app.secret_key = "YOUR_SECRET_KEY"

    STYLE = """
    <style>
      body { background:#0a0a0a; color:#39ff14; font-family:Consolas,monospace; padding:20px; max-width:600px; margin:auto; }
      h1, h2 { color:#00c8ff; }
      input[type=text], input[type=password] { width:100%; padding:10px; margin:6px 0;
          background:#111; border:1px solid #00c8ff; border-radius:6px; color:#39ff14; }
      button { background:#39ff14; color:#0a0a0a; border:none; padding:10px 18px;
          border-radius:6px; font-weight:bold; cursor:pointer; margin-top:6px; }
      button.danger { background:#ff3355; color:white; }
      pre { background:#111; padding:12px; border-radius:6px; white-space:pre-wrap; word-break:break-all; }
      .warn { color:#ff3355; font-weight:bold; }
      .card { background:#111; border:1px solid #39ff14; border-radius:8px; padding:16px; margin:14px 0; }
    </style>
    """

    LOGIN_HTML = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{STYLE}</head>
    <body><h1>AI CLI Shell - Kirish</h1>
    <form method="POST">
      <input type="text" name="username" placeholder="Foydalanuvchi nomi" required>
      <input type="password" name="password" placeholder="Parol" required>
      <button type="submit">KIRISH</button>
    </form>
    {{% if error %}}<p class="warn">{{{{ error }}}}</p>{{% endif %}}
    </body></html>"""

    MAIN_HTML = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{STYLE}</head>
    <body>
    <h1>AI CONTEXTUAL CLI SHELL</h1>
    <p class="warn">Ogohlantirish: bu vosita joriy qurilmada haqiqiy buyruq bajaradi.
    Faqat ishonchli tarmoqda ishlating.</p>

    <div class="card">
      <h2>So'rov yozing</h2>
      <form method="POST" action="/generate">
        <input type="text" name="user_request" placeholder="masalan: eng katta 5 ta faylni korsat" required>
        <button type="submit">BUYRUQ YARATISH</button>
      </form>
    </div>

    {{% if cmd %}}
    <div class="card">
      <h2>Taklif qilingan buyruq</h2>
      <pre>{{{{ cmd }}}}</pre>
      {{% if dangerous %}}<p class="warn">OGOHLANTIRISH: xavfli naqshga mos keladi!</p>{{% endif %}}
      <form method="POST" action="/execute">
        <input type="hidden" name="cmd" value="{{{{ cmd }}}}">
        <button type="submit" class="{{{{ 'danger' if dangerous else '' }}}}">TASDIQLASH VA BAJARISH</button>
      </form>
    </div>
    {{% endif %}}

    {{% if output %}}
    <div class="card">
      <h2>Natija</h2>
      <pre>{{{{ output }}}}</pre>
    </div>
    {{% endif %}}

    {{% if error %}}<p class="warn">{{{{ error }}}}</p>{{% endif %}}
    </body></html>"""

    def login_required(f):
        def wrapper(*a, **kw):
            if not session.get("logged_in"):
                return redirect(url_for("login"))
            return f(*a, **kw)
        wrapper.__name__ = f.__name__
        return wrapper

    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            password = request.form.get("password", "")
            if hmac.compare_digest(password, BROWSER_PASSWORD):
                session["logged_in"] = True
                return redirect(url_for("main_page"))
            return render_template_string(LOGIN_HTML, error="Parol noto'g'ri!")
        return render_template_string(LOGIN_HTML, error=None)

    @app.route("/main")
    @login_required
    def main_page():
        return render_template_string(MAIN_HTML, cmd=None, output=None, error=None, dangerous=False)

    @app.route("/generate", methods=["POST"])
    @login_required
    def generate():
        user_request = request.form.get("user_request", "").strip()
        cmd, error = ask_ai_for_command(user_request)
        dangerous = False
        if cmd:
            dangerous, _ = is_dangerous(cmd)
        return render_template_string(MAIN_HTML, cmd=cmd, output=None, error=error, dangerous=dangerous)

    @app.route("/execute", methods=["POST"])
    @login_required
    def execute():
        cmd = request.form.get("cmd", "")
        dangerous, pattern = is_dangerous(cmd)
        if dangerous:
            output = f"BLOKLANDI: xavfli naqshga mos keldi ({pattern}). Bajarilmadi."
        else:
            output = run_command(cmd)
        return render_template_string(MAIN_HTML, cmd=cmd, output=output, error=None, dangerous=dangerous)

    print("=" * 55)
    print("  AI CLI SHELL - BRAUZER REJIMI")
    print(f"  Parol: {BROWSER_PASSWORD}")
    print("  Brauzerda oching: http://<telefon-IP>:8080")
    print("=" * 55)
    app.run(host="0.0.0.0", port=8080, debug=False)


# ==========================================================
# DASTUR MENYUSI
# ==========================================================

if __name__ == "__main__":
    print("AI CONTEXTUAL CLI SHELL")
    print("1. Terminal rejimi")
    print("2. Brauzer rejimi (Flask)")
    choice = input("Tanlang (1/2): ").strip()

    if choice == "1":
        terminal_mode()
    else:
        browser_mode()
