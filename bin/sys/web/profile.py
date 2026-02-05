import os, sys, json
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineCore import QWebEngineProfile

_profile = None

def find_os_root():
    # Ищем папку проекта, где реально лежит root/bin/user.config
    candidates = [
        os.getcwd(),
        os.path.dirname(os.path.abspath(__file__)),
        os.path.dirname(os.path.abspath(sys.argv[0])),
    ]
    for start in candidates:
        p = os.path.abspath(start)
        for _ in range(8):  # подняться вверх до 8 уровней
            test = os.path.join(p, "root", "bin", "user.config")
            if os.path.exists(test):
                return p
            p = os.path.dirname(p)
    # fallback (если не нашли)
    return os.path.dirname(os.path.abspath(sys.argv[0]))

BASE_DIR = find_os_root()
USER_CONFIG_PATH = os.path.join(BASE_DIR, "root", "bin", "user.config")

def get_current_username():
    try:
        with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        username = data.get("user_name", "Unknown User")
    except Exception as e:
        print("[ERROR] user.config read:", e)
        username = "Unknown User"
    print(f"[INFO] Current User Name: {username}")
    return username

username = get_current_username()

def get_shared_profile(parent=None):
    global _profile
    if _profile is not None:
        return _profile

    base_dir = os.path.join(BASE_DIR, "root", username, "browser")
    storage_dir = os.path.join(base_dir, "web_profile")
    cache_dir   = os.path.join(base_dir, "web_cache")
    os.makedirs(storage_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    print("[WEB] BASE_DIR     =", BASE_DIR)
    print("[WEB] storage_dir =", storage_dir)
    print("[WEB] cache_dir   =", cache_dir)

    # parent намеренно игнорируем, чтобы профиль не удалялся вместе с окном
    _profile = QWebEngineProfile("StellarSharedProfile", None)
    _profile.setPersistentStoragePath(storage_dir)
    _profile.setCachePath(cache_dir)
    _profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
    return _profile
