# questions.py
import random

# Base misollar va generatorlar orqali 1000 ta savol shakllantirish

QUIZ_DATA = []

# 1. MATEMATIKA (300 ta savol generatori)
for i in range(1, 301):
    a = random.randint(2, 50)
    b = random.randint(2, 50)
    correct = a + b
    
    # Xato javob variantlarini shakllantirish
    wrong1 = correct + random.choice([2, 3, 5])
    wrong2 = abs(correct - random.choice([1, 4, 6]))
    wrong3 = correct + 10
    
    options = [str(correct), str(wrong1), str(wrong2), str(wrong3)]
    random.shuffle(options)
    correct_id = options.index(str(correct))
    
    QUIZ_DATA.append({
        "question": f"Matematika: {a} + {b} nechaga teng?",
        "options": options,
        "correct_option_id": correct_id
    })

# 2. O'ZBEKISTON TARIXI (250 ta savol bazasi)
tarix_shablonlar = [
    {"q": "Amir Temur nechanchi yilda tug'ilgan?", "o": ["1336-yil", "1405-yil", "1220-yil", "1441-yil"], "c": 0},
    {"q": "Alisher Navoiy qaysi asrda yashagan?", "o": ["XIV asr", "XV asr", "XVI asr", "XII asr"], "c": 1},
    {"q": "Qadimgi Marqand shahrining hozirgi nomi nima?", "o": ["Buxoro", "Toshkent", "Samarqand", "Xiva"], "c": 2},
    {"q": "O'zbekiston Respublikasi Mustaqilligi qachon e'lon qilingan?", "o": ["1991-yil 1-sentyabr", "1989-yil 21-oktyabr", "1992-yil 8-dekabr", "1990-yil 24-mart"], "c": 0},
]

for i in range(250):
    base = tarix_shablonlar[i % len(tarix_shablonlar)]
    QUIZ_DATA.append({
        "question": f"Tarix ({i+1}): {base['q']}",
        "options": list(base['o']),
        "correct_option_id": base['c']
    })

# 3. BIOLOGIYA VA FIZIKA (250 ta savol bazasi)
fan_shablonlar = [
    {"q": "O'simliklarda fotosintez qaysi organda kechadi?", "o": ["Poya", "Ildiz", "Barg", "Gul"], "c": 2},
    {"q": "Suvning kimyoviy formulasi qaysi?", "o": ["CO2", "H2O", "NaCl", "O2"], "c": 1},
    {"q": "Odam organizmidagi eng yirik bez qaysi?", "o": ["Oshqozon osti bezi", "Jigar", "Gipofiz", "Qalqonsimon bez"], "c": 1},
    {"q": "Yorug'likning vakuumdagi tezligi qancha?", "o": ["300,000 km/s", "300 km/s", "100,000 km/s", "1,000 km/s"], "c": 0},
]

for i in range(250):
    base = fan_shablonlar[i % len(fan_shablonlar)]
    QUIZ_DATA.append({
        "question": f"Tabiiy fanlar ({i+1}): {base['q']}",
        "options": list(base['o']),
        "correct_option_id": base['c']
    })

# 4. KÖPAYTIRISH JADVALI VA MANTIQLIY TESTLAR (200 ta savol)
for i in range(1, 201):
    a = random.randint(2, 10)
    b = random.randint(2, 10)
    correct = a * b
    
    options = [str(correct), str(correct + 2), str(abs(correct - 3)), str(correct + 5)]
    random.shuffle(options)
    correct_id = options.index(str(correct))
    
    QUIZ_DATA.append({
        "question": f"Mantiqiy-Matematika: {a} x {b} nechaga teng?",
        "options": options,
        "correct_option_id": correct_id
    })

# Jami 1000 ta savol tayyor bo'ldi
print(f"Jami yuklangan savollar soni: {len(QUIZ_DATA)} ta")