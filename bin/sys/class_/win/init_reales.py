from PyQt6.QtCore import QTimer, QTime, QDate, QPropertyAnimation, QEasingCurve, QRect, QEvent
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, 
    QFrame, QLabel, QMessageBox, QStackedWidget, QMenuBar, QToolBar, QLineEdit, 
    QTabWidget, QMenu
)
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt, QSize, QUrl, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QMouseEvent, QColor, QPainter, QBrush, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
from PyQt6.QtGui import QAction
import os
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtCore import Qt, QTimer, QPoint

from PyQt6.QtCore import QObject, QEvent
from PyQt6.QtGui import QMouseEvent

class ActivationEventFilter(QObject):
    """Перехватывает клик мыши и активирует родительское окно."""
    def __init__(self, target_window, parent=None):
        super().__init__(parent)
        self.target_window = target_window

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                # --- ИСПОЛЬЗУЕМ НОВЫЙ set_active ---
                self.target_window.function()
        
        # Обязательно возвращаем False, чтобы клик дошел до элемента (QListWidget, QLineEdit)
        return False

from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QRect

class SnapPresetButton(QPushButton):
    """
    Кнопка-пресет у стилі Win11:
    всередині малюється маленький "монітор" з потрібним поділом
    і підсвіченою областю, куди стане вікно.
    """
    def __init__(self, mode: str, parent=None):
        super().__init__("", parent)
        self.mode = mode  # 'left', 'right', 'full', 'top', 'bottom', 'center'
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(90, 56)
        self.setFlat(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )

        rect = self.rect().adjusted(3, 3, -3, -3)

        base_bg   = QColor(40, 40, 40, 240)   # фон плитки
        base_slot = QColor(75, 75, 75, 250)   # "сіра" зона
        accent    = QColor(90, 165, 255, 230) # підсвітка вибраної області
        border    = QColor(120, 120, 120, 255)

        # фон плитки
        painter.setPen(border)
        painter.setBrush(base_bg)
        painter.drawRoundedRect(rect, 7, 7)

        inner = rect.adjusted(4, 4, -4, -4)

        def draw_slot(r: QRect, highlighted: bool):
            r = r.adjusted(1, 1, -1, -1)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(accent if highlighted else base_slot)
            painter.drawRoundedRect(r, 4, 4)

        w = inner.width()
        h = inner.height()

        if self.mode in ("left", "right", "full"):
            # дві вертикальні половини
            left_rect  = QRect(inner.left(), inner.top(), w // 2 - 1, h)
            right_rect = QRect(inner.left() + w // 2 + 1, inner.top(),
                               w // 2 - 1, h)

            if self.mode == "full":
                # вся площа підсвічена
                draw_slot(inner, True)
            else:
                draw_slot(left_rect, self.mode == "left")
                draw_slot(right_rect, self.mode == "right")

        elif self.mode in ("top", "bottom", "center"):
            # дві горизонтальні половини
            top_rect    = QRect(inner.left(), inner.top(), w, h // 2 - 1)
            bottom_rect = QRect(inner.left(), inner.top() + h // 2 + 1,
                                w, h // 2 - 1)

            if self.mode in ("top", "bottom"):
                draw_slot(top_rect,    self.mode == "top")
                draw_slot(bottom_rect, self.mode == "bottom")
            else:  # center
                # вузький прямокутник по центру
                cw = int(w * 0.6)
                ch = int(h * 0.6)
                cx = inner.center().x() - cw // 2
                cy = inner.center().y() - ch // 2
                center_rect = QRect(cx, cy, cw, ch)
                draw_slot(center_rect, True)

        # легкий контур при наведені
        if self.underMouse():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QColor(90, 165, 255, 220))
            painter.drawRoundedRect(rect, 7, 7)

class SnapLayoutPopup(QFrame):
    def __init__(self, host: "DraggableResizableWindow"):
        super().__init__(None)
        self.host = host

        # --- АВТО-ХАЙД ТАЙМЕР ---
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self._on_auto_hide)
        # ------------------------

        self.setObjectName("snapLayoutPopup")
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setStyleSheet("""
        #snapLayoutPopup {
            background-color: rgba(20,20,20,0.97);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.20);
        }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        row1 = QHBoxLayout()
        row1.setSpacing(6)
        row2 = QHBoxLayout()
        row2.setSpacing(6)

        # Верхній ряд: ліва / права / фулл
        btn_left  = SnapPresetButton("left",  self)
        # btn_left.setToolTip("Ліва половина екрана")
        btn_left.clicked.connect(lambda: self._apply_and_close("left"))

        btn_right = SnapPresetButton("right", self)
        # btn_right.setToolTip("Права половина екрана")
        btn_right.clicked.connect(lambda: self._apply_and_close("right"))

        btn_full  = SnapPresetButton("full",  self)
        # btn_full.setToolTip("На весь робочий простір")
        btn_full.clicked.connect(lambda: self._apply_and_close("full"))

        row1.addWidget(btn_left)
        row1.addWidget(btn_right)
        row1.addWidget(btn_full)

        # Нижній ряд: верх / низ / центр
        btn_top = SnapPresetButton("top", self)
        # btn_top.setToolTip("Верхня половина")
        btn_top.clicked.connect(lambda: self._apply_and_close("top"))

        btn_bottom = SnapPresetButton("bottom", self)
        # btn_bottom.setToolTip("Нижня половина")
        btn_bottom.clicked.connect(lambda: self._apply_and_close("bottom"))

        btn_center = SnapPresetButton("center", self)
        # btn_center.setToolTip("Центр")
        btn_center.clicked.connect(lambda: self._apply_and_close("center"))

        row2.addWidget(btn_top)
        row2.addWidget(btn_bottom)
        row2.addWidget(btn_center)

        main_layout.addLayout(row1)
        main_layout.addLayout(row2)

    def _apply_and_close(self, mode: str):
        self.auto_hide_timer.stop()
        self.host.apply_snap_layout(mode)
        self.hide()

    def start_auto_hide(self, ms: int = 4000):
        """Запускає/перезапускає таймер автозакриття."""
        self.auto_hide_timer.start(ms)

    def _on_auto_hide(self):
        """Ховаємо попап, якщо він ще видимий."""
        if self.isVisible():
            self.hide()

    def enterEvent(self, event):
        self.start_auto_hide()
        super().enterEvent(event)

    def mouseMoveEvent(self, event):
        self.start_auto_hide()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        # все одно перезапускаємо — 4 секунди після останнього руху
        self.start_auto_hide()
        super().leaveEvent(event)

class DraggableResizableWindow(QFrame):
    def __init__(self, parent=None, window_name="", enable_maximize=True):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name
        self.enable_maximize = enable_maximize  # ✅ новий параметр
        self.last_click_time = 0
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.reset_click_count)
        self.click_count = 0
        self.is_maximized = False
        self.is_active = False
        self.open_windows = {}
        self.active_window = None
        self.minimized = False
        self.inactive_timer = QTimer()
        self.inactive_timer.timeout.connect(self.release_inactive_resources)
        self.inactive_timer.setInterval(30000)  # 30 секунд бездействия
        self.snap_hover_timer = QTimer(self)
        self.snap_hover_timer.setSingleShot(True)
        self.snap_hover_timer.timeout.connect(self._on_snap_hover_timeout)

        # чтобы ловить hover по кнопке развёртывания
        if hasattr(self, "maximize_button") and self.maximize_button is not None:
            self.maximize_button.installEventFilter(self)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            DraggableResizableWindow {
                background-color: rgba(50, 50, 50, 220);
                border-radius: 15px;
                border: 2px solid transparent;
            }
        """)
        self.old_pos = None
        self.resizing = False
        self.setMinimumSize(100, 70)

        # Верхняя панель с кнопками управления
        self.title_bar = QFrame(self)
        self.title_bar.setFixedHeight(38)
        self.title_bar.setStyleSheet("""
            QFrame {
                background-color: #3A3A3A;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
        """)

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)
        title_layout.setSpacing(8)

        # Кнопки управления
        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5E57;
                border-radius: 10px;
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF3B30;
            }
        """)
        self.close_button.clicked.connect(self.close_window)

        self.minimize_button = QPushButton("-")
        self.minimize_button.setFixedSize(20, 20)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #FFBD2E;
                border-radius: 10px;
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFA500;
            }
        """)
        self.minimize_button.clicked.connect(self.minimize_window)

        self.maximize_button = QPushButton("O")
        self.maximize_button.setFixedSize(20, 20)
        self.maximize_button.setStyleSheet("""
            QPushButton {
                background-color: #28C940;
                border-radius: 10px;
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1EAD33;
            }
        """)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)

        # ✅ керуємо показом кнопки
        self.maximize_button.setVisible(self.enable_maximize)
        # === Snap Layout popup ===
        self.snap_popup = SnapLayoutPopup(self)
        self.snap_popup.hide()

        title_layout.addWidget(self.close_button)
        title_layout.addWidget(self.minimize_button)
        title_layout.addWidget(self.maximize_button)

        self.title_widgets_container = QWidget()
        self.title_widgets_layout = QHBoxLayout(self.title_widgets_container)
        self.title_widgets_layout.setContentsMargins(0, 0, 0, 0)
        self.title_widgets_layout.setSpacing(10)

        self.title_label = QLabel(window_name)
        self.title_label.setStyleSheet("color: white; font-size: 14px;")
        self.title_widgets_layout.addWidget(self.title_label)

        title_layout.addWidget(self.title_widgets_container)
        title_layout.addStretch()

        self.title_bar.setLayout(title_layout)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.title_bar)
        
        self.content_area = QFrame(self)
        self.content_area.setStyleSheet("""
            background-color: #3A3A3A; 
            border-bottom-left-radius: 15px; 
            border-bottom-right-radius: 15px;
        """)
        self.main_layout.addWidget(self.content_area)
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_area.setLayout(self.content_layout)
        self._install_activation_filter(self)

        # Флаг для отслеживания состояния ресурсов
        self.resources_released = False

    def _on_snap_hover_timeout(self):
        """Показать snap-popup под кнопкой развёртывания, если мышь всё ещё над ней."""
        if not self.isVisible():
            return
        if not hasattr(self, "maximize_button") or self.maximize_button is None:
            return

        btn = self.maximize_button
        # если курсор уже ушёл с кнопки — не показываем
        if not btn.underMouse():
            return

        global_pos = btn.mapToGlobal(btn.rect().bottomLeft())
        self.snap_popup.move(global_pos.x(), global_pos.y() + 4)
        self.snap_popup.show()
        self.snap_popup.raise_()
        self.snap_popup.start_auto_hide()


    def show_snap_popup(self):
        """Показати меню розкладки вікон біля кнопки maximize так,
        щоб попап завжди був повністю в межах екрана.
        """
        if not hasattr(self, "snap_popup"):
            self.snap_popup = SnapLayoutPopup(self)

        btn = self.maximize_button

        # Базова точка — центр кнопки, трохи нижче
        anchor = btn.mapToGlobal(QPoint(btn.width() // 2, btn.height()))

        # Розмір попапа
        self.snap_popup.adjustSize()
        popup_size = self.snap_popup.size()

        # Початкові координати: по центру над кнопкою
        x = anchor.x() - popup_size.width() // 2
        y = anchor.y() + 6

        # Межі робочої області екрана
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            margin = 8

            # Фіксуємо X, щоб не вилазив за лівий/правий край
            if x < geo.left() + margin:
                x = geo.left() + margin
            if x + popup_size.width() > geo.right() - margin:
                x = geo.right() - popup_size.width() - margin

            # Якщо знизу не влазить — показуємо над кнопкою
            if y + popup_size.height() > geo.bottom() - margin:
                y = anchor.y() - popup_size.height() - 6
                if y < geo.top() + margin:
                    y = geo.top() + margin

        self.snap_popup.move(x, y)
        self.snap_popup.show()
        self.snap_popup.raise_()

        # 🔥 запуск авто-закриття через 4 секунди без дій
        self.snap_popup.start_auto_hide(4000)

    def apply_snap_layout(self, mode: str):
        """
        Розміщує вікно в одну з зон екрану:
        mode: 'left', 'right', 'top', 'bottom', 'center', 'full'
        Використовує ті ж офсети, що й toggle_maximize_restore,
        щоб не перекривати док-панель та інші віджети.
        """
        import json, os

        config_path = os.path.join("bin", "sys", "path", "widgets.json")

        # Значення за замовчуванням (як у toggle_maximize_restore)
        top_offset = 33
        bottom_offset = 60
        left_offset = 0
        right_offset = 0

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)

                # 1) Пробуємо взяти з кореня (як toggle_maximize_restore)
                top_offset = int(cfg.get("top_offset", top_offset))
                bottom_offset = int(cfg.get("bottom_offset", bottom_offset))
                left_offset = int(cfg.get("left_offset", left_offset))
                right_offset = int(cfg.get("right_offset", right_offset))

                # 2) Для сумісності: якщо є секція desktop_geometry —
                #    можемо дозволити їй переоприділити значення (за бажанням)
                desk_cfg = cfg.get("desktop_geometry", {})
                top_offset = int(desk_cfg.get("top_offset", top_offset))
                bottom_offset = int(desk_cfg.get("bottom_offset", bottom_offset))
                left_offset = int(desk_cfg.get("left_offset", left_offset))
                right_offset = int(desk_cfg.get("right_offset", right_offset))

            except Exception as e:
                print(f"[SnapLayout] widgets.json read error: {e}")

        screen = QApplication.primaryScreen()
        if not screen:
            return

        screen_geometry = screen.geometry()
        work_area = screen.availableGeometry()

        total_height = screen_geometry.height()
        total_width = screen_geometry.width()

        # Висота системної панелі (taskbar / dock), яку ОС вже “з’їла” у work_area
        bottom_bar_height = total_height - work_area.height()
        # Не даємо подвійному відступу знизу
        real_bottom_offset = max(bottom_offset - bottom_bar_height, 0)

        available_height = total_height - top_offset - real_bottom_offset
        available_width = total_width - left_offset - right_offset

        base_x = screen_geometry.x() + left_offset
        base_y = screen_geometry.y() + top_offset

        # Базовий прямокутник "робочого простору"
        x = base_x
        y = base_y
        w = available_width
        h = available_height

        if mode == "left":
            w = available_width // 2
        elif mode == "right":
            w = available_width // 2
            x = base_x + available_width // 2
        elif mode == "top":
            h = available_height // 2
        elif mode == "bottom":
            h = available_height // 2
            y = base_y + available_height // 2
        elif mode == "center":
            w = available_width // 2
            h = available_height // 2
            x = base_x + (available_width - w) // 2
            y = base_y + (available_height - h) // 2
        elif mode == "full":
            # вже маємо (x, y, w, h) як повний робочий простір з урахуванням офсетів
            pass

        target_rect = QRect(x, y, w, h)

        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(self.geometry())
        anim.setEndValue(target_rect)
        anim.start()

        # Щоб GC не прибрав анімацію
        self._snap_anim = anim

        # оновлюємо індикатори у менеджері вікон, якщо є
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)
        if self.parent_window and hasattr(self.parent_window, "update_dock_indicators"):
            self.parent_window.update_dock_indicators()

    def set_maximize_enabled(self, enabled: bool):
        """Вмикає або вимикає кнопку розгортання вікна на весь екран."""
        self.enable_maximize = enabled
        if hasattr(self, "maximize_button"):
            self.maximize_button.setVisible(enabled)

    # В explorer.py, в классе ExplorerWindow

    def activate_window(self):
        """Принудительно активирует и поднимает окно."""
        self.raise_()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        # Убедитесь, что ваш флаг is_active обновляется, 
        # если вы его используете для стилизации
        if self.parent_window and hasattr(self.parent_window, "update_active_window"):
             # Вызывайте метод вашего главного класса (например, MacOSWindow) 
             # для регистрации окна как активного
            self.parent_window.update_active_window(self.window_name)

    # ВСТАВИТЬ В init.py в класс DraggableResizableWindow

    def _recursive_apply_filter(self, widget: QWidget, filter_instance: QObject):
        """Рекурсивно устанавливает фильтр на все дочерние виджеты."""
        if widget.isWidgetType():
            # Устанавливаем фильтр на текущий виджет, если он интерактивный
            widget.installEventFilter(filter_instance)
            
            # Обходим всех потомков (children)
            for child in widget.findChildren(QWidget):
                self._recursive_apply_filter(child, filter_instance)
        
    def setup_focus_activation(self, content_widget: QWidget):
        """Запускает рекурсивную установку фильтра для всего содержимого окна."""
        
        # Убедитесь, что класс ActivationEventFilter доступен здесь (импортирован или определен)
        self.activation_filter = ActivationEventFilter(self)
        
        # Начинаем обход с главного виджета, содержащего контент (например, self.container)
        self._recursive_apply_filter(content_widget, self.activation_filter)

    def reset_click_count(self):
        self.click_count = 0

    def add_title_widget(self, widget):
        self.title_widgets_layout.addWidget(widget)

    def minimize_window(self):
        """Анимация сворачивания окна с оптимизацией ресурсов"""
        self.activate()
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        start_rect = self.geometry()
        screen_height = QApplication.primaryScreen().geometry().height()
        end_rect = QRect(start_rect.x(), screen_height, start_rect.width(), start_rect.height())

        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(self._on_minimize_animation_finished)
        self.animation.start()

    def _on_minimize_animation_finished(self):
        """Обработка завершения анимации минимизации с освобождением ресурсов"""
        self.hide()
        self.minimized = True
        self.release_content_resources()
        
        # Запускаем таймер для освобождения ресурсов при длительном бездействии
        self.inactive_timer.start()
        
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu("desktop")

    def release_content_resources(self):
        """Освобождает ресурсы содержимого окна при минимизации"""
        if hasattr(self, 'content_widget'):
            # Для QWebEngineView
            if isinstance(self.content_widget, QWebEngineView):
                self.content_widget.setHtml("")  # Очищаем содержимое
                self.content_widget.page().setBackgroundColor(QColor(0, 0, 0, 0))
            
            # Для других виджетов можно добавить дополнительные проверки
            self.content_widget.setUpdatesEnabled(False)
            self.resources_released = True

    def restore_content_resources(self):
        """Восстанавливает ресурсы содержимого при восстановлении окна"""
        if hasattr(self, 'content_widget') and self.resources_released:
            self.content_widget.setUpdatesEnabled(True)
            
            # Для QWebEngineView
            if isinstance(self.content_widget, QWebEngineView):
                self.content_widget.page().setBackgroundColor(QColor(255, 255, 255, 255))
            
            self.resources_released = False

    def release_inactive_resources(self):
        """Освобождает дополнительные ресурсы при длительном бездействии"""
        if self.minimized and not self.resources_released:
            self.release_content_resources()

    def close_window(self):
        """Анимация закрытия окна с полным освобождением ресурсов"""
        self.activate()
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        start_rect = self.geometry()
        end_rect = QRect(start_rect.x(), -start_rect.height(), start_rect.width(), start_rect.height())

        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(self._on_close_animation_finished)
        self.animation.start()

    def _on_close_animation_finished(self):
        """Полное освобождение ресурсов при закрытии окна"""
        # Остановка таймера бездействия
        self.inactive_timer.stop()

        # Если есть метод save_session — сохраняем вкладки
        if hasattr(self, "save_session"):
            try:
                self.save_session()
            except Exception as e:
                print("[SESSION] Помилка збереження при закритті:", e)

        # Освобождение ресурсов содержимого
        if hasattr(self, 'content_widget'):
            self.content_widget.deleteLater()
            del self.content_widget

        # Удаление из родительского окна
        window_name = None
        if self.parent():
            for name, window in self.parent().open_windows.items():
                if window == self:
                    window_name = name
                    break

        if window_name:
            self.parent().open_windows[window_name] = None
            if hasattr(self.parent(), 'update_dock_indicators'):
                self.parent().update_dock_indicators()
            if hasattr(self.parent(), 'active_windows'):
                self.parent().active_windows[window_name] = False

        self.hide()
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu("desktop")
        self.setParent(None)
        self.deleteLater()

    def _install_activation_filter(self, root: QWidget):
        """
        Вішаємо eventFilter на root і ВСІ його поточні дочірні віджети.
        Далі нові віджети будуть перехоплюватись через childEvent().
        """
        root.installEventFilter(self)
        for child in root.findChildren(QWidget):
            child.installEventFilter(self)

    def childEvent(self, event):
        """
        Коли до вікна додається новий віджет – одразу вішаємо на нього eventFilter,
        щоб кліки по ньому теж активували це вікно.
        """
        if event.type() == QEvent.Type.ChildAdded:
            obj = event.child()
            if isinstance(obj, QWidget):
                obj.installEventFilter(self)
        super().childEvent(event)

    def eventFilter(self, obj, event):
        """
        Фільтр подій:
        - стартує таймер snap-layout при довгому наведенні на maximize
        - робить вікно активним при будь-якому кліку всередині
        """

        max_btn = getattr(self, "maximize_button", None)

        # --- 1. Поведінка для кнопки maximize ---
        if max_btn is not None and obj is max_btn:
            # курсор зайшов на кнопку → запускаємо таймер "довгого ховера"
            if event.type() == QEvent.Type.Enter:
                self.snap_hover_timer.start(600)  # 0.6 c до появи меню
            # рух по кнопці – просто не заважаємо, таймер вже тікає
            elif event.type() == QEvent.Type.MouseMove:
                # можемо перезапускати, щоб меню з’являлося тільки після
                # 0.6 c безперервного наведення
                if max_btn.underMouse():
                    self.snap_hover_timer.start(600)
            # курсор пішов з кнопки → скасовуємо показ меню
            elif event.type() == QEvent.Type.Leave:
                self.snap_hover_timer.stop()
            # клік по кнопці → звичайний клік, без меню
            elif event.type() in (
                QEvent.Type.MouseButtonPress,
                QEvent.Type.MouseButtonDblClick,
            ):
                self.snap_hover_timer.stop()
                if self.snap_popup.isVisible():
                    self.snap_popup.hide()
            # важливо: повертаємо False, щоб сигнал clicked() спрацював
            return False

        # --- 2. Активація вікна при будь-якому кліку всередині ---
        if event.type() == QEvent.Type.MouseButtonPress:
            from PyQt6.QtGui import QMouseEvent
            if isinstance(event, QMouseEvent):
                if event.button() in (
                    Qt.MouseButton.LeftButton,
                    Qt.MouseButton.RightButton,
                    Qt.MouseButton.MiddleButton,
                ):
                    self.raise_()
                    self.activate()

        return super().eventFilter(obj, event)

    def set_content(self, widget):
        """Добавляет содержимое в окно с отслеживанием виджета"""
        for i in reversed(range(self.content_layout.count())):
            w = self.content_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        self.content_layout.addWidget(widget)
        self.content_widget = widget  # Сохраняем ссылку для управления ресурсами

        # 👉 важливо: навішуємо фільтр на новий контент, щоб кліки в ньому активували вікно
        self._install_activation_filter(widget)

    def toggle_maximize_restore(self):
        """Разворачивает/восстанавливает окно, беря отступы из bin/sys/path/widgets.json"""
        import os, json

        self.activate()

        # === Загружаем настройки отступов ===
        config_path = os.path.join("bin", "sys", "path", "widgets.json")

        # Значения по умолчанию
        top_offset = 33
        bottom_offset = 60
        left_offset = 0
        right_offset = 0

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    top_offset = data.get("top_offset", top_offset)
                    bottom_offset = data.get("bottom_offset", bottom_offset)
                    left_offset = data.get("left_offset", left_offset)
                    right_offset = data.get("right_offset", right_offset)
            except Exception as e:
                print(f"[toggle_maximize_restore] Ошибка чтения widgets.json: {e}")

        # === Подготовка анимации ===
        if not hasattr(self, 'normal_geometry'):
            self.normal_geometry = self.geometry()
            self.is_maximized = False

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # === Параметры экрана ===
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()           # вся область экрана
        work_area = screen.availableGeometry()        # видимая часть без панели задач

        if self.is_maximized:
            # 🔽 Восстановление
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.normal_geometry)
            self.is_maximized = False
        else:
            # 🔼 Разворачивание с учетом JSON-отступов
            self.normal_geometry = self.geometry()

            total_height = screen_geometry.height()
            total_width = screen_geometry.width()
            bottom_bar_height = total_height - work_area.height()
            real_bottom_offset = max(bottom_offset - bottom_bar_height, 0)

            available_height = total_height - top_offset - real_bottom_offset
            available_width = total_width - left_offset - right_offset

            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(QRect(
                screen_geometry.x() + left_offset,
                screen_geometry.y() + top_offset,
                available_width,
                available_height
            ))
            self.is_maximized = True

        self.animation.start()
        self.raise_()

        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)

    def function(self):
        self.activate()
        self.raise_()

    def set_active(self, active: bool):
        """
        Устанавливает состояние активности окна, используя отложенное выполнение
        для предотвращения лагов UI.
        """
        # 🟢 ПРОВЕРКА ДЛЯ УСТРАНЕНИЯ ЛАГОВ: Выход, если статус не меняется
        if self.is_active == active:
            return
            
        self.is_active = active
        
        # --- 1. КРИТИЧЕСКИ ВАЖНЫЕ, БЫСТРЫЕ ОПЕРАЦИИ (Немедленно) ---
        if active:
            # Поднять окно наверх и дать ему фокус
            self.raise_()
            self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
            
            # Остановка таймера бездействия
            self.inactive_timer.stop()
            
            # 🚀 Откладываем ресурсоемкие операции (restore_content_resources, update_win_menu)
            
            if self.resources_released:
                # Откладываем восстановление ресурсов (особенно тяжелое для QWebEngineView)
                QTimer.singleShot(0, self.restore_content_resources)

            # Откладываем обновление главного меню/активного окна (если есть)
            if self.parent_window and hasattr(self.parent_window, "update_active_window"):
                QTimer.singleShot(0, lambda: self.parent_window.update_active_window(self.window_name))
            
            if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
                QTimer.singleShot(0, lambda: self.parent_window.update_win_menu(self.window_name))
        
        elif self.minimized:
            # Запуск таймера при деактивации свернутого окна
            self.inactive_timer.start()

        # Обернем всю стилизацию в одну отложенную функцию
        def delayed_style_update():
            # Ваш блок стилизации (setStyleSheet)
            close_color = "#FF6666" if active else "#808080"
            close_hover = "#F38686" if active else "#707070"
            minimize_color = "#FFE942" if active else "#808080"
            minimize_hover = "#FFF28E" if active else "#707070"
            maximize_color = "#5EFF64" if active else "#808080"
            maximize_hover = "#8FFF93" if active else "#707070"
            
            self.close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {close_color};
                    border-radius: 10px;
                    color: black;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {close_hover};
                }}
            """)
            
            self.minimize_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {minimize_color};
                    border-radius: 10px;
                    color: black;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {minimize_hover};
                }}
            """)
            
            self.maximize_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {maximize_color};
                    border-radius: 10px;
                    color: black;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {maximize_hover};
                }}
            """)
            
            bg_color = "#4A4A4A" if active else "#3A3A3A"
            self.title_bar.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border-top-left-radius: 15px;
                    border-top-right-radius: 15px;
                }}
            """)
            
            border_style = "2px solid #758ac3" if active else "2px solid transparent"
            self.setStyleSheet(f"""
                DraggableResizableWindow {{
                    background-color: rgba(50, 50, 50, 220);
                    border-radius: 15px;
                    border: {border_style};
                }}
            """)
            
            self.close_button.update()
            self.minimize_button.update()
            self.maximize_button.update()
            self.title_bar.update()
            self.update()
            # Конец блока стилизации

        # Вызываем отложенную функцию стилизации
        QTimer.singleShot(0, delayed_style_update)

    # 1. Обычный клик (таскание и ресайз)
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Проверка на активность (убирает фризы)
            if not self.isActiveWindow():
                self.raise_()
                self.activateWindow()

            TITLE_BAR_HEIGHT = 30
            RESIZE_AREA = 10
            
            if event.pos().y() < TITLE_BAR_HEIGHT:
                self.old_pos = event.globalPosition().toPoint()
                # Заметьте: тут НЕТ логики maximize, она в mouseDoubleClickEvent

            elif (event.pos().x() > self.width() - RESIZE_AREA and 
                  event.pos().y() > self.height() - RESIZE_AREA):
                self.resizing = True

    # 2. Двойной клик (разворот окна)
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.pos().y() < 30: # Если двойной клик был по шапке
                self.toggle_maximize_restore()

    def activate(self):
        """Активирует окно и управляет ресурсами"""
        if self.parent_window:
            for name, window in self.parent_window.open_windows.items():
                if window and window != self:
                    window.set_active(False)
            
            self.set_active(True)
            self.parent_window.active_window = self
            
            if hasattr(self.parent_window, 'update_dock_indicators'):
                self.parent_window.update_dock_indicators()
            
            if hasattr(self.parent_window, "update_win_menu"):
                self.parent_window.update_win_menu(self.window_name)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos and not self.resizing:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
        elif self.resizing:
            self.resize(event.pos().x(), event.pos().y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.old_pos = None
        self.resizing = False

    def update_win_menu(self, window_name):
        self.win_menu.setTitle(window_name)
    
    def restore_window(self):
        """Відновлює вікно після нашого кастомного мінімайзу."""
        if getattr(self, "minimized", False):
            # 1) показати і одразу витягнути поверх інших
            self.show()
            self.raise_()
            self.activateWindow()
            if hasattr(self, "activate"):
                # наш кастомний метод, який підсвічує рамку / оновлює стан
                self.activate()

            self.minimized = False

            # 2) повертаємо ресурси
            try:
                self.restore_content_resources()
            except Exception:
                pass

            if hasattr(self, "inactive_timer"):
                self.inactive_timer.stop()

            # 3) анімація "виїзду" знизу (як було)
            screen = QApplication.primaryScreen()
            if screen is not None:
                screen_geometry = screen.geometry()
                start_rect = QRect(
                    self.x(),
                    screen_geometry.height(),
                    self.width(),
                    self.height()
                )
                end_rect = QRect(
                    self.x(),
                    screen_geometry.height() // 2 - self.height() // 2,
                    self.width(),
                    self.height()
                )

                self.animation = QPropertyAnimation(self, b"geometry")
                self.animation.setDuration(150)
                self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
                self.animation.setStartValue(start_rect)
                self.animation.setEndValue(end_rect)
                self.animation.start()

    def toggle_window(self):
        if self.minimized:
            self.restore_window()
        else:
            self.minimize_window()
