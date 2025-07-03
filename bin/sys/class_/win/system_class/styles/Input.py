import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class Input(QLineEdit):
    def __init__(
        self,
        parent=None,
        placeholder_text="Password",
        initial_text="",
        echo_mode=QLineEdit.EchoMode.Normal  # Изменено с Password на Normal
    ):
        super().__init__(parent)

        self.setPlaceholderText(placeholder_text)
        self.setText(initial_text)
        self.setEchoMode(echo_mode)

        self.setFont(QFont("Segoe UI", 14))
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #555;
                border-radius: 5px;
                padding: 5px;
                background-color: rgba(0, 0, 0, 150);
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #0078D7;
            }
        """)