[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Usage Guide

This guide covers the main user workflows for Dataset Forge. For advanced configuration and developer patterns, see [advanced.md](advanced.md).

---

## Quick Start

1. Clone the repository and set up your environment (see [README.md](../README.md)).
2. Activate your virtual environment and install requirements.
3. Run the application using `dataset-forge`, `py main.py`, or `./run.bat`.

## Main Workflows

### Dataset Management

- Create, combine, split, and shuffle datasets using the Dataset Management menu.
- Use Clean & Organize to deduplicate, batch rename, and filter images.

### Analysis & Validation

- Run validation and generate reports from the Analysis & Validation menu.
- Use quality scoring and outlier detection to assess dataset quality.

### Image Processing & Augmentation

- Apply augmentations, tiling, and batch processing from the Augmentation and Image Processing menus.

### CBIR (Semantic Duplicate Detection)

1. Go to Dataset Management > Clean & Organize > CBIR.
2. Select your workflow: single-folder or HQ/LQ pair.
3. Choose the embedding model (CLIP recommended).
4. Set the similarity threshold (default: 0.92 for cosine similarity).
5. Choose an action: Find, Remove, Move, or Copy duplicates.
6. Review the summary of affected files after each operation.

### Monitoring & Analytics

- Access live resource usage, error tracking, and analytics from the System Monitoring menu.
- View menu load times and health checks.

---

For troubleshooting and advanced usage, see [troubleshooting.md](troubleshooting.md) and [advanced.md](advanced.md).

## Native Resolution Detection (getnative & resdet)

The 'Find Native Resolution' feature allows you to estimate the original resolution of an image using two methods:

- **getnative** (Python, VapourSynth): Works natively on Windows and Linux. Requires VapourSynth and Python dependencies.
- **resdet** (C binary): Fast, supports PNG/JPEG. On Windows, the CLI will use WSL to run resdet if available. On Linux, resdet is run natively.

### How to Use
1. From the main menu, navigate to:
   - `Analysis & Validation` → `Analyze Properties` → `Find Native Resolution`
2. Choose whether to analyze a folder (HQ/LQ) or a single image.
3. Select your preferred method:
   - **getnative**: Requires VapourSynth and Python dependencies.
   - **resdet**: Requires resdet to be installed and available in your PATH (or in WSL PATH on Windows).

### Windows Users
- If you select resdet, the CLI will automatically use WSL if available.
- You must install resdet in your WSL environment and ensure it is in the WSL PATH.
- See [special_installation.md](special_installation.md) for detailed instructions.

### Linux Users
- Install resdet natively and ensure it is in your PATH.

### Troubleshooting
- If resdet is not found, you will receive a clear error message with installation instructions.
