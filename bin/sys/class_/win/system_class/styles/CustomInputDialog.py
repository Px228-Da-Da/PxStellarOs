import os
import platform
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QLabel, QLineEdit, QFrame, QMenu,
    QInputDialog, QMessageBox, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor

class CustomInputDialog(QDialog):
    def __init__(self, parent=None, title="", label="", text=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("""
            QDialog {
                background-color: transparent;
            }
            QWidget#background {
                background-color: #2d2d2d;
                border: 2px solid #0078d7;
                border-radius: 12px;
            }
            QLabel {
                font-size: 14px;
                color: white;
                background-color: transparent;
            }
            QLineEdit {
                background-color: #3d3d3d;
                color: white;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 6px 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2899f5;
            }
            QPushButton:disabled {
                background-color: #555;
            }
            QDialogButtonBox {
                background-color: transparent;
            }
        """)
        
        # Создаем фоновый виджет для закругленных углов
        self.background_widget = QWidget(self)
        self.background_widget.setObjectName("background")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.background_widget)
        
        # Основной layout внутри фонового виджета
        layout = QVBoxLayout(self.background_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        self.line_edit = QLineEdit(text)
        layout.addWidget(self.line_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.line_edit.textChanged.connect(self.validate_input)
        self.validate_input(text)
        
        # Устанавливаем фиксированный размер для диалога
        self.setFixedSize(400, 160)
    
    def validate_input(self, text):
        button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        button.setEnabled(bool(text.strip()))
    
    def getText(parent=None, title="", label="", text=""):
        dialog = CustomInputDialog(parent, title, label, text)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return (dialog.line_edit.text(), True)
        return (text, False)