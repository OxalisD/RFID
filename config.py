import datetime

CONNECT = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=sql;DATABASE=inv;UID=service;PWD=Vinnipuh1;Encrypt=no'

DICT_FILES = r'C:\Users\Kislitsa\PycharmProjects\RFID\files'
DICT_FILE_RESULT = r'C:\Users\Kislitsa\PycharmProjects\RFID\result'
FILIALS = {'ЦБС': None, 'Публичная Библиотека': 'ПБ', 'Талнахская Городская Библиотека': 'ТГБ', 'Библиотека 1': 'Ф1', 'Библиотека 2': 'Ф2', 'Библиотека 3': 'Ф3', 'Библиотека 4': 'Ф4',
           'Библиотека 6': 'Ф6', 'Библиотека 8': 'Ф8', 'Библиотека 10': 'Ф10'}
#DATE_BEGIN = '2023-10-14'
REPORTS = {'Отчет по инвентаризации': 1, 'Пустые инвентарные номера': 2}
PARAMETERS = ['все', 'отмеченые', 'недостача', 'пустой_номер', 'пустой_и_аналоги']
params = {
  "ip_scaner": "10.1.0.50",
  "port": 4800
}
#Задержка после 10 пустых ответов от сканера
DELAY_SEND_SCANER = 0.3
DELAY_SEND_RFID_IN_DB = 0.1