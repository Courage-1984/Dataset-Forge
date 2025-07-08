import os
from dataset_forge import exif_scrubber

# If ICCToSRGBConverter is not available, leave a TODO stub


def exif_scrubber_menu():
    """Scrub EXIF metadata from images in a folder or paired HQ/LQ folders."""
    print("\n=== Metadata (EXIF) Scrubber ===")
    if not exif_scrubber.has_exiftool():
        print(
            "ExifTool is not installed or not in PATH. Please install ExifTool and ensure it is available."
        )
        print("See: https://exiftool.org/")
        return
    print("Choose mode:")
    print("  1. Single folder")
    print("  2. HQ/LQ paired folders (preserve alignment)")
    mode = input("Select mode [1-2]: ").strip()
    if mode == "1":
        folder = input("Enter input folder path: ").strip()
        if not os.path.isdir(folder):
            print(f"Folder does not exist: {folder}")
            return
        print(f"Scrubbing EXIF metadata from all images in: {folder}")
        count, failed = exif_scrubber.scrub_exif_single_folder(folder)
        print(f"Processed {count} images.")
        if failed:
            print(f"Failed to process {len(failed)} files: {failed}")
        else:
            print("All images processed successfully.")
    elif mode == "2":
        hq_folder = input("Enter HQ folder path: ").strip()
        lq_folder = input("Enter LQ folder path: ").strip()
        if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
            print("Both HQ and LQ folders must exist.")
            return
        print(
            f"Scrubbing EXIF metadata from paired HQ/LQ folders:\n  HQ: {hq_folder}\n  LQ: {lq_folder}"
        )
        count, failed = exif_scrubber.scrub_exif_hq_lq_folders(hq_folder, lq_folder)
        print(f"Processed {count} HQ/LQ image pairs.")
        if failed:
            print(f"Failed to process {len(failed)} pairs:")
            for fname, err in failed:
                print(f"  {fname}: {err}")
        else:
            print("All HQ/LQ pairs processed successfully.")
    else:
        print("Invalid mode.")


def icc_to_srgb_menu():
    """Convert ICC profile to sRGB for images in a file or folder."""
    from dataset_forge.image_ops import ICCToSRGBConverter

    print("\n=== ICC to sRGB Conversion ===")
    input_path = input("Enter input file or folder path: ").strip()
    if not os.path.exists(input_path):
        print(f"Input path does not exist: {input_path}")
        return
    print("Choose operation mode:")
    print("  1. In place (overwrite original files)")
    print("  2. Copy to new folder (preserve originals)")
    op_choice = input("Select mode [1-2]: ").strip()
    if op_choice == "1":
        # In-place: overwrite original files
        if os.path.isfile(input_path):
            ICCToSRGBConverter.process_image(input_path, input_path)
        elif os.path.isdir(input_path):
            ICCToSRGBConverter.process_folder(input_path, input_path)
        else:
            print(f"Invalid input: {input_path} is neither a file nor a directory.")
            return
    elif op_choice == "2":
        output_path = input("Enter output folder path: ").strip()
        if not output_path:
            print("Output folder path required for copy mode.")
            return
        os.makedirs(output_path, exist_ok=True)
        ICCToSRGBConverter.process_input(input_path, output_path)
    else:
        print("Invalid choice.")
        return
    print("ICC to sRGB conversion completed.")
