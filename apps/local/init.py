from PyQt6.QtCore import QTimer, QTime, QDate, QPropertyAnimation, QEasingCurve, QRect  # Добавлен QPropertyAnimation и QEasingCurve
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QFrame, QLabel, QMessageBox, QStackedWidget, QMenuBar, QToolBar, QLineEdit, QTabWidget, QMenu
)
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt, QSize, QUrl, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QMouseEvent, QColor, QPainter, QBrush, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
from PyQt6.QtGui import QAction

from PyQt6.QtCore import QTimer, QTime, QDate
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import QLabel, QMenuBar

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import QProcess

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import QProcess

import os

from PyQt6.QtWidgets import QHBoxLayout, QLabel  # Убедитесь, что QLabel импортирован

class DraggableResizableWindow(QFrame):
    def __init__(self, parent=None, window_name=""):
        super().__init__(parent)
        self.parent_window = parent  # Сохраняем ссылку на главное окно
        self.window_name = window_name  # Сохраняем имя окна

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(50, 50, 50, 220); border-radius: 15px;")
        self.old_pos = None
        self.resizing = False
        self.minimized = False  # Флаг для отслеживания свёрнутости

        # Устанавливаем минимальный размер окна
        self.setMinimumSize(100, 70)  # Минимальная ширина и высота окна

        # Верхняя панель с кнопками управления
        self.title_bar = QFrame(self)
        self.title_bar.setFixedHeight(38)
        self.title_bar.setStyleSheet("background-color: #3A3A3A; border-top-left-radius: 15px; border-top-right-radius: 15px;")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)  # Отступы внутри панели
        title_layout.setSpacing(8)  # Расстояние между элементами

        # Кнопки управления
        self.close_button = QPushButton("✖")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("background-color: red; border-radius: 10px;")
        self.close_button.clicked.connect(self.close_window)

        self.minimize_button = QPushButton("➖")
        self.minimize_button.setFixedSize(20, 20)
        self.minimize_button.setStyleSheet("background-color: yellow; border-radius: 10px;")
        self.minimize_button.clicked.connect(self.minimize_window)

        self.maximize_button = QPushButton("🗖")
        self.maximize_button.setFixedSize(20, 20)
        self.maximize_button.setStyleSheet("background-color: green; border-radius: 10px;")
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)

        # Добавляем кнопки управления
        title_layout.addWidget(self.close_button)
        title_layout.addWidget(self.minimize_button)
        title_layout.addWidget(self.maximize_button)

        # Контейнер для дополнительных элементов
        self.title_widgets_container = QWidget()  # Контейнер для виджетов
        self.title_widgets_layout = QHBoxLayout(self.title_widgets_container)
        self.title_widgets_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы внутри контейнера
        self.title_widgets_layout.setSpacing(10)  # Расстояние между элементами

        # Пример: Добавляем заголовок окна
        self.title_label = QLabel(window_name)  # Заголовок окна
        self.title_label.setStyleSheet("color: white; font-size: 14px;")
        self.title_widgets_layout.addWidget(self.title_label)

        # Добавляем контейнер с элементами в title_layout
        title_layout.addWidget(self.title_widgets_container)

        # Растягиваем оставшееся пространство
        title_layout.addStretch()

        self.title_bar.setLayout(title_layout)

        # Основной layout окна
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы вокруг основного layout
        self.main_layout.setSpacing(0)  # Убираем расстояние между элементами
        self.main_layout.addWidget(self.title_bar)
        self.content_area = QFrame(self)
        self.content_area.setStyleSheet("background-color: #222; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px;")
        self.main_layout.addWidget(self.content_area)
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(8, 8, 8, 8)  # Отступы внутри content_area
        self.content_area.setLayout(self.content_layout)

    def add_title_widget(self, widget):
        """
        Добавляет виджет в заголовок окна (рядом с кнопками управления).
        """
        self.title_widgets_layout.addWidget(widget)

    def minimize_window(self):
        """
        Анимация сворачивания окна (вниз).
        """
        # Создаем анимацию для перемещения окна вниз
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)  # Длительность анимации в миллисекундах
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце

        # Начальная позиция окна
        start_rect = self.geometry()
        # Конечная позиция окна (за пределами экрана вниз)
        screen_height = QApplication.primaryScreen().geometry().height()
        end_rect = QRect(start_rect.x(), screen_height, start_rect.width(), start_rect.height())

        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(self._on_minimize_animation_finished)  # Скрываем окно после завершения анимации
        self.animation.start()


    def _on_minimize_animation_finished(self):
        """
        Скрывает окно после завершения анимации сворачивания.
        """
        self.hide()
        self.minimized = True
        # Обновляем заголовок меню в главном окне
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu("desktop")
        else:
            print("Ошибка: `parent_window` не найден или `update_win_menu` отсутствует!")


    def close_window(self):
        """
        Анимация закрытия окна (вверх).
        """
        # Создаем анимацию для перемещения окна вверх
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)  # Длительность анимации в миллисекундах
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце

        # Начальная позиция окна
        start_rect = self.geometry()
        # Конечная позиция окна (за пределами экрана вверх)
        end_rect = QRect(start_rect.x(), -start_rect.height(), start_rect.width(), start_rect.height())

        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(self._on_close_animation_finished)  # Закрываем окно после завершения анимации
        self.animation.start()

    def _on_close_animation_finished(self):
        """
        Закрывает окно после завершения анимации.
        """
        window_name = None
        for name, window in self.parent().open_windows.items():
            if window == self:
                window_name = name
                break

        if window_name:
            self.parent().active_windows[window_name] = False
            self.parent().update_dock_indicators()
            self.parent().open_windows[window_name] = None  # Убираем ссылку на удалённое окно

        self.hide()  # Скрываем окно перед удалением
        # Обновляем заголовок меню в главном окне
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu("desktop")
        else:
            print("Ошибка: `parent_window` не найден или `update_win_menu` отсутствует!")
        self.setParent(None)  # Убираем родителя
        self.deleteLater()  # Удаляем объект

    def set_content(self, widget):
        """
        Добавляет содержимое в окно.
        """
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)

        self.content_layout.addWidget(widget)

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()  # Восстановить в нормальный размер
        else:
            # Получаем размеры рабочего стола
            screen_geometry = QApplication.primaryScreen().availableGeometry()

            # Учитываем высоту верхней панели и док-панели
            top_bar_height = 30  # Высота верхней панели
            dock_height = 0  # Высота док-панели
            top_offset = 33  # Дополнительный отступ сверху

            # Устанавливаем размеры окна с учетом панелей и отступа сверху
            available_height = screen_geometry.height() - top_bar_height - dock_height - top_offset
            self.setGeometry(screen_geometry.x(), screen_geometry.y() + top_offset, screen_geometry.width(), available_height)

        self.raise_()  # Поднять окно на передний план

        # Обновляем заголовок меню в главном окне, если оно есть
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)
        else:
            print("Ошибка: `parent_window` не найден или `update_win_menu` отсутствует!")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.pos().y() < 30:  # Захват за заголовок
                self.old_pos = event.globalPosition().toPoint()
            elif event.pos().x() > self.width() - 10 and event.pos().y() > self.height() - 10:
                self.resizing = True

        self.raise_()  # Поднимет окно на передний план при нажатии мыши

        # Обновляем заголовок меню в главном окне
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)
        else:
            print("Ошибка: `parent_window` не найден или `update_win_menu` отсутствует!")

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos and not self.resizing:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

        elif self.resizing:
            self.resize(event.pos().x(), event.pos().y())

        self.raise_()  # Поднимаем окно на передний план

        # Обновляем заголовок меню в главном окне
        if self.parent_window and hasattr(self.parent_window, "update_win_menu"):
            self.parent_window.update_win_menu(self.window_name)
        else:
            print("Ошибка: `parent_window` не найден или `update_win_menu` отсутствует!")

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.old_pos = None
        self.resizing = False

    def update_win_menu(self, window_name):
        """
        Обновляет текст меню "Win" на активное окно.
        """
        self.win_menu.setTitle(window_name)
    
    def restore_window(self):
        """
        Восстанавливает окно после сворачивания.
        """
        if self.minimized:
            # Показываем окно
            self.show()
            self.minimized = False

            # Восстанавливаем позицию и размер окна
            screen_geometry = QApplication.primaryScreen().geometry()
            start_rect = QRect(self.x(), screen_geometry.height(), self.width(), self.height())
            end_rect = QRect(self.x(), screen_geometry.height() // 2 - self.height() // 2, self.width(), self.height())

            # Анимация восстановления окна
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(150)  # Длительность анимации в миллисекундах
            self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Плавное замедление в конце
            self.animation.setStartValue(start_rect)
            self.animation.setEndValue(end_rect)
            self.animation.start()

    def toggle_window(self):
        """
        Переключает состояние окна: сворачивает или восстанавливает.
        """
        if self.minimized:
            self.restore_window()
        else:
            self.minimize_window()
