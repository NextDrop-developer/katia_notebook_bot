import asyncio
import json
import random
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# Токен берем из переменных окружения (Environment Variables в Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID менеджера (твой или Кати) оставляем жестко в коде
MANAGER_CHAT_ID = 6127906696 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- СЕРВЕР ДЛЯ ОБМАНА RENDER (чтобы не падал порт) ---
async def handle_health(request):
    return web.Response(text="Bot is running...")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render сам назначит порт
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# --- ЛОГИКА БОТА ---
def get_webapp_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📒 Открыть блокнот", web_app=WebAppInfo(url="https://nextdrop-developer.github.io/katia_notebook_bot/"))]
    ])
    return keyboard

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Нажми на кнопку ниже, чтобы посмотреть блокнот и сделать предзаказ ✨", 
        reply_markup=get_webapp_keyboard()
    )

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        # Парсим то, что прилетело из твоего HTML
        data = json.loads(message.web_app_data.data)
        
        name = data.get("name")
        country = data.get("country")
        phone = data.get("phone")
        order_number = random.randint(1000, 9999)
        username = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"

        # Ответ пользователю
        await message.answer(f"✅ Спасибо! Ваш заказ #{order_number} принят. Менеджер скоро свяжется с вами.")
        
        # Отправка лида тебе/Кате
        manager_msg = (
            f"🚨 **НОВЫЙ ПРЕДЗАКАЗ!**\n\n"
            f"📦 Номер: #{order_number}\n"
            f"👤 Имя: {name}\n"
            f"🌍 Страна: {country}\n"
            f"📞 Тел: {phone}\n"
            f"💬 TG: {username}"
        )
        await bot.send_message(chat_id=MANAGER_CHAT_ID, text=manager_msg, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Ошибка в handle_web_app_data: {e}")

async def main():
    # Запускаем сервер и бота в одном цикле
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
