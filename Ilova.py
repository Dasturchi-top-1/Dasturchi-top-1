# ==========================================
# LOYIHA: Global Translator App Inspector v5.2
# PLATFORMA: Python (Pydroid 3 / Termux)
# ==========================================

import json
import os
import re
import urllib.parse
import urllib.request


def translate_text(text, target_lang='uz'):
  """Google Translate API orqali matnni o'zbek tiliga o'giradi"""
  if not text or text == "Ma'lumot topilmadi.":
    return text

  try:
    encoded_text = urllib.parse.quote(text)
    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={encoded_text}'
    req = urllib.request.Request(
        url, headers={'User-Agent': 'Mozilla/5.0 Translator'}
    )
    with urllib.request.urlopen(req, timeout=6) as response:
      res_data = json.loads(response.read().decode('utf-8'))
      return ''.join([item[0] for item in res_data[0] if item[0]])
  except:
    return text


def fetch_wiki_data(query, lang):
  """Ko'rsatilgan tildagi Wikipedia API'dan ma'lumot izlaydi"""
  encoded_query = urllib.parse.quote(query)
  search_url = f'https://{lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&format=json'

  try:
    req = urllib.request.Request(
        search_url, headers={'User-Agent': 'Mozilla/5.0 GlobalInspector'}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
      data = json.loads(response.read().decode('utf-8'))
      results = data.get('query', {}).get('search', [])

      if not results:
        return None

      top_result = results[0]
      pageid = top_result['pageid']
      title = top_result['title']

      # Matn xulosasini tortish
      summary_url = f'https://{lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&pageids={pageid}&format=json'
      req_summary = urllib.request.Request(
          summary_url, headers={'User-Agent': 'Mozilla/5.0 GlobalInspector'}
      )

      with urllib.request.urlopen(req_summary, timeout=5) as sum_response:
        sum_data = json.loads(sum_response.read().decode('utf-8'))
        pages = sum_data.get('query', {}).get('pages', {})
        content = pages.get(str(pageid), {}).get(
            'extract', "Ma'lumot topilmadi."
        )

        return {'title': title, 'content': content, 'lang': lang}
  except:
    return None


def save_to_file(app_name, title, content, source_lang):
  """Natijalarni Download papkasiga .txt fayl qilib saqlash funksiyasi"""
  clean_filename = re.sub(r'[\\/*?:"<>|]', '', app_name).strip()
  filename = f'{clean_filename}.txt'

  # Ichki xotiradagi Download papkasi yo'li
  download_path = '/storage/emulated/0/Download'

  if os.path.exists(download_path):
    filepath = os.path.join(download_path, filename)
  else:
    filepath = filename

  file_text = (
      '==================================================\n'
      '🛡️ GLOBAL TRANSLATOR APP INSPECTOR REPORT 🛡️\n'
      '==================================================\n'
      f'🎯 Qidirilgan nom: {app_name}\n'
      f'📌 Manba sarlavhasi: {title} ({source_lang}-Wikipedia)\n'
      '--------------------------------------------------\n'
      "🇺🇿 MA'LUMOT (O'ZBEK TILIDA):\n\n"
      f'{content}\n'
      '==================================================\n'
  )

  try:
    with open(filepath, 'w', encoding='utf-8') as file:
      file.write(file_text)
    print('\n💾 Natija muvaffaqiyatli saqlandi!')
    print(f'📍 Fayl manzili: {filepath}')
  except PermissionError:
    print(
        "\n❌ Xatolik: Pydroid 3 ilovasiga xotiradan (Storage) foydalanishga"
        ' ruxsat berilmagan!'
    )
  except Exception as e:
    print(f'\n❌ Faylga saqlashda xatolik yuz berdi: {e}')


def search_global_internet(app_name):
  print(f"\n🌍 Qidirilmoqda: '{app_name}'...")
  print('-' * 50)

  clean_name = re.sub(
      r'\.(tj|uz|com|ru|org|net|io|app|dev)$', '', app_name, flags=re.IGNORECASE
  ).strip()

  languages = ['uz', 'tg', 'ru', 'en']
  result = None

  for lang in languages:
    result = fetch_wiki_data(app_name, lang=lang)
    if result:
      break

  if not result and clean_name != app_name:
    for lang in languages:
      result = fetch_wiki_data(clean_name, lang=lang)
      if result:
        break

  if result:
    source_lang = result['lang'].upper()
    title = result['title']
    content = result['content']

    print(f'🎯 TOPILGAN MANBA: {title} ({source_lang}-Wikipedia)')

    if app_name.lower() not in title.lower():
      print(
          f"💡 Eslatma: '{app_name}' uchun alohida sahifa bo'lmagani sababli,"
          f" unga bog'liq eng yaqin manba ({title}) ko'rsatilmoqda."
      )

    print("⏳ Ma'lumot o'zbek tiliga tayyorlanmoqda...")
    print('=' * 50)

    # Tarjima qilish
    if result['lang'] != 'uz':
      translated_title = translate_text(title, 'uz')
      translated_content = translate_text(content, 'uz')
      final_title = translated_title
      final_content = translated_content
      print(f'🇺🇿 Sarlavha: {final_title}')
      print(f'📜 Ma\'lumot:\n{final_content}\n')
      print('=' * 50)
      print(f"✅ Ma'lumot {source_lang} tilidan o'zbek tiliga tarjima qilindi!")
    else:
      final_title = title
      final_content = content
      print(f'🇺🇿 Sarlavha: {final_title}')
      print(f'📜 Ma\'lumot:\n{final_content}\n')
      print('=' * 50)
      print("✅ Ma'lumot o'zbekcha manbadan to'g'ridan-to'g'ri olindi!")

    # TXT FAYLGA SAQLASH
    save_to_file(app_name, final_title, final_content, source_lang)

  else:
    print(
        f"❌ Kechirasiz, '{app_name}' bo'yicha hech qaysi tilda ma'lumot"
        ' topilmadi.'
    )


# --- DASTUR MENYUSI ---
print('🛡️ GLOBAL TRANSLATOR APP INSPECTOR v5.2 🛡️')
print('-' * 50)
target = input("Ilova, o'yin yoki kompaniya nomini kiriting: ").strip()

if target:
  search_global_internet(target)
else:
  print('❌ Nom kiritilmadi!')
