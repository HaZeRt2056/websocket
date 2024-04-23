from flask import Flask, jsonify,request
from flask_socketio import SocketIO, emit
import json

from configs import *

app = Flask(__name__)
socketio = SocketIO(app)

import requests

@app.route('/', methods=['POST'])
def handle_post():
    print("ew")
    data = request.get_json()
    print(data)

    if 'data' in data:
        data_json = json.loads(data['data'])
        if 'transactions_history' in data_json and 'type_history' in data_json['transactions_history'] and \
                data_json['transactions_history']['type_history'] == 'changeprocessingstatus':
            # Выполняем GET-запрос
            transaction_id = data['object_id']
            token = TOKEN
            url = f"https://joinposter.com/api/dash.getTransaction?token={token}&transaction_id={transaction_id}&include_history=true&include_products=true&include_delivery=true"
            response = requests.get(url)
            # Выводим результат GET-запроса
            print(response.json())

            data = response.json()

            if 'response' in data and isinstance(data['response'], list):
                for item in data['response']:
                    if 'delivery' in item and 'courier_id' in item['delivery']:
                        # Если courier_id присутствует, отправляем запрос
                        response_employees = requests.get(
                            f'https://joinposter.com/api/access.getEmployees?token={TOKEN}')

                        # Проверяем успешность запроса
                        if response_employees.status_code == 200:
                            employees_data = response_employees.json()
                            print(employees_data)
                        else:
                            print("Ошибка при выполнении запроса")

                        break  # Прерываем цикл, если нашли courier_id
            return jsonify(message="POST request received"), 200

    return jsonify(message="POST request received"), 200


@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'success', 'message': 'You are now connected to the server'})
    return jsonify(message="Hello, World!"), 200


@socketio.on('message')
def handle_message(message):
    try:
        data = json.loads(message)
        emit('message', data, broadcast=True)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
