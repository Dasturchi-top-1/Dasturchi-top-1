#car_0 = {
#      'model' : 'BMW',
#      'rang' : 'koʻk',
#      'yil' : 2026,
#      'narx' : 1000000,
#      'km' : '320km',
#      'karopka' : 'avtomat'
#      }
      
#car_1 = {
#      'model' : 'tesla',
#      'rang' : 'qizil',
#      'yil' : 2026,
#      'narx' : 92849274,
#      'km' : '293km',
#      'karopka' : 'avtomat',
#      }
      
#car_2 = {
#      'model' : 'Lamborgini',
#      'rang' : 'sariq',
#      'yil' : 2022,
#      'narx' : 92749,
#      'km' : '310km'
#      }
  
#car = car_0
#print(f "{car['model'].title( )}, "
#         f "{car['rang']} rang, "
#         f "{car['yil']}-yil, (car['narx'])$ ")

#cars = [car_0, car_1, car_2]
#for car in cars:
#    print(f "{car['model'].title( )}, "
#         f "{car['rang']} rang, "
#         f "{car['yil']}-yil, (car['narx'])$ ")
#cars[0]['model']

#print(f"{cars[2]['rang'].title( )} "
#         f"{cars[2]['model']} ")

#bmw = [ ]
#for n in range(10):
#    new_car = {
#             'model' : 'BMW',
#             'rang' :None,
#             'narx' :None,
#             'yil' : 2026,
#             'km' : 0,
#             'karopka' : 'avto'
#             }
#     bmw.append(new_car)
      
#for bmw in bmw[:3]:
#    bmw['rang']-"qizil"

dasturchilar = {
          'Anilan' :["Python", "Java"],
          'Blip' :["Python", "Java", "C++", "JavaSkript", "C"],
          'Grox' :["Java", "Python", "C++"],
          'Gemni' :["U ozi dastur oʻrqali yaratilgan"]
          }
          
for ism, tillar in dasturchilar.items( ):
    print(f"\n{ism.title()} quyidagi dasturlashlar-2ni biladi")
    for til in tillar:
#        print(til.upper( )) 
           print(f"{til.upper( )} ", end= ' ')