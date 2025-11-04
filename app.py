import os
import logging
import wikipedia
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Environment variables
API_TOKEN = os.getenv('BOT_TOKEN')
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL')  # Railway avtomatik beradi
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{RAILWAY_STATIC_URL}{WEBHOOK_PATH}" if RAILWAY_STATIC_URL else None

wikipedia.set_lang('uz')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "🤖 Wikipedia Bot (Railway)\n\n"
        "✨ Railway hostingda 24/7 ishlaydi\n\n"
        "Mavzu nomini yuboring!\n\n"
        "📚 Misollar:\n"
        "• Namangan\n• Python\n• Alisher Navoiy\n• Matematika"
    )
    await message.reply(welcome_text)

@dp.message_handler(commands=['status'])
async def status_command(message: types.Message):
    await message.answer("✅ Bot Railway da 24/7 ishlayapti!")

@dp.message_handler(commands=['mavzular'])
async def topics_command(message: types.Message):
    topics_text = (
        "🧭 Mavzu misollari:\n\n"
        "🏛️ Shaharlar: Namangan, Andijon, Farg'ona\n"
        "👨‍🎓 Shaxslar: Alisher Navoiy, Amir Temur\n"
        "🔬 Fan: Python, Matematika, Fizika\n"
        "🌍 Davlatlar: O'zbekiston, Qozog'iston"
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
        await message.answer("❌ Ma'lumot topilmadi!To'g'ri ma'lumot yozsangchi")

# Webhook sozlamalari
async def on_startup(app):
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook sozlandi: {WEBHOOK_URL}")
    else:
        print("⚠️ WEBHOOK_URL topilmadi")

async def on_shutdown(app):
    await bot.session.close()
    print("🔴 Bot to'xtatildi")

# Aiohttp app
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# Webhook handler
webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
webhook_requests_handler.register(app, path=WEBHOOK_PATH)

setup_application(app, dp, bot=bot)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Bot {port}-portda ishga tushmoqda...")
    web.run_app(app, host='0.0.0.0', port=port)
