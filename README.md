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
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   py main.py
   # or
   ./run.bat
   ```

---

## 🖥️ Supported Platforms & Requirements

- **Python**: 3.8+ (tested on 3.12)
- **OS**: Windows (primary), Linux (partial support)
- **CUDA**: 12.1+ (for GPU acceleration)
- **RAM**: 8GB+ (16GB+ recommended for large datasets)
- **Storage**: SSD recommended for faster I/O
- See [Requirements](docs/advanced.md#requirements) for full details.

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

---

## About

Dataset Forge is a professional-grade tool for ML researchers and data scientists, designed for high-quality dataset curation, analysis, and transformation. For full documentation, see the [docs/](docs/) folder or the links above.

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

**To update documentation:**

- Edit the relevant file in the [docs/](docs/) folder.
- Keep the main README.md concise and up-to-date with links to detailed docs.
- Add new sections to docs/ as the project grows.

---

<!-- Badges (add more as needed) -->
<p align="center">
  <a href="https://github.com/Courage-1984/Dataset-Forge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-CC--BY--SA--4.0-blue" alt="License"></a>
  <!-- Add CI/build/test badges here if available -->
</p>
