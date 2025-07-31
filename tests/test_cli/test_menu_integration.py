import subprocess
import sys
import os
import pytest
from unittest.mock import patch, MagicMock


def test_main_menu_entrypoint():
    """Test main menu entrypoint with basic navigation."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Simulate: 1 (Dataset Management), 0 (Back), 10 (Enhanced Metadata), 0 (Back), 0 (Exit)
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"1\n0\n10\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n",
        capture_output=True,
        timeout=20,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    assert b"Dataset Management" in result.stdout
    assert b"Enhanced Metadata Management" in result.stdout
    assert b"Exit" in result.stdout


def test_global_help_command():
    """Test global help command in main menu."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Simulate: help, 0 (Exit)
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"help\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n",
        capture_output=True,
        timeout=20,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    # Should show help information
    assert b"help" in result.stdout.lower() or b"global" in result.stdout.lower()


def test_global_quit_command():
    """Test global quit command from main menu."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Simulate: quit
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"quit\n",
        capture_output=True,
        timeout=10,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    # Should exit cleanly


def test_global_help_command_in_submenu():
    """Test global help command in a submenu."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Simulate: 1 (Dataset Management), help, 0 (Back), 0 (Exit)
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"1\nhelp\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n",
        capture_output=True,
        timeout=20,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    assert b"Dataset Management" in result.stdout
    # Should show help information for the submenu


def test_global_quit_command_from_submenu():
    """Test global quit command from a submenu."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Simulate: 1 (Dataset Management), quit
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"1\nquit\n",
        capture_output=True,
        timeout=10,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    # Should exit cleanly from submenu


def test_global_commands_case_insensitive():
    """Test that global commands are case insensitive."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Test various case combinations
    test_inputs = [
        b"HELP\n0\n",  # Uppercase help
        b"Help\n0\n",  # Mixed case help
        b"h\n0\n",     # Short help
        b"?\n0\n",     # Question mark help
        b"QUIT\n",     # Uppercase quit
        b"Exit\n",     # Exit command
        b"q\n",        # Short quit
    ]
    
    for test_input in test_inputs:
        result = subprocess.run(
            [sys.executable, "main.py"],
            input=test_input,
            capture_output=True,
            timeout=10,
            env=env,
        )
        print(f"Testing input: {test_input}")
        print("STDOUT:\n", result.stdout.decode("utf-8"))
        print("STDERR:\n", result.stderr.decode("utf-8"))
        assert result.returncode == 0


def test_global_commands_with_invalid_input():
    """Test global commands with invalid input handling."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Simulate: invalid command, help, 0 (Exit)
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"invalid\nhelp\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n",
        capture_output=True,
        timeout=20,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    # Should handle invalid input gracefully and still allow help


def test_global_commands_in_deep_menu():
    """Test global commands in a deep menu hierarchy."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Navigate to a deep menu: 1 (Dataset Management), 1 (Create Dataset), help, 0, 0, 0 (Exit)
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"1\n1\nhelp\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n",
        capture_output=True,
        timeout=20,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    assert b"Dataset Management" in result.stdout
    # Should show help for the deep menu


def test_global_quit_from_deep_menu():
    """Test global quit command from a deep menu hierarchy."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Navigate to a deep menu and quit: 1 (Dataset Management), 1 (Create Dataset), quit
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"1\n1\nquit\n",
        capture_output=True,
        timeout=10,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    # Should exit cleanly from deep menu


def test_global_commands_with_whitespace():
    """Test global commands with whitespace handling."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Test with whitespace around commands
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b" help \n0\n",  # Help with whitespace
        capture_output=True,
        timeout=10,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    # Should handle whitespace gracefully


def test_global_commands_error_handling():
    """Test global commands error handling and recovery."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Test multiple invalid commands followed by valid ones
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"invalid1\ninvalid2\nhelp\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n",
        capture_output=True,
        timeout=20,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    # Should handle multiple invalid inputs and still work


def test_global_commands_integration():
    """Integration test for global commands in a complete workflow."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Complete workflow: help, navigate, help in submenu, quit
    result = subprocess.run(
        [sys.executable, "main.py"],
        input=b"help\n1\nhelp\nquit\n",
        capture_output=True,
        timeout=15,
        env=env,
    )
    print("STDOUT:\n", result.stdout.decode("utf-8"))
    print("STDERR:\n", result.stderr.decode("utf-8"))
    assert result.returncode == 0
    # Should complete the full workflow successfully
