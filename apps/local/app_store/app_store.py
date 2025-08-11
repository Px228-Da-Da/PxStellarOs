import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QFrame, QTabWidget, QScrollArea, QGridLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QIcon, QPixmap


import zipfile
import shutil


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

class App_storeWindow(DraggableResizableWindow):
    def __init__(self, parent=None, window_name="App Store", translator=None, lang_code="en"):
        super().__init__(parent)
        self.parent_window = parent
        self.window_name = window_name
        self.lang_code = lang_code
        self.app_cards = []
        self.card_width = 180  # Fixed card width
        self.card_height = 220  # Fixed card height
        self.spacing = 20  # Spacing between cards

        # Set window properties
        self.setWindowTitle(self.tr("App Store"))
        self.setGeometry(200, 100, 800, 600)

        # Create a container widget for our content
        self.container = QWidget()
        self.content_layout.addWidget(self.container)

        # Main layout - УСТАНОВИТЕ MARGINS И SPACING
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Важно!
        self.main_layout.setSpacing(0)  # Важно!

        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # ПРИМЕНЯЕМ СТИЛЬ К QTabBar НАПРЯМУЮ
        tab_bar_style = """
            QTabBar {
                background: transparent;
                spacing: 4px;
            }
            
            QTabBar::tab {
                background: rgba(50, 50, 50, 200);
                color: white;
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #444;
                margin-right: 2px;
                min-width: 100px;
            }
            
            QTabBar::tab:selected {
                background: rgba(70, 70, 70, 220);
                border-bottom-color: transparent;
            }
            
            QTabBar::tab:hover {
                background: rgba(60, 60, 60, 210);
            }
            
            QTabBar::tab:selected:hover {
                background: rgba(80, 80, 80, 230);
            }
        """
        
        pane_style = """
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 4px;
                background: rgba(40, 40, 40, 220);
                margin-top: 4px;
                position: absolute;
                top: -1px;
            }
        """
        
        # Применяем стили отдельно
        self.tab_widget.tabBar().setStyleSheet(tab_bar_style)
        self.tab_widget.setStyleSheet(pane_style)


        # Create tabs
        self.create_local_apps_tab()
        self.create_updates_tab()

        # Add tab bar to title widget
        self.add_title_widget(self.tab_widget.tabBar())
        
        # Add tab widget content to main layout
        self.main_layout.addWidget(self.tab_widget)

    def create_local_apps_tab(self):
        """Create the Local Apps tab with improved tab styling"""
        self.local_apps_tab = QWidget()
        self.tab_widget.addTab(self.local_apps_tab, self.tr("Local Apps"))

        # Main layout for the tab - растягиваем на весь доступный размер
        tab_layout = QVBoxLayout(self.local_apps_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)  # Убираем margins
        tab_layout.setSpacing(0)  # Убираем spacing

        # Create scroll area for apps
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        
        # Style the scroll area - растягиваем на всю вкладку
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        # Container for apps - основной контейнер с карточками
        self.apps_container = QWidget()
        self.apps_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setWidget(self.apps_container)
        
        # Добавляем scroll area в layout с растягиванием
        tab_layout.addWidget(self.scroll_area)

        # Use QGridLayout для карточек
        self.apps_layout = QGridLayout(self.apps_container)
        self.apps_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)
        self.apps_layout.setSpacing(self.spacing)
        self.apps_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # ... остальной код метода без изменений ...

        # Load apps from config file
        config_path = os.path.join("root", "bin", "install_apps.config")
        
        try:
            with open(config_path, 'r') as f:
                content = f.read()
                apps = [line.split(':')[0].strip().strip('"') for line in content.split(',') if line.strip()]
                
                for app_name in apps:
                    clean_name = app_name.replace('.None', '')
                    # Пропускаем создание карточки для App_store
                    if clean_name.lower() != "app_store":
                        self.add_app_card(clean_name)
                    
            # После загрузки всех карточек обновляем их расположение
            self.update_apps_layout()
                    
        except Exception as e:
            print(f"Error loading apps: {e}")

        # Установим обработчик изменения размера
        self.scroll_area.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle resize events for both tabs"""
        if obj == self.scroll_area and event.type() == QEvent.Type.Resize:
            self.update_apps_layout()
        elif obj == self.updates_scroll_area and event.type() == QEvent.Type.Resize:
            self.update_updates_layout()
        return super().eventFilter(obj, event)


    def update_apps_layout(self):
        """Обновляет расположение карточек при изменении размера"""
        if not self.app_cards:
            return

        # Получаем текущую ширину области прокрутки
        scroll_width = self.scroll_area.viewport().width()
        
        # Рассчитываем количество карточек в строке
        cards_per_row = max(1, (scroll_width - self.spacing) // (self.card_width + self.spacing))
        
        # Очищаем текущий layout
        for i in reversed(range(self.apps_layout.count())):
            item = self.apps_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        
        # Перераспределяем карточки по новому layout
        row, col = 0, 0
        for card in self.app_cards:
            if card.parent() is None:  # Проверяем, не был ли виджет удален
                self.apps_layout.addWidget(card, row, col)
                col += 1
                if col >= cards_per_row:
                    col = 0
                    row += 1

        # Обновляем размер контейнера
        rows = (len(self.app_cards) + cards_per_row - 1) // cards_per_row
        container_width = cards_per_row * (self.card_width + self.spacing) + self.spacing
        container_height = rows * (self.card_height + self.spacing) + self.spacing
        self.apps_container.setMinimumSize(container_width, container_height)

    def load_local_apps(self):
        """Load local apps from the install_apps.config file"""
        config_path = os.path.join("root", "bin", "install_apps.config")
        
        try:
            with open(config_path, 'r') as f:
                content = f.read()
                apps = [line.split(':')[0].strip().strip('"') for line in content.split(',') if line.strip()]
                
                for app_name in apps:
                    clean_name = app_name.replace('.None', '')
                    # Пропускаем создание карточки для App_store
                    if clean_name.lower() != "app_store":
                        self.add_app_card(clean_name)
                    
            # После загрузки всех карточек обновляем их расположение
            self.update_apps_layout()
                    
        except Exception as e:
            print(f"Error loading apps: {e}")

    def add_app_card(self, app_name):
        """Add an app card with proper alignment and clean design"""
        # Create card widget
        card = QWidget()
        card.setFixedSize(self.card_width, self.card_height)
        card.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 180);
                border-radius: 12px;
            }
            QWidget:hover {
                background-color: rgba(50, 50, 50, 200);
            }
        """)

        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(2, 2)
        card.setGraphicsEffect(shadow)

        # Main card layout
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        # Icon label
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(80, 80)
        icon_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                padding: 0;
            }
        """)
        
        # Load and scale icon
        icon_path = os.path.join("bin", "icons", "local_icons", "inons_apps", app_name, "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
        else:
            pixmap = QPixmap(os.path.join("bin", "icons", "local_icons", "default_app.png"))
        
        pixmap = pixmap.scaled(
            64, 64, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        icon_label.setPixmap(pixmap)
        card_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # App name label
        name_label = QLabel(app_name.capitalize())
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: 500;
                padding: 0;
                border: none;
                background: transparent;
            }
        """)
        name_label.setFixedWidth(self.card_width - 30)
        name_label.setWordWrap(True)
        card_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Button container - теперь с вертикальным расположением
        btn_container = QWidget()
        btn_container.setStyleSheet("background: transparent;")
        btn_layout = QVBoxLayout(btn_container)  # Изменено на QVBoxLayout
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)  # Расстояние между кнопками

        # Open button
        open_btn = QPushButton(self.tr("Open"))
        open_btn.setFixedSize(100, 32)  # Немного шире для лучшего вида
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(74, 110, 169, 200);
                color: white;
                border-radius: 8px;
                border: none;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(90, 126, 185, 220);
            }
            QPushButton:pressed {
                background-color: rgba(58, 94, 153, 200);
            }
        """)
        open_btn.clicked.connect(lambda _, app=app_name: self.open_app(app))
        btn_layout.addWidget(open_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Reload button
        reload_btn = QPushButton(self.tr("Reload"))
        reload_btn.setFixedSize(100, 32)
        reload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reload_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(169, 74, 74, 200);
                color: white;
                border-radius: 8px;
                border: none;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(185, 90, 90, 220);
            }
            QPushButton:pressed {
                background-color: rgba(153, 58, 58, 200);
            }
        """)
        reload_btn.clicked.connect(lambda _, app=app_name: self.reload_app(app))
        btn_layout.addWidget(reload_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Add button container to card
        card_layout.addWidget(btn_container, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.app_cards.append(card)
        self.apps_layout.addWidget(card)

    def reload_app(self, app_name):
        """Перезагружает приложение с подхватом обновлённого кода"""
        import importlib
        try:
            # Закрываем старое окно
            if hasattr(self.parent_window, 'open_windows') and self.parent_window.open_windows.get(app_name):
                self.parent_window.open_windows[app_name].close()
                self.parent_window.open_windows[app_name] = None

            # Перезагружаем модуль
            module_name = f"apps.local.{app_name}.{app_name}"
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                __import__(module_name)

            # Создаём новое окно
            AppClass = getattr(sys.modules[module_name], f"{app_name.capitalize()}Window")
            app_window = AppClass(
                parent=self.parent_window,
                window_name=app_name,
                translator=self.parent_window.tr if hasattr(self.parent_window, 'tr') else None,
                lang_code=getattr(self.parent_window, 'current_language', 'en')
            )
            self.parent_window.open_windows[app_name] = app_window
            app_window.show()
        except Exception as e:
            print(f"Ошибка при перезагрузке {app_name}: {e}")


    def open_app(self, app_name):
        """Open the selected application"""
        try:
            # Check if app window already exists
            app_window = None
            if hasattr(self.parent_window, 'open_windows'):
                app_window = self.parent_window.open_windows.get(app_name)
                
                if app_window is not None and not hasattr(app_window, 'isVisible'):
                    app_window = None
                    self.parent_window.open_windows[app_name] = None
            
            # If app window doesn't exist, create it
            if app_window is None:
                try:
                    app_module = __import__(f"apps.local.{app_name}.{app_name}", fromlist=[f"{app_name.capitalize()}Window"])
                    AppWindow = getattr(app_module, f"{app_name.capitalize()}Window")
                    
                    app_window = AppWindow(
                        parent=self.parent_window,
                        window_name=app_name,
                        translator=self.parent_window.tr if hasattr(self.parent_window, 'tr') else None,
                        lang_code=getattr(self.parent_window, 'current_language', 'en')
                    )
                    
                    if hasattr(self.parent_window, 'open_windows'):
                        self.parent_window.open_windows[app_name] = app_window
                except Exception as e:
                    StellarMessageBox.warning(self, self.tr("Error"), 
                                           self.tr("Could not open {}: {}").format(app_name, str(e)))
                    return

            # Show the app window
            if app_window:
                app_window.show()
                app_window.raise_()
                app_window.activateWindow()
                
                if hasattr(self.parent_window, 'switch_window'):
                    self.parent_window.switch_window(app_name)
                    
        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"), 
                                    self.tr("Could not open application: {}").format(str(e)))


    def create_updates_tab(self):
        """Create the Updates tab that shows apps with available updates"""
        self.updates_tab = QWidget()
        self.tab_widget.addTab(self.updates_tab, self.tr("Updates"))
        
        # Main layout for the tab - растягиваем на весь размер
        tab_layout = QVBoxLayout(self.updates_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)  # Убираем margins
        tab_layout.setSpacing(0)  # Убираем spacing

        # Create scroll area for update cards
        self.updates_scroll_area = QScrollArea()
        self.updates_scroll_area.setWidgetResizable(True)
        self.updates_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.updates_scroll_area.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.updates_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        # Container for update cards
        self.updates_container = QWidget()
        self.updates_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updates_scroll_area.setWidget(self.updates_container)
        
        # Добавляем scroll area в layout с растягиванием
        tab_layout.addWidget(self.updates_scroll_area)

        # Layout for update cards
        self.updates_layout = QGridLayout(self.updates_container)
        self.updates_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)
        self.updates_layout.setSpacing(self.spacing)
        self.updates_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # ... остальной код метода без изменений ...

        # Check for updates button
        self.check_updates_btn = QPushButton(self.tr("Check for Updates"))
        self.check_updates_btn.setFixedHeight(35)
        self.check_updates_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #6b8eca, stop:1 #5a7eb9);
                color: white;
                border-radius: 6px;
                border: 1px solid #3a5e99;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #7c9fdb, stop:1 #6b8eca);
            }
        """)
        self.check_updates_btn.clicked.connect(self.check_for_updates)
        tab_layout.addWidget(self.check_updates_btn)

        # Установим обработчик изменения размера
        self.updates_scroll_area.installEventFilter(self)

    def check_for_updates(self):
        """Check for available updates for all installed apps"""
        # print("=== Starting update check ===")
        
        # Clear previous update cards
        for i in reversed(range(self.updates_layout.count())):
            widget = self.updates_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Get list of installed apps
        config_path = os.path.join("root", "bin", "install_apps.config")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                apps = [line.split(':')[0].strip().strip('"') for line in content.split(',') if line.strip()]
                
                # print(f"Found {len(apps)} installed apps")
                
                for app_name in apps:
                    clean_name = app_name.replace('.None', '')
                    if clean_name.lower() != "app_store":
                        self.check_app_update(clean_name)
                        
            # Update layout after loading all update cards
            self.update_updates_layout()
                    
        except Exception as e:
            print(f"Error checking updates: {str(e)}")
        
        # print("=== Update check completed ===")

    def check_app_update(self, app_name):
        """Check if update is available for specific app"""
        try:
            # Get local version
            local_version_path = os.path.join("apps", "local", app_name, "version.json")
            if not os.path.exists(local_version_path):
                print(f"No version.json found for {app_name}")
                return
                
            with open(local_version_path, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
                local_version = local_data.get("version", "0.0.0")
                download_url = local_data.get("download_url", "")
                
            # Extract repo info from download_url (assuming GitHub URL)
            if "github.com" in download_url:
                # Handle different GitHub URL formats
                if download_url.endswith("/archive/refs/heads/main.zip"):
                    repo_url = download_url.replace("/archive/refs/heads/main.zip", "")
                elif download_url.endswith("/archive/main.zip"):
                    repo_url = download_url.replace("/archive/main.zip", "")
                else:
                    print(f"Unsupported GitHub URL format for {app_name}")
                    return
                    
                raw_version_url = f"{repo_url}/raw/main/version.json"
                
                # Debug print
                # print(f"Checking update for {app_name}:")
                # print(f"Local version: {local_version}")
                # print(f"Remote version URL: {raw_version_url}")
                
                # Download remote version file
                import urllib.request
                try:
                    req = urllib.request.Request(
                        raw_version_url,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    with urllib.request.urlopen(req) as response:
                        if response.status == 200:
                            remote_data = json.loads(response.read().decode('utf-8'))
                            remote_version = remote_data.get("version", "0.0.0")
                            
                            # print(f"Remote version: {remote_version}")
                            
                            # Compare versions
                            if self.compare_versions(local_version, remote_version) < 0:
                                print(f"Update available for {app_name}: {local_version} -> {remote_version}")
                                self.add_update_card(app_name, local_version, remote_version, download_url)
                            else:
                                print(f"No update needed for {app_name}")
                        else:
                            print(f"Failed to fetch version for {app_name}: HTTP {response.status}")
                            
                except urllib.error.HTTPError as e:
                    print(f"HTTP Error checking update for {app_name}: {e.code} {e.reason}")
                except Exception as e:
                    print(f"Error checking update for {app_name}: {str(e)}")
                    
        except Exception as e:
            print(f"Error processing {app_name} version: {str(e)}")

    def compare_versions(self, v1, v2):
        """Compare two version strings (format X.Y.Z)"""
        def version_to_tuple(v):
            try:
                return tuple(map(int, (v.split('.') + ['0', '0'])[:3]))
            except:
                return (0, 0, 0)
        
        v1_tuple = version_to_tuple(v1)
        v2_tuple = version_to_tuple(v2)
        
        print(f"Comparing versions: {v1_tuple} vs {v2_tuple}")
        
        if v1_tuple < v2_tuple:
            return -1
        elif v1_tuple > v2_tuple:
            return 1
        return 0

    def add_update_card(self, app_name, current_version, new_version, download_url):
        """Add an update card to the updates tab"""
        # Create update card widget
        card = QWidget()
        card.setFixedSize(self.card_width, self.card_height)
        card.setStyleSheet("""
            QWidget {
                background-color: rgba(60, 50, 50, 200);
                border-radius: 10px;
                border: 1px solid #755;
            }
            QWidget:hover {
                background-color: rgba(70, 60, 60, 220);
                border: 1px solid #966;
            }
        """)

        # Card layout
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # App icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(64, 64)
        icon_label.setScaledContents(True)
        
        icon_path = os.path.join("bin", "icons", "local_icons", "inons_apps", app_name, "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
        else:
            pixmap = QPixmap(os.path.join("bin", "icons", "local_icons", "default_app.png"))
        
        icon_label.setPixmap(pixmap)
        card_layout.addWidget(icon_label)

        # App name
        name_label = QLabel(app_name.capitalize())
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        card_layout.addWidget(name_label)

        # Version info
        version_label = QLabel(f"{self.tr('Current')}: {current_version}\n{self.tr('New')}: {new_version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                color: #ccc;
                font-size: 12px;
            }
        """)
        card_layout.addWidget(version_label)

        # Update button
        update_btn = QPushButton(self.tr("Update"))
        update_btn.setFixedHeight(30)
        update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #b95a5a, stop:1 #a94a4a);
                color: white;
                border-radius: 6px;
                border: 1px solid #993a3a;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                  stop:0 #ca6b6b, stop:1 #b95a5a);
            }
        """)
        update_btn.clicked.connect(lambda: self.update_app(app_name, download_url))
        card_layout.addWidget(update_btn)

        # Add card to updates layout
        self.updates_layout.addWidget(card)

    def update_app(self, app_name, download_url):
        """Update the specified app by downloading the update and unpacking it"""
        try:
            # Папка для загрузок
            download_dir = os.path.join("root", "user", "download")
            os.makedirs(download_dir, exist_ok=True)
            
            # Имя файла архива
            filename = f"{app_name}_update.zip"
            file_path = os.path.join(download_dir, filename)
            
            # Папка приложения
            app_dir = os.path.join("apps", "local", app_name)
            
            StellarMessageBox.information(
                self, self.tr("Update Started"), 
                self.tr("Downloading update for {}...").format(app_name)
            )
            
            import urllib.request
            try:
                req = urllib.request.Request(
                    download_url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )

                def download_progress(count, block_size, total_size):
                    percent = int(count * block_size * 100 / total_size)
                    print(f"Downloading {app_name}: {percent}%", end='\r')

                print(f"\nDownloading {app_name} update from {download_url}")
                urllib.request.urlretrieve(
                    download_url, 
                    file_path,
                    reporthook=download_progress
                )
                print(f"\nSuccessfully downloaded update to {file_path}")
                
                # ======= РАСПАКОВКА =======
                temp_extract_dir = os.path.join(download_dir, f"{app_name}_temp_extract")
                if os.path.exists(temp_extract_dir):
                    shutil.rmtree(temp_extract_dir)
                os.makedirs(temp_extract_dir, exist_ok=True)

                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract_dir)

                # GitHub-архивы обычно содержат папку-обёртку, найдём её
                extracted_items = os.listdir(temp_extract_dir)
                if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_extract_dir, extracted_items[0])):
                    source_dir = os.path.join(temp_extract_dir, extracted_items[0])
                else:
                    source_dir = temp_extract_dir

                # Удаляем старую версию приложения
                if os.path.exists(app_dir):
                    shutil.rmtree(app_dir)

                # Переносим новую версию
                shutil.move(source_dir, app_dir)

                # Чистим временные файлы
                shutil.rmtree(temp_extract_dir)
                os.remove(file_path)

                StellarMessageBox.information(
                    self, self.tr("Update Installed"), 
                    self.tr("Update for {} installed successfully.").format(app_name)
                )

                self.check_for_updates()

            except urllib.error.HTTPError as e:
                error_msg = f"HTTP Error downloading update: {e.code} {e.reason}"
                print(error_msg)
                StellarMessageBox.warning(self, self.tr("Download Error"), 
                                        self.tr("Failed to download update:\n{}").format(error_msg))
            except Exception as e:
                error_msg = str(e)
                print(f"Error downloading update: {error_msg}")
                StellarMessageBox.warning(self, self.tr("Error"), 
                                        self.tr("Failed to update {}:\n{}").format(app_name, error_msg))
                
        except Exception as e:
            error_msg = str(e)
            print(f"Error during update process: {error_msg}")
            StellarMessageBox.warning(self, self.tr("Error"), 
                                    self.tr("Failed to update {}:\n{}").format(app_name, error_msg))


    def update_updates_layout(self):
        """Update the layout of update cards"""
        # Get all widgets in the layout
        widgets = []
        for i in range(self.updates_layout.count()):
            item = self.updates_layout.itemAt(i)
            if item and item.widget():
                widgets.append(item.widget())
        
        if not widgets:
            return

        # Get current scroll area width
        scroll_width = self.updates_scroll_area.viewport().width()
        
        # Calculate how many cards fit in a row
        cards_per_row = max(1, (scroll_width - self.spacing) // (self.card_width + self.spacing))
        
        # Clear the current layout
        for i in reversed(range(self.updates_layout.count())):
            item = self.updates_layout.itemAt(i)
            if item.widget():
                self.updates_layout.removeWidget(item.widget())
        
        # Redistribute cards in the new layout
        row, col = 0, 0
        for widget in widgets:
            self.updates_layout.addWidget(widget, row, col)
            col += 1
            if col >= cards_per_row:
                col = 0
                row += 1

        # Update container size
        rows = (len(widgets) + cards_per_row - 1) // cards_per_row
        container_width = cards_per_row * (self.card_width + self.spacing) + self.spacing
        container_height = rows * (self.card_height + self.spacing) + self.spacing
        self.updates_container.setMinimumSize(container_width, container_height)
        self.updates_container.adjustSize()