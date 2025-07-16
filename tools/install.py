import os
import sys
import subprocess
import shutil

VENV_DIR = "venv312"
PYTHON_EXE = sys.executable

CUDA_INDEX_URL = "https://download.pytorch.org/whl/cu121"
TORCH_PACKAGES = [
    "torch",
    "torchvision",
    "torchaudio",
]


def print_info(msg: str):
    print(f"[INFO] {msg}")


def print_success(msg: str):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")


def print_error(msg: str):
    print(f"\033[91m[ERROR]\033[0m {msg}")


def check_python_version():
    if sys.version_info < (3, 12):
        print_error("Python 3.12+ is required. Aborting.")
        sys.exit(1)


def run(cmd, env=None, check=True):
    print_info(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=check, env=env)
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


def install_project():
    pip = get_venv_pip()
    print_info("Installing Dataset Forge and all requirements...")
    run([pip, "install", "."])


def main():
    check_python_version()
    create_venv()
    install_torch()
    install_project()
    print_success(
        "Installation complete. To run, activate the venv and use: dataset-forge"
    )
    if os.name == "nt":
        print_info(f"Activate: {VENV_DIR}\\Scripts\\activate.bat")
    else:
        print_info(f"Activate: source {VENV_DIR}/bin/activate")


if __name__ == "__main__":
    main()
