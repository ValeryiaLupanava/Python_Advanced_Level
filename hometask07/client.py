"""
Программа-клиент.
Функции клиента:
1. сформировать presence-сообщение;
2. отправить сообщение серверу;
3. получить ответ сервера;
4. разобрать сообщение сервера;
5. параметры командной строки скрипта client.py <addr> [<port>]:
    addr — ip-адрес сервера;
    port — tcp-порт на сервере, по умолчанию 7777.
"""

import sys
import json
import socket
import time
import logging
import argparse
from common.variables import ACTION, PRESENCE, TIME, ACCOUNT_NAME, \
    USER, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, \
    NAME, SURNAME, HOST, IP_ADDRESS, SENDER, MESSAGE, MESSAGE_TEXT
from common.utils import get_message, send_message
import logs.client_log_config
from decorator import log

CLIENT_LOGGER = logging.getLogger('log_client')

@log
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        CLIENT_LOGGER.info(f"Получено сообщение от пользователя " \
                           f"{message[SENDER]}:\n{message[MESSAGE_TEXT]}.")
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}.')


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной комманды
    """
    message = input('Введите сообщение для отправки или \'quit\' для завершения работы: ')
    if message.lower() == 'quit':
        sock.close()
        CLIENT_LOGGER.info("Завершение работы по команде пользователя." \
                           "До свидания.")
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}.')
    return message_dict


@log
def create_presence(account_name='Guest'):
    """Функция генерирует запрос о присутствии клиента"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}.')
    return out

@log
def process_ans(message):
    '''
    Функция разбирает ответ сервера
    :param message:
    :return:
    '''
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return f"200 : OK. HOST: {DEFAULT_IP_ADDRESS}. PORT: {DEFAULT_PORT}"

        return f"400 : {message[ERROR]}"
    raise ValueError

@log
def arg_parser():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    # Проверим допустим ли выбранный режим работы клиента
    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f"Указан недопустимый режим работы {client_mode}, " \
                               f"допустимые режимы: listen , send")
        sys.exit(1)

    return server_address, server_port, client_mode

def main():
    '''Загружаем параметы коммандной строки'''
    CLIENT_LOGGER.info('Запуск клиента.')
    server_address, server_port, client_mode = arg_parser()
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence())
        answer = process_ans(get_message(transport))
        CLIENT_LOGGER.info(f"Соедиение с сервером: {server_address} {server_port}.")
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
        CLIENT_LOGGER.error(f"Получены пустые значения для адреса и порта сервера. " \
                            f"Для дальнейшей работы будут использовать значения по " \
                            f"умолчанию: {server_address} {server_port}.")
    except ValueError:
        CLIENT_LOGGER.error("В качестве порта может быть указано только " \
                            "число в диапазоне от 1024 до 65535.")
        sys.exit(1)

    # Инициализация сокета и обмен
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    CLIENT_LOGGER.info(f"Сокет: {transport}.")

    message_to_server = create_presence()
    CLIENT_LOGGER.info(f"Ответ серверу сформирован: {message_to_server}.")
    send_message(transport, message_to_server)
    CLIENT_LOGGER.info("Ответ серверу отправлен.")

    try:
        answer = process_ans(get_message(transport))
        CLIENT_LOGGER.debug(f"Получено сообщение от сервера: {answer}.")
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOGGER.error("Не удалось декодировать сообщение сервера.")
        sys.exit(1)
    else:
        # Обмен сообщений
        if client_mode == 'send':
            CLIENT_LOGGER.info(f"Режим работы: {client_mode}.")
        else:
            CLIENT_LOGGER.info(f"Режим работы: {client_mode}.")
        while True:
            # Отправка сообщений
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)
            # Прием сообщений
            if client_mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                    CLIENT_LOGGER.debug(f"Получено сообщение от сервера: {message_from_server(get_message(transport))}.")
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f"Соединение с сервером {server_address} было потеряно.")
                    sys.exit(1)


if __name__ == '__main__':
    main()


