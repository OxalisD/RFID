from kivy.properties import ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.toast import toast
from kivymd.uix.button import MDRaisedButton, MDRoundFlatIconButton, MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField, MDTextFieldRect

import config
import inventoryapp
import asyncio

import scaner

GREY = [0, 0, 0, 50]
class MyCheckBox(MDCheckbox):
    numb = 0
    app = None

    def __init__(self, numb, app, **kwargs):
        super().__init__(**kwargs)
        self.numb = numb
        self.app = app

    def on_active(self, *args) -> None:
        super().on_active(*args)
        if self.active:
            print(self.numb)
            #self.app.param = self.numb
            if self.numb == 1:
                self.app.param = 1
            elif self.numb == 2:
                self.app.param = 2
            elif self.numb == 3:
                self.app.param = 3
            elif self.numb == 4:
                self.app.param = 4
            elif self.numb == 5:
                self.app.param = 5
            elif self.numb == 6:
                self.app.param = 6
            elif self.numb == 7:
                self.app.param = 7
            elif self.numb == 8:
                self.app.param = 8


class ItemCheck(BoxLayout):
    orientation = 'horizontal'

    def __init__(self, text, numb, app, active=False, **kwargs):
        super().__init__(**kwargs)
        self.label = MDLabel(text=text,
                             text_size='100dp')

        self.check_box = MyCheckBox(group='group',
                                    size_hint=(None, None),
                                    size=(25, 25),
                                    active=active,
                                    numb=numb,
                                    app=app)
        self.add_widget(self.label)
        self.add_widget(self.check_box)


class MyButton(MDFillRoundFlatIconButton):
    font_size = 20
    pos_hint = {'center_x': .5, 'center_y': .5}


class Dialog(BoxLayout):
    orientation = 'vertical'
    spacing = 20
    height = 400
    padding = [50, 50, 50, 50]

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app


class DialogScanerAndDBParams(Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.status_label = MDLabel(text='')
        self.text_field_ip = MDTextFieldRect(hint_text=str(self.app.scaner.ip),
                                             font_size=20,
                                             size_hint=(1, None),
                                             height=40)
        # Поле для указания порта. Потом добавлю
        # self.text_field_port = MDTextFieldRect(hint_text=str(self.app.scaner.port),
        #                                        font_size=20,
        #                                        size_hint=(1, None),
        #                                        height=40)

        self.button_file_test = MyButton(text='Тест соединения',
                                         icon='connection',
                                         on_release=lambda x: self.test_ip())

        self.button_file_search = MyButton(text='Поиск сканера',
                                           icon='nfc-search-variant',
                                           on_release=lambda x: asyncio.create_task(self.app.scaner.search_scaner()))
        self.add_widget(self.status_label)
        self.add_widget(self.text_field_ip)
        self.add_widget(self.button_file_test)
        self.add_widget(self.button_file_search)
        print("status scaner", self.app.scaner_status)
        self.update_data()

    def __str__(self):
        return "DialogScaner"

    def update_data(self):
        self.text_field_ip.hint_text = self.app.scaner.ip
        if self.app.scaner_status == scaner.CONNECT:
            self.status_label.text = "Соединение установлено"
        elif self.app.scaner_status == scaner.DISCONNECT:
            self.status_label.text = "Соединение разорвано"

    def test_ip(self):
        print("Пошел тест")
        test_list = self.text_field_ip.text.split(".")
        if len(test_list) != 4 or not "".join(test_list).isdigit():
            toast("Недопустимый IP")
            return False
        else:
            for i in test_list:
                i = int(i)
                if i < 0 or i > 255:
                    toast("Недопустимый IP")
                    return False
        print("Тест пройден")
        self.app.scaner.test_connect(self.text_field_ip.text)

class DialogContentUniversy(Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text_field_file_save = MDTextField(hint_text=self.app.dict_file_result,
                                           helper_text='Папка для сохранения',
                                           helper_text_mode='persistent',
                                           mode='fill')
        self.text_field_file_save.fill_color = GREY

        self.text_field_file_search = MDTextField(hint_text=self.app.dict_file_search,
                                                helper_text='Папка для поиска',
                                                helper_text_mode='persistent',
                                                mode='fill')
        self.text_field_file_search.fill_color = GREY

        self.button_file = MDRoundFlatIconButton(text='Выбрать',
                                                 icon='folder',
                                                 pos_hint={'center_x': .9, 'center_y': .9},
                                                 on_release=lambda x: self.app.file_manager_open())

        self.button_change_report = MyButton(text=self.app.report,
                                             icon='dots-vertical',
                                             on_release=lambda x: self.app.menu_reports.open())

        self.button_library = MyButton(text=self.app.item_library,
                                       icon='dots-vertical',
                                       on_release=lambda x: self.app.menu.open())

        if self.app.mode == inventoryapp.REPORT:
            self.add_widget(self.text_field_file_save)
            self.add_widget(self.button_file)
            self.add_widget(self.button_change_report)
            self.add_widget(self.button_library)

            if self.app.report == list(config.REPORTS.keys())[0]:
                self.add_date()

        elif self.app.mode == inventoryapp.INVENTORY:
            self.add_widget(self.text_field_file_search)
            self.add_widget(self.button_file)
            self.add_widget(self.button_library)
            self.add_date()
            self.app.param = 6

        elif self.app.mode == inventoryapp.STRANGERS:
            self.add_widget(self.text_field_file_save)
            self.add_widget(self.button_file)

        self.add_boxs()

    def __str__(self):
        return "DialogContentUniversy"

    def add_date(self):
        self.button_date = MyButton(text=self.app.date_inv.strftime('%d. %m. %Y'),
                                    icon='calendar-month-outline',
                                    on_release=lambda x: self.app.show_date_picker())
        self.add_widget(self.button_date)

    def del_date(self):
        if 'button_date' in list(self.__dict__.keys()):
            self.remove_widget(self.button_date)

    def add_boxs(self):
        if self.app.mode == inventoryapp.INVENTORY:
            self.checkbox_6 = ItemCheck('Онлайн - сканер', 6, app=self.app, active=True)
            self.checkbox_7 = ItemCheck('Онлайн - файл', 7, app=self.app)
            self.checkbox_8 = ItemCheck('Офлайн - сканер', 8, app=self.app)
            self.add_widget(self.checkbox_6)
            self.add_widget(self.checkbox_7)
            self.add_widget(self.checkbox_8)
        elif config.REPORTS[self.app.report] == 1:
            self.checkbox_1 = ItemCheck('все книги', 1, app=self.app, active=True)
            self.checkbox_2 = ItemCheck('только проверенные', 2, app=self.app)
            self.checkbox_3 = ItemCheck('только недостача', 3, app=self.app)
            self.add_widget(self.checkbox_1)
            self.add_widget(self.checkbox_2)
            self.add_widget(self.checkbox_3)
        elif config.REPORTS[self.app.report] == 2:
            self.checkbox_4 = ItemCheck('только книги с пустым номером', 4, app=self.app, active=True)
            self.checkbox_5 = ItemCheck('включая такие же книги с номерами', 5, app=self.app)
            self.add_widget(self.checkbox_4)
            self.add_widget(self.checkbox_5)


    def del_boxs(self):
        if config.REPORTS[self.app.report] == 2:
            self.remove_widget(self.checkbox_1)
            self.remove_widget(self.checkbox_2)
            self.remove_widget(self.checkbox_3)
        elif (config.REPORTS[self.app.report] == 1) and ('checkbox_4' in list(self.__dict__.keys())):
            self.remove_widget(self.checkbox_4)
            self.remove_widget(self.checkbox_5)



