#!/usr/bin/env python3
# ==========================================================
# LOYIHA: JARVIS - SUHBAT + ILOVA OCHISH
# PLATFORMA: Termux (Android)
# FUNKSIYA: Erkin suhbat (AI) + "...ni och" desangiz, ilovani ochadi
# ==========================================================

import subprocess
import requests

# ==========================================================
# SOZLAMALAR
# ==========================================================
OPENROUTER_API_KEY = "YOUR_OPENROUTER_KEY"
AI_MODEL = "deepseek/deepseek-v4-flash"

# Ilova nomi (o'zbekcha, siz aytadigan) -> Android paket nomi
# Ro'yxatga o'zingizga kerak ilovalarni qo'shishingiz mumkin
APP_PACKAGES = {
    "telegram": "org.telegram.messenger",
    "whatsapp": "com.whatsapp",
    "instagram": "com.instagram.android",
    "youtube": "com.google.android.youtube",
    "chrome": "com.android.chrome",
    "brauzer": "com.android.chrome",
    "kamera": "com.android.camera",
    "galereya": "com.google.android.apps.photos",
    "sozlamalar": "com.android.settings",
    "play market": "com.android.vending",
    "gmail": "com.google.android.gm",
    "xarita": "com.google.android.apps.maps",
    "maps": "com.google.android.apps.maps",
    "facebook": "com.facebook.katana",
    "tiktok": "com.zhiliaoapp.musically",
    "spotify": "com.spotify.music",
    "pydroid": "ru.iiec.pydroid3",
}


def open_app(package_name):
    """Android ilovasini paket nomi orqali ochadi (root talab qilmaydi)"""
    try:
        result = subprocess.run(
            ['monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def find_app_in_text(text):
    """Foydalanuvchi matnida qaysi ilova nomi borligini qidiradi"""
    lower = text.lower()
    for app_name, package in APP_PACKAGES.items():
        if app_name in lower:
            return app_name, package
    return None, None


class AIBrain:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        self.history = [
            {"role": "system", "content": "Sen Jarvis ismli yordamchisan. Qisqa va aniq javob ber."}
        ]

    def ask(self, text):
        self.history.append({"role": "user", "content": text})
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": self.history},
                timeout=30,
            )
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"Kechirasiz, xato yuz berdi: {e}"


OPEN_KEYWORDS = ['och', 'ochib ber', 'ishga tushir', 'kirit']


def handle_command(text, brain):
    lower = text.lower()

    # "och" so'zi bormi va ilova nomi aniqlanganmi - tekshiramiz
    if any(kw in lower for kw in OPEN_KEYWORDS):
        app_name, package = find_app_in_text(text)
        if package:
            success = open_app(package)
            if success:
                return f"{app_name.capitalize()} ochilmoqda."
            else:
                return f"{app_name.capitalize()}ni ochib bo'lmadi. O'rnatilganligini tekshiring."
        else:
            available = ', '.join(sorted(set(APP_PACKAGES.keys())))
            return f"Qaysi ilovani nazarda tutganingizni tushunmadim. Mavjud ilovalar: {available}"

    # Aks holda - erkin savol, AI'ga yuboramiz
    return brain.ask(text)


def main():
    print("🤖 JARVIS - SUHBAT + ILOVA OCHISH 🤖")
    print("=" * 50)
    print("Misol: 'Telegram'ni och', yoki 'Havo qanday?' kabi savol bering.")
    print("Chiqish uchun: 'chiqish' deb yozing.\n")

    if OPENROUTER_API_KEY == "SIZNING_API_KALITINGIZ":
        print("⚠️  Avval OPENROUTER_API_KEY ni sozlang!")
        return

    brain = AIBrain(OPENROUTER_API_KEY, AI_MODEL)

    while True:
        user_text = input("👤 Siz: ").strip()

        if not user_text:
            continue
        if user_text.lower() in ('chiqish', 'exit', "to'xta", 'stop'):
            print("🤖 Jarvis: Xayr, ko'rishguncha!")
            break

        reply = handle_command(user_text, brain)
        print(f"🤖 Jarvis: {reply}\n")


if __name__ == '__main__':
    main()
