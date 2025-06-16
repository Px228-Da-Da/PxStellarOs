import os
import sys
import json
import time
import platform
import subprocess

import pywifi
from pywifi import const

from PyQt6.QtCore import (
    Qt, QSize, QRect, QPoint, QUrl,
    QTimer, QTime, QDate, QProcess,
    QPropertyAnimation, QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import (
    QIcon, QColor, QPixmap, QCursor,
    QMouseEvent, QEnterEvent, QKeyEvent,
    QPainter, QBrush, QFont, QAction
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QStackedWidget, QMenuBar, QToolBar,
    QLineEdit, QTabWidget, QMenu, QSlider,
    QInputDialog, QListWidget, QListWidgetItem,
    QCalendarWidget, QTextEdit, QProgressBar,
    QGraphicsDropShadowEffect, QGridLayout
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class DeathScreen(QWidget):
    def __init__(self, parent=None, error_message="Unknown error"):
        super().__init__(parent)
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setStyleSheet("background-color: black; color: white;")
        
        # Основной лэйаут
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Сообщение об ошибке
        self.error_label = QLabel(f"Your OS ran into a problem and needs to restart.\n\nError: {error_message}")
        self.error_label.setFont(QFont("Arial", 16))
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)
        
        # Кнопка для перезагрузки
        self.reboot_button = QPushButton("Reboot Now")
        self.reboot_button.setFont(QFont("Arial", 14))
        self.reboot_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005BB5;
            }
        """)
        self.reboot_button.clicked.connect(self.reboot_system)
        layout.addWidget(self.reboot_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        
        # Анимация появления экрана смерти
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(1000)
        self.animation.setStartValue(QRect(0, -self.height(), self.width(), self.height()))
        self.animation.setEndValue(QRect(0, 0, self.width(), self.height()))
        self.animation.start()
    
    def reboot_system(self):
        """Перезагружает систему."""
        system_platform = platform.system()
        if system_platform == "Windows":
            # Команда для перезагрузки Windows
            QProcess.startDetached("shutdown", ["/r", "/t", "0"])
        elif system_platform == "Linux":
            # Команда для перезагрузки Linux
            QProcess.startDetached("reboot")
        else:
            print(f"Unsupported platform: {system_platform}")

