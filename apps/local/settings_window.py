from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QListWidget, QStackedWidget, QPushButton, QHBoxLayout
)
from apps.local.init import DraggableResizableWindow  # Импортируем базовый класс окна

class SettingsWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name=""):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name  # Сохраняем имя окна
        self.setGeometry(300, 150, 500, 400)

        # Основной контейнер
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)  # Меняем на горизонтальный layout

        # Создаем боковое меню (таб-меню)
        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(180)  # Ограничиваем ширину списка
        self.menu_list.addItem("Общие")
        # self.menu_list.addItem("Дисплей")
        # self.menu_list.addItem("Сеть")
        # self.menu_list.addItem("Звук")
        self.menu_list.setStyleSheet(""
            "background-color: #2E2E2E; color: white; font-size: 14px;"
            "border-right: 1px solid #555; padding: 5px;"
        "")

        # Контентная область (правый экран)
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #3B3B3B; color: white; font-size: 14px;")

        # Страница "Общие"
        general_page = QWidget()
        general_layout = QVBoxLayout(general_page)
        general_layout.addWidget(QLabel("Общие настройки"))
        general_layout.addWidget(QPushButton("Сохранить изменения"))
        self.content_area.addWidget(general_page)

        # Страница "Дисплей"
        display_page = QWidget()
        display_layout = QVBoxLayout(display_page)
        display_layout.addWidget(QLabel("Настройки дисплея"))
        display_layout.addWidget(QPushButton("Изменить разрешение"))
        self.content_area.addWidget(display_page)

        # Страница "Сеть"
        network_page = QWidget()
        network_layout = QVBoxLayout(network_page)
        network_layout.addWidget(QLabel("Настройки сети"))
        network_layout.addWidget(QPushButton("Переподключиться"))
        self.content_area.addWidget(network_page)

        # Страница "Звук"
        sound_page = QWidget()
        sound_layout = QVBoxLayout(sound_page)
        sound_layout.addWidget(QLabel("Настройки звука"))
        sound_layout.addWidget(QPushButton("Настроить громкость"))
        self.content_area.addWidget(sound_page)

        # Подключаем смену контента
        self.menu_list.currentRowChanged.connect(self.content_area.setCurrentIndex)

        # Добавляем элементы в основной layout
        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(self.content_area)

        main_widget.setLayout(main_layout)
        self.set_content(main_widget)

        # Устанавливаем стили окна
        self.setStyleSheet(""
            "background-color: #2E2E2E; border-radius: 10px;"
            " font-family: 'Ubuntu', sans-serif;"
        "")

        # Обновляем заголовок меню
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)

        self.hide()

