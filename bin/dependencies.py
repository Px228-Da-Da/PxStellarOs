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
    QApplication, QScrollArea, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLabel, QMessageBox, QStackedWidget, QMenuBar, QToolBar, QLineEdit, QTabWidget, QMenu,
    QTextEdit, QCalendarWidget, QListWidget, QListWidgetItem, QProgressBar, QGridLayout, 
    QGraphicsDropShadowEffect, QSlider, QFileDialog, QInputDialog, QComboBox, QDialog, QGroupBox, QCheckBox
)

from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6.QtGui import (
    QIcon, QColor, QEnterEvent, QMouseEvent, QKeyEvent, QCursor, QPixmap,
    QPainter, QBrush, QFont, QAction, QGuiApplication
)

from PyQt6.QtCore import (
    Qt, QSize, QRect, QEvent, QPropertyAnimation, QEasingCurve, QTimer,
    QTime, QDate, QUrl, QPoint, QProcess, pyqtProperty, QDateTime, QParallelAnimationGroup
)

from bin.sys.class_.win.init import DraggableResizableWindow


from bin.sys.path.path_loader import setup_sys_path  # Инициализация путей


from TerminalApp import TerminalApp


from JumpingButton import JumpingButton


from DeathScreen import DeathScreen

from ToggleSwitch import ToggleSwitch
from Input import Input
from InputPassword import InputPassword
from Button import Button
from StellarMessageBox import StellarMessageBox
from ScrollBar import CastScrollBar
from Menu import CustomMenu
from CustomInputDialog import CustomInputDialog



from CalendarWidget import CalendarWidget
from VolumeControlWidget import VolumeControlWidget
from WifiWindow import WifiWindow
from LinuxStartMenu import LinuxStartMenu


def get_local_apps_list():
    """Возвращает список приложений из папки apps/local"""
    apps_dir = os.path.join("apps", "local")
    apps = []
    
    if not os.path.exists(apps_dir):
        print(f"Папка {apps_dir} не найдена!")
        return apps
    
    for app_name in os.listdir(apps_dir):
        app_path = os.path.join(apps_dir, app_name)
        if os.path.isdir(app_path):
            # Проверяем наличие основного файла приложения (например, app_name.py)
            main_file = os.path.join(app_path, f"{app_name}.py")
            if os.path.exists(main_file):
                apps.append(app_name)
    
    print("Найденные приложения:", apps)
    return apps

# get_local_apps_list()

# from cmd_window import CmdWindow
# from browser_window import BrowserWindow
# from settings_window import SettingsWindow


from updater import UpdateDialog
from updater import get_current_version, get_latest_version, update_application, UPDATE_BRANCHES
from updater import *
