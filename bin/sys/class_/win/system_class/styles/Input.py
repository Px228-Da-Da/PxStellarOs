from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class Input(QLineEdit):
    def __init__(
        self,
        parent=None,
        placeholder_text="Password",
        initial_text="",
        echo_mode=QLineEdit.EchoMode.Password
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
