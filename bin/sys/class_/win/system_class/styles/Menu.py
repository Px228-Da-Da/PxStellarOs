# import os
# import platform
# import shutil
# from PyQt6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
#     QPushButton, QFileDialog, QLabel, QLineEdit, QFrame, QMenu,
#     QInputDialog, QMessageBox, QDialog, QDialogButtonBox
# )
# from PyQt6.QtCore import Qt, QSize, QPoint
# from PyQt6.QtGui import QIcon, QFont, QPalette, QColor

# class Menu(QMenu):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setStyleSheet("""
#             QMenu {
#                 background-color: #2d2d2d;
#                 border: 1px solid #444;
#                 color: white;
#             }
#             QMenu::item {
#                 padding: 5px 25px 5px 20px;
#                 margin: 2px;
#             }
#             QMenu::item:selected {
#                 background-color: #0078d7;
#             }
#             QMenu::separator {
#                 height: 1px;
#                 background-color: #444;
#                 margin: 2px 0;
#             }
#         """)

from PyQt6.QtWidgets import QMenu, QGraphicsDropShadowEffect, QWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor

class Menu(QMenu):
    """
    macOS-styled QMenu.
    Поддерживает вызовы: Menu(), Menu(parent), Menu(title, parent).
    Без setIconSize — в Qt6 его уже нет.
    """
    def __init__(self, *args, use_fallback_style: bool = False, **kwargs):
        # ---- разруливаем перегрузки ----
        title = None
        parent = None
        if len(args) == 1:
            # Menu(parent) ИЛИ Menu(title)
            if isinstance(args[0], QWidget) or args[0] is None:
                parent = args[0]
            else:
                title = str(args[0])
        elif len(args) >= 2:
            title = str(args[0])
            parent = args[1]

        if title is None:
            super().__init__(parent)
        else:
            super().__init__(title, parent)

        # ---- оформление ----
        self.setObjectName("macMenu")
        self.setSeparatorsCollapsible(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # мягкая тень по периметру
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.setGraphicsEffect(shadow)

        if use_fallback_style:
            self.setStyleSheet(self.macos_qss())

    @staticmethod
    def macos_qss(accent: str = "#2d64f0") -> str:
        return f"""
        /* ---------- macOS-like QMenu ---------- */
        QMenu#macMenu {{
            background: rgba(255,255,255,0.98);
            border: 1px solid rgba(0,0,0,0.10);
            border-radius: 12px;
            padding: 6px;
        }}
        QMenu#macMenu::item {{
            padding: 6px 14px;
            border-radius: 8px;
            color: #111;
            background: transparent;
        }}
        QMenu#macMenu::item:selected {{
            background: {accent};
            color: white;
        }}
        QMenu#macMenu::item:disabled {{
            color: rgba(0,0,0,0.35);
            background: transparent;
        }}
        QMenu#macMenu::icon {{ padding-left: 2px; padding-right: 8px; }}
        QMenu#macMenu::indicator {{ width: 16px; height: 16px; margin-right: 8px; }}
        QMenu#macMenu::separator {{ height: 1px; margin: 6px 10px; background: rgba(0,0,0,0.12); }}
        QMenu#macMenu::right-arrow {{ margin-right: 6px; }}
        """
