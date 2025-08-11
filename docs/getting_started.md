# Getting Started

> **UI/UX Note:**  
> All CLI output in Dataset Forge uses the Catppuccin Mocha color scheme for a consistent, visually appealing experience. All prompts, menus, and progress bars are styled using the centralized color utilities.

Welcome to Dataset Forge!  
This guide will help you install and launch Dataset Forge for the first time.

---

## Prerequisites

- **Python**: 3.12+ (see [requirements.txt](../requirements.txt))
- **OS**: Windows (primary)
- **CUDA/cuDNN**: For GPU acceleration (see [Special Installation](special_installation.md))
- **RAM**: 8GB+ (16GB+ recommended)
- **Storage**: SSD recommended

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Courage-1984/Dataset-Forge.git
   cd Dataset-Forge
   ```

2. **Set up the environment:**

   **Option A: Automated Installation (Recommended)**

   ```bash
   # Windows (easiest)
   install.bat
   # or
   tools\install.bat

   # Or manually
   py -3.12 -m venv venv312
   venv312\Scripts\activate
   python tools\install.py
   ```

   **Option B: Manual Installation**

   ```bash
   py -3.12 -m venv venv312
   venv312\Scripts\activate
   python -m pip install --upgrade pip setuptools wheel
   # Install the correct CUDA-enabled torch/torchvision/torchaudio first!
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   pip install -r requirements.txt
   pip install -e .
   ```

   **Option C: Using setup.py directly**

   ```bash
   py -3.12 -m venv venv312
   venv312\Scripts\activate
   python setup.py install
   ```

   > **Note:** For other CUDA versions, see [PyTorch Get Started](https://pytorch.org/get-started/locally/).

---

## First Run

```bash
./run.bat
OR
venv312\Scripts\activate
py main.py
OR
dataset-forge
```

---

## Special Installation Notes

- On Windows, `python-magic` requires extra DLLs.
- You must install VapourSynth before using [getnative](https://github.com/Infiziert90/getnative).
- You must compile/build [resdet](https://github.com/0x09/resdet) before using it.
- AND MORE;;;

- See [Special Installation Instructions](special_installation.md) for further details.

---

## Need Help?

- For common issues, see the [Troubleshooting Guide](troubleshooting.md).
- For advanced configuration, see [Advanced Features](advanced.md).

---

## See Also

- [Features](features.md)
- [Usage Guide](usage.md)
- [Advanced Features](advanced.md)
- [Project Architecture](architecture.md)
