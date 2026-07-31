print("--- Black AI Kalkulyator tizimi ---")
print("(Dasturni to'xtatish uchun 'exit' deb yozing)")

while True: # Bu sikl dasturni cheksiz aylantiradi
    amal = input("\nAmalni tanlang (+, -, *, /): ").lower() # .lower() hamma harfni kichik qiladi
    
    if amal == 'exit':
        print("Tizim o'chirildi. Xayr!")
        break # Siklni to'xtatish uchun
    
    a = float(input("Birinchi son: "))
    b = float(input("Ikkinchi son: "))

    if amal == '+':
        print(f"Natija: {a + b}")
    elif amal == '-':
        print(f"Natija: {a - b}")
    elif amal == '*':
        print(f"Natija: {a * b}")
    elif amal == '/':
        if b != 0:
            print(f"Natija: {a / b}")
        else:
            print("Xato: Nolga bo'lish mumkin emas!")
    else:
        print("Noto'g'ri amal kiritildi. Iltimos, qaytadan urinib ko'ring.")
