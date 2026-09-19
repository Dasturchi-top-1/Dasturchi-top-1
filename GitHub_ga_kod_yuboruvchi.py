import os
import requests
import base64

print("🚀 Pydroid orqali GitHub'ga to'g'ridan-to'g'ri yuboruvchi dastur\n")

fayl_nomi = input("Qaysi faylni yubormoqchisiz? (Masalan, black_ai.py): ")
yol = f"/storage/emulated/0/.kivy/{fayl_nomi}"

# 1. Fayl borligini tekshiramiz
if not os.path.exists(yol):
    print(f"\n❌ Xatolik: {yol} papkasida bunday fayl topilmadi!")
    exit()

print(f"\n⏳ {fayl_nomi} GitHub'ga yuklanmoqda, kuting...")

# 2. Fayl ichini o'qiymiz va GitHub qabul qiladigan formatga (Base64) o'tkazamiz
with open(yol, "rb") as f:
    fayl_matni = f.read()
encoded_content = base64.b64encode(fayl_matni).decode("utf-8")

# 3. GitHub ma'lumotlari (Sening profiling va tokening)
TOKEN = "YOUR_TOKEN"
USERNAME = "Dasturchi-top-1"
REPO = "Dasturchi-top-1"

url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{fayl_nomi}"
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 4. Agar fayl oldin yuklangan bo'lsa, uning xeshi (sha) kerak bo'ladi
r = requests.get(url, headers=headers)
data = {
    "message": f"Avtomatik yangilandi: {fayl_nomi}",
    "content": encoded_content
}

if r.status_code == 200:
    data["sha"] = r.json()["sha"]  # Faylni yangilash uchun eski fayl xeshini qoshamiz

# 5. Faylni GitHub'ga to'g'ridan-to'g'ri yuborish (Git'siz!)
r_put = requests.put(url, headers=headers, json=data)

if r_put.status_code in [200, 201]:
    print(f"\n✅ Ajoyib! '{fayl_nomi}' muvaffaqiyatli GitHub'ga yuklandi!")
else:
    print("\n❌ Yuklashda xato yuz berdi:")
    print(r_put.json())