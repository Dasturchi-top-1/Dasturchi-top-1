class Shaxs:
    """Shaxslar haqida maʼlumot """
    def __init__(self, ism, familya, passport, tyil):
        self.ism = ism
        self.familya = familya
        self.passport = passort
        self.tyil = tyil
        
    def get_info(self):
         """Shaxs haqida maʼlumot"""
         info = f"{self.ism} {self.familya}. "
         info += f"Passport:{self.passport} {self.tyil}"
         return info
    def get_age(self, yil):
         """Shaxs-ning yoshi-ni qaytaruvchi metod"""
         return yil - self.tyil
         
class talaba(Shaxs):
    """Talaba klassi"""
    def __init__(self, ism, familya, passport, tyil, idraqam):
        super( ).__init__(ism, familya, passport, tyil)
    self.idraqam = idraqam
    self.bosqich = 1
    
    def get_id(self):
        """Talaba-ning ID raqami"""
        return self.idraqam
        
    def get_bosqich(self):
        """Talaba-ning oʻqish bosqichi"""
        return self.bosqich