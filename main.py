import os
import random
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  #запросы Telegram Mini App


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003728858401"

@app.route("/api/preorder", methods=["POST"])
def handle_preorder():
    data = request.json
    if not data:
        return jsonify({"error": "Пустой запрос"}), 400

    name = data.get("name")
    phone = data.get("phone")
    country = data.get("country")
    username = data.get("username", "Не указан")

    if not all([name, phone, country]):
        return jsonify({"error": "Заполните все поля!"}), 400

    order_id = random.randint(100000, 999999)

    # спецсимволы для HTML
    safe_name = str(name).replace("<", "&lt;").replace(">", "&gt;")
    safe_phone = str(phone).replace("<", "&lt;").replace(">", "&gt;")
    safe_country = str(country).replace("<", "&lt;").replace(">", "&gt;")
    
    if username != "Не указан":
        tg_line = f"@{username.replace('<', '&lt;').replace('>', '&gt;')}"
    else:
        tg_line = "нету"

    message_text = (
        f"📦 <b>НОВЫЙ ПРЕДЗАКАЗ</b>\n\n"
        f"🔢 <b>Номер заказа:</b> #{order_id}\n"
        f"👤 <b>Имя:</b> {safe_name}\n"
        f"📞 <b>Телефон:</b> {safe_phone}\n"
        f"🌍 <b>Страна:</b> {safe_country}\n"
        f"💬 <b>Телеграм:</b> {tg_line}"
    )

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message_text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(telegram_url, json=payload)
        telegram_result = response.json()

        if response.status_code == 200 and telegram_result.get("ok"):
            return jsonify({"status": "success", "order_id": order_id}), 200
        else:
            return jsonify({
                "error": "Ошибка Telegram API",
                "details": telegram_result.get("description", response.text)
            }), 500
            
    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка сервера: {str(e)}"}), 500



@app.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    update = request.json
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        
        if text == "/start":
            welcome_text = "Привет! В этом приложении ты сможешь сделать предзаказ на блокнот. ✨"
            payload = {
                "chat_id": chat_id,
                "text": welcome_text
            }
            send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(send_url, json=payload)
            
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "Бот работает!", 200
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
