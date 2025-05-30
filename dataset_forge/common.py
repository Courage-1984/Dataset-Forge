import os
import shutil
import logging


def get_unique_filename(dest_dir, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_name = filename
    while os.path.exists(os.path.join(dest_dir, unique_name)):
        unique_name = f"{base}_{counter}{ext}"
        counter += 1
    return unique_name


def get_folder_path(prompt):
    while True:
        path = input(prompt).strip()
        if os.path.isdir(path):
            return path
        else:
            print("Error: Invalid path. Please enter a valid directory.")


def get_file_operation_choice():
    while True:
        choice = input("Enter operation choice (copy/move/inplace): ").strip().lower()
        if choice in ["copy", "move", "inplace"]:
            return choice
        else:
            print("Invalid choice. Please enter 'copy', 'move', or 'inplace'.")


def get_destination_path(is_optional=False):
    while True:
        path = input(
            "Enter the destination directory path (leave blank if not moving/copying to a new location): "
        ).strip()
        if is_optional and not path:
            return ""
        # Check if the parent directory exists. If not, offer to create.
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


def perform_file_operation(src_path, dest_dir, operation, filename):
    """
    Performs file operations (copy, move, inplace save).
    Returns the path to the resulting file if successful, None otherwise.
    """
    try:
        if operation == "inplace":
            # For inplace operations, the dest_dir is not used for creating a new path.
            # The file is modified and saved back to src_path.
            # This function currently only handles moving/copying.
            # Inplace modifications will be handled directly in the functions that modify images.
            return (
                src_path  # Return original path if inplace, as no new file is created.
            )

        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, get_unique_filename(dest_dir, filename))

        if operation == "copy":
            shutil.copy2(src_path, dest_path)
        elif operation == "move":
            shutil.move(src_path, dest_path)
        return dest_path
    except Exception as e:
        logging.error(f"Error performing {operation} on {src_path} to {dest_dir}: {e}")
        return None
