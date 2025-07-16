<h3 align="center">
  Dataset Forge
</h3>
<p align="center">
  <img src="https://pomf2.lain.la/f/2ulflln.png" width="300" alt="Dataset Forge Thumbnail"/>
    <!-- <img src="https://files.catbox.moe/9jaag6.png" width="300" alt="Dataset Forge Thumbnail Backup"/> -->
</p>
<div align="center">
  <img src="https://pomf2.lain.la/f/oyxcxpr.png" width="600" alt="Separator"/>
    <!-- <img src="https://files.catbox.moe/0fyb8o.png" width="600" alt="Separator Backup"/> -->
</div>

<p align="center"><i>The all-in-one, modular image dataset utility for ML, with a focus on HQ/LQ image pairs for SISR and general computer vision. CLI-first, highly extensible, and packed with advanced tools for dataset curation, analysis, transformation, and validation.</i></p>

---

## What is Dataset Forge?

**Dataset Forge** is a Python command-line tool for managing image datasets used in machine learning, espescially for SISR. It helps researchers and data scientists:

- Clean and organize image datasets (especially high/low quality pairs for super-resolution)
- Analyze dataset quality and generate reports
- Process, augment, and transform images
- Remove duplicates and validate data
- Extract, view, edit, filter, and anonymize image metadata (EXIF, IPTC, XMP) with the Enhanced Metadata Management menu ([see docs](docs/features.md#🗂️-enhanced-metadata-management-new-july-2025)).
- Align images from two folders (flat or recursive) using projective transformation (SIFT+FLANN) with the '🧭 Align Images' menu option ([see docs](docs/features.md#🧭-align-images-batch-projective-alignment)).

It's designed to streamline the tedious work of preparing image datasets for training ML models, with an intuitive interface and robust processing capabilities. Please see [Features](docs/features.md).

---

## 📖 Documentation Links

- [Features](docs/features.md)
- [Utility Scripts (tools/)](docs/features.md#️-utility-scripts-tools)
- [Special Installation Instructions](docs/special_installation.md)
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
- See [Requirements.txt](requirements.txt) and [Special Installation Instructions](docs/special_installation.md) for full details.
- For GPU acceleration, ensure your CUDA and cuDNN versions match your PyTorch install. See [PyTorch Get Started](https://pytorch.org/get-started/locally/) for details.
- If you use a different CUDA/cuDNN version, install the matching PyTorch build.

> **IMPORTANT:** You must install the correct version of torch/torchvision/torchaudio for your CUDA version **before** running `pip install .`. If you skip this, pip will install the CPU-only version of torch by default. See the Quick Start below for the recommended command.

> **IMPORTANT:** On Windows, python-magic (required for 'Enhanced Directory Tree') requires extra DLLs in System32. See [Special Installation Instructions](docs/special_installation.md) for full details.

> **IMPORTANT:** You must install VapourSynth before installing or using [getnative](https://github.com/Infiziert90/getnative). See the [Requirements.txt](requirements.txt) and [Special Installation Instructions](docs/special_installation.md) for full details.

> **IMPORTANT:** You must compile/buiild [resdet](https://github.com/0x09/resdet) first before using resdet. See the [Requirements.txt](requirements.txt) and [Special Installation Instructions](docs/special_installation.md) for full details.

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

3. **Run the application:**
   ```bash
   dataset-forge
   # or
   py main.py
   # or
   ./run.bat
   ```

---

## 📝 TODO / Planned Features

This section collects all future feature/functionality ideas, goals, and implementation notes for Dataset Forge. Add new ideas here to keep the roadmap in one place.

- [ ] **Debug Mode**: I want to add a *Debug Mode* to my project, which when used, activates the showing of more verbose output and debug output/print
- [ ] **tl;dr**: Create a '# Features (tl;dr)' section in ./docs/features.md
- [ ] ***Packaging***: "Compile Dataset-Forge" AND/OR "Create docker file/container"
- [ ] **Augmentation**: Document augmentation operations, and degradations and implement 'Advanced Data Augmentation'
- [x] **Dataset Health Scoring**: Add a "Dataset Health Scoring" workflow and menu option
- [ ] **Batch Scripts**: Save and replay complex multi-step operations/workflows
- [ ] **Phhofm's sisr**: Investigate Phhofm's [sisr](https://github.com/Phhofm/sisr) for stuff i can add to DF
- [ ] **the-database's img-ab**: Fork and improve.

- [ ] **Example**: Improve error reporting for Example workflows

<!-- Add your TODOs and feature ideas below -->

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

<!-- Badges -->
<p align="center">
  <a href="https://github.com/Courage-1984/Dataset-Forge/actions"><img src="https://img.shields.io/github/workflow/status/Courage-1984/Dataset-Forge/CI?label=build" alt="Build Status"></a>
  <a href="https://github.com/Courage-1984/Dataset-Forge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-CC--BY--SA--4.0-blue" alt="License"></a>
  <a href="https://img.shields.io/badge/python-3.12%2B-blue.svg"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg" alt="Python Version"></a>
  <a href="https://img.shields.io/github/issues/Courage-1984/Dataset-Forge"><img src="https://img.shields.io/github/issues/Courage-1984/Dataset-Forge" alt="Issues"></a>
  <a href="https://img.shields.io/github/stars/Courage-1984/Dataset-Forge"><img src="https://img.shields.io/github/stars/Courage-1984/Dataset-Forge" alt="Stars"></a>
  <a href="https://img.shields.io/github/last-commit/Courage-1984/Dataset-Forge"><img src="https://img.shields.io/github/last-commit/Courage-1984/Dataset-Forge" alt="Last Commit"></a>
</p>

# VERBOSE:

## 🧪 Comprehensive Test Suite

Dataset Forge now includes a robust, cross-platform test suite covering all major features:

- DPID implementations (BasicSR, OpenMMLab, Phhofm)
- CBIR and deduplication workflows
- Report generation
- Audio feedback, memory, parallel, and progress utilities
- Session state, config, and error handling

**Run all tests:**

```sh
venv312\Scripts\activate
venv312\Scripts\python -m pytest --maxfail=5 --disable-warnings -v tests/
```

All new features and bugfixes must include appropriate tests. See [docs/features.md](docs/features.md) and [docs/usage.md](docs/usage.md) for details.

## Project Architecture

A high-level overview of Dataset Forge's modular architecture:

```mermaid
flowchart TD
    A["CLI Entrypoint (main.py)"] --> B["Menus (dataset_forge/menus)"]
    B --> C["Actions (dataset_forge/actions)"]
    C --> D["Utils (dataset_forge/utils)"]
    C --> E["DPID Implementations (dataset_forge/dpid)"]
    B --> F["Session State (menus/session_state.py)"]
    B --> G["System Monitoring, Settings, User Profile Menus"]
    C --> H["CBIR, Deduplication, Preprocessing, etc."]
    D --> I["Memory, Parallel, Progress, Color, Audio, File Ops"]
    B --> J["Reports, Configs, Assets"]
    subgraph "External"
      K["User Input/Output"]
      L["Third-party Libraries"]
    end
    A --> K
    D --> L
    E --> L
    F --> D
    G --> D
    H --> D
    J --> D
    J --> L
```
---

## 🧑‍💻 Static Analysis & Code Quality

Dataset Forge includes a comprehensive static analysis tool for maintainers and contributors:

- **Location:** `tools/find_code_issues/find_code_issues.py`
- **Checks:**
  - Unused (dead) code, functions, classes, and methods
  - Untested code (missing test coverage)
  - Functions/classes defined but never called
  - Test/code mapping (tests without code, code without tests)
  - Missing docstrings in public functions/classes/methods
  - Unused imports/variables, and more
- **How to run:**
  ```sh
  python tools/find_code_issues/find_code_issues.py [options]
  # Run with no options to perform all checks
  ```
- **Output:**
  - Overwrites files in `tools/find_code_issues/` on each run:
    - `find_code_issues.log` (raw output)
    - `find_code_issues_report.txt` (actionable summary)
    - `find_code_issues_view.txt` (detailed results)
- **Requirements:**
  - `pip install vulture pytest pytest-cov coverage pyan3 pyflakes`

See [docs/usage.md](docs/usage.md) and [docs/features.md](docs/features.md) for details.
