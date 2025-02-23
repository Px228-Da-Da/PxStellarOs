import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect

class JumpingButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)  # Длительность анимации в миллисекундах
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Тип анимации
        self.is_animating = False  # Флаг для отслеживания состояния анимации

    def mousePressEvent(self, event):
        if not self.is_animating:  # Проверяем, не выполняется ли уже анимация
            self.jump()
            super().mousePressEvent(event)

    def jump(self):
        self.is_animating = True  # Устанавливаем флаг, что анимация началась
        start_rect = self.geometry()
        end_rect = QRect(start_rect.x(), start_rect.y() - 10, start_rect.width(), start_rect.height())
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(self.resetPosition)  # Связываем завершение анимации с возвратом в исходное положение
        self.animation.start()

    def resetPosition(self):
        start_rect = self.geometry()
        end_rect = QRect(start_rect.x(), start_rect.y() + 10, start_rect.width(), start_rect.height())
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.disconnect(self.resetPosition)  # Отключаем сигнал, чтобы избежать рекурсии
        self.animation.finished.connect(self.onAnimationFinished)  # Связываем завершение анимации с разблокировкой кнопки
        self.animation.start()

    def onAnimationFinished(self):
        self.is_animating = False  # Сбрасываем флаг после завершения анимации
        self.animation.finished.disconnect(self.onAnimationFinished)  # Отключаем сигнал

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Jumping Button Example')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.button = JumpingButton('Click Me!', self)
        self.button.clicked.connect(self.on_button_clicked)

        layout.addWidget(self.button)
        self.setLayout(layout)

    def on_button_clicked(self):
        print("Button clicked!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())