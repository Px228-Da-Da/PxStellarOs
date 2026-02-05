import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *


class ToggleSwitch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 20)
        self._checked = True
        self._circle_position = self.width() - self.height() + 2

        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setDuration(200)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        if self._checked:
            self.animation.setEndValue(self.width() - self.height() + 2)
        else:
            self.animation.setEndValue(2)
        self.animation.start()
        self.update()
        # безопасно ищем родителя с методом toggle_wifi
        p = self.parent()
        while p is not None:
            if hasattr(p, "toggle_wifi"):
                p.toggle_wifi(self._checked)
                break
            p = p.parent()

    def paintEvent(self, event):
        radius = self.height() // 2
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._checked:
            painter.setBrush(QColor(0, 122, 255))
        else:
            painter.setBrush(QColor(180, 180, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), radius, radius)

        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawEllipse(QRect(int(self._circle_position), 2, self.height() - 4, self.height() - 4))

    def sizeHint(self):
        return QSize(30, 20)

    def isChecked(self):
        return self._checked

    def setChecked(self, state: bool):
        self._checked = state
        self._circle_position = self.width() - self.height() + 2 if state else 2
        self.update()

    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, pos):
        self._circle_position = pos
        self.update()

    circle_position = pyqtProperty(float, fget=get_circle_position, fset=set_circle_position)
