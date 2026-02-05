from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QPushButton, QLineEdit, QHBoxLayout, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import QUrl, QStandardPaths
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

from PyQt6.QtGui import QPixmap

import tempfile
import shutil

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

BROWSER_DIR = os.path.dirname(os.path.abspath(__file__))
# print(BROWSER_DIR)

from PyQt6.QtWidgets import QMenu, QStyle, QProxyStyle
from PyQt6.QtGui import QContextMenuEvent
from PyQt6.QtCore import Qt

class CustomMenuStyle(QProxyStyle):
    def drawControl(self, element, option, painter, widget=None):
        if element == QStyle.ControlElement.CE_MenuItem:
            option.palette.setColor(option.palette.ColorRole.Text, Qt.GlobalColor.white)
        super().drawControl(element, option, painter, widget)

class StyledWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Включаем стандартное контекстное меню Chromium
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)

    def contextMenuEvent(self, event: QContextMenuEvent):
        # ✅ Правильный способ в PyQt6
        menu = self.createStandardContextMenu()

        # === Кастомный стиль ===
        menu.setStyle(CustomMenuStyle())
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                color: #f0f0f0;
                padding: 8px 18px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #3d6ddf;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #555;
                margin: 4px 8px;
            }
        """)

        menu.exec(event.globalPos())
        menu.deleteLater()



class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent, browser_window):
        # profile: QWebEngineProfile, parent: QWebEngineView
        super().__init__(profile, parent)
        self.browser_window = browser_window

    # Переопределяем метод: все window.open() будут сюда
    def createWindow(self, web_window_type):
        return self.browser_window.create_new_tab_from_page(web_window_type)
    
    def javaScriptConfirm(self, securityOrigin, msg: str) -> bool:
        # ✅ авто-нажатие OK для "leave this page"
        low = (msg or "").lower()
        if "leave this page" in low or "changes that you made may not be saved" in low:
            return True
        return super().javaScriptConfirm(securityOrigin, msg)

    def chooseFiles(self, mode, old_files, accepted_mime_types):
        try:
            parent_widget = self.parent()

            if mode == QWebEnginePage.FileSelectionMode.FileSelectOpen:
                file_path, _ = CustomFileDialog.getOpenFileName(
                    parent_widget,
                    "Select File",
                    "root/user",
                    "All Files (*);;Images (*.png *.jpg *.jpeg *.bmp *.webp)"
                )
                if not file_path:
                    return []

                # --- Копіюємо у системну тимчасову теку ---
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, os.path.basename(file_path))
                shutil.copy2(file_path, temp_path)
                print(f"[BROWSER] Копіюємо {file_path} → {temp_path}")
                return [temp_path]

            elif mode == QWebEnginePage.FileSelectionMode.FileSelectOpenMultiple:
                files, _ = CustomFileDialog.getOpenFileNames(
                    parent_widget,
                    "Select Files",
                    "root/user",
                    "All Files (*);;Images (*.png *.jpg *.jpeg *.bmp *.webp)"
                )
                temp_files = []
                for f in files:
                    temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(f))
                    shutil.copy2(f, temp_path)
                    temp_files.append(temp_path)
                return temp_files

            elif mode == QWebEnginePage.FileSelectionMode.FileSelectSave:
                file_path, _ = CustomFileDialog.getSaveFileName(
                    parent_widget,
                    "Save File As",
                    "root/user",
                    "All Files (*)"
                )
                if not file_path:
                    return []

                temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(file_path))
                return [temp_path]

        except Exception as e:
            print(f"[BROWSER] Помилка у CustomFileDialog: {e}")
            return []

        return []

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

USER_CONFIG_PATH = os.path.join(BASE_DIR, 'root', 'bin', 'user.config')


def get_current_username():
    """
    Читает user.config, выводит имя пользователя в системную консоль и возвращает его.
    """
    username = "Unknown User"
    
    try:
        # Проверяем существование файла
        if not os.path.exists(USER_CONFIG_PATH):
            error_msg = f"[ERROR] user.config not found. Expected path: {USER_CONFIG_PATH}"
            print(error_msg)
            return "Error: File not found"
            
        with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # Извлекаем имя пользователя
            username = config_data.get("user_name", "Unknown User (key missing)")
            
    except json.JSONDecodeError:
        error_msg = "[ERROR] Invalid JSON format in user.config."
        print(error_msg)
        username = "Error: Invalid JSON"
    except Exception as e:
        error_msg = f"[ERROR] Error reading user data: {e}"
        print(error_msg)
        username = "Error: General Exception"

    # 🟢 Вывод имени пользователя прямо в системную консоль (CMD)
    print(f"[INFO] Current User Name: {username}")
    
    return username
# get_current_username()

class BrowserWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="", translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.parent_window = parent
        self.window_name = window_name
        self.pinned_tabs_urls = []
        # self.lang_code = lang_code  # Сохраняем переданный язык

        self.lang_code = lang_code
        self.download_path = os.path.join("root", "user", "download")
        os.makedirs(self.download_path, exist_ok=True)

        # Папка для настроек
        self.username = get_current_username()
        self.settings_dir = os.path.join("root", f"{self.username}", "browser", "config")
        os.makedirs(self.settings_dir, exist_ok=True)

        # Файл с настройками
        self.settings_file = os.path.join(self.settings_dir, "settings.json")

        # Создаем дефолтный файл, если его нет
        if not os.path.exists(self.settings_file) or os.path.getsize(self.settings_file) == 0:
            default_settings = {
                "lang_code": self.lang_code,
                "download_path": self.download_path
            }
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(default_settings, f, indent=2, ensure_ascii=False)

        # Загружаем настройки из файла, если он существует
        if os.path.exists(self.settings_file) and os.path.getsize(self.settings_file) > 0:
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    settings_data = json.load(f)
                self.lang_code = settings_data.get("lang_code", self.lang_code)
                self.download_path = settings_data.get("download_path", self.download_path)
            except Exception as e:
                print(f"[SETTINGS] Ошибка чтения файла настроек: {e}")




        self.setGeometry(200, 100, 800, 600)
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #3a3a3a;
            }

            QTabBar {
                background: #3a3a3a;
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
                image: url(apps/local/browser/icons/close-light.png);
                subcontrol-position: right;
                width: 20px;
                height: 20px;
            }

            QTabBar::close-button:hover {
                image: url(apps/local/browser/icons/close-light-hover.png);
            }
            """)
        self.set_content(self.tab_widget)

        # Включаем перетаскивание и крестик на вкладках
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Профиль для кеша/куков
        # self.profile = QWebEngineProfile("BrowserProfile", self)
        # cache_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
        # self.profile.setCachePath(cache_path)
        # self.profile.setPersistentStoragePath(cache_path)
        # Профиль для кеша/куков
        # self.profile = QWebEngineProfile("BrowserProfile", self)
        # cache_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
        # self.profile.setCachePath(cache_path)
        # self.profile.setPersistentStoragePath(cache_path)
        self.profile = get_shared_profile(self)

        # === Автоскачивание файлов ===
        self.download_path = os.path.join("root", "user", "download")
        os.makedirs(self.download_path, exist_ok=True)
        self.profile.downloadRequested.connect(self.handle_download)


        self.tab_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)

        self.pinned_tabs = set()  # Хранит закреплённые вкладки по индексу


        # Общие стили (тёмная тема, закруглённые вкладки...)
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #3a3a3a;
            }

            QTabBar {
                background: #3a3a3a;
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

        # === Сесії браузера ===

        self.session_file = os.path.join("root", f"{self.username}", "browser", "config", "browser.json")
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        # Додати після оголошення self.session_file
        if not os.path.exists(self.session_file) or os.path.getsize(self.session_file) == 0:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            # створюємо дефолтну порожню сесію
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump({"tabs": [], "active_index": 0}, f)


        # Відновлюємо сесію перед створенням fallback-вкладки
        self.restore_session()
        if self.tab_widget.count() == 0:
            self.add_tab(f"https://www.google.com/?hl={self.lang_code}")

        self.hide()

    # --- CLOSE EVENT ---
    def closeEvent(self, event):
        try:
            for i in reversed(range(self.tab_widget.count())):
                w = self.tab_widget.widget(i)
                if w:
                    w.deleteLater()
            self.tab_widget.clear()
        except Exception as e:
            print("[CLOSE] cleanup error:", e)

        self.save_session()
        super().closeEvent(event)


    # --- SAVE SESSION ---
    def save_session(self):
        tabs_data = []
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, QWebEngineView):
                url = widget.url().toString()
                pinned = url in self.pinned_tabs_urls
                tabs_data.append({"url": url, "pinned": pinned})

        session = {
            "tabs": tabs_data,
            "active_index": self.tab_widget.currentIndex()
        }

        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
            print("[SESSION] Сесія збережена")
        except Exception as e:
            print("[SESSION] Помилка збереження:", e)

    # --- RESTORE SESSION ---
    def restore_session(self):
        if not os.path.exists(self.session_file):
            return

        # Перевіряємо, що файл не порожній
        if os.path.getsize(self.session_file) == 0:
            print("[SESSION] Файл порожній, пропускаємо відновлення")
            return

        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                session = json.load(f)

            self.tab_widget.clear()
            self.pinned_tabs_urls.clear()

            for tab in session.get("tabs", []):
                url = tab.get("url", "https://www.google.com")
                self.add_tab(url)
                index = self.tab_widget.currentIndex()
                if tab.get("pinned"):
                    self.pinned_tabs_urls.append(url)
                    title = self.tab_widget.tabText(index)
                    self.tab_widget.setTabText(index, "📌 " + title)

            active = session.get("active_index", 0)
            if 0 <= active < self.tab_widget.count():
                self.tab_widget.setCurrentIndex(active)

            print("[SESSION] Сесія відновлена")

        except json.JSONDecodeError:
            print("[SESSION] Некоректний JSON, пропускаємо відновлення")
        except Exception as e:
            print("[SESSION] Помилка відновлення:", e)



    def handle_download(self, download: QWebEngineDownloadRequest):
        """Автоматически сохраняем все загрузки в root/user/download"""
        target_path = os.path.join(self.download_path, download.downloadFileName())
        download.setDownloadDirectory(self.download_path)
        download.setDownloadFileName(download.downloadFileName())
        download.accept()

        print(f"[DOWNLOAD] Файл будет сохранён: {target_path}")

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

        menu = CustomContextMenu(self)

        # Перезапустить
        restart_action = QAction(self.tr("🔁 Restart"), self)
        restart_action.triggered.connect(lambda: self.restart_tab(index))
        menu.addAction(restart_action)

        # Дублировать
        duplicate_action = QAction(self.tr("📄 Duplicate"), self)
        duplicate_action.triggered.connect(lambda: self.duplicate_tab(index))
        menu.addAction(duplicate_action)

        # Закрыть
        close_action = QAction(self.tr("❌ Close (Ctrl+W)"), self)
        # close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(lambda: self.close_tab(index))
        menu.addAction(close_action)

        menu.exec(self.tab_widget.tabBar().mapToGlobal(position))

    def restart_tab(self, index):
        tab_name = self.tab_widget.tabText(index)
        if tab_name == self.tr("Settings"):
            print("[INFO] Вкладку 'Settings' не можна перезапустити.")
            return

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



    # def add_search_and_buttons_to_title_bar(self):
    #     back_button = QPushButton("⬅️")
    #     forward_button = QPushButton("➡️")
    #     reload_button = QPushButton("🔁")
    #     new_tab_button = QPushButton("➕")
    #     downloads_button = QPushButton("📂")

    #     back_button.clicked.connect(lambda: self.tab_widget.currentWidget().back())
    #     forward_button.clicked.connect(lambda: self.tab_widget.currentWidget().forward())
    #     reload_button.clicked.connect(lambda: self.tab_widget.currentWidget().reload())
    #     new_tab_button.clicked.connect(self.add_tab)
    #     downloads_button.clicked.connect(self.open_downloads_explorer)

    #     # В методе add_search_and_buttons_to_title_bar():
    #     button_style = """
    #         QPushButton {
    #             font-size: 18px;
    #             background-color: transparent;
    #             border: none;
    #             width: 20px;
    #             height: 20px;
    #         }
    #         QPushButton:hover {
    #             background-color: rgba(255, 255, 255, 0.1);
    #         }
    #     """

    #     back_button.setStyleSheet(button_style)
    #     forward_button.setStyleSheet(button_style)
    #     reload_button.setStyleSheet(button_style)
    #     new_tab_button.setStyleSheet(button_style)
    #     downloads_button.setStyleSheet(button_style)

    #     self.search_input = Input(
    #         parent=self,
    #         translator=self.tr,
    #         lang_code=self.lang_code
    #     )
    #     self.search_input.setPlaceholderText(self.tr("Enter URL or search"))
    #     self.search_input.returnPressed.connect(self.load_url)

    #     url_layout = QHBoxLayout()
    #     url_layout.setContentsMargins(0, 0, 0, 0)
    #     url_layout.setSpacing(5)
    #     # url_layout.addWidget(lock_label)
    #     url_layout.addWidget(self.search_input)

    #     url_widget = QWidget()
    #     url_widget.setLayout(url_layout)

    #     self.add_title_widget(back_button)   
    #     self.add_title_widget(forward_button)
    #     self.add_title_widget(reload_button) 
    #     self.add_title_widget(url_widget)    
    #     self.add_title_widget(new_tab_button)
    #     self.add_title_widget(downloads_button)
    def add_search_and_buttons_to_title_bar(self):
        back_button = QPushButton("⬅️")
        forward_button = QPushButton("➡️")
        reload_button = QPushButton("🔁")
        new_tab_button = QPushButton("➕")
        downloads_button = QPushButton("📂")
        settings_button = QPushButton("⚙️")  # новая кнопка

        # back_button.clicked.connect(lambda: self.tab_widget.currentWidget().back())
        # forward_button.clicked.connect(lambda: self.tab_widget.currentWidget().forward())
        back_button.clicked.connect(lambda: self.tab_widget.currentWidget().back() if isinstance(self.tab_widget.currentWidget(), QWebEngineView) else None)
        forward_button.clicked.connect(lambda: self.tab_widget.currentWidget().forward() if isinstance(self.tab_widget.currentWidget(), QWebEngineView) else None)

        # reload_button.clicked.connect(lambda: self.tab_widget.currentWidget().reload())
        reload_button.clicked.connect(self.reload_current_tab)

        new_tab_button.clicked.connect(self.add_tab)
        downloads_button.clicked.connect(self.open_downloads_explorer)
        settings_button.clicked.connect(self.open_settings_tab)  # открываем вкладку настроек

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

        for btn in [back_button, forward_button, reload_button, new_tab_button, downloads_button, settings_button]:
            btn.setStyleSheet(button_style)

        self.search_input = Input(
            parent=self,
            translator=self.tr,
            lang_code=self.lang_code
        )
        self.search_input.setPlaceholderText(self.tr("Enter URL or search"))
        self.search_input.returnPressed.connect(self.load_url)

        url_layout = QHBoxLayout()
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(5)
        url_layout.addWidget(self.search_input)

        url_widget = QWidget()
        url_widget.setLayout(url_layout)

        self.add_title_widget(back_button)     
        self.add_title_widget(forward_button)  
        self.add_title_widget(reload_button)   
        self.add_title_widget(url_widget)      
        self.add_title_widget(new_tab_button)  
        self.add_title_widget(downloads_button)
        self.add_title_widget(settings_button)  # добавляем кнопку на панель

    def reload_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        tab_name = self.tab_widget.tabText(current_index)
        widget = self.tab_widget.currentWidget()

        # Не перезапускаємо вкладку Settings
        if tab_name == self.tr("Settings"):
            print("[INFO] Вкладку 'Settings' не можна перезапустити.")
            return

        # Перевіряємо, чи це QWebEngineView (тобто вебсторінка)
        if isinstance(widget, QWebEngineView):
            widget.reload()
        else:
            print(f"[INFO] Вкладка '{tab_name}' не є вебсторінкою, перезапуск не потрібен.")



    def open_downloads_explorer(self):
        """Открывает ExplorerWindow сразу в папке root/user/download"""
        # Строго фиксированный путь
        path = os.path.join("root", "user", "download")
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)  # если нет папки — создаём

        try:
            explorer_window = None

            # Проверяем, существует ли окно Explorer в родительском окне
            if hasattr(self.parent_window, 'open_windows'):
                explorer_window = self.parent_window.open_windows.get("explorer")

                # Если окно существует, но невалидное – пересоздаём
                if explorer_window is not None and not hasattr(explorer_window, 'isVisible'):
                    explorer_window = None
                    self.parent_window.open_windows["explorer"] = None

            # Если Explorer ещё не открыт – создаём
            if explorer_window is None:
                try:
                    explorer_module = __import__("apps.local.explorer.explorer", fromlist=["ExplorerWindow"])
                    ExplorerWindow = getattr(explorer_module, "ExplorerWindow")

                    explorer_window = ExplorerWindow(
                        parent=self.parent_window,
                        window_name="explorer",
                        translator=self.parent_window.tr if hasattr(self.parent_window, 'tr') else None,
                        lang_code=getattr(self.parent_window, 'current_language', 'en')
                    )

                    # Сохраняем ссылку на Explorer в open_windows
                    if hasattr(self.parent_window, 'open_windows'):
                        self.parent_window.open_windows["explorer"] = explorer_window

                except Exception as e:
                    StellarMessageBox.warning(self, self.tr("Error"),
                                              self.tr("Could not create Explorer window: {}").format(str(e)))
                    return

            # === Открываем конкретную папку загрузок ===
            if hasattr(explorer_window, "open_or_switch_tab"):
                explorer_window.open_or_switch_tab(path)
            elif hasattr(explorer_window, "open_path"):
                explorer_window.open_path(path)
            else:
                # fallback
                explorer_window.load_directory(path)


            explorer_window.show()
            explorer_window.raise_()
            explorer_window.activateWindow()

            # Обновляем менеджер окон, если есть
            if hasattr(self.parent_window, 'switch_window'):
                self.parent_window.switch_window("explorer")

        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"),
                                      self.tr("Could not open Explorer in downloads folder: {}").format(str(e)))


    def add_tab(self, url="https://www.google.com"):
        if not isinstance(url, str):
            url = f"https://www.google.com/?hl={self.lang_code}"

        # browser = QWebEngineView()
        browser = StyledWebEngineView()

        # browser.setStyleSheet("background-color: #D1D1D1; ")
        browser.setStyleSheet("background-color: transparent; border: none;")

        browser.loadFinished.connect(lambda ok: self.update_tab_title(browser))


        # Используем наш CustomWebEnginePage
        page = CustomWebEnginePage(self.profile, browser, self)
        browser.setPage(page)

        # Fullscreen
        # browser.page().fullScreenRequested.connect(self.handle_fullscreen_request)

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
        # new_browser.page().fullScreenRequested.connect(self.handle_fullscreen_request)

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

    # def handle_fullscreen_request(self, request):
    #     # if request.toggleOn():
    #     #     self.showFullScreen()
    #     # else:
    #     #     self.showNormal()
    #     # request.accept()
    #     request.reject()
    def handle_fullscreen_request(self, request):
        request.reject()


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


    def open_settings_tab(self):
        # Проверяем, есть ли уже вкладка настроек
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == self.tr("Settings"):
                self.tab_widget.setCurrentIndex(i)
                return

        from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                                    QComboBox, QLineEdit, QPushButton, QListWidget, 
                                    QStackedWidget, QFormLayout, QSizePolicy)
        from PyQt6.QtCore import Qt

        settings_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # --- Меню ---
        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(200)
        self.menu_list.addItem(self.tr("General"))

        # Кастомный скроллбар (требуется класс CastScrollBar)
        self.menu_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.menu_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))

        self.menu_list.setStyleSheet("""
            QListWidget {
                background-color: #2E2E2E;
                color: #E0E0E0;
                border: none;
                border-radius: 8px;
                padding-top: 10px;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px 15px;
                margin: 2px 8px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #4C8ED9;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3C3C3C;
            }
        """)

        # --- Контент страниц ---
        self.stack = QStackedWidget()
        self.stack.setMinimumWidth(500)

        # Страница General
        general_page = QWidget()
        general_layout = QVBoxLayout(general_page)
        general_layout.setContentsMargins(20, 20, 20, 20)
        general_layout.setSpacing(20)

        # Заголовок
        title_label = QLabel(self.tr("General"))
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #E0E0E0;
            margin-bottom: 10px;
        """)
        general_layout.addWidget(title_label)

        # Форма для настроек
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # Язык
        lang_label = QLabel(self.tr("Language:"))
        lang_label.setStyleSheet("color: #E0E0E0; font-size: 14px;")
        lang_combo = ComboBox()
        lang_combo.addItems(["en", "uk", "ru"])
        lang_combo.setCurrentText(self.lang_code)
        lang_combo.setFixedWidth(200)
        form_layout.addRow(lang_label, lang_combo)

        # Папка загрузок
        download_label = QLabel(self.tr("Download Path:"))
        download_label.setStyleSheet("color: #E0E0E0; font-size: 14px;")
        download_path_input = Input(
            parent=self,
            initial_text=self.download_path,
            translator=self.tr,
            lang_code=self.lang_code
        )
        download_path_input.setFixedWidth(300)
        form_layout.addRow(download_label, download_path_input)

        general_layout.addWidget(form_widget)
        general_layout.addStretch()

        # Кнопка сохранения
        save_button = QPushButton(self.tr("Save Settings"))
        save_button.setFixedWidth(220)
        save_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                background-color: #2196F3;
                color: white;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #1976D2; 
            }
            QPushButton:pressed { 
                background-color: #1565C0; 
            }
        """)
        general_layout.addWidget(save_button, 0, Qt.AlignmentFlag.AlignLeft)

        def save_settings():
            self.lang_code = lang_combo.currentText()
            self.download_path = download_path_input.text()
            os.makedirs(self.download_path, exist_ok=True)

            # Сохраняем в файл
            settings_data = {
                "lang_code": self.lang_code,
                "download_path": self.download_path
            }
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)

            StellarMessageBox.information(self, self.tr("Settings"), self.tr("Settings saved!"))

        save_button.clicked.connect(save_settings)

        # Создаем остальные страницы с заголовками
        def create_placeholder_page(title):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(20, 20, 20, 20)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #E0E0E0;
                margin-bottom: 10px;
            """)
            layout.addWidget(title_label)
            
            placeholder_label = QLabel(self.tr("This section is under development"))
            placeholder_label.setStyleSheet("color: #888888; font-size: 14px;")
            layout.addWidget(placeholder_label)
            layout.addStretch()
            
            return page

        system_update_page = create_placeholder_page(self.tr("System Update"))
        backups_page = create_placeholder_page(self.tr("Backups"))
        time_page = create_placeholder_page(self.tr("Time Settings"))

        self.stack.addWidget(general_page)
        self.stack.addWidget(system_update_page)
        self.stack.addWidget(backups_page)
        self.stack.addWidget(time_page)

        # Связываем меню и стек страниц
        self.menu_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.menu_list.setCurrentRow(0)  # по умолчанию показываем General

        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(self.stack)

        settings_widget.setLayout(main_layout)

        # Добавляем вкладку
        index = self.tab_widget.addTab(settings_widget, self.tr("Settings"))
        self.tab_widget.setCurrentIndex(index)