# -*- coding: utf-8 -*-
import sys
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QScrollArea, QMessageBox, QFrame, QSizePolicy,
    QSplitter, QTextBrowser, QPlainTextEdit
)
from PyQt6.QtWidgets import QAbstractScrollArea

import re

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


# ==================== МОДЕЛЬ В ОТДЕЛЬНОМ ПОТОКЕ ====================
class ModelLoaderThread(QThread):
    finished = pyqtSignal(object, object)  # tokenizer, model
    error = pyqtSignal(str)

    def run(self):
        try:
            model_id = "Qwen/Qwen2.5-0.5B-Instruct"
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float32,
                device_map="cpu",
                trust_remote_code=False
            )
            model.eval()
            self.finished.emit(tokenizer, model)
        except Exception as e:
            self.error.emit(f"Ошибка загрузки модели:\n{str(e)}")

class CodeBlockWidget(QFrame):
    def __init__(self, code: str, lang: str = "text"):
        super().__init__()
        self.setObjectName("codeBlock")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("codeHeader")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 8, 12, 8)

        self.lang_label = QLabel(lang if lang else "text")
        self.lang_label.setObjectName("codeLang")
        hl.addWidget(self.lang_label)

        hl.addStretch(1)

        self.copy_btn = QPushButton("Копировать код")
        self.copy_btn.setObjectName("copyBtn")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        hl.addWidget(self.copy_btn)

        root.addWidget(header)

        # Code area
        self.editor = QPlainTextEdit()
        self.editor.setObjectName("codeEditor")
        self.editor.setPlainText(code.rstrip("\n"))
        self.editor.setReadOnly(True)
        self.editor.setFrameShape(QFrame.Shape.NoFrame)
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)  # как в IDE
        root.addWidget(self.editor)

        self.copy_btn.clicked.connect(self.copy_code)

        self.setStyleSheet("""
            QFrame#codeBlock {
                background: #0B0D12;
                border: 1px solid #2A2F3A;
                border-radius: 14px;
            }
            QFrame#codeHeader {
                background: transparent;
                border-bottom: 1px solid #1F2430;
            }
            QLabel#codeLang {
                color: #98A2B3;
                font-weight: 700;
                font-size: 10.5pt;
            }
            QPushButton#copyBtn {
                background: transparent;
                border: none;
                color: #C7D2FE;
                font-weight: 700;
                padding: 4px 6px;
            }
            QPushButton#copyBtn:hover { color: #E0E7FF; }

            QPlainTextEdit#codeEditor {
                background: transparent;
                color: #E8ECF3;
                font-family: "Consolas";
                font-size: 10.5pt;
                padding: 10px 12px 12px 12px;
            }
        """)

    def copy_code(self):
        QApplication.clipboard().setText(self.editor.toPlainText())
        self.copy_btn.setText("Скопировано ✓")
        QTimer.singleShot(1200, lambda: self.copy_btn.setText("Копировать код"))


class ChatWorkerThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, tokenizer, model, messages):
        super().__init__()
        self.tokenizer = tokenizer
        self.model = model
        self.messages = messages

    def run(self):
        try:
            text = self.tokenizer.apply_chat_template(
                self.messages,
                tokenize=False,
                add_generation_prompt=True
            )
            inputs = self.tokenizer(text, return_tensors="pt")

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100000,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )
            self.finished.emit(response.strip())
        except Exception as e:
            self.error.emit(f"Ошибка генерации:\n{str(e)}")

class AutoHeightTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def wheelEvent(self, e):
        e.ignore()


    def keyPressEvent(self, e):
        # чтобы PageUp/PageDown/Home/End не скроллили внутри сообщения
        if e.key() in (Qt.Key.Key_PageUp, Qt.Key.Key_PageDown, Qt.Key.Key_Home, Qt.Key.Key_End):
            e.ignore()
            return
        super().keyPressEvent(e)

    def setMarkdownAndFit(self, md: str):
        self.setMarkdown(md)
        self._fitHeight()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._fitHeight()

    def _fitHeight(self):
        w = max(10, self.viewport().width())
        self.document().setTextWidth(w)
        h = int(self.document().size().height())
        self.setFixedHeight(h + 2)

    def ensureCursorVisible(self):
        # Отключаем автопрокрутку при выделении/перетаскивании курсора
        return

    def mouseMoveEvent(self, e):
        # при выделении и протягивании мыши QTextBrowser пытается автоскроллить —
        # блокируем это
        if e.buttons() & Qt.MouseButton.LeftButton:
            e.ignore()
            return
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e):
        # чтобы выделение работало, но без "автоскролла"
        super().mousePressEvent(e)


# ==================== UI ЭЛЕМЕНТЫ ====================
class MessageBubble(QFrame):
    """Пузырёк сообщения: markdown + красивые code blocks с кнопкой Copy."""
    CODE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)

    def __init__(self, text: str, is_user: bool):
        super().__init__()
        self.setObjectName("bubble")

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        container.setObjectName("bubbleInner")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(14, 10, 14, 10)
        container_layout.setSpacing(10)

        # Ограничение ширины как у веб-чатов
        # Ширина пузырей/карточек
        # if is_user:
        #     container.setMaximumWidth(1400)   # пользователь справа — компактнее
        # else:
        #     container.setMaximumWidth(1400)   # ответ по центру — шире, как “панель”

        container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)


        # Стили пузырьков
        container.setProperty("role", "user" if is_user else "assistant")
        self._apply_styles(container, is_user)

        # Контент: текст + code blocks
        self._render_content(container_layout, text)

        if is_user:
            outer.addStretch(1)
            outer.addWidget(container, 0, Qt.AlignmentFlag.AlignRight)
        else:
            outer.addStretch(1)
            outer.addWidget(container, 0, Qt.AlignmentFlag.AlignHCenter)
            outer.addStretch(1)


    def _apply_styles(self, container: QFrame, is_user: bool):
        # Важно: у пользователя фон синий — для кода это плохо читается.
        # Поэтому code-block карточки будут сами тёмные и хорошо читаемые поверх синего.
        self.setStyleSheet("""
            QFrame#bubble { background: transparent; }

            QFrame#bubbleInner[role="user"] {
                background-color: #2B6DEB;
                border-radius: 16px;
            }
            QFrame#bubbleInner[role="assistant"] {
                background-color: #121520;
                border: 1px solid #2A2F3A;
                border-radius: 18px;
            }


            QTextBrowser#bubbleText {
                background: transparent;
                border: none;
                color: #E8ECF3;
                font-size: 11pt;
                font-family: "Segoe UI";
            }
        """)

    def _add_markdown_block(self, layout: QVBoxLayout, md_text: str):
        md_text = md_text.strip("\n")
        if not md_text.strip():
            return

        view = AutoHeightTextBrowser()
        view.setObjectName("bubbleText")
        view.setMarkdownAndFit(md_text)

        view.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        layout.addWidget(view)


    def _render_content(self, layout: QVBoxLayout, full_text: str):
        pos = 0
        for m in self.CODE_RE.finditer(full_text):
            start, end = m.span()

            # Текст до кода
            before = full_text[pos:start]
            self._add_markdown_block(layout, before)

            # Код-блок
            lang = (m.group(1) or "text").strip()
            code = m.group(2) or ""
            layout.addWidget(CodeBlockWidget(code=code, lang=lang))

            pos = end

        # Хвост после последнего кода
        tail = full_text[pos:]
        self._add_markdown_block(layout, tail)

class AnswerCard(QFrame):
    """Центральный вывод ответа как в ChatGPT: без пузыря/рамки, просто контент по центру."""
    def __init__(self, text: str):
        super().__init__()
        self.setObjectName("assistantOutput")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)   # без внутренних паддингов "карточки"
        root.setSpacing(12)

        self._render_content(root, text)

        # Никакой рамки/фона — как у ChatGPT
        self.setStyleSheet("""
            QFrame#assistantOutput {
                background: transparent;
                border: none;
            }
        """)

    def _add_md(self, layout: QVBoxLayout, md: str):
        md = md.strip("\n")
        if not md.strip():
            return

        view = AutoHeightTextBrowser()
        view.setObjectName("assistantText")
        view.setMarkdownAndFit(md)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Чуть более "чатгпт"-типографика
        view.setStyleSheet("""
            QTextBrowser#assistantText {
                background: transparent;
                border: none;
                color: #E8ECF3;
                font-family: "Segoe UI";
                font-size: 11.5pt;
            }
        """)
        layout.addWidget(view)

    def _render_content(self, layout: QVBoxLayout, full_text: str):
        pos = 0
        for m in MessageBubble.CODE_RE.finditer(full_text):
            start, end = m.span()

            before = full_text[pos:start]
            self._add_md(layout, before)

            lang = (m.group(1) or "text").strip()
            code = m.group(2) or ""
            layout.addWidget(CodeBlockWidget(code=code, lang=lang))

            pos = end

        tail = full_text[pos:]
        self._add_md(layout, tail)



class ChatView(QWidget):
    """Центральная область чата + скролл."""
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setObjectName("chatScroll")

        self.chat_area = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_area)
        self.chat_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setContentsMargins(22, 18, 22, 18)
        self.chat_layout.setSpacing(12)

        # Центруем колонку, как в ChatGPT
        # self.chat_area.setMaximumWidth(900)  # ширина колонки (поставь 900-1200 по вкусу)

        wrapper = QWidget()
        wl = QHBoxLayout(wrapper)
        wl.setContentsMargins(0, 0, 0, 0)

        # chat_area получает stretch=1 и центрируется
        wl.addWidget(self.chat_area, 1, Qt.AlignmentFlag.AlignHCenter)


        self.scroll.setWidget(wrapper)

        root.addWidget(self.scroll)

    def add_message(self, text: str, is_user: bool):
        row = QWidget()
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        if is_user:
            bubble = MessageBubble(text, True)
            rl.addStretch(1)
            rl.addWidget(bubble, 0, Qt.AlignmentFlag.AlignRight)
        else:
            ans = AnswerCard(text)

            # пусть занимает ширину колонки (до chat_area maxWidth)
            ans.setMaximumWidth(self.chat_area.maximumWidth())
            ans.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

            rl.addWidget(ans, 1, Qt.AlignmentFlag.AlignLeft)  # stretch=1
            # rl.addStretch(1)  <-- УБРАТЬ


        self.chat_layout.addWidget(row)
        QTimer.singleShot(0, self.scroll_to_bottom)





    def scroll_to_bottom(self):
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())


# ==================== ГЛАВНОЕ ОКНО ====================
class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Локальный чат (DeepSeek-style)")
        self.resize(1150, 760)

        self.tokenizer = None
        self.model = None
        self.is_generating = False

        # История: сразу задаём системную инструкцию (и язык)
        self.chat_history = [{
            "role": "system",
            "content": (
                "Ты — локальный ИИ-ассистент. Всегда отвечай по-русски. "
                "Пиши кратко и по делу. Если пользователь пишет на русском — отвечай только на русском."
            )
        }]

        self._apply_dark_theme()
        self._build_ui()
        self._wire()
        self.load_model()

    def _apply_dark_theme(self):
        app = QApplication.instance()
        if not app:
            return
        app.setStyle("Fusion")

        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#0F1116"))
        pal.setColor(QPalette.ColorRole.WindowText, QColor("#E8ECF3"))
        pal.setColor(QPalette.ColorRole.Base, QColor("#0F1116"))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor("#121520"))
        pal.setColor(QPalette.ColorRole.Text, QColor("#E8ECF3"))
        pal.setColor(QPalette.ColorRole.Button, QColor("#1A1D24"))
        pal.setColor(QPalette.ColorRole.ButtonText, QColor("#E8ECF3"))
        pal.setColor(QPalette.ColorRole.Highlight, QColor("#2B6DEB"))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        app.setPalette(pal)

        self.setStyleSheet("""
            QMainWindow { background: #0F1116; }
            QScrollArea#chatScroll { border: none; background: #0F1116; }
            QScrollArea#chatScroll > QWidget > QWidget { background: #0F1116; }

            /* Скроллбар */
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 6px 4px 6px 4px;
            }
            QScrollBar::handle:vertical {
                background: #2A2F3A;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        """)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter)

        # ========= ЛЕВЫЙ САЙДБАР =========
        self.sidebar = QFrame()
        self.sidebar.setMinimumWidth(260)
        self.sidebar.setMaximumWidth(320)
        self.sidebar.setObjectName("sidebar")
        sb = QVBoxLayout(self.sidebar)
        sb.setContentsMargins(14, 14, 14, 14)
        sb.setSpacing(12)

        brand = QLabel("DeepSeek-style")
        brand.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        brand.setStyleSheet("color: #E8ECF3; padding: 6px 6px;")
        sb.addWidget(brand)

        self.new_chat_btn = QPushButton("＋ Новый чат")
        self.new_chat_btn.setFixedHeight(40)
        self.new_chat_btn.setObjectName("newChatBtn")
        sb.addWidget(self.new_chat_btn)

        sb.addSpacing(6)
        chats_label = QLabel("Чаты")
        chats_label.setStyleSheet("color: #98A2B3; padding: 2px 6px;")
        sb.addWidget(chats_label)

        self.chat_item_btn = QPushButton("💬  Чат 1")
        self.chat_item_btn.setObjectName("chatItem")
        self.chat_item_btn.setFixedHeight(38)
        self.chat_item_btn.setChecked(True)
        self.chat_item_btn.setCheckable(True)
        sb.addWidget(self.chat_item_btn)

        sb.addStretch(1)

        footer = QLabel("Локально • без интернета")
        footer.setStyleSheet("color: #667085; padding: 6px;")
        sb.addWidget(footer)

        self.sidebar.setStyleSheet("""
            QFrame#sidebar { background: #0B0D12; border-right: 1px solid #1F2430; }
            QPushButton#newChatBtn {
                background: #1A1D24;
                border: 1px solid #2A2F3A;
                border-radius: 12px;
                color: #E8ECF3;
                font-weight: 600;
                text-align: left;
                padding: 0 12px;
            }
            QPushButton#newChatBtn:hover { border: 1px solid #3A4150; }

            QPushButton#chatItem {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 12px;
                color: #E8ECF3;
                text-align: left;
                padding: 0 12px;
            }
            QPushButton#chatItem:checked {
                background: #121520;
                border: 1px solid #2A2F3A;
            }
            QPushButton#chatItem:hover { border: 1px solid #2A2F3A; }
        """)

        # ========= ПРАВАЯ ПАНЕЛЬ (ХЕДЕР + ЧАТ + ВВОД) =========
        self.main_panel = QFrame()
        self.main_panel.setObjectName("mainPanel")
        mp = QVBoxLayout(self.main_panel)
        mp.setContentsMargins(0, 0, 0, 0)
        mp.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(18, 14, 18, 14)

        self.header_title = QLabel("Локальный ИИ-ассистент")
        self.header_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        hl.addWidget(self.header_title)

        hl.addStretch(1)

        self.status_pill = QLabel("Загрузка модели…")
        self.status_pill.setObjectName("statusPill")
        self.status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_pill.setFixedHeight(28)
        self.status_pill.setMinimumWidth(160)
        hl.addWidget(self.status_pill)

        mp.addWidget(header)

        # Chat view
        self.chat_view = ChatView()
        mp.addWidget(self.chat_view, 1)

        # Input bar
        input_wrap = QFrame()
        input_wrap.setObjectName("inputWrap")
        il = QHBoxLayout(input_wrap)
        il.setContentsMargins(18, 12, 18, 16)
        il.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Напишите сообщение…  (Enter — отправить)")
        self.input_field.setObjectName("inputField")
        self.input_field.setFixedHeight(44)
        self.input_field.setFont(QFont("Segoe UI", 11))
        il.addWidget(self.input_field, 1)

        self.send_btn = QPushButton("➤")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setFixedSize(QSize(52, 44))
        il.addWidget(self.send_btn)

        mp.addWidget(input_wrap)

        self.main_panel.setStyleSheet("""
            QFrame#mainPanel { background: #0F1116; }

            QFrame#header {
                background: #0F1116;
                border-bottom: 1px solid #1F2430;
            }
            QLabel { color: #E8ECF3; }

            QLabel#statusPill {
                background: #121520;
                border: 1px solid #2A2F3A;
                border-radius: 14px;
                color: #98A2B3;
                padding: 0 10px;
                font-weight: 600;
            }

            QFrame#inputWrap {
                background: #0F1116;
                border-top: 1px solid #1F2430;
            }
            QLineEdit#inputField {
                background: #121520;
                border: 1px solid #2A2F3A;
                border-radius: 14px;
                padding: 0 14px;
                color: #E8ECF3;
            }
            QLineEdit#inputField:focus { border: 1px solid #2B6DEB; }

            QPushButton#sendBtn {
                background: #2B6DEB;
                border: none;
                border-radius: 14px;
                color: white;
                font-size: 18px;
                font-weight: 700;
            }
            QPushButton#sendBtn:hover { background: #2A63D7; }
            QPushButton#sendBtn:disabled { background: #2A2F3A; color: #98A2B3; }
        """)

        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.main_panel)
        # splitter.setSizes([400, 870])

    def _wire(self):
        self.send_btn.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)
        self.new_chat_btn.clicked.connect(self.reset_chat)

    # ==================== ЛОГИКА ====================
    def load_model(self):
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)
        self.status_pill.setText("Загрузка…")

        self.loader_thread = ModelLoaderThread()
        self.loader_thread.finished.connect(self.on_model_loaded)
        self.loader_thread.error.connect(self.on_model_error)
        self.loader_thread.start()

    def on_model_loaded(self, tokenizer, model):
        self.tokenizer = tokenizer
        self.model = model
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.status_pill.setText("Готово")
        self.status_pill.setStyleSheet("""
            QLabel#statusPill {
                background: #0E1A12;
                border: 1px solid #1F3B2A;
                border-radius: 14px;
                color: #73E2A3;
                padding: 0 10px;
                font-weight: 700;
            }
        """)
        self.input_field.setFocus()

        hello = "Привет! Я локальный ассистент. Напиши, что нужно 🙂"
        self.chat_view.add_message(hello, is_user=False)
        self.chat_history.append({"role": "assistant", "content": hello})

    def on_model_error(self, error_msg):
        self.status_pill.setText("Ошибка")
        QMessageBox.critical(self, "Ошибка", error_msg)

    def reset_chat(self):
        # пока “один чат”: просто очищаем переписку и историю
        # (сайдбар оставляем с одним пунктом)
        while self.chat_view.chat_layout.count():
            item = self.chat_view.chat_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.chat_history = [self.chat_history[0]]  # оставляем system
        hello = "Новый чат. Чем помочь?"
        self.chat_view.add_message(hello, is_user=False)
        self.chat_history.append({"role": "assistant", "content": hello})

    def send_message(self):
        if self.is_generating or not self.model:
            return

        user_text = self.input_field.text().strip()
        if not user_text:
            return

        self.input_field.clear()
        self.is_generating = True
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)
        self.status_pill.setText("Думаю…")

        self.chat_view.add_message(user_text, is_user=True)
        self.chat_history.append({"role": "user", "content": user_text})

        self.worker_thread = ChatWorkerThread(self.tokenizer, self.model, self.chat_history)
        self.worker_thread.finished.connect(self.on_bot_response)
        self.worker_thread.error.connect(self.on_generation_error)
        self.worker_thread.start()

    def on_bot_response(self, text):
        self.chat_view.add_message(text, is_user=False)
        self.chat_history.append({"role": "assistant", "content": text})

        self.is_generating = False
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.status_pill.setText("Готово")
        self.input_field.setFocus()

    def on_generation_error(self, error_msg):
        self.chat_view.add_message(f"❌ {error_msg}", is_user=False)

        self.is_generating = False
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.status_pill.setText("Ошибка")

    def closeEvent(self, event):
        if self.model:
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        event.accept()


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
