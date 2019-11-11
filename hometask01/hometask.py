"""homework"""

import subprocess
import chardet


class Homework:

    # Task 1
    def task_1_0(data):
        print('The result of task_1_0:')
        for elem in data:
            print(elem)
            print(type(elem))

    def task_1_1(data):
        print('The result of task_1_1:')
        for elem in data:
            print(elem)
            print(type(elem))

    # Task 2
    def task_2(data):
        print('The result of task_2:')
        for elem in data:
            print(bytes(elem, encoding='utf-8'))
            print(type(bytes(elem, encoding='utf-8')))
            print(len(bytes(elem, encoding='utf-8')))

    # Task 3
    def task_3(data):
        print('The result of task_3')
        failed = []
        for elem in data:
            try:
                print(bytes(elem, encoding='ASCII'))
            except BaseException:
                failed.append(elem.rstrip())
        print('The following words could not be transformed:', failed)

    # Task 4
    def task_4(data):
        print('The result of task_4:')
        for elem in data:
            elem_bytes = str.encode(elem, encoding='utf-8')
            print(elem_bytes)
            print(elem_bytes.decode('utf-8'))

    # Task 5
    def task_5(data):
        print('The result of task_5:')
        for link in data:
            PING = subprocess.Popen(link, stdout=subprocess.PIPE)
            print(PING)
            for line in PING.stdout:
                result = chardet.detect(line)
                line = line.decode(result['encoding']).encode('utf-8')
                print(line.decode('utf-8'))

    # Task 6
    def task_6(data):
        print('The result of task_6:')
        CR = open(data[0], 'w+', encoding='utf-8')
        CR.write('сетевое программирование\n' + 'сокет\n' + 'декоратор\n')
        CR.close()
        print(type(CR))

        with open('test_file.txt', encoding='utf-8') as cr:
            for el_str in cr:
                print(el_str, end='')

WORDS_1 = ['разработка', 'сокет', 'декоратор']
WORDS_2 = ['\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
           '\u0441\u043e\u043a\u0435\u0442',
           '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440']
WORDS_3 = ['class', 'function', 'method']
WORDS_4 = ['attribute', 'класс', 'функция', 'type']
WORDS_5 = ['разработка', 'администрирование', 'protocol', 'standard']
ARGS = [['ping', 'yandex.ru'], ['ping', 'youtube.com']]
WORDS_6 = ['test_file.txt']

task_1_result_0 = Homework.task_1_0(WORDS_1)
task_1_result_1 = Homework.task_1_1(WORDS_2)
task_2_result = Homework.task_2(WORDS_3)
task_3_result = Homework.task_3(WORDS_4)
task_4_result = Homework.task_4(WORDS_5)
task_5_result = Homework.task_5(ARGS)
task_6_result = Homework.task_6(WORDS_6)
