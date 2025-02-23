import sys
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame

class NestedWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Вложенное окно')
        self.setGeometry(50, 50, 400, 300)

        self.button_minimize = QPushButton('Сворачивать', self)
        self.button_minimize.clicked.connect(self.minimize_window)
        
        self.button_restore = QPushButton('Разворачивать', self)
        self.button_restore.clicked.connect(self.restore_window)
        self.button_restore.setEnabled(False)  # Кнопка для восстановления будет отключена на старте
        
        layout = QVBoxLayout()
        layout.addWidget(self.button_minimize)
        layout.addWidget(self.button_restore)
        self.setLayout(layout)

        self.is_minimized = False
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(120)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def minimize_window(self):
        # Анимация сворачивания
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(int(self.x() + self.width() / 2), int(self.y() + self.height() / 2), 10, 10))
        self.animation.start()
        self.is_minimized = True

        # Отключаем кнопку сворачивания, включаем кнопку развертывания
        self.button_minimize.setEnabled(False)
        self.button_restore.setEnabled(True)

    def restore_window(self):
        # Анимация разворачивания
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(50, 50, 400, 300))
        self.animation.start()
        self.is_minimized = False

        # Отключаем кнопку развертывания, включаем кнопку сворачивания
        self.button_minimize.setEnabled(True)
        self.button_restore.setEnabled(False)


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Основное окно с вложенными окнами')
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout(self)

        self.button = QPushButton('Создать вложенное окно', self)
        self.button.clicked.connect(self.create_nested_window)
        
        self.layout.addWidget(self.button)

        self.nested_window_frame = QFrame(self)
        self.nested_window_frame.setGeometry(50, 50, 400, 300)
        self.nested_window_frame.setStyleSheet("background-color: lightgray; border: 1px solid black;")

        self.layout.addWidget(self.nested_window_frame)

    def create_nested_window(self):
        # Вложенное окно будет добавлено в этот фрейм
        nested_window = NestedWindow()
        nested_window.setParent(self.nested_window_frame)  # Вложение окна в основной контейнер
        nested_window.setGeometry(0, 0, 400, 300)
        nested_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
