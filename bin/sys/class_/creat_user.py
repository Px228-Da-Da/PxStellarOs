
from __future__ import annotations

import os, sys, json, time, math, random
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QStackedWidget, QGraphicsOpacityEffect, QFrame, QApplication,
    QSpacerItem, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRegularExpression
from PyQt6.QtGui import QFont, QPainter, QRadialGradient, QColor, QBrush, QRegularExpressionValidator


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *


class SoftGlowBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._t = 0.0
        self._speed = 0.3
        self._last_time = time.time()

        self.colors = [
            QColor(90, 160, 255, 120),
            QColor(150, 120, 255, 120),
            QColor(80, 200, 255, 120),
            QColor(100, 180, 255, 120)
        ]
        self.current_color = self.colors[0]
        self.next_color = random.choice(self.colors[1:])
        self.color_blend = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def animate(self):
        now = time.time()
        dt = now - self._last_time
        self._last_time = now
        self._t += dt * self._speed

        self.color_blend += dt * 0.05
        if self.color_blend >= 1.0:
            self.current_color = self.next_color
            self.next_color = random.choice([c for c in self.colors if c != self.current_color])
            self.color_blend = 0.0
        self.update()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor(0, 0, 0))

        cx, cy = w / 2, h / 2
        ax, ay = 0.3 * w, 0.25 * h
        bx, by = 0.4 * w, 0.35 * h

        x1 = cx + ax * math.sin(self._t * 0.8)
        y1 = cy + ay * math.cos(self._t * 0.9)
        x2 = cx + bx * math.cos(self._t * 1.2 + 1.3)
        y2 = cy + by * math.sin(self._t * 1.0 + 0.8)

        r = int(self.current_color.red() * (1 - self.color_blend) + self.next_color.red() * self.color_blend)
        g = int(self.current_color.green() * (1 - self.color_blend) + self.next_color.green() * self.color_blend)
        b = int(self.current_color.blue() * (1 - self.color_blend) + self.next_color.blue() * self.color_blend)
        color_mix = QColor(r, g, b, 130)

        grad1 = QRadialGradient(x1, y1, max(w, h) * 0.6)
        grad1.setColorAt(0.0, color_mix)
        grad1.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad1))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        grad2 = QRadialGradient(x2, y2, max(w, h) * 0.7)
        grad2.setColorAt(0.0, QColor(color_mix.red(), color_mix.green(), color_mix.blue(), 90))
        grad2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad2))
        painter.drawRect(self.rect())

        painter.end()


@dataclass
class SetupState:
    lang: str = "en"
    user_name: str = ""
    password: str = ""


def ensure_list_apps_config():
    """
    Создаёт папку root/bin/list_apps и нужные конфиги:
      - list_apps.config (JSON dict)
      - dock.config (JSON list)
      - install_apps.config (JSON dict: app.status -> url)
    Возвращает путь к list_apps.config
    """
    config_dir = os.path.join("root", "bin", "list_apps")
    list_apps_path = os.path.join(config_dir, "list_apps.config")
    dock_path = os.path.join("root", "bin", "dock.config")
    install_apps_path = os.path.join("root", "bin", "install_apps.config")

    config_dir_desk = os.path.join("root", "user", "desk")
    desk_path = os.path.join(config_dir_desk, "desk.config")

    config_dir_Documents = os.path.join("root", "user", "Documents")
    Documents_path = os.path.join(config_dir_Documents, "Documents.config")

    config_dir_download = os.path.join("root", "user", "download")
    download_path = os.path.join(config_dir_download, "download.config")

    config_dir_images = os.path.join("root", "user", "images")

    # 1) list_apps.config
    default_list_apps = {
        "browser": None,
        "cmd": None,
        "settings": None,
        "calc": None,
        "explorer": None,
        "notebook": None,
        "manager_all": None
    }

    text_null = ["null"]

    # 2) dock.config (лучше список, не set)
    default_dock = ["browser", "settings", "cmd"]

    # 3) install_apps.config
    default_install_apps = [
        '"browser.None": "https://github.com/lumister/browser/archive/refs/heads/main.zip",',
        '"cmd.None": "https://github.com/lumister/cmd/archive/refs/heads/main.zip",',
        '"settings.None": "https://github.com/lumister/settings/archive/refs/heads/main.zip",',
        '"calc.None": "https://github.com/lumister/calc/archive/refs/heads/main.zip",',
        '"explorer.None": "https://github.com/lumister/explorer/archive/refs/heads/main.zip",',
        '"notebook.None": "https://github.com/lumister/notebook/archive/refs/heads/main.zip",',
        '"manager_all.None": "https://github.com/lumister/manager_all/archive/refs/heads/main.zip",',
    ]

    default_desk = {
        "wallpaper_path": "bin/icons/local_icons/IconOs/wallpaper.jpg",
        "lockscreen_path": "bin/icons/local_icons/IconOs/wallpaper_defolt.jpg"
    }

    try:
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(config_dir_desk, exist_ok=True)
        os.makedirs(config_dir_Documents, exist_ok=True)
        os.makedirs(config_dir_download, exist_ok=True)
        os.makedirs(config_dir_images, exist_ok=True)

        if not os.path.exists(list_apps_path):
            with open(list_apps_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(default_list_apps, ensure_ascii=False, indent=4))
            print(f"[OK] Создан {list_apps_path}")

        if not os.path.exists(dock_path):
            with open(dock_path, "w", encoding="utf-8") as f:
                f.write("\n".join(default_dock) + "\n")
            print(f"[OK] Создан {dock_path}")

        if not os.path.exists(install_apps_path):
            with open(install_apps_path, "w", encoding="utf-8") as f:
                f.write("\n".join(default_install_apps) + "\n")
            print(f"[OK] Создан {install_apps_path}")

        if not os.path.exists(desk_path):
            with open(desk_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(default_desk, ensure_ascii=False, indent=4))
            print(f"[OK] Создан {desk_path}")
            
        if not os.path.exists(Documents_path):
            with open(Documents_path, "w", encoding="utf-8") as f:
                f.write("\n".join(text_null) + "\n")
            print(f"[OK] Создан {Documents_path}")

        if not os.path.exists(download_path):
            with open(download_path, "w", encoding="utf-8") as f:
                f.write("\n".join(text_null) + "\n")
            print(f"[OK] Создан {download_path}")


    except Exception as e:
        print(f"[ERROR] ensure_list_apps_config: {e}")

    return list_apps_path



class SetupWizard(QWidget):
    TRANSLATIONS = {
        "uk": {
            "t_lang": "Оберіть мову",
            "s_lang": "Оберіть мову інтерфейсу та натисніть «Далі».",
            "btn_uk": "Українська",
            "btn_en": "English",

            "t_user": "Створення користувача",
            "s_user": "Введіть ім'я користувача.",
            "username": "Ім'я користувача",

            "t_pass": "Пароль",
            "s_pass": "Створіть пароль та підтвердіть його.",
            "password": "Пароль",
            "password2": "Підтвердіть пароль",

            "t_done": "Готово!",
            "s_done": "Налаштування завершено. Натисніть «Перезавантажити».",

            "back": "Назад",
            "next": "Далі",
            "restart": "Перезавантажити",
            "exit": "Вийти",

            "err_user": "Вкажіть ім'я користувача (мін. 2 символи).",
            "err_pass_len": "Пароль має бути мінімум 4 символи.",
            "err_pass_match": "Паролі не співпадають.",
        },
        "en": {
            "t_lang": "Choose language",
            "s_lang": "Pick a language and click Next.",
            "btn_uk": "Українська",
            "btn_en": "English",

            "t_user": "Create user",
            "s_user": "Enter a username.",
            "username": "Username",

            "t_pass": "Password",
            "s_pass": "Create a password and confirm it.",
            "password": "Password",
            "password2": "Confirm password",

            "t_done": "All set!",
            "s_done": "Setup is complete. Click Restart.",

            "back": "Back",
            "next": "Next",
            "restart": "Restart",
            "exit": "Exit",

            "err_user": "Enter a username (min 2 chars).",
            "err_pass_len": "Password must be at least 4 chars.",
            "err_pass_match": "Passwords do not match.",
        }
    }

    def __init__(self):
        super().__init__()
        self.state = SetupState()
        self._pass2 = ""

        self.is_windows = (os.name == "nt")
        self.setWindowTitle("Stellar OS Setup")
        self.setObjectName("setup_root")

        self.bg = SoftGlowBackground(self)
        self.bg.lower()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        center = QWidget()
        center.setObjectName("center")
        center_lay = QVBoxLayout(center)
        center_lay.setContentsMargins(0, 0, 0, 0)
        center_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedSize(860, 510)  # ширина/высота карточки
        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(36, 30, 36, 24)
        card_lay.setSpacing(18)

        self.h_title = QLabel("")
        self.h_title.setObjectName("hTitle")
        self.h_title.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        self.h_title.setWordWrap(True)

        self.h_sub = QLabel("")
        self.h_sub.setObjectName("hSub")
        self.h_sub.setFont(QFont("Segoe UI", 14))
        self.h_sub.setWordWrap(True)

        self.err = QLabel("")
        self.err.setObjectName("error")
        self.err.hide()

        card_lay.addWidget(self.h_title)
        card_lay.addWidget(self.h_sub)
        card_lay.addWidget(self.err)

        # Step dots
        self.step_dots = QHBoxLayout()
        self.step_dots.setSpacing(8)
        self.step_dots.setContentsMargins(0, 6, 0, 6)
        self.step_dots.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._dots = []
        for _ in range(4):
            d = QLabel()
            d.setObjectName("stepDot")
            d.setFixedSize(10, 10)
            self._dots.append(d)
            self.step_dots.addWidget(d)

        card_lay.addLayout(self.step_dots)


        self.stack = QStackedWidget()
        self.stack.setObjectName("stack")
        card_lay.addWidget(self.stack, 1)

        footer = QHBoxLayout()
        footer.setSpacing(10)

        self.btn_exit = QPushButton("")
        self.btn_exit.setObjectName("btnGhost")
        self.btn_exit.clicked.connect(QApplication.quit)

        self.btn_back = QPushButton("")
        self.btn_back.setObjectName("btnSecondary")
        self.btn_back.clicked.connect(self.go_back)

        self.btn_next = QPushButton("")
        self.btn_next.setObjectName("btnPrimary")
        self.btn_next.clicked.connect(self.go_next)

        footer.addWidget(self.btn_exit)
        footer.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        footer.addWidget(self.btn_back)
        footer.addWidget(self.btn_next)

        card_lay.addLayout(footer)

        center_lay.addWidget(self.card)
        root.addWidget(center)

        self._build_pages()
        self._apply_style()

        self.set_language("en", immediate=True)
        self._set_page(0)

        self.showFullScreen()

    def t(self, key: str) -> str:
        return self.TRANSLATIONS.get(self.state.lang, {}).get(key, key)

    def set_language(self, lang: str, immediate: bool = False):
        self.state.lang = "uk" if str(lang).lower().startswith("uk") else "en"
        if immediate:
            self._refresh_texts()
        else:
            self._fade_to(self._refresh_texts)

    def _build_pages(self):
        self.pages = []

        # 1) Language (choose + Next)
        p0 = QWidget()
        l0 = QVBoxLayout(p0)
        l0.setContentsMargins(0, 0, 0, 0)
        l0.setSpacing(14)

        row = QHBoxLayout()
        row.setSpacing(12)

        self.btn_lang_uk = QPushButton("Українська")
        self.btn_lang_uk.setObjectName("btnLang")
        self.btn_lang_uk.setCheckable(True)
        self.btn_lang_uk.clicked.connect(lambda: self._select_lang("uk"))

        self.btn_lang_en = QPushButton("English")
        self.btn_lang_en.setObjectName("btnLang")
        self.btn_lang_en.setCheckable(True)
        self.btn_lang_en.clicked.connect(lambda: self._select_lang("en"))

        row.addWidget(self.btn_lang_uk)
        row.addWidget(self.btn_lang_en)

        wrap = QWidget()
        wrap_l = QVBoxLayout(wrap)
        wrap_l.setContentsMargins(0, 0, 0, 0)
        wrap_l.setSpacing(14)
        wrap_l.setAlignment(Qt.AlignmentFlag.AlignTop)

        wrap_l.addLayout(row)
        wrap_l.addSpacing(10)

        l0.addWidget(wrap)
        l0.addStretch(1)  # теперь оно нормально работает, потому что карточка ниже по высоте


        self.stack.addWidget(p0)
        self.pages.append(("t_lang", "s_lang"))

        # 2) Username
        p2 = QWidget()
        l2 = QVBoxLayout(p2)
        l2.setContentsMargins(0, 0, 0, 0)
        l2.setSpacing(12)

        self.lbl_user = QLabel("")
        self.lbl_user.setObjectName("fieldLabel")

        self.ed_user = Input()
        self.ed_user.setObjectName("edit")
        self.ed_user.setPlaceholderText("user")
        # Ограничения для username
        self.ed_user.setMaxLength(20)  # максимум 20 символов
        self.ed_user.setValidator(QRegularExpressionValidator(QRegularExpression(r"[A-Za-z0-9_-]+")))

        # Всегда берем текст из поля, а не параметр сигнала (он может быть не строкой)
        self.ed_user.textChanged.connect(lambda _: setattr(self.state, "user_name", self.ed_user.text().strip()))


        l2.addWidget(self.lbl_user)
        l2.addWidget(self.ed_user)
        l2.addStretch(1)

        self.stack.addWidget(p2)
        self.pages.append(("t_user", "s_user"))

        # 3) Password + confirm
        p3 = QWidget()
        l3 = QVBoxLayout(p3)
        l3.setContentsMargins(0, 0, 0, 0)
        l3.setSpacing(12)

        self.lbl_pass1 = QLabel("")
        self.lbl_pass1.setObjectName("fieldLabel")
        self.ed_pass1 = InputPassword(
                initial_text="",
                echo_mode=QLineEdit.EchoMode.Password
            )
        self.ed_pass1.setObjectName("edit")
        # self.ed_pass1.setEchoMode(QLineEdit.EchoMode.Password)
        self.ed_pass1.textChanged.connect(lambda v: setattr(self.state, "password", v))

        self.lbl_pass2 = QLabel("")
        self.lbl_pass2.setObjectName("fieldLabel")
        self.ed_pass2 = InputPassword(
                initial_text="",
                echo_mode=QLineEdit.EchoMode.Password
            )
        self.ed_pass2.setObjectName("edit")
        # self.ed_pass2.setEchoMode(QLineEdit.EchoMode.Password)
        self.ed_pass2.textChanged.connect(lambda v: setattr(self, "_pass2", v))

        l3.addWidget(self.lbl_pass1)
        l3.addWidget(self.ed_pass1)
        l3.addWidget(self.lbl_pass2)
        l3.addWidget(self.ed_pass2)
        l3.addStretch(1)

        self.stack.addWidget(p3)
        self.pages.append(("t_pass", "s_pass"))

        # 4) Done
        p4 = QWidget()
        l4 = QVBoxLayout(p4)
        l4.setContentsMargins(0, 0, 0, 0)
        l4.setSpacing(14)

        self.done_lbl = QLabel("")
        self.done_lbl.setObjectName("done")
        self.done_lbl.setWordWrap(True)

        self.btn_restart = QPushButton("")
        self.btn_restart.setObjectName("btnPrimary")
        self.btn_restart.clicked.connect(self._write_and_restart)

        l4.addWidget(self.done_lbl)
        l4.addStretch(1)
        l4.addWidget(self.btn_restart, alignment=Qt.AlignmentFlag.AlignRight)

        self.stack.addWidget(p4)
        self.pages.append(("t_done", "s_done"))

    def _select_lang(self, lang: str):
        if lang == "uk":
            self.btn_lang_uk.setChecked(True)
            self.btn_lang_en.setChecked(False)
        else:
            self.btn_lang_en.setChecked(True)
            self.btn_lang_uk.setChecked(False)
        self.set_language(lang)
        self._sync_nav()  # enable Next

    def _set_page(self, idx: int):
        idx = max(0, min(idx, self.stack.count() - 1))
        self.stack.setCurrentIndex(idx)
        self._refresh_texts()

    def _refresh_texts(self):
        t_key, s_key = self.pages[self.stack.currentIndex()]
        self.h_title.setText(self.t(t_key))
        self.h_sub.setText(self.t(s_key))

        self.btn_back.setText(self.t("back"))
        self.btn_next.setText(self.t("next"))
        self.btn_exit.setText(self.t("exit"))
        self.btn_restart.setText(self.t("restart"))
        self.lbl_user.setText(self.t("username"))
        self.lbl_pass1.setText(self.t("password"))
        self.lbl_pass2.setText(self.t("password2"))
        self.done_lbl.setText(self.t("s_done"))

        self._sync_nav()

    def _sync_nav(self):
        i = self.stack.currentIndex()
        self.err.hide()

        self.btn_back.setVisible(i > 0)
        self.btn_exit.setVisible(i < self.stack.count() - 1)

        if i == self.stack.count() - 1:
            self.btn_next.hide()
            self.btn_back.hide()
            self.btn_exit.hide()
            return

        self.btn_next.show()

        if i == 0:
            chosen = self.btn_lang_uk.isChecked() or self.btn_lang_en.isChecked()
            self.btn_next.setEnabled(chosen)
        else:
            self.btn_next.setEnabled(True)


        # update step dots
        # i = self.stack.currentIndex()
        for idx, d in enumerate(self._dots):
            d.setProperty("active", idx == i)
            d.style().unpolish(d)
            d.style().polish(d)


    def go_back(self):
        self.err.hide()
        self._set_page(self.stack.currentIndex() - 1)

    def _validate_username(self, name: str) -> tuple[bool, str]:
        name = (name or "").strip()

        if len(name) < 2:
            return False, self.t("err_user")
        if len(name) > 20:
            return False, "Max 20 characters" if self.state.lang == "en" else "Максимум 20 символів"
        if " " in name:
            return False, "Spaces are not allowed" if self.state.lang == "en" else "Пробіли заборонені"

        # только безопасные символы для имени папки
        import re
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            return False, "Only A-Z, 0-9, _ and -" if self.state.lang == "en" else "Тільки A-Z, 0-9, _ та -"

        # Windows reserved device names
        if os.name == "nt":
            reserved = {
                "CON","PRN","AUX","NUL",
                "COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9",
                "LPT1","LPT2","LPT3","LPT4","LPT5","LPT6","LPT7","LPT8","LPT9"
            }
            if name.upper() in reserved:
                return False, "Reserved username on Windows" if self.state.lang == "en" else "Зарезервоване ім'я у Windows"

        return True, ""


    def go_next(self):
        i = self.stack.currentIndex()

        if i == 1:
            u = self.ed_user.text().strip()   # <-- всегда текст!
            ok, msg = self._validate_username(u)
            if not ok:
                self._show_error(msg)
                return
            self.state.user_name = u  # сохраняем уже валидный username


        if i == 2:
            if len(self.state.password or "") < 4:
                self._show_error(self.t("err_pass_len"))
                return
            if (self.state.password or "") != (self._pass2 or ""):
                self._show_error(self.t("err_pass_match"))
                return

            self._write_setup_files()

        self.err.hide()
        self._set_page(i + 1)

    def _show_error(self, msg: str):
        self.err.setText(msg)
        self.err.show()

    def _write_setup_files(self):
        username = str(self.state.user_name).strip()

        # Корень проекта: PxStellarOs (т.к. этот файл лежит в bin/sys/class_)
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        ROOT_DIR = os.path.join(BASE_DIR, "root")

        cfg_dir = os.path.join(ROOT_DIR, username, "user")
        os.makedirs(cfg_dir, exist_ok=True)

        # install
        try:
            with open(os.path.join(cfg_dir, "install"), "w", encoding="utf-8") as f:
                f.write("yes")
        except Exception:
            pass

        # password
        try:
            with open(os.path.join(cfg_dir, "password"), "w", encoding="utf-8") as f:
                f.write(self.state.password)
        except Exception:
            pass


        config_path = ensure_list_apps_config()

        try:
            with open(config_path, "r", encoding="utf-8") as file:
                content = file.read().strip()
                self.open_windows = json.loads(content)
        except Exception as e:
            print(e)

        # user.config (в ROOT_DIR/bin)
        try:
            os.makedirs(os.path.join(ROOT_DIR, "bin"), exist_ok=True)
            with open(os.path.join(ROOT_DIR, "bin", "user.config"), "w", encoding="utf-8") as f:
                json.dump({"user_name": username}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


    def _write_and_restart(self):
        # If you have a real reboot command, call it here.
        QApplication.quit()

    def _fade_to(self, callback, duration=220):
        eff = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(eff)

        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        def _out_done():
            callback()
            anim2 = QPropertyAnimation(eff, b"opacity")
            anim2.setDuration(duration)
            anim2.setStartValue(0.0)
            anim2.setEndValue(1.0)
            anim2.setEasingCurve(QEasingCurve.Type.InOutQuad)
            anim2.start()
            self._anim2 = anim2

        anim.finished.connect(_out_done)
        anim.start()
        self._anim = anim

    def _apply_style(self):
        self.setStyleSheet("""
            #setup_root { background: transparent; }
            #center { background: transparent; }

            #card {
                background: rgba(18,18,18,205);
                border: 1px solid rgba(255,255,255,18);
                border-radius: 22px;
            }

            #hTitle { color: rgba(255,255,255,245); }
            #hSub   { color: rgba(255,255,255,155); }

            QLabel#stepDot {
                background: rgba(255,255,255,35);
                border-radius: 5px;
            }
            QLabel#stepDot[active="true"] {
                background: rgba(0,120,212,230);
            }

            QLabel#fieldLabel {
                color: rgba(255,255,255,170);
                font-size: 12px;
            }

            Input#edit {
                height: 40px;
                border-radius: 12px;
                padding-left: 12px;
                padding-right: 12px;
                background: rgba(12,12,12,210);
                border: 1px solid rgba(255,255,255,18);
                color: rgba(255,255,255,235);
                font-size: 14px;
            }
            Input#edit:focus { border: 1px solid rgba(0,120,212,210); }

            QComboBox#combo {
                height: 40px;
                border-radius: 12px;
                padding-left: 12px;
                padding-right: 28px;
                background: rgba(12,12,12,210);
                border: 1px solid rgba(255,255,255,18);
                color: rgba(255,255,255,235);
                font-size: 14px;
            }
            QComboBox#combo:focus { border: 1px solid rgba(0,120,212,210); }
            QComboBox#combo::drop-down { border: none; width: 28px; }
            QComboBox#combo::down-arrow { image: none; }

            QPushButton#btnPrimary {
                background-color: rgb(0,120,212);
                color: white;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 700;
                border: none;
                min-width: 140px;
                height: 40px;
            }
            QPushButton#btnPrimary:hover { background-color: rgb(0,105,185); }
            QPushButton#btnPrimary:disabled { background: rgba(255,255,255,10); color: rgba(255,255,255,120); }

            QPushButton#btnSecondary {
                background: rgba(255,255,255,0);
                color: rgba(255,255,255,220);
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 650;
                border: 1px solid rgba(255,255,255,18);
                min-width: 120px;
                height: 40px;
            }
            QPushButton#btnSecondary:hover { background: rgba(255,255,255,10); }

            QPushButton#btnGhost {
                background: transparent;
                color: rgba(255,255,255,180);
                border: none;
                padding: 10px 12px;
                font-size: 13px;
                height: 40px;
            }
            QPushButton#btnGhost:hover { color: rgba(255,255,255,235); }

            /* Language tiles */
            QPushButton#btnLang {
                background: rgba(255,255,255,10);
                border: 1px solid rgba(255,255,255,18);
                color: rgba(255,255,255,235);
                border-radius: 16px;
                padding: 18px 18px;
                font-size: 16px;
                font-weight: 700;
                min-width: 340px;
                height: 64px;
            }
            QPushButton#btnLang:hover {
                background: rgba(255,255,255,14);
                border: 1px solid rgba(0,120,212,180);
            }
            QPushButton#btnLang:checked {
                background: rgba(0,120,212,22);
                border: 1px solid rgba(0,120,212,230);
            }

            QLabel#error {
                color: rgb(255, 120, 120);
                font-size: 13px;
                padding: 10px 12px;
                background: rgba(255, 120, 120, 12);
                border: 1px solid rgba(255, 120, 120, 22);
                border-radius: 12px;
            }

            QLabel#done {
                color: rgba(255,255,255,220);
                font-size: 16px;
            }
        """)


    def resizeEvent(self, e):
        if hasattr(self, "bg") and self.bg:
            self.bg.resize(self.size())
        super().resizeEvent(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SetupWizard()
    w.show()
    sys.exit(app.exec())
