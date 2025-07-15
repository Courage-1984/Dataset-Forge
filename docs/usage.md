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
