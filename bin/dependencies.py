# === Проверка и установка зависимостей ===

def install_dependencies():
    """
    Проверяет и при необходимости устанавливает все зависимости для ОС.
    """
    import subprocess
    import sys
    import platform
    import time

    print("[CHECK] Проверка установленных библиотек...\n")
    sys.stdout.flush()
    time.sleep(0.5)

    base_packages = [
        "PyQt6",
        "PyQt6-WebEngine",
        "requests",
        "pywifi",
        "pillow",
        "pycaw",
        "comtypes",
        "psutil"
    ]

    linux_packages = ["pulsectl"]

    required_packages = base_packages.copy()
    if platform.system() == "Linux":
        required_packages += linux_packages

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"[YES] {package} уже установлено.")
            sys.stdout.flush()
            time.sleep(0.3)
        except ImportError:
            print(f"[INSTALL] Устанавливаю {package} ...")
            sys.stdout.flush()
            time.sleep(0.5)
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"[YES] {package} установлено успешно!\n")
                sys.stdout.flush()
                time.sleep(0.4)
            except Exception as e:
                print(f"[ERROR] Не удалось установить {package}: {e}\n")
                sys.stdout.flush()
                time.sleep(0.8)

    print("\n[YES] Проверка зависимостей завершена.\n")


import sys, os
os.system("chcp 65001 >nul")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


install_dependencies()

# | Символ  | Заміна      |
# | ------  | ----------- |
# | 🔍      | `[CHECK]`   |
# | ⬇       | `[INSTALL] ` |
# | ✅      | `[OK]`      |
# | ❌      | `[ERROR]`   |


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
import psutil
import hmac

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
    QLabel, QMessageBox, QStackedWidget, QMenuBar, QToolBar, QLineEdit, QTabWidget, QMenu, QPlainTextEdit,
    QTextEdit, QCalendarWidget, QListWidget, QListWidgetItem, QProgressBar, QGridLayout, 
    QGraphicsDropShadowEffect, QSlider, QFileDialog, QInputDialog, QComboBox, QDialog, QGroupBox, QCheckBox, QSpinBox, QSizePolicy, QFormLayout
)

from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6.QtGui import (
    QIcon, QColor, QEnterEvent, QMouseEvent, QKeyEvent, QCursor, QPixmap,
    QPainter, QBrush, QFont, QAction, QGuiApplication,
    QPainter, QBrush, QLinearGradient, QDrag, QPalette, QLinearGradient
)

from PyQt6.QtCore import (
    Qt, QSize, QRect, QEvent, QPropertyAnimation, QEasingCurve, QTimer,
    QTime, QDate, QUrl, QPoint, QProcess, pyqtProperty, QDateTime, QParallelAnimationGroup,
    QRectF, QMimeData
)

# from PyQt6.QtGui import QColor, 
# from PyQt6.QtCore import 



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
from Menu import Menu
from CustomInputDialog import CustomInputDialog
from CustomContextMenu import CustomContextMenu, ContextMenuMixin, CustomTextEdit, CustomPlainTextEdit, CustomLineEdit, CustomContextMenu_cmd, ContextMenuMixin_cmd, CustomTextEdit_cmd, CustomPlainTextEdit_cmd, CustomLineEdit_cmd
from FileListContextMenu import FileListContextMenu
from CustomFileDialog import CustomFileDialog
from ComboBox import ComboBox


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
