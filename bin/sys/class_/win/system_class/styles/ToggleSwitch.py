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


class ToggleSwitch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self._checked = True
        self._circle_position = self.width() - self.height() + 2

        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setDuration(200)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        if self._checked:
            self.animation.setEndValue(self.width() - self.height() + 2)
        else:
            self.animation.setEndValue(2)
        self.animation.start()
        self.update()
        self.parent().toggle_wifi(self._checked)

    def paintEvent(self, event):
        radius = self.height() // 2
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._checked:
            painter.setBrush(QColor(0, 122, 255))
        else:
            painter.setBrush(QColor(180, 180, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), radius, radius)

        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawEllipse(QRect(int(self._circle_position), 2, self.height() - 4, self.height() - 4))

    def sizeHint(self):
        return QSize(60, 30)

    def isChecked(self):
        return self._checked

    def setChecked(self, state: bool):
        self._checked = state
        self._circle_position = self.width() - self.height() + 2 if state else 2
        self.update()

    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, pos):
        self._circle_position = pos
        self.update()

    circle_position = pyqtProperty(float, fget=get_circle_position, fset=set_circle_position)
