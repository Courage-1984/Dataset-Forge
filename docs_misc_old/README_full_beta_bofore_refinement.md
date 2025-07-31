[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)


# Dataset Forge Full Documentation

---

# Table of Contents

- [Features](features.md)
- [Usage Guide](usage.md)
- [Advanced Features & Configuration](advanced.md)
- [Project Architecture](architecture.md)
- [Troubleshooting](troubleshooting.md)
- [Style Guide](style_guide.md)
- [Changelog](changelog.md)
- [Contributing](contributing.md)
- [FAQ](faq.md)
- [License](license.md)


---


# Features


# Features

## Core & Configuration

- **Multi-format config support**: JSON, YAML, HCL
- **External tool integration**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer), [traiNNer-redux](https://github.com/the-database/traiNNer-redux)
- **Model management**: List, select, and run upscaling with trained models
- **Validation tools**: Validate HQ/LQ and validation datasets from config
- **Built-in config editors** for .hcl and .yml files
- **User profiles**: Save favorites, presets, and quick access paths

## Dataset Management

- **Dataset Creation**: Multiscale dataset generation (DPID), video frame extraction, image tiling
- **Dataset Operations**: Combine, split, extract random pairs, shuffle datasets
- **HQ/LQ Pair Management**: Manual pairing, fuzzy matching, scale correction
- **Clean & Organize**: Visual deduplication, hash-based deduplication, ImageDedup advanced duplicate detection, batch renaming
- **Orientation Organization**: Sort by landscape/portrait/square
- **Size Filtering**: Remove small/invalid image pairs

## Analysis & Validation

- **Comprehensive Validation**: Progressive dataset validation suite
- **Rich Reporting**: HTML/Markdown reports with plots and sample images
- **Quality Scoring**: Automated dataset quality assessment (NIQE, etc.)
- **Issue Detection**: Corruption detection, misalignment detection, outlier detection
- **Property Analysis**: Consistency checks, aspect ratio testing, dimension reporting
- **BHI Filtering**: Blockiness, HyperIQA, IC9600 quality assessment
- **Scale Detection**: Find and test HQ/LQ scale relationships

## Image Processing & Augmentation

- **Augmentation**: Flip, rotate, crop, color jitter, random erasing, and more
- **Tiling**: IC9600 and custom tiling for large images
- **Alpha Channel Handling**: Remove, preserve, or process alpha channels
- **Batch Processing**: Efficient batch operations for large datasets

## CBIR (Content-Based Image Retrieval) for Duplicates

- **Semantic Duplicate Detection**: Uses deep learning embeddings (CLIP, ResNet, VGG) to find images that are conceptually similar, even if visually transformed.
- **Feature Extraction**: Extracts high-dimensional feature vectors for each image using a pre-trained CNN (CLIP preferred, fallback to ResNet/VGG).
- **Similarity Search**: Computes cosine similarity or Euclidean distance between embeddings to identify near-duplicates.
- **ANN Indexing**: Uses approximate nearest neighbor (ANN) indexing for efficient search in large datasets.
- **Grouping & Actions**: Clusters images by semantic similarity and provides user options to find, remove, move, or copy duplicate groups.
- **GPU Acceleration**: Leverages GPU for fast embedding extraction and search.
- **Menu Integration**: Accessible from the Clean & Organize submenu under Dataset Management.

## Monitoring, Analytics & Error Tracking

- **Live Resource Monitoring**: Real-time CPU, GPU (NVIDIA), RAM, and disk usage for all processes/threads
- **Performance Analytics**: Decorator-based analytics for all major operations, with live and persistent session summaries
- **Error Tracking**: Logs errors to file and CLI, with summary granularity and critical error notifications (sound/visual)
- **Audio error feedback**: All user-facing errors trigger an error sound (error.mp3) for immediate notification.
- **Health Checks**: Automated checks for RAM, disk, CUDA, Python version, and permissions, with CLI output and recommendations
- **Background Task Management**: Registry of all subprocesses/threads, with CLI controls for pause/resume/kill and session-only persistence
- **Persistent Logging**: All analytics and errors are logged to ./logs/ for later review
- **Memory & CUDA Cleanup**: Automatic cleanup on exit/errors for all tracked processes/threads
- **Dedicated CLI Menu**: Access all monitoring, analytics, and management features from the System Monitoring menu

## Automated Test Suite

- Covers CLI entry, menu navigation, timing/profiling, error feedback (audio), memory management, parallel processing, and file/image utilities.
- Handles Unicode, subprocess, and Windows-specific edge cases.
- Includes manual/script-style tests for BHI filtering and pepeline (run directly).
- All tests pass as of this integration.

See [usage.md](usage.md#running-tests) for instructions on running tests.

---

For advanced implementation details, code patterns, and developer best practices, see [advanced.md](advanced.md) and [style_guide.md](style_guide.md).

- Dual native resolution detection: Choose between getnative (Python/VapourSynth) and resdet (C binary, fast, WSL integration on Windows). See [special_installation.md](special_installation.md) for install details.

---


# Usage


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

---


# Advanced


# Advanced Features & Configuration

This document covers advanced usage, configuration, and developer patterns for Dataset Forge. For user-facing features, see [features.md](features.md).

---

## Advanced Configuration

- **Custom config files**: Use JSON, YAML, or HCL for advanced workflows.
- **Integration with external tools**: See [features.md](features.md#core--configuration).
- **Batch processing and memory optimization**: Tune batch sizes and memory settings in the config files for large datasets.
- **OpenModelDB integration**: Advanced model management and upscaling workflows.

## Extending Dataset Forge

- **Add new menu actions**: Use the lazy import pattern (see [style_guide.md](style_guide.md)).
- **Add new analytics or monitoring hooks**: Decorate long-running or user-facing functions with the provided decorators.
- **Add new CBIR models**: Extend the CBIR system by adding new embedding models in the actions layer.

## Implementation Patterns (for Developers)

- **Robust Menu Loop**: All menus and submenus must use the robust menu loop pattern. See [style_guide.md](style_guide.md) for the required code snippet and rationale.
- **Timing & Profiling**: Use the centralized timing utility (`time_and_record_menu_load` in `utils/monitoring.py`) to wrap menu and submenu loads. Timing prints are shown to the user and aggregated for analytics. See [style_guide.md](style_guide.md) for best practices.
- **Lazy Imports**: Use `lazy_action()` and `lazy_menu()` helpers to defer heavy imports until needed. This keeps the CLI fast and memory-efficient.

## Advanced CBIR (Content-Based Image Retrieval)

- **Add new embedding models**: Extend `cbir_actions.py` with new model support.
- **Optimize similarity search**: Use ANN indexing for large datasets.
- **Batch actions**: Implement new batch actions (remove, move, copy) in the CBIR workflow.

## Advanced Monitoring & Analytics

- **Add new analytics hooks**: Decorate new actions with `@monitor_performance` and `@track_errors`.
- **Background task management**: Register new subprocesses/threads for monitoring.
- **Persistent logging**: Ensure all analytics and errors are logged to ./logs/.

---

For user workflows and feature summaries, see [features.md](features.md). For code style and requirements, see [style_guide.md](style_guide.md).

---


# Architecture


# Project Architecture

Dataset Forge is built with a modular, extensible architecture for maintainability and performance.

## Directory Structure

- **menus/**: UI layer (CLI menus, user interaction)
- **actions/**: Business logic (core dataset/image operations)
- **utils/**: Reusable utilities (file ops, memory, parallelism, color, monitoring, etc.)
- **dpid/**: Multiple DPID (degradation) implementations
- **configs/**: Example and user configuration files
- **reports/**: Report templates for HTML/Markdown output

## Monitoring & Analytics

- Centralized resource monitoring, analytics, error tracking, health checks, and background task registry (see utils/monitoring.py).
- CLI menu for live resource usage, analytics, error summaries, health checks, and background task management (see menus/system_monitoring_menu.py).
- Persistent logging and notifications for all major operations.

## Test Suite Integration

- Comprehensive automated test suite using pytest.
- Covers CLI, menu timing, error feedback, memory, parallelism, and file/image utilities.

---

For coding standards and best practices, see [style_guide.md](style_guide.md).

---


# Troubleshooting


# Troubleshooting

This guide provides solutions to common issues in Dataset Forge. For advanced usage and developer troubleshooting, see [advanced.md](advanced.md).

---

## Menu Timing & Profiling Issues

**Problem:** Timing prints do not appear after loading a menu or submenu.

- Ensure you are running the latest version of Dataset Forge.
- Check that the menu or submenu uses the `time_and_record_menu_load` utility.
- "Back" and "Exit" options do not trigger timing prints.

## Menu Loop Issues

**Problem:** Errors occur when navigating menus (e.g., `TypeError: 'str' object is not callable`).

- All menu loops should check if the action is callable before calling it.
- Update your menu code to follow the robust menu loop pattern (see [style_guide.md](style_guide.md)).

**Problem:** Menu redraws repeatedly or submenus do not appear.

- Ensure the menu loop uses the robust pattern:
  - Get the user's choice (key) from `show_menu`.
  - Look up the action in the options dictionary.
  - Call the action if callable.

## CBIR Troubleshooting

- **Model loading errors**: Ensure torch, torchvision, and timm are installed and match your CUDA version.
- **GPU out of memory**: Lower the batch size or use CPU fallback. Close other GPU-intensive applications.
- **Slow performance**: Use GPU if available. For very large datasets, increase system RAM or process in smaller batches.

## Other Issues

- For monitoring/analytics issues, check the logs in the ./logs/ directory.
- If tests fail, ensure your environment matches the requirements and all dependencies are installed.

---

For further help, see [usage.md](usage.md) or contact the project maintainer.

---


# Style Guide


# Dataset Forge Style Guide

This guide defines the coding standards, architecture, and best practices for Dataset Forge contributors. For user-facing features and workflows, see [features.md](features.md) and [usage.md](usage.md).

---

## General Principles

- **Python 3.8+**. Use modern Python features.
- **PEP 8** style, 4-space indentation, 88-char line length (Black standard).
- **Google-style docstrings** for all public functions/classes.
- **Type hints** for all function parameters and return values.
- **Absolute imports** for all `dataset_forge` modules.
- **Modular design**: UI (menus/), business logic (actions/), utilities (utils/), DPID (dpid/).

## Project Architecture

- Keep UI, logic, and utilities separate.
- Use thin UI layers (menus), business logic in actions, helpers in utils.

## Coding Standards

- Use type hints everywhere.
- Google-style docstrings for all public functions/classes.
- Example:

```python
def process_images(image_paths: List[str], output_dir: str) -> List[str]:
    """
    Process a list of images and save results to output directory.
    Args:
        image_paths: List of input image file paths
        output_dir: Directory to save processed images
    Returns:
        List of output image file paths
    Raises:
        FileNotFoundError: If input files don't exist
        PermissionError: If output directory is not writable
    Example:
        >>> paths = process_images(['img1.jpg', 'img2.png'], 'output/')
        >>> print(f"Processed {len(paths)} images")
    """
```

## Import Organization

1. Standard library
2. Third-party
3. Local imports (`dataset_forge.*`)
4. Relative imports (only within same module)

- Always use absolute imports for `dataset_forge` modules.

## Memory Management

- Use centralized memory management: `from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache`
- Use context managers: `with memory_context("Operation Name"):`
- Use decorators: `@auto_cleanup`, `@monitor_memory_usage`
- Clear memory after large operations.

## Parallel Processing

- Use centralized parallel system: `from dataset_forge.utils.parallel_utils import parallel_map, ProcessingType`
- Use `smart_map`, `image_map`, `batch_map` for optimized processing.

## Progress Tracking & User Feedback

- Use `from dataset_forge.utils.progress_utils import tqdm`
- Use AudioTqdm for audio notifications.
- Always show progress for long operations.

## Color Scheme & UI

- Use Catppuccin Mocha color scheme: `from dataset_forge.utils.color import Mocha`
- Use centralized printing: `print_info`, `print_success`, `print_warning`, `print_error`
- Use `print_header()` and `print_section()` for menu organization.

## Menu System

- Use hierarchical menu structure (7 main categories).
- Use `show_menu()` from `dataset_forge.utils.menu`.
- Include emojis in menu options.
- Handle `KeyboardInterrupt` and `EOFError` gracefully.
- Use the robust menu loop pattern (see code example below):

```python
while True:
    choice = show_menu("Menu Title", options, ...)
    if choice is None or choice == "0":
        break
    action = options[choice][1]
    if callable(action):
        action()
```

## Input Handling

- Use centralized input utilities: `from dataset_forge.utils.input_utils import get_path_with_history, get_folder_path`
- Support path history, favorites, and intelligent defaults.

## File Operations

- Use centralized file utilities: `from dataset_forge.utils.file_utils import is_image_file, get_unique_filename`
- Support all major image formats.
- Handle file operations safely (copy, move, inplace).

## Image Processing

- Use centralized image utilities: `from dataset_forge.utils.image_ops import get_image_size`
- Handle alpha channels properly.
- Use PIL for basic, OpenCV for advanced processing.

## Logging & Error Handling

- Use centralized logging: `from dataset_forge.utils.history_log import log_operation`
- Log all major operations with timestamps.
- Use try-except with meaningful error messages.
- Provide graceful degradation for non-critical errors.
- All user-facing errors must trigger the error sound (error.mp3) via the centralized print_error utility.

## Session State & Configuration

- Use centralized session state: `from dataset_forge.menus.session_state import parallel_config, user_preferences`
- Store user preferences and settings.
- Cache expensive operation results.

## DPID (Degradation) Patterns

- Use centralized DPID utilities: `from dataset_forge.utils.dpid_phhofm import process_image, downscale_folder`
- Support multiple DPID implementations.
- Use parallel processing for efficiency.

## Audio & User Feedback

- Use centralized audio utilities: `from dataset_forge.utils.audio_utils import play_done_sound`
- Play completion sounds for long operations.
- Respect user audio preferences.
- All user-facing errors must trigger the error sound (error.mp3) via the centralized print_error utility.

## Testing & Validation

- Validate input paths and file existence.
- Check image format compatibility.
- Verify HQ/LQ pair alignment.
- Provide detailed error messages.

## Performance Optimization

- Use parallel processing for I/O and CPU.
- Implement batch processing for large datasets.
- Use memory-efficient operations.
- Cache expensive computations.

## Monitoring, Analytics & Error Tracking

- Use centralized monitoring utilities: `from dataset_forge.utils.monitoring import monitor_performance, track_errors, register_background_task, health_check`
- Decorate all user-facing and long-running functions in actions/ with `@monitor_performance` and `@track_errors` for analytics and error tracking
- Register all subprocesses/threads with `register_background_task` for background task management
- Use `health_check()` for RAM, disk, CUDA, and permissions validation
- Ensure persistent logging of analytics and errors to ./logs/
- Trigger notifications (sound/visual) for critical errors
- Integrate memory and CUDA cleanup on exit/errors for all tracked processes/threads
- All monitoring and analytics features must be accessible from the System Monitoring menu

## Error Handling & Recovery

- Catch specific exceptions (`FileNotFoundError`, `PermissionError`, etc.).
- Provide recovery options when possible.
- Log errors for debugging.
- Continue processing when individual items fail.

## Documentation Requirements

- Google-style docstrings for all public functions/classes.
- Include parameter types, return values, exceptions.
- Provide usage examples in docstrings.

## Security Considerations

- Validate all user inputs.
- Sanitize file paths to prevent path traversal.
- Use safe file operations.
- Handle sensitive data appropriately.

## Dependency Management

- Add new dependencies to `requirements.txt`.
- Use version constraints for stability.
- Document optional dependencies.
- Test with minimal dependency sets.

## Git Ignore Patterns

- See `.gitignore` for patterns.
- Ignore venvs, caches, logs, configs (except examples), results, and user-specific files.

## Final Reminders

1. **Always activate the virtual environment**: `venv312\Scripts\activate`
2. **Always use centralized utilities from `dataset_forge.utils`**
3. **Always include proper error handling and logging**
4. **Always use the Catppuccin Mocha color scheme**
5. **Always follow the modular architecture patterns**
6. **Always implement parallel processing for performance**
7. **Always manage memory properly, especially for CUDA operations**
8. **Always provide user-friendly feedback and progress tracking**
9. **Always document your code with Google-style docstrings**
10. **Always test your changes thoroughly before committing**
11. **All user-facing errors must trigger the error sound (error.mp3) via the centralized print_error utility.**

---

For questions, see [Contributing](contributing.md) or ask the project maintainer.

---


# Changelog


[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Changelog

## [Unreleased]

- Added comprehensive [Style Guide](style_guide.md) to docs/ for coding standards, architecture, and best practices (July 2025).
- **OpenModelDB Integration:**
  - Added OpenModelDB Model Browser with classic and CLI-interactive modes
  - Search, filter, view, download, and test models from OpenModelDB
  - Robust download logic (SHA256, Google Drive, OneDrive/manual fallback)
  - CLI-interactive mode with live search, arrow keys, and dynamic actions
  - Batch upscaling, Spandrel/ONNX support, tiling, alpha handling, device/precision selection
  - Improved error handling, user feedback, and Catppuccin Mocha UI
- **Advanced Monitoring, Analytics & Error Tracking:**
  - Added monitoring.py utility for live resource usage (CPU, GPU, RAM, disk), performance analytics, error tracking, health checks, and background task registry.
  - Added system_monitoring_menu.py for CLI access to monitoring, analytics, error summaries, health checks, and background task management.
  - Decorator-based integration for analytics and error tracking in all action modules.
  - Persistent logging of analytics and errors to ./logs/.
  - Notifications for critical errors (sound/visual).
  - Memory and CUDA cleanup integrated on exit/errors for all tracked processes/threads.
  - Background task management: pause, resume, kill subprocesses/threads from CLI.
- Added Content-Based Image Retrieval (CBIR) for Duplicates:
  - Semantic duplicate detection using CLIP, ResNet, and VGG embeddings
  - Fast similarity search and grouping with ANN indexing
  - Batch actions: find, remove, move, copy duplicate groups
  - Integrated into Clean & Organize submenu under Dataset Management
- Integrated comprehensive automated test suite (pytest-based)
- Covers CLI, menu timing, error feedback, memory, parallelism, file/image utils
- Handles Unicode, subprocess, and Windows-specific issues
- Manual/script tests for BHI filtering and pepeline
- All tests pass as of this integration

## [July 2025]

- Added menu timing/profiling system: every menu and submenu load is timed and printed to the user.
- All menu load times are recorded and viewable in the System Monitoring menu ("⏱️ View Menu Load Times").
- Lazy import pattern enforced for all menus and actions for maximum CLI speed.
- Timing prints use the Catppuccin Mocha color scheme for clarity.
- Documentation updated across README.md and docs/ to reflect these changes.
- Global robust menu loop pattern integration for all menus and submenus
- Improved reliability and navigation throughout the CLI
- Added menu timing & profiling integration for all menus and submenus
- Implemented robust menu loop pattern for reliability
- Integrated Content-Based Image Retrieval (CBIR) for semantic duplicate detection
- Centralized monitoring, analytics, and error tracking system
- Comprehensive test suite covering CLI, memory, parallelism, and error feedback
- requirements.txt is now grouped and commented by category
- Added install order warnings for VapourSynth/getnative and CUDA/torch

This file will track major changes and releases in the future.


---


# Contributing


[ Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Contributing

Thank you for your interest in contributing to **Dataset Forge**! We welcome contributions from the community to improve features, fix bugs, and enhance documentation.

## How to Contribute

1. **Read the [Style Guide](style_guide.md):**
   - All code must follow the project's coding standards, modular architecture, and documentation requirements.
2. **Fork the repository** and create a new branch for your feature or fix.
3. **Write clear, well-documented code:**
   - Use Google-style docstrings and type hints for all public functions/classes.
   - Add or update tests in `tests/` for new features or bugfixes.
   - Update or add documentation in the appropriate `docs/` file(s).
4. **Test your changes:**
   - Activate the virtual environment: `venv312\Scripts\activate`
   - Run the test suite: `pytest`
   - Ensure all tests pass on your platform (Windows and/or Linux).
5. **Submit a Pull Request (PR):**
   - Describe your changes clearly in the PR description.
   - Reference any related issues or discussions.
   - If your change affects documentation, mention which files were updated.
   - Be responsive to code review feedback.

## Development Guidelines

- **Modular Design:**
  - UI in `menus/`, business logic in `actions/`, helpers in `utils/`.
  - Use lazy imports for menu actions (see [advanced.md](advanced.md)).
- **Memory & Performance:**
  - Use centralized memory and parallel processing utilities.
  - Always clean up memory after large operations.
- **Testing:**
  - Add tests for new features and bugfixes.
  - Use pytest fixtures and monkeypatching as needed.
- **Documentation:**
  - Update relevant docs in `docs/` and regenerate `README_full.md` and `toc.md` using `merge_docs.py` after changes.
  - Keep navigation links at the top of each doc file.
- **Commit Messages:**
  - Use clear, descriptive commit messages (e.g., `feat: add CBIR duplicate detection`, `fix: handle VapourSynth import error`).
- **Community Standards:**
  - Be respectful and constructive in all communications.
  - Report bugs or suggest features via GitHub Issues.

## Doc Maintenance

- After updating any documentation, always regenerate `docs/README_full.md` and `docs/toc.md` using `merge_docs.py`.
- For major changes, update `docs/changelog.md`.
- For new documentation sections, create a new markdown file in `docs/` and add it to the Table of Contents in `README.md` and `docs/toc.md`.

---

For questions, open an issue or contact the project maintainer.


---


# Faq


# Frequently Asked Questions (FAQ)

---

### What is Dataset Forge?

Dataset Forge is a modular Python CLI tool for managing, analyzing, and transforming image datasets, with a focus on HQ/LQ pairs for super-resolution and ML workflows.

### What platforms are supported?

- Windows (primary)
- Linux (tested)
- macOS is not officially supported but may work with some features disabled.

### What Python version is required?

Python 3.12+ is recommended. The project supports Python 3.8+ but is tested on 3.12.

### How do I install Dataset Forge and its dependencies?

See the [Quick Start](../README.md#quick-start) and [Special Installation Instructions](special_installation.md). Always install the correct CUDA-enabled torch/torchvision/torchaudio **before** running `pip install .`.

### Why do I need to install VapourSynth before getnative?

getnative depends on VapourSynth. If VapourSynth is not installed first, getnative will fail to import or function. See [special_installation.md](special_installation.md#vapoursynth--getnative-for-getnative-functionality).

### How do I fix python-magic errors on Windows?

You must copy the required DLLs from `assets/libmagicwin64-master.zip` to `C:/Windows/System32/`. See [special_installation.md](special_installation.md#python-magic-for-directory-utilities).

### How do I run the test suite?

Activate the virtual environment and run `pytest`. See [usage.md](usage.md#running-tests).

### What is CBIR for Duplicates?

CBIR (Content-Based Image Retrieval) for Duplicates uses deep learning models (CLIP, ResNet, VGG) to find images that are semantically similar, even if visually transformed. It extracts feature embeddings, computes similarity, and groups duplicates for easy management. See [features.md](features.md#cbir-content-based-image-retrieval-for-duplicates).

### How do I use the monitoring and analytics features?

Access the System Monitoring menu from the CLI to view live resource usage, error tracking, analytics, and health checks. See [features.md](features.md#monitoring-analytics--error-tracking).

### What should I do if I get CUDA or GPU errors?

- Ensure your CUDA and cuDNN versions match your PyTorch install.
- Close other GPU-intensive applications.
- Lower batch size or use CPU fallback if you run out of memory.
- See [troubleshooting.md](troubleshooting.md).

### What if a menu or feature is missing or crashes?

- Make sure you are running the latest version.
- Check the logs in the `./logs/` directory for error details.
- See [troubleshooting.md](troubleshooting.md) for solutions to common issues.

### How do I get help or report a bug?

Open an issue on GitHub or contact the project maintainer.

---

If your question is not answered here, check the [usage guide](usage.md), [troubleshooting guide](troubleshooting.md), or open an issue.

---


# License


# License

This project is licensed under the Creative Commons CC-BY-SA-4.0. See the [LICENSE](../LICENSE) file for details.

---
