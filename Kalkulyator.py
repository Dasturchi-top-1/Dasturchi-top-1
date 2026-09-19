# Oddiy kalkulyator (internet shart emas)
print("=== MINI KALKULYATOR ===")
print("Amallar: +, -, *, /")
print("Chiqish: 'exit'")

while True:
    ifoda = input("\nHisoblash: ").strip()
    if ifoda.lower() == "exit":
        print("Xayr!")
        break
    try:
        natija = eval(ifoda)
        print("Natija:", natija)
    except:
        print("Xato! Masalan: 12+5 yoki 10/2")