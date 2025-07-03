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
        # profile: QWebEngineProfile, parent: QWebEngineView
        super().__init__(profile, parent)
        self.browser_window = browser_window

    # Переопределяем метод: все window.open() будут сюда
    def createWindow(self, web_window_type):
        return self.browser_window.create_new_tab_from_page(web_window_type)


class BrowserWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="", translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.parent_window = parent
        self.window_name = window_name
        self.pinned_tabs_urls = []
        self.lang_code = lang_code  # Сохраняем переданный язык


        self.setGeometry(200, 100, 800, 600)
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #202124;
            }

            QTabBar {
                background: #202124;
            }

            QTabBar::tab {
                background: #2b2b2b;
                color: #cccccc;
                padding: 6px 16px;
                margin: 0px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }

            QTabBar::tab:selected {
                background: #3c3c3c;
                color: white;
            }

            QTabBar::close-button {
                image: url(icons/close-light.png);
                subcontrol-position: right;
                margin-left: 8px;
                width: 30px;
                height: 30px;
            }

            QTabBar::close-button:hover {
                image: url(icons/close-light-hover.png);
            }
            """)
        self.set_content(self.tab_widget)

        # Включаем перетаскивание и крестик на вкладках
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Профиль для кеша/куков
        self.profile = QWebEngineProfile("BrowserProfile", self)
        cache_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
        self.profile.setCachePath(cache_path)
        self.profile.setPersistentStoragePath(cache_path)

        self.tab_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)

        self.pinned_tabs = set()  # Хранит закреплённые вкладки по индексу


        # Общие стили (тёмная тема, закруглённые вкладки...)
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #202124;
            }

            QTabBar {
                background: #202124;
            }

            QTabBar::tab {
                background: #2b2b2b;
                color: #cccccc;
                padding: 6px 16px;
                margin: 0px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }

            QTabBar::tab:selected {
                background: #3c3c3c;
                color: white;
            }

            QTabBar::close-button {
                image: url(icons/close-light.png);
                subcontrol-position: right;
                margin-left: 8px;
                width: 30px;
                height: 30px;
            }

            QTabBar::close-button:hover {
                image: url(icons/close-light-hover.png);
            }


            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                padding: 6px;
                border-radius: 10px;
                border: 1px solid #444;
            }

            QPushButton {
                font-size: 18px;
                background-color: transparent;
                border: none;
                width: 20px;
                height: 20px;
            }
        """)


        self.add_search_and_buttons_to_title_bar()

        self.lang_code = getattr(self.parent_window, "current_language", "en")
        self.add_tab(f"https://www.google.com/?hl={self.lang_code}")

        self.restore_pinned_tabs()


        self.hide()

    def restore_pinned_tabs(self):
        for url in self.pinned_tabs_urls:
            self.add_tab(url)
            index = self.tab_widget.currentIndex()
            title = self.tab_widget.tabText(index)
            self.tab_widget.setTabText(index, "📌 " + title)


    def show_tab_context_menu(self, position: QPoint):
        index = self.tab_widget.tabBar().tabAt(position)
        if index == -1:
            return

        menu = Menu(self)

        # Перезапустить
        restart_action = QAction(self.tr("🔁 Restart"), self)
        restart_action.triggered.connect(lambda: self.restart_tab(index))
        menu.addAction(restart_action)

        # Дублировать
        duplicate_action = QAction(self.tr("📄 Duplicate"), self)
        duplicate_action.triggered.connect(lambda: self.duplicate_tab(index))
        menu.addAction(duplicate_action)

        # Закрепить/Открепить
        if index in self.pinned_tabs:
            pin_text = "📌 Unpin"
        else:
            pin_text = "📌 Pin"
        pin_action = QAction(self.tr(pin_text), self)
        pin_action.triggered.connect(lambda: self.toggle_pin_tab(index))
        menu.addAction(pin_action)

        # Закрыть (с Ctrl+W)
        close_action = QAction(self.tr("❌ Close (Ctrl+W)"), self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(lambda: self.close_tab(index))
        menu.addAction(close_action)

        menu.exec(self.tab_widget.tabBar().mapToGlobal(position))

    def restart_tab(self, index):
        widget = self.tab_widget.widget(index)
        if isinstance(widget, QWebEngineView):
            widget.reload()

    def duplicate_tab(self, index):
        widget = self.tab_widget.widget(index)
        if isinstance(widget, QWebEngineView):
            url = widget.url().toString()
            self.add_tab(url)

    def toggle_pin_tab(self, index):
        tabbar = self.tab_widget.tabBar()
        browser = self.tab_widget.widget(index)
        if not isinstance(browser, QWebEngineView):
            return

        url = browser.url().toString()
        title = tabbar.tabText(index).replace("📌 ", "")

        if url in self.pinned_tabs_urls:
            self.pinned_tabs_urls.remove(url)
            tabbar.setTabText(index, title)
        else:
            self.pinned_tabs_urls.append(url)
            tabbar.setTabText(index, "📌 " + title)



    def add_search_and_buttons_to_title_bar(self):
        back_button = QPushButton("⬅️")
        forward_button = QPushButton("➡️")
        reload_button = QPushButton("🔁")
        new_tab_button = QPushButton("➕")

        back_button.clicked.connect(lambda: self.tab_widget.currentWidget().back())
        forward_button.clicked.connect(lambda: self.tab_widget.currentWidget().forward())
        reload_button.clicked.connect(lambda: self.tab_widget.currentWidget().reload())
        new_tab_button.clicked.connect(self.add_tab)

        # В методе add_search_and_buttons_to_title_bar():
        button_style = """
            QPushButton {
                font-size: 18px;
                background-color: transparent;
                border: none;
                width: 20px;
                height: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """

        back_button.setStyleSheet(button_style)
        forward_button.setStyleSheet(button_style)
        reload_button.setStyleSheet(button_style)
        new_tab_button.setStyleSheet(button_style)

        self.search_input = Input()
        self.search_input.setPlaceholderText(self.tr("Enter URL or search"))
        self.search_input.returnPressed.connect(self.load_url)

        # lock_label = QLabel()
        # lock_icon = QPixmap("icons/lock.png")
        # if not lock_icon.isNull():
        #     lock_label.setPixmap(lock_icon.scaled(16, 16))

        url_layout = QHBoxLayout()
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(5)
        # url_layout.addWidget(lock_label)
        url_layout.addWidget(self.search_input)

        url_widget = QWidget()
        url_widget.setLayout(url_layout)

        self.add_title_widget(back_button)
        self.add_title_widget(forward_button)
        self.add_title_widget(reload_button) 
        self.add_title_widget(url_widget)    
        self.add_title_widget(new_tab_button)

    def add_tab(self, url="https://www.google.com"):
        if not isinstance(url, str):
            url = f"https://www.google.com/?hl={self.lang_code}"

        browser = QWebEngineView()
        browser.setStyleSheet("background-color: #D1D1D1; ")
        browser.loadFinished.connect(lambda ok: self.update_tab_title(browser))


        # Используем наш CustomWebEnginePage
        page = CustomWebEnginePage(self.profile, browser, self)
        browser.setPage(page)

        # Fullscreen
        browser.page().fullScreenRequested.connect(self.handle_fullscreen_request)

        browser.setUrl(QUrl(url))

        index = self.tab_widget.addTab(browser, self.tr("New Tab"))
        self.tab_widget.setCurrentIndex(index)

        # URL и favicon
        browser.urlChanged.connect(lambda u: self.search_input.setText(u.toString()))
        browser.iconChanged.connect(lambda icon: self.tab_widget.setTabIcon(index, icon))

    def update_tab_title(self, browser):
        index = self.tab_widget.indexOf(browser)
        if index != -1:
            self.tab_widget.setTabText(index, browser.title())


    def create_new_tab_from_page(self, window_type=None):
        """
        Вызывается из CustomWebEnginePage.createWindow(),
        когда сайт делает window.open()
        """
        # Создаём новую вкладку почти так же, как в add_tab, но без initial URL
        new_browser = QWebEngineView()
        new_browser.setStyleSheet("background-color: #121212;")

        page = CustomWebEnginePage(self.profile, new_browser, self)
        new_browser.setPage(page)
        new_browser.page().fullScreenRequested.connect(self.handle_fullscreen_request)

        index = self.tab_widget.addTab(new_browser, self.tr("New Tab"))
        self.tab_widget.setCurrentIndex(index)

        new_browser.urlChanged.connect(lambda u: self.search_input.setText(u.toString()))
        new_browser.iconChanged.connect(lambda icon: self.tab_widget.setTabIcon(index, icon))

        return page  # Метод должен вернуть QWebEnginePage

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            widget.deleteLater()
        self.tab_widget.removeTab(index)

    def handle_fullscreen_request(self, request):
        if request.toggleOn():
            self.showFullScreen()
        else:
            self.showNormal()
        request.accept()

    def load_url(self):
        url = self.search_input.text().strip()
        if not url.startswith("http"):
            url = "https://" + url
        if self.tab_widget.currentWidget():
            self.tab_widget.currentWidget().setUrl(QUrl(url))

    def switch_window(self, window_name):
        window_name = window_name.strip()
        if window_name.lower() == "desktop":
            for win in self.open_windows.values():
                if win:
                    win.hide()
            self.active_window_name = "desktop"
            return

        window = self.open_windows.get(window_name)
        self.active_windows[window_name] = True
        self.update_dock_indicators()
        self.active_window_name = window_name

        if window is not None:
            try:
                if window.isHidden() or window.minimized:
                    window.show()
                    window.minimized = False
                    window.raise_()
                    window.activateWindow()
                else:
                    window.close_window()
                    self.open_windows[window_name] = None
            except RuntimeError:
                self.open_windows[window_name] = getattr(self, f"create_{window_name}_window")()
                self.open_windows[window_name].show()
        else:
            self.open_windows[window_name] = getattr(self, f"create_{window_name}_window")()
            self.open_windows[window_name].show()
