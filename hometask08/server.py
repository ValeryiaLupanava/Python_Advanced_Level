"""
Программа-сервер.
Функции сервера:
1. принимает сообщение клиента;
2. формирует ответ клиенту;
3. отправляет ответ клиенту;
4. имеет параметры командной строки:
    -p <port> — TCP-порт для работы (по умолчанию использует 7777);
    -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
"""

import socket
import sys
import logging
import argparse
import select
from common.variables import ACTION, ADDRESSEE, EXIT, \
    MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, \
    ACCOUNT_NAME, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE
from common.utils import get_message, send_message
import logs.server_log_config
from decorator import log


SERVER_LOGGER = logging.getLogger('log_server')

@log
def process_client_message(message, messages_list, client, clients, names):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
    проверяет корректность, отправляет словарь-ответ в случае необходимости
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}.')
    # Если это сообщение о присутствии, принимаем и отвечаем
    if ACTION in message and message[ACTION] == PRESENCE and \
            TIME in message and USER in message:
        # Если такой пользователь ещё не зарегистрирован,
        # регистрируем, иначе отправляем ответ и завершаем соединение.
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200})
        else:
            response = {RESPONSE: 400,
                        ERROR: None
                        }
            response[ERROR] = "Имя пользователя уже занято."
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # Если это сообщение, то добавляем его в очередь сообщений.
    # Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            ADDRESSEE in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    # Если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # Иначе отдаём Bad request
    else:
        response = {RESPONSE: 400,
                    ERROR: None
                    }
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает
    """
    if message[ADDRESSEE] in names and names[message[ADDRESSEE]] in listen_socks:
        send_message(names[message[ADDRESSEE]], message)
        SERVER_LOGGER.info(f"Отправлено сообщение пользователю {message[ADDRESSEE]} "
                           f"от пользователя {message[SENDER]}.")
    elif message[ADDRESSEE] in names and names[message[ADDRESSEE]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f"Пользователь {message[ADDRESSEE]} не зарегистрирован на сервере, "
            f"отправка сообщения невозможна.")


@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(
            f'Попытка запуска сервера с указанием неподходящего порта {listen_port}. '
            f'Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port


def main():
    """
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию
    """
    listen_address, listen_port = arg_parser()

    print(f"Запущен сервер.")

    SERVER_LOGGER.info(
        f"Запущен сервер, порт для подключений: {listen_port}, "
        f"адрес с которого принимаются подключения: {listen_address}. "
        f"Если адрес не указан, принимаются соединения с любых адресов.")
    # Готовим сокет
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    # список клиентов , очередь сообщений
    clients = []
    messages = []

    # Словарь, содержащий имена пользователей и соответствующие им сокеты.
    names = dict()

    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)
    # Основной цикл программы сервера
    while True:
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f"Установлено соедение с ПК {client_address}.")
            clients.append(client)

        recieved_data = []
        sent_data = []
        error_data = []

        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                recieved_data, sent_data, error_data = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # принимаем сообщения и если ошибка, исключаем клиента.
        if recieved_data:
            for client_with_message in recieved_data:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message, clients, names)
                except Exception:
                    SERVER_LOGGER.info(f"Клиент {client_with_message.getpeername()} "
                                       f"отключился от сервера.")
                    clients.remove(client_with_message)

        # Если есть сообщения, обрабатываем каждое.
        for i in messages:
            try:
                process_message(i, names, sent_data)
            except Exception:
                SERVER_LOGGER.info(f"Связь с клиентом с именем {i[ADDRESSEE]} была потеряна.")
                clients.remove(names[i[ADDRESSEE]])
                del names[i[ADDRESSEE]]
        messages.clear()


if __name__ == '__main__':
    main()
