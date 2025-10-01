from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QPushButton, QLineEdit, QHBoxLayout, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import QUrl, QStandardPaths

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

from PyQt6.QtGui import QPixmap

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent, browser_window):
        super().__init__(profile, parent)
        self.browser_window = browser_window

    # Перехватываем window.open()
    def createWindow(self, web_window_type):
        return self.browser_window.create_new_tab_from_page(web_window_type)


class YoutubemusicWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="YouTube Music", translator=None, lang_code="en"):
        super().__init__(parent)
        self.window_name = window_name
        self.lang_code = lang_code

        self.setWindowTitle(self.tr("YouTube Music"))
        self.setGeometry(300, 150, 1000, 700)

        # Создаём центральный виджет для layout
        self.container = QWidget(self)  # <- это будет "центральный" виджет
        self.set_content(self.container)  # используем метод DraggableResizableWindow
        layout = QVBoxLayout(self.container)
        self.container.setLayout(layout)

        # Настраиваем профиль
        # self.profile = QWebEngineProfile("SublimeProfile", self)
        # self.profile.setPersistentStoragePath(os.path.join(os.getcwd(), "web_profile"))
        # self.profile.setCachePath(os.path.join(os.getcwd(), "web_cache"))
        # Настраиваем профиль
        self.profile = QWebEngineProfile("SublimeProfile", self)

        # Создаем путь к папке browser внутри dataLacmi
        browser_data_path = os.path.join(os.getcwd(), "root", "dataLacmi", "browser")

        # Создаем папку, если она не существует
        os.makedirs(browser_data_path, exist_ok=True)

        self.profile.setPersistentStoragePath(os.path.join(browser_data_path, "web_profile"))
        self.profile.setCachePath(os.path.join(browser_data_path, "web_cache"))


        # Создаём браузер
        self.browser = QWebEngineView()
        self.page = CustomWebEnginePage(self.profile, self.browser, self)
        self.browser.setPage(self.page)

        # Загружаем VSCode Web
        self.browser.setUrl(QUrl("https://music.youtube.com/"))

        layout.addWidget(self.browser)


    # Метод для window.open()
    def create_new_tab_from_page(self, window_type=None):
        new_browser = QWebEngineView()
        new_page = CustomWebEnginePage(self.profile, new_browser, self)
        new_browser.setPage(new_page)
        self.central_layout.addWidget(new_browser)
        return new_page