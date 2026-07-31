def summa(x, y,*sonlar):
    """Kiritilgan sonni yigʻindisini hisoblaydigan funksiya"""
    return x+y+sum(sonlar)
     
print(summa(1, 2))
print(summa(1, 2, 3, 4, 5))
print(summa(4, 5, 6, 7))

def avto_info_mod(kompaniya, model, **maʼlumotlar):
    """Avto haqida maʼlumotlarni lugʻat koʻrinishida qaytaruvchi funksiya"""
    maʼlumotlar["kompaniya"]=kompaniya
    maʼlumotlar["model"]=model
    return maʼlumotlar
    
    alinfo = ["Grox", "Anilan", "Blip", "Gemini", "Black AI"]
  
avto_1 = avto_info_mod("BMW", "M5 f90", rang='qora', yil=2026, karopka='avtomat')
avto_2 = avto_info_mod("Kia", "K5", rang='oq', narx=35000,  yil=2022, karopka='avtomat')
print(avto_2)

import math
x=400
print(math.sqrt(x))
print(math.pow(5, 3))
print(math.pi)
print(math.log2(8))
print(math.log10(100))

import random as r

son = r.randint(0, 100)
print(son)

ismlar = ["Black AI", "Gemini", "Anilan", "Grox", "Dream", "Blip"]
ism = r.choice(ismlar)
print(ism)
print(r.choice(ism))

x = list(range(0,51,5))
print(x)
print(r.choice(x))

x = list(range(11))
print(x)
r.shuffle(x)
print(x)