import os
import random
import dataset_forge.utils.path_history as path_history


def get_path_with_history(
    prompt,
    allow_hq_lq=True,
    allow_single_folder=True,
    is_destination=False,
    is_optional=False,
):
    """
    Prompt the user for a path, allowing selection from history, manual entry, or HQ/LQ from settings.
    - allow_hq_lq: If True, user can select HQ/LQ from settings.
    - allow_single_folder: If True, user can select a single folder (not paired HQ/LQ).
    - is_destination: If True, this is a destination path (may allow blank if is_optional).
    - is_optional: If True, user can leave blank (for destination paths).
    """
    while True:
        print("\nPath Entry Options:")
        print("[1] Enter path manually")
        print("[2] Use last used path")
        print("[3] View path history")
        if allow_hq_lq:
            print("[4] Use HQ path from settings")
            print("[5] Use LQ path from settings")
        choice = input(f"{prompt}\nSelect option (1-5): ").strip()
        if choice == "1":
            path = input("Enter path: ").strip()
            if path:
                path_history.add_path(path)
                return path
        elif choice == "2":
            last_path = path_history.get_last_path()
            if last_path:
                print(f"Using last used path: {last_path}")
                return last_path
            else:
                print("No path in history.")
        elif choice == "3":
            history = path_history.get_history()
            if not history:
                print("No path history available.")
                continue
            for idx, p in enumerate(history, 1):
                print(f"[{idx}] {p}")
            sel = input("Select a path by number, or press Enter to cancel: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(history):
                path = history[int(sel) - 1]
                path_history.add_path(path)
                return path
        elif allow_hq_lq and choice == "4":
            from dataset_forge.menus import session_state

            if session_state.hq_folder:
                path_history.add_path(session_state.hq_folder)
                return session_state.hq_folder
            else:
                print("HQ folder not set in settings.")
        elif allow_hq_lq and choice == "5":
            from dataset_forge.menus import session_state

            if session_state.lq_folder:
                path_history.add_path(session_state.lq_folder)
                return session_state.lq_folder
            else:
                print("LQ folder not set in settings.")
        elif is_optional and choice == "":
            return ""
        else:
            print("Invalid choice. Please try again.")


def get_folder_path(prompt):
    while True:
        path = get_path_with_history(prompt)
        if os.path.isdir(path):
            return path
        print("Error: Invalid path. Please enter a valid directory.")


def get_file_operation_choice():
    """Prompt the user to choose a file operation: copy, move, or inplace."""
    while True:
        choice = input("Enter operation choice (copy/move/inplace): ").strip().lower()
        if choice in ["copy", "move", "inplace"]:
            return choice
        print("Invalid choice. Please enter 'copy', 'move', or 'inplace'.")


def get_destination_path(is_optional=False):
    while True:
        path = get_path_with_history(
            "Enter the destination directory path",
            is_destination=True,
            is_optional=is_optional,
        )
        if is_optional and not path:
            return ""
        parent_dir = os.path.dirname(path) or "."
        if not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir)
                print(f"Created parent directory: {parent_dir}")
                return path
            except OSError as e:
                print(f"Error creating parent directory {parent_dir}: {e}")
                print("Please enter a valid path.")
        else:
            return path


def get_pairs_to_process(matching_files, operation_name="process"):
    """Prompt the user for how many pairs to process and return a randomly ordered list of selected file names."""
    if not matching_files:
        print(f"No matching pairs found to {operation_name}.")
        return []
    num_available = len(matching_files)
    print(f"\nFound {num_available} matching pairs.")
    while True:
        choice_prompt = (
            f"How many pairs do you want to {operation_name}?\n"
            f"  - Enter 'all' to {operation_name} all {num_available} pairs.\n"
            f"  - Enter a specific number (e.g., 100).\n"
            f"  - Enter a percentage (e.g., 10% of {num_available}).\n"
            f"  - Enter 'random' for a random number of pairs (1 to {num_available}).\n"
            f"Your choice: "
        )
        choice = input(choice_prompt).strip().lower()
        num_to_process = 0
        if choice == "all":
            num_to_process = num_available
            break
        elif choice == "random":
            if num_available == 0:
                num_to_process = 0
            else:
                num_to_process = random.randint(1, num_available)
            print(f"Selected random amount: {num_to_process} pairs.")
            break
        elif choice.endswith("%"):
            try:
                percentage = float(choice[:-1])
                if 0 <= percentage <= 100:
                    num_to_process = int(num_available * (percentage / 100))
                    break
                else:
                    print("Percentage must be between 0 and 100.")
            except ValueError:
                print("Invalid percentage format. Example: '10%'")
        else:
            try:
                num = int(choice)
                if 0 <= num <= num_available:
                    num_to_process = num
                    break
                else:
                    print(f"Number of pairs must be between 0 and {num_available}.")
            except ValueError:
                print(
                    "Invalid input. Please enter 'all', a number, a percentage (e.g., '10%'), or 'random'."
                )
    if num_to_process == 0:
        print(f"No pairs selected to {operation_name}. Exiting this operation.")
        return []
    print(
        f"\nWill {operation_name} {num_to_process} pairs out of {num_available} available pairs."
    )
    selected_files = random.sample(matching_files, num_to_process)
    random.shuffle(selected_files)
    return selected_files
