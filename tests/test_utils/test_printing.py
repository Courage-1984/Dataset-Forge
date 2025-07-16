import pytest
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
)
from dataset_forge.utils.color import Mocha


@pytest.mark.parametrize(
    "func,msg",
    [
        (print_info, "info"),
        (print_success, "success"),
        (print_warning, "warning"),
        (print_error, "error"),
    ],
)
def test_print_functions(func, msg, capsys):
    """Test that print functions output the correct message."""
    func(f"Test {msg}")
    captured = capsys.readouterr()
    assert f"Test {msg}" in captured.out


def test_print_header(capsys):
    """Test that print_header outputs the correct header and color code."""
    print_header("HeaderTest", char="*", color=Mocha.lavender)
    captured = capsys.readouterr()
    assert "HeaderTest" in captured.out
    assert "\033[" in captured.out  # ANSI color code present
