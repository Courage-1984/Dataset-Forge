import importlib

from .printing import print_header, print_error, print_prompt


def show_menu(title, options, header_color, char="#"):
    print_header(title, char=char, color=header_color)
    for key, value in options.items():
        if key.lower() == "0":
            print(
                f"\033[38;2;249;226;175m[ {key} ]  \033[38;2;205;214;244m{value[0]}\033[0m"
            )
        else:
            print(
                f"\033[38;2;137;180;250m[ {key} ]  \033[38;2;205;214;244m{value[0]}\033[0m"
            )
    while True:
        print_prompt("\nEnter your choice: ")
        choice = input().strip()
        if choice in options:
            return choice
        else:
            print_error("Invalid choice. Please try again.")


def lazy_action(module_name: str, func_name: str):
    """
    Returns a callable that lazy-loads and calls the specified function.
    """

    def _action(*args, **kwargs):
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func(*args, **kwargs)

    return _action


def lazy_menu(module_name: str, func_name: str):
    """
    Returns a callable that lazy-loads and calls the specified menu function.
    """

    def _menu(*args, **kwargs):
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func(*args, **kwargs)

    return _menu
