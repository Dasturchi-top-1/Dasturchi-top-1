import random
import threading
import requests
from bs4 import BeautifulSoup

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

class KiberSpyApp(App):
    def build(self):
        # Asosiy konteyner (Mobil uchun padding va oraliq masofalar)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        
        # Sarlavha (Katta va yorqin kiber-yashil)
        self.title_label = Label(
            text="🕵️‍♂️ KIBER-AYG'OQCHI",
            font_size='28sp',
            bold=True,
            color=get_color_from_hex("#00FF66"),
            size_hint_y=None,
            height=60
        )
        layout.add_widget(self.title_label)
        
        # Holat paneli (Nima bo'layotganini ko'rsatadi)
        self.status_label = Label(
            text="Tizim tayyor. Ma'lumotni torting...",
            font_size='15sp',
            color=get_color_from_hex("#888888"),
            size_hint_y=None,
            height=30
        )
        layout.add_widget(self.status_label)
        
        # ScrollView (Hikmatlar matni kattalashsa, bemalol barmoq bilan surish uchun)
        scroll = ScrollView(size_hint=(1, 1))
        
        # Matn ko'rsatadigan label
        self.quote_label = Label(
            text="Internetdan eng sara hikmatlarni tortish uchun quyidagi yashil tugmani bosing.",
            font_size='20sp',
            color=get_color_from_hex("#E0E0E0"),
            halign='center',
            valign='middle',
            size_hint_y=None
        )
        # Telefon ekranining kengligiga moslab matnni avtomat qatorga ko'chirish (wrap)
        self.quote_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.quote_label.bind(texture_size=lambda s, t: s.setter('height')(s, t[1]))
        
        scroll.add_widget(self.quote_label)
        layout.add_widget(scroll)
        
        # Tugma (Barmoq bilan bosishga juda qulay, katta tugma)
        self.btn = Button(
            text="MA'LUMOTNI TORTISH",
            font_size='18sp',
            bold=True,
            background_normal='',
            background_color=get_color_from_hex("#1E1E1E"),
            color=get_color_from_hex("#00FF66"),
            size_hint_y=None,
            height=80
        )
        # Tugma bosilganda ishlaydigan funksiya
        self.btn.bind(on_press=self.start_scraping)
        layout.add_widget(self.btn)
        
        return layout

    def start_scraping(self, instance):
        # Tugmani yuklash jarayonida bloklaymiz
        self.btn.disabled = True
        self.status_label.text = "🌐 Serverga ulanmoqda..."
        self.status_label.color = get_color_from_hex("#00FF66")
        
        # Tarmoq so'rovini orqa oqimda (Thread) bajaramiz
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        url = "http://quotes.toscrape.com/"
        try:
            response = requests.get(url, timeout=7)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            quotes = soup.find_all("div", class_="quote")
            
            if quotes:
                chosen = random.choice(quotes)
                text = chosen.find("span", class_="text").text
                author = chosen.find("small", class_="author").text
                
                # Kivy asosiy oqimida UI ni xavfsiz yangilash
                Clock.schedule_once(lambda dt: self.update_ui(text, author), 0)
            else:
                Clock.schedule_once(lambda dt: self.update_ui_error("Ma'lumot topilmadi!"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_ui_error("Internet xatoligi!"), 0)

    def update_ui(self, text, author):
        self.quote_label.text = f'"{text}"\n\n✍️ Muallif: {author}'
        self.status_label.text = "✅ Ma'lumot muvaffaqiyatli yuklandi!"
        self.status_label.color = get_color_from_hex("#00FF00")
        self.btn.disabled = False

    def update_ui_error(self, err_msg):
        self.quote_label.text = "Internet aloqasini tekshirib, qayta urinib ko'ring."
        self.status_label.text = f"❌ {err_msg}"
        self.status_label.color = get_color_from_hex("#FF3333")
        self.btn.disabled = False

if __name__ == '__main__':
    KiberSpyApp().run()