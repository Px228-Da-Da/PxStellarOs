# from PyQt6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
# )
# from PyQt6.QtWebEngineWidgets import QWebEngineView
# from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
# from PyQt6.QtCore import QUrl, Qt

# from PyQt6.QtWidgets import QTabBar

# import os, sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
# from dependencies import *


# class CustomWebEnginePage(QWebEnginePage):
#     def __init__(self, profile, parent, browser_window):
#         super().__init__(profile, parent)
#         self.browser_window = browser_window

#     # Перехватываем window.open()
#     def createWindow(self, web_window_type):
#         return self.browser_window.create_new_tab_from_page(web_window_type)


# class VscodeWindow(DraggableResizableWindow):
#     def __init__(self, parent=None, window_name="Vs Code", translator=None, lang_code="en"):
#         super().__init__(parent)
#         self.window_name = window_name
#         self.lang_code = lang_code
#         self.current_file = None
#         self.open_files = {}  # словарь file_path -> вкладка

#         self.setWindowTitle(self.tr("VSCode (Monaco)"))
#         self.setGeometry(300, 150, 1000, 700)

#         # Центральный контейнер
#         self.container = QWidget(self)
#         self.set_content(self.container)
#         layout = QVBoxLayout(self.container)
#         self.container.setLayout(layout)

#         # === Панель инструментов ===
#         toolbar_layout = QHBoxLayout()
#         self.new_btn = QPushButton("New")
#         self.open_btn = QPushButton("Open")
#         self.save_btn = QPushButton("Save")

#         self.new_btn.clicked.connect(self.new_file)
#         self.open_btn.clicked.connect(self.open_file)
#         self.save_btn.clicked.connect(self.save_file)

#         for btn in [self.new_btn, self.open_btn, self.save_btn]:
#             btn.setStyleSheet("""
#                 QPushButton {
#                     padding: 6px 14px;
#                     border-radius: 6px;
#                     background-color: #2196F3;
#                     color: white;
#                     border: none;
#                 }
#                 QPushButton:hover { background-color: #1976D2; }
#                 QPushButton:pressed { background-color: #1565C0; }
#             """)
#             self.add_title_widget(btn)

#         # === Таб файлов ===
#         self.tab_bar = QTabBar()
#         self.tab_bar.setTabsClosable(True)
#         self.tab_bar.tabCloseRequested.connect(self.close_tab)
#         self.tab_bar.currentChanged.connect(self.switch_tab)
#         toolbar_layout.addWidget(self.tab_bar)
#         layout.addLayout(toolbar_layout)

#         # Разделитель
#         separator = QFrame()
#         separator.setFrameShape(QFrame.Shape.HLine)
#         separator.setFrameShadow(QFrame.Shadow.Sunken)
#         layout.addWidget(separator)

#         # === Monaco Editor ===
#         self.browser = QWebEngineView()
#         html_path = os.path.abspath(os.path.join("apps", "local", "Vscode", "monaco", "index.html"))
#         if not os.path.exists(html_path):
#             print("❌ Не найден index.html:", html_path)
#         else:
#             print("✅ Загружаем Monaco:", html_path)

#         self.browser.setUrl(QUrl.fromLocalFile(html_path))
#         layout.addWidget(self.browser)

#         # === Статус-бар ===
#         self.status_label = QLabel("    Ready")

#         # Настраиваем профиль
#         self.profile = QWebEngineProfile("SublimeProfile", self)
#         browser_data_path = os.path.join(os.getcwd(), "root", "dataLacmi", "browser")
#         os.makedirs(browser_data_path, exist_ok=True)
#         self.profile.setPersistentStoragePath(os.path.join(browser_data_path, "web_profile"))
#         self.profile.setCachePath(os.path.join(browser_data_path, "web_cache"))

#         self.tab_bar.setStyleSheet("""
#             QTabWidget::pane {
#                 border: none;
#                 background-color: #2d2d30;
#             }
#             QTabBar::tab {
#                 background: #3e3e42;
#                 color: #ffffff;
#                 padding: 8px;
#                 border-radius: 5px;
#             }
#             QTabBar::tab:selected {
#                 background: #0078d7;
#                 color: #ffffff;
#             }
#         """)

#     # === Определяем язык Monaco по расширению ===
#     def detect_language(self, file_path: str) -> str:
#         ext = os.path.splitext(file_path)[1].lower()
#         filename = os.path.basename(file_path).lower()
        
#         mapping = {
#             ".py": "python",
#             ".js": "javascript",
#             ".jsx": "javascript",
#             ".ts": "typescript",
#             ".tsx": "typescript",
#             ".json": "json",
#             ".html": "html",
#             ".htm": "html",
#             ".css": "css",
#             ".scss": "scss",
#             ".less": "less",
#             ".cpp": "cpp",
#             ".c": "c",
#             ".h": "cpp",
#             ".hpp": "cpp",
#             ".java": "java",
#             ".txt": "plaintext",
#             ".md": "markdown",
#             ".xml": "xml",
#             ".php": "php",
#             ".rb": "ruby",
#             ".go": "go",
#             ".rs": "rust",
#             ".sh": "shell",
#             ".bash": "shell",
#             ".zsh": "shell",
#             ".sql": "sql",
#             ".yaml": "yaml",
#             ".yml": "yaml",
#             ".dockerfile": "dockerfile",
#             "dockerfile": "dockerfile",
#             ".config": "xml",
#             ".cs": "csharp",
#             ".vb": "vb",
#             ".fs": "fsharp",
#         }
        
#         # Специальные случаи для файлов без расширения или с особыми именами
#         if filename == "dockerfile":
#             return "dockerfile"
#         elif filename == "makefile":
#             return "makefile"
#         elif filename.startswith(".env"):
#             return "plaintext"
        
#         return mapping.get(ext, "plaintext")

#     # === Взаимодействие с Monaco ===
#     def set_text(self, text: str, language: str = "plaintext"):
#         js = f"""
#         (function waitForEditor() {{
#             if (window.editor) {{
#                 var model = window.editor.getModel();
#                 if (!model) {{
#                     model = monaco.editor.createModel({repr(text)}, {repr(language)});
#                     window.editor.setModel(model);
#                 }} else {{
#                     // Сначала устанавливаем язык, потом текст
#                     monaco.editor.setModelLanguage(model, {repr(language)});
#                     window.editor.setValue({repr(text)});
#                 }}
#             }} else {{
#                 setTimeout(waitForEditor, 50);
#             }}
#         }})();
#         """
#         self.browser.page().runJavaScript(js)


#     def get_text(self, callback):
#         """Получить текст из Monaco Editor после полной инициализации"""
#         js = """
#         (function waitForEditor() {
#             if (window.editor) {
#                 return window.editor.getValue();
#             } else {
#                 setTimeout(waitForEditor, 50);
#             }
#         })();
#         """
#         self.browser.page().runJavaScript(js, callback)


#     # === Кнопки ===
#     def new_file(self):
#         self.set_text("", "plaintext")
#         self.current_file = None
#         self.status_label.setText("    New file created")

#     def open_file(self):
#         file_path, _ = CustomFileDialog.getOpenFileName(
#             self,
#             self.tr("Open File"),
#             "",
#             "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js);;HTML (*.html);;CSS (*.css);;JSON (*.json)"
#         )
#         if not file_path:
#             return

#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 content = f.read()
#             language = self.detect_language(file_path)
#             self.set_text(content, language)
#             self.current_file = file_path

#             # --- Добавляем вкладку в tab_bar ---
#             if file_path not in self.open_files:
#                 index = self.tab_bar.addTab(os.path.basename(file_path))
#                 self.open_files[file_path] = index
#                 self.tab_bar.setCurrentIndex(index)
#             else:
#                 # если файл уже открыт, переключаемся на его вкладку
#                 self.tab_bar.setCurrentIndex(self.open_files[file_path])

#             self.status_label.setText(f"    Opened: {os.path.basename(file_path)} [{language}]")
#         except Exception as e:
#             self.status_label.setText(f"    Error: {e}")


#     def save_file(self):
#         """Сохраняем текст из Monaco в файл"""
#         def handle_code(code):
#             if not self.current_file:
#                 file_path, _ = CustomFileDialog.getSaveFileName(
#                     self,
#                     self.tr("Save File"),
#                     "",
#                     "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js)"
#                 )
#                 if not file_path:
#                     return
#                 self.current_file = file_path

#             try:
#                 with open(self.current_file, "w", encoding="utf-8") as f:
#                     f.write(code)
#                 self.status_label.setText(f"    Saved: {os.path.basename(self.current_file)}")
#             except Exception as e:
#                 self.status_label.setText(f"    Error: {e}")

#         self.get_text(handle_code)

#     # Для window.open()
#     def create_new_tab_from_page(self, window_type=None):
#         new_browser = QWebEngineView()
#         new_page = CustomWebEnginePage(self.profile, new_browser, self)
#         new_browser.setPage(new_page)
#         self.container.layout().addWidget(new_browser)
#         return new_page

#     def close_tab(self, index):
#         file_to_close = None
#         for file_path, tab_index in self.open_files.items():
#             if tab_index == index:
#                 file_to_close = file_path
#                 break
#         if file_to_close:
#             self.tab_bar.removeTab(index)
#             del self.open_files[file_to_close]
#             if self.current_file == file_to_close:
#                 self.current_file = None
#                 if self.open_files:
#                     # переключаем на первый открытый файл
#                     first_file = list(self.open_files.keys())[0]
#                     self.open_file_by_path(first_file)

#     def switch_tab(self, index):
#         for file_path, tab_index in self.open_files.items():
#             if tab_index == index:
#                 self.open_file_by_path(file_path)
#                 break

#     def open_file_by_path(self, file_path):
#         if not os.path.exists(file_path):
#             return

#         self.current_file = file_path

#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 content = f.read()
#             language = self.detect_language(file_path)

#             # Ждём, пока браузер полностью загрузит страницу
#             def try_set_text():
#                 js_check_editor = "typeof window.editor !== 'undefined';"
#                 def callback(result):
#                     if result:
#                         # Если редактор готов, устанавливаем текст и язык
#                         js_set_language = f"""
#                         (function() {{
#                             if (window.editor) {{
#                                 var model = window.editor.getModel();
#                                 if (!model) {{
#                                     model = monaco.editor.createModel({repr(content)}, {repr(language)});
#                                     window.editor.setModel(model);
#                                 }} else {{
#                                     window.editor.setValue({repr(content)});
#                                     monaco.editor.setModelLanguage(model, {repr(language)});
#                                 }}
#                             }}
#                         }})();
#                         """
#                         self.browser.page().runJavaScript(js_set_language)
                        
#                         self.status_label.setText(f"    Opened: {os.path.basename(file_path)} [{language}]")
#                         # Добавляем вкладку в tab_bar
#                         if file_path not in self.open_files:
#                             index = self.tab_bar.addTab(os.path.basename(file_path))
#                             self.open_files[file_path] = index
#                             self.tab_bar.setCurrentIndex(index)
#                         else:
#                             self.tab_bar.setCurrentIndex(self.open_files[file_path])
#                     else:
#                         # Если не готов, повторяем через 50мс
#                         QTimer.singleShot(50, try_set_text)
#                 self.browser.page().runJavaScript(js_check_editor, callback)

#             from PyQt6.QtCore import QTimer
#             try_set_text()

#         except Exception as e:
#             self.status_label.setText(f"    Error: {e}")
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QTabBar
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtWebChannel import QWebChannel
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *  # предполагаю, что здесь определён CustomFileDialog, DraggableResizableWindow и т.д.


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent, browser_window):
        super().__init__(profile, parent)
        self.browser_window = browser_window

    # Перехватываем window.open()
    def createWindow(self, web_window_type):
        return self.browser_window.create_new_tab_from_page(web_window_type)

from PyQt6.QtCore import QObject, pyqtSlot
import os

class Bridge(QObject):
    def __init__(self, parent=None, editor_window=None):
        super().__init__(parent)
        self.editor_window = editor_window
        self.current_folder = None

    # @pyqtSlot()
    # def open_folder(self):
    #     from PyQt6.QtWidgets import QFileDialog
    #     folder = QFileDialog.getExistingDirectory(None, "Select Project Folder")
    #     if folder:
    #         self.current_folder = folder
    #         files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    #         self.editor_window.browser.page().runJavaScript(f"loadProjectFiles({files});")

    @pyqtSlot(str)
    def open_file(self, filename):
        if not self.current_folder:
            return
        path = os.path.join(self.current_folder, filename)
        if not os.path.exists(path):
            return

        # Проверяем, не открыт ли файл уже
        if path in self.editor_window.open_files:
            idx = self.editor_window.open_files.index(path)
            self.editor_window.tab_bar.setCurrentIndex(idx)
            self.editor_window.switch_tab(idx)
            return

        # Читаем содержимое
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()

        # Определяем язык
        ext = os.path.splitext(filename)[1].lower()
        lang = self.editor_window.detect_language(path)

        # Создаём новую вкладку и загружаем содержимое
        self.editor_window.create_tab(title=filename, path=path, content=code, language=lang)

    @pyqtSlot(str)
    def create_file(self, name):
        if not self.current_folder:
            return
        path = os.path.join(self.current_folder, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("")  # пустой файл
        self.open_folder(self.current_folder)


    @pyqtSlot(str)
    def create_folder(self, name):
        if not self.current_folder:
            return
        path = os.path.join(self.current_folder, name)
        os.makedirs(path, exist_ok=True)
        self.open_folder(self.current_folder)


    @pyqtSlot(str)
    def open_folder(self, path=None):
        from PyQt6.QtWidgets import QFileDialog
        if not path:
            path = QFileDialog.getExistingDirectory(None, "Select Project Folder")
        if path:
            self.current_folder = path
            entries = []
            for name in os.listdir(path):
                full = os.path.join(path, name)
                if os.path.isdir(full):
                    entries.append({"name": name, "type": "folder"})
                else:
                    entries.append({"name": name, "type": "file"})
            # передаём в JS
            self.editor_window.browser.page().runJavaScript(f"loadProjectFiles({entries}, {repr(path)});")




class VscodeWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="Vs Code", translator=None, lang_code="en"):
        super().__init__(parent)
        self.window_name = window_name
        self.lang_code = lang_code
        self.current_file = None
        self.open_files = []  # список: индекс в таббаре -> путь или None (unsaved)
        self.untitled_count = 1

        self.setWindowTitle(self.tr("VSCode (Monaco)"))
        self.setGeometry(300, 150, 1000, 700)

        # Центральный контейнер
        self.container = QWidget(self)
        self.set_content(self.container)
        layout = QVBoxLayout(self.container)
        self.container.setLayout(layout)

        # === Панель инструментов (кнопки в заголовке окна) ===
        self.new_btn = QPushButton("New")
        self.open_btn = QPushButton("Open")
        self.save_btn = QPushButton("Save")

        self.new_btn.clicked.connect(self.new_file)
        self.open_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save_file)

        for btn in [self.new_btn, self.open_btn, self.save_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 14px;
                    border-radius: 6px;
                    background-color: #2196F3;
                    color: white;
                    border: none;
                }
                QPushButton:hover { background-color: #1976D2; }
                QPushButton:pressed { background-color: #1565C0; }
            """)
            self.add_title_widget(btn)

        # === TabBar для файлов (PyQt) ===
        self.tab_bar = QTabBar()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.switch_tab)
        layout.addWidget(self.tab_bar)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # === Monaco Editor (QWebEngineView) ===
        self.browser = QWebEngineView()
        html_path = os.path.abspath(os.path.join("apps", "local", "Vscode", "monaco", "index.html"))
        if not os.path.exists(html_path):
            print("❌ Не найден index.html:", html_path)
        else:
            print("✅ Загружаем Monaco:", html_path)

        # Настраиваем профиль (путь для кеша и storage)
        self.profile = QWebEngineProfile("VscodeProfile", self)
        browser_data_path = os.path.join(os.getcwd(), "root", "dataLacmi", "browser")
        os.makedirs(browser_data_path, exist_ok=True)
        self.profile.setPersistentStoragePath(os.path.join(browser_data_path, "web_profile"))
        self.profile.setCachePath(os.path.join(browser_data_path, "web_cache"))

        # Устанавливаем кастомную страницу, чтобы перехватывать window.open()
        page = CustomWebEnginePage(self.profile, self.browser, self)
        self.browser.setPage(page)


        # создаём QWebChannel и регистрируем bridge
        self.channel = QWebChannel(self.browser.page())
        self.bridge = Bridge(editor_window=self)
        self.channel.registerObject("bridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)

        # потом уже загружаем HTML
        self.browser.setUrl(QUrl.fromLocalFile(html_path))

        self.browser.setUrl(QUrl.fromLocalFile(html_path))
        layout.addWidget(self.browser)

        # === Статус-бар PyQt (информативно) ===
        self.tab_bar.setStyleSheet("""
            QTabBar {
                background: #2d2d2d;
                border: none;
                padding: 0px;
                height: 30px;
            }

            QTabBar::tab {
                background: #3c3c3c;
                color: #cccccc;
                padding: 6px 12px;
                margin-right: 1px;
                height: 20px;
            }

            QTabBar::tab:hover {
                background: #444444;
            }

            QTabBar::tab:selected {
                background: #1e1e1e;
                color: #ffffff;
                border-bottom: 2px solid #007acc;
            }

            QTabBar::close-button {
                image: url(close-icon.png);  /* можешь заменить на свою иконку */
                subcontrol-position: right;
                margin-left: 8px;
            }

            QTabBar::close-button:hover {
                image: url(close-icon-hover.png);
            }
        """)


    # --- Вспомогательные: установка текста в Monaco (ждём создания editor) ---
    # def set_text(self, text: str, language: str = "plaintext"):
    #     # Используем JS API, определённый в index.html: setValueWithLanguage
    #     js = f"""
    #     (function waitForEditor() {{
    #         if (typeof window.setValueWithLanguage === 'function') {{
    #             window.setValueWithLanguage({repr(text)}, {repr(language)});
    #         }} else {{
    #             setTimeout(waitForEditor, 50);
    #         }}
    #     }})();
    #     """
    #     self.browser.page().runJavaScript(js)
    def set_text(self, text: str, language: str = "plaintext"):
        """Установка текста в редактор (основной метод)"""
        self.set_text_safe(text, language)

    def get_text(self, callback):
        js = """
        (function waitForEditor() {
            if (typeof window.getValue === 'function') {
                return window.getValue();
            } else {
                setTimeout(waitForEditor, 50);
            }
        })();
        """
        self.browser.page().runJavaScript(js, callback)

    # === Управление вкладками ===
    # def create_tab(self, title: str = None, path: str = None, content: str = None, language: str = "plaintext"):
    #     if title is None:
    #         if path:
    #             title = os.path.basename(path)
    #         else:
    #             title = f"Untitled-{self.untitled_count}"
    #             self.untitled_count += 1

    #     index = self.tab_bar.addTab(title)
    #     # вставляем путь (или None) в список на позицию index
    #     self.open_files.insert(index, path)
    #     self.tab_bar.setCurrentIndex(index)

    #     # загружаем содержимое
    #     if path and content is None:
    #         try:
    #             with open(path, "r", encoding="utf-8") as f:
    #                 content = f.read()
    #         except Exception as e:
    #             content = ""
    #             # self.status_label.setText(f"    Error reading file: {e}")

    #     if content is None:
    #         content = ""

    #     # если язык не указан и есть путь — определяем
    #     if not language and path:
    #         language = self.detect_language(path)

    #     self.set_text(content, language or "plaintext")
    #     self.current_file = path
    #     # self.status_label.setText(f"    Opened: {title} [{language}]")

    #     # обновим HTML-статусбар кодировку (если нужно)
    #     self.browser.page().runJavaScript(f"window.setEncoding({repr('UTF-8')});")
    def create_tab(self, title: str = None, path: str = None, content: str = None, language: str = "plaintext"):
        if title is None:
            if path:
                title = os.path.basename(path)
            else:
                title = f"Untitled-{self.untitled_count}"
                self.untitled_count += 1

        index = self.tab_bar.addTab(title)
        # вставляем путь (или None) в список на позицию index
        self.open_files.insert(index, path)
        self.tab_bar.setCurrentIndex(index)

        # загружаем содержимое
        if path and content is None:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                content = ""
                print(f"❌ Error reading file {path}: {e}")

        if content is None:
            content = ""

        # если язык не указан и есть путь — определяем
        if not language and path:
            language = self.detect_language(path)

        # Сохраняем данные для текущей вкладки
        self.current_file = path
        self.current_content = content
        self.current_language = language or "plaintext"

        # Загружаем содержимое с ожиданием готовности редактора
        self.load_content_for_current_tab()

    def load_content_for_current_tab(self):
        """Загружает содержимое для текущей активной вкладки"""
        if hasattr(self, 'current_content') and hasattr(self, 'current_language'):
            self.set_text_safe(self.current_content, self.current_language)
            
            # обновим HTML-статусбар кодировку
            self.browser.page().runJavaScript(f"window.setEncoding({repr('UTF-8')});")
            print(f"✅ Content loaded for: {self.current_file}")

    def new_file(self):
        # Создаём пустую вкладку без привязки к файлу
        self.create_tab(title=None, path=None, content="", language="plaintext")
        self.current_file = None
        # self.status_label.setText("    New file created")

    def open_file(self):
        file_path, _ = CustomFileDialog.getOpenFileName(
            self,
            self.tr("Open File"),
            "",
            "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js);;HTML (*.html);;CSS (*.css);;JSON (*.json)"
        )
        if not file_path:
            return

        # Если уже открыт — просто переключаемся
        if file_path in self.open_files:
            idx = self.open_files.index(file_path)
            self.tab_bar.setCurrentIndex(idx)
            self.switch_tab(idx)
            return

        # Иначе создаём новую вкладку и загружаем
        self.create_tab(title=os.path.basename(file_path), path=file_path)

    def save_file(self):
        """Сохраняем текст из Monaco в файл (если вкладка была Untitled — спросим путь)"""
        def handle_code(code):
            idx = self.tab_bar.currentIndex()
            if idx < 0 or idx >= len(self.open_files):
                # нет активной вкладки — спросим путь
                file_path, _ = CustomFileDialog.getSaveFileName(
                    self,
                    self.tr("Save File"),
                    "",
                    "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js)"
                )
                if not file_path:
                    return
            else:
                current_path = self.open_files[idx]
                if not current_path:
                    file_path, _ = CustomFileDialog.getSaveFileName(
                        self,
                        self.tr("Save File"),
                        "",
                        "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js)"
                    )
                    if not file_path:
                        return
                    # обновляем путь в списке и текст вкладки
                    self.open_files[idx] = file_path
                    self.tab_bar.setTabText(idx, os.path.basename(file_path))
                else:
                    file_path = current_path

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                self.current_file = file_path
                # self.status_label.setText(f"    Saved: {os.path.basename(file_path)}")
                # обновляем HTML-статусбар (например кодировку)
                self.browser.page().runJavaScript(f"window.setEncoding({repr('UTF-8')});")
            except Exception as e:
                # self.status_label.setText(f"    Error: {e}")
                pass

        self.get_text(handle_code)

    def close_tab(self, index):
        if index < 0 or index >= len(self.open_files):
            return
        was_current_path = self.open_files[index]
        # удаляем таб и запись
        self.tab_bar.removeTab(index)
        removed = self.open_files.pop(index)

        # если вкладки остались — переключаемся на ближайшую
        if self.open_files:
            new_index = min(index, len(self.open_files) - 1)
            self.tab_bar.setCurrentIndex(new_index)
            self.switch_tab(new_index)
        else:
            # нет вкладок — очистим редактор
            self.set_text("", "plaintext")
            self.current_file = None
            # self.status_label.setText("    Ready")
            # сброс статуса HTML
            self.browser.page().runJavaScript("window.updateStatus('UTF-8', 1, 1);")

        # === Определяем язык Monaco по расширению ===
    def detect_language(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path).lower()
        
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".json": "json",
            ".html": "html",
            ".mhtml": "html",
            ".htm": "html",
            ".css": "css",
            ".qss": "css",
            ".scss": "scss",
            ".less": "less",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "cpp",
            ".hpp": "cpp",
            ".java": "java",
            ".txt": "plaintext",
            ".md": "markdown",
            ".xml": "xml",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".sh": "shell",
            ".bash": "shell",
            ".zsh": "shell",
            ".sql": "sql",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".dockerfile": "dockerfile",
            "dockerfile": "dockerfile",
            ".config": "xml",
            ".cs": "csharp",
            ".vb": "vb",
            ".fs": "fsharp",
        }
        
        # Специальные случаи для файлов без расширения или с особыми именами
        if filename == "dockerfile":
            return "dockerfile"
        elif filename == "makefile":
            return "makefile"
        elif filename.startswith(".env"):
            return "plaintext"
        
        return mapping.get(ext, "plaintext")

    # def switch_tab(self, index):
    #     if index < 0 or index >= len(self.open_files):
    #         return
    #     file_path = self.open_files[index]
    #     if file_path:
    #         # загружаем файл без добавления новой вкладки
    #         self.load_path_into_editor(file_path)
    #         self.tab_bar.setTabText(index, os.path.basename(file_path))
    #     else:
    #         # unsaved/new
    #         self.set_text("", "plaintext")
    #         self.current_file = None
    #         # self.status_label.setText("    New file")
    def switch_tab(self, index):
        if index < 0 or index >= len(self.open_files):
            return
            
        file_path = self.open_files[index]
        self.current_file = file_path
        
        if file_path:
            # Загружаем содержимое файла
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    language = self.detect_language(file_path)
                    
                    # Сохраняем данные и загружаем
                    self.current_content = content
                    self.current_language = language
                    self.load_content_for_current_tab()
                    
                except Exception as e:
                    print(f"❌ Error reading file when switching tabs: {e}")
                    self.set_text_safe("", "plaintext")
            else:
                self.set_text_safe("", "plaintext")
        else:
            # unsaved/new tab
            self.set_text_safe("", "plaintext")

    def load_path_into_editor(self, file_path):
        if not os.path.exists(file_path):
            # self.status_label.setText(f"    File not found: {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            language = self.detect_language(file_path)
            self.set_text(content, language)
            self.current_file = file_path
            # self.status_label.setText(f"    Opened: {os.path.basename(file_path)} [{language}]")
            # Обновим HTML-статусбар (кодировка)
            self.browser.page().runJavaScript(f"window.setEncoding({repr('UTF-8')});")
        except Exception as e:
            # self.status_label.setText(f"    Error: {e}")
            pass

    # Для window.open() в вебе (если монaко или содержимое попытается открыть новое окно) 
    def create_new_tab_from_page(self, window_type=None):
        # создаём новый QWebEngineView внутри контейнера — поведение простое
        new_browser = QWebEngineView()
        new_page = CustomWebEnginePage(self.profile, new_browser, self)
        new_browser.setPage(new_page)
        # добавляем визуально в контейнер (внизу)
        self.container.layout().addWidget(new_browser)
        return new_page

    def wait_for_editor_ready(self, callback, max_attempts=50, attempt=0):
        """Ждем, пока редактор будет готов к работе"""
        if attempt >= max_attempts:
            print("❌ Editor not ready after maximum attempts")
            return
            
        js_check = """
        (function() {
            return typeof window.editor !== 'undefined' && 
                   window.editor.getModel() !== null &&
                   typeof window.setValueWithLanguage === 'function';
        })();
        """
        
        def handle_result(result):
            if result:
                callback()
            else:
                # Пробуем снова через 50мс
                QTimer.singleShot(50, lambda: self.wait_for_editor_ready(callback, max_attempts, attempt + 1))
        
        self.browser.page().runJavaScript(js_check, handle_result)

    def set_text_safe(self, text: str, language: str = "plaintext"):
        """Безопасная установка текста с ожиданием готовности редактора"""
        def set_text():
            js = f"""
            (function() {{
                if (typeof window.setValueWithLanguage === 'function') {{
                    window.setValueWithLanguage({repr(text)}, {repr(language)});
                    return true;
                }}
                return false;
            }})();
            """
            
            def handle_set_result(result):
                if not result:
                    # Если не удалось, пробуем альтернативный метод
                    self.set_text_fallback(text, language)
            
            self.browser.page().runJavaScript(js, handle_set_result)
        
        self.wait_for_editor_ready(set_text)

    def set_text_fallback(self, text: str, language: str = "plaintext"):
        """Альтернативный метод установки текста"""
        js = f"""
        (function() {{
            if (window.editor) {{
                var model = window.editor.getModel();
                if (!model) {{
                    model = monaco.editor.createModel({repr(text)}, {repr(language)});
                    window.editor.setModel(model);
                }} else {{
                    window.editor.setValue({repr(text)});
                    monaco.editor.setModelLanguage(model, {repr(language)});
                }}
                window.editor.layout();
                return true;
            }}
            return false;
        }})();
        """
        self.browser.page().runJavaScript(js)