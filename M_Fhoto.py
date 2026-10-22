import os
import hashlib
import random
import time
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

RASM_KENGA = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')

def tozalash():
    os.system('clear' if os.name != 'nt' else 'cls')

def rasm_qidirish():
    papkalar = [
        "/storage/emulated/0/Download",
        "/storage/emulated/0/DCIM/Camera",
        "/storage/emulated/0/Pictures",
        "/storage/emulated/0/DCIM",
    ]
    topilgan = []
    for papka in papkalar:
        if not os.path.exists(papka):
            continue
        try:
            for f in os.listdir(papka):
                if f.lower().endswith(RASM_KENGA):
                    topilgan.append(os.path.join(papka, f))
        except:
            pass
    return topilgan

def fayl_sha256(fayl_yoli):
    h = hashlib.sha256()
    try:
        with open(fayl_yoli, "rb") as f:
            for blok in iter(lambda: f.read(4096), b""):
                h.update(blok)
        return h.hexdigest()
    except:
        return None

def _onlik_ga(coord, ref):
    d = float(coord[0])
    m = float(coord[1])
    s = float(coord[2])
    qiymat = d + (m / 60.0) + (s / 3600.0)
    if ref in ('S', 'W'):
        qiymat = -qiymat
    return qiymat

def gps_olish(img):
    exif = img.getexif()
    gps_info = exif.get_ifd(ExifTags.IFD.GPSInfo)
    if not gps_info:
        return None
    try:
        lat = gps_info[2]
        lat_ref = gps_info[1]
        lon = gps_info[4]
        lon_ref = gps_info[3]
        return {
            "latitude": _onlik_ga(lat, lat_ref),
            "longitude": _onlik_ga(lon, lon_ref),
        }
    except (KeyError, IndexError, TypeError):
        return None

def exif_olish(img):
    exif_dict = {}
    try:
        exif = img.getexif()
        if exif:
            for tag, value in exif.items():
                nom = TAGS.get(tag, tag)
                if nom in ['Make', 'Model', 'DateTime', 'Software', 'Artist', 'Copyright']:
                    exif_dict[nom] = str(value)
    except:
        pass
    return exif_dict

def rasm_malumot(fayl_yoli):
    try:
        img = Image.open(fayl_yoli)
    except Exception as e:
        return None

    eni, boyi = img.size
    format = img.format
    mode = img.mode
    hajm = os.path.getsize(fayl_yoli) // 1024

    # O'rtacha rang
    try:
        kichik = img.resize((50, 50))
        pixels = list(kichik.getdata())
        r = sum(p[0] for p in pixels) // len(pixels)
        g = sum(p[1] for p in pixels) // len(pixels)
        b = sum(p[2] for p in pixels) // len(pixels)
        ortacha_rang = f"#{r:02x}{g:02x}{b:02x}"
    except:
        ortacha_rang = "Noma'lum"

    # Dominant ranglar
    try:
        kichik2 = img.resize((100, 100)).convert('RGB')
        colors = kichik2.getcolors(10000)
        colors.sort(reverse=True)
        top3 = [f"#{c[1][0]:02x}{c[1][1]:02x}{c[1][2]:02x}" for c in colors[:3]]
        dominant = ", ".join(top3)
    except:
        dominant = "Noma'lum"

    exif = exif_olish(img)
    gps = gps_olish(img)

    return {
        "fayl_nomi": os.path.basename(fayl_yoli),
        "fayl_hajmi_kb": hajm,
        "olcham": f"{eni}x{boyi}",
        "format": format,
        "mode": mode,
        "ortacha_rang": ortacha_rang,
        "dominant_ranglar": dominant,
        "exif": exif,
        "gps": gps,
    }

def matrix_yomgiri(davomiylik=100):
    tozalash()
    print(GREEN + "Matritsa yomg'iri boshlanmoqda..." + RESET)
    time.sleep(1)
    for _ in range(davomiylik * 1000):
        qator = ''.join(random.choice('921324') if random.random() > 0.5 else ' ' for _ in range(60))
        print(GREEN + qator + RESET)
        time.sleep(0.005)
    tozalash()

def asosiy():
    tozalash()
    print(GREEN + "=== RASM TEXNIK TAHLILCHI (OFFLINE) ===" + RESET)
    rasmlar = rasm_qidirish()
    if not rasmlar:
        print(RED + "Oddiy papkalarda rasm topilmadi." + RESET)
        return

    print(YELLOW + f"Jami {len(rasmlar)} ta rasm topildi:" + RESET)
    for i, r in enumerate(rasmlar, 1):
        print(f"{i}. {os.path.basename(r)}")

    try:
        tan = int(input("\nRasm raqamini tanlang: "))
        if tan < 1 or tan > len(rasmlar):
            print(RED + "Noto'g'ri raqam." + RESET)
            return
    except ValueError:
        print(RED + "Raqam kiriting!" + RESET)
        return

    fayl_yoli = rasmlar[tan - 1]
    info = rasm_malumot(fayl_yoli)
    if not info:
        print(RED + "Rasmni o'qib bo'lmadi." + RESET)
        return

    sha = fayl_sha256(fayl_yoli)

    tozalash()
    print(GREEN + "=" * 50 + RESET)
    print(GREEN + "BLIP TEXNIK TAHLILCHI" + RESET)
    print(GREEN + "=" * 50 + RESET)
    print(YELLOW + "Fayl nomi: " + RESET + info["fayl_nomi"])
    print(YELLOW + "Hajmi: " + RESET + str(info["fayl_hajmi_kb"]) + " KB")
    print(YELLOW + "O'lchamlari: " + RESET + info["olcham"])
    print(YELLOW + "Format: " + RESET + str(info["format"]))
    print(YELLOW + "Rang rejimi: " + RESET + info["mode"])
    print(YELLOW + "O'rtacha rang: " + RESET + info["ortacha_rang"])
    print(YELLOW + "Dominant ranglar: " + RESET + info["dominant_ranglar"])

    if info["exif"]:
        print(GREEN + "\nEXIF ma'lumotlar:" + RESET)
        for k, v in info["exif"].items():
            print(f"  {k}: {v}")
    else:
        print(RED + "\nEXIF ma'lumot topilmadi." + RESET)

    if info["gps"]:
        print(GREEN + "\nGPS koordinatalar:" + RESET)
        print(f"  Latitude: {info['gps']['latitude']:.6f}")
        print(f"  Longitude: {info['gps']['longitude']:.6f}")
    else:
        print(RED + "\nGPS ma'lumot yo'q." + RESET)

    if sha:
        print(GREEN + "\nSHA256 ID: " + RESET + sha)

    print(GREEN + "=" * 50 + RESET)

    tan = input("\nMatritsa yomg'irini ko'rishni xohlaysizmi? (ha/yo'q): ").strip().lower()
    if tan in ["ha", "h", "yes", "y", "blip", "s"]:
        matrix_yomgiri()

if __name__ == "__main__":
    asosiy()