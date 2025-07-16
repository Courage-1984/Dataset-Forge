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

## Advanced: Modular Integration of Umzi's Dataset_Preprocessing

The original Dataset_Preprocessing_consolidated_script.py has been fully ported into Dataset Forge as a modular, maintainable set of actions and menu files:

- All business logic is in `dataset_forge/actions/umzi_dataset_preprocessing_actions.py`, following project conventions for memory management, progress tracking, and error handling.
- The menu interface is in `dataset_forge/menus/umzi_dataset_preprocessing_menu.py`, using lazy imports and the robust menu loop pattern.
- All workflows are testable, with comprehensive unit and CLI integration tests.
- The codebase uses Google-style docstrings, type hints, and follows the modular architecture described in `docs/architecture.md`.
- This integration demonstrates how to port monolithic scripts into the Dataset Forge ecosystem for maintainability and testability.

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
