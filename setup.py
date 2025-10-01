import sys
import os
import shutil
# импорт наверху рядом с остальными:
from PyQt6.QtCore import QMargins
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



# --- ALT+TAB SWITCHER -------------------------------------------------
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect, QScrollArea, QFrame
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QSize, QRect, QEasingCurve, QPropertyAnimation

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
        self.wifi = pywifi.PyWiFi()
        self.iface = None

        stylesheet = load_stylesheet("styles.qss")
        self.setStyleSheet(stylesheet)
        
        try:
            if self.wifi.interfaces():
                self.iface = self.wifi.interfaces()[0]
            else:
                StellarMessageBox.warning(self, self.tr("Error"), self.tr("Error_wifi"))
        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"), f"Error initialization Wi-Fi: {str(e)}")
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
        """Создает кнопку меню Пуск в правом нижнем углу"""
        # Создаем контейнер для кнопки
        self.start_button_container = QWidget(self)
        self.start_button_container.setFixedSize(60, 60)
        self.start_button_container.move(
            10,  # Позиция слева от кнопки времени
            self.height() - 65   # Такая же высота как у кнопки времени
        )
        
        # Вертикальный лэйаут для кнопки
        layout = QVBoxLayout(self.start_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем кнопку
        self.start_button = QPushButton()
        self.start_button.setFixedSize(60, 60)
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
        
        # Иконка меню Пуск
        self.start_icon = QLabel(self.start_button)
        self.start_icon.setPixmap(QIcon(os.path.join("bin", "icons", "local_icons", "start.png")).pixmap(60, 60))
        self.start_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_icon.setGeometry(15, 15, 30, 30)
        
        layout.addWidget(self.start_button)
        
        # Подключаем клик по кнопке меню Пуск
        self.start_button.clicked.connect(self.toggle_start_menu)

    def create_volume_button(self):
        """Создает кнопку громкости в правом нижнем углу"""
        # Создаем контейнер для кнопки
        self.volume_button_container = QWidget(self)
        self.volume_button_container.setFixedSize(60, 60)
        self.volume_button_container.move(
            self.width() - 190,  # Позиция слева от кнопки времени
            self.height() - 65   # Такая же высота как у кнопки времени
        )
        
        # Вертикальный лэйаут для кнопки
        layout = QVBoxLayout(self.volume_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем кнопку
        self.volume_button = QPushButton()
        self.volume_button.setFixedSize(60, 60)

        self.volume_button.setObjectName("volume_button")
        
        # Иконка громкости
        self.volume_icon = QLabel(self.volume_button)
        self.volume_icon.setPixmap(QIcon(os.path.join("bin", "icons", "local_icons", "system", "volume.png")).pixmap(30, 30))
        self.volume_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_icon.setGeometry(15, 15, 30, 30)
        
        layout.addWidget(self.volume_button)
        
        # Создаем виджет управления громкостью (изначально скрыт)
        self.volume_widget = VolumeControlWidget(
            parent=self,
            translator=self.tr,  # Передаем функцию перевода из MacOSWindow
            lang_code=self.current_language  # Передаем текущий язык
        )
        self.volume_widget.setParent(self)

        self.volume_widget.hide()
        
        # Подключаем клик по кнопке громкости
        self.volume_button.clicked.connect(self.toggle_volume_control)
        
        # Таймер для обновления иконки громкости
        self.volume_timer = QTimer(self)
        self.volume_timer.timeout.connect(self.update_volume_icon)
        self.volume_timer.start(1000)

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
        """Создает кнопку с временем и датой в правом нижнем углу"""
        # Создаем контейнер для кнопки
        self.time_button_container = QWidget(self)
        self.time_button_container.setFixedSize(120, 60)
        self.time_button_container.move(
            self.width() - 120,  # Правый край с отступом
            self.height() - 65   # Нижний край с отступом
        )
        
        # Вертикальный лэйаут для кнопки
        layout = QVBoxLayout(self.time_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем кнопку
        self.time_button = QPushButton()
        self.time_button.setFixedSize(120, 60)

        self.time_button.setObjectName("time_button")

        
        # Лэйаут для текста внутри кнопки
        text_layout = QVBoxLayout(self.time_button)
        text_layout.setContentsMargins(5, 5, 5, 5)
        text_layout.setSpacing(0)
        
        # Метка для времени
        self.time_button_time = QLabel()
        self.time_button_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.time_button_time.setObjectName("time_button_time")
        
        # Метка для даты
        self.time_button_date = QLabel()
        self.time_button_date.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.time_button_date.setObjectName("time_button_date")
        
        text_layout.addWidget(self.time_button_time)
        text_layout.addWidget(self.time_button_date)
        
        layout.addWidget(self.time_button)
        
        # Создаем виджет календаря (изначально скрыт)
        self.calendar_widget = CalendarWidget(
            parent=self,
            translator=self.tr,  # Передаем функцию перевода из MacOSWindow
            lang_code=self.current_language  # Передаем текущий язык
        )
        self.calendar_widget.setParent(self)
        self.calendar_widget.setFixedSize(350, 350)
        self.calendar_widget.move(
            self.width() - 370,  # Позиционируем слева от кнопки
            self.height() - 420  # Позиционируем выше кнопки
        )
        self.calendar_widget.hide()
        
        # Подключаем клик по кнопке времени
        self.time_button.clicked.connect(self.toggle_calendar)
        
        # Обновляем время сразу
        self.update_time_button()
        
        # Таймер для обновления времени каждую секунду
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
        """Обновляет текст на кнопке времени"""
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        
        # Форматируем время и дату
        time_text = current_time.toString("hh:mm:ss")
        date_text = current_date.toString("dd.MM.yyyy")
        
        # Устанавливаем текст
        self.time_button_time.setText(time_text)
        self.time_button_date.setText(date_text)


    def resizeEvent(self, event):
        """Обновляет позицию элементов при изменении размера окна"""
        super().resizeEvent(event)
        if hasattr(self, 'time_button_container'):
            self.time_button_container.move(
                self.width() - 120,
                self.height() - 65
            )
        if hasattr(self, 'volume_button_container'):
            self.volume_button_container.move(
                self.width() - 190,
                self.height() - 65
            )
        if hasattr(self, 'wifi_button_container'):
            self.wifi_button_container.move(
                self.width() - 260,
                self.height() - 65
            )
        if hasattr(self, 'calendar_widget') and self.calendar_widget.isVisible():
            self.calendar_widget.move(
                self.width() - 370,
                self.height() - 420
            )
        if hasattr(self, 'volume_widget') and self.volume_widget.isVisible():
            self.volume_widget.move(
                self.width() - 370,
                self.height() - 140
            )
        if hasattr(self, 'wifi_window') and self.wifi_window.isVisible():
            self.wifi_window.move(
                self.width() - 370,
                self.height() - 520
            )
        self.load_background_image()

    def create_lock_screen(self):
        """Создает экран блокировки."""
        self.is_locked = True  # Устанавливаем флаг блокировки
        # Если lock_widget уже существует, удаляем его
        if hasattr(self, 'lock_widget') and self.lock_widget is not None:
            self.lock_widget = None

        # Создаем новый виджет для экрана блокировки
        self.lock_widget = QWidget(self)
        self.lock_widget.setGeometry(0, 0, self.width(), self.height())

        # Устанавливаем фон (например, изображение)
        background_pixmap = QPixmap(os.path.join("bin", "icons", "local_icons", "IconOs", "lock.jpg"))
        background_label = QLabel(self.lock_widget)
        background_label.setPixmap(background_pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        background_label.setGeometry(0, 0, self.width(), self.height())

        # Логотип
        icon_dir_path = os.path.join("bin", "icons", "local_icons", "IconOs", "OS.png")
        logo_pixmap = QPixmap(icon_dir_path)
        scaled_pixmap = logo_pixmap.scaled(logo_pixmap.width() // 2, logo_pixmap.height() // 2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label = QLabel(self.lock_widget)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setGeometry(
            (self.width() - scaled_pixmap.width()) // 2,
            (self.height() - scaled_pixmap.height()) // 2 - 50,
            scaled_pixmap.width(),
            scaled_pixmap.height()
        )

        # Метка для отображения времени (часы:минуты:секунды)
        self.time_label = QLabel(self.lock_widget)

        self.time_label.setObjectName("time_label")
        self.time_label.setGeometry(10, 10, 150, 30)  # Левый верхний угол
        self.update_time_label()  # Установить начальное значение

        # Таймер для обновления времени каждую секунду
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_time_label)
        self.clock_timer.start(1000)  # 1000 мс = 1 секунда

        # Поле ввода пароля
        self.password_input = InputPassword(
            parent=self.lock_widget,
            placeholder_text=self.tr("Password"),
            initial_text="",  # Можно указать заранее введённый текст, если нужно
            echo_mode=QLineEdit.EchoMode.Password,  # Или QLineEdit.EchoMode.Normal для обычного текста
            translator=self.tr,  # Передаем функцию перевода из MacOSWindow
            lang_code=self.current_language  # Передаем текущий язык
        )
        self.password_input.setGeometry(
            (self.width() - 200) // 2,
            logo_label.y() + logo_label.height() + 20,
            200,
            30
        )
        self.password_input.returnPressed.connect(self.unlock_screen)
        self.password_input.setFocus()


        # Добавляем кнопку с картинкой 50x50
        self.main_button = QPushButton(self.lock_widget)
        self.main_button.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "IconOs", "shutdown.png")))  # Укажите путь к изображению
        self.main_button.setIconSize(QSize(50, 50))
        self.main_button.setFixedSize(50, 50)

        self.main_button.setObjectName("main_button")
        self.main_button.move((self.width() - 50) // 2, logo_label.y() + logo_label.height() + 80)
        self.main_button.clicked.connect(self.toggle_additional_buttons)

        # Контейнер для дополнительных кнопок
        self.additional_buttons_container = QWidget(self.lock_widget)
        self.additional_buttons_container.setGeometry(
            (self.width() - 150) // 2,  # Центрируем по горизонтали
            self.main_button.y() - 60,  # Размещаем выше основной кнопки
            150,  # Ширина контейнера
            100   # Высота контейнера
        )

        self.additional_buttons_container.setObjectName("additional_buttons_container")
        self.additional_buttons_container.hide()  # Скрываем контейнер по умолчанию

        # Вертикальный лэйаут для дополнительных кнопок
        additional_layout = QVBoxLayout(self.additional_buttons_container)
        additional_layout.setSpacing(10)
        additional_layout.setContentsMargins(10, 10, 10, 10)

        # Первая дополнительная кнопка
        self.button1 = QPushButton(self.tr("Shutdown"), self)  # Текст кнопки
        self.button1.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "IconOs", "shutdown.png")))  # Иконка кнопки
        self.button1.setIconSize(QSize(30, 30))  # Размер иконки
        self.button1.setFixedSize(120, 40)  # Размер кнопки (ширина, высота)
        self.button1.clicked.connect(self.shutdown_system)  # Используем clicked.connect

        self.button1.setObjectName("shutdown_button")
        additional_layout.addWidget(self.button1)  # Добавляем кнопку в лэйаут

        # Вторая дополнительная кнопка
        self.button2 = QPushButton(self.tr("Reboot"), self)  # Текст кнопки
        self.button2.setIcon(QIcon(os.path.join("bin", "icons", "local_icons", "IconOs", "reboot.png")))  # Иконка кнопки
        self.button2.setIconSize(QSize(30, 30))  # Размер иконки
        self.button2.setFixedSize(120, 40)  # Размер кнопки (ширина, высота)
        self.button2.clicked.connect(self.reboot_system)  # Используем clicked.connect

        self.button2.setObjectName("reboot_button")
        additional_layout.addWidget(self.button2)  # Добавляем кнопку в лэйаут

        # Обработчики событий для скрытия/показа контейнера
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
        """Разблокирует экран, если пароль верный."""
        # Проверяем, существует ли еще виджет и поле ввода пароля
        if not hasattr(self, 'lock_widget') or self.lock_widget is None:
            return  # Если виджет уже удален, выходим из метода

        if not hasattr(self, 'password_input') or self.password_input is None:
            return  # Если поле ввода пароля уже удалено, выходим из метода

        # Проверяем, существует ли объект password_input
        try:
            # Проверяем пароль (например, пароль "0000")
            if self.password_input.text() == "":
                self.is_locked = False

                # Остановить и удалить таймер и метку времени
                if hasattr(self, "clock_timer"):
                    self.clock_timer.stop()
                    self.clock_timer.deleteLater()

                self.animation = QPropertyAnimation(self.lock_widget, b"geometry")
                self.animation.setDuration(200)
                self.animation.setStartValue(QRect(0, 0, self.width(), self.height()))
                self.animation.setEndValue(QRect(0, -self.height(), self.width(), self.height()))
                self.animation.finished.connect(self.lock_widget.deleteLater)
                self.animation.start()

                # Удаляем виджет после завершения анимации
                self.animation.finished.connect(self.lock_widget.deleteLater)
                self.animation.start()
            else:
                # Показываем сообщение об ошибке
                StellarMessageBox.warning(self, self.tr("Error"), self.tr("Incorrect password!"))
        except RuntimeError:
            # Если объект уже удален, просто выходим из метода
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
        """Загрузка фонового изображения для всего приложения"""
        try:
            with open(self.desk_config, "r", encoding="utf-8") as f:
                image_path = f.read().strip()
            
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path).scaled(
                    self.size(), 
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.background.setPixmap(pixmap)
                self.background.setGeometry(0, 0, self.width(), self.height())
        except Exception as e:
            pass


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

    # def create_all_windows(self):
    #     """
    #     Инициализация окон. Окна создаются только при первом открытии.
    #     """
    #     self.open_windows = {
    #         "browser": None,
    #         "cmd": None,
    #         "settings": None,
    #         "calc": None,
    #         "explorer": None,
    #         "notebook": None,
    #         "Vscode": None,
    #         "app_store": None
    #     }

    def create_all_windows(self):
        """
        Инициализация окон. Окна создаются только при первом открытии.
        """
        config_path = r"root\bin\list_apps\list_apps.config"
        
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
                "app_store": None
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
                "app_store": None
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
                "app_store": None
            }


    # def create_menu(self):
    #     """
    #     Создает меню с использованием QMenuBar и добавляет время/дату в правый угол.
    #     """
    #     menubar = self.menuBar()
    #     menubar.setObjectName("main_menu_bar")

    #     # Меню "Win" (динамически изменяет название на активное окно)
    #     self.win_menu = menubar.addMenu("Win")
    #     self.update_win_menu("desktop")

    #     # Меню "Power" (Выключение и перезагрузка)
    #     power_menu = menubar.addMenu(self.tr("Power"))

    #     # Действие для выключения
    #     shutdown_action = QAction(self.tr("Shutdown"), self)
    #     shutdown_action.triggered.connect(self.shutdown_system)
    #     power_menu.addAction(shutdown_action)

    #     # Действие для перезагрузки
    #     reboot_action = QAction(self.tr("Reboot"), self)
    #     reboot_action.triggered.connect(self.reboot_system)
    #     power_menu.addAction(reboot_action)

    #     # Действие для блокировки экрана
    #     lock_action = QAction(self.tr("Lock"), self)  # Кнопка блокировки
    #     lock_action.triggered.connect(self.lock_screen)  # Связываем с методом блокировки
    #     power_menu.addAction(lock_action)  # Добавляем в меню "Power"
        
    #     # Добавляем разделитель
    #     power_menu.addSeparator()
        
    #     # Действие для закрытия приложения
    #     quit_action = QAction(self.tr("Quit"), self)
    #     # quit_action.setShortcut("Ctrl+Q")  # Горячая клавиша
    #     quit_action.triggered.connect(self.close)  # Закрываем главное окно
    #     power_menu.addAction(quit_action)

    #     # Создание метки для времени и даты
    #     self.time_label = QLabel()
    #     self.time_label.setFont(QFont("Helvetica", 14))
    #     self.time_label.setStyleSheet("color: black; padding: 5px;")
    #     # self.update_time()  # Обновляем сразу при старте
    #     self.create_wifi_button()

    #     # Создание таймера для обновления времени
    #     self.timer = QTimer(self)
    #     self.timer.timeout.connect(self.update_time)
    #     self.timer.start(1000)  # Обновление каждую секунду

    #     # Добавление времени в правый угол меню
    #     menubar.setCornerWidget(self.time_label, Qt.Corner.TopRightCorner)
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
        if hasattr(self, "start_menu") and self.start_menu.isVisible():
            if event.text():  # перевірка, що це текстовий символ
                self.search_box.setFocus()
                cursor = self.search_box.cursorPosition()
                current_text = self.search_box.text()
                # вставляємо символ у поточну позицію курсора
                self.search_box.setText(current_text[:cursor] + event.text() + current_text[cursor:])
                self.search_box.setCursorPosition(cursor + 1)
                return  # не передаємо подію далі
        if self.is_locked or self.is_splash_screen_active:
            return super().keyPressEvent(event)

        current_time = QDateTime.currentMSecsSinceEpoch()
        
        # Win key (Meta) - открытие/закрытие меню
        # if event.key() == Qt.Key.Key_Meta:
        #     self.toggle_start_menu()
        #     return
        # Win + L (у вас Win + Y)
        if event.key() == Qt.Key.Key_L and event.modifiers() & Qt.KeyboardModifier.MetaModifier:
            self.lock_screen()
            return  # дуже важливо повернутися, щоб не відкривалося меню

        # Win key — відкриття/закриття меню
        elif event.key() == Qt.Key.Key_Meta:
            self.toggle_start_menu()
            return
        
        # # Win + L (вместо Ctrl + L)
        # if event.key() == Qt.Key.Key_Y and event.modifiers() & Qt.KeyboardModifier.MetaModifier:
        #     self.lock_screen()
        # Alt + Shift (оставляем без изменений)
        # elif ((event.key() == Qt.Key.Key_Shift and event.modifiers() & Qt.KeyboardModifier.AltModifier) or
        #      (event.key() == Qt.Key.Key_Alt and event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
        #     if current_time - self.last_layout_switch_time > self.layout_switch_delay:
        #         self._switch_keyboard_layout()
        #         self.last_layout_switch_time = current_time
        elif ((event.key() == Qt.Key.Key_Shift and event.modifiers() & Qt.KeyboardModifier.AltModifier) or
            (event.key() == Qt.Key.Key_Alt and event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
            if current_time - self.last_layout_switch_time > self.layout_switch_delay:
                self.switch_language()   # <-- использует set_language(...) и notify-send
                self.last_layout_switch_time = current_time


        # Win + Tab (вместо Alt + Tab)
        elif event.key() == Qt.Key.Key_Tab and event.modifiers() & Qt.KeyboardModifier.MetaModifier:
            self.switch_to_next_window()
        # Enter (оставляем без изменений)
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.unlock_screen()


        # ALT+TAB — открыть/листать; ALT+SHIFT+TAB — назад
        elif event.key() == Qt.Key.Key_Control and (event.modifiers() & Qt.KeyboardModifier.AltModifier):
            if not self._switcher_active:
                self._open_switcher(reverse=bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier))
            else:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.task_switcher.prev()
                else:
                    self.task_switcher.next()
            return  # не пробрасываем дальше

        # ESC — отменить выбор, если открыт переключатель
        elif self._switcher_active and event.key() == Qt.Key.Key_Escape:
            self.task_switcher.cancel()
            self._switcher_active = False
            return
        
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        # отпускание ALT — применить выбор
        if self._switcher_active and event.key() == Qt.Key.Key_Alt:
            chosen = self.task_switcher.finalize()
            self._switcher_active = False
            if chosen:
                self.switch_window(chosen)  # уже есть у тебя
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
        """Створює меню 'Пуск' у стилі Windows 10 з пошуком і динамічною висотою"""
        all_apps = self.get_available_apps()

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
            translator=self.tr,  # Передаем функцию перевода из MacOSWindow
            lang_code=self.current_language  # Передаем текущий язык
        )
        self.search_box.setPlaceholderText("Пошук...")
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

        all_apps_label = QLabel("Усі додатки")
        all_apps_label.setStyleSheet("color: white; font-size: 14px; margin-top: 10px;")
        left_layout.addWidget(all_apps_label)

        # Список застосунків
        apps_scroll = QScrollArea()
        apps_scroll.setWidgetResizable(True)
        apps_scroll.setStyleSheet("background: transparent; border: none;")
        apps_scroll.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        apps_scroll.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        
        self.apps_widget = QWidget()
        self.apps_list_layout = QVBoxLayout(self.apps_widget)
        self.apps_list_layout.setSpacing(5)

        self.app_buttons = []  # Зберігаємо кнопки для фільтрації

        for app in all_apps:
            btn = QPushButton(app["name"])
            btn.setIcon(QIcon(app["icon"]))
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
            btn.clicked.connect(lambda _, a=app["id"]: self.handle_app_launch(a))
            self.apps_list_layout.addWidget(btn)
            self.app_buttons.append((btn, app["name"].lower()))

        apps_scroll.setWidget(self.apps_widget)
        left_layout.addWidget(apps_scroll)
        layout.addWidget(left_panel, 2)

        # Додаємо пошук
        def filter_apps():
            text = self.search_box.text().lower()
            for btn, name in self.app_buttons:
                btn.setVisible(text in name)

            # Оновлюємо висоту меню під видимі кнопки
            self.update_start_menu_height()

        self.search_box.textChanged.connect(filter_apps)

        # Підрахунок початкової висоти
        self.start_menu.setFixedHeight(self.calculate_start_menu_height(len(all_apps)))
        self.start_menu.move(0, self.height() - self.start_menu.height())
        self.start_menu.hide()
        self.start_menu.is_showing = False
        # Фільтр подій для закриття при кліку поза меню
        self.start_menu.installEventFilter(self)
        QApplication.instance().installEventFilter(self)

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
            self.password_input.setFocus()  # Активируем поле ввода пароля

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

    def update_win_menu(self, window_name):
        """
        Обновляет текст меню "Win" на активное окно и выделяет кнопку в доке.
        """
        self.win_menu.setTitle(window_name)
        
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
        """Создает кнопку Wi-Fi в правом нижнем углу"""
        # Создаем контейнер для кнопки
        self.wifi_button_container = QWidget(self)
        self.wifi_button_container.setFixedSize(60, 60)
        self.wifi_button_container.move(
            self.width() - 260,  # Позиция слева от кнопки громкости
            self.height() - 65   # Такая же высота как у других кнопок
        )
        
        # Вертикальный лэйаут для кнопки
        layout = QVBoxLayout(self.wifi_button_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем кнопку
        self.wifi_button = QPushButton()
        self.wifi_button.setFixedSize(60, 60)
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
        
        # Иконка Wi-Fi
        self.wifi_icon = QLabel(self.wifi_button)
        self.wifi_icon.setPixmap(QIcon(os.path.join("bin", "icons", "local_icons", "system", "wifi", "wifi_signal_4.png")).pixmap(30, 30))
        self.wifi_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wifi_icon.setGeometry(15, 15, 30, 30)
        
        layout.addWidget(self.wifi_button)
        
        # Создаем виджет Wi-Fi (изначально скрыт)
        self.wifi_window = WifiWindow(
            parent=self,
            translator=self.tr,  # Передаем функцию перевода из MacOSWindow
            lang_code=self.current_language  # Передаем текущий язык
        )
        self.wifi_window.setParent(self)
        self.wifi_window.setObjectName("wifi_window")
        self.wifi_window.hide()
        
        # Подключаем клик по кнопке Wi-Fi
        self.wifi_button.clicked.connect(self.toggle_wifi_control)
        
        # Добавляем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.wifi_window.setGraphicsEffect(shadow)

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
        
        # Устанавливаем начальную позицию (невидимая, за экраном справа)
        start_pos = QPoint(self.width(), self.height() - 520)
        end_pos = QPoint(self.width() - 370, self.height() - 520)
        
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
        """Добавляет кнопку в док-панель"""
        if app_name in self.dock_buttons:
            return  # Кнопка уже существует

        button_size = 44  # Размер кнопки
        
        # Пути к иконке приложения (пробуем несколько вариантов)
        possible_icon_paths = [
            os.path.join("apps", "local", app_name, f"{app_name}.png"),
            os.path.join("apps", "local", f"{app_name}.png"),
            os.path.join("apps", "local", app_name, "icon.png")
        ]
        
        icon_path = None
        for path in possible_icon_paths:
            if os.path.exists(path):
                icon_path = path
                break
        
        if not icon_path:
            print(f"Иконка для {app_name} не найдена по путям: {possible_icon_paths}")
            return

        btn = JumpingButton(icon_path=icon_path, parent=self)
        btn.setFixedSize(button_size, button_size)
        btn.setIconSize(QSize(50, 50))
        btn.clicked.connect(lambda _, n=app_name: self.switch_window(n))
        
        # Устанавливаем прозрачный фон для кнопки
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

        # Добавляем эффект тени для кнопки
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(10)
        btn_shadow.setColor(QColor(0, 0, 0, 100))
        btn_shadow.setOffset(2, 2)
        btn.setGraphicsEffect(btn_shadow)

        indicator = QLabel()
        indicator.setFixedSize(20, 4)
        indicator.setStyleSheet("background: transparent; border: none; border-radius: 2px;")

        # Контейнер для кнопки и индикатора
        container = QWidget()
        container.setStyleSheet("background: transparent;")  # Прозрачный фон контейнера
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 8, 0, 0)
        container_layout.setSpacing(5)
        container_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(indicator, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.dock_layout.addWidget(container)
        self.dock_buttons[app_name] = (btn, indicator)
        
        # Обновляем размер дока
        dock_padding = 20  # Отступы док-панели
        dock_spacing = 15  # Промежуток между кнопками
        dock_width = len(self.dock_buttons) * (button_size + dock_spacing) + dock_padding * 2
        self.dock.setFixedSize(dock_width, 65)
            
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
                        self.animate_window_open(window)
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
        """Добавляет временную кнопку в док-панель для нестандартных приложений"""
        if app_name in self.dynamic_dock_buttons:
            return  # Кнопка уже существует

        button_size = 44  # Размер кнопки
        
        # Пути к иконке приложения (пробуем несколько вариантов)
        possible_icon_paths = [
            os.path.join("apps", "local", app_name, f"{app_name}.png"),
            os.path.join("apps", "local", f"{app_name}.png"),
            os.path.join("apps", "local", app_name, "icon.png"),
            os.path.join("bin", "icons", "local_icons", "system", "default_app.png")  # Иконка по умолчанию
        ]
        
        icon_path = None
        for path in possible_icon_paths:
            if os.path.exists(path):
                icon_path = path
                break
        
        if not icon_path:
            print(f"Иконка для {app_name} не найдена по путям: {possible_icon_paths}")
            return

        btn = JumpingButton(icon_path=icon_path, parent=self)
        btn.setFixedSize(button_size, button_size)
        btn.setIconSize(QSize(50, 50))
        btn.clicked.connect(lambda _, n=app_name: self.switch_window(n))
        
        # Устанавливаем прозрачный фон для кнопки
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

        # Добавляем эффект тени для кнопки
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(10)
        btn_shadow.setColor(QColor(0, 0, 0, 100))
        btn_shadow.setOffset(2, 2)
        btn.setGraphicsEffect(btn_shadow)

        indicator = QLabel()
        indicator.setFixedSize(20, 4)
        indicator.setStyleSheet("background: transparent; border: none; border-radius: 2px;")

        # Контейнер для кнопки и индикатора
        container = QWidget()
        container.setStyleSheet("background: transparent;")  # Прозрачный фон контейнера
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 8, 0, 0)
        container_layout.setSpacing(5)
        container_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(indicator, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.dock_layout.addWidget(container)
        self.dynamic_dock_buttons[app_name] = (btn, indicator)
        
        # Обновляем размер дока
        dock_padding = 20  # Отступы док-панели
        dock_spacing = 15  # Промежуток между кнопками
        dock_width = (len(self.dock_buttons) + len(self.dynamic_dock_buttons)) * (button_size + dock_spacing) + dock_padding * 2
        self.dock.setFixedSize(dock_width, 65)



    def update_dock_indicators(self):
        """
        Обновляет индикаторы запущенных приложений в доке.
        """
        if not hasattr(self, 'active_windows'):
            self.active_windows = {}
            
        # Сначала собираем список окон для удаления
        windows_to_remove = []
        
        # Обновляем индикаторы для стандартных кнопок
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
        
        # Обработка динамических кнопок
        for window_name, (button, indicator) in self.dynamic_dock_buttons.items():
            window = self.open_windows.get(window_name)
            if window is None:  # Окно полностью закрыто
                windows_to_remove.append(window_name)
            elif not window.isHidden():  # Окно открыто и не скрыто
                indicator.setStyleSheet("""
                    background-color: #4bcfff;
                    border: none;
                    border-radius: 22px;
                    min-height: 4px;
                """)
            elif window.minimized:  # Окно свернуто
                indicator.setStyleSheet("""
                    background-color: #4bcfff;
                    border: none;
                    border-radius: 22px;
                    min-height: 4px;
                    opacity: 0.5;
                """)
        
        # Удаляем кнопки для закрытых окон
        for window_name in windows_to_remove:
            if window_name in self.dynamic_dock_buttons:
                container = self.dynamic_dock_buttons[window_name][0].parent()
                self.dock_layout.removeWidget(container)
                container.deleteLater()
                del self.dynamic_dock_buttons[window_name]
                
        # Обновляем размер дока
        button_size = 44
        dock_padding = 20
        dock_spacing = 15
        dock_width = (len(self.dock_buttons) + len(self.dynamic_dock_buttons)) * (button_size + dock_spacing) + dock_padding * 2
        self.dock.setFixedSize(dock_width, 65)



if __name__ == "__main__":
    # Устанавливаем глобальный обработчик исключений
    sys.excepthook = global_exception_handler

    try:
        app = QApplication(sys.argv)
        window = MacOSWindow()
        window.show()

        # Таймер для проверки зависания
        timer = QTimer()
        timer.timeout.connect(lambda: None)  # Пустая функция для проверки отклика
        timer.start(1000)  # Проверка каждую секунду

        sys.exit(app.exec())
    except Exception as e:
        # Если ошибка произошла до создания окна, показываем её в DeathScreen через временное окно
        global_exception_handler(type(e), e, e.__traceback__)