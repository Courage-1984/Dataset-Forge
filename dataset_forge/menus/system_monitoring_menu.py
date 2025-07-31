"""
system_monitoring_menu.py - System Monitoring & Health Menu for Dataset Forge

Provides:
- Live resource usage (CPU, RAM, disk, GPU)
- Performance analytics (live + historical)
- Error summary/logs
- Health checks
- Background task management (pause/resume/kill)

Integrates with utils.monitoring.
"""

import importlib
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import print_info
from dataset_forge.utils.cache_utils import clear_disk_cache
from dataset_forge.utils.printing import print_success

# Import monitoring utilities (stubs for now)
from dataset_forge.utils import monitoring

# Import cleanup menu
from dataset_forge.menus.cleanup_menu import cleanup_menu


def lazy_action(module_path, func_name):
    def _action(*args, **kwargs):
        return monitoring.time_and_record_menu_load(
            func_name,
            lambda: getattr(importlib.import_module(module_path), func_name)(
                *args, **kwargs
            ),
        )

    return _action


monitor_instance = None
task_registry = None
perf_analytics = None
error_tracker = None
health_checker = None


def manage_background_tasks():
    global task_registry
    if task_registry is None:
        task_registry = monitoring.TaskRegistry()
    tasks = task_registry.list_tasks()
    if not tasks:
        print_info("No background tasks registered.")
        return
    print("\n--- Background Tasks ---")
    for i, t in enumerate(tasks):
        print(
            f"{i+1}. ID: {t['id']} | Type: {t['type']} | Status: {t['status']} | Alive: {t.get('alive', '?')}"
        )
    try:
        idx = int(input("Select task number to manage (0 to cancel): "))
    except Exception:
        print_info("Invalid input.")
        return
    if idx == 0:
        return
    if not (1 <= idx <= len(tasks)):
        print_info("Invalid selection.")
        return
    task_id = tasks[idx - 1]["id"]
    print("Options: [p]ause, [r]esume, [k]ill, [c]ancel")
    action = input("Action: ").strip().lower()
    if action == "p":
        try:
            task_registry.pause_task(task_id)
            print_info("Task paused.")
        except Exception as e:
            print_info(f"Pause failed: {e}")
    elif action == "r":
        try:
            task_registry.resume_task(task_id)
            print_info("Task resumed.")
        except Exception as e:
            print_info(f"Resume failed: {e}")
    elif action == "k":
        try:
            task_registry.kill_task(task_id)
            print_info("Task killed.")
        except Exception as e:
            print_info(f"Kill failed: {e}")
    else:
        print_info("Cancelled.")


def show_performance_analytics():
    global perf_analytics
    if perf_analytics is None:
        perf_analytics = monitoring.PerformanceAnalytics()
    # Demo: add a test record if empty
    if not perf_analytics.records:
        perf_analytics.record_operation("demo_op", 0.123)
    monitoring.print_performance_summary(perf_analytics.summary())


def show_error_summary():
    global error_tracker
    if error_tracker is None:
        error_tracker = monitoring.ErrorTracker()
    # Demo: add a test error if empty
    if not error_tracker.errors:
        try:
            raise ValueError("Demo error for monitoring")
        except Exception as e:
            error_tracker.log_error(e, critical=False)
    monitoring.print_error_summary(error_tracker.summary())


def run_health_checks():
    global health_checker
    if health_checker is None:
        health_checker = monitoring.HealthChecker()
    results = health_checker.run_all()
    monitoring.print_health_check_results(results)


def show_menu_load_times():
    summary = monitoring.perf_analytics.summary()
    menu_summary = {k: v for k, v in summary.items() if k.startswith("menu:")}
    if not menu_summary:
        print_info("No menu load timings recorded yet.")
    else:
        monitoring.print_performance_summary(menu_summary)


def clear_caches():
    """Clear all caches (in-memory and disk)."""
    clear_disk_cache()
    print_success(
        "All disk caches cleared. (In-memory caches are cleared per function as needed)"
    )


def system_monitoring_menu():
    global monitor_instance
    if monitor_instance is None:
        monitor_instance = monitoring.ResourceMonitor()
    global task_registry
    if task_registry is None:
        task_registry = monitoring.TaskRegistry()
    global perf_analytics
    if perf_analytics is None:
        perf_analytics = monitoring.PerformanceAnalytics()
    global error_tracker
    if error_tracker is None:
        error_tracker = monitoring.ErrorTracker()
    global health_checker
    if health_checker is None:
        health_checker = monitoring.HealthChecker()
    options = {
        "1": (
            "📊 View Live Resource Usage",
            lambda: monitoring.print_resource_snapshot(monitor_instance.snapshot()),
        ),
        "2": (
            "📈 View Performance Analytics",
            lazy_action(__name__, "show_performance_analytics"),
        ),
        "3": ("🛑 View Error Summary", lazy_action(__name__, "show_error_summary")),
        "4": ("🩺 Run Health Checks", lazy_action(__name__, "run_health_checks")),
        "5": (
            "🧵 Manage Background Tasks",
            lazy_action(__name__, "manage_background_tasks"),
        ),
        "6": ("⏱️  View Menu Load Times", show_menu_load_times),
        "7": ("🧹 Clear All Caches (Disk & In-Memory)", clear_caches),
        "8": ("🧹 Cleanup & Optimization", cleanup_menu),
        "0": ("⬅️  Back to Main Menu", None),
    }
    # Define menu context for help system
    menu_context = {
        "Purpose": "Monitor system resources, performance, and health",
        "Total Options": "8 monitoring operations",
        "Navigation": "Use numbers 1-8 to select, 0 to go back",
        "Key Features": [
            "Resource monitoring, performance analytics, error tracking, health checks",
            "Background task management, menu load timing analysis",
            "Cache management and comprehensive cleanup operations"
        ],
    }

    while True:
        try:
            key = show_menu("🩺 System Monitoring & Health", options, Mocha.lavender, current_menu="System Monitoring & Health", menu_context=menu_context)
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting System Monitoring Menu...")
            return
