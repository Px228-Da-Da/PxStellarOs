import sys
import os
import shutil

# 1) QtWebEngine: отключаем GPU/композитинг Chromium
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu "
    "--disable-gpu-compositing "
    "--disable-features=VizDisplayCompositor "
    "--disable-software-rasterizer"
)

os.environ["QT_OPENGL"] = "software"
os.environ["QT_QUICK_BACKEND"] = "software"
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS",
    os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS","") + " --log-level=3 --disable-logging"
)
# 2) Qt/OpenGL: принудительно software
os.environ["QT_OPENGL"] = "software"

# (иногда помогает ещё это)
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

# импорт наверху рядом с остальными:

import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

with open("bin/sys/path/path.json", "r", encoding="utf-8") as f:
    path_data = json.load(f)
    file_paths = path_data.get("files_path", [])
    files = {os.path.basename(p): p for p in file_paths}

def global_exception_handler(exctype, value, tb):
    """Глобальный обработчик исключений."""
    error_message = "".join(traceback.format_exception(exctype, value, tb))
    print(f"Critical error: {error_message}")
    
    # Если окно уже создано, показываем экран смерти
    if 'window' in globals():
        window.show_death_screen(f"Critical error: {error_message}")
    else:
        # Если окно не создано, создаем временное окно для отображения ошибки
        temp_app = QApplication(sys.argv)
        temp_window = QWidget()
        temp_window.setWindowTitle("Critical Error")
        temp_window.setGeometry(100, 100, 800, 600)
        
        death_screen = DeathScreen(temp_window, f"Critical error: {error_message}")
        death_screen.show()
        
        sys.exit(temp_app.exec())


# # Активна кнопка
# active_btn = CustomButton("Активна кнопка", style='contained', enabled=True)
# layout.addWidget(active_btn)

# # Неактивна кнопка
# disabled_btn = CustomButton("Неактивна кнопка", style='contained', enabled=False)
# layout.addWidget(disabled_btn)

def load_stylesheet(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Не вдалося завантажити стилі: {e}")
        return ""

import json
import os
import sys

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
            # Извлекаем имя пользователя
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
# get_current_username()


# --- ALT+TAB SWITCHER -------------------------------------------------
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect, QScrollArea, QFrame
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QSize, QRect, QEasingCurve, QPropertyAnimation
from PyQt6.QtCore import QMargins
from PyQt6.QtCore import QFileSystemWatcher


class _SwitchCard(QWidget):
    def __init__(self, title: str, icon: QPixmap | None, selected=False, parent=None):
        super().__init__(parent)
        self.setProperty("sel", selected)
        lay = QVBoxLayout(self); lay.setContentsMargins(10,10,10,10); lay.setSpacing(8)

        self.thumb = QLabel()
        self.thumb.setFixedSize(120, 120)  # Уменьшаем размер для иконки
        self.thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if icon and not icon.isNull():
            # Масштабируем иконку с сохранением пропорций
            scaled_icon = icon.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.thumb.setPixmap(scaled_icon)
        else:
            # Иконка по умолчанию если не найдена
            default_icon = QPixmap(80, 80)
            default_icon.fill(Qt.GlobalColor.darkGray)
            self.thumb.setPixmap(default_icon)

        # Добавляем название приложения под иконкой
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: white; font-size: 14px; margin-top: 5px;")
        self.title_label.setMaximumWidth(120)
        self.title_label.setWordWrap(True)

        lay.addWidget(self.thumb)
        lay.addWidget(self.title_label)

        self._apply_selected_style()

    def set_selected(self, sel: bool):
        if self.property("sel") == sel: return
        self.setProperty("sel", sel)
        self._apply_selected_style()

    def _apply_selected_style(self):
        if self.property("sel"):
            self.setStyleSheet("""
                QWidget { 
                    border: 3px solid #4bcfff; 
                    border-radius: 14px; 
                    background: rgba(40, 40, 40, 0.9); 
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget { 
                    border: 2px solid rgba(255,255,255,0.15); 
                    border-radius: 12px; 
                    background: rgba(30, 30, 30, 0.8); 
                }
            """)


class TaskSwitcher(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Изменено для получения фокуса
        
        # Таймер для авто-закрытия при бездействии
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.cancel)
        self.auto_close_timeout = 5000  # 5 секунд

        self._items: list[tuple[str, QWidget]] = []  # [(name, win)]
        self._cards: list[_SwitchCard] = []
        self._index = 0

        # центрированный контейнер
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        self.container = QWidget()
        self.container.setObjectName("switcher_container")
        self.container.setStyleSheet("""
            #switcher_container { 
                background: rgba(20, 20, 20, 0.95); 
                border-radius: 20px; 
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        cLay = QVBoxLayout(self.container); cLay.setContentsMargins(40,40,40,40); cLay.setSpacing(16)

        self.row = QHBoxLayout(); self.row.setSpacing(18)
        self.row.setContentsMargins(0,0,0,0)

        scroll_host = QFrame()
        sh_lay = QHBoxLayout(scroll_host); sh_lay.setContentsMargins(0,0,0,0)
        self.row_widget = QWidget()
        self.row_widget.setLayout(self.row)
        sh_lay.addWidget(self.row_widget)

        scroll = QScrollArea()
        scroll.setWidget(scroll_host); scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { 
                background: transparent; 
                border: none; 
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        cLay.addWidget(scroll)
        root.addWidget(self.container)

        # Устанавливаем фильтр событий для родителя
        if parent:
            parent.installEventFilter(self)

    def _get_app_icon(self, app_name: str) -> QPixmap:
        """Получает иконку приложения по его имени"""
        # Пути к иконке приложения (пробуем несколько вариантов)
        possible_icon_paths = [
            os.path.join("apps", "local", app_name, f"{app_name}.png"),
            os.path.join("apps", "local", app_name, "icon.png"),
            os.path.join("apps", "local", f"{app_name}.png"),
            os.path.join("bin", "icons", "local_icons", "inons_apps", app_name, "icon.png"),
            os.path.join("bin", "icons", "local_icons", "system", "default_app.png")  # Иконка по умолчанию
        ]
        
        for path in possible_icon_paths:
            if os.path.exists(path):
                return QPixmap(path)
        
        # Если иконка не найдена, создаем простую иконку с буквой
        default_icon = QPixmap(100, 100)
        default_icon.fill(Qt.GlobalColor.darkGray)
        return default_icon

    def open_with(self, items: list[tuple[str, QWidget]], initial_name: str | None):
        self._items = items
        for i in reversed(range(self.row.count())):
            w = self.row.itemAt(i).widget()
            if w: 
                w.setParent(None)
        self._cards.clear()

        for name, win in self._items:
            # Вместо скриншота окна используем иконку приложения
            icon = self._get_app_icon(name)
            card = _SwitchCard(name.capitalize(), icon, False, self)  # Добавляем название
            self.row.addWidget(card)
            self._cards.append(card)

        self._index = 0
        if initial_name:
            for i, (nm, _) in enumerate(self._items):
                if nm == initial_name:
                    self._index = i
                    break
        self._sync_selection()

        # Рассчитать размер окна под карточки (теперь они меньше)
        card_width = 140  # Уменьшаем ширину карточки
        card_spacing = self.row.spacing()
        margin = 40  # padding контейнера
        total_width = len(self._cards) * card_width + (len(self._cards)-1) * card_spacing + 2*margin
        total_height = 160 + 2*margin + 20  # Уменьшаем высоту

        # Установить размер и центрировать на родителе
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - total_width) // 2
            y = parent_rect.y() + (parent_rect.height() - total_height) // 2
            self.setGeometry(x, y, total_width, total_height)
        else:
            self.resize(total_width, total_height)

        self.show()
        self.raise_()
        self.setFocus()  # Захватываем фокус
        self.auto_close_timer.start(self.auto_close_timeout)  # Запускаем таймер авто-закрытия

    def next(self):
        if not self._cards: 
            return
        self._index = (self._index + 1) % len(self._cards)
        self._sync_selection()
        self.auto_close_timer.start(self.auto_close_timeout)  # Сбрасываем таймер при действии

    def prev(self):
        if not self._cards: 
            return
        self._index = (self._index - 1 + len(self._cards)) % len(self._cards)
        self._sync_selection()
        self.auto_close_timer.start(self.auto_close_timeout)  # Сбрасываем таймер при действии

    def _sync_selection(self):
        for i, card in enumerate(self._cards):
            card.set_selected(i == self._index)

    def finalize(self) -> str | None:
        self.auto_close_timer.stop()
        if not self._items: 
            self.hide()
            return None
        chosen = self._items[self._index][0]
        self.hide()
        if self.parent():
            self.parent()._switcher_active = False
        return chosen

    def cancel(self):
        self.auto_close_timer.stop()
        self.hide()
        if self.parent():
            self.parent()._switcher_active = False

    def mousePressEvent(self, event):
        """Закрывать при клике вне карточек"""
        if event.button() == Qt.MouseButton.LeftButton or event.button() == Qt.MouseButton.RightButton:
            self.cancel()
        super().mousePressEvent(event)

    # алт таб tab (((
    def keyPressEvent(self, event):
        """Обработка клавиш"""
        if event.key() == Qt.Key.Key_Escape:
            self.cancel()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.finalize()
        elif event.key() == Qt.Key.Key_Tab:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.prev()
            else:
                self.next()
        elif event.key() == Qt.Key.Key_Left:
            self.prev()
        elif event.key() == Qt.Key.Key_Right:
            self.next()
        else:
            super().keyPressEvent(event)
        
        # Сбрасываем таймер при любом нажатии клавиши
        self.auto_close_timer.start(self.auto_close_timeout)

    def eventFilter(self, obj, event):
        """Фильтр событий для родительского окна"""
        if event.type() == QEvent.Type.MouseButtonPress:
            # Если клик вне switcher'а - закрываем
            if not self.geometry().contains(event.globalPosition().toPoint()):
                self.cancel()
                return True
        return super().eventFilter(obj, event)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        left   = int(self.width() * 0.05)
        top    = int(self.height() * 0.25)
        right  = int(self.width() * 0.05)
        bottom = int(self.height() * 0.35)
        self.container.setGeometry(self.rect().marginsRemoved(QMargins(left, top, right, bottom)))

    def hideEvent(self, event):
        """При скрытии останавливаем таймер"""
        self.auto_close_timer.stop()
        super().hideEvent(event)


class MacOSWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_language = "uk"  # або "en", або зчитуй із конфіг-файлу
        self.load_translations(self.current_language)

        self.last_layout_switch_time = 0
        self.layout_switch_delay = 500  # 500ms задержка
        self.current_layout_label = None
        self.layout_timer = QTimer()
        self.layout_timer.timeout.connect(self._hide_layout_label)
        self.layout_timer.setSingleShot(True)
        self.keyboard_layouts = ["EN", "RU"]  # Список поддерживаемых раскладок
        self.current_layout_index = 0  # Текущая раскладка
        # super().__init__()
        self.is_locked = False  # Флаг для отслеживания состояния блокировки
        self.is_splash_screen_active = False  # Флаг для отслеживания состояния загрузочного экрана
        self.is_password_input_deleted = False
        # Инициализация Wi-Fi
        self.wifi = None
        self.iface = None
        self.wifi_available = False
        self.wifi_error = ""
        self._meta_down = False
        self._meta_combo_used = False

        self.pinned_apps = set()  # Зберігає id закріплених додатків


        # stylesheet = load_stylesheet("styles.qss")
        # stylesheet = load_stylesheet("bin\sys\class_\win\system_class\styles\styles.qss")
        # self.setStyleSheet(stylesheet)
        import os, sys
        BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

        styles_path = os.path.join(
            BASE_DIR,
            "bin", "sys", "class_", "win", "system_class", "styles", "styles.qss"
        )
        stylesheet = load_stylesheet(styles_path)
        if stylesheet:
            self.setStyleSheet(stylesheet)
        else:
            print(f"[STYLE] Стиль не завантажено, шлях: {styles_path}")

        
        # try:
        #     if self.wifi.interfaces():
        #         self.iface = self.wifi.interfaces()[0]
        #     else:
        #         StellarMessageBox.warning(self, self.tr("Error"), self.tr("Error_wifi"))
        # except Exception as e:
        #     StellarMessageBox.warning(self, self.tr("Error"), f"Error initialization Wi-Fi: {str(e)}")
        try:
            # ✅ Linux: если нет wpa_supplicant — НЕ ПАДАЕМ, просто выключаем Wi-Fi
            if platform.system().lower() == "linux":
                if not os.path.exists("/var/run/wpa_supplicant"):
                    raise FileNotFoundError("/var/run/wpa_supplicant")

            self.wifi = pywifi.PyWiFi()
            ifaces = self.wifi.interfaces()
            if ifaces:
                self.iface = ifaces[0]
                self.wifi_available = True
            else:
                self.wifi_available = False
                self.wifi_error = "No Wi-Fi adapter"
        except Exception as e:
            self.wifi_available = False
            self.iface = None
            self.wifi_error = str(e)
            print(f"[WIFI] disabled: {self.wifi_error}")
            # можно показать мягкое предупреждение, но НЕ критическую ошибку:
            # StellarMessageBox.warning(self, self.tr("Error"), f"Wi-Fi disabled: {self.wifi_error}")

            
        try:
            self.desk_config = files.get("desk.config", "root/user/desk/desk.config")
            self.active_windows = {}
            
            # Настройки главного окна
            self.setWindowTitle("OS")
            self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), 
                            QApplication.primaryScreen().size().height())
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            # Фоновое изображение для всего приложения
            self.background = QLabel(self)
            self.background.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.load_background_image()
            self.watch_background_changes()
            
            # Основной контейнер
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            self.main_layout = QVBoxLayout(central_widget)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            
            # Рабочий стол (прозрачный)
            self.create_desktop_window()
            self.create_start_menu()

            # self.create_wifi_button()

            
            # Док-панель
            self.create_dock_panel()
            self.create_time_button()
            # Создаем кнопку громкости
            self.create_volume_button()
            self.create_start_button()
            
            # Остальные элементы
            self.create_menu()
            self.open_windows = {}
            self.create_all_windows()
            # self.check_for_updates()

            # Alt+Tab switcher
            self._switcher_active = False
            self.task_switcher = TaskSwitcher(self)
            self.task_switcher.hide()

            self.sc_win_e = QShortcut(QKeySequence(Qt.KeyboardModifier.MetaModifier | Qt.Key.Key_E), self)
            self.sc_win_e.setContext(Qt.ShortcutContext.ApplicationShortcut)
            self.sc_win_e.activated.connect(lambda: self._on_win_combo("explorer"))

            self._win_num_shortcuts = []
            num_keys = [
                Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3,
                Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6,
                Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9,
            ]

            for idx, key in enumerate(num_keys, start=1):
                sc = QShortcut(QKeySequence(Qt.KeyboardModifier.MetaModifier | key), self)
                sc.setContext(Qt.ShortcutContext.ApplicationShortcut)
                sc.activated.connect(lambda i=idx: self._activate_dock_slot(i - 1))
                self._win_num_shortcuts.append(sc)

            # (опционально) Win+0 = 10-е приложение, как в Windows
            sc0 = QShortcut(QKeySequence(Qt.KeyboardModifier.MetaModifier | Qt.Key.Key_0), self)
            sc0.setContext(Qt.ShortcutContext.ApplicationShortcut)
            sc0.activated.connect(lambda: self._activate_dock_slot(9))
            self._win_num_shortcuts.append(sc0)

            
            # Создаем экран блокировки
            self.create_lock_screen()
        except Exception as e:
            # Если ошибка происходит в конструкторе, показываем её в DeathScreen
            self.show_death_screen(f"Critical error in constructor: {str(e)}")

    def _task_items(self) -> list[tuple[str, QWidget]]:
        items = []
        # видимые/свернутые окна: берём те, что существуют
        for name, win in self.open_windows.items():
            if win is not None:  # показываем все, даже если свернуты
                items.append((name, win))
        # активное окно ставим первым
        if hasattr(self, "active_window_name") and self.active_window_name:
            items.sort(key=lambda t: 0 if t[0] == self.active_window_name else 1)
        return items

    def _open_switcher(self, reverse: bool = False):
        items = self._task_items()
        if not items:
            return
        initial = getattr(self, "active_window_name", None)
        self.task_switcher.open_with(items, initial)
        self._switcher_active = True
        if reverse:
            self.task_switcher.prev()
        else:
            self.task_switcher.next()

    def load_translations(self, language_code):
        """Завантажує файл перекладу за кодом мови."""
        import json
        translation_path = files.get(f"{language_code}.json", os.path.join("bin", "lang", language_code, f"{language_code}.json"))
        try:
            with open(translation_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            print(f"Translation file {translation_path} not found.")
            self.translations = {}
        except Exception as e:
            print(f"Error loading translation: {e}")
            self.translations = {}

    def tr(self, key):
        """Повертає перекладений текст або ключ, якщо не знайдено."""
        return self.translations.get(key, key)

    def create_start_button(self):
        """Создает кнопку меню Пуск с возможностью настройки позиции и размера через widgets.json"""
        import os, json

        config_path = os.path.join("bin", "sys", "path", "widgets.json")
        config = {}

        # === Загружаем конфиг ===
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"[create_start_button] Ошибка чтения widgets.json: {e}")

        # === Получаем параметры кнопки ===
        start_cfg = config.get("start_button", {})
        btn_x = start_cfg.get("x", 10)
        btn_y = start_cfg.get("y", -65)
        btn_w = start_cfg.get("width", 60)
        btn_h = start_cfg.get("height", 60)

        if btn_y < 0:
            btn_y = self.height() + btn_y  # Считаем от нижнего края

        # === Контейнер ===
        self.start_button_container = QWidget(self)
        self.start_button_container.setFixedSize(btn_w, btn_h)
        self.start_button_container.move(btn_x, btn_y)

        # === Лэйаут ===
        layout = QVBoxLayout(self.start_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === Кнопка Пуск ===
        self.start_button = QPushButton()
        self.start_button.setFixedSize(btn_w, btn_h)
        self.start_button.setObjectName("start_button")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)

        # === Иконка ===
        self.start_icon = QLabel(self.start_button)
        self.start_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def update_start_icon_size():
            icon_size = min(btn_w, btn_h) * 0.65  # Иконка занимает 55% кнопки
            pixmap = QIcon(os.path.join("bin", "icons", "local_icons", "start.png")).pixmap(int(icon_size), int(icon_size))
            self.start_icon.setPixmap(pixmap)
            self.start_icon.setGeometry(
                int((btn_w - icon_size) / 2),
                int((btn_h - icon_size) / 2),
                int(icon_size),
                int(icon_size)
            )

        update_start_icon_size()
        layout.addWidget(self.start_button)

        # === Обработчик клика ===
        self.start_button.clicked.connect(self.toggle_start_menu)

    # def create_volume_button(self):
    #     """Создает кнопку громкости с возможностью настройки размера и позиции через widgets.json"""
    #     import os, json

    #     config_path = os.path.join("bin", "sys", "path", "widgets.json")
    #     config = {}

    #     # Загружаем конфиг
    #     if os.path.exists(config_path):
    #         try:
    #             with open(config_path, "r", encoding="utf-8") as f:
    #                 config = json.load(f)
    #         except Exception as e:
    #             print(f"[create_volume_button] Ошибка чтения widgets.json: {e}")

    #     # Получаем параметры кнопки
    #     volume_cfg = config.get("volume_button", {})
    #     btn_x = volume_cfg.get("x", self.width() - 190)
    #     btn_y = volume_cfg.get("y", self.height() - 65)
    #     btn_w = volume_cfg.get("width", 60)
    #     btn_h = volume_cfg.get("height", 60)

    #     if btn_y < 0:
    #         btn_y = self.height() + btn_y  # Считаем от нижнего края

    #     # === Контейнер ===
    #     self.volume_button_container = QWidget(self)
    #     self.volume_button_container.setFixedSize(btn_w, btn_h)
    #     self.volume_button_container.move(btn_x, btn_y)

    #     # === Лэйаут ===
    #     layout = QVBoxLayout(self.volume_button_container)
    #     layout.setContentsMargins(0, 0, 0, 0)
    #     layout.setSpacing(0)

    #     # === Кнопка ===
    #     self.volume_button = QPushButton()
    #     self.volume_button.setFixedSize(btn_w, btn_h)
    #     self.volume_button.setObjectName("volume_button")

    #     # === Иконка ===
    #     self.volume_icon = QLabel(self.volume_button)
    #     self.volume_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

    #     # --- динамічне оновлення іконки при зміні розміру ---
    #     def update_icon_size():
    #         icon_size = min(btn_w, btn_h) * 0.65  # Іконка займає ~55% кнопки
    #         pixmap = QIcon(
    #             os.path.join("bin", "icons", "local_icons", "system", "volume.png")
    #         ).pixmap(int(icon_size), int(icon_size))
    #         self.volume_icon.setPixmap(pixmap)
    #         self.volume_icon.setGeometry(
    #             int((btn_w - icon_size) / 2),
    #             int((btn_h - icon_size) / 2),
    #             int(icon_size),
    #             int(icon_size)
    #         )


    #     update_icon_size()

    #     layout.addWidget(self.volume_button)

    #     # === Виджет громкости ===
    #     self.volume_widget = VolumeControlWidget(
    #         parent=self,
    #         translator=self.tr,
    #         lang_code=self.current_language
    #     )
    #     self.volume_widget.setParent(self)
    #     self.volume_widget.hide()

    #     # === Сигналы ===
    #     self.volume_button.clicked.connect(self.toggle_volume_control)

    #     # === Таймер ===
    #     self.volume_timer = QTimer(self)
    #     self.volume_timer.timeout.connect(self.update_volume_icon)
    #     self.volume_timer.start(1000)
    def create_volume_button(self):
        """Создает кнопку громкости с управлением колесиком мыши и отображением процента"""
        import os, json

        config_path = os.path.join("bin", "sys", "path", "widgets.json")
        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"[create_volume_button] Ошибка чтения widgets.json: {e}")

        volume_cfg = config.get("volume_button", {})
        btn_x = volume_cfg.get("x", self.width() - 190)
        btn_y = volume_cfg.get("y", self.height() - 65)
        btn_w = volume_cfg.get("width", 60)
        btn_h = volume_cfg.get("height", 60)

        if btn_y < 0:
            btn_y = self.height() + btn_y

        # === Контейнер ===
        self.volume_button_container = QWidget(self)
        self.volume_button_container.setFixedSize(btn_w, btn_h)
        self.volume_button_container.move(btn_x, btn_y)

        layout = QVBoxLayout(self.volume_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === Кнопка ===
        self.volume_button = QPushButton()
        self.volume_button.setFixedSize(btn_w, btn_h)
        self.volume_button.setObjectName("volume_button")

        # === Иконка ===
        self.volume_icon = QLabel(self.volume_button)
        self.volume_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def update_icon_size():
            icon_size = min(btn_w, btn_h) * 0.65
            pixmap = QIcon(
                os.path.join("bin", "icons", "local_icons", "system", "volume.png")
            ).pixmap(int(icon_size), int(icon_size))
            self.volume_icon.setPixmap(pixmap)
            self.volume_icon.setGeometry(
                int((btn_w - icon_size) / 2),
                int((btn_h - icon_size) / 2),
                int(icon_size),
                int(icon_size)
            )

        update_icon_size()
        layout.addWidget(self.volume_button)

        # === Виджет громкости ===
        self.volume_widget = Volume(
            parent=self,
            translator=self.tr,
            lang_code=self.current_language
        )
        self.volume_widget.hide()

        self.volume_button.clicked.connect(self.toggle_volume_control)

        # === Надпись с громкостью (появляется при наведении) ===
        self.volume_label = QLabel(self)
        self.volume_label.setText("100%")
        self.volume_label.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 190);
                color: #ffffff;
                font-weight: 600;
                font-size: 11px;
                border-radius: 6px;
                padding: 2px 6px;
            }
        """)
        self.volume_label.hide()

        def show_volume_label():
            """Показывает процент громкости при наведении"""
            vol = int(self.volume_widget.get_current_volume())
            self.volume_label.setText(f"{vol}%")
            label_x = btn_x + btn_w/2 - self.volume_label.width()/2
            label_y = btn_y - 25
            self.volume_label.move(int(label_x), int(label_y))
            self.volume_label.adjustSize()
            self.volume_label.show()

        def hide_volume_label():
            """Скрывает процент при уходе курсора"""
            self.volume_label.hide()

        # === Прокрутка колеса мыши ===
        # def wheelEvent(event):
        #     delta = event.angleDelta().y()
        #     if hasattr(self.volume_widget, "volume"):
        #         current = self.volume_widget.get_current_volume() / 100.0
        #         change = 0.05 if delta > 0 else -0.05
        #         new_volume = max(0.0, min(1.0, current + change))
        #         try:
        #             self.volume_widget.volume.SetMasterVolumeLevelScalar(new_volume, None)
        #         except Exception as e:
        #             print(f"[VOLUME] Error setting volume: {e}")

        #         # Обновляем UI
        #         self.volume_widget.update_volume()
        #         self.update_volume_icon()

        #         # 🔸 обновляем текст процента (даже если мышь не ушла)
        #         show_volume_label()

        #         # print(f"[VOLUME] Volume set to: {int(new_volume * 100)}%")
        def wheelEvent(event):
            delta = event.angleDelta().y()
            step = 5

            # print(f"[VOLUME] wheel delta={delta}")  # 👈 тимчасовий лог

            try:
                current = int(self.volume_widget.get_current_volume())
            except Exception as e:
                print(f"[VOLUME] Error get_current_volume: {e}")
                return

            if delta > 0:
                new_volume = current + step
            else:
                new_volume = current - step

            new_volume = max(0, min(100, new_volume))

            try:
                self.volume_widget.set_current_volume(new_volume)
                self.volume_widget.update_volume()
                self.update_volume_icon()
                show_volume_label()
            except Exception as e:
                print(f"[VOLUME] Error setting volume: {e}")


        # Привязываем события
        self.volume_button_container.enterEvent = lambda e: show_volume_label()
        self.volume_button_container.leaveEvent = lambda e: hide_volume_label()
        self.volume_button_container.wheelEvent = wheelEvent
        self.volume_button.wheelEvent = wheelEvent

        # === Таймер ===
        self.volume_timer = QTimer(self)
        self.volume_timer.timeout.connect(self.update_volume_icon)
        self.volume_timer.start(1000)

    def _get_dock_order(self) -> list[str]:
        """
        Порядок приложений как в доке:
        1) закрепленные из dock.config (self.allowed_apps)
        2) динамические (если ты добавляешь открытые не закрепленные)
        """
        order = []

        # закрепленные (в правильном порядке из dock.config)
        if hasattr(self, "allowed_apps") and self.allowed_apps:
            order.extend(self.allowed_apps)
        else:
            # запасной вариант: порядок ключей dock_buttons
            order.extend(list(getattr(self, "dock_buttons", {}).keys()))

        # динамические кнопки (добавляются при открытии не закрепленных) :contentReference[oaicite:1]{index=1}
        for name in getattr(self, "dynamic_dock_buttons", {}).keys():
            if name not in order:
                order.append(name)

        return order


    def _activate_dock_slot(self, slot_index: int):
        order = self._get_dock_order()
        if slot_index < 0 or slot_index >= len(order):
            return

        app_id = order[slot_index]

        # чтобы после Win+цифра не открывался Start при отпускании Win
        if hasattr(self, "_meta_combo_used"):
            self._meta_combo_used = True

        # поведение "как в Windows": если уже активно — свернуть, иначе активировать/открыть
        win = getattr(self, "open_windows", {}).get(app_id)
        active = getattr(self, "active_window_name", None)

        if win and active == app_id and not win.isMinimized():
            win.showMinimized()
            return

        # switch_window у тебя и активирует окно, и добавляет кнопку в док если надо :contentReference[oaicite:2]{index=2}
        self.switch_window(app_id)


    def toggle_volume_control(self):
        """Показывает/скрывает панель управления громкостью"""
        if self.volume_widget.isVisible():
            self.hide_volume_control()
        else:
            self.show_volume_control()

    def show_volume_control(self):
        """Показывает панель управления громкостью с анимацией"""
        # Обновляем текущее значение громкости
        self.volume_widget.update_volume()
        
        # Устанавливаем начальную позицию (невидимая, за экраном справа)
        start_pos = QPoint(self.width(), self.height() - 170)
        end_pos = QPoint(self.width() - 370, self.height() - 170)
        
        self.volume_widget.move(start_pos)
        self.volume_widget.show()
        self.volume_widget.raise_()
        
        # Анимация появления
        self.volume_animation = QPropertyAnimation(self.volume_widget, b"pos")
        self.volume_animation.setDuration(200)
        self.volume_animation.setStartValue(start_pos)
        self.volume_animation.setEndValue(end_pos)
        self.volume_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.volume_animation.start()

    def hide_volume_control(self):
        """Скрывает панель управления громкостью с анимацией"""
        start_pos = self.volume_widget.pos()
        end_pos = QPoint(self.width(), self.height() - 170)
        
        # Анимация исчезновения
        self.volume_animation = QPropertyAnimation(self.volume_widget, b"pos")
        self.volume_animation.setDuration(200)
        self.volume_animation.setStartValue(start_pos)
        self.volume_animation.setEndValue(end_pos)
        self.volume_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.volume_animation.finished.connect(self.volume_widget.hide)
        self.volume_animation.start()

    def update_volume_icon(self):
        """Обновляет иконку громкости"""
        try:
            if hasattr(self, 'volume_widget') and self.volume_widget and self.volume_widget.volume:
                current_volume = self.volume_widget.volume.GetMasterVolumeLevelScalar()
                
                if current_volume <= 0:
                    icon_name = "volume_mute.png"
                elif current_volume < 0.33:
                    icon_name = "volume_low.png"
                elif current_volume < 0.66:
                    icon_name = "volume_medium.png"
                else:
                    icon_name = "volume.png"
                    
                icon_path = os.path.join("bin", "icons", "local_icons", "system", icon_name)
                if os.path.exists(icon_path):
                    self.volume_icon.setPixmap(QIcon(icon_path).pixmap(30, 30))
        except Exception as e:
            print(f"Volume icon update error: {e}")


    def show_death_screen(self, error_message):
        """Показывает экран смерти с сообщением об ошибке."""
        self.death_screen = DeathScreen(self, error_message)
        self.death_screen.show()
    
    
    def create_time_button(self):
        """Создает кнопку с временем и датой с возможностью настройки позиции и размера через widgets.json"""
        import os, json

        config_path = os.path.join("bin", "sys", "path", "widgets.json")
        config = {}

        # Загружаем конфиг
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"[create_time_button] Ошибка чтения widgets.json: {e}")

        # Получаем параметры кнопки
        time_cfg = config.get("time_button", {})
        btn_x = time_cfg.get("x", self.width() - 120)
        btn_y = time_cfg.get("y", self.height() - 65)
        btn_w = time_cfg.get("width", 120)
        btn_h = time_cfg.get("height", 60)

        if btn_y < 0:
            btn_y = self.height() + btn_y  # Считаем от нижнего края

        # === Контейнер ===
        self.time_button_container = QWidget(self)
        self.time_button_container.setFixedSize(btn_w, btn_h)
        self.time_button_container.move(btn_x, btn_y)

        # === Лэйаут контейнера ===
        layout = QVBoxLayout(self.time_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === Кнопка ===
        self.time_button = QPushButton()
        self.time_button.setFixedSize(btn_w, btn_h)
        self.time_button.setObjectName("time_button")

        # === Внутренний лэйаут для текста ===
        text_layout = QVBoxLayout(self.time_button)
        text_layout.setContentsMargins(5, 5, 5, 5)
        text_layout.setSpacing(0)

        # Метка времени
        self.time_button_time = QLabel()
        self.time_button_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_button_time.setObjectName("time_button_time")

        # Метка даты
        self.time_button_date = QLabel()
        self.time_button_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_button_date.setObjectName("time_button_date")

        text_layout.addWidget(self.time_button_time)
        text_layout.addWidget(self.time_button_date)

        layout.addWidget(self.time_button)

        # === Виджет календаря ===
        self.calendar_widget = Calendar(
            parent=self,
            translator=self.tr,
            lang_code=self.current_language
        )
        self.calendar_widget.setParent(self)
        self.calendar_widget.setFixedSize(350, 350)
        self.calendar_widget.hide()

        # Позиция календаря (можно тоже вынести в JSON)
        self.calendar_widget.move(
            self.width() - 370,
            self.height() - 420
        )

        # === Подключаем события ===
        self.time_button.clicked.connect(self.toggle_calendar)

        # === Таймер обновления времени ===
        self.update_time_button()
        self.time_button_timer = QTimer(self)
        self.time_button_timer.timeout.connect(self.update_time_button)
        self.time_button_timer.start(1000)


    def toggle_calendar(self):
        """Показывает/скрывает календарь"""
        if self.calendar_widget.isVisible():
            self.hide_calendar()
        else:
            self.show_calendar()

    def show_calendar(self):
        """Показывает календарь с анимацией"""
        # Устанавливаем начальную позицию (невидимая, за экраном справа)
        start_pos = QPoint(self.width(), self.height() - 350)
        end_pos = QPoint(self.width() - 370, self.height() - 420)
        
        self.calendar_widget.move(start_pos)
        self.calendar_widget.show()
        self.calendar_widget.raise_()
        
        # Устанавливаем флаг, чтобы предотвратить немедленное закрытие
        self.calendar_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # Анимация появления
        self.calendar_animation = QPropertyAnimation(self.calendar_widget, b"pos")
        self.calendar_animation.setDuration(200)
        self.calendar_animation.setStartValue(start_pos)
        self.calendar_animation.setEndValue(end_pos)
        self.calendar_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.calendar_animation.start()

    def hide_calendar(self):
        """Скрывает календарь с анимацией"""
        start_pos = self.calendar_widget.pos()
        end_pos = QPoint(self.width(), self.height() - 350)
        
        # Анимация исчезновения
        self.calendar_animation = QPropertyAnimation(self.calendar_widget, b"pos")
        self.calendar_animation.setDuration(200)
        self.calendar_animation.setStartValue(start_pos)
        self.calendar_animation.setEndValue(end_pos)
        self.calendar_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.calendar_animation.finished.connect(self.calendar_widget.hide)
        self.calendar_animation.start()
    
    def update_time_button(self):
        """Обновляет отображение времени и даты в кнопке"""
        import os, json
        from datetime import datetime

        # === Загружаем настройку показа секунд ===
        config_path = os.path.join("bin", "sys", "path", "widgets.json")
        show_seconds = True  # по умолчанию показываем

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # поддержка строк и булевых значений
                    value = data.get("clock_widget_sec", "True")
                    show_seconds = str(value).lower() in ("true", "1", "yes")
            except Exception as e:
                print(f"[update_time_button] Ошибка чтения widgets.json: {e}")

        # === Формат времени ===
        now = datetime.now()
        time_format = "%H:%M:%S" if show_seconds else "%H:%M"
        time_str = now.strftime(time_format)
        date_str = now.strftime("%d.%m.%Y")

        self.time_button_time.setText(time_str)
        self.time_button_date.setText(date_str)



    def resizeEvent(self, event):
        """Обновляет позицию элементов при изменении размера окна (позиции читаются из widgets.json)"""
        import json, os
        super().resizeEvent(event)

        # Путь к файлу конфигурации
        config_path = os.path.join("bin", "sys", "path", "widgets.json")
        positions = {}

        # Загружаем позиции, если файл существует
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    positions = json.load(f)
            except Exception as e:
                print(f"[resizeEvent] Ошибка чтения widgets.json: {e}")

        def get_pos(name, default_x, default_y):
            pos = positions.get(name, {"x": default_x, "y": default_y})
            return pos.get("x", default_x), pos.get("y", default_y)

        # === Перемещаем элементы ===
        if hasattr(self, 'time_button_container'):
            x, y = get_pos('time_button', self.width() - 120, self.height() - 65)
            if y < 0:
                y = self.height() + y  # корректно считаем от нижнего края
            self.time_button_container.move(x, y)

        if hasattr(self, 'volume_button_container'):
            x, y = get_pos('volume_button', self.width() - 190, self.height() - 65)
            if y < 0:
                y = self.height() + y
            self.volume_button_container.move(x, y)

        if hasattr(self, 'wifi_button_container'):
            x, y = get_pos('wifi_button', self.width() - 260, self.height() - 65)
            if y < 0:
                y = self.height() + y
            self.wifi_button_container.move(x, y)

        if hasattr(self, 'start_button_container'):
            x, y = get_pos('start_button', 10, self.height() - 65)
            if y < 0:
                y = self.height() + y
            self.start_button_container.move(x, y)

        # Перерисовка фона
        self.load_background_image()

    def watch_background_changes(self):
        """Відстежує зміни у desk.config та оновлює фон"""
        try:
            config_path = self.desk_config if hasattr(self, "desk_config") else os.path.join("root", "user", "desk", "desk.config")
            self.config_watcher = QFileSystemWatcher([config_path])
            self.config_watcher.fileChanged.connect(self.on_background_config_changed)
            print(f"[watch_background_changes] Відстеження запущено для: {config_path}")
        except Exception as e:
            print(f"[watch_background_changes] Помилка: {e}")

    def on_background_config_changed(self):
        """Автоматичне оновлення фону при зміні desk.config"""
        try:
            print("[on_background_config_changed] Змінено desk.config — оновлюю фон...")
            self.load_background_image()

            # Якщо Qt не бачить файл одразу — повторно додаємо його
            if os.path.exists(self.desk_config):
                self.config_watcher.addPath(self.desk_config)
        except Exception as e:
            print(f"[on_background_config_changed] Помилка при оновленні фону: {e}")


    def create_lock_screen(self):
        """Создает экран блокировки. Если в файле пароль 'none' — показывает кнопку 'Войти'."""
        import os, json
        from datetime import datetime

        self.is_locked = True
        config_path = os.path.join("bin", "sys", "path", "widgets.json")

        # Если lock_widget уже существует, удаляем его
        if hasattr(self, 'lock_widget') and self.lock_widget is not None:
            self.lock_widget = None

        # === Создаем новый виджет ===
        self.lock_widget = QWidget(self)
        self.lock_widget.setGeometry(0, 0, self.width(), self.height())

        # === Фон ===
        try:
            import shutil

            log_path = os.path.join("root", "user", "desk", "lock_debug.log")

            def log(msg):
                print(msg)

            desk_config_path = os.path.join("root", "user", "desk", "desk.config")
            default_fallback = os.path.join("bin", "icons", "local_icons", "IconOs", "wallpaper_defolt.jpg")
            lock_dest = os.path.join("bin", "icons", "local_icons", "IconOs", "lock.jpg")

            background_path = None

            # === Пробуємо прочитати з desk.config ===
            if os.path.exists(desk_config_path):
                try:
                    with open(desk_config_path, "r", encoding="utf-8") as f:
                        desk_data = json.load(f)
                        background_path = desk_data.get("lock_screen_path") or desk_data.get("lockscreen_path")
                        if background_path:
                            # Нормалізація для Linux/Win
                            background_path = background_path.replace("\\", "/")
                            background_path = os.path.normpath(background_path)
                        log(f"[LockScreen] Path from config: {background_path}")
                except json.JSONDecodeError:
                    log("[LockScreen] JSON decode error у desk.config")
                except Exception as e:
                    log(f"[LockScreen] Помилка читання desk.config: {e}")
            else:
                log(f"[LockScreen] desk.config не знайдено: {desk_config_path}")

            # === Якщо фон не існує — fallback ===
            if not background_path or not os.path.exists(background_path):
                log(f"[LockScreen] Фон не знайдено, використовую дефолт: {default_fallback}")
                background_path = default_fallback

            # === Копіюємо фон у локальний lock.jpg ===
            try:
                os.makedirs(os.path.dirname(lock_dest), exist_ok=True)
                if os.path.abspath(background_path) != os.path.abspath(lock_dest):
                    shutil.copy(background_path, lock_dest)
                    log(f"[LockScreen] Скопійовано фон: {background_path} → {lock_dest}")
                else:
                    log("[LockScreen] Шлях співпадає, копіювання пропущено.")
            except Exception as e:
                log(f"[LockScreen] Не вдалося скопіювати фон: {e}")
                if not os.path.exists(lock_dest):
                    background_path = default_fallback

            # === Завантажуємо фінальне зображення ===
            final_bg = lock_dest if os.path.exists(lock_dest) else default_fallback

            pixmap = QPixmap(final_bg).scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

            self.background_label = QLabel(self.lock_widget)  # ✅ атрибут, щоб не зникав
            self.background_label.setPixmap(pixmap)
            self.background_label.setGeometry(0, 0, self.width(), self.height())
            self.background_label.lower()

            log(f"[LockScreen] Фінальний фон: {final_bg}")

        except Exception as e:
            with open("root/user/desk/lock_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[LockScreen] Головна помилка: {e}\n")
            print(f"[LockScreen] Головна помилка: {e}")


        # === Логотип ===
        icon_dir_path = os.path.join("bin", "icons", "local_icons", "IconOs", "OS.png")
        logo_pixmap = QPixmap(icon_dir_path)

        # Загружаем параметры из widgets.json
        logo_cfg = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logo_cfg = data.get("lock_logo", {})
            except Exception as e:
                print(f"[LockScreen] Ошибка чтения widgets.json для логотипа: {e}")

        # Настройки по умолчанию
        scale_factor = logo_cfg.get("scale", 0.5)
        x_offset = logo_cfg.get("x_offset", 0)
        y_offset = logo_cfg.get("y_offset", -50)

        scaled_pixmap = logo_pixmap.scaled(
            int(logo_pixmap.width() * scale_factor),
            int(logo_pixmap.height() * scale_factor),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        logo_label = QLabel(self.lock_widget)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setGeometry(
            (self.width() - scaled_pixmap.width()) // 2 + x_offset,
            (self.height() - scaled_pixmap.height()) // 2 + y_offset,
            scaled_pixmap.width(),
            scaled_pixmap.height()
        )

        # === Загружаем настройки часов ===
        show_lock_clock = True
        show_lock_seconds = True
        clock_pos = {"x": 10, "y": 10}  # позиция по умолчанию

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    show_lock_clock = bool(cfg.get("lock_clock_enable", True))
                    show_lock_seconds = str(cfg.get("lock_clock_sec", "True")).lower() in ("true", "1", "yes")
                    clock_pos.update(cfg.get("lock_clock_pos", {}))  # подгружаем координаты
            except Exception as e:
                print(f"[LockScreen] Ошибка чтения widgets.json: {e}")

        # === Если часы включены — создаем их ===
        if show_lock_clock:
            self.time_label = QLabel(self.lock_widget)
            self.time_label.setObjectName("time_label")

            # Позиция часов из JSON
            clock_x = clock_pos.get("x", 10)
            clock_y = clock_pos.get("y", 10)
            self.time_label.setGeometry(clock_x, clock_y, 100, 40)
            self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # Функция обновления часов
            def update_lock_time():
                now = datetime.now()
                fmt = "%H:%M:%S" if show_lock_seconds else "%H:%M"
                self.time_label.setText(now.strftime(fmt))

            update_lock_time()

            # Таймер
            self.clock_timer = QTimer(self)
            self.clock_timer.timeout.connect(update_lock_time)
            self.clock_timer.start(1000 if show_lock_seconds else 60000)


        # === Загрузка пароля ===
        username = get_current_username()
        password_path = os.path.join("root", f"{username}", "user", "password")
        self._lock_password = None
        try:
            with open(password_path, "r", encoding="utf-8") as f:
                self._lock_password = f.read().strip()
        except FileNotFoundError:
            self._lock_password = None
        except Exception as e:
            print(f"[LockScreen] Ошибка чтения пароля: {e}")
            self._lock_password = None

        # === Загружаем позицию кнопки/поля входа ===
        login_pos = {"x": 0, "y": 20}
        config_path = os.path.join("bin", "sys", "path", "widgets.json")

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    login_pos.update(cfg.get("lock_login_pos", {}))
            except Exception as e:
                print(f"[LockScreen] Ошибка чтения widgets.json для позиции кнопки входа: {e}")

        # === Если 'none' → кнопка входа ===
        if self._lock_password and self._lock_password.lower() == "none":
            self.password_input = None
            self.login_button = QPushButton(self.tr("sing"), self.lock_widget)
            self.login_button.setObjectName("login_button")
            self.login_button.setFixedSize(200, 36)

            # Применяем позицию из JSON
            btn_x = (self.width() - 200) // 2 + login_pos["x"]
            btn_y = logo_label.y() + logo_label.height() + login_pos["y"]
            self.login_button.move(btn_x, btn_y)

            self.login_button.clicked.connect(self.unlock_screen)
            self.login_button.setStyleSheet("""
            QPushButton#login_button {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 8px;
                color: white;
                font-size: 15px;
                font-weight: 500;
                letter-spacing: 0.5px;
                padding: 6px 0;
            }
            QPushButton#login_button:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton#login_button:pressed {
                background-color: rgba(255, 255, 255, 0.35);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            """)
            self.login_button.setFocus()

        else:
            # === Поле ввода пароля ===
            self.login_button = None
            self.password_input = InputPassword(
                parent=self.lock_widget,
                placeholder_text=self.tr("Password"),
                initial_text="",
                echo_mode=QLineEdit.EchoMode.Password,
                translator=self.tr,
                lang_code=self.current_language
            )
            input_x = (self.width() - 200) // 2 + login_pos["x"]
            input_y = logo_label.y() + logo_label.height() + login_pos["y"]
            self.password_input.setGeometry(input_x, input_y, 200, 30)

            self.password_input.returnPressed.connect(self.unlock_screen)
            self.password_input.setFocus()

            if hasattr(self, "password_input") and self.password_input is not None:
                self.password_input.setFocus()
            elif hasattr(self, "login_button") and self.login_button is not None:
                self.login_button.setFocus()


        # === Кнопка с картинкой (основная) ===
        self.main_button = QPushButton(self.lock_widget)
        self.main_button.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "IconOs", "shutdown.png")))
        self.main_button.setIconSize(QSize(50, 50))
        self.main_button.setFixedSize(50, 50)
        self.main_button.setObjectName("main_button")

        # Загружаем позицию кнопки из JSON
        main_btn_pos = {"x": 0, "y": 80}  # значения по умолчанию
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    main_btn_pos.update(cfg.get("lock_main_button_pos", {}))
            except Exception as e:
                print(f"[LockScreen] Ошибка чтения widgets.json для lock_main_button_pos: {e}")

        # Применяем позицию
        btn_x = (self.width() - 50) // 2 + main_btn_pos["x"]
        btn_y = logo_label.y() + logo_label.height() + main_btn_pos["y"]
        self.main_button.move(btn_x, btn_y)

        # Подключаем событие
        self.main_button.clicked.connect(self.toggle_additional_buttons)


        # === Контейнер для дополнительных кнопок ===
        self.additional_buttons_container = QWidget(self.lock_widget)
        self.additional_buttons_container.setGeometry(
            (self.width() - 150) // 2,
            self.main_button.y() - 60,
            150,
            100
        )
        self.additional_buttons_container.setObjectName("additional_buttons_container")
        self.additional_buttons_container.hide()


        # Лэйаут и кнопки
        additional_layout = QVBoxLayout(self.additional_buttons_container)
        additional_layout.setSpacing(10)
        additional_layout.setContentsMargins(10, 10, 10, 10)

                # === Кнопки завершення та перезавантаження ===
        button_style = """
        QPushButton {
            background-color: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 14px;
            font-weight: 500;
            border-radius: 10px;
            padding-left: 12px;
            text-align: left;
        }

        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.35);
        }

        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.45);
        }

        QPushButton::icon {
            margin-right: 8px;
        }
        """

        # Кнопка Shutdown
        self.button1 = QPushButton(self.tr("Shutdown"), self)
        self.button1.setObjectName("shutdown_button")
        self.button1.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "IconOs", "shutdown.png")))
        self.button1.setIconSize(QSize(28, 28))
        self.button1.setFixedSize(130, 42)
        self.button1.clicked.connect(self.shutdown_system)
        self.button1.setStyleSheet(button_style)
        additional_layout.addWidget(self.button1)

        # Кнопка Reboot
        self.button2 = QPushButton(self.tr("Reboot"), self)
        self.button2.setObjectName("reboot_button")
        self.button2.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "IconOs", "reboot.png")))
        self.button2.setIconSize(QSize(28, 28))
        self.button2.setFixedSize(130, 42)
        self.button2.clicked.connect(self.reboot_system)
        self.button2.setStyleSheet(button_style)
        additional_layout.addWidget(self.button2)

        # Обработчики событий
        self.additional_buttons_container.enterEvent = self.additional_buttons_enter_event
        self.additional_buttons_container.leaveEvent = self.additional_buttons_leave_event


    def update_time_label(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.time_label.setText(current_time)


    def additional_buttons_enter_event(self, event):
        """Обработчик события, когда курсор входит в область контейнера."""
        # Ничего не делаем, контейнер остается видимым
        pass

    def additional_buttons_leave_event(self, event):
        """Обработчик события, когда курсор покидает область контейнера."""
        # Скрываем контейнер с анимацией
        self.animate_container(self.additional_buttons_container, 0)

    def toggle_additional_buttons(self):
        """Показывает или скрывает дополнительные кнопки."""
        if self.additional_buttons_container.isVisible():
            # Анимация скрытия
            self.animate_container(self.additional_buttons_container, 0)
        else:
            # Анимация появления
            self.additional_buttons_container.show()
            self.animate_container(self.additional_buttons_container, 1)

    def animate_container(self, widget, opacity):
        """Анимация изменения прозрачности контейнера."""
        self.animation = QPropertyAnimation(widget, b"windowOpacity")
        self.animation.setDuration(200)  # Длительность анимации 200 мс
        self.animation.setStartValue(widget.windowOpacity())
        self.animation.setEndValue(opacity)
        if opacity == 0:
            self.animation.finished.connect(lambda: widget.hide())  # Скрываем виджет после завершения анимации
        self.animation.start()

    def unlock_screen(self):
        """Разблокирует экран, если пароль верный. Поддерживает режим 'none' (кнопка входа)."""
        # Проверяем, существует ли еще виджет блокировки
        if not hasattr(self, 'lock_widget') or self.lock_widget is None:
            return

        # Если есть поле password_input — проверяем текст оттуда.
        # Если поля нет, но есть login_button — считаем это режимом "none" и разрешаем вход.
        try:
            # вариант — режим з кнопкою (файл містив "none")
            if (not hasattr(self, 'password_input') or self.password_input is None) and \
               (hasattr(self, 'login_button') and self.login_button is not None):
                # Режим без пароля — просто розблоковуємо
                allowed = True
            elif hasattr(self, 'password_input') and self.password_input is not None:
                entered = self.password_input.text()
                # Якщо пароль з файлу встановлено в self._lock_password, порівнюємо з ним.
                if hasattr(self, "_lock_password") and self._lock_password:
                    allowed = (entered == self._lock_password)
                else:
                    # Якщо пароля в конфі ні — можна визначити правило (наприклад, порожній рядок)
                    allowed = (entered == "")
            else:
                # Немає ні поля, ні кнопки — нічого не робимо
                return

            if allowed:
                self.is_locked = False

                # Остановить и удалить таймер и метку времени
                if hasattr(self, "clock_timer") and self.clock_timer:
                    try:
                        self.clock_timer.stop()
                        self.clock_timer.deleteLater()
                    except Exception:
                        pass

                # Якщо був лоґін баттон — видаляємо його
                if hasattr(self, "login_button") and self.login_button is not None:
                    try:
                        self.login_button.deleteLater()
                    except Exception:
                        pass
                    self.login_button = None

                # Якщо було поле вводу — видаляємо його
                if hasattr(self, "password_input") and self.password_input is not None:
                    try:
                        self.password_input.deleteLater()
                    except Exception:
                        pass
                    self.password_input = None

                # Анімація закриття екрану блокування
                self.animation = QPropertyAnimation(self.lock_widget, b"geometry")
                self.animation.setDuration(200)
                self.animation.setStartValue(QRect(0, 0, self.width(), self.height()))
                self.animation.setEndValue(QRect(0, -self.height(), self.width(), self.height()))
                self.animation.finished.connect(self.lock_widget.deleteLater)
                self.animation.start()
            else:
                StellarMessageBox.warning(self, self.tr("Error"), self.tr("Incorrect password!"))
        except RuntimeError:
            # Якщо об'єкт вже видалено
            return
        except Exception as e:
            print(f"[unlock_screen] unexpected error: {e}")
            return



    def update_progress(self):
        # Обновляем значение прогресс-бара
        current_value = 50
        if current_value < 50:
            self.progress_bar.setValue(current_value + 1)
        else:
            self.progress_timer.stop()  # Останавливаем таймер, когда прогресс-бар достигнет 100%

    def start_animation(self):
        self.is_splash_screen_active = False  # Снимаем флаг загрузочного экрана
        # Анимация исчезания вверх
        self.animation = QPropertyAnimation(self.splash_widget, b"geometry")
        self.animation.setDuration(200)  # Длительность анимации 1 секунда
        self.animation.setStartValue(QRect(0, 0, self.width(), self.height()))
        self.animation.setEndValue(QRect(0, -self.height(), self.width(), self.height()))
        self.animation.finished.connect(self.splash_widget.deleteLater)  # Удаляем виджет после завершения анимации
        self.animation.start()



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
            # print("Обновление завершено. Перезапустите приложение.")
            # sys.exit(0)
            self.reboot_system()
        else:
            # print("Ошибка при обновлении.")
            self.reboot_system()


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
            # print("Обновление завершено. Перезапустите приложение.")
            # sys.exit(0)
            self.reboot_system()
        else:
            # print("Ошибка при обновлении.")
            self.reboot_system()


    def load_background_image(self):
        """Завантажує фон робочого столу з desk.config (JSON)"""
        import json, os

        try:
            # Шлях до файлу конфігурації
            config_path = self.desk_config if hasattr(self, "desk_config") else os.path.join("root", "user", "desk", "desk.config")

            if not os.path.exists(config_path):
                return  # нічого не робимо, якщо конфігу немає

            with open(config_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("[load_background_image] Помилка JSON — перевір формат desk.config")
                    return

            # Отримуємо шлях до шпалер
            image_path = data.get("wallpaper_path")
            if not image_path or not os.path.exists(image_path):
                # fallback: стандартний фон
                image_path = os.path.join("bin", "icons", "local_icons", "IconOs", "wallpaper.jpg")

            # Встановлюємо зображення
            pixmap = QPixmap(image_path).scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.background.setPixmap(pixmap)
            self.background.setGeometry(0, 0, self.width(), self.height())

        except Exception as e:
            print(f"[load_background_image] Помилка: {e}")



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

    def create_all_windows(self):
        """
        Инициализация окон. Окна создаются только при первом открытии.
        """
        #config_path = r"root\bin\list_apps\list_apps.config"
        config_path = os.path.join("root", "bin", "list_apps", "list_apps.config")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                # Преобразуем JSON строку в словарь Python
                self.open_windows = json.loads(content)
                
        except FileNotFoundError:
            print(f"Файл конфигурации {config_path} не найден. Используются значения по умолчанию.")
            # Значения по умолчанию на случай отсутствия файла
            self.open_windows = {
                "browser": None,
                "cmd": None,
                "settings": None,
                "calc": None,
                "explorer": None,
                "notebook": None,
                "manager_all": None
            }
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON в файле {config_path}: {e}")
            # Значения по умолчанию на случай ошибки парсинга
            self.open_windows = {
                "browser": None,
                "cmd": None,
                "settings": None,
                "calc": None,
                "explorer": None,
                "notebook": None,
                "manager_all": None
            }
        except Exception as e:
            print(f"Неожиданная ошибка при загрузке конфигурации: {e}")
            self.open_windows = {
                "browser": None,
                "cmd": None,
                "settings": None,
                "calc": None,
                "explorer": None,
                "notebook": None,
                "manager_all": None
            }

    def create_menu(self):
        """
        Создает меню с использованием QMenuBar и добавляет время/дату в правый угол.
        """
        menubar = self.menuBar()
        menubar.setObjectName("main_menu_bar")

        # Меню "Win" (динамически изменяет название на активное окно)
        self.win_menu = menubar.addMenu("Win")
        self.update_win_menu("desktop")

        # Меню "Power" (Выключение и перезагрузка)
        power_menu = menubar.addMenu(self.tr("Power"))

        # Действие для выключения
        shutdown_action = QAction(self.tr("Shutdown"), self)
        shutdown_action.triggered.connect(self.shutdown_system)
        power_menu.addAction(shutdown_action)

        # Действие для перезагрузки
        reboot_action = QAction(self.tr("Reboot"), self)
        reboot_action.triggered.connect(self.reboot_system)
        power_menu.addAction(reboot_action)

        # Действие для блокировки экрана
        lock_action = QAction(self.tr("Lock"), self)  # Кнопка блокировки
        lock_action.triggered.connect(self.lock_screen)  # Связываем с методом блокировки
        power_menu.addAction(lock_action)  # Добавляем в меню "Power"
        
        # Добавляем разделитель
        power_menu.addSeparator()
        
        # Действие для закрытия приложения
        quit_action = QAction(self.tr("Quit"), self)
        # quit_action.setShortcut("Ctrl+Q")  # Горячая клавиша
        quit_action.triggered.connect(self.close)  # Закрываем главное окно
        power_menu.addAction(quit_action)

        # Меню "Language" для переключения раскладки клавиатуры
        # language_menu = menubar.addMenu(self.tr("Language"))
        self.language_menu = menubar.addMenu(self.tr("Language"))

        
        # Действие для переключения следующего языка
        switch_lang_action = QAction(self.tr("Next Language (Alt+Shift)"), self)
        switch_lang_action.triggered.connect(self.switch_language)
        self.language_menu.addAction(switch_lang_action)
        
        # Добавляем разделитель
        self.language_menu.addSeparator()
        
        # Добавляем действия для выбора конкретного языка
        self.languages = [
            {"name": "English", "layout": "us", "flag": "🇺🇸"},
            {"name": "Russian", "layout": "ru", "flag": "🇷🇺"},
            {"name": "Ukrainian", "layout": "ua", "flag": "🇺🇦"}
        ]
        
        for i, lang in enumerate(self.languages):
            lang_action = QAction(f"{lang['flag']} {lang['name']}", self)
            lang_action.triggered.connect(lambda checked, idx=i: self.set_language(idx))
            self.language_menu.addAction(lang_action)

        # Создание метки для времени и даты
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Helvetica", 14))
        self.time_label.setStyleSheet("color: black; padding: 5px;")
        # self.update_time()  # Обновляем сразу при старте
        self.create_wifi_button()

        # Создание таймера для обновления времени
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Обновление каждую секунду

        # Добавление времени в правый угол меню
        menubar.setCornerWidget(self.time_label, Qt.Corner.TopRightCorner)

        # Инициализация отображения текущего языка
        self.update_language_display()

    def switch_language(self):
        """Переключает на следующий язык в списке"""
        thread = threading.Thread(target=self._switch_language_thread)
        thread.daemon = True
        thread.start()

    def _switch_language_thread(self):
        """Поток для переключения языка"""
        current_layout = self.get_current_layout()
        current_index = 0
        
        for i, lang in enumerate(self.languages):
            if lang['layout'] == current_layout:
                current_index = i
                break
        
        next_index = (current_index + 1) % len(self.languages)
        self.set_language(next_index)

    def set_language(self, index):
        """Устанавливает конкретный язык по индексу"""
        lang = self.languages[index]
        try:
            subprocess.run(['setxkbmap', '-layout', lang['layout']])
            subprocess.run([
                'notify-send', '-t', '1000',
                self.tr('Keyboard Language'),
                f"{lang['flag']} {lang['name']}"
            ])
            self.update_language_display()
        except Exception as e:
            print(f"Error: {e}")

    def get_current_layout(self):
        """Получает текущую раскладку клавиатуры"""
        try:
            result = subprocess.run(
                ['setxkbmap', '-query'], 
                capture_output=True, 
                text=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('layout:'):
                    return line.split(':')[1].strip()
        except:
            pass
        return "us"

    def update_language_display(self):
        """Обновляет отображение текущего языка в меню Language"""
        current_layout = self.get_current_layout()
        for lang in self.languages:
            if lang['layout'] == current_layout:
                current_lang_text = f"{lang['flag']} {lang['name']}"
                if hasattr(self, 'language_menu'):
                    self.language_menu.setTitle(current_lang_text)
                break

    
    def keyPressEvent(self, event: QKeyEvent):
        """Обробляє натискання клавіш у глобальному контексті"""
        WIN_KEYS = {Qt.Key.Key_Meta, Qt.Key.Key_Super_L, Qt.Key.Key_Super_R}

        # если Start открыт — печатаем в search_box (твоя логика)
        if hasattr(self, "start_menu") and self.start_menu.isVisible():
            if event.text():
                self.search_box.setFocus()
                cursor = self.search_box.cursorPosition()
                current_text = self.search_box.text()
                self.search_box.setText(current_text[:cursor] + event.text() + current_text[cursor:])
                self.search_box.setCursorPosition(cursor + 1)
                return

        if self.is_locked or self.is_splash_screen_active:
            return super().keyPressEvent(event)

        current_time = QDateTime.currentMSecsSinceEpoch()

        # --- Win+L (оставим твою обработку) ---
        if event.key() == Qt.Key.Key_L and (event.modifiers() & Qt.KeyboardModifier.MetaModifier):
            self._meta_combo_used = True
            self.lock_screen()
            return

        # --- Нажали Win (Meta/Super) ---
        if event.key() in WIN_KEYS:
            if event.isAutoRepeat():
                return
            self._meta_down = True
            self._meta_combo_used = False
            return

        # --- Пока Win зажат: ловим любые комбинации ---
        if getattr(self, "_meta_down", False):
            # любая другая клавиша + Win = "комбо было", Start потом не открывать
            if event.key() not in WIN_KEYS:
                self._meta_combo_used = True

            # Win + E -> открыть твой проводник
            if event.key() == Qt.Key.Key_E:
                self._on_win_combo("explorer")
                return

            # (опционально) если хочешь, чтобы Win+L работал даже когда modifiers не пришли:
            if event.key() == Qt.Key.Key_L:
                self.lock_screen()
                return

            # остальные Win+... пусть обрабатываются QShortcut-ами (Win+1..9 и т.п.)
            # поэтому не return

        # --- дальше твой существующий код ---
        if ((event.key() == Qt.Key.Key_Shift and event.modifiers() & Qt.KeyboardModifier.AltModifier) or
            (event.key() == Qt.Key.Key_Alt and event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
            if current_time - self.last_layout_switch_time > self.layout_switch_delay:
                self.switch_language()
                self.last_layout_switch_time = current_time

        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.unlock_screen()

        elif event.key() == Qt.Key.Key_Tab and (event.modifiers() & Qt.KeyboardModifier.AltModifier):
            if not self._switcher_active:
                self._open_switcher(reverse=bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier))
            else:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.task_switcher.prev()
                else:
                    self.task_switcher.next()
            return

        elif self._switcher_active and event.key() == Qt.Key.Key_Escape:
            self.task_switcher.cancel()
            self._switcher_active = False
            return

        super().keyPressEvent(event)


    def keyReleaseEvent(self, event):
        WIN_KEYS = {Qt.Key.Key_Meta, Qt.Key.Key_Super_L, Qt.Key.Key_Super_R}

        # отпустили Win — открыть Start только если Win был "один"
        if event.key() in WIN_KEYS:
            if event.isAutoRepeat():
                return
            if self._meta_down and not self._meta_combo_used:
                self.toggle_start_menu()
            self._meta_down = False
            self._meta_combo_used = False
            return

        # ... дальше твой код (ALT для switcher и т.д.)
        if self._switcher_active and event.key() == Qt.Key.Key_Alt:
            chosen = self.task_switcher.finalize()
            self._switcher_active = False
            if chosen:
                self.switch_window(chosen)
            return

        super().keyReleaseEvent(event)




    def _switch_keyboard_layout(self):
        """Переключает между раскладками (Linux и Windows)."""
        try:
            # Если у тебя есть self.languages, лучше брать layout'ы оттуда:
            layout_codes = [lang.get('layout', '').lower() for lang in getattr(self, 'languages', []) if lang.get('layout')]
            if not layout_codes:
                # fallback
                layout_codes = ['us', 'ru']

            # пытаемся узнать текущую раскладку
            current = self.get_current_layout().lower()
            try:
                idx = layout_codes.index(current)
            except ValueError:
                idx = 0

            next_idx = (idx + 1) % len(layout_codes)
            new_layout = layout_codes[next_idx]

            if os.name == 'nt':
                # Для Windows - оставляем существующую логику
                self._switch_windows_layout(new_layout)
            else:
                # Linux / X11
                subprocess.run(['setxkbmap', '-layout', new_layout])

            # Обновляем отображение и показываем уведомление
            self.update_language_display()
            # Покажем набольшую метку (можешь отобразить флаг/имя через mapping)
            self._show_layout_notification(new_layout.upper())

        except Exception as e:
            print(f"_switch_keyboard_layout error: {e}")


    def _switch_windows_layout(self, layout):
        """Переключение раскладки в Windows"""
        try:
            import ctypes
            # Получаем список всех раскладок
            layout_count = ctypes.windll.user32.GetKeyboardLayoutList(0, None)
            layout_list = (ctypes.c_void_p * layout_count)()
            ctypes.windll.user32.GetKeyboardLayoutList(layout_count, layout_list)
            
            # Находим нужную раскладку
            target_layout = None
            for layout_ptr in layout_list:
                lang_id = layout_ptr & 0xFFFF
                lang_name = self._get_language_name(lang_id)
                if layout.lower() in lang_name.lower():
                    target_layout = layout_ptr
                    break
            
            if target_layout:
                # Активируем нужную раскладку
                ctypes.windll.user32.ActivateKeyboardLayout(target_layout, 0)
        except Exception as e:
            print(f"Windows layout switch error: {e}")

    def _get_language_name(self, lang_id):
        """Получает название языка по ID"""
        language_names = {
            0x409: "EN",  # English
            0x419: "RU",  # Russian
            0x422: "UA",  # Ukrainian
        }
        return language_names.get(lang_id, "EN")

    def _show_layout_notification(self, text):
        """Показывает уведомление о текущей раскладке"""
        if self.current_layout_label:
            self.current_layout_label.deleteLater()
        
        self.current_layout_label = QLabel(text, self)
        self.current_layout_label.setObjectName("current_layout_label")
        self.current_layout_label.adjustSize()
        self.current_layout_label.move(self.width() - self.current_layout_label.width() - 20, 20)
        self.current_layout_label.show()
        self.current_layout_label.raise_()
        
        self.layout_timer.start(1000)  # Скрыть через 1 секунду

    def _hide_layout_label(self):
        """Скрывает уведомление"""
        if self.current_layout_label:
            self.current_layout_label.deleteLater()
            self.current_layout_label = None

    def create_start_menu(self):
        """Створює меню 'Пуск' з пошуком і можливістю закріплення застосунків (⭐).
        Підвантажує закріплені додатки з dock.config і показує їх у док-панелі."""
        all_apps = self.get_available_apps()

        # --- Зчитуємо pinned apps з dock.config (як у create_dock_panel) ---
        try:
            dock_config_path = files.get("dock.config", os.path.join("root", "bin", "dock.config"))
        except Exception:
            dock_config_path = os.path.join("root", "bin", "dock.config")

        self.pinned_apps = set()
        try:
            with open(dock_config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.pinned_apps.add(line)
        except FileNotFoundError:
            # Якщо немає файлу — просто залишаємо порожній набір
            self.pinned_apps = set()
        except Exception as e:
            print(f"[START MENU] Error reading dock.config: {e}")
            self.pinned_apps = set()

        # --- Створюємо віджет меню ---
        self.start_menu = QWidget(self)
        self.start_menu.setObjectName("win10StartMenu")
        self.start_menu.setFixedWidth(400)
        self.start_menu.setStyleSheet("background-color: rgba(40, 40, 40, 0.95); border-radius: 10px;")

        layout = QHBoxLayout(self.start_menu)
        layout.setContentsMargins(0, 0, 0, 0)

        # Ліва панель
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)

        # Пошук
        self.search_box = Input(
            parent=self,
            translator=self.tr,
            lang_code=getattr(self, "current_language", "en")
        )
        self.search_box.setPlaceholderText(self.tr("Search..."))
        self.search_box.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 8px;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid #4bcfff;
            }
        """)
        left_layout.addWidget(self.search_box)

        all_apps_label = QLabel(self.tr("all_apps"))
        all_apps_label.setStyleSheet("color: white; font-size: 14px; margin-top: 10px;")
        left_layout.addWidget(all_apps_label)

        # Список застосунків (з прокруткою)
        apps_scroll = QScrollArea()
        apps_scroll.setWidgetResizable(True)
        apps_scroll.setStyleSheet("background: transparent; border: none;")
        apps_scroll.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        apps_scroll.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))

        self.apps_widget = QWidget()
        self.apps_list_layout = QVBoxLayout(self.apps_widget)
        self.apps_list_layout.setSpacing(5)
        self.apps_list_layout.setContentsMargins(0, 0, 0, 0)

        self.app_buttons = []  # зберігаємо для фільтрації

        # --- Створюємо кнопки застосунків ---
        for app in all_apps:
            app_id = app.get("id", app.get("name"))
            app_name = app.get("name", str(app_id))
            app_icon = app.get("icon", "")

            # Основна кнопка запуску
            btn = QPushButton(app_name)
            if app_icon:
                btn.setIcon(QIcon(app_icon))
                btn.setIconSize(QSize(40, 40))
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 6px;
                    font-size: 14px;
                    color: white;
                    background: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 5px;
                }
            """)
            btn.clicked.connect(lambda _, a=app_id: self.handle_app_launch(a))

            # Зірочка — кнопка "Закріпити"
            is_pinned = app_id in self.pinned_apps
            star_btn = QPushButton("★" if is_pinned else "☆")
            star_btn.setFixedSize(26, 26)
            star_btn.setStyleSheet("""
                QPushButton {
                    color: gold;
                    background: transparent;
                    font-size: 18px;
                    border: none;
                }
                QPushButton:hover {
                    color: yellow;
                }
            """)

            # --- Обробник натискання на зірку ---
            def make_toggle(a, s):
                def toggle_pin():
                    if not hasattr(self, "pinned_apps"):
                        self.pinned_apps = set()

                    # --- Закрепить / открепить ---
                    was_pinned = a in self.pinned_apps
                    if was_pinned:
                        self.pinned_apps.remove(a)
                        s.setText("☆")
                        try:
                            self.remove_from_dock(a)
                        except Exception as e:
                            print(f"[START MENU] remove_from_dock error: {e}")
                    else:
                        self.pinned_apps.add(a)
                        s.setText("★")
                        try:
                            self.add_to_dock(a)
                        except Exception as e:
                            print(f"[START MENU] add_to_dock error: {e}")

                    # --- Сохраняем новый список в dock.config ---
                    try:
                        dock_path = files.get("dock.config", os.path.join("root", "bin", "dock.config"))
                    except Exception:
                        dock_path = os.path.join("root", "bin", "dock.config")

                    try:
                        with open(dock_path, "w", encoding="utf-8") as f:
                            for pid in sorted(self.pinned_apps):
                                f.write(pid + "\n")
                    except Exception as e:
                        print(f"[START MENU] Error saving dock.config: {e}")

                    # --- 🔄 Обновляем док-панель независимо от того, добавили или убрали ---
                    try:
                        self.refresh_dock_panel()
                    except Exception as e:
                        print(f"[START MENU] Error refreshing dock: {e}")
                return toggle_pin


            star_btn.clicked.connect(make_toggle(app_id, star_btn))

            # Контейнер для кнопки застосунку + зірочки
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)
            row_layout.addWidget(btn)
            row_layout.addWidget(star_btn)
            self.apps_list_layout.addWidget(row)

            # зберігаємо кнопку для пошуку (зберігаємо також row щоб приховувати повністю)
            self.app_buttons.append((row, app_name.lower()))

        apps_scroll.setWidget(self.apps_widget)
        left_layout.addWidget(apps_scroll)
        layout.addWidget(left_panel, 2)

        # --- Пошук по додатках ---
        def filter_apps():
            text = self.search_box.text().lower()
            for row, name in self.app_buttons:
                row.setVisible(text in name)
            self.update_start_menu_height()

        self.search_box.textChanged.connect(filter_apps)

        # --- Налаштування висоти ---
        self.start_menu.setFixedHeight(self.calculate_start_menu_height(len(all_apps)))
        self.start_menu.move(0, self.height() - self.start_menu.height())
        self.start_menu.hide()
        self.start_menu.is_showing = False

        # Закриття при кліку поза меню
        self.start_menu.installEventFilter(self)
        QApplication.instance().installEventFilter(self)

        # --- Додаємо вже закріплені додатки в док (щоб відобразити їх на панелі) ---
        # Викликаємо add_to_dock лише після того, як док ініціалізовано (create_dock_panel)
        try:
            for pid in list(self.pinned_apps):
                try:
                    self.add_to_dock(pid)
                except Exception:
                    # якщо док ще не створений — ігноруємо, док створиться пізніше і зчитає dock.config
                    pass
        except Exception as e:
            print(f"[START MENU] Error adding pinned apps to dock: {e}")


    def add_to_dock(self, app_id):
        """Додає додаток на док-панель"""
        if app_id not in self.dynamic_dock_buttons:
            self._add_dock_button(app_id)
            print(f"[DOCK] {app_id} закріплено")

    # def remove_from_dock(self, app_id):
    #     """Видаляє додаток із док-панелі"""
    #     if app_id in self.dynamic_dock_buttons:
    #         btn = self.dynamic_dock_buttons.pop(app_id)
    #         self.dock_layout.removeWidget(btn)
    #         btn.deleteLater()
    #         print(f"[DOCK] {app_id} відкріплено")

    def save_pinned_apps(self):
        """Зберігає закріплені програми у dock.config"""
        try:
            dock_config_path = files.get("dock.config", os.path.join("root", "bin", "dock.config"))
            with open(dock_config_path, "w", encoding="utf-8") as f:
                for app in sorted(self.pinned_apps):
                    f.write(app + "\n")
            print(f"[DOCK] Збережено {len(self.pinned_apps)} закріплених програм")
        except Exception as e:
            print(f"[DOCK] Помилка при збереженні dock.config: {e}")


    def remove_from_dock(self, app_id):
        """Удаляет одно приложение из док-панели"""
        if app_id in self.dynamic_dock_buttons:
            btn = self.dynamic_dock_buttons.pop(app_id)
            self.dock_layout.removeWidget(btn)
            btn.deleteLater()
            print(f"[DOCK] {app_id} откреплено")
        # сразу подчищаем лишние отступы
        self.dock_layout.update()


    def handle_app_launch(self, app_id):
        """Обработчик запуска приложения"""
        self.hide_menu()
        self.switch_window(app_id)

    def calculate_start_menu_height(self, num_buttons):
        """Обчислює висоту меню залежно від кількості кнопок"""
        min_height = 260  # 🔺 Раніше було 200
        max_visible = 10
        button_height = 44  # 🔺 Раніше було 35
        padding = 140  # 🔺 Раніше було 120
        total = min(num_buttons, max_visible) * button_height + padding
        return max(total, min_height)

    def eventFilter(self, source, event):
        """Закриває меню, якщо клік поза меню 'Пуск'"""
        if hasattr(self, 'start_menu') and self.start_menu.isVisible():
            if event.type() == QEvent.Type.MouseButtonPress:
                if source != self.start_menu and not self.start_menu.geometry().contains(event.globalPosition().toPoint()):
                    self.hide_menu()
        return super().eventFilter(source, event)

    def update_start_menu_height(self):
        """Оновлює висоту меню на основі видимих кнопок"""
        visible_count = sum(1 for btn, _ in self.app_buttons if btn.isVisible())
        new_height = self.calculate_start_menu_height(visible_count)
        self.start_menu.setFixedHeight(new_height)
        self.start_menu.move(0, self.height() - new_height)



    def get_available_apps(self):
        """Повертає список доступних застосунків та копіює іконки в icons_apps"""
        apps = []
        apps_dir = os.path.join("apps", "local")
        output_dir = "bin/icons/local_icons/inons_apps"

        if os.path.exists(apps_dir):
            for app_id in os.listdir(apps_dir):
                app_path = os.path.join(apps_dir, app_id)
                if os.path.isdir(app_path):
                    config_path = os.path.join(app_path, "config.json")
                    icon_src = os.path.join(app_path, "icon.png")
                    app_name = app_id.capitalize()

                    # Читаємо ім’я з config.json (якщо є)
                    if os.path.exists(config_path):
                        try:
                            with open(config_path, "r", encoding="utf-8") as f:
                                config = json.load(f)
                                app_name = config.get("name", app_name)
                        except Exception as e:
                            print(f"Помилка читання {config_path}: {e}")

                    # Копіюємо іконку
                    icon_dest_folder = os.path.join(output_dir, app_id)
                    icon_dest_path = os.path.join(icon_dest_folder, "icon.png")
                    if os.path.exists(icon_src):
                        try:
                            os.makedirs(icon_dest_folder, exist_ok=True)
                            shutil.copyfile(icon_src, icon_dest_path)
                        except Exception as e:
                            print(f"Не вдалося скопіювати іконку {app_id}: {e}")
                    else:
                        print(f"Іконка не знайдена: {icon_src}")

                    apps.append({
                        "id": app_id,
                        "name": app_name,
                        "icon": icon_dest_path if os.path.exists(icon_dest_path) else ""
                    })

        return apps

    def get_app_display_name(self, app_id: str) -> str:
        """Возвращает красивое имя приложения из apps/local/<id>/config.json, иначе fallback."""
        if not app_id:
            return "Win"

        # desktop / системные можно обработать отдельно
        if app_id == "desktop":
            return "Desktop"

        config_path = os.path.join("apps", "local", app_id, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f) or {}
                name = config.get("name")
                if isinstance(name, str) and name.strip():
                    return name.strip()
            except Exception as e:
                print(f"Помилка читання {config_path}: {e}")

        return app_id.capitalize()



    def show_menu(self):
        """Показывает меню с анимацией"""
        if not self.start_menu.is_showing:
            self.start_menu.show()
            self.start_menu.raise_()
            
            # Анимация появления (из прозрачного в непрозрачное)
            self.menu_animation = QPropertyAnimation(self.start_menu, b"windowOpacity")
            self.menu_animation.setDuration(200)
            self.menu_animation.setStartValue(0)
            self.menu_animation.setEndValue(1)
            self.menu_animation.start()
            
            self.start_menu.is_showing = True

    def hide_menu(self):
        """Скрывает меню с анимацией"""
        if self.start_menu.is_showing:
            # Анимация исчезновения (из непрозрачного в прозрачное)
            self.menu_animation = QPropertyAnimation(self.start_menu, b"windowOpacity")
            self.menu_animation.setDuration(200)
            self.menu_animation.setStartValue(1)
            self.menu_animation.setEndValue(0)
            self.menu_animation.finished.connect(self.start_menu.hide)
            self.menu_animation.start()
            
            self.start_menu.is_showing = False

    def toggle_start_menu(self):
        """Переключает состояние меню"""
        if self.start_menu.is_showing:
            self.hide_menu()
        else:
            self.show_menu()
    
    def create_window_switch_menu(self):
        """Создает меню для переключения между открытыми окнами."""
        self.window_switch_menu = Menu(self)
        
        # Получаем список открытых окон
        open_windows = [name for name, win in self.open_windows.items() if win and not win.isHidden()]
        
        # Добавляем пункты меню для каждого открытого окна
        for window_name in open_windows:
            action = QAction(window_name.capitalize(), self)
            action.triggered.connect(lambda _, name=window_name: self.switch_window(name))
            self.window_switch_menu.addAction(action)
        
        # Показываем меню в центре экрана
        self.window_switch_menu.popup(QPoint(self.width() // 2, self.height() // 2))

    def lock_screen(self):
        """Блокирует экран с анимацией."""
        # Скрываем рабочий стол и док-панель
        self.create_lock_screen()

        # Создаем экран блокировки, если он еще не создан или был удален
        if not hasattr(self, 'lock_widget') or self.lock_widget is None:
            self.create_lock_screen()

        # Показываем экран блокировки
        if self.lock_widget is not None:
            self.lock_widget.show()
            # self.password_input.setFocus()  # Активируем поле ввода пароля
            if hasattr(self, "password_input") and self.password_input is not None:
                self.password_input.setFocus()
            elif hasattr(self, "login_button") and self.login_button is not None:
                self.login_button.setFocus()

            # Анимация появления экрана блокировки сверху вниз
            self.animation = QPropertyAnimation(self.lock_widget, b"geometry")
            self.animation.setDuration(500)  # Длительность анимации 500 мс
            self.animation.setStartValue(QRect(0, -self.height(), self.width(), self.height()))
            self.animation.setEndValue(QRect(0, 0, self.width(), self.height()))
            self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце
            self.animation.start()

        
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
            pass
        elif system_platform == "Linux":
            # Команда для перезагрузки Linux
            QProcess.startDetached("reboot")
        else:
            print(f"Unsupported platform: {system_platform}")

    def update_win_menu(self, window_name: str):
        display = self.get_app_display_name(window_name)
        self.win_menu.setTitle(display)

        """
        Обновляет текст меню "Win" на активное окно и выделяет кнопку в доке.
        """
        # self.win_menu.setTitle(window_name)
        
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


    def create_wifi_button(self):
        """Создает кнопку Wi-Fi с возможностью настройки позиции и размера через widgets.json"""
        import os, json

        config_path = os.path.join("bin", "sys", "path", "widgets.json")
        config = {}

        # Загружаем конфиг
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"[create_wifi_button] Ошибка чтения widgets.json: {e}")

        # Получаем параметры кнопки
        wifi_cfg = config.get("wifi_button", {})
        btn_x = wifi_cfg.get("x", self.width() - 260)
        btn_y = wifi_cfg.get("y", self.height() - 65)
        btn_w = wifi_cfg.get("width", 60)
        btn_h = wifi_cfg.get("height", 60)

        if btn_y < 0:
            btn_y = self.height() + btn_y  # Считаем от нижнего края

        # === Контейнер ===
        self.wifi_button_container = QWidget(self)
        self.wifi_button_container.setFixedSize(btn_w, btn_h)
        self.wifi_button_container.move(btn_x, btn_y)

        # === Лэйаут ===
        layout = QVBoxLayout(self.wifi_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === Кнопка ===
        self.wifi_button = QPushButton()
        self.wifi_button.setFixedSize(btn_w, btn_h)
        self.wifi_button.setObjectName("wifi_button")
        self.wifi_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)

        # === Иконка Wi-Fi ===
        self.wifi_icon = QLabel(self.wifi_button)
        self.wifi_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def update_wifi_icon_size():
            icon_size = min(btn_w, btn_h) * 0.65  # Іконка займає 55% кнопки
            pixmap = QIcon(
                os.path.join("bin", "icons", "local_icons", "system", "wifi", "wifi_signal_4_lock.png")
            ).pixmap(int(icon_size), int(icon_size))
            self.wifi_icon.setPixmap(pixmap)
            self.wifi_icon.setGeometry(
                int((btn_w - icon_size) / 2),
                int((btn_h - icon_size) / 2),
                int(icon_size),
                int(icon_size)
            )

        update_wifi_icon_size()
        layout.addWidget(self.wifi_button)

        # === Виджет Wi-Fi ===
        self.wifi_window = Wifi(
            parent=self,
            translator=self.tr,
            lang_code=self.current_language
        )
        self.wifi_window.setParent(self)
        self.wifi_window.setObjectName("wifi_window")
        self.wifi_window.hide()

        # === Тень ===
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.wifi_window.setGraphicsEffect(shadow)

        # === Сигнал ===
        self.wifi_button.clicked.connect(self.toggle_wifi_control)


    def toggle_wifi_control(self):
        """Показывает/скрывает панель управления Wi-Fi"""
        if self.wifi_window.isVisible():
            self.hide_wifi_control()
        else:
            self.show_wifi_control()

    def show_wifi_control(self):
        """Показывает панель управления Wi-Fi с анимацией"""
        # Обновляем список сетей
        self.wifi_window.scan_networks()
        # 370 420
        # Устанавливаем начальную позицию (невидимая, за экраном справа)
        start_pos = QPoint(self.width(), self.height() - 580)
        end_pos = QPoint(self.width() - 370, self.height() - 580)
        
        self.wifi_window.move(start_pos)
        self.wifi_window.show()
        self.wifi_window.raise_()
        
        # Анимация появления
        self.wifi_animation = QPropertyAnimation(self.wifi_window, b"pos")
        self.wifi_animation.setDuration(200)
        self.wifi_animation.setStartValue(start_pos)
        self.wifi_animation.setEndValue(end_pos)
        self.wifi_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.wifi_animation.start()

    def hide_wifi_control(self):
        """Скрывает панель управления Wi-Fi с анимацией"""
        start_pos = self.wifi_window.pos()
        end_pos = QPoint(self.width(), self.height() - 520)
        
        # Анимация исчезновения
        self.wifi_animation = QPropertyAnimation(self.wifi_window, b"pos")
        self.wifi_animation.setDuration(200)
        self.wifi_animation.setStartValue(start_pos)
        self.wifi_animation.setEndValue(end_pos)
        self.wifi_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.wifi_animation.finished.connect(self.wifi_window.hide)
        self.wifi_animation.start()

    
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
        self.dynamic_dock_buttons = {}  # Для хранения динамически добавленных кнопок

        # Создаем фрейм для док-панели
        self.dock = QFrame()
        self.dock.setObjectName("dock")

        # Эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.dock.setGraphicsEffect(shadow)

        # Настройка лэйаута
        self.dock_layout = QHBoxLayout()
        self.dock_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dock_layout.setSpacing(15)
        self.dock_layout.setContentsMargins(10, 2, 10, 2)

        # Чтение конфигурации из файла dock.config
        dock_config_path = files.get("dock.config", os.path.join("root", "bin", "dock.config"))
        self.allowed_apps = []
        
        try:
            with open(dock_config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):  # Пропускаем пустые строки и комментарии
                        self.allowed_apps.append(line)
        except FileNotFoundError:
            print(f"Файл конфигурации {dock_config_path} не найден. Используются настройки по умолчанию.")
            self.allowed_apps = ["browser", "settings", "cmd"]  # Приложения по умолчанию
        except Exception as e:
            print(f"Ошибка при чтении файла конфигурации: {e}")
            self.allowed_apps = ["browser", "settings", "cmd"]  # Приложения по умолчанию

        # Создаем кнопки для стандартных приложений
        for app_name in self.allowed_apps:
            self._add_dock_button(app_name)

        self.dock.setLayout(self.dock_layout)
        self.main_layout.addWidget(self.dock, alignment=Qt.AlignmentFlag.AlignHCenter)

    def refresh_dock_panel(self):
        """Полностью пересоздаёт док-панель, чтобы соответствовать текущему dock.config"""
        try:
            dock_config_path = files.get("dock.config", os.path.join("root", "bin", "dock.config"))
        except Exception:
            dock_config_path = os.path.join("root", "bin", "dock.config")

        # --- Удаляем ВСЕ кнопки из панели ---
        for i in reversed(range(self.dock_layout.count())):
            item = self.dock_layout.itemAt(i)
            widget = item.widget()
            if widget:
                self.dock_layout.removeWidget(widget)
                widget.deleteLater()

        self.dock_buttons.clear()
        self.dynamic_dock_buttons.clear()

        # --- Перечитываем конфиг ---
        self.allowed_apps = []
        try:
            with open(dock_config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.allowed_apps.append(line)
        except FileNotFoundError:
            print(f"[DOCK] Конфигурация {dock_config_path} не найдена. Используются стандартные приложения.")
        except Exception as e:
            print(f"[DOCK] Ошибка при чтении файла конфигурации: {e}")

        # --- Если файл пустой, показываем cmd ---
        if not self.allowed_apps:
            self.allowed_apps = ["cmd"]

        # --- Добавляем кнопки заново ---
        for app_name in self.allowed_apps:
            try:
                self._add_dock_button(app_name)
            except Exception as e:
                print(f"[DOCK] Ошибка при добавлении {app_name}: {e}")

        # --- Обновляем панель ---
        self.dock_layout.update()
        print(f"[DOCK] Панель обновлена ({len(self.allowed_apps)} приложений).")




    def update_time(self):
        """
        Обновляет время и дату в метке.
        """
        pass


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
            # print(f"Окно {window_name} не открыто. Открываем...")
            self.open_windows[window_name] = getattr(self, f"create_{window_name}_window")()
            self.open_windows[window_name].show()

    def _add_dock_button(self, app_name):
        """Добавляет кнопку в док-панель (автоматический расчет размера иконок по dock_height)"""
        import os, json

        if app_name in self.dock_buttons:
            return  # Кнопка уже существует

        # === Загружаем настройки из widgets.json ===
        config_path = os.path.join("bin", "sys", "path", "widgets.json")
        dock_height = 45  # минимальная высота панели

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    dock_height = max(45, min(data.get("dock_height", 45), 65))
            except Exception as e:
                print(f"[_add_dock_button] Ошибка чтения widgets.json: {e}")

        # === Автоматический расчет размера иконок ===
        # при 45 → иконка 30, при 65 → иконка 44
        button_size = int(30 + (dock_height - 45) * (44 - 30) / (65 - 45))
        button_size = max(30, min(button_size, 44))

        # === Пути к иконке приложения ===
        possible_icon_paths = [
            os.path.join("apps", "local", app_name, f"{app_name}.png"),
            os.path.join("apps", "local", f"{app_name}.png"),
            os.path.join("apps", "local", app_name, "icon.png")
        ]
        icon_path = next((p for p in possible_icon_paths if os.path.exists(p)), None)
        if not icon_path:
            print(f"Иконка для {app_name} не найдена по путям: {possible_icon_paths}")
            return

        # === Создаем кнопку ===
        btn = JumpingButton(icon_path=icon_path, parent=self)
        btn.setFixedSize(button_size, button_size)
        btn.setIconSize(QSize(button_size, button_size))
        btn.clicked.connect(lambda _, n=app_name: self.switch_window(n))
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 8px;
            }
        """)

        # === Эффект тени ===
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(10)
        btn_shadow.setColor(QColor(0, 0, 0, 100))
        btn_shadow.setOffset(2, 2)
        btn.setGraphicsEffect(btn_shadow)

        # === Индикатор активности ===
        indicator = QLabel()
        indicator.setFixedSize(20, 4)
        indicator.setStyleSheet("background: transparent; border: none; border-radius: 2px;")

        # === Контейнер для кнопки и индикатора ===
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 8, 0, 0)
        container_layout.setSpacing(5)
        container_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(indicator, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.dock_layout.addWidget(container)
        self.dock_buttons[app_name] = (btn, indicator)

        # === Автоматический расчет ширины панели ===
        dock_padding = 20
        dock_spacing = 15
        dock_width = len(self.dock_buttons) * (button_size + dock_spacing) + dock_padding * 2

        # === Применяем рассчитанную высоту панели ===
        self.dock.setFixedSize(dock_width, dock_height)

            
    def switch_window(self, window_name):
        window_name = window_name.strip()

        # Если окно не в доке, добавляем его
        if window_name not in self.dock_buttons and window_name not in self.dynamic_dock_buttons:
            self._add_dynamic_dock_button(window_name)

        # Снимаем выделение со всех кнопок
        for name, (button, _) in {**self.dock_buttons, **self.dynamic_dock_buttons}.items():
            button.setStyleSheet("")

        # Проверяем, есть ли окно в self.open_windows
        if window_name in self.open_windows:
            if self.open_windows[window_name] is None:
                # Динамически загружаем модуль приложения из apps/local
                try:
                    module_name = f"apps.local.{window_name}.{window_name}"
                    module = __import__(module_name, fromlist=[window_name])
                    app_class = getattr(module, f"{window_name.capitalize()}Window")
                    
                    # Создаем экземпляр приложения с передачей языка и переводчика
                    self.open_windows[window_name] = app_class(
                        parent=self,
                        window_name=window_name,
                        translator=self.tr,
                        lang_code=self.current_language  # Передаем текущий язык
                    )
                except Exception as e:
                    print(f"Ошибка загрузки приложения {window_name}: {e}")
                    return

            window = self.open_windows[window_name]

            if window is not None:
                if hasattr(window, 'minimized') and window.minimized:
                    window.restore_window()
                else:
                    if window.isMinimized():
                        window.showNormal()
                        window.activateWindow()
                    else:
                        # self.animate_window_open(window)
                        window.show()
                        window.raise_()
                        window.activateWindow()
                        window.activate()

                self.active_window_name = window_name
                self.update_win_menu(window_name)
                self.active_windows[window_name] = True
                self.update_dock_indicators()

                if window_name in {**self.dock_buttons, **self.dynamic_dock_buttons}:
                    button, _ = {**self.dock_buttons, **self.dynamic_dock_buttons}[window_name]
                    button.setStyleSheet("background-color: #181818; border-radius: 8px;")

    def handle_app_hang(self, app_name):
        """Обработчик зависания приложения."""
        error_message = f"Приложение '{app_name}' не отвечает. Закрыть его?"
        reply = StellarMessageBox.question(
            self,
            "Ошибка",
            error_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if app_name in self.open_windows:
                self.open_windows[app_name].close()
                self.open_windows[app_name] = None
                self.update_dock_indicators()

    def animate_window_open(self, window):
        """Анимация открытия окна"""
        # Устанавливаем начальный размер окна (очень маленький)
        start_size = QSize(10, 10)
        end_size = window.size()

        # Устанавливаем начальный размер окна
        window.resize(start_size)

        # Создаем анимацию для изменения размера окна
        self.animation = QPropertyAnimation(window, b"size")
        self.animation.setDuration(150)  # Длительность анимации в миллисекундах
        self.animation.setStartValue(start_size)
        self.animation.setEndValue(end_size)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце

        # Запускаем анимацию
        self.animation.start()

    def _add_dynamic_dock_button(self, app_name):
        """Добавляет временную кнопку в док-панель с автоподстройкой размера под dock_height"""
        import os, json

        if app_name in self.dynamic_dock_buttons:
            return  # Кнопка уже существует

        # === Загружаем настройки из widgets.json ===
        config_path = os.path.join("bin", "sys", "path", "widgets.json")
        dock_height = 45  # минимум

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    dock_height = max(45, min(data.get("dock_height", 45), 65))
            except Exception as e:
                print(f"[_add_dynamic_dock_button] Ошибка чтения widgets.json: {e}")

        # === Автоматический расчет размера кнопки ===
        # при 45 → 30, при 65 → 44
        button_size = int(30 + (dock_height - 45) * (44 - 30) / (65 - 45))
        button_size = max(30, min(button_size, 44))

        # === Пути к иконке ===
        possible_icon_paths = [
            os.path.join("apps", "local", app_name, f"{app_name}.png"),
            os.path.join("apps", "local", f"{app_name}.png"),
            os.path.join("apps", "local", app_name, "icon.png"),
            os.path.join("bin", "icons", "local_icons", "system", "default_app.png")
        ]
        icon_path = next((p for p in possible_icon_paths if os.path.exists(p)), None)
        if not icon_path:
            print(f"Иконка для {app_name} не найдена по путям: {possible_icon_paths}")
            return

        # === Кнопка ===
        btn = JumpingButton(icon_path=icon_path, parent=self)
        btn.setFixedSize(button_size, button_size)
        btn.setIconSize(QSize(button_size, button_size))
        btn.clicked.connect(lambda _, n=app_name: self.switch_window(n))

        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 8px;
            }
        """)

        # === Эффект тени ===
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(10)
        btn_shadow.setColor(QColor(0, 0, 0, 100))
        btn_shadow.setOffset(2, 2)
        btn.setGraphicsEffect(btn_shadow)

        # === Индикатор активности ===
        indicator = QLabel()
        indicator.setFixedSize(20, 4)
        indicator.setStyleSheet("background: transparent; border: none; border-radius: 2px;")

        # === Контейнер ===
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 8, 0, 0)
        container_layout.setSpacing(5)
        container_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(indicator, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.dock_layout.addWidget(container)
        self.dynamic_dock_buttons[app_name] = (btn, indicator)

        # === Пересчет ширины панели ===
        dock_padding = 20
        dock_spacing = 15
        dock_width = (len(self.dock_buttons) + len(self.dynamic_dock_buttons)) * (button_size + dock_spacing) + dock_padding * 2

        # === Применяем рассчитанную высоту панели ===
        self.dock.setFixedSize(dock_width, dock_height)

    def update_dock_indicators(self):
        """
        Обновляет индикаторы запущенных приложений в доке.
        Автоматически подстраивает размер панели и кнопок по dock_height.
        """
        import os, json

        if not hasattr(self, 'active_windows'):
            self.active_windows = {}

        # === Загружаем dock_height из widgets.json ===
        config_path = os.path.join("bin", "sys", "path", "widgets.json")
        dock_height = 45  # минимальная высота панели

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    dock_height = max(45, min(data.get("dock_height", 45), 65))
            except Exception as e:
                print(f"[update_dock_indicators] Ошибка чтения widgets.json: {e}")

        # === Автоматический расчет размера кнопок ===
        # при 45 → 30, при 65 → 44
        button_size = int(30 + (dock_height - 45) * (44 - 30) / (65 - 45))
        button_size = max(30, min(button_size, 44))

        # === Список окон для удаления ===
        windows_to_remove = []

        # === Обновляем индикаторы для стандартных кнопок ===
        for window_name, (button, indicator) in self.dock_buttons.items():
            window = self.open_windows.get(window_name)
            if window is not None and not window.isHidden():  # Окно открыто и не скрыто
                indicator.setStyleSheet("""
                    background-color: #4bcfff;
                    border: none;
                    border-radius: 22px;
                    min-height: 4px;
                """)
            elif window is not None and window.minimized:  # Окно свернуто
                indicator.setStyleSheet("""
                    background-color: #4bcfff;
                    border: none;
                    border-radius: 22px;
                    min-height: 4px;
                    opacity: 0.5;
                """)
            else:  # Окно закрыто
                indicator.setStyleSheet("""
                    background-color: transparent;
                    border: none;
                """)

        # === Обработка динамических кнопок ===
        for window_name, (button, indicator) in self.dynamic_dock_buttons.items():
            window = self.open_windows.get(window_name)
            if window is None:  # Окно полностью закрыто
                windows_to_remove.append(window_name)
            elif not window.isHidden():  # Окно открыто
                indicator.setStyleSheet("""
                    background-color: #4bcfff;
                    border: none;
                    border-radius: 22px;
                    min-height: 4px;
                """)
            elif window.minimized:  # Свернуто
                indicator.setStyleSheet("""
                    background-color: #4bcfff;
                    border: none;
                    border-radius: 22px;
                    min-height: 4px;
                    opacity: 0.5;
                """)

        # === Удаляем кнопки закрытых окон ===
        for window_name in windows_to_remove:
            if window_name in self.dynamic_dock_buttons:
                container = self.dynamic_dock_buttons[window_name][0].parent()
                self.dock_layout.removeWidget(container)
                container.deleteLater()
                del self.dynamic_dock_buttons[window_name]

        # === Пересчет ширины и высоты панели ===
        dock_padding = 20
        dock_spacing = 15
        dock_width = (len(self.dock_buttons) + len(self.dynamic_dock_buttons)) * (button_size + dock_spacing) + dock_padding * 2

        self.dock.setFixedSize(dock_width, dock_height)

    def _on_win_combo(self, window_name: str):
        # помечаем, что Win использовали в комбинации (чтобы Start не открывался)
        self._meta_combo_used = True
        self.switch_window(window_name)



    def reload_widgets(self):
        """Перезавантажує системні елементи без перезапуску ОС"""
        try:
            config_path = os.path.join("bin", "sys", "path", "widgets.json")
            if not os.path.exists(config_path):
                print("[reload_widgets] Файл widgets.json не знайдено.")
                return

            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # === TIME BUTTON ===
            if hasattr(self, "time_button_container") and self.time_button_container:
                cfg = data.get("time_button", {})
                x = cfg.get("x", 1245)
                y = cfg.get("y", -60)
                w = cfg.get("width", 120)
                h = cfg.get("height", 45)

                if y < 0:
                    y = self.height() + y

                self.time_button_container.setGeometry(x, y, w, h)
                self.time_button.setFixedSize(w, h)
                self.time_button_container.show()
                self.time_button.show()
                print("[reload_widgets] TIME BUTTON оновлено.")

            # === START BUTTON ===
            cfg = data.get("start_button", {})
            x = cfg.get("x", 0)
            y = cfg.get("y", -60)
            w = cfg.get("width", 45)
            h = cfg.get("height", 45)

            if y < 0:
                y = self.height() + y

            target = None
            if hasattr(self, "start_button_container"):
                target = self.start_button_container
            elif hasattr(self, "start_button"):
                target = self.start_button
            elif hasattr(self, "dock_start_container"):
                target = self.dock_start_container

            if target:
                target.setGeometry(x, y, w, h)
                try:
                    if hasattr(self, "start_button"):
                        self.start_button.setFixedSize(w, h)
                        self.start_button.show()
                except Exception:
                    pass
                target.show()
                print("[reload_widgets] START BUTTON оновлено.")
            else:
                print("[reload_widgets] START BUTTON не знайдено у вікні.")

            # === WIFI BUTTON ===
            cfg = data.get("wifi_button", {})
            x = cfg.get("x", 1123)
            y = cfg.get("y", -60)
            w = cfg.get("width", 45)
            h = cfg.get("height", 45)

            if y < 0:
                y = self.height() + y

            wifi_target = None
            if hasattr(self, "wifi_button_container"):
                wifi_target = self.wifi_button_container
            elif hasattr(self, "wifi_button"):
                wifi_target = self.wifi_button

            if wifi_target:
                wifi_target.setGeometry(x, y, w, h)
                try:
                    if hasattr(self, "wifi_button"):
                        self.wifi_button.setFixedSize(w, h)
                        self.wifi_button.show()
                except Exception:
                    pass
                wifi_target.show()
                print("[reload_widgets] WIFI BUTTON оновлено.")
            else:
                print("[reload_widgets] WIFI BUTTON не знайдено у вікні.")

            # === VOLUME BUTTON ===
            cfg = data.get("volume_button", {})
            x = cfg.get("x", 1179)
            y = cfg.get("y", -60)
            w = cfg.get("width", 45)
            h = cfg.get("height", 45)

            if y < 0:
                y = self.height() + y

            vol_target = None
            if hasattr(self, "volume_button_container"):
                vol_target = self.volume_button_container
            elif hasattr(self, "volume_button"):
                vol_target = self.volume_button

            if vol_target:
                vol_target.setGeometry(x, y, w, h)
                try:
                    if hasattr(self, "volume_button"):
                        self.volume_button.setFixedSize(w, h)
                        self.volume_button.show()
                except Exception:
                    pass
                vol_target.show()
                print("[reload_widgets] VOLUME BUTTON оновлено.")
            else:
                print("[reload_widgets] VOLUME BUTTON не знайдено у вікні.")

            print("[reload_widgets] ✅ Усі віджети оновлено і відображено.")

        except Exception as e: 
            print(f"[reload_widgets] ❌ Помилка: {e}")




# В начало файла, вместе с другими импортами
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QTimer


# --- Проверка статуса установки ---
def check_installation_status():
    username = get_current_username()

    install_file = os.path.join(BASE_DIR, "root", username, "user", "install")
    if not os.path.exists(install_file):
        # print("[ERROR] Файл установки не найден:", install_file)
        return False

    try:
        with open(install_file, "r", encoding="utf-8") as f:
            status = f.read().strip().lower()
        if status == "yes":
            return True
        else:
            print("[INFO] Приложение не установлено (install != yes). Запуск отменён.")
            return False
    except Exception as e:
        print(f"[ERROR] Ошибка чтения файла установки: {e}")
        return False



from bin.sys.class_.creat_user import SetupWizard


# --- Основная функция ---
# if __name__ == "__main__":

def main():
    if not check_installation_status():
        app = QApplication(sys.argv)
        setup = SetupWizard()
        setup.show()
        sys.exit(app.exec())


    # Устанавливаем глобальный обработчик исключений
    sys.excepthook = global_exception_handler

    try:
        app = QApplication(sys.argv)
        # ПРЕДВАРИТЕЛЬНАЯ ИНИЦИАЛИЗАЦИЯ QWebEngineView ДЛЯ УСКОРЕНИЯ ЗАПУСКА
        # print("Preloading QWebEngineView...")
        # preload_webengine = QWebEngineView()
        # preload_webengine.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        # preload_webengine.settings().setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        # preload_webengine.setHtml("<html><body><p>Loading...</p></body></html>")
        # QTimer.singleShot(100, preload_webengine.deleteLater)
        QApplication.processEvents()
        
        # Создаём и показываем основное окно
        window = MacOSWindow()
        window.show()

        # Таймер для проверки зависания
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(1000)

        sys.exit(app.exec())
    except Exception as e:
        global_exception_handler(type(e), e, e.__traceback__)


if __name__ == "__main__":
    main()