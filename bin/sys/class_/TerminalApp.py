from PyQt6.QtCore import QTimer, QTime, QDate
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QFrame, QLabel, QMessageBox, QStackedWidget, QMenuBar, QToolBar, QLineEdit,QTabWidget, QMenu
)
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt, QSize, QUrl, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QMouseEvent, QColor, QPainter, QBrush, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
from PyQt6.QtGui import QAction

from PyQt6.QtCore import QTimer, QTime, QDate
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import QLabel, QMenuBar

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import QProcess


import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import QProcess

class TerminalTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Поле вывода
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            background-color: #1e1e1e;  
            color: #dcdcdc;  
            font-family: Consolas, Monospace;
            font-size: 14px;
            border: none;
            padding: 5px;
        """)

        # Поле ввода
        self.input = QLineEdit()
        self.input.setStyleSheet("""
            background-color: #252526;
            color: #dcdcdc;
            font-family: Consolas, Monospace;
            font-size: 14px;
            border: 2px solid #3e3e3e;
            border-radius: 5px;
            padding: 5px;
        """)

        self.input.returnPressed.connect(self.execute_command)

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)

        # Запуск терминала (отдельный процесс для каждой вкладки)
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)  # Объединение stdout и stderr
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_output)
        self.process.start("cmd", ["/K"])  # Оставляем процесс открытым

    def execute_command(self):
        command = self.input.text()
        if command.strip():
            self.output.append(f"> {command}")  # Показываем введённую команду
            self.process.write((command + "\n").encode("utf-8"))  # Отправляем в терминал
            self.input.clear()

    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode("cp866", errors="ignore").strip()
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

        # Верхняя панель с кнопкой
        self.top_bar = QHBoxLayout()
        self.main_layout.addLayout(self.top_bar)

        # Кнопка "Создать вкладку"
        self.add_tab_button = QPushButton("➕")
        self.add_tab_button.setStyleSheet("""
            background-color: #0078d7;
            color: white;
            font-size: 16px;
            border-radius: 10px;
            padding: 5px;
            margin: 3px;
        """)
        self.add_tab_button.clicked.connect(self.add_new_tab)
        self.top_bar.addWidget(self.add_tab_button)

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
        index = self.tabs.addTab(new_tab, f"Tab {self.tabs.count() + 1}")
        self.tabs.setCurrentIndex(index)  # Переключаемся на новую вкладку

    def close_tab(self, index):
        """Закрывает вкладку"""
        if self.tabs.count() > 1:  # Минимум 1 вкладка должна оставаться
            widget = self.tabs.widget(index)
            widget.deleteLater()  # Удаляем объект
            self.tabs.removeTab(index)