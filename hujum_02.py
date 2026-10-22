#!/usr/bin/env python3
# Blip Param Miner v1.0 — Yashirin parametrlarni topish
# Faqat ruxsat etilgan test muhitida!
# Terminal va Brauzer rejimi, parol: 921324

import requests
import time
import sys
import threading
from urllib.parse import urlparse, urljoin, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from flask import Flask, render_template_string, request, redirect, url_for, session
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
M = '\033[95m'
C = '\033[96m'
W = '\033[0m'

# Umumiy parametr nomlari (topish uchun lug'at)
COMMON_PARAMS = [
    'id', 'page', 'user', 'admin', 'debug', 'test', 'source', 'file', 'path',
    'redirect', 'url', 'next', 'return', 'ref', 'callback', 'jsonp', 'format',
    'action', 'cmd', 'exec', 'command', 'shell', 'php', 'include', 'require',
    'template', 'view', 'theme', 'lang', 'locale', 'country', 'ip', 'host',
    'port', 'key', 'token', 'auth', 'session', 'login', 'logout', 'search',
    'q', 'query', 'filter', 'sort', 'order', 'limit', 'offset', 'start', 'end',
    'from', 'to', 'date', 'time', 'year', 'month', 'day', 'name', 'email',
    'password', 'passwd', 'username', 'user_id', 'product_id', 'category',
    'type', 'id_type', 'api_key', 'secret', 'client_id', 'scope', 'state',
    'code', 'error', 'msg', 'message', 'status', 'result', 'data', 'output',
    'format', 'output_format', 'download', 'file_path', 'dir', 'folder',
    'path', 'include_path', 'module', 'controller', 'method', 'class', 'function'
]

def validate_url(url):
    """URLni tekshirish va HTTPS majburlash."""
    url = url.strip()
    if url.startswith('http://'):
        url = 'https://' + url[7:]
    elif not url.startswith('https://'):
        url = 'https://' + url
    try:
        p = urlparse(url)
        if not p.netloc:
            return None
        r = requests.head(url, timeout=5, verify=False)
        if r.status_code < 500:
            return url
        else:
            return url
    except:
        return None

def get_baseline(url, method='GET'):
    """Asosiy so'rovni yuborib, javob xususiyatlarini o'lchash."""
    try:
        if method.upper() == 'GET':
            r = requests.get(url, timeout=5, verify=False)
        else:
            r = requests.post(url, timeout=5, verify=False)
        return {
            'status': r.status_code,
            'length': len(r.content),
            'time': r.elapsed.total_seconds(),
            'text_hash': hash(r.text)
        }
    except:
        return None

def test_param(base_url, param, method='GET'):
    """Bitta parametrni sinash va javob farqini aniqlash."""
    # GET uchun parametrni qo'shamiz
    if method.upper() == 'GET':
        sep = '&' if '?' in base_url else '?'
        test_url = f"{base_url}{sep}{param}=test"
        try:
            r = requests.get(test_url, timeout=5, verify=False, allow_redirects=False)
            return {
                'param': param,
                'url': test_url,
                'status': r.status_code,
                'length': len(r.content),
                'time': r.elapsed.total_seconds(),
                'hash': hash(r.text)
            }
        except:
            return None
    else:
        # POST uchun ma'lumot yuboramiz
        try:
            r = requests.post(base_url, data={param: 'test'}, timeout=5, verify=False, allow_redirects=False)
            return {
                'param': param,
                'url': base_url,
                'status': r.status_code,
                'length': len(r.content),
                'time': r.elapsed.total_seconds(),
                'hash': hash(r.text)
            }
        except:
            return None

def analyze_results(baseline, results, threshold_length=50, threshold_status=1, threshold_time=0.5):
    """Natijalarni taqqoslab, muhim farqlarni qaytarish."""
    findings = []
    if not baseline:
        return findings
    for res in results:
        if not res:
            continue
        # Javob uzunligi sezilarli o'zgargan
        if abs(res['length'] - baseline['length']) > threshold_length:
            findings.append({
                'param': res['param'],
                'type': 'length_change',
                'detail': f"Uzunlik {baseline['length']} -> {res['length']}"
            })
        # Status kod o'zgargan
        if abs(res['status'] - baseline['status']) >= threshold_status:
            findings.append({
                'param': res['param'],
                'type': 'status_change',
                'detail': f"Status {baseline['status']} -> {res['status']}"
            })
        # Javob vaqti sezilarli oshgan
        if res['time'] > baseline['time'] + threshold_time:
            findings.append({
                'param': res['param'],
                'type': 'time_increase',
                'detail': f"Vaqt {baseline['time']:.2f}s -> {res['time']:.2f}s"
            })
    return findings

def run_miner(target_url, method='GET', threads=10, wordlist=None):
    """Asosiy qidiruv funksiyasi."""
    if wordlist is None:
        wordlist = COMMON_PARAMS
    baseline = get_baseline(target_url, method)
    if not baseline:
        print(f"{R}[-] Nishonga ulanishda xato.{W}")
        return []
    print(f"{G}[+] Asosiy javob: Status={baseline['status']}, Uzunlik={baseline['length']} bayt, Vaqt={baseline['time']:.2f}s{W}")
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(test_param, target_url, param, method): param for param in wordlist}
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
    findings = analyze_results(baseline, results)
    return findings

def display_terminal(findings):
    """Terminalda natijalarni chiqarish."""
    if not findings:
        print(f"{Y}[~] Hech qanday yashirin parametr topilmadi.{W}")
        return
    print(f"{G}[+] Topilgan potensial parametrlar:{W}")
    for f in findings:
        if f['type'] == 'length_change':
            print(f"  {G}[LENGTH] {f['param']} — {f['detail']}{W}")
        elif f['type'] == 'status_change':
            print(f"  {M}[STATUS] {f['param']} — {f['detail']}{W}")
        elif f['type'] == 'time_increase':
            print(f"  {Y}[TIME] {f['param']} — {f['detail']}{W}")

def browser_mode():
    """Flask veb-interfeys."""
    if not FLASK_AVAILABLE:
        print(f"{R}Flask o'rnatilmagan. Brauzer rejimi uchun: pip3 install flask{W}")
        return
    app = Flask(__name__)
    app.secret_key = 'YOUR_SECRET_KEY'
    PASSWORD = 'YOUR_PASSWORD'

    HTML_LOGIN = '''
    <h2>Blip Param Miner Login</h2>
    <form method="POST">
    Parol: <input type="password" name="password">
    <input type="submit" value="Kirish">
    </form>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    '''

    HTML_INDEX = '''
    <h1>Blip Param Miner v1.0</h1>
    <form method="POST">
    Nishon URL: <input type="text" name="target" size="40" placeholder="https://example.com">
    <select name="method">
      <option value="GET">GET</option>
      <option value="POST">POST</option>
    </select>
    <input type="submit" value="Qidirish">
    </form>
    {% if results %}
    <h2>Natijalar:</h2>
    <ul>
    {% for f in results %}
      <li>{{ f.param }} — {{ f.type }} ({{ f.detail }})</li>
    {% endfor %}
    </ul>
    {% endif %}
    '''

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            if 'password' in request.form and not session.get('auth'):
                if request.form['password'] == PASSWORD:
                    session['auth'] = True
                else:
                    return render_template_string(HTML_LOGIN, error="Noto'g'ri parol")
            if 'target' in request.form and session.get('auth'):
                target = request.form['target'].strip()
                method = request.form.get('method', 'GET')
                findings = run_miner(target, method)
                return render_template_string(HTML_INDEX, results=findings)
            return render_template_string(HTML_LOGIN, error=None)
        if not session.get('auth'):
            return render_template_string(HTML_LOGIN, error=None)
        return render_template_string(HTML_INDEX, results=None)

    print(f"{G}Brauzer rejimi: http://127.0.0.1:5000{W}")
    app.run(host='127.0.0.1', port=5000, debug=False)

def main():
    print(f"{C}╔══════════════════════════════════════╗{W}")
    print(f"{C}║   BLIP PARAM MINER v1.0              ║{W}")
    print(f"{C}║   Yashirin parametrlarni topish       ║{W}")
    print(f"{C}╚══════════════════════════════════════╝{W}")
    if len(sys.argv) > 1 and sys.argv[1] == 'browser':
        browser_mode()
        return
    print(f"{M}[?] Nishon URL (faqat ruxsat etilgan):{W}")
    target = input(">>> ").strip()
    url = validate_url(target)
    if not url:
        print(f"{R}[-] Noto'g'ri URL yoki HTTPS ulanish muvaffaqiyatsiz.{W}")
        sys.exit(1)
    print(f"{M}[?] Usul (GET/POST, default GET):{W}")
    method = input(">>> ").strip().upper() or 'GET'
    if method not in ['GET', 'POST']:
        method = 'GET'
    print(f"{Y}[*] Qidiruv boshlanmoqda...{W}")
    findings = run_miner(url, method)
    display_terminal(findings)

if __name__ == '__main__':
    main()