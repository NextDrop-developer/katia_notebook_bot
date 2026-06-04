Import os
import random
import aiohttp
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1003728858401  # <-- твой канал

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


async def send_to_telegram(text):
    async with aiohttp.ClientSession() as session:
        await session.post(API_URL, data={
            "chat_id": CHANNEL_ID,
            "text": text
        })


async def order(request):
    try:
        data = await request.json()

        name = data.get("name")
        country = data.get("country")
        phone = data.get("phone")
        username = data.get("username", "Hidden")

        order_id = random.randint(1000, 9999)

        message = (
            f"🛒 НОВЫЙ ЗАКАЗ #{order_id}\n\n"
            f"👤 Имя: {name}\n"
            f"🌍 Страна: {country}\n"
            f"📞 Телефон: {phone}\n"
            f"💬 TG: @{username}"
        )

        await send_to_telegram(message)

        return web.json_response({"status": "ok", "order": order_id})

    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)})


app = web.Application()
app.router.add_post("/order", order)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
