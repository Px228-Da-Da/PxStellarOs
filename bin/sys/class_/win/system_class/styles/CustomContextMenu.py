from PyQt6.QtWidgets import QMenu, QApplication
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class CustomContextMenu(QMenu):
    def __init__(self, parent=None, widget_type="text", translator=None, lang_code="en"):
        super().__init__(parent)
        self.widget_type = widget_type
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code
        self.setup_style()
        self.setup_actions()
    
    def setup_style(self):
        """Настройка стилей меню"""
        self.setStyleSheet("""
            CustomContextMenu {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 6px;
            }
            CustomContextMenu::item {
                background-color: transparent;
                color: #e0e0e0;
                padding: 8px 25px 8px 20px;
                margin: 2px;
                border-radius: 4px;
                font-size: 14px;
            }
            CustomContextMenu::item:selected {
                background-color: #4a9eff;
                color: #ffffff;
            }
            CustomContextMenu::item:disabled {
                color: #666666;
            }
            CustomContextMenu::separator {
                height: 1px;
                background: #555;
                margin: 5px 12px;
            }
            CustomContextMenu::right-arrow {
                margin-right: 5px;
            }
        """)
    
    def setup_actions(self):
        """Создание стандартных действий"""
        # Основные действия

        self.cut_action = QAction(self.tr("✂️ Cut"), self)
        self.copy_action = QAction(self.tr("📋 Copy"), self)
        self.paste_action = QAction(self.tr("📝 Paste"), self)
        self.delete_action = QAction(self.tr("🗑️ Delete"), self)
        self.select_all_action = QAction(self.tr("☑️ SelectAll"), self)
        self.undo_action = QAction(self.tr("↶ Undo"), self)
        self.redo_action = QAction(self.tr("↷ Redo"), self)

        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        
        self.delete_action.setShortcut(QKeySequence("Del"))
        
        # self.select_all_action = QAction("☑️ Выделить все", self)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        
        self.undo_action = QAction("↶ Отменить", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        
        self.redo_action = QAction("↷ Повторить", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
    
    def create_text_edit_menu(self, text_widget):
        """Создать меню для QTextEdit/QPlainTextEdit"""
        self.clear()
        
        # Проверяем доступность действий
        can_undo = text_widget.isUndoRedoEnabled() and text_widget.document().isUndoAvailable()
        can_redo = text_widget.isUndoRedoEnabled() and text_widget.document().isRedoAvailable()
        has_selection = text_widget.textCursor().hasSelection()
        
        self.undo_action.setEnabled(can_undo)
        self.redo_action.setEnabled(can_redo)
        self.cut_action.setEnabled(has_selection)
        self.copy_action.setEnabled(has_selection)
        self.delete_action.setEnabled(has_selection)
        
        # Подключаем сигналы
        self.undo_action.triggered.connect(text_widget.undo)
        self.redo_action.triggered.connect(text_widget.redo)
        self.cut_action.triggered.connect(text_widget.cut)
        self.copy_action.triggered.connect(text_widget.copy)
        self.paste_action.triggered.connect(text_widget.paste)
        self.delete_action.triggered.connect(self.delete_selected_text)
        self.select_all_action.triggered.connect(text_widget.selectAll)
        
        # Добавляем действия в меню
        if can_undo or can_redo:
            if can_undo:
                self.addAction(self.undo_action)
            if can_redo:
                self.addAction(self.redo_action)
            self.addSeparator()
        
        self.addAction(self.cut_action)
        self.addAction(self.copy_action)
        self.addAction(self.paste_action)
        self.addAction(self.delete_action)
        self.addSeparator()
        self.addAction(self.select_all_action)
        
        self.text_widget = text_widget
    
    def create_line_edit_menu(self, line_edit):
        """Создать меню для QLineEdit"""
        self.clear()
        
        has_selection = line_edit.hasSelectedText()
        
        self.cut_action.setEnabled(has_selection)
        self.copy_action.setEnabled(has_selection)
        self.delete_action.setEnabled(has_selection)
        self.paste_action.setEnabled(True)
        
        # Подключаем сигналы
        self.cut_action.triggered.connect(line_edit.cut)
        self.copy_action.triggered.connect(line_edit.copy)
        self.paste_action.triggered.connect(line_edit.paste)
        self.delete_action.triggered.connect(self.clear_line_edit_text)
        self.select_all_action.triggered.connect(line_edit.selectAll)
        
        self.addAction(self.cut_action)
        self.addAction(self.copy_action)
        self.addAction(self.paste_action)
        self.addAction(self.delete_action)
        self.addSeparator()
        self.addAction(self.select_all_action)
        
        self.line_edit = line_edit
    
    def create_basic_menu(self, widget):
        """Создать базовое меню для любого виджета"""
        self.clear()
        
        self.addAction(self.copy_action)
        self.addAction(self.select_all_action)
        
        self.widget = widget
    
    def delete_selected_text(self):
        """Удалить выделенный текст"""
        if hasattr(self, 'text_widget'):
            cursor = self.text_widget.textCursor()
            cursor.removeSelectedText()
    
    def clear_line_edit_text(self):
        """Очистить QLineEdit"""
        if hasattr(self, 'line_edit'):
            self.line_edit.clear()

class ContextMenuMixin:
    """Миксин для добавления кастомного контекстного меню к виджетам"""
    
    def contextMenuEvent(self, event):
        menu = CustomContextMenu(
            parent=self,
            translator=getattr(self, "tr", lambda x: x),   # якщо немає tr, використати identity
            lang_code=getattr(self, "lang_code", "en")    # якщо немає lang_code, "en"
        )

        if isinstance(self, (QTextEdit, QPlainTextEdit)):
            menu.create_text_edit_menu(self)
        elif hasattr(self, 'cut') and hasattr(self, 'copy') and hasattr(self, 'paste'):
            menu.create_line_edit_menu(self)
        else:
            menu.create_basic_menu(self)

        menu.exec(event.globalPos())

# CustomTextEdit(
#             parent=self,
#             translator=self.tr,
#             lang_code=self.lang_code
#     )
class CustomTextEdit(QTextEdit, ContextMenuMixin):
    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code


class CustomPlainTextEdit(QPlainTextEdit, ContextMenuMixin):
    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code


class CustomLineEdit(QLineEdit, ContextMenuMixin):
    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code





class CustomContextMenu_cmd(QMenu):
    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code
        self.setup_style()
        self.setup_actions()

    def setup_style(self):
        """Настройка стилей меню"""
        self.setStyleSheet("""
            CustomContextMenu_cmd {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 6px;
            }
            CustomContextMenu_cmd::item {
                background-color: transparent;
                color: #e0e0e0;
                padding: 8px 25px 8px 20px;
                margin: 2px;
                border-radius: 4px;
                font-size: 14px;
            }
            CustomContextMenu_cmd::item:selected {
                background-color: #4a9eff;
                color: #ffffff;
            }
        """)

    def setup_actions(self):
        """Создание только Copy и Select All"""
        self.copy_action = QAction(self.tr("📋 Copy"), self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        
        self.select_all_action = QAction(self.tr("☑️ SelectAll"), self)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)

    def create_text_edit_menu(self, text_widget):
        self.clear()
        has_selection = text_widget.textCursor().hasSelection()
        self.copy_action.setEnabled(has_selection)

        self.copy_action.triggered.connect(text_widget.copy)
        self.select_all_action.triggered.connect(text_widget.selectAll)

        self.addAction(self.copy_action)
        self.addAction(self.select_all_action)

        self.text_widget = text_widget

    def create_line_edit_menu(self, line_edit):
        self.clear()
        has_selection = line_edit.hasSelectedText()
        self.copy_action.setEnabled(has_selection)

        self.copy_action.triggered.connect(line_edit.copy)
        self.select_all_action.triggered.connect(line_edit.selectAll)

        self.addAction(self.copy_action)
        self.addAction(self.select_all_action)

        self.line_edit = line_edit

    def create_basic_menu(self, widget):
        self.clear()
        self.addAction(self.copy_action)
        self.addAction(self.select_all_action)
        self.widget = widget


class ContextMenuMixin_cmd:
    """Миксин для добавления кастомного контекстного меню с Copy и Select All"""
    def contextMenuEvent(self, event):
        menu = CustomContextMenu_cmd(
            parent=self,
            translator=getattr(self, "tr", lambda x: x),
            lang_code=getattr(self, "lang_code", "en")
        )

        if isinstance(self, (QTextEdit, QPlainTextEdit)):
            menu.create_text_edit_menu(self)
        elif hasattr(self, 'copy'):
            menu.create_line_edit_menu(self)
        else:
            menu.create_basic_menu(self)

        menu.exec(event.globalPos())


class CustomTextEdit_cmd(QTextEdit, ContextMenuMixin_cmd):
    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code


class CustomPlainTextEdit_cmd(QPlainTextEdit, ContextMenuMixin_cmd):
    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code


class CustomLineEdit_cmd(QLineEdit, ContextMenuMixin_cmd):
    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code
