class Talabalar:
    def __init__(self, ism, familya,  tyil):
        self.ism = ism
        self.familya = familya
        self.tyil = tyil
        self.bosqich = 1
        
    def get_info(self):
      """Talaba haqida maʼlumot"""
      return f"{self.ism} {self.familya} {self.yosh} {self.tyil} {self.bosqich}-bosqich talabasa "
      
    def get_name(self):
        """Talaba-ning ismini qaytaradi"""
        return self.ism
        
    def set_bosqich(self, yangi_bosqich):
        """Talaba-ning kursini yangilovchi metod"""
        self.bosqich = yangi_bosqich
        
    def update_bosqich(self):
        """Talaba-ning boshqichi-ni Itaga korsatuvchi """
        self.boshqich += 1
        
    def get_age(self, tyil):
        return tyil - self.tyil
        
    def get_lastname(self):
        """Talaba-ning familyasini qaytaradi """
        return self.familya
    
    def tanishtirish(self):
        return f"Ismim {self.ism} {self.familya} {self.yosh} {self.tyil}"        
talaba_1 = Talabalar("Salo-xiddin-jon", "Pirnazarzoda", 2013)
talaba_2 = Talabalar("Anvar", "Narzullayev",  1991)
talaba_3 = Talabalar("Abdurauf", "Hasanov", 1999)

class Fan( ):
    """Fan nomli klass"""
    def __init__(self, nomi):
        self.nomi = nomi
        self.talabalar_soni = 0
        self.talabalar = [ ]
        
    def add_student(self, talaba):
        """Fonga talaba qoʻshish """
        self.talabalar.append(talaba)
        self.talabalar_soni += 1

    def get_students(self):
         """Fon-ga yozilgan talabalar haqida maʼlumot """
         return [x.get_fullname( ) for x in self.talabalar]
    def get_students_num(self):
        """Fon-ga yozilgan talalabalar soni"""
        return self.talabalar_soni 
        
matematika = Fan("Oʻliy Matematika")
talaba_1 = Talabalar("Salo-xiddin-jon", "Pirnazarzoda", 2013)
talaba_2 =Talabalar("Anvar", "Narzullayev", 1991)
talaba_3 = Talabalar("Abdurauf", "Hasanov", 1999)
matematika.add_student(talaba_1)
matematika.add_student(talaba_2)
matematika.add_student(talaba_3)

# def see_methods(klass):
#     return [method for method in dir(klass) if method.startswith('__')]
