"""Тестирование приложения client"""

import unittest
from lesson05.client import create_presence, process_ans
from lesson05.common.variables import RESPONSE, DEFAULT_IP_ADDRESS, DEFAULT_PORT



class TestClientFunctions(unittest.TestCase):
    """"Набор unit-тестов для приложения client"""

    def test_msg_to_server_keys(self):
        """"Проверка наличия ключевых элементов в сообщении серверу"""
        msg_to_server = create_presence(account_name='Valeryia Lupanava')
        current_keys = list(msg_to_server.keys())
        necessary_keys = ['host', 'ip_address', 'user', 'action', 'time']
        self.assertEqual(current_keys, necessary_keys)

    def test_msg_to_server_empty(self):
        """"Проверка заполнения ключевых элементов в сообщении серверу"""
        msg_to_server = create_presence(account_name='Valeryia Lupanava')
        current_values = list(msg_to_server.values())
        current_length = len(current_values)
        minimum_length = len(['host', 'ip_address'])
        self.assertGreaterEqual(current_length, minimum_length)

    def test_is_correct_connection(self):
        """"Проверка сообщения на наличие корректного соединения с сервера"""
        msg_to_clnt = f'200 : OK.\nHOST: {DEFAULT_IP_ADDRESS}.\nPORT: {DEFAULT_PORT}.'
        msg_from_server = process_ans({RESPONSE: 200})
        self.assertEqual(msg_from_server, msg_to_clnt)


if __name__ == '__main__':
    unittest.main()
