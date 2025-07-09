import os
from typing import List

HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..", ".path_history"
)
MAX_HISTORY = 20


def _read_history() -> List[str]:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


def _write_history(history: List[str]):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for path in history[:MAX_HISTORY]:
            f.write(path + "\n")


def add_path(path: str):
    path = os.path.abspath(path)
    history = _read_history()
    if path in history:
        history.remove(path)
    history.insert(0, path)
    _write_history(history)


def get_history() -> List[str]:
    return _read_history()


def get_last_path() -> str:
    history = _read_history()
    return history[0] if history else None
