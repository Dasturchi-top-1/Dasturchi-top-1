def bahola(ismlar):
    baholar = { }
    while ismlar:
        ism = ismlar.pop( )
        baho = input(f"Talaba {ism.title( )}-ning bahosi. ")
    baholar[ism]=int(baho)
    return baholar
     
talabalar = ["Jasur", "Akbar", "Mustafo", "Muxlisa", "Sabina"]
baholar = bahola(talabalar[:])
print(bahola)
print(talabalar)