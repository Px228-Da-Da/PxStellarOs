import subprocess
import sys
import json
import pywifi
from pywifi import const
import time
import os
import platform
import traceback

# Установка пакетов
def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    except subprocess.CalledProcessError:
        print(f"Не вдалося встановити {package_name}")

# Проверка и установка PyQt6 и PyQt6-WebEngine
try:
    import PyQt6
except ImportError:
    install_package("PyQt6")

try:
    import PyQt6.QtWebEngineWidgets
except ImportError:
    install_package("PyQt6-WebEngine")

# Добавьте новый импорт для PulseAudio
# try:
#     import pulsectl
# except ImportError:
#     subprocess.check_call([sys.executable, "-m", "pip", "install", "pulsectl"])
#     import pulsectl

# PyQt6 импорты
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLabel, QMessageBox, QStackedWidget, QMenuBar, QToolBar, QLineEdit, QTabWidget, QMenu,
    QTextEdit, QCalendarWidget, QListWidget, QListWidgetItem, QProgressBar, QGridLayout, QGraphicsDropShadowEffect, QSlider
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import (
    QIcon, QColor, QEnterEvent, QMouseEvent, QKeyEvent, QCursor, QPixmap,
    QPainter, QBrush, QFont, QAction
)
from PyQt6.QtCore import (
    Qt, QSize, QRect, QPropertyAnimation, QEasingCurve, QTimer,
    QTime, QDate, QUrl, QPoint, QProcess, pyqtProperty
)

# Пути и модули проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin", "sys", "class_")))
from TerminalApp import TerminalApp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin", "sys", "class_", "win", "system_class", "animations")))
from JumpingButton import JumpingButton
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin", "sys", "class_", "win", "system_class", "errors")))
from DeathScreen import DeathScreen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin", "sys", "class_", "win", "system_class", "styles")))
from ToggleSwitch import ToggleSwitch
from Input import Input



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin", "sys", "class_", "win", "Widgets")))
from CalendarWidget import CalendarWidget
from VolumeControlWidget import VolumeControlWidget
from WifiWindow import WifiWindow



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "apps", "local")))
from init import DraggableResizableWindow
from cmd_window import CmdWindow
from browser_window import BrowserWindow
from settings_window import SettingsWindow


from updater import UpdateDialog
from updater import *

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


class MacOSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_locked = False  # Флаг для отслеживания состояния блокировки
        self.is_splash_screen_active = False  # Флаг для отслеживания состояния загрузочного экрана
        self.is_password_input_deleted = False
        # Инициализация Wi-Fi
        self.wifi = pywifi.PyWiFi()
        self.iface = None
        
        try:
            if self.wifi.interfaces():
                self.iface = self.wifi.interfaces()[0]
            else:
                QMessageBox.warning(self, "Ошибка", "Wi-Fi адаптер не найден")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка инициализации Wi-Fi: {str(e)}")
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
            self.setWindowTitle("OS")
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

            # self.create_wifi_button()

            
            # Док-панель
            self.create_dock_panel()
            self.create_time_button()
            # Создаем кнопку громкости
            # self.create_volume_button()
            
            # Остальные элементы
            self.create_menu()
            self.open_windows = {}
            self.create_all_windows()
            self.check_for_updates()

            
            # Создаем экран блокировки
            self.create_lock_screen()
            # Создаем черный экран с логотипом
            # self.create_splash_screen()
        except Exception as e:
            # Если ошибка происходит в конструкторе, показываем её в DeathScreen
            self.show_death_screen(f"Critical error in constructor: {str(e)}")

    # def create_volume_button(self):
    #     """Создает кнопку громкости в правом нижнем углу"""
    #     # Создаем контейнер для кнопки
    #     self.volume_button_container = QWidget(self)
    #     self.volume_button_container.setFixedSize(60, 60)
    #     self.volume_button_container.move(
    #         self.width() - 190,  # Позиция слева от кнопки времени
    #         self.height() - 65   # Такая же высота как у кнопки времени
    #     )
        
    #     # Вертикальный лэйаут для кнопки
    #     layout = QVBoxLayout(self.volume_button_container)
    #     layout.setContentsMargins(0, 0, 0, 0)
    #     layout.setSpacing(0)
        
    #     # Создаем кнопку
    #     self.volume_button = QPushButton()
    #     self.volume_button.setFixedSize(60, 60)
    #     self.volume_button.setStyleSheet("""
    #         QPushButton {
    #             background-color: rgba(255, 255, 255, 0.25);
    #             border-radius: 16px;
    #             border: 1px solid rgba(255, 255, 255, 0.3);
    #             padding: 0;
    #         }
    #         QPushButton:hover {
    #             background-color: rgba(255, 255, 255, 0.35);
    #         }
    #     """)
        
    #     # Иконка громкости
    #     self.volume_icon = QLabel(self.volume_button)
    #     self.volume_icon.setPixmap(QIcon(os.path.join("bin", "icons", "local_icons", "system", "volume.png")).pixmap(30, 30))
    #     self.volume_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #     self.volume_icon.setGeometry(15, 15, 30, 30)
        
    #     layout.addWidget(self.volume_button)
        
    #     # Создаем виджет управления громкостью (изначально скрыт)
    #     self.volume_widget = VolumeControlWidget()
    #     self.volume_widget.setParent(self)
    #     # self.volume_widget.move(
    #     #     self.width() - 370,  # Позиционируем слева от кнопки
    #     #     self.height() - 140  # Позиционируем выше кнопки
    #     # )
    #     self.volume_widget.hide()
        
    #     # Подключаем клик по кнопке громкости
    #     self.volume_button.clicked.connect(self.toggle_volume_control)
        
    #     # Таймер для обновления иконки громкости
    #     self.volume_timer = QTimer(self)
    #     self.volume_timer.timeout.connect(self.update_volume_icon)
    #     self.volume_timer.start(1000)

    def toggle_volume_control(self):
        """Показывает/скрывает панель управления громкостью"""
        if self.volume_widget.isVisible():
            self.hide_volume_control()
        else:
            self.show_volume_control()

    def show_volume_control(self):
        """Показывает панель управления громкостью с анимацией"""
        # Обновляем текущее значение громкости
        self.volume_widget.update_volume()
        
        # Устанавливаем начальную позицию (невидимая, за экраном справа)
        start_pos = QPoint(self.width(), self.height() - 170)
        end_pos = QPoint(self.width() - 370, self.height() - 170)
        
        self.volume_widget.move(start_pos)
        self.volume_widget.show()
        self.volume_widget.raise_()
        
        # Анимация появления
        self.volume_animation = QPropertyAnimation(self.volume_widget, b"pos")
        self.volume_animation.setDuration(200)
        self.volume_animation.setStartValue(start_pos)
        self.volume_animation.setEndValue(end_pos)
        self.volume_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.volume_animation.start()

    def hide_volume_control(self):
        """Скрывает панель управления громкостью с анимацией"""
        start_pos = self.volume_widget.pos()
        end_pos = QPoint(self.width(), self.height() - 170)
        
        # Анимация исчезновения
        self.volume_animation = QPropertyAnimation(self.volume_widget, b"pos")
        self.volume_animation.setDuration(200)
        self.volume_animation.setStartValue(start_pos)
        self.volume_animation.setEndValue(end_pos)
        self.volume_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.volume_animation.finished.connect(self.volume_widget.hide)
        self.volume_animation.start()

    def update_volume_icon(self):
        """Обновляет иконку громкости"""
        try:
            if hasattr(self, 'volume_widget') and self.volume_widget and self.volume_widget.volume:
                current_volume = self.volume_widget.volume.GetMasterVolumeLevelScalar()
                
                if current_volume <= 0:
                    icon_name = "volume_mute.png"
                elif current_volume < 0.33:
                    icon_name = "volume_low.png"
                elif current_volume < 0.66:
                    icon_name = "volume_medium.png"
                else:
                    icon_name = "volume.png"
                    
                icon_path = os.path.join("bin", "icons", "local_icons", "system", icon_name)
                if os.path.exists(icon_path):
                    self.volume_icon.setPixmap(QIcon(icon_path).pixmap(30, 30))
        except Exception as e:
            print(f"Volume icon update error: {e}")


    def show_death_screen(self, error_message):
        """Показывает экран смерти с сообщением об ошибке."""
        self.death_screen = DeathScreen(self, error_message)
        self.death_screen.show()
    
    
    def create_time_button(self):
        """Создает кнопку с временем и датой в правом нижнем углу"""
        # Создаем контейнер для кнопки
        self.time_button_container = QWidget(self)
        self.time_button_container.setFixedSize(120, 60)
        self.time_button_container.move(
            self.width() - 120,  # Правый край с отступом
            self.height() - 65   # Нижний край с отступом
        )
        
        # Вертикальный лэйаут для кнопки
        layout = QVBoxLayout(self.time_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем кнопку
        self.time_button = QPushButton()
        self.time_button.setFixedSize(120, 60)
        self.time_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 0;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)
        
        # Лэйаут для текста внутри кнопки
        text_layout = QVBoxLayout(self.time_button)
        text_layout.setContentsMargins(5, 5, 5, 5)
        text_layout.setSpacing(0)
        
        # Метка для времени
        self.time_button_time = QLabel()
        self.time_button_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_button_time.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # Метка для даты
        self.time_button_date = QLabel()
        self.time_button_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_button_date.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        
        text_layout.addWidget(self.time_button_time)
        text_layout.addWidget(self.time_button_date)
        
        layout.addWidget(self.time_button)
        
        # Создаем виджет календаря (изначально скрыт)
        self.calendar_widget = CalendarWidget()
        self.calendar_widget.setParent(self)
        self.calendar_widget.setFixedSize(350, 350)
        self.calendar_widget.move(
            self.width() - 370,  # Позиционируем слева от кнопки
            self.height() - 420  # Позиционируем выше кнопки
        )
        self.calendar_widget.hide()
        
        # Подключаем клик по кнопке времени
        self.time_button.clicked.connect(self.toggle_calendar)
        
        # Обновляем время сразу
        self.update_time_button()
        
        # Таймер для обновления времени каждую секунду
        self.time_button_timer = QTimer(self)
        self.time_button_timer.timeout.connect(self.update_time_button)
        self.time_button_timer.start(1000)

    def toggle_calendar(self):
        """Показывает/скрывает календарь"""
        if self.calendar_widget.isVisible():
            self.hide_calendar()
        else:
            self.show_calendar()

    def show_calendar(self):
        """Показывает календарь с анимацией"""
        # Устанавливаем начальную позицию (невидимая, за экраном справа)
        start_pos = QPoint(self.width(), self.height() - 350)
        end_pos = QPoint(self.width() - 370, self.height() - 420)
        
        self.calendar_widget.move(start_pos)
        self.calendar_widget.show()
        self.calendar_widget.raise_()
        
        # Устанавливаем флаг, чтобы предотвратить немедленное закрытие
        self.calendar_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # Анимация появления
        self.calendar_animation = QPropertyAnimation(self.calendar_widget, b"pos")
        self.calendar_animation.setDuration(200)
        self.calendar_animation.setStartValue(start_pos)
        self.calendar_animation.setEndValue(end_pos)
        self.calendar_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.calendar_animation.start()

    def hide_calendar(self):
        """Скрывает календарь с анимацией"""
        start_pos = self.calendar_widget.pos()
        end_pos = QPoint(self.width(), self.height() - 350)
        
        # Анимация исчезновения
        self.calendar_animation = QPropertyAnimation(self.calendar_widget, b"pos")
        self.calendar_animation.setDuration(200)
        self.calendar_animation.setStartValue(start_pos)
        self.calendar_animation.setEndValue(end_pos)
        self.calendar_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.calendar_animation.finished.connect(self.calendar_widget.hide)
        self.calendar_animation.start()
    
    def update_time_button(self):
        """Обновляет текст на кнопке времени"""
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        
        # Форматируем время и дату
        time_text = current_time.toString("hh:mm:ss")
        date_text = current_date.toString("dd.MM.yyyy")
        
        # Устанавливаем текст
        self.time_button_time.setText(time_text)
        self.time_button_date.setText(date_text)


    def resizeEvent(self, event):
        """Обновляет позицию элементов при изменении размера окна"""
        super().resizeEvent(event)
        if hasattr(self, 'time_button_container'):
            self.time_button_container.move(
                self.width() - 120,
                self.height() - 65
            )
        if hasattr(self, 'volume_button_container'):
            self.volume_button_container.move(
                self.width() - 190,
                self.height() - 65
            )
        if hasattr(self, 'wifi_button_container'):
            self.wifi_button_container.move(
                self.width() - 260,
                self.height() - 65
            )
        if hasattr(self, 'calendar_widget') and self.calendar_widget.isVisible():
            self.calendar_widget.move(
                self.width() - 370,
                self.height() - 420
            )
        if hasattr(self, 'volume_widget') and self.volume_widget.isVisible():
            self.volume_widget.move(
                self.width() - 370,
                self.height() - 140
            )
        if hasattr(self, 'wifi_window') and self.wifi_window.isVisible():
            self.wifi_window.move(
                self.width() - 370,
                self.height() - 520
            )
        self.load_background_image()

    def create_lock_screen(self):
        """Создает экран блокировки."""
        self.is_locked = True  # Устанавливаем флаг блокировки
        # Если lock_widget уже существует, удаляем его
        if hasattr(self, 'lock_widget') and self.lock_widget is not None:
            self.lock_widget = None

        # Создаем новый виджет для экрана блокировки
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
        scaled_pixmap = logo_pixmap.scaled(logo_pixmap.width() // 2, logo_pixmap.height() // 2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label = QLabel(self.lock_widget)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setGeometry(
            (self.width() - scaled_pixmap.width()) // 2,
            (self.height() - scaled_pixmap.height()) // 2 - 50,
            scaled_pixmap.width(),
            scaled_pixmap.height()
        )

        # Метка для отображения времени (часы:минуты:секунды)
        self.time_label = QLabel(self.lock_widget)
        self.time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 100);
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        self.time_label.setGeometry(10, 10, 150, 30)  # Левый верхний угол
        self.update_time_label()  # Установить начальное значение

        # Таймер для обновления времени каждую секунду
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_time_label)
        self.clock_timer.start(1000)  # 1000 мс = 1 секунда

        # Поле ввода пароля
        self.password_input = Input(
            parent=self.lock_widget,
            placeholder_text="Password",
            initial_text="",  # Можно указать заранее введённый текст, если нужно
            echo_mode=QLineEdit.EchoMode.Password  # Или QLineEdit.EchoMode.Normal для обычного текста
        )
        self.password_input.setGeometry(
            (self.width() - 200) // 2,
            logo_label.y() + logo_label.height() + 20,
            200,
            30
        )
        self.password_input.returnPressed.connect(self.unlock_screen)
        self.password_input.setFocus()


        # Добавляем кнопку с картинкой 50x50
        self.main_button = QPushButton(self.lock_widget)
        self.main_button.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "IconOs", "shutdown.png")))  # Укажите путь к изображению
        self.main_button.setIconSize(QSize(50, 50))
        self.main_button.setFixedSize(50, 50)
        self.main_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        self.main_button.move((self.width() - 50) // 2, logo_label.y() + logo_label.height() + 80)
        self.main_button.clicked.connect(self.toggle_additional_buttons)

        # Контейнер для дополнительных кнопок
        self.additional_buttons_container = QWidget(self.lock_widget)
        self.additional_buttons_container.setGeometry(
            (self.width() - 150) // 2,  # Центрируем по горизонтали
            self.main_button.y() - 60,  # Размещаем выше основной кнопки
            150,  # Ширина контейнера
            100   # Высота контейнера
        )
        self.additional_buttons_container.setStyleSheet("""
            background: rgba(0, 0, 0, 150); 
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);  /* Обводка контейнера */
        """)
        self.additional_buttons_container.hide()  # Скрываем контейнер по умолчанию

        # Вертикальный лэйаут для дополнительных кнопок
        additional_layout = QVBoxLayout(self.additional_buttons_container)
        additional_layout.setSpacing(10)
        additional_layout.setContentsMargins(10, 10, 10, 10)

        # Первая дополнительная кнопка
        self.button1 = QPushButton("Shutdown", self)  # Текст кнопки
        self.button1.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "IconOs", "shutdown.png")))  # Иконка кнопки
        self.button1.setIconSize(QSize(30, 30))  # Размер иконки
        self.button1.setFixedSize(120, 40)  # Размер кнопки (ширина, высота)
        self.button1.clicked.connect(self.shutdown_system)  # Используем clicked.connect
        self.button1.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.2);  /* Обводка кнопки */
                color: white;  /* Белый цвет текста */
                font-size: 14px;  /* Размер шрифта */
                padding-left: 10px;  /* Отступ слева для текста */
                text-align: left;  /* Выравнивание текста по левому краю */
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);  /* Фон при наведении */
            }
            QPushButton::icon {
                color: white;  /* Белый цвет иконки */
            }
        """)
        additional_layout.addWidget(self.button1)  # Добавляем кнопку в лэйаут

        # Вторая дополнительная кнопка
        self.button2 = QPushButton("Reboot", self)  # Текст кнопки
        self.button2.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "IconOs", "reboot.png")))  # Иконка кнопки
        self.button2.setIconSize(QSize(30, 30))  # Размер иконки
        self.button2.setFixedSize(120, 40)  # Размер кнопки (ширина, высота)
        self.button2.clicked.connect(self.reboot_system)  # Используем clicked.connect
        self.button2.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.2);  /* Обводка кнопки */
                color: white;  /* Белый цвет текста */
                font-size: 14px;  /* Размер шрифта */
                padding-left: 10px;  /* Отступ слева для текста */
                text-align: left;  /* Выравнивание текста по левому краю */
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);  /* Фон при наведении */
            }
            QPushButton::icon {
                color: white;  /* Белый цвет иконки */
            }
        """)
        additional_layout.addWidget(self.button2)  # Добавляем кнопку в лэйаут

        # Обработчики событий для скрытия/показа контейнера
        self.additional_buttons_container.enterEvent = self.additional_buttons_enter_event
        self.additional_buttons_container.leaveEvent = self.additional_buttons_leave_event

    def update_time_label(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.time_label.setText(current_time)


    def additional_buttons_enter_event(self, event):
        """Обработчик события, когда курсор входит в область контейнера."""
        # Ничего не делаем, контейнер остается видимым
        pass

    def additional_buttons_leave_event(self, event):
        """Обработчик события, когда курсор покидает область контейнера."""
        # Скрываем контейнер с анимацией
        self.animate_container(self.additional_buttons_container, 0)

    def toggle_additional_buttons(self):
        """Показывает или скрывает дополнительные кнопки."""
        if self.additional_buttons_container.isVisible():
            # Анимация скрытия
            self.animate_container(self.additional_buttons_container, 0)
        else:
            # Анимация появления
            self.additional_buttons_container.show()
            self.animate_container(self.additional_buttons_container, 1)

    def animate_container(self, widget, opacity):
        """Анимация изменения прозрачности контейнера."""
        self.animation = QPropertyAnimation(widget, b"windowOpacity")
        self.animation.setDuration(200)  # Длительность анимации 200 мс
        self.animation.setStartValue(widget.windowOpacity())
        self.animation.setEndValue(opacity)
        if opacity == 0:
            self.animation.finished.connect(lambda: widget.hide())  # Скрываем виджет после завершения анимации
        self.animation.start()


    def unlock_screen(self):
        """Разблокирует экран, если пароль верный."""
        # Проверяем, существует ли еще виджет и поле ввода пароля
        if not hasattr(self, 'lock_widget') or self.lock_widget is None:
            return  # Если виджет уже удален, выходим из метода

        if not hasattr(self, 'password_input') or self.password_input is None:
            return  # Если поле ввода пароля уже удалено, выходим из метода

        # Проверяем, существует ли объект password_input
        try:
            # Проверяем пароль (например, пароль "0000")
            if self.password_input.text() == "":
                self.is_locked = False

                # Остановить и удалить таймер и метку времени
                if hasattr(self, "clock_timer"):
                    self.clock_timer.stop()
                    self.clock_timer.deleteLater()

                self.animation = QPropertyAnimation(self.lock_widget, b"geometry")
                self.animation.setDuration(200)
                self.animation.setStartValue(QRect(0, 0, self.width(), self.height()))
                self.animation.setEndValue(QRect(0, -self.height(), self.width(), self.height()))
                self.animation.finished.connect(self.lock_widget.deleteLater)
                self.animation.start()

                # Удаляем виджет после завершения анимации
                self.animation.finished.connect(self.lock_widget.deleteLater)
                self.animation.start()
            else:
                # Показываем сообщение об ошибке
                QMessageBox.warning(self, "Error", "Incorrect password!")
        except RuntimeError:
            # Если объект уже удален, просто выходим из метода
            return


    def create_splash_screen(self):
        self.is_splash_screen_active = True  # Устанавливаем флаг загрузочного экрана
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
        current_value = 50
        if current_value < 50:
            self.progress_bar.setValue(current_value + 1)
        else:
            self.progress_timer.stop()  # Останавливаем таймер, когда прогресс-бар достигнет 100%

    def start_animation(self):
        self.is_splash_screen_active = False  # Снимаем флаг загрузочного экрана
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
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 0;
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
        # self.update_time()  # Обновляем сразу при старте
        self.create_wifi_button()

        # Создание таймера для обновления времени
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Обновление каждую секунду

        # Добавление времени в правый угол меню
        menubar.setCornerWidget(self.time_label, Qt.Corner.TopRightCorner)
    
    def keyPressEvent(self, event: QKeyEvent):
        # Игнорируем все события клавиатуры, если экран блокировки или загрузочный экран активен
        if self.is_locked or self.is_splash_screen_active:
            return

        # Обработка нажатия Ctrl + L для блокировки экрана
        if event.key() == Qt.Key.Key_L and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.lock_screen()
        
        # Обработка нажатия Ctrl + Tab для переключения между окнами
        if event.key() == Qt.Key.Key_Tab and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.switch_to_next_window()
        
        # Обработка нажатия Enter для разблокировки экрана
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.unlock_screen()
        
        super().keyPressEvent(event)

    
    def create_window_switch_menu(self):
        """Создает меню для переключения между открытыми окнами."""
        self.window_switch_menu = QMenu(self)
        
        # Получаем список открытых окон
        open_windows = [name for name, win in self.open_windows.items() if win and not win.isHidden()]
        
        # Добавляем пункты меню для каждого открытого окна
        for window_name in open_windows:
            action = QAction(window_name.capitalize(), self)
            action.triggered.connect(lambda _, name=window_name: self.switch_window(name))
            self.window_switch_menu.addAction(action)
        
        # Показываем меню в центре экрана
        self.window_switch_menu.popup(QPoint(self.width() // 2, self.height() // 2))

    def lock_screen(self):
        """Блокирует экран с анимацией."""
        # Скрываем рабочий стол и док-панель
        self.create_lock_screen()

        # Создаем экран блокировки, если он еще не создан или был удален
        if not hasattr(self, 'lock_widget') or self.lock_widget is None:
            self.create_lock_screen()

        # Показываем экран блокировки
        if self.lock_widget is not None:
            self.lock_widget.show()
            self.password_input.setFocus()  # Активируем поле ввода пароля

            # Анимация появления экрана блокировки сверху вниз
            self.animation = QPropertyAnimation(self.lock_widget, b"geometry")
            self.animation.setDuration(500)  # Длительность анимации 500 мс
            self.animation.setStartValue(QRect(0, -self.height(), self.width(), self.height()))
            self.animation.setEndValue(QRect(0, 0, self.width(), self.height()))
            self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце
            self.animation.start()

        
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
            pass
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
        # current_time = QTime.currentTime()
        # current_date = QDate.currentDate()
        # self.time_label.setText(f"{current_time.toString('hh:mm:ss')}  {current_date.toString('dd.MM.yyyy')}")
        pass

    def create_wifi_button(self):
        """Создает кнопку Wi-Fi в правом нижнем углу"""
        # Создаем контейнер для кнопки
        self.wifi_button_container = QWidget(self)
        self.wifi_button_container.setFixedSize(60, 60)
        self.wifi_button_container.move(
            self.width() - 260,  # Позиция слева от кнопки громкости
            self.height() - 65   # Такая же высота как у других кнопок
        )
        
        # Вертикальный лэйаут для кнопки
        layout = QVBoxLayout(self.wifi_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем кнопку
        self.wifi_button = QPushButton()
        self.wifi_button.setFixedSize(60, 60)
        self.wifi_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)
        
        # Иконка Wi-Fi
        self.wifi_icon = QLabel(self.wifi_button)
        self.wifi_icon.setPixmap(QIcon(os.path.join("bin", "icons", "local_icons", "system", "wifi.png")).pixmap(30, 30))
        self.wifi_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wifi_icon.setGeometry(15, 15, 30, 30)
        
        layout.addWidget(self.wifi_button)
        
        # Создаем виджет Wi-Fi (изначально скрыт)
        self.wifi_window = WifiWindow()
        self.wifi_window.setParent(self)
        self.wifi_window.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.9);
                color: white;
                border-radius: 8px;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 18px;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
            #header {
                background-color: transparent;
                color: white;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px;
            }
            #monthYearLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
            #weekdays {
                font-size: 12px;
                font-weight: bold;
                color: rgba(255, 255, 255, 0.8);
                padding: 5px 0;
            }
            .day {
                font-size: 14px;
                border-radius: 4px;
                min-width: 30px;
                min-height: 30px;
                color: white;
            }
            .day:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            .current-day {
                background-color: rgba(255, 255, 255, 0.3);
                color: white;
                font-weight: bold;
            }
            .selected-day {
                background-color: rgba(255, 255, 255, 0.4);
                color: white;
                font-weight: bold;
            }
            .other-month {
                color: rgba(255, 255, 255, 0.5);
            }
            .nav-button {
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 16px;
            }
            .nav-button:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.wifi_window.hide()
        
        # Подключаем клик по кнопке Wi-Fi
        self.wifi_button.clicked.connect(self.toggle_wifi_control)
        
        # Добавляем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.wifi_window.setGraphicsEffect(shadow)

    def toggle_wifi_control(self):
        """Показывает/скрывает панель управления Wi-Fi"""
        if self.wifi_window.isVisible():
            self.hide_wifi_control()
        else:
            self.show_wifi_control()

    def show_wifi_control(self):
        """Показывает панель управления Wi-Fi с анимацией"""
        # Обновляем список сетей
        self.wifi_window.scan_networks()
        
        # Устанавливаем начальную позицию (невидимая, за экраном справа)
        start_pos = QPoint(self.width(), self.height() - 520)
        end_pos = QPoint(self.width() - 370, self.height() - 520)
        
        self.wifi_window.move(start_pos)
        self.wifi_window.show()
        self.wifi_window.raise_()
        
        # Анимация появления
        self.wifi_animation = QPropertyAnimation(self.wifi_window, b"pos")
        self.wifi_animation.setDuration(200)
        self.wifi_animation.setStartValue(start_pos)
        self.wifi_animation.setEndValue(end_pos)
        self.wifi_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.wifi_animation.start()

    def hide_wifi_control(self):
        """Скрывает панель управления Wi-Fi с анимацией"""
        start_pos = self.wifi_window.pos()
        end_pos = QPoint(self.width(), self.height() - 520)
        
        # Анимация исчезновения
        self.wifi_animation = QPropertyAnimation(self.wifi_window, b"pos")
        self.wifi_animation.setDuration(200)
        self.wifi_animation.setStartValue(start_pos)
        self.wifi_animation.setEndValue(end_pos)
        self.wifi_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.wifi_animation.finished.connect(self.wifi_window.hide)
        self.wifi_animation.start()

    
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

        # Чтение конфигурации из файла
        dock_config_path = os.path.join("root", "bin", "dock.config")
        icons = []
        
        try:
            with open(dock_config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):  # Пропускаем пустые строки и комментарии
                        parts = line.split(":")
                        if len(parts) >= 2:
                            icon_name = parts[0].strip()
                            window_name = parts[1].strip()
                            icons.append((icon_name, window_name))
        except FileNotFoundError:
            print(f"Файл конфигурации {dock_config_path} не найден. Используются настройки по умолчанию.")
            # Конфигурация по умолчанию
            icons = [
                ("app_store", "desktop"),
                ("safari", "browser"),
                ("settings", "settings"),
                ("cmd", "cmd")
            ]
        except Exception as e:
            print(f"Ошибка при чтении файла конфигурации: {e}")
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

