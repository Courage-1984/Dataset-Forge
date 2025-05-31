import os
from dataset_forge.io_utils_old import is_image_file
from dataset_forge.common import (
    get_file_operation_choice,
    get_destination_path,
    get_unique_filename,
)
import cv2
from tqdm import tqdm

def fix_corrupted_images(folder_path, grayscale=False):
    """Re-save images to fix corruption issues."""
    print("\n" + "=" * 30)
    print("  Fixing Corrupted Images")
    print("=" * 30)

    operation = get_file_operation_choice()
    dest_dir = ""
    if operation != "inplace":
        dest_dir = get_destination_path()
        if not dest_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(dest_dir, exist_ok=True)

    def process_image(input_path, dest_path=None):
        try:
            image = cv2.imread(input_path)
            if image is None:
                return False, "Failed to read image"

            if grayscale:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            save_path = dest_path if dest_path else input_path
            return cv2.imwrite(save_path, image), None
        except Exception as e:
            return False, str(e)

    image_files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
    ]

    processed_count = 0
    errors = []

    for filename in tqdm(image_files, desc="Processing Images"):
        input_path = os.path.join(folder_path, filename)
        dest_path = (
            input_path
            if operation == "inplace"
            else os.path.join(dest_dir, get_unique_filename(dest_dir, filename))
        )

        success, error = process_image(input_path, dest_path)

        if success:
            processed_count += 1
            if operation == "move" and input_path != dest_path:
                os.remove(input_path)
        else:
            errors.append(f"Error processing {filename}: {error}")

    print("\n" + "-" * 30)
    print("  Fix Corrupted Images Summary")
    print("-" * 30)
    print(f"Total images processed: {processed_count}")
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)
