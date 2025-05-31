import os
import random
import shutil
from PIL import Image, ImageEnhance, UnidentifiedImageError, ImageFont, ImageDraw
from collections import Counter, defaultdict
from tqdm import tqdm
import cv2
import numpy as np
import concurrent.futures
import logging
import sys
import traceback
import imageio
import torch
from dataset_forge.io_utils_old import (
    log_uncaught_exceptions,
    get_folder_path,
    get_file_operation_choice,
    get_destination_path,
    get_pairs_to_process,
    is_image_file,
    IMAGE_TYPES,
)
from dataset_forge.analysis import (
    find_hq_lq_scale,
    test_hq_lq_scale,
    check_consistency,
    report_dimensions,
    find_extreme_dimensions,
    verify_images,
    find_misaligned_images,
    generate_hq_lq_dataset_report,
)
from dataset_forge.operations import (
    remove_small_image_pairs,
    extract_random_pairs,
    shuffle_image_pairs,
    transform_dataset,
    dataset_colour_adjustment,
    grayscale_conversion,
    split_adjust_dataset,
    optimize_png_menu,
    convert_to_webp_menu,
)
from dataset_forge.common import get_unique_filename
from dataset_forge.combine import combine_datasets
from dataset_forge.alpha import find_alpha_channels, remove_alpha_channels
from dataset_forge.comparison import create_comparison_images, create_gif_comparison
from dataset_forge.corruption import fix_corrupted_images
from dataset_forge.tiling import (
    tile_dataset_menu,
    tile_hq_lq_dataset,
    tile_aligned_pairs,
    tile_images,
)
from dataset_forge.frames import extract_frames_menu
from subprocess import run, CalledProcessError
import subprocess
import yaml
import re
import gc


# --- Catppuccin Mocha ANSI Color Helper ---
class Mocha:
    # Catppuccin Mocha palette (https://catppuccin.com/palette/mocha)
    rosewater = "\033[38;2;245;224;220m"
    flamingo = "\033[38;2;242;205;205m"
    pink = "\033[38;2;245;194;231m"
    mauve = "\033[38;2;203;166;247m"
    red = "\033[38;2;243;139;168m"
    maroon = "\033[38;2;235;160;172m"
    peach = "\033[38;2;250;179;135m"
    yellow = "\033[38;2;249;226;175m"
    green = "\033[38;2;166;227;161m"
    teal = "\033[38;2;148;226;213m"
    sky = "\033[38;2;137;220;235m"
    sapphire = "\033[38;2;116;199;236m"
    blue = "\033[38;2;137;180;250m"
    lavender = "\033[38;2;180;190;254m"
    text = "\033[38;2;205;214;244m"
    subtext1 = "\033[38;2;186;194;222m"
    subtext0 = "\033[38;2;166;173;200m"
    overlay2 = "\033[38;2;147;153;178m"
    overlay1 = "\033[38;2;127;132;156m"
    overlay0 = "\033[38;2;108;112;134m"
    surface2 = "\033[38;2;88;91;112m"
    surface1 = "\033[38;2;69;71;90m"
    surface0 = "\033[38;2;49;50;68m"
    base = "\033[38;2;30;30;46m"
    mantle = "\033[38;2;24;24;37m"
    crust = "\033[38;2;17;17;27m"
    reset = "\033[0m"
    bold = "\033[1m"
    underline = "\033[4m"


# --- Print helpers using Catppuccin Mocha ---
def print_header(title, char="#", color=Mocha.mauve):
    print(color + Mocha.bold + char * 50 + Mocha.reset)
    print(color + Mocha.bold + f"{title.center(50)}" + Mocha.reset)
    print(color + Mocha.bold + char * 50 + Mocha.reset)


def print_section(title, char="-", color=Mocha.sapphire):
    print(color + char * 40 + Mocha.reset)
    print(color + Mocha.bold + f"{title.center(40)}" + Mocha.reset)
    print(color + char * 40 + Mocha.reset)


def print_success(msg):
    print(Mocha.green + Mocha.bold + "✔ " + msg + Mocha.reset)


def print_warning(msg):
    print(Mocha.peach + Mocha.bold + "! " + msg + Mocha.reset)


def print_error(msg):
    print(Mocha.red + Mocha.bold + "✖ " + msg + Mocha.reset)


def print_info(msg):
    print(Mocha.sky + msg + Mocha.reset)


def print_prompt(msg):
    print(Mocha.yellow + msg + Mocha.reset, end="")


def release_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def main_menu():
    hq_folder = ""
    lq_folder = ""
    config = None
    config_path = None

    def input_with_cancel(prompt):
        val = input(prompt)
        if val.strip().lower() == "cancel":
            print("Returning to main menu...")
            raise KeyboardInterrupt("User cancelled to main menu")
        return val

    def extract_val_paths_from_yml(yml_path):
        if not yml_path or not os.path.isfile(yml_path):
            return None, None
        try:
            with open(yml_path, "r") as f:
                yml_data = yaml.safe_load(f)
            val = yml_data.get("datasets", {}).get("val", {})
            val_hq = None
            val_lq = None
            if isinstance(val, dict):
                gt = val.get("dataroot_gt")
                lq = val.get("dataroot_lq")
                if isinstance(gt, list) and gt:
                    val_hq = gt[0]
                elif isinstance(gt, str):
                    val_hq = gt
                if isinstance(lq, list) and lq:
                    val_lq = lq[0]
                elif isinstance(lq, str):
                    val_lq = lq
            return val_hq, val_lq
        except Exception as e:
            print(f"Warning: Could not parse .yml for Val Dataset paths: {e}")
            return None, None

    def extract_model_dir_from_yml(yml_path):
        if not yml_path or not os.path.isfile(yml_path):
            return None, None, None
        try:
            with open(yml_path, "r") as f:
                yml_data = yaml.safe_load(f)
            name = yml_data.get("name")
            # Try to find the experiments dir by walking up from yml_path
            yml_dir = os.path.dirname(yml_path)
            exp_dir = None
            for _ in range(4):
                candidate = os.path.join(yml_dir, "experiments")
                if os.path.isdir(candidate):
                    exp_dir = candidate
                    break
                yml_dir = os.path.dirname(yml_dir)
            if not name or not exp_dir:
                return name, None, []
            model_dir = os.path.join(exp_dir, name)
            models_subdir = os.path.join(model_dir, "models")
            model_files = []
            if os.path.isdir(models_subdir):
                for f in os.listdir(models_subdir):
                    if f.startswith("net_g_ema_") and f.endswith(".safetensors"):
                        model_files.append(os.path.join(models_subdir, f))
            return name, model_dir, model_files
        except Exception as e:
            print(f"Warning: Could not parse .yml for model dir: {e}")
            return None, None, []

    def add_config_file():
        print("\n=== Add Config File ===")
        model_name = input("Enter model name (used as config filename): ").strip()
        scale = input("Enter scale (e.g., 2, 4): ").strip()
        hq_path = input("Enter path to HQ dataset: ").strip()
        lq_path = input("Enter path to LQ dataset: ").strip()
        yml_path = input("Enter path to traiNNer-redux .yml config: ").strip()
        hcl_path = input("Enter path to wtp_dataset_destroyer .hcl config: ").strip()
        min_lq_w = input("Enter minimum LQ width (px): ").strip()
        min_lq_h = input("Enter minimum LQ height (px): ").strip()
        config_data = {
            "model_name": model_name,
            "scale": float(scale),
            "hq_path": hq_path,
            "lq_path": lq_path,
            "yml_path": yml_path,
            "hcl_path": hcl_path,
            "min_lq_w": int(min_lq_w),
            "min_lq_h": int(min_lq_h),
        }
        # Parse .hcl for extra info if provided and file exists
        import os
        import json

        if hcl_path and os.path.isfile(hcl_path):
            try:
                with open(hcl_path, "r") as f:
                    lines = f.readlines()
                for line in lines:
                    if line.strip().startswith("input") and "=" in line:
                        config_data["hcl_input"] = (
                            line.split("=", 1)[1].strip().strip('"')
                        )
                    if line.strip().startswith("output") and "=" in line:
                        config_data["hcl_output"] = (
                            line.split("=", 1)[1].strip().strip('"')
                        )
                in_global = False
                global_block = {}
                for line in lines:
                    if line.strip().startswith("global {"):
                        in_global = True
                        continue
                    if in_global:
                        if line.strip().startswith("}"):
                            break
                        if "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"')
                            try:
                                v = int(v)
                            except Exception:
                                pass
                            global_block[k] = v
                if global_block:
                    config_data["hcl_global"] = global_block
            except Exception as e:
                print(f"Warning: Failed to parse .hcl file for extra info: {e}")
        # Parse .yml for Val Dataset paths
        val_hq, val_lq = extract_val_paths_from_yml(yml_path)
        if val_hq and val_lq:
            config_data["val_hq_path"] = val_hq
            config_data["val_lq_path"] = val_lq
            print(
                f"Extracted Val Dataset HQ: {val_hq}\nExtracted Val Dataset LQ: {val_lq}"
            )
        else:
            add_val = (
                input(
                    "Val Dataset paths not found in .yml. Add custom Val Dataset HQ/LQ paths? (y/n): "
                )
                .strip()
                .lower()
            )
            if add_val == "y":
                val_hq = input("Enter path to Val HQ dataset: ").strip()
                val_lq = input("Enter path to Val LQ dataset: ").strip()
                config_data["val_hq_path"] = val_hq
                config_data["val_lq_path"] = val_lq
        # Parse .yml for model dir and model files
        yml_name, model_dir, model_files = extract_model_dir_from_yml(yml_path)
        if model_dir:
            config_data["model_dir"] = model_dir
            config_data["model_files"] = model_files
            print(f"Model directory: {model_dir}")
            print(f"Found {len(model_files)} model(s) in models subfolder.")
        config_dir = "configs"
        os.makedirs(config_dir, exist_ok=True)
        config_filename = os.path.join(config_dir, f"{model_name}_config.json")
        with open(config_filename, "w") as f:
            json.dump(config_data, f, indent=2)
        print(f"Config saved as {config_filename}")

    def load_config_file():
        nonlocal config, config_path, hq_folder, lq_folder
        print("\n=== Load Config File ===")
        import os
        import json

        config_dir = "configs"
        if not os.path.isdir(config_dir):
            print("No configs directory found. No configs to load.")
            return
        config_files = [f for f in os.listdir(config_dir) if f.endswith("_config.json")]
        if not config_files:
            print("No config files found in 'configs' directory.")
            return
        print("Available config files:")
        for idx, fname in enumerate(config_files, 1):
            print(f"  {idx}. {fname}")
        while True:
            choice = input_with_cancel(
                f"Select config file [1-{len(config_files)}] or 'cancel': "
            ).strip()
            if choice.isdigit() and 1 <= int(choice) <= len(config_files):
                selected = config_files[int(choice) - 1]
                break
            else:
                print("Invalid selection. Please enter a valid number or 'cancel'.")
        path = os.path.join(config_dir, selected)
        try:
            with open(path, "r") as f:
                config = json.load(f)
            config_path = path
            hq_folder = config.get("hq_path", "")
            lq_folder = config.get("lq_path", "")
            print(f"Loaded config from {path}")
        except Exception as e:
            print(f"Failed to load config: {e}")

    def view_config_info():
        print("\n=== Config Info ===")
        if not config:
            print("No config loaded.")
            return
        for k, v in config.items():
            print(f"{k}: {v}")

    def validate_dataset_from_config():
        print("\n=== Validate HQ/LQ Dataset Based on Config ===")
        if not config:
            print("No config loaded.")
            return
        # Validate scale, min size, no alpha, etc.
        from dataset_forge.analysis import find_hq_lq_scale, report_dimensions
        from dataset_forge.alpha import find_alpha_channels

        hq = config["hq_path"]
        lq = config["lq_path"]
        scale = float(config["scale"])
        min_w = int(config["min_lq_w"])
        min_h = int(config["min_lq_h"])
        print("- Checking scale...")
        scale_result = find_hq_lq_scale(hq, lq, verbose=False)
        if scale_result["scales"]:
            most_common = max(
                set(scale_result["scales"]), key=scale_result["scales"].count
            )
            if abs(most_common - scale) < 1e-2:
                print(f"  Scale OK: {most_common}")
            else:
                print(
                    f"  Scale mismatch! Most common: {most_common}, expected: {scale}"
                )
        else:
            print("  No valid scales found.")
        print("- Checking LQ min size...")
        dims = report_dimensions(lq, "LQ", verbose=False)
        too_small = [d for d in dims["dimensions"] if d[0] < min_w or d[1] < min_h]
        if too_small:
            print(f"  {len(too_small)} LQ images smaller than {min_w}x{min_h}")
        else:
            print("  All LQ images meet minimum size.")
        print("- Checking for alpha channels...")
        alpha = find_alpha_channels(hq, lq)
        if alpha["hq_alpha"] or alpha["lq_alpha"]:
            print(
                f"  Images with alpha found: HQ={len(alpha['hq_alpha'])}, LQ={len(alpha['lq_alpha'])}"
            )
        else:
            print("  No alpha channels found.")
        print("Validation complete.")

    def validate_val_dataset_from_config():
        print("\n=== Validate Val Dataset HQ/LQ Pair Based on Config ===")
        if not config or not config.get("val_hq_path") or not config.get("val_lq_path"):
            print("No Val Dataset HQ/LQ paths set in loaded config.")
            return
        from dataset_forge.analysis import find_hq_lq_scale, report_dimensions
        from dataset_forge.alpha import find_alpha_channels

        hq = config["val_hq_path"]
        lq = config["val_lq_path"]
        scale = float(config.get("scale", 2))
        min_w = int(config.get("min_lq_w", 0))
        min_h = int(config.get("min_lq_h", 0))
        print("- Checking scale...")
        scale_result = find_hq_lq_scale(hq, lq, verbose=False)
        if scale_result["scales"]:
            most_common = max(
                set(scale_result["scales"]), key=scale_result["scales"].count
            )
            if abs(most_common - scale) < 1e-2:
                print(f"  Scale OK: {most_common}")
            else:
                print(
                    f"  Scale mismatch! Most common: {most_common}, expected: {scale}"
                )
        else:
            print("  No valid scales found.")
        print("- Checking LQ min size...")
        dims = report_dimensions(lq, "Val LQ", verbose=False)
        too_small = [d for d in dims["dimensions"] if d[0] < min_w or d[1] < min_h]
        if too_small:
            print(f"  {len(too_small)} Val LQ images smaller than {min_w}x{min_h}")
        else:
            print("  All Val LQ images meet minimum size.")
        print("- Checking for alpha channels...")
        alpha = find_alpha_channels(hq, lq)
        if alpha["hq_alpha"] or alpha["lq_alpha"]:
            print(
                f"  Images with alpha found: HQ={len(alpha['hq_alpha'])}, LQ={len(alpha['lq_alpha'])}"
            )
        else:
            print("  No alpha channels found.")
        print("Validation complete.")

    def run_wtp_dataset_destroyer():
        if not config or not config.get("hcl_path"):
            print("No .hcl config path set in loaded config.")
            return
        hcl_path = config["hcl_path"]
        if not os.path.isfile(hcl_path):
            print(f".hcl config file not found: {hcl_path}")
            return
        destroyer_dir = os.path.dirname(hcl_path)
        hcl_filename = os.path.basename(hcl_path)
        # Try to find venv/Scripts/activate in the destroyer_dir or parent
        venv_path = os.path.join(destroyer_dir, "venv", "Scripts", "activate")
        if not os.path.isfile(venv_path):
            venv_path = os.path.join(destroyer_dir, "..", "venv", "Scripts", "activate")
        destroyer_py = os.path.join(destroyer_dir, "destroyer.py")
        if not os.path.isfile(destroyer_py):
            print(f"destroyer.py not found in {destroyer_dir}")
            return
        print(f"Running wtp_dataset_destroyer in: {destroyer_dir}")
        print(f"Command:")
        print(f"cd {destroyer_dir}")
        print(f"venv\\Scripts\\activate")
        print(f"python destroyer.py -f {hcl_filename}")
        # Run the commands
        try:
            subprocess.run(
                f'cd "{destroyer_dir}" && venv\\Scripts\\activate && python destroyer.py -f "{hcl_filename}"',
                shell=True,
                check=True,
            )
        except Exception as e:
            print(f"Error running wtp_dataset_destroyer: {e}")

    def run_trainner_redux():
        if not config or not config.get("yml_path"):
            print("No .yml config path set in loaded config.")
            return
        yml_path = config["yml_path"]
        if not os.path.isfile(yml_path):
            print(f".yml config file not found: {yml_path}")
            return
        # Assume train.py is in the traiNNer-redux directory (parent of yml_path or user should set)
        # Try to find train.py in parent or grandparent
        yml_dir = os.path.dirname(yml_path)
        trainner_dir = yml_dir
        for _ in range(3):
            if os.path.isfile(os.path.join(trainner_dir, "train.py")):
                break
            trainner_dir = os.path.dirname(trainner_dir)
        train_py = os.path.join(trainner_dir, "train.py")
        if not os.path.isfile(train_py):
            print(f"train.py not found near {yml_path}")
            return
        # Assume conda env is named 'trainner_redux'
        print(f"Running traiNNer-redux in: {trainner_dir}")
        print(f"Command:")
        print(f"cd {trainner_dir}")
        print(f"conda activate trainner_redux")
        print(f"python train.py --auto_resume -opt {yml_path}")
        # Run the commands
        try:
            subprocess.run(
                f'cd "{trainner_dir}" && conda activate trainner_redux && python train.py --auto_resume -opt "{yml_path}"',
                shell=True,
                check=True,
            )
        except Exception as e:
            print(f"Error running traiNNer-redux: {e}")

    def edit_hcl_file():
        if not config or not config.get("hcl_path"):
            print("No .hcl config path set in loaded config.")
            return
        hcl_path = config["hcl_path"]
        if not os.path.isfile(hcl_path):
            print(f".hcl config file not found: {hcl_path}")
            return
        print(f"Opening {hcl_path} in default editor...")
        try:
            if os.name == "nt":
                os.startfile(hcl_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", hcl_path])
            else:
                subprocess.run(["xdg-open", hcl_path])
        except Exception as e:
            print(f"Failed to open .hcl file: {e}")

    def edit_yml_file():
        if not config or not config.get("yml_path"):
            print("No .yml config path set in loaded config.")
            return
        yml_path = config["yml_path"]
        if not os.path.isfile(yml_path):
            print(f".yml config file not found: {yml_path}")
            return
        print(f"Opening {yml_path} in default editor...")
        try:
            if os.name == "nt":
                os.startfile(yml_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", yml_path])
            else:
                subprocess.run(["xdg-open", yml_path])
        except Exception as e:
            print(f"Failed to open .yml file: {e}")

    def natural_key(s):
        # Extract the number after net_g_ema_ and before .safetensors for sorting
        m = re.search(r"net_g_ema_(\d+)\.safetensors$", os.path.basename(s))
        return int(m.group(1)) if m else float("inf")

    def list_and_upscale_with_model():
        if not config or not config.get("model_dir"):
            print("No model directory found in config.")
            return
        model_dir = config["model_dir"]
        models_subdir = os.path.join(model_dir, "models")
        if not os.path.isdir(models_subdir):
            print(f"Models directory not found: {models_subdir}")
            return
        # Dynamically list all net_g_ema_*.safetensors files
        model_files = [
            os.path.join(models_subdir, f)
            for f in os.listdir(models_subdir)
            if f.startswith("net_g_ema_") and f.endswith(".safetensors")
        ]
        if not model_files:
            print("No model files found in models directory.")
            return

        # Sort model files by iteration number (true natural sort)
        def model_sort_key(path):
            m = re.search(r"net_g_ema_(\d+)\.safetensors$", os.path.basename(path))
            return int(m.group(1)) if m else float("inf")

        model_files_sorted = sorted(model_files, key=model_sort_key)
        print("Available models:")
        for idx, m in enumerate(model_files_sorted, 1):
            print(f"  {idx}. {os.path.basename(m)}")
        while True:
            choice = input_with_cancel(
                f"Select model [1-{len(model_files_sorted)}] or 'cancel': "
            ).strip()
            if choice.isdigit() and 1 <= int(choice) <= len(model_files_sorted):
                selected_model = model_files_sorted[int(choice) - 1]
                break
            else:
                print("Invalid selection. Please enter a valid number or 'cancel'.")
        model_used_name = os.path.splitext(os.path.basename(selected_model))[0]
        input_path = input_with_cancel(
            "Enter input image file or directory to upscale (or 'cancel'): "
        ).strip()
        output_path = input_with_cancel(
            "Enter output directory (or 'cancel'): "
        ).strip()
        script_path = os.path.join("dataset_forge", "upscale-script.py")
        if not os.path.isfile(script_path):
            script_path = input_with_cancel(
                "Enter path to upscale-script.py (or 'cancel'): "
            ).strip()
            if not os.path.isfile(script_path):
                print("upscale-script.py not found.")
                return
        # If input is a directory, enumerate files and set output filenames accordingly
        if os.path.isdir(input_path):
            from glob import glob
            import shutil

            SUPPORTED_FORMATS = (
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
                ".tga",
                ".bmp",
                ".tiff",
            )
            files = []
            for ext in SUPPORTED_FORMATS:
                files.extend(glob(os.path.join(input_path, f"*{ext}")))
            if not files:
                print("No supported images found in input directory.")
                return
            for file in files:
                base = os.path.splitext(os.path.basename(file))[0]
                out_file = f"{base}_{model_used_name}.png"
                out_full = os.path.join(output_path, out_file)
                print(f"Upscaling {file} -> {out_full}")
                try:
                    subprocess.run(
                        f'python "{script_path}" --input "{file}" --output "{output_path}" --model "{selected_model}"',
                        shell=True,
                        check=True,
                    )
                    # Rename output to desired format
                    orig_out = os.path.join(output_path, os.path.basename(file))
                    orig_out = os.path.splitext(orig_out)[0] + ".png"
                    if os.path.exists(orig_out):
                        shutil.move(orig_out, out_full)
                        print(f"Saved: {out_full}")
                except Exception as e:
                    print(f"Error upscaling {file}: {e}")
        else:
            base = os.path.splitext(os.path.basename(input_path))[0]
            out_file = f"{base}_{model_used_name}.png"
            out_full = os.path.join(output_path, out_file)
            print(f"Upscaling {input_path} -> {out_full}")
            try:
                subprocess.run(
                    f'python "{script_path}" --input "{input_path}" --output "{output_path}" --model "{selected_model}"',
                    shell=True,
                    check=True,
                )
                # Rename output to desired format
                orig_out = os.path.join(output_path, os.path.basename(input_path))
                orig_out = os.path.splitext(orig_out)[0] + ".png"
                if os.path.exists(orig_out):
                    os.rename(orig_out, out_full)
                    print(f"Saved: {out_full}")
            except Exception as e:
                print(f"Error upscaling {input_path}: {e}")

    option_map = {
        "0": ("Add Config File", add_config_file),
        "00": ("Load Config File", load_config_file),
        "000": ("View Config Info", view_config_info),
        "0000": ("Validate HQ/LQ Dataset from Config", validate_dataset_from_config),
        "00000": ("Validate Val Dataset HQ/LQ Pair", validate_val_dataset_from_config),
        "00001": ("Run wtp_dataset_destroyer", run_wtp_dataset_destroyer),
        "00002": ("Edit .hcl config file", edit_hcl_file),
        "00003": ("Run traiNNer-redux", run_trainner_redux),
        "00004": ("Edit .yml config file", edit_yml_file),
        "00005": ("List/Run Upscale with Model", list_and_upscale_with_model),
        "1": ("Find HQ/LQ Scale", lambda: find_hq_lq_scale(hq_folder, lq_folder)),
        "2": ("Test HQ/LQ Scale", lambda: test_hq_lq_scale(hq_folder, lq_folder)),
        "3": (
            "Check Image Consistency",
            lambda: (
                check_consistency(hq_folder, "HQ"),
                check_consistency(lq_folder, "LQ"),
            ),
        ),
        "4": (
            "Report Image Dimensions",
            lambda: (
                report_dimensions(hq_folder, "HQ"),
                report_dimensions(lq_folder, "LQ"),
            ),
        ),
        "5": (
            "Find Extreme Dimensions",
            lambda: (
                find_extreme_dimensions(hq_folder, "HQ"),
                find_extreme_dimensions(lq_folder, "LQ"),
            ),
        ),
        "6": ("Verify Image Integrity", lambda: verify_images(hq_folder, lq_folder)),
        "7": (
            "Find Misaligned Images",
            lambda: find_misaligned_images(hq_folder, lq_folder),
        ),
        "8": (
            "Generate Full HQ/LQ Dataset REPORT",
            lambda: generate_hq_lq_dataset_report(hq_folder, lq_folder),
        ),
        "9": (
            "Remove Small Image Pairs",
            lambda: remove_small_image_pairs(hq_folder, lq_folder),
        ),
        "10": (
            "Extract Random Image Pairs",
            lambda: extract_random_pairs(hq_folder, lq_folder),
        ),
        "11": (
            "Shuffle Image Pairs",
            lambda: shuffle_image_pairs(hq_folder, lq_folder),
        ),
        "12": ("Transform Dataset", lambda: transform_dataset(hq_folder, lq_folder)),
        "13": (
            "Dataset Color Adjustment",
            lambda: dataset_colour_adjustment(hq_folder, lq_folder),
        ),
        "14": (
            "Grayscale Conversion",
            lambda: grayscale_conversion(hq_folder, lq_folder),
        ),
        "15": (
            "Advanced Split/Adjust Dataset",
            lambda: split_adjust_dataset(hq_folder, lq_folder),
        ),
        "16": ("Combine Multiple Datasets", combine_datasets),
        "17": ("Find Alpha", lambda: find_alpha_channels(hq_folder, lq_folder)),
        "18": ("Remove Alpha", lambda: remove_alpha_channels(hq_folder, lq_folder)),
        "19": ("Comparisons", lambda: create_comparison_images(hq_folder, lq_folder)),
        "20": ("Fix Corrupted Images", lambda: fix_corrupted_images(hq_folder)),
        "21": ("Optimize PNG", lambda: optimize_png_menu(hq_folder, lq_folder)),
        "22": ("Convert to WebP", lambda: convert_to_webp_menu(hq_folder, lq_folder)),
        "23": (
            "HQ/LQ Dataset Image Tiling",
            lambda: tile_dataset_menu(hq_folder, lq_folder),
        ),
        "24": (
            "Create HQ/LQ Animated gif/webp Comparisons",
            lambda: create_gif_comparison(hq_folder, lq_folder),
        ),
        "25": ("Extract Frames", extract_frames_menu),
        "26": ("Exit", None),
        "27": ("Exit", None),
    }

    while True:
        try:
            os.system("cls" if os.name == "nt" else "clear")
            print_header("Image Training Dataset Utility")
            print_info(f"Current Folders:")
            print(
                f"  {Mocha.rosewater}HQ Folder:{Mocha.reset} {hq_folder if hq_folder else Mocha.red + 'Not set' + Mocha.reset}"
            )
            print(
                f"  {Mocha.rosewater}LQ Folder:{Mocha.reset} {lq_folder if lq_folder else Mocha.red + 'Not set' + Mocha.reset}"
            )
            print(
                f"  {Mocha.rosewater}Config:{Mocha.reset} {config_path if config_path else Mocha.red + 'Not loaded' + Mocha.reset}"
            )
            print_section("Menu", "=")
            for choice, (label, _) in option_map.items():
                print(Mocha.flamingo + f"  {choice}. {label}")
            print_section("HQ/LQ Dataset Analysis", "-")
            if hq_folder and lq_folder:
                print(f"  {Mocha.green}1. Find HQ/LQ Scale{Mocha.reset}")
                print(f"  {Mocha.green}2. Test HQ/LQ Scale{Mocha.reset}")
                print(
                    f"  {Mocha.green}3. Check Image Consistency (Formats/Modes in HQ & LQ){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}4. Report Image Dimensions (Stats for HQ & LQ){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}5. Find Extreme Dimensions (Biggest/Smallest in HQ & LQ){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}6. Verify Image Integrity (Corrupted Files in HQ & LQ){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}7. Find Misaligned Images (using Phase Correlation){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}8. Generate Full HQ/LQ Dataset REPORT{Mocha.reset}"
                )
                print_section("HQ/LQ Dataset Operations", "-")
                print(
                    f"  {Mocha.green}9. Remove Small Image Pairs (based on min dimension){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}10. Extract Random Image Pairs (subset to new location){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}11. Shuffle Image Pairs (renames to sequential in place or new location){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}12. Transform Dataset (Rotate, Flip, Brightness, etc. on subset){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}13. Dataset Color Adjustment (Contrast, Saturation, etc. on subset){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}14. Grayscale Conversion (convert subset to grayscale){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}15. Advanced Split/Adjust Dataset (Remove by criteria, Split){Mocha.reset}"
                )
                print_section("General Dataset Operations", "-")
                print(
                    f"  {Mocha.green}16. Combine Multiple Datasets (merges several HQ/LQ paired datasets){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}17. Find Alpha (detect images with alpha channels){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}18. Remove Alpha (remove alpha channels from images){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}19. Comparisons (create side-by-side HQ/LQ comparisons){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}20. Fix Corrupted Images (re-save images to fix corruption){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}21. Optimize PNG (convert all to PNG and optimize with oxipng){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}22. Convert to WebP (convert all images to WebP format){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}23. HQ/LQ Dataset Image Tiling (create image tiles){Mocha.reset}"
                )
                print(
                    f"  {Mocha.green}24. Create HQ/LQ Animated gif/webp Comparisons (animated gifs/webps of pairs){Mocha.reset}"
                )
                print(f"  {Mocha.green}25. Extract Frames (from video){Mocha.reset}")
                print(f"  {Mocha.green}26. Exit{Mocha.reset}")
            print_section("General Dataset Operations", "-")
            print(f"  {Mocha.green}27. Exit{Mocha.reset}")
            print("-" * 40)

            choice = input_with_cancel(
                "Enter your choice (or 'cancel' to return to main menu): "
            ).strip()
            if choice == "1":
                hq_folder = get_folder_path("Enter HQ folder path: ")
                lq_folder = get_folder_path("Enter LQ folder path: ")
            elif choice in option_map and option_map[choice][1]:
                try:
                    option_map[choice][1]()
                except KeyboardInterrupt:
                    continue
                release_memory()
            elif choice in option_map and option_map[choice][0] == "Exit":
                print("Exiting Image Training Dataset Utility. Goodbye!")
                break
            else:
                print(
                    "Invalid choice. Please enter a number from the menu or 'cancel'."
                )

            if choice not in [
                "1",
                "27",
            ]:
                input_with_cancel(
                    "\nPress Enter to return to the main menu (or type 'cancel'): "
                )
        except KeyboardInterrupt:
            print("Returned to main menu.")
            continue


if __name__ == "__main__":
    # Setup global logging to a file for the entire session, if desired
    # This can be complex if functions also try to set up their own file handlers.
    # For simplicity, individual functions might log to console or specific files.
    # Default basicConfig here will just go to console if no file handler is set.
    # logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # A session log file:
    session_log_file = "image_dataset_utility_session.log"
    # Clear or append to session log
    # For this example, let's append. For clearing each session, mode='w'.
    # Be careful with multiple file handlers if functions also create them.
    # It's often better for functions to use `logging.getLogger(__name__)`
    # and configure handlers at the top level.

    # Minimal global logging to console. Functions can add specific file handlers.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    main_menu()
