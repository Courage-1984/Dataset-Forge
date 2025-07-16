[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Features (tl;dr)

# Features (main menus)

## ⚙️ Core & Configuration

- **🔧 External tool integration**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer), [traiNNer-redux](https://github.com/the-database/traiNNer-redux), [getnative](https://github.com/Infiziert90/getnative), [resdet](https://github.com/0x09/resdet), [Oxipng](https://github.com/oxipng/oxipng), [Steghide](https://steghide.sourceforge.net/), [zsteg](https://github.com/zed-0xff/zsteg), [umzi's Dataset_Preprocessing](https://github.com/umzi2/Dataset_Preprocessing), []()
- **📦 Model management**: List, select, download and run upscaling with trained models (also [OpenModelDB](https://openmodeldb.info/) integration)
- **✅ Validation tools**: Validate HQ/LQ pairs and validation datasets from config
- **👤 User profiles**: Save favorites, presets, links and quick access paths
- **⚙️ Multi-format config support**: JSON, YAML, HCL

## 📂 Dataset Management

- **🎯 Dataset Creation**: Multiscale dataset generation (DPID), video frame extraction, image tiling (using IC9600)
- **🔗 Dataset Operations**: Combine, split, extract random pairs, shuffle datasets, remove/move
- **🔍 HQ/LQ Pair Management**: Create/Correct Manual Pairings, fuzzy matching, scale correction, shuffle, extract random pairs
- **🧹 Clean & Organize**: De-dupe (Visual deduplication, hash-based deduplication, ImageDedup advanced duplicate detection, CBIR (Semantic Duplicate Detection)), batch renaming
- **🔄 Orientation Organization**: Sort by landscape/portrait/square
- **📏 Size Filtering**: Remove small/invalid image pairs
- **🧭 Align Images (Batch Projective Alignment)**: Aligns images from two folders (flat or recursive, matching by filename) using SIFT+FLANN projective transformation. Supports batch processing, robust error handling, and both flat and subfolder workflows. See Usage Guide for details.

## 🔍 Analysis & Validation

- **🔍 Comprehensive Validation**: Progressive dataset validation suite
- **📊 Rich Reporting**: HTML/Markdown reports with plots and sample images
- **⭐ Quality Scoring**: Automated dataset quality assessment (NIQE, etc.)
- **🔧 Issue Detection**: Corruption detection, misalignment detection, outlier detection. alpha channel detection
- **🧪 Property Analysis**: Consistency checks, aspect ratio testing, dimension reporting
- **⭐ BHI Filtering**: Blockiness, HyperIQA, IC9600 quality assessment
- **🔍 Scale Detection**: Find and test HQ/LQ scale relationships
- **🎯 Find Native Resolution**: Find image native resolution using [getnative](https://github.com/Infiziert90/getnative) or [resdet](https://github.com/0x09/resdet)

## ✨ Image Processing & Augmentation

- **🔄 Basic Transformations**: Downsample Images, crop, flip, rotate, shuffle, remove alpha channel
- **🎨 Colour, Tone & Levels Adjustments**: Brightness, contrast, hue, saturation, HDR>SDR, grayscale
- **🧪 Degradations**: Blur, noise, pixelate, dithering, sharpen, banding & many more
- **🚀 Augmentation**: List, create, edit or delete _recipes_ or run advanced augmentation pipelines (using recipes)
- **📋 Metadata**: Scrub EXIF Metadata, Convert ICC Profile to sRGB
- **✏️ Find & extract sketches/drawings/line art**: Find & extract sketches/drawings/line art using pre-trained model
- **🗳️ Batch Processing**: Efficient batch operations for large datasets

## 🚀 Training & Inference

- **🛠️ Run wtp_dataset_destroyer**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer) integration, create HQ/LQ pairs with custom degradations
- **🚀 Run traiNNer-redux**: [traiNNer-redux](https://github.com/the-database/traiNNer-redux) integration, train your own SISR models
- **🧠 OpenModelDB Model Browser**: Robust integration with [OpenModelDB](https://openmodeldb.info/)
- **⚙️ Config files**: Add, load, view & edit configs

## 🛠️ Utilities

- **🖼️ Create Comparisons**: Create striking image / gif comparisons
- **📦 Compression**: Compress images or directories
- **🧹 Sanitize Images**: Comprehensive, interactive image file sanitization. Each major step (corruption fix, copy, batch rename, ICC to sRGB, PNG conversion, remove alpha, metadata removal, steganography) is prompted interactively with emoji and Mocha color. Steganography checks prompt for steghide and zsteg individually, and the summary reports both. A visually distinct summary box is always shown at the end, including zsteg results file path if produced. All output uses the Catppuccin Mocha color scheme and emoji-rich prompts. Menu header is reprinted after returning to the workflow menu.
- **🌳 Enhanced Directory Tree**: Directory tree visualization using emojis
- **🧹 Filter non-Images**: Filter all non image type files
- **🗂️ Enhanced Metadata Management**: Batch Extract Metadata: Extract EXIF/IPTC/XMP from all images in a folder to CSV or SQLite using exiftool and pandas/SQLite. View/Edit Metadata: View and edit metadata for a single image (EXIF, IPTC, XMP) using Pillow and exiftool. Filter by Metadata: Query and filter images by metadata fields (e.g., ISO, camera, date) using pandas/SQLite. Batch Anonymize Metadata: Strip all identifying metadata from images using exiftool, with robust error handling and progress.

> **Dependencies:** Requires [exiftool](https://exiftool.org/) (external), pandas, and SQLite (Python stdlib).

## ⚙️ System & Settings

- **📁 Set HQ/LQ Folder**: set HQ/LQ image pair folders to use throughout Dataset Forge
- **👤 User Profile Management**: Create and manage custom profiles for Dataset Forge
- **🧠 Memory Management**: View, clear & optimize memory management
- **⚙️ Settings**: View & configure project settings

## 🔗 Links

- **🌐 Community Links**: Browse/List important and usefull links curated by me and the community
- **🔗 Personal Links**: Browse/List & add your own links

## 🩺 System Monitoring & Health

- **📊 View Live Resource Usage**: Real-time CPU, GPU (NVIDIA), RAM, and disk usage for all processes/threads
- **📈 View Performance Analytics**: Decorator-based analytics for all major operations, with live and persistent session summaries
- **🛑 View Error Summary**: Logs errors to file and CLI, with summary granularity and critical error notifications (sound/visual)
- **🩺 Run Health Checks**: Automated checks for RAM, disk, CUDA, Python version, and permissions, with CLI output and recommendations
- **🧵 Manage Background Tasks**: Registry of all subprocesses/threads, with CLI controls for pause/resume/kill and session-only persistence
- **⏱️ View Menu Load Times**: View the menu load times

## ⚡ Caching System (NEW July 2025)

Dataset Forge now features a robust caching system to accelerate repeated operations:

- **In-Memory Caching:** Frequently-used, lightweight results (e.g., image property analysis, directory scans) are cached in RAM for the current session.
- **Disk Caching:** Expensive, large results (e.g., deep feature embeddings for CBIR) are cached persistently in `store/cache/` for reuse across sessions.
- **Automatic Integration:** Caching is transparently applied to key functions:
  - CBIR feature extraction (CLIP, ResNet, VGG embeddings)
  - Directory image scans
  - Image property analysis
- **Cache Management:**
  - A new menu option in System Monitoring allows you to clear all caches (disk and in-memory) with one click.
  - Disk cache is stored in `store/cache/` (auto-ignored by git).

**Benefits:**

- Dramatically faster repeated analysis, deduplication, and reporting on large datasets.
- Reduces redundant computation and I/O.

See `docs/advanced.md` for technical details and customization.

# Features (expanded/misc)

- **Audio error feedback**: All user-facing errors trigger an error sound (error.mp3) for immediate notification.
- **Persistent Logging**: All analytics and errors are logged to ./logs/ for later review
- **Memory & CUDA Cleanup**: Automatic cleanup on exit/errors for all tracked processes/threads

## 🧪 Comprehensive Test Suite (Updated July 2025)

Dataset Forge now includes a robust, cross-platform test suite covering all major features:

- Enhanced Metadata Management (extract, edit, filter, anonymize)
- Quality Scoring (single and batch, via public API)
- Sanitize Images (remove metadata, convert, remove alpha, steganography checks)
- Visual Deduplication (find, move, copy, remove duplicate groups)
- DPID implementations (BasicSR, OpenMMLab, Phhofm)
- CBIR and deduplication workflows
- Report generation
- Audio feedback, memory, parallel, and progress utilities
- Session state, config, and error handling

**Run all tests:**

You can now use the flexible test runner script for convenience:

```sh
python tools/run_tests.py
```

This script provides a menu to select the test mode, or you can pass an option (see below). See [usage.md](usage.md#🦾-running-the-test-suite) for details.

**Test suite highlights:**

- All features have public, non-interactive APIs for programmatic access and testing.
- Tests use monkeypatching and dummy objects to avoid reliance on external binaries or real files.
- Multiprocessing tests use module-level worker functions for compatibility.
- Only one test is marked XFAIL (ignore patterns in directory tree), which is expected and documented.

See [Usage Guide](usage.md#testing) and [Style Guide](style_guide.md#testing-patterns) for details.

## Testing & Validation

- Dataset Forge includes a comprehensive, cross-platform test suite using pytest.
- All core business logic, utilities, and integration flows are covered by unit and integration tests.
- Tests cover DPID, CBIR, deduplication, reporting, audio, memory, parallel, and session state features.
- Tests are robust on Windows and Linux, and use fixtures and monkeypatching for reliability.
- All new features and bugfixes must include appropriate tests.

---

## 🧑‍💻 Developer Tools: Static Analysis & Code Quality

> **Documentation Convention:** When adding new features or modules, update the architecture diagrams (Mermaid) in README.md and docs/architecture.md as needed. Use standard badges in the README and document their meaning in the docs.

- **Static Analysis Tool:** Located at `tools/find_code_issues/find_code_issues.py`.
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
  - `

## 🛠️ Utility Scripts (tools/)

Dataset Forge includes several utility scripts in the `tools/` directory to assist with development, documentation, and environment setup. These scripts are user-facing and documented in detail in [usage.md](usage.md#utility-scripts-tools).

- **run_tests.py**: Flexible test runner for the test suite. Lets you choose between basic, recommended, and verbose pytest runs via menu or CLI argument. See [usage.md](usage.md#run_testspy-flexible-test-runner-new-july-2025) for usage and options.
- **find_code_issues.py**: Comprehensive static analysis tool for code quality and maintainability. Checks for dead code, untested code, missing docstrings, test/code mapping, and more. See [usage.md](usage.md#find_code_issuespy-static-analysis-tool) for full usage and options.
- **merge_docs.py**: Merges all documentation files in `docs/` into a single `README_full.md` and generates a hierarchical Table of Contents (`toc.md`). Keeps documentation in sync. See [usage.md](usage.md#merge_docspy-documentation-merging-tool).
- **install.py**: Automated environment setup script. Creates a virtual environment, installs CUDA-enabled torch, and installs all project requirements. See [usage.md](usage.md#installpy-environment-setup-tool).
- **print_zsteg_env.py**: Prints the current PATH and the location of the `zsteg` binary for troubleshooting steganography tool integration. See [usage.md](usage.md#print_zsteg_envpy-zsteg-environment-check).

For detailed usage, CLI options, and troubleshooting, see [usage.md](usage.md#utility-scripts-tools).

# 🩺 Dataset Health Scoring (NEW July 2025)

**Location:** Dataset Management menu → 🩺 Dataset Health Scoring

**Purpose:**

- Assess the overall health and readiness of an image dataset for ML workflows.
- Supports both single-folder datasets and HQ/LQ parent folder structures (for super-resolution and paired tasks).

**Workflow:**

- User selects either a single folder or an HQ/LQ parent folder (auto-detects or prompts for HQ/LQ subfolders).
- Runs a series of modular checks:
  - Basic validation (file existence, supported formats, min count)
  - Unreadable/corrupt files
  - Image format consistency
  - Quality metrics (resolution, blur, etc.)
  - Aspect ratio consistency
  - File size outliers
  - Consistency checks (duplicates, naming, alignment)
  - Compliance scan (metadata, forbidden content)
- Each check is weighted; partial credit is possible.
- Shows a detailed breakdown of results, a final health score (0–100), and a status (✅ Production Ready, ⚠️ Needs Improvement, ❌ Unusable).
- Provides actionable suggestions for improvement if any step fails.

**Extensibility:**

- Checks are modular; new steps can be added easily.
- Scoring weights and logic are configurable in the business logic module.

**Testing:**

- Fully covered by unit and integration tests (see `tests/test_utils/test_dataset_health_scoring.py` and `tests/test_cli/test_dataset_health_scoring_menu.py`).
- Tests simulate both single-folder and HQ/LQ menu flows, including edge cases and input handling.

**Robustness:**

- Uses centralized input, printing, memory, and error handling utilities.
- Follows the robust menu loop and lazy import patterns.
- CLI integration is non-blocking and fully automated for testing.

[Back to Table of Contents](#table-of-contents)
