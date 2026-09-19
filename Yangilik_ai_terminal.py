# ==========================================================
# LOYIHA: AI (SUN'IY INTELLEKT) YANGILIKLARI - O'ZBEK TILIDA
# PLATFORMA: Python (Pydroid 3)
# FUNKSIYA: 1) Ingliz AI manbalaridan yangilik olib, o'zbekchaga tarjima qiladi
#           2) To'g'ridan-to'g'ri o'zbek tilidagi AI yangiliklarini qidiradi
# ==========================================================

import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

# Ingliz tilidagi AI-fokusli manbalar
ENGLISH_AI_SOURCES = {
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
}

# O'zbek tilida AI yangiliklarini qidirish (Google News orqali, manba ko'rsatiladi)
UZBEK_SEARCH_URL = "https://news.google.com/rss/search?q=sun%27iy+intellekt&hl=uz&gl=UZ&ceid=UZ:uz"


def translate_to_uzbek(text):
    """Matnni bepul (norasmiy) Google Translate orqali o'zbekchaga tarjima qiladi"""
    try:
        params = urllib.parse.urlencode({
            'client': 'gtx', 'sl': 'en', 'tl': 'uz', 'dt': 't', 'q': text,
        })
        url = f"https://translate.googleapis.com/translate_a/single?{params}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        # Tarjima bo'laklarini birlashtiramiz
        translated = ''.join(part[0] for part in data[0])
        return translated
    except Exception:
        return text  # Tarjima ishlamasa, asl matnni qaytaradi


def fetch_rss(url, source_name, needs_translation=False):
    """RSS manbadan yangiliklarni yuklaydi, kerak bo'lsa tarjima qiladi"""
    news_items = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 AINewsCollector/1.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

        for item in root.findall('.//item'):
            title = item.findtext('title', default='').strip()
            link = item.findtext('link', default='').strip()
            pub_date_str = item.findtext('pubDate', default='')

            pub_date = None
            if pub_date_str:
                try:
                    pub_date = parsedate_to_datetime(pub_date_str)
                    if pub_date.tzinfo is not None:
                        pub_date = pub_date.replace(tzinfo=None)
                except Exception:
                    pub_date = None

            original_title = title
            if needs_translation:
                title = translate_to_uzbek(title)

            news_items.append({
                'source': source_name,
                'title': title,
                'original_title': original_title if needs_translation else None,
                'link': link,
                'date': pub_date,
            })

    except Exception as e:
        print(f"  ❌ {source_name}: xato ({e})")

    return news_items


def filter_last_week(news_items):
    week_ago = datetime.now() - timedelta(days=7)
    return [it for it in news_items if it['date'] is None or it['date'] >= week_ago]


def collect_ai_news():
    print("🤖 AI (SUN'IY INTELLEKT) YANGILIKLARI YIG'ILMOQDA...")
    print("=" * 60)

    all_news = []

    # 1. Ingliz manbalardan - tarjima bilan
    for source_name, url in ENGLISH_AI_SOURCES.items():
        print(f"\n📡 {source_name} (ingliz, tarjima qilinadi)...")
        items = fetch_rss(url, source_name, needs_translation=True)
        weekly = filter_last_week(items)
        all_news.extend(weekly)
        print(f"  ✅ {len(weekly)} ta yangilik topildi va tarjima qilindi")

    # 2. O'zbek tilidagi manbalar - to'g'ridan-to'g'ri
    print(f"\n📡 O'zbek manbalar (Google News orqali qidirilmoqda)...")
    uz_items = fetch_rss(UZBEK_SEARCH_URL, "O'zbek AI yangiliklari", needs_translation=False)
    weekly_uz = filter_last_week(uz_items)
    all_news.extend(weekly_uz)
    print(f"  ✅ {len(weekly_uz)} ta o'zbekcha yangilik topildi")

    all_news.sort(key=lambda x: x['date'] or datetime.min, reverse=True)
    return all_news


def display_news(news_list):
    print("\n" + "=" * 60)
    print(f"📰 JAMI {len(news_list)} TA AI YANGILIGI (so'nggi 7 kun)")
    print("=" * 60)

    grouped = {}
    for item in news_list:
        grouped.setdefault(item['source'], []).append(item)

    for source, items in grouped.items():
        print(f"\n🔹 {source} ({len(items)} ta):\n")
        for i, item in enumerate(items[:10], 1):
            date_str = item['date'].strftime('%d.%m.%Y %H:%M') if item['date'] else "Sana noma'lum"
            print(f"  {i}. {item['title']}")
            if item.get('original_title'):
                print(f"     (asl: {item['original_title']})")
            print(f"     🕐 {date_str}")
            print(f"     🔗 {item['link']}\n")


def save_to_file(news_list, filename="ai_yangiliklari.txt"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("AI (SUN'IY INTELLEKT) YANGILIKLARI\n")
            f.write(f"Yig'ilgan sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
            f.write("=" * 60 + "\n\n")

            for item in news_list:
                date_str = item['date'].strftime('%d.%m.%Y %H:%M') if item['date'] else "Sana noma'lum"
                f.write(f"[{item['source']}] {item['title']}\n")
                f.write(f"Sana: {date_str}\n")
                f.write(f"Havola: {item['link']}\n")
                f.write("-" * 60 + "\n")

        print(f"\n💾 Yangiliklar '{filename}' fayliga saqlandi!")
    except Exception as e:
        print(f"\n⚠️  Faylga saqlashda xato: {e}")


# --- DASTUR MENYUSI ---
if __name__ == '__main__':
    ai_news = collect_ai_news()
    display_news(ai_news)

    save_choice = input("\n💾 Natijani faylga saqlaymi? (ha/yo'q): ").strip().lower()
    if save_choice in ('ha', 'h', 'yes', 'y'):
        save_to_file(ai_news)

    print("\n✅ Tayyor!")
