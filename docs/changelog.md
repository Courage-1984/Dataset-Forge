[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Changelog

## [Unreleased]

### 🧩 PepeDP-powered Umzi's Dataset_Preprocessing Integration (July 2025)

- Replaced all legacy Umzi Dataset_Preprocessing logic with thin, testable wrappers around PepeDP.
- All four main workflows (Best Tile Extraction, Video Frame Extraction, Duplicate Detection, IQA Filtering) now use the latest PepeDP API.
- All workflows are robust, modular, and fully covered by non-interactive, public API tests.
- Updated all relevant documentation, style guide, and .mdc rules.

### 🚀 Performance Optimization Suite (NEW July 2025)

#### **GPU Acceleration**

- **New module:** `dataset_forge/utils/gpu_acceleration.py`
- GPU-accelerated image preprocessing operations (brightness/contrast, saturation/hue, sharpness/blur)
- Batch transformation support with PyTorch/TorchVision
- GPU image analysis and SIFT keypoint detection
- Automatic device detection and memory management
- Cached operations with TTL and compression

#### **Distributed Processing**

- **New module:** `dataset_forge/utils/distributed_processing.py`
- Multi-machine and single-machine multi-GPU processing
- Dask and Ray integration with automatic resource detection
- Auto-detection of optimal processing mode and worker count
- Cluster management with dashboard and monitoring
- Batch processing with progress tracking and error handling

#### **Intelligent Sample Prioritization**

- **New module:** `dataset_forge/utils/sample_prioritization.py`
- Quality-based sample prioritization using advanced image analysis
- Sharpness, contrast, noise, artifact, and complexity analysis
- Hybrid scoring with configurable weights
- Adaptive batch creation based on priority scores
- Extensible analysis framework

#### **Pipeline Compilation**

- **New module:** `dataset_forge/utils/pipeline_compilation.py`
- JIT compilation using Numba, Cython, and PyTorch JIT
- Auto-detection of optimal compilation strategy
- Decorator-based compilation with fallback support
- Pre-compiled utility functions for common operations
- Compilation status monitoring and management

#### **Performance Optimization Menu**

- **New menu:** `dataset_forge/menus/performance_optimization_menu.py`
- Centralized UI for all performance optimization features
- GPU acceleration testing and configuration
- Distributed processing cluster management
- Sample prioritization configuration and testing
- Pipeline compilation testing and settings
- Performance analytics and monitoring
- Global optimization settings

#### **Comprehensive Testing**

- **New test suite:** `tests/test_utils/test_performance_optimization.py`
- Complete coverage of all performance optimization modules
- Integration tests for end-to-end workflows
- Performance benchmarks and memory management checks
- Error handling and edge case testing

#### **Dependencies**

- Added Dask[complete], Ray[default] for distributed processing
- Added Numba, Cython for pipeline compilation
- Added Kornia, Albumentations for GPU acceleration
- All dependencies properly grouped and documented in requirements.txt

### 🔧 Technical Improvements

- Enhanced memory management integration across all optimization features
- Centralized monitoring and analytics for performance tracking
- Robust error handling with graceful fallbacks
- Comprehensive logging and debugging support
- Cross-platform compatibility (Windows, Linux)

### 📚 Documentation

- Updated features.md with comprehensive performance optimization documentation
- Added usage examples and integration guides
- Updated architecture diagrams and technical specifications
- Enhanced troubleshooting guides for optimization features

- **Enhanced Caching System (July 2025):**
  - Completely rewrote and enhanced the caching system from basic implementation to production-ready solution
  - Added AdvancedLRUCache class with TTL, compression, statistics, and thread safety
  - Implemented comprehensive disk caching with integrity checks and file management
  - Added specialized model caching for expensive AI model loading operations
  - Created smart cache decorator with auto-detection of optimal caching strategy
  - Built comprehensive cache management menu with statistics, maintenance, and optimization tools
  - Added cache warmup, validation, repair, and export functionality
  - Integrated caching into key functions: get_image_size, enum_to_model, get_clip_model, is_image_file
  - Created robust test suite covering all caching functionality with 107 passing tests
  - Fixed critical issues: UnboundLocalError in smart_cache, disk cache filename validation, None value handling
  - Updated all documentation to reflect enhanced caching capabilities and best practices
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
- Refactored all DPID logic to use the new modular structure (`dataset_forge.dpid.*`). Legacy imports from `dataset_forge.utils.dpid_phhofm` removed.
- All menus now use the robust menu loop pattern (get key, look up action, call if callable, handle errors).
- All user-facing workflows are responsible for their own 'Press Enter to return to the menu...' prompt. Menu loops no longer include this prompt.
- All output, prompts, and progress messages now use the centralized printing utilities and Catppuccin Mocha color scheme. No raw print statements remain in user-facing workflows.
- Exception handling and debug prints added to menu actions and workflows for easier debugging and error diagnosis.
- Major test suite improvements: added and improved unit/integration tests for DPID, CBIR, deduplication, reporting, utilities, session state, and more.
- All core business logic and utilities now covered by tests.
- Fixed test import errors, function signatures, and monkeypatches for reliability.
- Integrated Umzi's Dataset_Preprocessing as a modular menu and actions set.
- Added Best Tile Extraction, Video Frame Extraction, Image Deduplication, IQA Filtering, and Embedding Extraction workflows.
- All features are fully interactive, testable, and documented.
- Added robust unit and CLI integration tests for all workflows.
- Updated documentation in features.md, usage.md, advanced.md, architecture.md, changelog.md, and .cursorrules.
- Major refactor of the Sanitize Images workflow (July 2025):
  - All step prompts are now interactive, Mocha-styled, and emoji-rich.
  - Steganography checks prompt for steghide and zsteg individually, and the summary reports both.
  - A visually distinct summary box is always shown at the end, including zsteg results file path if produced.
  - Menu header is reprinted after returning to the workflow menu.
  - All output uses centralized, Mocha-styled printing utilities.
  - No duplicate prompts, debug prints, or raw print statements remain.
  - Documentation and .cursorrules updated accordingly.
- **Enhanced Metadata Management:**
  - Added new menu for batch extract, view/edit, filter, and anonymize image metadata (EXIF, IPTC, XMP) using exiftool, Pillow, pandas, and SQLite.
  - Fully integrated with centralized printing, memory, progress, and logging utilities.
  - Documented in all relevant docs and .cursorrules.
- Added '🧭 Align Images (Batch Projective Alignment)' feature to Dataset Management menu. Allows batch alignment of images from two folders (flat or recursive) using SIFT+FLANN projective transformation. Robust error handling, modular implementation, and public API.
- Added robust, non-interactive test for Align Images using feature-rich dummy images to ensure SIFT keypoint detection and alignment.

### 🆕 DPID: Umzi's DPID (pepedpid) Integration (July 2025)

- **New DPID implementation:** Added Umzi's DPID (pepedpid) as a modular DPID method in `dataset_forge/dpid/umzi_dpid.py`.
- **Menu integration:** Umzi's DPID is now selectable in all DPID menus (single-folder and HQ/LQ workflows).
- **Testing:** Comprehensive, non-interactive tests for Umzi's DPID (single-folder and HQ/LQ) using pytest and monkeypatching.
- **Documentation:** Updated all relevant docs and .cursorrules to reflect the new DPID method, its usage, and its test coverage.

## [July 2025]

- Added '🩺 Dataset Health Scoring' workflow and menu option under Dataset Management.
- Supports both single-folder and HQ/LQ parent folder modes.
- Modular, weighted checks: validation, quality, consistency, compliance, and more.
- Actionable suggestions and detailed scoring breakdown.
- Fully covered by unit and integration tests.
- Robust CLI integration and extensible design.
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
- Comprehensive test suite upgrade: all major features now have robust, non-interactive, public APIs and are fully covered by real tests.
- Test suite uses monkeypatching, dummy objects, and multiprocessing-safe patterns.
- Only one test is marked XFAIL (ignore patterns in directory tree), which is expected and documented.
- Documentation updated to reflect new test patterns and requirements.

This file will track major changes and releases in the future.
