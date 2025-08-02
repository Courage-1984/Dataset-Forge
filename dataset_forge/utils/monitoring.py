"""
monitoring.py - Advanced system/resource monitoring for Dataset Forge

Features:
- Resource Monitoring: CPU, RAM, disk, GPU (NVIDIA, extensible)
- Performance Analytics: Operation timing, throughput
- Error Tracking: Summary logging, critical error sound
- Health Checks: System, CUDA, disk, RAM, etc.
- Subprocess/Thread Registry: Track, pause, resume, kill
- CLI-friendly output for menu integration

Dependencies: psutil, GPUtil, torch, pygame
"""

import os
import logging
import threading
import time
from typing import List, Dict, Optional, Any

import uuid
import signal
import sys

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    psutil,
    GPUtil,
    torch,
    pygame,
)

from logging.handlers import RotatingFileHandler

LOG_PATH = os.path.join("logs", "monitoring.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# Set up logging with rotation
logger = logging.getLogger("monitoring")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=3)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# Global singletons for integration
# perf_analytics = PerformanceAnalytics()
# error_tracker = ErrorTracker()
# task_registry = TaskRegistry()

# Decorators for easy integration
import functools


def monitor_performance(op_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start
                if perf_analytics:
                    perf_analytics.record_operation(op_name, duration)

        return wrapper

    return decorator


def monitor_all(op_name, critical_on_error=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_tracker:
                    error_tracker.log_error(e, critical=critical_on_error)
                raise
            finally:
                duration = time.time() - start
                if perf_analytics:
                    perf_analytics.record_operation(op_name, duration)

        return wrapper

    return decorator


# Export for import *
__all__ = [
    "ResourceMonitor",
    "PerformanceAnalytics",
    "ErrorTracker",
    "HealthChecker",
    "TaskRegistry",
    "print_resource_snapshot",
    "print_performance_summary",
    "print_error_summary",
    "print_health_check_results",
    "perf_analytics",
    "error_tracker",
    "task_registry",
    "monitor_performance",
    "monitor_all",
]


# Resource Monitoring
class ResourceMonitor:
    """
    Monitors CPU, RAM, disk, and GPU usage for main and subprocesses.
    """

    def __init__(self):
        self._running = False
        self._thread = None
        self.interval = 2.0
        self.snapshots = []

    def snapshot(self) -> Dict[str, Any]:
        """Return current resource usage snapshot."""
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(os.getcwd())
        gpu_info = []
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_info.append(
                        {
                            "id": gpu.id,
                            "name": gpu.name,
                            "load": gpu.load,
                            "mem_total": gpu.memoryTotal,
                            "mem_used": gpu.memoryUsed,
                            "mem_util": gpu.memoryUtil,
                            "temperature": gpu.temperature,
                        }
                    )
            except Exception as e:
                gpu_info.append({"error": str(e)})
        elif torch and torch.cuda.is_available():
            try:
                for i in range(torch.cuda.device_count()):
                    gpu_info.append(
                        {
                            "id": i,
                            "name": torch.cuda.get_device_name(i),
                            "mem_allocated": torch.cuda.memory_allocated(i),
                            "mem_reserved": torch.cuda.memory_reserved(i),
                        }
                    )
            except Exception as e:
                gpu_info.append({"error": str(e)})
        snapshot = {
            "cpu_percent": cpu,
            "ram_percent": mem.percent,
            "ram_used": mem.used,
            "ram_total": mem.total,
            "disk_percent": disk.percent,
            "disk_used": disk.used,
            "disk_total": disk.total,
            "gpu": gpu_info,
            "timestamp": time.time(),
        }
        return snapshot

    def _background_loop(self):
        while self._running:
            snap = self.snapshot()
            self.snapshots.append(snap)
            logger.info(f"Resource snapshot: {snap}")
            time.sleep(self.interval)

    def start_background(self, interval: float = 2.0):
        """Start background monitoring thread."""
        if self._running:
            return
        self.interval = interval
        self._running = True
        self._thread = threading.Thread(target=self._background_loop, daemon=True)
        self._thread.start()

    def stop_background(self):
        """Stop background monitoring thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None


# Performance Analytics
class PerformanceAnalytics:
    """
    Tracks operation timing, throughput, and efficiency.
    """

    def __init__(self):
        self.records = []  # List of dicts: {name, duration, extra, timestamp}

    def record_operation(
        self, name: str, duration: float, extra: Optional[Dict[str, Any]] = None
    ):
        """Record an operation's performance."""
        rec = {
            "name": name,
            "duration": duration,
            "extra": extra or {},
            "timestamp": time.time(),
        }
        self.records.append(rec)
        # logger.info(f"Performance: {rec}")  # <-- Remove or comment out this line to suppress console output

    def summary(self) -> Dict[str, Any]:
        """Return analytics summary."""
        from collections import defaultdict

        stats = defaultdict(
            lambda: {"count": 0, "total": 0.0, "min": float("inf"), "max": 0.0}
        )
        for rec in self.records:
            s = stats[rec["name"]]
            s["count"] += 1
            s["total"] += rec["duration"]
            s["min"] = min(s["min"], rec["duration"])
            s["max"] = max(s["max"], rec["duration"])
        for name, s in stats.items():
            if s["count"]:
                s["avg"] = s["total"] / s["count"]
            else:
                s["avg"] = 0.0
        return dict(stats)


# Error Tracking
class ErrorTracker:
    """
    Logs errors, triggers sound on critical errors, provides summary.
    """

    def __init__(self, error_sound_path: str = "assets/error.wav"):
        self.error_sound_path = error_sound_path
        self.errors = []  # List of dicts: {type, message, critical, timestamp}

    def log_error(self, error: Exception, critical: bool = False):
        """Log error and play sound if critical."""
        err_type = type(error).__name__
        msg = str(error)
        entry = {
            "type": err_type,
            "message": msg,
            "critical": critical,
            "timestamp": time.time(),
        }
        self.errors.append(entry)
        logger.error(f"Error: {entry}")
        if critical and pygame:
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(self.error_sound_path)
                pygame.mixer.music.play()
            except Exception as e:
                logger.error(f"Failed to play error sound: {e}")

    def summary(self) -> Dict[str, Any]:
        """Return error summary."""
        from collections import Counter

        if not self.errors:
            return {"count": 0, "by_type": {}, "last": None}
        by_type = Counter(e["type"] for e in self.errors)
        last = self.errors[-1]
        return {
            "count": len(self.errors),
            "by_type": dict(by_type),
            "last": last,
        }


# Health Checks
class HealthChecker:
    """
    Runs system health checks (RAM, disk, CUDA, etc.).
    """

    def run_all(self) -> Dict[str, Any]:
        results = {}
        # RAM
        mem = psutil.virtual_memory()
        results["ram_total_gb"] = round(mem.total / (1024**3), 2)
        results["ram_available_gb"] = round(mem.available / (1024**3), 2)
        results["ram_ok"] = mem.available / mem.total > 0.1
        # Disk
        disk = psutil.disk_usage(os.getcwd())
        results["disk_total_gb"] = round(disk.total / (1024**3), 2)
        results["disk_free_gb"] = round(disk.free / (1024**3), 2)
        results["disk_ok"] = disk.free / disk.total > 0.05
        # CUDA
        cuda_ok = False
        cuda_msg = ""
        if torch:
            try:
                cuda_ok = torch.cuda.is_available()
                cuda_msg = (
                    f"CUDA available: {cuda_ok}, devices: {torch.cuda.device_count()}"
                )
            except Exception as e:
                cuda_msg = f"CUDA check failed: {e}"
        else:
            cuda_msg = "torch not installed"
        results["cuda_ok"] = cuda_ok
        results["cuda_msg"] = cuda_msg
        # Python version
        pyver = sys.version_info
        results["python_version"] = f"{pyver.major}.{pyver.minor}.{pyver.micro}"
        results["python_ok"] = pyver >= (3, 8)
        # Permissions
        try:
            testfile = os.path.join(os.getcwd(), ".__healthcheck_test__")
            with open(testfile, "w") as f:
                f.write("ok")
            os.remove(testfile)
            results["write_permission"] = True
        except Exception:
            results["write_permission"] = False
        return results


# Subprocess/Thread Registry
class TaskRegistry:
    """
    Tracks subprocesses and threads, allows pause/resume/kill.
    """

    def __init__(self):
        self.tasks = (
            {}
        )  # task_id: {'type': 'process'|'thread', 'obj': obj, 'status': str, ...}

    def register_process(self, proc):
        """Register a subprocess.Popen object."""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {"type": "process", "obj": proc, "status": "running"}
        return task_id

    def register_thread(self, thread, stop_flag=None):
        """Register a threading.Thread object. Optionally provide a stop_flag (thread-safe Event)."""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "type": "thread",
            "obj": thread,
            "status": "running",
            "stop_flag": stop_flag,
        }
        return task_id

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tracked tasks."""
        result = []
        for tid, info in self.tasks.items():
            entry = {"id": tid, "type": info["type"], "status": info["status"]}
            if info["type"] == "process":
                proc = info["obj"]
                entry["pid"] = getattr(proc, "pid", None)
                entry["alive"] = proc.poll() is None
            elif info["type"] == "thread":
                thread = info["obj"]
                entry["name"] = getattr(thread, "name", None)
                entry["alive"] = thread.is_alive()
            result.append(entry)
        return result

    def pause_task(self, task_id: str):
        """Pause a task by ID (best effort, only works for processes on POSIX)."""
        info = self.tasks.get(task_id)
        if not info:
            raise ValueError(f"No such task: {task_id}")
        if info["type"] == "process":
            proc = info["obj"]
            try:
                proc.send_signal(signal.SIGSTOP)
                info["status"] = "paused"
            except Exception as e:
                logger.error(f"Failed to pause process {task_id}: {e}")
        elif info["type"] == "thread":
            # No safe way to pause threads in Python
            logger.warning(f"Cannot pause threads safely in Python (task {task_id})")
        else:
            logger.error(f"Unknown task type for {task_id}")

    def resume_task(self, task_id: str):
        """Resume a paused task by ID (processes only)."""
        info = self.tasks.get(task_id)
        if not info:
            raise ValueError(f"No such task: {task_id}")
        if info["type"] == "process":
            proc = info["obj"]
            try:
                proc.send_signal(signal.SIGCONT)
                info["status"] = "running"
            except Exception as e:
                logger.error(f"Failed to resume process {task_id}: {e}")
        elif info["type"] == "thread":
            logger.warning(f"Cannot resume threads safely in Python (task {task_id})")
        else:
            logger.error(f"Unknown task type for {task_id}")

    def kill_task(self, task_id: str):
        """Kill a task by ID."""
        info = self.tasks.get(task_id)
        if not info:
            raise ValueError(f"No such task: {task_id}")
        if info["type"] == "process":
            proc = info["obj"]
            try:
                proc.terminate()
                info["status"] = "terminated"
            except Exception as e:
                logger.error(f"Failed to terminate process {task_id}: {e}")
        elif info["type"] == "thread":
            stop_flag = info.get("stop_flag")
            if stop_flag is not None:
                stop_flag.set()
                info["status"] = "stopping"
            else:
                logger.warning(
                    f"No stop_flag for thread {task_id}; cannot kill cleanly."
                )
        else:
            logger.error(f"Unknown task type for {task_id}")


# CLI Output Helpers


def print_resource_snapshot(snapshot: Dict[str, Any]):
    """Pretty-print resource usage snapshot for CLI."""
    print("\n--- Resource Usage Snapshot ---")
    print(f"CPU: {snapshot['cpu_percent']}%")
    print(
        f"RAM: {snapshot['ram_percent']}% ({snapshot['ram_used'] // (1024**2)}MB / {snapshot['ram_total'] // (1024**2)}MB)"
    )
    print(
        f"Disk: {snapshot['disk_percent']}% ({snapshot['disk_used'] // (1024**3)}GB / {snapshot['disk_total'] // (1024**3)}GB)"
    )
    if snapshot["gpu"]:
        for gpu in snapshot["gpu"]:
            if "error" in gpu:
                print(f"GPU Error: {gpu['error']}")
            else:
                print(f"GPU {gpu.get('id', '?')}: {gpu.get('name', '?')}")
                if "load" in gpu:
                    print(
                        f"  Load: {gpu['load']*100:.1f}%  Mem: {gpu['mem_used']}/{gpu['mem_total']}MB  Util: {gpu['mem_util']*100:.1f}%  Temp: {gpu['temperature']}C"
                    )
                elif "mem_allocated" in gpu:
                    print(
                        f"  Mem Allocated: {gpu['mem_allocated']//(1024**2)}MB  Mem Reserved: {gpu['mem_reserved']//(1024**2)}MB"
                    )
    else:
        print("GPU: None detected")
    print(
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(snapshot['timestamp']))}"
    )


def print_performance_summary(summary: Dict[str, Any]):
    """Pretty-print performance analytics summary for CLI."""
    print("\n--- Performance Analytics ---")
    if not summary:
        print("No performance data recorded.")
        return
    for name, stats in summary.items():
        print(f"Operation: {name}")
        print(
            f"  Count: {stats['count']}  Avg: {stats['avg']:.3f}s  Min: {stats['min']:.3f}s  Max: {stats['max']:.3f}s  Total: {stats['total']:.3f}s"
        )


def print_error_summary(summary: Dict[str, Any]):
    """Pretty-print error summary for CLI."""
    print("\n--- Error Summary ---")
    print(f"Total errors: {summary.get('count', 0)}")
    if summary.get("by_type"):
        for t, c in summary["by_type"].items():
            print(f"  {t}: {c}")
    if summary.get("last"):
        last = summary["last"]
        print(
            f"Last error: [{last['type']}] {last['message']} (critical={last['critical']}) at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last['timestamp']))}"
        )


def print_health_check_results(results: Dict[str, Any]):
    """Pretty-print health check results for CLI."""
    print("\n--- System Health Check ---")
    print(
        f"RAM: {results['ram_available_gb']}GB free / {results['ram_total_gb']}GB total - {'OK' if results['ram_ok'] else 'LOW'}"
    )
    print(
        f"Disk: {results['disk_free_gb']}GB free / {results['disk_total_gb']}GB total - {'OK' if results['disk_ok'] else 'LOW'}"
    )
    print(
        f"CUDA: {results['cuda_msg']} - {'OK' if results['cuda_ok'] else 'NOT AVAILABLE'}"
    )
    print(
        f"Python: {results['python_version']} - {'OK' if results['python_ok'] else 'TOO OLD'}"
    )
    print(
        f"Write permission in cwd: {'OK' if results['write_permission'] else 'NO PERMISSION'}"
    )


perf_analytics = PerformanceAnalytics()
error_tracker = ErrorTracker()
task_registry = TaskRegistry()


def time_and_record_menu_load(menu_name):
    """
    Decorator to time and record the duration of a menu or submenu load.
    Records the timing in perf_analytics and prints to the user.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            from dataset_forge.utils.printing import print_info, print_warning

            if not callable(func):
                print_warning(f"[Menu Timing] {menu_name} is not callable; skipping timing.")
                return func
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            perf_analytics.record_operation(f"menu:{menu_name}", duration)
            print_info(f"⏱️ Loaded {menu_name} in {duration:.3f} seconds.")
            return result
        return wrapper
    return decorator
