# Проверка зависимостей
def install_dependencies():
    import subprocess
    import sys
    required = ["PyQt6", "PyQt6-WebEngine", "pywifi"]
    for package in required:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

import subprocess
import sys
import json
import pywifi
from pywifi import const
import time
import os
import platform
import traceback
import datetime
import requests
import zipfile
import shutil

# Условные импорты для Windows
if platform.system() == "Windows":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
else:
    # Альтернативные импорты для Linux
    import pulsectl  # Для управления звуком


# PyQt6 импорты
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLabel, QMessageBox, QStackedWidget, QMenuBar, QToolBar, QLineEdit, QTabWidget, QMenu,
    QTextEdit, QCalendarWidget, QListWidget, QListWidgetItem, QProgressBar, QGridLayout, 
    QGraphicsDropShadowEffect, QSlider, QFileDialog, QInputDialog, QComboBox, QDialog
)

from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6.QtGui import (
    QIcon, QColor, QEnterEvent, QMouseEvent, QKeyEvent, QCursor, QPixmap,
    QPainter, QBrush, QFont, QAction, QGuiApplication
)

from PyQt6.QtCore import (
    Qt, QSize, QRect, QPropertyAnimation, QEasingCurve, QTimer,
    QTime, QDate, QUrl, QPoint, QProcess, pyqtProperty, QDateTime
)

from apps.local.init import DraggableResizableWindow

from apps.local.init import DraggableResizableWindow

from bin.sys.path.path_loader import setup_sys_path  # Инициализация путей


from TerminalApp import TerminalApp


from JumpingButton import JumpingButton


from DeathScreen import DeathScreen

from ToggleSwitch import ToggleSwitch
from Input import Input
from Button import Button

from CalendarWidget import CalendarWidget
from VolumeControlWidget import VolumeControlWidget
from WifiWindow import WifiWindow

from init import DraggableResizableWindow
from cmd_window import CmdWindow
from browser_window import BrowserWindow
from settings_window import SettingsWindow


from updater import UpdateDialog
from updater import get_current_version, get_latest_version, update_application, UPDATE_BRANCHES
from updater import *
