from PyQt6.QtWidgets import QVBoxLayout, QWidget
from bin.sys.class_.TerminalApp import TerminalApp  # Импортируем TerminalApp
from apps.local.init import DraggableResizableWindow  # Импортируем базовый класс окна

class CmdWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name=""):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name  # Сохраняем имя окна

        self.setGeometry(300, 150, 800, 500)
        
        self.terminal = TerminalApp()  # Создаём терминал
        self.set_content(self.terminal)
        
        self.hide()
