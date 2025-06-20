from PyQt6.QtWidgets import QVBoxLayout, QWidget, QTabWidget, QPushButton, QLineEdit, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import QUrl, QStandardPaths
from PyQt6.QtGui import QIcon
# from apps.local.init import DraggableResizableWindow  # Импортируем базовый класс окна
from init import DraggableResizableWindow  # Импортируем базовый класс окна

class BrowserWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name=""):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name  # Сохраняем имя окна

        self.setGeometry(200, 100, 800, 600)

        self.tab_widget = QTabWidget(self)
        self.set_content(self.tab_widget)

        # Создаем профиль пользователя для хранения кеша и куков
        self.profile = QWebEngineProfile("BrowserProfile", self)
        cache_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
        self.profile.setCachePath(cache_path)
        self.profile.setPersistentStoragePath(cache_path)

        # Добавляем элементы управления в заголовок окна
        self.add_search_and_buttons_to_title_bar()

        self.add_tab("https://www.google.com")
        self.hide()

    def add_search_and_buttons_to_title_bar(self):
        """
        Добавляет поле поиска и кнопки управления в заголовок окна.
        """
        # Создаем кнопки управления
        button_style = "font-size: 18px; padding: 5px; width: 20px; height: 20px; background-color: transparent; border: none;"

        back_button = QPushButton("⬅️")
        back_button.setStyleSheet(button_style)
        forward_button = QPushButton("➡️")
        forward_button.setStyleSheet(button_style)
        reload_button = QPushButton("🔁")
        reload_button.setStyleSheet(button_style)
        new_tab_button = QPushButton("➕")
        new_tab_button.setStyleSheet(button_style)

        # Подключаем действия к кнопкам
        back_button.clicked.connect(lambda: self.tab_widget.currentWidget().back())
        forward_button.clicked.connect(lambda: self.tab_widget.currentWidget().forward())
        reload_button.clicked.connect(lambda: self.tab_widget.currentWidget().reload())
        new_tab_button.clicked.connect(lambda: self.add_tab())

        # Создаем поле ввода для URL
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter URL or search")
        self.search_input.setStyleSheet("background-color: white; color: black; padding: 5px; border-radius: 10px;")
        self.search_input.returnPressed.connect(self.load_url)

        # Добавляем кнопки и поле ввода в заголовок окна
        self.add_title_widget(back_button)
        self.add_title_widget(forward_button)
        self.add_title_widget(reload_button)
        self.add_title_widget(self.search_input)
        self.add_title_widget(new_tab_button)

    def add_tab(self, url="https://www.google.com"):
        browser = QWebEngineView()
        browser.setStyleSheet("background-color: #D1D1D1; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px;")
        
        # Используем профиль пользователя для этой вкладки
        browser.setPage(QWebEnginePage(self.profile, browser))
        
        # Разрешаем полноэкранный режим
        settings = browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        
        # Обрабатываем запрос на полноэкранный режим
        browser.page().fullScreenRequested.connect(self.handle_fullscreen_request)
        
        browser.setUrl(QUrl(url))
        self.tab_widget.addTab(browser, f"Tab {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentWidget(browser)

        # Обновление строки поиска при изменении URL текущей вкладки
        def update_search_input_on_change(url):
            self.search_input.setText(url.toString())

        # Подключение сигнала urlChanged для текущей вкладки
        def connect_url_changed():
            current_browser = self.tab_widget.currentWidget()
            if current_browser:
                current_browser.urlChanged.connect(update_search_input_on_change)

        self.tab_widget.currentChanged.connect(connect_url_changed)
        connect_url_changed()

    def handle_fullscreen_request(self, request):
        """
        Обрабатывает запрос на полноэкранный режим.
        """
        if request.toggleOn():
            # Если запрос на включение полноэкранного режима
            self.showFullScreen()
            request.accept()
        else:
            # Если запрос на выключение полноэкранного режима
            self.showNormal()
            request.accept()

    def load_url(self):
        url = self.search_input.text()
        if self.tab_widget.currentWidget():
            self.tab_widget.currentWidget().setUrl(QUrl(url))

    def switch_window(self, window_name):
        window_name = window_name.strip()

        if window_name.lower() == "desktop":  # Проверяем, является ли это рабочим столом
            for win in self.open_windows.values():
                if win:
                    win.hide()  # Скрываем все открытые окна
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
                print(f"Окно {window_name} было удалено. Создаём заново...")
                self.open_windows[window_name] = getattr(self, f"create_{window_name}_window")()
                self.open_windows[window_name].show()
        else:
            print(f"Создаём новое окно {window_name}")
            self.open_windows[window_name] = getattr(self, f"create_{window_name}_window")()
            self.open_windows[window_name].show()


# Добавляем в конец browser_window.py:
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    browser = BrowserWindow()
    browser.show()
    sys.exit(app.exec())