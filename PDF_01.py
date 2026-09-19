import os, random, string, getpass
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
try:
    from reportlab.lib.pdfencrypt import StandardEncryption
    ENCRYPT_AVAILABLE = True
except ImportError:
    ENCRYPT_AVAILABLE = False

def kuchli_parol(uzunlik=16):
    belgilar = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(belgilar) for _ in range(uzunlik))

def txtdan_pdf(matn, pdf_yoli, parol):
    enc = None
    if ENCRYPT_AVAILABLE:
        enc = StandardEncryption(parol, parol)
    c = canvas.Canvas(pdf_yoli, pagesize=A4, encrypt=enc)
    y = 800
    for qator in matn.split('\n'):
        while len(qator) > 90:
            c.drawString(50, y, qator[:90])
            qator = qator[90:]
            y -= 20
            if y < 50:
                c.showPage()
                y = 800
        c.drawString(50, y, qator)
        y -= 20
        if y < 50:
            c.showPage()
            y = 800
    c.save()

def fayldan_oqish(yol):
    with open(yol, 'r', encoding='utf-8') as f:
        return f.read()

print("=== PDF YARATUVCHI ===")
print("1. Mavjud .txt fayldan")
print("2. Qo'lda matn kiritish")
tan = input("Tanlang: ").strip()

if tan == "1":
    txt_yol = input("TXT fayl yo'lini kiriting: ").strip()
    try:
        matn = fayldan_oqish(txt_yol)
    except Exception as e:
        print("Xato:", e)
        exit()
else:
    print("Matnni kiriting. Yakunlash uchun 'STOP' deb yozing.")
    qatorlar = []
    while True:
        qator = input()
        if qator.strip().upper() == "STOP":
            break
        qatorlar.append(qator)
    matn = "\n".join(qatorlar)

pdf_nomi = input("PDF nomini kiriting (masalan: hujjat.pdf): ").strip()
if not pdf_nomi.endswith(".pdf"):
    pdf_nomi += ".pdf"

downloads = "/storage/emulated/0/Download"
os.makedirs(downloads, exist_ok=True)
pdf_yoli = os.path.join(downloads, pdf_nomi)

parol_tanlash = input("Kuchli parol avtomatik yaratilsinmi? (ha/yo'q): ").strip().lower()
if parol_tanlash in ["ha", "h", "yes", "y"]:
    parol = kuchli_parol()
    print("Yaratilgan parol:", parol)
else:
    parol = input("PDF parolini kiriting: ").strip()

txtdan_pdf(matn, pdf_yoli, parol)
print(f"\nPDF tayyor: {pdf_yoli}")
print("Uni ochishda parol so'raladi.")