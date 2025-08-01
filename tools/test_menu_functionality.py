#!/usr/bin/env python3
"""
Quick test runner for menu functionality after lazy implementation.

This script provides a simple way to test that all menus work correctly
after the lazy import implementation.
"""

import sys
import os
import time
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_menu_imports():
    """Test that all menu modules can be imported."""
    print("🔍 Testing menu imports...")
    
    menu_modules = [
        "dataset_forge.menus.main_menu",
        "dataset_forge.menus.dataset_management_menu",
        "dataset_forge.menus.analysis_menu",
        "dataset_forge.menus.image_processing_menu",
        "dataset_forge.menus.training_inference_menu",
        "dataset_forge.menus.utilities_menu",
        "dataset_forge.menus.system_settings_menu",
        "dataset_forge.menus.system_monitoring_menu",
        "dataset_forge.menus.performance_optimization_menu",
        "dataset_forge.menus.transform_menu",
        "dataset_forge.menus.user_profile_menu",
    ]
    
    success_count = 0
    for module_name in menu_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            print(f"  ✅ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
    
    print(f"\n📊 Menu imports: {success_count}/{len(menu_modules)} successful")
    return success_count == len(menu_modules)

def test_menu_functions():
    """Test that all menu functions are callable."""
    print("\n🔍 Testing menu functions...")
    
    menu_functions = [
        ("dataset_forge.menus.main_menu", "main_menu"),
        ("dataset_forge.menus.dataset_management_menu", "dataset_management_menu"),
        ("dataset_forge.menus.analysis_menu", "analysis_menu"),
        ("dataset_forge.menus.image_processing_menu", "image_processing_menu"),
        ("dataset_forge.menus.training_inference_menu", "training_inference_menu"),
        ("dataset_forge.menus.utilities_menu", "utilities_menu"),
        ("dataset_forge.menus.system_settings_menu", "system_settings_menu"),
        ("dataset_forge.menus.system_monitoring_menu", "system_monitoring_menu"),
        ("dataset_forge.menus.performance_optimization_menu", "performance_optimization_menu"),
        ("dataset_forge.menus.transform_menu", "transform_menu"),
        ("dataset_forge.menus.user_profile_menu", "user_profile_menu"),
    ]
    
    success_count = 0
    for module_name, func_name in menu_functions:
        try:
            module = __import__(module_name, fromlist=[func_name])
            func = getattr(module, func_name)
            if callable(func):
                print(f"  ✅ {module_name}.{func_name}")
                success_count += 1
            else:
                print(f"  ❌ {module_name}.{func_name}: not callable")
        except Exception as e:
            print(f"  ❌ {module_name}.{func_name}: {e}")
    
    print(f"\n📊 Menu functions: {success_count}/{len(menu_functions)} successful")
    return success_count == len(menu_functions)

def test_lazy_menu_function():
    """Test the lazy_menu function."""
    print("\n🔍 Testing lazy_menu function...")
    
    try:
        from dataset_forge.utils.menu import lazy_menu
        
        # Test lazy_menu for main menu
        test_menu = lazy_menu("dataset_forge.menus.main_menu", "main_menu")
        if callable(test_menu):
            print("  ✅ lazy_menu function works")
            
            # Test that it can be called
            with patch('dataset_forge.utils.menu.show_menu', return_value='0'):
                with patch('dataset_forge.utils.audio_utils.play_startup_sound'):
                    test_menu()
            print("  ✅ lazy_menu can be called")
            return True
        else:
            print("  ❌ lazy_menu function not callable")
            return False
    except Exception as e:
        print(f"  ❌ lazy_menu function: {e}")
        return False

def test_lazy_import_system():
    """Test the lazy import system."""
    print("\n🔍 Testing lazy import system...")
    
    try:
        from dataset_forge.utils.lazy_imports import (
            torch, cv2, numpy_as_np, PIL_Image,
            get_import_times, clear_import_cache
        )
        
        # Test that lazy imports are available
        assert hasattr(torch, '__class__')
        assert hasattr(cv2, '__class__')
        assert hasattr(numpy_as_np, '__class__')
        assert hasattr(PIL_Image, '__class__')
        
        print("  ✅ Lazy imports available")
        
        # Test import times tracking
        clear_import_cache()
        _ = torch.__class__  # Trigger lazy import
        
        import_times = get_import_times()
        if 'torch' in import_times:
            print(f"  ✅ Import times tracked: torch={import_times['torch']:.3f}s")
            return True
        else:
            print("  ❌ Import times not tracked")
            return False
            
    except Exception as e:
        print(f"  ❌ Lazy import system: {e}")
        return False

def test_menu_navigation():
    """Test menu navigation with lazy loading."""
    print("\n🔍 Testing menu navigation...")
    
    try:
        from dataset_forge.menus.main_menu import main_menu
        
        # Test that main menu can be called
        with patch('dataset_forge.utils.menu.show_menu', return_value='0'):
            with patch('dataset_forge.utils.audio_utils.play_startup_sound'):
                main_menu()
        
        print("  ✅ Main menu navigation works")
        return True
    except Exception as e:
        print(f"  ❌ Menu navigation: {e}")
        return False

def test_performance_improvement():
    """Test that performance has improved."""
    print("\n🔍 Testing performance improvement...")
    
    try:
        # Time the import of main module
        start_time = time.time()
        import main
        import_time = time.time() - start_time
        
        print(f"  📊 Import time: {import_time:.3f}s")
        
        if import_time < 0.1:
            print("  ✅ Performance improvement confirmed")
            return True
        else:
            print("  ⚠️  Import time is slower than expected")
            return False
            
    except Exception as e:
        print(f"  ❌ Performance test: {e}")
        return False

def test_global_commands():
    """Test global commands with lazy loading."""
    print("\n🔍 Testing global commands...")
    
    try:
        from dataset_forge.utils.menu import handle_global_command
        
        # Test help command
        result = handle_global_command('help', 'Test Menu', pause=False)
        if result is True:
            print("  ✅ Help command works")
        else:
            print("  ❌ Help command failed")
            return False
        
        # Test quit command
        try:
            handle_global_command('quit', 'Test Menu', pause=False)
            print("  ❌ Quit command should have raised SystemExit")
            return False
        except SystemExit:
            print("  ✅ Quit command works")
        
        return True
    except Exception as e:
        print(f"  ❌ Global commands: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Menu Functionality After Lazy Implementation")
    print("=" * 60)
    
    tests = [
        ("Menu Imports", test_menu_imports),
        ("Menu Functions", test_menu_functions),
        ("Lazy Menu Function", test_lazy_menu_function),
        ("Lazy Import System", test_lazy_import_system),
        ("Menu Navigation", test_menu_navigation),
        ("Performance Improvement", test_performance_improvement),
        ("Global Commands", test_global_commands),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name}: Exception - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Menu functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 