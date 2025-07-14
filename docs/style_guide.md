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
