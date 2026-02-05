import os
import platform
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QLabel, QLineEdit, QFrame, QMenu,
    QInputDialog, QMessageBox, QSplitter, QTextEdit
)
from PyQt6.QtWidgets import QTabBar, QPushButton
from PyQt6.QtCore import Qt, QSize, QPoint, QDateTime
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette
from PyQt6.QtCore import QTimer, QThreadPool, QRunnable, pyqtSignal, QObject
from PyQt6.QtGui import QImageReader, QImage, QPixmap
from PyQt6.QtGui import QPainter, QPen, QFontMetrics, QBrush


from PyQt6.QtCore import QMimeData, QUrl
from PyQt6.QtGui import QDrag

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *
import zipfile
import tarfile

import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QHBoxLayout, QPushButton, QCheckBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtCore import QObject, QEvent

from collections import OrderedDict


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

class PathDotGuard(QObject):
    def __init__(self, owner, parent=None):
        super().__init__(parent)
        self.owner = owner  # ExplorerWindow

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if not self.owner._op_allows_dot():
                # блокируем именно ввод '.'
                if event.text() == ".":
                    # вместо точки — сразу подставим root
                    cur = obj.text().strip()
                    if cur == "":
                        obj.setText("root")
                    elif cur in {".", "./", ".\\"}:
                        obj.setText("root")
                    return True
        return False

class DraggableFileList(QListWidget):
    """
    Список файлов с поддержкой перетаскивания (Drag-and-Drop).
    Исправленная версия: dropEvent теперь находится ВНУТРИ этого класса.
    """
    def __init__(self, owner):
        super().__init__()
        self.owner = owner  # Ссылка на главное окно (ExplorerWindow)
        self._hover_item = None

        # Включаем прием файлов
        self.setAcceptDrops(True)
        # Важно для режима иконок:
        self.viewport().setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        # Скрываем стандартный индикатор, так как рисуем сами или просто копируем
        self.setDropIndicatorShown(False)

    # --- Подсветка папки при наведении ---
    def _clear_hover(self):
        if self._hover_item is not None:
            self._hover_item.setBackground(QBrush(Qt.GlobalColor.transparent))
            self._hover_item = None

    def _set_hover(self, item):
        if item is self._hover_item:
            return
        self._clear_hover()
        if item is None:
            return
        # Подсвечиваем синим
        item.setBackground(QBrush(QColor(58, 109, 240, 60)))
        self._hover_item = item

    def _unique_path(self, dst: str) -> str:
        """Создает уникальное имя (файл (1).txt), если файл уже есть."""
        if not os.path.exists(dst):
            return dst
        base_dir = os.path.dirname(dst)
        name = os.path.basename(dst)
        stem, ext = os.path.splitext(name)
        n = 1
        while True:
            cand = os.path.join(base_dir, f"{stem} ({n}){ext}")
            if not os.path.exists(cand):
                return cand
            n += 1

    # --- Начало перетаскивания (Drag) ---
    def startDrag(self, supportedActions):
        items = self.selectedItems()
        if not items:
            return

        urls = []
        paths = []
        for it in items:
            p = it.data(Qt.ItemDataRole.UserRole)
            if isinstance(p, str) and os.path.exists(p):
                ap = os.path.abspath(p)
                urls.append(QUrl.fromLocalFile(ap))
                paths.append(ap)

        if not urls:
            return

        mime = QMimeData()
        mime.setUrls(urls)
        drag = QDrag(self)
        drag.setMimeData(mime)

        # Рисуем красивую картинку перетаскивания
        if paths:
            icon = items[0].icon()
            title = os.path.basename(paths[0])
            if len(paths) > 1:
                title = f"{title}  (+{len(paths)-1})"
            
            w, h = 240, 58
            pm = QPixmap(w, h)
            pm.fill(Qt.GlobalColor.transparent)
            pnt = QPainter(pm)
            pnt.setPen(QPen(QColor(255, 255, 255, 55), 1))
            pnt.setBrush(QColor(25, 25, 25, 220))
            pnt.drawRoundedRect(0, 0, w-1, h-1, 12, 12)
            ico = icon.pixmap(34, 34)
            pnt.drawPixmap(12, (h-34)//2, ico)
            pnt.setPen(QColor(255, 255, 255, 235))
            pnt.drawText(56, 0, 170, h, Qt.AlignmentFlag.AlignVCenter, title)
            pnt.end()
            drag.setPixmap(pm)
            drag.setHotSpot(QPoint(20, h//2))

        drag.exec(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction, Qt.DropAction.CopyAction)

    # --- Вход мыши с файлом в зону списка ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    # --- Перемещение мыши (подсветка папок) ---
    def dragMoveEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        item = self.itemAt(pos)

        # Логика подсветки папки
        if item:
            p = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(p, str) and os.path.isdir(p):
                self._set_hover(item)
            else:
                self._set_hover(None)
        else:
            self._set_hover(None)

        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._clear_hover()
        super().dragLeaveEvent(event)

    # --- ОТПУСКАНИЕ ФАЙЛА (САМОЕ ВАЖНОЕ) ---
    def dropEvent(self, event):
        self._clear_hover()

        if not event.mimeData().hasUrls():
            event.ignore()
            return

        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        item = self.itemAt(pos)

        # 1. Куда кидаем? (В папку под курсором или в текущую открытую папку)
        dest_dir = getattr(self.owner, "current_path", None)
        if not dest_dir: 
            dest_dir = os.getcwd()

        if item:
            p = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(p, str) and os.path.isdir(p):
                dest_dir = p  # Кидаем ВНУТРЬ папки под курсором

        # 2. Это перемещение или копирование?
        # Если источник - это наше окно, то перемещаем. Иначе (из винды) - копируем.
        is_move = (event.source() is self)

        files_processed = False
        for url in event.mimeData().urls():
            src = url.toLocalFile()
            if not src or not os.path.exists(src):
                continue
            
            src = os.path.normpath(src)
            basename = os.path.basename(src)
            dst = os.path.join(dest_dir, basename)

            # Не копируем файл сам в себя
            if os.path.abspath(src) == os.path.abspath(dst):
                continue

            dst = self._unique_path(dst) # Делаем имя уникальным

            try:
                if is_move:
                    shutil.move(src, dst)
                else:
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                files_processed = True
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка: {e}")

        # Обновляем список, если что-то произошло
        if files_processed:
            if hasattr(self.owner, "load_directory"):
                self.owner.load_directory(self.owner.current_path)

        event.acceptProposedAction()

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

class _PreviewSignal(QObject):
    done = pyqtSignal(int, str, QImage)  # req_id, path, image

class _PreviewTask(QRunnable):
    def __init__(self, req_id: int, path: str, target_w: int, target_h: int, sig: _PreviewSignal):
        super().__init__()
        self.req_id = req_id
        self.path = path
        self.target_w = target_w
        self.target_h = target_h
        self.sig = sig

    def run(self):
        img = QImage()
        try:
            reader = QImageReader(self.path)
            reader.setAutoTransform(True)

            # ✅ ключевое: декодим сразу в маленький размер
            # reader.setScaledSize(QSize(self.target_w, self.target_h))

            # img = reader.read()  # QImage
            reader.setAutoTransform(True)

            orig = reader.size()  # берёт размер из метаданных (быстро)
            if orig.isValid():
                scaled = orig.scaled(self.target_w, self.target_h, Qt.AspectRatioMode.KeepAspectRatio)
                reader.setScaledSize(scaled)
            else:
                reader.setScaledSize(QSize(self.target_w, self.target_h))  # fallback

            img = reader.read()

        except Exception:
            img = QImage()

        self.sig.done.emit(self.req_id, self.path, img)

class EscToFilesFilter(QObject):
    def __init__(self, owner, parent=None):
        super().__init__(parent)
        self.owner = owner  # ExplorerWindow

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                # снять фокус с поля ввода
                try:
                    obj.clearFocus()
                    obj.deselect()
                except Exception:
                    pass

                # вернуть фокус на список файлов
                try:
                    self.owner.file_list.setFocus(Qt.FocusReason.ShortcutFocusReason)
                    # опционально: если ничего не выделено — выделим первый элемент
                    if self.owner.file_list.count() > 0 and not self.owner.file_list.selectedItems():
                        self.owner.file_list.setCurrentRow(0)
                except Exception:
                    pass

                return True  # событие обработали
        return False



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
        self.show_system_folders = False
        self.SHOW_SYSTEM_STATE_PATH = "bin/sys/path/explorer"
        self.TABS_SESSION_PATH = "bin/sys/path/explorer_tabs.json"
        # --- Archive in-place mode ---
        self._archive_mode = False
        self._archive_path = ""
        self._archive_prefix = ""      # текущая "папка" внутри архива ("" = корень)
        self._archive_parent_dir = ""  # папка, из которой открыли архив


        self._thread_pool = QThreadPool(self)
        self._thread_pool.setMaxThreadCount(1)   # важно: не плодим параллельные декоды

        self._preview_sig = _PreviewSignal()
        self._preview_sig.done.connect(self._on_preview_ready)

        self._details_req_id = 0
        self._preview_cache = OrderedDict()      # path -> (mtime, QPixmap)
        self._preview_cache_limit = 200

        # дебаунс, чтобы при скролле/быстром выборе не стартовать 50 превью подряд
        self._details_timer = QTimer(self)
        self._details_timer.setSingleShot(True)
        self._details_timer.timeout.connect(self.update_file_details)


        # === Window setup ===
        self.setWindowTitle(self.tr("File Explorer"))
        self.setGeometry(200, 100, 910, 600)

        # === Root container ===
        self.container = QWidget()
        self.content_layout.addWidget(self.container)
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Toolbar (top) ===
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(5, 5, 5, 5)
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
        # self.path_edit.returnPressed.connect(self.navigate_to_path)
        self.path_edit.returnPressed.connect(self._on_path_entered)
        self._path_dot_guard = PathDotGuard(self, self)
        self.path_edit.installEventFilter(self._path_dot_guard)
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

        self.show_system_cb = ToggleSwitch(self)   # оставляем имя переменной, чтобы меньше менять
        self.show_system_cb.setChecked(False)
        toolbar.addWidget(self.show_system_cb)
        self.show_system_folders = self._load_show_system_state()
        self.show_system_cb.setChecked(self.show_system_folders)

        # === Tabs (Windows 11 style) in title bar ===
        self._tabs = {}          # idx -> state
        self._tabs_paths = []    # список путей по вкладкам (для заголовков)
        self._prev_tab_index = None

        self._esc_to_files = EscToFilesFilter(self, self)
        self.path_edit.installEventFilter(self._esc_to_files)
        self.search_edit.installEventFilter(self._esc_to_files)



        self.tab_bar = QTabBar()
        self.tab_bar.setDocumentMode(True)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setMovable(True)
        self.tab_bar.tabMoved.connect(self._on_tab_moved)
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setElideMode(Qt.TextElideMode.ElideRight)

        self.tab_bar.setStyleSheet("""
        QTabBar {
            background: transparent;
            border: 0px;
        }
        QTabBar::tab {
            background: #2b2b2b;
            color: #d7d7d7;
            padding: 6px 14px;
            margin-right: 6px;
            border: 0px;              /* ✅ */
            border-bottom: 0px;       /* ✅ */
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            min-height: 26px;
        }

        QTabBar::tab:selected {
            background: #3a3a3a;
            color: white;
            border: 0px;              /* ✅ */
            border-bottom: 0px;       /* ✅ */
        }
        QTabBar::tab:hover { background: #353535; }

        QTabBar::close-button {
            image: url(apps/local/browser/icons/close-light.png);
            subcontrol-position: right;
            width: 20px;
            height: 20px;
        }

        QTabBar::close-button:hover {
            image: url(apps/local/browser/icons/close-light-hover.png);
        }
        """)


        self.tab_bar.currentChanged.connect(self._on_tab_changed)
        self.tab_bar.tabCloseRequested.connect(self._close_tab)

        # Кнопка "+"
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(28, 28)
        self.new_tab_btn.setStyleSheet("""
        QPushButton {
            background: #2b2b2b;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
        }
        QPushButton:hover { background: #3a3a3a; }
        QPushButton:pressed { background: #444; }
        """)
        self.new_tab_btn.clicked.connect(lambda: self._new_tab(self.current_path if hasattr(self, "current_path") else os.path.expanduser("root")))

        # ВАЖНО: добавляем в title bar
        self.add_title_widget(self.tab_bar)
        self.add_title_widget(self.new_tab_btn)

        # Combine path + search
        path_layout = QHBoxLayout()
        path_layout.setSpacing(5)
        path_layout.addWidget(self.path_edit, 1)
        path_layout.addWidget(self.search_edit)
        path_layout.addWidget(self.search_button)

        toolbar.addLayout(path_layout, 1)
        main_layout.addLayout(toolbar)

        # === Splitter: sidebar | files | details ===
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(2)

        # === Left: Places list ===
        self.places_list = QListWidget()
        self.places_list.setMinimumWidth(170)
        self.main_splitter.setCollapsible(0, False)
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
        self.file_list = DraggableFileList(owner=self)
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
        self.file_list.itemSelectionChanged.connect(self._schedule_update_file_details)
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
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #2f2f2f;
            }
            QListWidget::item:selected {
                background-color: #3a6df0;
            }
        """)
        self.file_list.setDragEnabled(True)
        self.file_list.setAcceptDrops(True)
        self.file_list.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        self.file_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.file_list.setDropIndicatorShown(False)

        self.main_splitter.addWidget(self.file_list)

        # === Right: Details panel ===
        self.details_panel = QWidget()
        self.details_panel.setMinimumWidth(250)
        self.details_panel.setMaximumWidth(350)
        details_layout = QVBoxLayout(self.details_panel)
        details_layout.setContentsMargins(0, 0, 0, 0)
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

        QTimer.singleShot(0, lambda: self.main_splitter.setSizes([170, 100000, 320]))

        self.setup_focus_activation(self.container)

        # Восстановить вкладки из прошлой сессии
        restored = self._restore_tabs_session()
        if not restored:
            # если нечего восстанавливать — создаём одну вкладку как обычно
            self._new_tab(os.path.expanduser("root"))


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
        print("file_list viewport:", self.file_list.viewport().width())


    def _tab_state_default(self, path: str) -> dict:
        return {
            "path": path,
            "history": [path],
            "history_index": 0,
            "archive_mode": False,
            "archive_path": None,
            "archive_prefix": "",
        }

    def _save_tabs_session(self):
        """Сохраняет вкладки на диск (пути + активная + история каждой вкладки)."""
        try:
            # сначала сохраним текущее состояние активной вкладки в память
            cur = self.tab_bar.currentIndex() if hasattr(self, "tab_bar") else -1
            if cur >= 0:
                self._save_tab_state(cur)  # важно: именно текущую

            session = {
                "active": int(self.tab_bar.currentIndex()),
                "tabs": []
            }

            # собираем вкладки по порядку
            for i in range(self.tab_bar.count()):
                # если у тебя состояние хранится в self._tabs[idx]
                st = self._tabs.get(i)
                if not st:
                    # fallback — если нет стейта, создадим из пути
                    p = ""
                    if i < len(self._tabs_paths):
                        p = self._tabs_paths[i]
                    if not p:
                        p = os.path.expanduser("root")
                    st = self._tab_state_default(p)

                # гарантируем ключи
                p = st.get("path") or (self._tabs_paths[i] if i < len(self._tabs_paths) else os.path.expanduser("root"))
                session["tabs"].append({
                    "path": p,
                    "history": list(st.get("history", [p])),
                    "history_index": int(st.get("history_index", 0)),
                    "archive_mode": bool(st.get("archive_mode", False)),
                    "archive_path": st.get("archive_path", None),
                    "archive_prefix": st.get("archive_prefix", "") or "",
                })

            os.makedirs(os.path.dirname(self.TABS_SESSION_PATH), exist_ok=True)
            with open(self.TABS_SESSION_PATH, "w", encoding="utf-8") as f:
                json.dump(session, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[EXPLORER] tabs session save error: {e}")

    def _load_tabs_session(self) -> dict | None:
        """Читает с диска сессию вкладок."""
        try:
            if not os.path.exists(self.TABS_SESSION_PATH):
                return None
            with open(self.TABS_SESSION_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or "tabs" not in data:
                return None
            if not isinstance(data["tabs"], list) or len(data["tabs"]) == 0:
                return None
            return data
        except Exception as e:
            print(f"[EXPLORER] tabs session load error: {e}")
            return None

    def _restore_tabs_session(self):
        """Восстанавливает вкладки из файла."""
        session = self._load_tabs_session()
        if not session:
            return False

        self.tab_bar.blockSignals(True)
        try:
            # чистим всё
            self._clear_tabbar()
            self._tabs.clear()
            self._tabs_paths.clear()

            # создаём вкладки
            for tab in session.get("tabs", []):
                p = tab.get("path") or os.path.expanduser("root")
                title = self._tab_title_for_path(p)
                idx = self.tab_bar.addTab(title)
                self.tab_bar.setTabToolTip(idx, p)
                self._tabs_paths.append(p)

                self._tabs[idx] = {
                    "path": p,
                    "history": list(tab.get("history", [p])),
                    "history_index": int(tab.get("history_index", 0)),
                    "archive_mode": bool(tab.get("archive_mode", False)),
                    "archive_path": tab.get("archive_path", None),
                    "archive_prefix": tab.get("archive_prefix", "") or "",
                }

            active = int(session.get("active", 0))
            if active < 0 or active >= self.tab_bar.count():
                active = 0

            self.tab_bar.setCurrentIndex(active)
            self._prev_tab_index = active

        except Exception as e:
            print(f"[EXPLORER] tabs session restore error: {e}")
            return False
        finally:
            self.tab_bar.blockSignals(False)

        # восстановим UI уже после включения сигналов
        self._restore_tab_state(self.tab_bar.currentIndex())
        return True



    def _tab_title_for_path(self, path: str) -> str:
        if not path:
            return self.tr("Tab")
        p = path.replace("\\", "/").rstrip("/")
        name = os.path.basename(p)
        return name if name else p

    def _new_tab(self, path: str):
        title = self._tab_title_for_path(path)
        idx = self.tab_bar.addTab(title)
        self.tab_bar.setTabToolTip(idx, path)

        self._tabs_paths.append(path)
        self._ensure_tab_state(idx, path)   # ✅ ДО setCurrentIndex

        self.tab_bar.setCurrentIndex(idx)
        self.load_directory(path)
        self._save_tabs_session()


    def _ensure_tab_state(self, idx: int, start_path: str):
        if idx not in self._tabs:
            self._tabs[idx] = {
                "path": start_path,
                "history": [start_path],
                "history_index": 0,
                "archive_mode": False,
                "archive_path": None,
                "archive_prefix": "",
            }

    def _save_tab_state(self, idx: int):
        """Сохраняем состояние КОНКРЕТНОЙ вкладки idx (не currentIndex())."""
        if idx < 0:
            return
        start = getattr(self, "current_path", os.path.expanduser("root"))
        self._ensure_tab_state(idx, start)
        st = self._tabs[idx]

        st["path"] = getattr(self, "current_path", st["path"])
        st["history"] = list(getattr(self, "history", []))
        st["history_index"] = int(getattr(self, "history_index", -1))

        # если есть режим архива:
        st["archive_mode"] = bool(getattr(self, "_archive_mode", False))
        st["archive_path"] = getattr(self, "_archive_path", None)
        st["archive_prefix"] = getattr(self, "_archive_prefix", "") or ""

    def _restore_tab_state(self, idx: int):
        if idx < 0:
            return
        start = os.path.expanduser("root")
        self._ensure_tab_state(idx, start)
        st = self._tabs[idx]

        # восстановили историю
        self.history = list(st.get("history", []))
        self.history_index = int(st.get("history_index", -1))

        # восстановили путь
        self.current_path = st.get("path", start)

        # восстановили архив-режим (если используешь)
        self._archive_mode = bool(st.get("archive_mode", False))
        self._archive_path = st.get("archive_path", None)
        self._archive_prefix = st.get("archive_prefix", "") or ""

        # показать содержимое
        # ВАЖНО: load_directory должен принимать add_history=False
        self.load_directory(self.current_path, add_history=False)
        self.update_nav_buttons()

    def _on_tab_changed(self, idx: int):
        """Правильно: сохраняем ПРЕДЫДУЩУЮ вкладку, потом восстанавливаем НОВУЮ."""
        prev = self._prev_tab_index

        # первый раз просто запоминаем
        if prev is None:
            self._prev_tab_index = idx
            self._restore_tab_state(idx)
            return

        # сохраняем состояние предыдущей вкладки (а не текущей!)
        if prev != idx:
            self._save_tab_state(prev)

        # восстанавливаем выбранную вкладку
        self._restore_tab_state(idx)
        self._prev_tab_index = idx
        self._save_tabs_session()

    def closeEvent(self, event):
        try:
            self._save_tabs_session()
        except:
            pass
        super().closeEvent(event)

    def _clear_tabbar(self):
        """Полностью очищает QTabBar (в PyQt6 у QTabBar нет .clear())."""
        while self.tab_bar.count() > 0:
            self.tab_bar.removeTab(0)



    def _close_tab(self, idx: int):
        try:
            count = self.tab_bar.count()
            if idx < 0 or idx >= count:
                return

            # сохраним порядок стейтов ДО удаления
            states = [self._tabs.get(i) for i in range(count)]
            paths  = list(self._tabs_paths)

            # удаляем вкладку из UI
            self.tab_bar.removeTab(idx)

            # удаляем из списков
            if idx < len(states):
                states.pop(idx)
            if idx < len(paths):
                paths.pop(idx)

            # пересобираем dict
            self._tabs = {i: states[i] for i in range(len(states))}
            self._tabs_paths = paths

            # если закрыли последнюю — создаём новую
            if self.tab_bar.count() == 0:
                home = os.path.expanduser("root")
                self._new_tab(home)

            self._prev_tab_index = self.tab_bar.currentIndex()
            self._save_tabs_session()
        except Exception as e:
            print(f"[EXPLORER] close tab error: {e}")



    def _schedule_update_file_details(self):
        self._details_timer.start(80)  # 60-120мс нормально

    def _load_show_system_state(self) -> bool:
        try:
            with open(self.SHOW_SYSTEM_STATE_PATH, "r", encoding="utf-8") as f:
                v = f.read().strip().lower()
            return v in ("1", "true", "yes", "on")
        except Exception:
            return False  # по умолчанию скрываем системные

    def _save_show_system_state(self, state: bool) -> None:
        try:
            os.makedirs(os.path.dirname(self.SHOW_SYSTEM_STATE_PATH), exist_ok=True)
            with open(self.SHOW_SYSTEM_STATE_PATH, "w", encoding="utf-8") as f:
                f.write("1" if state else "0")
        except Exception as e:
            print(f"[EXPLORER] can't save system toggle: {e}")


    def toggle_wifi(self, checked: bool):
        # ToggleSwitch вызывает это на parent()
        self.show_system_folders = bool(checked)
        self._save_show_system_state(self.show_system_folders)
        self.load_directory(self.current_path)


    def _op_allows_dot(self) -> bool:
        # Разрешаем '.' только если в файле есть ключ Px228-Da-Da
        try:
            p = os.path.join("bin", "sys", "path", "op")
            with open(p, "r", encoding="utf-8") as f:
                return "Px228-Da-Da" in f.read()
        except Exception:
            return False

    def _map_dot_path(self, raw: str) -> str:
        """Если '.' запрещена — маппим '.' в root."""
        raw = (raw or "").strip()
        if self._op_allows_dot():
            return raw

        # '.' / './' / '.\' -> root
        if raw in {".", "./", ".\\"}:
            return "root"

        # './sub' или '.\sub' -> root/sub
        if raw.startswith("./") or raw.startswith(".\\"):
            rest = raw[2:]
            if rest:
                return os.path.join("root", rest)
            return "root"

        return raw

    def open_or_switch_tab(self, path: str):
        """Открывает путь во вкладке: если уже есть такая вкладка — переключается на неё."""
        if not path:
            return

        # нормализуем, чтобы сравнение работало на Windows
        norm = os.path.normpath(path)

        # если таббар ещё не создан — просто открыть как раньше
        if not hasattr(self, "tab_bar"):
            return self.open_path(path)

        # ищем вкладку по tooltip (ты туда кладёшь path)
        for i in range(self.tab_bar.count()):
            tip = self.tab_bar.tabToolTip(i) or ""
            if tip and os.path.normpath(tip) == norm:
                # переключаемся на неё (сработает твой _on_tab_changed)
                self.tab_bar.setCurrentIndex(i)

                # на всякий случай обновим содержимое без записи в историю
                try:
                    self.load_directory(path, add_history=False)
                except TypeError:
                    self.load_directory(path)
                return

        # если не нашли — создаём новую вкладку
        self._new_tab(path)

    def _on_path_entered(self):
        """Enter in address bar:
        - 'cmd'            -> open CMD in current directory
        - 'cmd <path>'     -> open CMD in that folder
        Otherwise behaves like normal path navigation.
        """
        raw = (self.path_edit.text() or "").strip()
        low = raw.lower()

        # cmd command
        if low == "cmd" or low.startswith("cmd "):
            # cmd <path> can be either absolute OS-path or your virtual path.
            target = None
            if low == "cmd":
                target = getattr(self, "current_path", "") or ""
            else:
                arg = raw[4:].strip()
                if arg:
                    target = self._map_dot_path(arg)

            # fallback
            if not target:
                target = getattr(self, "current_path", "") or ""

            self._open_cmd_for_path(target)

            # restore address bar to actual current path
            if hasattr(self, "current_path"):
                self.path_edit.setText(self.current_path)

            # return focus to file list (so esc/keys work as expected)
            try:
                self.file_list.setFocus()
            except Exception:
                pass
            return

        # normal behaviour
        self.navigate_to_path()


    def _open_cmd_for_path(self, path: str):
        """Helper: open CMD for a path (folder or file)."""
        try:
            p = path
            if not p:
                return
            if os.path.isfile(p):
                p = os.path.dirname(p)
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.open_in_cmd(item)
        except Exception as e:
            try:
                StellarMessageBox.warning(self, self.tr("Error"), self.tr("Could not open CMD: {} ").format(str(e)))
            except Exception:
                print("[EXPLORER] Could not open CMD:", e)


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
        self._details_req_id += 1
        req_id = self._details_req_id

        selected_items = self.file_list.selectedItems()
        if not selected_items:
            self.file_preview_label.clear()
            self.file_details_text.clear()
            return

        if selected_items and len(selected_items) > 1:
            not_path = os.path.join(self.icons_files_path, "not.png")

            # превью
            if os.path.exists(not_path):
                pix = QPixmap(not_path)
                if not pix.isNull():
                    pix = pix.scaled(
                        self.file_preview_label.width(),
                        self.file_preview_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.file_preview_label.setPixmap(pix)
                    self.file_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.file_preview_label.setScaledContents(False)
                else:
                    self.file_preview_label.clear()
            else:
                self.file_preview_label.clear()

            # суммарный размер (суммируем только файлы — папки не трогаем, чтобы не лагало)
            total_bytes = 0
            folders_count = 0
            missing_count = 0

            for it in selected_items:
                p = it.data(Qt.ItemDataRole.UserRole)
                try:
                    if os.path.isfile(p):
                        total_bytes += os.path.getsize(p)
                    elif os.path.isdir(p):
                        folders_count += 1
                    else:
                        missing_count += 1
                except Exception:
                    missing_count += 1

            details = []
            details.append(f"{self.tr('Selected')}: {len(selected_items)}")
            details.append(f"{self.tr('Total size')}: {self._format_bytes(total_bytes)}")

            if folders_count:
                details.append(f"{self.tr('Folders')}: {folders_count} ({self.tr('not counted to avoid lag')})")
            if missing_count:
                details.append(f"{self.tr('Missing')}: {missing_count}")

            self.file_details_text.setPlainText("\n".join(details))
            return

        item = selected_items[0]
        data = item.data(Qt.ItemDataRole.UserRole)

        # ✅ ВАЖНО: если это элемент архива (dict) — НЕ трогаем os.path.*
        if isinstance(data, dict) and data.get("type") == "archive":
            name = data.get("name", "")
            is_dir = bool(data.get("is_dir"))
            inner = data.get("inner", "")

            if is_dir:
                icon = self.folder_icon or QIcon()
                self.file_preview_label.setPixmap(icon.pixmap(100, 100))
            else:
                ext = os.path.splitext(name)[1].lower()
                icon_name = ext[1:] if ext.startswith(".") else (ext or "file")
                icon_path = os.path.join(self.icons_files_path, f"{icon_name}.png")
                icon = QIcon(icon_path) if os.path.exists(icon_path) else (self.not_found_icon or QIcon())
                self.file_preview_label.setPixmap(icon.pixmap(100, 100))

            details = []
            details.append(f"{self.tr('Name')}: {name}")
            details.append(f"{self.tr('Type')}: {self.tr('File folder') if is_dir else self.tr('File')}")
            details.append(f"{self.tr('Path')}: {self._archive_display_path()}")
            if inner:
                details.append(f"{self.tr('Inside')}: {inner}")

            self.file_details_text.setPlainText("\n".join(details))
            return

        # ✅ обычный режим — теперь data точно строка/PathLike
        path = data
        if not isinstance(path, (str, bytes, os.PathLike)):
            self.file_preview_label.clear()
            self.file_details_text.setPlainText(self.tr("Preview error"))
            return

        # дальше твой существующий код для картинок/деталей
        image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
        ext = os.path.splitext(path)[1].lower()

        if os.path.isfile(path) and ext in image_extensions:
            # Плейсхолдер, чтобы UI не "пустел"
            self.file_preview_label.setText(self.tr("Loading..."))

            try:
                if os.path.getsize(path) > 25 * 1024 * 1024:  # 25MB
                    self.file_preview_label.setText(self.tr("Preview disabled (large image)"))
                else:
                    # --- cache ---
                    mtime = os.path.getmtime(path)
                    cached = self._preview_cache.get(path)
                    if cached and cached[0] == mtime:
                        self.file_preview_label.setPixmap(cached[1])
                        self.file_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.file_preview_label.setScaledContents(False)
                    else:
                        # ВАЖНО: превью всегда 100x100 (или фактический размер лейбла, если он фиксирован)
                        target_w = max(1, self.file_preview_label.width())
                        target_h = max(1, self.file_preview_label.height())

                        task = _PreviewTask(req_id, path, target_w, target_h, self._preview_sig)
                        self._thread_pool.start(task)
            except Exception:
                self.file_preview_label.setText(self.tr("Preview error"))
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

    def _on_preview_ready(self, req_id: int, path: str, img: QImage):
        if req_id != self._details_req_id:
            return

        if img.isNull():
            icon = self.get_icon(path)
            self.file_preview_label.setPixmap(icon.pixmap(100, 100))
            return

        pix = QPixmap.fromImage(img)

        # cache store
        try:
            mtime = os.path.getmtime(path)
            self._preview_cache[path] = (mtime, pix)
            self._preview_cache.move_to_end(path)
            while len(self._preview_cache) > self._preview_cache_limit:
                self._preview_cache.popitem(last=False)
        except Exception:
            pass

        self.file_preview_label.setPixmap(pix)
        self.file_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_preview_label.setScaledContents(False)

    def _format_bytes(self, b: int) -> str:
        try:
            size = float(b)
            for unit in ["B", "KB", "MB", "GB", "TB"]:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} PB"
        except Exception:
            return "Unknown"


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

    def extract_archive(self, archive_path: str, dest_dir: str | None = None):
        if not self._is_archive(archive_path):
            return

        if dest_dir is None:
            # по умолчанию — в текущую папку, в подпапку с именем архива
            name = os.path.basename(archive_path)
            base = name
            for ext in (".tar.gz", ".tgz", ".tar", ".zip"):
                if base.lower().endswith(ext):
                    base = base[:-len(ext)]
                    break
            dest_dir = os.path.join(self.current_path, base)

        os.makedirs(dest_dir, exist_ok=True)

        try:
            p = archive_path.lower()

            # --- ZIP ---
            if p.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as z:
                    for member in z.infolist():
                        # защита от ../
                        safe_path = self._safe_join(dest_dir, member.filename)
                        # если это папка
                        if member.is_dir():
                            os.makedirs(safe_path, exist_ok=True)
                            continue
                        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
                        with z.open(member, "r") as src, open(safe_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)

            # --- TAR / TGZ ---
            else:
                mode = "r:gz" if (p.endswith(".tar.gz") or p.endswith(".tgz")) else "r"
                with tarfile.open(archive_path, mode) as t:
                    for member in t.getmembers():
                        safe_path = self._safe_join(dest_dir, member.name)
                        if member.isdir():
                            os.makedirs(safe_path, exist_ok=True)
                            continue
                        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
                        f = t.extractfile(member)
                        if f is None:
                            continue
                        with f, open(safe_path, "wb") as out:
                            shutil.copyfileobj(f, out)

            self.load_directory(self.current_path)
            self.status_label.setText(self.tr("Extracted: {}").format(os.path.basename(archive_path)))

        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Extract failed: {}").format(str(e)))

    def create_zip_from_selection(self):
        selected = self.file_list.selectedItems()
        if not selected:
            return

        # имя архива
        name, ok = CustomInputDialog.getText(self, self.tr("Create archive"),
                                                self.tr("Archive name (.zip):"),
                                                "archive.zip")
        if not ok or not name:
            return
        if not name.lower().endswith(".zip"):
            name += ".zip"

        out_path = os.path.join(self.current_path, name)

        try:
            with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
                for it in selected:
                    src = it.data(Qt.ItemDataRole.UserRole)

                    # кладём относительные пути относительно current_path
                    if os.path.isdir(src):
                        for root, dirs, files in os.walk(src):
                            for fn in files:
                                fpath = os.path.join(root, fn)
                                arcname = os.path.relpath(fpath, self.current_path)
                                z.write(fpath, arcname)
                    else:
                        arcname = os.path.relpath(src, self.current_path)
                        z.write(src, arcname)

            self.load_directory(self.current_path)
            self.status_label.setText(self.tr("Archive created: {}").format(name))

        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Create archive failed: {}").format(str(e)))


    def open_archive_view(self, archive_path: str):
        if not self._is_archive(archive_path):
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(self.tr("Archive"))
        dlg.setFixedSize(520, 520)

        lay = QVBoxLayout(dlg)
        lbl = QLabel(os.path.basename(archive_path))
        lay.addWidget(lbl)

        lst = QListWidget()
        lay.addWidget(lst, 1)

        btns = QHBoxLayout()
        b_extract = QPushButton(self.tr("Extract here"))
        b_close = QPushButton(self.tr("Close"))
        btns.addWidget(b_extract)
        btns.addWidget(b_close)
        lay.addLayout(btns)

        try:
            p = archive_path.lower()

            if p.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as z:
                    for n in z.namelist():
                        lst.addItem(n)
            else:
                mode = "r:gz" if (p.endswith(".tar.gz") or p.endswith(".tgz")) else "r"
                with tarfile.open(archive_path, mode) as t:
                    for m in t.getmembers():
                        lst.addItem(m.name)

        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Open archive failed: {}").format(str(e)))
            dlg.close()
            return

        b_extract.clicked.connect(lambda: (self.extract_archive(archive_path, None), dlg.close()))
        b_close.clicked.connect(dlg.close)
        dlg.exec()

    def open_archive_in_place(self, archive_path: str, prefix: str = ""):
        """Открыть архив внутри проводника (как папку)"""
        if not self._is_archive(archive_path):
            return

        self._archive_mode = True
        self._archive_path = archive_path
        self._archive_prefix = prefix or ""
        self._archive_parent_dir = os.path.dirname(archive_path)

        # показываем "путь" в строке адреса
        shown = self._archive_display_path()
        self.path_edit.setText(shown)

        # обновим историю навигации (как load_directory делает)
        if not self.history or (self.history and self.history[self.history_index] != shown):
            self.history = self.history[:self.history_index + 1]
            self.history.append(shown)
            self.history_index += 1
        self.update_nav_buttons()

        self._render_archive_listing()


    def _archive_display_path(self) -> str:
        # красивый путь типа: C:\...\file.zip::folder/sub
        if self._archive_prefix:
            return f"{self._archive_path}::{self._archive_prefix}"
        return f"{self._archive_path}::"


    def _render_archive_listing(self):
        """Заполнить file_list содержимым архива на уровне self._archive_prefix"""
        self.file_list.clear()

        try:
            children = self._list_archive_children(self._archive_path, self._archive_prefix)
        except Exception as e:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Open archive failed: {}").format(str(e)))
            # выходим назад
            self._archive_mode = False
            self.load_directory(self._archive_parent_dir or self.current_path)
            return

        # сортировка: папки сверху, потом файлы
        children.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

        for ch in children:
            item = QListWidgetItem(ch["name"])
            # кладём dict в UserRole (Qt это умеет)
            item.setData(Qt.ItemDataRole.UserRole, ch)

            # иконка (папка/файл)
            if ch["is_dir"]:
                icon = self.folder_icon or QIcon.fromTheme("folder") or QIcon()
            else:
                # иконку подбираем по расширению имени внутри архива
                fake_path = ch["name"]
                ext = os.path.splitext(fake_path)[1].lower()
                # используем твою get_icon, но ей нужен "путь" — поэтому делаем через ext-иконки:
                icon_name = ext[1:] if ext.startswith(".") else ext or "file"
                icon_path = os.path.join(self.icons_files_path, f"{icon_name}.png")
                if os.path.exists(icon_path):
                    icon = QIcon(icon_path)
                else:
                    icon = self.not_found_icon or self.default_file_icon or QIcon()

            item.setIcon(icon)
            self.file_list.addItem(item)

        self.status_label.setText(self.tr("Loaded archive: {}").format(os.path.basename(self._archive_path)))


    def _list_archive_children(self, archive_path: str, prefix: str):
        """
        Вернёт элементы на текущем уровне prefix.
        Каждый элемент: {"type":"archive","archive":...,"inner":...,"name":...,"is_dir":bool}
        """
        prefix = (prefix or "").replace("\\", "/")
        if prefix and not prefix.endswith("/"):
            prefix += "/"

        names = []

        p = archive_path.lower()
        if p.endswith(".zip"):
            with zipfile.ZipFile(archive_path, "r") as z:
                names = z.namelist()
        else:
            mode = "r:gz" if (p.endswith(".tar.gz") or p.endswith(".tgz")) else "r"
            with tarfile.open(archive_path, mode) as t:
                names = [m.name for m in t.getmembers()]

        # фильтруем по текущей "папке" prefix
        seen_dirs = set()
        children = []

        for n in names:
            n = (n or "").replace("\\", "/")
            if not n or n.startswith("/") or n.startswith("../"):
                continue

            if prefix and not n.startswith(prefix):
                continue

            rest = n[len(prefix):] if prefix else n
            if not rest:
                continue

            # берём только первый сегмент после prefix
            first = rest.split("/", 1)[0]

            # если внутри есть "/" значит это папка (или файл глубже)
            is_dir = "/" in rest

            if is_dir:
                if first in seen_dirs:
                    continue
                seen_dirs.add(first)
                children.append({
                    "type": "archive",
                    "archive": archive_path,
                    "inner": (prefix + first).strip("/"),
                    "name": first,
                    "is_dir": True
                })
            else:
                children.append({
                    "type": "archive",
                    "archive": archive_path,
                    "inner": (prefix + first).strip("/"),
                    "name": first,
                    "is_dir": False
                })

        return children


    def _is_archive_item(self, data) -> bool:
        return isinstance(data, dict) and data.get("type") == "archive"


    def _exit_archive(self):
        """Выйти из архива обратно в папку где он лежит"""
        self._archive_mode = False
        self._archive_path = ""
        self._archive_prefix = ""
        # возвращаемся в папку архива
        if self._archive_parent_dir and os.path.isdir(self._archive_parent_dir):
            self.load_directory(self._archive_parent_dir)
        else:
            self.load_directory(self.current_path)


    def _safe_join(self, base_dir: str, target: str) -> str:
        # target может быть "folder/file.txt" из архива
        dest = os.path.abspath(os.path.join(base_dir, target))
        base = os.path.abspath(base_dir)
        if not dest.startswith(base + os.sep) and dest != base:
            raise RuntimeError(f"Unsafe path in archive: {target}")
        return dest


    def _is_archive(self, path: str) -> bool:
        if not os.path.isfile(path):
            return False
        p = path.lower()
        return p.endswith(".zip") or p.endswith(".tar") or p.endswith(".tar.gz") or p.endswith(".tgz")


    def show_context_menu(self, position: QPoint):
        menu = CustomContextMenu()
        clicked_item = self.file_list.itemAt(position)
        if clicked_item is not None:
            data = clicked_item.data(Qt.ItemDataRole.UserRole)
            # ✅ ПКМ отключаем только по виртуальным элементам архива (dict)
            if isinstance(data, dict) and data.get("type") == "archive":
                return

        # Проверяем: клик по элементу или по пустому месту
        clicked_item = self.file_list.itemAt(position)
        selected_items = self.file_list.selectedItems()

        # Если клик по пустому месту — снимаем выделение (как в Windows)
        if clicked_item is None:
            self.file_list.clearSelection()
            selected_items = []

            # ✅ Только на пустом месте показываем создание
            new_file_action = menu.addAction(self.tr("New File"))
            new_file_action.triggered.connect(self.create_new_file)

            new_folder_action = menu.addAction(self.tr("New Folder"))
            new_folder_action.triggered.connect(self.create_new_folder)

            menu.addSeparator()

        # ---- Действия для выделенных файлов/папок ----
        if selected_items:
            # paths = [it.data(Qt.ItemDataRole.UserRole) for it in selected_items]
            paths = []
            arc_entries = []

            for it in selected_items:
                d = it.data(Qt.ItemDataRole.UserRole)
                if isinstance(d, dict) and d.get("type") == "archive":
                    arc_entries.append(d)
                else:
                    paths.append(d)  # обычные файловые пути (строки)


            # ✅ Подменю как на скрине: Archive ▶
            # archive_menu = menu.addMenu(self.tr("Archive"))
            archive_menu = CustomContextMenu(menu)
            archive_menu.setTitle(self.tr("Archive"))
            archive_menu.setStyleSheet(menu.styleSheet())  # на всякий случай, если стиль задан через setStyleSheet
            menu.addMenu(archive_menu)

            create_zip_action = archive_menu.addAction(self.tr("Add to archive..."))  # аналог "Добавить в архив..."
            create_zip_action.triggered.connect(self.create_zip_from_selection)

            # Если выбран ровно 1 архив — показать распаковку/открытие внутри подменю
            # if len(paths) == 1 and self._is_archive(paths[0]):
            if len(paths) == 1 and isinstance(paths[0], (str, bytes, os.PathLike)) and self._is_archive(paths[0]):
                archive_menu.addSeparator()

                open_arc = archive_menu.addAction(self.tr("Open archive"))
                # open_arc.triggered.connect(lambda: self.open_archive_view(paths[0]))
                open_arc.triggered.connect(lambda: self.open_archive_in_place(paths[0], ""))

                extract_here = archive_menu.addAction(self.tr("Extract here"))
                extract_here.triggered.connect(lambda: self.extract_archive(paths[0], None))

                # extract_to = archive_menu.addAction(self.tr("Extract to..."))
                # def _extract_to():
                #     folder = CustomFileDialog.getExistingDirectory(self, self.tr("Select folder"))
                #     if folder:
                #         self.extract_archive(paths[0], folder)
                # extract_to.triggered.connect(_extract_to)

            menu.addSeparator()

            delete_action = menu.addAction(self.tr("Delete"))
            delete_action.triggered.connect(self.delete_selected_items)

            if len(selected_items) == 1:
                rename_action = menu.addAction(self.tr("Rename"))
                rename_action.triggered.connect(self.rename_item)

            copy_action = menu.addAction(self.tr("Copy"))
            copy_action.triggered.connect(lambda: self.copy_selected_items("copy"))

            cut_action = menu.addAction(self.tr("Cut"))
            cut_action.triggered.connect(lambda: self.copy_selected_items("cut"))

            menu.addSeparator()

        # Open in CMD только для одной папки
        # if len(selected_items) == 1 and os.path.isdir(selected_items[0].data(Qt.ItemDataRole.UserRole)):
        if len(selected_items) == 1:
            d0 = selected_items[0].data(Qt.ItemDataRole.UserRole)
            if isinstance(d0, (str, bytes, os.PathLike)) and os.path.isdir(d0):
                open_cmd_action = menu.addAction(self.tr("Open in CMD"))
                open_cmd_action.triggered.connect(lambda: self.open_in_cmd(selected_items[0]))

        # Paste если есть что вставить
        if self.clipboard:
            paste_action = menu.addAction(self.tr("Paste"))
            paste_action.triggered.connect(self.paste_items)

        # Open in Notebook / VSCode только для файлов (только если UserRole = путь)
        if len(selected_items) == 1:
            d0 = selected_items[0].data(Qt.ItemDataRole.UserRole)
            if isinstance(d0, (str, bytes, os.PathLike)) and os.path.isfile(d0):
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
        raw = self.path_edit.text()
        path = self._map_dot_path(raw)

        # чтобы поле тоже обновилось (безопасно)
        if path != raw:
            self.path_edit.setText(path)

        if os.path.exists(path) and os.path.isdir(path):
            self.load_directory(path)
        else:
            StellarMessageBox.warning(self, self.tr("Error"), self.tr("Invalid path"))

    def _in_archive(self) -> bool:
        return bool(getattr(self, "_archive_mode", False))

    def _guard_archive(self, fn, *args, **kwargs):
        # в архиве — просто игнорируем действие
        if self._in_archive():
            return
        return fn(*args, **kwargs)

    def _is_archive_history(self, s: str) -> bool:
        return isinstance(s, str) and "::" in s

    def _open_history_entry(self, entry: str):
        # entry может быть обычной папкой или "zip::prefix"
        if self._is_archive_history(entry):
            arc, pref = entry.split("::", 1)
            arc = arc.strip()
            pref = pref.strip().strip("/").strip("\\")
            self.open_archive_in_place(arc, pref)
        else:
            self.load_directory(entry)


    def load_directory(self, path, add_history=True):
        # ✅ если загружаем реальную папку — значит мы НЕ в архиве
        self._archive_mode = False
        self._archive_path = ""
        self._archive_prefix = ""
        self._archive_parent_dir = ""
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
        # --- tabs: обновляем путь вкладки сразу ---
        if hasattr(self, "tab_bar"):
            cur = self.tab_bar.currentIndex()
            if cur >= 0:
                # обновим список путей
                if cur < len(self._tabs_paths):
                    self._tabs_paths[cur] = path

                # обновим текст/tooltip вкладки
                self.tab_bar.setTabToolTip(cur, path)
                self.tab_bar.setTabText(cur, self._tab_title_for_path(path))

                # обновим стейт вкладки (чтобы при сохранении не стали одинаковые)
                self._ensure_tab_state(cur, path)
                self._tabs[cur]["path"] = path


        # Обновление истории
        if add_history:
            if not self.history or (self.history and self.history[self.history_index] != path):
                self.history = self.history[:self.history_index + 1]
                self.history.append(path)
                self.history_index += 1
        # сохраняем стейт текущей вкладки после обновления истории
        try:
            cur = self.tab_bar.currentIndex()
            if cur >= 0:
                self._save_tab_state(cur)
        except:
            pass
        self.update_nav_buttons()

        # Служебные папки, которые скрываем
        # excluded_folders = {"bin", ".git", "__pycache__"}
        # # Добавляем папки и файлы в QListWidget, игнорируя служебные
        # for name in sorted(items, key=lambda s: s.lower()):
        #     if name.lower() in excluded_folders:
        #         continue  # пропускаем служебные папки
        excluded_folders = {"bin", ".git", "__pycache__"}

        show_system = getattr(self, "show_system_folders", False)

        for name in sorted(items, key=lambda s: s.lower()):
            # когда System выключен — скрываем служебное и "точечные" папки/файлы
            if not show_system:
                if name.lower() in excluded_folders or name.startswith("."):
                    continue

            full_path = os.path.join(path, name)
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, full_path)
            item.setIcon(self.get_icon(full_path))

            # ✅ ВАЖНО: drag можно всем, drop — только папкам
            flags = item.flags() | Qt.ItemFlag.ItemIsDragEnabled

            if os.path.isdir(full_path):
                flags |= Qt.ItemFlag.ItemIsDropEnabled     # папка принимает drop
            else:
                flags &= ~Qt.ItemFlag.ItemIsDropEnabled    # файл НЕ принимает drop

            item.setFlags(flags)

            self.file_list.addItem(item)



            # full_path = os.path.join(path, name)
            # item = QListWidgetItem(name)
            # item.setData(Qt.ItemDataRole.UserRole, full_path)
            # icon = self.get_icon(full_path)
            # item.setIcon(icon)
            # self.file_list.addItem(item)


        self.status_label.setText(self.tr("Loaded directory: {}").format(path))

    def update_nav_buttons(self):
        self.back_button.setEnabled(self.history_index > 0)
        self.forward_button.setEnabled(self.history_index < len(self.history) - 1)

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self._open_history_entry(self.history[self.history_index])

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._open_history_entry(self.history[self.history_index])


    def go_up(self):
        if getattr(self, "_archive_mode", False):
            # если внутри архива мы в подпапке — поднимаемся на уровень выше
            pref = (self._archive_prefix or "").replace("\\", "/").strip("/")
            if pref:
                parent = "/".join(pref.split("/")[:-1])
                self.open_archive_in_place(self._archive_path, parent)
            else:
                # если мы в корне архива — выйти из архива
                self._exit_archive()
            return

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


    def on_item_double_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)

        # --- если мы в режиме архива ---
        if getattr(self, "_archive_mode", False) and self._is_archive_item(data):
            if data.get("is_dir"):
                # зайти в папку внутри архива
                self.open_archive_in_place(data["archive"], data["inner"])
            else:
                # файл внутри архива: пока просто ничего не делаем (можно потом "extract+open")
                # либо можно сделать "Extract here" для выбранного
                pass
            return

        # --- обычный режим ---
        path = data
        if os.path.isdir(path):
            self.load_directory(path)
            return

        if self._is_archive(path):
            self.open_archive_in_place(path, "")
            return




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



    def dragMoveEvent(self, event):
        """Дозволяє рух перетягуваних елементів"""
        event.acceptProposedAction()

    def _on_tab_moved(self, frm: int, to: int):
        """После перетаскивания вкладок переупорядочиваем стейт, чтобы не путались пути/история."""
        try:
            if frm == to:
                return

            count = self.tab_bar.count()
            if count <= 0:
                return

            # old order states by index
            states = [self._tabs.get(i) for i in range(count)]
            paths  = list(self._tabs_paths)

            # move in lists
            st = states.pop(frm)
            states.insert(to, st)

            p = paths.pop(frm)
            paths.insert(to, p)

            # rebuild dict by new order
            self._tabs = {i: states[i] for i in range(len(states))}
            self._tabs_paths = paths

            # prev index поправим на текущую активную
            self._prev_tab_index = self.tab_bar.currentIndex()

            self._save_tabs_session()
        except Exception as e:
            print(f"[EXPLORER] tab move error: {e}")



    def startDrag(self, supportedActions):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        mime_data = QMimeData()
        urls = []

        for item in selected_items:
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                abs_path = os.path.abspath(path)
                if os.path.exists(abs_path):
                    urls.append(QUrl.fromLocalFile(abs_path))

        if not urls:
            return

        mime_data.setUrls(urls)
        # иногда помогает (не обязательно, но полезно)
        mime_data.setText("\n".join([u.toLocalFile() for u in urls]))

        drag = QDrag(self.file_list)
        drag.setMimeData(mime_data)

        # разрешаем и Copy и Move, default = Copy
        drag.exec(
            Qt.DropAction.CopyAction | Qt.DropAction.MoveAction,
            Qt.DropAction.CopyAction
        )


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
    def open_selected_item(self):
        """Открыть выбранный элемент по Enter (как двойной клик)."""
        items = self.file_list.selectedItems() if hasattr(self, "file_list") else []
        if not items:
            return
        try:
            self.on_item_double_clicked(items[0])
        except Exception as e:
            # чтобы проводник не падал из-за одного файла/элемента
            try:
                StellarMessageBox.warning(
                    self, self.tr("Error"),
                    self.tr("Could not open: {}").format(str(e))
                )
            except Exception:
                pass


    def focus_search(self):
        """F3 — фокус в поле поиска."""
        w = getattr(self, "search_edit", None)
        if w is None:
            w = getattr(self, "search_input", None)
        if w is None:
            w = getattr(self, "search_box", None)

        if w is not None:
            w.setFocus()
            try:
                w.selectAll()
            except Exception:
                pass


    def focus_path(self):
        """F4 — фокус в поле пути."""
        w = getattr(self, "path_edit", None)
        if w is not None:
            w.setFocus()
            try:
                w.selectAll()
            except Exception:
                pass

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
            activated=lambda: self._guard_archive(self.delete_selected_items)
        )

        # F2 — Переименовать
        self.sc_rename = QShortcut(
            QKeySequence(Qt.Key.Key_F2),
            self,
            activated=lambda: self._guard_archive(self.rename_item)
        )


        # === Буфер обмена (стандартные шорткаты, не зависят от раскладки) ===

        # Copy
        self.sc_copy = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Copy),
            self,
            activated=lambda: self._guard_archive(self.copy_selected_items, "copy")
        )

        # Cut
        self.sc_cut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Cut),
            self,
            activated=lambda: self._guard_archive(self.copy_selected_items, "cut")
        )

        # Paste
        self.sc_paste = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Paste),
            self,
            activated=lambda: self._guard_archive(self.paste_items)
        )

        # Select All
        self.sc_select_all = QShortcut(
            QKeySequence(QKeySequence.StandardKey.SelectAll),
            self,
            activated=lambda: self.file_list.selectAll()
        )

        # Enter — открыть выбранное (папку / архив / папку в архиве)
        self.sc_open_enter = QShortcut(
            QKeySequence(Qt.Key.Key_Return),
            self.file_list,
            activated=self.open_selected_item
        )
        self.sc_open_enter2 = QShortcut(
            QKeySequence(Qt.Key.Key_Enter),
            self.file_list,
            activated=self.open_selected_item
        )
        # ✅ Enter работает только когда фокус на списке файлов
        self.sc_open_enter.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.sc_open_enter2.setContext(Qt.ShortcutContext.WidgetShortcut)


        # F3 — фокус в поиск
        self.sc_focus_search = QShortcut(
            QKeySequence(Qt.Key.Key_F3),
            self,
            activated=self.focus_search
        )

        # F4 — фокус в путь
        self.sc_focus_path = QShortcut(
            QKeySequence(Qt.Key.Key_F4),
            self,
            activated=self.focus_path
        )


        print("[EXPLORER] Hotkeys initialized (layout-friendly).")