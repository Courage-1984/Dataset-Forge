<!--
README_full.md: This file is a comprehensive, auto-generated documentation for Dataset Forge.
Whenever you update any documentation in README.md or docs/*.md, you MUST update this file as well.
-->

# Dataset Forge — Full Documentation

---

<!-- Main README.md content -->
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

See [Project Architecture](#project-architecture) for details.

---

## 🏎️ Fast CLI Menus with Lazy Imports

Dataset Forge now uses a lazy import pattern for all main menus and submenus. This means the CLI is extremely fast and responsive, even as the project grows. Heavy modules and actions are only imported when needed, keeping startup and navigation snappy.

See [Advanced Features & Configuration](#advanced-features--configuration) for details on the lazy import pattern.

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
- See [Advanced Features & Configuration](#advanced-features--configuration) for full details.

---

## 📖 Table of Contents

- [Features](#features)
- [Usage Guide](#usage-guide)
- [Advanced Features & Configuration](#advanced-features--configuration)
- [Project Architecture](#project-architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Style Guide](#dataset-forge-style-guide)
- [FAQ](#frequently-asked-questions-faq)
- [Changelog](#changelog)
- [License](#license)

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

Dataset Forge is a professional-grade tool for ML researchers and data scientists, designed for high-quality dataset curation, analysis, and transformation. For full documentation, see the [docs/](#full-documentation) section or the links above.

**Audio error feedback:** Whenever an error is reported to the user, an error sound (error.mp3) is played for immediate feedback, ensuring you never miss a critical issue.

**For coding standards and best practices, see the [Style Guide](#dataset-forge-style-guide).**

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

- Edit the relevant file in the [docs/](#full-documentation) section.
- Keep the main README.md concise and up-to-date with links to detailed docs.
- Add new sections to docs/ as the project grows.
- **Whenever you update any documentation in README.md or docs/\*.md, you MUST update this file as well.**

---

<!-- Badges (add more as needed) -->
<p align="center">
  <a href="https://github.com/Courage-1984/Dataset-Forge/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-CC--BY--SA--4.0-blue" alt="License"></a>
  <!-- Add CI/build/test badges here if available -->
</p>

---

# Features

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

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

- **Basic Transformations**: Downsampling (DPID, OpenCV, PIL), HDR to SDR conversion, grayscale conversion, alpha channel removal
- **Color & Tone Adjustments**: Brightness, contrast, hue, saturation adjustments
- **Metadata Tools**: EXIF scrubbing, ICC to sRGB conversion
- **Augmentation Pipeline**: Custom transformation recipes, data augmentation
- **Advanced Tiling**: BestTile with Laplacian/IC9600 complexity analysis
- **Sketch/Line Art Extraction**: Find and extract sketches, drawings, and line art from images using a deep learning model ([Sketch-126-DomainNet](https://huggingface.co/prithivMLmods/Sketch-126-DomainNet)). Supports single folder or HQ/LQ pairs, with copy/move options and confidence threshold.

## Training & Inference

- **OpenModelDB Model Browser**: Browse, search, filter, and manage models from [OpenModelDB](https://openmodeldb.info) directly in the CLI.
  - Hierarchical menu and modern CLI-interactive mode (arrow keys, live search, dynamic actions)
  - Search/filter by tag, architecture, scale, or free text
  - View model details, resources, and sample images
  - Download models (with SHA256 verification, OneDrive/Google Drive/manual fallback)
  - Test models on user images (with Spandrel/ONNX support, robust upscaling pipeline)
  - Batch upscaling and directory support
  - Open model page in browser
  - List and manage already downloaded models
  - Catppuccin Mocha-themed interface and progress bars
  - Robust error handling and user feedback

## Utilities

- **Visual Comparison**: Side-by-side comparisons, animated GIF comparisons
- **Folder Comparison**: Find missing files between folders
- **Compression Tools**: Image compression, directory archiving
- **Enhanced Directory Tree**: Advanced directory visualization with emoji categorization, statistics, and multiple output formats
- **Path History**: Smart path management with history and favorites
- **Parallel Processing**: High-performance multiprocessing and multithreading
- **System Monitoring, Analytics & Error Tracking**: Live monitoring of CPU, GPU, RAM, and disk usage for all processes and threads; performance analytics with persistent logging; error tracking with CLI and log summaries; health checks (RAM, disk, CUDA, permissions); background task management (pause/resume/kill); notifications for critical errors; memory and CUDA cleanup integration; all accessible from a dedicated CLI menu.

## Beautiful CLI Interface

- **Catppuccin Mocha Theme**: Beautiful ANSI color scheme
- **Hierarchical Menus**: Intuitive 7-category main menu with logical sub-menus
- **Progress Tracking**: Progress bars, error handling, memory management
- **Smart Input**: Path history, favorites, and intelligent defaults
- **Parallel Processing**: Multiprocessing and multithreading for speed improvements
- **Audio error feedback**: Whenever an error is reported to the user, an error sound (error.mp3) is played for immediate feedback.
- ⚡ **Fast CLI menus with lazy imports:** All main menus and submenus use a lazy import pattern, so heavy modules are only loaded when needed. This makes the CLI extremely fast and responsive, even for large projects.

---

# Advanced Features

## AI-Powered Image Analysis

### Sketch Extraction with Deep Learning

- **Model**: [Sketch-126-DomainNet](https://huggingface.co/prithivMLmods/Sketch-126-DomainNet) from Hugging Face
- **Capabilities**: Detect and extract sketches, drawings, and line art from images
- **Features**: Configurable confidence thresholds, support for single folders and HQ/LQ pairs
- **Operations**: Copy or move detected sketches to separate directories
- **Performance**: GPU-accelerated inference with automatic memory management

### BHI Filtering - Multi-Metric Quality Assessment

- **Blockiness Detection**: Identify compression artifacts using DCT analysis
- **HyperIQA**: Perceptual quality assessment using deep learning
- **IC9600**: Neural quality assessment with ICNet architecture
- **Preset Thresholds**: Pre-configured moderate, strict, and lenient filtering options
- **Custom Thresholds**: Adjustable parameters for fine-tuned quality control
- **Batch Processing**: Efficient GPU-accelerated processing of large datasets

### Advanced Tiling with AI Complexity Analysis

- **IC9600 Complexity**: Neural network-based complexity assessment using ICNet
- **Laplacian Complexity**: Traditional complexity measure for comparison
- **BestTile Algorithm**: Dynamic tile selection based on image complexity
- **Adaptive Tiling**: Automatically adjust tile count based on image characteristics
- **Dual Strategy Support**: Choose between traditional and AI-powered tiling
- **Memory Optimization**: Efficient processing with automatic CUDA memory management

## Advanced Processing & Transformation

### Batch Operations Pipeline

- **Dataset Splitting**: Split by count, percentage, or random selection
- **Dimension Filtering**: Remove images based on width/height thresholds
- **File Type Filtering**: Filter by specific image formats
- **Advanced Color Adjustments**: Precise control over brightness, contrast, saturation
- **Format Conversion**: PNG optimization, WebP conversion with quality control
- **HDR to SDR Conversion**: Multiple tone mapping algorithms (Hable, Reinhard, etc.)

### Upscaling with Advanced Model Support

- **Spandrel Integration**: Support for various upscaling models and architectures
- **Chainner-ext Processing**: Advanced image processing with high-quality filters
- **Tile-Based Upscaling**: Configurable tile sizes for memory-efficient processing
- **Alpha Channel Handling**: Upscale, resize, or discard alpha channels
- **Precision Control**: FP32, FP16, and BF16 precision options
- **GPU Memory Management**: Automatic memory optimization for large images

### Image Sanitization & Security

- **Steganography Detection**: Use steghide and zsteg to detect hidden data
- **ICC Profile Conversion**: Convert to sRGB for consistent color reproduction
- **Alpha Channel Removal**: Optional transparency channel removal
- **Metadata Scrubbing**: Comprehensive EXIF data removal
- **Dry Run Mode**: Preview changes before applying modifications
- **Security Analysis**: Comprehensive image security assessment

## Memory & Performance Optimization

### Advanced Memory Management

- **CUDA Memory Management**: Automatic GPU memory cleanup and optimization
- **Context Managers**: Memory-safe operations for intensive processing
- **Safe Tensor Operations**: Device-agnostic tensor handling
- **Memory Monitoring**: Real-time memory usage tracking and optimization
- **Automatic Cleanup**: Memory cleanup after large operations
- **Memory Recommendations**: Intelligent suggestions for optimal settings

### Smart Parallel Processing

- **Processing Type Selection**: Automatic choice between thread/process/sequential
- **Batch Processing**: Memory-efficient processing of large datasets
- **GPU Memory Fraction Control**: Configurable GPU memory allocation
- **Timeout Handling**: Graceful handling of long-running operations
- **Progress Tracking**: Real-time progress with memory usage monitoring
- **Error Recovery**: Robust error handling with automatic retry mechanisms

## Advanced Configuration & Integration

### External Tool Integration

- **WTP Dataset Destroyer**: Full integration with advanced dataset processing
- **traiNNer-redux**: Seamless training pipeline integration
- **VapourSynth**: Required for getnative functionality. **You must install VapourSynth before installing or using getnative.**
- **ExifTool**: Advanced metadata handling and manipulation
- **FFmpeg**: Video processing and HDR conversion capabilities

### Configuration Management

- **HCL File Support**: WTP Dataset Destroyer configuration format
- **YAML Configuration**: traiNNer-redux training configurations
- **JSON Configuration**: Flexible project and model configurations
- **User Profile System**: Personalized settings, favorites, and presets
- **Community Links**: Curated resource collections and external tools
- **Configuration Validation**: Automatic validation of configuration files

## Rich Reporting & Analysis

### Advanced Reporting System

- **HTML Report Templates**: Interactive reports with embedded visualizations
- **Quality Score Histograms**: Multi-metric quality assessment visualization
- **Class Balance Analysis**: Dataset composition and distribution analysis
- **Sample Image Generation**: Automatic sample selection for reports
- **Dimension Analysis**: Comprehensive size and aspect ratio reporting
- **Scale Relationship Detection**: HQ/LQ scale analysis and validation

### Advanced Analysis Features

- **Native Resolution Detection**: Automatic detection of original image resolutions
- **Extreme Dimension Analysis**: Identification of unusually sized images
- **Aspect Ratio Testing**: Comprehensive aspect ratio validation
- **Scale Relationship Detection**: Automatic HQ/LQ scale factor detection
- **Outlier Detection**: Statistical analysis for anomalous images
- **Corruption Detection**: Comprehensive image integrity checking

## System Monitoring, Analytics & Error Tracking

- **Live Resource Monitoring**: Real-time CPU, GPU (NVIDIA), RAM, and disk usage for all processes/threads
- **Performance Analytics**: Decorator-based analytics for all major operations, with live and persistent session summaries
- **Error Tracking**: Logs errors to file and CLI, with summary granularity and critical error notifications (sound/visual)
- **Audio error feedback**: All user-facing errors trigger an error sound (error.mp3) for immediate notification.
- **Health Checks**: Automated checks for RAM, disk, CUDA, Python version, and permissions, with CLI output and recommendations
- **Background Task Management**: Registry of all subprocesses/threads, with CLI controls for pause/resume/kill and session-only persistence
- **Persistent Logging**: All analytics and errors are logged to ./logs/ for later review
- **Memory & CUDA Cleanup**: Automatic cleanup on exit/errors for all tracked processes/threads
- **Dedicated CLI Menu**: Access all monitoring, analytics, and management features from the System Monitoring menu

---

# Advanced Features & Configuration

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Advanced Features & Configuration

(Include the full "Advanced Features", "Configuration", and "Requirements" sections from the original README here, preserving formatting and navigation.)

## Advanced OpenModelDB Integration

- **CLI-interactive Mode:** Modern, dynamic interface for model browsing, search, and actions (requires `questionary`).
- **Batch Upscaling:** Use downloaded models for batch upscaling of directories, with progress bars and error handling.
- **Robust Download Handling:** SHA256 verification, Google Drive via gdown, OneDrive manual fallback, user confirmation, and progress bars.
- **Testing & Inference:** Supports Spandrel and ONNX models, tiling, alpha handling, device/precision selection, and output format options.
- **Extensibility:** Designed for future features (batch, metrics, advanced filtering, etc.).
- **User Experience:** Catppuccin Mocha color scheme, progress bars, audio feedback, and clear error messages throughout the workflow.

## Advanced System Monitoring & Analytics

Dataset Forge includes a comprehensive monitoring and analytics system for live resource usage, performance analytics, error tracking, health checks, and background task management.

- **Accessing Monitoring:**

  - Use the 'System Monitoring' menu from the main CLI to view live CPU, GPU, RAM, and disk usage for all processes and threads.
  - View performance analytics and error summaries for the current session and review persistent logs in ./logs/.

- **Performance Analytics:**

  - All major operations are instrumented with decorators for analytics and error tracking.
  - Analytics are shown live in the CLI and saved to disk for later review.

- **Error Tracking & Notifications:**

  - Errors are logged to both file and CLI, with summaries and critical error notifications (sound/visual).
  - **Audio error feedback:** Whenever an error is reported to the user (via print_error), an error sound (error.mp3) is played for immediate feedback.

- **Health Checks:**

  - Automated checks for RAM, disk, CUDA, Python version, and permissions are available from the monitoring menu.
  - CLI output provides recommendations and warnings.

- **Background Task Management:**

  - All subprocesses/threads are registered and can be paused, resumed, or killed from the CLI menu.
  - Session-only persistence ensures background tasks are managed safely.

- **Memory & CUDA Cleanup:**

  - Automatic cleanup is triggered on exit/errors for all tracked processes/threads.

- **Configuration:**
  - Monitoring and analytics are enabled by default. Advanced users can customize logging, notification, and analytics settings in the configuration files.

See the [Usage Guide](usage.md) for step-by-step instructions.

---

## Fast CLI Menus with Lazy Imports (Updated)

Dataset Forge now uses a comprehensive lazy import pattern for all main menus and submenus. This means:

- **Heavy modules and actions are only imported when the user selects a menu option.**
- The CLI main menu and all submenus are now extremely fast and responsive, even as the project grows.
- The `lazy_action()` helper is used throughout menu files to wrap actions and submenu calls, ensuring imports are deferred until needed.
- This pattern is applied to: main menu, dataset management, analysis & validation, image processing, system monitoring, model management, and more.

**Why?**

- Python imports can be slow, especially with large dependencies (e.g., torch, PIL, OpenCV).
- Lazy imports keep the CLI snappy and reduce memory usage.

**How to use in new menus:**

- Use the `lazy_action(module_path, func_name)` helper to wrap any action or submenu that imports heavy modules.
- See `dataset_forge/menus/main_menu.py` and other menu files for examples.

This is now the recommended pattern for all new menu and action integrations.

## Robust Menu Loop Pattern (July 2025)

All menus and submenus now use a robust, standardized menu loop pattern:

- The user's choice (key) is obtained from `show_menu`.
- The action is looked up in the options dictionary.
- The action is called if it is callable.
- This pattern is applied globally, ensuring reliable navigation and submenu invocation everywhere.
- No more redraw bugs or dead options—every menu and submenu works as intended.

This pattern complements the lazy import and timing/profiling systems, maximizing CLI speed, reliability, and user experience.

# Usage Guide

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Advanced Features](advanced.md)

# Usage Guide

(Include the full "Usage Examples" and "Menu Structure" sections from the original README here, preserving formatting and navigation.)

## Using the System Monitoring Menu

The System Monitoring menu provides live resource usage, analytics, error tracking, health checks, and background task management:

1. Select '🖥️ System Monitoring' from the main menu.
2. Features available:
   - **Live Resource Usage**: View CPU, GPU, RAM, and disk usage for all processes/threads.
   - **Performance Analytics**: See live and session analytics for all major operations.
   - **Error Summaries**: Review error logs and summaries, with notifications for critical errors.
   - **Health Checks**: Run automated checks for RAM, disk, CUDA, Python version, and permissions.
   - **Background Task Management**: List, pause, resume, or kill subprocesses/threads.
   - **Persistent Logs**: All analytics and errors are saved to ./logs/ for later review.
   - **Notifications**: Critical errors trigger sound/visual notifications.
   - **Audio error feedback**: All user-facing errors trigger an error sound (error.mp3) for immediate notification.

See the [Advanced Features](advanced.md) for more details on configuration and integration.

## Using the OpenModelDB Model Browser

The OpenModelDB Model Browser is available from the Training & Inference menu:

1. Select '🧠 OpenModelDB Model Browser'.
2. Choose between:
   - **Basic Menu (classic):** Hierarchical, emoji-rich menu system
   - **CLI-interactive (modern):** Arrow keys, live search, and dynamic actions (requires `questionary`)

### Features

- Browse, search, and filter models by tag, architecture, scale, or free text
- View model details, resources, and sample images
- Download models (with SHA256 verification, Google Drive/OneDrive/manual fallback)
- Test models on your images (with Spandrel/ONNX support)
- List and manage already downloaded models
- Open model page in your browser

### Downloading from OneDrive

If a model is hosted on OneDrive, you will be prompted to download it manually. The browser will open the link for you, and you should place the file in the indicated models directory.

### CLI-interactive Mode

- Use arrow keys and type to search models
- After selecting a model, choose actions: View Details, Download, Test, Open in Browser, or go back
- Requires `questionary` (install with `pip install questionary`)

## Content-Based Image Retrieval (CBIR) for Duplicates

- Semantic duplicate detection using deep learning embeddings (CLIP, ResNet, VGG)
- Feature extraction, similarity search, ANN indexing, grouping, and batch actions (find, remove, move, copy)
- GPU acceleration and robust menu integration
- See features, usage, and advanced sections for details

# Project Architecture

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Project Architecture

(Include the full "Modular Architecture" and "Project Structure" sections from the original README here, preserving formatting and navigation.)

## Monitoring & Analytics Architecture

- **dataset_forge/utils/monitoring.py**: Centralized resource monitoring, analytics, error tracking, health checks, and background task registry. Provides decorators and context managers for integration with all action modules. Handles persistent logging and notifications.
- **dataset_forge/menus/system_monitoring_menu.py**: CLI menu for live resource usage, analytics, error summaries, health checks, and background task management. Integrates with monitoring.py and is accessible from the main menu.

All major operations in actions/ are instrumented with monitoring/analytics hooks, and memory/CUDA cleanup is integrated throughout the app lifecycle.

## Audio Error Feedback

The CLI interface now provides audio error feedback: whenever an error is reported to the user (via print_error), an error sound (error.mp3) is played for immediate feedback. This is handled by the centralized print_error utility in utils/printing.py, which calls play_error_sound from utils/audio_utils.py.

# Dataset Forge Style Guide

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md) | [Contributing](contributing.md)

# Dataset Forge Style Guide

Welcome to the official style and coding standards guide for Dataset Forge. All contributors **must** follow these guidelines to ensure code quality, maintainability, and a consistent user experience.

---

## Table of Contents

- [General Principles](#general-principles)
- [Project Architecture](#project-architecture)
- [Coding Standards](#coding-standards)
- [Import Organization](#import-organization)
- [Memory Management](#memory-management)
- [Parallel Processing](#parallel-processing)
- [Progress Tracking & User Feedback](#progress-tracking--user-feedback)
- [Color Scheme & UI](#color-scheme--ui)
- [Menu System](#menu-system)
- [Input Handling](#input-handling)
- [File Operations](#file-operations)
- [Image Processing](#image-processing)
- [Logging & Error Handling](#logging--error-handling)
- [Session State & Configuration](#session-state--configuration)
- [DPID (Degradation) Patterns](#dpid-degradation-patterns)
- [Audio & User Feedback](#audio--user-feedback)
- [Testing & Validation](#testing--validation)
- [Performance Optimization](#performance-optimization)
- [Error Handling & Recovery](#error-handling--recovery)
- [Documentation Requirements](#documentation-requirements)
- [Security Considerations](#security-considerations)
- [Dependency Management](#dependency-management)
- [Git Ignore Patterns](#git-ignore-patterns)
- [Final Reminders](#final-reminders)

---

## General Principles

- **Python 3.8+**. Use modern Python features.
- **PEP 8** style, 4-space indentation, 88-char line length (Black standard).
- **Google-style docstrings** for all public functions/classes.
- **Type hints** for all function parameters and return values.
- **Absolute imports** for all `dataset_forge` modules.
- **Modular design**: UI (menus/), business logic (actions/), utilities (utils/), DPID (dpid/).

## Project Architecture

- See [Project Architecture](architecture.md) for directory structure and modularity.
- Keep UI, logic, and utilities separate.
- Use thin UI layers (menus), business logic in actions, helpers in utils.

## Coding Standards

- PEP 8, 4-space indent, 88-char lines.
- Use type hints everywhere.
- Google-style docstrings (see below).
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

# Contributing

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md) | [Style Guide](style_guide.md)

# Contributing

> **All code contributions must follow the [Style Guide](style_guide.md).**

(Include the full "Contributing" and "Development Guidelines" sections from the original README here, preserving formatting and navigation.)

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

All tests pass as of this integration. See [usage.md](usage.md) and [features.md](features.md) for details.

# Frequently Asked Questions (FAQ)

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Frequently Asked Questions (FAQ)

(If there are not enough FAQs in the original README, leave this as a stub for future expansion.)

# Troubleshooting

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Troubleshooting

(Include the full "Troubleshooting" section from the original README here, preserving formatting and navigation.)

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

This file will track major changes and releases in the future.

# License

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# License

This project is licensed under the Creative Commons CC-BY-SA-4.0. See the [LICENSE](../LICENSE) file for details.

---

## Menu Timing & Profiling (New in July 2025)

Dataset Forge now features a fast, responsive CLI menu system with built-in timing and profiling:

- Every time you load a menu or submenu, you will see a timing print (e.g., `⏱️ Loaded dataset_management_menu in 0.123 seconds.`) in the Catppuccin Mocha color scheme.
- All menu load times are recorded and can be viewed in the System Monitoring menu under "⏱️ View Menu Load Times".
- This helps you identify slow-loading menus and provides transparency for performance optimization.
- The timing system uses lazy imports to maximize CLI speed and minimize memory usage.

See also:

- [Features](features.md#menu-timing--profiling-july-2025)
- [Usage](usage.md#menu-timing--profiling)
- [Advanced](advanced.md#advanced-menu-timing-profiling-and-lazy-imports)
- [Architecture](architecture.md#menu-timing--profiling-in-the-architecture)
- [Style Guide](style_guide.md#menu-timing--profiling-best-practices)
- [Troubleshooting](troubleshooting.md#troubleshooting-menu-timing--profiling)
