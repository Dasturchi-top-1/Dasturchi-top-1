#!/usr/bin/env python3
# ==========================================================
# BLIP OS DASHBOARD v2 - Oddiy parol + AI Loyiha Taklifchisi
# PLATFORMA: Termux / Pydroid 3
# REJIMLAR: 1) Terminal  2) Brauzer (Flask + oddiy parol)
# ==========================================================
# MUHIM: 'blip_watchdog.py' BIR XIL papkada bo'lishi shart!
# ==========================================================

import os
import re
import ast
import json
import subprocess
from datetime import datetime

import blip_watchdog as wd

# ==========================================================
# SOZLAMALAR
# ==========================================================
DASHBOARD_PORT = 8080
DASHBOARD_PAROL = "921324"          # Brauzer rejimi uchun oddiy parol
PROPOSALS_FOLDER = "AI/proposals"
os.makedirs(PROPOSALS_FOLDER, exist_ok=True)

OPENROUTER_API_KEY = "YOUR_API_KEY"
AI_MODEL = "deepseek/deepseek-v4-flash"


def get_battery_info():
    try:
        result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return f"{data.get('percentage', '?')}% ({data.get('status', '?')})"
    except Exception:
        pass
    return "Noma'lum"


# ==========================================================
# AI LOYIHA TAKLIFCHISI
# ==========================================================
def ask_ai_for_proposal(existing_services):
    if OPENROUTER_API_KEY == "SIZNING_API_KALITINGIZ":
        return None, None, None, "OPENROUTER_API_KEY sozlanmagan."

    services_list = ", ".join(existing_services) if existing_services else "hali hech narsa yo'q"

    system = (
        "Sen Blip OS nomli shaxsiy server tizimi uchun g'oya generatorisan. "
        f"Hozirgi xizmatlar: {services_list}. "
        "Shu tizimga mos, kichik, FOYDALI, standart Python kutubxonalari bilan "
        "yoziladigan BITTA yangi xizmat g'oyasini taklif qil. "
        "Javobni ANIQ shu formatda ber:\n"
        "SARLAVHA: <qisqa nom>\n"
        "TAVSIF: <1-2 gap, nima qilishi>\n"
        "```python\n<to'liq, ishga tayyor kod>\n```"
    )

    try:
        import requests
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={"model": AI_MODEL, "messages": [{"role": "system", "content": system},
                                                     {"role": "user", "content": "Yangi g'oya taklif qil"}]},
            timeout=45,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"]

        title_match = re.search(r'SARLAVHA:\s*(.+)', text)
        desc_match = re.search(r'TAVSIF:\s*(.+)', text)
        code_match = re.search(r'```python\s*(.*?)\s*```', text, re.DOTALL)

        title = title_match.group(1).strip() if title_match else "Noma'lum loyiha"
        desc = desc_match.group(1).strip() if desc_match else ""
        code = code_match.group(1).strip() if code_match else None

        if not code:
            return title, desc, None, "AI javobida kod topilmadi."

        return title, desc, code, None
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 401:
            return None, None, None, "401 Unauthorized - API kalit noto'g'ri yoki sozlanmagan."
        return None, None, None, f"HTTP xato: {e}"
    except Exception as e:
        return None, None, None, f"Xato: {e}"


def validate_code(code):
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)


def save_proposal(title, code):
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', title.lower())[:40]
    filename = f"{safe_name}.py"
    filepath = os.path.join(PROPOSALS_FOLDER, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
    return filepath


# ==========================================================
# 1-REJIM: TERMINAL
# ==========================================================
def terminal_mode():
    watchdog = wd.Watchdog()
    watchdog.start_monitoring()

    print("=" * 55)
    print("  BLIP OS DASHBOARD v2 (TERMINAL REJIM)")
    print("=" * 55)
    print("Buyruqlar: holat, ai-taklif, qosh, ochir, log, chiqish\n")

    while True:
        try:
            cmd = input("dashboard> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue

        if cmd == "chiqish":
            print("Xayr, jigarim!")
            break

        elif cmd == "holat":
            for s in watchdog.get_status():
                state = "ISHLAYAPTI" if s["alive"] else "TO'XTAGAN"
                print(f"  [{state}] {s['name']}")

        elif cmd == "ai-taklif":
            print("[AI g'oya o'ylab topmoqda...]")
            existing = [s["name"] for s in watchdog.get_status()]
            title, desc, code, error = ask_ai_for_proposal(existing)

            if not code:
                print(f"  Xato: {error}")
                continue

            print(f"\n  SARLAVHA: {title}")
            print(f"  TAVSIF: {desc}")
            print(f"\n  --- KOD ---\n{code}\n  -----------\n")

            valid, syntax_error = validate_code(code)
            if not valid:
                print(f"  Kod sintaksis xatosi bilan rad etildi: {syntax_error}")
                continue

            confirm = input("  Bu loyihani qo'shishga RUXSAT berasizmi? (ha/yo'q): ").strip().lower()
            if confirm == "ha":
                path = save_proposal(title, code)
                watchdog.add_service(title, path)
                print(f"  Qo'shildi va ishga tushirildi: {path}")
            else:
                print("  Rad etildi, hech narsa saqlanmadi.")

        elif cmd == "qosh":
            name = input("  Xizmat nomi: ").strip()
            path = input("  Skript yo'li: ").strip()
            ok, msg = watchdog.add_service(name, path)
            print(f"  {msg}")

        elif cmd == "ochir":
            name = input("  O'chiriladigan xizmat: ").strip()
            ok, msg = watchdog.remove_service(name)
            print(f"  {msg}")

        elif cmd == "log":
            for entry in wd.load_logs()[-10:]:
                print(f"  [{entry['timestamp']}] {entry['message']}")

        else:
            print("  Noma'lum buyruq")


# ==========================================================
# 2-REJIM: BRAUZER (Flask + oddiy parol)
# ==========================================================
def browser_mode():
    from flask import Flask, request, session, redirect, url_for, render_template_string

    watchdog = wd.Watchdog()
    watchdog.start_monitoring()

    app = Flask(__name__)
    app.secret_key = "YOUR_SECRET_KEY"

    STYLE = """
    <style>
      body { background:#0a0a0a; color:#39ff14; font-family:Consolas,monospace; padding:20px; max-width:700px; margin:auto; }
      h1, h2 { color:#00c8ff; }
      input[type=text], input[type=password] { width:100%; padding:10px; margin:6px 0; background:#111;
          border:1px solid #00c8ff; border-radius:6px; color:#39ff14; }
      button, .btn { background:#39ff14; color:#0a0a0a; border:none; padding:10px 18px;
          border-radius:6px; font-weight:bold; cursor:pointer; text-decoration:none; display:inline-block; }
      button.danger { background:#ff3355; color:white; }
      button.warn { background:#f0a500; color:#0a0a0a; }
      .card { background:#111; border:1px solid #39ff14; border-radius:8px; padding:16px; margin:12px 0; }
      table { width:100%; border-collapse:collapse; }
      th, td { border:1px solid #222; padding:6px; text-align:left; font-size:13px; }
      .alive { color:#39ff14; } .dead { color:#ff3355; } .disabled { color:#888; }
      pre { background:#000; padding:10px; border-radius:6px; font-size:12px; white-space:pre-wrap; }
    </style>
    """

    LOGIN_HTML = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{STYLE}</head>
    <body><h1>BLIP OS - Kirish</h1>
    <form method="POST" action="/login">
      <input type="password" name="parol" placeholder="Parolni kiriting" required>
      <button type="submit">KIRISH</button>
    </form>
    {{% if error %}}<p style="color:#ff3355">{{{{ error }}}}</p>{{% endif %}}
    </body></html>"""

    MAIN_HTML = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{STYLE}</head>
    <body>
    <h1>BLIP OS DASHBOARD v2</h1>
    <p>Xush kelibsiz! | <a href="/logout" style="color:#00c8ff">Chiqish</a></p>
    <p>Batareya: {{{{ battery }}}}</p>

    <div class="card">
      <h2>AI Loyiha Taklifchisi</h2>
      <p>AI hozirgi tizim asosida yangi xizmat g'oyasini taklif qiladi.
         HECH NARSA sizning ruxsatingizsiz qo'shilmaydi.</p>
      <form method="POST" action="/ai-proposal"><button type="submit">AI'DAN YANGI G'OYA SO'RASH</button></form>

      {{% if proposal %}}
      <div style="margin-top:12px; border-top:1px solid #222; padding-top:12px;">
        <h3>{{{{ proposal.title }}}}</h3>
        <p>{{{{ proposal.desc }}}}</p>
        <pre>{{{{ proposal.code }}}}</pre>
        {{% if proposal.valid %}}
        <form method="POST" action="/approve-proposal">
          <input type="hidden" name="title" value="{{{{ proposal.title }}}}">
          <input type="hidden" name="code" value="{{{{ proposal.code_escaped }}}}">
          <button type="submit">RUXSAT BERISH VA QO'SHISH</button>
          <button type="submit" formaction="/reject-proposal" class="danger">RAD ETISH</button>
        </form>
        {{% else %}}
        <p style="color:#ff3355">Kod sintaksis xatosi bilan avtomatik rad etildi: {{{{ proposal.error }}}}</p>
        {{% endif %}}
      </div>
      {{% endif %}}
    </div>

    <div class="card">
      <h2>Xizmat qo'shish (qo'lda)</h2>
      <form method="POST" action="/add">
        <input type="text" name="name" placeholder="Nomi" required>
        <input type="text" name="script_path" placeholder="Skript yo'li" required>
        <button type="submit">QO'SHISH</button>
      </form>
    </div>

    <div class="card">
      <h2>Xizmatlar</h2>
      <table>
        <tr><th>Nomi</th><th>Holat</th><th>Amal</th></tr>
        {{% for s in services %}}
        <tr>
          <td>{{{{ s.name }}}}</td>
          <td class="{{{{ 'alive' if s.alive else 'dead' }}}}">{{{{ 'ISHLAYAPTI' if s.alive else 'TOXTAGAN' }}}}</td>
          <td><form method="POST" action="/remove/{{{{ s.name }}}}">
              <button type="submit" class="danger">Ochirish</button></form></td>
        </tr>
        {{% endfor %}}
      </table>
    </div>
    </body></html>"""

    def login_required(f):
        def wrapper(*a, **kw):
            if not session.get("auth"):
                return redirect(url_for("login"))
            return f(*a, **kw)
        wrapper.__name__ = f.__name__
        return wrapper

    @app.route("/")
    def login():
        return render_template_string(LOGIN_HTML, error=request.args.get("error"))

    @app.route("/login", methods=["POST"])
    def do_login():
        parol = request.form.get("parol", "")
        if parol == DASHBOARD_PAROL:
            session["auth"] = True
            return redirect(url_for("dashboard"))
        return render_template_string(LOGIN_HTML, error="Noto'g'ri parol")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template_string(
            MAIN_HTML, services=watchdog.get_status(),
            battery=get_battery_info(), proposal=session.pop("proposal", None),
        )

    @app.route("/ai-proposal", methods=["POST"])
    @login_required
    def ai_proposal():
        existing = [s["name"] for s in watchdog.get_status()]
        title, desc, code, error = ask_ai_for_proposal(existing)

        if not code:
            session["proposal"] = {"title": "Xato", "desc": error, "code": "", "valid": False, "error": error}
        else:
            valid, syntax_error = validate_code(code)
            session["proposal"] = {
                "title": title, "desc": desc, "code": code,
                "code_escaped": code, "valid": valid, "error": syntax_error,
            }
        return redirect(url_for("dashboard"))

    @app.route("/approve-proposal", methods=["POST"])
    @login_required
    def approve_proposal():
        title = request.form.get("title", "yangi_loyiha")
        code = request.form.get("code", "")
        valid, error = validate_code(code)
        if valid:
            path = save_proposal(title, code)
            watchdog.add_service(title, path)
        return redirect(url_for("dashboard"))

    @app.route("/reject-proposal", methods=["POST"])
    @login_required
    def reject_proposal():
        return redirect(url_for("dashboard"))

    @app.route("/add", methods=["POST"])
    @login_required
    def add():
        name = request.form.get("name", "").strip()
        path = request.form.get("script_path", "").strip()
        if name and path:
            watchdog.add_service(name, path)
        return redirect(url_for("dashboard"))

    @app.route("/remove/<name>", methods=["POST"])
    @login_required
    def remove(name):
        watchdog.remove_service(name)
        return redirect(url_for("dashboard"))

    print("=" * 55)
    print("  BLIP OS DASHBOARD v2 - BRAUZER REJIMI")
    print(f"  Brauzerda oching: http://127.0.0.1:{DASHBOARD_PORT}")
    print("  Parol: 921324")
    print("=" * 55)
    app.run(host="0.0.0.0", port=DASHBOARD_PORT, debug=False)


# ==========================================================
# DASTUR MENYUSI
# ==========================================================
if __name__ == "__main__":
    print("BLIP OS DASHBOARD v2")
    print("1. Terminal rejimi")
    print("2. Brauzer rejimi (oddiy parol)")
    choice = input("Tanlang (1/2): ").strip()

    if choice == "1":
        terminal_mode()
    else:
        browser_mode()