import os
import sys
import json
from typing import List

def get_project_root() -> str:
    """Возвращает абсолютный путь до папки bin"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_paths() -> List[str]:
    """Загружает пути из path.config и возвращает их"""
    config_path = os.path.join(os.path.dirname(__file__), "path.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["paths"]

def setup_sys_path() -> None:
    """Добавляет все пути из конфига в sys.path"""
    root_dir = get_project_root()
    for rel_path in load_paths():
        abs_path = os.path.abspath(os.path.join(root_dir, rel_path))
        if abs_path not in sys.path:
            sys.path.append(abs_path)

# Автоматически настраиваем пути при импорте
setup_sys_path()