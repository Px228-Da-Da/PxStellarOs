# import os
# import platform
# import shutil
# from PyQt6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
#     QPushButton, QFileDialog, QLabel, QLineEdit, QFrame, QMenu,
#     QInputDialog, QMessageBox, QSplitter, QTextEdit
# )
# from PyQt6.QtCore import Qt, QSize, QPoint, QDateTime
# from PyQt6.QtGui import QIcon, QFont, QColor, QPalette


# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
# from dependencies import *

# class ExplorerWindow(DraggableResizableWindow):
#     def __init__(self, parent=None, window_name="Explorer", translator=None, lang_code="en"):
#         super().__init__(parent)
#         self.parent_window = parent
#         self.window_name = window_name
#         self.lang_code = lang_code
#         self.icon_cache = {}
#         self.folder_icon = None
#         self.history = []
#         self.history_index = -1
#         self.clipboard = []
#         self.clipboard_operation = None

#         # Set window properties
#         self.setWindowTitle(self.tr("File Explorer"))
#         self.setGeometry(200, 100, 800, 600)

#         # Create a container widget for our content
#         self.container = QWidget()
#         self.content_layout.addWidget(self.container)  # Add to DraggableResizableWindow's content area

#         # Main layout - applied to our container widget
#         main_layout = QVBoxLayout(self.container)
#         main_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.setSpacing(0)

#         # Toolbar (top panel)
#         toolbar = QHBoxLayout()
#         toolbar.setContentsMargins(5, 5, 5, 5)
#         toolbar.setSpacing(5)

#         # Navigation buttons with local icons
#         nav_buttons = QHBoxLayout()
#         nav_buttons.setSpacing(2)

#         # Path to icons folder
#         icons_dir = os.path.join("bin", "icons", "local_icons")
#         os.makedirs(icons_dir, exist_ok=True)

#         # Back button
#         self.back_button = QPushButton()
#         back_icon = QIcon(os.path.join(icons_dir, "back.png"))
#         self.back_button.setIcon(back_icon)
#         self.back_button.setFixedSize(32, 32)
#         self.back_button.clicked.connect(self.go_back)

#         # Forward button
#         self.forward_button = QPushButton()
#         forward_icon = QIcon(os.path.join(icons_dir, "forward.png"))
#         self.forward_button.setIcon(forward_icon)
#         self.forward_button.setFixedSize(32, 32)
#         self.forward_button.clicked.connect(self.go_forward)

#         # Up button
#         self.up_button = QPushButton()
#         up_icon = QIcon(os.path.join(icons_dir, "up.png"))
#         self.up_button.setIcon(up_icon)
#         self.up_button.setFixedSize(32, 32)
#         self.up_button.clicked.connect(self.go_up)

#         # Home button
#         self.home_button = QPushButton()
#         home_icon = QIcon(os.path.join(icons_dir, "home.png"))
#         self.home_button.setIcon(home_icon)
#         self.home_button.setFixedSize(32, 32)
#         self.home_button.clicked.connect(lambda: self.load_directory(os.path.expanduser(".")))

#         # Refresh button
#         self.refresh_button = QPushButton()
#         refresh_icon = QIcon(os.path.join(icons_dir, "refresh.png"))
#         self.refresh_button.setIcon(refresh_icon)
#         self.refresh_button.setFixedSize(32, 32)
#         self.refresh_button.clicked.connect(lambda: self.load_directory(self.current_path))

#         nav_buttons.addWidget(self.back_button)
#         nav_buttons.addWidget(self.forward_button)
#         nav_buttons.addWidget(self.up_button)
#         nav_buttons.addWidget(self.home_button)

#         toolbar.addLayout(nav_buttons)

#         # Path field
#         self.path_edit = Input()
#         self.path_edit.setPlaceholderText(self.tr("Enter path..."))
#         self.path_edit.returnPressed.connect(self.navigate_to_path)
#         self.path_edit.setMinimumHeight(32)
        
#         # Search field
#         self.search_edit = Input()
#         self.search_edit.setPlaceholderText(self.tr("Search..."))
#         self.search_edit.setMinimumHeight(32)
#         self.search_edit.setMaximumWidth(200)
#         self.search_edit.textChanged.connect(self.filter_items)
        
#         # Add a search button with icon
#         self.search_button = QPushButton()
#         search_icon = QIcon(os.path.join(icons_dir, "search.png"))  # Make sure you have search.png in your icons folder
#         self.search_button.setIcon(search_icon)
#         self.search_button.setFixedSize(32, 32)
#         self.search_button.clicked.connect(self.filter_items)
        
#         # Create a container for path and search fields
#         path_search_layout = QHBoxLayout()
#         path_search_layout.setSpacing(5)
#         path_search_layout.addWidget(self.path_edit, 1)
#         path_search_layout.addWidget(self.search_edit)
#         path_search_layout.addWidget(self.search_button)
        
#         toolbar.addLayout(path_search_layout, 1)  # Add the combined layout to toolbar

#         # Refresh button
#         toolbar.addWidget(self.refresh_button)

#         main_layout.addLayout(toolbar)

#         # Separator
#         separator = QFrame()
#         separator.setFrameShape(QFrame.Shape.HLine)
#         separator.setFrameShadow(QFrame.Shadow.Sunken)
#         main_layout.addWidget(separator)

#         # Main area with files and details panel
#         self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
#         # File list widget with white text
#         self.file_list = QListWidget()
#         self.file_list.setViewMode(QListWidget.ViewMode.IconMode)
#         self.file_list.setIconSize(QSize(45, 45))
#         self.file_list.setGridSize(QSize(150, 120))
#         self.file_list.setResizeMode(QListWidget.ResizeMode.Adjust)
#         self.file_list.setMovement(QListWidget.Movement.Static)
#         self.file_list.setWordWrap(True)
#         self.file_list.setUniformItemSizes(True)
#         self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
#         self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
#         self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
#         self.file_list.customContextMenuRequested.connect(self.show_context_menu)
#         self.file_list.itemSelectionChanged.connect(self.update_file_details)
#         self.file_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
#         self.file_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        
#         # Custom border styling
#         self.file_list.setStyleSheet("""
#             QListWidget {
#                 background-color: rgba(30, 30, 30, 180);
#                 border: 1px solid #444;
#                 border-radius: 4px;
#                 padding: 2px;
#             }
#             QListWidget::item {
#                 color: white;
#                 padding: 5px;
#                 border-radius: 3px;
#             }
#             QListWidget::item:hover {
#                 background-color: rgba(60, 60, 60, 150);
#             }
#             QListWidget::item:selected {
#                 background-color: rgba(75, 110, 175, 200);
#             }
#             QListWidget::item:selected:!active {
#                 background-color: rgba(65, 90, 150, 200);
#             }
#         """)

#         # Set white text color for file list
#         palette = self.file_list.palette()
#         palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
#         self.file_list.setPalette(palette)

#         # Details panel (right side)
#         self.details_panel = QWidget()
#         self.details_panel.setMinimumWidth(250)
#         self.details_panel.setMaximumWidth(350)
#         details_layout = QVBoxLayout(self.details_panel)
#         details_layout.setContentsMargins(10, 10, 10, 10)
        
#         # Preview/icon section
#         self.file_preview_label = QLabel()
#         self.file_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.file_preview_label.setFixedSize(100, 100)
        
#         # File details section
#         self.file_details_text = QTextEdit()
#         self.file_details_text.setReadOnly(True)
#         self.file_details_text.setStyleSheet("""
#             QTextEdit {
#                 background: transparent;
#                 border: none;
#                 color: white;
#                 font-size: 12px;
#             }
#         """)
        
#         # Toggle button for details panel
#         self.toggle_details_button = QPushButton(">")
#         self.toggle_details_button.setFixedSize(20, 60)
#         self.toggle_details_button.setCheckable(True)
#         self.toggle_details_button.setChecked(True)
#         self.toggle_details_button.clicked.connect(self.toggle_details_panel)
        
#         details_layout.addWidget(self.file_preview_label, 0, Qt.AlignmentFlag.AlignHCenter)
#         details_layout.addWidget(self.file_details_text, 1)
        
#         # Add widgets to splitter
#         self.main_splitter.addWidget(self.file_list)
#         self.main_splitter.addWidget(self.details_panel)
#         self.main_splitter.setStretchFactor(0, 3)
#         self.main_splitter.setStretchFactor(1, 1)
        
#         # Add the splitter to main layout instead of just file_list
#         main_layout.addWidget(self.main_splitter, 1)

#         # Status bar
#         self.status_bar = QHBoxLayout()
#         self.status_bar.setContentsMargins(5, 2, 5, 2)

#         self.status_label = QLabel("")
#         self.status_label.setFont(QFont("Noto Sans", 9))
#         self.status_bar.addWidget(self.status_label, 1)

#         main_layout.addLayout(self.status_bar)

#         # Load icons
#         self.load_custom_icons()

#         # Initialization
#         self.current_path = os.path.expanduser(".")  # Start directory
#         self.load_directory(self.current_path)

#     def filter_items(self):
#         """Filter files and folders based on search text"""
#         search_text = self.search_edit.text().lower()
        
#         for i in range(self.file_list.count()):
#             item = self.file_list.item(i)
#             item_text = item.text().lower()
#             item.setHidden(search_text not in item_text and search_text != "")


#     def toggle_details_panel(self):
#         """Toggle the visibility of the details panel"""
#         is_visible = self.toggle_details_button.isChecked()
#         self.details_panel.setVisible(is_visible)
#         self.toggle_details_button.setText(">" if is_visible else "<")

#     def update_file_details(self):
#         """Update the details panel with information about selected file"""
#         selected_items = self.file_list.selectedItems()
#         if not selected_items or len(selected_items) > 1:
#             self.file_preview_label.clear()
#             self.file_details_text.clear()
#             return
            
#         item = selected_items[0]
#         path = item.data(Qt.ItemDataRole.UserRole)
        
#         # Set preview icon
#         icon = self.get_icon(path)
#         self.file_preview_label.setPixmap(icon.pixmap(100, 100))
        
#         # Get file details
#         details = []
#         details.append(f"Name: {os.path.basename(path)}")
        
#         if os.path.isdir(path):
#             details.append("Type: File folder")
#             try:
#                 num_items = len(os.listdir(path))
#                 details.append(f"Items: {num_items}")
#             except:
#                 pass
#         else:
#             details.append(f"Type: {os.path.splitext(path)[1].upper()[1:] or 'File'}")
#             details.append(f"Size: {self.get_file_size(path)}")
            
#         # Add date modified
#         try:
#             mtime = os.path.getmtime(path)
#             dt = QDateTime.fromSecsSinceEpoch(int(mtime))
#             details.append(f"Modified: {dt.toString('yyyy-MM-dd hh:mm:ss')}")
#         except:
#             pass
            
#         # Add path
#         details.append(f"Path: {path}")
        
#         self.file_details_text.setPlainText("\n".join(details))

#     def get_file_size(self, path):
#         """Get human-readable file size"""
#         try:
#             size = os.path.getsize(path)
#             for unit in ['B', 'KB', 'MB', 'GB']:
#                 if size < 1024:
#                     return f"{size:.1f} {unit}"
#                 size /= 1024
#             return f"{size:.1f} TB"
#         except:
#             return "Unknown size"

#     def show_context_menu(self, position: QPoint):
#         menu = CustomMenu()
#         selected_items = self.file_list.selectedItems()

#         new_file_action = menu.addAction(self.tr("New File"))
#         new_file_action.triggered.connect(self.create_new_file)

#         new_folder_action = menu.addAction(self.tr("New Folder"))
#         new_folder_action.triggered.connect(self.create_new_folder)

#         menu.addSeparator()

#         if selected_items:
#             delete_action = menu.addAction(self.tr("Delete"))
#             delete_action.triggered.connect(self.delete_selected_items)

#             if len(selected_items) == 1:
#                 rename_action = menu.addAction(self.tr("Rename"))
#                 rename_action.triggered.connect(self.rename_item)

#                 open_notebook_action = menu.addAction(self.tr("Open in Notebook"))
#                 open_notebook_action.triggered.connect(lambda: self.open_in_notebook(selected_items[0]))

#             copy_action = menu.addAction(self.tr("Copy"))
#             copy_action.triggered.connect(lambda: self.copy_selected_items('copy'))

#             cut_action = menu.addAction(self.tr("Cut"))
#             cut_action.triggered.connect(lambda: self.copy_selected_items('cut'))

#             menu.addSeparator()

#         if self.clipboard:
#             paste_action = menu.addAction(self.tr("Paste"))
#             paste_action.triggered.connect(self.paste_items)

#         menu.exec(self.file_list.viewport().mapToGlobal(position))


#     def open_in_notebook(self, item: QListWidgetItem):
#         path = item.data(Qt.ItemDataRole.UserRole)
#         if not os.path.isfile(path):
#             StellarMessageBox.warning(self, self.tr("Error"), self.tr("Selected item is not a file"))
#             return

#         try:
#             notebook = None
            
#             # Проверяем, существует ли окно notebook в родительском окне
#             if hasattr(self.parent_window, 'open_windows'):
#                 notebook = self.parent_window.open_windows.get("notebook")
                
#                 # Если окно существует, но было закрыто, создаем новое
#                 if notebook is not None and not hasattr(notebook, 'isVisible'):
#                     notebook = None
#                     self.parent_window.open_windows["notebook"] = None
            
#             # Если notebook не существует, создаем новый экземпляр
#             if notebook is None:
#                 try:
#                     # Динамически импортируем модуль Notebook
#                     notebook_module = __import__("apps.local.notebook.notebook", fromlist=["NotebookWindow"])
#                     NotebookWindow = getattr(notebook_module, "NotebookWindow")
                    
#                     notebook = NotebookWindow(
#                         parent=self.parent_window,
#                         window_name="notebook",
#                         translator=self.parent_window.tr if hasattr(self.parent_window, 'tr') else None,
#                         lang_code=getattr(self.parent_window, 'current_language', 'en')
#                     )
                    
#                     # Сохраняем ссылку на notebook в родительском окне
#                     if hasattr(self.parent_window, 'open_windows'):
#                         self.parent_window.open_windows["notebook"] = notebook
#                 except Exception as e:
#                     StellarMessageBox.warning(self, self.tr("Error"), 
#                                            self.tr("Could not create notebook: {}").format(str(e)))
#                     return

#             # Загружаем файл и показываем notebook
#             if hasattr(notebook, 'load_file'):
#                 notebook.load_file(path)
#                 notebook.show()
#                 notebook.raise_()
#                 notebook.activateWindow()
                
#                 # Обновляем родительское окно, если возможно
#                 if hasattr(self.parent_window, 'switch_window'):
#                     self.parent_window.switch_window("notebook")
                    
#         except Exception as e:
#             StellarMessageBox.warning(self, self.tr("Error"), 
#                                     self.tr("Could not open file in notebook: {}").format(str(e)))


#     def create_new_file(self):
#         """Создает новый файл в текущей директории"""
#         text, ok = CustomInputDialog.getText(self, self.tr("New File"),
#                                       self.tr("Enter file name:"))
#         if ok and text:
#             file_path = os.path.join(self.current_path, text)
#             try:
#                 open(file_path, 'a').close()
#                 self.load_directory(self.current_path)
#                 self.status_label.setText(self.tr("File created: {}").format(file_path))
#             except Exception as e:
#                 StellarMessageBox.warning(self, self.tr("Error"),
#                                     self.tr("Could not create file: {}").format(str(e)))

#     def create_new_folder(self):
#         """Создает новую папку в текущей директории"""
#         text, ok = CustomInputDialog.getText(self, self.tr("New Folder"),
#                                       self.tr("Enter folder name:"))
#         if ok and text:
#             folder_path = os.path.join(self.current_path, text)
#             try:
#                 os.mkdir(folder_path)
#                 self.load_directory(self.current_path)
#                 self.status_label.setText(self.tr("Folder created: {}").format(folder_path))
#             except Exception as e:
#                 StellarMessageBox.warning(self, self.tr("Error"),
#                                     self.tr("Could not create folder: {}").format(str(e)))

#     def delete_selected_items(self):
#         """Удаляет выбранные файлы/папки"""
#         selected_items = self.file_list.selectedItems()
#         if not selected_items:
#             return

#         # Подтверждение удаления
#         reply = StellarMessageBox.question(
#             parent=self,
#             title=self.tr("Confirm Delete"),
#             message=self.tr("Delete {} selected items?").format(len(selected_items)),
#             buttons=StellarMessageBox.StandardButton.Yes | StellarMessageBox.StandardButton.No
#         )

#         if reply == StellarMessageBox.StandardButton.Yes:
#             for item in selected_items:
#                 path = item.data(Qt.ItemDataRole.UserRole)
#                 try:
#                     if os.path.isdir(path):
#                         shutil.rmtree(path)
#                     else:
#                         os.remove(path)
#                 except Exception as e:
#                     StellarMessageBox.warning(self, self.tr("Error"),
#                                         self.tr("Could not delete {}: {}").format(path, str(e)))

#             self.load_directory(self.current_path)
#             self.status_label.setText(self.tr("Deleted {} items").format(len(selected_items)))

#     def rename_item(self):
#         """Переименовывает выбранный файл/папку"""
#         selected_items = self.file_list.selectedItems()
#         if len(selected_items) != 1:
#             return

#         old_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
#         old_name = selected_items[0].text()

#         # Corrected call to getText with only 4 arguments
#         text, ok = CustomInputDialog.getText(
#             self,
#             self.tr("Rename"),
#             self.tr("Enter new name:"),
#             old_name  # Only passing the initial text as the 4th argument
#         )

#         if ok and text and text != old_name:
#             new_path = os.path.join(os.path.dirname(old_path), text)
#             try:
#                 os.rename(old_path, new_path)
#                 self.load_directory(self.current_path)
#                 self.status_label.setText(self.tr("Renamed to {}").format(text))
#             except Exception as e:
#                 StellarMessageBox.warning(self, self.tr("Error"),
#                                     self.tr("Could not rename: {}").format(str(e)))

#     def copy_selected_items(self, operation):
#         """Копирует или вырезает выбранные элементы"""
#         self.clipboard = []
#         selected_items = self.file_list.selectedItems()
#         if not selected_items:
#             return
#         for item in selected_items:
#             self.clipboard.append(item.data(Qt.ItemDataRole.UserRole))
#         self.clipboard_operation = operation
#         self.status_label.setText(self.tr("{} {} items to clipboard").format(operation.capitalize(), len(self.clipboard)))

#     def paste_items(self):
#         """Вставляет файлы/папки из буфера обмена в текущую директорию"""
#         if not self.clipboard:
#             return

#         for src_path in self.clipboard:
#             base_name = os.path.basename(src_path)
#             dest_path = os.path.join(self.current_path, base_name)

#             # Если такой файл/папка уже существует, добавляем суффикс
#             counter = 1
#             while os.path.exists(dest_path):
#                 name, ext = os.path.splitext(base_name)
#                 dest_path = os.path.join(self.current_path, f"{name}_copy{counter}{ext}")
#                 counter += 1

#             try:
#                 if os.path.isdir(src_path):
#                     shutil.copytree(src_path, dest_path)
#                 else:
#                     shutil.copy2(src_path, dest_path)

#                 # Если операция была вырезанием, удаляем исходники
#                 if self.clipboard_operation == 'cut':
#                     if os.path.isdir(src_path):
#                         shutil.rmtree(src_path)
#                     else:
#                         os.remove(src_path)

#             except Exception as e:
#                 StellarMessageBox.warning(self, self.tr("Error"),
#                                     self.tr("Could not paste {}: {}").format(src_path, str(e)))

#         self.clipboard = []
#         self.clipboard_operation = None
#         self.load_directory(self.current_path)
#         self.status_label.setText(self.tr("Items pasted"))

#     def navigate_to_path(self):
#         """Переход к указанному пути в поле ввода"""
#         path = self.path_edit.text()
#         if os.path.exists(path) and os.path.isdir(path):
#             self.load_directory(path)
#         else:
#             StellarMessageBox.warning(self, self.tr("Error"), self.tr("Invalid path"))

#     def load_directory(self, path):
#         """Загружает содержимое указанной директории в список"""
#         if not os.path.isdir(path):
#             return

#         try:
#             items = os.listdir(path)
#         except Exception as e:
#             StellarMessageBox.warning(self, self.tr("Error"), self.tr("Could not open directory: {}").format(str(e)))
#             return

#         self.file_list.clear()
#         self.current_path = path
#         self.path_edit.setText(path)

#         # Обновление истории
#         if not self.history or (self.history and self.history[self.history_index] != path):
#             self.history = self.history[:self.history_index + 1]
#             self.history.append(path)
#             self.history_index += 1
#         self.update_nav_buttons()

#         # Добавляем папки и файлы в QListWidget
#         for name in sorted(items, key=lambda s: s.lower()):
#             full_path = os.path.join(path, name)
#             item = QListWidgetItem(name)
#             item.setData(Qt.ItemDataRole.UserRole, full_path)
#             icon = self.get_icon(full_path)
#             item.setIcon(icon)
#             self.file_list.addItem(item)

#         self.status_label.setText(self.tr("Loaded directory: {}").format(path))

#     def update_nav_buttons(self):
#         self.back_button.setEnabled(self.history_index > 0)
#         self.forward_button.setEnabled(self.history_index < len(self.history) - 1)

#     def go_back(self):
#         if self.history_index > 0:
#             self.history_index -= 1
#             self.load_directory(self.history[self.history_index])

#     def go_forward(self):
#         if self.history_index < len(self.history) - 1:
#             self.history_index += 1
#             self.load_directory(self.history[self.history_index])

#     def go_up(self):
#         parent = os.path.dirname(self.current_path)
#         if parent and parent != self.current_path:
#             self.load_directory(parent)

#     def on_item_double_clicked(self, item: QListWidgetItem):
#         """Обработка двойного клика по элементу"""
#         path = item.data(Qt.ItemDataRole.UserRole)
#         if os.path.isdir(path):
#             self.load_directory(path)
#         else:
#             pass

#     def load_custom_icons(self):
#         """Загрузка пользовательских иконок"""
#         # Путь к иконкам файлов
#         self.icons_files_path = os.path.join("bin", "icons", "local_icons", "icons_files")

#         os.makedirs(self.icons_files_path, exist_ok=True)
        
#         # Загружаем единую иконку для папок
#         folder_icon_path = os.path.join(self.icons_files_path, "explorer.png")
#         if os.path.exists(folder_icon_path):
#             self.folder_icon = QIcon(folder_icon_path)
#         else:
#             # Если explorer.png не найден, используем системную иконку папки
#             self.folder_icon = QIcon.fromTheme("folder")
        
#         # Загружаем дефолтную иконку для файлов
#         self.default_file_icon = QIcon.fromTheme("text-x-generic")
        
#         # Загружаем иконку "not found"
#         not_found_icon = os.path.join(self.icons_files_path, "not.png")
#         if os.path.exists(not_found_icon):
#             self.not_found_icon = QIcon(not_found_icon)
#         else:
#             self.not_found_icon = self.default_file_icon


#     def get_icon(self, path):
#         """Получает иконку для файла/папки"""
#         if os.path.isdir(path):
#             return self.folder_icon or QIcon.fromTheme("folder") or QIcon()
        
#         # Получаем имя файла
#         filename = os.path.basename(path)
        
#         # Определяем расширение файла
#         if filename.startswith('.'):  # Файлы типа ".bashrc"
#             ext = filename
#         else:
#             ext = os.path.splitext(filename)[1].lower()
#             if not ext:  # Файлы без расширения
#                 ext = 'file'
        
#         # Проверяем кэш
#         if ext in self.icon_cache:
#             return self.icon_cache[ext]
        
#         # Пытаемся найти иконку в локальной папке
#         icon_name = ext[1:] if ext.startswith('.') else ext
#         icon_path = os.path.join(self.icons_files_path, f"{icon_name}.png")
        
#         if os.path.exists(icon_path):
#             icon = QIcon(icon_path)
#         else:
#             # Пробуем получить иконку из темы системы
#             theme_names = [
#                 f"text-x-{icon_name}",
#                 f"application-x-{icon_name}",
#                 icon_name,
#                 "text-x-generic"
#             ]
            
#             for name in theme_names:
#                 icon = QIcon.fromTheme(name)
#                 if not icon.isNull():
#                     break
#             else:
#                 icon = self.not_found_icon or self.default_file_icon or QIcon()
        
#         # Кэшируем иконку
#         self.icon_cache[ext] = icon
#         return icon

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


from PyQt6.QtCore import QMimeData, QUrl
from PyQt6.QtGui import QDrag

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QHBoxLayout, QPushButton, QCheckBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtCore import QObject, QEvent


class MouseNavFilter(QObject):
    def __init__(self, on_back, on_forward, parent=None):
        super().__init__(parent)
        self._on_back = on_back
        self._on_forward = on_forward

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            btn = event.button()

            # Основные коды (обычно так и будет)
            if btn in (Qt.MouseButton.BackButton, Qt.MouseButton.ExtraButton1):
                self._on_back()
                return True

            if btn in (Qt.MouseButton.ForwardButton, Qt.MouseButton.ExtraButton2):
                self._on_forward()
                return True

        return False

class OpenWithDialog(QDialog):
    CONFIG_PATH = "bin/sys/path/open_with.json"

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.selected_app = None
        self.setWindowTitle("Відкрити за допомогою")
        self.setFixedSize(400, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                color: #ddd;
                font-size: 14px;
            }
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #333;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 8px 10px;
                color: #eee;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #3a6df0;
                color: white;
            }
            QPushButton {
                background-color: #3a6df0;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #547bf7;
            }
            QCheckBox {
                color: #aaa;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        # === Заголовок ===
        lbl = QLabel(f"Виберіть програму для відкриття файлу:\n<b>{os.path.basename(file_path)}</b>")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        # === Список програм ===
        self.list = QListWidget()
        self.list.setIconSize(QSize(36, 36))
        layout.addWidget(self.list)

        # === Список доступных приложений ===
        apps = [
            {"name": "Python", "icon": "bin/icons/local_icons/apps/python.png"},
            {"name": "Visual Studio Code", "icon": "bin/icons/local_icons/apps/vscode.png"},
            {"name": "Sublime Text", "icon": "bin/icons/local_icons/apps/sublime.png"},
            {"name": "PxEditor", "icon": "bin/icons/local_icons/apps/text.png"},
        ]
        for app in apps:
            item = QListWidgetItem(QIcon(app["icon"]) if os.path.exists(app["icon"]) else QIcon(), app["name"])
            self.list.addItem(item)

        # === Чекбокс ===
        self.remember_check = QCheckBox("Завжди використовувати цю програму для цього типу файлів")
        layout.addWidget(self.remember_check)

        # === Кнопки ===
        buttons = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Скасувати")
        buttons.addWidget(self.ok_btn)
        buttons.addWidget(self.cancel_btn)
        layout.addLayout(buttons)

        # === Сигнали ===
        self.ok_btn.clicked.connect(self.accept_selection)
        self.cancel_btn.clicked.connect(self.reject)
        self.list.itemDoubleClicked.connect(self.accept_selection)
        self.list.currentItemChanged.connect(lambda: self.ok_btn.setEnabled(True))
        self.ok_btn.setEnabled(False)

        # === Завантаження конфігу ===
        self.config = self.load_config()

    # --- Обробка вибору ---
    def accept_selection(self):
        item = self.list.currentItem()
        if not item:
            return
        self.selected_app = item.text()
        ext = os.path.splitext(self.file_path)[1].lower()

        if self.remember_check.isChecked():
            self.config[ext] = self.selected_app
            self.save_config(self.config)

        self.accept()

    # --- Конфіг ---
    def load_config(self):
        try:
            if os.path.exists(self.CONFIG_PATH):
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_config(self, data):
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)



class ExplorerWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="Explorer", translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code
        self.parent_window = parent
        self.window_name = window_name
        self.icon_cache = {}
        self.folder_icon = None
        self.history = []
        self.history_index = -1
        self.clipboard = []
        self.clipboard_operation = None

        # === Window setup ===
        self.setWindowTitle(self.tr("File Explorer"))
        self.setGeometry(200, 100, 900, 600)

        # === Root container ===
        self.container = QWidget()
        self.content_layout.addWidget(self.container)
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Toolbar (top) ===
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 8, 8, 8)
        toolbar.setSpacing(6)

        icons_dir = os.path.join("bin", "icons", "local_icons")
        os.makedirs(icons_dir, exist_ok=True)

        # Navigation buttons
        nav_buttons = QHBoxLayout()
        for name in ["back", "forward", "up", "home", "refresh"]:
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            icon_path = os.path.join(icons_dir, f"{name}.png")
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
            setattr(self, f"{name}_button", btn)
            nav_buttons.addWidget(btn)

        self.back_button.clicked.connect(self.go_back)
        self.forward_button.clicked.connect(self.go_forward)
        self.up_button.clicked.connect(self.go_up)
        self.home_button.clicked.connect(lambda: self.load_directory(os.path.expanduser("root")))
        self.refresh_button.clicked.connect(lambda: self.load_directory(self.current_path))

        toolbar.addLayout(nav_buttons)

        # === Path field ===
        self.path_edit = Input(parent=self, translator=self.tr, lang_code=self.lang_code)
        self.path_edit.setPlaceholderText(self.tr("Enter path..."))
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        self.path_edit.setMinimumHeight(32)

        # === Search field ===
        self.search_edit = Input(parent=self, translator=self.tr, lang_code=self.lang_code)
        self.search_edit.setPlaceholderText(self.tr("Search..."))
        self.search_edit.setMinimumHeight(32)
        self.search_edit.setMaximumWidth(200)
        self.search_edit.textChanged.connect(self.filter_items)

        self.search_button = QPushButton()
        search_icon = QIcon(os.path.join(icons_dir, "search.png"))
        self.search_button.setIcon(search_icon)
        self.search_button.setFixedSize(32, 32)
        self.search_button.clicked.connect(self.filter_items)

        # Combine path + search
        path_layout = QHBoxLayout()
        path_layout.setSpacing(5)
        path_layout.addWidget(self.path_edit, 1)
        path_layout.addWidget(self.search_edit)
        path_layout.addWidget(self.search_button)

        toolbar.addLayout(path_layout, 1)
        toolbar.addWidget(self.refresh_button)
        main_layout.addLayout(toolbar)

        # === Splitter: sidebar | files | details ===
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(2)

        # === Left: Places list ===
        self.places_list = QListWidget()
        # self.places_list.setFixedWidth(200)
        self.places_list.itemClicked.connect(self.on_place_clicked)
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
        self.main_splitter.addWidget(self.places_list)
        self.setup_places()

        # === Center: File list ===
        self.file_list = QListWidget()
        self.file_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.file_list.setIconSize(QSize(48, 48))
        self.file_list.setGridSize(QSize(150, 120))
        self.file_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.file_list.setMovement(QListWidget.Movement.Static)
        self.file_list.setWordWrap(True)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.itemSelectionChanged.connect(self.update_file_details)
        self.file_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.file_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: none;
                color: white;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px;
            }
            QListWidget::item:hover {
                background-color: #2f2f2f;
            }
            QListWidget::item:selected {
                background-color: #3a6df0;
                border-radius: 6px;
            }
        """)
        self.file_list.setDragEnabled(True)
        self.file_list.setAcceptDrops(True)
        self.file_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.file_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        self.main_splitter.addWidget(self.file_list)

        # === Right: Details panel ===
        self.details_panel = QWidget()
        self.details_panel.setMinimumWidth(250)
        self.details_panel.setMaximumWidth(350)
        details_layout = QVBoxLayout(self.details_panel)
        details_layout.setContentsMargins(10, 10, 10, 10)
        details_layout.setSpacing(8)

        self.file_preview_label = QLabel()
        self.file_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_preview_label.setFixedSize(100, 100)

        self.file_details_text = CustomTextEdit_cmd(
            parent=self, translator=self.tr, lang_code=self.lang_code
        )
        self.file_details_text.setReadOnly(True)
        self.file_details_text.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 12px;
            }
        """)

        self.file_details_text.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.file_details_text.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))

        details_layout.addWidget(self.file_preview_label, 0, Qt.AlignmentFlag.AlignHCenter)
        details_layout.addWidget(self.file_details_text, 1)
        self.main_splitter.addWidget(self.details_panel)

        # Stretch factors
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 3)
        self.main_splitter.setStretchFactor(2, 1)
        main_layout.addWidget(self.main_splitter, 1)

        # === Status bar ===
        self.status_bar = QHBoxLayout()
        self.status_bar.setContentsMargins(5, 3, 5, 3)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #bbb; font-size: 11px;")
        self.status_bar.addWidget(self.status_label, 1)
        main_layout.addLayout(self.status_bar)

        # === Load icons and initialize ===
        self.load_custom_icons()
        self.current_path = os.path.expanduser("root")
        self.load_directory(self.current_path)

        self.setup_focus_activation(self.container)

        # === Windows 11 visual polish ===
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: "Segoe UI";
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QLineEdit {
                background-color: #252525;
                border: 1px solid #444;
                border-radius: 6px;
                padding-left: 8px;
                height: 28px;
            }
        """)

        # === Hotkeys ===
        self.setup_shortcuts()
                # === Mouse back/forward buttons ===
        self._mouse_nav_filter = MouseNavFilter(self.go_back, self.go_forward, self)

        # Вешаем на окно и ключевые зоны, чтобы работало независимо от фокуса
        self.installEventFilter(self._mouse_nav_filter)
        self.container.installEventFilter(self._mouse_nav_filter)

        # Главное: QListWidget часто принимает клики через viewport()
        self.file_list.installEventFilter(self._mouse_nav_filter)
        self.file_list.viewport().installEventFilter(self._mouse_nav_filter)

        self.places_list.installEventFilter(self._mouse_nav_filter)
        self.places_list.viewport().installEventFilter(self._mouse_nav_filter)

        # Дополнительно можно повесить на поля ввода
        self.path_edit.installEventFilter(self._mouse_nav_filter)
        self.search_edit.installEventFilter(self._mouse_nav_filter)

        # И на панель деталей
        self.details_panel.installEventFilter(self._mouse_nav_filter)



    def open_path(self, path: str):
        """Открывает конкретный путь в проводнике"""
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            StellarMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Path does not exist or is not a directory: {}").format(path)
            )

    # def setup_places(self):
    #     """Setup common places + disks"""
    #     self.places_list.clear()

    #     places = [
    #         (self.tr("Desktop"), os.path.expanduser("root/user/desk")),
    #         (self.tr("Documents"), os.path.expanduser("root/user/Documents")),
    #         (self.tr("Downloads"), os.path.expanduser("root/user/download")),
    #         (self.tr("Images"), os.path.expanduser("root/user/images")),
    #     ]

    #     for name, path in places:
    #         if os.path.exists(path):
    #             item = QListWidgetItem(f"📁 {name}")
    #             item.setData(Qt.ItemDataRole.UserRole, path)
    #             self.places_list.addItem(item)

    #     # === Add drives (Windows-like “This PC”) ===
    #     drives = self.get_drives()
    #     if drives:
    #         # self.places_list.addItem("───────────────")
    #         for drive in drives:
    #             item = QListWidgetItem(f"💽 {drive}")
    #             item.setData(Qt.ItemDataRole.UserRole, drive)
    #             self.places_list.addItem(item)
    def get_drive_label(self, path):
        """Возвращает имя диска: C, D, / и т.д."""
        import platform
        if platform.system() == "Windows":
            return path.strip("\\").replace(":", "")
        else:
            base = os.path.basename(path)
            return base if base else "/"

    def setup_places(self):
        """Setup common places + disks with Windows-like style"""
        import psutil
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

        self.places_list.clear()

        # --- Основные папки ---
        places = [
            (self.tr("Desktop"), os.path.expanduser("root/user/desk")),
            (self.tr("Documents"), os.path.expanduser("root/user/Documents")),
            (self.tr("Downloads"), os.path.expanduser("root/user/download")),
            (self.tr("Images"), os.path.expanduser("root/user/images")),
        ]

        for name, path in places:
            if os.path.exists(path):
                item = QListWidgetItem(f"📁 {name}")
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.places_list.addItem(item)

        # --- Раздел: Диски ---
        drives = self.get_drives()
        if not drives:
            return

        for drive in drives:
            try:
                usage = psutil.disk_usage(drive)
                total_gb = usage.total / (1024 ** 3)
                free_gb = usage.free / (1024 ** 3)
                percent_used = int(usage.percent)

                # --- Внешний вид блока диска ---
                widget = QWidget()
                layout = QVBoxLayout(widget)
                # layout.setContentsMargins(-1, -1, -1, -1)
                # layout.setSpacing(7)

                # Имя диска (с меткой)
                drive_name = self.get_drive_label(drive)
                label_title = QLabel(f"({drive_name})")
                label_title.setStyleSheet("color: #f0f0f0; font-weight: 500; font-size: 12px;")

                # Прогресс-бар
                progress = QProgressBar()
                progress.setRange(0, 100)
                progress.setValue(percent_used)
                progress.setTextVisible(False)
                # progress.setFixedHeight(14)
                progress.setStyleSheet("""
                    QProgressBar {
                        background-color: #3a3a3a;
                    }
                    QProgressBar::chunk {
                        background-color: #3399ff;
                    }
                """)

                # Текст "свободно из"
                label_size = QLabel(f"{free_gb:.1f} ГБ вільно з {total_gb:.1f} ГБ")
                label_size.setStyleSheet("color: #b0b0b0; font-size: 11px;")

                layout.addWidget(label_title)
                layout.addWidget(progress)
                layout.addWidget(label_size)

                # Добавляем в список
                item = QListWidgetItem()
                item.setSizeHint(widget.sizeHint())
                item.setData(Qt.ItemDataRole.UserRole, drive)
                self.places_list.addItem(item)
                self.places_list.setItemWidget(item, widget)

            except Exception as e:
                print(f"[EXPLORER] Не вдалося отримати розмір для {drive}: {e}")



    def get_drives(self):
        """Повертає список доступних дисків / точок монтування"""
        drives = []

        if platform.system() == "Windows":
            import string
            from ctypes import windll
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(f"{letter}:\\")
                bitmask >>= 1
        else:
            # --- Linux / macOS ---
            try:
                mounts = set()
                # читаем список точек монтирования
                with open("/proc/mounts", "r") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 2:
                            mount_point = parts[1]
                            # фильтруем системные и временные
                            if mount_point.startswith("/media") or mount_point.startswith("/mnt") or mount_point == "/":
                                if os.path.exists(mount_point):
                                    mounts.add(mount_point)

                # добавляем найденные точки
                drives.extend(sorted(mounts))

                # если ничего не найдено — добавляем хотя бы корень
                if not drives:
                    drives.append("/")
            except Exception as e:
                print(f"[EXPLORER] Не вдалося отримати диски: {e}")
                drives = ["/"]

        return drives


    def on_place_clicked(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and os.path.exists(path):
            self.load_directory(path)


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

    # def update_file_details(self):
    #     """Update the details panel with information about selected file"""
    #     selected_items = self.file_list.selectedItems()
    #     if not selected_items or len(selected_items) > 1:
    #         self.file_preview_label.clear()
    #         self.file_details_text.clear()
    #         return
            
    #     item = selected_items[0]
    #     path = item.data(Qt.ItemDataRole.UserRole)
        
    #     # Set preview icon
    #     icon = self.get_icon(path)
    #     self.file_preview_label.setPixmap(icon.pixmap(100, 100))
        
    #     # Get file details
    #     details = []
    #     details.append(f"{self.tr('Name')}: {os.path.basename(path)}")
        
    #     if os.path.isdir(path):
    #         details.append(f"{self.tr('Type')}: {self.tr('File folder')}")
    #         try:
    #             num_items = len(os.listdir(path))
    #             details.append(f"{self.tr('Items')}: {num_items}")
    #         except:
    #             pass
    #     else:
    #         file_type = os.path.splitext(path)[1].upper()[1:] or self.tr('File')
    #         details.append(f"{self.tr('Type')}: {file_type}")
    #         details.append(f"{self.tr('Size')}: {self.get_file_size(path)}")
            
    #     # Add date modified
    #     try:
    #         mtime = os.path.getmtime(path)
    #         dt = QDateTime.fromSecsSinceEpoch(int(mtime))
    #         details.append(f"{self.tr('Modified')}: {dt.toString('yyyy-MM-dd hh:mm:ss')}")
    #     except:
    #         pass
            
    #     # Add path
    #     details.append(f"{self.tr('Path')}: {path}")
        
    #     self.file_details_text.setPlainText("\n".join(details))
    def update_file_details(self):
        """Оновлює панель деталей при виборі файлу"""
        selected_items = self.file_list.selectedItems()
        if not selected_items or len(selected_items) > 1:
            self.file_preview_label.clear()
            self.file_details_text.clear()
            return

        item = selected_items[0]
        path = item.data(Qt.ItemDataRole.UserRole)

        # === Якщо файл — це зображення ===
        image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
        ext = os.path.splitext(path)[1].lower()

        if os.path.isfile(path) and ext in image_extensions:
            try:
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # === Автоматичне масштабування під розмір панелі ===
                    available_width = self.file_preview_label.width()
                    available_height = self.file_preview_label.height()

                    # Якщо розміри ще не визначені, ставимо запасні
                    if available_width < 50 or available_height < 50:
                        available_width, available_height = 250, 250

                    scaled_pixmap = pixmap.scaled(
                        available_width,
                        available_height,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.file_preview_label.setPixmap(scaled_pixmap)
                    self.file_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.file_preview_label.setScaledContents(False)  # зберігає пропорції
                else:
                    icon = self.get_icon(path)
                    self.file_preview_label.setPixmap(icon.pixmap(100, 100))
            except Exception as e:
                print(f"[EXPLORER] Помилка попереднього перегляду зображення: {e}")
                icon = self.get_icon(path)
                self.file_preview_label.setPixmap(icon.pixmap(100, 100))

        else:
            # --- Якщо не зображення: просто іконка ---
            icon = self.get_icon(path)
            self.file_preview_label.setPixmap(icon.pixmap(100, 100))

        # === Деталі файлу ===
        details = []
        details.append(f"{self.tr('Name')}: {os.path.basename(path)}")

        if os.path.isdir(path):
            details.append(f"{self.tr('Type')}: {self.tr('File folder')}")
            try:
                num_items = len(os.listdir(path))
                details.append(f"{self.tr('Items')}: {num_items}")
            except:
                pass
        else:
            file_type = os.path.splitext(path)[1].upper()[1:] or self.tr('File')
            details.append(f"{self.tr('Type')}: {file_type}")
            details.append(f"{self.tr('Size')}: {self.get_file_size(path)}")

        # --- Дата зміни ---
        try:
            mtime = os.path.getmtime(path)
            dt = QDateTime.fromSecsSinceEpoch(int(mtime))
            details.append(f"{self.tr('Modified')}: {dt.toString('yyyy-MM-dd hh:mm:ss')}")
        except:
            pass

        # --- Повний шлях ---
        details.append(f"{self.tr('Path')}: {path}")

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
        menu = CustomContextMenu()
        selected_items = self.file_list.selectedItems()

        # Основные действия
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

            copy_action = menu.addAction(self.tr("Copy"))
            copy_action.triggered.connect(lambda: self.copy_selected_items('copy'))

            cut_action = menu.addAction(self.tr("Cut"))
            cut_action.triggered.connect(lambda: self.copy_selected_items('cut'))

            menu.addSeparator()

        # Новая кнопка: Open in CMD для папок
        if len(selected_items) == 1 and os.path.isdir(selected_items[0].data(Qt.ItemDataRole.UserRole)):
            open_cmd_action = menu.addAction(self.tr("Open in CMD"))
            open_cmd_action.triggered.connect(lambda: self.open_in_cmd(selected_items[0]))

        # Paste если есть что вставить
        if self.clipboard:
            paste_action = menu.addAction(self.tr("Paste"))
            paste_action.triggered.connect(self.paste_items)

        # Open in Notebook / VSCode только для файлов в самом низу меню
        if len(selected_items) == 1 and os.path.isfile(selected_items[0].data(Qt.ItemDataRole.UserRole)):
            menu.addSeparator()
            open_notebook_action = menu.addAction(self.tr("Open in Notebook"))
            open_notebook_action.triggered.connect(lambda: self.open_in_notebook(selected_items[0]))

            open_vscode_action = menu.addAction(self.tr("Open in VsCode"))
            open_vscode_action.triggered.connect(lambda: self.open_in_vscode(selected_items[0]))

        menu.exec(self.file_list.viewport().mapToGlobal(position))


    def open_in_cmd(self, item: QListWidgetItem):
        """Открывает CMD в выбранной папке"""
        path = item.data(Qt.ItemDataRole.UserRole)
        if not os.path.isdir(path):
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Selected item is not a folder"))
            return

        try:
            cmd_window = None
            
            # Проверяем, существует ли окно CMD в родительском окне
            if hasattr(self.parent_window, 'open_windows'):
                cmd_window = self.parent_window.open_windows.get("cmd")
                
                # Если окно существует, но было закрыто, создаем новое
                if cmd_window is not None and not hasattr(cmd_window, 'isVisible'):
                    cmd_window = None
                    self.parent_window.open_windows["cmd"] = None
            
            # Если CMD не существует, создаем новый экземпляр
            if cmd_window is None:
                try:
                    # Динамически импортируем модуль CMD
                    cmd_module = __import__("apps.local.cmd.cmd", fromlist=["CmdWindow"])
                    CmdWindow = getattr(cmd_module, "CmdWindow")
                    
                    cmd_window = CmdWindow(
                        parent=self.parent_window,
                        window_name="CMD",
                        translator=self.parent_window.tr if hasattr(self.parent_window, 'tr') else None,
                        lang_code=getattr(self.parent_window, 'current_language', 'en')
                    )
                    
                    # Сохраняем ссылку на CMD в родительском окне
                    if hasattr(self.parent_window, 'open_windows'):
                        self.parent_window.open_windows["cmd"] = cmd_window
                except Exception as e:
                    StellarMessageBox.warning(self, self.tr("Error"), 
                                           self.tr("Could not create CMD window: {}").format(str(e)))
                    return

            # Меняем рабочую директорию в терминале и показываем окно
            if hasattr(cmd_window, 'terminal') and hasattr(cmd_window.terminal, 'tabs'):
                current_tab = cmd_window.terminal.tabs.currentWidget()
                if current_tab and hasattr(current_tab, 'process'):
                    # Отправляем команду смены директории в процесс терминала
                    change_dir_command = f"cd /d \"{path}\"\n" if platform.system() == "Windows" else f"cd \"{path}\"\n"
                    current_tab.process.write(change_dir_command.encode("utf-8"))
                    
                    # Показываем текущую директорию
                    if platform.system() == "Windows":
                        current_tab.process.write(b"cd\n")
                    else:
                        current_tab.process.write(b"pwd\n")
            
            cmd_window.show()
            cmd_window.raise_()
            cmd_window.activateWindow()
            
            # Обновляем родительское окно, если возможно
            if hasattr(self.parent_window, 'switch_window'):
                self.parent_window.switch_window("cmd")
                
        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"), 
                                    self.tr("Could not open CMD in folder: {}").format(str(e)))

    def open_in_vscode(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if not os.path.isfile(path):
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Selected item is not a file"))
            return

        try:
            vscode = None

            # Проверяем, существует ли окно vscode в родительском окне
            if hasattr(self.parent_window, 'open_windows'):
                vscode = self.parent_window.open_windows.get("Vscode")

                # Проверяем, существует ли окно и видимо ли оно
                if vscode is not None:
                    # Если окно было закрыто (уничтожено), создаем новое
                    try:
                        # Простая проверка - пытаемся получить свойство окна
                        _ = vscode.windowTitle()
                    except RuntimeError:
                        # Окно было уничтожено
                        vscode = None
                        self.parent_window.open_windows["Vscode"] = None

            # Если vscode не существует, создаем новый экземпляр
            if vscode is None:
                try:
                    # Динамически импортируем модуль Vscode
                    vscode_module = __import__("apps.local.Vscode.Vscode", fromlist=["VscodeWindow"])
                    VscodeWindow = getattr(vscode_module, "VscodeWindow")

                    vscode = VscodeWindow(
                        parent=self.parent_window,
                        window_name="VSCode",
                        translator=getattr(self.parent_window, 'tr', None),
                        lang_code=getattr(self.parent_window, 'current_language', 'en')
                    )

                    # Сохраняем ссылку на vscode в родительском окне
                    if hasattr(self.parent_window, 'open_windows'):
                        self.parent_window.open_windows["Vscode"] = vscode
                        
                    print(f"[EXPLORER] Создано новое окно VSCode")
                    
                except Exception as e:
                    StellarMessageBox.warning(
                        self,
                        self.tr("Error"),
                        self.tr("Could not create VSCode window: {}").format(str(e))
                    )
                    return

            # Загружаем файл в VSCode
            try:
                # Показываем окно
                vscode.show()
                vscode.raise_()
                vscode.activateWindow()
                
                # Загружаем файл - используем метод open_file_by_path если он есть, иначе create_tab
                if hasattr(vscode, 'open_file_by_path'):
                    vscode.open_file_by_path(path)
                    print(f"[EXPLORER] Файл открыт через open_file_by_path: {path}")
                elif hasattr(vscode, 'create_tab'):
                    # Используем существующий метод create_tab
                    vscode.create_tab(title=os.path.basename(path), path=path)
                    print(f"[EXPLORER] Файл открыт через create_tab: {path}")
                else:
                    # Альтернативный способ - напрямую загружаем в редактор
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                        language = vscode.detect_language(path) if hasattr(vscode, 'detect_language') else "plaintext"
                        vscode.set_text(content, language)
                        vscode.current_file = path
                        print(f"[EXPLORER] Файл загружен напрямую: {path}")
                    except Exception as read_error:
                        StellarMessageBox.warning(
                            self,
                            self.tr("Error"),
                            self.tr("Could not read file: {}").format(str(read_error))
                        )
                        return

                # Обновляем родительское окно, если возможно
                if hasattr(self.parent_window, 'switch_window'):
                    self.parent_window.switch_window("Vscode")
                    
                print(f"[EXPLORER] Файл успешно открыт в VSCode: {path}")

            except Exception as load_error:
                StellarMessageBox.warning(
                    self,
                    self.tr("Error"),
                    self.tr("Could not load file in VSCode: {}").format(str(load_error))
                )
                return

        except Exception as e:
            StellarMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Could not open file in VSCode: {}").format(str(e))
            )
            import traceback
            print(f"[EXPLORER] Full error: {traceback.format_exc()}")


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

        # Служебные папки, которые скрываем
        excluded_folders = {"bin", ".git", "__pycache__"}
        # Добавляем папки и файлы в QListWidget, игнорируя служебные
        for name in sorted(items, key=lambda s: s.lower()):
            if name.lower() in excluded_folders:
                continue  # пропускаем служебные папки

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

    # def on_item_double_clicked(self, item: QListWidgetItem):
    #     """Обработка двойного клика по файлу"""
    #     path = item.data(Qt.ItemDataRole.UserRole)
    #     if os.path.isdir(path):
    #         self.load_directory(path)
    #         return

    #     ext = os.path.splitext(path)[1].lower()
    #     config_path = "bin/sys/path/open_with.json"

    #     # Загружаем конфиг
    #     import json
    #     if os.path.exists(config_path):
    #         try:
    #             with open(config_path, "r", encoding="utf-8") as f:
    #                 config = json.load(f)
    #         except:
    #             config = {}
    #     else:
    #         config = {}

    #     # Если расширение уже ассоциировано — открываем напрямую
    #     if ext in config:
    #         app = config[ext]
    #         print(f"[OPEN] Відкрито {path} через {app}")
    #         self.open_file_with_app(path, app)
    #         return

    #     # Иначе показываем окно выбора
    #     dlg = OpenWithDialog(path, self)
    #     if dlg.exec():
    #         app = dlg.selected_app
    #         if app:
    #             self.open_file_with_app(path, app)

    # def open_file_with_app(self, path, app):
    #     """Имитирует открытие файла через выбранное приложение"""
    #     print(f"[OPEN] {path} відкрито через {app}")
    #     # Здесь ты можешь добавить логику:
    #     # if app == "Visual Studio Code": self.open_in_vscode(...)
    #     # if app == "Python": self.open_in_notebook(...)
    #     # и т.д.


    def on_item_double_clicked(self, item: QListWidgetItem): # ТОПОМ НАДО СДЕЛАТЬ ↑ open_file_with_app on_item_double_clicked
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


    def dragEnterEvent(self, event):
        """Приймаємо перетягування файлів/папок"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Дозволяє рух перетягуваних елементів"""
        event.acceptProposedAction()

    def dropEvent(self, event):
        """Обробляє скидання файлів/папок"""
        if not event.mimeData().hasUrls():
            return

        target_dir = self.current_path
        for url in event.mimeData().urls():
            source_path = url.toLocalFile()
            if not os.path.exists(source_path):
                continue

            try:
                dest_path = os.path.join(target_dir, os.path.basename(source_path))
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, dest_path)
            except Exception as e:
                QMessageBox.warning(self, "Помилка копіювання", f"Не вдалося перемістити {source_path}:\n{e}")

        self.load_directory(self.current_path)
        event.acceptProposedAction()

    def startDrag(self, supportedActions):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        mime_data = QMimeData()
        urls = []
        for item in selected_items:
            path = item.data(Qt.ItemDataRole.UserRole)
            if os.path.exists(path):
                urls.append(QUrl.fromLocalFile(os.path.abspath(path)))

        mime_data.setUrls(urls)
        drag = QDrag(self.file_list)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)

    # def setup_shortcuts(self):
    #     """Назначает горячие клавиши (как в Windows Explorer)"""
    #     from PyQt6.QtGui import QShortcut, QKeySequence

    #     # Навигация
    #     QShortcut(QKeySequence("Alt+Left"), self, activated=self.go_back)
    #     QShortcut(QKeySequence("Backspace"), self, activated=self.go_back)
    #     QShortcut(QKeySequence("Alt+Right"), self, activated=self.go_forward)
    #     QShortcut(QKeySequence("Alt+Up"), self, activated=self.go_up)
    #     QShortcut(QKeySequence("F5"), self, activated=lambda: self.load_directory(self.current_path))

    #     # Файловые операции
    #     QShortcut(QKeySequence("Ctrl+Shift+N"), self, activated=self.create_new_folder)
    #     QShortcut(QKeySequence("Delete"), self, activated=self.delete_selected_items)
    #     QShortcut(QKeySequence("F2"), self, activated=self.rename_item)

    #     # Буфер обмена
    #     QShortcut(QKeySequence("Ctrl+C"), self, activated=lambda: self.copy_selected_items('copy'))
    #     QShortcut(QKeySequence("Ctrl+X"), self, activated=lambda: self.copy_selected_items('cut'))
    #     QShortcut(QKeySequence("Ctrl+V"), self, activated=self.paste_items)

    #     # Выделение
    #     QShortcut(QKeySequence("Ctrl+A"), self, activated=lambda: self.file_list.selectAll())

    #     # Домашняя директория
    #     QShortcut(QKeySequence("Alt+Home"), self, activated=lambda: self.load_directory(os.path.expanduser("root")))

    #     print("[EXPLORER] Hotkeys initialized.")
    def setup_shortcuts(self):
        """Назначает горячие клавиши (по возможности независимые от раскладки)"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        from PyQt6.QtCore import Qt
        import os

        # === Навигация ===
        # Alt + Left
        self.sc_back = QShortcut(
            QKeySequence(Qt.KeyboardModifier.AltModifier | Qt.Key.Key_Left),
            self,
            activated=self.go_back
        )

        # Backspace
        self.sc_backspace = QShortcut(
            QKeySequence(Qt.Key.Key_Backspace),
            self,
            activated=self.go_back
        )

        # Alt + Right
        self.sc_forward = QShortcut(
            QKeySequence(Qt.KeyboardModifier.AltModifier | Qt.Key.Key_Right),
            self,
            activated=self.go_forward
        )

        # Alt + Up
        self.sc_up = QShortcut(
            QKeySequence(Qt.KeyboardModifier.AltModifier | Qt.Key.Key_Up),
            self,
            activated=self.go_up
        )

        # F5 — обновить
        self.sc_refresh = QShortcut(
            QKeySequence(Qt.Key.Key_F5),
            self,
            activated=lambda: self.load_directory(self.current_path)
        )

        # Домашняя директория (Alt + Home)
        self.sc_home = QShortcut(
            QKeySequence(Qt.KeyboardModifier.AltModifier | Qt.Key.Key_Home),
            self,
            activated=lambda: self.load_directory(os.path.expanduser("root"))
        )

        # === Файловые операции ===
        # Ctrl + Shift + N — новая папка
        self.sc_new_folder = QShortcut(
            QKeySequence(
                Qt.KeyboardModifier.ControlModifier
                | Qt.KeyboardModifier.ShiftModifier
                | Qt.Key.Key_N
            ),
            self,
            activated=self.create_new_folder
        )

        # Delete — удалить
        self.sc_delete = QShortcut(
            QKeySequence(Qt.Key.Key_Delete),
            self,
            activated=self.delete_selected_items
        )

        # F2 — Переименовать
        self.sc_rename = QShortcut(
            QKeySequence(Qt.Key.Key_F2),
            self,
            activated=self.rename_item
        )

        # === Буфер обмена (стандартные шорткаты, не зависят от раскладки) ===

        # Copy
        self.sc_copy = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Copy),
            self,
            activated=lambda: self.copy_selected_items("copy")
        )

        # Cut
        self.sc_cut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Cut),
            self,
            activated=lambda: self.copy_selected_items("cut")
        )

        # Paste
        self.sc_paste = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Paste),
            self,
            activated=self.paste_items
        )

        # Select All
        self.sc_select_all = QShortcut(
            QKeySequence(QKeySequence.StandardKey.SelectAll),
            self,
            activated=lambda: self.file_list.selectAll()
        )

        print("[EXPLORER] Hotkeys initialized (layout-friendly).")
