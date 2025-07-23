[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Usage Guide

This guide covers the main user workflows for Dataset Forge. For advanced configuration and developer patterns, see [advanced.md](advanced.md).

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

## 🔊 Project Sounds & Audio Feedback

Dataset Forge provides instant audio feedback for key events:

- **Startup (startup.mp3):** When the app starts (ready to use)
- **Success (done.wav):** After long or successful operations (operation completed)
- **Error (error.mp3):** On any user-facing error (attention required)
- **Shutdown (shutdown.mp3):** When the app exits (normal or Ctrl+C)

See [Features](features.md#🔊-project-sounds--audio-feedback) for a full table and more details.

## 👣 Main Workflows

### Dataset Management

- Create, combine, split, and shuffle datasets using the Dataset Management menu.
- Use Clean & Organize to deduplicate, batch rename, and filter images.

### Align Images (Batch Projective Alignment)

- Select '🧭 Align Images' from the Dataset Management menu.
- Choose two folders (source and reference). Images are matched by filename.
- Choose output folder. Optionally select flat or recursive (subfolder) processing.
- The workflow aligns each matching image pair using SIFT+FLANN projective transformation.
- Output images are saved in the specified output folder, preserving subfolder structure if recursive.
- **Note:** Images must have detectable features (edges, shapes, or text) for alignment to succeed. Solid color images will not align.

### Analysis & Validation

- Run validation and generate reports from the Analysis & Validation menu.
- Use quality scoring and outlier detection to assess dataset quality.

### Image Processing & Augmentation

- Apply augmentations, tiling, and batch processing from the Augmentation and Image Processing menus.

### Monitoring & Analytics

- Access live resource usage, error tracking, and analytics from the System Monitoring menu.
- View menu load times and health checks.

### Cache Management

- Access comprehensive cache management from System Settings → Cache Management.
- View cache statistics, clear caches, perform maintenance, and optimize performance.
- Monitor hit rates, memory usage, and disk space for all cache types.
- Export cache data and perform warmup operations for frequently used data.

---

## July 2025 Update

- Menus now use a robust loop pattern and provide clear error/debug feedback.
- All user-facing workflows end with a styled prompt to return to the menu.
- DPID workflows are modular and support four methods: BasicSR, OpenMMLab, Phhofm, and Umzi (pepedpid). You can select Umzi's DPID in all DPID menus for both single-folder and HQ/LQ paired workflows.
- CLI output and prompts are visually consistent and styled.

For troubleshooting and advanced usage, see [troubleshooting.md](troubleshooting.md) and [advanced.md](advanced.md).

## 🧪 Running the Test Suite

To run all tests, you can now use the flexible test runner script:

```sh
python tools/run_tests.py
```

This script provides a menu to select between different test run modes, or you can pass an option directly:

- **Option 1:** Basic: venv312\Scripts\activate + pytest
- **Option 2:** Recommended: venv312\Scripts\activate + venv312\Scripts\python -m pytest --maxfail=5 --disable-warnings -v tests/
- **Option 3:** Verbose: venv312\Scripts\activate + venv312\Scripts\python -m pytest -s --maxfail=5 --disable-warnings -v tests/ (no output capture)

Example:

```sh
python tools/run_tests.py 2  # Recommended
```

You can still run pytest directly if you prefer:

```sh
venv312\Scripts\activate
venv312\Scripts\python -m pytest --maxfail=5 --disable-warnings -v tests/
```

- All major features are covered by robust, non-interactive tests. This includes all DPID implementations (BasicSR, OpenMMLab, Phhofm, and Umzi), which are fully tested using public APIs and monkeypatching for reliability.
- Tests use monkeypatching and dummy objects for reliability.
- One test is marked XFAIL (ignore patterns in directory tree); this is expected and not a failure.

### Using Public APIs for Testing

All major features (enhanced metadata, quality scoring, sanitize images, visual deduplication, etc.) provide public, non-interactive API functions for programmatic use and testing. See the relevant modules in `dataset_forge/actions/` for details and usage examples.

---

## 🧑‍💻 Static Analysis & Code Quality

Dataset Forge includes a static analysis tool for maintainers and contributors:

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

Review the actionable report and detailed results before submitting code or documentation changes.

## Using Umzi's Dataset_Preprocessing

You can access Umzi's Dataset_Preprocessing from the main menu (option 9: 🧩 Umzi's Dataset_Preprocessing). This menu provides the following workflows:

- **Best Tile Extraction**: Extracts the most informative tile(s) from images in a folder. Prompts for input/output folders, tile size, complexity function, and other options.
- **Video Frame Extraction**: Extracts frames from a video based on embedding distance. Prompts for video path, output folder, model, and threshold.
- **Image Deduplication**: Create embeddings for all images in a folder, or find duplicate clusters from embeddings. Prompts for folders, model, and thresholds.
- **IQA Filtering**: Filter or sort images by IQA score using various algorithms. Prompts for input folder, algorithm, and thresholds.
- **Embedding Extraction**: Extract and print the embedding for a single image.

All options are fully interactive, use Dataset Forge's input and printing utilities, and are covered by robust unit and CLI tests. See the main menu for access.

### 🧹 Sanitize Images (NEW July 2025)

- The workflow now prompts you interactively for each major step (corruption fix, copy, batch rename, ICC to sRGB, PNG, remove alpha, metadata, steganography), with emoji and Mocha-styled prompts.
- Steganography checks prompt for steghide and zsteg individually, and only the selected tools are run.
- At the end, a visually distinct summary box shows all steps (run/skipped), both steganography sub-choices, and the zsteg results file path if produced.
- The menu header is reprinted after returning to the workflow menu.
- All output is Mocha-styled and visually consistent.

### 🗂️ Enhanced Metadata Management (NEW July 2025)

- **Batch Extract Metadata:**

  1. Open the Enhanced Metadata Management menu from the main menu.
  2. Select 'Batch Extract Metadata'.
  3. Choose a folder, output format (CSV/SQLite), and output path.
  4. Requires exiftool to be installed and in PATH.

- **View/Edit Metadata:**

  1. Select 'View/Edit Metadata' from the menu.
  2. Enter the image file path.
  3. View EXIF (Pillow) and full metadata (exiftool).
  4. Optionally set or remove fields using exiftool.

- **Filter by Metadata:**

  1. Select 'Filter by Metadata'.
  2. Choose metadata source (CSV/SQLite from batch extract).
  3. Enter a pandas query string (e.g., 'ISO > 800 and Model == "Canon"').
  4. View and/or export filtered results.

- **Batch Anonymize Metadata:**
  1. Select 'Batch Anonymize Metadata'.
  2. Choose a folder and confirm operation.
  3. All metadata will be stripped using exiftool.

> **Note:** If exiftool is not found, you will be prompted to install it. See [Troubleshooting](troubleshooting.md) for help.

> **Note:** Architecture diagrams in this documentation use Mermaid code blocks. No Python package is required; diagrams are rendered by supported Markdown viewers (e.g., GitHub, VSCode with Mermaid extension).
>
> **Badges:** Standard badges (build, license, Python version, etc.) are included in the README. See the README for their meaning.

# 🛠️ Utility Scripts (tools/)

This section documents the user-facing utility scripts in the `tools/` directory. These scripts assist with code quality, documentation, environment setup, and troubleshooting.

## run_tests.py: Flexible Test Runner (NEW July 2025)

A flexible script for running the test suite with multiple options and interactive menu.

- **Location:** `tools/run_tests.py`
- **Purpose:** Lets you run the test suite in different modes (basic, recommended, verbose) with or without output capture.
- **How to run:**
  ```sh
  python tools/run_tests.py
  # or, to skip the menu:
  python tools/run_tests.py 2  # Recommended
  python tools/run_tests.py 3  # Verbose (no output capture)
  ```
- **Options:**
  - `1` Basic: venv312\Scripts\activate + pytest
  - `2` Recommended: venv312\Scripts\activate + venv312\Scripts\python -m pytest --maxfail=5 --disable-warnings -v tests/
  - `3` Verbose: venv312\Scripts\activate + venv312\Scripts\python -m pytest -s --maxfail=5 --disable-warnings -v tests/ (no output capture)
- **Menu:** If no option is given, a menu will be shown to select the mode interactively.
- **Troubleshooting:**
  - If you get import errors, check your virtual environment and Python version.
  - If the script reports no files found, check your directory structure.
  - Review the console output for error messages.

## find_code_issues.py: Static Analysis Tool

A comprehensive static analysis tool for maintainers and contributors.

- **Location:** `tools/find_code_issues/find_code_issues.py`
- **Purpose:** Checks for dead code, untested code, missing docstrings, test/code mapping, and more.
- **How to run:**
  ```sh
  python tools/find_code_issues/find_code_issues.py [options]
  # Run with no options to perform all checks
  ```
- **Options:**
  - `--vulture` Run vulture for dead code
  - `--coverage` Run pytest-cov for coverage
  - `--callgraph` Run pyan3 for call graph analysis
  - `--pyflakes` Run pyflakes for unused imports/variables
  - `--test-mapping` Check test/code correspondence
  - `--ast` AST: Find defined but never called functions/classes
  - `--all` Run all analyses (default)
  - `--view` View detailed results for each analysis after run
  - `-h, --help` Show help
- **Output:**
  - Overwrites files in `tools/find_code_issues/` on each run:
    - `find_code_issues.log` (raw output)
    - `find_code_issues_report.txt` (actionable summary)
    - `find_code_issues_view.txt` (detailed results)
- **Requirements:**
  - `pip install vulture pytest pytest-cov coverage pyan3 pyflakes`
- **Troubleshooting:**
  - Ensure all dependencies are installed.
  - If you get import errors, check your virtual environment and Python version.
  - If the script reports no files found, check your directory structure.
  - Review the log file for detailed error messages.

## merge_docs.py: Documentation Merging Tool

- **Location:** `tools/merge_docs.py`
- **Purpose:** Merges all documentation files in `docs/` into a single `README_full.md` and generates a hierarchical Table of Contents (`toc.md`).
- **How to run:**
  ```sh
  python tools/merge_docs.py
  ```
- **Output:**
  - `docs/README_full.md` (merged documentation)
  - `docs/toc.md` (hierarchical Table of Contents)
- **Troubleshooting:**
  - Ensure all documentation files exist and are readable.
  - If you see missing file warnings, check the `DOC_ORDER` list in the script.

## install.py: Environment Setup Tool

- **Location:** `tools/install.py`
- **Purpose:** Automated environment setup. Creates a virtual environment, installs CUDA-enabled torch, and all project requirements.
- **How to run:**
  ```sh
  python tools/install.py
  ```
- **What it does:**
  - Checks Python version (requires 3.12+)
  - Creates `venv312` if not present
  - Installs torch/torchvision/torchaudio with CUDA 12.1 support
  - Installs all project requirements
- **Troubleshooting:**
  - If Python version is too low, upgrade Python.
  - If CUDA-enabled torch fails, check your CUDA version and use the correct index URL.
  - If pip install fails, check your internet connection and permissions.

## print_zsteg_env.py: zsteg Environment Check

- **Location:** `tools/print_zsteg_env.py`
- **Purpose:** Prints the current PATH and the location of the `zsteg` binary for troubleshooting steganography tool integration.
- **How to run:**
  ```sh
  python tools/print_zsteg_env.py
  ```
- **Output:**
  - Prints the current PATH and the path to `zsteg` (if found) to the console.
- **Troubleshooting:**
  - If `zsteg` is not found, ensure it is installed and in your PATH.
  - On Windows, you may need to restart your terminal after adding to PATH.

## 🩺 Using Dataset Health Scoring

1. From the main menu, select 'Dataset Management'.
2. Choose '🩺 Dataset Health Scoring'.
3. Select whether to score a single folder or an HQ/LQ parent folder (for paired datasets).
   - If HQ/LQ, the tool will auto-detect or prompt for HQ and LQ subfolders.
4. The workflow will run a series of checks (validation, quality, consistency, compliance, etc.).
5. At the end, you'll see:
   - A step-by-step breakdown (pass/fail, points per step)
   - The overall health score (0–100)
   - Status (✅ Production Ready, ⚠️ Needs Improvement, ❌ Unusable)
   - Actionable suggestions for improvement if needed

**Tips:**

- Use the suggestions to address any issues before using the dataset for ML training.
- The workflow is fully automated and robust to input errors.
- All steps are covered by automated tests for reliability.

[Back to Table of Contents](#table-of-contents)
