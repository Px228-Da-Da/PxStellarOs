import sys
import os
import json
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *

# Ensure QAbstractItemView is available (dependencies may not export it)
try:
    from PyQt6.QtWidgets import QAbstractItemView
except Exception:
    try:
        from PyQt5.QtWidgets import QAbstractItemView  # type: ignore
    except Exception:
        QAbstractItemView = None  # fallback; we will guard usage

# Ensure QPen is available (dependencies may not export it)
try:
    from PyQt6.QtGui import QPen
except Exception:
    try:
        from PyQt5.QtGui import QPen  # type: ignore
    except Exception:
        QPen = None  # fallback; paintEvent will guard



# --- Win11-like connecting animation (spinner dots in Wi‑Fi icon) ---
class ConnectingSpinner(QWidget):
    """
    Lightweight dot-spinner (Windows 11-like) used inside the Wi‑Fi icon slot.
    """
    def __init__(self, parent=None, size=24):
        super().__init__(parent)
        self._size = int(size)
        self._step = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self.setFixedSize(self._size, self._size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def start(self):
        if not self._timer.isActive():
            self._step = 0
            self._timer.start(60)  # smooth enough, cheap

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()
        self.update()

    def _tick(self):
        self._step = (self._step + 1) % 12
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0

        # dot ring
        dots = 12
        radius = min(w, h) * 0.35
        dot_r = max(1.6, min(w, h) * 0.06)

        # accent blue (Win11-ish)
        base = QColor(0, 120, 212)

        for i in range(dots):
            # make the "leading" dot brightest
            rel = (i - self._step) % dots
            # 0 -> brightest, farther -> dimmer
            alpha = int(40 + (1.0 - (rel / (dots - 1))) * 185)
            c = QColor(base)
            c.setAlpha(alpha)

            ang = (2.0 * math.pi * i) / dots
            x = cx + radius * math.cos(ang)
            y = cy + radius * math.sin(ang)

            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(c))
            p.drawEllipse(QPointF(x, y), dot_r, dot_r)


class WifiIconSlot(QWidget):
    """
    A small container that can show either a Wi‑Fi icon pixmap or a connecting spinner.
    """
    def __init__(self, parent=None, size=26):
        super().__init__(parent)
        self.setFixedSize(int(size), int(size))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._icon = QLabel(self)
        self._icon.setFixedSize(self.size())
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._spinner = ConnectingSpinner(self, size=int(size))
        self._spinner.move(0, 0)
        self._spinner.hide()

    def set_icon(self, pix: QPixmap):
        self._icon.setPixmap(pix)
        self._icon.show()

    def set_connecting(self, connecting: bool):
        if connecting:
            self._spinner.show()
            self._spinner.start()
        else:
            self._spinner.stop()
            self._spinner.hide()

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
USER_CONFIG_PATH = os.path.join(BASE_DIR, "root", "bin", "user.config")


def get_current_username():
    try:
        if not os.path.exists(USER_CONFIG_PATH):
            return "Unknown User"
        with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        return config_data.get("user_name", "Unknown User")
    except Exception:
        return "Unknown User"


GLOBAL_USERNAME = get_current_username()


class WifiPasswordManager:
    def __init__(self, filename=None):
        if filename is None:
            wifi_dir = os.path.join(BASE_DIR, "root", GLOBAL_USERNAME, "wifi")
            os.makedirs(wifi_dir, exist_ok=True)
            filename = os.path.join(wifi_dir, "wifi_passwords.json")
        self.filename = filename
        self.passwords = {}
        self.load_passwords()

    def load_passwords(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.passwords = json.load(f)
            except Exception:
                self.passwords = {}

    def save_passwords(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.passwords, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_password(self, ssid):
        return self.passwords.get(ssid)

    def save_password(self, ssid, password):
        self.passwords[ssid] = password
        self.save_passwords()

    def forget(self, ssid):
        if ssid in self.passwords:
            del self.passwords[ssid]
            self.save_passwords()


class Win11NetworkRow(QWidget):
    """
    Windows 11-like Wi‑Fi list row (light theme).
    NOTE: This widget is intended to be embedded into a QListWidget via setItemWidget.
    """

    def __init__(self, parent, ssid: str, signal_percent: int, locked: bool, saved: bool, connected: bool):
        super().__init__(parent)
        self.ssid = ssid
        self.signal_percent = int(signal_percent)
        self.locked = bool(locked)
        self.saved = bool(saved)
        self.connected = bool(connected)

        self.setObjectName("netRow")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)

        self.icon_slot = WifiIconSlot(self, size=26)
        lay.addWidget(self.icon_slot)

        col = QVBoxLayout()
        col.setSpacing(2)

        self.lbl_name = QLabel(ssid)
        self.lbl_name.setObjectName("netName")
        self.lbl_meta = QLabel("")
        self.lbl_meta.setObjectName("netMeta")

        col.addWidget(self.lbl_name)
        col.addWidget(self.lbl_meta)

        lay.addLayout(col, 1)

        self.badge = QLabel("")
        self.badge.setObjectName("netBadge")
        self.badge.hide()
        lay.addWidget(self.badge)

        self.refresh()

    def refresh(self):
        # Windows 11 list uses simple descriptors rather than percentages
        meta = []
        if self.connected:
            meta.append("Connected")
        else:
            meta.append("Secured" if self.locked else "Open")

        # Subtle "saved" hint (optional)
        if self.saved and not self.connected:
            meta.append("saved")

        self.lbl_meta.setText("  •  ".join(meta))

        if self.connected:
            self.badge.setText("✓")
            self.badge.show()
        else:
            self.badge.hide()


class Win11InlineConnect(QFrame):
    """
    Inline expanded connect panel (like Windows 11 Wi‑Fi flyout expanded item).
    Emits connect request via callbacks (parent handles).
    """

    def __init__(self, parent, ssid: str, tr=lambda x: x):
        super().__init__(parent)
        self.tr = tr
        self.ssid = ssid

        self.setObjectName("inlinePanel")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        self.title = QLabel(ssid)
        self.title.setObjectName("inlineTitle")
        lay.addWidget(self.title)

        self.sub = QLabel(self.tr("Secured"))
        self.sub.setObjectName("inlineSub")
        lay.addWidget(self.sub)

        self.label = QLabel(self.tr("Enter network security key"))
        self.label.setObjectName("inlineLabel")
        lay.addWidget(self.label)

        self.edit = QLineEdit()
        self.edit.setObjectName("inlineEdit")
        self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit.setPlaceholderText(self.tr("Network security key"))
        # Win11-like vertical centering (avoid weird padding/clipping)
        try:
            # Fixed control height similar to Windows 11
            self.edit.setFixedHeight(34)
            # Qt sometimes renders text baseline off; force vertical centering
            try:
                self.edit.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            except Exception:
                # PyQt5 fallback
                self.edit.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

            fm = self.edit.fontMetrics()
            h = self.edit.height() or 34
            vpad = max(0, int((h - fm.height()) / 2) - 1)
            self.edit.setTextMargins(10, vpad, 10, vpad)
        except Exception:
            pass
        lay.addWidget(self.edit)

        self.show_chars = QCheckBox(self.tr("Show characters"))
        self.show_chars.setObjectName("inlineCheck")
        self.show_chars.toggled.connect(self._toggle_chars)
        lay.addWidget(self.show_chars)
        
        btnrow = QHBoxLayout()
        btnrow.addStretch(1)

        self.btn_cancel = QPushButton(self.tr("Cancel"))
        self.btn_cancel.setObjectName("inlineCancel")
        btnrow.addWidget(self.btn_cancel)

        self.btn_connect = QPushButton(self.tr("Connect"))
        self.btn_connect.setObjectName("inlineConnect")
        btnrow.addWidget(self.btn_connect)

        lay.addLayout(btnrow)

        self.edit.returnPressed.connect(self.btn_connect.click)

    def _toggle_chars(self, checked: bool):
        self.edit.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)

    def password(self) -> str:
        return self.edit.text()

    def set_focus(self):
        QTimer.singleShot(0, self.edit.setFocus)

class Win11InlineConnecting(QFrame):
    def __init__(self, parent, ssid: str, tr=lambda x: x):
        super().__init__(parent)
        self.tr = tr
        self.ssid = ssid

        self.setObjectName("inlinePanel")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        self.title = QLabel(ssid)
        self.title.setObjectName("inlineTitle")
        lay.addWidget(self.title)

        self.status = QLabel(self.tr("Checking network requirements"))
        self.status.setObjectName("inlineSub")
        lay.addWidget(self.status)

        # 🔥 Progress bar (marquee)
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)   # ← бесконечная анимация
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(4)
        self.bar.setObjectName("inlineProgress")
        lay.addWidget(self.bar)

        btnrow = QHBoxLayout()
        btnrow.addStretch(1)

        self.btn_cancel = QPushButton(self.tr("Cancel"))
        self.btn_cancel.setObjectName("inlineCancel")
        btnrow.addWidget(self.btn_cancel)

        lay.addLayout(btnrow)


class Wifi(QWidget):
    """
    Windows 11 Wi‑Fi flyout (light theme, inline expanded connect like the screenshot):
    - Top bar: "Wi‑Fi" + toggle
    - Wi‑Fi networks list
    - Expanded inline connect panel inserted right under selected secured network
    - Bottom link: "More Wi‑Fi settings"
    """

    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else (lambda x: x)
        self.lang_code = lang_code

        self.password_manager = WifiPasswordManager()

        self.setWindowTitle(self.tr("Wi‑Fi"))
        self.setFixedSize(350, 505)

        # Acrylic-ish window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Wi‑Fi backend
        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0] if self.wifi.interfaces() else None


        # Scan state (prevents scanning when Wi‑Fi is toggled off)
        self._wifi_enabled = True

        # Timers (so we can cancel pending scan callbacks when Wi‑Fi is turned off)
        self._scan_timer = QTimer(self)
        self._scan_timer.setSingleShot(True)
        self._scan_timer.timeout.connect(self._perform_scan)

        self._scan_results_timer = QTimer(self)
        self._scan_results_timer.setSingleShot(True)
        self._scan_results_timer.timeout.connect(self._process_scan_results)
        self._last_connect = {"ssid": None, "used_saved": False}

        # Inline expand state
        self._expanded_item = None
        self._expanded_widget = None
        self._expanded_ssid = None

        # ===== Layout =====
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # Top bar
        top = QFrame()
        top.setObjectName("topBar")
        t = QHBoxLayout(top)
        t.setContentsMargins(12, 10, 12, 10)
        t.setSpacing(10)

        self.lbl_title = QLabel(self.tr("Wi‑Fi"))
        self.lbl_title.setObjectName("topTitle")
        t.addWidget(self.lbl_title, 1)

        self.toggle_switch = ToggleSwitch(self)
        if hasattr(self.toggle_switch, "toggled"):
            self.toggle_switch.toggled.connect(self.toggle_wifi)
        elif hasattr(self.toggle_switch, "stateChanged"):
            self.toggle_switch.stateChanged.connect(lambda v: self.toggle_wifi(bool(v)))
        else:
            self.toggle_switch.installEventFilter(self)
        t.addWidget(self.toggle_switch)

        root.addWidget(top)

        # Status line (small, like Windows uses under title area)
        self.lbl_status = QLabel(self.tr("Not connected"))
        self.lbl_status.setObjectName("statusLine")
        root.addWidget(self.lbl_status)

        # Network list
        self.net_list = QListWidget()
        self.net_list.setObjectName("netList")
        self.net_list.setVerticalScrollBar(CastScrollBar(Qt.Orientation.Vertical))
        self.net_list.setHorizontalScrollBar(CastScrollBar(Qt.Orientation.Horizontal))
        self.net_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection if QAbstractItemView is not None else 1)
        self.net_list.setSpacing(6)
        self.net_list.itemClicked.connect(self._on_network_clicked)
        root.addWidget(self.net_list, 1)

        # === Bottom bar (More settings + Refresh) ===
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        self.btn_settings = QPushButton(self.tr("More Wi-Fi settings"))
        self.btn_settings.setObjectName("settingsLink")
        self.btn_settings.clicked.connect(self._open_settings_stub)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setObjectName("refreshButton")
        self.btn_refresh.setFixedSize(30, 30)
        # self.btn_refresh.setToolTip(self.tr("Refresh"))
        self.btn_refresh.clicked.connect(self.scan_networks)

        # Иконка обновления
        refresh_icon = QIcon.fromTheme("view-refresh")
        if refresh_icon.isNull():
            refresh_icon = QIcon("bin/icons/local_icons/system/refresh.png")  # если есть
        self.btn_refresh.setIcon(refresh_icon)
        self.btn_refresh.setIconSize(QSize(16, 16))


        # Disabled if Wi‑Fi toggle is off
        try:
            self.btn_refresh.setEnabled(bool(self.toggle_switch.isChecked()))
        except Exception:
            pass
        bottom.addWidget(self.btn_settings, 1)
        bottom.addWidget(self.btn_refresh)

        root.addLayout(bottom)

        # Style (Windows 11 dark-ish)
        self.setStyleSheet('''
            QWidget { font-family: 'Segoe UI', sans-serif; }

            #topBar {
                background: rgba(32,32,32,220);
                border: 1px solid rgba(255,255,255,18);
                border-radius: 14px;
            }
            #topTitle { font-size: 14px; font-weight: 600; color: rgba(255,255,255,235); }

            #statusLine { color: rgba(255,255,255,140); font-size: 11px; padding-left: 6px; }

            #netList {
                background: rgba(28,28,28,185);
                border: 1px solid rgba(255,255,255,16);
                border-radius: 14px;
                padding: 6px;
            }
            QListWidget::item { border: none; padding: 0px; margin: 0px; }
            QListWidget::item:selected { background: transparent; }

            #netRow {
                background: rgba(40,40,40,220);
                border: 1px solid rgba(255,255,255,14);
                border-radius: 12px;
            }
            #netRow:hover {
                background: rgba(52,52,52,235);
                border: 1px solid rgba(0,120,212,160);
            }
            #netName { font-size: 12.5px; font-weight: 600; color: rgba(255,255,255,235); }
            #netMeta { font-size: 10.5px; color: rgba(255,255,255,150); }

            #netBadge {
                min-width: 22px;
                min-height: 22px;
                border-radius: 11px;
                background: rgba(0,120,212,230);
                color: white;
                font-weight: 800;
                qproperty-alignment: AlignCenter;
            }

            #inlinePanel {
                background: rgba(42,42,42,235);
                border: 1px solid rgba(255,255,255,14);
                border-radius: 12px;
            }
            #inlineTitle { font-size: 12.5px; font-weight: 700; color: rgba(255,255,255,235); }
            #inlineSub, #inlineLabel { font-size: 10.5px; color: rgba(255,255,255,150); }
            #inlineHint { font-size: 10.5px; color: rgba(255,255,255,130); }

            #inlineEdit {
                min-height: 32px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,22);
                background: rgba(20,20,20,235);
                color: rgba(255,255,255,235);
                font-size: 11.5px;
            }
            #inlineEdit:focus { border: 1px solid rgba(0,120,212,210); }

            #inlineCheck { color: rgba(255,255,255,150); }

            #inlineConnect {
                height: 30px;
                padding: 0 14px;
                border-radius: 10px;
                background: rgb(0,120,212);
                color: #fff;
                border: none;
            }
            #inlineConnect:hover { background: rgb(0,105,185); }

            #inlineCancel {
                height: 30px;
                padding: 0 14px;
                border-radius: 10px;
                background: rgba(255,255,255,0);
                color: rgba(255,255,255,210);
                border: 1px solid rgba(255,255,255,22);
            }
            #inlineCancel:hover { background: rgba(255,255,255,8); }

            #settingsLink {
                height: 30px;
                border-radius: 10px;
                background: rgba(32,32,32,220);
                border: 1px solid rgba(255,255,255,14);
                color: rgb(125, 190, 255);
                font-size: 11px;
                text-align: left;
                padding-left: 10px;
            }
            #settingsLink:hover { background: rgba(44,44,44,235); }

            #inlineProgress {
                border: none;
                background: rgba(255,255,255,18);
                border-radius: 2px;
            }
            #inlineProgress::chunk {
                background: rgb(180, 130, 255);
                border-radius: 2px;
            }

            #refreshButton {
                background: rgba(32,32,32,220);
                border: 1px solid rgba(255,255,255,14);
                border-radius: 8px;
            }
            #refreshButton:hover { background: rgba(44,44,44,235); }
            #refreshButton:pressed { background: rgba(255,255,255,10); }
        ''')


        self.update_current_network()
        
        # Respect the toggle state on startup
        try:
            initial_enabled = bool(self.toggle_switch.isChecked())
        except Exception:
            initial_enabled = True
        self.toggle_wifi(initial_enabled)

    def _show_connecting_panel(self, ssid: str):
        self._collapse_inline()

        anchor = self._find_item_by_ssid(ssid)
        if not anchor:
            return

        row = self.net_list.row(anchor)

        item = QListWidgetItem()
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setSizeHint(QSize(10, 140))

        panel = Win11InlineConnecting(self.net_list, ssid, tr=self.tr)
        panel.btn_cancel.clicked.connect(self._collapse_inline)

        self.net_list.insertItem(row + 1, item)
        self.net_list.setItemWidget(item, panel)

        self._expanded_item = item
        self._expanded_widget = panel
        self._expanded_ssid = ssid

        
    def paintEvent(self, event):
        # Light acrylic-ish background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0, 0, self.width(), self.height())
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor(24, 24, 24, 235))
        grad.setColorAt(1, QColor(14, 14, 14, 235))
        painter.setBrush(QBrush(grad))
        if QPen is not None:
            painter.setPen(QPen(QColor(0, 0, 0, 25), 1))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), 18, 18)

    def eventFilter(self, obj, event):
        if obj is getattr(self, "toggle_switch", None):
            if event.type() == QEvent.Type.MouseButtonRelease:
                try:
                    self.toggle_wifi(bool(self.toggle_switch.isChecked()))
                except Exception:
                    pass
        return super().eventFilter(obj, event)

    # ===== UI helpers =====
    def _open_settings_stub(self):
        StellarMessageBox.information(self, self.tr("Wi‑Fi"), self.tr("Open Settings is not wired here yet."))

    def _set_placeholder(self, text: str):
        self._collapse_inline()
        self.net_list.clear()
        item = QListWidgetItem()
        item.setSizeHint(QSize(10, 44))
        self.net_list.addItem(item)
        lbl = QLabel(text)
        lbl.setStyleSheet("padding: 10px; color: rgba(255,255,255,140);")
        self.net_list.setItemWidget(item, lbl)

    def _collapse_inline(self):
        if self._expanded_item is not None:
            try:
                row = self.net_list.row(self._expanded_item)
                if row >= 0:
                    it = self.net_list.takeItem(row)
                    del it
            except Exception:
                pass
        self._expanded_item = None
        self._expanded_widget = None
        self._expanded_ssid = None

    def _expand_inline_under(self, anchor_item: QListWidgetItem, ssid: str):
        self._collapse_inline()

        anchor_row = self.net_list.row(anchor_item)
        if anchor_row < 0:
            return

        inline_item = QListWidgetItem()
        inline_item.setFlags(Qt.ItemFlag.NoItemFlags)
        inline_item.setSizeHint(QSize(10, 205))

        panel = Win11InlineConnect(self.net_list, ssid, tr=self.tr)

        panel.btn_cancel.clicked.connect(self._collapse_inline)
        panel.btn_connect.clicked.connect(lambda: self._connect_from_inline(panel))
        panel.set_focus()

        self.net_list.insertItem(anchor_row + 1, inline_item)
        self.net_list.setItemWidget(inline_item, panel)

        self._expanded_item = inline_item
        self._expanded_widget = panel
        self._expanded_ssid = ssid

    def _connect_from_inline(self, panel: Win11InlineConnect):
        ssid = panel.ssid.strip()
        pwd = panel.password()
        if not ssid or not pwd:
            return
        self._show_connecting_panel(ssid)
        self._connect_to_network(ssid, pwd, used_saved=False, open_network=False)

    def _find_item_by_ssid(self, ssid: str):
        for i in range(self.net_list.count()):
            item = self.net_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(data, dict) and data.get("ssid") == ssid:
                return item
        return None


    def _set_row_connecting(self, ssid: str, connecting: bool):
        """Toggle the Win11 spinner in the Wi‑Fi icon for a given SSID (if present in the list)."""
        try:
            for i in range(self.net_list.count()):
                it = self.net_list.item(i)
                data = it.data(Qt.ItemDataRole.UserRole)
                if isinstance(data, dict) and data.get("ssid") == ssid:
                    w = self.net_list.itemWidget(it)
                    if hasattr(w, "set_connecting"):
                        w.set_connecting(connecting)
                    break
        except Exception:
            pass

    def _win_get_wifi_interface_name(self) -> str | None:
        """Try to detect Wi-Fi adapter interface name on Windows (e.g. 'Wi-Fi')."""
        if os.name != "nt":
            return None
        try:
            import subprocess, re
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            # Example line: "    Name                   : Wi-Fi"
            m = re.search(r"^\s*Name\s*:\s*(.+)$", out, flags=re.MULTILINE)
            if m:
                return m.group(1).strip()
        except Exception:
            pass
        return None


    def _set_system_wifi_enabled(self, enabled: bool):
        """
        Enable/disable Wi-Fi on the host OS.
        Windows: netsh
        Linux: nmcli (NetworkManager) or rfkill fallback
        """
        try:
            import subprocess
            if os.name == "nt":
                # Windows (как у тебя было)
                self._set_windows_wifi_enabled(enabled)
                return

            # Linux / other unix-like
            state = "on" if enabled else "off"

            # 1) NetworkManager
            try:
                subprocess.check_call(
                    ["nmcli", "radio", "wifi", state],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return
            except Exception:
                pass

            # 2) rfkill fallback (может требовать root)
            try:
                cmd = ["rfkill", "unblock", "wifi"] if enabled else ["rfkill", "block", "wifi"]
                subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except Exception:
                pass

            # Если ни один способ не сработал — просто молча выходим (UI всё равно выключится)
        except Exception:
            pass


    def _set_windows_wifi_enabled(self, enabled: bool):
        """
        Enable/disable Wi-Fi adapter in Windows.
        Requires admin rights in many setups.
        """
        if os.name != "nt":
            return

        name = self._win_get_wifi_interface_name() or "Wi-Fi"

        try:
            import subprocess
            admin_state = "enabled" if enabled else "disabled"
            subprocess.check_call(
                ["netsh", "interface", "set", "interface", f'name={name}', f"admin={admin_state}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            # If not admin / name mismatch / other issue, just ignore silently
            # (UI will still toggle off)
            pass


    # ===== Wi‑Fi logic =====
    def toggle_wifi(self, enabled: bool):
        # Keep a local flag so any pending timers can't repopulate the list when Wi-Fi is off
        self._wifi_enabled = bool(enabled)

        # Try to actually toggle Windows Wi-Fi adapter
        # (enable -> admin=enabled, disable -> disconnect + admin=disabled)
        try:
            if not self._wifi_enabled:
                # Disconnect via pywifi first (best effort)
                try:
                    if self.iface:
                        self.iface.disconnect()
                except Exception:
                    pass

                self._set_system_wifi_enabled(False)
            else:
                self._set_system_wifi_enabled(True)
        except Exception:
            pass

        # Refresh button (if present)
        try:
            self.btn_refresh.setEnabled(self._wifi_enabled)
        except Exception:
            pass

        if self._wifi_enabled:
            self.lbl_status.setText(self.tr("Not connected"))
            self.scan_networks()
        else:
            # Cancel pending scan callbacks
            try:
                if hasattr(self, "_scan_timer") and self._scan_timer.isActive():
                    self._scan_timer.stop()
                if hasattr(self, "_scan_results_timer") and self._scan_results_timer.isActive():
                    self._scan_results_timer.stop()
            except Exception:
                pass

            self._collapse_inline()
            self.net_list.clear()
            self.lbl_status.setText(self.tr("Wi-Fi is off"))
            self._set_placeholder(self.tr("Wi-Fi is off"))


    def _get_connected_ssid(self):
        try:
            import subprocess, re

            # Windows
            if os.name == "nt":
                out = subprocess.check_output(["netsh", "wlan", "show", "interfaces"],
                                              stderr=subprocess.STDOUT, universal_newlines=True)
                m = re.search(r"^\s*SSID\s*:\s*(.+)$", out, flags=re.MULTILINE)
                if m:
                    ssid = m.group(1).strip()
                    return ssid if ssid else None

            # Linux (NetworkManager)
            try:
                out = subprocess.check_output(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
                                              stderr=subprocess.STDOUT, universal_newlines=True)
                for line in out.splitlines():
                    # формат: "yes:MyWifi"
                    if line.startswith("yes:"):
                        ssid = line.split(":", 1)[1].strip()
                        return ssid if ssid else None
            except Exception:
                pass

            # Linux fallback: iwgetid
            try:
                out = subprocess.check_output(["iwgetid", "-r"],
                                              stderr=subprocess.STDOUT, universal_newlines=True).strip()
                return out if out else None
            except Exception:
                pass

        except Exception:
            pass

        # fallback на последнее SSID
        try:
            ssid = self._last_connect.get("ssid")
            return ssid if ssid else None
        except Exception:
            return None



    def update_current_network(self):
        if not self.iface:
            self.lbl_status.setText(self.tr("Wi-Fi adapter not found"))
            return

        if self.iface.status() == const.IFACE_CONNECTED:
            ssid = self._get_connected_ssid()
            if ssid:
                self.lbl_status.setText(f"{self.tr('Connected')} • {ssid}")
            else:
                self.lbl_status.setText(self.tr("Connected"))
        else:
            self.lbl_status.setText(self.tr("Not connected"))


    def get_signal_icon(self, signal_percent: int, locked: bool) -> QIcon:
        level = 0
        if signal_percent > 75:
            level = 4
        elif signal_percent > 50:
            level = 3
        elif signal_percent > 25:
            level = 2
        elif signal_percent > 0:
            level = 1
        icon_name = f"bin/icons/local_icons/system/wifi/wifi_signal_{level}{'_lock' if locked else ''}.png"
        return QIcon(icon_name)

    def signal_strength_to_percent(self, signal):
        signal = max(min(signal, -30), -90)
        return int((signal + 90) / 60 * 100)

    def scan_networks(self):
        if not self.iface:
            self._set_placeholder(self.tr("Wi‑Fi adapter not found"))
            return

        # Respect toggle state
        if not getattr(self, "_wifi_enabled", True):
            self._set_placeholder(self.tr("Wi‑Fi is off"))
            return

        self._collapse_inline()
        self._set_placeholder(self.tr("Scanning…"))

        # Start scan via a cancellable timer (instead of singleShot)
        try:
            self._scan_results_timer.stop()
        except Exception:
            pass
        self._scan_timer.start(0)

    def _perform_scan(self):
        # If Wi‑Fi was turned off while waiting, do nothing
        if not getattr(self, "_wifi_enabled", True):
            return
        try:
            self.iface.scan()
            # Use cancellable timer
            self._scan_results_timer.start(2300)
        except Exception as e:
            self._set_placeholder(f"{self.tr('Scan error')}: {e}")

    def _process_scan_results(self):
        if not self.iface:
            return
        # If Wi‑Fi was turned off while scanning, ignore results
        if not getattr(self, "_wifi_enabled", True):
            return

        self._collapse_inline()
        self.net_list.clear()

        try:
            results = self.iface.scan_results()
            seen = set()
            nets = []
            for n in results:
                if not n.ssid:
                    continue
                if n.ssid in seen:
                    continue
                seen.add(n.ssid)
                sig = self.signal_strength_to_percent(n.signal)
                locked = const.AKM_TYPE_NONE not in n.akm
                saved = self.password_manager.get_password(n.ssid) is not None
                nets.append((n.ssid, sig, locked, saved))

            # Saved networks first, then by signal
            nets.sort(key=lambda x: (not x[3], -x[1], x[0].lower()))

            if not nets:
                self._set_placeholder(self.tr("No available networks"))
                self.update_current_network()
                return

            for ssid, sig, locked, saved in nets:
                self._add_network(ssid, sig, locked, saved)

            self.update_current_network()

        except Exception as e:
            self._set_placeholder(f"{self.tr('Error')}: {e}")

    def _add_network(self, ssid: str, sig: int, locked: bool, saved: bool):
        roww = Win11NetworkRow(self, ssid, sig, locked, saved, connected=False)
        roww.icon_slot.set_icon(self.get_signal_icon(sig, locked).pixmap(24, 24))
        item = QListWidgetItem()
        item.setSizeHint(QSize(10, 54))
        item.setData(Qt.ItemDataRole.UserRole, {"ssid": ssid, "sig": sig, "locked": locked, "saved": saved})
        self.net_list.addItem(item)
        self.net_list.setItemWidget(item, roww)

    def _on_network_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole) if item else None
        if not isinstance(data, dict):
            return

        ssid = data.get("ssid")
        locked = bool(data.get("locked"))
        if not ssid:
            return

        # If clicked the same SSID that is already expanded, collapse (Win11-like toggle)
        if self._expanded_ssid == ssid:
            self._collapse_inline()
            return

        saved_pwd = self.password_manager.get_password(ssid)

        # Saved -> connect immediately
        if saved_pwd:
            self._collapse_inline()
            self._connect_to_network(ssid, saved_pwd, used_saved=True, open_network=False)
            return

        # Secured -> expand inline panel (like Windows 11 screenshot)
        if locked:
            self._expand_inline_under(item, ssid)
            return

        # Open network -> connect directly
        self._collapse_inline()
        self._connect_to_network(ssid, "", used_saved=False, open_network=True)

    def _connect_to_network(self, ssid: str, password: str, used_saved: bool, open_network: bool):
        if not self.iface:
            StellarMessageBox.warning(self, self.tr("Wi‑Fi"), self.tr("Wi‑Fi adapter not found"))
            return

        self._last_connect = {"ssid": ssid, "used_saved": used_saved}
        self.lbl_status.setText(self.tr("Connecting…"))

        self._set_row_connecting(ssid, True)

        try:
            profile = pywifi.Profile()
            profile.ssid = ssid
            profile.auth = const.AUTH_ALG_OPEN

            if open_network:
                profile.akm = [const.AKM_TYPE_NONE]
                profile.cipher = const.CIPHER_TYPE_NONE
                profile.key = ""
            else:
                profile.akm = [const.AKM_TYPE_WPA2PSK]
                profile.cipher = const.CIPHER_TYPE_CCMP
                profile.key = password

            self.iface.remove_all_network_profiles()
            tmp_profile = self.iface.add_network_profile(profile)
            self.iface.connect(tmp_profile)

            QTimer.singleShot(4500, lambda: self._check_connection_status(ssid, password, open_network))
        except Exception as e:
            self._set_row_connecting(ssid, False)
            StellarMessageBox.warning(self, self.tr("Wi‑Fi"), f"{self.tr('Connection error')}: {e}")
            self.update_current_network()

    def _check_connection_status(self, ssid: str, password: str, open_network: bool):
        self._set_row_connecting(ssid, False)
        if not self.iface:
            return

        if self.iface.status() == const.IFACE_CONNECTED:
            self._collapse_inline()
            # self.lbl_status.setText(self.tr("Connected"))
            self.update_current_network()
            if not open_network and password and not self._last_connect.get("used_saved"):
                self.password_manager.save_password(ssid, password)
            self.scan_networks()
            return

        # Failed: if saved failed, re-open inline panel to enter new key
        used_saved = bool(self._last_connect.get("used_saved")) and self._last_connect.get("ssid") == ssid
        if used_saved and not open_network:
            anchor = self._find_item_by_ssid(ssid)
            if anchor:
                self._expand_inline_under(anchor, ssid)
            return

        StellarMessageBox.warning(self, self.tr("Wi‑Fi"), self.tr("Failed to connect"))
        self.update_current_network()

        if not open_network:
            anchor = self._find_item_by_ssid(ssid)
            if anchor:
                self._expand_inline_under(anchor, ssid)
        else:
            self._collapse_inline()

