import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

from PyQt6.QtWidgets import QScrollBar
from PyQt6.QtCore import Qt

from CustomContextMenu import CustomContextMenu, ContextMenuMixin, CustomTextEdit, CustomPlainTextEdit, CustomLineEdit, CustomContextMenu_cmd, ContextMenuMixin_cmd, CustomTextEdit_cmd, CustomPlainTextEdit_cmd, CustomLineEdit_cmd
from PyQt6.QtCore import pyqtSignal


class CastScrollBar(QScrollBar):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                margin: 16px 0 16px 0;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #888;
                min-height: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #555;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
                height: 16px;
                subcontrol-origin: margin;
            }

            QScrollBar::add-line:vertical:hover,
            QScrollBar::sub-line:vertical:hover {
                background: #ccc;
            }

            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                width: 8px;
                height: 8px;
                background: transparent;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 12px;
                margin: 0 16px 0 16px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background: #888;
                min-width: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #555;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background: none;
                width: 16px;
                subcontrol-origin: margin;
            }

            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                width: 8px;
                height: 8px;
                background: transparent;
            }

            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)


class TerminalTab(QWidget, ContextMenuMixin):
    new_tab_requested = pyqtSignal()  # 🔥 сигнал оголошується тут, на рівні класу

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Поле вывода
        self.output = CustomTextEdit_cmd()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            background-color: #1e1e1e;  
            color: #dcdcdc;  
            font-family: Consolas, Monospace;
            font-size: 14px;
            border: none;
            padding: 5px;
        """)
        self.output.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.output.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))

        # Поле ввода
        self.input = CustomLineEdit()
        self.input.setStyleSheet("""
            background-color: #252526;
            color: #dcdcdc;
            font-family: Consolas, Monospace;
            font-size: 14px;
            border: 2px solid #3e3e3e;
            border-radius: 5px;
            padding: 5px;
        """)

        # Кнопка "➕" справа от поля ввода
        self.add_tab_button = QPushButton("➕")
        self.add_tab_button.setFixedSize(30, 30)
        self.add_tab_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 16px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #3399ff;
            }
            QPushButton:pressed {
                background-color: #0066cc;
            }
        """)
        self.add_tab_button.clicked.connect(self.new_tab_requested.emit)  # 🔥 теперь работает

        # Горизонтальный layout
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(5)
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.add_tab_button)

        self.input.returnPressed.connect(self.execute_command)

        self.layout.addWidget(self.output)
        self.layout.addLayout(input_layout)
        self.setLayout(self.layout)

        # Запуск терминала
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_output)
        if platform.system() == "Windows":
            self.process.start("cmd", ["/K"])
        else:
            if os.path.exists("/bin/bash"):
                self.process.start("/bin/bash")
            else:
                self.process.start("/bin/sh")


  # Оставляем процесс открытым

    def execute_command(self):
        command = self.input.text()
        if command.strip():
            self.output.append(f"> {command}")  # Показываем введённую команду
            self.process.write((command + "\n").encode("utf-8"))  # Отправляем в терминал
            self.input.clear()

    def read_output(self):
        if platform.system() == "Windows":
            output = self.process.readAllStandardOutput().data().decode("cp866", errors="ignore").strip()
        else:
            output = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore").strip()

        if output:
            self.output.append(output)  # Показываем результат выполнения

class TerminalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Win11 Terminal")
        self.resize(800, 600)

        # Основной виджет (верхний контейнер)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Главный вертикальный layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Вкладки терминала
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)  # Возможность закрывать вкладки
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.main_layout.addWidget(self.tabs)

        # Стилизация
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d30;
            }
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

        self.add_new_tab()  # Создаём первую вкладку

    def add_new_tab(self):
        """Добавляет новую вкладку с терминалом"""
        new_tab = TerminalTab()
        new_tab.new_tab_requested.connect(self.add_new_tab)  # подписка на сигнал 🔥
        index = self.tabs.addTab(new_tab, f"cmd {self.tabs.count() + 1}")
        self.tabs.setCurrentIndex(index)


    def close_tab(self, index):
        """Закрывает вкладку"""
        if self.tabs.count() > 1:  # Минимум 1 вкладка должна оставаться
            widget = self.tabs.widget(index)
            widget.deleteLater()  # Удаляем объект
            self.tabs.removeTab(index)