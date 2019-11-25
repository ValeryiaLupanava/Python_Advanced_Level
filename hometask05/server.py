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
import json
import logging
from common.variables import ACTION, RESPONSE, \
    MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, \
    RESPONDEFAULT_IP_ADDRESSSE
from common.utils import get_message, send_message
import logs.server_log_config


SERVER_LOGGER = logging.getLogger('log_server')

def process_client_message(message):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента

    :param message:
    :return:
    '''

    SERVER_LOGGER.info(f'Сообщение клиента: {message}.')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESSSE: 400,
        ERROR: 'Bad Request'
    }


def main():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8888 -a 127.0.0.1
    :return:
    '''

    SERVER_LOGGER.info('Запуск сервера.')
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
            SERVER_LOGGER.info(f'Порт: {listen_port}.')
        else:
            listen_port = DEFAULT_PORT
            SERVER_LOGGER.info('Используется порт по умолчанию.')
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        SERVER_LOGGER.error('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        SERVER_LOGGER.error('В качастве порта может быть указано только число \
        в диапазоне от 1024 до 65535.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
            SERVER_LOGGER.info(f'Адрес: {listen_address}.')
        else:
            listen_address = ''
            SERVER_LOGGER.info('Используется адрес по умолчанию.')
    except IndexError:
        SERVER_LOGGER.error('После параметра \'a\'- необходимо указать адрес, который \
        будет слушать сервер.')
        sys.exit(1)

    # Готовим сокет

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    SERVER_LOGGER.info(f'Сокет: {transport}.')

    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        SERVER_LOGGER.info(f'Начинается соединение с клиентом.')
        SERVER_LOGGER.info(f'Соединение с клиентом {client} {client_address} установлено.')
        try:
            message_from_clnt = get_message(client)
            SERVER_LOGGER.debug(f'Получено сообщение от клиента: {message_from_clnt}.')
            response = process_client_message(message_from_clnt)
            SERVER_LOGGER.debug(f'Ответ клиенту сформирован: {response}.')
            send_message(client, response)
            SERVER_LOGGER.debug(f'Ответ клиенту отправлен.')
            client.close()
            SERVER_LOGGER.info(f'Соединение с клиентом закрыто.')
        except (ValueError, json.JSONDecodeError):
            SERVER_LOGGER.error('Принято некорретное сообщение от клиента.')
            client.close()
            SERVER_LOGGER.info(f'Соединение с клиентом закрыто.')


if __name__ == '__main__':
    main()
