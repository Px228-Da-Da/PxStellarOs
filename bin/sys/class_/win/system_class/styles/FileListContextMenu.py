from PyQt6.QtWidgets import QMenu, QApplication, QListWidget
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt, QSize


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class FileListContextMenu(QListWidget, ContextMenuMixin_cmd):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(QSize(45, 45))
        self.setGridSize(QSize(150, 120))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setWordWrap(True)
        self.setUniformItemSizes(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)

        # --- стили ---
        self.setStyleSheet("""
            QListWidget {
                background-color: rgba(30, 30, 30, 180);
                border: 1px solid #444;
                border-radius: 4px;
                padding: 2px;
            }
            QListWidget::item {
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: rgba(60, 60, 60, 150);
            }
            QListWidget::item:selected {
                background-color: rgba(75, 110, 175, 200);
            }
            QListWidget::item:selected:!active {
                background-color: rgba(65, 90, 150, 200);
            }
        """)

    def contextMenuEvent(self, event):
        """Кастомное контекстное меню для QListWidget"""
        menu = CustomContextMenu_cmd(self)
        self.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                background-color: transparent;
                color: #e0e0e0;
                padding: 8px 25px 8px 20px;
                margin: 2px;
                border-radius: 4px;
                font-size: 14px;
            }
            QMenu::item:selected {
                background-color: #4a9eff;
                color: #ffffff;
            }
            QMenu::item:disabled {
                color: #666666;
            }
            QMenu::separator {
                height: 1px;
                background: #555;
                margin: 5px 12px;
            }
            QMenu::right-arrow {
                margin-right: 5px;
            }
        """)


        selected_items = self.selectedItems()
        has_selection = bool(selected_items)

        copy_action = QAction("📋 Копировать имя", self)
        delete_action = QAction("🗑️ Удалить", self)
        select_all_action = QAction("☑️ Выделить все", self)

        copy_action.setEnabled(has_selection)
        delete_action.setEnabled(has_selection)

        copy_action.triggered.connect(self.copy_selected_names)
        delete_action.triggered.connect(self.delete_selected_items)
        select_all_action.triggered.connect(self.selectAll)

        menu.addAction(copy_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(select_all_action)

        menu.exec(event.globalPos())

    def copy_selected_names(self):
        """Копировать имена выбранных элементов"""
        names = [item.text() for item in self.selectedItems()]
        if names:
            QApplication.clipboard().setText("\n".join(names))

    def delete_selected_items(self):
        """Удалить выбранные элементы"""
        for item in self.selectedItems():
            row = self.row(item)
            self.takeItem(row)
