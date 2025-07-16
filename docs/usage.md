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

## 👣 Main Workflows

### Dataset Management

- Create, combine, split, and shuffle datasets using the Dataset Management menu.
- Use Clean & Organize to deduplicate, batch rename, and filter images.

### Analysis & Validation

- Run validation and generate reports from the Analysis & Validation menu.
- Use quality scoring and outlier detection to assess dataset quality.

### Image Processing & Augmentation

- Apply augmentations, tiling, and batch processing from the Augmentation and Image Processing menus.

### Monitoring & Analytics

- Access live resource usage, error tracking, and analytics from the System Monitoring menu.
- View menu load times and health checks.

---

## July 2025 Update

- Menus now use a robust loop pattern and provide clear error/debug feedback.
- All user-facing workflows end with a styled prompt to return to the menu.
- DPID workflows are modular and use the new import structure.
- CLI output and prompts are visually consistent and styled.

For troubleshooting and advanced usage, see [troubleshooting.md](troubleshooting.md) and [advanced.md](advanced.md).

## Running the Test Suite

To run all tests (recommended after any major change):

```
venv312\Scripts\activate
venv312\Scripts\python -m pytest --maxfail=5 --disable-warnings -v tests/
```

The test suite covers all major features and runs quickly. Tests use fixtures and monkeypatching for reliability.

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

> **Note:** Architecture diagrams in this documentation use Mermaid code blocks. No Python package is required; diagrams are rendered by supported Markdown viewers (e.g., GitHub, VSCode with Mermaid extension).
>
> **Badges:** Standard badges (build, license, Python version, etc.) are included in the README. See the README for their meaning.
