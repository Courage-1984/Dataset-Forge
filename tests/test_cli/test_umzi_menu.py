import subprocess
import sys
import os


def test_umzi_menu_entrypoint():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # '1' selects Dataset Management, '7' selects Umzi's Dataset Preprocessing, then '0' to exit
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"1\n7\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n",
        capture_output=True,
        timeout=15,
        env=env,
    )
    assert result.returncode == 0
    stdout = result.stdout.decode("utf-8")
    assert "🐸 Umzi's Dataset Preprocessing (PepeDP)" in stdout
    assert "Best Tile Extraction" in stdout
