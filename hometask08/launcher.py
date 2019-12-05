"""Программа запуска процессов"""

import subprocess

PROCESSES = []

while True:
    ACTION = input('Выберите действие:\n1. s -> запуск сервера и клиентов,\n2. e -> закрыть все окна,\n3. q -> выход.\n==> ')

    if ACTION == 'q':
        break

    elif ACTION == 's':
        PROCESSES.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n client1', creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n client2', creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n client3', creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n client4', creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif ACTION == 'e':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()
