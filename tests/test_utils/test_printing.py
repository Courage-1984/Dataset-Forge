import pytest
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)


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
    func(f"Test {msg}")
    captured = capsys.readouterr()
    assert f"Test {msg}" in captured.out
