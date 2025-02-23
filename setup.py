import subprocess
import sys

# Функція для перевірки та установки пакунків
def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        self.reboot_system()
    except subprocess.CalledProcessError:
        print(f"Не вдалося встановити {package_name}")

# Перевірка і установка PyQt6 та PyQt6-WebEngine
try:
    import PyQt6
except ImportError:
    install_package("PyQt6")

try:
    import PyQt6.QtWebEngineWidgets
except ImportError:
    install_package("PyQt6-WebEngine")




from PyQt6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, Qt, QSize
from PyQt6.QtGui import QIcon, QColor, QEnterEvent, QMouseEvent
from PyQt6.QtCore import QTimer, QTime, QDate
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QFrame, QLabel, QMessageBox, QStackedWidget, QMenuBar, QToolBar, QLineEdit,QTabWidget, QMenu
)
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt, QSize, QUrl, QPoint
from PyQt6.QtGui import QCursor, QIcon, QPixmap, QMouseEvent, QColor, QPainter, QBrush, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtCore import QTimer, QTime, QDate
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import QLabel, QMenuBar
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import QApplication, QWidget, QProgressBar, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import os
import platform  # Добавьте этот импорт





sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin", "sys", "class_")))
from TerminalApp import TerminalApp


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "apps", "local")))
from init import DraggableResizableWindow


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "apps", "local")))

icon_dir_PATH = os.path.join("bin", "icons", "local_icons", "IconOs", f"OS.png")

from cmd_window import CmdWindow
from browser_window import BrowserWindow
from settings_window import SettingsWindow

from updater import UpdateDialog
from updater import *


class JumpingButton(QPushButton):
    def __init__(self, icon_path=None, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.is_animating = False
        self.default_size = 44
        self.setFixedSize(self.default_size, self.default_size)
        self.original_geometry = None

        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(self.default_size, self.default_size))

        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)

    def enterEvent(self, event: QEnterEvent):
        if not self.is_animating:
            self.original_geometry = self.geometry()
            self.animateJump(-10)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_animating:
            self.animateJump(10)
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if not self.is_animating:
            self.animateJump(-20, True)
        super().mousePressEvent(event)

    def animateJump(self, offset, is_click=False):
        if self.original_geometry is None:
            self.original_geometry = self.geometry()

        self.is_animating = True
        start_rect = self.geometry()
        end_rect = QRect(start_rect.x(), self.original_geometry.y() + offset, start_rect.width(), start_rect.height())
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(lambda: self.resetPosition(is_click))
        self.animation.start()

    def resetPosition(self, is_click):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.original_geometry)
        self.animation.finished.disconnect()
        self.animation.finished.connect(self.onAnimationFinished)
        self.animation.start()

    def onAnimationFinished(self):
        self.is_animating = False
        self.animation.finished.disconnect()

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

import traceback


def global_exception_handler(exctype, value, tb):
    """Глобальный обработчик исключений."""
    error_message = "".join(traceback.format_exception(exctype, value, tb))
    print(f"Critical error: {error_message}")
    
    # Если окно уже создано, показываем экран смерти
    if 'window' in globals():
        window.show_death_screen(f"Critical error: {error_message}")
    else:
        # Если окно не создано, создаем временное окно для отображения ошибки
        temp_app = QApplication(sys.argv)
        temp_window = QWidget()
        temp_window.setWindowTitle("Critical Error")
        temp_window.setGeometry(100, 100, 800, 600)
        
        death_screen = DeathScreen(temp_window, f"Critical error: {error_message}")
        death_screen.show()
        
        sys.exit(temp_app.exec())



import os
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QTimer

class MacOSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.desk_config = "root/user/desk/desk.config"
            self.active_windows = {}

            # Загружаем курсор из файла Normal.cur
            icon_dir_cursors = os.path.join("bin", "icons", "local_icons", "cursors", "Normal.cur")
            cursor_pixmap = QPixmap(icon_dir_cursors)  # Загружаем изображение курсора

            # Уменьшаем размер курсора (например, в 2 раза)
            new_width = cursor_pixmap.width() // 2
            new_height = cursor_pixmap.height() // 2
            scaled_pixmap = cursor_pixmap.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            # Создаем курсор с точкой наведения (0, 0)
            cursor = QCursor(scaled_pixmap, hotX=0, hotY=0)  # Устанавливаем hotspot на (0, 0)
            
            # Устанавливаем курсор для главного окна
            self.setCursor(cursor)
            
            # Настройки главного окна
            self.setWindowTitle("MacOS-Style OS")
            self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), 
                            QApplication.primaryScreen().size().height())
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            # Фоновое изображение для всего приложения
            self.background = QLabel(self)
            self.background.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.load_background_image()
            
            # Основной контейнер
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            self.main_layout = QVBoxLayout(central_widget)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            
            # Рабочий стол (прозрачный)
            self.create_desktop_window()
            
            # Док-панель
            self.create_dock_panel()
            
            # Остальные элементы
            self.create_menu()
            self.open_windows = {}
            self.create_all_windows()
            self.check_for_updates()

            
            # Создаем экран блокировки
            self.create_lock_screen()
            # Создаем черный экран с логотипом
            self.create_splash_screen()
        except Exception as e:
            # Если ошибка происходит в конструкторе, показываем её в DeathScreen
            self.show_death_screen(f"Critical error in constructor: {str(e)}")


    def show_death_screen(self, error_message):
        """Показывает экран смерти с сообщением об ошибке."""
        self.death_screen = DeathScreen(self, error_message)
        self.death_screen.show()


    def create_lock_screen(self):
        # Создаем виджет для экрана блокировки
        self.lock_widget = QWidget(self)
        self.lock_widget.setGeometry(0, 0, self.width(), self.height())

        # Устанавливаем фон (например, изображение)
        background_pixmap = QPixmap(os.path.join("bin", "icons", "local_icons", "IconOs", "lock.jpg"))
        background_label = QLabel(self.lock_widget)
        background_label.setPixmap(background_pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        background_label.setGeometry(0, 0, self.width(), self.height())

        # Логотип
        icon_dir_path = os.path.join("bin", "icons", "local_icons", "IconOs", "OS.png")
        logo_pixmap = QPixmap(icon_dir_path)

        # Уменьшаем размер изображения логотипа (например, в 2 раза)
        new_width = logo_pixmap.width() // 2
        new_height = logo_pixmap.height() // 2
        scaled_pixmap = logo_pixmap.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        logo_label = QLabel(self.lock_widget)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setGeometry(
            (self.width() - scaled_pixmap.width()) // 2,
            (self.height() - scaled_pixmap.height()) // 2 - 50,  # Сдвигаем логотип выше, чтобы освободить место для поля ввода пароля
            scaled_pixmap.width(),
            scaled_pixmap.height()
        )

        # Поле ввода пароля
        self.password_input = QLineEdit(self.lock_widget)
        self.password_input.setGeometry(
            (self.width() - 200) // 2,  # Центрируем поле ввода по горизонтали
            logo_label.y() + logo_label.height() + 20,  # Размещаем поле ввода под логотипом
            200,  # Ширина поля ввода
            30    # Высота поля ввода
        )
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # Скрываем вводимые символы

        # Устанавливаем стиль для поля ввода
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #555;  /* Граница поля ввода */
                border-radius: 5px;      /* Закругленные углы */
                padding: 5px;           /* Внутренний отступ */
                background-color: rgba(0, 0, 0, 150);  /* Полупрозрачный черный фон */
                color: white;           /* Цвет текста */
                font-size: 14px;        /* Размер шрифта */
            }
            QLineEdit:focus {
                border: 2px solid #0078D7;  /* Граница при фокусе */
            }
        """)
        self.password_input.returnPressed.connect(self.unlock_screen)  # Обработка нажатия Enter

        # Активируем поле ввода пароля
        self.password_input.setFocus()

    def unlock_screen(self):
        # Проверяем пароль (например, пароль "0000")
        if self.password_input.text() == "":
            # Запускаем анимацию разблокировки
            self.animation = QPropertyAnimation(self.lock_widget, b"geometry")
            self.animation.setDuration(200)  # Длительность анимации 0.5 секунды
            self.animation.setStartValue(QRect(0, 0, self.width(), self.height()))
            self.animation.setEndValue(QRect(0, -self.height(), self.width(), self.height()))
            self.animation.finished.connect(self.lock_widget.deleteLater)  # Удаляем виджет после завершения анимации
            self.animation.start()

        else:
            # Показываем сообщение об ошибке
            QMessageBox.warning(self, "Error", "Incorrect password!")

    def keyPressEvent(self, event):
        # Обработка нажатия клавиши Enter
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.unlock_screen()
        else:
            super().keyPressEvent(event)

    def create_splash_screen(self):
        # Создаем виджет для черного экрана
        self.splash_widget = QWidget(self)
        self.splash_widget.setGeometry(0, 0, self.width(), self.height())
        self.splash_widget.setStyleSheet("background-color: black;")

        # Логотип
        icon_dir_path = os.path.join("bin", "icons", "local_icons", "IconOs", "OS.png")
        logo_pixmap = QPixmap(icon_dir_path)

        # Уменьшаем размер изображения логотипа (например, в 2 раза)
        new_width = logo_pixmap.width() // 2
        new_height = logo_pixmap.height() // 2
        scaled_pixmap = logo_pixmap.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        logo_label = QLabel(self.splash_widget)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setGeometry(
            (self.width() - scaled_pixmap.width()) // 2,
            (self.height() - scaled_pixmap.height()) // 2 - 50,  # Сдвигаем логотип выше, чтобы освободить место для прогресс-бара
            scaled_pixmap.width(),
            scaled_pixmap.height()
        )

        # Прогресс-бар
        self.progress_bar = QProgressBar(self.splash_widget)
        self.progress_bar.setGeometry(
            (self.width() - 300) // 2,  # Центрируем прогресс-бар по горизонтали
            logo_label.y() + logo_label.height() + 20,  # Размещаем прогресс-бар под логотипом
            300,  # Ширина прогресс-бара
            20    # Высота прогресс-бара
        )
        self.progress_bar.setRange(0, 100)  # Устанавливаем диапазон от 0 до 100
        self.progress_bar.setValue(0)  # Начальное значение прогресс-бара
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                background-color: black;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 10px;
            }
        """)

        # Таймер для задержки перед анимацией
        self.timer = QTimer()
        self.timer.setSingleShot(True)  # Таймер сработает только один раз
        self.timer.timeout.connect(self.start_animation)  # Подключаем слот для запуска анимации
        self.timer.start(5000)  # Задержка 8 секунд

        # Таймер для обновления прогресс-бара
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(80)  # Обновляем прогресс-бар каждые 80 мс (примерно 8 секунд до 100%)

    def update_progress(self):
        # Обновляем значение прогресс-бара
        current_value = self.progress_bar.value()
        if current_value < 50:
            self.progress_bar.setValue(current_value + 1)
        else:
            self.progress_timer.stop()  # Останавливаем таймер, когда прогресс-бар достигнет 100%

    def start_animation(self):
        # Анимация исчезания вверх
        self.animation = QPropertyAnimation(self.splash_widget, b"geometry")
        self.animation.setDuration(200)  # Длительность анимации 1 секунда
        self.animation.setStartValue(QRect(0, 0, self.width(), self.height()))
        self.animation.setEndValue(QRect(0, -self.height(), self.width(), self.height()))
        self.animation.finished.connect(self.splash_widget.deleteLater)  # Удаляем виджет после завершения анимации
        self.animation.start()



    def check_for_updates(self):
        """Проверяет наличие обновлений и показывает окно обновления."""
        current_version = get_current_version()
        latest_version = get_latest_version()

        if latest_version and latest_version > current_version:
            self.update_window = UpdateDialog(current_version, latest_version, self)
            self.update_window.show()
    
    def run_update(self):
        """Запускает процесс обновления."""
        progress_dialog = UpdateProgressDialog(self)
        progress_dialog.show()

        # Имитация процесса обновления
        for i in range(0, 101, 10):
            QTimer.singleShot(i * 100, lambda i=i: progress_dialog.update_progress(i))
            QApplication.processEvents()

        progress_dialog.close()  # Закрываем прогресс-бар

        if update_application():
            print("Обновление завершено. Перезапустите приложение.")
            # sys.exit(0)
            self.reboot_system()
        else:
            print("Ошибка при обновлении.")


    def start_update_process(self):
        """Запускает процесс обновления."""
        progress_dialog = UpdateProgressDialog(self)
        progress_dialog.show()

        # Имитация процесса обновления
        for i in range(0, 101, 10):
            QTimer.singleShot(i * 100, lambda i=i: progress_dialog.update_progress(i))
            QApplication.processEvents()

        # Закрываем прогресс-бар после завершения
        progress_dialog.close()

        # Запускаем процесс обновления
        if update_application():
            print("Обновление завершено. Перезапустите приложение.")
            sys.exit(0)
        else:
            print("Ошибка при обновлении.")
    

    def load_background_image(self):
        """Загрузка фонового изображения для всего приложения"""
        try:
            with open(self.desk_config, "r", encoding="utf-8") as f:
                image_path = f.read().strip()
            
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path).scaled(
                    self.size(), 
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.background.setPixmap(pixmap)
                self.background.setGeometry(0, 0, self.width(), self.height())
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")

    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Tab and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.switch_to_next_window()

    def switch_to_next_window(self):
        """Переключение между активными окнами"""
        open_windows = [name for name, win in self.open_windows.items() if win and not win.isHidden()]
        if not open_windows:
            return
        
        current_index = open_windows.index(self.active_window_name) if self.active_window_name in open_windows else -1
        next_index = (current_index + 1) % len(open_windows)
        next_window_name = open_windows[next_index]
        
        self.switch_window(next_window_name)
        self.active_window_name = next_window_name


    # def create_all_windows(self):
    #     self.open_windows["browser"] = BrowserWindow(self, "browser")
    #     self.open_windows["cmd"] = CmdWindow(self, "cmd")
    #     self.open_windows["settings"] = SettingsWindow(self, "settings")

    #     # self.open_windows["settings"] = self.create_settings_window()

    def create_all_windows(self):
        """
        Инициализация окон. Окна создаются только при первом открытии.
        """
        self.open_windows = {
            "browser": None,
            "cmd": None,
            "settings": None,
        }
        self.open_windows["browser"] = BrowserWindow(self, "browser")

    def create_menu(self):
        """
        Создает меню с использованием QMenuBar и добавляет время/дату в правый угол.
        """
        menubar = self.menuBar()

        # Устанавливаем стиль меню
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #D1D1D1;  /* Цвет, как у док-панели */
                color: black;
                font-size: 14px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background: #B1B1B1;  /* Цвет фона для выбранного пункта */
            }
        """)

        # Меню "Win" (динамически изменяет название на активное окно)
        self.win_menu = menubar.addMenu("Win")
        self.update_win_menu("desktop")

        # Меню "File"
        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)

        # Меню "Edit"
        edit_menu = menubar.addMenu("Edit")
        cut_action = QAction("Cut", self)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)

        # Меню "View"
        view_menu = menubar.addMenu("View")
        full_screen_action = QAction("Full Screen", self)
        full_screen_action.triggered.connect(self.toggle_maximize_restore)
        view_menu.addAction(full_screen_action)

        # Меню "Tools"
        tools_menu = menubar.addMenu("Tools")
        settings_action = QAction("Settings", self)
        tools_menu.addAction(settings_action)

        # Меню "Power" (Выключение и перезагрузка)
        power_menu = menubar.addMenu("Power")

        # Действие для выключения
        shutdown_action = QAction("Shutdown", self)
        shutdown_action.triggered.connect(self.shutdown_system)
        power_menu.addAction(shutdown_action)

        # Действие для перезагрузки
        reboot_action = QAction("Reboot", self)
        reboot_action.triggered.connect(self.reboot_system)
        power_menu.addAction(reboot_action)

        # Действие для блокировки экрана
        lock_action = QAction("Lock", self)  # Кнопка блокировки
        lock_action.triggered.connect(self.lock_screen)  # Связываем с методом блокировки
        power_menu.addAction(lock_action)  # Добавляем в меню "Power"

        # Создание метки для времени и даты
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Helvetica", 14))
        self.time_label.setStyleSheet("color: black; padding: 5px;")
        self.update_time()  # Обновляем сразу при старте

        # Создание таймера для обновления времени
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Обновление каждую секунду

        # Добавление времени в правый угол меню
        menubar.setCornerWidget(self.time_label, Qt.Corner.TopRightCorner)

    def lock_screen(self):
        """Блокирует экран."""
        # Скрываем рабочий стол и док-панель
        self.centralWidget().hide()
        if hasattr(self, 'dock_panel'):
            self.dock_panel.hide()

        # Создаем экран блокировки, если он еще не создан
        if not hasattr(self, 'lock_widget'):
            self.create_lock_screen()

        # Показываем экран блокировки
        # self.lock_widget.show()
        # self.password_input.setFocus()  # Активируем поле ввода пароля

        
    def shutdown_system(self):
        """
        Выключает систему.
        """
        system_platform = platform.system()
        if system_platform == "Windows":
            # Команда для выключения Windows
            QProcess.startDetached("shutdown", ["/s", "/t", "0"])
        elif system_platform == "Linux":
            # Команда для выключения Linux
            QProcess.startDetached("shutdown", ["-h", "now"])
        else:
            print(f"Unsupported platform: {system_platform}")

    def reboot_system(self):
        """
        Перезагружает систему.
        """
        system_platform = platform.system()
        if system_platform == "Windows":
            # Команда для перезагрузки Windows
            QProcess.startDetached("shutdown", ["/r", "/t", "0"])
        elif system_platform == "Linux":
            # Команда для перезагрузки Linux
            QProcess.startDetached("reboot")
        else:
            print(f"Unsupported platform: {system_platform}")

    def update_win_menu(self, window_name):
        """
        Обновляет текст меню "Win" на активное окно и выделяет кнопку в доке.
        """
        self.win_menu.setTitle(window_name)
        
        # Сбрасываем стиль всех кнопок
        for name, (button, _) in self.dock_buttons.items():
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 0;
                    margin: 0;
                }
                QPushButton:hover {
                    background-color: #B1B1B1;
                    border-radius: 8px;
                }
            """)
        
        # Выделяем кнопку активного приложения
        if window_name.lower() == "desktop":
            window_name = "desktop"  # Синхронизируем с идентификатором в доке
        
        if window_name in self.dock_buttons:
            button, _ = self.dock_buttons[window_name]
            button.setStyleSheet("""
                QPushButton {
                    background-color: #181818;
                    border-radius: 8px;
                    padding: 0;
                    margin: 0;
                }
                QPushButton:hover {
                    background-color: #B1B1B1;
                }
            """)

    def update_time(self):
        """
        Обновляет время и дату в метке.
        """
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        formatted_time = current_time.toString("hh:mm:ss")
        formatted_date = current_date.toString("dddd, d MMM yyyy")
        
        self.time_label.setText(f"{formatted_date} | {formatted_time}")
    
    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()  # Восстановить в нормальный размер
        else:
            # Получаем размеры рабочего стола
            screen_geometry = QApplication.primaryScreen().availableGeometry()

            # Учитываем высоту верхней панели и док-панели
            top_bar_height = 30  # Высота верхней панели
            dock_height = 80  # Высота док-панели

            # Устанавливаем размеры окна с учетом панелей
            available_height = screen_geometry.height() - top_bar_height - dock_height
            self.setGeometry(screen_geometry.x(), screen_geometry.y(), screen_geometry.width(), available_height)

    def create_desktop_window(self):
        """Создание прозрачного рабочего стола"""
        self.desktop = QFrame()
        self.desktop.setStyleSheet("""
            background: transparent;
            border: none;
        """)
        self.main_layout.addWidget(self.desktop)
        
    def create_dock_panel(self):
        """Стилизация док-панели в стиле macOS с динамическим размером"""
        self.dock_buttons = {}
        self.active_windows = {}

        # Создаем фрейм для док-панели
        self.dock = QFrame()

        # Стили с эффектом тени
        self.dock.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 0;
            }
        """)

        # Эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.dock.setGraphicsEffect(shadow)

        # Настройка лэйаута
        dock_layout = QHBoxLayout()
        dock_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dock_layout.setSpacing(15)
        dock_layout.setContentsMargins(10, 2, 10, 2)

        # Конфигурация иконок
        icons = [
            ("app_store", "desktop"),
            ("safari", "browser"),
            ("settings", "settings"),
            ("cmd", "cmd")
        ]

        button_size = 44  # Размер кнопки
        dock_padding = 20  # Отступы док-панели
        dock_spacing = 15  # Промежуток между кнопками
        dock_width = len(icons) * (button_size + dock_spacing) + dock_padding * 2
        self.dock.setFixedSize(dock_width, 65)  # Устанавливаем ширину док-панели

        for icon_name, window_name in icons:
            icon_path = os.path.join("bin", "icons", "local_icons", "local_apps", icon_name, f"{icon_name}.png")

            if not os.path.exists(icon_path):
                print(f"Ошибка: Иконка {icon_path} не найдена!")
                continue

            btn = JumpingButton(icon_path=icon_path, parent=self)
            btn.setFixedSize(button_size, button_size)
            btn.setIconSize(QSize(50, 50))
            btn.clicked.connect(lambda _, n=window_name: self.switch_window(n))

            # Добавляем эффект тени для кнопки
            btn_shadow = QGraphicsDropShadowEffect()
            btn_shadow.setBlurRadius(10)
            btn_shadow.setColor(QColor(0, 0, 0, 100))
            btn_shadow.setOffset(2, 2)
            btn.setGraphicsEffect(btn_shadow)

            indicator = QLabel()
            indicator.setFixedSize(20, 4)
            indicator.setStyleSheet("background: transparent; border: none; border-radius: 2px;")

            # Контейнер для кнопки и индикатора
            container = QWidget()  # Создаем контейнерный виджет
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 8, 0, 0)
            container_layout.setSpacing(5)
            container_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            container_layout.addWidget(indicator, alignment=Qt.AlignmentFlag.AlignHCenter)

            # Поднимаем кнопку на верхний слой
            btn.raise_()

            # Добавляем контейнер в док-панель
            dock_layout.addWidget(container)

            self.dock_buttons[window_name] = (btn, indicator)

        self.dock.setLayout(dock_layout)
        self.main_layout.addWidget(self.dock, alignment=Qt.AlignmentFlag.AlignHCenter)






    def resizeEvent(self, event):
        """Обновление фона при изменении размера окна"""
        self.load_background_image()
        super().resizeEvent(event)

    def toggle_window(self, window_name):
        """
        Переключает состояние окна: если оно активно - сворачивает, если нет - разворачивает.
        """
        window = self.open_windows.get(window_name)

        if window:
            if window.isMinimized():
                window.showNormal()  # Разворачиваем свернутое окно
                window.activateWindow()
            else:
                window.showMinimized()  # Сворачиваем окно
        else:
            print(f"Окно {window_name} не открыто. Открываем...")
            self.open_windows[window_name] = getattr(self, f"create_{window_name}_window")()
            self.open_windows[window_name].show()
            


    def show_context_menu(self, window_name, button):
        """
        Показывает контекстное меню при нажатии правой кнопкой мыши на иконку в док-панели.
        """
        menu = QMenu()

        # Опции меню
        action_pin = QAction("Закрепить на панели задач", self)
        action_close = QAction("Закрыть окно", self)
        action_kill = QAction("Завершить задачу", self)

        # Привязка действий к кнопкам
        action_close.triggered.connect(lambda: self.close_window(window_name))
        action_kill.triggered.connect(lambda: self.force_close_window(window_name))

        # Добавление опций в меню
        menu.addAction(action_pin)
        menu.addAction(action_kill)
        menu.addAction(action_close)

        # Отображение меню под кнопкой
        menu.exec(button.mapToGlobal(QPoint(0, button.height())))

    def close_window(self, window_name):
        """ Закрывает окно, если оно открыто. """
        window = self.open_windows.get(window_name)
        if window:
            window.close()
            self.open_windows[window_name] = None
            print(f"Окно {window_name} закрыто.")

    def force_close_window(self, window_name):
        """ Принудительно завершает процесс приложения. """
        if window_name in self.processes:
            self.processes[window_name].terminate()
            del self.processes[window_name]
            print(f"Процесс {window_name} завершён принудительно.")


    def switch_window(self, window_name):
        window_name = window_name.strip()

        # Снимаем выделение со всех кнопок
        for name, (button, _) in self.dock_buttons.items():
            button.setStyleSheet("")  # Сбрасываем стиль кнопки

        if window_name.lower() == "desktop":  # Проверяем, является ли это рабочим столом
            for win in self.open_windows.values():
                if win:
                    win.hide()  # Скрываем все открытые окна
            self.active_window_name = "desktop"
            self.update_win_menu("desktop")  # Обновляем заголовок меню
            self.update_dock_indicators()  # Обновляем индикаторы в доке
            return

        # Проверяем, есть ли окно в self.open_windows
        if window_name in self.open_windows:
            if self.open_windows[window_name] is None:
                # Создаем окно только при первом открытии
                if window_name == "browser":
                    self.open_windows[window_name] = BrowserWindow(self, "browser")
                elif window_name == "cmd":
                    self.open_windows[window_name] = CmdWindow(self, "cmd")
                elif window_name == "settings":
                    self.open_windows[window_name] = SettingsWindow(self, "settings")
                else:
                    print(f"Ошибка: Неизвестное окно {window_name}")
                    return

            window = self.open_windows[window_name]

            # Проверяем, что window не None перед вызовом isMinimized()
            if window is not None:
                if window.minimized:  # Проверяем, свернуто ли окно
                    window.restore_window()  # Восстанавливаем окно
                else:
                    if window.isMinimized():  # Если окно свернуто стандартным способом
                        window.showNormal()
                        window.activateWindow()
                    else:
                        # Анимация открытия окна
                        self.animate_window_open(window)
                        window.show()
                        window.raise_()
                        window.activateWindow()

                self.active_window_name = window_name
                self.update_win_menu(window_name)  # Обновляем название в меню "Win"

                # Устанавливаем флаг активности и обновляем индикаторы в доке
                self.active_windows[window_name] = True
                self.update_dock_indicators()

                # Выделяем активную кнопку
                if window_name in self.dock_buttons:
                    button, _ = self.dock_buttons[window_name]
                    button.setStyleSheet("background-color: #181818; border-radius: 8px;")  # Выделяем активную кнопку

    def animate_window_open(self, window):
        """Анимация открытия окна"""
        # Устанавливаем начальный размер окна (очень маленький)
        start_size = QSize(10, 10)
        end_size = window.size()

        # Устанавливаем начальный размер окна
        window.resize(start_size)

        # Создаем анимацию для изменения размера окна
        self.animation = QPropertyAnimation(window, b"size")
        self.animation.setDuration(150)  # Длительность анимации в миллисекундах
        self.animation.setStartValue(start_size)
        self.animation.setEndValue(end_size)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце

        # Запускаем анимацию
        self.animation.start()


    def update_dock_indicators(self):
        """
        Обновляет индикаторы запущенных приложений в доке.
        """
        if not hasattr(self, 'active_windows'):
            self.active_windows = {}
            
        for window_name, (button, indicator) in self.dock_buttons.items():
            if self.active_windows.get(window_name, False):
                indicator.setStyleSheet("""
                    background-color: #4bcfff;
                    border: none;
                    border-radius: 22px;
                    min-height: 4px;
                """)
            else:
                indicator.setStyleSheet("""
                    background-color: transparent;
                    border: none;
                """)


if __name__ == "__main__":
    # Устанавливаем глобальный обработчик исключений
    sys.excepthook = global_exception_handler

    try:
        app = QApplication(sys.argv)
        window = MacOSWindow()
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        # Если ошибка произошла до создания окна, показываем её в DeathScreen через временное окно
        global_exception_handler(type(e), e, e.__traceback__)


