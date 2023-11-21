from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatIconButton, MDRaisedButton, MDFloatingActionButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel

import config
import scaner
from scaner import Scaner
from report import Report
from layouts import DialogContentUniversy, DialogScanerAndDBParams
from db_lib import DBLib
import datetime
import asyncio
import os

INVENTORY = 'inventory'
REPORT = 'report'
STRANGERS = 'strangers'


class ItemInventory(BoxLayout):
    orientation = 'horizontal'

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        label = MDLabel(text=text, font_size=20, size_hint=(0.5, 1))
        self.label_digit = MDLabel(size_hint=(0.2, 1))
        self.add_widget(label)
        self.add_widget(self.label_digit)


class ButtonSaveExcel(MDFloatingActionButton):
    icon = 'file-excel'
    elevation = 5


class FirstScreen(MDScreen):
    pass


class InventoryScreen(MDScreen):
    app = None
    library = ''


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_all = ItemInventory(text=f'Всего книг в {self.library}: ')
        self.item_inv_all = ItemInventory(text='Инвентаризированно: ')
        self.item_inv_today = ItemInventory(text='Инвентаризированно сегодня: ')
        self.item_inv_not = ItemInventory(text='Осталось: ')
        self.item_inv_strangers = ItemInventory(text='Чужих книг: ')
        self.item_inv_unidentified = ItemInventory(text='Нет в базе: ')

        self.button_save_strangers = ButtonSaveExcel(on_press=lambda x: self.app.show_confirmation_dialog(STRANGERS))
        general_box = MDGridLayout(rows=2,
                                   cols=1,
                                   md_bg_color='orange')

        box_for_items = MDBoxLayout(orientation='vertical',
                                    padding=[30, 30, 30, 30],
                                    spacing=1,
                                    size_hint=(1, 0.3))
        box_for_buttons = MDBoxLayout(orientation='vertical',
                                    padding=[50, 50, 50, 50],
                                    spacing=1,
                                    size_hint=(1, 0.2))
        button_end = MDRaisedButton(text='Закончить',
                                    font_size=20,
                                    size=(50, 20),
                                    on_release=lambda x: self.exit(),
                                    pos_hint={'center_x':.5, 'center_y':.2})

        box_for_items.add_widget(self.item_all)
        box_for_items.add_widget(self.item_inv_all)
        box_for_items.add_widget(self.item_inv_today)
        box_for_items.add_widget(self.item_inv_not)
        box_for_items.add_widget(self.item_inv_strangers)
        box_for_items.add_widget(self.item_inv_unidentified)
        box_for_buttons.add_widget(button_end)
        general_box.add_widget(box_for_items)
        general_box.add_widget(box_for_buttons)
        self.add_widget(general_box)
        self.ids['item_all'] = self.item_all
        self.ids['item_inv_all'] = self.item_inv_all
        self.ids['item_inv_today'] = self.item_inv_today
        self.ids['item_inv_not'] = self.item_inv_not
        self.ids['item_inv_strangers'] = self.item_inv_strangers
        self.ids['item_inv_unidentified'] = self.item_inv_unidentified

    def exit(self):
        self.app.inventory = False
        self.app.root.current = 'first_screen'

    def update_data(self):
        self.library = self.app.item_library
        library = self.app.item_library
        date = self.app.date_inv
        print(date)
        today = datetime.date.today()

        all = self.app.data_base.get_count_book_in_filial(library=library)
        all_inv = self.app.data_base.get_count_book_in_filial(library=library, date=date)
        today_inv = self.app.data_base.get_count_book_in_filial(library=library, date=today)

        strangers = len(self.app.strangers)
        if strangers > 0:
            self.ids.item_inv_strangers.add_widget(self.button_save_strangers)

        unidentified = self.app.unidentified
        print(today_inv)
        self.ids.item_all.label_digit.text = str(all)
        self.ids.item_inv_all.label_digit.text = str(all_inv)
        self.ids.item_inv_today.label_digit.text = str(today_inv)
        self.ids.item_inv_not.label_digit.text = str(all - all_inv)
        self.ids.item_inv_strangers.label_digit.text = str(strangers)
        self.ids.item_inv_unidentified.label_digit.text = str(unidentified)


class WindowsManager(MDScreenManager):
    pass


class InventoryApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_base = DBLib(self)

        self.item_library = list(config.FILIALS.keys())[0]
        #self.date_last_inv = self.data_base.get_last_date_inv()[0]
        self.date_inv = self.data_base.get_last_date_inv()[0]
        self.report = list(config.REPORTS.keys())[0]
        self.mode = 'inventory'
        self.param = 1

        self.dict_file_result = config.DICT_FILE_RESULT
        self.dict_file_search = config.DICT_FILES
        self.dialog = None
        self.conf_dialog = None
        self.scaner = Scaner(self)
        self.scaner_status = scaner.DISCONNECT
        #self.index = '1'
        self.inventory = False
        self.strangers = []
        self.unidentified = 0
        self.screen = Builder.load_file('./inventory_new.kv')

        self.menu = MDDropdownMenu(caller=self.screen.screens[0].ids.button_inv,
                                   items=self.menu_dict('librarys'),
                                   width_mult=5)
        self.menu_reports = MDDropdownMenu(caller=self.screen.screens[0].ids.button_inv,
                                           items=self.menu_dict('reports'),
                                           width_mult=8)

        self.manager_open = False
        self.file_manager = MDFileManager(exit_manager=self.exit_manager,
                                          select_path=self.select_path,
                                          preview=True)

        InventoryScreen.app = self


    def build(self):
        asyncio.create_task(self.scaner.get_connect())
        self.theme_cls.primary_palette = 'DeepPurple'
        return self.screen

    # Выпадающие меню с выбором библиотек и отчетов
    def lib_menu_collback(self, lib):
        self.menu.dismiss()
        self.menu_reports.dismiss()
        if lib in list(config.REPORTS.keys()):
            if self.report != lib:
                self.report = lib

                if config.REPORTS[lib] == 1:
                    self.param = 1
                    self.conf_dialog.content_cls.add_date()
                    self.conf_dialog.content_cls.del_boxs()
                    self.conf_dialog.content_cls.add_boxs()
                elif config.REPORTS[lib] == 2:
                    self.param = 4
                    self.conf_dialog.content_cls.del_date()
                    self.conf_dialog.content_cls.del_boxs()
                    self.conf_dialog.content_cls.add_boxs()

                self.conf_dialog.content_cls.button_change_report.text = lib

        elif lib in list(config.FILIALS.keys()):
            if self.item_library != lib:
                self.item_library = lib
                self.conf_dialog.content_cls.button_library.text = lib

    def menu_dict(self, req):
        menu = []
        content = None
        if req == 'librarys':
            content = list(config.FILIALS.keys())
        elif req == 'reports':
            content = list(config.REPORTS.keys())
        for lib in content:
            item = {
                'text': lib,
                'viewclass': 'OneLineListItem',
                'on_release': lambda x=lib: self.lib_menu_collback(x)
            }
            menu.append(item)
        return menu

    # Диалоговое окно в свыбором даты
    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        date = value.strftime('%d. %m. %Y')
        self.date_inv = value
        self.conf_dialog.content_cls.button_date.text = str(date)

    # Файловый менеджер
    def file_manager_open(self):
        if self.mode == INVENTORY:
            self.file_manager.show(self.dict_file_search)
        else:
            self.file_manager.show(self.dict_file_result)
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        if self.mode == REPORT or self.mode == STRANGERS:
            self.dict_file_result = path
            self.conf_dialog.content_cls.text_field_file_save.hint_text = self.dict_file_result
        elif self.mode == INVENTORY:
            self.dict_file_search = path
            self.conf_dialog.content_cls.text_field_file_search.text = self.dict_file_search
        toast(path)

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def close_dialog(self, instance):
        print('Нажата кнопка: Отмена')
        self.scaner.search = False
        self.conf_dialog.dismiss()
        self.conf_dialog = None

    def ok_dialog(self):
        if self.mode == REPORT:
            if config.REPORTS[self.report] == 1:
                self.data_base.search_report(file=self.dict_file_result,
                                            library=self.item_library,
                                            date=self.date_inv)
            elif config.REPORTS[self.report] == 2:
                self.data_base.get_empty_inv()
        elif self.mode == INVENTORY:
            self.inventory = True
            self.root.current = 'inventory_screen'
            self.root.screens[1].update_data()
            self.conf_dialog.dismiss()
            self.conf_dialog = None
            asyncio.create_task(self.data_base.search_file())
        elif self.mode == STRANGERS:
            report = Report(self.dict_file_result)
            report.report_library(self.strangers)
            self.conf_dialog.dismiss()
            self.conf_dialog = None

    def show_confirmation_dialog(self, mode:str):
        """Основное диалоговое окно"""
        self.mode = mode
        title = f'Настройте параметры {"инвентаризации"if mode == INVENTORY else "отчёта"}:'
        if not self.conf_dialog:
            self.conf_dialog = MDDialog(
                title=title,
                type='custom',
                size_hint_x=0.8,
                content_cls=DialogContentUniversy(app=self),
                buttons=[MDRectangleFlatIconButton(text='Отмена',
                                                   text_color=self.theme_cls.primary_color,
                                                   icon='cancel',
                                                   on_release=self.close_dialog),
                         MDRectangleFlatIconButton(text='Старт',
                                                   text_color=self.theme_cls.primary_color,
                                                   icon='download',
                                                   on_release=lambda x: self.ok_dialog())])
        self.conf_dialog.open()

    def show_params_dialog(self, mode: str):
        """Диалоговое окно настроек сканера"""
        self.mode = mode
        title = f'Настройте параметры сканера:'
        if not self.conf_dialog:
            self.conf_dialog = MDDialog(
                title=title,
                type='custom',
                size_hint_x=0.8,
                content_cls=DialogScanerAndDBParams(app=self),
                buttons=[MDRectangleFlatIconButton(text='Отмена',
                                                   text_color=self.theme_cls.primary_color,
                                                   icon='cancel',
                                                   on_release=self.close_dialog),
                         MDRectangleFlatIconButton(text='Принять',
                                                   text_color=self.theme_cls.primary_color,
                                                   icon='check-circle-outline',
                                                   on_release=lambda x: self.scaner.test_connect(
                                                       self.conf_dialog.content_cls.text_field_ip.text))])
        self.conf_dialog.open()



    # def filling_inv_screen(self):
    #     item_inv_all = ItemInventory(text='Инвентаризированно: ')
    #     self.root.screens[1].ids.widget.add_widget(item_inv_all)