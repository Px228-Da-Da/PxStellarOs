import sys
import os
import requests
import zipfile
import shutil
from PyQt6.QtWidgets import QApplication, QMessageBox

# Путь к файлу с версией
VERSION_FILE = "version.txt"
# URL к файлу с версией на GitHub
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/Px228-Da-Da/PxStellarOs/master/version.txt"
# URL к ZIP-архиву репозитория
GITHUB_ZIP_URL = "https://github.com/Px228-Da-Da/PxStellarOs/archive/refs/heads/master.zip"
# Временная папка для распаковки
TEMP_FOLDER = "temp_update"

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
        os.remove(zip_path)

        return True
    except Exception as e:
        print(f"Ошибка при скачивании и распаковке ZIP-архива: {e}")
        return False

def update_files(source_folder, destination_folder):
    """Обновляет файлы и папки в локальной системе."""
    try:
        # Удаляем старые файлы и папки (кроме временной папки)
        for item in os.listdir(destination_folder):
            item_path = os.path.join(destination_folder, item)
            if item != TEMP_FOLDER:  # Пропускаем временную папку
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

        # Копируем новые файлы и папки
        for item in os.listdir(source_folder):
            item_path = os.path.join(source_folder, item)
            dest_path = os.path.join(destination_folder, item)
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
