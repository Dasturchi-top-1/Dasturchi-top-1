def salom_ber(ism):
   """Foydalanuvchi ismini qabul qilib, unga Salom beradigan funksiya"""
   print(f"Asalomu Aleykum Hurmatli Dost {ism.title( )}! ")
    
salom_ber('Blip')
salom_ber('Gemini')
salom_ber("Grox")
salom_ber("Anilan")

print(salom_ber.__doc__)

def toliq_ism(ism, familya):
    """Foydalanuvchidan ism va familya saqlovchi funksiya"""
    print(f"Foydalanuvchi ismi: {ism.title( )}\n"
    f"Foydalanuvchi familyasi: {familya.title( )}")
toliq_ism("Salo-xiddin-jon", "Pirnazarzoda")

def yosh_hisobla(ism, tugʻilgan_yil):
    """Foydalanuvchi tugʻilgan yilini hisoblovchi funksiya"""
    print(f"{ism.title( )} {2026-tugʻilgan_yil}-yoshda")
yosh_hisobla(tugʻilgan_yil=2013, ism="Blip")

def yosh_hisobla(tugʻilgan_yil, joriy_yil=2026):
    """Foydalanuvchidan son olib yoshini hisoblaydigan dastur. """
    print(f"{joriy_yil-tugʻilgan_yil}-yoshdasiz")
    
yosh_hisobla(1999)
yosh_hisobla(2013)