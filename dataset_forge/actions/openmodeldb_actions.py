"""
OpenModelDB Actions
Handles API integration, caching, filtering, download, and verification for OpenModelDB models.
"""

import os
import json
import hashlib
import requests
import re
from tqdm import tqdm
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.input_utils import get_input
import webbrowser
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success

OPENMODELDB_API_URL = "https://openmodeldb.info/api/v1/models.json"


def update_model_cache(cache_dir: str) -> None:
    """
    Fetches the latest model metadata from OpenModelDB and caches it locally.
    Args:
        cache_dir: Directory to store the cache file.
    """
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "models.json")
    try:
        resp = requests.get(OPENMODELDB_API_URL, timeout=15)
        resp.raise_for_status()
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print_success("Model cache updated from OpenModelDB.")
    except Exception as e:
        print_warning(f"Failed to update model cache: {e}")
        if not os.path.exists(cache_path):
            print_error("No cache available. Cannot proceed.")


def get_cached_models(cache_dir: str) -> dict:
    """
    Loads cached model metadata from disk.
    Args:
        cache_dir: Directory where cache is stored.
    Returns:
        Dictionary of models.
    """
    cache_path = os.path.join(cache_dir, "models.json")
    if not os.path.exists(cache_path):
        print_warning("Model cache not found. Updating...")
        update_model_cache(cache_dir)
    with open(cache_path, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_models(
    models: dict,
    tag: str = None,
    architecture: str = None,
    scale: int = None,
    text: str = None,
) -> dict:
    """
    Filters models by tag, architecture, scale, or free text.
    Args:
        models: Model dictionary
        tag: Tag to filter by
        architecture: Architecture to filter by
        scale: Scale to filter by
        text: Free text search
    Returns:
        Filtered model dictionary
    """
    filtered = {}
    for k, v in models.items():
        if tag and tag not in v.get("tags", []):
            continue
        if (
            architecture
            and architecture.lower() not in v.get("architecture", "").lower()
        ):
            continue
        if scale and v.get("scale") != scale:
            continue
        if text and text.lower() not in json.dumps(v).lower():
            continue
        filtered[k] = v
    return filtered


def get_model_details(models: dict, model_key: str) -> dict:
    """
    Returns details for a specific model.
    Args:
        models: Model dictionary
        model_key: Key of the model
    Returns:
        Model details dict
    """
    return models[model_key]


def is_gdrive_url(url: str) -> bool:
    return "drive.google.com" in url


def is_onedrive_url(url: str) -> bool:
    return "1drv.ms" in url or "onedrive.live.com" in url


def extract_gdrive_id(url: str) -> str:
    # Handles both /file/d/<id>/ and id=... patterns
    m = re.search(r"/d/([\w-]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"id=([\w-]+)", url)
    if m:
        return m.group(1)
    return None


def get_resource_filename(resource, model_details):
    # Prefer explicit filename in resource, else infer from model name/type
    if "filename" in resource:
        return resource["filename"]
    # Try to infer from type/extension
    ext = resource.get("type", "pth")
    model_name = model_details.get("name", "model").replace(" ", "_")
    return f"{model_name}.{ext}"


@monitor_all("Download Model", critical_on_error=True)
def download_model(
    model_details: dict, models_dir: str, verify_sha256: bool = False
) -> None:
    """
    Downloads the model file(s) to the models directory, with progress bar and optional SHA256 verification.
    Always prompts for confirmation before downloading. If file exists but SHA256 fails, prompts to overwrite.
    Handles Google Drive, OneDrive, and direct links.
    """
    import os

    os.makedirs(models_dir, exist_ok=True)
    for resource in model_details.get("resources", []):
        url = resource["urls"][0]
        filename = get_resource_filename(resource, model_details)
        dest_path = os.path.join(models_dir, filename)
        sha256 = resource.get("sha256")
        # Check if file exists and verify hash if available
        if os.path.exists(dest_path):
            if sha256:
                if verify_file_sha256(dest_path, sha256):
                    print_success(f"Model already downloaded and verified: {filename}")
                    continue
                else:
                    print_warning(f"File exists but SHA256 does not match: {filename}")
                    resp = get_input(f"Overwrite {filename}? [y/N]: ").strip().lower()
                    if resp != "y":
                        print_info("Skipping download.")
                        continue
            else:
                print_success(f"Model already downloaded: {filename}")
                continue
        # Prompt for confirmation
        resp = (
            get_input(f"Download model '{filename}' from {url}? [y/N]: ")
            .strip()
            .lower()
        )
        if resp != "y":
            print_info("Skipping download.")
            continue
        # Download logic
        try:
            if is_gdrive_url(url):
                gdrive_id = extract_gdrive_id(url)
                if not gdrive_id:
                    print_error("Could not extract Google Drive file ID.")
                    continue
                try:
                    import gdown
                except ImportError:
                    print_error(
                        "gdown is required for Google Drive downloads. Please install it: pip install gdown"
                    )
                    continue
                print_info(f"Downloading from Google Drive: {filename}")
                gdown.download(id=gdrive_id, output=dest_path, quiet=False)
            elif is_onedrive_url(url):
                print_warning("Automatic OneDrive downloads are not supported.")
                print_warning(
                    f"Please download manually from: {url}\nThen place the file as '{filename}' in your models directory: {models_dir}"
                )
                webbrowser.open(url)
                continue
            else:
                print_info(f"Downloading: {filename}")
                with requests.get(url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    total = int(r.headers.get("content-length", 0))
                    with open(dest_path, "wb") as f, tqdm(
                        total=total, unit="B", unit_scale=True, desc=filename
                    ) as pbar:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
            play_done_sound()
            print_success(f"Downloaded: {filename}")
            # Optionally verify SHA256
            if verify_sha256 and sha256:
                if verify_file_sha256(dest_path, sha256):
                    print_success("SHA256 verified.")
                else:
                    print_error("SHA256 verification failed!")
        except Exception as e:
            print_error(f"Download failed: {e}")


def verify_file_sha256(filepath: str, expected_hash: str) -> bool:
    """
    Verifies the SHA256 hash of a file.
    Args:
        filepath: Path to file
        expected_hash: Expected SHA256 hash
    Returns:
        True if matches, False otherwise
    """
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest().lower() == expected_hash.lower()


@monitor_all("Test Model", critical_on_error=True)
def test_model(model_details: dict, models_dir: str, image_path: str) -> None:
    """
    Runs a test upscaling using the selected model and image.
    Args:
        model_details: Model metadata
        models_dir: Directory where model is stored
        image_path: Path to image to upscale
    """
    from dataset_forge.utils.printing import (
        print_info,
        print_success,
        print_warning,
        print_error,
    )
    from dataset_forge.utils.audio_utils import play_done_sound
    from dataset_forge.utils.memory_utils import to_device_safe
    import os
    import torch
    import numpy as np
    from PIL import Image

    # Find model file
    resources = model_details.get("resources", [])
    if not resources:
        print_error("No downloadable resources for this model.")
        return
    # Use the same filename logic as download_model
    filename = get_resource_filename(resources[0], model_details)
    model_path = os.path.join(models_dir, filename)
    if not os.path.exists(model_path):
        print_error(f"Model file not found: {model_path}. Please download first.")
        return
    # Build output filename: originalFilename__x{scale}_{modelName}.ext
    orig_base, orig_ext = os.path.splitext(os.path.basename(image_path))
    scale = model_details.get("scale", "?")
    model_name = model_details.get("name", "model").replace(" ", "_")
    output_filename = f"{orig_base}__x{scale}_{model_name}{orig_ext}"
    output_path = os.path.join(os.path.dirname(image_path), output_filename)
    try:
        import spandrel
        import spandrel_extra_arches

        # Only install extra arches once per process
        if not getattr(spandrel_extra_arches, "_already_installed", False):
            spandrel_extra_arches.install()
            spandrel_extra_arches._already_installed = True
        print_info(f"Loading model with Spandrel: {model_path}")
        model = spandrel.ModelLoader().load_from_file(model_path)
        model = to_device_safe(
            model, "cuda" if torch.cuda.is_available() else "cpu"
        ).eval()
        img = Image.open(image_path)
        has_alpha = img.mode == "RGBA"
        if has_alpha:
            rgb_img, alpha = img.convert("RGB"), img.split()[3]
        else:
            rgb_img = img
        rgb_tensor = (
            torch.from_numpy(np.array(rgb_img))
            .permute(2, 0, 1)
            .float()
            .div(255.0)
            .unsqueeze(0)
        )
        rgb_tensor = to_device_safe(
            rgb_tensor,
            (
                model.device
                if hasattr(model, "device")
                else ("cuda" if torch.cuda.is_available() else "cpu")
            ),
        )
        with torch.inference_mode():
            out_tensor = model(rgb_tensor)
        out_img = Image.fromarray(
            (out_tensor[0].permute(1, 2, 0).cpu().numpy() * 255)
            .clip(0, 255)
            .astype(np.uint8)
        )
        if has_alpha:
            # Simple: resize alpha to match output
            alpha = alpha.resize(out_img.size, Image.LANCZOS)
            out_img.putalpha(alpha)
        out_img.save(output_path)
        print_success(f"Upscaled image saved to: {output_path}")
        play_done_sound()
        return
    except ImportError:
        print_warning("Spandrel not installed. Trying fallback upscaling script...")
    except Exception as e:
        print_error(f"Spandrel upscaling failed: {e}")
        import traceback

        traceback.print_exc()
        return
    # Fallback: Try to call dataset_forge.utils.upscale_script if available
    try:
        from dataset_forge.utils.upscale_script import upscale_image

        print_info(
            f"Running fallback upscaling script...\nModel: {model_path}\nImage: {image_path}"
        )
        upscale_image(model_path, image_path, output_path)
        print_success(f"Upscaled image saved to: {output_path}")
        play_done_sound()
    except Exception as e:
        print_error(f"No upscaling backend available: {e}")
        print_info("[Stub] Please install Spandrel or provide an upscaling script.")
