import datetime
import os

CONNECT = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=sql;DATABASE=inv;UID=service;PWD=Vinnipuh1;Encrypt=no'

DICT_FILES = os.path.join(os.getcwd(), 'files')
DICT_FILE_RESULT = os.path.join(os.getcwd(), 'result')
if not os.access(DICT_FILE_RESULT, os.F_OK):
    os.mkdir(DICT_FILE_RESULT)
if not os.access(DICT_FILES, os.F_OK):
    os.mkdir(DICT_FILES)
FILIALS = {'ЦБС': None, 'Публичная Библиотека': 'ПБ', 'Талнахская Городская Библиотека': 'ТГБ', 'Библиотека 1': 'Ф1', 'Библиотека 2': 'Ф2', 'Библиотека 3': 'Ф3', 'Библиотека 4': 'Ф4',
           'Библиотека 6': 'Ф6', 'Библиотека 8': 'Ф8', 'Библиотека 10': 'Ф10'}
#DATE_BEGIN = '2023-10-14'
REPORTS = {'Отчет по инвентаризации': 1, 'Пустые инвентарные номера': 2}
PARAMETERS = ['все', 'отмеченые', 'недостача', 'пустой_номер', 'пустой_и_аналоги']


TIMEOUT = 0.4
# Количество пустых ответов до переключения на отправку меток в БД
COUNT_EMPTY_ANSWER = 10
# Количество меток до переключения на сканер
COUNT_RFID_TO_BD = 10
# Задержка после N пустых ответов от сканера
DELAY_SEND_SCANER = 0
# Задержка после N отправленных меток в БД
DELAY_SEND_RFID_IN_DB = 0