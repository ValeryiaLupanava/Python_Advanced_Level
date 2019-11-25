"""Тестирование приложения server"""

import unittest
import time
import socket
from server import process_client_message
from common.variables import ACTION, RESPONSE, PRESENCE, \
    TIME, USER, IP_ADDRESS, HOST, NAME, SURNAME



class TestServerFunctions(unittest.TestCase):
    """"Набор unit-тестов для приложения server"""

    def test_msg_to_server_keys(self):
        """"Проверка наличия ключевых элементов в сообщении серверу"""
        msg_to_clnt = {RESPONSE: 200}
        msg_from_clnt = {HOST: socket.gethostname(),
                         IP_ADDRESS: socket.gethostbyname(socket.gethostname()),
                         USER: {
                             NAME: 'Valeryia',
                             SURNAME: 'Lupanava'
                         },
                         ACTION: PRESENCE,
                         TIME: time.time()}
        answ_to_clnt = process_client_message(msg_from_clnt)
        self.assertEqual(msg_to_clnt, answ_to_clnt)


if __name__ == '__main__':
    unittest.main()
