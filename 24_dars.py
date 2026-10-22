import math
#uzunlik = lambda pi, r : 2*pi*r
#print(uzunlik(math.pi,10))

#kvadrat = lambda x, y : x ** y
#print(kvadrat(3, 2))

#def daraja(n):
#    return lambda x : x**n
#print(daraja(3))

#kvadrat = daraja(26)
#kub = daraja(66)
#print(f"26-ning kvadrati {kvadrat(26)}-ga, "
#         f"kub {kub(66)}-ga teng")

#from math import sqrt
#sonlar = list(range(11))
#ildizlar = list(map(sqrt, sonlar))
#print(ildizlar)

#def daraja_2(x):
#    """Berilgan sonni kvadratini qaytaruvchi funksiya"""
#    return x*x
#print(list(map(daraja_2, sonlar)))

#kvadratlar = list(map(lambda x:x*x, sonlar))
#print(kvadratlar)

#a = [4, 5, 6]
#b = [7, 8, 9]
#a_plus_b = list(map(lambda x,y:x+y, a, b))
#print(a_plus_b)

#import random as r

#sonlar = r.sample(range(100), 10)
#print(sonlar)
#def juftmi(x):
 #   """X juft boʻlsa True, aks holda False qaytaradi"""
#    return x%2==0
   
#juft_sonlar = list(filter(juftmi, sonlar))

#juft_sonlar = list(filter(lambda son: son%2==0, sonlar))
#print(juft_sonlar)

mevalar = ["Olma", "Anor", "Anjir", "Shaftolu", "Oʻrik", "Tarvuz", "Qovun", "Banan"]
harf='b'
mevalar_b = list(filter(lambda meva:meva.startswith(harf), mevalar))
#print(mevalar_b)

mevalar_2 = list(filter(lambda meva:len(meva)<6, mevalar))
print(mevalar_2)

list(filter(lambda meva: (meva.startswith('a') and meva.endswith("r")),  mevalar))