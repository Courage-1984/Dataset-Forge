import subprocess
import sys
import os


def test_cli_entrypoint_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"0\n",
        capture_output=True,
        timeout=10,
        env=env,
    )
    assert result.returncode == 0
    assert b"Enter your choice" in result.stdout
