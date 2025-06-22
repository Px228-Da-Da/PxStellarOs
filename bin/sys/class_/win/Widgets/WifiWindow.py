import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *


class WifiPasswordManager:
    def __init__(self, filename="../../../root/dataLacmi/wifi/wifi_passwords.json"):
        self.filename = filename
        self.passwords = {}
        self.load_passwords()

    def load_passwords(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.passwords = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.passwords = {}

    def save_passwords(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.passwords, f)
        except IOError:
            pass

    def get_password(self, ssid):
        return self.passwords.get(ssid)

    def save_password(self, ssid, password):
        self.passwords[ssid] = password
        self.save_passwords()


class WifiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.password_manager = WifiPasswordManager()
        self.setWindowTitle("Wi-Fi")
        self.setFixedSize(360, 450)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(245, 245, 245, 220);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QListWidget {
                background-color: rgba(255, 255, 255, 180);
                border: 1px solid #ccc;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: rgba(0, 122, 255, 50);
                border-radius: 6px;
            }
            QPushButton {
                background-color: #eeeeee;
                padding: 6px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #dddddd;
            }
        """)

        layout = QVBoxLayout()

        self.current_network_label = QLabel("Текущая сеть: (не подключено)")
        layout.addWidget(self.current_network_label)

        # Создаем горизонтальный layout для переключателя и кнопки обновления
        toggle_layout = QHBoxLayout()
        
        # Добавляем метку "Wi-Fi"
        toggle_label = QLabel("Wi-Fi")
        toggle_layout.addWidget(toggle_label)
        
        # Добавляем растягивающийся элемент, чтобы прижать элементы к краям
        toggle_layout.addStretch()
        
        # Добавляем кнопку обновления
        refresh_btn = QPushButton("Обновить сети")
        refresh_btn.clicked.connect(self.scan_networks)
        toggle_layout.addWidget(refresh_btn)
        
        # Добавляем переключатель
        self.toggle_switch = ToggleSwitch(self)
        toggle_layout.addWidget(self.toggle_switch)
        
        # Добавляем горизонтальный layout в основной
        layout.addLayout(toggle_layout)

        self.network_list = QListWidget()
        self.network_list.itemClicked.connect(self.connect_to_selected_network)
        layout.addWidget(self.network_list)

        self.setLayout(layout)

        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0] if self.wifi.interfaces() else None

        self.update_current_network()
        self.scan_networks()

    def toggle_wifi(self, enabled):
        if enabled:
            self.scan_networks()
        else:
            self.network_list.clear()
            self.current_network_label.setText("Wi-Fi отключён")

    def update_current_network(self):
        if not self.iface:
            self.current_network_label.setText("Wi-Fi адаптер не найден")
            return
            
        if self.iface.status() == const.IFACE_CONNECTED:
            self.current_network_label.setText("Текущая сеть: подключено ✅")
        else:
            self.current_network_label.setText("Текущая сеть: (не подключено)")

    def get_signal_icon(self, signal_percent: int, locked: bool) -> QIcon:
        level = 0
        if signal_percent > 75:
            level = 4
        elif signal_percent > 50:
            level = 3
        elif signal_percent > 25:
            level = 2
        elif signal_percent > 0:
            level = 1
        icon_name = f"bin/icons/local_icons/system/wifi/wifi_signal_{level}{'_lock' if locked else ''}.png"
        return QIcon(icon_name)

    def scan_networks(self):
        if not self.iface:
            self.network_list.clear()
            self.network_list.addItem("Wi-Fi адаптер не найден")
            return
            
        self.network_list.clear()
        self.network_list.addItem("Сканирование...")
        
        # Используем QTimer для асинхронного выполнения
        QTimer.singleShot(0, self._perform_scan)

    def _perform_scan(self):
        try:
            self.iface.scan()
            # Проверяем результаты сканирования с задержкой
            QTimer.singleShot(3000, self._process_scan_results)
        except Exception as e:
            self.network_list.clear()
            self.network_list.addItem(f"Ошибка сканирования: {str(e)}")

    def _process_scan_results(self):
        if not self.iface:
            return
            
        self.network_list.clear()
        
        try:
            results = self.iface.scan_results()
            ssids = set()
            
            for network in results:
                if network.ssid and network.ssid not in ssids:
                    signal_percent = self.signal_strength_to_percent(network.signal)
                    locked = const.AKM_TYPE_NONE not in network.akm
                    icon = self.get_signal_icon(signal_percent, locked)
                    item = QListWidgetItem(icon, f"{network.ssid} ({signal_percent}%)")
                    
                    if self.password_manager.get_password(network.ssid):
                        item.setToolTip("Пароль сохранён")
                    
                    self.network_list.addItem(item)
                    ssids.add(network.ssid)

            if not ssids:
                self.network_list.addItem("Нет доступных сетей")
                
        except Exception as e:
            self.network_list.addItem(f"Ошибка обработки результатов: {str(e)}")
            
        self.update_current_network()

    def signal_strength_to_percent(self, signal):
        signal = max(min(signal, -30), -90)
        return int((signal + 90) / 60 * 100)

    def connect_to_selected_network(self, item):
        if not self.iface:
            QMessageBox.warning(self, "Ошибка", "Wi-Fi адаптер не найден")
            return
            
        ssid = item.text().split(" (")[0]
        saved_password = self.password_manager.get_password(ssid)
        
        if saved_password:
            reply = QMessageBox.question(
                self, 
                "Подключение к Wi-Fi", 
                f"Использовать сохранённый пароль для '{ssid}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                password = saved_password
            else:
                password, ok = QInputDialog.getText(
                    self, 
                    "Подключение к Wi-Fi", 
                    f"Введите пароль для '{ssid}':", 
                    QLineEdit.EchoMode.Password,
                    ""
                )
                if not ok:
                    return
        else:
            password, ok = QInputDialog.getText(
                self, 
                "Подключение к Wi-Fi", 
                f"Введите пароль для '{ssid}':", 
                QLineEdit.EchoMode.Password,
                ""
            )
            if not ok:
                return
        
        self.password_manager.save_password(ssid, password)
        
        # Показываем сообщение о подключении
        self.network_list.addItem(f"Подключение к {ssid}...")
        
        # Асинхронное подключение
        QTimer.singleShot(0, lambda: self._connect_to_network(ssid, password))

    def _connect_to_network(self, ssid, password):
        try:
            profile = pywifi.Profile()
            profile.ssid = ssid
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(const.AKM_TYPE_WPA2PSK)
            profile.cipher = const.CIPHER_TYPE_CCMP
            profile.key = password

            self.iface.remove_all_network_profiles()
            tmp_profile = self.iface.add_network_profile(profile)

            self.iface.connect(tmp_profile)
            # Проверяем статус подключения с задержкой
            QTimer.singleShot(5000, self._check_connection_status)
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка подключения: {str(e)}")

    def _check_connection_status(self):
        if not self.iface:
            return
            
        if self.iface.status() == const.IFACE_CONNECTED:
            QMessageBox.information(self, "Успех", f"Подключено к '{self.iface.scan_results()[0].ssid}'")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось подключиться")
            
        self.update_current_network()

    def check_connection_status(self):
        if not self.iface:
            return
            
        if self.iface.status() == const.IFACE_CONNECTED:
            QMessageBox.information(self, "Успех", f"Подключено к '{self.iface.scan_results()[0].ssid}'")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось подключиться")
            
        self.update_current_network()
