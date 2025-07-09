import os
import datetime
from typing import Optional, List

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "logs")

os.makedirs(LOGS_DIR, exist_ok=True)


def log_operation(action: str, details: str):
    """Log a dataset operation to a dated log file."""
    now = datetime.datetime.now()
    log_filename = now.strftime("%Y-%m-%d") + ".log"
    log_path = os.path.join(LOGS_DIR, log_filename)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {action}: {details}\n")


def list_logs() -> List[str]:
    """List all log files in the logs directory, sorted by date descending."""
    if not os.path.exists(LOGS_DIR):
        return []
    files = [f for f in os.listdir(LOGS_DIR) if f.endswith(".log")]
    return sorted(files, reverse=True)


def read_log(filename: str) -> Optional[str]:
    """Read the contents of a log file."""
    log_path = os.path.join(LOGS_DIR, filename)
    if not os.path.exists(log_path):
        return None
    with open(log_path, "r", encoding="utf-8") as f:
        return f.read()


def read_most_recent_log() -> Optional[str]:
    """Read the most recent log file."""
    logs = list_logs()
    if not logs:
        return None
    return read_log(logs[0])
