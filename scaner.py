import asyncio
import socket
import json

from kivymd.toast import toast

SEARCH = 'search'
CONNECT = 'connect'
DISCONNECT = 'disconnect'


class Scaner:
    UTF = 'UTF-8'
    request = b'\x05\x07\xff\xf0\x01\x00\x6a\x50'
    empty = b'\x05\x07\x01\xf0\x01\x00\x03\x89'

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

    async def get_connect(self):
        if self.search == False:
            print('Попытка соединения со сканером...')
            with open('params.json', 'r') as params:
                data = json.load(params)
                if data["ip_scaner"]:
                    print(data['ip_scaner'])
                    self.ip = data['ip_scaner']
                    self.port = data['port']
                    ans = await self.connect(data["ip_scaner"], data["port"])
                    if ans == self.empty:
                        await self.connect_scaner(data["ip_scaner"], data["port"])
                        self.change_inform('check-circle-outline', 'green', data['ip_scaner'])
                        self.app.scaner_status = CONNECT
                        return CONNECT

        self.change_inform('close-circle-outline', 'red', '')
        await asyncio.sleep(10)
        print("Добавление задачи")
        asyncio.create_task(self.get_connect())
        self.app.scaner_status = DISCONNECT
        return DISCONNECT


    async def search_scaner(self):
        print('Пошел поиск...')
        #self.change_inform('sync-circle', 'blue', 'поиск')
        self.search = True

        list_ip = self.main_ip.split('.')
        for i in range(200, 254):
            if not self.search:
                break
            ip = '.'.join(list_ip[:3]) + '.' + str(i)
            ans = await (self.connect(ip, self.port))
            if ans == self.empty:
                print('Нашелся! ', ip)

                await self.connect_scaner(ip, self.port)
                break
            await asyncio.sleep(0.1)
        return None



    async def connect(self, ip, port):
        print(ip)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0.2)
        try:
            self.socket.connect((ip, port))
            self.socket.send(self.request)
            ans = self.socket.recv(17)
        except TimeoutError:
            self.socket.close()
            return None
        return ans

    async def connect_scaner(self, ip, port):
        self.change_inform('check-circle-outline', 'green', ip)
        with open('params.json', 'r') as params:
            data = json.load(params)
        if data["ip_scaner"] != ip:
            with open('params.json', 'w') as params:
                data["ip_scaner"] = ip
                print(data)
                json.dump(data, params, indent=2)
        self.app.scaner_status = CONNECT
        print(ip)
        try:
            self.reader, self.writer = await asyncio.open_connection(ip, port)
        except TimeoutError:
            print('TimeoutError')
            return None
        await self.send_to_scaner()
        ans = await self.get_to_scaner()
        return ans

    async def send_to_scaner(self):
        print('send')
        self.writer.write(self.request)
        await self.writer.drain()

    async def get_to_scaner(self):
        ans = await self.reader.read(17)
        return ans

    def change_inform(self, icon, color, data):
        self.app.screen.screens[0].ids.icon_button_scan.icon = icon
        self.app.screen.screens[0].ids.icon_button_scan.text_color = color
        self.app.screen.screens[0].ids.ip_label.text = data
        print(self.app.conf_dialog)
        if self.app.conf_dialog.content_cls.update_data:
            self.app.conf_dialog.content_cls.update_data()



    def test_connect(self, ip):
        ans = self.connect(ip, self.port)
        if ans == self.empty:
            self.connect_scaner(ip, self.port)
        else:
            toast(ip, " Не отвечает")












            
