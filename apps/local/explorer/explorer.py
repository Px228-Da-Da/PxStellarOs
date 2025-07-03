import os
import platform
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QLabel, QLineEdit, QFrame, QMenu,
    QInputDialog, QMessageBox, QSplitter, QTextEdit
)
from PyQt6.QtCore import Qt, QSize, QPoint, QDateTime
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class ExplorerWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="Explorer", translator=None, lang_code="en"):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name
        self.lang_code = lang_code
        self.icon_cache = {}
        self.folder_icon = None
        self.history = []
        self.history_index = -1
        self.clipboard = []
        self.clipboard_operation = None

        # Set window properties
        self.setWindowTitle(self.tr("File Explorer"))
        self.setGeometry(200, 100, 800, 600)

        # Create a container widget for our content
        self.container = QWidget()
        self.content_layout.addWidget(self.container)  # Add to DraggableResizableWindow's content area

        # Main layout - applied to our container widget
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar (top panel)
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(5, 5, 5, 5)
        toolbar.setSpacing(5)

        # Navigation buttons with local icons
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
        self.back_button.clicked.connect(self.go_back)

        # Forward button
        self.forward_button = QPushButton()
        forward_icon = QIcon(os.path.join(icons_dir, "forward.png"))
        self.forward_button.setIcon(forward_icon)
        self.forward_button.setFixedSize(32, 32)
        self.forward_button.clicked.connect(self.go_forward)

        # Up button
        self.up_button = QPushButton()
        up_icon = QIcon(os.path.join(icons_dir, "up.png"))
        self.up_button.setIcon(up_icon)
        self.up_button.setFixedSize(32, 32)
        self.up_button.clicked.connect(self.go_up)

        # Home button
        self.home_button = QPushButton()
        home_icon = QIcon(os.path.join(icons_dir, "home.png"))
        self.home_button.setIcon(home_icon)
        self.home_button.setFixedSize(32, 32)
        self.home_button.clicked.connect(lambda: self.load_directory(os.path.expanduser(".")))

        # Refresh button
        self.refresh_button = QPushButton()
        refresh_icon = QIcon(os.path.join(icons_dir, "refresh.png"))
        self.refresh_button.setIcon(refresh_icon)
        self.refresh_button.setFixedSize(32, 32)
        self.refresh_button.clicked.connect(lambda: self.load_directory(self.current_path))

        nav_buttons.addWidget(self.back_button)
        nav_buttons.addWidget(self.forward_button)
        nav_buttons.addWidget(self.up_button)
        nav_buttons.addWidget(self.home_button)

        toolbar.addLayout(nav_buttons)

        # Path field
        self.path_edit = Input()
        self.path_edit.setPlaceholderText(self.tr("Enter path..."))
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        self.path_edit.setMinimumHeight(32)
        
        # Search field
        self.search_edit = Input()
        self.search_edit.setPlaceholderText(self.tr("Search..."))
        self.search_edit.setMinimumHeight(32)
        self.search_edit.setMaximumWidth(200)
        self.search_edit.textChanged.connect(self.filter_items)
        
        # Add a search button with icon
        self.search_button = QPushButton()
        search_icon = QIcon(os.path.join(icons_dir, "search.png"))  # Make sure you have search.png in your icons folder
        self.search_button.setIcon(search_icon)
        self.search_button.setFixedSize(32, 32)
        self.search_button.clicked.connect(self.filter_items)
        
        # Create a container for path and search fields
        path_search_layout = QHBoxLayout()
        path_search_layout.setSpacing(5)
        path_search_layout.addWidget(self.path_edit, 1)
        path_search_layout.addWidget(self.search_edit)
        path_search_layout.addWidget(self.search_button)
        
        toolbar.addLayout(path_search_layout, 1)  # Add the combined layout to toolbar

        # Refresh button
        toolbar.addWidget(self.refresh_button)

        main_layout.addLayout(toolbar)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # Main area with files and details panel
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # File list widget with white text
        self.file_list = QListWidget()
        self.file_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.file_list.setIconSize(QSize(45, 45))
        self.file_list.setGridSize(QSize(150, 120))
        self.file_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.file_list.setMovement(QListWidget.Movement.Static)
        self.file_list.setWordWrap(True)
        self.file_list.setUniformItemSizes(True)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.itemSelectionChanged.connect(self.update_file_details)
        self.file_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.file_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        
        # Custom border styling
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

        # Details panel (right side)
        self.details_panel = QWidget()
        self.details_panel.setMinimumWidth(250)
        self.details_panel.setMaximumWidth(350)
        details_layout = QVBoxLayout(self.details_panel)
        details_layout.setContentsMargins(10, 10, 10, 10)
        
        # Preview/icon section
        self.file_preview_label = QLabel()
        self.file_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_preview_label.setFixedSize(100, 100)
        
        # File details section
        self.file_details_text = QTextEdit()
        self.file_details_text.setReadOnly(True)
        self.file_details_text.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 12px;
            }
        """)
        
        # Toggle button for details panel
        self.toggle_details_button = QPushButton(">")
        self.toggle_details_button.setFixedSize(20, 60)
        self.toggle_details_button.setCheckable(True)
        self.toggle_details_button.setChecked(True)
        self.toggle_details_button.clicked.connect(self.toggle_details_panel)
        
        details_layout.addWidget(self.file_preview_label, 0, Qt.AlignmentFlag.AlignHCenter)
        details_layout.addWidget(self.file_details_text, 1)
        
        # Add widgets to splitter
        self.main_splitter.addWidget(self.file_list)
        self.main_splitter.addWidget(self.details_panel)
        self.main_splitter.setStretchFactor(0, 3)
        self.main_splitter.setStretchFactor(1, 1)
        
        # Add the splitter to main layout instead of just file_list
        main_layout.addWidget(self.main_splitter, 1)

        # Status bar
        self.status_bar = QHBoxLayout()
        self.status_bar.setContentsMargins(5, 2, 5, 2)

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Noto Sans", 9))
        self.status_bar.addWidget(self.status_label, 1)

        main_layout.addLayout(self.status_bar)

        # Load icons
        self.load_custom_icons()

        # Initialization
        self.current_path = os.path.expanduser(".")  # Start directory
        self.load_directory(self.current_path)

    def filter_items(self):
        """Filter files and folders based on search text"""
        search_text = self.search_edit.text().lower()
        
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item_text = item.text().lower()
            item.setHidden(search_text not in item_text and search_text != "")


    def toggle_details_panel(self):
        """Toggle the visibility of the details panel"""
        is_visible = self.toggle_details_button.isChecked()
        self.details_panel.setVisible(is_visible)
        self.toggle_details_button.setText(">" if is_visible else "<")

    def update_file_details(self):
        """Update the details panel with information about selected file"""
        selected_items = self.file_list.selectedItems()
        if not selected_items or len(selected_items) > 1:
            self.file_preview_label.clear()
            self.file_details_text.clear()
            return
            
        item = selected_items[0]
        path = item.data(Qt.ItemDataRole.UserRole)
        
        # Set preview icon
        icon = self.get_icon(path)
        self.file_preview_label.setPixmap(icon.pixmap(100, 100))
        
        # Get file details
        details = []
        details.append(f"Name: {os.path.basename(path)}")
        
        if os.path.isdir(path):
            details.append("Type: File folder")
            try:
                num_items = len(os.listdir(path))
                details.append(f"Items: {num_items}")
            except:
                pass
        else:
            details.append(f"Type: {os.path.splitext(path)[1].upper()[1:] or 'File'}")
            details.append(f"Size: {self.get_file_size(path)}")
            
        # Add date modified
        try:
            mtime = os.path.getmtime(path)
            dt = QDateTime.fromSecsSinceEpoch(int(mtime))
            details.append(f"Modified: {dt.toString('yyyy-MM-dd hh:mm:ss')}")
        except:
            pass
            
        # Add path
        details.append(f"Path: {path}")
        
        self.file_details_text.setPlainText("\n".join(details))

    def get_file_size(self, path):
        """Get human-readable file size"""
        try:
            size = os.path.getsize(path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "Unknown size"

    def show_context_menu(self, position: QPoint):
        menu = CustomMenu()
        selected_items = self.file_list.selectedItems()

        new_file_action = menu.addAction(self.tr("New File"))
        new_file_action.triggered.connect(self.create_new_file)

        new_folder_action = menu.addAction(self.tr("New Folder"))
        new_folder_action.triggered.connect(self.create_new_folder)

        menu.addSeparator()

        if selected_items:
            delete_action = menu.addAction(self.tr("Delete"))
            delete_action.triggered.connect(self.delete_selected_items)

            if len(selected_items) == 1:
                rename_action = menu.addAction(self.tr("Rename"))
                rename_action.triggered.connect(self.rename_item)

                open_notebook_action = menu.addAction(self.tr("Open in Notebook"))
                open_notebook_action.triggered.connect(lambda: self.open_in_notebook(selected_items[0]))

            copy_action = menu.addAction(self.tr("Copy"))
            copy_action.triggered.connect(lambda: self.copy_selected_items('copy'))

            cut_action = menu.addAction(self.tr("Cut"))
            cut_action.triggered.connect(lambda: self.copy_selected_items('cut'))

            menu.addSeparator()

        if self.clipboard:
            paste_action = menu.addAction(self.tr("Paste"))
            paste_action.triggered.connect(self.paste_items)

        menu.exec(self.file_list.viewport().mapToGlobal(position))


    def open_in_notebook(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if not os.path.isfile(path):
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Selected item is not a file"))
            return

        try:
            notebook = None
            
            # Проверяем, существует ли окно notebook в родительском окне
            if hasattr(self.parent_window, 'open_windows'):
                notebook = self.parent_window.open_windows.get("notebook")
                
                # Если окно существует, но было закрыто, создаем новое
                if notebook is not None and not hasattr(notebook, 'isVisible'):
                    notebook = None
                    self.parent_window.open_windows["notebook"] = None
            
            # Если notebook не существует, создаем новый экземпляр
            if notebook is None:
                try:
                    # Динамически импортируем модуль Notebook
                    notebook_module = __import__("apps.local.notebook.notebook", fromlist=["NotebookWindow"])
                    NotebookWindow = getattr(notebook_module, "NotebookWindow")
                    
                    notebook = NotebookWindow(
                        parent=self.parent_window,
                        window_name="notebook",
                        translator=self.parent_window.tr if hasattr(self.parent_window, 'tr') else None,
                        lang_code=getattr(self.parent_window, 'current_language', 'en')
                    )
                    
                    # Сохраняем ссылку на notebook в родительском окне
                    if hasattr(self.parent_window, 'open_windows'):
                        self.parent_window.open_windows["notebook"] = notebook
                except Exception as e:
                    StellarMessageBox.warning(self, self.tr("Error"), 
                                           self.tr("Could not create notebook: {}").format(str(e)))
                    return

            # Загружаем файл и показываем notebook
            if hasattr(notebook, 'load_file'):
                notebook.load_file(path)
                notebook.show()
                notebook.raise_()
                notebook.activateWindow()
                
                # Обновляем родительское окно, если возможно
                if hasattr(self.parent_window, 'switch_window'):
                    self.parent_window.switch_window("notebook")
                    
        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"), 
                                    self.tr("Could not open file in notebook: {}").format(str(e)))


    def create_new_file(self):
        """Создает новый файл в текущей директории"""
        text, ok = CustomInputDialog.getText(self, self.tr("New File"),
                                      self.tr("Enter file name:"))
        if ok and text:
            file_path = os.path.join(self.current_path, text)
            try:
                open(file_path, 'a').close()
                self.load_directory(self.current_path)
                self.status_label.setText(self.tr("File created: {}").format(file_path))
            except Exception as e:
                StellarMessageBox.warning(self, self.tr("Error"),
                                    self.tr("Could not create file: {}").format(str(e)))

    def create_new_folder(self):
        """Создает новую папку в текущей директории"""
        text, ok = CustomInputDialog.getText(self, self.tr("New Folder"),
                                      self.tr("Enter folder name:"))
        if ok and text:
            folder_path = os.path.join(self.current_path, text)
            try:
                os.mkdir(folder_path)
                self.load_directory(self.current_path)
                self.status_label.setText(self.tr("Folder created: {}").format(folder_path))
            except Exception as e:
                StellarMessageBox.warning(self, self.tr("Error"),
                                    self.tr("Could not create folder: {}").format(str(e)))

    def delete_selected_items(self):
        """Удаляет выбранные файлы/папки"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        # Подтверждение удаления
        reply = StellarMessageBox.question(
            parent=self,
            title=self.tr("Confirm Delete"),
            message=self.tr("Delete {} selected items?").format(len(selected_items)),
            buttons=StellarMessageBox.StandardButton.Yes | StellarMessageBox.StandardButton.No
        )

        if reply == StellarMessageBox.StandardButton.Yes:
            for item in selected_items:
                path = item.data(Qt.ItemDataRole.UserRole)
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception as e:
                    StellarMessageBox.warning(self, self.tr("Error"),
                                        self.tr("Could not delete {}: {}").format(path, str(e)))

            self.load_directory(self.current_path)
            self.status_label.setText(self.tr("Deleted {} items").format(len(selected_items)))

    def rename_item(self):
        """Переименовывает выбранный файл/папку"""
        selected_items = self.file_list.selectedItems()
        if len(selected_items) != 1:
            return

        old_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
        old_name = selected_items[0].text()

        # Corrected call to getText with only 4 arguments
        text, ok = CustomInputDialog.getText(
            self,
            self.tr("Rename"),
            self.tr("Enter new name:"),
            old_name  # Only passing the initial text as the 4th argument
        )

        if ok and text and text != old_name:
            new_path = os.path.join(os.path.dirname(old_path), text)
            try:
                os.rename(old_path, new_path)
                self.load_directory(self.current_path)
                self.status_label.setText(self.tr("Renamed to {}").format(text))
            except Exception as e:
                StellarMessageBox.warning(self, self.tr("Error"),
                                    self.tr("Could not rename: {}").format(str(e)))

    def copy_selected_items(self, operation):
        """Копирует или вырезает выбранные элементы"""
        self.clipboard = []
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.clipboard.append(item.data(Qt.ItemDataRole.UserRole))
        self.clipboard_operation = operation
        self.status_label.setText(self.tr("{} {} items to clipboard").format(operation.capitalize(), len(self.clipboard)))

    def paste_items(self):
        """Вставляет файлы/папки из буфера обмена в текущую директорию"""
        if not self.clipboard:
            return

        for src_path in self.clipboard:
            base_name = os.path.basename(src_path)
            dest_path = os.path.join(self.current_path, base_name)

            # Если такой файл/папка уже существует, добавляем суффикс
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(base_name)
                dest_path = os.path.join(self.current_path, f"{name}_copy{counter}{ext}")
                counter += 1

            try:
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)

                # Если операция была вырезанием, удаляем исходники
                if self.clipboard_operation == 'cut':
                    if os.path.isdir(src_path):
                        shutil.rmtree(src_path)
                    else:
                        os.remove(src_path)

            except Exception as e:
                StellarMessageBox.warning(self, self.tr("Error"),
                                    self.tr("Could not paste {}: {}").format(src_path, str(e)))

        self.clipboard = []
        self.clipboard_operation = None
        self.load_directory(self.current_path)
        self.status_label.setText(self.tr("Items pasted"))

    def navigate_to_path(self):
        """Переход к указанному пути в поле ввода"""
        path = self.path_edit.text()
        if os.path.exists(path) and os.path.isdir(path):
            self.load_directory(path)
        else:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Invalid path"))

    def load_directory(self, path):
        """Загружает содержимое указанной директории в список"""
        if not os.path.isdir(path):
            return

        try:
            items = os.listdir(path)
        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Could not open directory: {}").format(str(e)))
            return

        self.file_list.clear()
        self.current_path = path
        self.path_edit.setText(path)

        # Обновление истории
        if not self.history or (self.history and self.history[self.history_index] != path):
            self.history = self.history[:self.history_index + 1]
            self.history.append(path)
            self.history_index += 1
        self.update_nav_buttons()

        # Добавляем папки и файлы в QListWidget
        for name in sorted(items, key=lambda s: s.lower()):
            full_path = os.path.join(path, name)
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, full_path)
            icon = self.get_icon(full_path)
            item.setIcon(icon)
            self.file_list.addItem(item)

        self.status_label.setText(self.tr("Loaded directory: {}").format(path))

    def update_nav_buttons(self):
        self.back_button.setEnabled(self.history_index > 0)
        self.forward_button.setEnabled(self.history_index < len(self.history) - 1)

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.load_directory(self.history[self.history_index])

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_directory(self.history[self.history_index])

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.load_directory(parent)

    def on_item_double_clicked(self, item: QListWidgetItem):
        """Обработка двойного клика по элементу"""
        path = item.data(Qt.ItemDataRole.UserRole)
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            pass

    def load_custom_icons(self):
        """Загрузка пользовательских иконок"""
        # Путь к иконкам файлов
        self.icons_files_path = os.path.join("bin", "icons", "local_icons", "icons_files")

        os.makedirs(self.icons_files_path, exist_ok=True)
        
        # Загружаем единую иконку для папок
        folder_icon_path = os.path.join(self.icons_files_path, "explorer.png")
        if os.path.exists(folder_icon_path):
            self.folder_icon = QIcon(folder_icon_path)
        else:
            # Если explorer.png не найден, используем системную иконку папки
            self.folder_icon = QIcon.fromTheme("folder")
        
        # Загружаем дефолтную иконку для файлов
        self.default_file_icon = QIcon.fromTheme("text-x-generic")
        
        # Загружаем иконку "not found"
        not_found_icon = os.path.join(self.icons_files_path, "not.png")
        if os.path.exists(not_found_icon):
            self.not_found_icon = QIcon(not_found_icon)
        else:
            self.not_found_icon = self.default_file_icon


    def get_icon(self, path):
        """Получает иконку для файла/папки"""
        if os.path.isdir(path):
            return self.folder_icon or QIcon.fromTheme("folder") or QIcon()
        
        # Получаем имя файла
        filename = os.path.basename(path)
        
        # Определяем расширение файла
        if filename.startswith('.'):  # Файлы типа ".bashrc"
            ext = filename
        else:
            ext = os.path.splitext(filename)[1].lower()
            if not ext:  # Файлы без расширения
                ext = 'file'
        
        # Проверяем кэш
        if ext in self.icon_cache:
            return self.icon_cache[ext]
        
        # Пытаемся найти иконку в локальной папке
        icon_name = ext[1:] if ext.startswith('.') else ext
        icon_path = os.path.join(self.icons_files_path, f"{icon_name}.png")
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Пробуем получить иконку из темы системы
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
        
        # Кэшируем иконку
        self.icon_cache[ext] = icon
        return icon

