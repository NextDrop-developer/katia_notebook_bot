import random
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем запросы от нашей веб-странички

# --- НАСТРОЙКИ (Вставь свои данные) ---
BOT_TOKEN = "СЮДА_ВСТАВЬ_ТОКЕН_БОТА"
CHANNEL_ID = "СЮДА_ВСТАВЬ_ID_КАНАЛА"  # Например, -100123456789


@app.route("/api/preorder", methods=["POST"])
def handle_preorder():
    data = request.json

    # Получаем данные из формы
    name = data.get("name")
    phone = data.get("phone")
    country = data.get("country")
    # Юзернейм автоматически подтянется из Telegram Mini App
    username = data.get("username", "Не указан")

    if not all([name, phone, country]):
        return jsonify({"error": "Заполните все поля!"}), 400

    # Генерируем рандомный номер заказа
    order_id = random.randint(100000, 999999)

    # Формируем текст поста для менеджера
    message_text = (
        f"📦 **НОВЫЙ ПРЕДЗАКАЗ**\n\n"
        f"🔢 **Номер заказа:** #{order_id}\n"
        f"👤 **Имя:** {name}\n"
        f"📞 **Телефон:** {phone}\n"
        f"🌍 **Страна:** {country}\n"
        f"💬 **Телеграм:** @{username if username != 'Не указан' else 'нету'}"
    )

    # Отправляем сообщение в приватный канал через Telegram API
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message_text,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(telegram_url, json=payload)
        if response.status_code == 200:
            return jsonify({"status": "success", "order_id": order_id}), 200
        else:
            return (
                jsonify({"error": "Ошибка отправки в ТГ канал"}),
                500,
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
