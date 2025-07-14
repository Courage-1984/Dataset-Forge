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
from typing import Optional, Tuple
from dataset_forge.actions import exif_scrubber_actions
from dataset_forge.utils.image_ops import AlphaRemover
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
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
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound

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
    remove_alpha: bool = False,
    icc_to_srgb: bool = True,
    run_steg: bool = False,
    steg_tools: Optional[Tuple[bool, bool]] = None,  # (steghide, zsteg)
    dry_run: bool = False,
):
    """
    New sanitize workflow as specified by user, with parallelization for slow steps.
    """
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

    # 1. Fix Image Corruption in-place in input folder(s) (parallel)
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

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
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
    # 2. Copy all image files to temp_folder_A
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
        def batch_rename_sequential(folder):
            files = sorted(
                [
                    f
                    for f in os.listdir(folder)
                    if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)
                ]
            )
            n = len(files)
            padding = len(str(n))
            temp_names = []
            for idx, fname in enumerate(files, 1):
                ext = os.path.splitext(fname)[1].lower()
                new_name = f"{str(idx).zfill(padding)}{ext}"
                temp_names.append((fname, new_name))
            print_info(f"Batch renaming in {folder}...")
            for old, new in tqdm(temp_names, desc=f"Rename {os.path.basename(folder)}"):
                src = os.path.join(folder, old)
                dst = os.path.join(folder, new)
                if not dry_run:
                    os.rename(src, dst)
                else:
                    print_info(f"[Dry run] Would rename {src} -> {dst}")

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
            for idx in range(n):
                for folder, files in zip(tempA_folders, [hq_files, lq_files]):
                    old = files[idx]
                    ext = os.path.splitext(old)[1].lower()
                    new = f"{str(idx+1).zfill(padding)}{ext}"
                    src = os.path.join(folder, old)
                    dst = os.path.join(folder, new)
                    if not dry_run:
                        os.rename(src, dst)
                    else:
                        print_info(f"[Dry run] Would rename {src} -> {dst}")
        else:
            batch_rename_sequential(tempA_folders[0])
        # 4. ICC to sRGB (optional, in-place in tempA, parallel)
        if icc_to_srgb:
            print_info("Running ICC to sRGB conversion in tempA (parallel)...")

            def icc_one(fpath):
                if not dry_run:
                    ICCToSRGBConverter.process_image(fpath, fpath)
                else:
                    print_info(f"[Dry run] Would convert ICC to sRGB: {fpath}")

            for tempA in tempA_folders:
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
        # 5. Format normalization: convert to PNG, save to tempB (parallel)
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
        # 6. Remove transparency (optional, in-place in tempB, parallel)
        if remove_alpha:
            print_info("Removing transparency in tempB (parallel)...")

            def remove_alpha_one(fpath):
                if not dry_run:
                    remover = AlphaRemover()
                    success, result = remover.process(fpath, output_path=fpath)
                    if not success:
                        print_warning(f"Failed to remove alpha from {fpath}: {result}")
                else:
                    print_info(f"[Dry run] Would remove alpha: {fpath}")

            for tempB in tempB_folders:
                files = [
                    os.path.join(tempB, f)
                    for f in os.listdir(tempB)
                    if f.lower().endswith(".png")
                ]
                import threading

                thread = threading.Thread(target=lambda: None)
                task_registry.register_thread(thread)
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=max_workers
                ) as executor:
                    list(
                        tqdm(
                            executor.map(remove_alpha_one, files),
                            total=len(files),
                            desc=f"Remove alpha {os.path.basename(tempB)}",
                        )
                    )
                clear_memory()
                clear_cuda_cache()
        # 7. Metadata removal: oxipng to output (per-file parallel)
        print_info(
            "Running oxipng for metadata removal and final output (per-file parallel)..."
        )
        for idx, (_, out_folder) in enumerate(folders):
            tempB = tempB_folders[idx]
            if not dry_run:
                os.makedirs(out_folder, exist_ok=True)
                parallel_oxipng(tempB, out_folder, dry_run, max_workers)
            else:
                print_info(
                    f"[Dry run] Would run oxipng on all PNGs in {tempB} to {out_folder}"
                )
        # 8. Steganography checks (not parallelized, but could be if needed)
        zsteg_results_file = None
        if run_steg and steg_tools and steg_tools[1]:
            # Create a temp file for zsteg results
            zsteg_results_file = os.path.join(
                tempfile.gettempdir(), f"zsteg_results_{uuid.uuid4().hex[:8]}.txt"
            )
            with open(zsteg_results_file, "w", encoding="utf-8") as f:
                f.write("ZSTEG RESULTS LEGEND:\n")
                f.write("- text: Possible hidden text found in a channel.\n")
                f.write("- file: Possible embedded file signature detected.\n")
                f.write("- No hidden data: No suspicious output.\n")
                f.write("- Stack overflow: zsteg Ruby bug, not a workflow error.\n\n")
        if run_steg:
            print_info("Running steganography checks on output PNGs...")
            for _, out_folder in folders:
                png_files = [
                    f for f in os.listdir(out_folder) if f.lower().endswith(".png")
                ]
                for fname in tqdm(
                    png_files, desc=f"Steg check {os.path.basename(out_folder)}"
                ):
                    fpath = os.path.join(out_folder, fname)
                    if steg_tools and steg_tools[0]:
                        print_info(f"[Steghide] Checking {fpath}")
                        if not dry_run:
                            _run_steghide_check(fpath)
                        else:
                            print_info(f"[Dry run] Would run steghide on {fpath}")
                    if steg_tools and steg_tools[1]:
                        print_info(f"[zsteg] Checking {fpath}")
                        if not dry_run:
                            _run_zsteg_check(
                                fpath, zsteg_results_file=zsteg_results_file
                            )
                        else:
                            print_info(f"[Dry run] Would run zsteg on {fpath}")
    print_success("Sanitization complete.")
    play_done_sound()
    clear_memory()
    clear_cuda_cache()
    if zsteg_results_file:
        return zsteg_results_file
    return None


def _batch_rename_pngs(folder: str, dry_run: bool = False):
    import uuid

    files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".png")])
    padding = 5
    prefix = ""
    if dry_run:
        for idx, filename in enumerate(files, 1):
            ext = ".png"
            new_name = f"{prefix}{str(idx).zfill(padding)}{ext}"
            print(f"Would rename: {filename} -> {new_name}")
        print("Dry run complete. No files were renamed.")
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
    print("Phase 1: Renaming to temporary names...")
    for src, temp_path in tqdm(temp_renames, desc="Temp renaming"):
        os.rename(src, temp_path)
        log_operation("rename_temp", f"{src} -> {temp_path}")
    print("Phase 2: Renaming to final names...")
    for temp_path, final_path in tqdm(final_renames, desc="Final renaming"):
        os.rename(temp_path, final_path)
        log_operation("rename_final", f"{temp_path} -> {final_path}")
    print("Batch renaming complete.")


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
