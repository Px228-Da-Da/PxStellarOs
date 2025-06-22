import os
import json
from pathlib import Path

def get_project_root():
    """Возвращает абсолютный путь к корню проекта"""
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent.parent  # Поднимаемся на 4 уровня вверх из bin/sys/path/

def load_update_settings():
    """Загружает настройки обновления из path.json"""
    root_dir = get_project_root()
    config_path = root_dir / "bin" / "sys" / "path" / "path.json"
    
    default_settings = {
        "version_file": "bin/sys/updates/version.txt",
        "requirements_file": "bin/sys/updates/requirements.txt",
        "github_urls": {
            "version": "https://raw.githubusercontent.com/Px228-Da-Da/PxStellarOs/{branch}/version.txt",
            "zip": "https://github.com/Px228-Da-Da/PxStellarOs/archive/refs/heads/{branch}.zip"
        },
        "temp_folder": "temp_update",
        "branches": {
            "Master": "master",
            "Testing": "testing"
        }
    }
    
    try:
        with open(config_path, "r", encoding='utf-8') as f:
            config = json.load(f)
        return config.get("update_settings", default_settings)
    except Exception as e:
        print(f"Не удалось загрузить настройки из {config_path}, используются значения по умолчанию. Ошибка: {e}")
        return default_settings