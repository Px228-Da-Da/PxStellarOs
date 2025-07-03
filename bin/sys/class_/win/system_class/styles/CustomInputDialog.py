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
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
            }
            QLabel {
                font-size: 14px;
                color: white;
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
        """)
        
        layout = QVBoxLayout(self)
        
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
    
    def validate_input(self, text):
        button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        button.setEnabled(bool(text.strip()))
    
    def getText(parent=None, title="", label="", text=""):
        dialog = CustomInputDialog(parent, title, label, text)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return (dialog.line_edit.text(), True)
        return (text, False)
