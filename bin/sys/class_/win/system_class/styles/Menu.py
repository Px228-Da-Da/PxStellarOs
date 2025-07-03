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

class CustomMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #444;
                color: white;
            }
            QMenu::item {
                padding: 5px 25px 5px 20px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #0078d7;
            }
            QMenu::separator {
                height: 1px;
                background-color: #444;
                margin: 2px 0;
            }
        """)