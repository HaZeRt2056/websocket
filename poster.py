import hashlib
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Секретный ключ вашего приложения
client_secret = 'f671fc89ccaa3eae51ea5894c00a58c2'


@app.route('/webhook', methods=['POST'])
def webhook():
    post_json = request.get_json()
    verify_original = post_json['verify']
    del post_json['verify']

    verify = [
        post_json['account'],
        post_json['object'],
        post_json['object_id'],
        post_json['action'],
    ]

    # Если есть дополнительные параметры
    if 'data' in post_json:
        verify.append(post_json['data'])
    verify.append(post_json['time'])
    verify.append(client_secret)

    # Создаём строку для верификации запроса клиентом
    verify = hashlib.md5(';'.join(map(str, verify)).encode()).hexdigest()

    # Проверяем валидность данных
    if verify != verify_original:
        return '', 403

    # Если не ответить на запрос, Poster продолжит слать Webhook
    return jsonify({'status': 'accept'})

if __name__ == '__main__':
    app.run(debug=True)
