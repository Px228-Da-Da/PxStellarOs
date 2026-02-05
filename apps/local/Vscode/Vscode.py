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
from PyQt6.QtWidgets import QStackedWidget, QListWidget, QLineEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl, Qt, QTimer

from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *  # предполагаю, что здесь определён CustomFileDialog, DraggableResizableWindow и т.д.




class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent, browser_window):
        super().__init__(profile, parent)
        self.browser_window = browser_window  # VscodeWindow

    # --- helpers ---
    def _parent_widget(self):
        # чтобы окно было "внутри твоей ОС/контейнера"
        return self.browser_window

    def javaScriptAlert(self, securityOrigin: QUrl, msg: str):
        # alert()
        try:
            StellarMessageBox.warning(self._parent_widget(), "JS", msg)
        except Exception:
            # запасной вариант
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self._parent_widget(), "JS", msg)

    def javaScriptConfirm(self, securityOrigin: QUrl, msg: str) -> bool:
        # confirm()

        # ✅ отключаем надоедливые "leave this page?" (beforeunload)
        low = (msg or "").lower()
        if "leave this page" in low or "changes that you made may not be saved" in low:
            return True  # автоподтверждение без окна

        # Пытаемся показать “в твоём стиле”
        try:
            # если у StellarMessageBox есть question() — используем
            if hasattr(StellarMessageBox, "question"):
                # ожидаем True/False
                return bool(StellarMessageBox.question(self._parent_widget(), "JS", msg))
            # иначе хотя бы warning + OK/Cancel через Qt
        except Exception:
            pass

        from PyQt6.QtWidgets import QMessageBox
        res = QMessageBox.question(
            self._parent_widget(),
            "JS",
            msg,
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        return res == QMessageBox.StandardButton.Ok

    def javaScriptPrompt(self, securityOrigin: QUrl, msg: str, defaultValue: str):
        # prompt()
        try:
            # если у тебя есть свой диалог ввода — вставь сюда
            from PyQt6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(self._parent_widget(), "JS", msg, text=defaultValue or "")
            return (ok, text)
        except Exception:
            return (False, defaultValue or "")

    # Перехватываем window.open()
    def createWindow(self, web_window_type):
        return self.browser_window.create_new_tab_from_page(web_window_type)

class DropForwarder(QObject):
    def __init__(self, target_window):
        super().__init__(target_window)
        self.target = target_window

    def eventFilter(self, obj, event):
        t = event.type()
        if t in (QEvent.Type.DragEnter, QEvent.Type.DragMove, QEvent.Type.Drop):
            md = event.mimeData()
            if md and md.hasUrls():
                if t == QEvent.Type.DragEnter:
                    self.target.dragEnterEvent(event)
                elif t == QEvent.Type.DragMove:
                    self.target.dragMoveEvent(event)
                else:
                    self.target.dropEvent(event)
                return True
        return False

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
        if os.path.isdir(path):
            self.open_folder(path)
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


    @pyqtSlot()
    def open_folder(self):
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(None, "Select Project Folder")
        if path:
            self._open_folder_impl(path)

    @pyqtSlot(str)
    def open_folder_path(self, path: str):
        if path:
            self._open_folder_impl(path)

    def _open_folder_impl(self, path: str):
        self.current_folder = path
        entries = []
        for name in os.listdir(path):
            full = os.path.join(path, name)
            if os.path.isdir(full):
                entries.append({"name": name, "type": "folder"})
            else:
                entries.append({"name": name, "type": "file"})

        payload = json.dumps(entries, ensure_ascii=False)
        path_js = json.dumps(path, ensure_ascii=False)

        self.editor_window.browser.page().runJavaScript(
            f"loadProjectFiles({payload}, {path_js});"
        )


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

        self.username = get_current_username()
        self.projects_db = os.path.join(os.getcwd(), "root", f"{self.username}", "vscode_projects.json")
        os.makedirs(os.path.dirname(self.projects_db), exist_ok=True)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptDrops, True)

        # Центральный контейнер
        self.container = QWidget(self)
        self.setAcceptDrops(True)
        self.container.setAcceptDrops(True)
        self.set_content(self.container)
        layout = QVBoxLayout(self.container)
        self.container.setLayout(layout)

        # === Панель инструментов (кнопки в заголовке окна) ===
        self.new_btn = QPushButton("New")
        self.open_btn = QPushButton("Open")
        self.save_btn = QPushButton("Save")
        self.run_btn  = QPushButton("Run")   # ✅ добавили

        self.new_btn.clicked.connect(self.new_file)
        self.open_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save_file)
        self.run_btn.clicked.connect(self.run_current)  # ✅ добавили

        for btn in [self.new_btn, self.open_btn, self.save_btn, self.run_btn]:
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

        # ✅ для предпросмотра (чтобы закрывать прошлое окно)
        self._hs_preview_window = None

        # ✅ F5 = Run (не зависимо от фокуса в браузере)
        self.sc_run_hs = QShortcut(QKeySequence(Qt.Key.Key_F5), self)
        self.sc_run_hs.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.sc_run_hs.activated.connect(self.run_current)

        # === TabBar для файлов (PyQt) ===
        self.tab_bar = QTabBar()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.switch_tab)
        # layout.addWidget(self.tab_bar)
        layout.addWidget(self.tab_bar)

        # === Monaco Editor (QWebEngineView) ===
        self.browser = QWebEngineView()
        # Чтобы QWebEngineView не перехватывал drop — пусть событие дойдёт до окна.
        self.browser.setAcceptDrops(False)
        self._monaco_loaded = False
        self._pending_open = None  # (text, language)
        self.browser.loadFinished.connect(self._on_monaco_loaded)
        html_path = os.path.abspath(os.path.join("apps", "local", "Vscode", "monaco", "index.html"))
        if not os.path.exists(html_path):
            print("❌ Не найден index.html:", html_path)
        else:
            # print("✅ Загружаем Monaco:", html_path)
            pass

        # Настраиваем профиль (путь для кеша и storage)
        self.profile = QWebEngineProfile("VscodeProfile", self)
        browser_data_path = os.path.join(os.getcwd(), "root", f"{self.username}", "browser")
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

        # self.browser.setUrl(QUrl.fromLocalFile(html_path))
        # layout.addWidget(self.browser)

        # --- STACK: стартовый экран / редактор ---
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # 1) Стартовый экран проектов
        self.start_page = QWidget()
        self._build_start_page(self.start_page)
        self.stack.addWidget(self.start_page)

        # 2) Страница редактора (Monaco)
        self.editor_page = QWidget()
        editor_layout = QVBoxLayout(self.editor_page)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        # --- Enable drops on top widgets (stack/pages), иначе курсор будет 🚫 ---
        for w in (self.stack, self.start_page, self.editor_page, self.tab_bar):
            w.setAcceptDrops(True)
            w.setAttribute(Qt.WidgetAttribute.WA_AcceptDrops, True)

        # --- Forward drag/drop from stack pages to window handlers ---
        self._drop_forwarder = DropForwarder(self)
        self.stack.installEventFilter(self._drop_forwarder)
        self.start_page.installEventFilter(self._drop_forwarder)
        self.editor_page.installEventFilter(self._drop_forwarder)
        self.tab_bar.installEventFilter(self._drop_forwarder)


        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        editor_layout.addWidget(self.browser)
        self.stack.addWidget(self.editor_page)

        # Показать сначала проекты
        self.stack.setCurrentWidget(self.start_page)


        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)


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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        md = event.mimeData()
        if not md.hasUrls():
            event.ignore()
            return

        paths = []
        for url in md.urls():
            p = url.toLocalFile()
            if p:
                paths.append(os.path.abspath(p))

        folders = [p for p in paths if os.path.isdir(p)]
        files   = [p for p in paths if os.path.isfile(p)]

        if folders and hasattr(self, "open_project"):
            self.open_project(folders[0])

        for fp in files:
            # у тебя есть create_tab(title, path)
            self.create_tab(title=os.path.basename(fp), path=fp)

        event.acceptProposedAction()



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

    def _load_projects(self):
        try:
            if os.path.exists(self.projects_db):
                with open(self.projects_db, "r", encoding="utf-8") as f:
                    data = json.load(f) or []
                # оставляем только существующие папки
                return [p for p in data if isinstance(p, str) and os.path.isdir(p)]
        except Exception as e:
            print("[VSCODE] projects db read error:", e)
        return []

    def _save_projects(self, projects: list[str]):
        try:
            with open(self.projects_db, "w", encoding="utf-8") as f:
                json.dump(projects[:30], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("[VSCODE] projects db save error:", e)

    def _on_monaco_loaded(self, ok: bool):
        self._monaco_loaded = bool(ok)
        if not ok:
            return

        # если был запрос открыть файл пока Monaco грузился — применяем
        if self._pending_open:
            text, lang = self._pending_open
            self._pending_open = None
            QTimer.singleShot(0, lambda: self.set_text_safe(text, lang))


    def _add_recent_project(self, path: str):
        path = os.path.abspath(path)
        projects = self._load_projects()
        if path in projects:
            projects.remove(path)
        projects.insert(0, path)
        self._save_projects(projects)
        self._refresh_projects_list()

    def _build_start_page(self, page: QWidget):
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        title = QLabel("Projects")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: 600;")
        lay.addWidget(title)

        self.projects_list = QListWidget()
        self.projects_list.setStyleSheet("""
            QListWidget { background: #1e1e1e; color: #ddd; border: 1px solid #333; }
            QListWidget::item { padding: 8px; }
            QListWidget::item:selected { background: #2a2a2a; }
        """)
        self.projects_list.itemDoubleClicked.connect(lambda _: self.open_selected_project())
        lay.addWidget(self.projects_list, 1)

        # Create project
        row = QHBoxLayout()
        self.new_project_name = Input(
            parent=self,
            translator=self.tr,
            lang_code=getattr(self, "Project name…", "en")
        )
        self.new_project_name.setPlaceholderText("Project name…")
        self.new_project_name.setStyleSheet("padding: 6px; background:#111; color:#ddd; border:1px solid #333;")
        row.addWidget(self.new_project_name, 1)

        btn_create = QPushButton("Create")
        btn_open = QPushButton("Open existing…")
        btn_add = QPushButton("Add to list…")

        for b in (btn_create, btn_open, btn_add):
            b.setStyleSheet("""
                QPushButton{ padding: 6px 12px; border-radius: 6px; background:#2196F3; color:white; border:none; }
                QPushButton:hover{ background:#1976D2; }
                QPushButton:pressed{ background:#1565C0; }
            """)

        btn_create.clicked.connect(self.create_project)
        btn_open.clicked.connect(self.open_project_dialog)
        btn_add.clicked.connect(self.add_project_dialog)

        row.addWidget(btn_create)
        row.addWidget(btn_open)
        row.addWidget(btn_add)
        lay.addLayout(row)

        btn_open_sel = QPushButton("Open selected")
        btn_open_sel.setStyleSheet("""
            QPushButton{ padding: 8px 12px; border-radius: 8px; background:#3c3c3c; color:#ddd; border:1px solid #444; }
            QPushButton:hover{ background:#444; }
        """)
        btn_open_sel.clicked.connect(self.open_selected_project)
        lay.addWidget(btn_open_sel)

        self._refresh_projects_list()

    def _refresh_projects_list(self):
        self.projects_list.clear()
        for p in self._load_projects():
            self.projects_list.addItem(p)

    def open_selected_project(self):
        item = self.projects_list.currentItem()
        if not item:
            return
        self.open_project(item.text())

    def open_project(self, path: str):
        if not os.path.isdir(path):
            return
        self._add_recent_project(path)

        # передаём в bridge и грузим дерево
        try:
            self.bridge.open_folder_path(path)  # у тебя уже есть :contentReference[oaicite:3]{index=3}
        except Exception as e:
            print("[VSCODE] open_folder error:", e)

        # показываем редактор
        self.stack.setCurrentWidget(self.editor_page)
        self.setWindowTitle(f"VSCode (Monaco) — {os.path.basename(path)}")

    def open_project_dialog(self):
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(None, "Select Project Folder")
        if path:
            self.open_project(path)

    def add_project_dialog(self):
        # почти как open_project_dialog, но не переключаемся — только добавляем
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(None, "Add Project Folder")
        if path:
            self._add_recent_project(path)

    def create_project(self):
        name = (self.new_project_name.text() or "").strip()
        if not name:
            return

        # куда создавать: root/<user>/projects/<name>
        base = os.path.join(os.getcwd(), "root", f"{self.username}", "projects")
        os.makedirs(base, exist_ok=True)

        proj = os.path.join(base, name)
        os.makedirs(proj, exist_ok=True)

        # минимальный шаблон для твоей ОС
        # (позже ты заменишь на DSL-template)
        app_dir = os.path.join(proj, name)
        os.makedirs(app_dir, exist_ok=True)

        cfg = os.path.join(app_dir, "config.json")
        if not os.path.exists(cfg):
            with open(cfg, "w", encoding="utf-8") as f:
                json.dump({"name": name}, f, ensure_ascii=False, indent=2)

        main_hs = os.path.join(app_dir, "main.hs")
        if not os.path.exists(main_hs):
            with open(main_hs, "w", encoding="utf-8") as f:
                f.write(
                    f'app "{name}" size(520, 300)\n\n'
                    'namber = Input(lang_code="current_language", placeholder_text="input namber")\n'
                    'title  = Label(text="Type number:")\n'
                    'btn    = Button(text="Show")\n\n'
                    'add(title)\n'
                    'add(namber)\n'
                    'add(btn)\n'
                )


        self.open_project(proj)


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
    def create_tab(self, title: str = None, path: str = None, content: str = None, language: str | None = None):
        # показать редактор, если открываем файл
        if hasattr(self, "stack") and hasattr(self, "editor_page"):
            self.stack.setCurrentWidget(self.editor_page)
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
        # ✅ язык определяем всегда по расширению, если открываем файл
        if path:
            detected = self.detect_language(path)
            if (language is None) or (language == "plaintext"):
                language = detected


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
            # print(f"✅ Content loaded for: {self.current_file}")

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
            "All Files (*);;Hitti Script (*.hs);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js);;HTML (*.html);;CSS (*.css);;JSON (*.json)"
        )
        if not file_path:
            return

        # ✅ ВАЖНО: если выбрали папку — не открываем как файл
        if os.path.isdir(file_path):
            # вариант 1: открыть как проект
            self.open_project(file_path)
            return
            # вариант 2: просто return (если не хочешь открывать как проект)

        # дальше твой текущий код открытия файла...
        if file_path in self.open_files:
            idx = self.open_files.index(file_path)
            self.tab_bar.setCurrentIndex(idx)
            self.switch_tab(idx)
            return

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
            ".hs": "HittiScript",
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
        if hasattr(self, "stack") and hasattr(self, "editor_page"):
            self.stack.setCurrentWidget(self.editor_page)
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
        if not getattr(self, "_monaco_loaded", False):
            self._pending_open = (text, language)
            return
        """Безопасная установка текста с ожиданием готовности редактора"""
        def set_text():
            js = f"""
                (function() {{
                    if (typeof window.setValueWithLanguage === 'function') {{
                        window.setValueWithLanguage({repr(text)}, {repr(language)});
                        if (window.editor) {{
                            window.editor.layout();
                            if (typeof window.editor.render === 'function') window.editor.render();
                            setTimeout(() => window.editor && window.editor.layout(), 0);
                            setTimeout(() => window.editor && window.editor.layout(), 50);
                        }}
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

    def run_current(self):
        """Run текущего .hs: сохраняем, парсим DSL и показываем окно."""
        idx = self.tab_bar.currentIndex()
        if idx < 0 or idx >= len(self.open_files):
            return

        path = self.open_files[idx]

        # если файл не сохранён — спросим путь
        def after_saved(file_path: str, code: str):
            if not file_path.lower().endswith(".hs"):
                StellarMessageBox.warning(self, self.tr("Run"), "Run работает только для .hs файлов.")
                return
            self._run_hs_code(code)

        self._save_current_for_run(after_saved)


    def _save_current_for_run(self, done_cb):
        """Сохраняет текущий файл и возвращает (path, code) в done_cb."""
        import os

        def handle_code(code: str):
            idx = self.tab_bar.currentIndex()
            if idx < 0 or idx >= len(self.open_files):
                return

            current_path = self.open_files[idx]

            # если вкладка без пути — спросим путь
            if not current_path:
                file_path, _ = CustomFileDialog.getSaveFileName(
                    self,
                    self.tr("Save File"),
                    "",
                    "HittiScript (*.hs);All Files (*)"
                )
                if not file_path:
                    return
                if not file_path.lower().endswith(".hs"):
                    file_path += ".hs"

                self.open_files[idx] = file_path
                self.tab_bar.setTabText(idx, os.path.basename(file_path))
                current_path = file_path

            try:
                with open(current_path, "w", encoding="utf-8") as f:
                    f.write(code)
                self.current_file = current_path
                try:
                    self.browser.page().runJavaScript(f"window.setEncoding({repr('UTF-8')});")
                except Exception:
                    pass
                done_cb(current_path, code)
            except Exception as e:
                StellarMessageBox.warning(self, self.tr("Save error"), str(e))

        self.get_text(handle_code)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        QTimer.singleShot(0, lambda: self.browser.page().runJavaScript(
            "if(window.editor){window.editor.layout();}"
        ))

    def _run_hs_code(self, code: str):
        """Парсит DSL (dsl_v1.py) и показывает окно внутри твоей ОС (насколько возможно)."""
        import os, sys, traceback, importlib.util

        # закрываем прошлый предпросмотр
        try:
            if self._hs_preview_window is not None:
                self._hs_preview_window.close()
        except Exception:
            pass
        self._hs_preview_window = None

        try:
            # ✅ добавляем системные пути (чтобы dsl_v1 импортнул init/styles из системы)
            base = os.getcwd()
            sys_paths = [
                os.path.join(base, "bin"),
                os.path.join(base, "bin", "sys", "class_", "win"),
                os.path.join(base, "bin", "sys", "class_", "win", "system_class"),
            ]
            for p in sys_paths:
                if p not in sys.path:
                    sys.path.insert(0, p)

            # ✅ HittiScript движок из системы: bin/sys/HittiScript/dsl_v1.py
            base = os.getcwd()  # корень PxStellarOs
            dsl_path = os.path.join(base, "bin", "sys", "HittiScript", "dsl_v1.py")
            if not os.path.exists(dsl_path):
                raise FileNotFoundError(f"Не найден HittiScript движок: {dsl_path}")


            spec = importlib.util.spec_from_file_location("stellar_dsl_v1", dsl_path)
            mod = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)

            app_spec, widget_specs, layout_cmds, actions = mod.parse_hs(code)
            win = mod.build_app(app_spec, widget_specs, layout_cmds, actions)

            # ✅ попытка “встроить” в твою ОС: делаем parent как у окна Vscode
            try:
                if hasattr(self, "parent_window") and self.parent_window is not None:
                    win.setParent(self.parent_window)
                    if hasattr(win, "parent_window"):
                        win.parent_window = self.parent_window
            except Exception:
                pass

            win.show()
            self._hs_preview_window = win

        except Exception:
            StellarMessageBox.warning(self, self.tr("DSL error"), traceback.format_exc())
