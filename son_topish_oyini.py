import random

def kiber_son_topish_oyini():
    print("🤖 Kiber-jang boshlandi! 1-bosqich: Men son o'ylayman, sen topasan!")
    # Kompyuter 1 dan 10 gacha tasodifiy son o'ylaydi (xohlasang 100 gacha o'zgartirishing mumkin)
    kompyuter_soni = random.randint(1, 100)
    foydalanuvchi_urinishlari = 0

    while True:
        taxmin = int(input("👉 1 dan 100 gacha son o'yladim. Qani, top-chi: "))
        foydalanuvchi_urinishlari += 1

        if taxmin < kompyuter_soni:
            print("❌ Xato! Men o'ylagan son bundan kattaroq.")
        elif taxmin > kompyuter_soni:
            print("❌ Xato! Men o'ylagan son bundan kichikroq.")
        else:
            print(f"🎉 Dahoona! Sen mening sonimni {foydalanuvchi_urinishlari} ta urinishda topding!\n")
            break

    print("😎 2-bosqich: Endi sen son o'ylaysan, men topaman!")
    input("Son o'ylagan bo'lsang, o'yinni boshlash uchun istalgan tugmani bos (Enter)...")

    quyi_chegara = 1
    yuqori_chegara = 10
    kompyuter_urinishlari = 0

    while True:
        # Kompyuter qolgan chegaralar ichidan tasodifiy son tanlaydi
        if quyi_chegara != yuqori_chegara:
            taxmin = random.randint(quyi_chegara, yuqori_chegara)
        else:
            taxmin = quyi_chegara
            
        kompyuter_urinishlari += 1
        javob = input(f"Menimcha sen {taxmin} sonini o'ylading! To'g'rimi (t), sening soning kattaroqmi (+), yoki kichikroqmi (-)? ").lower()

        if javob == 't':
            print(f"🤖 Kiber-miya g'alaba qozondi! Men {kompyuter_urinishlari} ta urinishda topdim!")
            break
        elif javob == '+':
            quyi_chegara = taxmin + 1
        elif javob == '-':
            yuqori_chegara = taxmin - 1
        else:
            print("⚠️ Noma'lum buyruq! Iltimos, faqat 't', '+' yoki '-' belgilarini kirit.")

    # Kiber-jang natijasini hisoblash
    print("\n🏆 --- NATIJALAR --- 🏆")
    if foydalanuvchi_urinishlari < kompyuter_urinishlari:
        print("Sening g'alabang! Kiber-imperator kompyuterni dog'da qoldirdi!")
    elif foydalanuvchi_urinishlari > kompyuter_urinishlari:
        print("Mening g'alabam! Kiber-tizim ustun keldi!")
    else:
        print("Durrang! Haqiqiy pro-geymerlar to'qnashuvi!")

# Dasturni ishga tushirish
kiber_son_topish_oyini()
