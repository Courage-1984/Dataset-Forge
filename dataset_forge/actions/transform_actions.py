import os
import shutil
import logging
import numpy as np
from tqdm import tqdm
from PIL import Image
from dataset_forge.io_utils import (
    is_image_file,
)
from dataset_forge.utils.input_utils import (
    get_pairs_to_process,
    get_file_operation_choice,
    get_destination_path,
)
from dataset_forge.utils.file_utils import IMAGE_TYPES, get_unique_filename
from dataset_forge.image_ops import ColorAdjuster
import subprocess
from dataset_forge import dpid_phhofm


# --- Downsample Images ---
def downsample_images_menu():
    """Downsample images using various methods, including DPID and OpenCV/PIL."""
    print("\n=== Downsample Images (Batch/Single, Multiple Methods) ===")
    print("Select downsampling implementation:")
    print("  1. DPID (BasicSR)")
    print("  2. DPID (OpenMMLab)")
    print("  3. OpenCV INTER_AREA")
    print("  4. OpenCV INTER_LANCZOS4")
    print("  5. OpenCV INTER_CUBIC")
    print("  6. PIL LANCZOS")
    print("  7. Phhofm's DPID Downscaler (pepedpid)")
    method = input("Enter method number (default 1): ").strip() or "1"
    if method != "7":
        input_folder = input("Enter path to HR (100%) images folder: ").strip()
        if not os.path.isdir(input_folder):
            print(f"Input folder '{input_folder}' does not exist.")
            return
        output_folder = input(
            "Enter base output folder (subfolders will be created for each scale): "
        ).strip()
        if not output_folder:
            print("Output folder is required.")
            return
        os.makedirs(output_folder, exist_ok=True)
        scale_str = input(
            "Enter scale factors (comma-separated, e.g. 0.75,0.5,0.25): "
        ).strip()
        try:
            scales = [float(s) for s in scale_str.split(",") if 0 < float(s) < 1]
        except Exception:
            print("Invalid scale factors.")
            return
        if not scales:
            print("No valid scales provided.")
            return
        dpid_lambda = 0.5
        if method in ["1", "2"]:
            try:
                dpid_lambda = float(
                    input(
                        "Enter DPID lambda (0=smooth, 1=detail, default 0.5): "
                    ).strip()
                    or 0.5
                )
            except Exception:
                dpid_lambda = 0.5
        # TODO: Implement the actual downsampling logic for each method (BasicSR, OpenMMLab, OpenCV, PIL)
        print(
            "[TODO] Downsampling logic for methods 1-6 not yet implemented in modular actions."
        )
        return
    # --- Phhofm's DPID Downscaler integration ---
    print("Phhofm's DPID Downscaler selected.")
    print("Choose mode:")
    print("  1. Single folder")
    print("  2. HQ/LQ paired folders (preserve alignment)")
    mode = input("Select mode (1=single, 2=pair): ").strip()
    if mode == "2":
        hq_folder = input("Enter HQ folder path: ").strip()
        lq_folder = input("Enter LQ folder path: ").strip()
        out_hq_folder = input("Enter HQ output folder: ").strip()
        out_lq_folder = input("Enter LQ output folder: ").strip()
        scale = input("Enter downscale factor (integer >=2, e.g. 2, 3, 4): ").strip()
        try:
            scale = int(scale)
            if scale < 2:
                raise ValueError
        except Exception:
            print("Invalid scale factor.")
            return
        output_ext = (
            input("Output extension (.png/.jpg/.webp, default .png): ").strip()
            or ".png"
        )
        threads = input("Threads (default 4): ").strip()
        try:
            threads = int(threads) if threads else 4
        except Exception:
            threads = 4
        skip_existing = (
            input("Skip existing files? (y/n, default n): ").strip().lower() == "y"
        )
        verbose = input("Verbose output? (y/n, default n): ").strip().lower() == "y"
        processed, skipped, failed = dpid_phhofm.downscale_hq_lq_pair(
            hq_folder,
            lq_folder,
            out_hq_folder,
            out_lq_folder,
            scale,
            output_ext=output_ext,
            threads=threads,
            skip_existing=skip_existing,
            verbose=verbose,
        )
        print(f"\nOperation complete:")
        print(f"  Processed: {processed} pairs")
        print(f"  Skipped:   {skipped} pairs")
        print(f"  Failed:    {failed} pairs")
        print(f"  Output HQ: {out_hq_folder}")
        print(f"  Output LQ: {out_lq_folder}")
    else:
        input_folder = input("Enter input folder path: ").strip()
        output_folder = input("Enter output folder path: ").strip()
        scale = input("Enter downscale factor (integer >=2, e.g. 2, 3, 4): ").strip()
        try:
            scale = int(scale)
            if scale < 2:
                raise ValueError
        except Exception:
            print("Invalid scale factor.")
            return
        output_ext = (
            input("Output extension (.png/.jpg/.webp, default .png): ").strip()
            or ".png"
        )
        threads = input("Threads (default 4): ").strip()
        try:
            threads = int(threads) if threads else 4
        except Exception:
            threads = 4
        recursive = (
            input("Process subdirectories recursively? (y/n, default n): ")
            .strip()
            .lower()
            == "y"
        )
        skip_existing = (
            input("Skip existing files? (y/n, default n): ").strip().lower() == "y"
        )
        verbose = input("Verbose output? (y/n, default n): ").strip().lower() == "y"
        processed, skipped, failed = dpid_phhofm.downscale_folder(
            input_folder,
            output_folder,
            scale,
            output_ext=output_ext,
            threads=threads,
            recursive=recursive,
            skip_existing=skip_existing,
            verbose=verbose,
        )
        print(f"\nOperation complete:")
        print(f"  Processed: {processed} images")
        print(f"  Skipped:   {skipped} images")
        print(f"  Failed:    {failed} images")
        print(f"  Output:    {output_folder}")


# --- HDR to SDR Tone Mapping ---
class ToneMapper:
    """Base class for HDR to SDR tone mapping using ffmpeg."""

    def __init__(self, algorithm="hable"):
        self.algorithm = algorithm

    def ffmpeg_command(self, input_path, output_path):
        return [
            "ffmpeg",
            "-i",
            input_path,
            "-vf",
            f"zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap={self.algorithm}:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            output_path,
        ]

    def run(self, input_path, output_path):
        cmd = self.ffmpeg_command(input_path, output_path)
        print("\nRunning ffmpeg command:")
        print(" ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
            print(f"\nTone mapping complete! Output: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error running ffmpeg: {e}")


def hdr_to_sdr_menu():
    """Convert HDR video to SDR using ffmpeg and various tone mapping algorithms."""
    print("\n=== HDR to SDR Tone Mapping ===")
    input_path = input("Enter path to input HDR video: ").strip()
    if not input_path or not os.path.isfile(input_path):
        print(f"Input file '{input_path}' does not exist.")
        return
    output_path = input("Enter path for output SDR video: ").strip()
    if not output_path:
        print("Output path is required.")
        return
    print("Select tone mapping algorithm:")
    print("  1. hable (default)")
    print("  2. reinhard")
    print("  3. mobius")
    algo_choice = input("Enter algorithm number (1/2/3): ").strip() or "1"
    algo_map = {"1": "hable", "2": "reinhard", "3": "mobius"}
    algorithm = algo_map.get(algo_choice, "hable")
    tonemapper = ToneMapper(algorithm=algorithm)
    tonemapper.run(input_path, output_path)


# --- Dataset Color Adjustment ---
def dataset_colour_adjustment(hq_folder, lq_folder):
    """Adjust color properties of HQ/LQ images using ColorAdjuster class."""
    print("\n" + "=" * 30)
    print("  Dataset Color Adjustment")
    print("=" * 30)
    adjustment_type = (
        input("Enter adjustment type (brightness/contrast/color/sharpness): ")
        .strip()
        .lower()
    )
    try:
        factor = float(input("Enter adjustment factor (e.g., 1.2 for +20%): ").strip())
    except Exception:
        print("Invalid factor. Aborting.")
        return
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
    adjuster = ColorAdjuster(adjustment_type, factor)
    for folder, label in [(hq_folder, "HQ"), (lq_folder, "LQ")]:
        image_files = [
            f
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and is_image_file(f)
        ]
        for filename in tqdm(image_files, desc=f"Adjusting {label}"):
            src_path = os.path.join(folder, filename)
            dest_path = (
                src_path
                if operation == "inplace"
                else os.path.join(dest_dir, get_unique_filename(dest_dir, filename))
            )
            success, msg = adjuster.process(
                src_path, output_path=dest_path, operation=operation
            )
            if not success:
                print(f"Error adjusting {label} {filename}: {msg}")
    print("Adjustment complete.")


# --- Grayscale Conversion ---
def grayscale_conversion(hq_folder, lq_folder):
    """Convert HQ/LQ images to grayscale using ColorAdjuster class."""
    print("\n" + "=" * 30)
    print("  Grayscale Conversion")
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
    for folder, label in [(hq_folder, "HQ"), (lq_folder, "LQ")]:
        image_files = [
            f
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and is_image_file(f)
        ]
        for filename in tqdm(image_files, desc=f"Converting {label}"):
            src_path = os.path.join(folder, filename)
            dest_path = (
                src_path
                if operation == "inplace"
                else os.path.join(dest_dir, get_unique_filename(dest_dir, filename))
            )
            adjuster = ColorAdjuster("color", 0)
            success, msg = adjuster.process(
                src_path, output_path=dest_path, operation=operation
            )
            if not success:
                print(f"Error converting {label} {filename}: {msg}")
    print("Grayscale conversion complete.")


# --- Remove Alpha Channels ---
def remove_alpha_channels(hq_folder, lq_folder):
    """Remove images with alpha channels from HQ/LQ datasets."""
    print("\n" + "=" * 30)
    print("  Removing Images with Alpha Channels")
    print("=" * 30)
    operation = get_file_operation_choice()
    destination = ""
    if operation == "move":
        destination = get_destination_path()
        if not destination:
            print("Operation aborted as no destination path was provided for move.")
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)
    elif operation == "copy":
        destination = get_destination_path()
        if not destination:
            print("Operation aborted as no destination path was provided for copy.")
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)
    removed_count = 0
    checked_count = 0
    errors = []
    for folder, label in [(hq_folder, "HQ"), (lq_folder, "LQ")]:
        files = sorted(
            [
                f
                for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f)) and is_image_file(f)
            ]
        )
        for filename in tqdm(files, desc=f"Checking {label}"):
            path = os.path.join(folder, filename)
            checked_count += 1
            try:
                with Image.open(path) as img:
                    if img.mode in ("RGBA", "LA") or (
                        img.mode == "P" and "transparency" in img.info
                    ):
                        if operation == "inplace":
                            os.remove(path)
                        else:
                            dest_folder = os.path.join(destination, label.lower())
                            dest_path = os.path.join(
                                dest_folder, get_unique_filename(dest_folder, filename)
                            )
                            if operation == "copy":
                                shutil.copy2(path, dest_path)
                            elif operation == "move":
                                shutil.move(path, dest_path)
                        removed_count += 1
            except Exception as e:
                errors.append(f"Error processing {label} {filename}: {e}")
    print("\n" + "-" * 30)
    print("  Remove Alpha Channel Summary")
    print("-" * 30)
    print(f"Checked {checked_count} images.")
    print(f"Processed ({operation}ed) {removed_count} images with alpha channels.")
    if errors:
        print(f"Errors encountered: {len(errors)}")
        for i, error in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors.")
    print("-" * 30)
    print("=" * 30)


# --- Apply Custom Transformations ---
def transform_dataset(hq_folder, lq_folder):
    print("\n" + "=" * 30)
    print("  Transforming Dataset")
    print("=" * 30)
    BATCH_SIZE = 1000
    hq_files_list = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    lq_files_list = sorted(
        [
            f
            for f in os.listdir(lq_folder)
            if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
        ]
    )
    matching_files = [f for f in hq_files_list if f in lq_files_list]
    if not matching_files:
        print("No matching HQ/LQ pairs found for transformation.")
        print("=" * 30)
        return
    files_to_process = get_pairs_to_process(matching_files, operation_name="transform")
    if not files_to_process:
        print("=" * 30)
        return
    num_selected_for_transform = len(files_to_process)
    transform_options = {
        "1": "brightness",
        "2": "contrast",
        "3": "saturation",
        "4": "sharpness",
        "5": "rotate",
        "6": "flip_horizontal",
        "7": "flip_vertical",
        "8": "grayscale",
    }
    print("\nSelect a transformation:")
    for key, value in transform_options.items():
        print(f"  {key}. {value.replace('_', ' ').capitalize()}")
    while True:
        transform_choice = input("Enter the number of your choice: ").strip()
        if transform_choice in transform_options:
            selected_transform = transform_options[transform_choice]
            break
        else:
            print("Invalid choice. Please enter a valid number.")
    value = None
    if selected_transform in ["brightness", "contrast", "saturation", "sharpness"]:
        while True:
            try:
                val_str = input(
                    f"Enter {selected_transform} factor (e.g., 0.5 for half, 1.0 for original, 1.5 for 50% more): "
                ).strip()
                value = float(val_str)
                if value >= 0:
                    break
                else:
                    print("Factor must be non-negative.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    elif selected_transform == "rotate":
        while True:
            try:
                val_str = input(
                    "Enter rotation angle in degrees (e.g., 90, -90, 180). Positive = counter-clockwise: "
                ).strip()
                value = float(val_str)
                break
            except ValueError:
                print("Invalid input. Please enter a number for angle.")
    operation = get_file_operation_choice()
    destination_hq_folder = ""
    destination_lq_folder = ""
    if operation != "inplace":
        output_base_dir_prompt = (
            f"Enter base destination directory for {operation}ed transformed pairs: "
        )
        output_base_dir = (
            get_destination_path(prompt=output_base_dir_prompt)
            if callable(get_destination_path)
            else get_destination_path()
        )
        if not output_base_dir:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        sane_transform_name = selected_transform.replace("_", "-")
        destination_hq_folder = os.path.join(
            output_base_dir, f"transformed_{sane_transform_name}_hq"
        )
        destination_lq_folder = os.path.join(
            output_base_dir, f"transformed_{sane_transform_name}_lq"
        )
        os.makedirs(destination_hq_folder, exist_ok=True)
        os.makedirs(destination_lq_folder, exist_ok=True)
        print(
            f"Transformed pairs will be {operation}d to respective subfolders in {output_base_dir}"
        )
    else:
        print(
            f"Performing '{selected_transform}' transformation in-place on {num_selected_for_transform} selected pairs."
        )
    processed_count = 0
    errors = []
    print(
        f"\nApplying transformation ({selected_transform}) to {num_selected_for_transform} randomly selected and ordered pairs..."
    )
    for batch_start in range(0, len(files_to_process), BATCH_SIZE):
        batch = files_to_process[batch_start : batch_start + BATCH_SIZE]
        print(f"Processing batch {batch_start//BATCH_SIZE+1} ({len(batch)} pairs)...")
        for filename in tqdm(
            batch,
            desc=f"Transforming Pairs ({selected_transform}) [Batch {batch_start//BATCH_SIZE+1}]",
        ):
            hq_src_path = os.path.join(hq_folder, filename)
            lq_src_path = os.path.join(lq_folder, filename)
            hq_dest_path_for_apply = None
            lq_dest_path_for_apply = None
            if operation != "inplace":
                hq_dest_path_for_apply = os.path.join(
                    destination_hq_folder,
                    get_unique_filename(destination_hq_folder, filename),
                )
                lq_dest_path_for_apply = os.path.join(
                    destination_lq_folder,
                    get_unique_filename(destination_lq_folder, filename),
                )
            else:
                hq_dest_path_for_apply = hq_src_path
                lq_dest_path_for_apply = lq_src_path
            hq_success = apply_transformation_to_image(
                hq_src_path,
                selected_transform,
                value,
                operation,
                hq_dest_path_for_apply,
            )
            lq_success = False
            if hq_success or operation != "move":
                lq_success = apply_transformation_to_image(
                    lq_src_path,
                    selected_transform,
                    value,
                    operation,
                    lq_dest_path_for_apply,
                )
            if hq_success and lq_success:
                processed_count += 1
            else:
                err_msg = f"Pair {filename}: "
                if not hq_success:
                    err_msg += f"HQ failed. "
                if not lq_success:
                    err_msg += f"LQ failed."
                errors.append(err_msg)
                logging.warning(
                    f"Failed to fully transform pair {filename}. HQ status: {hq_success}, LQ status: {lq_success}"
                )
    print("\n" + "-" * 30)
    print("  Transform Dataset Summary")
    print("-" * 30)
    print(
        f"Transformation: {selected_transform} (Value: {value if value is not None else 'N/A'})"
    )
    print(f"Operation: {operation.capitalize()}")
    print(f"Total matching pairs in source: {len(matching_files)}")
    print(f"Number of pairs selected for transformation: {num_selected_for_transform}")
    print(f"Successfully transformed: {processed_count} pairs.")
    if errors:
        print(f"Errors or partial failures encountered for {len(errors)} pairs:")
        for i, error_msg in enumerate(errors[: min(len(errors), 5)]):
            print(f"  - {error_msg}")
        if len(errors) > 5:
            print(
                f"  ... and {len(errors) - 5} more issues (check console/log for details)."
            )
    print("-" * 30)
    print("=" * 30)
