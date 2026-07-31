#print("Yaqin Dostlaringiz roʻyxati-ni tuzamiz")
#ismlar = [ ]
#n=1
#while True:
#    savol = f"{n}-dostingiz ismi-ni kiriting:"
#    ism = input(savol)
#    ismlar.append(ism)
#    takrorlash = input("Yana dostingiz ismini kiritasizmi? (ha/yoq)")
#    n+=1
#    if takrorlash != 'ha':
#        break
#print("Dostlaringiz royxati:")
#for ism in ismlar:
#    print(ism.title( ))
#print("Dastur tugadi!")

#print("Dostlaringiz yoshi-ni saqlaymiz: ")
#dostlar = { }
#ishora = True
#while ishora:
#    ism = input("Dostingiz ismini kiriting: ")
#    yosh = input(f"{ism.title( )}-ning yoshini kiriting: ")
#    dostlar[ism] = int(yosh)
    
#    javob = input("Yana maʼlumot kiritasizmi? (ha/yoq)")
#    if javob == 'yoq':
#        ishora = False
        
#for ism, yoshlar in dostlar.items( ):
#    print(f"{ism.title( )} {yosh}-yosh-da")

#cars_2013 = ["BMW", "Tesla", "Bugati", "Mersedes", "Audi", "Mersedes", "Royl-Roys", "Mersedes"]
#while 'Mersedes' in cars_2013:
#    cars_2013.remove("Mersedes")
#print(cars_2013)

talabalar = ["Jasur", "Akbar", "Bahrom", "Asilbek"]
baholangan_talabalar = { }
while talabalar:
    baho = { }
    talaba = talabalar.pop( )
    baho = input(f"{talaba.title( )}-ga baho-ni kiriting: ")
    print(f"{talaba.title( )} baholan-di")
    baholangan_talabalar[talaba] = int(baho)