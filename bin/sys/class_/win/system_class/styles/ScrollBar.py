from PyQt6.QtWidgets import QScrollBar
from PyQt6.QtCore import Qt

class CastScrollBar(QScrollBar):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #3a3a3a;
                width: 12px;
                margin: 16px 0 16px 0;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #888;
                min-height: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #555;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
                height: 16px;
                subcontrol-origin: margin;
            }

            QScrollBar::add-line:vertical:hover,
            QScrollBar::sub-line:vertical:hover {
                background: #ccc;
            }

            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                width: 8px;
                height: 8px;
                background: transparent;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 12px;
                margin: 0 16px 0 16px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background: #888;
                min-width: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #555;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background: none;
                width: 16px;
                subcontrol-origin: margin;
            }

            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                width: 8px;
                height: 8px;
                background: transparent;
            }

            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
