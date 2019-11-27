"""Декоратор для функций приложений server и client"""


import logging
import argparse
import traceback
import re

# Определение исполняемой програмы
PARSER = argparse.ArgumentParser()
PROGRAM = PARSER.prog.split('.')[0].lower()

# Определение регистратора
if PROGRAM == 'server':
    LOGGER = logging.getLogger('log_server')
elif PROGRAM == 'client':
    LOGGER = logging.getLogger('log_client')
else:
    raise ValueError

def log(func):
    """Функция-обертка для логирования функций"""
    def wrapper(*args):
        result = func(*args)
        # Определяем выполняемый стэк
        module_stack = traceback.format_stack()
        # Очищаем строку от специальных символов
        current_module = re.sub(r'[ |\n]', r'', module_stack[0])
        # Извлекаем название родительской функции
        parent_function = current_module.partition('<module>')[2]
        # Формируем набор логов
        LOGGER.info(f"Вызов декоратора {log.__name__.upper()}.")
        LOGGER.debug(f"Вызов функции {func.__name__.upper()}.")
        LOGGER.debug(f"Параметры функции: {args}.")
        LOGGER.debug(f"Вызов из модуля {func.__module__.upper()}.")
        LOGGER.debug(f"Функция {func.__name__.upper()} вызвана из " \
                     f"функции {parent_function.upper()}.")
        return result
    return wrapper
