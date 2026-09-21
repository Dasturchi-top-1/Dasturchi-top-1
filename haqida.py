#!/usr/bin/env python3
# Blip Remote Toolkit v1.1 — Shaxsiy qurilmani masofadan boshqarish
# Faqat o'zingga tegishli qurilmada ishlatish uchun!
# Terminal va Brauzer rejimi, parol: 921324

import os
import subprocess
import sys
import sqlite3
import shutil
import time
import json
from datetime import datetime
from pathlib import Path

try:
    from flask import Flask, render_template_string, request, redirect, url_for, session, send_file, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

DB = 'remote_toolkit.db'
PASSWORD = 'YOUR_PASSWORD'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
M = '\033[95m'
C = '\033[96m'
W = '\033[0m'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  action TEXT,
                  detail TEXT)''')
    conn.commit()
    conn.close()

def log_action(action, detail):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, action, detail) VALUES (?, ?, ?)",
              (datetime.now().isoformat(), action, str(detail)))
    conn.commit()
    conn.close()

def run_cmd(cmd, timeout=10):
    """Buyruqni bajarib, natijani qaytaradi."""
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=timeout, text=True)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Xato: buyruq belgilangan vaqtdan oshib ketdi."
    except Exception as e:
        return f"Xato: {e}"

def get_system_info():
    """Tizim haqida qisqacha ma'lumot."""
    info = {}
    info['os'] = run_cmd("uname -a").strip()
    uptime = run_cmd("uptime").strip()
    info['uptime'] = uptime if uptime else "Mavjud emas"
    df = run_cmd("df -h /").strip()
    info['disk'] = df if df else "Mavjud emas"
    mem = run_cmd("free -h").strip()
    info['memory'] = mem if mem else "Mavjud emas"
    return info

def list_files(path='.'):
    """Katalogni ko'rsatish."""
    try:
        items = os.listdir(path)
    except Exception as e:
        return f"Xato: {e}"
    result = []
    for item in sorted(items):
        full = os.path.join(path, item)
        if os.path.isdir(full):
            result.append(f"[DIR]  {item}/")
        else:
            size = os.path.getsize(full)
            result.append(f"[FILE] {item} ({size} bayt)")
    return "\n".join(result)

def download_file(path):
    """Faylni yuklab olish uchun to'liq yo'l."""
    if os.path.isfile(path):
        return path
    return None

def upload_file(file, target_dir='.'):
    """Faylni yuklash."""
    if not os.path.isdir(target_dir):
        return "Xato: maqsad katalog mavjud emas."
    filename = file.filename
    if not filename:
        return "Xato: fayl nomi yo'q."
    dest = os.path.join(target_dir, filename)
    try:
        file.save(dest)
        log_action('upload', dest)
        return f"Fayl yuklandi: {dest}"
    except Exception as e:
        return f"Xato: {e}"

def delete_file(path):
    """Faylni o'chirish."""
    try:
        if os.path.isfile(path):
            os.remove(path)
            log_action('delete', path)
            return f"O'chirildi: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            log_action('delete_dir', path)
            return f"Katalog o'chirildi: {path}"
        else:
            return "Xato: yo'l topilmadi."
    except Exception as e:
        return f"Xato: {e}"

def rename_file(old, new):
    """Fayl nomini o'zgartirish."""
    try:
        os.rename(old, new)
        log_action('rename', f"{old} -> {new}")
        return f"Qayta nomlandi: {old} -> {new}"
    except Exception as e:
        return f"Xato: {e}"

def move_file(src, dst):
    """Faylni ko'chirish."""
    try:
        shutil.move(src, dst)
        log_action('move', f"{src} -> {dst}")
        return f"Ko'chirildi: {src} -> {dst}"
    except Exception as e:
        return f"Xato: {e}"

def copy_file(src, dst):
    """Faylni nusxalash."""
    try:
        shutil.copy2(src, dst)
        log_action('copy', f"{src} -> {dst}")
        return f"Nusxalandi: {src} -> {dst}"
    except Exception as e:
        return f"Xato: {e}"

def terminal_mode():
    """Terminal interaktiv rejim."""
    print(f"{C}╔══════════════════════════════════════╗{W}")
    print(f"{C}║   BLIP REMOTE TOOLKIT v1.1          ║{W}")
    print(f"{C}║   Shaxsiy masofaviy boshqaruv        ║{W}")
    print(f"{C}╚══════════════════════════════════════╝{W}")
    print(f"{Y}Buyruqlar: help, sysinfo, ls <path>, cmd <shell>, download <path>, upload <file>, delete <path>, exit{W}")
    while True:
        try:
            cmd_input = input(f"{G}>>> {W}").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not cmd_input:
            continue
        parts = cmd_input.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if command == 'help':
            print(f"{Y}Mavjud buyruqlar:{W}")
            print("  sysinfo              — tizim ma'lumoti")
            print("  ls <path>            — katalogni ko'rish (default '.')")
            print("  cmd <shell buyruq>   — shell buyrug'ini bajarish")
            print("  download <path>      — faylni yuklab olish (nusxalash)")
            print("  upload <fayl> <dest> — faylni yuklash (nusxalash)")
            print("  delete <path>        — fayl/katalogni o'chirish")
            print("  exit                 — chiqish")
        elif command == 'sysinfo':
            info = get_system_info()
            print(f"{Y}OS:{W}\n{info['os']}")
            print(f"{Y}Ish vaqti:{W}\n{info['uptime']}")
            print(f"{Y}Disk:{W}\n{info['disk']}")
            print(f"{Y}Xotira:{W}\n{info['memory']}")
            log_action('sysinfo', 'terminal')
        elif command == 'ls':
            path = arg if arg else '.'
            result = list_files(path)
            print(result)
            log_action('ls', path)
        elif command == 'cmd':
            if not arg:
                print(f"{R}Buyruq kiriting: cmd <shell buyruq>{W}")
            else:
                output = run_cmd(arg)
                print(output)
                log_action('cmd', arg)
        elif command == 'download':
            if not arg:
                print(f"{R}Fayl yo'lini kiriting: download <path>{W}")
            else:
                path = download_file(arg)
                if path:
                    print(f"{G}Fayl mavjud: {path}. Uni o'zingiz nusxalab oling.{W}")
                    log_action('download', path)
                else:
                    print(f"{R}Fayl topilmadi.{W}")
        elif command == 'upload':
            if not arg:
                print(f"{R}Format: upload <manba> <maqsad>{W}")
            else:
                args = arg.split()
                if len(args) >= 2:
                    src, dst = args[0], args[1]
                    try:
                        shutil.copy2(src, dst)
                        print(f"{G}Nusxalandi: {src} -> {dst}{W}")
                        log_action('upload', f"{src} -> {dst}")
                    except Exception as e:
                        print(f"{R}Xato: {e}{W}")
                else:
                    print(f"{R}Yetarli argument yo'q.{W}")
        elif command == 'delete':
            if not arg:
                print(f"{R}Fayl/katalog yo'lini kiriting: delete <path>{W}")
            else:
                result = delete_file(arg)
                print(result)
        elif command == 'exit':
            break
        else:
            print(f"{R}Noma'lum buyruq. Yordam uchun 'help'.{W}")

def browser_mode():
    """Flask veb-interfeys."""
    if not FLASK_AVAILABLE:
        print(f"{R}Flask o'rnatilmagan. Brauzer rejimi uchun: pip3 install flask{W}")
        return
    app = Flask(__name__)
    app.secret_key = 'YOUR_SECRET_KEY'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    HTML_LOGIN = '''
    <h2>Blip Remote Toolkit Login</h2>
    <form method="POST">
    Parol: <input type="password" name="password">
    <input type="submit" value="Kirish">
    </form>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    '''

    HTML_DASHBOARD = '''
    <h1>Blip Remote Toolkit v1.1</h1>
    <p><a href="/logout">Chiqish</a></p>
    <h2>Tizim ma'lumoti</h2>
    <pre>{{ sysinfo }}</pre>
    <h2>Fayl boshqaruvi</h2>
    <form method="POST" action="/list">
      Katalog: <input type="text" name="path" value=".">
      <input type="submit" value="Ko'rish">
    </form>
    <pre>{{ listing }}</pre>
    <h2>Buyruq bajarish</h2>
    <form method="POST" action="/cmd">
      Buyruq: <input type="text" name="cmd" size="40">
      <input type="submit" value="Bajarish">
    </form>
    <pre>{{ cmd_output }}</pre>
    <h2>Fayl yuklash</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
      Fayl: <input type="file" name="file">
      Maqsad katalog: <input type="text" name="dir" value=".">
      <input type="submit" value="Yuklash">
    </form>
    <p>{{ upload_msg }}</p>
    '''

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            if request.form.get('password') == PASSWORD:
                session['auth'] = True
                return redirect(url_for('dashboard'))
            else:
                return render_template_string(HTML_LOGIN, error="Noto'g'ri parol")
        if session.get('auth'):
            return redirect(url_for('dashboard'))
        return render_template_string(HTML_LOGIN, error=None)

    @app.route('/dashboard')
    def dashboard():
        if not session.get('auth'):
            return redirect(url_for('index'))
        sysinfo = get_system_info()
        return render_template_string(HTML_DASHBOARD,
                                      sysinfo=json.dumps(sysinfo, indent=2, ensure_ascii=False),
                                      listing='',
                                      cmd_output='',
                                      upload_msg='')

    @app.route('/list', methods=['POST'])
    def list_path():
        if not session.get('auth'):
            return redirect(url_for('index'))
        path = request.form.get('path', '.')
        listing = list_files(path)
        sysinfo = get_system_info()
        return render_template_string(HTML_DASHBOARD,
                                      sysinfo=json.dumps(sysinfo, indent=2, ensure_ascii=False),
                                      listing=listing,
                                      cmd_output='',
                                      upload_msg='')

    @app.route('/cmd', methods=['POST'])
    def run_command():
        if not session.get('auth'):
            return redirect(url_for('index'))
        cmd = request.form.get('cmd', '')
        output = run_cmd(cmd)
        log_action('cmd', cmd)
        sysinfo = get_system_info()
        return render_template_string(HTML_DASHBOARD,
                                      sysinfo=json.dumps(sysinfo, indent=2, ensure_ascii=False),
                                      listing='',
                                      cmd_output=output,
                                      upload_msg='')

    @app.route('/upload', methods=['POST'])
    def upload():
        if not session.get('auth'):
            return redirect(url_for('index'))
        if 'file' not in request.files:
            msg = "Fayl tanlanmadi"
        else:
            file = request.files['file']
            dir = request.form.get('dir', '.')
            msg = upload_file(file, dir)
        sysinfo = get_system_info()
        return render_template_string(HTML_DASHBOARD,
                                      sysinfo=json.dumps(sysinfo, indent=2, ensure_ascii=False),
                                      listing='',
                                      cmd_output='',
                                      upload_msg=msg)

    @app.route('/logout')
    def logout():
        session.pop('auth', None)
        return redirect(url_for('index'))

    print(f"{G}Brauzer rejimi: http://127.0.0.1:5000{W}")
    app.run(host='127.0.0.1', port=5000, debug=False)

def main_menu():
    print(f"{C}╔══════════════════════════════════════╗{W}")
    print(f"{C}║   BLIP REMOTE TOOLKIT v1.1          ║{W}")
    print(f"{C}║   Rejim tanlash                     ║{W}")
    print(f"{C}╚══════════════════════════════════════╝{W}")
    print(f"{Y}1. Terminal rejimi{W}")
    print(f"{Y}2. Brauzer rejimi (Flask veb-panel){W}")
    print(f"{Y}0. Chiqish{W}")
    choice = input(f"{G}>>> {W}").strip()
    return choice

if __name__ == '__main__':
    init_db()
    while True:
        choice = main_menu()
        if choice == '1':
            terminal_mode()
        elif choice == '2':
            if FLASK_AVAILABLE:
                browser_mode()
            else:
                print(f"{R}Flask o'rnatilmagan. Brauzer rejimi uchun: pip3 install flask{W}")
        elif choice == '0':
            print(f"{C}[~] Dastur tugadi.{W}")
            sys.exit(0)
        else:
            print(f"{R}Noto'g'ri tanlov. Qayta urinib ko'r.{W}")