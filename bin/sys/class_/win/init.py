# from PyQt6.QtCore import QTimer, QTime, QDate, QPropertyAnimation, QEasingCurve, QRect  # Добавлен QPropertyAnimation и QEasingCurve
# from PyQt6.QtWidgets import (
#     QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QFrame, QLabel, QMessageBox, QStackedWidget, QMenuBar, QToolBar, QLineEdit, QTabWidget, QMenu
# )
# from PyQt6.QtGui import QKeyEvent
# from PyQt6.QtCore import Qt, QSize, QUrl, QPoint
# from PyQt6.QtGui import QIcon, QPixmap, QMouseEvent, QColor, QPainter, QBrush, QFont
# from PyQt6.QtWebEngineWidgets import QWebEngineView
# import sys
# from PyQt6.QtGui import QAction

# from PyQt6.QtCore import QTimer, QTime, QDate
# from PyQt6.QtGui import QAction, QFont
# from PyQt6.QtWidgets import QLabel, QMenuBar

# from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
# from PyQt6.QtCore import QProcess

# from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
# from PyQt6.QtCore import QProcess

# import os

# from PyQt6.QtWidgets import QHBoxLayout, QLabel  # Убедитесь, что QLabel импортирован

# class DraggableResizableWindow(QFrame):
#     def __init__(self, parent=None, window_name=""):
#         super().__init__(parent)
#         self.parent_window = parent
#         self.window_name = window_name
#         self.last_click_time = 0
#         self.click_timer = QTimer()
#         self.click_timer.setSingleShot(True)
#         self.click_timer.timeout.connect(self.reset_click_count)
#         self.click_count = 0
#         self.is_maximized = False
#         self.is_active = False
#         self.open_windows = {}  # Словарь открытых окон
#         self.active_window = None  # Текущее активное окно

#         self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
#         self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
#         # Устанавливаем стиль с белой обводкой
#         self.setStyleSheet("""
#             DraggableResizableWindow {
#                 background-color: rgba(50, 50, 50, 220);
#                 border-radius: 15px;
#                 border: 2px solid transparent;
#             }
#         """)
#         self.old_pos = None
#         self.resizing = False
#         self.minimized = False
#         self.setMinimumSize(100, 70)

#         # Верхняя панель с кнопками управления
#         self.title_bar = QFrame(self)
#         self.title_bar.setFixedHeight(38)
#         self.title_bar.setStyleSheet("""
#             QFrame {
#                 background-color: #3A3A3A;
#                 border-top-left-radius: 15px;
#                 border-top-right-radius: 15px;
#                 border-bottom-left-radius: 0px;
#                 border-bottom-right-radius: 0px;
#             }
#         """)

#         title_layout = QHBoxLayout(self.title_bar)
#         title_layout.setContentsMargins(10, 5, 10, 5)
#         title_layout.setSpacing(8)

#         # Кнопки управления с обновленными стилями
#         self.close_button = QPushButton("X")
#         self.close_button.setFixedSize(20, 20)
#         self.close_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #FF5E57;
#                 border-radius: 10px;
#                 color: black;
#                 font-weight: bold;
#             }
#             QPushButton:hover {
#                 background-color: #FF3B30;
#             }
#         """)
#         self.close_button.clicked.connect(self.close_window)

#         self.minimize_button = QPushButton("-")
#         self.minimize_button.setFixedSize(20, 20)
#         self.minimize_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #FFBD2E;
#                 border-radius: 10px;
#                 color: black;
#                 font-weight: bold;
#             }
#             QPushButton:hover {
#                 background-color: #FFA500;
#             }
#         """)
#         self.minimize_button.clicked.connect(self.minimize_window)

#         self.maximize_button = QPushButton("O")
#         self.maximize_button.setFixedSize(20, 20)
#         self.maximize_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #28C940;
#                 border-radius: 10px;
#                 color: black;
#                 font-weight: bold;
#             }
#             QPushButton:hover {
#                 background-color: #1EAD33;
#             }
#         """)
#         self.maximize_button.clicked.connect(self.toggle_maximize_restore)

#         title_layout.addWidget(self.close_button)
#         title_layout.addWidget(self.minimize_button)
#         title_layout.addWidget(self.maximize_button)

#         self.title_widgets_container = QWidget()
#         self.title_widgets_layout = QHBoxLayout(self.title_widgets_container)
#         self.title_widgets_layout.setContentsMargins(0, 0, 0, 0)
#         self.title_widgets_layout.setSpacing(10)

#         self.title_label = QLabel(window_name)
#         self.title_label.setStyleSheet("color: white; font-size: 14px;")
#         self.title_widgets_layout.addWidget(self.title_label)

#         title_layout.addWidget(self.title_widgets_container)
#         title_layout.addStretch()

#         self.title_bar.setLayout(title_layout)

#         self.main_layout = QVBoxLayout(self)
#         self.main_layout.setContentsMargins(0, 0, 0, 0)
#         self.main_layout.setSpacing(0)
#         self.main_layout.addWidget(self.title_bar)
        
#         self.content_area = QFrame(self)
#         self.content_area.setStyleSheet("""
#             background-color: #3A3A3A; 
#             border-top-left-radius: 0px; 
#             border-top-right-radius: 0px; 
#             border-bottom-left-radius: 15px; 
#             border-bottom-right-radius: 15px;
#         """)
#         self.main_layout.addWidget(self.content_area)
        
#         self.content_layout = QVBoxLayout(self.content_area)
#         self.content_layout.setContentsMargins(8, 8, 8, 8)
#         self.content_area.setLayout(self.content_layout)

#     def reset_click_count(self):
#         """Сбрасывает счетчик кликов по истечении времени"""
#         self.click_count = 0


#     def add_title_widget(self, widget):
#         """
#         Добавляет виджет в заголовок окна (рядом с кнопками управления).
#         """
#         self.title_widgets_layout.addWidget(widget)

#     def minimize_window(self):
#         """
#         Анимация сворачивания окна (вниз).
#         """
#         self.activate()
#         # Создаем анимацию для перемещения окна вниз
#         self.animation = QPropertyAnimation(self, b"geometry")
#         self.animation.setDuration(150)  # Длительность анимации в миллисекундах
#         self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце

#         # Начальная позиция окна
#         start_rect = self.geometry()
#         # Конечная позиция окна (за пределами экрана вниз)
#         screen_height = QApplication.primaryScreen().geometry().height()
#         end_rect = QRect(start_rect.x(), screen_height, start_rect.width(), start_rect.height())

#         self.animation.setStartValue(start_rect)
#         self.animation.setEndValue(end_rect)
#         self.animation.finished.connect(self._on_minimize_animation_finished)  # Скрываем окно после завершения анимации
#         self.animation.start()


#     def _on_minimize_animation_finished(self):
#         """
#         Скрывает окно после завершения анимации сворачивания.
#         """
#         self.hide()
#         self.minimized = True
#         # Обновляем заголовок меню в главном окне
#         if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
#             self.parent_window.update_win_menu("desktop")
#         else:
#             print("Ошибка: `parent_window` не найден или `update_win_menu` отсутствует!")


#     def close_window(self):
#         """
#         Анимация закрытия окна (вверх).
#         """
#         self.activate()
#         # Создаем анимацию для перемещения окна вверх
#         self.animation = QPropertyAnimation(self, b"geometry")
#         self.animation.setDuration(150)  # Длительность анимации в миллисекундах
#         self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце

#         # Начальная позиция окна
#         start_rect = self.geometry()
#         # Конечная позиция окна (за пределами экрана вверх)
#         end_rect = QRect(start_rect.x(), -start_rect.height(), start_rect.width(), start_rect.height())

#         self.animation.setStartValue(start_rect)
#         self.animation.setEndValue(end_rect)
#         self.animation.finished.connect(self._on_close_animation_finished)  # Закрываем окно после завершения анимации
#         self.animation.start()

#     def _on_close_animation_finished(self):
#         """
#         Закрывает окно после завершения анимации.
#         """
#         window_name = None
#         for name, window in self.parent().open_windows.items():
#             if window == self:
#                 window_name = name
#                 break

#         if window_name:
#             self.parent().active_windows[window_name] = False
#             self.parent().update_dock_indicators()
#             self.parent().open_windows[window_name] = None  # Убираем ссылку на удалённое окно

#         self.hide()  # Скрываем окно перед удалением
#         # Обновляем заголовок меню в главном окне
#         if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
#             self.parent_window.update_win_menu("desktop")
#         else:
#             print("Ошибка: `parent_window` не найден или `update_win_menu` отсутствует!")
#         self.setParent(None)  # Убираем родителя
#         self.deleteLater()  # Удаляем объект

#     def update_dock_indicators(self):
#         """Обновляет индикаторы активного окна в док-панели"""
#         active_window_name = self.active_window.window_name if self.active_window else None
        
#         for app_name, (btn, indicator) in self.dock_buttons.items():
#             if app_name == active_window_name:
#                 indicator.setStyleSheet("background: white; border-radius: 2px;")
#             else:
#                 indicator.setStyleSheet("background: transparent; border-radius: 2px;")

#     def set_content(self, widget):
#         """
#         Добавляет содержимое в окно.
#         """
#         for i in reversed(range(self.content_layout.count())):
#             self.content_layout.itemAt(i).widget().setParent(None)

#         self.content_layout.addWidget(widget)

#     def toggle_maximize_restore(self):
#         self.activate()
#         if not hasattr(self, 'normal_geometry'):
#             self.normal_geometry = self.geometry()
#             self.is_maximized = False
        
#         # Создаем анимацию
#         self.animation = QPropertyAnimation(self, b"geometry")
#         self.animation.setDuration(200)  # Увеличиваем длительность для плавности
#         self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
#         if self.is_maximized:
#             # Анимация восстановления
#             self.animation.setStartValue(self.geometry())
#             self.animation.setEndValue(self.normal_geometry)
#             self.is_maximized = False
#         else:
#             # Сохраняем текущий размер перед максимизацией
#             self.normal_geometry = self.geometry()
            
#             # Получаем геометрию экрана
#             screen_geometry = QApplication.primaryScreen().availableGeometry()
            
#             # Настройки отступов (можно регулировать)
#             top_offset = 33
#             available_height = screen_geometry.height() - top_offset
            
#             # Анимация максимизации
#             self.animation.setStartValue(self.geometry())
#             self.animation.setEndValue(QRect(
#                 screen_geometry.x(),
#                 screen_geometry.y() + top_offset,
#                 screen_geometry.width(),
#                 available_height
#             ))
#             self.is_maximized = True
        
#         self.animation.start()
#         self.raise_()
        
#         # Обновляем меню
#         if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
#             self.parent_window.update_win_menu(self.window_name)

#     def set_active(self, active):
#         """Устанавливает состояние активности окна и меняет стиль кнопок и обводку"""
#         if self.is_active == active:
#             return  # Не изменяем, если состояние уже совпадает
        
#         self.is_active = active
        
#         # Определяем стили для кнопок
#         close_color = "#FF5E57" if active else "#808080"
#         close_hover = "#FF3B30" if active else "#707070"
#         minimize_color = "#FFBD2E" if active else "#808080"
#         minimize_hover = "#FFA500" if active else "#707070"
#         maximize_color = "#28C940" if active else "#808080"
#         maximize_hover = "#1EAD33" if active else "#707070"
        
#         # Применяем стили к кнопкам
#         self.close_button.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {close_color};
#                 border-radius: 10px;
#                 color: black;
#                 font-weight: bold;
#             }}
#             QPushButton:hover {{
#                 background-color: {close_hover};
#             }}
#         """)
        
#         self.minimize_button.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {minimize_color};
#                 border-radius: 10px;
#                 color: black;
#                 font-weight: bold;
#             }}
#             QPushButton:hover {{
#                 background-color: {minimize_hover};
#             }}
#         """)
        
#         self.maximize_button.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {maximize_color};
#                 border-radius: 10px;
#                 color: black;
#                 font-weight: bold;
#             }}
#             QPushButton:hover {{
#                 background-color: {maximize_hover};
#             }}
#         """)
        
#         # Обновляем стиль заголовка
#         bg_color = "#4A4A4A" if active else "#3A3A3A"
#         self.title_bar.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {bg_color};
#                 border-top-left-radius: 15px;
#                 border-top-right-radius: 15px;
#             }}
#         """)
        
#         # Устанавливаем или убираем белую обводку
#         border_style = "2px solid white" if active else "2px solid transparent"
#         self.setStyleSheet(f"""
#             DraggableResizableWindow {{
#                 background-color: rgba(50, 50, 50, 220);
#                 border-radius: 15px;
#                 border: {border_style};
#             }}
#         """)
        
#         # Принудительное обновление
#         self.close_button.update()
#         self.minimize_button.update()
#         self.maximize_button.update()
#         self.title_bar.update()
#         self.update()


#     def mousePressEvent(self, event: QMouseEvent):
#         if event.button() == Qt.MouseButton.LeftButton:
#             self.raise_()
#             self.activate()  # Используем новый метод активации
            
#             if event.pos().y() < 30:
#                 self.old_pos = event.globalPosition().toPoint()
                
#                 current_time = QTime.currentTime().msecsSinceStartOfDay()
#                 if current_time - self.last_click_time < 300:
#                     self.click_count += 1
#                     if self.click_count >= 2:
#                         self.toggle_maximize_restore()
#                         self.click_count = 0
#                 else:
#                     self.click_count = 1
                
#                 self.last_click_time = current_time
#                 self.click_timer.start(300)
                
#             elif event.pos().x() > self.width() - 10 and event.pos().y() > self.height() - 10:
#                 self.resizing = True

#     def activate(self):
#         """Активирует окно и обновляет все связанные элементы"""
#         if self.parent_window:
#             # Деактивируем все другие окна
#             for name, window in self.parent_window.open_windows.items():
#                 if window and window != self:
#                     window.set_active(False)
            
#             # Активируем текущее окно
#             self.set_active(True)
            
#             # Устанавливаем активное окно в parent_window
#             self.parent_window.active_window = self
            
#             # Обновляем док-панель
#             if hasattr(self.parent_window, 'update_dock_indicators'):
#                 self.parent_window.update_dock_indicators()
            
#             # Обновляем заголовок меню
#             if hasattr(self.parent_window, "update_win_menu"):
#                 self.parent_window.update_win_menu(self.window_name)

#     def mouseMoveEvent(self, event: QMouseEvent):
#         if self.old_pos and not self.resizing:
#             delta = event.globalPosition().toPoint() - self.old_pos
#             self.move(self.x() + delta.x(), self.y() + delta.y())
#             self.old_pos = event.globalPosition().toPoint()

#         elif self.resizing:
#             self.resize(event.pos().x(), event.pos().y())

#         self.raise_()  # Поднимаем окно на передний план

#         # Обновляем заголовок меню в главном окне
#         if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
#             self.parent_window.update_win_menu(self.window_name)
#         else:
#             print("Ошибка: `parent_window` не найден или `update_win_menu` отсутствует!")

#     def mouseReleaseEvent(self, event: QMouseEvent):
#         self.old_pos = None
#         self.resizing = False

#     def update_win_menu(self, window_name):
#         """
#         Обновляет текст меню "Win" на активное окно.
#         """
#         self.win_menu.setTitle(window_name)
    
#     def restore_window(self):
#         """
#         Восстанавливает окно после сворачивания.
#         """
#         if self.minimized:
#             # Показываем окно
#             self.show()
#             self.minimized = False

#             # Восстанавливаем позицию и размер окна
#             screen_geometry = QApplication.primaryScreen().geometry()
#             start_rect = QRect(self.x(), screen_geometry.height(), self.width(), self.height())
#             end_rect = QRect(self.x(), screen_geometry.height() // 2 - self.height() // 2, self.width(), self.height())

#             # Анимация восстановления окна
#             self.animation = QPropertyAnimation(self, b"geometry")
#             self.animation.setDuration(150)  # Длительность анимации в миллисекундах
#             self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце
#             self.animation.setStartValue(start_rect)
#             self.animation.setEndValue(end_rect)
#             self.animation.start()

#     def toggle_window(self):
#         """
#         Переключает состояние окна: сворачивает или восстанавливает.
#         """
#         if self.minimized:
#             self.restore_window()
#         else:
#             self.minimize_window()
from PyQt6.QtCore import QTimer, QTime, QDate, QPropertyAnimation, QEasingCurve, QRect
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

class DraggableResizableWindow(QFrame):
    def __init__(self, parent=None, window_name=""):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name
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

        # Флаг для отслеживания состояния ресурсов
        self.resources_released = False

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
	    
	    # Освобождение ресурсов содержимого
	    if hasattr(self, 'content_widget'):
	        self.content_widget.deleteLater()
	        del self.content_widget
	    
	    # Удаление из родительского окна
	    window_name = None
	    for name, window in self.parent().open_windows.items():
	        if window == self:
	            window_name = name
	            break

	    if window_name:
	        # Явно удаляем окно из словаря open_windows
	        self.parent().open_windows[window_name] = None
	        # Обновляем индикаторы в доке
	        if hasattr(self.parent(), 'update_dock_indicators'):
	            self.parent().update_dock_indicators()
	        # Обновляем активные окна
	        if hasattr(self.parent(), 'active_windows'):
	            self.parent().active_windows[window_name] = False

	    self.hide()
	    if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
	        self.parent_window.update_win_menu("desktop")
	    self.setParent(None)
	    self.deleteLater()

    def set_content(self, widget):
        """Добавляет содержимое в окно с отслеживанием виджета"""
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)

        self.content_layout.addWidget(widget)
        self.content_widget = widget  # Сохраняем ссылку для управления ресурсами

    def toggle_maximize_restore(self):
        self.activate()
        if not hasattr(self, 'normal_geometry'):
            self.normal_geometry = self.geometry()
            self.is_maximized = False
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        if self.is_maximized:
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.normal_geometry)
            self.is_maximized = False
        else:
            self.normal_geometry = self.geometry()
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            top_offset = 33
            available_height = screen_geometry.height() - top_offset
            
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(QRect(
                screen_geometry.x(),
                screen_geometry.y() + top_offset,
                screen_geometry.width(),
                available_height
            ))
            self.is_maximized = True
        
        self.animation.start()
        self.raise_()
        
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)

    def set_active(self, active):
        """Устанавливает состояние активности окна"""
        if self.is_active == active:
            return
        
        self.is_active = active
        
        # Остановка таймера бездействия при активации
        if active:
            self.inactive_timer.stop()
            if self.resources_released:
                self.restore_content_resources()
        elif self.minimized:
            # Запуск таймера при деактивации свернутого окна
            self.inactive_timer.start()
        
        close_color = "#FF5E57" if active else "#808080"
        close_hover = "#FF3B30" if active else "#707070"
        minimize_color = "#FFBD2E" if active else "#808080"
        minimize_hover = "#FFA500" if active else "#707070"
        maximize_color = "#28C940" if active else "#808080"
        maximize_hover = "#1EAD33" if active else "#707070"
        
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
        
        border_style = "2px solid white" if active else "2px solid transparent"
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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.raise_()
            self.activate()
            
            if event.pos().y() < 30:
                self.old_pos = event.globalPosition().toPoint()
                
                current_time = QTime.currentTime().msecsSinceStartOfDay()
                if current_time - self.last_click_time < 300:
                    self.click_count += 1
                    if self.click_count >= 2:
                        self.toggle_maximize_restore()
                        self.click_count = 0
                else:
                    self.click_count = 1
                
                self.last_click_time = current_time
                self.click_timer.start(300)
                
            elif event.pos().x() > self.width() - 10 and event.pos().y() > self.height() - 10:
                self.resizing = True

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

        self.raise_()

        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.old_pos = None
        self.resizing = False

    def update_win_menu(self, window_name):
        self.win_menu.setTitle(window_name)
    
    def restore_window(self):
        """Восстанавливает окно с восстановлением ресурсов"""
        if self.minimized:
            self.show()
            self.minimized = False
            self.restore_content_resources()
            self.inactive_timer.stop()

            screen_geometry = QApplication.primaryScreen().geometry()
            start_rect = QRect(self.x(), screen_geometry.height(), self.width(), self.height())
            end_rect = QRect(self.x(), screen_geometry.height() // 2 - self.height() // 2, self.width(), self.height())

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