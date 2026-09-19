#!/usr/bin/env python3
# ==========================================================
# BLIP OS - WATCHDOG (NAZORATCHI)
# PLATFORMA: Termux / Pydroid 3
# REJIMLAR: 1) Terminal  2) Brauzer (Flask)
# ==========================================================
# VAZIFA: Bir nechta Python skriptni (xizmatni) subprocess sifatida
# ishga tushiradi, ularni kuzatib turadi. Agar biror xizmat
# to'xtab/cho'kib qolsa - avtomatik qayta ishga tushiradi va
# buni logga yozadi.
# ==========================================================

import os
import json
import time
import threading
import subprocess
import requests
from datetime import datetime

LOG_FOLDER = "AI/watchdog"
LOG_FILE = os.path.join(LOG_FOLDER, "watchdog_log.json")
CONFIG_FILE = os.path.join(LOG_FOLDER, "services.json")

os.makedirs(LOG_FOLDER, exist_ok=True)

CHECK_INTERVAL = 5          # necha soniyada bir tekshiradi
MAX_RESTARTS_PER_HOUR = 5   # bir soatda shu sonidan ko'p qayta ishga tushsa, to'xtatadi (halokatli tsikldan himoya)

# YANGI: Telegram orqali muhim xabarlarni yuborish
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN"   # @BotFather'dan olinadi
TELEGRAM_CHAT_ID = "7807361049"        # @userinfobot orqali bilib olinadi


def send_telegram_alert(message):
    """Watchdog'dagi muhim hodisalarni Telegram'ga yuboradi.
    Agar sozlanmagan bo'lsa yoki internet bo'lmasa, jim o'tkazib yuboradi -
    Watchdog'ning o'zi buning uchun to'xtab qolmasligi kerak."""
    if TELEGRAM_BOT_TOKEN == "SIZNING_BOT_TOKENINGIZ":
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": f"🐕 Blip Watchdog: {message}"}, timeout=8)
    except Exception:
        pass  # Telegram ishlamasa ham, Watchdog o'z vazifasini davom ettirishi kerak


# ==========================================================
# SOZLAMALARNI SAQLASH/YUKLASH
# ==========================================================

def load_services():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_services(services):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(services, f, ensure_ascii=False, indent=2)


def append_log(message):
    entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": message}
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(entry)
    logs = logs[-200:]  # faqat oxirgi 200 ta yozuvni saqlaymiz
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"[{entry['timestamp']}] {message}")


def load_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


# ==========================================================
# XIZMATNI BOSHQARISH
# ==========================================================

class ManagedService:
    """Bitta kuzatilayotgan xizmatning holatini saqlaydi"""

    def __init__(self, name, script_path):
        self.name = name
        self.script_path = script_path
        self.process = None
        self.restart_times = []  # oxirgi qayta ishga tushirishlar vaqti (tsikl himoyasi uchun)
        self.enabled = True

    def start(self):
        if not os.path.exists(self.script_path):
            append_log(f"'{self.name}' ishga tushmadi: fayl topilmadi ({self.script_path})")
            self.enabled = False
            return

        try:
            self.process = subprocess.Popen(
                ["python3", self.script_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            append_log(f"'{self.name}' ishga tushirildi (PID: {self.process.pid})")
        except Exception as e:
            append_log(f"'{self.name}' ishga tushmadi: {e}")
            self.enabled = False

    def is_alive(self):
        if self.process is None:
            return False
        return self.process.poll() is None  # None = hali ishlayapti

    def get_exit_reason(self):
        if self.process is None:
            return "Noma'lum"
        try:
            _, stderr = self.process.communicate(timeout=1)
            if stderr:
                lines = stderr.strip().split("\n")
                return "\n".join(lines[-3:])
        except Exception:
            pass
        return f"Chiqish kodi: {self.process.returncode}"

    def can_restart(self):
        """Bir soat ichida MAX_RESTARTS_PER_HOUR martadan ko'p qayta ishga
        tushirilmasligi kerak - bu halokatli tsikldan (crash loop) himoya"""
        now = time.time()
        self.restart_times = [t for t in self.restart_times if now - t < 3600]
        return len(self.restart_times) < MAX_RESTARTS_PER_HOUR

    def record_restart(self):
        self.restart_times.append(time.time())

    def stop(self):
        if self.process and self.is_alive():
            self.process.terminate()
            append_log(f"'{self.name}' to'xtatildi (qo'lda).")
        self.enabled = False


# ==========================================================
# WATCHDOG ASOSIY MANTIG'I
# ==========================================================

class Watchdog:
    def __init__(self):
        self.services = {}  # {nom: ManagedService}
        self._load_from_config()
        self.running = False

    def _load_from_config(self):
        for entry in load_services():
            svc = ManagedService(entry["name"], entry["script_path"])
            self.services[svc.name] = svc

    def add_service(self, name, script_path):
        if name in self.services:
            return False, "Bu nomdagi xizmat allaqachon mavjud."

        svc = ManagedService(name, script_path)
        self.services[name] = svc
        svc.start()

        config = load_services()
        config.append({"name": name, "script_path": script_path})
        save_services(config)

        return True, f"'{name}' qo'shildi va ishga tushirildi."

    def remove_service(self, name):
        if name not in self.services:
            return False, "Bunday xizmat topilmadi."

        self.services[name].stop()
        del self.services[name]

        config = [c for c in load_services() if c["name"] != name]
        save_services(config)

        return True, f"'{name}' o'chirildi."

    def start_all(self):
        for svc in self.services.values():
            if svc.enabled and not svc.is_alive():
                svc.start()

    def _monitor_loop(self):
        while self.running:
            for svc in list(self.services.values()):
                if not svc.enabled:
                    continue

                if not svc.is_alive():
                    returncode = svc.process.returncode if svc.process else None

                    # MUHIM: chiqish kodi 0 = dastur MUVAFFAQIYATLI tugadi
                    # (masalan "bir martalik" skript - ma'lumot chiqarib tugaydi).
                    # Bu XATO EMAS, shuning uchun qayta ishga tushirmaymiz.
                    if returncode == 0:
                        append_log(f"'{svc.name}' muvaffaqiyatli tugadi (chiqish kodi 0) - bu one-shot skript, qayta ishga tushirilmaydi.")
                        svc.enabled = False
                        continue

                    reason = svc.get_exit_reason()
                    append_log(f"'{svc.name}' TO'XTAB QOLDI! Sabab: {reason}")
                    send_telegram_alert(f"⚠️ '{svc.name}' to'xtab qoldi!\nSabab: {reason}")

                    if svc.can_restart():
                        svc.record_restart()
                        append_log(f"'{svc.name}' avtomatik qayta ishga tushirilmoqda...")
                        svc.start()
                    else:
                        svc.enabled = False
                        append_log(
                            f"'{svc.name}' 1 soat ichida {MAX_RESTARTS_PER_HOUR} martadan "
                            f"ko'p cho'kdi - HALOKATLI TSIKL DEB TOPILDI, to'xtatildi. "
                            f"Kodni tekshiring!"
                        )
                        send_telegram_alert(
                            f"🚨 HALOKATLI TSIKL: '{svc.name}' 1 soatda {MAX_RESTARTS_PER_HOUR} "
                            f"martadan ko'p cho'kdi va TO'XTATILDI. Kodni tekshiring!"
                        )

            time.sleep(CHECK_INTERVAL)

    def start_monitoring(self):
        self.running = True
        self.start_all()
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()

    def get_status(self):
        return [
            {
                "name": svc.name,
                "script_path": svc.script_path,
                "alive": svc.is_alive(),
                "enabled": svc.enabled,
                "restarts_last_hour": len(svc.restart_times),
            }
            for svc in self.services.values()
        ]


# ==========================================================
# 1-REJIM: TERMINAL
# ==========================================================

def terminal_mode():
    watchdog = Watchdog()
    watchdog.start_monitoring()

    print("=" * 55)
    print("  BLIP OS WATCHDOG (TERMINAL REJIM)")
    print("=" * 55)
    print("Buyruqlar: qosh, ochir, holat, log, chiqish\n")

    while True:
        try:
            cmd = input("watchdog> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue

        if cmd == "chiqish":
            print("Xayr, jigarim! Xizmatlar fonda davom etadi.")
            break

        elif cmd == "qosh":
            name = input("  Xizmat nomi: ").strip()
            path = input("  Skript yo'li (.py fayl): ").strip()
            ok, msg = watchdog.add_service(name, path)
            print(f"  {msg}")

        elif cmd == "ochir":
            name = input("  O'chiriladigan xizmat nomi: ").strip()
            ok, msg = watchdog.remove_service(name)
            print(f"  {msg}")

        elif cmd == "holat":
            status = watchdog.get_status()
            if not status:
                print("  Hali hech qanday xizmat qo'shilmagan.")
            for s in status:
                state = "ISHLAYAPTI" if s["alive"] else ("O'CHIRILGAN" if not s["enabled"] else "TO'XTAGAN")
                print(f"  [{state}] {s['name']} - qayta ishga tushishlar (1 soat): {s['restarts_last_hour']}")

        elif cmd == "log":
            logs = load_logs()
            for entry in logs[-15:]:
                print(f"  [{entry['timestamp']}] {entry['message']}")

        else:
            print("  Noma'lum buyruq. Mavjud: qosh, ochir, holat, log, chiqish")


# ==========================================================
# 2-REJIM: BRAUZER (Flask)
# ==========================================================

def browser_mode():
    from flask import Flask, request, session, redirect, url_for, render_template_string
    import hmac

    watchdog = Watchdog()
    watchdog.start_monitoring()

    app = Flask(__name__)
    app.secret_key = "YOUR_SECRET_KEY"
    PASSWORD = "921324"

    STYLE = """
    <style>
      body { background:#0a0a0a; color:#39ff14; font-family:Consolas,monospace; padding:20px; max-width:650px; margin:auto; }
      h1, h2 { color:#00c8ff; }
      input[type=text], input[type=password] { width:100%; padding:10px; margin:6px 0;
          background:#111; border:1px solid #00c8ff; border-radius:6px; color:#39ff14; }
      button { background:#39ff14; color:#0a0a0a; border:none; padding:8px 16px;
          border-radius:6px; font-weight:bold; cursor:pointer; }
      button.danger { background:#ff3355; color:white; }
      .card { background:#111; border:1px solid #39ff14; border-radius:8px; padding:16px; margin:12px 0; }
      table { width:100%; border-collapse:collapse; }
      th, td { border:1px solid #222; padding:6px; text-align:left; font-size:13px; }
      .alive { color:#39ff14; } .dead { color:#ff3355; } .disabled { color:#888; }
      pre { background:#000; padding:10px; border-radius:6px; font-size:11px; max-height:250px; overflow-y:auto; }
    </style>
    """

    LOGIN_HTML = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{STYLE}</head>
    <body><h1>BLIP WATCHDOG - Kirish</h1>
    <form method="POST"><input type="password" name="password" placeholder="Parol" required>
    <button type="submit">KIRISH</button></form>
    {{% if error %}}<p style="color:#ff3355">{{{{ error }}}}</p>{{% endif %}}
    </body></html>"""

    MAIN_HTML = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{STYLE}
    <meta http-equiv="refresh" content="10"></head>
    <body>
    <h1>BLIP OS WATCHDOG</h1>
    <p><a href="/logout" style="color:#00c8ff">Chiqish</a> (sahifa 10 soniyada avtomatik yangilanadi)</p>

    <div class="card">
      <h2>Yangi xizmat qo'shish</h2>
      <form method="POST" action="/add">
        <input type="text" name="name" placeholder="Xizmat nomi" required>
        <input type="text" name="script_path" placeholder="Skript yo'li (masalan: blip_links.py)" required>
        <button type="submit">QO'SHISH VA ISHGA TUSHIRISH</button>
      </form>
    </div>

    <div class="card">
      <h2>Xizmatlar holati</h2>
      <table>
        <tr><th>Nomi</th><th>Holat</th><th>Qayta ishga tushishlar (1 soat)</th><th>Amal</th></tr>
        {{% for s in services %}}
        <tr>
          <td>{{{{ s.name }}}}</td>
          <td class="{{{{ 'alive' if s.alive else ('disabled' if not s.enabled else 'dead') }}}}">
            {{{{ 'ISHLAYAPTI' if s.alive else ('OCHIRILGAN' if not s.enabled else 'TOXTAGAN') }}}}
          </td>
          <td>{{{{ s.restarts_last_hour }}}}</td>
          <td>
            <form method="POST" action="/remove/{{{{ s.name }}}}" style="display:inline;">
              <button type="submit" class="danger">Ochirish</button>
            </form>
          </td>
        </tr>
        {{% endfor %}}
      </table>
    </div>

    <div class="card">
      <h2>Oxirgi hodisalar (log)</h2>
      <pre>{{% for entry in logs %}}[{{{{ entry.timestamp }}}}] {{{{ entry.message }}}}
{{% endfor %}}</pre>
    </div>
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
            if hmac.compare_digest(request.form.get("password", ""), PASSWORD):
                session["logged_in"] = True
                return redirect(url_for("dashboard"))
            return render_template_string(LOGIN_HTML, error="Parol noto'g'ri!")
        return render_template_string(LOGIN_HTML, error=None)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        logs = list(reversed(load_logs()[-20:]))
        return render_template_string(MAIN_HTML, services=watchdog.get_status(), logs=logs)

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
    print("  BLIP OS WATCHDOG - BRAUZER REJIMI")
    print(f"  Parol: {PASSWORD}")
    print("  Brauzerda oching: http://<telefon-IP>:8090")
    print("=" * 55)
    app.run(host="0.0.0.0", port=8090, debug=False)


# ==========================================================
# DASTUR MENYUSI
# ==========================================================

if __name__ == "__main__":
    print("BLIP OS WATCHDOG")
    print("1. Terminal rejimi")
    print("2. Brauzer rejimi (Flask)")
    choice = input("Tanlang (1/2): ").strip()

    if choice == "1":
        terminal_mode()
    else:
        browser_mode()
