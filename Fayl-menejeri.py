#!/usr/bin/env python3
# ============================================================
# AI CODE REVIEWER v1.0 – Pydroid 3 / Termux Moslashgan
# ============================================================
import os
import time
import requests
import json

# API sozlamalari
OPENROUTER_API_KEY = "YOUR_API_KEY"  # Bu yerga OpenRouter kalitingizni qo'ying
MODEL_NAME = "deepseek/deepseek-chat"

# Kuzatiladigan papka (Pydroid 3 loyihalari papkasi yoki joriy papka)
WATCH_DIR = "." 

# Tahlil qilingan fayllarning oxirgi o'zgarish vaqtini saqlash
file_timestamps = {}

def analyze_code_with_ai(file_path, code_content):
    """Kodni OpenRouter orqali DeepSeek'ga yuborib tahlil qilish"""
    prompt = f"""Siz tajribali Python Senior Developer va Cyber Security mutaxassisiz. 
Quyidagi Python kodini tahlil qiling:
1. Xavfsizlik zaifliklari va xatolar bormi?
2. Kodni optimallashtirish (reaktent va tezroq qilish) bo'yicha maslahatlar.
3. Maksimal 3-4 ta eng muhim punktda, qisqa va aniq o'zbek tilida izoh bering.

KOD:
```python
{code_content}
```"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "AI Code Reviewer"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 500
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            print(f"[API XATO] Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ULANISH XATOSI] {e}")
        return None

def append_review_to_file(file_path, review_text):
    """AI taqrizini faylning oxiriga izoh ko'rinishida qo'shish"""
    formatted_review = "\n\n# " + "="*52 + "\n"
    formatted_review += "# AI REVIEW & SUGGESTIONS\n"
    formatted_review += "# " + "="*52 + "\n"
    
    for line in review_text.split("\n"):
        formatted_review += f"# {line}\n"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(formatted_review)
    print(f"[MUVAFFAQIYAT] {file_path} fayliga AI sharhi yozildi!")

def scan_and_review():
    """Papkadagi fayllarni skanerlash"""
    for root, _, files in os.walk(WATCH_DIR):
        for file in files:
            # Faqat .py fayllarni va o'zimizning reviewer skriptini o'zini o'tkazib yuborish
            if file.endswith(".py") and file != os.path.basename(__file__):
                file_path = os.path.join(root, file)
                
                try:
                    current_mtime = os.path.getmtime(file_path)
                except OSError:
                    continue

                # Agar fayl yangi bo'lsa yoki o'zgartirilgan bo'lsa
                if file_path not in file_timestamps:
                    file_timestamps[file_path] = current_mtime
                elif current_mtime > file_timestamps[file_path]:
                    file_timestamps[file_path] = current_mtime
                    
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Agar faylda allaqachon AI review bo'lsa, qayta-qayta review qilmaslik uchun ajratamiz
                    if "# AI REVIEW & SUGGESTIONS" in content:
                        clean_content = content.split("# AI REVIEW & SUGGESTIONS")[0].strip()
                    else:
                        clean_content = content.strip()

                    if not clean_content:
                        continue

                    print(f"\n[O'ZGARISH SEZILDI] {file} tahlil qilinmoqda...")
                    review = analyze_code_with_ai(file_path, clean_content)
                    
                    if review:
                        append_review_to_file(file_path, review)
                        # Fayl o'zgargani uchun mtime yangilanadi, uni saqlab qo'yamiz
                        file_timestamps[file_path] = os.path.getmtime(file_path)

if __name__ == "__main__":
    print("AI Code Reviewer ishga tushdi...")
    print(f"Kuzatilayotgan papka: {os.path.abspath(WATCH_DIR)}")
    print("Fayllarga o'zgartirish kiritsangiz, AI avtomatik tahlil qiladi.\n")
    
    while True:
        try:
            scan_and_review()
            time.sleep(3)  # Har 3 soniyada tekshiradi
        except KeyboardInterrupt:
            print("\nDastur to'xtatildi.")
            break
