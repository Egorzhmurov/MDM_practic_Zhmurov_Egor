import socketio
import eventlet
from eventlet import wsgi
import subprocess
import threading
import os

# Шлях до вашого ADB (перевірте, чи він збігається з вашим фактичним шляхом)
ADB_PATH = r"C:\Program Files (x86)\Android\android-sdk\platform-tools\adb.exe"

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

def operator_console():
    """Потік для керування пристроєм через консоль оператора"""
    while True:
        # Отримуємо команду від користувача
        cmd = input("MDM> ").strip().lower()


        # 1. ПЕРЕЗАВАНТАЖЕННЯ
        if cmd == "reboot":
            print("🔄 Перезавантаження через ADB...")
            try:
                subprocess.run([ADB_PATH, "reboot"], check=True)
                print("✅ Команда на перезавантаження відправлена")
            except Exception as e:
                print(f"❌ Помилка ADB: {e}")

        # 2. ЗМЕНШЕННЯ ГУЧНОСТІ
        elif cmd == "vol-":
            print("🔉 Зменшення гучності...")
            try:
                # Код 25 — системна подія натискання кнопки зменшення гучності
                subprocess.run([ADB_PATH, "shell", "input", "keyevent", "25"], check=True)
                print("✅ Гучність зменшено")
            except Exception as e:
                print(f"❌ Помилка ADB: {e}")

        # 3. ЗБІЛЬШЕННЯ ГУЧНОСТІ (додав для зручності)
        elif cmd == "vol+":
            print("🔊 Збільшення гучності...")
            try:
                # Код 24 — системна подія натискання кнопки збільшення гучності
                subprocess.run([ADB_PATH, "shell", "input", "keyevent", "24"], check=True)
                print("✅ Гучність збільшено")
            except Exception as e:
                print(f"❌ Помилка ADB: {e}")

        # 4. ВІДКРИТТЯ БРАУЗЕРА (приклад: url https://google.com)
        elif cmd.startswith("url "):
            try:
                url = cmd.split(" ")[1]
                if not url.startswith("http"):
                    url = "https://" + url
                print(f"🌐 Відкриття сайту: {url}...")
                # Запуск браузера через Android Intent
                subprocess.run([ADB_PATH, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url], check=True)
                print("✅ Браузер відкрито")
            except IndexError:
                print("❌ Помилка: введіть адресу після команди url (наприклад: url google.com)")
            except Exception as e:
                print(f"❌ Помилка ADB: {e}")

        # 5. ВИХІД
        elif cmd in ("exit", "quit"):
            print("⛔ Сервер зупинено")
            os._exit(0)

        else:
            print("❓ Невідома команда")
            print("Доступні команди: reboot, vol-, vol+, url <адреса>, exit")

@sio.event
def connect(sid, environ):
    """Обробка нового підключення від Android-пристрою"""
    client_ip = environ.get('REMOTE_ADDR')
    print(f"📡 Підключився новий пристрій! ID: {sid}")
    print(f"📍 IP адреса клієнта: {client_ip}")

    sio.emit('message', {'data': 'Ласкаво просимо до системи керування MDM'}, room=sid)

@sio.event
def message(sid, data):
    """Отримання даних від Android-пристрою"""
    print(f"📥 Отримано від {sid}: {data}")

@sio.event
def disconnect(sid):
    """Обробка відключення пристрою"""
    print(f"🔌 Пристрій відключено: {sid}")

if __name__ == '__main__':
    print("==========================================")
    print("🚀 MDM сервер успішно запущено!")
    print("🌐 Адреса сервера: 0.0.0.0:8080")
    print("🛠️ Доступні команди: reboot, vol-, vol+, url <посилання>, exit")
    print("==========================================")

    # Запуск консолі в окремому потоці, щоб не блокувати сервер
    threading.Thread(target=operator_console, daemon=True).start()

    # Запуск WSGI сервера
    try:
        eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8080)), app)
    except KeyboardInterrupt:
        print("\nСервер вимкнено користувачем")