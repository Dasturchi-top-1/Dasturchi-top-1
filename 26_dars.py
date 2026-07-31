import random
from uz_words import words

def get_word( ):
    word = random.choice(words)
    while "-" in word or ' ' in word:
        word = random.chice(words)
    return word.upper( )
def display(usser_latters, word):
    display_latter 
    for latter in word:
        if latter in usser_latters.upper( ):
            display_latter += latter
        else:
            display_latter += "-"
        return display_latter
     
def play( ):
    word = get_word( )
    word_latters = set(word)
    usser_latters = ' '
    print(f"Men {len(word)}-xonali soʻz oʻyladim. Topa olasizmi? ")
    while len(word_latter)>0:
        print(display(usser_latters, word))
        if len(usser_latters)>0:
            print(f"Shu payt-gacha kiritilgan harflaringiz: {usser_latters}")
            
        latter = input("Harf kiriting: ").upper( )
        if latter in usser_latters:
            print("Bu har-ni avval kiritgansiz. Boshqa harf kiriting: ")
            continue 
        elif latter in word:
            word_latters.remove(latter)
            print(f"{latter}-harfi togʻri. ")
        else:
            print("Bunday harf yoʻq")
            usser_latters += latter
            print(f"Tabriklayman! {word} soʻzi-ni {len(usser_latters)} ta urinish-da topdingiz")