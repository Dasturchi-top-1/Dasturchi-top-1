# Tojikiston haqida Black AI boshlang'ich bazasi
tojikiston_bazasi = {
    "poytaxt": "Dushanbe",
    "til": "Tojik tili",
    "sadriddin ayni": "Tojikiston Qahramoni, zamonaviy tojik adabiyoti asoschisi, yozuvchi va olim.",
    "ismoil somoni": "Somoniylar davlatining asoschisi, buyuk shoh."
}

print("=== BLACK AI BAZA TIZIMI ISHGA TUSHDI ===")
print("Buyruqlar: 'qidir', 'qosh', 'chiq'")

while True:
    # Foydalanuvchidan buyruq olish
    amal = input("\nNima qilamiz? (qidir/qosh/chiq): ").lower()
    
    if amal == "chiq":
        print("Tizim yopildi. Imperiya xavfsiz qoldi!")
        break
        
    elif amal == "qidir":
        soz = input("Qidirilayotgan so'z yoki odam nomi: ").lower()
        if soz in tojikiston_bazasi:
            print(f"Natija: {tojikiston_bazasi[soz]}")
        else:
            print("Kechirasiz, bunday ma'lumot bazada yo'q.")
            
    elif amal == "qosh":
        yangi_kalit = input("Yangi mavzu nomini kiriting (masalan: skuter): ").lower()
        yangi_qiymat = input(f"'{yangi_kalit}' haqida ma'lumot yozing: ")
        
        # Mana shu qator ma'lumotni ishlab turgan vaqtda bazaga qo'shadi!
        tojikiston_bazasi[yangi_kalit] = yangi_qiymat
        print(f"Muvaffaqiyatli! '{yangi_kalit}' bazaga qo'shildi.")
        
    else:
        print("Noto'g'ri buyruq! Qaytadan urinib ko'ring.")
