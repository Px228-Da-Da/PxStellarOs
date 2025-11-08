def ensure_console_dependencies():
    """
    Проверяет наличие библиотек, необходимых для работы ConsoleScreen (PyQt6),
    и автоматически устанавливает их при отсутствии.
    """
    import importlib.util
    import subprocess
    import sys
    import time

    required = ["PyQt6"]

    print("🔍 Проверка библиотек, необходимых для запуска ConsoleScreen...\n")
    time.sleep(0.8)

    for package in required:
        if importlib.util.find_spec(package) is None:
            print(f"⬇ Не найдена {package}, выполняю установку...")
            time.sleep(0.7)
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} установлена успешно!")
                time.sleep(0.5)
            except Exception as e:
                print(f"❌ Ошибка при установке {package}: {e}")
                time.sleep(3)
                sys.exit(1)
        else:
            print(f"✅ {package} уже установлена.")
            time.sleep(0.4)

    print("✅ Все зависимости для ConsoleScreen готовы.\n")
    time.sleep(1.2)

ensure_console_dependencies()

from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
import sys, ctypes, traceback

class ConsoleScreen(QWidget):
    """Повноекранний чорний екран для показу системних логів і помилок."""
    instance = None

    def __init__(self):
        super().__init__()
        ConsoleScreen.instance = self  # глобальна ссилка
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("""
            background-color: black;
            color: white;
            font-family: Consolas;
            font-size: 14px;
        """)

        layout = QVBoxLayout(self)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: black; color: white; border: none;")
        layout.addWidget(self.console)

        # Перенаправляємо stdout/stderr
        sys.stdout = self
        sys.stderr = self

        # Ховаємо консоль Windows (cmd)
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except Exception:
            pass

    def write(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console.setTextCursor(cursor)
        self.console.insertPlainText(text)
        self.console.moveCursor(QTextCursor.MoveOperation.End)
        self.console.ensureCursorVisible()
        self.console.repaint()
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()  # ✅ обновление GUI в реальном времени


    def flush(self):
        pass

    @staticmethod
    def show_error(message: str):
        """Показує помилку на екрані, навіть якщо ОС не завантажилась."""
        if ConsoleScreen.instance:
            ConsoleScreen.instance.write(f"\n❌ CRITICAL ERROR:\n{message}\n")
        else:
            # fallback у випадку, якщо екран ще не створено
            print(f"\n❌ CRITICAL ERROR:\n{message}\n")

# === Проверка и установка зависимостей ===
# def install_dependencies():
#     """
#     Проверяет и при необходимости устанавливает все зависимости для ОС.
#     """
#     import subprocess
#     import sys
#     import platform
#     import time

#     print("🔍 Проверка установленных библиотек...\n")
#     sys.stdout.flush()
#     time.sleep(0.5)

#     base_packages = [
#         "PyQt6",
#         "PyQt6-WebEngine",
#         "requests",
#         "pywifi",
#         "pillow",
#         "pycaw",
#         "comtypes",
#         "psutil"
#     ]

#     linux_packages = ["pulsectl"]

#     required_packages = base_packages.copy()
#     if platform.system() == "Linux":
#         required_packages += linux_packages

#     for package in required_packages:
#         try:
#             __import__(package.replace("-", "_"))
#             print(f"✅ {package} уже установлено.")
#             sys.stdout.flush()
#             time.sleep(0.3)
#         except ImportError:
#             print(f"⬇ Устанавливаю {package} ...")
#             sys.stdout.flush()
#             time.sleep(0.5)
#             try:
#                 subprocess.check_call([sys.executable, "-m", "pip", "install", package])
#                 print(f"✅ {package} установлено успешно!\n")
#                 sys.stdout.flush()
#                 time.sleep(0.4)
#             except Exception as e:
#                 print(f"❌ Не удалось установить {package}: {e}\n")
#                 sys.stdout.flush()
#                 time.sleep(0.8)

#     print("\n✅ Проверка зависимостей завершена.\n")
#     sys.stdout.flush()
#     time.sleep(1.0)

def install_dependencies():
    """
    Проверяет и при необходимости устанавливает все зависимости для ОС.
    Показывает весь реальный вывод pip в ConsoleScreen.
    """
    import subprocess
    import sys
    import platform
    import time

    print("🔍 Проверка установленных библиотек...\n")
    sys.stdout.flush()
    time.sleep(0.8)

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
            print(f"✅ {package} уже установлено.")
            sys.stdout.flush()
            time.sleep(0.4)
        except ImportError:
            print(f"⬇ Устанавливаю {package} ...")
            sys.stdout.flush()
            time.sleep(0.6)
            try:
                # 🔹 потоковое чтение вывода pip install
                process = subprocess.Popen(
                    [sys.executable, "-m", "pip", "install", package, "--upgrade"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                for line in process.stdout:
                    print(line, end="")  # вывод каждой строки прямо в ConsoleScreen
                    sys.stdout.flush()

                process.wait()

                if process.returncode == 0:
                    print(f"✅ {package} установлено успешно!\n")
                else:
                    print(f"❌ Ошибка при установке {package} (код {process.returncode})\n")

                sys.stdout.flush()
                time.sleep(0.5)

            except Exception as e:
                print(f"❌ Не удалось установить {package}: {e}\n")
                sys.stdout.flush()
                time.sleep(1.0)

    print("\n✅ Проверка зависимостей завершена.\n")
    sys.stdout.flush()
    time.sleep(1.0)

# install_dependencies()



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
