import asyncio
import os
import random
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = 6127906696  # Сюда вставь числовой ID Кати (менеджера), чтобы ей летели лиды

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Кнопка для запуска WebApp
def get_webapp_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть блокнот", web_app=WebAppInfo(url="https://nextdrop-developer.github.io/katia_notebook_bot/"))]
    ])
    return keyboard


@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Нажми на кнопку ниже, чтобы посмотреть блокнот и сделать предзаказ ✨",
        reply_markup=get_webapp_keyboard()
    )


# Ловим данные, которые прислал нам WebApp при клике на "Подтвердить"
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        # Парсим JSON, который пришел из JavaScript
        data = json.loads(message.web_app_data.data)

        name = data.get("name")
        country = data.get("country")
        phone = data.get("phone")
        order_number = random.randint(1000, 9999)  # Генерируем красивый ID заказа

        username = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"

        # 1. Отвечаем юзеру
        await message.answer(
            f"Спасибо за ваш предзаказ!\n\n"
            f"Номер вашего заказа: #{order_number}\n"
            f"Менеджер скоро свяжется с вами. 💛"
        )

        # 2. Отправляем инфу Кате (Менеджеру)
        manager_message = (
            f"🚨 **Новый горячий предзаказ!**\n\n"
            f"📦 Заказ: #{order_number}\n"
            f"👤 Имя: {name}\n"
            f"🌍 Страна: {country}\n"
            f"📞 Телефон: {phone}\n"
            f"💬 Telegram: {username}"
        )
        await bot.send_message(chat_id=MANAGER_CHAT_ID, text=manager_message, parse_mode="Markdown")

    except Exception as e:
        await message.answer("Произошла ошибка при обработке заказа. Попробуйте еще раз.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
