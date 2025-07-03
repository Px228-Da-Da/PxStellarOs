from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QStyle
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
import os


class StellarMessageBox(QDialog):
    class StandardButton:
        NoButton = 0
        OK = 1
        Cancel = 2
        Yes = 4
        No = 8

    ICON_PATHS = {
        "info": "bin/icons/local_icons/system/info.png",
        "warning": "bin/icons/local_icons/system/warning.png",
        "error": "bin/icons/local_icons/system/close.png",
        "question": "bin/icons/local_icons/system/question.png",
    }

    def __init__(self, parent=None, title="Повідомлення", message="Текст повідомлення", icon_type="info", buttons=["OK"]):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)

        self.background_widget = QWidget(self)
        self.background_widget.setObjectName("background")
        self.background_widget.setStyleSheet("""
            QWidget#background {
                background-color: #3B3B3B;
                border: 2px solid #0078d7;
                border-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.background_widget)

        layout = QVBoxLayout(self.background_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Іконка + текст
        content_layout = QHBoxLayout()
        layout.addLayout(content_layout)

        icon_label = QLabel()
        icon_pix = self.get_icon_pixmap(icon_type)
        if icon_pix:
            icon_label.setPixmap(icon_pix.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        content_layout.addWidget(icon_label)

        text_label = QLabel(message)
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        content_layout.addWidget(text_label)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addLayout(button_layout)

        for btn_text in buttons:
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda _, b=btn_text: self.button_clicked(b))
            button_layout.addWidget(btn)

        self.clicked_button = None
        self.resize(400, 160)

        # Додаткове стилізування кнопок і тексту
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: white;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 6px 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2899f5;
            }
        """)




    def get_icon_pixmap(self, icon_type):
        path = self.ICON_PATHS.get(icon_type)
        if path and os.path.exists(path):
            return QPixmap(path)
        else:
            # fallback на системну іконку
            style = self.style()
            if icon_type == "info":
                return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation).pixmap(64, 64)
            elif icon_type == "warning":
                return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning).pixmap(120, 120)
            elif icon_type == "error":
                return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical).pixmap(64, 64)
            elif icon_type == "question":
                return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion).pixmap(64, 64)

        return None

    def button_clicked(self, button_name):
        self.clicked_button = button_name
        self.accept()

    @staticmethod
    def show_message(parent=None, title="Повідомлення", message="...", icon="info", buttons=["OK"]):
        dlg = StellarMessageBox(parent, title, message, icon, buttons)
        dlg.exec()
        return dlg.clicked_button

    @staticmethod
    def information(parent=None, title="Інформація", message=""):
        return StellarMessageBox.show_message(
            parent=parent,
            title=title,
            message=message,
            icon="info",
            buttons=["OK"]
        )

    @staticmethod
    def warning(parent=None, title="Попередження", message=""):
        return StellarMessageBox.show_message(
            parent=parent,
            title=title,
            message=message,
            icon="warning",
            buttons=["OK"]
        )

    @staticmethod
    def critical(parent=None, title="Помилка", message=""):
        return StellarMessageBox.show_message(
            parent=parent,
            title=title,
            message=message,
            icon="error",
            buttons=["OK"]
        )

    @staticmethod
    def question(parent=None, title="Питання", message="Ви впевнені?", icon="question", buttons=None):
        if buttons is None:
            buttons = StellarMessageBox.StandardButton.Yes | StellarMessageBox.StandardButton.No

        btn_texts = []
        mapping = {}

        if buttons & StellarMessageBox.StandardButton.Yes:
            btn_texts.append("Так")
            mapping["Так"] = StellarMessageBox.StandardButton.Yes
        if buttons & StellarMessageBox.StandardButton.No:
            btn_texts.append("Ні")
            mapping["Ні"] = StellarMessageBox.StandardButton.No
        if buttons & StellarMessageBox.StandardButton.Cancel:
            btn_texts.append("Скасувати")
            mapping["Скасувати"] = StellarMessageBox.StandardButton.Cancel
        if buttons & StellarMessageBox.StandardButton.OK:
            btn_texts.append("OK")
            mapping["OK"] = StellarMessageBox.StandardButton.OK

        clicked = StellarMessageBox.show_message(
            parent=parent,
            title=title,
            message=message,
            icon="question",
            buttons=btn_texts
        )
        return mapping.get(clicked, StellarMessageBox.StandardButton.NoButton)
