import sys
import os
import requests
from PyQt6.QtWidgets import QApplication, QMessageBox

# Путь к файлу с версией
VERSION_FILE = "version.txt"
# URL к файлу с версией на GitHub
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/ваш-репозиторий/ваш-проект/main/version.txt"
# URL к файлу setup.py на GitHub
GITHUB_SETUP_URL = "https://raw.githubusercontent.com/ваш-репозиторий/ваш-проект/main/setup.py"

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

def download_file(url, destination):
    """Скачивает файл с указанного URL и сохраняет его в destination."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(destination, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Ошибка при скачивании файла: {e}")
        return False

def update_application():
    """Обновляет приложение, заменяя setup.py на новую версию."""
    try:
        # Скачиваем новую версию setup.py
        if not download_file(GITHUB_SETUP_URL, "setup.py"):
            return False

        # Скачиваем новую версию version.txt
        if not download_file(GITHUB_VERSION_URL, "version.txt"):
            return False

        return True
    except Exception as e:
        print(f"Ошибка при обновлении приложения: {e}")
        return False

def ask_for_update(current_version, latest_version):
    """Спрашивает пользователя, хочет ли он обновиться."""
    app = QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Question)
    msg.setText(f"Доступна новая версия: {latest_version}\nТекущая версия: {current_version}\nХотите обновиться?")
    msg.setWindowTitle("Обновление")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    return msg.exec() == QMessageBox.StandardButton.Yes

def main():
    # Получаем текущую и последнюю версии
    current_version = get_current_version()
    latest_version = get_latest_version()

    if not latest_version:
        print("Не удалось получить информацию о новой версии.")
        return

    if latest_version > current_version:
        print(f"Доступна новая версия: {latest_version}")
        if ask_for_update(current_version, latest_version):
            print("Начинаем обновление...")
            if update_application():
                print("Обновление завершено. Перезапустите приложение.")
                # Закрываем текущее приложение
                sys.exit(0)
            else:
                print("Ошибка при обновлении.")
        else:
            print("Обновление отменено пользователем.")
    else:
        print("У вас установлена последняя версия.")

if __name__ == "__main__":
    main()
