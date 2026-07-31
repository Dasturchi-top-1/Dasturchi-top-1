import json
import os
from datetime import datetime

FAYL_NOMI = "eslatmalar.json"

def yuklash():
    # Json fayldan ma'lumotlarni o'qish
    if os.path.exists(FAYL_NOMI):
        with open(FAYL_NOMI, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def saqlash(malumotlar):
    # O'zgarishlarni Json faylga yozish
    with open(FAYL_NOMI, 'w', encoding='utf-8') as f:
        json.dump(malumotlar, f, indent=4)

def eslatmalarni_tekshir():
    malumotlar = yuklash()
    bugun = datetime.now()
    
    print("\n=== YAQINLASHAYOTGAN HODISALAR ===")
    if not malumotlar:
        print("Hozircha hech qanday eslatma yo'q.")
        return

    for voqea, sana_matni in malumotlar.items():
        try:
            sana = datetime.strptime(sana_matni, "%Y-%m-%d")
            farq = (sana.date() - bugun.date()).days
            
            if farq < 0:
                print(f"[O'TIB KETGAN] {voqea} ({sana_matni})")
            elif farq == 0:
                print(f"[BUGUN!!!] 🔔 {voqea} ({sana_matni})")
            elif farq <= 7:
                print(f"[YAQINDA] ⏳ {voqea} - {farq} kun qoldi ({sana_matni})")
            else:
                print(f"[KUTILMOQDA] {voqea} - {farq} kun qoldi ({sana_matni})")
        except ValueError:
            print(f"[XATO] '{voqea}' sanasi noto'g'ri formatda!")

def yangi_qoshish():
    print("\n--- YANGI ESLATMA QO'SHISH ---")
    voqea = input("Voqea nomini kiriting: ")
    sana = input("Sanani kiriting (Masalan, 2026-07-20): ")
    
    try:
        # Sanani to'g'ri yozilganini tekshirish
        datetime.strptime(sana, "%Y-%m-%d")
        malumotlar = yuklash()
        malumotlar[voqea] = sana
        saqlash(malumotlar)
        print(f"\n>> Muvaffaqiyatli saqlandi: {voqea} -> {sana}")
    except ValueError:
        print("\n>> XATO: Sanani YYYY-MM-DD formatida kiritishingiz shart!")

def menyu():
    while True:
        print("\n" + "="*30)
        print("1. Eslatmalarni ko'rish")
        print("2. Yangi eslatma qo'shish")
        print("3. Dasturdan chiqish")
        print("="*30)
        
        tanlov = input("Tanlang (1/2/3): ")
        
        if tanlov == '1':
            eslatmalarni_tekshir()
        elif tanlov == '2':
            yangi_qoshish()
        elif tanlov == '3':
            print("\nKiber-tizim o'chirilmoqda. Xayr, bro!")
            break
        else:
            print("\n>> Noto'g'ri buyruq. Qaytadan urinib ko'ring.")

if __name__ == "__main__":
    # Dastur yoqilganda avtomatik eslatmalarni ko'rsatadi
    eslatmalarni_tekshir()
    menyu()
