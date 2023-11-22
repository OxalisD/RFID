import asyncio
import socket
import json

from kivymd.toast import toast

import config

SEARCH = 'search'
CONNECT = 'connect'
DISCONNECT = 'disconnect'


class Scaner:
    UTF = 'UTF-8'
    request = b'\x05\x07\xff\xf0\x01\x00\x6a\x50'
    empty = b'\x05\x07\x01\xf0\x01\x00\x03\x89'
    find = 'E004'

    def __init__(self, app):
        self.app = app
        self.main_ip = socket.gethostbyname(socket.gethostname())
        self.ip = None
        self.port = None
        self.socket = None
        self.status = SEARCH
        self.writer = None
        self.reader = None
        self.search = False
        self.rfid_set = set()
        self.rfid_list = []

    async def get_connect(self):
        if self.app.inventory == False:
            await asyncio.sleep(1)
            sec = 3
            if self.search == False :
                print('Попытка соединения со сканером...')
                with open('params.json', 'r') as params:
                    data = json.load(params)
                    if data["ip_scaner"]:
                        print(data['ip_scaner'])
                        self.ip = data['ip_scaner']
                        self.port = data['port']
                        ans = self.connect(data["ip_scaner"], data["port"])
                        if ans == self.empty:
                            if self.app.scaner_status != CONNECT:
                                await self.connect_scaner(data["ip_scaner"], data["port"])
                                self.change_inform('check-circle-outline', 'green', data['ip_scaner'])
                                self.app.scaner_status = CONNECT
                                sec = 10

                        else:
                            if self.app.scaner_status == CONNECT:
                                toast("Сканер недоступен!")
                            self.change_inform('close-circle-outline', 'red', '')
                            self.app.scaner_status = DISCONNECT

        await asyncio.sleep(sec)
        asyncio.create_task(self.get_connect())


    async def search_scaner(self):
        print('Пошел поиск...')
        #self.change_inform('sync-circle', 'blue', 'поиск')

        list_ip = self.main_ip.split('.')
        for i in range(0, 254):
            if not self.search:
                break
            ip = '.'.join(list_ip[:3]) + '.' + str(i)
            ans = (self.connect(ip, self.port))
            if ans == self.empty:
                print('Нашелся! ', ip)

                await self.connect_scaner(ip, self.port)
                break
            await asyncio.sleep(0.1)
        return None


    def connect(self, ip, port):
        print(ip)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(config.TIMEOUT)
        try:
            self.socket.connect((ip, port))
            self.socket.send(self.request)
            ans = self.socket.recv(17)
        except TimeoutError:
            self.socket.close()
            return None
        return ans

    async def connect_scaner(self, ip, port):
        print('connect_scaner', ip)
        self.change_inform('check-circle-outline', 'green', ip)
        with open('params.json', 'r') as params:
            data = json.load(params)
        if data["ip_scaner"] != ip:
            with open('params.json', 'w') as params:
                data["ip_scaner"] = ip
                print(data)
                json.dump(data, params, indent=2)
        self.app.scaner_status = CONNECT
        print("ip: ", ip)
        try:
            self.reader, self.writer = await asyncio.open_connection(ip, port)
        except TimeoutError:
            print('TimeoutError')
            return None
        await self.send_to_scaner()
        ans = await self.get_to_scaner()
        return ans

    async def send_to_scaner(self):
        self.writer.write(self.request)
        await self.writer.drain()

    async def get_to_scaner(self):
        ans = await self.reader.read(17)
        return ans

    def change_inform(self, icon, color, data):
        self.app.screen.screens[0].ids.icon_button_scan.icon = icon
        self.app.screen.screens[0].ids.icon_button_scan.text_color = color
        self.app.screen.screens[0].ids.ip_label.text = data

        if self.app.conf_dialog:
            if self.app.conf_dialog.content_cls.__str__() == "DialogScaner":
                print("Объект ", self.app.conf_dialog.content_cls)
                self.app.conf_dialog.content_cls.update_data()

    def test_connect(self, ip):
        ans = self.connect(ip, self.port)
        if ans == self.empty:
            print(ip, " Найден!")
            toast(f"{ip} Найден!")
            asyncio.create_task(self.connect_scaner(ip, self.port))
        else:
            toast(f"{ip} Не отвечает...")

    async def work_scaner(self, param, file=None):
        i = 0
        if param == 6:
            asyncio.create_task(self.send_rfid())

        while self.app.inventory:
            await self.send_to_scaner()
            ans = await self.get_to_scaner()
            if self.empty not in ans:
                ans = reversed([f'{byte:02X}' for byte in ans])
                rfid = ''.join(ans)
                index = rfid.find(self.find)
                rfid = rfid[index:index+16]
                if len(rfid) == 16 and rfid not in self.rfid_set:
                    self.rfid_set.add(rfid)
                    self.rfid_list.append(rfid)
                    print(rfid)
                    print(len(self.rfid_set))
                    i += 1
                    continue
            else:
                i += 1
            if i > config.COUNT_EMPTY_ANSWER:
                if param == 8:
                    await self.load_to_file(file)
                await asyncio.sleep(config.DELAY_SEND_SCANER)
                i = 0

    async def send_rfid(self):
        print(self.rfid_list)
        i = 0
        while self.app.inventory or self.rfid_list:
            if not self.rfid_list or i > config.COUNT_RFID_TO_BD:
                await asyncio.sleep(config.DELAY_SEND_RFID_IN_DB)
                if i > 0:
                    self.app.root.screens[1].update_data()
                    i = 0
            else:
                self.app.data_base.inventory_update(self.rfid_list.pop(0))
                i += 1

        self.rfid_set = set()

    async def load_to_file(self, file):
        print("file", file)
        with open(file, 'a') as f:
            for rfid in self.rfid_list:
                f.write(rfid)














            
