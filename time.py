import time
import random

print("--- BLACK AI KIBER-HIMOYA TIZIMI ISHGA TUSHDI ---")

# Black AI har daqiqa (yoki har soniya) yangi maxfiy kalit yaratadi
while True:
    # 100000 va 999999 oraliqida tasodifiy yangi super-kod yaratiladi
    yangi_kod = random.randint(100000, 999999)
    
    print(f"🔒 Tizim himoyalandi! Joriy kiber-kalit: {yangi_kod}")
    print("Xakerlar bu kodni topguncha...")
    
    # Tizim 10 soniya (yoki 1 daqiqa) kutadi va kodni butunlay o'zgartiradi
    time.sleep(10) 
    print("🔄 VAQT TUGADI! Superkompyuter kodni avtomatik ravishda o'zgartirdi!\n")
