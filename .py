import sys
import os
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

# Шлях до іконки
icon_dir_PATH = os.path.join("bin", "icons", "local_icons", "IconOs", "OS.png")

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        # Налаштування вікна SplashScreen
        self.setWindowTitle("Завантаження...")
        self.setStyleSheet("background-color: black;")  # Чорний фон

        # Лейбл для відображення іконки
        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(QPixmap(icon_dir_PATH))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Встановлення розмірів вікна на весь екран
        self.showFullScreen()

        # Таймер для автоматичного переходу через 8 секунд
        QTimer.singleShot(8000, self.switch_to_main_window)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.end()

    def switch_to_main_window(self):
        self.close()
        window = MacOSWindow()  # Замініть на свій основний клас
        window.show()

class MacOSWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Основне вікно")
        self.setGeometry(100, 100, 1024, 768)
        self.setStyleSheet("background-color: white;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash_screen = SplashScreen()
    splash_screen.show()
    sys.exit(app.exec())
