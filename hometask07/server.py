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
import time
import select
from common.variables import ACTION, RESPONSE, \
    MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, \
    ACCOUNT_NAME, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message
import logs.server_log_config
from decorator import log


SERVER_LOGGER = logging.getLogger('log_server')

@log
def process_client_message(message, messages_list, client):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента

    :param message:
    :return:
    '''

    SERVER_LOGGER.debug(f"Сообщение клиента: {message}.")
    # Если это сообщение о присутствии, принимаем и отвечаем, если успех
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    # Иначе отдаём Bad request
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return

@log
def arg_parser():
    """Парсинг аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default='', nargs='?')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.error("В качастве порта может быть указано только число " \
                            "в диапазоне от 1024 до 65535.")
        sys.exit(1)

    return listen_address, listen_port


def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""

    SERVER_LOGGER.info("Запуск сервера.")

    listen_address, listen_port = arg_parser()
    try:
        if listen_port == DEFAULT_PORT:
            SERVER_LOGGER.info("Используется порт по умолчанию.")
        else:
            SERVER_LOGGER.info(f"Порт: {listen_port}.")
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        SERVER_LOGGER.error("После параметра -'p' необходимо указать номер порта.")
        sys.exit(1)
    except ValueError:
        SERVER_LOGGER.error("В качастве порта может быть указано только число "\
                            "в диапазоне от 1024 до 65535.")
        sys.exit(1)

    try:
        if listen_address == '':
            SERVER_LOGGER.info("Используется адрес по умолчанию.")
        else:
            SERVER_LOGGER.info(f"Адрес: {listen_address}.")
    except IndexError:
        SERVER_LOGGER.error("После параметра 'a'- необходимо указать адрес, который "\
                            "будет слушать сервер.")
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER_LOGGER.info(f"Сокет: {transport}.")

    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    # Список клиентов , очередь сообщений
    clients = []
    messages = []

    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)
    # Основной цикл программы сервера
    SERVER_LOGGER.info(f"Начинается соединение с клиентами.")
    while True:
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f"Соединение с клиентом {client} {client_address} установлено.")
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            SERVER_LOGGER.debug(f"Системная ошибка была замечена: {OSError}.")
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message)
                    SERVER_LOGGER.debug(f"Получено сообщение от клиента: {get_message(client_with_message)}.")
                except:
                    SERVER_LOGGER.info(f"Клиент {client_with_message.getpeername()} отключился от сервера.")
                    clients.remove(client_with_message)
                    SERVER_LOGGER.info(f"Сообщение клиента удалено.")

        # Отправка сообщений
        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f"Клиент {waiting_client.getpeername()} отключился от сервера.")
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
