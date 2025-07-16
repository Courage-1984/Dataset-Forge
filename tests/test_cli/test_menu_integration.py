import subprocess
import sys
import os
import pytest


def test_main_menu_entrypoint():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Simulate: 1 (Dataset Management), 0 (Back), 10 (Enhanced Metadata), 0 (Back), 0 (Exit)
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"1\n0\n10\n0\n0\n",
        capture_output=True,
        timeout=20,
        env=env,
    )
    assert result.returncode == 0
    assert b"Dataset Management" in result.stdout
    assert b"Enhanced Metadata Management" in result.stdout
    assert b"Exit" in result.stdout
