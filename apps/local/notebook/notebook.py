import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QPlainTextEdit, QFileDialog, QFontDialog, QFrame
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class NotebookWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="Notebook", translator=None, lang_code="en"):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name
        self.lang_code = lang_code
        self.current_file = None  # Добавляем инициализацию current_file
        
        # Set window properties
        self.setWindowTitle(self.tr("Notebook"))
        self.setGeometry(300, 150, 800, 600)

        # Використовуємо вже наявний layout або створюємо новий
        main_layout = self.layout()
        if not main_layout:
            main_layout = QVBoxLayout()
            self.setLayout(main_layout)

        self.toolbar = QHBoxLayout()

        # Кнопки
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self.new_file)

        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.open_file)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_file)

        self.add_title_widget(self.save_btn)
        self.add_title_widget(self.open_btn)
        self.add_title_widget(self.new_btn)
        main_layout.addLayout(self.toolbar)

        # Роздільник
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # Заменяем QTextEdit на кастомный
        self.text_edit = CustomTextEdit()
        self.content_layout.addWidget(self.text_edit)
        
        # Настройка скроллбаров (ваш существующий код)
        self.text_edit.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.text_edit.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
        """)

        # Статус-бар
        self.status_bar = QHBoxLayout()
        self.status_label = QLabel("    Ready")
        self.status_bar.addWidget(self.status_label)
        main_layout.addLayout(self.status_bar)

        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QPlainTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                padding: 10px;
                font-size: 14px;
            }
            QLabel {
                color: #555;
            }
        """)

        button_style = """
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: #2196F3;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """

        self.new_btn.setStyleSheet(button_style)
        self.open_btn.setStyleSheet(button_style)
        self.save_btn.setStyleSheet(button_style)

    def load_file(self, file_path):
        """Load a file into the notebook"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.text_edit.setText(f.read())
            self.current_file = file_path
        except Exception as e:
            print(f"Error loading file: {e}")

    def new_file(self):
        self.text_edit.clear()
        self.current_file = None
        self.status_label.setText("     New file created")

    def open_file(self):
        file_path, _ = CustomFileDialog.getOpenFileName(
            self, 
            self.tr("Open File"), 
            "", 
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.text_edit.setPlainText(f.read())
                self.current_file = file_path
                self.status_label.setText(f"    {self.tr('Opened')}: {os.path.basename(file_path)}")
            except Exception as e:
                self.status_label.setText(f"    {self.tr('Error')}: {str(e)}")

    def save_file(self):
        if not hasattr(self, 'current_file') or not self.current_file:
            file_path, _ = CustomFileDialog.getSaveFileName(
                self, 
                self.tr("Save File"), 
                "", 
                "Text Files (*.txt);;All Files (*)"
            )
            if not file_path:
                return
            self.current_file = file_path

        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            self.status_label.setText(f"    {self.tr('Saved')}: {os.path.basename(self.current_file)}")
        except Exception as e:
            self.status_label.setText(f"    {self.tr('Error')}: {str(e)}")