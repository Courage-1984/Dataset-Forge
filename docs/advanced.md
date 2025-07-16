[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

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

## ⚡ Caching System: Technical Details (NEW July 2025)

Dataset Forge uses a hybrid caching system for performance:

- **In-Memory Caching:**

  - Uses `functools.lru_cache` via the `@in_memory_cache` decorator (see `utils/cache_utils.py`).
  - Applied to lightweight, frequently-called functions (e.g., image property analysis, directory scans).
  - Cache is per-session and cleared on process exit or via function-specific calls.

- **Disk Caching:**

  - Uses `joblib.Memory` via the `@disk_cache` decorator (see `utils/cache_utils.py`).
  - Applied to expensive, large-result functions (e.g., CBIR feature extraction).
  - Cache is persistent across sessions and stored in `store/cache/`.
  - Disk cache can be cleared from the System Monitoring menu or by deleting the folder.

- **Cache Management:**

  - Use the System Monitoring menu to clear all caches.
  - Disk cache is auto-ignored by git (see `.gitignore`).

- **How to Use in Your Code:**

  - Import decorators from `dataset_forge.utils.cache_utils`:
    ```python
    from dataset_forge.utils.cache_utils import in_memory_cache, disk_cache
    ```
  - Decorate your function:

    ```python
    @in_memory_cache(maxsize=128)
    def my_func(...):
        ...

    @disk_cache
    def expensive_func(...):
        ...
    ```

  - Use `clear_disk_cache()` and `clear_in_memory_cache(func)` to clear caches programmatically.

- **Best Practices:**
  - Use in-memory cache for small, fast, frequently-repeated operations.
  - Use disk cache for large, expensive, or cross-session results.
  - Always document cache usage in your function docstrings.

See `docs/features.md` for user-facing info and `README_full.md` for a merged overview.

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
