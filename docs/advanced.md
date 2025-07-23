[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

> **Note:** Architecture diagrams in this documentation use Mermaid code blocks. No Python package is required; diagrams are rendered by supported Markdown viewers (e.g., GitHub, VSCode with Mermaid extension).
>
> **Badges:** Standard badges (build, license, Python version, etc.) are included in the README. See the README for their meaning.

# Advanced Features & Configuration

This document covers advanced usage, configuration, and developer patterns for Dataset Forge. For user-facing features, see [features.md](features.md).

---

## Advanced Configuration

- **Custom config files**: Use JSON, YAML, or HCL for advanced workflows.
- **Integration with external tools**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer), [traiNNer-redux](https://github.com/the-database/traiNNer-redux), [getnative](https://github.com/Infiziert90/getnative), [resdet](https://github.com/0x09/resdet)
- **Batch processing and memory optimization**: Tune batch sizes and memory settings in the config files for large datasets.
- **OpenModelDB integration**: Advanced model management and upscaling workflows.

## Advanced Monitoring & Analytics

- **Add new analytics hooks**: Decorate new actions with `@monitor_performance` and `@track_errors`.
- **Background task management**: Register new subprocesses/threads for monitoring.
- **Persistent logging**: Ensure all analytics and errors are logged to ./logs/.

---

For user workflows and feature summaries, see [features.md](features.md). For code style and requirements, see [style_guide.md](style_guide.md).

## Robust Menu Loop Pattern (July 2025)

All Dataset Forge menus now use a robust menu loop pattern to ensure reliability and maintainability. This pattern ensures that:

- The user's menu selection (key) is always used to look up the corresponding action in the options dictionary.
- Only callable actions are executed; if the action is not callable, a clear error is printed.
- Debug prints for both the selected key and resolved action are included for easier debugging.

**Pattern Example:**

```python
while True:
    key = show_menu("Menu Title", options, ...)
    print(f"DEBUG: key={key!r}, type={type(key)}")
    if key is None or key == "0":
        break
    action = options.get(key, (None, None))[1]
    print(f"DEBUG: action={action!r}, type={type(action)}")
    if callable(action):
        action()
    else:
        print_error(f"Selected action is not callable: {action!r} (type={type(action)})")
```

**Why this matters:**

- Prevents menu loops from breaking if the user input is not mapped to a callable.
- Ensures all menu actions are robust to user error and code changes.
- Makes debugging easier by providing clear output for both valid and invalid selections.

**Enforcement:**

- As of July 2025, all menus in Dataset Forge have been updated to use this pattern.
- If you add a new menu, you must use this pattern for consistency and reliability.

## Advanced Testing Patterns

- The test suite uses pytest fixtures and monkeypatching to isolate tests and mock external dependencies (audio, file I/O, heavy computation).
- To add tests for new features, create a new test file in tests/test_utils/ or tests/ as appropriate.
- All new features and bugfixes must include appropriate tests.

---

## 🧑‍💻 Advanced Developer Tools: Static Analysis

Dataset Forge includes a comprehensive static analysis tool for code quality and maintainability:

- **Script:** `tools/find_code_issues/find_code_issues.py`
- **Tools used:** vulture, pytest-cov, coverage, pyan3, pyflakes, ast
- **Checks performed:**
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
- **Extending:**
  - The script is modular and can be extended to add new static analysis checks or output formats. See the script for extension points.
- **Requirements:**
  - `pip install vulture pytest pytest-cov coverage pyan3 pyflakes`

Review the actionable report and detailed results before submitting code or documentation changes.

## 🛠️ Advanced: Utility Scripts (tools/)

### Extending find_code_issues.py

- The static analysis tool is modular and can be extended to add new checks or output formats.
- To add a new analysis, define a new function and add it to the main() dispatcher.
- Output files are overwritten on each run; see the script for extension points.
- Review the actionable report and detailed results before submitting code or documentation changes.

### Extending merge_docs.py

- The documentation merging tool uses a configurable DOC_ORDER list to determine which files to merge and in what order.
- To add a new documentation file, update DOC_ORDER and ensure navigation links are consistent.
- The script parses headings to build a hierarchical Table of Contents.

### Adding New Utility Scripts

- All new user-facing scripts in tools/ must be documented in features.md and usage.md, and kept up to date.
- Add troubleshooting entries for new scripts in troubleshooting.md as needed.

## ⚡ Enhanced Caching System: Technical Details (UPDATED July 2025)

Dataset Forge implements a comprehensive, production-ready caching system with advanced features, monitoring, and management capabilities.

### **Core Architecture**

The caching system is built around four main components:

1. **AdvancedLRUCache Class:** Thread-safe, feature-rich in-memory cache with TTL, compression, and statistics
2. **Disk Cache:** Persistent storage using joblib.Memory with enhanced file management
3. **Model Cache:** Specialized cache for expensive model loading operations
4. **Smart Cache:** Auto-detection system that chooses optimal caching strategy

### **In-Memory Caching (AdvancedLRUCache)**

**Features:**

- Thread-safe LRU eviction with configurable max size
- Time-to-live (TTL) support with automatic expiration
- Data compression for memory efficiency
- Comprehensive statistics tracking (hits, misses, memory usage)
- Sentinel-based cache miss detection (handles None values correctly)

**Implementation:**

```python
from dataset_forge.utils.cache_utils import in_memory_cache

@in_memory_cache(maxsize=1000, ttl_seconds=3600, compression=True)
def expensive_calculation(data):
    return complex_processing(data)
```

**Key Features:**

- **Thread Safety:** Uses threading.Lock for concurrent access
- **Memory Monitoring:** Tracks cache size and memory usage
- **Compression:** Optional gzip compression for large objects
- **Statistics:** Hit/miss rates, memory usage, eviction counts

### **Disk Caching**

**Features:**

- Persistent storage across sessions
- TTL-based expiration
- Automatic compression
- File integrity validation
- Manual file management capabilities

**Implementation:**

```python
from dataset_forge.utils.cache_utils import disk_cache

@disk_cache(ttl_seconds=86400, compression=True, cache_dir="custom/path")
def expensive_feature_extraction(image_path):
    return extract_deep_features(image_path)
```

**Key Features:**

- **Persistent Storage:** Survives application restarts
- **File Management:** Automatic cleanup of expired files
- **Compression:** Reduces disk space usage
- **Integrity Checks:** Validates cached files on access

### **Model Caching**

**Features:**

- Specialized for expensive model loading operations
- Automatic CUDA memory management
- Statistics tracking for model operations
- Optimized for large, memory-intensive objects

**Implementation:**

```python
from dataset_forge.utils.cache_utils import model_cache

@model_cache(maxsize=5, ttl_seconds=7200)
def load_ai_model(model_name):
    return load_pretrained_model(model_name)
```

### **Smart Caching**

**Auto-Detection Logic:**

- **Model Cache:** Functions with "model", "load", "embedding" in name
- **Disk Cache:** Functions with "extract", "compute", "process" in name
- **In-Memory Cache:** All other functions

**Implementation:**

```python
from dataset_forge.utils.cache_utils import smart_cache

@smart_cache(ttl_seconds=3600, maxsize=500, compression=True)
def process_image_data(image_path):
    # Automatically selects optimal caching strategy
    return process_image(image_path)
```

### **Cache Management System**

**Comprehensive Management Menu:**

- **Statistics Viewing:** Real-time performance metrics
- **Cache Clearing:** Selective or complete cache clearing
- **Performance Analysis:** Efficiency metrics and optimization suggestions
- **Data Export:** Cache statistics and backup functionality
- **Maintenance Tools:** Validation, repair, cleanup, optimization
- **Warmup Operations:** Pre-load frequently accessed data

**Programmatic Management:**

```python
from dataset_forge.utils.cache_utils import (
    clear_all_caches, get_cache_stats, validate_cache,
    repair_cache, warmup_cache, export_cache_stats
)

# Clear all caches
clear_all_caches()

# Get comprehensive statistics
stats = get_cache_stats()

# Validate and repair cache integrity
validate_cache()
repair_cache()

# Warmup frequently used data
warmup_cache(['frequently_used_function'])

# Export statistics
export_cache_stats('cache_report.json')
```

### **Advanced Features**

**TTL Management:**

- Configurable time-to-live for all cache types
- Automatic cleanup of expired entries
- Different TTL strategies for different data types

**Compression:**

- Automatic gzip compression for disk cache
- Memory-efficient compression for in-memory cache
- Configurable compression levels

**Statistics & Analytics:**

- Real-time hit/miss rates
- Memory usage tracking
- Disk space monitoring
- Performance metrics

**Integrity & Maintenance:**

- Automatic validation of cached files
- Repair of corrupted cache entries
- Cleanup of orphaned cache files
- Optimization of cache performance

### **Integration with Existing Functions**

The enhanced caching system is automatically applied to key functions:

```python
# Image operations with TTL-based caching
@in_memory_cache(ttl_seconds=300, maxsize=1000)
def get_image_size(image_path):
    # Cached for 5 minutes with max 1000 entries
    pass

# Model loading with specialized caching
@model_cache(ttl_seconds=3600, maxsize=10)
def enum_to_model(model_enum):
    # Cached for 1 hour with max 10 models
    pass

# File operations with in-memory caching
@in_memory_cache(maxsize=5000)
def is_image_file(filename):
    # Frequently called, cached in memory
    pass
```

### **Best Practices**

**When to Use Each Cache Type:**

- **In-Memory Cache:** Small, frequently accessed data, session-only results
- **Disk Cache:** Large, expensive computations, cross-session persistence
- **Model Cache:** AI model loading, GPU memory management
- **Smart Cache:** Let the system choose based on function characteristics

**Performance Optimization:**

- Set appropriate TTL values based on data volatility
- Use compression for large objects
- Monitor cache statistics for optimization opportunities
- Implement cache warmup for critical data

**Memory Management:**

- Set reasonable maxsize limits for in-memory caches
- Use TTL to prevent memory leaks
- Monitor memory usage with cache statistics
- Clear caches when memory pressure is high

### **Troubleshooting**

**Common Issues:**

- **Cache Misses:** Check TTL settings and cache size limits
- **Memory Issues:** Monitor cache statistics and adjust maxsize
- **Disk Space:** Use compression and regular cleanup
- **Performance:** Analyze hit rates and optimize cache strategy

**Debug Tools:**

- Cache statistics provide detailed performance metrics
- Validation tools detect and repair cache corruption
- Export functionality for offline analysis

See `docs/features.md` for user-facing information and `README_full.md` for a comprehensive overview.

## Advanced: Modular Integration of Umzi's Dataset_Preprocessing (PepeDP-powered, July 2025)

The original Dataset_Preprocessing_consolidated_script.py has been fully ported into Dataset Forge as a modular, maintainable set of actions and menu files, now powered by PepeDP:

- All business logic is in `dataset_forge/actions/umzi_dataset_preprocessing_actions.py` as thin wrappers around PepeDP classes/functions. All user inputs are overridable via function arguments for robust, non-interactive testing.
- The menu interface is in `dataset_forge/menus/umzi_dataset_preprocessing_menu.py`, using lazy imports and the robust menu loop pattern.
- All four main workflows (Best Tile Extraction, Video Frame Extraction, Duplicate Detection, IQA Filtering) are testable, with comprehensive unit and CLI integration tests. All tests call the action functions with arguments to bypass prompts.
- The codebase uses Google-style docstrings, type hints, and follows the modular architecture described in `docs/architecture.md`.
- This integration demonstrates how to port monolithic scripts into the Dataset Forge ecosystem for maintainability, testability, and robust documentation.

## Advanced: Performance Optimization Suite (NEW July 2025t Forge implements a comprehensive performance optimization suite designed for maximum efficiency in image dataset processing. This suite provides GPU acceleration, distributed processing, intelligent sample prioritization, and pipeline compilation capabilities.

### **Core Architecture**

The performance optimization suite is built around four main components:

1. **GPU Acceleration:** PyTorch-based image processing with automatic device management
2. **Distributed Processing:** Dask and Ray integration for scalable computing
3. **Sample Prioritization:** Quality-based processing order optimization
   4peline Compilation:\*\* JIT compilation for performance-critical code paths

### **GPU Acceleration (dataset_forge/utils/gpu_acceleration.py)**

**Features:**

- GPU-accelerated image preprocessing operations (brightness/contrast, saturation/hue, sharpness/blur)
- Automatic device detection and memory management
- Batch transformation support with PyTorch/TorchVision
- GPU image analysis and SIFT keypoint detection
- Cached operations with TTL and compression

**Implementation:**

```python
from dataset_forge.utils.gpu_acceleration import GPUImageProcessor, gpu_brightness_contrast

# GPU-accelerated image transformations
result = gpu_brightness_contrast(image, brightness=1.2, contrast=1.1)

# Batch processing
processor = GPUImageProcessor()
results = processor.gpu_batch_transform(images, transform_config)

# GPU image analysis
analysis = processor.gpu_image_analysis(image)
```

**Key Features:**

- **Device Management:** Automatic CUDA detection and memory cleanup
- **Batch Processing:** Efficient processing of large image batches
- **Memory Optimization:** Automatic tensor management and cleanup
- **Caching:** TTL-based caching for expensive operations

### **Distributed Processing (dataset_forge/utils/distributed_processing.py)**

**Features:**

- Multi-machine and single-machine multi-GPU processing
- Dask and Ray integration with automatic resource detection
- Auto-detection of optimal processing mode and worker count
- Cluster management with dashboard and monitoring
- Batch processing with progress tracking and error handling

**Implementation:**

```python
from dataset_forge.utils.distributed_processing import distributed_map, start_distributed_processing

# Start distributed processing
start_distributed_processing()

# Process items with distributed computing
results = distributed_map(process_function, items, desc="Processing")

# Multi-GPU processing
from dataset_forge.utils.distributed_processing import multi_gpu_map
results = multi_gpu_map(process_function, items, desc="Multi-GPU Processing")
```

**Key Features:**

- **Auto-Detection:** Automatically detects available resources and optimal configuration
- **Fallback Support:** Graceful fallback to local processing when distributed resources unavailable
- **Error Handling:** Robust error aggregation and reporting
- **Progress Tracking:** Real-time progress monitoring with descriptive messages

### **Sample Prioritization (dataset_forge/utils/sample_prioritization.py)**

**Features:**

- Quality-based sample prioritization using advanced image analysis
- Sharpness, contrast, noise, artifact, and complexity analysis
- Hybrid scoring with configurable weights
- Adaptive batch creation based on priority scores
- Extensible analysis framework

**Implementation:**

```python
from dataset_forge.utils.sample_prioritization import prioritize_samples, PrioritizationStrategy

# Prioritize samples by quality
prioritized = prioritize_samples(image_paths, strategy=PrioritizationStrategy.QUALITY_SCORE)

# Analyze image quality
from dataset_forge.utils.sample_prioritization import QualityAnalyzer
analyzer = QualityAnalyzer()
quality_metrics = analyzer.analyze_quality(image_path)
```

**Key Features:**

- **Quality Analysis:** Comprehensive image quality assessment
- **Complexity Analysis:** Edge density, texture complexity, color variety analysis
- **Configurable Weights:** Adjustable importance of different quality metrics
- **Adaptive Batching:** Intelligent batch creation based on priority scores

### **Pipeline Compilation (dataset_forge/utils/pipeline_compilation.py)**

**Features:**

- JIT compilation using Numba, Cython, and PyTorch JIT
- Auto-detection of optimal compilation strategy
- Decorator-based compilation with fallback support
- Pre-compiled utility functions for common operations
- Compilation status monitoring and management

**Implementation:**

```python
from dataset_forge.utils.pipeline_compilation import compile_function, auto_compile, CompilationType

# Manual compilation
compiled_func = compile_function(original_func)
result = compiled_func(data)

# Auto-compilation decorator
@auto_compile(CompilationType.AUTO)
def process_data(data):
    return complex_processing(data)
```

**Key Features:**

- **Multi-Backend Support:** Numba, Cython, and PyTorch JIT compilation
- **Auto-Detection:** Automatically selects optimal compilation strategy
- **Fallback Support:** Graceful fallback when compilation fails
- **Performance Monitoring:** Compilation time and performance tracking

### **Performance Optimization Menu**

The Performance Optimization menu provides a centralized interface for all optimization features:

- **GPU Acceleration:** Test, configure, and benchmark GPU operations
- **Distributed Processing:** Start/stop clusters, configure workers, monitor performance
- **Sample Prioritization:** Configure quality analysis, test prioritization strategies
- **Pipeline Compilation:** Test compilation backends, configure optimization settings
- **Performance Analytics:** Monitor system performance, GPU usage, distributed metrics
- **Optimization Settings:** Configure global optimization preferences and thresholds

### **Integration Patterns**

**Combining Optimization Strategies:**

```python
# End-to-end optimized pipeline
from dataset_forge.utils.sample_prioritization import prioritize_samples
from dataset_forge.utils.gpu_acceleration import gpu_batch_transform
from dataset_forge.utils.distributed_processing import distributed_map
from dataset_forge.utils.pipeline_compilation import compile_function

# 1. Prioritize samples by quality
prioritized_samples = prioritize_samples(image_paths)

# 2. Process with GPU acceleration
def process_batch(batch):
    return gpu_batch_transform(batch, transform_config)

# 3. Compile the processing function
compiled_process = compile_function(process_batch)

# 4. Distribute processing across multiple machines/GPUs
results = distributed_map(compiled_process, prioritized_samples, desc="Optimized Processing")
```

**Performance Monitoring:**

- Real-time performance metrics and optimization suggestions
- GPU usage monitoring and memory management
- Distributed processing cluster status and health
- Compilation performance tracking and optimization

### **Best Practices**

**GPU Acceleration:**

- Use batch processing for maximum GPU utilization
- Monitor memory usage and implement proper cleanup
- Cache expensive operations with appropriate TTL
- Handle device availability gracefully

**Distributed Processing:**

- Start with local processing and scale up as needed
- Monitor cluster health and resource utilization
- Implement robust error handling and recovery
- Use appropriate batch sizes for your workload

**Sample Prioritization:**

- Configure quality weights based on your specific use case
- Use hybrid scoring for balanced quality and complexity
- Implement adaptive batching for optimal resource utilization
- Monitor prioritization effectiveness and adjust strategies

**Pipeline Compilation:**

- Use auto-compilation for automatic optimization
- Monitor compilation time and performance gains
- Implement fallback mechanisms for compilation failures
- Profile and optimize performance-critical code paths

### **Troubleshooting**

**Common Issues:**

- **GPU Memory Issues:** Monitor memory usage and implement proper cleanup
- **Distributed Processing Failures:** Check cluster health and resource availability
- **Compilation Failures:** Verify dependencies and use fallback mechanisms
- **Performance Degradation:** Monitor metrics and adjust optimization strategies

**Debug Tools:**

- Performance analytics provide detailed optimization metrics
- GPU monitoring tools for memory and utilization tracking
- Distributed processing dashboard for cluster health monitoring
- Compilation status monitoring for optimization effectiveness

See `docs/features.md` for user-facing information and `README_full.md` for a comprehensive overview.

## Interactive Workflow Prompt Handling (July 2025)

- The sanitize images workflow now handles all step prompts interactively within the workflow function, not in the menu.
- Steganography checks prompt for steghide and zsteg individually, and the summary reports both sub-choices.
- The summary box is always shown at the end, listing all steps (run/skipped) and the zsteg results file path if produced.
- The menu header is reprinted after returning to the workflow menu.
- All output uses centralized, Mocha-styled printing utilities and emoji-rich prompts.
- No duplicate prompts or debug prints remain.
- This pattern is now the standard for all interactive workflows in Dataset Forge.

## 🗂️ Enhanced Metadata Management (NEW July 2025)

- **Technical Details:**
  - Uses exiftool for robust, cross-format metadata extraction, editing, and anonymization (supports EXIF, IPTC, XMP, and more).
  - Batch extract uses exiftool's -csv or -j (JSON) output, loaded into pandas for CSV/SQLite export and filtering.
  - View/Edit uses Pillow for simple EXIF and exiftool for advanced/other tags.
  - Filtering leverages pandas' query syntax for flexible, powerful queries.
  - Batch anonymization uses exiftool with -all= and -overwrite_original, with progress and error handling.
- **Rationale:**
  - exiftool is the industry standard for metadata, supporting more tags and formats than any Python library alone.
  - pandas/SQLite provide scalable, scriptable analysis and filtering.
- **Extensibility:**
  - Future support for batch editing, IPTC/XMP-specific workflows, and advanced search/export is planned.
- **Integration:**
  - All actions use centralized printing, memory, progress, and logging utilities.
  - Robust error handling and user feedback throughout.

## 🧪 Advanced Test Design Patterns (July 2025)

- All tests use monkeypatching and dummy objects to isolate logic and avoid external dependencies.
- Multiprocessing tests require worker functions to be at module level for pickling compatibility.
- All new features must include robust, non-interactive tests using the public API.
- Public APIs are required for all major features to ensure testability and programmatic access.

See [Style Guide](style_guide.md#testing-patterns) and [features.md](features.md#comprehensive-test-suite) for more.

## Align Images: Advanced Options (Planned)

- The Align Images workflow is modular and robust, supporting both flat and recursive batch processing.
- Advanced options (e.g., number of SIFT matches, FLANN parameters) are planned for future releases.
- The implementation is fully testable and covered by non-interactive tests using feature-rich dummy images.

## DPID Modular Integration (July 2025)

Dataset Forge supports multiple DPID (degradation) methods for downscaling images, including:

- BasicSR DPID
- OpenMMLab DPID
- Phhofm DPID (pepedpid)
- **Umzi DPID (pepedpid)**

All DPID implementations are modular, live in `dataset_forge/dpid/`, and are exposed via public APIs for both single-folder and HQ/LQ paired workflows. Umzi's DPID is implemented in `umzi_dpid.py` and can be selected in all DPID menus. The API matches the other DPID modules and uses the same error handling, memory management, and I/O conventions.

**Testing:**
All DPID implementations (including Umzi's) are covered by robust, non-interactive tests using pytest and monkeypatching. Tests validate that output files are created for both single-folder and HQ/LQ workflows, and that the API is reliable and isolated from external dependencies.
