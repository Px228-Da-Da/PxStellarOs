import subprocess
import sys
import time
import traceback
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)

from PyQt6.QtCore import Qt

LOG_PATH = "boot_error.log"

import sys, os
os.system("chcp 65001 >nul")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def early_log(msg, print_to_console=False):
    """Пише повідомлення у файл логів навіть якщо GUI не запущений."""
    timestamp = time.strftime("%H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")
    if print_to_console:
        print(msg)


def run_setup():
    """Запускає setup.py у підпроцесі та виводить лог у реальному часі."""
    try:
        early_log("[BOOT] Запуск setup.py...", True)

        # 🔹 Запуск run.py
        process = subprocess.Popen(
            [sys.executable, "run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace"
        )

        output_lines = []
        for line in process.stdout:
            sys.stdout.write(line)      # показываем в терминале
            sys.stdout.flush()
            early_log(line.strip())     # только в файл, без print()
            output_lines.append(line)

        process.wait()
        code = process.returncode
        early_log(f"[BOOT] setup.py завершено з кодом {code}", True)

        if code != 0:
            combined_output = "".join(output_lines)
            raise RuntimeError(
                f"setup.py завершився з помилкою (код {code}):\n\n{combined_output}"
            )

    except Exception as e:
        error_text = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        early_log("[ERROR] Критична помилка при запуску setup.py:\n" + error_text, True)
        show_error_window(error_text)
        sys.exit(1)


def show_error_window(error_text: str):
    """Показує GUI-вікно з текстом помилки."""
    app = QApplication.instance() or QApplication(sys.argv)

    w = QWidget()
    w.setWindowTitle("StellarOS — Boot Error")
    w.setStyleSheet("background:black;color:red;font-family:monospace;font-size:14px;")
    w.showFullScreen()

    layout = QVBoxLayout(w)
    t = QTextEdit()
    t.setReadOnly(True)
    t.setText(error_text)
    layout.addWidget(t)

    app.exec()


if __name__ == "__main__":
    early_log("==============================", True)
    early_log("[BOOT] Ініціалізація запуску StellarOS...", True)
    run_setup()
