import os
import json

CONFIGS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "configs"
)
ACTIVE_PROFILE_PATH = os.path.join(CONFIGS_DIR, "user_profile_active.txt")
PROFILE_PREFIX = "user_profile_"
PROFILE_SUFFIX = ".json"

DEFAULT_PROFILE = {"favorites": [], "presets": [], "favorite_paths": [], "settings": {}}


def get_profile_path(profile_name):
    return os.path.join(CONFIGS_DIR, f"{PROFILE_PREFIX}{profile_name}{PROFILE_SUFFIX}")


def list_profiles():
    if not os.path.exists(CONFIGS_DIR):
        return []
    return [
        f[len(PROFILE_PREFIX) : -len(PROFILE_SUFFIX)]
        for f in os.listdir(CONFIGS_DIR)
        if f.startswith(PROFILE_PREFIX) and f.endswith(PROFILE_SUFFIX)
    ]


def create_profile(profile_name):
    path = get_profile_path(profile_name)
    if os.path.exists(path):
        raise ValueError("Profile already exists.")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_PROFILE, f, indent=2, ensure_ascii=False)
    set_active_profile(profile_name)


def delete_profile(profile_name):
    path = get_profile_path(profile_name)
    if os.path.exists(path):
        os.remove(path)
        # If deleted profile was active, unset active
        if get_active_profile() == profile_name:
            set_active_profile(None)


def set_active_profile(profile_name):
    if profile_name is None:
        if os.path.exists(ACTIVE_PROFILE_PATH):
            os.remove(ACTIVE_PROFILE_PATH)
    else:
        with open(ACTIVE_PROFILE_PATH, "w", encoding="utf-8") as f:
            f.write(profile_name)


def get_active_profile():
    if not os.path.exists(ACTIVE_PROFILE_PATH):
        profiles = list_profiles()
        if profiles:
            set_active_profile(profiles[0])
            return profiles[0]
        return None
    with open(ACTIVE_PROFILE_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_user_profile():
    profile_name = get_active_profile()
    if not profile_name:
        return DEFAULT_PROFILE.copy()
    path = get_profile_path(profile_name)
    if not os.path.exists(path):
        return DEFAULT_PROFILE.copy()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_profile(profile):
    profile_name = get_active_profile()
    if not profile_name:
        raise ValueError("No active profile set.")
    path = get_profile_path(profile_name)
    os.makedirs(CONFIGS_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def add_favorite(menu_item):
    profile = load_user_profile()
    if menu_item not in profile["favorites"]:
        profile["favorites"].append(menu_item)
        save_user_profile(profile)


def remove_favorite(menu_item):
    profile = load_user_profile()
    if menu_item in profile["favorites"]:
        profile["favorites"].remove(menu_item)
        save_user_profile(profile)


def add_preset(preset):
    profile = load_user_profile()
    profile["presets"].append(preset)
    save_user_profile(profile)


def remove_preset(index):
    profile = load_user_profile()
    if 0 <= index < len(profile["presets"]):
        profile["presets"].pop(index)
        save_user_profile(profile)


def add_favorite_path(path):
    profile = load_user_profile()
    if path not in profile["favorite_paths"]:
        profile["favorite_paths"].append(path)
        save_user_profile(profile)


def remove_favorite_path(path):
    profile = load_user_profile()
    if path in profile["favorite_paths"]:
        profile["favorite_paths"].remove(path)
        save_user_profile(profile)


def update_setting(key, value):
    profile = load_user_profile()
    profile["settings"][key] = value
    save_user_profile(profile)


def get_setting(key, default=None):
    profile = load_user_profile()
    return profile["settings"].get(key, default)
