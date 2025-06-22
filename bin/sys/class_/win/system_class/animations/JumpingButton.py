import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class JumpingButton(QPushButton):
    def __init__(self, icon_path=None, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.is_animating = False
        self.default_size = 44
        self.setFixedSize(self.default_size, self.default_size)
        self.original_geometry = None

        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(self.default_size, self.default_size))

        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)

    def enterEvent(self, event: QEnterEvent):
        if not self.is_animating:
            self.original_geometry = self.geometry()
            self.animateJump(-10)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_animating:
            self.animateJump(10)
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if not self.is_animating:
            self.animateJump(-20, True)
        super().mousePressEvent(event)

    def animateJump(self, offset, is_click=False):
        if self.original_geometry is None:
            self.original_geometry = self.geometry()

        self.is_animating = True
        start_rect = self.geometry()
        end_rect = QRect(start_rect.x(), self.original_geometry.y() + offset, start_rect.width(), start_rect.height())
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(lambda: self.resetPosition(is_click))
        self.animation.start()

    def resetPosition(self, is_click):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.original_geometry)
        self.animation.finished.disconnect()
        self.animation.finished.connect(self.onAnimationFinished)
        self.animation.start()

    def onAnimationFinished(self):
        self.is_animating = False
        self.animation.finished.disconnect()
