import subprocess
import sys
import os


def test_umzi_menu_entrypoint():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # '9' selects Umzi's Dataset_Preprocessing, then '0' to exit
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"9\n0\n0\n",
        capture_output=True,
        timeout=15,
        env=env,
    )
    assert result.returncode == 0
    assert b"Umzi's Dataset_Preprocessing Menu" in result.stdout
    assert b"Best Tile Extraction" in result.stdout
