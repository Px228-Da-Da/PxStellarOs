import os
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QFrame, QSplitter,
    QWidget, QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor, QPalette

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class CustomFileDialog(QDialog):
    def __init__(self, parent=None, caption="Open File", directory="", filter="All Files (*)", translator=None):
        super().__init__(parent)
        self.caption = caption
        self.directory = directory or os.path.expanduser("root")
        self.filter = filter
        self.selected_files = []
        self.current_file = ""
        self.translator = translator or (lambda x: x)
        self.icon_cache = {}
        
        # Инициализация иконок до setup_ui
        self.load_custom_icons()
        
        self.setWindowTitle(self.tr(caption))
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(900, 600)
        
        self.setup_ui()
        self.load_directory(self.directory)
    
    def tr(self, text):
        """Метод для перевода текста"""
        return self.translator(text) if self.translator else text
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Background widget for rounded corners
        self.background_widget = QWidget()
        self.background_widget.setObjectName("background")
        self.background_widget.setStyleSheet("""
            QWidget#background {
                background-color: #2d2d2d;
                border: 2px solid #0078d7;
                border-radius: 12px;
            }
        """)
        
        main_layout.addWidget(self.background_widget)
        
        # Content layout
        content_layout = QVBoxLayout(self.background_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(8)
        
        # Header with title and buttons
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.tr(self.caption))
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 18px;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
        """)
        self.close_button.clicked.connect(self.reject)
        header_layout.addWidget(self.close_button)
        
        content_layout.addLayout(header_layout)
        
        # Toolbar with navigation
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(5)
        
        # Navigation buttons
        nav_buttons = QHBoxLayout()
        nav_buttons.setSpacing(2)
        
        # Path to icons folder
        icons_dir = os.path.join("bin", "icons", "local_icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        # Back button
        self.back_button = QPushButton()
        back_icon = QIcon(os.path.join(icons_dir, "back.png"))
        self.back_button.setIcon(back_icon)
        self.back_button.setFixedSize(32, 32)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 50);
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 10);
            }
        """)
        self.back_button.clicked.connect(self.go_back)

        # Forward button
        self.forward_button = QPushButton()
        forward_icon = QIcon(os.path.join(icons_dir, "forward.png"))
        self.forward_button.setIcon(forward_icon)
        self.forward_button.setFixedSize(32, 32)
        self.forward_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 50);
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 10);
            }
        """)
        self.forward_button.clicked.connect(self.go_forward)
        
        # Up button
        self.up_button = QPushButton()
        up_icon = QIcon(os.path.join(icons_dir, "up.png"))
        self.up_button.setIcon(up_icon)
        self.up_button.setFixedSize(32, 32)
        self.up_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 50);
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 10);
            }
        """)
        self.up_button.clicked.connect(self.go_up)

        # Home button
        self.home_button = QPushButton()
        home_icon = QIcon(os.path.join(icons_dir, "home.png"))
        self.home_button.setIcon(home_icon)
        self.home_button.setFixedSize(32, 32)
        self.home_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 50);
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 10);
            }
        """)
        self.home_button.clicked.connect(self.go_home)
        
        nav_buttons.addWidget(self.back_button)
        nav_buttons.addWidget(self.forward_button)
        nav_buttons.addWidget(self.up_button)
        nav_buttons.addWidget(self.home_button)
        
        toolbar.addLayout(nav_buttons)
        
        # Path field
        self.path_edit = CustomLineEdit()
        self.path_edit.setPlaceholderText(self.tr("Enter path..."))
        self.path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: white;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        
        # Search field
        self.search_edit = CustomLineEdit()
        self.search_edit.setPlaceholderText(self.tr("Search..."))
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: white;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        self.search_edit.textChanged.connect(self.filter_items)
        
        # Create container for path and search
        path_search_layout = QHBoxLayout()
        path_search_layout.setSpacing(5)
        path_search_layout.addWidget(self.path_edit, 1)
        path_search_layout.addWidget(self.search_edit)
        # path_search_layout.addWidget(self.search_button)
        
        toolbar.addLayout(path_search_layout, 1)
        
        content_layout.addLayout(toolbar)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #555;")
        content_layout.addWidget(separator)
        
        # Main content area
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Places sidebar
        self.places_widget = QWidget()
        self.places_widget.setMaximumWidth(200)
        places_layout = QVBoxLayout(self.places_widget)
        
        self.places_list = QListWidget()
        # Установка кастомного скроллбара для меню
        self.places_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.places_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        self.places_list.setStyleSheet("""
            QListWidget {
                background-color: #2E2E2E;
                color: #E0E0E0;
                border: none;
                padding-top: 10px;
                font-size: 15px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 10px;
                margin: 4px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background-color: #4C8ED9;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3C3C3C;
            }
        """)
        self.places_list.itemClicked.connect(self.on_place_clicked)
        self.setup_places()
        places_layout.addWidget(self.places_list)
        
        # File list
        self.file_list_widget = QWidget()
        file_list_layout = QVBoxLayout(self.file_list_widget)
        
        self.file_list = QListWidget()
        self.file_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.file_list.setIconSize(QSize(45, 45))
        self.file_list.setGridSize(QSize(150, 120))
        self.file_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.file_list.setMovement(QListWidget.Movement.Static)
        self.file_list.setWordWrap(True)
        self.file_list.setUniformItemSizes(True)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setStyleSheet("""
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
        
        # Set white text color for file list
        palette = self.file_list.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        self.file_list.setPalette(palette)
        
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        file_list_layout.addWidget(self.file_list)
        
        main_splitter.addWidget(self.places_widget)
        main_splitter.addWidget(self.file_list_widget)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        
        content_layout.addWidget(main_splitter, 1)
        
        # File name and options
        file_name_layout = QHBoxLayout()
        
        file_name_label = QLabel(self.tr("File name:"))
        file_name_label.setStyleSheet("color: white; font-size: 14px;")
        file_name_layout.addWidget(file_name_label)
        
        self.file_name_edit = CustomLineEdit()
        self.file_name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: white;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        file_name_layout.addWidget(self.file_name_edit, 1)
        
        content_layout.addLayout(file_name_layout)
        
        # Options
        options_layout = QHBoxLayout()
        
        options_layout.addStretch()
        
        content_layout.addLayout(options_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.setStyleSheet(self.get_button_style())
        self.cancel_button.clicked.connect(self.reject)
        
        self.open_button = QPushButton(self.tr("Open"))
        self.open_button.setStyleSheet(self.get_button_style(primary=True))
        self.open_button.clicked.connect(self.accept_selection)
        
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.open_button)
        
        content_layout.addLayout(buttons_layout)
        
        # History for navigation
        self.history = []
        self.history_index = -1
        
    def get_button_style(self, primary=False):
        if primary:
            return """
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #2899f5;
                }
                QPushButton:disabled {
                    background-color: #555;
                    color: #999;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #3d3d3d;
                    color: white;
                    border: 1px solid #555;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 14px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
            """
    
    def load_custom_icons(self):
        """Загрузка пользовательских иконок"""
        self.icons_files_path = os.path.join("bin", "icons", "local_icons", "icons_files")
        os.makedirs(self.icons_files_path, exist_ok=True)
        
        # Загружаем иконку для папок
        folder_icon_path = os.path.join(self.icons_files_path, "explorer.png")
        if os.path.exists(folder_icon_path):
            self.folder_icon = QIcon(folder_icon_path)
        else:
            self.folder_icon = QIcon.fromTheme("folder")
        
        # Дефолтная иконка для файлов
        self.default_file_icon = QIcon.fromTheme("text-x-generic")
        
        # Иконка "not found" на случай отсутствия иконки
        not_found_icon = os.path.join(self.icons_files_path, "not.png")
        if os.path.exists(not_found_icon):
            self.not_found_icon = QIcon(not_found_icon)
        else:
            self.not_found_icon = self.default_file_icon
    
    def get_icon(self, path):
        """Получает иконку для файла/папки"""
        if os.path.isdir(path):
            return self.folder_icon or QIcon.fromTheme("folder") or QIcon()
        
        filename = os.path.basename(path)
        if filename.startswith('.'):
            ext = filename
        else:
            ext = os.path.splitext(filename)[1].lower()
            if not ext:
                ext = 'file'
        
        if ext in self.icon_cache:
            return self.icon_cache[ext]
        
        icon_name = ext[1:] if ext.startswith('.') else ext
        icon_path = os.path.join(self.icons_files_path, f"{icon_name}.png")
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            theme_names = [
                f"text-x-{icon_name}",
                f"application-x-{icon_name}",
                icon_name,
                "text-x-generic"
            ]
            
            for name in theme_names:
                icon = QIcon.fromTheme(name)
                if not icon.isNull():
                    break
            else:
                icon = self.not_found_icon or self.default_file_icon or QIcon()
        
        self.icon_cache[ext] = icon
        return icon
    
    def setup_places(self):
        """Setup common places"""
        places = [
            (self.tr("Desktop"), os.path.expanduser("root/user/desk")),
            (self.tr("Documents"), os.path.expanduser("root/user/Documents")),
            (self.tr("download"), os.path.expanduser("root/user/download")),
            (self.tr("images"), os.path.expanduser("root/user/images")),
        ]
        
        for name, path in places:
            if os.path.exists(path):
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.places_list.addItem(item)
    
    def load_directory(self, path):
        """Load directory contents"""
        if not os.path.isdir(path):
            return
        
        try:
            # Update history
            if not self.history or self.history[self.history_index] != path:
                self.history = self.history[:self.history_index + 1]
                self.history.append(path)
                self.history_index += 1
            
            self.directory = path
            self.path_edit.setText(path)
            self.update_nav_buttons()
            
            # Clear file list
            self.file_list.clear()
            
            # Get items
            items = os.listdir(path)
            
            # Add parent directory
            if path != os.path.dirname(path):
                parent_item = QListWidgetItem("[..]")
                parent_item.setData(Qt.ItemDataRole.UserRole, os.path.dirname(path))
                parent_item.setIcon(self.get_icon(os.path.dirname(path)))
                self.file_list.addItem(parent_item)
            
            # Add directories first
            # for name in sorted(items, key=lambda s: s.lower()):
            #     full_path = os.path.join(path, name)
                
            #     # Пропускаем папки с названием "bin"
            #     if os.path.isdir(full_path) and name.lower() == "bin":
            #         continue
                    
            #     if os.path.isdir(full_path):
            #         item = QListWidgetItem(name)
            #         item.setData(Qt.ItemDataRole.UserRole, full_path)
            #         item.setIcon(self.get_icon(full_path))
            #         self.file_list.addItem(item)
            # Служебные папки, которые скрываем
            excluded_folders = {".git", "__pycache__"}

            # Add directories first
            for name in sorted(items, key=lambda s: s.lower()):
                full_path = os.path.join(path, name)

                # Пропускаем служебные папки
                if os.path.isdir(full_path) and name.lower() in excluded_folders:
                    continue

                if os.path.isdir(full_path):
                    item = QListWidgetItem(name)
                    item.setData(Qt.ItemDataRole.UserRole, full_path)
                    item.setIcon(self.get_icon(full_path))
                    self.file_list.addItem(item)

            
            # Add files
            for name in sorted(items, key=lambda s: s.lower()):
                full_path = os.path.join(path, name)
                
                # Пропускаем файлы в папке bin (на всякий случай)
                if os.path.dirname(full_path).lower().endswith(os.path.sep + "bin"):
                    continue
                    
                if os.path.isfile(full_path):
                    item = QListWidgetItem(name)
                    item.setData(Qt.ItemDataRole.UserRole, full_path)
                    item.setIcon(self.get_icon(full_path))
                    self.file_list.addItem(item)
                        
        except PermissionError:
            self.show_error(self.tr("Permission denied"))
        except Exception as e:
            self.show_error(self.tr("Error loading directory: {}").format(str(e)))

    def filter_items(self):
        """Filter items based on search text"""
        search_text = self.search_edit.text().lower()
        
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item_text = item.text().lower().replace('[', '').replace(']', '')
            item.setHidden(search_text not in item_text and search_text != "")
    
    def on_item_double_clicked(self, item):
        """Handle double click on item"""
        path = item.data(Qt.ItemDataRole.UserRole)
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            self.current_file = path
            self.file_name_edit.setText(os.path.basename(path))
            if hasattr(self, 'mode') and self.mode == "open":
                self.accept_selection()
    
    def on_selection_changed(self):
        """Handle selection change"""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            path = item.data(Qt.ItemDataRole.UserRole)
            if os.path.isfile(path):
                self.current_file = path
                self.file_name_edit.setText(os.path.basename(path))
    
    def on_place_clicked(self, item):
        """Handle place selection"""
        path = item.data(Qt.ItemDataRole.UserRole)
        self.load_directory(path)
    
    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.load_directory(self.history[self.history_index])
    
    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_directory(self.history[self.history_index])
    
    def go_up(self):
        parent = os.path.dirname(self.directory)
        if parent and parent != self.directory:
            self.load_directory(parent)
    
    def go_home(self):
        self.load_directory(os.path.expanduser("root"))
    
    def navigate_to_path(self):
        path = self.path_edit.text()
        if os.path.exists(path) and os.path.isdir(path):
            self.load_directory(path)
        else:
            self.show_error(self.tr("Invalid path"))
    
    def update_nav_buttons(self):
        self.back_button.setEnabled(self.history_index > 0)
        self.forward_button.setEnabled(self.history_index < len(self.history) - 1)
    
    def load_current_directory(self):
        self.load_directory(self.directory)
    
    def accept_selection(self):
        """Accept the current selection"""
        if self.file_name_edit.text():
            selected_path = os.path.join(self.directory, self.file_name_edit.text())
            if os.path.exists(selected_path) or not hasattr(self, 'mode') or self.mode != "save":
                self.current_file = selected_path
                self.accept()
            else:
                self.current_file = selected_path
                self.accept()
        elif self.current_file:
            self.accept()
        else:
            self.show_error(self.tr("Please select a file or enter a file name"))
    
    def show_error(self, message):
        """Show error message"""
        self.file_name_edit.setPlaceholderText(message)
        self.file_name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: #ff6b6b;
                border: 1px solid #ff6b6b;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
    
    # Static methods for different dialog types
    @staticmethod
    def getOpenFileName(parent=None, caption="Open File", directory="", filter="All Files (*)", translator=None):
        dialog = CustomFileDialog(parent, caption, directory, filter, translator)
        dialog.mode = "open"
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return (dialog.current_file, filter)
        return ("", "")
    
    @staticmethod
    def getSaveFileName(parent=None, caption="Save File", directory="", filter="All Files (*)", translator=None):
        dialog = CustomFileDialog(parent, caption, directory, filter, translator)
        dialog.mode = "save"
        dialog.open_button.setText(dialog.tr("Save"))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return (dialog.current_file, filter)
        return ("", "")
    
    @staticmethod
    def getExistingDirectory(parent=None, caption="Select Directory", directory="", translator=None):
        dialog = CustomFileDialog(parent, caption, directory, "All Files (*)", translator)
        dialog.mode = "directory"
        dialog.open_button.setText(dialog.tr("Select"))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.current_file
        return ""