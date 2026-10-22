# ==========================================
# LOYIHA: CyberVault v2.3 (Kirish Xavfsizligi Bilan)
# PLATFORMA: Pydroid 3 / Python standard library
# ==========================================

import hashlib
import json
import os
import sys

VAULT_FILE = "Vault.json"


def generate_key(master_password, salt="CyberSecurity2026"):
    """Master paroldan 256-bitli shifrlash kaliti yaratish"""
    return hashlib.pbkdf2_hmac(
        "sha256", master_password.encode(), salt.encode(), 100000
    )


def hash_password(password):
    """Parolni bazada solishtirish uchun SHA-256 hash qilish"""
    return hashlib.sha256(password.encode()).hexdigest()


def cipher_data(data_bytes, key_bytes):
    """XOR shifrlash va deşifrlash"""
    key_stream = hashlib.sha256(key_bytes).digest()
    result = bytearray()
    for i, byte in enumerate(data_bytes):
        key_byte = key_stream[i % len(key_stream)]
        result.append(byte ^ key_byte)
    return bytes(result)


def load_vault():
    """JSON fayldan ma'lumotlarni o'qish"""
    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, "r") as f:
            return json.load(f)
    return {}


def save_vault(data):
    """JSON faylga saqlash"""
    with open(VAULT_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --- DASTURGA KIRISH VA TEKSHIRUV ---
print("🛡️ CYBER VAULT v2.3 — Xavfsiz JSON Seyfi 🛡️")
print("--------------------------------------------------")

vault = load_vault()

# 1-QADAM: Birinchi marta ishlatilayotgan bo'lsa, Master Parol o'rnatamiz
if "_master_hash" not in vault:
    print("⚙️ Birinchi marta kiryapsiz! Seyf uchun Master Parol o'rnating.")
    new_master = input("🔑 Yangi Master Parol kiriting: ").strip()
    if not new_master:
        print("❌ Parol bo'sh bo'lishi mumkin emas!")
        sys.exit()

    vault["_master_hash"] = hash_password(new_master)
    save_vault(vault)
    print("✅ Master Parol muvaffaqiyatli saqlandi!\n")
    master_pass = new_master
else:
    # Keyingi kirishlarda parolni tekshiramiz
    master_pass = input("🔑 Kirish uchun Master Parolni kiriting: ").strip()
    if hash_password(master_pass) != vault["_master_hash"]:
        print(
            "\n⛔ XATO PAROL! Ruxsat berilmadi. Dastur to'xtatildi (Xakerlar kirishi taqiqlandi)!"
        )
        sys.exit()  # Dasturdan chiqarib yuborish
    print("🔓 Xush kelibsiz! Parol to'g'ri.\n")

crypto_key = generate_key(master_pass)

# --- ASOSIY MENYU (Faqat to'g'ri parol terilganda ochiladi) ---
while True:
    print("\n1. ➕ Yangi sir saqlash")
    print("2. 🔓 Sirlarni o'qish")
    print("3. 🗑️ Sirni o'chirish")
    print("4. 🚪 Chiqish")

    tanlov = input("\nTanlovingiz (1-4): ").strip()

    if tanlov == "1":
        sarlavha = input("\nNima haqida sir (masalan: Instagram_parol): ")
        sir_matn = input("Maxfiy ma'lumotni kiriting: ")

        encrypted = cipher_data(sir_matn.encode("utf-8"), crypto_key)
        vault[sarlavha] = encrypted.hex()

        save_vault(vault)
        print(f"✅ '{sarlavha}' vault.json fayliga shifrlanib saqlandi!")

    elif tanlov == "2":
        # Sirlarni ko'rish (_master_hash ni ro'yxatda ko'rsatmaymiz)
        keys_list = [k for k in vault.keys() if k != "_master_hash"]
        if not keys_list:
            print("⚠️ Seyf hozircha bo'sh!")
            continue

        print("\n📦 Saqlangan sirlar ro'yxati:")
        for idx, key in enumerate(keys_list, start=1):
            print(f" {idx}. {key}")

        qidiruv = (
            input(
                "\nQaysi birini ochamiz? (Raqamini yoki bosh harflarini yozing): "
            )
            .strip()
            .lower()
        )
        target_key = None

        if qidiruv.isdigit():
            index = int(qidiruv) - 1
            if 0 <= index < len(keys_list):
                target_key = keys_list[index]
        else:
            matches = [k for k in keys_list if k.lower().startswith(qidiruv)]
            if len(matches) == 1:
                target_key = matches[0]

        if target_key:
            try:
                enc_bytes = bytes.fromhex(vault[target_key])
                decrypted = cipher_data(enc_bytes, crypto_key)
                print(
                    f"\n🔓 [{target_key}] Maxfiy matn: {decrypted.decode('utf-8')}"
                )
            except Exception:
                print("❌ Xato: Ma'lumot shifrlanishida xatolik!")
        else:
            print("❌ Topilmadi yoki noto'g'ri tanlov.")

    elif tanlov == "3":
        keys_list = [k for k in vault.keys() if k != "_master_hash"]
        if not keys_list:
            print("⚠️ Seyf hozircha bo'sh!")
            continue

        print("\n📦 Saqlangan sirlar ro'yxati:")
        for idx, key in enumerate(keys_list, start=1):
            print(f" {idx}. {key}")

        qidiruv = (
            input("\nO'chirmoqchi bo'lgan siringiz raqami yoki bosh harfi: ")
            .strip()
            .lower()
        )
        ochiriladigan = None

        if qidiruv.isdigit():
            index = int(qidiruv) - 1
            if 0 <= index < len(keys_list):
                ochiriladigan = keys_list[index]
        else:
            matches = [k for k in keys_list if k.lower().startswith(qidiruv)]
            if len(matches) == 1:
                ochiriladigan = matches[0]

        if ochiriladigan:
            del vault[ochiriladigan]
            save_vault(vault)
            print(f"\n🗑️ '{ochiriladigan}' to'liq o'chirildi!")
        else:
            print("❌ Topilmadi.")

    elif tanlov == "4":
        print("👋 Seyf yopildi. Xayr!")
        break
