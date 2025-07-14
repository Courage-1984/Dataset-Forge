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

## Menu Timing & Profiling

Dataset Forge features a fast, responsive CLI menu system with built-in timing and profiling. Every time you load a menu or submenu, a timing print (e.g., `⏱️ Loaded dataset_management_menu in 0.123 seconds.`) is shown in the Catppuccin Mocha color scheme. All menu load times are recorded and can be viewed in the System Monitoring menu under "⏱️ View Menu Load Times". This helps identify slow-loading menus and provides transparency for performance optimization. The timing system uses lazy imports to maximize CLI speed and minimize memory usage.

## Robust Menu Loop Pattern

All menus and submenus use a robust, standardized menu loop pattern:

- The user's choice (key) is obtained from `show_menu`.
- The action is looked up in the options dictionary.
- The action is called if it is callable.
  This pattern ensures reliable navigation and submenu invocation everywhere. Example:

```python
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha

def my_menu():
    options = {
        "1": ("📂 Option 1", function1),
        "2": ("🔍 Option 2", function2),
        "0": ("🚪 Exit", None),
    }
    while True:
        try:
            action = show_menu("Menu Title", options, Mocha.lavender)
            if action is None:
                break
            action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break
```

## Content-Based Image Retrieval (CBIR) for Duplicates

CBIR uses deep learning embeddings (CLIP, ResNet, VGG) for semantic duplicate detection. It supports feature extraction, similarity search, ANN indexing, grouping, and batch actions (find, remove, move, copy). Access CBIR features from the Duplicates menu. See the usage guide for workflow details.

## Monitoring, Analytics & Error Tracking

Dataset Forge uses centralized monitoring and analytics utilities. All user-facing and long-running functions are decorated for performance and error tracking. Subprocesses/threads are registered for background task management. Health checks for RAM, disk, CUDA, and permissions are available. Persistent logging of analytics and errors is stored in ./logs/. All monitoring and analytics features are accessible from the System Monitoring menu.

## Test Suite

Dataset Forge includes a comprehensive, automated test suite covering CLI entry and menu navigation, menu timing/profiling, error feedback (including audio), memory management and parallel processing, file and image utilities, and robust handling of Unicode, subprocess, and Windows-specific issues. To run all tests:

```sh
venv312\Scripts\activate
pytest
```

## Dependency Management: Grouped Requirements & Install Order

The `requirements.txt` is grouped and commented for clarity. Please install VapourSynth before getnative, and install the correct CUDA-enabled torch/torchvision/torchaudio before running `pip install .`. See the advanced guide for details.

---

## Robust Menu Loop Pattern (July 2025)

All menus and submenus now use a robust, standardized menu loop pattern:

- The user's choice (key) is obtained from `show_menu`.
- The action is looked up in the options dictionary.
- The action is called if it is callable.
- This pattern is applied globally, ensuring reliable navigation and submenu invocation everywhere.
- No more redraw bugs or dead options—every menu and submenu works as intended.

This pattern complements the lazy import and timing/profiling systems, maximizing CLI speed, reliability, and user experience.

See [docs/usage.md](usage.md) and [docs/advanced.md](advanced.md) for implementation details and code examples.

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

## Content-Based Image Retrieval (CBIR) for Duplicates

- **Semantic Duplicate Detection**: Uses deep learning embeddings (CLIP, ResNet, VGG) to find images that are conceptually similar, even if visually transformed.
- **Feature Extraction**: Extracts high-dimensional feature vectors for each image using a pre-trained CNN (CLIP preferred, fallback to ResNet/VGG).
- **Similarity Search**: Computes cosine similarity or Euclidean distance between embeddings to identify near-duplicates.
- **ANN Indexing**: Uses approximate nearest neighbor (ANN) indexing for efficient search in large datasets.
- **Grouping & Actions**: Clusters images by semantic similarity and provides user options to find, remove, move, or copy duplicate groups.
- **GPU Acceleration**: Leverages GPU for fast embedding extraction and search.
- **Menu Integration**: Accessible from the Clean & Organize submenu under Dataset Management.

## Automated Test Suite

Dataset Forge now includes a robust, automated test suite:

- Covers CLI entry, menu navigation, timing/profiling, error feedback (audio), memory management, parallel processing, and file/image utilities.
- Handles Unicode, subprocess, and Windows-specific edge cases.
- Includes manual/script-style tests for BHI filtering and pepeline (run directly).
- All tests pass as of this integration.

See [usage.md](usage.md#running-tests) for instructions on running tests.

---


# Usage


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

---

## Using Content-Based Image Retrieval (CBIR) for Duplicates

1. Navigate to the main menu, then Dataset Management > Clean & Organize > CBIR (Semantic Duplicate Detection).
2. Choose your workflow: single-folder or HQ/LQ pair.
3. Select the embedding model: CLIP (recommended), ResNet, or VGG.
4. Set the similarity threshold (default: 0.92 for cosine similarity).
5. Choose an action:
   - **Find**: List groups of semantically similar images.
   - **Remove**: Delete all but one image in each group.
   - **Move**: Move duplicates to a specified folder.
   - **Copy**: Copy duplicates to a specified folder.
6. Review the summary of affected files after each operation.

CBIR supports GPU acceleration and is optimized for large datasets. For advanced options, see the advanced features documentation.

## Menu Timing & Profiling

Whenever you load a menu or submenu in Dataset Forge, you will see a timing print in the CLI, such as:

    ⏱️ Loaded dataset_management_menu in 0.123 seconds.

This print uses the Catppuccin Mocha color scheme for clarity and consistency.

All menu load times are recorded. To view a summary of all menu/submenu load timings:

1. Go to the **System Monitoring** menu from the main menu.
2. Select **"⏱️ View Menu Load Times"**.
3. You will see a table of all menu/submenu load times for your session.

This helps you identify slow-loading menus and optimize your workflow.

## Menu Navigation: Robust Pattern Everywhere

All menus and submenus now use a robust, standardized menu loop pattern:

- You select an option; the system looks up the action and calls it if callable.
- This ensures every menu and submenu works as intended, with no redraw bugs or dead options.
- Navigation is now consistent and reliable everywhere in the CLI.

For more details, see [docs/features.md](features.md) and [docs/advanced.md](advanced.md).

## Running Tests

Dataset Forge includes a comprehensive automated test suite. To run all tests:

1. Activate your virtual environment:
   ```sh
   venv312\Scripts\activate
   ```
2. Run all automated tests from the project root:
   ```sh
   pytest
   ```

Manual/script-style tests (for BHI filtering and pepeline) can be run directly:

```sh
python tests/test_bhi_filtering.py
python tests/test_pepeline.py
```

The test suite covers:

- CLI entry and menu navigation
- Menu timing/profiling
- Error feedback (including audio)
- Memory management and parallel processing
- File and image utilities
- Robust handling of Unicode, subprocess, and Windows-specific issues

See the [README.md](../README.md) and [features.md](features.md) for more details on test coverage and philosophy.

---


# Advanced


# Advanced Features & Configuration

## Requirements & Dependency Matrix

Dataset Forge requires the following for full functionality (especially for GPU acceleration):

- **Python**: 3.8+ (tested on 3.12)
- **OS**: Windows (primary), Linux (partial support)
- **CUDA**: 12.1+ (for GPU acceleration)
- **cuDNN**: 8.9+ (required for PyTorch CUDA)
- **PyTorch**: 2.2.0+ (see below)
- **RAM**: 8GB+ (16GB+ recommended for large datasets)
- **Storage**: SSD recommended for faster I/O
- **VapourSynth**: Required for getnative functionality. **You must install VapourSynth before installing or using getnative.**

**Dependency Matrix:**

| Python | CUDA Toolkit | cuDNN | PyTorch | OS      |
| ------ | ------------ | ----- | ------- | ------- |
| 3.12   | 12.1         | 8.9+  | 2.2.0+  | Windows |
| 3.8+   | 11.8/12.1    | 8.6+  | 2.0.0+  | Linux   |

- For GPU acceleration, ensure your CUDA and cuDNN versions match your PyTorch install. See [PyTorch Get Started](https://pytorch.org/get-started/locally/) for details.
- If you use a different CUDA/cuDNN version, install the matching PyTorch build.

**Installation via pip (recommended):**

```bash
py -3.12 -m venv venv312
venv312\Scripts\activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install .
```

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

---

## Advanced: Menu Timing, Profiling, and Lazy Imports

### Lazy Import Pattern

All menus and submenus in Dataset Forge use a lazy import pattern. This means that heavy modules and actions are only imported when the user selects a menu option, not at startup. This keeps the CLI fast and responsive, even as the codebase grows.

- Use the `lazy_action()` and `lazy_menu()` helpers to defer imports until needed.
- See `dataset_forge/menus/main_menu.py` for the canonical pattern.

### Menu Timing & Profiling Integration

- Every menu and submenu load is timed using a centralized utility (`time_and_record_menu_load` in `utils/monitoring.py`).
- Timing prints are shown to the user after each menu load, and all timings are aggregated for analytics.
- The System Monitoring menu provides a summary of all menu load times for the session.

### Extending/Customizing Timing Analytics

- Developers can use the timing utility in any new menu or action by wrapping the function call with `time_and_record_menu_load`.
- The timing system is extensible: you can add custom analytics, logging, or performance alerts as needed.

#### Rationale

- Lazy imports and timing analytics together ensure the CLI remains fast, memory-efficient, and transparent for both users and developers.

## Robust Menu Loop Pattern: Implementation & Rationale

To ensure reliable navigation and submenu invocation, all menus and submenus now use the following pattern:

```python
while True:
    choice = show_menu("Menu Title", options, ...)
    if choice is None or choice == "0":
        break
    action = options[choice][1]
    if callable(action):
        action()
```

- The user's choice (key) is obtained from `show_menu`.
- The action is looked up in the options dictionary.
- The action is called if it is callable.
- This pattern is now required for all menus and submenus.

This approach prevents redraw bugs and dead options, and works seamlessly with the lazy import and timing/profiling systems.

**Best Practice:** Always use this pattern for new menus. See [docs/style_guide.md](style_guide.md) for requirements.

## Content-Based Image Retrieval (CBIR) for Duplicates (Advanced)

CBIR enables semantic duplicate detection using deep learning embeddings:

- **Embedding Extraction**: Uses CLIP, ResNet, or VGG to generate feature vectors for each image. GPU acceleration is used if available.
- **Similarity Matrix**: Computes cosine similarity (default) or Euclidean distance between all image embeddings.
- **ANN Indexing**: For large datasets, uses approximate nearest neighbor (ANN) search for fast duplicate detection.
- **Grouping**: Clusters images by similarity threshold, forming groups of near-duplicates.
- **Batch Actions**: Supports batch removal, move, or copy of duplicates, keeping one image per group.
- **Parallel Processing**: Uses smart_map and batch_map for efficient processing.
- **Memory Management**: Integrates with memory_context and auto_cleanup for safe operation.
- **Menu Integration**: Follows the robust menu loop and lazy import patterns for fast, user-friendly CLI navigation.

For implementation details, see `cbir_actions.py` and `cbir_menu.py`.

## Test Suite & Best Practices

- Dataset Forge uses pytest for all automated testing.
- Tests are organized by utility, CLI, and integration level.
- Manual/script-style tests are provided for BHI filtering and pepeline.
- Contributors should add tests for new features and bugfixes.
- For CI integration, add a GitHub Actions workflow to run pytest on push/PR.
- See [usage.md](usage.md#running-tests) for how to run tests.

---


# Architecture


# Project Architecture

(Include the full "Modular Architecture" and "Project Structure" sections from the original README here, preserving formatting and navigation.)

## Monitoring & Analytics Architecture

- **dataset_forge/utils/monitoring.py**: Centralized resource monitoring, analytics, error tracking, health checks, and background task registry. Provides decorators and context managers for integration with all action modules. Handles persistent logging and notifications.
- **dataset_forge/menus/system_monitoring_menu.py**: CLI menu for live resource usage, analytics, error summaries, health checks, and background task management. Integrates with monitoring.py and is accessible from the main menu.

All major operations in actions/ are instrumented with monitoring/analytics hooks, and memory/CUDA cleanup is integrated throughout the app lifecycle.

## Audio Error Feedback

The CLI interface now provides audio error feedback: whenever an error is reported to the user (via print_error), an error sound (error.mp3) is played for immediate feedback. This is handled by the centralized print_error utility in utils/printing.py, which calls play_error_sound from utils/audio_utils.py.

---

## Menu System, Robust Loop, and Timing

The menu system uses a robust loop pattern and integrates timing/profiling for all menu and submenu loads. This ensures reliability and performance.

## Content-Based Image Retrieval (CBIR)

CBIR is integrated as a modular component for semantic duplicate detection.

## Monitoring, Analytics & Error Tracking

Monitoring and analytics are integrated throughout the architecture for performance and error tracking.

## Test Suite

The test suite is integrated to cover all major architectural components.

---


# Troubleshooting


# Troubleshooting

(Include the full "Troubleshooting" section from the original README here, preserving formatting and navigation.)

---

## Troubleshooting: Menu Timing & Profiling

**Problem:** Timing prints do not appear after loading a menu or submenu.

- Ensure you are running the latest version of Dataset Forge.
- Check that the menu or submenu uses the `time_and_record_menu_load` utility (see `utils/monitoring.py`).
- Make sure you are not selecting a "Back" or "Exit" option, which do not trigger timing prints.

**Problem:** Errors occur when navigating menus (e.g., `TypeError: 'str' object is not callable`).

- This usually means a menu action is not callable. All menu loops should check if the action is callable before calling it.
- Update your menu code to follow the latest menu loop pattern (see `docs/style_guide.md`).

If issues persist, consult the documentation or contact the project maintainer.

## Menu Loop Issues

If you encounter a menu that redraws repeatedly or a submenu that does not appear:

- Ensure the menu loop uses the robust pattern:
  - Get the user's choice (key) from `show_menu`.
  - Look up the action in the options dictionary.
  - Call the action if callable.
- This resolves most navigation and invocation issues in the CLI.

## CBIR Troubleshooting

- **Model loading errors**: Ensure torch, torchvision, and timm are installed and match your CUDA version. See requirements and install instructions.
- **GPU out of memory**: Lower the batch size or use CPU fallback. Close other GPU-intensive applications.
- **Slow performance**: Use GPU if available. For very large datasets, increase system RAM or process in smaller batches.
- **CLIP/ResNet/VGG not found**: Check requirements.txt and reinstall dependencies.

## Troubleshooting Test Issues

- **UnicodeEncodeError**: Set PYTHONIOENCODING=utf-8 in your environment or subprocess.
- **PermissionError on file deletion (Windows)**: Ensure files are closed before deleting; move os.unlink outside with blocks.
- **Monkeypatching not working**: Patch the function in the namespace where it is used, not just where it is defined.
- **Multiprocessing pickling errors**: Use top-level functions, not lambdas or closures, for functions passed to process pools.
- **Manual/script tests not running**: Run them directly with python, not via pytest.

## VapourSynth/getnative and CUDA/torch Install Order

If you encounter issues with getnative, ensure VapourSynth is installed first. For CUDA acceleration, install the correct CUDA-enabled torch/torchvision/torchaudio before running `pip install .`.

## Troubleshooting Menu Timing, Robust Loop, CBIR, Monitoring, and Test Suite

- If menu timing prints do not appear, check your CLI environment and ensure the latest version is installed.
- If robust menu navigation fails, ensure you are using the latest code and that all dependencies are installed.
- For CBIR issues, verify that all required deep learning models are installed and that your GPU drivers are up to date.
- For monitoring/analytics issues, check the logs in the ./logs/ directory.
- If tests fail, ensure your environment matches the requirements and all dependencies are installed.

---


# Style Guide


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

---

## Menu Timing & Profiling: Best Practices

- All new menus and submenus must use the `time_and_record_menu_load` utility from `utils/monitoring.py` to time and record menu loads.
- Use the `lazy_action()` and `lazy_menu()` helpers to ensure lazy imports and proper timing.
- Timing prints must use the Catppuccin Mocha color scheme for consistency and clarity.
- Do not print raw analytics logs to the console; only user-facing timing prints should be shown.
- Ensure that "Back" and "Exit" options do not trigger timing prints or errors.
- Document any new timing/profiling features in the appropriate docs/ files and README_full.md.

## Robust Menu Loop Pattern (Required)

- All menus and submenus must use the robust menu loop pattern:
  - Get the user's choice (key) from `show_menu`.
  - Look up the action in the options dictionary.
  - Call the action if callable.
- This is required for reliability and maintainability.
- Always use the Catppuccin Mocha color scheme for menu headers and prompts.
- Integrate timing/profiling as described in the relevant sections.

## CBIR Code Style

- Follow modular design: separate menu (cbir_menu.py) and actions (cbir_actions.py)
- Use robust error handling and logging for all file operations
- Integrate memory management (memory_context, auto_cleanup)
- Use parallel processing (smart_map, batch_map) for efficiency
- Provide clear user feedback and progress tracking

## Test Code Style & Best Practices

- Use pytest for all automated tests.
- Use fixtures for temp files, directories, and configs.
- Use monkeypatching/mocking for audio, error feedback, and subprocesses.
- Ensure tests are robust on Windows (file locks, Unicode, etc.).
- Add tests for new features and bugfixes.
- See [advanced.md](advanced.md#test-suite--best-practices) for more.

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


# Contributing

> **All code contributions must follow the [Style Guide](style_guide.md).**

(Include the full "Contributing" and "Development Guidelines" sections from the original README here, preserving formatting and navigation.)

---


# Faq


# Frequently Asked Questions (FAQ)

(If there are not enough FAQs in the original README, leave this as a stub for future expansion.)

### What is CBIR for Duplicates?

CBIR (Content-Based Image Retrieval) for Duplicates uses deep learning models (CLIP, ResNet, VGG) to find images that are semantically similar, even if they look different at the pixel level. It extracts feature embeddings, computes similarity, and groups duplicates for easy management.

---


# License


# License

This project is licensed under the Creative Commons CC-BY-SA-4.0. See the [LICENSE](../LICENSE) file for details.

---
