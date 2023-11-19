import asyncio
import socket
import json

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
        self.socket = None
        self.status = SEARCH
        self.writer = None
        self.reader = None

    async def get_connect(self):
        print('Попытка соединения со сканером...')
        with open('params.json', 'r') as params:
            data = json.load(params)
            if data["ip_scaner"]:
                print(data['ip_scaner'])
                ans = await self.connect(data["ip_scaner"], data["port"])
                if ans == self.empty:
                    await self.connect_scaner(data["ip_scaner"], data["port"])
                    self.change_inform('check-circle-outline', 'green', data['ip_scaner'])
                    return CONNECT

        ip = await self.search_scaner(data["port"])
        if ip:
            print("Опа!")
            await self.connect_scaner(ip, data["port"])
            with open('params.json', 'w') as params:
                data["ip_scaner"] = ip
                print(data)
                json.dump(data, params, indent=2)
            return CONNECT
        self.change_inform('close-circle-outline', 'red', 'не найден')
        return DISCONNECT


    async def search_scaner(self, port):
        print('Пошел поиск...')
        self.change_inform('sync-circle', 'blue', 'поиск')

        list_ip = self.main_ip.split('.')
        for i in range(0, 254):
            ip = '.'.join(list_ip[:3]) + '.' + str(i)
            ans = await (self.connect(ip, port))
            if ans == self.empty:
                print('Нашелся! ', ip)

                self.change_inform('check-circle-outline', 'green', ip)
                return ip
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









            
