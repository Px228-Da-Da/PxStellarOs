import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QIcon, QEnterEvent, QMouseEvent

class JumpingButton(QPushButton):
    def __init__(self, icon_path=None, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.is_animating = False
        self.default_size = 48
        self.setFixedSize(self.default_size, self.default_size)
        self.original_geometry = None

        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(self.size())

        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0.12);
                border-radius: 15px;
                border: 2px solid rgba(0, 0, 0, 0.12);
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.12);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.12);
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

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Jumping Button Dock')
        self.setGeometry(100, 100, 400, 100)
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        icon_paths = [
            "/home/laski/Документи/GitHub/PxStellarOs/bin/icons/local_icons/local_apps/cmd/cmd.png",
            "/home/laski/Документи/GitHub/PxStellarOs/bin/icons/local_icons/local_apps/cmd/cmd.png",
            "/home/laski/Документи/GitHub/PxStellarOs/bin/icons/local_icons/local_apps/cmd/cmd.png",
            "/home/laski/Документи/GitHub/PxStellarOs/bin/icons/local_icons/local_apps/cmd/cmd.png",
            "/home/laski/Документи/GitHub/PxStellarOs/bin/icons/local_icons/local_apps/cmd/cmd.png"
        ]
        
        self.buttons = []
        for icon in icon_paths:
            button = JumpingButton(icon_path=icon, parent=self)
            button.clicked.connect(self.on_button_clicked)
            layout.addWidget(button)
            self.buttons.append(button)

        self.setLayout(layout)

    def on_button_clicked(self):
        print("Button clicked!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())