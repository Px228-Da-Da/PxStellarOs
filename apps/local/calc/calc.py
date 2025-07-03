from PyQt6.QtWidgets import QGridLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class CalcWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="Calculator", translator=None, lang_code="en"):
        super().__init__(parent, window_name)  # Передаем оба аргумента в родительский класс
        self.setFixedSize(300, 400)
        self.init_ui()
        self.lang_code = lang_code
        
    def init_ui(self):
        # Создаем поле для вывода
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                padding: 10px;
                font-size: 24px;
                color: #212529;
            }
        """)
        self.display.setFont(QFont("Arial", 24))
        
        # Создаем кнопки
        buttons = [
            ('7', (0, 0)), ('8', (0, 1)), ('9', (0, 2)), ('/', (0, 3)), ('C', (0, 4)),
            ('4', (1, 0)), ('5', (1, 1)), ('6', (1, 2)), ('*', (1, 3)), ('⌫', (1, 4)),
            ('1', (2, 0)), ('2', (2, 1)), ('3', (2, 2)), ('-', (2, 3)), ('%', (2, 4)),
            ('0', (3, 0)), ('.', (3, 1)), ('=', (3, 2)), ('+', (3, 3)), ('±', (3, 4))
        ]
        
        # Создаем layout для кнопок
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Добавляем поле вывода
        grid_layout.addWidget(self.display, 0, 0, 1, 5)
        
        # Создаем и добавляем кнопки
        for text, pos in buttons:
            button = QPushButton(text)
            button.setFixedSize(50, 50)
            button.clicked.connect(self.on_button_click)
            
            # Стилизация кнопок
            if text in ['=', '+', '-', '*', '/']:
                # Оранжевые кнопки операций (как в macOS)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #ff9500;
                        color: white;
                        border-radius: 25px;
                        font-size: 18px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #ffaa33;
                    }
                    QPushButton:pressed {
                        background-color: #cc7700;
                    }
                """)
            elif text in ['C', '⌫', '%', '±']:
                # Серые кнопки функций (как в macOS)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #a5a5a5;
                        color: black;
                        border-radius: 25px;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        background-color: #b5b5b5;
                    }
                    QPushButton:pressed {
                        background-color: #858585;
                    }
                """)
            else:
                # Темно-серые цифровые кнопки (как в Windows 11)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #333333;
                        color: white;
                        border-radius: 25px;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        background-color: #444444;
                    }
                    QPushButton:pressed {
                        background-color: #222222;
                    }
                """)
            
            grid_layout.addWidget(button, pos[0]+1, pos[1])
        
        # Устанавливаем layout в content_area
        self.content_layout.addLayout(grid_layout)
        
        # Инициализируем переменные калькулятора
        self.current_input = ""
        self.previous_input = ""
        self.operation = None
        self.reset_input = False
        
    def on_button_click(self):
        sender = self.sender()
        text = sender.text()
        
        if text in '0123456789':
            if self.reset_input:
                self.current_input = ""
                self.reset_input = False
            self.current_input += text
            self.display.setText(self.current_input)
            
        elif text == '.':
            if self.reset_input:
                self.current_input = "0"
                self.reset_input = False
            if '.' not in self.current_input:
                self.current_input += '.'
                self.display.setText(self.current_input)
                
        elif text in ['+', '-', '*', '/']:
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
            self.display.setText("0")
            
        elif text == '⌫':
            if self.current_input:
                self.current_input = self.current_input[:-1]
                if not self.current_input:
                    self.current_input = "0"
                self.display.setText(self.current_input)
                
        elif text == '%':
            if self.current_input:
                self.current_input = str(float(self.current_input) / 100)
                self.display.setText(self.current_input)
                
        elif text == '±':
            if self.current_input:
                self.current_input = str(-float(self.current_input))
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
            self.display.setText(self.current_input)
            self.previous_input = self.current_input
            self.reset_input = True
            
        except:
            self.display.setText("Error")
            self.current_input = ""
            self.previous_input = ""
            self.operation = None