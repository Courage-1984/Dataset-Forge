[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

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
