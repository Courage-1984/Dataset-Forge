import os
import json
import subprocess
import re
from dataset_forge.analysis import find_hq_lq_scale, report_dimensions
from dataset_forge.alpha import find_alpha_channels


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


def extract_val_paths_from_yml(yml_path):
    import yaml

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
    import yaml

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
    for k, v in config.items():
        print(f"{k}: {v}")


def validate_dataset_from_config():
    global config
    print("\n=== Validate HQ/LQ Dataset Based on Config ===")
    if not config:
        print("No config loaded.")
        return
    hq = config["hq_path"]
    lq = config["lq_path"]
    scale = float(config["scale"])
    min_w = int(config["min_lq_w"])
    min_h = int(config["min_lq_h"])
    print("- Checking scale...")
    scale_result = find_hq_lq_scale(hq, lq, verbose=False)
    if scale_result["scales"]:
        most_common = max(set(scale_result["scales"]), key=scale_result["scales"].count)
        if abs(most_common - scale) < 1e-2:
            print(f"  Scale OK: {most_common}")
        else:
            print(f"  Scale mismatch! Most common: {most_common}, expected: {scale}")
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
    global config
    print("\n=== Validate Val Dataset HQ/LQ Pair Based on Config ===")
    if not config or not config.get("val_hq_path") or not config.get("val_lq_path"):
        print("No Val Dataset HQ/LQ paths set in loaded config.")
        return
    hq = config["val_hq_path"]
    lq = config["val_lq_path"]
    scale = float(config.get("scale", 2))
    min_w = int(config.get("min_lq_w", 0))
    min_h = int(config.get("min_lq_h", 0))
    print("- Checking scale...")
    scale_result = find_hq_lq_scale(hq, lq, verbose=False)
    if scale_result["scales"]:
        most_common = max(set(scale_result["scales"]), key=scale_result["scales"].count)
        if abs(most_common - scale) < 1e-2:
            print(f"  Scale OK: {most_common}")
        else:
            print(f"  Scale mismatch! Most common: {most_common}, expected: {scale}")
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
    global config
    if not config or not config.get("hcl_path"):
        print("No .hcl config path set in loaded config.")
        return
    hcl_path = config["hcl_path"]
    if not os.path.isfile(hcl_path):
        print(f".hcl config file not found: {hcl_path}")
        return
    destroyer_dir = os.path.dirname(hcl_path)
    hcl_filename = os.path.basename(hcl_path)
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
    try:
        subprocess.run(
            f'cd "{destroyer_dir}" && venv\\Scripts\\activate && python destroyer.py -f "{hcl_filename}"',
            shell=True,
            check=True,
        )
    except Exception as e:
        print(f"Error running wtp_dataset_destroyer: {e}")


def run_trainner_redux():
    global config
    if not config or not config.get("yml_path"):
        print("No .yml config path set in loaded config.")
        return
    yml_path = config["yml_path"]
    if not os.path.isfile(yml_path):
        print(f".yml config file not found: {yml_path}")
        return
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
    print(f"Running traiNNer-redux in: {trainner_dir}")
    print(f"Command:")
    print(f"cd {trainner_dir}")
    print(f"conda activate trainner_redux")
    print(f"python train.py --auto_resume -opt {yml_path}")
    try:
        subprocess.run(
            f'cd "{trainner_dir}" && conda activate trainner_redux && python train.py --auto_resume -opt "{yml_path}"',
            shell=True,
            check=True,
        )
    except Exception as e:
        print(f"Error running traiNNer-redux: {e}")


def edit_hcl_file():
    global config
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
        elif os.sys.platform == "darwin":
            subprocess.run(["open", hcl_path])
        else:
            subprocess.run(["xdg-open", hcl_path])
    except Exception as e:
        print(f"Failed to open .hcl file: {e}")


def edit_yml_file():
    global config
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
        elif os.sys.platform == "darwin":
            subprocess.run(["open", yml_path])
        else:
            subprocess.run(["xdg-open", yml_path])
    except Exception as e:
        print(f"Failed to open .yml file: {e}")


def list_and_upscale_with_model():
    global config
    if not config or not config.get("model_dir"):
        print("No model directory found in config.")
        return
    model_dir = config["model_dir"]
    models_subdir = os.path.join(model_dir, "models")
    if not os.path.isdir(models_subdir):
        print(f"Models directory not found: {models_subdir}")
        return
    model_files = [
        os.path.join(models_subdir, f)
        for f in os.listdir(models_subdir)
        if f.startswith("net_g_ema_") and f.endswith(".safetensors")
    ]
    if not model_files:
        print("No model files found in models directory.")
        return

    def model_sort_key(path):
        m = re.search(r"net_g_ema_(\d+)\.safetensors$", os.path.basename(path))
        return int(m.group(1)) if m else float("inf")

    model_files_sorted = sorted(model_files, key=model_sort_key)
    print("Available models:")
    for idx, m in enumerate(model_files_sorted, 1):
        print(f"  {idx}. {os.path.basename(m)}")
    while True:
        choice = input(
            f"Select model [1-{len(model_files_sorted)}] or 'cancel': "
        ).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(model_files_sorted):
            selected_model = model_files_sorted[int(choice) - 1]
            break
        elif choice.lower() in ("cancel", "back", "c"):
            print("Returning to previous menu...")
            return
        else:
            print("Invalid selection. Please enter a valid number or 'cancel'.")
    model_used_name = os.path.splitext(os.path.basename(selected_model))[0]
    input_path = input(
        "Enter input image file or directory to upscale (or 'cancel'): "
    ).strip()
    if input_path.lower() in ("cancel", "back", "c"):
        print("Returning to previous menu...")
        return
    output_path = input("Enter output directory (or 'cancel'): ").strip()
    if output_path.lower() in ("cancel", "back", "c"):
        print("Returning to previous menu...")
        return
    script_path = os.path.join("dataset_forge", "upscale-script.py")
    if not os.path.isfile(script_path):
        script_path = input("Enter path to upscale-script.py (or 'cancel'): ").strip()
        if not os.path.isfile(script_path):
            print("upscale-script.py not found.")
            return
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
            orig_out = os.path.join(output_path, os.path.basename(input_path))
            orig_out = os.path.splitext(orig_out)[0] + ".png"
            if os.path.exists(orig_out):
                os.rename(orig_out, out_full)
                print(f"Saved: {out_full}")
        except Exception as e:
            print(f"Error upscaling {input_path}: {e}")
