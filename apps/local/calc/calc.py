from PyQt6.QtWidgets import QGridLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

from PyQt6.QtWidgets import QGridLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont

from PyQt6.QtWidgets import QGridLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont

class CalcWindow(DraggableResizableWindow):
    # def __init__(self, parent=None, window_name="", translator=None, lang_code="en"):
    #     super().__init__(parent)
    def __init__(self, parent=None, window_name="Calculator", translator=None, lang_code="en", enable_maximize=False):
        super().__init__(parent, window_name, enable_maximize=False)
        self.setFixedSize(320, 450)
        self.tr = translator if translator else lambda x: x
        self.parent_window = parent
        self.lang_code = lang_code
        self.init_ui()
        self.current_input = ""
        self.previous_input = ""
        self.operation = None
        self.reset_input = False

        # Делаем поле ввода активным сразу
        self.display.setFocus()

    def init_ui(self):
        # Поле для ввода
        self.display = Input(
            parent=self,
            translator=self.tr,
            lang_code=self.lang_code
        )
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFont(QFont("Segoe UI", 24))
        self.display.setText("0")
        self.display.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                padding: 10px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #0a84ff;
            }
        """)
        self.display.installEventFilter(self)  # ловим клавиши
        self.content_layout.addWidget(self.display)

        # Кнопки
        buttons = [
            ('7', (0, 0)), ('8', (0, 1)), ('9', (0, 2)), ('/', (0, 3)), ('C', (0, 4)),
            ('4', (1, 0)), ('5', (1, 1)), ('6', (1, 2)), ('*', (1, 3)), ('⌫', (1, 4)),
            ('1', (2, 0)), ('2', (2, 1)), ('3', (2, 2)), ('-', (2, 3)), ('%', (2, 4)),
            ('0', (3, 0)), ('.', (3, 1)), ('=', (3, 2)), ('+', (3, 3)), ('±', (3, 4))
        ]

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.addWidget(self.display, 0, 0, 1, 5)

        for text, pos in buttons:
            button = QPushButton(text)
            button.setFixedSize(50, 50)
            button.setFont(QFont("Segoe UI", 16))
            button.clicked.connect(self.on_button_click)

            # Стилізація кнопок для темного дизайну
            if text in '+-*/=':
                # Яскраві кнопки операцій
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #0a84ff;
                        color: #ffffff;
                        border-radius: 15px;
                    }
                    QPushButton:hover {
                        background-color: #3399ff;
                    }
                    QPushButton:pressed {
                        background-color: #0066cc;
                    }
                """)
            elif text in ['C', '⌫', '%', '±']:
                # Темно-сірі кнопки функцій
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a3a;
                        color: #ffffff;
                        border-radius: 15px;
                    }
                    QPushButton:hover {
                        background-color: #505050;
                    }
                    QPushButton:pressed {
                        background-color: #1f1f1f;
                    }
                """)
            else:
                # Темні цифрові кнопки
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2b2b2b;
                        color: #ffffff;
                        border-radius: 15px;
                    }
                    QPushButton:hover {
                        background-color: #3c3c3c;
                    }
                    QPushButton:pressed {
                        background-color: #1f1f1f;
                    }
                """)

            grid_layout.addWidget(button, pos[0]+1, pos[1])

        self.content_layout.addLayout(grid_layout)

    def on_button_click(self):
        sender = self.sender()
        self.handle_input(sender.text())

    def handle_input(self, text):
        if text in '0123456789':
            if self.reset_input:
                self.current_input = ""
                self.reset_input = False
            if self.current_input == "0":
                self.current_input = text
            else:
                self.current_input += text

        elif text == '.':
            if self.reset_input:
                self.current_input = "0"
                self.reset_input = False
            if '.' not in self.current_input:
                self.current_input += '.'

        elif text in '+-*/':
            if self.current_input and self.previous_input and not self.reset_input:
                self.calculate()
            self.operation = text
            self.previous_input = self.current_input
            self.reset_input = True

        elif text == '=':
            if self.current_input and self.previous_input:
                self.calculate()
                self.operation = None
                self.reset_input = True

        elif text == 'C':
            self.current_input = ""
            self.previous_input = ""
            self.operation = None

        elif text == '⌫':
            self.current_input = self.current_input[:-1]
            if not self.current_input:
                self.current_input = "0"

        elif text == '%':
            try:
                self.current_input = str(float(self.current_input) / 100)
            except:
                self.current_input = "0"

        elif text == '±':
            try:
                if not self.current_input or self.current_input == ".":
                    self.current_input = "0"
                self.current_input = str(-float(self.current_input))
            except:
                self.current_input = "0"

        self.display.setText(self.current_input)

    def calculate(self):
        try:
            num1 = float(self.previous_input)
            num2 = float(self.current_input)
            if self.operation == '+':
                result = num1 + num2
            elif self.operation == '-':
                result = num1 - num2
            elif self.operation == '*':
                result = num1 * num2
            elif self.operation == '/':
                result = num1 / num2 if num2 != 0 else "Error"
            self.current_input = str(result)
            self.previous_input = self.current_input
            self.reset_input = True
        except:
            self.current_input = "0"
        self.display.setText(self.current_input)

    def eventFilter(self, source, event):
        # Ввод с клавиатуры
        if source == self.display and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
                self.handle_input(str(key - Qt.Key.Key_0))
                return True
            elif key == Qt.Key.Key_Period:
                self.handle_input('.')
                return True
            elif key == Qt.Key.Key_Backspace:
                self.handle_input('⌫')
                return True
            elif key == Qt.Key.Key_Plus:
                self.handle_input('+')
                return True
            elif key == Qt.Key.Key_Minus:
                self.handle_input('-')
                return True
            elif key == Qt.Key.Key_Asterisk:
                self.handle_input('*')
                return True
            elif key == Qt.Key.Key_Slash:
                self.handle_input('/')
                return True
            elif key in [Qt.Key.Key_Enter, Qt.Key.Key_Return]:
                self.handle_input('=')
                return True
        return super().eventFilter(source, event)
