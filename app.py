import os
import logging
import wikipedia
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from flask import Flask
from threading import Thread

# Flask server for 24/7 (UptimeRobot uchun)
app = Flask('')

@app.route('/')
def home():
    return "🤖 Wikipedia Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Start Flask server
keep_alive()

# Environment variables
API_TOKEN = os.getenv('BOT_TOKEN')

wikipedia.set_lang('uz')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "🤖 Wikipedia Bot\n\n"
        "Mavzu nomini yuboring!\n\n"
        "📚 Misollar:\n"
        "• Namangan\n• Python\n• Alisher Navoiy\n• Matematika"
    )
    await message.reply(welcome_text)

@dp.message_handler(commands=['status'])
async def status_command(message: types.Message):
    await message.answer("✅ Bot ishlayapti!")

@dp.message_handler(commands=['mavzular'])
async def topics_command(message: types.Message):
    topics_text = (
        "🧭 Mavzu misollari:\n\n"
        "🏛 Shaharlar: Namangan, Andijon, Farg'ona\n"
        "👨‍🎓 Shaxslar: Alisher Navoiy, Amir Temur\n"
        "🔬 Fan: Python, Matematika, Fizika\n"
        "🌍 Davlatlar: O'zbekiston, Qozog'iston"
        "18+ savollarga javob yo'q"
    )
    await message.answer(topics_text)

def smart_search(query):
    """Aqlli ko'p tilli qidiruv"""
    languages = [('uz', "🇺🇿 O'zbekcha"), ('ru', "🇷🇺 Ruscha"), ('en', "🇺🇸 Inglizcha")]
    
    for lang_code, lang_name in languages:
        try:
            wikipedia.set_lang(lang_code)
            result = wikipedia.summary(query, sentences=5)
            return f"{lang_name}:\n\n{result}"
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:6]
            options_text = "\n".join([f"• {opt}" for opt in options])
            return f"❌ Noaniq!\n\nVariantlar:\n{options_text}"
        except wikipedia.exceptions.PageError:
            continue
        except Exception:
            continue
    
    return None

@dp.message_handler()
async def handle_message(message: types.Message):
    user_text = message.text.strip()
    
    if not user_text or user_text.startswith('/'):
        return
    
    await message.answer("🔍 Qidirilmoqda...")
    
    result = smart_search(user_text)
    
    if result:
        await message.answer(result)
    else:
        await message.answer("❌ Ma'lumot topilmadi! To'g'ri ma'lumot yozsangchi")

if __name__ == '__main__':
    print("🤖 Bot ishga tushmoqda...")
    executor.start_polling(dp, skip_updates=True)

