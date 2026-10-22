# ==========================================
# LOYIHA: CYBER WEB SCANNER v2.0
# PLATFORMA: Python (Pydroid 3)
# ==========================================

import urllib.error
import urllib.request


def scan_website(url_input):
  # 1. URL manzilini to'g'ri formatga keltiramiz
  url_input = url_input.strip().lower()

  if not url_input.startswith(('http://', 'https://')):
    url = 'https://' + url_input
  else:
    url = url_input

  # Agar foydalanuvchi domen qo'shmagan bo'lsa (.com, .org kabi), avtomatik .com qo'shamiz
  domain_part = url.split('://')[-1].split('/')[0]
  if '.' not in domain_part:
    url = url + '.com'

  print(f"\n🔍 Sayt skanerlanmoqda: {url}")
  print('-' * 50)

  try:
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CyberScanner/2.0'
            )
        },
    )

    with urllib.request.urlopen(req, timeout=10) as response:
      headers = response.info()

      print('✅ Saytga muvaffaqiyatli ulanildi!')
      print(f'📊 Javob kodi: {response.getcode()}')
      print('-' * 50)
      print('🛡️ XAVFSIZLIK SARLAVHALARI (HEADERS) TEKSHIRUVI:\n')

      # Asosiy xavfsizlik headerlarini tekshiramiz
      security_headers = {
          'Strict-Transport-Security': 'HSTS (HTTPS majburiyligi)',
          'X-Frame-Options': 'Clickjacking himoyasi',
          'X-Content-Type-Options': 'MIME-sniffing himoyasi',
          'Content-Security-Policy': 'XSS va Inyeksiya himoyasi',
          'Referrer-Policy': 'Referrer ma\'lumotlar himoyasi',
      }

      missing_headers = []
      found_headers = []

      for header, desc in security_headers.items():
        if header in headers:
          found_headers.append(f"  🟢 {header} -> {desc} (O'RNATILGAN)")
        else:
          missing_headers.append(f"  🔴 {header} -> {desc} (YO'Q)")

      for item in found_headers:
        print(item)
      for item in missing_headers:
        print(item)

      print('-' * 50)

      if not missing_headers:
        print(
            '🎉 O\'rmon tinch! Saytda barcha asosiy xavfsizlik sarlavhalari'
            ' o\'rnatilgan.'
        )
      else:
        print(
            f'⚠️ DIQQAT: Saytda {len(missing_headers)} ta xavfsizlik sarlavhasi'
            ' yetishmayapti!'
        )

  except urllib.error.URLError as e:
    print(f'❌ Ulanishda xatolik yuz berdi: {e.reason}')
    print('💡 Maslahat: Sayt nomini to\'g\'ri kiritganingizni tekshiring.')
  except Exception as e:
    print(f'❌ Kutilmagan xatolik: {e}')


# --- DASTUR MENYUSI ---
print('🛡️ CYBER WEB SCANNER & REPORT GENERATOR 🛡️')
print('-' * 50)
target = input(
    'Skanerlash uchun sayt manzilini kiriting (masalan: openai, google.com): '
)

if target:
  scan_website(target)
else:
  print('❌ Manzil kiritilmadi!')
