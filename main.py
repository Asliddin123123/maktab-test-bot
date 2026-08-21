import os
import random
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from questions import QUIZ_DATA

BOT_TOKEN = "BU_YERGA_TOKENINGIZNI_YOZING"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 24/7 Ishlashi uchun veb-server sozlamalari
async def handle(request):
    return web.Response(text="Bot 24/7 rejimda faol ishlamoqda!")

app = web.Application()
app.router.add_get('/', handle)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# Foydalanuvchi ma'lumotlari xotirasi
user_data = {}
user_sessions = {}

def get_user_db(user_id: int):
    if user_id not in user_data:
        user_data[user_id] = {
            "total_solved": 0,
            "correct_count": 0,
            "balance": 0,
            "solved_questions": set(),
            "hard_questions": []
        }
    return user_data[user_id]

def get_main_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Mashq boshlash")],
            [KeyboardButton(text="📊 Natijalarim"), KeyboardButton(text="🔥 Qiyin savollarim")]
        ],
        resize_keyboard=True
    )
    return kb

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    get_user_db(message.from_user.id)
    await message.answer(
        f"Salom, {message.from_user.full_name}!\n"
        f"Maktab testlari botiga xush kelibsiz. Tanlang:",
        reply_markup=get_main_menu()
    )

# 📚 Mashq boshlash
@dp.message(F.text == "📚 Mashq boshlash")
async def start_practice(message: types.Message):
    user_id = message.from_user.id
    db = get_user_db(user_id)
    
    available_questions = [
        q for q in QUIZ_DATA 
        if q["question"] not in db["solved_questions"] and q not in db["hard_questions"]
    ]
    
    if not available_questions:
        await message.answer("🎉 Tabriklaymiz! Siz bazadagi barcha 1000 ta testni to'liq yechib bo'ldingiz!")
        return

    sample_size = min(20, len(available_questions))
    selected_questions = random.sample(available_questions, sample_size)
    
    user_sessions[user_id] = {
        "questions": selected_questions,
        "current_index": 0,
        "mode": "normal"
    }
    
    await message.answer(f"🚀 Siz uchun {sample_size} ta yangi test tanlandi. Omad!")
    await send_next_question(message.chat.id, user_id)

# 🔥 Qiyin savollarim
@dp.message(F.text == "🔥 Qiyin savollarim")
async def start_hard_practice(message: types.Message):
    user_id = message.from_user.id
    db = get_user_db(user_id)
    
    if not db["hard_questions"]:
        await message.answer("🎉 Sizda hozircha qiyin (xato qilingan) savollar yo'q!")
        return

    user_sessions[user_id] = {
        "questions": list(db["hard_questions"]),
        "current_index": 0,
        "mode": "hard"
    }
    
    await message.answer(f"🔥 Ilgari xato qilgan {len(db['hard_questions'])} ta savolingiz qayta taqdim etilmoqda:")
    await send_next_question(message.chat.id, user_id)

# Savol yuborish
async def send_next_question(chat_id: int, user_id: int):
    session = user_sessions.get(user_id)
    if not session:
        return

    idx = session["current_index"]
    questions = session["questions"]

    if idx < len(questions):
        q = questions[idx]
        
        await bot.send_poll(
            chat_id=chat_id,
            question=f"[{idx + 1}/{len(questions)}] {q['question']}",
            options=q['options'],
            type="quiz",
            correct_option_id=q['correct_option_id'],
            is_anonymous=False
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="💡 Yordam (100 tanga)", callback_data="use_hint")
        
        await bot.send_message(
            chat_id,
            "Qiynalsangiz, yordam tugmasidan foydalanishingiz mumkin:",
            reply_markup=builder.as_markup()
        )
    else:
        await bot.send_message(
            chat_id,
            "🎉 **Sessiya yakunlandi!**\nNatijalaringizni ko'rish uchun **📊 Natijalarim** tugmasini bosing.",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        del user_sessions[user_id]

# 💡 Yordam (100 tanga)
@dp.callback_query(F.data == "use_hint")
async def handle_hint(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    db = get_user_db(user_id)
    session = user_sessions.get(user_id)

    if not session:
        await callback.answer("Aktiv test topilmadi.", show_alert=True)
        return

    if db["balance"] < 100:
        await callback.answer("⚠️ Balansingiz yetarli emas! Yordam olish uchun kamida 100 tanga kerak.", show_alert=True)
        return

    db["balance"] -= 100
    idx = session["current_index"]
    current_q = session["questions"][idx]
    correct_id = current_q["correct_option_id"]
    options = current_q["options"]

    wrong_indices = [i for i in range(len(options)) if i != correct_id]
    keep_wrong_id = random.choice(wrong_indices)

    hint_text = (
        f"💡 **Yordam ishlatildi (-100 tanga)!**\n\n"
        f"Javob faqat ushbu 2 ta variantdan biri:\n"
        f"1️⃣ **{options[correct_id]}**\n"
        f"2️⃣ **{options[keep_wrong_id]}**"
    )

    await callback.message.edit_text(hint_text, parse_mode="Markdown")
    await callback.answer("100 tanga yechildi!")

# Test javobi
@dp.poll_answer()
async def handle_poll_answer(poll_answer: types.PollAnswer):
    user_id = poll_answer.user.id
    db = get_user_db(user_id)
    session = user_sessions.get(user_id)
    
    if not session:
        return

    idx = session["current_index"]
    current_q = session["questions"][idx]
    user_option = poll_answer.option_ids[0]
    correct_option = current_q["correct_option_id"]

    db["total_solved"] += 1

    if user_option == correct_option:
        db["correct_count"] += 1
        db["balance"] += 20
        db["solved_questions"].add(current_q["question"])
        
        if current_q in db["hard_questions"]:
            db["hard_questions"].remove(current_q)
            
        await bot.send_message(user_id, "✅ To'g'ri javob! Balansga +20 tanga qo'shildi.")
    else:
        correct_text = current_q["options"][correct_option]
        await bot.send_message(
            user_id, 
            f"❌ Noto'g'ri!\nTo'g'ri javob: **{correct_text}**", 
            parse_mode="Markdown"
        )
        
        if current_q not in db["hard_questions"]:
            db["hard_questions"].append(current_q)

    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Keyingi savol", callback_data="next_question")
    await bot.send_message(user_id, "Keyingi savolga o'tish uchun tugmani bosing:", reply_markup=builder.as_markup())

# ➡️ Keyingi savol
@dp.callback_query(F.data == "next_question")
async def next_question_cb(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    session = user_sessions.get(user_id)
    
    if session:
        session["current_index"] += 1
        await callback.answer()
        await send_next_question(callback.message.chat.id, user_id)
    else:
        await callback.answer("Sessiya yakunlangan.", show_alert=True)

# 📊 Natijalarim
@dp.message(F.text == "📊 Natijalarim")
async def show_results(message: types.Message):
    db = get_user_db(message.from_user.id)
    
    text = (
        f"📊 **Sizning natijalaringiz:**\n\n"
        f"📝 Jami yechilgan testlar: **{db['total_solved']} ta**\n"
        f"✅ Muvaffaqiyatli topshirilgan: **{len(db['solved_questions'])} ta**\n"
        f"🔥 Qiyin (xato) testlar: **{len(db['hard_questions'])} ta**\n"
        f"💰 Balansingiz: **{db['balance']} tanga**"
    )
    await message.answer(text, parse_mode="Markdown")

async def main():
    await start_web_server()
    print("Bot va 24/7 Veb-server ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())