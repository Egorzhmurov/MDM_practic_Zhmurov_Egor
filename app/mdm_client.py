import socketio

# клиент
sio = socketio.Client()

@sio.event
def connect():
    print("✅ Подключились к серверу")
    # отправим сообщение
    sio.emit('message', {'msg': 'Hello сервер!'})


@sio.event
def message(data):
    print(f"📩 Сервер прислал: {data}")


@sio.event
def disconnect():
    print("❌ Отключились от сервера")


sio.connect('http://127.0.0.1:8080')
sio.wait()
