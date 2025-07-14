[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

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
