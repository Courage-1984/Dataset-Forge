import os
from dataset_forge.actions import exif_scrubber_actions
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import (
    print_success,
    print_info,
    print_warning,
    print_error,
)
from dataset_forge.utils.audio_utils import play_done_sound

# If ICCToSRGBConverter is not available, leave a TODO stub


def exif_scrubber_menu():
    """Scrub EXIF metadata from images in a folder or paired HQ/LQ folders."""
    print_info("\n=== Metadata (EXIF) Scrubber ===")
    if not exif_scrubber_actions.has_exiftool():
        print_warning(
            "ExifTool is not installed or not in PATH. Please install ExifTool and ensure it is available."
        )
        print_info("See: https://exiftool.org/")
        return
    print_info("Choose mode:")
    print_info("  1. Single folder")
    print_info("  2. HQ/LQ paired folders (preserve alignment)")
    mode = input("Select mode [1-2]: ").strip()
    if mode == "1":
        folder = input("Enter input folder path: ").strip()
        if not os.path.isdir(folder):
            print_error(f"Folder does not exist: {folder}")
            return
        print_info(f"Scrubbing EXIF metadata from all images in: {folder}")
        count, failed = exif_scrubber_actions.scrub_exif_single_folder(folder)
        print_info(f"Processed {count} images.")
        if failed:
            print_warning(f"Failed to process {len(failed)} files: {failed}")
        else:
            print_info("All images processed successfully.")
            print_success("EXIF scrubbing complete!")
            play_done_sound()
    elif mode == "2":
        hq_folder = input("Enter HQ folder path: ").strip()
        lq_folder = input("Enter LQ folder path: ").strip()
        if not os.path.isdir(hq_folder) or not os.path.isdir(lq_folder):
            print_error("Both HQ and LQ folders must exist.")
            return
        print_info(
            f"Scrubbing EXIF metadata from paired HQ/LQ folders:\n  HQ: {hq_folder}\n  LQ: {lq_folder}"
        )
        count, failed = exif_scrubber_actions.scrub_exif_hq_lq_folders(
            hq_folder, lq_folder
        )
        print_info(f"Processed {count} HQ/LQ image pairs.")
        if failed:
            print_warning(f"Failed to process {len(failed)} pairs:")
            for fname, err in failed:
                print_error(f"  {fname}: {err}")
        else:
            print_info("All HQ/LQ pairs processed successfully.")
            print_success("HQ/LQ EXIF scrubbing complete!")
            play_done_sound()
    else:
        print_error("Invalid mode.")


def icc_to_srgb_menu():
    """Convert ICC profile to sRGB for images in a file or folder."""
    from dataset_forge.utils.image_ops import ICCToSRGBConverter

    print_info("\n=== ICC to sRGB Conversion ===")
    input_path = input("Enter input file or folder path: ").strip()
    if not os.path.exists(input_path):
        print_error(f"Input path does not exist: {input_path}")
        return
    print_info("Choose operation mode:")
    print_info("  1. In place (overwrite original files)")
    print_info("  2. Copy to new folder (preserve originals)")
    op_choice = input("Select mode [1-2]: ").strip()
    if op_choice == "1":
        # In-place: overwrite original files
        if os.path.isfile(input_path):
            ICCToSRGBConverter.process_image(input_path, input_path)
        elif os.path.isdir(input_path):
            ICCToSRGBConverter.process_folder(input_path, input_path)
        else:
            print_error(
                f"Invalid input: {input_path} is neither a file nor a directory."
            )
            return
    elif op_choice == "2":
        output_path = input("Enter output folder path: ").strip()
        if not output_path:
            print_error("Output folder path required for copy mode.")
            return
        os.makedirs(output_path, exist_ok=True)
        ICCToSRGBConverter.process_input(input_path, output_path)
    else:
        print_error("Invalid choice.")
        return
    print_info("ICC to sRGB conversion completed.")
    print_success("ICC to sRGB conversion complete!")
    play_done_sound()
