import os
import logging
import random

IMAGE_TYPES = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".tiff", ".webp"]


# Setup logging for better error reporting in background tasks
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_uncaught_exceptions(ex_cls, ex, tb):
    print(f"Uncaught exception: {ex_cls.__name__}: {ex}")
    logging.error("Uncaught exception", exc_info=(ex_cls, ex, tb))


def get_folder_path(prompt):
    path = input(prompt)
    if not os.path.isdir(path):
        print(f"Path does not exist: {path}")
        return ""
    return path


def get_file_operation_choice():
    print("Choose file operation: (c)opy, (m)ove, (s)kip")
    choice = input("Enter choice: ").lower()
    return choice


def get_destination_path(is_optional=False):
    path = input("Enter destination path" + (" (optional): " if is_optional else ": "))
    if is_optional and not path:
        return None
    if not os.path.isdir(path):
        print(f"Path does not exist: {path}")
        return None
    return path

def get_pairs_to_process(matching_files, operation_name="process"):
    """
    Prompts the user for how many pairs to process (all, specific number, percentage, or random)
    and returns a randomly ordered list of selected file names.
    """
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
    random.shuffle(selected_files)  # Ensure processing in random order
    return selected_files


def is_image_file(filename):
    """Checks if a file is an image based on its extension."""
    return any(filename.lower().endswith(image_type) for image_type in IMAGE_TYPES)
