"""Логирование приложения server"""

import logging.handlers
import os
import sys
sys.path.append('../')

"""Определение директории файла"""
LOG_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = str(os.path.join(LOG_PATH, 'server_log.log')).replace('\\','/')

"""Создание логгера"""
LOGGER = logging.getLogger('log_server')


"""Создание объектов логирования"""
LOG_STREAM = logging.StreamHandler(sys.stderr)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(LOG_PATH, interval=1, encoding='utf8', when='D')

"""Выбор уровня логирования"""
LOG_STREAM.setLevel(logging.DEBUG)
LOG_FILE.setLevel(logging.DEBUG)

"""Создание форматирования для логирования"""
LOG_FORMATTER = logging.Formatter('%(asctime)-22s : %(levelname)-8s : %(filename)-5s : %(message)s')

"""Назначения форматирования для логирования"""
LOG_STREAM.setFormatter(LOG_FORMATTER)
LOG_FILE.setFormatter(LOG_FORMATTER)

"""Добавление файла лога к хэндлеру"""
LOGGER.addHandler(LOG_STREAM)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(logging.DEBUG)