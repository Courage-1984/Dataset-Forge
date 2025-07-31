[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Dataset Forge Style Guide

This guide defines the coding standards, architecture, and best practices for Dataset Forge contributors. For user-facing features and workflows, see [features.md](features.md) and [usage.md](usage.md).

---

## General Principles

- **Python 3.12+**. Use modern Python features.
- **PEP 8** style, 4-space indentation, 88-char line length (Black standard).
- **Google-style docstrings** for all public functions/classes.
- **Type hints** for all function parameters and return values.
- **Absolute imports** for all `dataset_forge` modules.
- **Modular design**: UI (menus/), business logic (actions/), utilities (utils/), DPID (dpid/).

## Project Architecture

- Keep UI, logic, and utilities separate.
- Use thin UI layers (menus), business logic in actions, helpers in utils.
- Use lazy imports to keep CLI menu responsive and fast.

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
- Always use lazy imports for all menus.

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
- Use AudioTqdm for audio notifications (startup, success, error & shutdown).
- Always show progress for long operations.

## Color Scheme & UI

- Use Catppuccin Mocha color scheme: `from dataset_forge.utils.color import Mocha`
- Use centralized printing: `print_info`, `print_success`, `print_warning`, `print_error`
- Use `print_header()` and `print_section()` for menu organization.

## Menu System

- Use hierarchical menu structure.
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

- Supported DPID implementations: BasicSR, OpenMMLab, Phhofm, and Umzi (pepedpid). All DPID modules are modular, testable, and covered by robust, non-interactive tests using pytest and monkeypatching.
- Use parallel processing for efficiency.

## Audio & User Feedback

- Use centralized audio utilities: `from dataset_forge.utils.audio_utils import play_done_sound`
- Play completion sounds for long operations.
- Play startup and shutdown sounds appropriately.
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

## Enhanced Caching System (UPDATED July 2025)

- **Use centralized caching utilities:** `from dataset_forge.utils.cache_utils import in_memory_cache, disk_cache, model_cache, smart_cache`
- **Choose appropriate cache type:**
  - `@in_memory_cache`: Lightweight, frequently-called, session-only results with TTL and compression
  - `@disk_cache`: Expensive, large, or cross-session results with integrity checks
  - `@model_cache`: AI model loading operations with CUDA memory management
  - `@smart_cache`: Automatic selection based on function characteristics
- **Always document cache usage** in function docstrings with TTL, compression, and strategy rationale
- **Set appropriate TTL values** based on data volatility and memory constraints
- **Use compression** for large objects to reduce memory/disk footprint
- **Monitor cache statistics** for optimization opportunities
- **Implement cache warmup** for critical, frequently-accessed data
- **Handle cache misses gracefully** with fallback mechanisms
- **Test caching behavior** with unit tests covering cache hits, misses, and expiration

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
11. **Always update documentation appropriately after having added and tested new functionality or new menu items.**

---

For questions, see [Contributing](contributing.md) or ask the project maintainer.

## DPID Modularity (NEW)

- All DPID logic must use the new modular structure: `from dataset_forge.dpid.phhofm_dpid import ...`, etc.
- Do NOT import DPID logic from `dataset_forge.utils.dpid_phhofm` or legacy locations.

## Robust Menu Loop Pattern (UPDATED)

- All menus and submenus must use the robust menu loop pattern:
  - Get the user's choice (key) from `show_menu`.
  - Look up the action in the options dictionary.
  - Call the action if callable, with debug/error handling.
- Add debug prints and exception handling to menu actions for easier debugging.

## Workflow Prompt Handling (NEW)

- All user-facing workflows (not menu loops) are responsible for their own 'Press Enter to return to the menu...' prompt.
- Menu loops must NOT include this prompt.

## Centralized Printing & Style (UPDATED)

- All output, prompts, and progress must use the centralized printing utilities:
  - `print_header`, `print_section`, `print_info`, `print_success`, `print_error`, `print_prompt`
- All user-facing code must use the Catppuccin Mocha color scheme.
- No raw print statements in user-facing code.

## Exception Handling & Debug Prints (NEW)

- Add exception handling and debug prints to menu actions and workflows to catch and diagnose errors.

## Testing Requirements

- All new features and bugfixes must include appropriate unit and/or integration tests.
- Tests must use Google-style docstrings and be PEP8-compliant.
- Use pytest fixtures and monkeypatching for robust, isolated tests.

---

## Static Analysis & Code Quality (NEW)

- All public functions/classes/methods **must** have Google-style docstrings. This is enforced by the static analysis tool (`tools/find_code_issues/find_code_issues.py`).
- Before submitting a PR, contributors **must** run the static analysis tool and address all actionable issues (dead code, untested code, missing docstrings, etc.).
- The script overwrites its output files in `tools/find_code_issues/` on each run.
- See [docs/usage.md](usage.md) and [docs/features.md](features.md) for details.

## Interactive Workflow Prompt Pattern (July 2025)

- All interactive workflows must prompt for each major step within the workflow, not the menu.
- Steganography checks must prompt for steghide and zsteg individually, and the summary must report both.
- A visually distinct summary box must always be shown at the end, including zsteg results file path if produced.
- Menu header must be reprinted after returning to the workflow menu.
- All output must use centralized, Mocha-styled printing utilities and emoji-rich prompts.
- No duplicate prompts, debug prints, or raw print statements are allowed.
- This is now the standard for all interactive workflows in Dataset Forge.

## New Menu Integration (NEW)

- All new menu items and features (including Enhanced Metadata Management) must be documented in all relevant docs and README_full.md.
- Enhanced Metadata Management menu and features must be maintained, tested, and documented.
- exiftool, pandas, and SQLite are required for full metadata support; document their usage and troubleshooting.
- All user-facing errors must trigger error sound and be logged.
- All new features must include robust error handling, memory management, and user feedback.

## Testing Patterns & Requirements (Updated July 2025)

- All features must provide public, non-interactive APIs for programmatic access and testing.
- Tests should use monkeypatching and dummy objects to isolate logic and avoid external dependencies.
- Multiprocessing tests must use module-level worker functions for pickling compatibility.
- All tests must be robust, isolated, and cross-platform.
- Mark expected failures (XFAIL) and document them in the test and docs.

See [features.md](features.md#comprehensive-test-suite) and [advanced.md](advanced.md#advanced-test-design-patterns).

## Umzi's Dataset_Preprocessing (PepeDP-powered, July 2025)

- All menu actions must be thin wrappers around PepeDP, with all user inputs overridable for tests.
- All workflows must provide public, non-interactive APIs for robust, automated testing.
- All new features must be documented in all relevant docs and README_full.md.

## Workflow Heading Pattern for Interactive Workflows

All interactive workflows and menu actions in Dataset Forge must print a clear, Mocha-styled heading:

- **Before input/output prompts** (e.g., "Input/Output Selection")
- **Before progress bars or long-running operations** (e.g., "Progress")

### How to Implement

- Use `print_header` or `print_section` from `dataset_forge.utils.printing`.
- Use the Catppuccin Mocha color scheme (see `dataset_forge.utils.color.Mocha`).
- The heading should clearly indicate the workflow and the stage (e.g., "🧩 Best Tile Extraction (PepeDP) - Input/Output Selection").

### Example

```python
from dataset_forge.utils.printing import print_header, print_section
from dataset_forge.utils.color import Mocha

# Before input/output prompts
print_header("🧩 Best Tile Extraction (PepeDP) - Input/Output Selection", color=Mocha.pink)
# ... input prompts ...

# Before progress bar
print_section("Best Tile Extraction Progress", color=Mocha.pink)
# ... run progress bar ...
```

### Rationale

- Provides clear context for users at each stage of a workflow.
- Improves navigation and user experience, especially in complex or multi-step workflows.
- Ensures consistency across all CLI features and menus.

### Enforcement Checklist

- [ ] All new workflows print a heading before input/output prompts.
- [ ] All new workflows print a heading before progress bars/long-running operations.
- [ ] All headings use the Catppuccin Mocha color scheme and centralized printing utilities.
- [ ] All menu actions and workflows are reviewed for this pattern before merging.
