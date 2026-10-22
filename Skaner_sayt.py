# ==========================================
# LOYIHA: SQLi ZAIFLIK ANIQLOVCHI (Passiv skaner)
# PLATFORMA: Python (Pydroid 3)
# ESLATMA: Faqat OZINGIZGA tegishli yoki YOZMA ruxsat
#          berilgan saytlarni tekshiring!
# ==========================================

import urllib.error
import urllib.parse
import urllib.request


# Zararsiz "sinov belgilar" - bular ma'lumotni o'zgartirmaydi,
# faqat serverning qanday reaksiya berishini kuzatamiz
TEST_PAYLOADS = [
    "'Blip",
    "''Blip",
    '"Blip',
    "`Blip",
    "')Blip",
    "';Blip",
]

# Ma'lumotlar bazasi xatoligini bildiruvchi tipik so'zlar
ERROR_SIGNATURES = [
    "sql syntax",
    "mysql_fetch",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "sqlstate",
    "ora-01756",
    "postgresql query failed",
    "sqlite3.operationalerror",
    "odbc sql server driver",
    "microsoft ole db provider",
    "warning: mysql",
    "valid mysql result",
]


def test_url_parameter(base_url, param_name):
    """Bitta URL parametrini sinov belgilar bilan tekshiradi"""
    results = []

    for payload in TEST_PAYLOADS:
        try:
            # Parametr qiymatini payload bilan almashtiramiz
            parsed = urllib.parse.urlparse(base_url)
            query = urllib.parse.parse_qs(parsed.query)
            query[param_name] = payload
            new_query = urllib.parse.urlencode(query, doseq=True)
            test_url = urllib.parse.urlunparse(parsed._replace(query=new_query))

            req = urllib.request.Request(
                test_url,
                headers={
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/120.0 Safari/537.36'
                    )
                },
            )

            with urllib.request.urlopen(req, timeout=20) as response:
                body = response.read().decode('utf-8', errors='ignore').lower()

                found_signature = None
                for sig in ERROR_SIGNATURES:
                    if sig in body:
                        found_signature = sig
                        break

                results.append({
                    'payload': payload,
                    'status': response.getcode(),
                    'suspicious': found_signature is not None,
                    'signature': found_signature,
                })

        except urllib.error.HTTPError as e:
            # Ba'zan xato sahifasi ham signature'ni o'z ichiga olishi mumkin
            try:
                body = e.read().decode('utf-8', errors='ignore').lower()
                found_signature = next((s for s in ERROR_SIGNATURES if s in body), None)
            except Exception:
                found_signature = None

            results.append({
                'payload': payload,
                'status': e.code,
                'suspicious': found_signature is not None,
                'signature': found_signature,
            })
        except Exception as e:
            results.append({
                'payload': payload,
                'status': 'XATO',
                'suspicious': False,
                'signature': None,
                'error': str(e),
            })

    return results


def scan_for_sqli(url):
    print(f"\n🔍 SQLi zaiflik tekshiruvi: {url}")
    print('=' * 55)

    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed.query)

    if not query_params:
        print("⚠️  URL'da so'rov parametrlari (?param=value) topilmadi.")
        print("💡 Masalan: https://example.com/page?id=1")
        return

    print(f"📋 Topilgan parametrlar: {list(query_params.keys())}\n")

    total_suspicious = 0

    for param in query_params.keys():
        print(f"--- Parametr: '{param}' ---")
        results = test_url_parameter(url, param)

        for r in results:
            if r['suspicious']:
                print(f"  🔴 Payload: {r['payload']:10s} -> SHUBHALI! (belgisi: '{r['signature']}')")
                total_suspicious += 1
            elif r['status'] == 'XATO':
                print(f"  ⚪ Payload: {r['payload']:10s} -> Ulanish xatosi ({r.get('error', '')})")
            else:
                print(f"  🟢 Payload: {r['payload']:10s} -> Normal (status: {r['status']})")
        print()

    print('=' * 55)
    print('📋 YAKUNIY HISOBOT')
    print('=' * 55)

    if total_suspicious > 0:
        print(f"⚠️  DIQQAT: {total_suspicious} ta shubhali holat aniqlandi!")
        print("   Bu SQLi zaifligi borligini KAFOLATLAMAYDI — qo'lda tekshirish")
        print("   yoki sqlmap kabi professional vosita bilan tasdiqlash tavsiya etiladi.")
    else:
        print("✅ Shubhali xato xabarlari topilmadi.")
        print("   (Bu sayt 100% xavfsiz degani emas — chuqurroq test kerak bo'lishi mumkin)")


# --- DASTUR MENYUSI ---
if __name__ == '__main__':
    print('🛡️  SQL INJECTION ZAIFLIK ANIQLOVCHI 🛡️')
    print('=' * 55)
    print("⚠️  FAQAT o'zingizga tegishli yoki YOZMA ruxsat berilgan")
    print("    saytlarni tekshiring! Ruxsatsiz test - jinoiy javobgarlik.")
    print('=' * 55)

    target = input(
        "\nTo'liq URL kiriting (parametr bilan, masalan:\n"
        "https://example.com/page.php?id=1\n> "
    )

    if target and '?' in target:
        scan_for_sqli(target)
    else:
        print("❌ To'g'ri URL kiritilmadi yoki parametr yo'q (?id=1 kabi kerak)")
