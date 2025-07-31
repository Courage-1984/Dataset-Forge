#!/usr/bin/env python
"""
run_tests.py - Flexible test runner for Dataset Forge

Usage:
    python tools/run_tests.py [option]

Options:
    1   Basic: venv312\\Scripts\\activate + pytest
    2   Recommended: venv312\\Scripts\\activate + venv312\\Scripts\\python -m pytest --maxfail=5 --disable-warnings -v tests/
    3   Verbose: venv312\\Scripts\\activate + venv312\\Scripts\\python -m pytest -s --maxfail=5 --disable-warnings -v tests/

If no option is given, a menu will be shown.

Notes:
- Option 3 disables output capture (-s), so you see all print/debug output.
- Always activate the venv before running tests.
"""
import sys
import subprocess
import os

VENV_ACTIVATE = os.path.join("venv312", "Scripts", "activate")
PYTHON_EXE = os.path.join("venv312", "Scripts", "python")

TEST_COMMANDS = {
    "1": [f"call {VENV_ACTIVATE}", "pytest"],
    "2": [
        f"call {VENV_ACTIVATE}",
        f"{PYTHON_EXE} -m pytest --maxfail=5 --disable-warnings -v tests/",
    ],
    "3": [
        f"call {VENV_ACTIVATE}",
        f"{PYTHON_EXE} -m pytest -s --maxfail=5 --disable-warnings -v tests/",
    ],
    "4": [
        f"call {VENV_ACTIVATE}",
        f"{PYTHON_EXE} -m pytest --timeout=60 --maxfail=5 --disable-warnings -v tests/",
    ],
    "5": [
        f"call {VENV_ACTIVATE}",
        f"{PYTHON_EXE} -m pytest --full-trace --maxfail=5 --disable-warnings -v tests/",
    ],
}

MENU = """
Select test run mode:

1. Basic: venv312\\Scripts\\activate + pytest
2. Recommended: venv312\\Scripts\\activate + venv312\\Scripts\\python -m pytest --maxfail=5 --disable-warnings -v tests/
3. Verbose: venv312\\Scripts\\activate + venv312\\Scripts\\python -m pytest -s --maxfail=5 --disable-warnings -v tests/ (no output capture)
4. Timeout: venv312\\Scripts\\activate + venv312\\Scripts\\python -m pytest --timeout=60 --maxfail=5 --disable-warnings -v tests/
5. Full Trace: venv312\\Scripts\\activate + venv312\\Scripts\\python -m pytest --full-trace --maxfail=5 --disable-warnings -v tests/

Enter 1, 2, 3, 4, or 5 (or q to quit): """


def print_info(msg: str):
    print(f"[INFO] {msg}")


def print_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)


def run_commands(commands):
    # On Windows, each command must be run in a new shell with venv activated
    for i, cmd in enumerate(commands):
        print_info(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print_error(f"Command failed: {cmd}")
            sys.exit(result.returncode)
    print_info("All commands completed successfully.")


def main():
    if len(sys.argv) > 1:
        choice = sys.argv[1].strip()
    else:
        choice = input(MENU).strip()
    if choice.lower() in ("q", "quit", "exit"):
        print_info("Exiting.")
        sys.exit(0)
    if choice not in TEST_COMMANDS:
        print_error("Invalid option. Please enter 1, 2, 3, 4, or 5.")
        sys.exit(1)
    commands = TEST_COMMANDS[choice]
    run_commands(commands)


if __name__ == "__main__":
    main()
