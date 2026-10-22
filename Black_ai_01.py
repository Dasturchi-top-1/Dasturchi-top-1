import g4f
import json
import os

# ==========================================
# 1. XOTIRA VA FAYLLAR (BLIP UCHUN)
# ==========================================
FAYL_NOMI = "blip_terminal_xotira.json"

def xotirani_yukla():
    if os.path.exists(FAYL_NOMI):
        try:
            with open(FAYL_NOMI, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def xotirani_saqla(tarix):
    try:
        with open(FAYL_NOMI, 'w', encoding='utf-8') as f:
            json.dump(tarix, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[!] Xotirani saqlashda xatolik: {e}")

# ==========================================
# 2. ASOSIY CHAT TSIKLI (TERMINAL)
# ==========================================
def main():
    tarix = xotirani_yukla()
    
    print("==================================================")
    print("       👁️ BLACK AI :: BLIP TERMINAL v4.3         ")
    print("==================================================")
    print(" [✓] Rejim: Xavfsiz Lokal & Onlayn Chat")
    print(" [✓] Foydalanuvchi: Blip")
    print("--------------------------------------------------")
    print(" Chiqish uchun 'exit' deb yozing.\n")
    
    print(f"Black AI > Salom, Blip! Oldingi xotiralar yuklandi. Bugun qanday rejalaring bor?\n")

    while True:
        try:
            user_input = input("Blip > ")
            
            if not user_input.strip():
                continue
                
            if user_input.lower().strip() in ["exit", "stop", "chiqish"]:
                print("\n👁️ Black AI xotirani saqladi va uyquga ketdi!")
                break
            
            # Suhbat tarixiga qo'shish
            tarix.append({"kim": "Blip", "matn": user_input})
            
            print(" [*] O'ylamoqda...")
            
            # G4F orqali internetdan aqlli javob olish
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[{"role": "user", "content": f"Mening ismim Blip. {user_input}"}],
            )
            
            javob = str(response)
            print(f"\nBlack AI > {javob}\n")
            
            # AI javobini tarixga qo'shish va saqlash
            tarix.append({"kim": "Black AI", "matn": javob})
            xotirani_saqla(tarix)
            
        except KeyboardInterrupt:
            print("\n\n👁️ Tizim to'xtatildi.")
            break
        except Exception as e:
            print(f"\n⚠️ Xatolik yuz berdi: {e}\n")

if __name__ == "__main__":
    main()
