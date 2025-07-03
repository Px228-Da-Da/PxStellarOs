import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QScrollArea, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt, QSize, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush, QPen
from PyQt6.QtWidgets import QGraphicsDropShadowEffect


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class LinuxStartMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        self.setFixedSize(600, 500)
        self.is_showing = False
        
        # Стиль виджета
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 0.95);
                color: white;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 8px;
                text-align: left;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QLabel {
                color: white;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(30, 30, 30, 0.5);
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Поисковая строка
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_btn = QPushButton()
        self.search_btn.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "system", "search.png")))
        self.search_btn.setIconSize(QSize(20, 20))
        self.search_btn.setFixedSize(40, 40)
        
        self.search_input = QPushButton("Поиск в приложениях...")
        self.search_input.setStyleSheet("font-size: 14px;")
        self.search_input.setFixedHeight(40)
        
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)
        
        # Основное содержимое
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Левая панель - избранное
        favorites_panel = QWidget()
        favorites_panel.setFixedWidth(150)
        favorites_layout = QVBoxLayout(favorites_panel)
        favorites_layout.setContentsMargins(0, 0, 0, 0)
        favorites_layout.setSpacing(5)
        
        favorites_label = QLabel("Избранное")
        favorites_label.setStyleSheet("font-size: 16px; font-weight: bold; padding-bottom: 10px;")
        favorites_layout.addWidget(favorites_label)
        
        # Добавляем избранные приложения
        favorite_apps = [
            ("Терминал", "terminal.png", "terminal"),
            ("Браузер", "browser.png", "browser"),
            ("Файлы", "files.png", "files"),
            ("Настройки", "settings.png", "settings"),
            ("Текстовый редактор", "editor.png", "editor")
        ]
        
        for name, icon, app_id in favorite_apps:
            btn = self.create_app_button(name, icon, app_id)
            favorites_layout.addWidget(btn)
        
        favorites_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        content_layout.addWidget(favorites_panel)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: rgba(255, 255, 255, 0.1);")
        content_layout.addWidget(separator)
        
        # Правая панель - все приложения
        apps_panel = QWidget()
        apps_layout = QVBoxLayout(apps_panel)
        apps_layout.setContentsMargins(0, 0, 0, 0)
        apps_layout.setSpacing(5)
        
        apps_label = QLabel("Все приложения")
        apps_label.setStyleSheet("font-size: 16px; font-weight: bold; padding-bottom: 10px;")
        apps_layout.addWidget(apps_label)
        
        # Область прокрутки для приложений
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        apps_container = QWidget()
        apps_container_layout = QVBoxLayout(apps_container)
        apps_container_layout.setContentsMargins(0, 0, 0, 0)
        apps_container_layout.setSpacing(5)
        
        # Группы приложений
        app_groups = [
            {
                "name": "Интернет",
                "apps": [
                    ("Браузер", "browser.png", "browser"),
                    ("Почта", "email.png", "email"),
                    ("Чат", "chat.png", "chat")
                ]
            },
            {
                "name": "Офис",
                "apps": [
                    ("Текстовый редактор", "editor.png", "editor"),
                    ("Таблицы", "spreadsheet.png", "spreadsheet"),
                    ("Презентации", "presentation.png", "presentation")
                ]
            },
            {
                "name": "Системные",
                "apps": [
                    ("Терминал", "terminal.png", "terminal"),
                    ("Настройки", "settings.png", "settings"),
                    ("Файлы", "files.png", "files"),
                    ("Диспетчер задач", "taskmanager.png", "taskmanager")
                ]
            }
        ]
        
        for group in app_groups:
            group_label = QLabel(group["name"])
            group_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-top: 10px;")
            apps_container_layout.addWidget(group_label)
            
            for name, icon, app_id in group["apps"]:
                btn = self.create_app_button(name, icon, app_id)
                apps_container_layout.addWidget(btn)
        
        apps_container_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        scroll_area.setWidget(apps_container)
        apps_layout.addWidget(scroll_area)
        
        content_layout.addWidget(apps_panel, 1)
        main_layout.addLayout(content_layout, 1)
        
        # Нижняя панель - кнопки питания
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)
        
        power_btns = [
            ("Пользователь", "user.png", "user"),
            ("Настройки", "settings.png", "settings"),
            ("Завершение сеанса", "logout.png", "logout"),
            ("Выключение", "power.png", "power")
        ]
        
        for name, icon, btn_id in power_btns:
            btn = QPushButton()
            btn.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "system", icon)))
            btn.setIconSize(QSize(20, 20))
            btn.setToolTip(name)
            btn.setFixedSize(40, 40)
            btn.setProperty("id", btn_id)
            btn.clicked.connect(self.power_button_clicked)
            bottom_layout.addWidget(btn)
        
        bottom_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addWidget(bottom_panel)
    
    def create_app_button(self, name, icon, app_id):
        """Создает кнопку приложения"""
        btn = QPushButton(name)
        btn.setProperty("id", app_id)
        
        icon_path = os.path.join("bin", "icons", "local_icons", "apps", icon)
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
        
        btn.clicked.connect(self.app_button_clicked)
        return btn
    
    def app_button_clicked(self):
        """Обработчик клика по кнопке приложения"""
        sender = self.sender()
        app_id = sender.property("id")
        app_name = sender.text()
        
        # Здесь можно добавить логику запуска приложения
        print(f"Запуск приложения: {app_name} ({app_id})")
        self.hide()
    
    def power_button_clicked(self):
        """Обработчик клика по кнопке питания"""
        sender = self.sender()
        btn_id = sender.property("id")
        
        if btn_id == "power":
            # Выключение
            print("Выключение системы")
            self.parent().shutdown_system()
        elif btn_id == "logout":
            # Выход
            print("Завершение сеанса")
            self.parent().lock_screen()
        elif btn_id == "settings":
            # Настройки
            print("Открытие настроек")
            self.parent().switch_window("settings")
        elif btn_id == "user":
            # Пользователь
            print("Открытие профиля пользователя")
        
        self.hide()
    
    def show_menu(self):
        """Показывает меню по центру экрана с анимацией"""
        if self.is_showing:
            return
            
        self.is_showing = True
        
        # Получаем размеры экрана
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        
        # Вычисляем позицию для центрирования
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        
        # Устанавливаем позицию
        self.move(x, y)
        
        # Убедимся, что виджет получает фокус
        self.setFocus()
        
        # Анимация появления
        self.setWindowOpacity(0)
        self.show()
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(150)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.finished.connect(self.ensure_focus)
        self.animation.start()

    def ensure_focus(self):
        """Убеждаемся, что меню получило фокус"""
        self.activateWindow()
        self.setFocus()
    
    def hide_menu(self):
        """Скрывает меню с анимацией"""
        if not self.is_showing:
            return
            
        self.is_showing = False
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(150)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.animation.finished.connect(self.cleanup_after_hide)
        self.animation.start()
    
    def cleanup_after_hide(self):
        """Очистка после скрытия меню"""
        self.hide()
        # Возвращаем фокус родительскому окну
        if self.parent():
            self.parent().setFocus()
    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        # Закрытие меню по Esc
        if event.key() == Qt.Key.Key_Escape:
            self.hide_menu()
        else:
            super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """Автоматическое закрытие при потере фокуса"""
        if not self.isActiveWindow():
            self.hide_menu()
        super().focusOutEvent(event)

    
    def paintEvent(self, event):
        """Переопределяем метод отрисовки для скругленных углов"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем фон с скругленными углами
        rect = self.rect()
        painter.setBrush(QBrush(QColor(40, 40, 40, 240)))
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1))
        painter.drawRoundedRect(rect, 12, 12)
        
        # Рисуем разделитель между верхней и нижней частями
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawLine(15, 70, self.width() - 15, 70)
        
        painter.end()