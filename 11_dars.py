#son = 10
#if son<0:
#    print("Manfiy son")
#else:
#    print("Musbat son")

#yosh = int(input("Yoshingizni kiriting: "))
#if yosh<=4:
#    narx = 0
#elif yosh<=12:
#    narx = 5
#elif yosh<=18:
#        narx = 8
#else:
#    narx = 10#    
#print(f"Siz-ga kirish {narx} somoní")

#kun = input("Bugun nima kun?>>>")
#if kun.lower( ) == 'shanba' or kun.lower( ) #== 'yakshanba':
#    print("Bugun dam olish kuni. ")
#else:
#    print("Bugun ish kuni. ")
    
#un = input("Bugun nima kun?")
#harorat = float(input("Havo harorati qanday?"))
#if kun.lower( ) == (kun.lower( #)=='yakshanba' or kun.lower( ) == #'shanba') and harorat>=30:
#    print("Chomilgali ketdik! ")
# elif kun.lower( ) == 'yakshanba' or (kun.#lower( ) == 'shanba') and harorat<=30:
#else:
#     print("Unda ish kuni ekan yajshanba akungacha kutamiz")

#narx = 15
#choy = True
#salat = False

#if choy and salat:
#    narx = narx + 10
#elif choy or salat:
#    narx = narx + 5
#print(f"Jami {narx} somoní")

#narx = 15
#choy = True
#salat = True
#non = True
#kampot = True
#assorti = True

#if choy:
#    print("Mijoz choy oldi. ")
#    narx = narx + 5
#if salat:
#    print("Mijoz salat oldi. ")
#    narx = narx + 10
#if non:
#    print("Mijoz non oldi. ")
#    narx = narx + 2.5
#if kampot:
#    print("Mijoz kampot oldi. ")
#    narx = narx + 10
#if assorti:
#    print("Mijoz assorti oldi. ")
#print(f"Jami {narx} somoní boʻldi!")

menu = ["osh", "qazonkabob", "shashlik",]
#ovqat = input("Nima ovqat yeysiz? ")
#if ovqat.lower( ) in menu:
#    print("Buyurtma qabul qilindi. ")
#else:
#    print("Afsuski bizda bunday ovqat yoʻq")
buyurtmalar = ["osh", "somsa", "manti", "shashlik"]

for taom in buyurtmalar:
    if taom in menu:
        print(f"Menu {taom} bor ")
    else:
        print(f"Kechirasiz, menuda {taom} yoʻq")
        
buyurtmalar = [ ]
     if buyurtmalar:
         print(f"Roʻyxatda (len(buyurrmalar)) ta taom bor")
     else:
         print("Roʻyxat boʻsh")