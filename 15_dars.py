#car_0 = {"model" : 'ferari', 'rang' : "qizil"}
#print(car_0['model'])
#print(car_0['rang'])

#en_uz = {"apple" : "olma", "apricot" : "orik", "banana" : "banan"}
#print(en_uz["apple"])

#mevalar = {'olma' : 10, 'tarvuz' : 8, 'qovun' : 10}
#print(f"olma narxi {mevalar['olma']} somoní")
#print(mevalar["qovun"])

#talaba_0 = {'ism' : 'Salo-xuddin-jon', 'yosh' : 13, }
#print(talaba_0.items( ))
   
#for kalit, qiymat in talaba_0.items( ):
#    print(f"Kalit : {kalit}")
#    print(f"Qiymat : {qiymat}")

telefonlar = {
       'Men' : 'Honor Win',
       'Musobek' : 'Redmi 12C',
       'Uydagi tel' : 'OUKITEL W5 PRO',
       'Akbar' : 'Samsung A12',
       'Bahrom' : 'Redmi 14 Pro',
       'Daler' : 'Samsung A40',
       'Uydagi tel' : 'Itel P65c'
      }
#for k, q in telefonlar.items( ):
#   print(f" {k. title( )}ning telefoni {q}")

#mahsulotlar = {
#        'Olma' : 11,
#        'Sabzi' : 5,
#        'Shaftolu' : 17,
#        'Badiring' : 18
#        }
#print(mahsulotlar.keys( ))

#print('Do\'kondagi mahsulotlar: ')
#for mahsulot in mahsulotlar.keys( ):
#    print(mahsulot.title( ))

#bozorlik = ["anor", "uzum", "gilos", "olma", "orik", "shaftolu"]
#for mahsulot in mahsulotlar:
#    if mahsulot in bozorlik:
#        print(f" {mahsulot.title( )} {mahsulotlar[mahsulot]} somoní")
        
#for buyum in bozorlik:
#    if buyum not in mahsulotlar:
#        print(f"Iltimos dokoning-giz-ga {buyum} ham olib keling: ")
#        print('Dokoning-giz dagi  mahsulotlar:')
#for mahsulot in sorted(mahsulotlar):
#    print(mahsulot.title( ))

print(telefonlar.values( ))

print("Foydalanuvchilar shu qurilmalarni ishlatadi: ")
for tel in set(telefonlar.values( )):
    print(tel)
    
toys = {"ball", "car", "lamp", "ball"}
print(toys)