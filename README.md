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

**Dataset Forge** is a professional-grade Python CLI utility for managing, analyzing, and transforming image datasets—especially High-Quality (HQ) and Low-Quality (LQ) pairs for super-resolution (SISR) and general computer vision tasks. It is designed for ML researchers and data scientists who need:

- Powerful dataset curation, validation, and cleaning tools
- Deep analysis and reporting for dataset quality
- Advanced image processing, augmentation, and transformation
- A beautiful, user-friendly CLI with progress tracking and memory management

**Key Use Cases:**

- Preparing HQ/LQ datasets for super-resolution training
- Validating, cleaning, and analyzing large image datasets
- Running advanced deduplication, tiling, and augmentation pipelines
- Generating rich reports and statistics for ML workflows

---

## 🏗️ Modular Architecture (Summary)

Dataset Forge is built with a modular, extensible architecture:

- **menus/**: UI layer (CLI menus, user interaction)
- **actions/**: Business logic (core dataset/image operations)
- **utils/**: Reusable utilities (file ops, memory, parallelism, color, monitoring, etc.)
- **dpid/**: Multiple DPID (degradation) implementations
- **configs/**: Example and user configuration files
- **reports/**: Report templates for HTML/Markdown output

See [Project Architecture](docs/architecture.md) for details.

---

## 🏎️ Fast CLI Menus with Lazy Imports

Dataset Forge now uses a lazy import pattern for all main menus and submenus. This means the CLI is extremely fast and responsive, even as the project grows. Heavy modules and actions are only imported when needed, keeping startup and navigation snappy.

- See [docs/advanced.md](docs/advanced.md) for details on the lazy import pattern.

---

## 🧭 Robust Menu Loop Pattern (July 2025)

Dataset Forge now uses a robust, standardized menu loop pattern for all menus and submenus:

- The user's choice (key) is obtained from `show_menu`.
- The action is looked up in the options dictionary.
- The action is called if it is callable.
- This pattern is now applied globally, ensuring reliable navigation and submenu invocation everywhere.
- No more redraw bugs or dead options—every menu and submenu works as intended.

For implementation details and code examples, see the documentation in `docs/features.md`, `docs/usage.md`, and `docs/advanced.md`.

---

## 🖥️ Supported Platforms & Requirements

- **Python**: 3.8+ (tested on 3.12)
- **OS**: Windows (primary), Linux (partial support)
- **CUDA**: 12.1+ (for GPU acceleration)
- **cuDNN**: 8.9+ (for GPU acceleration, required for PyTorch CUDA)
- **RAM**: 8GB+ (16GB+ recommended for large datasets)
- **Storage**: SSD recommended for faster I/O
- **VapourSynth**: Required for getnative functionality. **You must install VapourSynth before installing or using getnative.**
- See [Requirements](docs/advanced.md#requirements) for full details.

**Dependency Matrix:**

| Python | CUDA Toolkit | cuDNN | PyTorch | OS      |
| ------ | ------------ | ----- | ------- | ------- |
| 3.12   | 12.1         | 8.9+  | 2.2.0+  | Windows |
| 3.8+   | 11.8/12.1    | 8.6+  | 2.0.0+  | Linux   |

- For GPU acceleration, ensure your CUDA and cuDNN versions match your PyTorch install. See [PyTorch Get Started](https://pytorch.org/get-started/locally/) for details.
- If you use a different CUDA/cuDNN version, install the matching PyTorch build.

> **IMPORTANT:** You must install the correct version of torch/torchvision/torchaudio for your CUDA version **before** running `pip install .`. If you skip this, pip will install the CPU-only version of torch by default. See the Quick Start below for the recommended command.
> **IMPORTANT:** You must install VapourSynth before installing or using getnative. See the requirements.txt and docs for details.

---

## Menu Timing & Profiling (New in July 2025)

Dataset Forge now features a fast, responsive CLI menu system with built-in timing and profiling:

- Every time you load a menu or submenu, you will see a timing print (e.g., `⏱️ Loaded dataset_management_menu in 0.123 seconds.`) in the Catppuccin Mocha color scheme.
- All menu load times are recorded and can be viewed in the System Monitoring menu under "⏱️ View Menu Load Times".
- This helps you identify slow-loading menus and provides transparency for performance optimization.
- The timing system uses lazy imports to maximize CLI speed and minimize memory usage.

For more details, see the documentation in `docs/features.md`, `docs/usage.md`, and `docs/advanced.md`.

---

## 📖 Table of Contents

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

## ✨ Key Features

- Modular, extensible CLI for image dataset management
- HQ/LQ pair support for super-resolution and ML
- 40+ operations: validation, analysis, augmentation, deduplication, reporting
- Beautiful Catppuccin Mocha-themed interface
- Smart memory and parallel processing
- Deep validation and reporting tools
- **Advanced system monitoring & analytics**: Live resource usage (CPU, GPU, RAM, disk), performance analytics, error tracking, health checks, and background task management, all accessible from a dedicated CLI menu. Includes persistent logging, notifications, and memory/CUDA cleanup integration.
- **Audio error feedback**: Whenever an error is reported to the user, an error sound (error.mp3) is played for immediate feedback.
- **getnative integration**: For native resolution detection (requires VapourSynth, see requirements).
- **Content-Based Image Retrieval (CBIR) for Duplicates**: Find, remove, move, or copy semantically similar images using deep learning embeddings (CLIP, ResNet, VGG). Detects duplicates and near-duplicates based on semantic content, not just pixel similarity.

---

## About

Dataset Forge is a professional-grade tool for ML researchers and data scientists, designed for high-quality dataset curation, analysis, and transformation. For full documentation, see the [docs/](docs/) folder or the links above.

**CBIR for Duplicates:** Use deep learning models (CLIP, ResNet, VGG) to find, group, and manage semantically similar images. Supports fast similarity search, grouping, and batch actions (find, remove, move, copy) with GPU acceleration.

**Audio error feedback:** Whenever an error is reported to the user, an error sound (error.mp3) is played for immediate feedback, ensuring you never miss a critical issue.

**For coding standards and best practices, see the [Style Guide](docs/style_guide.md).**

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

## 🛠️ Documentation Maintenance

**Whenever you update any documentation in the docs/ folder or the main README.md, you MUST also update:**

- `docs/README_full.md` (comprehensive, merged documentation)
- `docs/toc.md` (Table of Contents for all documentation)

This ensures that all documentation is always up to date and easy to navigate for users and contributors.

**To update documentation:**

- Edit the relevant file in the [docs/](docs/) folder.
- Keep the main README.md concise and up-to-date with links to detailed docs.
- Add new sections to docs/ as the project grows.

- The requirements.txt is now grouped and commented for clarity (see file for details).
- The install.bat and run.bat scripts have been updated for best practices and CUDA/torch install warnings.

---

## 🧪 Testing

Dataset Forge now includes a comprehensive, automated test suite covering:

- CLI entry and menu navigation
- Menu timing/profiling
- Error feedback (including audio)
- Memory management and parallel processing
- File and image utilities
- Robust handling of Unicode, subprocess, and Windows-specific issues
- Manual/script-style tests for BHI filtering and pepeline (run directly, not via pytest)

**How to run all tests:**

1. Activate your virtual environment:
   ```sh
   venv312\Scripts\activate
   ```
2. Run all automated tests from the project root:
   ```sh
   pytest
   ```
3. To run manual/script tests:
   ```sh
   python tests/test_bhi_filtering.py
   python tests/test_pepeline.py
   ```

All tests pass as of this integration. See [docs/usage.md](docs/usage.md) and [docs/features.md](docs/features.md) for details.

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
3. **Run the application:**
   ```bash
   dataset-forge
   # or
   py main.py
   # or
   ./run.bat
   ```
4. **Run the test suite (optional, recommended):**
   ```bash
   pytest
   ```

---

<!-- Badges (add more as needed) -->
<p align="center">
  <a href="https://github.com/Courage-1984/Dataset-Forge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-CC--BY--SA--4.0-blue" alt="License"></a>
  <!-- Add CI/build/test badges here if available -->
</p>
