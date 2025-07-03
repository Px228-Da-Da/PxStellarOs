from PyQt6.QtWidgets import QVBoxLayout, QWidget
# from bin.sys.class_.TerminalApp import TerminalApp  # Импортируем TerminalApp
# from apps.local.init import DraggableResizableWindow  # Импортируем базовый класс окна

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class CmdWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="", translator=None, lang_code="en"):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name  # Сохраняем имя окна
        self.lang_code = lang_code

        self.setGeometry(300, 150, 800, 500)
        
        self.terminal = TerminalApp()  # Создаём терминал
        self.set_content(self.terminal)
        
        self.hide()
