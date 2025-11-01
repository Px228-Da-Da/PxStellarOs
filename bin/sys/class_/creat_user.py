from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QApplication, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QPainter, QRadialGradient, QColor, QBrush
import sys, math, time, random, os


# ============================
# АНИМИРОВАННЫЙ ФОН
# ============================
class SoftGlowBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # пропуск кликов
        self._t = 0.0
        self._speed = 0.3
        self._last_time = time.time()

        self.colors = [
            QColor(90, 160, 255, 120),
            QColor(150, 120, 255, 120),
            QColor(80, 200, 255, 120),
            QColor(100, 180, 255, 120)
        ]
        self.current_color = self.colors[0]
        self.next_color = random.choice(self.colors[1:])
        self.color_blend = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

    def animate(self):
        now = time.time()
        dt = now - self._last_time
        self._last_time = now
        self._t += dt * self._speed

        self.color_blend += dt * 0.05
        if self.color_blend >= 1.0:
            self.current_color = self.next_color
            self.next_color = random.choice([c for c in self.colors if c != self.current_color])
            self.color_blend = 0.0
        self.update()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor(0, 0, 0))

        cx, cy = w / 2, h / 2
        ax, ay = 0.3 * w, 0.25 * h
        bx, by = 0.4 * w, 0.35 * h

        x1 = cx + ax * math.sin(self._t * 0.8)
        y1 = cy + ay * math.cos(self._t * 0.9)
        x2 = cx + bx * math.cos(self._t * 1.2 + 1.3)
        y2 = cy + by * math.sin(self._t * 1.0 + 0.8)

        r = int(self.current_color.red() * (1 - self.color_blend) + self.next_color.red() * self.color_blend)
        g = int(self.current_color.green() * (1 - self.color_blend) + self.next_color.green() * self.color_blend)
        b = int(self.current_color.blue() * (1 - self.color_blend) + self.next_color.blue() * self.color_blend)
        color_mix = QColor(r, g, b, 130)

        grad1 = QRadialGradient(x1, y1, max(w, h) * 0.6)
        grad1.setColorAt(0.0, color_mix)
        grad1.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad1))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        grad2 = QRadialGradient(x2, y2, max(w, h) * 0.7)
        grad2.setColorAt(0.0, QColor(color_mix.red(), color_mix.green(), color_mix.blue(), 90))
        grad2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad2))
        painter.drawRect(self.rect())
        painter.end()


# ============================
# ОСНОВНОЕ ОКНО
# ============================
class SetupWizard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lacmi OS Setup")

        # Добавляем фон
        self.bg = SoftGlowBackground(self)
        self.bg.lower()

        # Контейнер
        self.container = QWidget(self)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.container)

        self.setStyleSheet("""
            QWidget { color: #f0f0f0; font-family: 'Segoe UI Variable Display', 'Segoe UI'; }
            QLabel { color: #ffffff; }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 8px;
                padding: 12px 32px;
                font-size: 16px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #1084e0; }
        """)

        self.show_welcome()

        # Показываем окно только после инициализации
        self.showFullScreen()

    def resizeEvent(self, event):
        if hasattr(self, "bg") and self.bg:
            self.bg.resize(self.size())
        super().resizeEvent(event)



    # -------------------------------
    # WELCOME SCREEN
    # -------------------------------
    def show_welcome(self):
        self.clear_container()

        self.welcome_label = QLabel("Ласкаво просимо до Stellar OS")
        self.welcome_label.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle_label = QLabel("Давайте налаштуємо вашу систему разом.")
        self.subtitle_label.setFont(QFont("Segoe UI", 20))
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #aaaaaa;")

        self.next_button = QPushButton("Далі →")
        self.next_button.setMinimumWidth(180)
        self.next_button.clicked.connect(self.show_install_screen)

        self.container_layout.addWidget(self.welcome_label)
        self.container_layout.addWidget(self.subtitle_label)
        self.container_layout.addSpacing(60)
        self.container_layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Fade-in for the container
        self.fade_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.fade_effect)
        self.fade_in(self.fade_effect)

        # Gentle subtitle glow
        self.subtitle_glow = QGraphicsOpacityEffect()
        # self.subtitle_label.setGraphicsEffect(self.subtitle_glow)
        self.subtitle_anim = QPropertyAnimation(self.subtitle_glow, b"opacity")
        self.subtitle_anim.setDuration(1500)
        self.subtitle_anim.setStartValue(0.4)
        self.subtitle_anim.setEndValue(1.0)
        self.subtitle_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.subtitle_anim.setLoopCount(-1)
        self.subtitle_anim.start()

    # -------------------------------
    # INSTALL SCREEN
    # -------------------------------
    def show_install_screen(self):
        self.fade_out(self.fade_effect, self.show_main_setup)

    def show_main_setup(self):
        self.clear_container()

        title = QLabel("Почнемо з налаштування Stellar OS")
        title.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Виберіть свої налаштування та завершіть налаштування.")
        subtitle.setFont(QFont("Segoe UI", 18))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #bbbbbb;")

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start setup")
        self.start_button.setMinimumWidth(180)
        self.start_button.clicked.connect(self.start_setup)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setMinimumWidth(120)
        self.exit_button.clicked.connect(QApplication.quit)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.exit_button)

        self.container_layout.addWidget(title)
        self.container_layout.addWidget(subtitle)
        self.container_layout.addSpacing(80)
        self.container_layout.addLayout(button_layout)

        # Fade-in
        self.fade_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.fade_effect)
        self.fade_in(self.fade_effect)

    # -------------------------------
    # SETUP PROCESS
    # -------------------------------
    def start_setup(self):
        self.start_button.setEnabled(False)
        self.exit_button.setEnabled(False)

        print("[SETUP] Starting setup process...")
        os.makedirs("root/dataLacmi/user", exist_ok=True)
        with open("root/dataLacmi/user/install", "w", encoding="utf-8") as f:
            f.write("yes")

        self.fade_out(self.fade_effect, self.show_completion_screen)

    def show_completion_screen(self):
        self.clear_container()

        done_label = QLabel("✅ Setup completed successfully!\nYou can now restart Lacmi OS.")
        done_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        done_label.setFont(QFont("Segoe UI", 28))
        done_label.setStyleSheet("color: #00cc66;")

        self.container_layout.addWidget(done_label)

        done_effect = QGraphicsOpacityEffect(done_label)
        done_label.setGraphicsEffect(done_effect)
        self.fade_in(done_effect)

    # -------------------------------
    # ANIMATION HELPERS
    # -------------------------------
    def fade_in(self, effect, duration=1200):
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()
        self.anim = anim  # keep reference

    def fade_out(self, effect, callback, duration=1000):
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.finished.connect(callback)
        anim.start()
        self.anim = anim

    def clear_container(self):
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i).widget()
            if item:
                item.setParent(None)


# ============================
# ЗАПУСК
# ============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SetupWizard()
    w.show()
    sys.exit(app.exec())
