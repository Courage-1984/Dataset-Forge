"""
Sanitize Images Actions
- Remove all metadata (EXIF, XMP, IPTC) using exiftool
- Convert all images to PNG, optionally remove alpha channel
- Batch rename PNG files to neutral, zero-padded names
- Optionally run steganography checks (steghide/zsteg)
- Write all output to a separate output folder
"""

import os
import shutil
from typing import Optional, Tuple, List
from dataset_forge.actions import exif_scrubber_actions
from dataset_forge.utils.image_ops import AlphaRemover
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
    print_section,
)
from dataset_forge.utils.history_log import log_operation
import tempfile
import shutil
import subprocess
from PIL import Image
import cv2
from dataset_forge.utils.image_ops import ICCToSRGBConverter
import concurrent.futures
import uuid
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.input_utils import ask_yes_no
from dataset_forge.utils.color import Mocha

import subprocess
from PIL import Image
import os


def remove_metadata(input_path: str, output_path: str) -> bool:
    """
    Remove all metadata from an image using exiftool.

    Args:
        input_path: Path to the input image file
        output_path: Path to the output image file

    Returns:
        True if successful, False otherwise
    """
    cmd = ["exiftool", "-all=", "-o", output_path, input_path]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception:
        return False


def convert_to_png(input_path: str, output_path: str) -> bool:
    """
    Convert an image to PNG format.

    Args:
        input_path: Path to the input image file
        output_path: Path to the output PNG file

    Returns:
        True if successful, False otherwise
    """
    try:
        with Image.open(input_path) as img:
            img.save(output_path, format="PNG")
        return True
    except Exception:
        return False


def remove_alpha(input_path: str, output_path: str) -> bool:
    """
    Remove the alpha channel from a PNG image.

    Args:
        input_path: Path to the input PNG file
        output_path: Path to the output PNG file (no alpha)

    Returns:
        True if successful, False otherwise
    """
    try:
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "LA"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                bg.save(output_path, format="PNG")
            else:
                img.save(output_path, format="PNG")
        return True
    except Exception as e:
        print_error(f"remove_alpha failed: {e}")
        return False


def run_steghide_check(input_path: str) -> dict:
    """
    Run steghide to check for hidden data in an image.

    Args:
        input_path: Path to the image file

    Returns:
        Dictionary with steghide output or error
    """
    cmd = ["steghide", "info", input_path]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        return {"result": result.stdout}
    except Exception as e:
        return {"error": str(e)}


def run_zsteg_check(input_path: str) -> dict:
    """
    Run zsteg to check for hidden data in a PNG image.

    Args:
        input_path: Path to the PNG file

    Returns:
        Dictionary with zsteg output or error
    """
    cmd = ["zsteg", input_path]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        return {"result": result.stdout}
    except Exception as e:
        return {"error": str(e)}


SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp")


def run_oxipng_on_file(src, dst, dry_run=False):
    cmd = ["oxipng", "--opt", "3", "--strip", "all", "--out", dst, src]
    if dry_run:
        print_info(f"[Dry run] Would run: {' '.join(cmd)}")
        return
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print_warning(f"oxipng failed for {src}: {e}")


def parallel_oxipng(tempB_folder, out_folder, dry_run=False, max_workers=None):
    files = [f for f in os.listdir(tempB_folder) if f.lower().endswith(".png")]
    args = []
    for fname in files:
        src = os.path.join(tempB_folder, fname)
        dst = os.path.join(out_folder, fname)
        args.append((src, dst, dry_run))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(
            tqdm(
                executor.map(lambda x: run_oxipng_on_file(*x), args),
                total=len(args),
                desc="oxipng",
            )
        )


def _parse_zsteg_output(stdout: str, stderr: str) -> Tuple[str, str]:
    """
    Parse zsteg output and return (summary, full_output).
    Summary is a human-friendly one-line result for CLI.
    Full_output is the raw output for the temp file.
    """
    import re

    # Detect stack overflow or Ruby errors
    if (
        "stack level too deep" in stdout
        or "SystemStackError" in stdout
        or "stack level too deep" in stderr
        or "SystemStackError" in stderr
    ):
        return (
            "Stack overflow (zsteg Ruby bug, see details in results file)",
            stdout + "\n" + stderr,
        )
    if "zsteg not found" in stderr.lower():
        return ("[zsteg] Not found in PATH.", stdout + "\n" + stderr)
    # Summarize findings
    text_lines = []
    file_lines = []
    file_types = set()
    for line in stdout.splitlines():
        if "text:" in line:
            text_lines.append(line.strip())
        elif "file:" in line:
            file_lines.append(line.strip())
            # Try to extract file type after 'file:'
            m = re.search(r"file: (.+)$", line)
            if m:
                file_types.add(m.group(1).strip())
    summary_parts = []
    if text_lines:
        n = len(text_lines)
        shown = text_lines[:2]
        summary = f"Hidden text found in {n} channel{'s' if n > 1 else ''}"
        if n > 2:
            summary += f" (e.g. {', '.join(shown)[:60]}... +{n-2} more)"
        else:
            summary += f" (e.g. {', '.join(shown)[:60]})"
        summary_parts.append(summary)
    if file_types:
        types_list = list(file_types)
        shown_types = types_list[:2]
        summary = f"Embedded file signature detected ({', '.join(shown_types)[:60]}"
        if len(types_list) > 2:
            summary += f", +{len(types_list)-2} more)"
        else:
            summary += ")"
        summary_parts.append(summary)
    if not summary_parts:
        if stdout.strip():
            return ("No suspicious hidden data detected.", stdout + "\n" + stderr)
        else:
            return ("No suspicious hidden data detected.", stdout + "\n" + stderr)
    return ("; ".join(summary_parts), stdout + "\n" + stderr)


def _run_zsteg_check(image_path: str, zsteg_results_file=None):
    import subprocess
    import re
    import shutil

    zsteg_path = shutil.which("zsteg")
    if not zsteg_path:
        msg = "zsteg not found in PATH."
        print_error(msg)
        if zsteg_results_file:
            with open(zsteg_results_file, "a", encoding="utf-8") as f:
                f.write(f"{image_path}: {msg}\n\n")
        return
    try:
        result = subprocess.run(
            [zsteg_path, image_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        # Remove ANSI color codes if present
        stdout = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
        stderr = re.sub(r"\x1b\[[0-9;]*m", "", result.stderr)
        summary, full_output = _parse_zsteg_output(stdout, stderr)
        print_info(f"[zsteg] {os.path.basename(image_path)}: {summary}")
        if zsteg_results_file:
            with open(zsteg_results_file, "a", encoding="utf-8") as f:
                f.write(f"===== {image_path} =====\n{full_output}\n\n")
    except FileNotFoundError:
        msg = "zsteg not found in PATH."
        print_error(msg)
        if zsteg_results_file:
            with open(zsteg_results_file, "a", encoding="utf-8") as f:
                f.write(f"{image_path}: {msg}\n\n")
    except subprocess.CalledProcessError as e:
        msg = f"[zsteg] CalledProcessError for {image_path}: {e}"
        print_error(msg)
        if zsteg_results_file:
            with open(zsteg_results_file, "a", encoding="utf-8") as f:
                f.write(f"{image_path}: {msg}\n\n")
    except Exception as e:
        msg = f"[zsteg] Exception for {image_path}: {e}"
        print_error(msg)
        if zsteg_results_file:
            with open(zsteg_results_file, "a", encoding="utf-8") as f:
                f.write(f"{image_path}: {msg}\n\n")


@monitor_all("sanitize_images", critical_on_error=True)
def sanitize_images(
    input_path: str,
    output_folder: str,
    dry_run: bool = False,
):
    """
    Interactive sanitize workflow: prompts for each step, tracks run/skipped, returns summary dict.
    """
    from dataset_forge.utils.printing import (
        print_section,
        print_info,
        print_success,
        print_warning,
        print_error,
    )
    from dataset_forge.utils.input_utils import ask_yes_no
    import tempfile, os, shutil, concurrent.futures, uuid
    from PIL import Image
    from dataset_forge.utils.image_ops import ICCToSRGBConverter, AlphaRemover
    from dataset_forge.utils.progress_utils import tqdm
    from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
    from dataset_forge.utils.audio_utils import play_done_sound
    from dataset_forge.actions import exif_scrubber_actions
    from dataset_forge.utils.history_log import log_operation
    from dataset_forge.actions.sanitize_images_actions import (
        run_oxipng_on_file,
        parallel_oxipng,
        _run_steghide_check,
        _run_zsteg_check,
    )

    summary = {}
    max_workers = os.cpu_count() or 4
    hq_path = os.path.join(input_path, "hq")
    lq_path = os.path.join(input_path, "lq")
    is_pair = os.path.isdir(hq_path) and os.path.isdir(lq_path)
    if is_pair:
        print_info(f"Detected HQ/LQ folders: {hq_path}, {lq_path}")
        folders = [
            (hq_path, os.path.join(output_folder, "hq")),
            (lq_path, os.path.join(output_folder, "lq")),
        ]
    else:
        print_info(f"Detected single folder: {input_path}")
        folders = [(input_path, output_folder)]

    # 1. Fix Image Corruption
    print_section("🩹 Fix Image Corruption", char="-", color=Mocha.yellow)
    fix_corruption = ask_yes_no(
        "Fix image corruption in-place in input folder(s)?", default=False
    )
    summary["🩹 Fix Corruption"] = "Run" if fix_corruption else "Skipped"
    if fix_corruption:

        def fix_corruption_inplace(folder):
            files = [
                f
                for f in os.listdir(folder)
                if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)
            ]
            print_info(f"Fixing image corruption in-place in {folder} (parallel)...")
            import threading

            thread = threading.Thread(target=lambda: None)
            task_registry.register_thread(thread)

            def fix_one(fpath):
                try:
                    img = cv2.imread(fpath)
                    if img is not None:
                        cv2.imwrite(fpath, img)
                    else:
                        print_warning(f"Could not read {fpath} with OpenCV.")
                except Exception as e:
                    print_warning(f"Error fixing {fpath}: {e}")

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                list(
                    tqdm(
                        executor.map(fix_one, [os.path.join(folder, f) for f in files]),
                        total=len(files),
                        desc=f"Fix corruption {os.path.basename(folder)}",
                    )
                )
            clear_memory()
            clear_cuda_cache()

        for in_folder, _ in folders:
            if not dry_run:
                fix_corruption_inplace(in_folder)
            else:
                print_info(f"[Dry run] Would fix corruption in {in_folder}")
    else:
        print_info("Skipping image corruption fix.")

    # 2. Copy to Temp
    print_section("📂 Copy Images to Temp Folder", char="-", color=Mocha.lavender)
    copy_to_temp = ask_yes_no("Copy all image files to temp folder?", default=False)
    summary["📂 Copy to Temp"] = "Run" if copy_to_temp else "Skipped"
    if not copy_to_temp:
        print_info("Skipping copy to temp folder and all subsequent steps.")
        return summary
    with tempfile.TemporaryDirectory() as temp_root:
        tempA_folders = []
        for in_folder, _ in folders:
            tempA = os.path.join(temp_root, os.path.basename(in_folder) + "_A")
            tempA_folders.append(tempA)
            if not dry_run:
                os.makedirs(tempA, exist_ok=True)
            files = [
                f
                for f in os.listdir(in_folder)
                if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)
            ]
            for fname in tqdm(files, desc=f"Copy to tempA {os.path.basename(tempA)}"):
                src = os.path.join(in_folder, fname)
                dst = os.path.join(tempA, fname)
                if not dry_run:
                    shutil.copy2(src, dst)
                else:
                    print_info(f"[Dry run] Would copy {src} -> {dst}")
        # 3. Batch rename in tempA (strictly sequential, zero-padded, HQ/LQ aligned)
        print_section("🔢 Batch Rename Images", char="-", color=Mocha.sapphire)
        batch_rename = ask_yes_no("Batch rename images in tempA?", default=False)
        summary["🔢 Batch Rename"] = "Run" if batch_rename else "Skipped"
        if batch_rename:

            def batch_rename_sequential(folder):
                if not os.path.exists(folder):
                    print_warning(f"Folder does not exist: {folder}")
                    return
                files = sorted(
                    [
                        f
                        for f in os.listdir(folder)
                        if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)
                    ]
                )
                n = len(files)
                padding = len(str(n))

                # Two-phase approach: first rename all to temporary names, then to final names
                temp_renames = []
                final_renames = []

                # Phase 1: Create temporary names and plan final names
                for idx, filename in enumerate(files, 1):
                    ext = os.path.splitext(filename)[1].lower()
                    final_name = f"{str(idx).zfill(padding)}{ext}"
                    temp_name = f"temp_{uuid.uuid4().hex[:12]}{ext}"

                    src = os.path.join(folder, filename)
                    temp_path = os.path.join(folder, temp_name)
                    final_path = os.path.join(folder, final_name)

                    temp_renames.append((src, temp_path))
                    final_renames.append((temp_path, final_path))

                print_info(f"Batch renaming in {folder}...")

                # Phase 2: Execute temporary renames
                for src, temp_path in tqdm(
                    temp_renames, desc=f"Rename to temp {os.path.basename(folder)}"
                ):
                    if not dry_run:
                        try:
                            os.rename(src, temp_path)
                        except FileExistsError:
                            # If temp file exists, use a unique name
                            base, ext = os.path.splitext(temp_path)
                            counter = 1
                            while os.path.exists(temp_path):
                                temp_path = os.path.join(
                                    folder, f"{base}_{counter}{ext}"
                                )
                                counter += 1
                            os.rename(src, temp_path)
                    else:
                        print_info(f"[Dry run] Would rename {src} -> {temp_path}")

                # Phase 3: Execute final renames
                for temp_path, final_path in tqdm(
                    final_renames, desc=f"Rename to final {os.path.basename(folder)}"
                ):
                    if not dry_run:
                        try:
                            os.rename(temp_path, final_path)
                        except FileExistsError:
                            # If final name exists, use a unique name
                            base, ext = os.path.splitext(final_path)
                            counter = 1
                            while os.path.exists(final_path):
                                final_path = os.path.join(
                                    folder, f"{base}_{counter}{ext}"
                                )
                                counter += 1
                            os.rename(temp_path, final_path)
                    else:
                        print_info(
                            f"[Dry run] Would rename {temp_path} -> {final_path}"
                        )

            if is_pair:
                hq_files = sorted(
                    [
                        f
                        for f in os.listdir(tempA_folders[0])
                        if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)
                    ]
                )
                lq_files = sorted(
                    [
                        f
                        for f in os.listdir(tempA_folders[1])
                        if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)
                    ]
                )
                n = min(len(hq_files), len(lq_files))
                padding = len(str(n))

                # Two-phase approach for HQ/LQ folders
                hq_temp_renames = []
                lq_temp_renames = []
                hq_final_renames = []
                lq_final_renames = []

                # Phase 1: Create temporary names and plan final names
                for idx, filename in enumerate(hq_files[:n], 1):
                    ext = os.path.splitext(filename)[1].lower()
                    final_name = f"{str(idx).zfill(padding)}{ext}"
                    temp_name = f"temp_{uuid.uuid4().hex[:12]}{ext}"

                    hq_src = os.path.join(tempA_folders[0], filename)
                    lq_src = os.path.join(tempA_folders[1], filename)
                    hq_temp_path = os.path.join(tempA_folders[0], temp_name)
                    lq_temp_path = os.path.join(tempA_folders[1], temp_name)
                    hq_final_path = os.path.join(tempA_folders[0], final_name)
                    lq_final_path = os.path.join(tempA_folders[1], final_name)

                    hq_temp_renames.append((hq_src, hq_temp_path))
                    lq_temp_renames.append((lq_src, lq_temp_path))
                    hq_final_renames.append((hq_temp_path, hq_final_path))
                    lq_final_renames.append((lq_temp_path, lq_final_path))

                # Phase 2: Execute temporary renames
                print_info("Phase 1: Renaming to temporary names...")
                for hq_src, hq_temp_path in hq_temp_renames:
                    if not dry_run:
                        try:
                            os.rename(hq_src, hq_temp_path)
                        except FileExistsError:
                            # If temp file exists, use a unique name
                            base, ext = os.path.splitext(hq_temp_path)
                            counter = 1
                            while os.path.exists(hq_temp_path):
                                hq_temp_path = os.path.join(
                                    tempA_folders[0], f"{base}_{counter}{ext}"
                                )
                                counter += 1
                            os.rename(hq_src, hq_temp_path)
                    else:
                        print_info(f"[Dry run] Would rename {hq_src} -> {hq_temp_path}")

                for lq_src, lq_temp_path in lq_temp_renames:
                    if not dry_run:
                        try:
                            os.rename(lq_src, lq_temp_path)
                        except FileExistsError:
                            # If temp file exists, use a unique name
                            base, ext = os.path.splitext(lq_temp_path)
                            counter = 1
                            while os.path.exists(lq_temp_path):
                                lq_temp_path = os.path.join(
                                    tempA_folders[1], f"{base}_{counter}{ext}"
                                )
                                counter += 1
                            os.rename(lq_src, lq_temp_path)
                    else:
                        print_info(f"[Dry run] Would rename {lq_src} -> {lq_temp_path}")

                # Phase 3: Execute final renames
                print_info("Phase 2: Renaming to final names...")
                for hq_temp_path, hq_final_path in hq_final_renames:
                    if not dry_run:
                        try:
                            os.rename(hq_temp_path, hq_final_path)
                        except FileExistsError:
                            # If final name exists, use a unique name
                            base, ext = os.path.splitext(hq_final_path)
                            counter = 1
                            while os.path.exists(hq_final_path):
                                hq_final_path = os.path.join(
                                    tempA_folders[0], f"{base}_{counter}{ext}"
                                )
                                counter += 1
                            os.rename(hq_temp_path, hq_final_path)
                    else:
                        print_info(
                            f"[Dry run] Would rename {hq_temp_path} -> {hq_final_path}"
                        )

                for lq_temp_path, lq_final_path in lq_final_renames:
                    if not dry_run:
                        try:
                            os.rename(lq_temp_path, lq_final_path)
                        except FileExistsError:
                            # If final name exists, use a unique name
                            base, ext = os.path.splitext(lq_final_path)
                            counter = 1
                            while os.path.exists(lq_final_path):
                                lq_final_path = os.path.join(
                                    tempA_folders[1], f"{base}_{counter}{ext}"
                                )
                                counter += 1
                            os.rename(lq_temp_path, lq_final_path)
                    else:
                        print_info(
                            f"[Dry run] Would rename {lq_temp_path} -> {lq_final_path}"
                        )
            else:
                batch_rename_sequential(tempA_folders[0])
        else:
            print_info("Skipping batch rename.")
        # 4. ICC to sRGB
        print_section("🎨 ICC to sRGB Conversion", char="-", color=Mocha.green)
        icc_to_srgb = ask_yes_no("Run ICC to sRGB conversion?", default=False)
        summary["🎨 ICC to sRGB"] = "Run" if icc_to_srgb else "Skipped"
        if icc_to_srgb:
            print_info("Running ICC to sRGB conversion in tempA (parallel)...")

            def icc_one(fpath):
                if not dry_run:
                    ICCToSRGBConverter.process_image(fpath, fpath)
                else:
                    print_info(f"[Dry run] Would convert ICC to sRGB: {fpath}")

            for tempA in tempA_folders:
                if not os.path.exists(tempA):
                    print_warning(f"Folder does not exist: {tempA}")
                    continue
                files = [
                    os.path.join(tempA, f)
                    for f in os.listdir(tempA)
                    if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)
                ]
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=max_workers
                ) as executor:
                    list(
                        tqdm(
                            executor.map(icc_one, files),
                            total=len(files),
                            desc=f"ICC to sRGB {os.path.basename(tempA)}",
                        )
                    )
        else:
            print_info("Skipping ICC to sRGB conversion.")
        # 5. Format normalization: convert to PNG, save to tempB (parallel)
        print_section("🖼️  Convert to PNG", char="-", color=Mocha.blue)
        to_png = ask_yes_no("Convert images to PNG format?", default=False)
        summary["🖼️  Convert to PNG"] = "Run" if to_png else "Skipped"
        if to_png:
            tempB_folders = []

            def to_png_one(args):
                src, dst = args
                if not dry_run:
                    try:
                        with Image.open(src) as img:
                            img.save(dst, format="PNG")
                    except Exception as e:
                        print_warning(f"Failed to convert {src} to PNG: {e}")
                else:
                    print_info(f"[Dry run] Would convert {src} -> {dst}")

            for tempA in tempA_folders:
                tempB = tempA + "_B"
                tempB_folders.append(tempB)
                if not dry_run:
                    os.makedirs(tempB, exist_ok=True)
                if not os.path.exists(tempA):
                    print_warning(f"Folder does not exist: {tempA}")
                    continue
                files = [
                    f
                    for f in os.listdir(tempA)
                    if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)
                ]
                args_list = [
                    (
                        os.path.join(tempA, fname),
                        os.path.join(tempB, os.path.splitext(fname)[0] + ".png"),
                    )
                    for fname in files
                ]
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=max_workers
                ) as executor:
                    list(
                        tqdm(
                            executor.map(to_png_one, args_list),
                            total=len(args_list),
                            desc=f"To PNG {os.path.basename(tempB)}",
                        )
                    )
        else:
            print_info("Skipping PNG conversion.")
        # 6. Remove transparency (optional, in-place in tempB, parallel)
        print_section("🧊 Remove Transparency (Alpha)", char="-", color=Mocha.teal)
        remove_alpha = ask_yes_no("Remove transparency (alpha channel)?", default=False)
        summary["🧊 Remove Alpha"] = "Run" if remove_alpha else "Skipped"
        if remove_alpha:
            print_info("🔍 First, scanning for images with alpha channels...")

            def remove_alpha_one(fpath):
                if not dry_run:
                    remover = AlphaRemover()
                    success, result = remover.process(fpath, output_path=fpath)
                    if not success:
                        # Check if this is just an informational message about no alpha channel
                        if (
                            "No alpha channel to remove" in result
                            and "already processed" in result
                        ):
                            print_info(f"✓ {os.path.basename(fpath)}: {result}")
                        else:
                            print_warning(
                                f"Failed to remove alpha from {fpath}: {result}"
                            )
                    else:
                        print_success(f"✓ Removed alpha from {os.path.basename(fpath)}")
                else:
                    print_info(f"[Dry run] Would remove alpha: {fpath}")

            for tempB in tempB_folders:
                if not os.path.exists(tempB):
                    print_warning(f"Folder does not exist: {tempB}")
                    continue

                # First, scan for images with alpha channels
                print_info(
                    f"🔍 Scanning {os.path.basename(tempB)} for images with alpha channels..."
                )
                images_with_alpha = find_images_with_alpha(tempB)

                if not images_with_alpha:
                    print_success(
                        f"✓ No images with alpha channels found in {os.path.basename(tempB)}"
                    )
                    continue

                print_success(
                    f"✓ Found {len(images_with_alpha)} images with alpha channels in {os.path.basename(tempB)}"
                )

                # Show the files that will be processed
                if not dry_run:
                    print_info("📋 Images to process:")
                    for img_path in images_with_alpha:
                        print_info(f"  • {os.path.basename(img_path)}")

                # Now process only the images with alpha channels
                print_info(
                    f"🧊 Removing alpha channels from {len(images_with_alpha)} images..."
                )

                import threading

                thread = threading.Thread(target=lambda: None)
                task_registry.register_thread(thread)
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=max_workers
                ) as executor:
                    list(
                        tqdm(
                            executor.map(remove_alpha_one, images_with_alpha),
                            total=len(images_with_alpha),
                            desc=f"Remove alpha {os.path.basename(tempB)}",
                        )
                    )
                clear_memory()
                clear_cuda_cache()
        else:
            print_info("Skipping alpha removal.")
        # 7. Metadata removal: oxipng to output (per-file parallel)
        print_section("🗑️  Remove Metadata (oxipng)", char="-", color=Mocha.peach)
        remove_metadata = ask_yes_no("Remove metadata (oxipng)?", default=False)
        summary["🗑️  Remove Metadata"] = "Run" if remove_metadata else "Skipped"
        if remove_metadata:
            print_info(
                "Running oxipng for metadata removal and final output (per-file parallel)..."
            )
            for idx, (_, out_folder) in enumerate(folders):
                tempB = tempB_folders[idx]
                if not dry_run:
                    os.makedirs(out_folder, exist_ok=True)
                    parallel_oxipng(tempB, out_folder, dry_run, max_workers)
                else:
                    if not os.path.exists(tempB):
                        print_warning(f"Folder does not exist: {tempB}")
                        continue
                    print_info(
                        f"[Dry run] Would run oxipng on all PNGs in {tempB} to {out_folder}"
                    )
        else:
            print_info("Skipping metadata removal.")
        # 8. Steganography checks (not parallelized, but could be if needed)
        print_section("🕵️  Steganography Checks", char="-", color=Mocha.mauve)
        run_steg = ask_yes_no(
            "Run steganography checks (steghide/zsteg)?", default=False
        )
        steghide_choice = False
        zsteg_choice = False
        zsteg_results_file = None
        if run_steg:
            steghide_choice = ask_yes_no(
                "Use steghide for steganography checks?", default=False
            )
            zsteg_choice = ask_yes_no(
                "Use zsteg for steganography checks?", default=True
            )
            summary["🕵️  Steganography"] = (
                f"steghide: {'Run' if steghide_choice else 'Skipped'}, zsteg: {'Run' if zsteg_choice else 'Skipped'}"
            )
            if not (steghide_choice or zsteg_choice):
                print_info("Skipping steganography checks (no tool selected).")
            else:
                if zsteg_choice:
                    zsteg_results_file = os.path.join(
                        tempfile.gettempdir(),
                        f"zsteg_results_{uuid.uuid4().hex[:8]}.txt",
                    )
                    with open(zsteg_results_file, "w", encoding="utf-8") as f:
                        f.write("ZSTEG RESULTS LEGEND:\n")
                        f.write("- text: Possible hidden text found in a channel.\n")
                        f.write("- file: Possible embedded file signature detected.\n")
                        f.write("- No hidden data: No suspicious output.\n")
                        f.write(
                            "- Stack overflow: zsteg Ruby bug, not a workflow error.\n\n"
                        )
                print_info("Running steganography checks on output PNGs...")
                for _, out_folder in folders:
                    if not os.path.exists(out_folder):
                        print_warning(f"Folder does not exist: {out_folder}")
                        continue
                    png_files = [
                        f for f in os.listdir(out_folder) if f.lower().endswith(".png")
                    ]
                    for fname in tqdm(
                        png_files, desc=f"Steg check {os.path.basename(out_folder)}"
                    ):
                        fpath = os.path.join(out_folder, fname)
                        if steghide_choice:
                            print_info(f"[Steghide] Checking {fpath}")
                            if not dry_run:
                                _run_steghide_check(fpath)
                            else:
                                print_info(f"[Dry run] Would run steghide on {fpath}")
                        if zsteg_choice:
                            print_info(f"[zsteg] Checking {fpath}")
                            if not dry_run:
                                _run_zsteg_check(
                                    fpath, zsteg_results_file=zsteg_results_file
                                )
                            else:
                                print_info(f"[Dry run] Would run zsteg on {fpath}")
        else:
            summary["🕵️  Steganography"] = "steghide: Skipped, zsteg: Skipped"
            print_info("Skipping steganography checks.")
        if zsteg_results_file:
            summary["📄 Zsteg results file"] = zsteg_results_file
        print_success("Sanitization complete.")
        play_done_sound()
        clear_memory()
        clear_cuda_cache()
        return summary


def _batch_rename_pngs(folder: str, dry_run: bool = False):
    import uuid

    files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".png")])
    padding = 5
    prefix = ""
    if dry_run:
        for idx, filename in enumerate(files, 1):
            ext = ".png"
            new_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
        print_info(f"Would rename: {filename} -> {new_name}")
    print_info("Dry run complete. No files were renamed.")
    return
    temp_renames = []
    final_renames = []
    for idx, filename in enumerate(files, 1):
        ext = ".png"
        final_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
        temp_name = f"temp_{uuid.uuid4().hex[:12]}{ext}"
        src = os.path.join(folder, filename)
        temp_path = os.path.join(folder, temp_name)
        final_path = os.path.join(folder, final_name)
        temp_renames.append((src, temp_path))
        final_renames.append((temp_path, final_path))
    print_info("Phase 1: Renaming to temporary names...")
    for src, temp_path in tqdm(temp_renames, desc="Temp renaming"):
        os.rename(src, temp_path)
        log_operation("rename_temp", f"{src} -> {temp_path}")
    print_info("Phase 2: Renaming to final names...")
    for temp_path, final_path in tqdm(final_renames, desc="Final renaming"):
        os.rename(temp_path, final_path)
        log_operation("rename_final", f"{temp_path} -> {final_path}")
    print_info("Batch renaming complete.")


def has_alpha_channel(image_path: str) -> bool:
    """Check if an image has an alpha channel.

    Args:
        image_path: Path to the image file

    Returns:
        True if the image has an alpha channel, False otherwise
    """
    try:
        from PIL import Image

        with Image.open(image_path) as img:
            return img.mode.endswith("A")
    except Exception as e:
        print_warning(f"Error checking alpha channel for {image_path}: {e}")
        return False


def find_images_with_alpha(folder_path: str) -> List[str]:
    """Find all images with alpha channels in a folder.

    Args:
        folder_path: Path to the folder to search

    Returns:
        List of image paths that have alpha channels
    """
    images_with_alpha = []
    if not os.path.exists(folder_path):
        return images_with_alpha

    # Get all image files first
    image_files = [
        file
        for file in os.listdir(folder_path)
        if file.lower().endswith((".png", ".tiff", ".bmp", ".gif"))
    ]

    if not image_files:
        return images_with_alpha

    # Scan with progress bar
    for file in tqdm(image_files, desc="Scanning for alpha channels"):
        image_path = os.path.join(folder_path, file)
        if has_alpha_channel(image_path):
            images_with_alpha.append(image_path)

    return images_with_alpha


def _run_steghide_check(image_path: str):
    import subprocess
    import re
    import os

    # Only run steghide on supported formats
    SUPPORTED_STEGHIDE_EXTS = (".bmp", ".au", ".wav", ".jpg", ".jpeg")
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in SUPPORTED_STEGHIDE_EXTS:
        print_info(
            f"[Steghide] Skipping {image_path} (unsupported format for steghide)"
        )
        return
    try:
        result = subprocess.run(
            ["steghide", "info", image_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        # Remove ANSI color codes if present
        stdout = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
        stderr = re.sub(r"\x1b\[[0-9;]*m", "", result.stderr)
        if result.returncode == 0:
            if "embedded data" in stdout.lower():
                print_warning(f"[Steghide] Possible hidden data in {image_path}:")
                print_info(stdout.strip())
            else:
                print_success(f"[Steghide] No hidden data in {image_path}")
        else:
            print_warning(f"[Steghide] Error for {image_path}: {stderr.strip()}")
    except FileNotFoundError:
        print_error("Steghide not found in PATH.")
    except subprocess.CalledProcessError as e:
        print_error(f"[Steghide] CalledProcessError for {image_path}: {e}")
    except Exception as e:
        print_error(f"[Steghide] Exception for {image_path}: {e}")


# zsteg is always run for PNGs, as it is designed for that format.
