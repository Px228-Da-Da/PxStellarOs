# import sys
# import os
# import datetime
# import shutil
# import platform
# from updater import get_current_version, get_latest_version, update_application, UPDATE_BRANCHES
# # from ScrollBar import CastScrollBar  # Добавленный импорт
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
# from dependencies import *

# class SettingsWindow(DraggableResizableWindow):
#     def __init__(self, parent=None, window_name="", translator=None, lang_code="en"):
#         super().__init__(parent)
#         self.tr = translator if translator else lambda x: x
#         self.parent_window = parent
#         self.window_name = window_name
#         self.lang_code = lang_code
#         self.setGeometry(300, 150, 500, 400)

#         main_widget = QWidget()
#         main_layout = QHBoxLayout(main_widget)

#         self.menu_list = QListWidget()
#         self.menu_list.setFixedWidth(180)
#         self.menu_list.addItem(self.tr("general"))
#         self.menu_list.addItem(self.tr("System Update"))
#         self.menu_list.addItem(self.tr("Backups"))
        
#         # Установка кастомного скроллбара для меню
#         self.menu_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
#         self.menu_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))

#         self.menu_list.setStyleSheet("""
#             QListWidget {
#                 background-color: #2E2E2E;
#                 color: #E0E0E0;
#                 border: none;
#                 padding-top: 10px;
#                 font-size: 15px;
#                 outline: none;
#             }
#             QListWidget::item {
#                 padding: 10px 10px;
#                 margin: 4px;
#                 border-radius: 8px;
#             }
#             QListWidget::item:selected {
#                 background-color: #4C8ED9;
#                 color: white;
#             }
#             QListWidget::item:hover {
#                 background-color: #3C3C3C;
#             }
#         """)

#         self.content_area = QStackedWidget()
#         self.content_area.setStyleSheet("background-color: #3B3B3B; color: white; font-size: 14px;")

#         general_page = QWidget()
#         general_layout = QVBoxLayout(general_page)
#         general_layout.addWidget(QLabel(self.tr("General settings")))
#         general_layout.addWidget(QPushButton(self.tr("Save changes")))
#         self.content_area.addWidget(general_page)

#         update_page = QWidget()
#         update_layout = QVBoxLayout(update_page)

#         self.current_version_label = QLabel(f"{self.tr('Current version')}: {get_current_version()}")
#         update_layout.addWidget(self.current_version_label)

#         update_layout.addWidget(QLabel(self.tr("Update branch") + ":"))
#         self.branch_combo = QComboBox()
#         self.branch_combo.addItems(UPDATE_BRANCHES.keys())
#         update_layout.addWidget(self.branch_combo)

#         self.check_update_button = QPushButton(self.tr("Check for updates"))
#         self.check_update_button.clicked.connect(self.check_for_updates)
#         update_layout.addWidget(self.check_update_button)

#         self.update_button = QPushButton(self.tr("Update system"))
#         self.update_button.clicked.connect(self.run_update)
#         self.update_button.setEnabled(False)
#         update_layout.addWidget(self.update_button)

#         self.rollback_button = QPushButton(self.tr("Rollback update"))
#         self.rollback_button.clicked.connect(self.rollback_update)
#         self.rollback_button.setEnabled(os.path.exists("backup"))
#         update_layout.addWidget(self.rollback_button)

#         self.content_area.addWidget(update_page)

#         backup_page = QWidget()
#         backup_layout = QVBoxLayout(backup_page)

#         self.backup_info_label = QLabel(self.tr("No backups created."))
#         backup_layout.addWidget(self.backup_info_label)

#         self.backup_list = QListWidget()
#         # Установка кастомного скроллбара для списка бэкапов
#         self.backup_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
#         self.backup_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
#         self.backup_list.setStyleSheet("background-color: #2E2E2E; color: white; font-size: 14px; border-radius: 8px;")
#         backup_layout.addWidget(self.backup_list)

#         self.create_backup_button = QPushButton(self.tr("Create system backup"))
#         self.create_backup_button.clicked.connect(self.create_system_backup)
#         backup_layout.addWidget(self.create_backup_button)

#         self.restore_backup_button = QPushButton(self.tr("Restore from backup"))
#         self.restore_backup_button.clicked.connect(self.restore_system_backup)
#         self.restore_backup_button.setEnabled(False)
#         backup_layout.addWidget(self.restore_backup_button)

#         self.delete_backup_button = QPushButton(self.tr("Delete backup"))
#         self.delete_backup_button.clicked.connect(self.delete_system_backup)
#         self.delete_backup_button.setEnabled(False)
#         backup_layout.addWidget(self.delete_backup_button)

#         self.content_area.addWidget(backup_page)

#         self.menu_list.currentRowChanged.connect(self.content_area.setCurrentIndex)

#         main_layout.addWidget(self.menu_list)
#         main_layout.addWidget(self.content_area)
#         main_widget.setLayout(main_layout)
#         self.set_content(main_widget)

#         # self.setStyleSheet("""
#         #     background-color: #3B3B3B; border-radius: 10px;
#         #     font-family: 'Ubuntu', sans-serif;
#         # """)

#         if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
#             self.parent_window.update_win_menu(self.window_name)

#         self.update_backup_info()
#         self.hide()


#     def check_for_updates(self):
#         selected_branch = UPDATE_BRANCHES[self.branch_combo.currentText()]
#         latest_version = get_latest_version(selected_branch)
#         current_version = get_current_version()

#         if latest_version and latest_version > current_version:
#             self.current_version_label.setText(
#                 f"{self.tr('Current version')}: {current_version}\n"
#                 f"{self.tr('New version available')} ({self.branch_combo.currentText()}): {latest_version}"
#             )
#             self.update_button.setEnabled(True)
#         else:
#             self.current_version_label.setText(
#                 f"{self.tr('Current version')}: {current_version}\n"
#                 f"{self.tr('No updates found in branch')} {self.branch_combo.currentText()}"
#             )
#             self.update_button.setEnabled(False)


#     def backup_current_version(self):
#         """Создает резервную копию текущей версии системы"""
#         backup_dir = "backup"
#         try:
#             # Создаем папку для резервной копии (если не существует)
#             if not os.path.exists(backup_dir):
#                 os.makedirs(backup_dir)
            
#             # Копируем все файлы и папки, кроме самой папки backup
#             for item in os.listdir("."):
#                 if item != backup_dir and not item.startswith('.'):  # Исключаем скрытые файлы/папки
#                     src_path = os.path.join(".", item)
#                     dst_path = os.path.join(backup_dir, item)
                    
#                     if os.path.isdir(src_path):
#                         # Для директорий используем copytree с dirs_exist_ok=True
#                         shutil.copytree(src_path, dst_path, symlinks=True, 
#                                       ignore=None, dirs_exist_ok=True)
#                     else:
#                         # Для файлов просто копируем
#                         shutil.copy2(src_path, dst_path)
#             return True
#         except Exception as e:
#             print(f"Backup error: {e}")
#             StellarMessageBox.critical(self, "Ошибка резервного копирования", 
#                                f"Не удалось создать резервную копию:\n{str(e)}")
#             return False

#     def rollback_update(self):
#         backup_dir = "backup"
#         if not os.path.exists(backup_dir):
#             StellarMessageBox.warning(self, self.tr("Error"), self.tr("Backup not found. Rollback not possible."))
#             return False

#         try:
#             for item in os.listdir("."):
#                 if item != backup_dir and not item.startswith('.'):
#                     item_path = os.path.join(".", item)
#                     if os.path.isdir(item_path):
#                         shutil.rmtree(item_path)
#                     else:
#                         os.remove(item_path)

#             for item in os.listdir(backup_dir):
#                 src_path = os.path.join(backup_dir, item)
#                 dst_path = os.path.join(".", item)
#                 if os.path.isdir(src_path):
#                     shutil.copytree(src_path, dst_path, symlinks=True, ignore=None, dirs_exist_ok=True)
#                 else:
#                     shutil.copy2(src_path, dst_path)

#             StellarMessageBox.information(self, self.tr("Rollback complete"), self.tr("Application restored to previous version."))
#             self.rollback_button.setEnabled(False)
#             return True
#         except Exception as e:
#             print(f"Rollback error: {e}")
#             StellarMessageBox.critical(self, self.tr("Rollback error"), f"{self.tr('Could not rollback system')}:\n{str(e)}")
#             return False


#     def run_update(self):
#         selected_branch = UPDATE_BRANCHES[self.branch_combo.currentText()]

#         if not self.backup_current_version():
#             self.current_version_label.setText(self.tr("Backup failed. Update cancelled."))
#             return

#         if update_application(selected_branch):
#             self.current_version_label.setText(
#                 f"{self.tr('Update completed')} ({self.branch_combo.currentText()}). {self.tr('Please restart the system.')}."
#             )
#             self.rollback_button.setEnabled(True)
#             self.reboot_system()
#         else:
#             self.current_version_label.setText(self.tr("Update failed. Attempting rollback..."))
#             if self.rollback_update():
#                 self.current_version_label.setText(self.tr("Rollback completed successfully."))
#             else:
#                 self.current_version_label.setText(self.tr("Rollback failed. System may be unstable."))

#     def reboot_system(self):
#         """
#         Перезагружает систему.
#         """
#         system_platform = platform.system()
#         if system_platform == "Windows":
#             # Команда для перезагрузки Windows
#             # os.system("shutdown /r /t 0")
#             StellarMessageBox.warning(self, "Ошибка", "Windows адаптер не найден")
#         elif system_platform == "Linux":
#             # Команда для перезагрузки Linux
#             os.system("reboot")
#         else:
#             print(f"Unsupported platform: {system_platform}")


#     def create_system_backup(self):
#         """Создает резервную копию системы."""
#         backup_dir = "system_backup"
#         if not os.path.exists(backup_dir):
#             os.makedirs(backup_dir)
        
#         # Создаем уникальное имя для резервной копии
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#         backup_name = f"backup_{timestamp}"
#         backup_path = os.path.join(backup_dir, backup_name)

#         # Копируем текущую версию в папку резервной копии
#         for item in os.listdir("."):
#             if item != backup_dir:
#                 s = os.path.join(".", item)
#                 d = os.path.join(backup_path, item)
#                 if os.path.isdir(s):
#                     shutil.copytree(s, d, symlinks=True, ignore=None)
#                 else:
#                     shutil.copy2(s, d)
        
#         StellarMessageBox.information(self, "Резервная копия создана", f"Резервная копия успешно создана: {backup_name}")
#         # self.update_backup_info()

#     def restore_system_backup(self):
#         """Восстанавливает систему из резервной копии."""
#         backup_dir = "system_backup"
#         if not os.path.exists(backup_dir):
#             StellarMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
#             return
        
#         # Получаем список доступных резервных копий
#         backups = os.listdir(backup_dir)
#         if not backups:
#             StellarMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
#             return
        
#         # Показываем диалог выбора резервной копии
#         backup_name, ok = QInputDialog.getItem(self, "Выбор резервной копии", "Выберите резервную копию для восстановления:", backups, 0, False)
#         if not ok:
#             return
        
#         backup_path = os.path.join(backup_dir, backup_name)
        
#         # Удаляем текущую версию
#         for item in os.listdir("."):
#             if item != backup_dir:
#                 if os.path.isdir(item):
#                     shutil.rmtree(item)
#                 else:
#                     os.remove(item)
        
#         # Восстанавливаем резервную копию
#         for item in os.listdir(backup_path):
#             s = os.path.join(backup_path, item)
#             d = os.path.join(".", item)
#             if os.path.isdir(s):
#                 shutil.copytree(s, d, symlinks=True, ignore=None)
#             else:
#                 shutil.copy2(s, d)
        
#         StellarMessageBox.information(self, "Восстановление завершено", "Система успешно восстановлена из резервной копии.")
#         self.update_backup_info()

#     def delete_system_backup(self):
#         """Удаляет выбранную резервную копию."""
#         backup_dir = "system_backup"
#         if not os.path.exists(backup_dir):
#             StellarMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
#             return
        
#         # Получаем список доступных резервных копий
#         backups = os.listdir(backup_dir)
#         if not backups:
#             StellarMessageBox.warning(self, "Ошибка", "Резервные копии не найдены.")
#             return
        
#         # Показываем диалог выбора резервной копии для удаления
#         backup_name, ok = QInputDialog.getItem(self, "Удаление резервной копии", "Выберите резервную копию для удаления:", backups, 0, False)
#         if not ok:
#             return
        
#         backup_path = os.path.join(backup_dir, backup_name)
        
#         # Удаляем выбранную резервную копию
#         shutil.rmtree(backup_path)
        
#         StellarMessageBox.information(self, "Резервная копия удалена", f"Резервная копия {backup_name} успешно удалена.")
#         self.update_backup_info()

#     def update_backup_info(self):
#         """Обновляет информацию о резервных копиях с поддержкой перевода."""
#         backup_dir = "system_backup"
#         if os.path.exists(backup_dir):
#             backups = os.listdir(backup_dir)
#             if backups:
#                 self.backup_info_label.setText(self.tr("Backups available:"))
#                 self.backup_list.clear()
#                 self.backup_list.addItems(backups)
#                 self.restore_backup_button.setEnabled(True)
#                 self.delete_backup_button.setEnabled(True)
#             else:
#                 self.backup_info_label.setText(self.tr("No backups created."))
#                 self.backup_list.clear()
#                 self.restore_backup_button.setEnabled(False)
#                 self.delete_backup_button.setEnabled(False)
#         else:
#             self.backup_info_label.setText(self.tr("No backups created."))
#             self.backup_list.clear()
#             self.restore_backup_button.setEnabled(False)
#             self.delete_backup_button.setEnabled(False)

import sys
import os
import datetime
import shutil
import platform
from updater import get_current_version, get_latest_version, update_application, UPDATE_BRANCHES

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *


class SettingsWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="", translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.parent_window = parent
        self.window_name = window_name
        self.lang_code = lang_code
        self.setGeometry(300, 150, 500, 400)
        self.setMinimumSize(500, 400)
        self.setMaximumSize(600, 500)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Меню ---
        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(180)
        self.menu_list.addItem(self.tr("System Update"))
        self.menu_list.addItem(self.tr("Backups"))
        self.menu_list.addItem(self.tr("Time"))
        self.menu_list.addItem(self.tr("Password"))
        self.menu_list.addItem(self.tr("persin"))


        self.menu_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.menu_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))

        self.menu_list.setStyleSheet("""
            QListWidget {
                background-color: #2E2E2E;
                color: #E0E0E0;
                border: none;
                padding-top: 10px;
                font-size: 15px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 10px;
                margin: 4px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background-color: #4C8ED9;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3C3C3C;
            }
        """)

        # --- Content ---
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #3B3B3B; color: white; font-size: 14px;")

        ##### --- System Update Page --- #####
        update_page = QWidget()
        update_layout = QVBoxLayout()
        update_layout.setSpacing(15)
        update_layout.setContentsMargins(28, 28, 28, 28)
        update_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label_update = QLabel(self.tr("System Update"))
        title_label_update.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 8px;")
        update_layout.addWidget(title_label_update)

        self.current_version_label = QLabel(f"{self.tr('Current version')}: {get_current_version()}")
        self.current_version_label.setStyleSheet("margin-bottom: 3px;")
        update_layout.addWidget(self.current_version_label)

        branch_row = QHBoxLayout()
        branch_row.setSpacing(8)
        branch_row.addWidget(QLabel(self.tr("Update branch") + ":"))
        self.branch_combo = ComboBox()
        self.branch_combo.addItems(UPDATE_BRANCHES.keys())
        self.branch_combo.setFixedWidth(140)
        branch_row.addWidget(self.branch_combo)
        branch_row.addStretch(1)
        update_layout.addLayout(branch_row)

        self.check_update_button = QPushButton(self.tr("Check for updates"))
        self.check_update_button.clicked.connect(self.check_for_updates)
        self.check_update_button.setMinimumHeight(32)
        update_layout.addWidget(self.check_update_button)

        self.update_button = QPushButton(self.tr("Update system"))
        self.update_button.clicked.connect(self.run_update)
        self.update_button.setEnabled(False)
        self.update_button.setMinimumHeight(32)
        update_layout.addWidget(self.update_button)

        self.rollback_button = QPushButton(self.tr("Rollback update"))
        self.rollback_button.clicked.connect(self.rollback_update)
        self.rollback_button.setEnabled(os.path.exists("backup"))
        self.rollback_button.setMinimumHeight(32)
        update_layout.addWidget(self.rollback_button)

        update_layout.addStretch(1)

        update_page.setLayout(update_layout)
        self.content_area.addWidget(update_page)

        ##### --- Backup Page --- #####
        backup_page = QWidget()
        backup_layout = QVBoxLayout()
        backup_layout.setSpacing(13)
        backup_layout.setContentsMargins(28, 28, 28, 28)
        backup_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.backup_info_label = QLabel(self.tr("No backups created."))
        self.backup_info_label.setStyleSheet("margin-bottom: 3px;")
        backup_layout.addWidget(self.backup_info_label)

        self.backup_list = QListWidget()
        self.backup_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.backup_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        self.backup_list.setStyleSheet("background-color: #2E2E2E; color: white; font-size: 14px; border-radius: 8px;")
        self.backup_list.setMinimumHeight(90)
        backup_layout.addWidget(self.backup_list)

        # Кнопки теперь идут друг под другом
        self.create_backup_button = QPushButton(self.tr("Create system backup"))
        self.create_backup_button.clicked.connect(self.create_system_backup)
        self.create_backup_button.setMinimumHeight(32)
        backup_layout.addWidget(self.create_backup_button)

        self.restore_backup_button = QPushButton(self.tr("Restore from backup"))
        self.restore_backup_button.clicked.connect(self.restore_system_backup)
        self.restore_backup_button.setEnabled(False)
        self.restore_backup_button.setMinimumHeight(32)
        backup_layout.addWidget(self.restore_backup_button)

        self.delete_backup_button = QPushButton(self.tr("Delete backup"))
        self.delete_backup_button.clicked.connect(self.delete_system_backup)
        self.delete_backup_button.setEnabled(False)
        self.delete_backup_button.setMinimumHeight(32)
        backup_layout.addWidget(self.delete_backup_button)

        backup_layout.addStretch(1)

        backup_page.setLayout(backup_layout)
        self.content_area.addWidget(backup_page)

        ##### --- Time Page --- #####
        time_page = QWidget()
        time_layout = QVBoxLayout()
        time_layout.setSpacing(14)
        time_layout.setContentsMargins(28, 28, 28, 28)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label_time = QLabel(self.tr("System time settings"))
        title_label_time.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 8px;")
        time_layout.addWidget(title_label_time)

        self.auto_time_button = QPushButton(self.tr("Set time automatically"))
        self.auto_time_button.clicked.connect(self.set_time_automatically)
        self.auto_time_button.setMinimumHeight(32)
        self.auto_time_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.10);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                color: white;
                font-size: 14px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.20);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.30);
            }
        """)
        time_layout.addWidget(self.auto_time_button)

        time_layout.addStretch(1)
        time_page.setLayout(time_layout)
        self.content_area.addWidget(time_page)

        ##### --- Password Page --- #####
        password_page = QWidget()
        password_layout = QVBoxLayout()
        password_layout.setSpacing(14)
        password_layout.setContentsMargins(28, 28, 28, 28)
        password_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label_pass = QLabel(self.tr("Change system password"))
        title_label_pass.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 8px;")
        password_layout.addWidget(title_label_pass)

        # Поле старого пароля
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_password_input.setPlaceholderText(self.tr("Current password"))
        self.old_password_input.setMinimumHeight(32)
        self.old_password_input.setStyleSheet("padding-left: 8px;")
        password_layout.addWidget(self.old_password_input)

        # Поле нового пароля
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText(self.tr("New password"))
        self.new_password_input.setMinimumHeight(32)
        self.new_password_input.setStyleSheet("padding-left: 8px;")
        password_layout.addWidget(self.new_password_input)

        # Кнопка сохранения
        self.save_password_button = QPushButton(self.tr("Save password"))
        self.save_password_button.clicked.connect(self.save_new_password)
        self.save_password_button.setMinimumHeight(32)
        self.save_password_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.10);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                color: white;
                font-size: 14px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.20);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.30);
            }
        """)
        password_row = QHBoxLayout()
        password_row.addWidget(self.save_password_button)
        password_row.addStretch(1)
        password_layout.addLayout(password_row)

        password_layout.addStretch(1)
        password_page.setLayout(password_layout)
        self.content_area.addWidget(password_page)
        ##### --- Персоналізація --- #####
        personalization_page = QWidget()
        personalization_layout = QVBoxLayout()
        personalization_layout.setSpacing(14)
        personalization_layout.setContentsMargins(28, 28, 28, 28)
        personalization_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title_label_pers = QLabel("Персоналізація")
        title_label_pers.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 8px;")
        personalization_layout.addWidget(title_label_pers)
        # Кнопка для зміни фону робочого столу
        self.change_wallpaper_button = QPushButton(self.tr("Change desktop background"))
        self.change_wallpaper_button.clicked.connect(self.change_wallpaper)
        self.change_wallpaper_button.setMinimumHeight(32)
        personalization_layout.addWidget(self.change_wallpaper_button)
        # Кнопка для зміни фону екрана блокування
        self.change_lock_button = QPushButton(self.tr("Change the background of the lock screen"))
        self.change_lock_button.clicked.connect(self.change_lock_screen)

        self.change_lock_button.setMinimumHeight(32)
        personalization_layout.addWidget(self.change_lock_button)
        personalization_layout.addStretch(1)
        personalization_page.setLayout(personalization_layout)
        self.content_area.addWidget(personalization_page)

                # === Поточний фон екрана блокування ===
        current_lock_label = QLabel(self.tr("Current lock screen background:"))
        current_lock_label.setStyleSheet("font-size: 14px; margin-top: 10px; margin-bottom: 4px;")
        personalization_layout.addWidget(current_lock_label)

        self.lock_preview = QLabel()
        self.lock_preview.setFixedSize(200, 120)
        self.lock_preview.setStyleSheet("border: 1px solid rgba(255,255,255,0.2); border-radius: 6px;")
        self.lock_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        personalization_layout.addWidget(self.lock_preview)

        # === Відкладене оновлення прев’ю ===
        QTimer.singleShot(300, self.update_lock_preview)


        # Завантажуємо поточне зображення
        self.update_lock_preview()



        # -------- Layout --------
        self.menu_list.currentRowChanged.connect(self.content_area.setCurrentIndex)
        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(self.content_area)
        main_widget.setLayout(main_layout)
        self.set_content(main_widget)

        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)
        
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.10);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                color: white;
                font-size: 14px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.20);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.30);
            }
            """
        for button in [self.check_update_button, self.update_button, self.rollback_button, self.create_backup_button, self.restore_backup_button, self.delete_backup_button, self.auto_time_button, self.save_password_button, self.change_lock_button, self.change_wallpaper_button]:
            button.setStyleSheet(button_style)


        self.update_backup_info()
        self.hide()

    def save_new_password(self):
        """Змінює пароль у файлі root/dataLacmi/user/password"""
        password_file = os.path.join("root", "dataLacmi", "user", "password")

        old_pass = self.old_password_input.text().strip()
        new_pass = self.new_password_input.text().strip()

        # Якщо новий пароль порожній — питаємо підтвердження
        if new_pass == "":
            reply = StellarMessageBox.question(
                self, self.tr("Empty password"),
                self.tr("Set empty password? (Screen will unlock without password)"))
            if reply != StellarMessageBox.StandardButton.Yes:
                return

        # Зчитуємо поточний пароль (якщо є)
        current_pass = ""
        if os.path.exists(password_file):
            try:
                with open(password_file, "r", encoding="utf-8") as f:
                    current_pass = f.read().strip()
            except Exception as e:
                StellarMessageBox.critical(self, self.tr("Error"), f"Cannot read password file:\n{e}")
                return

        # Перевіряємо старий пароль, якщо він заданий
        if current_pass and current_pass.lower() != "none" and old_pass != current_pass:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Incorrect current password."))
            return

        # Записуємо новий пароль
        try:
            with open(password_file, "w", encoding="utf-8") as f:
                if new_pass == "":
                    f.write("none")  # якщо пустий → режим без пароля
                else:
                    f.write(new_pass)
            StellarMessageBox.information(self, self.tr("Success"), self.tr("Password updated successfully."))
            self.old_password_input.clear()
            self.new_password_input.clear()
        except Exception as e:
            StellarMessageBox.critical(self, self.tr("Error"), f"Failed to save password:\n{e}")


    # --- Time sync ---
    def set_time_automatically(self):
        system_platform = platform.system()
        if system_platform == "Windows":
            try:
                result = os.system("w32tm /resync")
                if result != 0:
                    StellarMessageBox.warning(
                        self, self.tr("Access denied"),
                        self.tr("Run the program as Administrator to sync time.")
                    )
                else:
                    StellarMessageBox.information(
                        self, self.tr("Success"),
                        self.tr("Time synchronized successfully.")
                    )
            except Exception as e:
                StellarMessageBox.critical(self, self.tr("Error"),
                    f"{self.tr('Failed to set time automatically')}: {e}")
        elif system_platform == "Linux":
            os.system("timedatectl set-ntp true")
            StellarMessageBox.information(self, self.tr("Success"),
                                          self.tr("NTP synchronization enabled."))

    # --- Update system ---
    def check_for_updates(self):
        selected_branch = UPDATE_BRANCHES[self.branch_combo.currentText()]
        latest_version = get_latest_version(selected_branch)
        current_version = get_current_version()

        if latest_version and latest_version > current_version:
            self.current_version_label.setText(
                f"{self.tr('Current version')}: {current_version}\n"
                f"{self.tr('New version available')} ({self.branch_combo.currentText()}): {latest_version}"
            )
            self.update_button.setEnabled(True)
        else:
            self.current_version_label.setText(
                f"{self.tr('Current version')}: {current_version}\n"
                f"{self.tr('No updates found in branch')} {self.branch_combo.currentText()}"
            )
            self.update_button.setEnabled(False)

    def backup_current_version(self):
        backup_dir = "backup"
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            for item in os.listdir("."):
                if item != backup_dir and not item.startswith('.'):
                    src_path = os.path.join(".", item)
                    dst_path = os.path.join(backup_dir, item)
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path, symlinks=True, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            StellarMessageBox.critical(self, self.tr("Backup error"),
                                       self.tr(f"Failed to create backup:\n{str(e)}"))
            return False

    def rollback_update(self):
        backup_dir = "backup"
        if not os.path.exists(backup_dir):
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Backup not found. Rollback not possible."))
            return False
        try:
            for item in os.listdir("."):
                if item != backup_dir and not item.startswith('.'):
                    item_path = os.path.join(".", item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
            for item in os.listdir(backup_dir):
                src_path = os.path.join(backup_dir, item)
                dst_path = os.path.join(".", item)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, symlinks=True, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dst_path)
            StellarMessageBox.information(self, self.tr("Rollback complete"),
                                          self.tr("Application restored to previous version."))
            self.rollback_button.setEnabled(False)
            return True
        except Exception as e:
            print(f"Rollback error: {e}")
            StellarMessageBox.critical(self, self.tr("Rollback error"),
                                       f"{self.tr('Could not rollback system')}:\n{str(e)}")
            return False

    def run_update(self):
        selected_branch = UPDATE_BRANCHES[self.branch_combo.currentText()]
        if not self.backup_current_version():
            self.current_version_label.setText(self.tr("Backup failed. Update cancelled."))
            return
        if update_application(selected_branch):
            self.current_version_label.setText(
                f"{self.tr('Update completed')} ({self.branch_combo.currentText()}). {self.tr('Please restart the system.')}"
            )
            self.rollback_button.setEnabled(True)
            self.reboot_system()
        else:
            self.current_version_label.setText(self.tr("Update failed. Attempting rollback..."))
            if self.rollback_update():
                self.current_version_label.setText(self.tr("Rollback completed successfully."))
            else:
                self.current_version_label.setText(self.tr("Rollback failed. System may be unstable."))

    def reboot_system(self):
        system_platform = platform.system()
        if system_platform == "Windows":
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Windows adapter not found"))
        elif system_platform == "Linux":
            os.system("reboot")
        else:
            print(f"{self.tr('Unsupported platform')}: {system_platform}")

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
        StellarMessageBox.information(self, self.tr("Backup created"),
                                      self.tr(f"Backup successfully created: {backup_name}"))

    def restore_system_backup(self):
        backup_dir = "system_backup"
        if not os.path.exists(backup_dir):
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("No backups found."))
            return
        backups = os.listdir(backup_dir)
        if not backups:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("No backups found."))
            return
        backup_name, ok = QInputDialog.getItem(self, self.tr("Select backup"),
                                               self.tr("Select a backup to restore:"), backups, 0, False)
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
        StellarMessageBox.information(self, self.tr("Restore completed"),
                                      self.tr("System successfully restored from backup."))
        self.update_backup_info()

    def delete_system_backup(self):
        backup_dir = "system_backup"
        if not os.path.exists(backup_dir):
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("No backups found."))
            return
        backups = os.listdir(backup_dir)
        if not backups:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("No backups found."))
            return
        backup_name, ok = QInputDialog.getItem(self, self.tr("Delete backup"),
                                               self.tr("Select a backup to delete:"), backups, 0, False)
        if not ok:
            return
        backup_path = os.path.join(backup_dir, backup_name)
        shutil.rmtree(backup_path)
        StellarMessageBox.information(self, self.tr("Backup deleted"),
                                      self.tr(f"Backup {backup_name} successfully deleted."))

    def update_backup_info(self):
        backup_dir = "system_backup"
        if os.path.exists(backup_dir):
            backups = os.listdir(backup_dir)
            if backups:
                self.backup_info_label.setText(self.tr("Backups available:"))
                self.backup_list.clear()
                self.backup_list.addItems(backups)
                self.restore_backup_button.setEnabled(True)
                self.delete_backup_button.setEnabled(True)
            else:
                self.backup_info_label.setText(self.tr("No backups created."))
                self.backup_list.clear()
                self.restore_backup_button.setEnabled(False)
                self.delete_backup_button.setEnabled(False)
        else:
            self.backup_info_label.setText(self.tr("No backups created."))
            self.backup_list.clear()
            self.restore_backup_button.setEnabled(False)
            self.delete_backup_button.setEnabled(False)

    def change_wallpaper(self):
        """Змінює фон робочого столу і записує шлях у desk.config"""
        file_path, _ = CustomFileDialog.getOpenFileName(
            self,
            self.tr("Виберіть зображення для фону робочого столу"),
            "",
            "Зображення (*.png *.jpg *.jpeg);;Усі файли (*)"
        )

        if file_path:
            try:
                # === Копіюємо картинку ===
                dest_path = os.path.join("bin", "icons", "local_icons", "IconOs", "wallpaper.jpg")
                shutil.copy(file_path, dest_path)

                # === Оновлюємо конфіг ===
                config_path = os.path.join("root", "user", "desk", "desk.config")
                data = {}

                # Якщо існує — читаємо
                if os.path.exists(config_path):
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    except Exception:
                        data = {}

                # Оновлюємо або створюємо ключ
                data["wallpaper_path"] = file_path

                # Записуємо назад
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                # Повідомлення
                StellarMessageBox.information(
                    self,
                    self.tr("Успішно"),
                    self.tr("Фон робочого столу змінено.")
                )

            except Exception as e:
                StellarMessageBox.critical(
                    self,
                    self.tr("Помилка"),
                    f"{self.tr('Не вдалося змінити фон')}: {str(e)}"
                )


    def change_lock_screen(self):
        """Змінює фон екрана блокування і записує шлях у desk.config"""
        import json, os, shutil

        file_path, _ = CustomFileDialog.getOpenFileName(
            self,
            self.tr("Виберіть зображення для екрана блокування"),
            "",
            "Зображення (*.png *.jpg *.jpeg);;Усі файли (*)"
        )

        if file_path:
            try:
                # === Копіюємо зображення ===
                dest_path = os.path.join("bin", "icons", "local_icons", "IconOs", "lock.jpg")
                shutil.copy(file_path, dest_path)

                # === Оновлюємо desk.config ===
                config_path = os.path.join("root", "user", "desk", "desk.config")
                data = {}

                if os.path.exists(config_path):
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    except Exception:
                        data = {}

                data["lockscreen_path"] = file_path

                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                StellarMessageBox.information(
                    self,
                    self.tr("Успішно"),
                    self.tr("Фон екрана блокування змінено.")
                )

                # 🔥 Оновлюємо прев’ю після зміни
                if hasattr(self, "update_lock_preview"):
                    self.update_lock_preview()

            except Exception as e:
                StellarMessageBox.critical(
                    self,
                    self.tr("Помилка"),
                    f"{self.tr('Не вдалося змінити фон блокування')}: {str(e)}"
                )


    def update_lock_preview(self):
        """Оновлює прев’ю поточного фону екрана блокування"""
        import json, os

        if not hasattr(self, "lock_preview") or self.lock_preview is None:
            return

        config_path = os.path.join("root", "user", "desk", "desk.config")
        image_path = None

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    image_path = data.get("lockscreen_path") or data.get("lock_screen_path")
            except Exception as e:
                print(f"[update_lock_preview] Помилка читання desk.config: {e}")

        if not image_path or not os.path.exists(image_path):
            image_path = os.path.join("bin", "icons", "local_icons", "IconOs", "lock.jpg")

        pixmap = QPixmap(image_path).scaled(
            self.lock_preview.width(),
            self.lock_preview.height(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lock_preview.setPixmap(pixmap)
