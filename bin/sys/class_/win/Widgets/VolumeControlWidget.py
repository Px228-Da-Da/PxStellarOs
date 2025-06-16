import os
import sys
import json
import time
import platform
import subprocess

import pywifi
from pywifi import const


# Условные импорты для Windows
if platform.system() == "Windows":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
else:
    # Альтернативные импорты для Linux
    import pulsectl  # Для управления звуком


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


class VolumeControlWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.volume = None  # Инициализируем как None
        self.init_audio()
        self.init_ui()

    def init_audio(self):
        """Инициализация аудио-интерфейса с обработкой ошибок"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, 
                CLSCTX_ALL, 
                None
            )
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            print(f"Audio initialization error: {e}")
            self.volume = None

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Громкость")
        self.resize(350, 100)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.9);
                color: white;
                border-radius: 8px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 6px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #4bcfff;
                border: 1px solid #5c5c5c;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #4bcfff;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.title_label = QLabel("Громкость")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.valueChanged.connect(self.set_system_volume)
        main_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("100%")
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.volume_label)

        self.update_volume()

    def update_volume(self):
        """Обновляет ползунок текущей громкостью"""
        try:
            if self.volume:
                current_volume = self.volume.GetMasterVolumeLevelScalar()
                volume_percent = int(current_volume * 100)
                self.volume_slider.setValue(volume_percent)
                self.volume_label.setText(f"{volume_percent}%")
        except Exception as e:
            print(f"Volume update error: {e}")

    def set_system_volume(self, value):
        """Устанавливает системную громкость"""
        try:
            if self.volume:
                volume_level = value / 100.0
                self.volume.SetMasterVolumeLevelScalar(volume_level, None)
                self.volume_label.setText(f"{value}%")
        except Exception as e:
            print(f"Volume set error: {e}")

    def closeEvent(self, event):
        """Очистка ресурсов при закрытии главного окна"""
        if hasattr(self, 'volume_widget') and self.volume_widget:
            self.volume_widget.close()
        super().closeEvent(event)

    def __del__(self):
        """Деструктор для дополнительной очистки"""
        if self.volume:
            self.volume.Release()
            self.volume = None
