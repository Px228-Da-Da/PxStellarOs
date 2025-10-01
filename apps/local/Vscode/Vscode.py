from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt

from PyQt6.QtWidgets import QTabBar

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent, browser_window):
        super().__init__(profile, parent)
        self.browser_window = browser_window

    # Перехватываем window.open()
    def createWindow(self, web_window_type):
        return self.browser_window.create_new_tab_from_page(web_window_type)


class VscodeWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="Vs Code", translator=None, lang_code="en"):
        super().__init__(parent)
        self.window_name = window_name
        self.lang_code = lang_code
        self.current_file = None
        self.open_files = {}  # словарь file_path -> вкладка

        self.setWindowTitle(self.tr("VSCode (Monaco)"))
        self.setGeometry(300, 150, 1000, 700)

        # Центральный контейнер
        self.container = QWidget(self)
        self.set_content(self.container)
        layout = QVBoxLayout(self.container)
        self.container.setLayout(layout)

        # === Панель инструментов ===
        toolbar_layout = QHBoxLayout()
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

        # === Таб файлов ===
        self.tab_bar = QTabBar()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.switch_tab)
        toolbar_layout.addWidget(self.tab_bar)
        layout.addLayout(toolbar_layout)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # === Monaco Editor ===
        self.browser = QWebEngineView()
        html_path = os.path.abspath(os.path.join("apps", "local", "Vscode", "monaco", "index.html"))
        if not os.path.exists(html_path):
            print("❌ Не найден index.html:", html_path)
        else:
            print("✅ Загружаем Monaco:", html_path)

        self.browser.setUrl(QUrl.fromLocalFile(html_path))
        layout.addWidget(self.browser)

        # === Статус-бар ===
        self.status_label = QLabel("    Ready")

        # Настраиваем профиль
        self.profile = QWebEngineProfile("SublimeProfile", self)
        browser_data_path = os.path.join(os.getcwd(), "root", "dataLacmi", "browser")
        os.makedirs(browser_data_path, exist_ok=True)
        self.profile.setPersistentStoragePath(os.path.join(browser_data_path, "web_profile"))
        self.profile.setCachePath(os.path.join(browser_data_path, "web_cache"))

        self.tab_bar.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #2d2d30;
            }
            QTabBar::tab {
                background: #3e3e42;
                color: #ffffff;
                padding: 8px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #0078d7;
                color: #ffffff;
            }
        """)

    # === Определяем язык Monaco по расширению ===
    def detect_language(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".json": "json",
            ".html": "html",
            ".css": "css",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "cpp",
            ".hpp": "cpp",
            ".java": "java",
            ".txt": "plaintext",
            ".md": "markdown",
        }
        return mapping.get(ext, "plaintext")

    # === Взаимодействие с Monaco ===
    def set_text(self, text: str, language: str = "plaintext"):
        js = f"""
        (function waitForEditor() {{
            if (window.editor) {{
                var model = window.editor.getModel();
                if (!model) {{
                    model = monaco.editor.createModel({repr(text)}, {repr(language)});
                    window.editor.setModel(model);
                }} else {{
                    window.editor.setValue({repr(text)});
                    monaco.editor.setModelLanguage(model, {repr(language)});
                }}
            }} else {{
                setTimeout(waitForEditor, 50);
            }}
        }})();
        """
        self.browser.page().runJavaScript(js)


    def get_text(self, callback):
        """Получить текст из Monaco Editor после полной инициализации"""
        js = """
        (function waitForEditor() {
            if (window.editor) {
                return window.editor.getValue();
            } else {
                setTimeout(waitForEditor, 50);
            }
        })();
        """
        self.browser.page().runJavaScript(js, callback)


    # === Кнопки ===
    def new_file(self):
        self.set_text("", "plaintext")
        self.current_file = None
        self.status_label.setText("    New file created")

    def open_file(self):
        file_path, _ = CustomFileDialog.getOpenFileName(
            self,
            self.tr("Open File"),
            "",
            "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js);;HTML (*.html);;CSS (*.css);;JSON (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            language = self.detect_language(file_path)
            self.set_text(content, language)
            self.current_file = file_path

            # --- Добавляем вкладку в tab_bar ---
            if file_path not in self.open_files:
                index = self.tab_bar.addTab(os.path.basename(file_path))
                self.open_files[file_path] = index
                self.tab_bar.setCurrentIndex(index)
            else:
                # если файл уже открыт, переключаемся на его вкладку
                self.tab_bar.setCurrentIndex(self.open_files[file_path])

            self.status_label.setText(f"    Opened: {os.path.basename(file_path)} [{language}]")
        except Exception as e:
            self.status_label.setText(f"    Error: {e}")


    def save_file(self):
        """Сохраняем текст из Monaco в файл"""
        def handle_code(code):
            if not self.current_file:
                file_path, _ = CustomFileDialog.getSaveFileName(
                    self,
                    self.tr("Save File"),
                    "",
                    "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js)"
                )
                if not file_path:
                    return
                self.current_file = file_path

            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(code)
                self.status_label.setText(f"    Saved: {os.path.basename(self.current_file)}")
            except Exception as e:
                self.status_label.setText(f"    Error: {e}")

        self.get_text(handle_code)

    # Для window.open()
    def create_new_tab_from_page(self, window_type=None):
        new_browser = QWebEngineView()
        new_page = CustomWebEnginePage(self.profile, new_browser, self)
        new_browser.setPage(new_page)
        self.container.layout().addWidget(new_browser)
        return new_page

    def close_tab(self, index):
        file_to_close = None
        for file_path, tab_index in self.open_files.items():
            if tab_index == index:
                file_to_close = file_path
                break
        if file_to_close:
            self.tab_bar.removeTab(index)
            del self.open_files[file_to_close]
            if self.current_file == file_to_close:
                self.current_file = None
                if self.open_files:
                    # переключаем на первый открытый файл
                    first_file = list(self.open_files.keys())[0]
                    self.open_file_by_path(first_file)

    def switch_tab(self, index):
        for file_path, tab_index in self.open_files.items():
            if tab_index == index:
                self.open_file_by_path(file_path)
                break

    def open_file_by_path(self, file_path):
        if not os.path.exists(file_path):
            return

        self.current_file = file_path

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            language = self.detect_language(file_path)

            # Ждём, пока браузер полностью загрузит страницу
            def try_set_text():
                js_check_editor = "typeof window.editor !== 'undefined';"
                def callback(result):
                    if result:
                        # Если редактор готов, устанавливаем текст
                        self.set_text(content, language)
                        self.status_label.setText(f"    Opened: {os.path.basename(file_path)} [{language}]")
                        # Добавляем вкладку в tab_bar
                        if file_path not in self.open_files:
                            index = self.tab_bar.addTab(os.path.basename(file_path))
                            self.open_files[file_path] = index
                            self.tab_bar.setCurrentIndex(index)
                        else:
                            self.tab_bar.setCurrentIndex(self.open_files[file_path])
                    else:
                        # Если не готов, повторяем через 50мс
                        QTimer.singleShot(50, try_set_text)
                self.browser.page().runJavaScript(js_check_editor, callback)

            from PyQt6.QtCore import QTimer
            try_set_text()

        except Exception as e:
            self.status_label.setText(f"    Error: {e}")
