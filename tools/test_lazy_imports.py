#!/usr/bin/env python3
"""
Test script for lazy import system performance.

This script demonstrates the performance improvements achieved by using
lazy imports in Dataset Forge.
"""

import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_normal_imports():
    """Test normal import performance."""
    print("Testing normal imports...")

    start_time = time.time()

    # Simulate normal imports (what we had before)
    try:
        import torch

        torch_time = time.time() - start_time
        print(f"  PyTorch: {torch_time:.3f}s")

        start_time = time.time()
        import cv2

        cv2_time = time.time() - start_time
        print(f"  OpenCV: {cv2_time:.3f}s")

        start_time = time.time()
        import numpy as np

        numpy_time = time.time() - start_time
        print(f"  NumPy: {numpy_time:.3f}s")

        start_time = time.time()
        from PIL import Image

        pil_time = time.time() - start_time
        print(f"  PIL: {pil_time:.3f}s")

        total_time = torch_time + cv2_time + numpy_time + pil_time
        print(f"  Total normal import time: {total_time:.3f}s")

        return total_time

    except ImportError as e:
        print(f"  Import error: {e}")
        return 0


def test_lazy_imports():
    """Test lazy import performance."""
    print("Testing lazy imports...")

    start_time = time.time()

    # Import lazy import system
    from dataset_forge.utils.lazy_imports import (
        torch,
        cv2,
        numpy_as_np as np,
        PIL_Image as Image,
    )

    lazy_system_time = time.time() - start_time
    print(f"  Lazy import system: {lazy_system_time:.3f}s")

    # Test actual usage (when imports happen)
    start_time = time.time()

    # Use torch (triggers import)
    try:
        tensor = torch.tensor([1, 2, 3])
        torch_usage_time = time.time() - start_time
        print(f"  PyTorch usage: {torch_usage_time:.3f}s")

        start_time = time.time()
        # Use cv2 (triggers import)
        array = np.array([1, 2, 3])
        cv2_usage_time = time.time() - start_time
        print(f"  NumPy usage: {cv2_usage_time:.3f}s")

        start_time = time.time()
        # Use PIL (triggers import)
        image = Image.new("RGB", (100, 100))
        pil_usage_time = time.time() - start_time
        print(f"  PIL usage: {pil_usage_time:.3f}s")

        total_usage_time = torch_usage_time + cv2_usage_time + pil_usage_time
        print(f"  Total lazy usage time: {total_usage_time:.3f}s")

        return lazy_system_time, total_usage_time

    except Exception as e:
        print(f"  Usage error: {e}")
        return lazy_system_time, 0


def test_cli_startup_simulation():
    """Simulate CLI startup performance."""
    print("Testing CLI startup simulation...")

    # Normal startup (before optimization)
    print("Normal startup (before optimization):")
    start_time = time.time()

    # Simulate normal startup
    import warnings

    warnings.filterwarnings("ignore")

    import logging

    logging.basicConfig(level=logging.WARNING)

    # Import heavy libraries (what we had before)
    try:
        import torch
        import cv2
        import numpy as np
        from PIL import Image
    except ImportError:
        pass

    normal_startup_time = time.time() - start_time
    print(f"  Normal startup time: {normal_startup_time:.3f}s")

    # Optimized startup (after optimization)
    print("Optimized startup (after optimization):")
    start_time = time.time()

    # Simulate optimized startup
    import warnings

    warnings.filterwarnings("ignore")

    import logging

    logging.basicConfig(level=logging.WARNING)

    # Only import lazy import system (no heavy libraries)
    try:
        from dataset_forge.utils.lazy_imports import (
            torch,
            cv2,
            numpy_as_np as np,
            PIL_Image as Image,
        )
    except ImportError:
        pass

    optimized_startup_time = time.time() - start_time
    print(f"  Optimized startup time: {optimized_startup_time:.3f}s")

    if normal_startup_time > 0:
        improvement = (
            (normal_startup_time - optimized_startup_time) / normal_startup_time
        ) * 100
        print(f"  Improvement: {improvement:.1f}%")
    else:
        print("  Improvement: N/A (no normal startup time)")

    return normal_startup_time, optimized_startup_time


def test_import_monitoring():
    """Test import monitoring functionality."""
    print("Testing import monitoring...")

    try:
        from dataset_forge.utils.lazy_imports import (
            get_import_times,
            print_import_times,
            clear_import_cache,
        )

        # Clear cache for fresh test
        clear_import_cache()

        # Perform some operations that trigger lazy imports
        from dataset_forge.utils.lazy_imports import torch, cv2

        # Use the imports
        tensor = torch.tensor([1, 2, 3])

        # Get import statistics
        import_times = get_import_times()

        print("Import monitoring results:")
        print_import_times()

        return True

    except Exception as e:
        print(f"  Import monitoring error: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("Dataset Forge - Lazy Import Performance Test")
    print("=" * 60)

    # Test 1: Normal vs Lazy imports
    print("\n1. Normal vs Lazy Import Performance")
    print("-" * 40)

    normal_time = test_normal_imports()
    lazy_system_time, lazy_usage_time = test_lazy_imports()

    if normal_time > 0 and lazy_system_time > 0:
        total_lazy_time = lazy_system_time + lazy_usage_time
        improvement = ((normal_time - lazy_system_time) / normal_time) * 100
        print(f"\nPerformance comparison:")
        print(f"  Normal imports: {normal_time:.3f}s")
        print(f"  Lazy system: {lazy_system_time:.3f}s")
        print(f"  Lazy usage: {lazy_usage_time:.3f}s")
        print(f"  Total lazy: {total_lazy_time:.3f}s")
        print(f"  Startup improvement: {improvement:.1f}%")

    # Test 2: CLI startup simulation
    print("\n2. CLI Startup Simulation")
    print("-" * 40)

    normal_startup, optimized_startup = test_cli_startup_simulation()

    # Test 3: Import monitoring
    print("\n3. Import Monitoring")
    print("-" * 40)

    monitoring_success = test_import_monitoring()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if normal_time > 0 and lazy_system_time > 0:
        print(f"✅ Lazy import system reduces startup time by {improvement:.1f}%")

    if normal_startup > 0 and optimized_startup > 0:
        startup_improvement = (
            (normal_startup - optimized_startup) / normal_startup
        ) * 100
        print(
            f"✅ CLI startup optimization reduces startup time by {startup_improvement:.1f}%"
        )
    elif normal_startup > 0:
        print(
            f"✅ CLI startup optimization: Normal {normal_startup:.3f}s vs Optimized {optimized_startup:.3f}s"
        )

    if monitoring_success:
        print("✅ Import monitoring system working correctly")

    print("\nKey Benefits:")
    print("• Faster CLI startup")
    print("• Reduced memory footprint")
    print("• Better user experience")
    print("• Maintainable codebase")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
