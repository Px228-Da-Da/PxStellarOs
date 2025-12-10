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
        self.setGeometry(300, 150, 557, 400)
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
        self.old_password_input = InputPassword(
                parent=password_page,
                placeholder_text=self.tr("Password"),
                initial_text="",
                echo_mode=QLineEdit.EchoMode.Password,
                translator=self.tr
            )
        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_password_input.setPlaceholderText(self.tr("Current password"))
        self.old_password_input.setMinimumHeight(32)
        self.old_password_input.setStyleSheet("padding-left: 8px;")
        password_layout.addWidget(self.old_password_input)

        # Поле нового пароля
        self.new_password_input = InputPassword(
                parent=password_page,
                placeholder_text=self.tr("Password"),
                initial_text="",
                echo_mode=QLineEdit.EchoMode.Password,
                translator=self.tr
            )
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

        # --- Основний layout ---
        personalization_layout = QVBoxLayout()
        personalization_layout.setSpacing(16)
        personalization_layout.setContentsMargins(28, 28, 28, 28)
        personalization_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label_pers = QLabel("Персоналізація")
        title_label_pers.setStyleSheet("font-size: 18px; font-weight: 600; margin-bottom: 8px;")
        personalization_layout.addWidget(title_label_pers)

        # --- Кнопки ---
        self.change_wallpaper_button = QPushButton(self.tr("Змінити фон робочого столу"))
        self.change_lock_button = QPushButton(self.tr("Змінити фон екрана блокування"))
        for btn in [self.change_wallpaper_button, self.change_lock_button]:
            btn.setMinimumHeight(36)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255,255,255,0.08);
                    border: 1px solid rgba(255,255,255,0.25);
                    border-radius: 6px;
                    color: white;
                    font-size: 14px;
                    padding: 6px 10px;
                }
                QPushButton:hover {
                    background-color: rgba(255,255,255,0.15);
                }
                QPushButton:pressed {
                    background-color: rgba(255,255,255,0.25);
                }
            """)
        self.change_wallpaper_button.clicked.connect(self.change_wallpaper)
        self.change_lock_button.clicked.connect(self.change_lock_screen)
        personalization_layout.addWidget(self.change_wallpaper_button)
        personalization_layout.addWidget(self.change_lock_button)

        # --- Поточний фон екрана блокування ---
        current_lock_label = QLabel(self.tr("Поточний фон екрана блокування:"))
        current_lock_label.setStyleSheet("font-size: 14px; margin-top: 15px; margin-bottom: 4px;")
        personalization_layout.addWidget(current_lock_label)

        self.lock_preview = QLabel()
        self.lock_preview.setFixedSize(240, 135)
        self.lock_preview.setStyleSheet("""
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: 8px;
            background-color: #2E2E2E;
        """)
        self.lock_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        personalization_layout.addWidget(self.lock_preview, alignment=Qt.AlignmentFlag.AlignLeft)

        QTimer.singleShot(300, self.update_lock_preview)
        self.update_lock_preview()

                # === Параметри елементів (time_button) ===
        params_group = QGroupBox("Параметри елемента time_button")
        params_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                margin-top: 14px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                top: -6px;
                background-color: #3B3B3B;
                padding: 0 6px;
            }
        """)

        # --- Форма полів ---
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(8)
        form_layout.setHorizontalSpacing(10)

        widgets_path = os.path.join("bin", "sys", "path", "widgets.json")
        try:
            with open(widgets_path, "r", encoding="utf-8") as f:
                widgets_data = json.load(f)
            time_data = widgets_data.get("time_button", {})
            clock_widget_sec = widgets_data.get("clock_widget_sec", False)
            lock_clock_sec = widgets_data.get("lock_clock_sec", False)
        except Exception:
            time_data = {}
            clock_widget_sec = False
            lock_clock_sec = False

        def make_input(value):
            field = Input(
                parent=self,
                initial_text="" if value is None else str(value),
                translator=self.tr
            )
            field.setFixedWidth(100)
            field.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 4px;
                    color: white;
                    padding: 3px 6px;
                }
                QLineEdit:focus {
                    border: 1px solid #4C8ED9;
                }
            """)
            return field

        self.x_input = make_input(time_data.get("x", 0))
        self.y_input = make_input(time_data.get("y", 0))
        self.w_input = make_input(time_data.get("width", 0))
        self.h_input = make_input(time_data.get("height", 0))

        labels = ["x:", "y:", "width:", "height:"]
        fields = [self.x_input, self.y_input, self.w_input, self.h_input]
        for i in range(4):
            lbl = QLabel(labels[i])
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            form_layout.addWidget(lbl, i, 0)
            form_layout.addWidget(fields[i], i, 1)

        # --- Чекбокси ---
        self.clock_widget_sec_checkbox = QCheckBox("Відображати секунди (на віджеті годинника)")
        self.clock_widget_sec_checkbox.setChecked(clock_widget_sec)
        self.clock_widget_sec_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 13px;
                padding: 2px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid rgba(255,255,255,0.4);
                background-color: rgba(255,255,255,0.1);
            }
            QCheckBox::indicator:checked {
                background-color: #4C8ED9;
                border: 1px solid #4C8ED9;
            }
        """)
        form_layout.addWidget(self.clock_widget_sec_checkbox, 4, 0, 1, 2)

        self.lock_clock_sec_checkbox = QCheckBox("Відображати секунди (екран блокування)")
        self.lock_clock_sec_checkbox.setChecked(lock_clock_sec)
        self.lock_clock_sec_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 13px;
                padding: 2px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid rgba(255,255,255,0.4);
                background-color: rgba(255,255,255,0.1);
            }
            QCheckBox::indicator:checked {
                background-color: #4C8ED9;
                border: 1px solid #4C8ED9;
            }
        """)
        form_layout.addWidget(self.lock_clock_sec_checkbox, 5, 0, 1, 2)

        # --- Кнопка збереження ---
        save_btn = QPushButton("💾 Зберегти параметри")
        save_btn.setMinimumHeight(34)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4C8ED9;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #5FA2EB; }
            QPushButton:pressed { background-color: #3C78C0; }
        """)

        def save_time_button():
            try:
                with open(widgets_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # створюємо розділ, якщо його немає
                if "time_button" not in data:
                    data["time_button"] = {}

                # оновлюємо параметри
                data["time_button"]["x"] = int(self.x_input.text())
                data["time_button"]["y"] = int(self.y_input.text())
                data["time_button"]["width"] = int(self.w_input.text())
                data["time_button"]["height"] = int(self.h_input.text())
                data["clock_widget_sec"] = self.clock_widget_sec_checkbox.isChecked()
                data["lock_clock_sec"] = self.lock_clock_sec_checkbox.isChecked()

                with open(widgets_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                StellarMessageBox.information(self, "Успішно", "Параметри time_button збережено.")
                # 🔥 миттєве оновлення без перезапуску
                if self.parent_window and hasattr(self.parent_window, "reload_widgets"):
                    self.parent_window.reload_widgets()

            except Exception as e:
                StellarMessageBox.critical(self, "Помилка", f"Не вдалося зберегти: {e}")

        save_btn.clicked.connect(save_time_button)
        form_layout.addWidget(save_btn, 6, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        params_group.setLayout(form_layout)
        personalization_layout.addWidget(params_group)


                # === Параметри елементів (volume_button) ===
        volume_group = QGroupBox("Параметри елемента volume_button")
        volume_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                margin-top: 14px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                top: -6px;
                background-color: #3B3B3B;
                padding: 0 6px;
            }
        """)

        # --- Форма полів ---
        volume_layout = QGridLayout()
        volume_layout.setVerticalSpacing(8)
        volume_layout.setHorizontalSpacing(10)

        try:
            with open(widgets_path, "r", encoding="utf-8") as f:
                widgets_data = json.load(f)
            volume_data = widgets_data.get("volume_button", {})
        except Exception:
            volume_data = {}

        def make_volume_input(value):
            field = Input(
                parent=self,
                initial_text="" if value is None else str(value),
                translator=self.tr
            )
            field.setFixedWidth(100)
            field.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 4px;
                    color: white;
                    padding: 3px 6px;
                }
                QLineEdit:focus {
                    border: 1px solid #4C8ED9;
                }
            """)
            return field

        self.v_x_input = make_volume_input(volume_data.get("x", 0))
        self.v_y_input = make_volume_input(volume_data.get("y", 0))
        self.v_w_input = make_volume_input(volume_data.get("width", 0))
        self.v_h_input = make_volume_input(volume_data.get("height", 0))

        v_labels = ["x:", "y:", "width:", "height:"]
        v_fields = [self.v_x_input, self.v_y_input, self.v_w_input, self.v_h_input]
        for i in range(4):
            lbl = QLabel(v_labels[i])
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            volume_layout.addWidget(lbl, i, 0)
            volume_layout.addWidget(v_fields[i], i, 1)

        # --- Кнопка збереження ---
        volume_save_btn = QPushButton("💾 Зберегти параметри")
        volume_save_btn.setMinimumHeight(34)
        volume_save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4C8ED9;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #5FA2EB; }
            QPushButton:pressed { background-color: #3C78C0; }
        """)

        def save_volume_button():
            try:
                with open(widgets_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "volume_button" not in data:
                    data["volume_button"] = {}
                data["volume_button"]["x"] = int(self.v_x_input.text())
                data["volume_button"]["y"] = int(self.v_y_input.text())
                data["volume_button"]["width"] = int(self.v_w_input.text())
                data["volume_button"]["height"] = int(self.v_h_input.text())

                with open(widgets_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                StellarMessageBox.information(self, "Успішно", "Параметри volume_button збережено.")
                # 🔥 миттєве оновлення без перезапуску
                if self.parent_window and hasattr(self.parent_window, "reload_widgets"):
                    self.parent_window.reload_widgets()
            except Exception as e:
                StellarMessageBox.critical(self, "Помилка", f"Не вдалося зберегти: {e}")

        volume_save_btn.clicked.connect(save_volume_button)
        volume_layout.addWidget(volume_save_btn, 6, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        volume_group.setLayout(volume_layout)
        personalization_layout.addWidget(volume_group)

                # === Параметри елементів (wifi_button) ===
        wifi_group = QGroupBox("Параметри елемента wifi_button")
        wifi_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                margin-top: 14px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                top: -6px;
                background-color: #3B3B3B;
                padding: 0 6px;
            }
        """)

        wifi_form = QGridLayout()
        wifi_form.setVerticalSpacing(8)
        wifi_form.setHorizontalSpacing(10)

        try:
            with open(widgets_path, "r", encoding="utf-8") as f:
                widgets_data = json.load(f)
            wifi_data = widgets_data.get("wifi_button", {})
        except Exception:
            wifi_data = {}

        def make_wifi_input(value):
            field = Input(
                parent=self,
                initial_text="" if value is None else str(value),
                translator=self.tr
            )
            field.setFixedWidth(100)
            field.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 4px;
                    color: white;
                    padding: 3px 6px;
                }
                QLineEdit:focus {
                    border: 1px solid #4C8ED9;
                }
            """)
            return field

        self.wifi_x_input = make_wifi_input(wifi_data.get("x", 0))
        self.wifi_y_input = make_wifi_input(wifi_data.get("y", 0))
        self.wifi_w_input = make_wifi_input(wifi_data.get("width", 0))
        self.wifi_h_input = make_wifi_input(wifi_data.get("height", 0))

        wifi_labels = ["x:", "y:", "width:", "height:"]
        wifi_fields = [self.wifi_x_input, self.wifi_y_input, self.wifi_w_input, self.wifi_h_input]

        for i in range(4):
            lbl = QLabel(wifi_labels[i])
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            wifi_form.addWidget(lbl, i, 0)
            wifi_form.addWidget(wifi_fields[i], i, 1)

        wifi_save_btn = QPushButton("💾 Зберегти параметри")
        wifi_save_btn.setMinimumHeight(34)
        wifi_save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4C8ED9;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #5FA2EB; }
            QPushButton:pressed { background-color: #3C78C0; }
        """)

        def save_wifi_button():
            try:
                with open(widgets_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "wifi_button" not in data:
                    data["wifi_button"] = {}
                data["wifi_button"]["x"] = int(self.wifi_x_input.text())
                data["wifi_button"]["y"] = int(self.wifi_y_input.text())
                data["wifi_button"]["width"] = int(self.wifi_w_input.text())
                data["wifi_button"]["height"] = int(self.wifi_h_input.text())
                with open(widgets_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                StellarMessageBox.information(self, "Успішно", "Параметри wifi_button збережено.")
                # 🔥 миттєве оновлення без перезапуску
                if self.parent_window and hasattr(self.parent_window, "reload_widgets"):
                    self.parent_window.reload_widgets()
            except Exception as e:
                StellarMessageBox.critical(self, "Помилка", f"Не вдалося зберегти: {e}")

        wifi_save_btn.clicked.connect(save_wifi_button)
        wifi_form.addWidget(wifi_save_btn, 5, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        wifi_group.setLayout(wifi_form)
        personalization_layout.addWidget(wifi_group)

                # === Параметри елемента (start_button) ===
        start_params_group = QGroupBox("Параметри елемента start_button")
        start_params_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                margin-top: 14px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                top: -6px;
                background-color: #3B3B3B;
                padding: 0 6px;
            }
        """)

        start_form_layout = QGridLayout()
        start_form_layout.setVerticalSpacing(8)
        start_form_layout.setHorizontalSpacing(10)

        try:
            with open(widgets_path, "r", encoding="utf-8") as f:
                widgets_data = json.load(f)
            start_data = widgets_data.get("start_button", {})
        except Exception:
            start_data = {}

        def make_input_start(value):
            field = Input(
                parent=self,
                initial_text="" if value is None else str(value),
                translator=self.tr
            )
            field.setFixedWidth(100)
            field.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 4px;
                    color: white;
                    padding: 3px 6px;
                }
                QLineEdit:focus {
                    border: 1px solid #4C8ED9;
                }
            """)
            return field

        self.start_x_input = make_input_start(start_data.get("x", 0))
        self.start_y_input = make_input_start(start_data.get("y", 0))
        self.start_w_input = make_input_start(start_data.get("width", 0))
        self.start_h_input = make_input_start(start_data.get("height", 0))

        start_labels = ["x:", "y:", "width:", "height:"]
        start_fields = [self.start_x_input, self.start_y_input, self.start_w_input, self.start_h_input]
        for i in range(4):
            lbl = QLabel(start_labels[i])
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            start_form_layout.addWidget(lbl, i, 0)
            start_form_layout.addWidget(start_fields[i], i, 1)

        # --- Кнопка збереження ---
        save_start_btn = QPushButton("💾 Зберегти параметри")
        save_start_btn.setMinimumHeight(34)
        save_start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4C8ED9;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #5FA2EB; }
            QPushButton:pressed { background-color: #3C78C0; }
        """)

        def save_start_button():
            try:
                with open(widgets_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "start_button" not in data:
                    data["start_button"] = {}
                data["start_button"]["x"] = int(self.start_x_input.text())
                data["start_button"]["y"] = int(self.start_y_input.text())
                data["start_button"]["width"] = int(self.start_w_input.text())
                data["start_button"]["height"] = int(self.start_h_input.text())
                with open(widgets_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                StellarMessageBox.information(self, "Успішно", "Параметри start_button збережено.")
                # 🔥 миттєве оновлення без перезапуску
                if self.parent_window and hasattr(self.parent_window, "reload_widgets"):
                    self.parent_window.reload_widgets()
            except Exception as e:
                StellarMessageBox.critical(self, "Помилка", f"Не вдалося зберегти: {e}")

        save_start_btn.clicked.connect(save_start_button)
        start_form_layout.addWidget(save_start_btn, 5, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        start_params_group.setLayout(start_form_layout)
        personalization_layout.addWidget(start_params_group)

                # === СИСТЕМНІ ВІДСТУПИ ТА ВИСОТА ДОКУ ===
        offsets_group = QGroupBox("Системні відступи та висота доку")
        offsets_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                margin-top: 14px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                top: -6px;
                background-color: #3B3B3B;
                padding: 0 6px;
            }
        """)

        offsets_layout = QGridLayout()
        offsets_layout.setVerticalSpacing(8)
        offsets_layout.setHorizontalSpacing(10)

        try:
            with open(widgets_path, "r", encoding="utf-8") as f:
                widgets_data = json.load(f)
            dock_height = widgets_data.get("dock_height", 45)
            top_offset = widgets_data.get("top_offset", 0)
            bottom_offset = widgets_data.get("bottom_offset", 0)
            left_offset = widgets_data.get("left_offset", 0)
            right_offset = widgets_data.get("right_offset", 0)
        except Exception:
            dock_height = 45
            top_offset = bottom_offset = left_offset = right_offset = 0

        def make_offset_input(value):
            field = Input(
                parent=self,
                initial_text="" if value is None else str(value),
                translator=self.tr
            )
            field.setFixedWidth(100)
            field.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 4px;
                    color: white;
                    padding: 3px 6px;
                }
                QLineEdit:focus {
                    border: 1px solid #4C8ED9;
                }
            """)
            return field

        self.dock_height_input = make_offset_input(dock_height)
        self.top_offset_input = make_offset_input(top_offset)
        self.bottom_offset_input = make_offset_input(bottom_offset)
        self.left_offset_input = make_offset_input(left_offset)
        self.right_offset_input = make_offset_input(right_offset)

        offset_labels = [
            "dock_height:", "top_offset:", "bottom_offset:", "left_offset:", "right_offset:"
        ]
        offset_fields = [
            self.dock_height_input, self.top_offset_input, self.bottom_offset_input,
            self.left_offset_input, self.right_offset_input
        ]
        for i in range(5):
            lbl = QLabel(offset_labels[i])
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            offsets_layout.addWidget(lbl, i, 0)
            offsets_layout.addWidget(offset_fields[i], i, 1)

        # --- Кнопка збереження ---
        offsets_save_btn = QPushButton("💾 Зберегти відступи та висоту доку")
        offsets_save_btn.setMinimumHeight(34)
        offsets_save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4C8ED9;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #5FA2EB; }
            QPushButton:pressed { background-color: #3C78C0; }
        """)

        def save_offsets():
            try:
                with open(widgets_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                data["dock_height"] = int(self.dock_height_input.text())
                data["top_offset"] = int(self.top_offset_input.text())
                data["bottom_offset"] = int(self.bottom_offset_input.text())
                data["left_offset"] = int(self.left_offset_input.text())
                data["right_offset"] = int(self.right_offset_input.text())

                with open(widgets_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                StellarMessageBox.information(self, "Успішно", "Системні параметри збережено.")
                # 🔥 миттєве оновлення без перезапуску
                if self.parent_window and hasattr(self.parent_window, "reload_widgets"):
                    self.parent_window.reload_widgets()
            except Exception as e:
                StellarMessageBox.critical(self, "Помилка", f"Не вдалося зберегти: {e}")

        offsets_save_btn.clicked.connect(save_offsets)
        offsets_layout.addWidget(offsets_save_btn, 6, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        offsets_group.setLayout(offsets_layout)
        personalization_layout.addWidget(offsets_group)



        # --- Scroll area ---
        scroll_widget = QWidget()
        scroll_widget.setLayout(personalization_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Настройка скроллбаров (ваш существующий код)
        scroll_area.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        # scroll_area.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #3B3B3B; }")

        outer_layout = QVBoxLayout(personalization_page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)
        self.content_area.addWidget(personalization_page)




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

    # def backup_current_version(self):
    #     backup_dir = "backup"
    #     try:
    #         if not os.path.exists(backup_dir):
    #             os.makedirs(backup_dir)
    #         for item in os.listdir("."):
    #             if item not in [backup_dir, ".venv"] and not item.startswith('.'):
    #                 src_path = os.path.join(".", item)
    #                 dst_path = os.path.join(backup_dir, item)
    #                 if os.path.isdir(src_path):
    #                     shutil.copytree(src_path, dst_path, symlinks=True, dirs_exist_ok=True)
    #                 else:
    #                     shutil.copy2(src_path, dst_path)
    #         return True
    #     except Exception as e:
    #         print(f"Backup error: {e}")
    #         StellarMessageBox.critical(self, self.tr("Backup error"),
    #                                    self.tr(f"Failed to create backup:\n{str(e)}"))
    #         return False
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
                        # 🔹 Копіюємо директорію без помилок при існуванні файлів
                        shutil.copytree(
                            src_path,
                            dst_path,
                            symlinks=True,
                            dirs_exist_ok=True,  # ✅ дозволяє існуючі файли
                            ignore=shutil.ignore_patterns("*.pyc", "__pycache__")
                        )
                    else:
                        # 🔹 Якщо файл уже існує — пропускаємо
                        try:
                            shutil.copy2(src_path, dst_path)
                        except FileExistsError:
                            pass

            return True

        except Exception as e:
            print(f"Backup error: {e}")
            StellarMessageBox.critical(
                self,
                self.tr("Backup error"),
                f"{self.tr('Failed to create backup')}:\n{str(e)}"
            )
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
