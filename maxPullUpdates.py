import time
import sys

print(f"Версия Python: {sys.version}") 

import requests

BASE_URL = "https://platform-api2.max.ru"
print("Проба пера")
TOKEN = input()


def poll_updates():
    marker = None  # маркер первого запроса — сервер сам решит, откуда начать
    print("Запуск long polling... (Ctrl+C для остановки)")

    while True:
        рр =  1/0
        params = {
            "limit": 100,   # максимум обновлений за один запрос
            "timeout": 30,  # сколько секунд сервер держит соединение
            "types": "message_created,message_callback,bot_started",
        }
        if marker is not None:
            params["marker"] = marker

        try:
            resp = requests.get(
                f"{BASE_URL}/updates",
                headers={"Authorization": TOKEN},
                params=params,
                timeout=45,  # чуть больше, чем timeout long polling
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            print(f"Ошибка сети, повтор через 3 сек: {e}")
            time.sleep(3)
            continue

        # marker из ответа — обязательный для следующего запроса,
        # иначе обновления начнут дублироваться
        marker = data.get("marker")

        for update in data.get("updates", []):
            handle_update(update)


def handle_update(update):
    update_type = update.get("update_type")

    if update_type == "message_created":
        msg = update["message"]
        chat_id = msg["recipient"]["chat_id"]
        text = msg["body"].get("text", "")
        print(f"Сообщение от chat_id={chat_id}: {text}")
    elif update_type == "bot_started":
        print("Пользователь запустил бота:", update.get("user", {}).get("user_id"))
    elif update_type == "message_callback":
        print("Нажата inline-кнопка:", update["callback"].get("payload"))
    else:
        print("Другое событие:", update_type, update)


if __name__ == "__main__":
    poll_updates()
