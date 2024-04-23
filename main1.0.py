from flask import Flask, jsonify,request
from flask_socketio import SocketIO, emit
import json

from configs import *

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/', methods=['POST'])
def handle_post():
    print(request.get_json())
    # Обработка POST запроса здесь
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