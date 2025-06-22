import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class Button(QPushButton):
    def __init__(self, text, style='contained', enabled=True):
        super().__init__(text)
        self.style = style
        self.setFixedSize(140, 48)
        self.setMouseTracking(True)
        self.setEnabled(enabled)
        self.pressed_flag = False
        self.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self):
        base = {
            "bg": "#3A2C6C",
            "hover": "#533CA4",
            "active": "#372871",
            "text": "#8160F4",
            "disabled_bg": "#555555",
            "disabled_text": "#2f2f2f",
        }

        if not self.isEnabled():
            return f"""
                QPushButton {{
                    background-color: {base['disabled_bg']};
                    color: {base['disabled_text']};
                    border-radius: 8px;
                    font-size: 16px;
                    
                }}
            """
        elif self.pressed_flag:
            return f"""
                QPushButton {{
                    background-color: {base['active']};
                    color: {base['text']};
                    border-radius: 8px;
                    font-size: 16px;
                    
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {base['bg']};
                    color: {base['text']};
                    border-radius: 8px;
                    font-size: 16px;
                    
                }}
                QPushButton:hover {{
                    background-color: {base['hover']};
                }}
            """

    def mousePressEvent(self, event):
        self.pressed_flag = True
        self.setStyleSheet(self.get_stylesheet())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.pressed_flag = False
        self.setStyleSheet(self.get_stylesheet())
        super().mouseReleaseEvent(event)
