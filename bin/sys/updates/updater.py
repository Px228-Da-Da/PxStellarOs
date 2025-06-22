import sys
import os
from pathlib import Path

# Добавляем путь к модулям проекта
sys.path.append(str(Path(__file__).parent / "bin"))
from dependencies import *
from bin.sys.path.config_loader import load_update_settings

# Загружаем настройки
UPDATE_SETTINGS = load_update_settings()

# Используем настройки
VERSION_FILE = UPDATE_SETTINGS["version_file"]
REQUIREMENTS_FILE = UPDATE_SETTINGS["requirements_file"]
GITHUB_VERSION_URL = UPDATE_SETTINGS["github_urls"]["version"]
GITHUB_ZIP_URL = UPDATE_SETTINGS["github_urls"]["zip"]
TEMP_FOLDER = UPDATE_SETTINGS["temp_folder"]
UPDATE_BRANCHES = UPDATE_SETTINGS["branches"]

class UpdateDialog(QDialog):
    def __init__(self, current_version, latest_version, branch, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Обновление")
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if self.layout():
            QVBoxLayout().addWidget(QLabel())
            self.setLayout(None)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(
            f"Доступна новая версия ({branch}): {latest_version}\n"
            f"Текущая версия: {current_version}"
        )
        self.label.setFont(QFont("Arial", 12))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.update_button = QPushButton("Обновиться")
        self.update_button.clicked.connect(self.start_update)
        layout.addWidget(self.update_button)

        self.later_button = QPushButton("Позже")
        self.later_button.clicked.connect(self.reject)
        layout.addWidget(self.later_button)

    def start_update(self):
        self.accept()
        parent = self.parent()
        if parent and hasattr(parent, "run_update"):
            parent.run_update()
        else:
            print("Ошибка: run_update() не найден в родительском объекте.")

    def paintEvent(self, event):
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

        self.label = QLabel("Обновление ОС...")
        self.label.setFont(QFont("Arial", 12))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

def get_current_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    return "1.0.0"

def get_latest_version(branch="master"):
    try:
        url = GITHUB_VERSION_URL.format(branch=branch)
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"Ошибка при получении версии с GitHub: {e}")
        return None

def download_and_extract_zip(branch, destination):
    try:
        url = GITHUB_ZIP_URL.format(branch=branch)
        response = requests.get(url)
        response.raise_for_status()

        zip_path = os.path.join(destination, "repo.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(destination)

        return True
    except Exception as e:
        print(f"Ошибка при скачивании и распаковке ZIP-архива: {e}")
        return False

def update_files(source_folder, destination_folder):
    try:
        files_to_update = ["apps", "bin", "root", "HittiScript", "version.txt", "updater.py", "setup.py"]

        for item in files_to_update:
            item_path = os.path.join(destination_folder, item)
            if os.path.exists(item_path):
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

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

def install_requirements():
    """Устанавливает зависимости из requirements.txt"""
    try:
        requirements_path = Path(REQUIREMENTS_FILE)
        if not requirements_path.exists():
            print(f"Файл требований не найден: {requirements_path}")
            return False
            
        print(f"Установка зависимостей из {requirements_path}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке зависимостей: {e.stderr}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return False

def update_application(branch="master"):
    try:
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)

        if not download_and_extract_zip(branch, TEMP_FOLDER):
            return False

        extracted_folder = os.path.join(TEMP_FOLDER, f"PxStellarOs-{branch}")

        if not os.path.exists(extracted_folder):
            print(f"Ошибка: Папка {extracted_folder} не найдена после распаковки.")
            return False

        if not update_files(extracted_folder, os.getcwd()):
            return False

        # Устанавливаем зависимости после обновления файлов
        if not install_requirements():
            print("Предупреждение: Не удалось установить все зависимости")

        shutil.rmtree(TEMP_FOLDER)
        return True
    except Exception as e:
        print(f"Ошибка при обновлении приложения: {e}")
        return False

def check_for_updates(branch="master"):
    current_version = get_current_version()
    latest_version = get_latest_version(branch)

    if latest_version and latest_version > current_version:
        app = QApplication(sys.argv)
        dialog = UpdateDialog(current_version, latest_version, branch.capitalize())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            progress_dialog = UpdateProgressDialog()
            progress_dialog.show()

            for i in range(0, 101, 10):
                QTimer.singleShot(i * 100, lambda i=i: progress_dialog.update_progress(i))
                QApplication.processEvents()

            progress_dialog.close()

            if update_application(branch):
                print("Обновление завершено. Перезагруска.")
            else:
                print("Ошибка при обновлении.")

if __name__ == "__main__":
    print("Запуск приложения...")
    check_for_updates()