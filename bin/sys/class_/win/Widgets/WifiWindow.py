import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

import json
# os и sys уже импортированы

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
USER_CONFIG_PATH = os.path.join(BASE_DIR, 'root', 'bin', 'user.config')


def get_current_username():
    """
    Читает user.config, выводит имя пользователя в системную консоль и возвращает его.
    """
    username = "Unknown User"
    
    try:
        # Проверяем существование файла
        if not os.path.exists(USER_CONFIG_PATH):
            error_msg = f"[ERROR] user.config not found. Expected path: {USER_CONFIG_PATH}"
            print(error_msg)
            return "Error: File not found"
            
        with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            username = config_data.get("user_name", "Unknown User (key missing)")
            
    except json.JSONDecodeError:
        error_msg = "[ERROR] Invalid JSON format in user.config."
        print(error_msg)
        username = "Error: Invalid JSON"
    except Exception as e:
        error_msg = f"[ERROR] Error reading user data: {e}"
        print(error_msg)
        username = "Error: General Exception"

    # 🟢 Вывод имени пользователя прямо в системную консоль (CMD)
    print(f"[INFO] Current User Name: {username}")
    
    return username

GLOBAL_USERNAME = get_current_username()


class WifiPasswordManager:
    # 2. ✅ ИСПОЛЬЗУЕМ СОХРАНЕННУЮ ГЛОБАЛЬНУЮ ПЕРЕМЕННУЮ
    def __init__(self, filename=f"../../../root/{GLOBAL_USERNAME}/wifi/wifi_passwords.json"):
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
    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__()
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code  # Сохраняем переданный язык
        self.password_manager = WifiPasswordManager()
        self.setWindowTitle(self.tr("Wi-Fi"))
        self.setFixedSize(350, 450)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 225);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-size: 14px;
                color: #fff;
            }
            QListWidget {
                background-color: rgba(30, 30, 30, 225);
                border: 1px solid #1c1c1c;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: rgba(30, 30, 30, 225);
                border-radius: 6px;
            }
            QPushButton {
                background-color: #eeeeee;
                padding: 6px;
                border-radius: 6px;
                color: #000;
            }
            QPushButton:hover {
                background-color: #dddddd;
                color: #000;
            }
        """)

        layout = QVBoxLayout()

        self.current_network_label = QLabel(self.tr("Current network: (not connected)"))
        layout.addWidget(self.current_network_label)

        # Создаем горизонтальный layout для переключателя и кнопки обновления
        toggle_layout = QHBoxLayout()
        
        # Добавляем метку "Wi-Fi"
        toggle_label = QLabel(self.tr("Wi-Fi"))
        toggle_layout.addWidget(toggle_label)
        
        # Добавляем растягивающийся элемент, чтобы прижать элементы к краям
        toggle_layout.addStretch()
        
        # Добавляем кнопку обновления
        refresh_btn = QPushButton(self.tr("Refresh networks"))
        refresh_btn.clicked.connect(self.scan_networks)
        toggle_layout.addWidget(refresh_btn)
        
        # Добавляем переключатель
        self.toggle_switch = ToggleSwitch(self)
        toggle_layout.addWidget(self.toggle_switch)
        
        # Добавляем горизонтальный layout в основной
        layout.addLayout(toggle_layout)

        self.network_list = QListWidget()
        self.network_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.network_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        self.network_list.itemClicked.connect(self.connect_to_selected_network)

        layout.addWidget(self.network_list)

        self.setLayout(layout)

        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0] if self.wifi.interfaces() else None

        self.update_current_network()
        self.scan_networks()

    def paintEvent(self, event):
        """Рисуем закруглённый фон"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Градиент или однотонный фон
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(30, 30, 30))
        gradient.setColorAt(1, QColor(20, 20, 20))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)

        rect = QRectF(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect, 15, 15)  # радиус закругления

    def toggle_wifi(self, enabled):
        if enabled:
            self.scan_networks()
        else:
            self.network_list.clear()
            self.current_network_label.setText(self.tr("Wi-Fi disabled"))

    def update_current_network(self):
        if not self.iface:
            self.current_network_label.setText(self.tr("Wi-Fi adapter not found"))
            return
            
        if self.iface.status() == const.IFACE_CONNECTED:
            self.current_network_label.setText(self.tr("Current network: connected ✅"))
        else:
            self.current_network_label.setText(self.tr("Current network: (not connected)"))

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
            self.network_list.addItem(self.tr("Wi-Fi adapter not found"))
            return
            
        self.network_list.clear()
        self.network_list.addItem(self.tr("Scanning..."))
        
        # Используем QTimer для асинхронного выполнения
        QTimer.singleShot(0, self._perform_scan)

    def _perform_scan(self):
        try:
            self.iface.scan()
            # Проверяем результаты сканирования с задержкой
            QTimer.singleShot(3000, self._process_scan_results)
        except Exception as e:
            self.network_list.clear()
            self.network_list.addItem(self.tr("Scan error: {}").format(str(e)))

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
                        item.setToolTip(self.tr("Password saved"))
                    
                    self.network_list.addItem(item)
                    ssids.add(network.ssid)

            if not ssids:
                self.network_list.addItem(self.tr("No available networks"))
                
        except Exception as e:
            self.network_list.addItem(self.tr("Error processing results: {}").format(str(e)))
            
        self.update_current_network()

    def signal_strength_to_percent(self, signal):
        signal = max(min(signal, -30), -90)
        return int((signal + 90) / 60 * 100)

    def connect_to_selected_network(self, item):
        # if not self.iface:
        #     StellarMessageBox.warning(self, self.tr("Error"), self.tr("Wi-Fi adapter not found"))
        #     return
            
        ssid = item.text().split(" (")[0]
        saved_password = self.password_manager.get_password(ssid)
        
        if saved_password:
            reply = StellarMessageBox.question(
                self, 
                self.tr("Connect to Wi-Fi"), 
                self.tr("Use saved password for '{}'?").format(ssid),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                password = saved_password
            else:
                password, ok = CustomInputDialog.getText(
                    self, 
                    self.tr("Connect to Wi-Fi"), 
                    self.tr("Enter password for '{}':").format(ssid),
                    ""  # Передаём начальный текст (пустую строку)
                )
                if not ok:
                    return
        else:
            password, ok = CustomInputDialog.getText(
                self, 
                self.tr("Connect to Wi-Fi"), 
                self.tr("Enter password for '{}':").format(ssid),
                ""  # Передаём начальный текст (пустую строку)
            )
            if not ok:
                return

        
        self.password_manager.save_password(ssid, password)
        
        # Показываем сообщение о подключении
        self.network_list.addItem(self.tr("Connecting to {}...").format(ssid))
        
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
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Connection error: {}").format(str(e)))

    def _check_connection_status(self):
        if not self.iface:
            return
            
        if self.iface.status() == const.IFACE_CONNECTED:
            StellarMessageBox.information(self, self.tr("Success"), self.tr("Connected to '{}'").format(self.iface.scan_results()[0].ssid))
        else:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Failed to connect"))
            
        self.update_current_network()

    def check_connection_status(self):
        if not self.iface:
            return
            
        if self.iface.status() == const.IFACE_CONNECTED:
            StellarMessageBox.information(self, self.tr("Success"), self.tr("Connected to '{}'").format(self.iface.scan_results()[0].ssid))
        else:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Failed to connect"))
            
        self.update_current_network()