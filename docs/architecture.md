[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Project Architecture

(Include the full "Modular Architecture" and "Project Structure" sections from the original README here, preserving formatting and navigation.)

## Monitoring & Analytics Architecture

- **dataset_forge/utils/monitoring.py**: Centralized resource monitoring, analytics, error tracking, health checks, and background task registry. Provides decorators and context managers for integration with all action modules. Handles persistent logging and notifications.
- **dataset_forge/menus/system_monitoring_menu.py**: CLI menu for live resource usage, analytics, error summaries, health checks, and background task management. Integrates with monitoring.py and is accessible from the main menu.

All major operations in actions/ are instrumented with monitoring/analytics hooks, and memory/CUDA cleanup is integrated throughout the app lifecycle.

## Audio Error Feedback

The CLI interface now provides audio error feedback: whenever an error is reported to the user (via print_error), an error sound (error.mp3) is played for immediate feedback. This is handled by the centralized print_error utility in utils/printing.py, which calls play_error_sound from utils/audio_utils.py.

---

## Menu Timing & Profiling in the Architecture

- The menu system now includes a timing/profiling layer that times every menu and submenu load.
- This is implemented via the `time_and_record_menu_load` utility in `utils/monitoring.py`.
- All menu and submenu actions use the lazy import pattern, and are wrapped with the timing utility for performance analytics.
- Timing data is available to the user via the System Monitoring menu, and is also available for developer analytics.
- This system is part of the broader monitoring and analytics utilities in `utils/monitoring.py`.
