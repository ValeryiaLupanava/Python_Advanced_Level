"""Программа запуска процессов"""

import subprocess

PROCESSES = []

while True:
    ACTION = input('Выберите действие:\n1. s -> запуск сервера и клиентов,\n2. e -> закрыть все окна,\n3. q -> выход.\n==> ')

    if ACTION == 'q':
        break

    elif ACTION == 's':
        PROCESSES.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(2):
            PROCESSES.append(subprocess.Popen('python client.py -m send',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(2):
            PROCESSES.append(subprocess.Popen('python client.py -m listen',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif ACTION == 'e':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()
