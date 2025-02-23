from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QListWidget, QStackedWidget, QPushButton, QHBoxLayout
)
from apps.local.init import DraggableResizableWindow  # Импортируем базовый класс окна
from updater import get_current_version, get_latest_version, update_application  # Импортируем функции обновления

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
        self.menu_list.addItem("Обновление системы")  # Добавляем новую вкладку
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

        # Страница "Обновление системы"
        update_page = QWidget()
        update_layout = QVBoxLayout(update_page)

        # Текущая версия
        self.current_version_label = QLabel(f"Текущая версия: {get_current_version()}")
        update_layout.addWidget(self.current_version_label)

        # Кнопка для проверки обновлений
        self.check_update_button = QPushButton("Проверить обновления")
        self.check_update_button.clicked.connect(self.check_for_updates)
        update_layout.addWidget(self.check_update_button)

        # Кнопка для запуска обновления
        self.update_button = QPushButton("Обновить систему")
        self.update_button.clicked.connect(self.run_update)
        self.update_button.setEnabled(False)  # По умолчанию кнопка отключена
        update_layout.addWidget(self.update_button)

        self.content_area.addWidget(update_page)

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

    def check_for_updates(self):
        """Проверяет наличие обновлений и обновляет интерфейс."""
        latest_version = get_latest_version()
        current_version = get_current_version()

        if latest_version and latest_version > current_version:
            self.current_version_label.setText(f"Текущая версия: {current_version}\nДоступна новая версия: {latest_version}")
            self.update_button.setEnabled(True)  # Включаем кнопку обновления
        else:
            self.current_version_label.setText(f"Текущая версия: {current_version}\nОбновлений не найдено.")
            self.update_button.setEnabled(False)  # Отключаем кнопку обновления

    def run_update(self):
        """Запускает процесс обновления."""
        if update_application():
            self.current_version_label.setText("Обновление завершено. Перезапустите ос.")
        else:
            self.current_version_label.setText("Ошибка при обновлении.")