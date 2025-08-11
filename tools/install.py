#!/usr/bin/env python3
"""
Installation script for Dataset Forge.

This script creates a virtual environment and installs all required dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataset_forge.utils.printing import print_info, print_success, print_error

# Configuration
PROJECT_ROOT = project_root  # Use the project root we calculated above
VENV_DIR = "venv312"
PYTHON_EXE = sys.executable

# PyTorch packages for CUDA 12.1
TORCH_PACKAGES = [
    "torch",
    "torchvision",
    "torchaudio",
]
CUDA_INDEX_URL = "https://download.pytorch.org/whl/cu121"


# Use imported print functions directly


def check_python_version():
    if sys.version_info < (3, 12):
        print_error("Python 3.12+ is required. Aborting.")
        sys.exit(1)


def run(cmd, env=None, check=True, cwd=None):
    print_info(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=check, env=env, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        sys.exit(e.returncode)


def create_venv():
    if os.path.isdir(VENV_DIR):
        print_info(f"Virtual environment '{VENV_DIR}' already exists.")
        return
    print_info(f"Creating virtual environment: {VENV_DIR}")
    run([PYTHON_EXE, "-m", "venv", VENV_DIR])


def get_venv_python():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "python")


def get_venv_pip():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "pip")


def install_torch():
    pip = get_venv_pip()
    print_info("Installing torch, torchvision, torchaudio (CUDA 12.1)...")
    run(
        [
            pip,
            "install",
            *TORCH_PACKAGES,
            "--index-url",
            CUDA_INDEX_URL,
        ]
    )


def upgrade_pip_setuptools_wheel():
    python = get_venv_python()
    print_info("Upgrading pip, setuptools, wheel in the virtual environment...")
    run([python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])


# def install_pepeline_pepedpid():
#     pip = get_venv_pip()
#     print_info("Installing pepeline and pepedpid (required for DPID workflows)...")
#     run([pip, "install", "pepeline", "pepedpid"])


def install_requirements():
    pip = get_venv_pip()
    req_path = os.path.join(PROJECT_ROOT, "requirements.txt")
    print_info(f"Installing requirements from {req_path} ...")
    run([pip, "install", "-r", req_path])


# def install_pepedp():
#     pip = get_venv_pip()
#     print_info("Installing pepedp (required for Umzi's Dataset Preprocessing)...")
#     run([pip, "install", "pepedp"])


# Comment out or remove install_project()
# def install_project():
#     pip = get_venv_pip()
#     print_info("Installing Dataset Forge and all requirements...")
#     run([pip, "install", "."], cwd=PROJECT_ROOT)


def main():
    check_python_version()
    create_venv()
    upgrade_pip_setuptools_wheel()
    install_torch()
    # install_pepeline_pepedpid()
    install_requirements()
    # install_pepedp()
    print_success("Installation complete. Dataset Forge is ready to use!")
    print_info("First run options:")
    print_info("  1. ./run.bat")
    print_info("  2. venv312\\Scripts\\activate && py main.py")
    print_info("  3. dataset-forge (if installed as CLI entry point)")
    print_info("")
    print_info(
        "See Special Installation Instructions (docs/special_installation.md) for details on extra dependencies and troubleshooting."
    )
    if os.name == "nt":
        print_info(
            f"Activate: {os.path.relpath(VENV_DIR, PROJECT_ROOT)}\\Scripts\\activate.bat"
        )
    else:
        print_info(
            f"Activate: source {os.path.relpath(VENV_DIR, PROJECT_ROOT)}/bin/activate"
        )


if __name__ == "__main__":
    main()
