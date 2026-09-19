import g4f

MODELS = [
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku",
    "gpt-4",
    "gpt-3.5-turbo",
    "llama-3-70b"
]

def ask_ai(prompt):
    # Tilni belgilash
    full_prompt = f"{prompt}\n\nIltimos, faqat o'zbek yoki ingliz tilida javob ber."
    for model in MODELS:
        try:
            resp = g4f.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                timeout=15
            )
            if resp:
                return f"[{model}] {resp}"
        except Exception:
            continue
    return "Hech qaysi model javob bermadi."

print("Bepul AI suhbatdoshi (exit/chiqish bilan to'xtaydi)")
while True:
    q = input(">>> ").strip()
    if q.lower() in ['exit', 'chiqish']:
        break
    if q:
        print(ask_ai(q))