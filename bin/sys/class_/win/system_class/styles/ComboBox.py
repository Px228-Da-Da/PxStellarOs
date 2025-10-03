from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen
from PyQt6.QtCore import Qt, QRect, QSize

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt

class ComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QComboBox {
                background-color: #2E2E2E;
                color: #E0E0E0;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 5px 20px 5px 10px;
                min-height: 28px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #555555;
                border-left-style: solid;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow-light.png); /* можно заменить на свой svg */
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2E2E2E;
                color: #E0E0E0;
                border: 1px solid #555555;
                selection-background-color: #4C8ED9;
                selection-color: white;
                padding: 5px;
                outline: none;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
