<h3 align="center">
  Dataset Forge
</h3>
<p align="center">
  <img src="https://pomf2.lain.la/f/2ulflln.png" width="300" alt="Dataset Forge Thumbnail"/>
</p>
<div align="center">
  <img src="https://pomf2.lain.la/f/oyxcxpr.png" width="600" alt="Separator"/>
</div>

<p align="center"><i>The all-in-one, modular image dataset utility for ML, with a focus on HQ/LQ image pairs for SISR and general computer vision. CLI-first, highly extensible, and packed with advanced tools for dataset curation, analysis, transformation, and validation.</i></p>

---

## What is Dataset Forge?

**Dataset Forge** is a Python command-line tool for managing image datasets used in machine learning. It helps researchers and data scientists:

- Clean and organize image datasets (especially high/low quality pairs for super-resolution)
- Analyze dataset quality and generate reports
- Process, augment, and transform images
- Remove duplicates and validate data

It's designed to streamline the tedious work of preparing image datasets for training ML models, with an intuitive interface and robust processing capabilities.

---

## 📖 Documentation Links

- [Features](docs/features.md)
- [Usage Guide](docs/usage.md)
- [Advanced Features & Configuration](docs/advanced.md)
- [Project Architecture](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Contributing](docs/contributing.md)
- [Style Guide](docs/style_guide.md)
- [FAQ](docs/faq.md)
- [Changelog](docs/changelog.md)
- [License](docs/license.md)

---

## 🖥️ Supported Platforms & Requirements

- **Python**: 3.12+ (tested on 3.12)
- **OS**: Windows (primary)
- **CUDA**: 12.1+ (for GPU acceleration)
- **cuDNN**: 9.1+ (for GPU acceleration, required for PyTorch CUDA, tested on 9.1)
- **RAM**: 8GB+ (16GB+ recommended for large datasets)
- **Storage**: SSD recommended for faster I/O
- **VapourSynth**: Required for getnative functionality. **You must install VapourSynth before installing or using getnative.**
- **python-magic**: Requires special DLLs on Windows. See [Special Installation Instructions](docs/special_installation.md).
- See [Requirements](docs/advanced.md#requirements) and [Special Installation Instructions](docs/special_installation.md) for full details.

**Dependency Matrix:**

| Python | CUDA Toolkit | cuDNN | PyTorch | OS      |
| ------ | ------------ | ----- | ------- | ------- |
| 3.12   | 12.1         | 8.9+  | 2.2.0+  | Windows |
| 3.8+   | 11.8/12.1    | 8.6+  | 2.0.0+  | Linux   |

- For GPU acceleration, ensure your CUDA and cuDNN versions match your PyTorch install. See [PyTorch Get Started](https://pytorch.org/get-started/locally/) for details.
- If you use a different CUDA/cuDNN version, install the matching PyTorch build.

> **IMPORTANT:** You must install the correct version of torch/torchvision/torchaudio for your CUDA version **before** running `pip install .`. If you skip this, pip will install the CPU-only version of torch by default. See the Quick Start below for the recommended command.
> **IMPORTANT:** You must install VapourSynth before installing or using getnative. See the requirements.txt and docs for details.
> **IMPORTANT:** On Windows, python-magic requires extra DLLs in System32. See [Special Installation Instructions](docs/special_installation.md).

---

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Courage-1984/Dataset-Forge.git
   cd Dataset-Forge
   ```
2. **Set up the environment:**
   ```bash
   py -3.12 -m venv venv312
   venv312\Scripts\activate
   # Install the correct CUDA-enabled torch/torchvision/torchaudio first!
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   pip install .
   ```
   > **Note:** If you use a different CUDA version, see https://pytorch.org/get-started/locally/ for the right install command.
   > **Note:** If you plan to use getnative, you must install VapourSynth before installing or using getnative. See requirements.txt and docs for details.
   > **Note:** On Windows, python-magic requires extra DLLs in System32. See [Special Installation Instructions](docs/special_installation.md).
3. **Run the application:**
   ```bash
   dataset-forge
   # or
   py main.py
   # or
   ./run.bat
   ```

---

## 💜 Credits

- Thanks [Kim2091](https://github.com/Kim2091)❤️ for [helpful-scripts](https://github.com/Kim2091/helpful-scripts)
- Thanks [umzi2](https://github.com/umzi2)❤️ for [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer) & [Dataset_Preprocessing](https://github.com/umzi2/Dataset_Preprocessing)
- Thanks [the-database](https://github.com/the-database)❤️ for [traiNNer-redux](https://github.com/the-database/traiNNer-redux)
- Thanks [Phhofm](https://github.com/Phhofm)❤️ for [sisr](https://github.com/Phhofm/sisr)

---

## License

This project is licensed under the Creative Commons CC-BY-SA-4.0. See [LICENSE](LICENSE) for details.

---

<!-- Badges (add more as needed) -->
<p align="center">
  <a href="https://github.com/Courage-1984/Dataset-Forge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-CC--BY--SA--4.0-blue" alt="License"></a>
  <!-- Add CI/build/test badges here if available -->
</p>
