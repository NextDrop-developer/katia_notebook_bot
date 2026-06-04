import asyncio
import json
import random
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = -1003728858401

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- WEB SERVER (Render keep-alive) ---
async def handle_health(request):
    return web.Response(text="Bot is running...")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)

    await site.start()

# --- KEYBOARD ---
def get_webapp_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📒 Открыть блокнот",
                web_app=WebAppInfo(
                    url="https://nextdrop-developer.github.io/katia_notebook_bot/"
                )
            )
        ]
    ])

# --- START ---
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Нажми на кнопку ниже, чтобы посмотреть блокнот и сделать предзаказ ✨",
        reply_markup=get_webapp_keyboard()
    )

# --- WEBAPP DATA (ИСПРАВЛЕНО) ---
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)

        name = data.get("name")
        country = data.get("country")
        phone = data.get("phone")

        order_number = random.randint(1000, 9999)
        username = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"

        await message.answer(
            f"✅ Спасибо! Ваш заказ #{order_number} принят. Менеджер скоро свяжется с вами."
        )

        manager_msg = (
            f"🚨 НОВЫЙ ПРЕДЗАКАЗ!\n\n"
            f"📦 Номер: #{order_number}\n"
            f"👤 Имя: {name}\n"
            f"🌍 Страна: {country}\n"
            f"📞 Тел: {phone}\n"
            f"💬 TG: {username}"
        )

        await bot.send_message(MANAGER_CHAT_ID, manager_msg)

    except Exception as e:
        print("ERROR web_app_data:", e)

# --- MAIN ---
async def main():
    print("BOT STARTING...")

    await bot.delete_webhook(drop_pending_updates=True)

    # запускаем web server в фоне
    asyncio.create_task(start_web_server())
    print("WEB SERVER TASK STARTED")

    # запускаем бот (главный цикл)
    await dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
