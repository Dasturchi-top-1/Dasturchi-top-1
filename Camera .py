import cv2

# Yuzni aniqlash uchun tayyor model (OpenCV bilan birga keladi)
yuz_aniqlovchi = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# Kamerani ochish (0 - asosiy kamera, orqa/old kamera bo'lsa 1 ni sinab ko'ring)
kamera = cv2.VideoCapture(0)

if not kamera.isOpened():
    print("Kamera ochilmadi! Ilova kameraga ruxsat olganini tekshiring.")
    exit()

print("Kamera ishga tushdi. To'xtatish uchun 'q' tugmasini bosing.")

while True:
    muvaffaqiyat, kadr = kamera.read()
    if not muvaffaqiyat:
        print("Kadr olinmadi.")
        break

    # Kulrang rangga o'tkazish (aniqlash tezroq ishlaydi)
    kulrang = cv2.cvtColor(kadr, cv2.COLOR_BGR2GRAY)

    # Yuzlarni aniqlash
    yuzlar = yuz_aniqlovchi.detectMultiScale(
        kulrang,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    # Har bir topilgan yuz atrofiga to'rtburchak chizish
    for (x, y, kenglik, balandlik) in yuzlar:
        cv2.rectangle(kadr, (x, y), (x + kenglik, y + balandlik), (0, 255, 0), 2)
        cv2.putText(kadr, "Yuz", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Nechta yuz topilganini ekranga chiqarish
    matn = f"Topilgan yuzlar: {len(yuzlar)}"
    cv2.putText(kadr, matn, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    # Natijani ko'rsatish
    cv2.imshow("Kamera - Narsalarni aniqlash", kadr)

    # 'q' tugmasi bosilsa chiqish
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

kamera.release()
cv2.destroyAllWindows()
