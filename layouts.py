from kivy.properties import ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton, MDRoundFlatIconButton, MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField, MDTextFieldRect

import config
import inventoryapp
import asyncio

import scaner


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

class Dialog(BoxLayout):
    orientation = 'vertical'
    spacing = 20
    height = 400
    padding = [50, 50, 50, 50]
    fill_color = ColorProperty([0, 0, 0, 50])

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app



class DialogScanerAndDBParams(Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text_field_ip = MDTextFieldRect(hint_text=self.app.scaner.ip,
                                             font_size=20,
                                             size_hint=(1, None),
                                             height=40)
        self.text_field_ip.fill_color = self.fill_color

        self.button_file_test = MDFillRoundFlatIconButton(text='Тест',
                                                          font_size=20,
                                                          icon='dots-vertical',
                                                          pos_hint={'center_x': .5, 'center_y': .5},
                                                          on_release=lambda x: self.app.menu.open())

        self.button_file_search = MDFillRoundFlatIconButton(text='Поиск',
                                                            font_size=20,
                                                            icon='dots-vertical',
                                                            pos_hint={'center_x': .5, 'center_y': .5},
                                                            on_release=lambda x: asyncio.create_task(self.app.scaner.search_scaner()))

        self.add_widget(self.text_field_ip)
        self.add_widget(self.button_file_test)
        self.add_widget(self.button_file_search)




class DialogContentUniversy(Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text_field_file_save = MDTextField(hint_text=self.app.dict_file_result,
                                           helper_text='Папка для сохранения',
                                           helper_text_mode='persistent',
                                           mode='fill')
        self.text_field_file_save.fill_color = self.fill_color

        self.text_field_file_search = MDTextField(hint_text=self.app.dict_file_search,
                                                helper_text='Папка для поиска',
                                                helper_text_mode='persistent',
                                                mode='fill')
        self.text_field_file_search.fill_color = self.fill_color

        self.button_file = MDRoundFlatIconButton(text='Выбрать',
                                                 icon='folder',
                                                 pos_hint={'center_x': .9, 'center_y': .9},
                                                 on_release=lambda x: self.app.file_manager_open())

        self.button_change_report = MDFillRoundFlatIconButton(text=self.app.report,
                                                              font_size=20,
                                                              icon='dots-vertical',
                                                              pos_hint={'center_x': .5, 'center_y': .5},
                                                              on_release=lambda x: self.app.menu_reports.open())

        self.button_library = MDFillRoundFlatIconButton(text=self.app.item_library,
                                                        font_size=20,
                                                        icon='dots-vertical',
                                                        pos_hint={'center_x': .5, 'center_y': .5},
                                                        on_release=lambda x: self.app.menu.open())

        if self.app.mode == inventoryapp.REPORT:
            self.add_widget(self.text_field_file_save)
            self.add_widget(self.button_file)
            self.add_widget(self.button_change_report)
            self.add_widget(self.button_library)

            if self.app.report == list(config.REPORTS.keys())[0]:
                self.add_date()

            self.add_boxs()

        elif self.app.mode == inventoryapp.INVENTORY:
            self.add_widget(self.text_field_file_search)
            self.add_widget(self.button_file)
            self.add_widget(self.button_library)
            self.add_date()

        elif self.app.mode == inventoryapp.STRANGERS:
            self.add_widget(self.text_field_file_save)
            self.add_widget(self.button_file)

    def add_date(self):
        self.button_date = MDFillRoundFlatIconButton(text=self.app.date_inv.strftime('%d. %m. %Y'),
                                                     font_size=20,
                                                     icon='calendar-month-outline',
                                                     pos_hint={'center_x': .5, 'center_y': .5},
                                                     on_release=lambda x: self.app.show_date_picker())
        self.add_widget(self.button_date)

    def del_date(self):
        if 'button_date' in list(self.__dict__.keys()):
            self.remove_widget(self.button_date)

    def add_boxs(self):
        if config.REPORTS[self.app.report] == 1:
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



