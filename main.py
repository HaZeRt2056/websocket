from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import requests
import json

from configs import *

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/', methods=['POST'])
def handle_post():
    print("count")
    data_request = request.get_json()
    print("data_request:",data_request)

    if 'data' in data_request:
        data_json = json.loads(data_request['data'])
        if 'transactions_history' in data_json and 'type_history' in data_json['transactions_history'] and \
                data_json['transactions_history']['type_history'] == 'changeprocessingstatus':
            # Выполняем GET-запрос
            transaction_id = data_request['object_id']
            token = TOKEN
            url = f"https://joinposter.com/api/dash.getTransaction?token={token}&transaction_id={transaction_id}&include_history=true&include_products=true&include_delivery=true"
            response = requests.get(url)
            # Выводим результат GET-запроса
            print(response.json())

            data = response.json()

            product_names_str = []  # Создаем пустой список для сохранения названий продуктов

            if 'response' in data and isinstance(data['response'], list):
                for item in data['response']:
                    if 'delivery' in item and 'courier_id' in item['delivery']:
                        courier_id = item['delivery']['courier_id']  # Сохраняем courier_id

                        # Если courier_id присутствует, отправляем запрос
                        response_employees = requests.get(
                            f'https://joinposter.com/api/access.getEmployees?token={TOKEN}')

                        # Проверяем успешность запроса
                        if response_employees.status_code == 200:
                            response_data = response_employees.json()
                            if 'response' in response_data:
                                employees = response_data['response']
                                for employee in employees:
                                    if isinstance(employee, dict) and 'user_id' in employee:
                                        if str(employee['user_id']) == str(courier_id):
                                            login = employee.get('login')
                                            print(f"courier_id: {courier_id}, login: {login}")

                                            username = login.split('@')[0]

                                            if 'products' in item:
                                                for product in item['products']:
                                                    product_id = product['product_id']

                                                    # Формирование URL для запроса на получение информации о продукте
                                                    product_url = f"https://joinposter.com/api/menu.getProduct?token={TOKEN}&product_id={product_id}"

                                                    # Отправка запроса на получение информации о продукте
                                                    product_response = requests.get(product_url)

                                                    # Проверка успешности запроса
                                                    if product_response.status_code == 200:
                                                        product_data = product_response.json()
                                                        print(product_data)
                                                        # Проверка наличия данных и наличия ключа 'product_name'
                                                        if 'response' in product_data and 'product_name' in \
                                                                product_data['response']:
                                                            product_name = product_data['response']['product_name']
                                                            print(f"Название продукта: {product_name}")

                                                            # Добавляем название продукта в общий список
                                                            product_names_str.append(product_name)

                                                    print("Список всех продуктов:", product_names_str)



            # Теперь вы можете включить product_name в ваше сообщение
                                                    message = f"""
                                                =================x
Заказ № {data["response"][0].get('transaction_id', '')}

Заведение:
{data_request.get('account', 'нет данных')}

Доставить до:
{data["response"][0]['delivery'].get('delivery_time', '')}

Клиент:
{data["response"][0].get('client_firstname', '')} {data["response"][0].get('client_lastname', '')}

Телефон:
{data['response'][0].get('client_phone', '')}


Адрес: 
{data['response'][0]['delivery'].get('address1', '')}
{data['response'][0]['delivery'].get('address2', '')}


Координаты:
{data["response"][0]['delivery'].get('lat', '')},{data["response"][0]['delivery'].get('lng', '')}


Комментарий курьеру:
{data['response'][0]['delivery'].get('comment', '')}


Комментарий к чеку:
{data["response"][0].get("transaction_comment", '')}


Товары:
Заказ содержит следующие продукты: {product_names_str}.


К оплате: {data["response"][0]['sum']} €
Купюры клиента: {data["response"][0]['payed_cash']} €
Баланс бонусов: {data["response"][0]['payed_bonus']}
Метод оплаты: {'Наличные' if data["response"][0]['pay_type'] == '0' else 'Карта' if data["response"][0]['pay_type'] == '1' else 'Другой'}
=================
                                            """

                                                    data = {
                                                        "chat_id": int(username),
                                                        "message": message,
                                                        "transaction_id": {data["response"][0].get('transaction_id', '')},
                                                        "spot_id": {data["response"][0].get('spot_id', '')}                                                    }

                                                    try:
                                                        socketio.emit('message', data)
                                                    except json.JSONDecodeError as e:
                                                        print("Error decoding JSON:", e)

                                                    break
                                                else:
                                                    print("Не удалось получить название продукта.")
                                            else:
                                                print("Ошибка при запросе информации о продукте.")
                                    else:
                                        print("Некорректные данные о пользователе:", employee)
                        else:
                            print("Ошибка при выполнении запроса")

    return jsonify(message="POST request received"), 200


@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'success', 'message': 'You are now connected to the server'})
    return jsonify(message="Hello, World!"), 200


# Обрабатывать message
@socketio.on('message')
def handle_message(message):
    try:
        data = json.loads(message)
        emit('message', data, broadcast=True)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

print("123")
# Витя пидор
