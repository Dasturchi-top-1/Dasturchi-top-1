# ==========================================
# LOYIHA: CYBER WEB SCANNER v3.0
# PLATFORMA: Python (Pydroid 3)
# YANGI: SSL tekshiruvi, Redirect kuzatish, To'liq hisobot
# ==========================================

import ssl
import socket
import urllib.error
import urllib.request
from datetime import datetime


def check_ssl(hostname, port=443):
    """SSL sertifikatini tekshiradi"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()

                expire_str = cert.get('notAfter')
                expire_date = datetime.strptime(expire_str, '%b %d %H:%M:%S %Y %Z')
                days_left = (expire_date - datetime.now()).days

                return {
                    'valid': True,
                    'issuer': dict(x[0] for x in cert.get('issuer', [])).get('organizationName', 'Noma\'lum'),
                    'expire_date': expire_date.strftime('%Y-%m-%d'),
                    'days_left': days_left,
                    'protocol': cipher[1] if cipher else 'Noma\'lum',
                }
    except ssl.SSLCertVerificationError as e:
        return {'valid': False, 'error': f'Sertifikat xato: {e.reason}'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}


def scan_website(url_input):
    url_input = url_input.strip().lower()

    if not url_input.startswith(('http://', 'https://')):
        url = 'https://' + url_input
    else:
        url = url_input

    domain_part = url.split('://')[-1].split('/')[0]
    if '.' not in domain_part:
        url = url + '.com'
        domain_part = domain_part + '.com'

    hostname = domain_part.split(':')[0]

    print(f"\n🔍 Sayt skanerlanmoqda: {url}")
    print('=' * 55)

    # --- 1. ULANISH VA HEADERLAR ---
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CyberScanner/3.0'
                )
            },
            method='HEAD',
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            headers = response.info()
            final_url = response.geturl()

            print('✅ Saytga muvaffaqiyatli ulanildi!')
            print(f'📊 Javob kodi: {response.getcode()}')

            if final_url != url:
                print(f'↪️  Redirect aniqlandi: {url} -> {final_url}')

            print('-' * 55)
            print('🛡️  XAVFSIZLIK SARLAVHALARI (HEADERS) TEKSHIRUVI:\n')

            security_headers = {
                'Strict-Transport-Security': 'HSTS (HTTPS majburiyligi)',
                'X-Frame-Options': 'Clickjacking himoyasi',
                'X-Content-Type-Options': 'MIME-sniffing himoyasi',
                'Content-Security-Policy': 'XSS va Inyeksiya himoyasi',
                'Referrer-Policy': "Referrer ma'lumotlar himoyasi",
                'Permissions-Policy': 'Brauzer funksiyalarini cheklash',
            }

            found = 0
            for header, desc in security_headers.items():
                if header in headers:
                    print(f"  🟢 {header:30s} -> {desc} (O'RNATILGAN)")
                    found += 1
                else:
                    print(f"  🔴 {header:30s} -> {desc} (YO'Q)")

            score = round((found / len(security_headers)) * 100)

            print('-' * 55)
            print(f'📈 Xavfsizlik headerlari darajasi: {found}/{len(security_headers)} ({score}%)')

            # Server ma'lumoti (agar oshkor qilingan bo'lsa)
            server_info = headers.get('Server')
            if server_info:
                print(f"\n⚠️  Server texnologiyasi oshkor qilingan: {server_info}")
                print('   (Bu ma\'lumot xakerlarga foydali bo\'lishi mumkin, yashirish tavsiya etiladi)')

    except urllib.error.HTTPError as e:
        print(f'⚠️  HTTP xatolik: {e.code} - {e.reason}')
    except urllib.error.URLError as e:
        print(f'❌ Ulanishda xatolik yuz berdi: {e.reason}')
        print('💡 Maslahat: Sayt nomini to\'g\'ri kiritganingizni tekshiring.')
        return
    except Exception as e:
        print(f'❌ Kutilmagan xatolik: {e}')
        return

    # --- 2. SSL SERTIFIKAT TEKSHIRUVI ---
    print('-' * 55)
    print('🔒 SSL SERTIFIKAT TEKSHIRUVI:\n')

    ssl_result = check_ssl(hostname)
    if ssl_result['valid']:
        print(f"  🟢 Sertifikat holati: Amal qiladi")
        print(f"  📅 Muddati tugaydi: {ssl_result['expire_date']} ({ssl_result['days_left']} kun qoldi)")
        print(f"  🏢 Beruvchi: {ssl_result['issuer']}")
        print(f"  🔐 Protokol: {ssl_result['protocol']}")

        if ssl_result['days_left'] < 30:
            print("  ⚠️  DIQQAT: Sertifikat tez orada tugaydi!")
    else:
        print(f"  🔴 SSL xatolik: {ssl_result.get('error', 'Noma\'lum xato')}")

    # --- 3. YAKUNIY XULOSA ---
    print('=' * 55)
    print('📋 YAKUNIY HISOBOT')
    print('=' * 55)
    if score == 100 and ssl_result['valid']:
        print('🎉 Ajoyib! Sayt yaxshi himoyalangan.')
    elif score >= 60:
        print('👍 Yaxshi, lekin yaxshilash uchun joy bor.')
    else:
        print('⚠️  Diqqat! Saytda jiddiy xavfsizlik kamchiliklari bor.')


# --- DASTUR MENYUSI ---
if __name__ == '__main__':
    print('🛡️  CYBER WEB SCANNER & REPORT GENERATOR v3.0 🛡️')
    print('=' * 55)
    print('⚠️  Faqat o\'zingizga tegishli yoki ruxsat berilgan saytlarni skanerlang!')
    print('=' * 55)

    target = input(
        '\nSkanerlash uchun sayt manzilini kiriting (masalan: openai.com): '
    )

    if target:
        scan_website(target)
    else:
        print('❌ Manzil kiritilmadi!')
