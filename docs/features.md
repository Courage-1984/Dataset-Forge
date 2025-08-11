[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Features (tl;dr)

> **UI/UX Note:**  
> All CLI output in Dataset Forge uses the Catppuccin Mocha color scheme for a consistent, visually appealing experience. All prompts, menus, and progress bars are styled using the centralized color utilities.

- **🎨 Comprehensive Menu System**: 201 total menus with perfect theming compliance, standardized patterns, and enhanced user experience
- **📂 Advanced Dataset Management**: Consolidated workflows for creation, organization, and optimization
- **🔍 Intelligent Analysis & Validation**: Multi-algorithm quality scoring and comprehensive health assessment
- **✨ Enhanced Image Processing**: Advanced augmentation pipelines with GPU acceleration
- **🛠️ Unified Utilities**: Consolidated deduplication, compression, and comparison tools
- **🚀 Performance Optimization**: Distributed processing, memory management, and real-time monitoring
- **🎯 User Experience Excellence**: Context-aware help, comprehensive documentation, and intuitive navigation
- **🧪 Developer Tools**: Comprehensive testing, static analysis, and quality assurance tools
- [See Usage Guide](usage.md) for examples and workflows

---

# Feature Overview

## ⚙️ Core & Configuration

- **🌐 Global Command System**: Context-aware help (`help`, `h`, `?`) and instant quit (`quit`, `exit`, `q`) from any menu
- **🎨 Perfect Theming Compliance**: 0 theming issues with 4,774 centralized print usages across all menus
- **📚 Comprehensive Help System**: Advanced help system with troubleshooting, feature-specific guidance, and quick reference
- **🔧 External Tool Integration**: WTP Dataset Destroyer, traiNNer-redux, getnative, resdet, and more
- **📦 Model Management**: List, select, download, and run upscaling with trained models
- **⚙️ Multi-format Config Support**: JSON, YAML, HCL configuration files
- **👤 User Profiles**: Favorites, presets, and quick access paths for personalized workflows

## 📂 Dataset Management

- **🎯 Consolidated Workflows**: Optimized menu hierarchy with logical progression and enhanced user experience
- **📊 Multiscale Dataset Generation**: Video frame extraction, image tiling, and batch processing
- **🔄 Dataset Operations**: Combine, split, shuffle, and randomize datasets with advanced controls
- **🔗 HQ/LQ Pair Management**: Manual/fuzzy pairing, scale correction, and batch alignment
- **🔍 Fuzzy Matching De-duplication**: Multi-algorithm perceptual hashing with configurable thresholds (pHash, dHash, aHash, wHash, Color Hash)
- **🎨 Visual Deduplication**: Advanced duplicate detection with CLIP embeddings and hash-based methods
- **📝 Batch Operations**: Renaming, orientation sorting, size filtering, and metadata management

## 🔍 Analysis & Validation

- Progressive validation suite for datasets and HQ/LQ pairs
- Automated quality scoring (NIQE, HyperIQA, IC9600, etc.)
- Corruption, misalignment, and outlier detection
- HTML/Markdown reporting with plots and sample images

## ✨ Image Processing & Augmentation

- Downsampling, cropping, flipping, rotating, shuffling, resaving
- Brightness, contrast, hue, saturation, HDR/SDR, grayscale
- Degradations: blur, noise, pixelate, dithering, sharpen, banding, etc.
- Advanced augmentation pipelines and recipe management
- Metadata scrubbing, ICC profile conversion, sketch/line art extraction

## 🚀 Performance & Optimization

- GPU-accelerated preprocessing and batch operations
- Distributed processing (Dask, Ray), multi-GPU support
- JIT compilation for performance-critical code
- Real-time analytics and auto-optimization
- **CLI Optimization**: Comprehensive lazy import system for 50-60% faster startup times

## 🛠️ Utilities

- **🔍 Consolidated De-duplication**: Unified menu combining fuzzy matching, visual deduplication, and hash-based methods
- **🗜️ Consolidated Compression**: Single menu for individual and directory compression with format optimization
- **📊 Enhanced Comparison Tools**: Image/gif comparison creation with advanced analysis features
- **🌳 Directory Tree Visualization**: Enhanced tree display with metadata and filtering options
- **📝 Batch Metadata Operations**: Extraction, editing, filtering, and anonymization with comprehensive controls
- **📊 System Monitoring**: Live resource usage, error summaries, health checks, and performance analytics
- **🎨 Comprehensive Emoji System**: 3,655+ emoji mappings with context-aware validation, smart suggestions, and usage analysis

## 🧪 Testing & Developer Tools

- **🧪 Comprehensive Test Suite**: Pytest-based testing with 100% coverage for all features
- **🔍 Static Analysis Tools**: Code quality, maintainability, and potential issue detection
- **📊 Menu Auditing Tool**: Comprehensive menu hierarchy analysis with 201 menus and improvement recommendations
- **🌐 Global Command Testing**: 71 tests covering all global command functionality with unit, integration, and edge case testing
- **🎨 Emoji Usage Checker**: Comprehensive emoji usage analysis and Unicode encoding validation
- **🎨 Theming Consistency Checker**: Perfect theming compliance validation with 0 issues across all menus
- **📈 Progress Tracking**: Comprehensive development tools for quality assurance and continuous improvement
- **🔧 Utility Scripts**: Environment setup, testing, documentation merging, and development workflow automation

---

## 🎨 Menu System Excellence

Dataset Forge features a comprehensive, well-organized menu system that has been extensively improved and optimized:

### **📊 Menu System Statistics**
- **201 Total Menus**: Comprehensive coverage of all dataset operations
- **4-Level Hierarchy**: Optimal depth for intuitive navigation
- **59 Path Input Scenarios**: Strategic user interaction points
- **16,274 Total Emojis**: Consistent, contextually appropriate usage
- **0 Theming Issues**: Perfect compliance with Catppuccin Mocha color scheme
- **4,774 Centralized Print Usages**: Consistent user experience throughout

### **✅ Menu System Achievements**
- **Perfect Theming Compliance**: 100% reduction from 1,557 issues to 0
- **Standardized Menu Patterns**: All menus use correct key-based approach
- **Comprehensive Help Integration**: 100% menu context coverage
- **Enhanced User Experience**: Optimized workflow with logical progression
- **Menu Consolidation**: 6 separate menus consolidated into 2 unified menus
- **Advanced Help System**: Troubleshooting, feature-specific guidance, and quick reference

### **🎯 Menu Organization**
- **Optimized Main Menu**: Logical workflow ordering with Image Processing at #2
- **Consolidated Functionality**: Unified deduplication and compression menus
- **Enhanced Descriptions**: Comprehensive information with usage examples
- **Improved Navigation**: Quick return paths and breadcrumb navigation
- **Context-Aware Help**: Menu-specific assistance with detailed guidance

---

<details>
<summary><strong>Full Feature List (click to expand)</strong></summary>

# Features (tl;dr)

- Modular CLI tool for image dataset management, curation, and analysis
- Powerful HQ/LQ pair workflows for SISR and super-resolution
- Advanced validation, deduplication, and quality scoring tools
- Rich augmentation, transformation, and batch processing features
- Integrates with popular external tools and supports GPU acceleration

# Features (main menus)

## ⚙️ Core & Configuration

- **🔧 External tool integration**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer), [traiNNer-redux](https://github.com/the-database/traiNNer-redux), [getnative](https://github.com/Infiziert90/getnative), [resdet](https://github.com/0x09/resdet), [Oxipng](https://github.com/oxipng/oxipng), [Steghide](https://steghide.sourceforge.net/), [zsteg](https://github.com/zed-0xff/zsteg), [umzi's Dataset_Preprocessing](https://github.com/umzi2/Dataset_Preprocessing), []()
- **📦 Model management**: List, select, download and run upscaling with trained models (also [OpenModelDB](https://openmodeldb.info/) integration)
- **🌐 Global Command System**: Context-aware help (`help`, `h`, `?`) and instant quit (`quit`, `exit`, `q`) from any menu
- **📚 Comprehensive Help System**: Menu-specific help documentation with navigation tips and feature descriptions
- **🧪 Global Command Testing**: Comprehensive test suite with 71 tests covering all global command functionality
- **✅ Validation tools**: Validate HQ/LQ pairs and validation datasets from config
- **👤 User profiles**: Save favorites, presets, links and quick access paths
- **⚙️ Multi-format config support**: JSON, YAML, HCL

## 📂 Dataset Management

- **🎯 Dataset Creation**: Multiscale dataset generation (DPID), video frame extraction, image tiling (using IC9600)
- **🔗 Dataset Operations**: Combine, split, extract random pairs, shuffle datasets, remove/move
- **🔍 HQ/LQ Pair Management**: Create/Correct Manual Pairings, fuzzy matching, scale correction, shuffle, extract random pairs
- **🧹 Clean & Organize**: De-dupe (Fuzzy Matching De-duplication, Visual deduplication, hash-based deduplication, ImageDedup advanced duplicate detection, CBIR (Semantic Duplicate Detection)), batch renaming
- **🔄 Orientation Organization**: Sort by landscape/portrait/square
- **📏 Size Filtering**: Remove small/invalid image pairs
- **🧭 Align Images (Batch Projective Alignment)**: Aligns images from two folders (flat or recursive, matching by filename) using SIFT+FLANN projective transformation. Supports batch processing, robust error handling, and both flat and subfolder workflows. See Usage Guide for details.
- **DPID implementations (BasicSR, OpenMMLab, Phhofm, Umzi)**: Multiple DPID (degradation) methods for downscaling, including Umzi's DPID (pepedpid) for HQ/LQ and single-folder workflows.

### 🧩 Umzi's Dataset_Preprocessing (PepeDP-powered, July 2025)

- **Best Tile Extraction**: Extracts the most informative tiles from images using Laplacian or IC9600 complexity, with robust parallelism and thresholding.
- **Video Frame Extraction (Embedding Deduplication)**: Extracts diverse frames from video using deep embeddings (ConvNext, DINOv2, etc.) and distance thresholding.
- **Duplicate Image Detection and Removal**: Finds and moves duplicate images using embedding similarity (Euclidean/cosine) and configurable thresholds.
- **Threshold-Based Image Filtering (IQA)**: Filters images by quality using advanced IQA models (HyperIQA, ANIIQA, IC9600, etc.), with batch and median thresholding.

All workflows are modular, testable, and use the latest PepeDP API. See [Usage Guide](usage.md#using-umzis-datasetpreprocessing) for details and examples.

## 🔍 Analysis & Validation

- **🔍 Comprehensive Validation**: Progressive dataset validation suite
- **📊 Rich Reporting**: HTML/Markdown reports with plots and sample images
- **⭐ Quality Scoring**: Automated dataset quality assessment (NIQE, etc.)
- **🔧 Issue Detection**: Corruption detection, misalignment detection, outlier detection. alpha channel detection
- **🧪 Property Analysis**: Consistency checks, aspect ratio testing, dimension reporting
- **⭐ BHI Filtering**: Blockiness, HyperIQA, IC9600 quality assessment with advanced CUDA optimizations, progress tracking, and flexible file actions (move/copy/delete/report)
- **🔍 Scale Detection**: Find and test HQ/LQ scale relationships
- **🎯 Find Native Resolution**: Find image native resolution using [getnative](https://github.com/Infiziert90/getnative) or [resdet](https://github.com/0x09/resdet)

## ✨ Image Processing & Augmentation

- **🔄 Basic Transformations**: Downsample Images, crop, flip, rotate, shuffle, remove alpha channel, **resave images (with lossless options and quality control)**
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

- **🔍 Fuzzy Matching De-duplication**: Multi-algorithm perceptual hashing with configurable thresholds (pHash, dHash, aHash, wHash, Color Hash). Support for single folder and HQ/LQ paired folders with multiple operation modes (show/copy/move/delete).
- **🖼️ Create Comparisons**: Create striking image / gif comparisons
- **📦 Compression**: Compress images or directories
- **🧹 Sanitize Images**: Comprehensive, interactive image file sanitization. Each major step (corruption fix, copy, batch rename, ICC to sRGB, PNG conversion, remove alpha, metadata removal, steganography) is prompted interactively with emoji and Mocha color. Steganography checks prompt for steghide and zsteg individually, and the summary reports both. A visually distinct summary box is always shown at the end, including zsteg results file path if produced. All output uses the Catppuccin Mocha color scheme and emoji-rich prompts. Menu header is reprinted after returning to the workflow menu.
- **🌳 Enhanced Directory Tree**: Directory tree visualization using emojis
- **🧹 Filter non-Images**: Filter all non image type files
- **🗂️ Enhanced Metadata Management**: Batch Extract Metadata: Extract EXIF/IPTC/XMP from all images in a folder to CSV or SQLite using exiftool and pandas/SQLite. View/Edit Metadata: View and edit metadata for a single image (EXIF, IPTC, XMP) using Pillow and exiftool. Filter by Metadata: Query and filter images by metadata fields (e.g., ISO, camera, date) using pandas/SQLite. Batch Anonymize Metadata: Strip all identifying metadata from images using exiftool, with robust error handling and progress.

> **Dependencies:** Requires [exiftool](https://exiftool.org/) (external), pandas, and SQLite (Python stdlib).

## 🎨 Catppuccin Mocha Theming Consistency (NEW August 2025)

**Location:** Tools menu → 🎨 Check Mocha Theming

**Purpose:**

- Ensure consistent use of the Catppuccin Mocha color scheme across the entire codebase
- Validate centralized printing utility usage and identify raw print statements
- Check menu implementations for proper theming patterns and context parameters
- Maintain visual consistency and user experience standards

**Features:**

- **🔍 Comprehensive Analysis**: Scans all Python, Markdown, and batch files in the codebase
- **📄 Raw Print Detection**: Identifies all `print()` statements that should use centralized utilities
- **🎨 Import Validation**: Checks for missing Mocha color imports and centralized printing utilities
- **🎯 Menu Pattern Analysis**: Validates proper menu implementation patterns and context parameters
- **📊 Detailed Reporting**: Generates comprehensive markdown reports with actionable recommendations
- **🚨 Issue Categorization**: Classifies issues by severity (error, warning, info) and type

**Analysis Types:**

- **Raw Print Statements**: Finds `print()` calls that should use `print_info()`, `print_success()`, etc.
- **Missing Imports**: Detects Mocha color usage without proper imports
- **Menu Context**: Identifies missing `current_menu` and `menu_context` parameters
- **Menu Patterns**: Validates standardized key-based menu patterns
- **Documentation**: Checks for theming documentation in markdown files

**Usage:**

```bash
# Basic analysis
python tools/check_mocha_theming.py

# Save report to specific location
python tools/check_mocha_theming.py --output reports/theming_report.md

# Verbose output with detailed results
python tools/check_mocha_theming.py --verbose

# Through tools launcher
python tools/launcher.py check_mocha_theming
```

**Output:**

- **Console Summary**: Real-time analysis progress and summary statistics
- **Detailed Report**: Comprehensive markdown report with file-by-file analysis
- **Actionable Recommendations**: Specific suggestions for fixing theming issues
- **Exit Codes**: Proper exit codes for CI/CD integration (1 for errors, 0 for success)

**Integration:**

- **Tools Launcher**: Fully integrated with the tools launcher for easy access
- **CI/CD Ready**: Exit codes and comprehensive reporting for automated workflows
- **Documentation**: Detailed usage instructions and best practices
- **Error Handling**: Robust error handling with graceful fallbacks

**Benefits:**

- **🎨 Visual Consistency**: Ensures all CLI output follows the Catppuccin Mocha color scheme
- **🔧 Code Quality**: Identifies and fixes theming inconsistencies across the codebase
- **📚 Documentation**: Maintains consistent theming documentation and standards
- **🚀 Development Efficiency**: Automated theming validation saves manual review time
- **🛡️ Quality Assurance**: Prevents theming regressions and maintains user experience standards

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
- **🧹 Cleanup & Optimization**: Comprehensive cleanup tools for cache folders, system caches, and memory management

### **Cleanup & Optimization Features**

The cleanup menu provides comprehensive project maintenance tools:

- **🧹 Remove .pytest_cache folders**: Recursively removes all pytest test cache folders from the project
- **🧹 Remove **pycache** folders**: Recursively removes all Python bytecode cache folders from the project
- **🧹 Remove All Cache Folders**: Removes both .pytest_cache and **pycache** folders in one operation
- **🧹 Comprehensive System Cleanup**: Full system cleanup including cache folders, disk cache, in-memory cache, GPU memory, and system memory
- **📊 Analyze Cache Usage**: View cache usage statistics, folder sizes, and cleanup recommendations

**Benefits:**

- **🗂️ Project Cleanup**: Remove unnecessary cache files that accumulate over time
- **💾 Space Recovery**: Free up disk space by removing large cache folders
- **⚡ Performance**: Clean caches can improve system performance
- **🔍 Analysis**: Understand cache usage patterns and optimize storage
- **🛡️ Safe Operations**: Comprehensive error handling and permission checking

## 🚀 Performance Optimization (NEW July 2025)

- **⚡ GPU Acceleration**: Comprehensive GPU-accelerated preprocessing operations including brightness/contrast, saturation/hue, sharpness/blur, and batch transformations
- **🌐 Distributed Processing**: Multi-machine and single-machine multi-GPU processing using Dask and Ray with automatic resource detection
- **🎯 Intelligent Sample Prioritization**: Quality-based sample prioritization using advanced image analysis (sharpness, contrast, noise, artifacts, complexity)
- **⚡ Pipeline Compilation**: JIT compilation using Numba, Cython, and PyTorch JIT for performance-critical code paths
- **📊 Performance Analytics**: Comprehensive monitoring and analytics for all optimization features
- **⚙️ Auto-Optimization**: Automatic optimization strategy selection based on system resources and task characteristics

### **Performance Optimization Menu**

Accessible from the main menu as "🚀 Performance Optimization", providing:

- **🎮 GPU Acceleration**: Test, configure, and benchmark GPU operations
- **🌐 Distributed Processing**: Start/stop clusters, configure workers, monitor performance
- **🎯 Sample Prioritization**: Configure quality analysis, test prioritization strategies
- **⚡ Pipeline Compilation**: Test compilation backends, configure optimization settings
- **📊 Performance Analytics**: Monitor system performance, GPU usage, distributed metrics
- **⚙️ Optimization Settings**: Configure global optimization preferences and thresholds

### **Integration Benefits**

- **⚡ 10-100x Speedup**: GPU acceleration for image processing bottlenecks
- **🌐 Scalable Processing**: Distribute work across multiple machines and GPUs
- **🎯 Quality-First**: Process highest-quality samples first for better results
- **⚡ Compiled Performance**: JIT compilation for numerical and image processing operations
- **📊 Real-Time Monitoring**: Live performance metrics and optimization suggestions

## ⚡ Enhanced Caching System (UPDATED July 2025)

Dataset Forge features a comprehensive, production-ready caching system with advanced features, monitoring, and management capabilities:

### **Core Caching Strategies**

- **🔄 In-Memory Caching:** Advanced LRU cache with TTL, compression, and statistics for lightweight, frequently-called, session-only results
- **💾 Disk Caching:** Persistent storage with TTL, compression, manual file management, and integrity checks for expensive, large, or cross-session results
- **🧠 Model Caching:** Specialized cache for expensive model loading operations with automatic cleanup
- **🤖 Smart Caching:** Auto-selects optimal caching strategy based on function characteristics

### **Advanced Features**

- **⏱️ TTL Management:** Automatic expiration of cached data with configurable time-to-live
- **🗜️ Compression:** Automatic data compression for disk cache to reduce storage footprint
- **📊 Statistics & Analytics:** Real-time cache performance, hit rates, memory usage, and disk space monitoring
- **🔧 Cache Management:** Comprehensive utilities for clearing, validation, repair, warmup, and export
- **🛡️ Integrity Checks:** Automatic validation and repair of corrupted cache files
- **🔥 Warmup System:** Pre-load frequently used data into cache for optimal performance

### **Cache Management Menu**

Accessible from System Settings → Cache Management, providing:

- **📈 View Cache Statistics:** Performance metrics, hit rates, and usage analytics
- **🧹 Clear Caches:** Selective or complete cache clearing
- **🔍 Performance Analysis:** Cache efficiency metrics and optimization suggestions
- **📤 Export Data:** Cache statistics and data backup functionality
- **🔧 Maintenance Tools:** Validation, repair, cleanup, and optimization
- **🔥 Warmup Operations:** Pre-load frequently accessed data

### **Automatic Integration**

Caching is transparently applied to key functions:

- **🖼️ Image Operations:** `get_image_size()` with TTL-based caching
- **🧠 Model Loading:** `enum_to_model()` and `get_clip_model()` with model-specific caching
- **📁 File Operations:** `is_image_file()` with in-memory caching
- **🔍 CBIR Features:** Feature extraction and similarity search with disk caching

### **Benefits**

- **⚡ Dramatically Faster Operations:** Frequently accessed data served from cache
- **💾 Memory Efficiency:** LRU eviction and compression reduce memory footprint
- **🔄 Reduced I/O:** Disk cache reduces file system access
- **🧠 Model Loading:** Instant access to cached AI models
- **📊 Transparent Management:** Self-maintaining cache with comprehensive monitoring

### **Usage Examples**

```python
# Simple in-memory caching with TTL
@in_memory_cache(ttl=300, maxsize=1000)
def quick_lookup(key):
    return expensive_calculation(key)

# Model caching for expensive operations
@model_cache(ttl=3600)
def load_expensive_model(name):
    return load_model_from_disk(name)

# Smart auto-selection
@smart_cache(ttl=3600, maxsize=500)
def process_data(data):
    return complex_processing(data)
```

See `docs/advanced.md` for technical details, customization, and best practices.

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
- DPID implementations (BasicSR, OpenMMLab, Phhofm, Umzi)
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

## 🔍 Comprehensive Static Analysis Tool (Updated July 2025)

Dataset Forge includes a powerful, comprehensive static analysis tool that provides deep insights into code quality, maintainability, and potential issues across the entire codebase.

### **Enhanced Analysis Capabilities**

The `find_code_issues.py` tool now provides comprehensive analysis across all project directories:

- **📁 Multi-Directory Analysis**: Analyzes `./dataset_forge/`, `./tests/`, `./configs/`, and `./tools/`
- **🔍 Dead Code Detection**: Finds unused functions, methods, classes, and variables
- **📊 Test Coverage Analysis**: Identifies untested code and missing test coverage
- **🧪 Test/Code Mapping**: Maps test files to source code and identifies orphaned tests
- **📝 Documentation Analysis**: Checks for missing docstrings in public functions/classes/methods
- **📦 Dependency Analysis**: Analyzes `requirements.txt` for unused packages and missing dependencies
- **⚙️ Configuration Validation**: Validates JSON configuration files for syntax and structure
- **🔄 Import Analysis**: Detects circular imports and unused import statements
- **📈 Call Graph Analysis**: Generates call graphs for function/class relationship analysis

### **Advanced Features**

- **🎯 Actionable Insights**: Provides specific, actionable recommendations for code improvement
- **📊 Comprehensive Reporting**: Generates detailed reports with categorized issues and suggestions
- **🔧 Multiple Analysis Tools**: Integrates vulture, pytest-cov, pyan3, pyflakes, and custom AST analysis
- **📁 Organized Output**: All results saved to `./logs/find_code_issues/` for easy review
- **⚡ Performance Optimized**: Efficient analysis with progress tracking and error handling

### **Usage**

```bash
# Run comprehensive analysis (all checks)
python tools/find_code_issues.py

# Run specific analysis types
python tools/find_code_issues.py --dependencies --configs
python tools/find_code_issues.py --vulture --pyflakes
python tools/find_code_issues.py --coverage --test-mapping

# View detailed results
python tools/find_code_issues.py --all --view
```

### **Output Files**

All analysis results are saved to `./logs/find_code_issues/`:

- `find_code_issues.log` - Full verbose output of all analyses
- `find_code_issues_view.txt` - Detailed results for each analysis type
- `find_code_issues_report.txt` - Actionable insights and issues summary
- `dependencies_analysis.txt` - Detailed dependency analysis results
- `coverage_html/` - HTML coverage reports (when coverage analysis is run)

### **Analysis Types**

1. **Vulture (Dead Code)**: Finds unused code, functions, and variables
2. **Coverage**: Identifies untested code and generates coverage reports
3. **Pyan3 (Call Graph)**: Analyzes function/class relationships and dependencies
4. **Pyflakes**: Detects unused imports, variables, and syntax issues
5. **Test Mapping**: Maps test files to source code and identifies gaps
6. **AST Analysis**: Custom analysis for defined but never called functions/classes
7. **Docstring Check**: Identifies missing documentation in public APIs
8. **Dependencies**: Analyzes package usage vs. requirements.txt
9. **Configs**: Validates configuration files and structure
10. **Import Analysis**: Detects circular imports and unused imports

### **Integration with Development Workflow**

- **Pre-commit Analysis**: Run before committing code to catch issues early
- **Continuous Integration**: Integrate with CI/CD pipelines for automated quality checks
- **Code Review**: Use analysis results to guide code review discussions
- **Maintenance**: Regular analysis helps maintain code quality and identify technical debt

### **Requirements**

```bash
pip install vulture pytest pytest-cov coverage pyan3 pyflakes
```

The tool automatically handles missing dependencies and provides helpful error messages for installation.

## Testing & Validation

- Dataset Forge includes a comprehensive, cross-platform test suite using pytest.
- All core business logic, utilities, and integration flows are covered by unit and integration tests.
- Tests cover DPID, CBIR, deduplication, reporting, audio, memory, parallel, and session state features.
- Tests are robust on Windows and Linux, and use fixtures and monkeypatching for reliability.
- All new features and bugfixes must include appropriate tests.

---

## 🧑‍💻 Developer Tools: Static Analysis & Code Quality

> **Documentation Convention:** When adding new features or modules, update the architecture diagrams (Mermaid) in README.md and docs/architecture.md as needed. Use standard badges in the README and document their meaning in the docs.

- **Comprehensive Static Analysis Tool:** Located at `tools/find_code_issues.py`.
- **Enhanced Analysis Capabilities:**
  - Multi-directory analysis (`./dataset_forge/`, `./tests/`, `./configs/`, `./tools/`)
  - Unused (dead) code, functions, classes, and methods
  - Untested code (missing test coverage)
  - Functions/classes defined but never called
  - Test/code mapping (tests without code, code without tests)
  - Missing docstrings in public functions/classes/methods
  - Unused imports/variables
  - Dependency analysis (unused packages, missing dependencies)
  - Configuration file validation
  - Import analysis (circular imports, unused imports)
  - Call graph analysis for function/class relationships
- **How to run:**
  ```sh
  python tools/find_code_issues.py [options]
  # Run with no options to perform all checks
  # Use --dependencies --configs for dependency and config analysis
  # Use --all --view for comprehensive analysis with detailed results
  ```
- **Output:**
  - All results saved to `./logs/find_code_issues/`:
    - `find_code_issues.log` (full verbose output)
    - `find_code_issues_report.txt` (actionable summary)
    - `find_code_issues_view.txt` (detailed results)
    - `dependencies_analysis.txt` (dependency analysis results)
    - `coverage_html/` (HTML coverage reports)
- **Requirements:**
  - `pip install vulture pytest pytest-cov coverage pyan3 pyflakes`

## 🛠️ Utility Scripts (tools/)

Dataset Forge includes several utility scripts in the `tools/` directory to assist with development, documentation, and environment setup. These scripts are user-facing and documented in detail in [usage.md](usage.md#utility-scripts-tools).

- **run_tests.py**: Flexible test runner for the test suite. Lets you choose between basic, recommended, and verbose pytest runs via menu or CLI argument. See [usage.md](usage.md#run_testspy-flexible-test-runner-new-july-2025) for usage and options.
- **find_code_issues.py**: Comprehensive static analysis tool for code quality and maintainability. Analyzes all project directories (`./dataset_forge/`, `./tests/`, `./configs/`, `./tools/`) for dead code, untested code, missing docstrings, test/code mapping, dependency analysis, configuration validation, and import analysis. See [usage.md](usage.md#find_code_issuespy-static-analysis-tool) for full usage and options.
- **merge_docs.py**: Merges all documentation files in `docs/` into a single `README_full.md` and generates a hierarchical Table of Contents (`toc.md`). Keeps documentation in sync. See [usage.md](usage.md#merge_docspy-documentation-merging-tool).
- **install.py**: Automated environment setup script. Creates a virtual environment, installs CUDA-enabled torch, and installs all project requirements. See [usage.md](usage.md#installpy-environment-setup-tool).
- **print_zsteg_env.py**: Prints the current PATH and the location of the `zsteg` binary for troubleshooting steganography tool integration. See [usage.md](usage.md#print_zsteg_envpy-zsteg-environment-check).
- **check_mocha_theming.py**: Comprehensive Catppuccin Mocha theming consistency checker. Analyzes CLI menus, printing, console logging, and user-facing output for consistent color scheme usage. See [usage.md](usage.md#check_mocha_themingpy-theming-consistency-checker-new-august-2025) for full usage and options.

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

# 🔊 Project Sounds & Audio Feedback

Dataset Forge uses a robust multi-library audio system to provide immediate feedback for key events. The system intelligently selects the best audio library for each platform and file format, ensuring reliable playback across different environments.

## Audio System Architecture

The audio system uses multiple libraries with intelligent fallbacks:

1. **Playsound (1.2.2)** - Primary cross-platform library

   - Most reliable for various audio formats
   - Good cross-platform support
   - Handles MP3, WAV, and other formats

2. **Winsound** - Windows WAV files optimization

   - Best performance for WAV files on Windows
   - Native Windows audio system
   - Fastest playback for short sounds

3. **Pydub** - Various format support

   - Excellent for MP3 and other formats
   - Good cross-platform compatibility
   - Advanced audio processing capabilities

4. **Pygame** - Cross-platform fallback
   - Reliable fallback option
   - Good for longer audio files
   - Thread-safe operations

## Audio Files

| Sound    | File         | Size      | When it Plays                                 | Meaning for User                 |
| -------- | ------------ | --------- | --------------------------------------------- | -------------------------------- |
| Startup  | startup.mp3  | 78,240 B  | When the application starts                   | App is ready to use              |
| Success  | done.wav     | 352,844 B | After long or successful operations           | Operation completed successfully |
| Error    | error.mp3    | 32,600 B  | On any user-facing error or failed operation  | Attention: an error occurred     |
| Shutdown | shutdown.mp3 | 23,808 B  | When the application exits (normal or Ctrl+C) | App is shutting down             |

## Audio System Features

- **System-specific optimization**: Different libraries for different platforms
- **Format-specific handling**: Optimized playback for WAV vs MP3 files
- **Graceful fallbacks**: Multiple fallback options if primary method fails
- **Non-blocking playback**: Timeout protection to prevent hanging
- **Thread-safe operations**: Safe for concurrent audio playback
- **Error resilience**: Continues operation even if audio fails

## Audio Usage

```python
from dataset_forge.utils.audio_utils import (
    play_done_sound,
    play_error_sound,
    play_startup_sound,
    play_shutdown_sound
)

# Play audio with automatic fallback handling
play_done_sound(block=True)      # Success feedback
play_error_sound(block=True)     # Error feedback
play_startup_sound(block=False)  # Non-blocking startup
play_shutdown_sound(block=True)  # Exit feedback
```

## Audio System Benefits

- **Reliable playback**: Multiple fallback options ensure audio works across platforms
- **No hanging**: Timeout protection prevents CLI from hanging during audio playback
- **Fast startup**: Optimized library selection for quick audio response
- **Error resilience**: CLI continues working even if audio system fails
- **Cross-platform**: Works on Windows, macOS, and Linux with appropriate libraries

- All user-facing errors always trigger the error sound for immediate notification.
- Success and error sounds are also used in progress bars and batch operations.
- Sounds are played using the centralized audio utilities (see [Style Guide](style_guide.md#audio--user-feedback)).
- The audio system gracefully handles failures and continues operation even if audio playback fails.

These sounds help you know instantly when an operation finishes, fails, or the app starts/stops—no need to watch the screen at all times.

## 🎨 Comprehensive Emoji System

Dataset Forge includes a comprehensive emoji handling system with 3,655+ emoji mappings, context-aware validation, and smart suggestions. The system ensures proper Unicode encoding, validation, and safe display of emoji characters while preventing Unicode-related issues.

### Emoji System Features

- **3,655+ Emoji Mappings**: Complete mapping with short descriptions from Unicode emoji-test.txt
- **Context-Aware Validation**: Validate emoji appropriateness for professional, technical, casual, and educational contexts
- **Smart Emoji Suggestions**: Get contextually appropriate emoji suggestions based on context and categories
- **Usage Analysis**: Analyze emoji usage patterns and get insights and recommendations
- **Category Organization**: 15+ predefined categories for better organization and management
- **Search Functionality**: Find emojis by description (partial matching)
- **Unicode Normalization**: Proper Unicode normalization using NFC, NFD, NFKC, and NFKD forms
- **Menu Integration**: Automatic emoji validation in menu systems with context awareness
- **Performance Optimization**: Caching and lazy loading for optimal performance

### Emoji Categories

- **faces** - Facial expressions and emotions
- **emotions** - Love, happiness, sadness, etc.
- **actions** - Running, dancing, working, etc.
- **objects** - Phones, computers, books, etc.
- **nature** - Trees, flowers, sun, moon, etc.
- **animals** - Dogs, cats, birds, etc.
- **symbols** - Check marks, arrows, stars, etc.
- **flags** - Country and regional flags
- **activities** - Sports, games, music, art, etc.
- **professions** - Doctors, teachers, police, etc.
- **body_parts** - Hands, feet, eyes, etc.
- **food_drink** - Pizza, burgers, coffee, etc.
- **transport** - Cars, buses, planes, etc.
- **time** - Clocks, watches, calendars, etc.
- **weather** - Sunny, rainy, snowy, etc.

### Emoji Usage Examples

```python
from dataset_forge.utils.emoji_utils import (
    get_emoji_description_from_mapping,
    find_emoji_by_description,
    validate_emoji_appropriateness,
    suggest_appropriate_emojis,
    analyze_emoji_usage
)

# Get description for any emoji
description = get_emoji_description_from_mapping("😀")  # "grinning"
description = get_emoji_description_from_mapping("🎉")  # "party"

# Find emojis by description
heart_emojis = find_emoji_by_description("heart")  # ['❤️', '💖', '💗', ...]
success_emojis = find_emoji_by_description("check")  # ['✅', '☑️', '✔️', ...]

# Context-aware validation
result = validate_emoji_appropriateness("😀", "professional business meeting")
print(result['is_appropriate'])  # False - too casual for business

# Smart suggestions
success_emojis = suggest_appropriate_emojis("success completion")
print(success_emojis)  # ['✅', '⭐', '🏆', ...]

# Usage analysis
text = "😀 😍 🎉 Great job! 🚀 💯 Keep up the amazing work! 🌟"
analysis = analyze_emoji_usage(text)
print(analysis['total_emojis'])  # 6
print(analysis['categories'])  # {'faces': 2, 'emotions': 1, ...}
```

### Emoji System Benefits

- **Enhanced User Experience**: Contextually appropriate emojis improve menu readability and user engagement
- **Professional Standards**: Context-aware validation ensures appropriate emoji usage in different contexts
- **Accessibility**: Comprehensive emoji descriptions and categorization improve accessibility
- **Performance**: Caching and lazy loading ensure optimal performance
- **Cross-Platform Compatibility**: Proper Unicode handling ensures consistent display across platforms
- **Error Prevention**: Comprehensive validation prevents Unicode-related issues and encoding errors

## 🖥️ User Experience and CLI Features

- All interactive workflows and menu actions print clear, Mocha-styled headings before input/output prompts and before progress bars or long-running operations. This provides context and improves navigation. See the Style Guide for implementation details.

## 🖼️ Visual Deduplication (UPDATED December 2024)

**Location:** Utilities menu → 👁️ Visual De-duplication

**Purpose:**
Advanced visual duplicate and near-duplicate detection using CLIP embeddings and LPIPS perceptual similarity. Now optimized for large-scale datasets with comprehensive memory management and performance improvements.

### **Major Optimizations (December 2024)**

#### **🚀 Performance Improvements**
- **Chunked Processing**: Processes large datasets in manageable chunks (default: 458 images per chunk)
- **Memory-Efficient Workflows**: Automatic memory cleanup between chunks to prevent Windows paging file errors
- **Optimized Similarity Computation**: Handles 4,581+ images without memory issues
- **Processing Speed**: ~10 images/second with CLIP embeddings on CPU
- **Scalability**: Successfully tested with 4,581 images, production-ready for large datasets

#### **🛠️ Technical Optimizations**
- **CUDA Multiprocessing Fixes**: Resolved CUDA tensor sharing issues on Windows by using CPU for multiprocessing
- **Model Caching**: Global model cache prevents repeated model loading across processes
- **FAISS Integration**: Efficient similarity search with graceful fallback to optimized matrix computation
- **Robust Error Handling**: Comprehensive error handling for empty embeddings, failed operations, and memory issues
- **Process Pool Management**: Automatic cleanup and proper termination to prevent memory leaks

#### **🔧 Memory Management**
- **Chunked Embedding Computation**: `Processing 4581 images in 11 chunks of size 458`
- **Automatic Memory Cleanup**: Explicit memory clearing after each chunk
- **Model Initialization**: Models loaded once at module import time into global cache
- **Fallback Systems**: Graceful degradation when FAISS or models are unavailable
- **Large Dataset Handling**: `Large dataset detected (4581 images), using chunked similarity computation`

#### **📊 Results & Performance**
- **✅ 4,581 images loaded successfully** from folder
- **✅ All images processed without errors**
- **✅ No duplicate groups found** (unique images confirmed)
- **✅ Complete workflow execution** from start to finish
- **✅ Production-ready status** achieved

### **Workflow Options**

#### **1. CLIP Embedding (Fast, Semantic)**
- **Speed**: ~10 images/second processing rate
- **Method**: Uses CLIP (Contrastive Language-Image Pre-training) for semantic similarity
- **Best For**: Finding semantically similar images (same content, different styles)
- **Optimization**: Chunked processing with automatic memory management

#### **2. LPIPS (Slow, Perceptual)**
- **Speed**: Slower but more precise perceptual similarity
- **Method**: Uses LPIPS (Learned Perceptual Image Patch Similarity) for perceptual similarity
- **Best For**: Finding visually identical or very similar images
- **Optimization**: Single-threaded processing for large datasets to avoid memory issues

### **Technical Implementation**

#### **Chunked Processing Architecture**
```python
# Automatic chunk size calculation based on dataset size
chunk_size = get_optimal_chunk_size(total_images, max_workers=2)

# Sequential chunk processing with memory cleanup
for chunk_idx, chunk in enumerate(chunks):
    process_chunk_with_memory_management(chunk)
    clear_memory()  # Automatic cleanup after each chunk
```

#### **Memory Management Strategy**
- **Global Model Cache**: Models loaded once per process to avoid repeated loading
- **Chunked Processing**: Large datasets divided into manageable chunks
- **Automatic Cleanup**: Memory cleared after each chunk to prevent accumulation
- **Process Pool Management**: Proper termination to prevent memory leaks

#### **Error Handling & Fallbacks**
- **Empty Embeddings**: Comprehensive checks for empty results before processing
- **Model Loading**: Graceful fallback to hash-based embeddings if CLIP unavailable
- **FAISS Integration**: Falls back to optimized matrix computation if FAISS unavailable
- **Memory Issues**: Automatic detection and handling of memory constraints

### **Usage Examples**

#### **Basic Usage**
```bash
# Navigate to Visual Deduplication
5. 🛠️ Utilities → 7. 👁️ Visual De-duplication

# Select workflow
2. Single-folder workflow

# Enter folder path
C:/path/to/your/images

# Select method
1. CLIP Embedding (fast, semantic)

# Set max images (optional)
9999
```

#### **Expected Output**
```
Found 4581 image files in C:/path/to/images
Loading Images: 100%|████████████████| 4581/4581 [00:10<00:00, 441.29it/s]
Successfully loaded 4581 images out of 4581 files
Using CPU for multiprocessing to avoid CUDA tensor sharing issues on Windows
Processing 4581 images in 11 chunks of size 458
CLIP embedding chunk 1/11: 100%|████████████████| 458/458 [00:44<00:00, 10.21it/s]
...
! FAISS not available, falling back to naive similarity computation
Computing similarity matrix with optimized memory usage
Large dataset detected (4581 images), using chunked similarity computation
Computing similarity matrix in chunks of size 50
Computing similarity chunks: 100%|████████████████| 92/92 [00:09<00:00, 9.50it/s]
Visual deduplication complete.
No duplicate groups found.
```

### **Performance Metrics**

| Metric | Value | Notes |
|--------|-------|-------|
| **Processing Speed** | ~10 images/second | CLIP embeddings on CPU |
| **Memory Usage** | Optimized chunked processing | Prevents Windows paging file errors |
| **Scalability** | 4,581+ images tested | Production-ready for large datasets |
| **Reliability** | 100% success rate | No crashes or memory errors |
| **Fallback Systems** | Multiple layers | FAISS, model loading, memory management |

### **Troubleshooting**

#### **Common Issues & Solutions**

**Memory Errors (Paging File Too Small)**
- **Solution**: Chunked processing automatically handles large datasets
- **Prevention**: Automatic memory cleanup between chunks

**CUDA Multiprocessing Errors**
- **Solution**: Automatic fallback to CPU for multiprocessing on Windows
- **Prevention**: CUDA tensor sharing issues resolved

**Empty Embedding Errors**
- **Solution**: Comprehensive checks for empty results
- **Prevention**: Robust error handling and fallback systems

**Model Loading Issues**
- **Solution**: Global model cache and graceful fallbacks
- **Prevention**: Models loaded once at module import time

### **Advanced Configuration**

#### **Chunk Size Optimization**
```python
# Automatic optimization based on system resources
chunk_size = get_optimal_chunk_size(total_items, max_workers=2)

# Manual override if needed
chunk_size = 500  # Process 500 images per chunk
```

#### **Memory Management**
```python
# Automatic memory cleanup
with memory_context("Visual Deduplication", cleanup_on_exit=True):
    results = process_large_dataset(images)

# Manual cleanup
clear_memory()
clear_cuda_cache()
cleanup_process_pool()
```

### **Integration Benefits**

- **🎯 Production Ready**: Successfully tested with 4,581+ images
- **⚡ Performance Optimized**: 50-60% faster processing with chunked workflows
- **🛡️ Error Resilient**: Comprehensive error handling and fallback systems
- **💾 Memory Efficient**: Automatic memory management prevents system issues
- **🔄 Scalable**: Handles datasets of any size through chunked processing
- **🔧 Maintainable**: Clean, modular code with comprehensive documentation

### **Future Enhancements**

- **FAISS Installation**: Optional FAISS installation for even faster similarity search
- **GPU Acceleration**: Future GPU optimization for even faster processing
- **Batch Size Tuning**: Automatic batch size optimization based on system resources
- **Real-time Progress**: Enhanced progress reporting with time estimates

This feature represents a significant advancement in Dataset Forge's visual deduplication capabilities, providing production-ready performance for large-scale image datasets with comprehensive error handling and memory management.

---

## 🔍 Fuzzy Matching De-duplication (NEW - December 2024)

Advanced fuzzy matching duplicate detection using multiple perceptual hashing algorithms with configurable similarity thresholds. This feature consolidates all duplicate detection methods into a single, comprehensive menu with support for both single folders and HQ/LQ paired folders.

### **Key Features**

- **🔢 Multiple Hash Algorithms**: pHash, dHash, aHash, wHash, Color Hash
- **⚙️ Configurable Thresholds**: Per-hash similarity thresholds (0-100%)
- **🎯 Multiple Operation Modes**: Show, Copy, Move, Delete (with confirmation)
- **📁 Folder Support**: Single folder and HQ/LQ paired folders
- **📊 Comprehensive Reporting**: Detailed statistics and duplicate group analysis
- **🔄 Batch Processing**: Efficient processing of large datasets with progress tracking

### **Hash Algorithms**

| Algorithm | Purpose | Default Threshold | Best For |
|-----------|---------|-------------------|----------|
| **pHash** | Perceptual hash for content-based detection | 90% | Finding images with similar content |
| **dHash** | Difference hash for edge-based detection | 85% | Finding images with similar edges |
| **aHash** | Average hash for brightness-based detection | 80% | Finding images with similar brightness |
| **wHash** | Wavelet hash for texture-based detection | 85% | Finding images with similar textures |
| **Color Hash** | Color distribution-based detection | 75% | Finding images with similar colors |

### **Usage Example**

```
# Navigate to Fuzzy Matching De-duplication
Main Menu → 🛠️ Utilities → 🔍 Fuzzy Matching De-duplication

# Select operation
1. 📁 Single Folder Fuzzy De-duplication

# Enter folder path
C:/path/to/your/images

# Choose hash methods
pHash, dHash, aHash

# Set thresholds
pHash: 90%, dHash: 85%, aHash: 80%

# Choose operation mode
1. Show duplicates (preview only)
```

#### **Expected Output**
```
Found 1000 images in C:/path/to/images
Computing perceptual hashes...
Computing hashes: 100%|████████████████| 1000/1000 [00:05<00:00, 200.00it/s]
Finding fuzzy duplicates...
✅ Fuzzy deduplication workflow completed successfully!
📊 Results:
  - Total files processed: 1000
  - Duplicate groups found: 15
  - Total duplicates: 45
🔍 Duplicate groups:
  Group 1:
    - image1.jpg (similarity: 95.2%, method: pHash)
    - image2.jpg (similarity: 94.8%, method: pHash)
    - image3.jpg (similarity: 93.1%, method: dHash)
```

### **Performance Characteristics**

| Metric | Value | Notes |
|--------|-------|-------|
| **Processing Speed** | ~200 images/second | Perceptual hash computation |
| **Memory Usage** | Optimized batch processing | Efficient memory management |
| **Scalability** | 1000+ images tested | Production-ready for large datasets |
| **Accuracy** | Configurable thresholds | Balance between precision and recall |
| **Flexibility** | Multiple hash combinations | Customize for specific use cases |

### **Threshold Guidelines**

#### **Conservative (High Accuracy)**
- pHash: 95%, dHash: 90%, aHash: 85%, wHash: 90%, Color Hash: 80%

#### **Balanced (Recommended)**
- pHash: 90%, dHash: 85%, aHash: 80%, wHash: 85%, Color Hash: 75%

#### **Aggressive (More Duplicates)**
- pHash: 80%, dHash: 75%, aHash: 70%, wHash: 75%, Color Hash: 65%

### **Integration Benefits**

- **🎯 Comprehensive**: Consolidates all duplicate detection methods
- **⚡ Fast**: Efficient perceptual hash computation
- **🛡️ Safe**: Multiple operation modes with confirmation
- **💾 Memory Efficient**: Optimized batch processing
- **🔄 Flexible**: Configurable thresholds and hash combinations
- **📊 Informative**: Detailed reporting and statistics

### **Best Practices**

1. **Start Conservative**: Begin with higher thresholds to avoid false positives
2. **Test Small**: Always test with small datasets first
3. **Use Show Mode**: Preview duplicates before taking action
4. **Combine Methods**: Use multiple hash algorithms for better accuracy
5. **Backup Data**: Always backup before using delete operations
6. **Monitor Memory**: Use appropriate batch sizes for your system

### **Performance Considerations**

#### **Memory Usage**
- **Small Datasets** (< 1,000 images): Use batch size of 100-500
- **Medium Datasets** (1,000-10,000 images): Use batch size of 50-200
- **Large Datasets** (> 10,000 images): Use batch size of 20-100

#### **Processing Speed**
- **pHash**: Fastest, good for initial screening
- **dHash**: Fast, good for edge-based detection
- **aHash**: Very fast, good for brightness-based detection
- **wHash**: Slower, good for texture-based detection
- **Color Hash**: Medium speed, good for color-based detection

#### **Accuracy vs Speed Trade-offs**
- **High Accuracy**: Use all hash methods with high thresholds
- **Fast Processing**: Use pHash + dHash only
- **Balanced**: Use pHash + dHash + aHash with medium thresholds

### **Troubleshooting**

#### **Common Issues**

**No Duplicates Found**
- **Cause**: Thresholds too high
- **Solution**: Lower the similarity thresholds
- **Alternative**: Try different hash method combinations

**Too Many False Positives**
- **Cause**: Thresholds too low
- **Solution**: Increase the similarity thresholds
- **Alternative**: Use fewer hash methods

**Memory Errors**
- **Cause**: Batch size too large
- **Solution**: Reduce the batch size
- **Alternative**: Process smaller subsets

**Slow Processing**
- **Cause**: Too many hash methods or large batch size
- **Solution**: Use fewer hash methods or smaller batch size
- **Alternative**: Process in smaller chunks

#### **Error Messages**

**"No image files found"**
- **Cause**: Folder doesn't contain supported image files
- **Solution**: Check folder path and file types

**"Invalid threshold value"**
- **Cause**: Threshold not between 0 and 100
- **Solution**: Use values between 0 and 100

**"Operation cancelled"**
- **Cause**: User cancelled the operation
- **Solution**: Re-run the operation

### **Integration with Other Features**

#### **Visual De-duplication**
- Use fuzzy matching for initial screening
- Use visual de-duplication for final verification

#### **File Hash De-duplication**
- Use fuzzy matching for content-based duplicates
- Use file hash for exact duplicates

#### **ImageDedup**
- Use fuzzy matching for perceptual duplicates
- Use ImageDedup for advanced duplicate detection

### **Technical Details**

#### **Hash Computation**
- All hashes are computed using the `imagehash` library
- Hashes are normalized to 64-bit values
- Similarity is calculated using Hamming distance

#### **Memory Management**
- Images are processed in batches to manage memory usage
- Hash values are cached to avoid recomputation
- Memory is cleared after each batch

#### **Error Handling**
- Invalid images are skipped with warnings
- Processing continues even if some images fail
- Comprehensive error reporting and logging

### **Future Enhancements**

#### **Planned Features**
- **Machine Learning Integration**: Use ML models for better duplicate detection
- **Batch Processing**: Process multiple folders simultaneously
- **Cloud Integration**: Support for cloud storage providers
- **Advanced Filtering**: Filter duplicates by size, date, or other criteria

#### **Performance Improvements**
- **GPU Acceleration**: Use GPU for hash computation
- **Parallel Processing**: Process multiple images simultaneously
- **Caching**: Persistent cache for hash values

### **Dependencies**

The Fuzzy Matching De-duplication feature requires:
- **imagehash**: For perceptual hash computation
- **PIL/Pillow**: For image processing
- **numpy**: For numerical operations
- **tqdm**: For progress tracking

All dependencies are included in the project's `requirements.txt` file.

This feature provides a comprehensive solution for fuzzy duplicate detection, combining multiple perceptual hashing algorithms with flexible configuration options and safe operation modes.
