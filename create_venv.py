import os
import sys
import subprocess
import platform

VENV_DIR = "venv"
PYTHON = sys.executable
REQUIREMENTS = "requirements.txt"

# CUDA version for torch/timm
CUDA_VERSION = "cu121"  # Change if you want a different CUDA version

# Torch and timm install commands
TORCH_URL = f"https://download.pytorch.org/whl/{CUDA_VERSION}"
TORCH_CMD = [
    "pip",
    "install",
    "torch",
    "torchvision",
    "torchaudio",
    f"--index-url={TORCH_URL}",
]

TIMM_CMD = ["pip", "install", "timm[torch]"]


def run(cmd, env=None):
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd, env=env)


def main():
    # 1. Create venv
    if not os.path.exists(VENV_DIR):
        run([PYTHON, "-m", "venv", VENV_DIR])

    # 2. Get pip path
    if platform.system() == "Windows":
        pip_path = os.path.join(VENV_DIR, "Scripts", "pip.exe")
        python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        pip_path = os.path.join(VENV_DIR, "bin", "pip")
        python_path = os.path.join(VENV_DIR, "bin", "python")

    # 3. Upgrade pip
    run([python_path, "-m", "pip", "install", "--upgrade", "pip"])

    # 4. Install requirements.txt
    run([pip_path, "install", "-r", REQUIREMENTS])

    # 5. Install CUDA version of torch
    run([pip_path] + TORCH_CMD[1:])

    # 6. Install CUDA version of timm
    run([pip_path] + TIMM_CMD[1:])

    print("\nSetup complete! Activate your venv with:")
    if platform.system() == "Windows":
        print(f"  {VENV_DIR}\\Scripts\\activate")
    else:
        print(f"  source {VENV_DIR}/bin/activate")


if __name__ == "__main__":
    main()
