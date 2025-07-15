[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Changelog

## [Unreleased]

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

## [July 2025]

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

This file will track major changes and releases in the future.
