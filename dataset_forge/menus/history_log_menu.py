from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_error,
    print_section,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.history_log import list_logs, read_log, read_most_recent_log


def view_most_recent_log():
    print_header("Most Recent Change/History Log", color=Mocha.mauve)
    log = read_most_recent_log()
    if log:
        print(log)
    else:
        print_info("No logs found.")
    input("\nPress Enter to return...")


def select_log_to_view():
    logs = list_logs()
    if not logs:
        print_info("No logs found.")
        input("\nPress Enter to return...")
        return
    print_section("Available Logs", color=Mocha.sapphire)
    for idx, fname in enumerate(logs, 1):
        print(f"[{idx}] {fname}")
    print()
    try:
        choice = int(input("Enter log number to view (0 to cancel): ").strip())
        if choice == 0:
            return
        if 1 <= choice <= len(logs):
            log = read_log(logs[choice - 1])
            print_header(f"Log: {logs[choice - 1]}", color=Mocha.mauve)
            print(log if log else "(Empty log)")
        else:
            print_error("Invalid choice.")
    except Exception:
        print_error("Invalid input.")
    input("\nPress Enter to return...")


def history_log_menu():
    options = history_log_menu.__menu_options__
    while True:
        choice = show_menu(
            "Change/History Log Menu", options, header_color=Mocha.lavender
        )
        if choice is None or choice == "0":
            break
        action = options[choice][1]
        if callable(action):
            action()


history_log_menu.__menu_options__ = {
    "1": ("View most recent log", view_most_recent_log),
    "2": ("Select a log to view", select_log_to_view),
    "0": ("Return to main menu", None),
}
