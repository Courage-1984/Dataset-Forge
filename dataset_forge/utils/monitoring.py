#!/usr/bin/env python3
"""
Monitoring utilities for Dataset Forge.

This module provides comprehensive monitoring capabilities including resource tracking,
performance analytics, error tracking, and health checks.
"""

import functools
import os
import psutil
import time
from typing import Any, Dict, List, Optional

from dataset_forge.utils.printing import print_info, print_warning, print_error


def monitor_performance(op_name):
    """Decorator to monitor and record function performance."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                perf_analytics.record_operation(op_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                perf_analytics.record_operation(op_name, duration, {"error": str(e)})
                raise
        return wrapper
    return decorator


def monitor_all(op_name, critical_on_error=False):
    """Comprehensive monitoring decorator that tracks performance, errors, and resources."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                perf_analytics.record_operation(op_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_tracker.log_error(e, critical=critical_on_error)
                perf_analytics.record_operation(op_name, duration, {"error": str(e)})
                if critical_on_error:
                    print_error(f"Critical error in {op_name}: {e}")
                raise
        return wrapper
    return decorator


class ResourceMonitor:
    """Monitor system resources in real-time."""

    def __init__(self):
        self.background_thread = None
        self.stop_flag = False

    def snapshot(self) -> Dict[str, Any]:
        """Take a snapshot of current resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Memory usage
            memory = psutil.virtual_memory()
            ram_percent = memory.percent
            ram_used = memory.used
            ram_total = memory.total

            # Disk usage
            disk = psutil.disk_usage('.')
            disk_percent = (disk.used / disk.total) * 100
            disk_used = disk.used
            disk_total = disk.total

            # GPU usage (if available)
            gpu_info = []
            try:
                import torch
                if torch.cuda.is_available():
                    for i in range(torch.cuda.device_count()):
                        gpu = {
                            'id': i,
                            'name': torch.cuda.get_device_name(i),
                            'load': 0.0,  # Not easily available
                            'mem_used': torch.cuda.memory_allocated(i),
                            'mem_total': torch.cuda.get_device_properties(i).total_memory,
                            'mem_util': torch.cuda.memory_allocated(i) / torch.cuda.get_device_properties(i).total_memory,
                            'temperature': 0,  # Not easily available
                            'mem_allocated': torch.cuda.memory_allocated(i),
                            'mem_reserved': torch.cuda.memory_reserved(i)
                        }
                        gpu_info.append(gpu)
            except ImportError:
                pass

            return {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'ram_percent': ram_percent,
                'ram_used': ram_used,
                'ram_total': ram_total,
                'disk_percent': disk_percent,
                'disk_used': disk_used,
                'disk_total': disk_total,
                'gpu': gpu_info
            }
        except Exception as e:
            print_error(f"Error taking resource snapshot: {e}")
            return {
                'timestamp': time.time(),
                'cpu_percent': 0,
                'ram_percent': 0,
                'ram_used': 0,
                'ram_total': 0,
                'disk_percent': 0,
                'disk_used': 0,
                'disk_total': 0,
                'gpu': []
            }

    def _background_loop(self):
        """Background monitoring loop."""
        while not self.stop_flag:
            snapshot = self.snapshot()
            # Store or process snapshot as needed
            time.sleep(2.0)

    def start_background(self, interval: float = 2.0):
        """Start background monitoring."""
        import threading
        self.stop_flag = False
        self.background_thread = threading.Thread(target=self._background_loop, daemon=True)
        self.background_thread.start()

    def stop_background(self):
        """Stop background monitoring."""
        self.stop_flag = True
        if self.background_thread:
            self.background_thread.join()


class PerformanceAnalytics:
    """Track and analyze performance metrics."""

    def __init__(self):
        self.operations = {}

    def record_operation(
        self, name: str, duration: float, extra: Optional[Dict[str, Any]] = None
    ):
        """Record an operation's performance."""
        if name not in self.operations:
            self.operations[name] = {
                'count': 0,
                'total': 0.0,
                'min': float('inf'),
                'max': 0.0,
                'errors': 0
            }
        
        op = self.operations[name]
        op['count'] += 1
        op['total'] += duration
        op['min'] = min(op['min'], duration)
        op['max'] = max(op['max'], duration)
        
        if extra and 'error' in extra:
            op['errors'] += 1

    def summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        summary = {}
        for name, stats in self.operations.items():
            if stats['count'] > 0:
                summary[name] = {
                    'count': stats['count'],
                    'avg': stats['total'] / stats['count'],
                    'min': stats['min'],
                    'max': stats['max'],
                    'total': stats['total'],
                    'errors': stats['errors']
                }
        return summary


class ErrorTracker:
    """Track and analyze errors."""

    def __init__(self, error_sound_path: str = "assets/error.wav"):
        self.errors = []
        self.error_sound_path = error_sound_path

    def log_error(self, error: Exception, critical: bool = False):
        """Log an error with timestamp and context."""
        error_info = {
            'timestamp': time.time(),
            'type': type(error).__name__,
            'message': str(error),
            'critical': critical
        }
        self.errors.append(error_info)
        
        # Play error sound for critical errors
        if critical:
            try:
                from .audio_utils import play_error_sound
                play_error_sound(block=False)
            except ImportError:
                pass

    def summary(self) -> Dict[str, Any]:
        """Get error summary."""
        if not self.errors:
            return {'count': 0}
        
        by_type = {}
        for error in self.errors:
            error_type = error['type']
            by_type[error_type] = by_type.get(error_type, 0) + 1
        
        return {
            'count': len(self.errors),
            'by_type': by_type,
            'last': self.errors[-1] if self.errors else None
        }


class HealthChecker:
    """System health checking utilities."""

    def run_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        
        # RAM check
        memory = psutil.virtual_memory()
        results['ram_total_gb'] = memory.total // (1024**3)
        results['ram_available_gb'] = memory.available // (1024**3)
        results['ram_ok'] = memory.percent < 90
        
        # Disk check
        disk = psutil.disk_usage('.')
        results['disk_total_gb'] = disk.total // (1024**3)
        results['disk_free_gb'] = disk.free // (1024**3)
        results['disk_ok'] = (disk.free / disk.total) > 0.1
        
        # CUDA check
        try:
            import torch
            if torch.cuda.is_available():
                results['cuda_ok'] = True
                results['cuda_msg'] = f"CUDA {torch.version.cuda} available"
            else:
                results['cuda_ok'] = False
                results['cuda_msg'] = "CUDA not available"
        except ImportError:
            results['cuda_ok'] = False
            results['cuda_msg'] = "PyTorch not installed"
        
        # Python version check
        import sys
        results['python_version'] = sys.version.split()[0]
        results['python_ok'] = sys.version_info >= (3, 8)
        
        # Write permission check
        try:
            test_file = '.health_check_test'
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            results['write_permission'] = True
        except Exception:
            results['write_permission'] = False
        
        return results


class TaskRegistry:
    """Registry for tracking background tasks."""

    def __init__(self):
        self.processes = {}
        self.threads = {}

    def register_process(self, proc):
        """Register a process for monitoring."""
        task_id = f"proc_{proc.pid}"
        self.processes[task_id] = {
            'type': 'process',
            'pid': proc.pid,
            'process': proc,
            'start_time': time.time()
        }
        return task_id

    def register_thread(self, thread, stop_flag=None):
        """Register a thread for monitoring."""
        task_id = f"thread_{thread.ident}"
        self.threads[task_id] = {
            'type': 'thread',
            'thread': thread,
            'stop_flag': stop_flag,
            'start_time': time.time()
        }
        return task_id

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all registered tasks."""
        tasks = []
        
        # Add processes
        for task_id, info in self.processes.items():
            try:
                proc = info['process']
                tasks.append({
                    'id': task_id,
                    'type': 'process',
                    'pid': proc.pid,
                    'status': proc.status(),
                    'cpu_percent': proc.cpu_percent(),
                    'memory_percent': proc.memory_percent(),
                    'start_time': info['start_time']
                })
            except psutil.NoSuchProcess:
                # Process has ended
                del self.processes[task_id]
        
        # Add threads
        for task_id, info in self.threads.items():
            thread = info['thread']
            tasks.append({
                'id': task_id,
                'type': 'thread',
                'alive': thread.is_alive(),
                'start_time': info['start_time']
            })
        
        return tasks

    def pause_task(self, task_id: str):
        """Pause a task (process only)."""
        if task_id in self.processes:
            try:
                proc = self.processes[task_id]['process']
                proc.suspend()
                print_info(f"Paused process {task_id}")
            except psutil.NoSuchProcess:
                print_error(f"Process {task_id} not found")
        else:
            print_error(f"Task {task_id} not found or not a process")

    def resume_task(self, task_id: str):
        """Resume a task (process only)."""
        if task_id in self.processes:
            try:
                proc = self.processes[task_id]['process']
                proc.resume()
                print_info(f"Resumed process {task_id}")
            except psutil.NoSuchProcess:
                print_error(f"Process {task_id} not found")
        else:
            print_error(f"Task {task_id} not found or not a process")

    def kill_task(self, task_id: str):
        """Kill a task."""
        if task_id in self.processes:
            try:
                proc = self.processes[task_id]['process']
                proc.terminate()
                del self.processes[task_id]
                print_info(f"Killed process {task_id}")
            except psutil.NoSuchProcess:
                print_error(f"Process {task_id} not found")
        elif task_id in self.threads:
            info = self.threads[task_id]
            if info['stop_flag']:
                info['stop_flag'].set()
            del self.threads[task_id]
            print_info(f"Stopped thread {task_id}")
        else:
            print_error(f"Task {task_id} not found")


def print_resource_snapshot(snapshot: Dict[str, Any]):
    """Pretty-print resource usage snapshot for CLI."""
    print_info("\n--- Resource Usage Snapshot ---")
    print_info(f"CPU: {snapshot['cpu_percent']}%")
    print_info(
        f"RAM: {snapshot['ram_percent']}% ({snapshot['ram_used'] // (1024**2)}MB / {snapshot['ram_total'] // (1024**2)}MB)"
    )
    print_info(
        f"Disk: {snapshot['disk_percent']}% ({snapshot['disk_used'] // (1024**3)}GB / {snapshot['disk_total'] // (1024**3)}GB)"
    )
    if snapshot["gpu"]:
        for gpu in snapshot["gpu"]:
            if "error" in gpu:
                print_error(f"GPU Error: {gpu['error']}")
            else:
                print_info(f"GPU {gpu.get('id', '?')}: {gpu.get('name', '?')}")
                if "load" in gpu:
                    print_info(
                        f"  Load: {gpu['load']*100:.1f}%  Mem: {gpu['mem_used']}/{gpu['mem_total']}MB  Util: {gpu['mem_util']*100:.1f}%  Temp: {gpu['temperature']}C"
                    )
                elif "mem_allocated" in gpu:
                    print_info(
                        f"  Mem Allocated: {gpu['mem_allocated']//(1024**2)}MB  Mem Reserved: {gpu['mem_reserved']//(1024**2)}MB"
                    )
    else:
        print_info("GPU: None detected")
    print_info(
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(snapshot['timestamp']))}"
    )


def print_performance_summary(summary: Dict[str, Any]):
    """Pretty-print performance analytics summary for CLI."""
    print_info("\n--- Performance Analytics ---")
    if not summary:
        print_info("No performance data recorded.")
        return
    for name, stats in summary.items():
        print_info(f"Operation: {name}")
        print_info(
            f"  Count: {stats['count']}  Avg: {stats['avg']:.3f}s  Min: {stats['min']:.3f}s  Max: {stats['max']:.3f}s  Total: {stats['total']:.3f}s"
        )


def print_error_summary(summary: Dict[str, Any]):
    """Pretty-print error summary for CLI."""
    print_info("\n--- Error Summary ---")
    print_info(f"Total errors: {summary.get('count', 0)}")
    if summary.get("by_type"):
        for t, c in summary["by_type"].items():
            print_info(f"  {t}: {c}")
    if summary.get("last"):
        last = summary["last"]
        print_info(
            f"Last error: [{last['type']}] {last['message']} (critical={last['critical']}) at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last['timestamp']))}"
        )


def print_health_check_results(results: Dict[str, Any]):
    """Pretty-print health check results for CLI."""
    print_info("\n--- System Health Check ---")
    print_info(
        f"RAM: {results['ram_available_gb']}GB free / {results['ram_total_gb']}GB total - {'OK' if results['ram_ok'] else 'LOW'}"
    )
    print_info(
        f"Disk: {results['disk_free_gb']}GB free / {results['disk_total_gb']}GB total - {'OK' if results['disk_ok'] else 'LOW'}"
    )
    print_info(
        f"CUDA: {results['cuda_msg']} - {'OK' if results['cuda_ok'] else 'NOT AVAILABLE'}"
    )
    print_info(
        f"Python: {results['python_version']} - {'OK' if results['python_ok'] else 'TOO OLD'}"
    )
    print_info(
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
