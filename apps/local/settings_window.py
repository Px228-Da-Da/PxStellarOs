from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QListWidget, QStackedWidget, QPushButton, 
    QHBoxLayout, QMessageBox, QFileDialog, QInputDialog, QComboBox
)
from apps.local.init import DraggableResizableWindow
from updater import get_current_version, get_latest_version, update_application, UPDATE_BRANCHES
import shutil
import os
import datetime

class SettingsWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name=""):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name
        self.setGeometry(300, 150, 500, 400)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(180)
        self.menu_list.addItem("Общие")
        self.menu_list.addItem("Обновление системы")
        self.menu_list.addItem("Резервная копия ОС")
        self.menu_list.setStyleSheet("""
            background-color: #2E2E2E; color: white; font-size: 14px;
            border-right: 1px solid #555; padding: 5px;
        """)

        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #3B3B3B; color: white; font-size: 14px;")

        # Общие настройки
        general_page = QWidget()
        general_layout = QVBoxLayout(general_page)
        general_layout.addWidget(QLabel("Общие настройки"))
        general_layout.addWidget(QPushButton("Сохранить изменения"))
        self.content_area.addWidget(general_page)

        # Обновление системы
        update_page = QWidget()
        update_layout = QVBoxLayout(update_page)

        # Выбор ветки обновления
        update_layout.addWidget(QLabel("Ветка обновления:"))
        self.branch_combo = QComboBox()
        self.branch_combo.addItems(UPDATE_BRANCHES.keys())
        update_layout.addWidget(self.branch_combo)

        self.current_version_label = QLabel(f"Текущая версия: {get_current_version()}")
        update_layout.addWidget(self.current_version_label)

        self.check_update_button = QPushButton("Проверить обновления")
        self.check_update_button.clicked.connect(self.check_for_updates)
        update_layout.addWidget(self.check_update_button)

        self.update_button = QPushButton("Обновить систему")
        self.update_button.clicked.connect(self.run_update)
        self.update_button.setEnabled(False)
        update_layout.addWidget(self.update_button)

        self.rollback_button = QPushButton("Откат обновления")
        self.rollback_button.clicked.connect(self.rollback_update)
        self.rollback_button.setEnabled(os.path.exists("backup"))
        update_layout.addWidget(self.rollback_button)

        self.content_area.addWidget(update_page)

        # Резервная копия ОС
        backup_page = QWidget()
        backup_layout = QVBoxLayout(backup_page)

        self.backup_info_label = QLabel("Резервные копии не созданы.")
        backup_layout.addWidget(self.backup_info_label)

        self.backup_list = QListWidget()
        self.backup_list.setStyleSheet("background-color: #2E2E2E; color: white; font-size: 14px;")
        backup_layout.addWidget(self.backup_list)

        self.create_backup_button = QPushButton("Создать резервную копию")
        self.create_backup_button.clicked.connect(self.create_system_backup)
        backup_layout.addWidget(self.create_backup_button)

        self.restore_backup_button = QPushButton("Восстановить из резервной копии")
        self.restore_backup_button.clicked.connect(self.restore_system_backup)
        self.restore_backup_button.setEnabled(False)
        backup_layout.addWidget(self.restore_backup_button)

        self.delete_backup_button = QPushButton("Удалить резервную копию")
        self.delete_backup_button.clicked.connect(self.delete_system_backup)
        self.delete_backup_button.setEnabled(False)
        backup_layout.addWidget(self.delete_backup_button)

        self.content_area.addWidget(backup_page)

        self.menu_list.currentRowChanged.connect(self.content_area.setCurrentIndex)

        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(self.content_area)

        main_widget.setLayout(main_layout)
        self.set_content(main_widget)

        self.setStyleSheet("""
            background-color: #2E2E2E; border-radius: 10px;
            font-family: 'Ubuntu', sans-serif;
        """)

        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)

        self.update_backup_info()
        self.hide()

    def check_for_updates(self):
        selected_branch = UPDATE_BRANCHES[self.branch_combo.currentText()]
        latest_version = get_latest_version(selected_branch)
        current_version = get_current_version()

        if latest_version and latest_version > current_version:
            self.current_version_label.setText(
                f"Текущая версия: {current_version}\n"
                f"Доступна новая версия ({self.branch_combo.currentText()}): {latest_version}"
            )
            self.update_button.setEnabled(True)
        else:
            self.current_version_label.setText(
                f"Текущая версия: {current_version}\n"
                f"Обновлений не найдено в ветке {self.branch_combo.currentText()}"
            )
            self.update_button.setEnabled(False)

    def backup_current_version(self):
        backup_dir = "backup"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        for item in os.listdir("."):
            if item != backup_dir:
                s = os.path.join(".", item)
                d = os.path.join(backup_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks=True, ignore=None)
                else:
                    shutil.copy2(s, d)

    def rollback_update(self):
        backup_dir = "backup"
        if not os.path.exists(backup_dir):
            QMessageBox.warning(self, "Ошибка", "Резервная копия не найдена. Откат невозможен.")
            return False
        
        for item in os.listdir("."):
            if item != backup_dir:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
        
        for item in os.listdir(backup_dir):
            s = os.path.join(backup_dir, item)
            d = os.path.join(".", item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks=True, ignore=None)
            else:
                shutil.copy2(s, d)
        
        QMessageBox.information(self, "Откат завершен", "Приложение восстановлено до предыдущей версии.")
        self.rollback_button.setEnabled(False)
        return True

    def run_update(self):
        selected_branch = UPDATE_BRANCHES[self.branch_combo.currentText()]
        self.backup_current_version()
        
        if update_application(selected_branch):
            self.current_version_label.setText(
                f"Обновление завершено (ветка {self.branch_combo.currentText()}). Перезапустите ос."
            )
            self.rollback_button.setEnabled(True)
        else:
            self.current_version_label.setText("Ошибка при обновлении. Попытка отката...")
            if self.rollback_update():
                self.current_version_label.setText("Откат выполнен успешно.")
            else:
                self.current_version_label.setText("Откат не удался.")

    def create_system_backup(self):
        backup_dir = "system_backup"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)

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
        backup_dir = "system_backup"
        if not os.path.exists(backup_dir):
            QMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
            return
        
        backups = os.listdir(backup_dir)
        if not backups:
            QMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
            return
        
        backup_name, ok = QInputDialog.getItem(
            self, "Выбор резервной копии", 
            "Выберите резервную копию для восстановления:", 
            backups, 0, False
        )
        if not ok:
            return
        
        backup_path = os.path.join(backup_dir, backup_name)
        
        for item in os.listdir("."):
            if item != backup_dir:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
        
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
        backup_dir = "system_backup"
        if not os.path.exists(backup_dir):
            QMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
            return
        
        backups = os.listdir(backup_dir)
        if not backups:
            QMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
            return
        
        backup_name, ok = QInputDialog.getItem(
            self, "Удаление резервной копии", 
            "Выберите резервную копию для удаления:", 
            backups, 0, False
        )
        if not ok:
            return
        
        backup_path = os.path.join(backup_dir, backup_name)
        shutil.rmtree(backup_path)
        
        QMessageBox.information(self, "Резервная копия удалена", f"Резервная копия {backup_name} успешно удалена.")
        self.update_backup_info()

    def update_backup_info(self):
        backup_dir = "system_backup"
        if os.path.exists(backup_dir):
            backups = os.listdir(backup_dir)
            if backups:
                self.backup_info_label.setText("Доступные резервные копии:")
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