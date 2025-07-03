import sys
import os
import shutil

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
            
            # Остальные элементы
            self.create_menu()
            self.open_windows = {}
            self.create_all_windows()
            # self.check_for_updates()

            
            # Создаем экран блокировки
            self.create_lock_screen()
        except Exception as e:
            # Если ошибка происходит в конструкторе, показываем её в DeathScreen
            self.show_death_screen(f"Critical error in constructor: {str(e)}")

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
        self.volume_widget = VolumeControlWidget()
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
        self.calendar_widget = CalendarWidget()
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
            echo_mode=QLineEdit.EchoMode.Password  # Или QLineEdit.EchoMode.Normal для обычного текста
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

    def create_all_windows(self):
        """
        Инициализация окон. Окна создаются только при первом открытии.
        """
        self.open_windows = {
            "browser": None,
            "cmd": None,
            "settings": None,
            "calc": None,
            "explorer": None,
            "notebook": None,
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
        
        # Ctrl key - открытие/закрытие меню
        if event.key() == Qt.Key.Key_Control:
            self.toggle_start_menu()
            return
        
        # Ctrl + L (вместо Win + L)
        if event.key() == Qt.Key.Key_L and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.lock_screen()
        # Alt + Shift
        elif ((event.key() == Qt.Key.Key_Shift and event.modifiers() & Qt.KeyboardModifier.AltModifier) or
             (event.key() == Qt.Key.Key_Alt and event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
            if current_time - self.last_layout_switch_time > self.layout_switch_delay:
                self._switch_keyboard_layout()
                self.last_layout_switch_time = current_time
        # Alt + Tab
        elif event.key() == Qt.Key.Key_Tab and event.modifiers() & Qt.KeyboardModifier.AltModifier:
            self.switch_to_next_window()
        # Enter
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.unlock_screen()
        
        super().keyPressEvent(event)

    def _switch_keyboard_layout(self):
        """Переключает между предопределёнными раскладками"""
        try:
            # Переключаем индекс раскладки
            self.current_layout_index = (self.current_layout_index + 1) % len(self.keyboard_layouts)
            new_layout = self.keyboard_layouts[self.current_layout_index]
            
            # Для Windows можно использовать системное переключение
            if os.name == 'nt':
                self._switch_windows_layout(new_layout)
            
            # Показываем уведомление
            self._show_layout_notification(new_layout)
            
        except Exception as e:
            # print(f"Ошибка переключения раскладки: {e}")
            pass

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
        self.search_box = QLineEdit()  # Сохраняем как атрибут класса
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
        self.window_switch_menu = QMenu(self)
        
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
        self.wifi_icon.setPixmap(QIcon(os.path.join("bin", "icons", "local_icons", "system", "wifi.png")).pixmap(30, 30))
        self.wifi_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wifi_icon.setGeometry(15, 15, 30, 30)
        
        layout.addWidget(self.wifi_button)
        
        # Создаем виджет Wi-Fi (изначально скрыт)
        self.wifi_window = WifiWindow()
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
            
        # Обновляем индикаторы для стандартных кнопок
        for window_name, (button, indicator) in self.dock_buttons.items():
            if self.active_windows.get(window_name, False):
                indicator.setStyleSheet("""
                    background-color: #4bcfff;
                    border: none;
                    border-radius: 22px;
                    min-height: 4px;
                """)
            else:
                indicator.setStyleSheet("""
                    background-color: transparent;
                    border: none;
                """)
        
        # Сначала собираем список окон для удаления
        windows_to_remove = []
        for window_name, (button, indicator) in self.dynamic_dock_buttons.items():
            if window_name in self.open_windows and self.open_windows[window_name] is not None and not self.open_windows[window_name].isHidden():
                indicator.setStyleSheet("""
                    background-color: #4bcfff;
                    border: none;
                    border-radius: 22px;
                    min-height: 4px;
                """)
            else:
                windows_to_remove.append(window_name)
        
        # Затем удаляем собранные окна
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

        sys.exit(app.exec())
    except Exception as e:
        # Если ошибка произошла до создания окна, показываем её в DeathScreen через временное окно
        global_exception_handler(type(e), e, e.__traceback__)

