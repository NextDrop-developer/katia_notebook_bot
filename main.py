import os
import random
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (нужно только для локальных тестов)
load_dotenv()

app = Flask(__name__)
CORS(app)  # Разрешаем запросы от твоего Telegram Mini App на GitHub Pages

# --- НАСТРОЙКИ (Берутся из Environment Variables на Render) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003728858401"


@app.route("/api/preorder", methods=["POST"])
def handle_preorder():
    data = request.json
    if not data:
        return jsonify({"error": "Пустой запрос"}), 400

    # Получаем данные, которые прислал фронтенд
    name = data.get("name")
    phone = data.get("phone")
    country = data.get("country")
    username = data.get("username", "Не указан")

    # Проверяем, что обязательные поля заполнены
    if not all([name, phone, country]):
        return jsonify({"error": "Заполните все поля!"}), 400

    # Генерируем случайный номер заказа
    order_id = random.randint(100000, 999999)

    # Заменяем опасные символы в пользовательском вводе, чтобы не сломать HTML-разметку ТГ
    safe_name = str(name).replace("<", "&lt;").replace(">", "&gt;")
    safe_phone = str(phone).replace("<", "&lt;").replace(">", "&gt;")
    safe_country = str(country).replace("<", "&lt;").replace(">", "&gt;")
    
    if username != "Не указан":
        tg_line = f"@{username.replace('<', '&lt;').replace('>', '&gt;')}"
    else:
        tg_line = "нету"

    # Формируем текст сообщения с использованием надежных HTML-тегов <b>
    message_text = (
        f"📦 <b>НОВЫЙ ПРЕДЗАКАЗ</b>\n\n"
        f"🔢 <b>Номер заказа:</b> #{order_id}\n"
        f"👤 <b>Имя:</b> {safe_name}\n"
        f"📞 <b>Телефон:</b> {safe_phone}\n"
        f"🌍 <b>Страна:</b> {safe_country}\n"
        f"💬 <b>Телеграм:</b> {tg_line}"
    )

    # URL для отправки запроса в Telegram API
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message_text,
        "parse_mode": "HTML",  # Теперь строго HTML-теги, они не ломаются
    }

    try:
        response = requests.post(telegram_url, json=payload)
        telegram_result = response.json()

        # Если Telegram одобрил отправку
        if response.status_code == 200 and telegram_result.get("ok"):
            return jsonify({"status": "success", "order_id": order_id}), 200
        else:
            # Возвращаем ошибку ТГ, чтобы сразу видеть её в консоли приложения
            return jsonify({
                "error": "Ошибка Telegram API",
                "details": telegram_result.get("description", response.text)
            }), 500
            
    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка сервера: {str(e)}"}), 500


if __name__ == "__main__":
    # На Render порт подставится автоматически. Локально запустится на 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
