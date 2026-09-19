# ==========================================================
# LOYIHA: HAFTALIK DUNYO YANGILIKLARI YIG'UVCHI
# PLATFORMA: Python (Pydroid 3 / Termux / PC)
# FUNKSIYA: RSS manbalardan so'nggi 7 kunlik yangiliklarni yig'adi
# ==========================================================

import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

# Dunyo yangiliklari RSS manbalari (bepul, ro'yxatdan o'tish shart emas)
RSS_SOURCES = {
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "CNN World": "http://rss.cnn.com/rss/edition_world.rss",
    "NPR World": "https://feeds.npr.org/1004/rss.xml",
}


def fetch_rss(url, source_name):
    """Bitta RSS manbadan yangiliklarni yuklab, ro'yxat qilib qaytaradi"""
    news_items = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 NewsCollector/1.0'})
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
                except Exception:
                    pub_date = None

            news_items.append({
                'source': source_name,
                'title': title,
                'link': link,
                'date': pub_date,
            })

    except urllib.error.URLError as e:
        print(f"  ❌ {source_name}: ulanish xatosi ({e.reason})")
    except ET.ParseError:
        print(f"  ❌ {source_name}: RSS formatini o'qib bo'lmadi")
    except Exception as e:
        print(f"  ❌ {source_name}: kutilmagan xato ({e})")

    return news_items


def filter_last_week(news_items):
    """Faqat so'nggi 7 kunlik yangiliklarni ajratib oladi"""
    now = datetime.now(tz=None)
    week_ago = now - timedelta(days=7)
    filtered = []

    for item in news_items:
        if item['date'] is None:
            # Sana aniqlanmasa ham, ro'yxatga qo'shamiz (ehtiyot chorasi)
            filtered.append(item)
            continue

        item_date = item['date'].replace(tzinfo=None)
        if item_date >= week_ago:
            filtered.append(item)

    return filtered


def collect_weekly_news():
    print("🌍 HAFTALIK DUNYO YANGILIKLARI YIG'ILMOQDA...")
    print("=" * 60)

    all_news = []

    for source_name, url in RSS_SOURCES.items():
        print(f"\n📡 {source_name} manbasidan yuklanmoqda...")
        items = fetch_rss(url, source_name)
        weekly_items = filter_last_week(items)
        all_news.extend(weekly_items)
        print(f"  ✅ {len(weekly_items)} ta yangilik topildi")

    return all_news


def display_news(news_list):
    print("\n" + "=" * 60)
    print(f"📰 JAMI {len(news_list)} TA YANGILIK (so'nggi 7 kun)")
    print("=" * 60)

    # Manba bo'yicha guruhlab ko'rsatamiz
    grouped = {}
    for item in news_list:
        grouped.setdefault(item['source'], []).append(item)

    for source, items in grouped.items():
        print(f"\n🔹 {source} ({len(items)} ta yangilik):\n")
        for i, item in enumerate(items[:10], 1):  # har bir manbadan max 10 ta ko'rsatamiz
            date_str = item['date'].strftime('%d.%m.%Y %H:%M') if item['date'] else "Sana noma'lum"
            print(f"  {i}. {item['title']}")
            print(f"     🕐 {date_str}")
            print(f"     🔗 {item['link']}\n")


def save_to_file(news_list, filename="haftalik_yangiliklar.txt"):
    """Yangiliklarni matn fayliga saqlaydi"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"HAFTALIK DUNYO YANGILIKLARI\n")
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
    weekly_news = collect_weekly_news()

    # Sana bo'yicha eng yangilaridan boshlab tartiblaymiz
    weekly_news.sort(key=lambda x: x['date'] or datetime.min, reverse=True)

    display_news(weekly_news)

    save_choice = input("\n💾 Natijani faylga saqlaymi? (ha/yo'q): ").strip().lower()
    if save_choice in ('ha', 'h', 'yes', 'y'):
        save_to_file(weekly_news)

    print("\n✅ Tayyor!")
