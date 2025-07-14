[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Advanced Features & Configuration

(Include the full "Advanced Features", "Configuration", and "Requirements" sections from the original README here, preserving formatting and navigation.)

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
