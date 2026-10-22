import tkinter as tk
import threading
import requests
import speech_recognition as sr  # Mikrofon uchun

API_KEY = "YOUR_API_KEY'Y"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

def ovozli_yozish():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        natija_label.config(text="Eshitmoqdaman...", fg="#39ff14")
        audio = r.listen(source)
        try:
            savol = r.recognize_google(audio, language="uz-UZ")
            qidiruv_input.delete(0, tk.END)
            qidiruv_input.insert(0, savol)
            qidir()
        except:
            natija_label.config(text="Tushunmadim, qaytadan urin.", fg="red")

def qidir():
    savol = qidiruv_input.get()
    if not savol: return
    natija_label.config(text="AI o'ylamoqda...", fg="#00c8ff")
    threading.Thread(target=lambda: ai_javob(savol), daemon=True).start()

def ai_javob(savol):
    try:
        data = {"contents": [{"parts": [{"text": savol}]}]}
        javob = requests.post(URL, json=data, headers={'Content-Type': 'application/json'}).json()
        matn = javob['candidates'][0]['content']['parts'][0]['text']
        natija_label.config(text=matn, fg="white")
    except Exception as e:
        natija_label.config(text=f"Xato: {e}", fg="red")

# Interfeys
oyna = tk.Tk()
oyna.geometry("320x460")
oyna.configure(bg="#12141c")

qidiruv_input = tk.Entry(oyna, bg="#1c1f2b", fg="white", font=("Arial", 14))
qidiruv_input.pack(pady=20, fill="x", padx=20)

tk.Button(oyna, text="OVOHLI SO'RASH", bg="#39ff14", command=ovozli_yozish).pack()
tk.Button(oyna, text="MATNLI QIDIRISH", bg="#00c8ff", command=qidir).pack(pady=10)

natija_label = tk.Label(oyna, text="Kutmoqdaman...", bg="#12141c", fg="white", wraplength=280, justify="left")
natija_label.pack(pady=20)

oyna.mainloop()