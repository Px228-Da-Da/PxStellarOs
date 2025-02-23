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

import sys
import os
import subprocess



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



class SplashScreen(QWidget):
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        
        # Устанавливаем чёрный фон
        self.setStyleSheet("background-color: black;")
        
        # Устанавливаем размеры экрана
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        
        # Создаем layout для размещения элементов
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем элементы
        
        # Загружаем логотип
        self.logo = QLabel(self)
        self.logo.setPixmap(QPixmap(icon_path).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Создаем прогресс-бар
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedWidth(300)  # Ширина прогресс-бара
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: #333;
                text-align: center;  # Убираем текст процентов
            }
            QProgressBar::chunk {
                background-color: #4bcfff;
                width: 10px;
            }
        """)
        self.progress_bar.setFormat("")  # Убираем текст процентов
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Таймер для имитации загрузки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0

    def start(self):
        """Запуск экрана загрузки"""
        self.timer.start(40)  # Обновление прогресс-бара каждые 40 мс

    def update_progress(self):
        """Обновление прогресс-бара"""
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)
        
        # Если прогресс достиг 100%, закрываем экран загрузки
        if self.progress_value >= 100:
            self.timer.stop()
            self.close()
import platform  # Добавьте этот импорт





class MacOSWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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
            sys.exit(0)
            # self.reboot_system()
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
      """
      )
  
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
      self.dock.setFixedSize(dock_width, 80)  # Устанавливаем ширину док-панели
  
      for icon_name, window_name in icons:
          icon_path = os.path.join("bin", "icons", "local_icons", "local_apps", icon_name, f"{icon_name}.png")
          
          if not os.path.exists(icon_path):
              print(f"Ошибка: Иконка {icon_path} не найдена!")
              continue
  
          btn = QPushButton()
          btn.setFixedSize(button_size, button_size)
          btn.setIcon(QIcon(icon_path))
          btn.setIconSize(QSize(50, 50))
          btn.setStyleSheet("""
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
          """
          )
          btn.clicked.connect(lambda _, n=window_name: self.switch_window(n))
          
          indicator = QLabel()
          indicator.setFixedSize(20, 4)
          indicator.setStyleSheet("background: transparent; border: none; border-radius: 2px;")
          
          container = QVBoxLayout()
          container.setContentsMargins(0, 0, 0, 0)
          container.setSpacing(5)
          container.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
          container.addWidget(indicator, alignment=Qt.AlignmentFlag.AlignHCenter)
          
          widget = QWidget()
          widget.setLayout(container)
          dock_layout.addWidget(widget)
  
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
                if window.isMinimized():
                    window.showNormal()
                    window.activateWindow()
                else:
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
    app = QApplication(sys.argv)

    # Путь к логотипу (переменная icon_dir_PATH)
    # icon_dir_PATH = os.path.join("bin", "icons", "logo.png")  # Укажи правильный путь к логотипу

    # Создаем экран загрузки
    # splash = SplashScreen(icon_dir_PATH)
    # splash.show()

    # # Имитируем загрузку
    # splash.start()

    # Создаем основное окно
    window = MacOSWindow()

    # Показываем основное окно после завершения загрузки
    window.show()
    # check_for_updates()

    sys.exit(app.exec())
