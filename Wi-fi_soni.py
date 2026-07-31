import random

print("📡 Qishloq vishkasi tizimiga ulanmoqda...")

# Tasodifiy ulangan telefonlar sonini belgilaymiz (masalan 50 tadan 500 tagacha)
ulangan_telefonlar = random.randint(50, 500)

print("✅ Qidiruv yakunlandi!")
print(f"📱 Hozirgi vaqtda minoraga {ulangan_telefonlar} ta telefon ulangan.")

# Foydalanuvchidan so'rov
tekshirish = input("Tarmoq holatini batafsil ko'rasizmi? (ha/yo'q): ")

if tekshirish.lower() == "ha":
    internetda_otirganlar = random.randint(10, ulangan_telefonlar)
    print(f"- 🌐 Internetdan aktiv foydalanayotganlar: {internetda_otirganlar} ta telefon")
else:
    print("Tizimdan chiqildi. Aloqa tugadi.")
