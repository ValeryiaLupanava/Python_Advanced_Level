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
import threading
from common.variables import ACTION, PRESENCE, TIME, ACCOUNT_NAME, \
    USER, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, ADDRESSEE, \
    SENDER, MESSAGE, MESSAGE_TEXT, EXIT
from common.utils import get_message, send_message
import logs.client_log_config
from decorator import log

CLIENT_LOGGER = logging.getLogger('log_client')

@log
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def message_from_server(sock, my_username):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and ADDRESSEE in message \
                    and MESSAGE_TEXT in message and message[ADDRESSEE] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f"Получено сообщение от пользователя {message[SENDER]}:"
                                   f"\n{message[MESSAGE_TEXT]}")
            else:
                CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_message(sock, account_name='Guest'):
    """
    Функция запрашивает кому отправить сообщение и само сообщение,
    и отправляет полученные данные на сервер
    :param sock:
    :param account_name:
    :return:
    """
    addressee = input(f'{account_name}, введите получателя сообщения: ')
    if account_name == addressee:
        print("Вы ввели некорректного получателя.")
        time.sleep(3)
        sys.exit(1)

    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        ADDRESSEE: addressee,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {addressee}')
    except:
        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)

@log
def create_presence(account_name):
    """Функция генерирует запрос о присутствии клиента"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out

@log
def process_response_ans(message):
    """
    Функция разбирает ответ сервера на сообщение о присутствии,
    возращает 200 если все ОК или генерирует исключение при ошибке
    :param message:
    :return:
    """
    CLIENT_LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            return f'400 : {message[ERROR]}'
            raise


@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f"Попытка запуска клиента с неподходящим номером порта: {server_port}. "
            f"Допустимы адреса с 1024 до 65535. Клиент завершается.")
        sys.exit(1)

    return server_address, server_port, client_name


def main():
    """Сообщаем о запуске"""
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    CLIENT_LOGGER.info(
        f"Запущен клиент с парамертами: адрес сервера: {server_address}, "
        f"порт: {server_port}, имя пользователя: {client_name}.")

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_response_ans(get_message(transport))
        CLIENT_LOGGER.info(f"Установлено соединение с сервером. Ответ сервера: {answer}.")
        print(f"Установлено соединение с сервером.")
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(
            f"Не удалось подключиться к серверу {server_address}:{server_port}, "
            f"конечный компьютер отверг запрос на подключение.")
        sys.exit(1)
    else:
        # Если соединение с сервером установлено корректно,
        # запускаем клиенский процесс приёма сообщний
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        getter = threading.Thread(target=create_message, args=(transport, client_name))
        getter.daemon = True
        getter.start()


        while True:
            time.sleep(1)
            if receiver.is_alive() and getter.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
