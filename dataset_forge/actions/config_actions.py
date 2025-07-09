import os
import json
import subprocess
import re
from dataset_forge.actions.analysis_actions import find_hq_lq_scale, report_dimensions
from dataset_forge.actions.alpha_actions import find_alpha_channels

# Helper functions from config_menu.py
import yaml


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
    if hcl_path and os.path.isfile(hcl_path):
        try:
            with open(hcl_path, "r") as f:
                lines = f.readlines()
            for line in lines:
                if line.strip().startswith("input") and "=" in line:
                    config_data["hcl_input"] = line.split("=", 1)[1].strip().strip('"')
                if line.strip().startswith("output") and "=" in line:
                    config_data["hcl_output"] = line.split("=", 1)[1].strip().strip('"')
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
        print(f"Extracted Val Dataset HQ: {val_hq}\nExtracted Val Dataset LQ: {val_lq}")
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
        config_data["model_files"] = model_files if model_files is not None else []
        print(f"Model directory: {model_dir}")
        print(
            f"Found {len(model_files) if model_files is not None else 0} model(s) in models subfolder."
        )
    config_dir = "configs"
    os.makedirs(config_dir, exist_ok=True)
    config_filename = os.path.join(config_dir, f"{model_name}_config.json")
    with open(config_filename, "w") as f:
        json.dump(config_data, f, indent=2)
    print(f"Config saved as {config_filename}")


def load_config_file():
    global config, config_path, hq_folder, lq_folder
    print("\n=== Load Config File ===")
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
        choice = input(
            f"Select config file [1-{len(config_files)}] or 'cancel': "
        ).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(config_files):
            selected = config_files[int(choice) - 1]
            break
        elif choice.lower() in ("cancel", "back", "c"):
            print("Returning to previous menu...")
            return
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
    global config
    print("\n=== Config Info ===")
    if not config:
        print("No config loaded.")
        return
    print(json.dumps(config, indent=2))


def validate_dataset_from_config():
    global config
    print("\n=== Validate HQ/LQ Dataset from Config ===")
    if not config:
        print("No config loaded.")
        return
    hq_path = config.get("hq_path")
    lq_path = config.get("lq_path")
    if not hq_path or not lq_path:
        print("HQ/LQ paths not set in config.")
        return
    print(f"Validating HQ: {hq_path}\nValidating LQ: {lq_path}")
    find_hq_lq_scale(hq_path, lq_path)
    report_dimensions(hq_path, "HQ")
    report_dimensions(lq_path, "LQ")
    find_alpha_channels(hq_path, lq_path)


def validate_val_dataset_from_config():
    global config
    print("\n=== Validate Val HQ/LQ Dataset from Config ===")
    if not config:
        print("No config loaded.")
        return
    val_hq = config.get("val_hq_path")
    val_lq = config.get("val_lq_path")
    if not val_hq or not val_lq:
        print("Val HQ/LQ paths not set in config.")
        return
    print(f"Validating Val HQ: {val_hq}\nValidating Val LQ: {val_lq}")
    find_hq_lq_scale(val_hq, val_lq)
    report_dimensions(val_hq, "Val HQ")
    report_dimensions(val_lq, "Val LQ")
    find_alpha_channels(val_hq, val_lq)


def run_wtp_dataset_destroyer():
    global config
    print("\n=== Run wtp_dataset_destroyer ===")
    if not config:
        print("No config loaded.")
        return
    hcl_path = config.get("hcl_path")
    if not hcl_path or not os.path.isfile(hcl_path):
        print(".hcl config file not set or does not exist in config.")
        return
    try:
        subprocess.run(["wtp_dataset_destroyer", hcl_path], check=True)
        print("wtp_dataset_destroyer completed successfully.")
    except Exception as e:
        print(f"Error running wtp_dataset_destroyer: {e}")


def run_trainner_redux():
    global config
    print("\n=== Run traiNNer-redux ===")
    if not config:
        print("No config loaded.")
        return
    yml_path = config.get("yml_path")
    if not yml_path or not os.path.isfile(yml_path):
        print(".yml config file not set or does not exist in config.")
        return
    try:
        subprocess.run(["python", "train.py", "-opt", yml_path], check=True)
        print("traiNNer-redux training started.")
    except Exception as e:
        print(f"Error running traiNNer-redux: {e}")


def edit_hcl_file():
    global config
    print("\n=== Edit .hcl Config File ===")
    if not config:
        print("No config loaded.")
        return
    hcl_path = config.get("hcl_path")
    if not hcl_path or not os.path.isfile(hcl_path):
        print(".hcl config file not set or does not exist in config.")
        return
    editor = os.environ.get("EDITOR", "notepad" if os.name == "nt" else "nano")
    try:
        subprocess.run([editor, hcl_path])
    except Exception as e:
        print(f"Error opening .hcl file: {e}")


def edit_yml_file():
    global config
    print("\n=== Edit .yml Config File ===")
    if not config:
        print("No config loaded.")
        return
    yml_path = config.get("yml_path")
    if not yml_path or not os.path.isfile(yml_path):
        print(".yml config file not set or does not exist in config.")
        return
    editor = os.environ.get("EDITOR", "notepad" if os.name == "nt" else "nano")
    try:
        subprocess.run([editor, yml_path])
    except Exception as e:
        print(f"Error opening .yml file: {e}")


def list_and_upscale_with_model():
    global config
    print("\n=== List/Run Upscale with Model ===")
    if not config:
        print("No config loaded.")
        return
    model_dir = config.get("model_dir")
    model_files = config.get("model_files", [])
    if not model_dir or not model_files:
        print("Model directory or model files not set in config.")
        return
    print(f"Model directory: {model_dir}")
    print("Available models:")
    for idx, f in enumerate(model_files, 1):
        print(f"  {idx}. {os.path.basename(f)}")
    # TODO: Implement actual upscaling logic or integration with upscaling tool
    print("[TODO] Actual upscaling logic not yet implemented.")
