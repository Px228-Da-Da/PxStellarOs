import sys
import os
import requests
import zipfile
import shutil
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QBrush, QFont

from apps.local.init import DraggableResizableWindow

# Путь к файлу с версией
VERSION_FILE = "version.txt"
# URL к файлу с версией на GitHub
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/Px228-Da-Da/PxStellarOs/master/version.txt"
# URL к ZIP-архиву репозитория
GITHUB_ZIP_URL = "https://github.com/Px228-Da-Da/PxStellarOs/archive/refs/heads/master.zip"
# Временная папка для распаковки
TEMP_FOLDER = "temp_update"

class UpdateDialog(QDialog):
    def __init__(self, current_version, latest_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Обновление")
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # **Переконайтеся, що немає попереднього layout**
        if self.layout():
            QVBoxLayout().addWidget(QLabel())  # Тимчасовий пустий layout
            self.setLayout(None)

        layout = QVBoxLayout(self)  # Новий layout
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Текст
        self.label = QLabel(f"Доступна новая версия: {latest_version}\nТекущая версия: {current_version}")
        self.label.setFont(QFont("Arial", 12))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Кнопки
        self.update_button = QPushButton("Обновиться")
        self.update_button.clicked.connect(self.start_update)  # Запускаем обновление
        layout.addWidget(self.update_button)

        self.later_button = QPushButton("Позже")
        self.later_button.clicked.connect(self.reject)  # Важливо!
        layout.addWidget(self.later_button)


    def start_update(self):
        """Запуск обновления"""
        self.accept()  # Закрываем окно диалога
        
        parent = self.parent()
        if parent and hasattr(parent, "run_update"):
            parent.run_update()  # Запускаем обновление из главного окна
        else:
            print("Ошибка: run_update() не найден в родительском объекте.")



    def paintEvent(self, event):
        """Отрисовка закруглённых углов."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

class UpdateProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Обновление")
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Текст с информацией о процессе обновления
        self.label = QLabel("Обновление ОС...")
        self.label.setFont(QFont("Arial", 12))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Прогресс-бар
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

    def paintEvent(self, event):
        """Отрисовка закруглённых углов."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def update_progress(self, value):
        """Обновляет прогресс-бар."""
        self.progress_bar.setValue(value)

def get_current_version():
    """Получает текущую версию из файла version.txt."""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    return "1.0.0"  # Версия по умолчанию, если файл отсутствует

def get_latest_version():
    """Получает последнюю версию с GitHub."""
    try:
        response = requests.get(GITHUB_VERSION_URL)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"Ошибка при получении версии с GitHub: {e}")
        return None

def download_and_extract_zip(url, destination):
    """Скачивает ZIP-архив и распаковывает его в указанную папку."""
    try:
        # Скачиваем ZIP-архив
        response = requests.get(url)
        response.raise_for_status()

        # Сохраняем ZIP-архив во временный файл
        zip_path = os.path.join(destination, "repo.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)

        # Распаковываем ZIP-архив
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(destination)

        # Удаляем ZIP-архив после распаковки
        # os.remove(zip_path)

        return True
    except Exception as e:
        print(f"Ошибка при скачивании и распаковке ZIP-архива: {e}")
        return False

def update_files(source_folder, destination_folder):
    """Обновляет только определенные файлы и папки в локальной системе."""
    try:
        files_to_update = ["apps", "bin", "root", "HittiScript", "version.txt", "updater.py", "setup.py"]

        # Удаляем только указанные файлы и папки
        for item in files_to_update:
            item_path = os.path.join(destination_folder, item)
            if os.path.exists(item_path):
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

        # Копируем только новые файлы и папки, если они есть в исходной папке
        for item in files_to_update:
            item_path = os.path.join(source_folder, item)
            dest_path = os.path.join(destination_folder, item)
            if os.path.exists(item_path):
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, dest_path)
                elif os.path.isdir(item_path):
                    shutil.copytree(item_path, dest_path)

        return True
    except Exception as e:
        print(f"Ошибка при обновлении файлов: {e}")
        return False


def update_application():
    """Обновляет приложение, заменяя файлы и папки."""
    try:
        # Создаем временную папку для распаковки
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)

        # Скачиваем и распаковываем ZIP-архив
        if not download_and_extract_zip(GITHUB_ZIP_URL, TEMP_FOLDER):
            return False

        # Путь к распакованной папке (GitHub добавляет суффикс -master)
        extracted_folder = os.path.join(TEMP_FOLDER, "PxStellarOs-master")

        # Проверяем, существует ли папка
        if not os.path.exists(extracted_folder):
            print(f"Ошибка: Папка {extracted_folder} не найдена после распаковки.")
            return False

        # Обновляем файлы и папки
        if not update_files(extracted_folder, os.getcwd()):
            return False

        # Удаляем временную папку после обновления
        shutil.rmtree(TEMP_FOLDER)

        return True
    except Exception as e:
        print(f"Ошибка при обновлении приложения: {e}")
        return False
def reboot_system():
    """
    Перезагружает систему.
    """
    system_platform = platform.system()
    if system_platform == "Windows":
        # Команда для перезагрузки Windows
        QProcess.startDetached("shutdown", ["/r", "/t", "0"])
    elif system_platform == "Linux":
        # Команда для перезагрузки Linux
        QProcess.startDetached("reboot")
    else:
        print(f"Unsupported platform: {system_platform}")

def check_for_updates():
    """Проверяет наличие обновлений и предлагает пользователю обновиться."""
    current_version = get_current_version()
    latest_version = get_latest_version()

    if latest_version and latest_version > current_version:
        app = QApplication(sys.argv)
        dialog = UpdateDialog(current_version, latest_version)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Пользователь согласился на обновление
            progress_dialog = UpdateProgressDialog()
            progress_dialog.show()

            # Имитация процесса обновления
            for i in range(0, 101, 10):
                QTimer.singleShot(i * 100, lambda i=i: progress_dialog.update_progress(i))
                QApplication.processEvents()

            # Закрываем прогресс-бар после завершения
            progress_dialog.close()

            # Запускаем процесс обновления
            if update_application():
                print("Обновление завершено. Перезапустите приложение.")
                reboot_system()
                # sys.exit(0)
            else:
                print("Ошибка при обновлении.")

if __name__ == "__main__":
    print("Запуск приложения...")
    check_for_updates()