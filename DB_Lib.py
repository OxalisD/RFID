from kivymd.toast import toast
import config
import pyodbc
import requests as r
from pprint import pprint
from Report import Report
import asyncio
import os


class DBLib:
    CONNECT = config.CONNECT

    def __init__(self, app):
        self.conn = pyodbc.connect(self.CONNECT)
        self.cursor = self.conn.cursor()
        self.app = app

    @staticmethod
    def conn_manager(func):
        def decor(self, *args, **kwargs):
            with self.conn:
                result = func(self, *args, **kwargs)
                return result
        return decor

    def inventory_update(self, rfid):
        try:
            self.cursor.execute(r.upload_dateinv_by_rfid(rfid))
            self.cursor.execute(r.request_book_by_t090f(rfid=rfid))
            book = self.cursor.fetchone()
            if not book:
                print('Не идентифицирован')
                self.app.unidentified += 1
            elif config.FILIALS[self.app.item_library] and book[5][:2] != config.FILIALS[self.app.item_library]:
                print(book[5], ' != ', config.FILIALS[self.app.item_library])
                self.app.strangers.append(book)
                print('Чужая книга: ', book)
        except TypeError:
            print('Что-то пошло не так.')

    #Количество книг
    @conn_manager
    def get_count_book_in_filial(self, library=None, date=None):
        self.cursor.execute(r.request_count_book(library, date))
        print(r.request_count_book(library, date))
        return self.cursor.fetchone()[0]

    #Отчет по инвентаризации
    @conn_manager
    def search_report(self, file, library=None, date=None, ):
        toast('Запрос к БД')
        print(r.request_book_by_t090f(library, date))
        if self.app.param == 1:
            self.cursor.execute(r.request_book_by_t090f(library))
        elif self.app.param == 2:
            self.cursor.execute(r.request_book_by_t090f(library, date))
        elif self.app.param == 3:
            self.cursor.execute(r.request_book_by_t090f(library, date, over=False))
        report = self.cursor.fetchall()
        file = Report(file, self.app.report, self.app.item_library, self.app.param, self.app.date_inv)
        file.report_library(report)

    #Поиск пустых инвентарных номеров
    @conn_manager
    def get_empty_inv(self):
        toast('Запрос к БД')
        self.cursor.execute(r.request_empty_inv(self.app.item_library))
        empty_list = self.cursor.fetchall()
        row_list = []
        for book in empty_list:
            book = list(book)
            id = book.pop(0)
            print(id, self.app.param)
            self.cursor.execute(r.request_count_empty_inv(id))
            if self.cursor.fetchone()[0] > 0:
                if self.app.param == 5:
                    self.cursor.execute(r.request_all_empty_inv(id))
                    for row in self.cursor.fetchall():
                        row_list.append(row)
                elif self.app.param == 4:
                    print(book)
                    row_list.append(book)
        file = Report(self.app.dict_file_result, self.app.report, self.app.item_library, self.app.param)
        file.report_library(row_list)


    @conn_manager
    def get_last_date_inv(self):
        self.cursor.execute(r.request_last_date_inv())
        last_date = self.cursor.fetchone()
        return last_date

    async def search_file(self):
        while self.app.inventory:
            dir = os.listdir(self.app.dict_file_search)
            if dir:
                with self.conn:
                    for obj in dir:
                        with open(self.app.dict_file_search + '/' + obj, 'r') as file:
                            toast('Обработка файла')
                            i = 0
                            for row in file:
                                i += 1
                                self.inventory_update(row[:-1])
                        toast(f'Обработано {i} книг')
                        os.remove(self.app.dict_file_search + '/' + obj)
                        self.app.root.screens[1].update_data()
            await asyncio.sleep(1)









