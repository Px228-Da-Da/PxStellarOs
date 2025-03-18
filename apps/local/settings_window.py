from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QListWidget, QStackedWidget, QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QInputDialog
)
from apps.local.init import DraggableResizableWindow  # Импортируем базовый класс окна
from updater import get_current_version, get_latest_version, update_application  # Импортируем функции обновления
import shutil
import os
import datetime

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
        self.menu_list.addItem("Резервная копия ОС")  # Добавляем вкладку для резервной копии
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

        # Кнопка для отката обновления
        self.rollback_button = QPushButton("Откат обновления")
        self.rollback_button.clicked.connect(self.rollback_update)
        self.rollback_button.setEnabled(os.path.exists("backup"))  # Включаем кнопку, если есть резервная копия
        update_layout.addWidget(self.rollback_button)

        self.content_area.addWidget(update_page)

        # Страница "Резервная копия ОС"
        backup_page = QWidget()
        backup_layout = QVBoxLayout(backup_page)

        # Метка для информации о резервных копиях
        self.backup_info_label = QLabel("Резервные копии не созданы.")
        backup_layout.addWidget(self.backup_info_label)

        # Список резервных копий
        self.backup_list = QListWidget()
        self.backup_list.setStyleSheet("background-color: #2E2E2E; color: white; font-size: 14px;")
        backup_layout.addWidget(self.backup_list)

        # Кнопка для создания резервной копии
        self.create_backup_button = QPushButton("Создать резервную копию")
        self.create_backup_button.clicked.connect(self.create_system_backup)
        backup_layout.addWidget(self.create_backup_button)

        # Кнопка для восстановления из резервной копии
        self.restore_backup_button = QPushButton("Восстановить из резервной копии")
        self.restore_backup_button.clicked.connect(self.restore_system_backup)
        self.restore_backup_button.setEnabled(False)  # По умолчанию кнопка отключена
        backup_layout.addWidget(self.restore_backup_button)

        # Кнопка для удаления резервной копии
        self.delete_backup_button = QPushButton("Удалить резервную копию")
        self.delete_backup_button.clicked.connect(self.delete_system_backup)
        self.delete_backup_button.setEnabled(False)  # По умолчанию кнопка отключена
        backup_layout.addWidget(self.delete_backup_button)

        self.content_area.addWidget(backup_page)

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

        self.update_backup_info()

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

    def backup_current_version(self):
        """Создает резервную копию текущей версии приложения."""
        backup_dir = "backup"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Копируем текущую версию в папку backup
        for item in os.listdir("."):
            if item != backup_dir:
                s = os.path.join(".", item)
                d = os.path.join(backup_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks=True, ignore=None)
                else:
                    shutil.copy2(s, d)

    def rollback_update(self):
        """Откатывает обновление, восстанавливая предыдущую версию приложения."""
        backup_dir = "backup"
        if not os.path.exists(backup_dir):
            QMessageBox.warning(self, "Ошибка", "Резервная копия не найдена. Откат невозможен.")
            return False
        
        # Удаляем текущую версию
        for item in os.listdir("."):
            if item != backup_dir:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
        
        # Восстанавливаем резервную копию
        for item in os.listdir(backup_dir):
            s = os.path.join(backup_dir, item)
            d = os.path.join(".", item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks=True, ignore=None)
            else:
                shutil.copy2(s, d)
        
        QMessageBox.information(self, "Откат завершен", "Приложение восстановлено до предыдущей версии.")
        self.rollback_button.setEnabled(False)  # Отключаем кнопку отката
        return True

    def run_update(self):
        """Запускает процесс обновления с возможностью отката."""
        # Создаем резервную копию перед обновлением
        self.backup_current_version()
        
        # Запускаем обновление
        if update_application():
            self.current_version_label.setText("Обновление завершено. Перезапустите ос.")
            self.rollback_button.setEnabled(True)  # Включаем кнопку отката
        else:
            self.current_version_label.setText("Ошибка при обновлении. Попытка отката...")
            if self.rollback_update():
                self.current_version_label.setText("Откат выполнен успешно.")
            else:
                self.current_version_label.setText("Откат не удался.")

    def create_system_backup(self):
        """Создает резервную копию системы."""
        backup_dir = "system_backup"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Создаем уникальное имя для резервной копии
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)

        # Копируем текущую версию в папку резервной копии
        for item in os.listdir("."):
            if item != backup_dir:
                s = os.path.join(".", item)
                d = os.path.join(backup_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks=True, ignore=None)
                else:
                    shutil.copy2(s, d)
        
        QMessageBox.information(self, "Резервная копия создана", f"Резервная копия успешно создана: {backup_name}")
        self.update_backup_info()

    def restore_system_backup(self):
        """Восстанавливает систему из резервной копии."""
        backup_dir = "system_backup"
        if not os.path.exists(backup_dir):
            QMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
            return
        
        # Получаем список доступных резервных копий
        backups = os.listdir(backup_dir)
        if not backups:
            QMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
            return
        
        # Показываем диалог выбора резервной копии
        backup_name, ok = QInputDialog.getItem(self, "Выбор резервной копии", "Выберите резервную копию для восстановления:", backups, 0, False)
        if not ok:
            return
        
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Удаляем текущую версию
        for item in os.listdir("."):
            if item != backup_dir:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
        
        # Восстанавливаем резервную копию
        for item in os.listdir(backup_path):
            s = os.path.join(backup_path, item)
            d = os.path.join(".", item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks=True, ignore=None)
            else:
                shutil.copy2(s, d)
        
        QMessageBox.information(self, "Восстановление завершено", "Система успешно восстановлена из резервной копии.")
        self.update_backup_info()

    def delete_system_backup(self):
        """Удаляет выбранную резервную копию."""
        backup_dir = "system_backup"
        if not os.path.exists(backup_dir):
            QMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
            return
        
        # Получаем список доступных резервных копий
        backups = os.listdir(backup_dir)
        if not backups:
            QMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
            return
        
        # Показываем диалог выбора резервной копии для удаления
        backup_name, ok = QInputDialog.getItem(self, "Удаление резервной копии", "Выберите резервную копию для удаления:", backups, 0, False)
        if not ok:
            return
        
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Удаляем выбранную резервную копию
        shutil.rmtree(backup_path)
        
        QMessageBox.information(self, "Резервная копия удалена", f"Резервная копия {backup_name} успешно удалена.")
        self.update_backup_info()

    def update_backup_info(self):
        """Обновляет информацию о резервных копиях."""
        backup_dir = "system_backup"
        if os.path.exists(backup_dir):
            backups = os.listdir(backup_dir)
            if backups:
                self.backup_info_label.setText(f"Доступные резервные копии:")
                self.backup_list.clear()
                self.backup_list.addItems(backups)
                self.restore_backup_button.setEnabled(True)
                self.delete_backup_button.setEnabled(True)
            else:
                self.backup_info_label.setText("Резервные копии не созданы.")
                self.backup_list.clear()
                self.restore_backup_button.setEnabled(False)
                self.delete_backup_button.setEnabled(False)
        else:
            self.backup_info_label.setText("Резервные копии не созданы.")
            self.backup_list.clear()
            self.restore_backup_button.setEnabled(False)
            self.delete_backup_button.setEnabled(False)