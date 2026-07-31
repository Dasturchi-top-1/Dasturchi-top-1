# ==========================================
# LOYIHA: Global Translator App Inspector v4.0
# PLATFORMA: Python (Pydroid 3)
# ==========================================

import json
import urllib.parse
import urllib.request


def translate_text(text, target_lang='uz'):
  """Google Translate orqali matnni avtomatik o'zbek tiliga tarjima qiladi"""
  try:
    encoded_text = urllib.parse.quote(text)
    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={encoded_text}'
    req = urllib.request.Request(
        url, headers={'User-Agent': 'Mozilla/5.0 Translator'}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
      res_data = json.loads(response.read().decode('utf-8'))
      # Tarjima qilingan qismlarni birlashtiramiz
      translated_sentence = ''.join(
          [item[0] for item in res_data[0] if item[0]]
      )
      return translated_sentence
  except:
    return text  # Tarjimada xato bo'lsa asl matnni qaytaradi


def search_global_internet(app_name):
  print(f'\n🌍 Global internetdan qidirilmoqda: \'{app_name}\'...')
  print('-' * 50)

  # Inglizcha Wikipedia API (eng boy baza)
  encoded_query = urllib.parse.quote(app_name)
  url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&format=json'

  try:
    req = urllib.request.Request(
        url, headers={'User-Agent': 'Mozilla/5.0 GlobalInspector'}
    )
    with urllib.request.urlopen(req, timeout=8) as response:
      data = json.loads(response.read().decode('utf-8'))
      search_results = data.get('query', {}).get('search', [])

      if not search_results:
        print(f'❌ Kechirasiz, \'{app_name}\' bo\'yicha hech qanday ma\'lumot topilmadi.')
        return

      top_result = search_results[0]
      title = top_result['title']
      pageid = top_result['pageid']

      # Sahifaning inglizcha matnini tortib olamiz
      summary_url = f'https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&pageids={pageid}&format=json'
      req_summary = urllib.request.Request(
          summary_url, headers={'User-Agent': 'Mozilla/5.0 GlobalInspector'}
      )

      with urllib.request.urlopen(req_summary, timeout=8) as sum_response:
        sum_data = json.loads(sum_response.read().decode('utf-8'))
        pages = sum_data.get('query', {}).get('pages', {})
        page_content = pages.get(str(pageid), {}).get(
            'extract', 'Ma\'lumot topilmadi.'
        )

        print(f'🎯 TOPILGAN MANBA: {title}')
        print('⏳ Ma\'lumot o\'zbek tiliga tarjima qilinmoqda...')
        print('=' * 50)

        # Matnni o'zbek tiliga tarjima qilamiz
        translated_title = translate_text(title, 'uz')
        translated_content = translate_text(page_content, 'uz')

        print(f'🇺🇿 Sarlavha: {translated_title}')
        print(f'📜 Ma\'lumot:\n{translated_content}\n')
        print('=' * 50)
        print('✅ Ma\'lumot ingliz tilidan o\'zbek tiliga tarjima qilib olib kelindi!')

  except Exception as e:
    print(
        f'❌ Internetga ulanishda xatolik yuz berdi: {e}\n(Tarmoq ulanishini'
        ' tekshiring)'
    )


# --- DASTUR MENYUSI ---
print('🛡️ GLOBAL TRANSLATOR APP INSPECTOR 🛡️')
print('-' * 50)
target = input(
    'Ilova, o\'yin yoki kompaniya nomini kiriting (masalan: Microsoft, Claude, Roblox): '
).strip()

if target:
  search_global_internet(target)
else:
  print('❌ Nom kiritilmadi!')
