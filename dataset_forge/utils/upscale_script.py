import os
import configparser
from concurrent.futures import ThreadPoolExecutor
import time
import traceback
import gc
import argparse
import sys
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.memory_utils import to_device_safe, clear_memory
from dataset_forge.utils.printing import print_info, print_error, print_success, print_warning
from dataset_forge.utils.color import Mocha
import chainner_ext

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    torch,
    PIL_Image as Image,
    numpy_as_np as np,
    spandrel,
    onnxruntime as ort,
)

try:
    import spandrel
    import spandrel_extra_arches

    spandrel_extra_arches.install()
except ImportError:
    spandrel = None

try:
    import onnxruntime as ort
except ImportError:
    ort = None

SUPPORTED_FORMATS = (".png", ".jpg", ".jpeg", ".webp", ".tga", ".bmp", ".tiff")


# ===================== CONFIGURATION =====================
def get_config_path(args):
    if hasattr(args, "config") and args.config:
        return args.config
    if os.path.exists(os.path.join("configs", "config.ini")):
        return os.path.join("configs", "config.ini")
    return "config.ini"


def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


# ===================== MODEL LOADING =====================
def load_model(model_path, device="cuda", use_onnx=False):
    """
    Load a model from file. Supports PyTorch (spandrel) and ONNX.
    """
    if use_onnx or (model_path.lower().endswith(".onnx") and ort is not None):
        if ort is None:
            raise ImportError("onnxruntime is not installed.")
        session = ort.InferenceSession(
            model_path, providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )
        return session
    if spandrel is None:
        raise ImportError("spandrel is not installed.")
    model = spandrel.ModelLoader().load_from_file(model_path)
    model = to_device_safe(model, device).eval()
    return model


# ===================== TILING UTILS =====================
def tile_image(img_tensor, tile_size, overlap, scale):
    """
    Split an image tensor into overlapping tiles.
    Returns a list of (y, x, tile_tensor).
    """
    _, _, h, w = img_tensor.shape
    tiles = []
    for y in range(0, h, tile_size - overlap):
        for x in range(0, w, tile_size - overlap):
            tile = img_tensor[
                :, :, y : min(y + tile_size, h), x : min(x + tile_size, w)
            ]
            tiles.append((y, x, tile))
    return tiles


def merge_tiles(tiles, out_shape, tile_size, overlap, scale):
    """
    Merge upscaled tiles into a full image tensor.
    """
    c, h, w = out_shape
    out = torch.zeros((c, h, w), dtype=tiles[0][2].dtype, device=tiles[0][2].device)
    weight = torch.zeros((1, h, w), dtype=tiles[0][2].dtype, device=tiles[0][2].device)
    for y, x, tile in tiles:
        y1, x1 = y * scale, x * scale
        y2, x2 = y1 + tile.shape[2], x1 + tile.shape[3]
        out[:, y1:y2, x1:x2] += tile[0]
        weight[:, y1:y2, x1:x2] += 1
    out /= weight
    return out


# ===================== UPSCALING CORE =====================
def upscale_single_image(
    input_path,
    output_path,
    model,
    model_type="pytorch",
    tile_size=None,
    overlap=16,
    alpha_handling="resize",
    gamma_correction=False,
    device="cuda",
    precision="auto",
    output_format="png",
    progress_callback=None,
):
    """
    Robust single-image upscaling with tiling, alpha, ONNX, and device/precision support.
    """
    img = Image.open(input_path)
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
    rgb_tensor = to_device_safe(rgb_tensor, device)
    scale = getattr(model, "scale", 1) if model_type == "pytorch" else 1
    # Tiling logic
    if tile_size is not None:
        tiles = tile_image(rgb_tensor, tile_size, overlap, scale)
        upscaled_tiles = []
        for i, (y, x, tile) in enumerate(tiles):
            if model_type == "pytorch":
                with torch.inference_mode():
                    out_tile = model(tile)
            else:
                ort_inputs = {model.get_inputs()[0].name: tile.cpu().numpy()}
                out_tile = torch.from_numpy(model.run(None, ort_inputs)[0])
            upscaled_tiles.append((y, x, out_tile.unsqueeze(0)))
            if progress_callback:
                progress_callback(i + 1, len(tiles))
        out_shape = (3, rgb_tensor.shape[2] * scale, rgb_tensor.shape[3] * scale)
        out_tensor = merge_tiles(upscaled_tiles, out_shape, tile_size, overlap, scale)
    else:
        if model_type == "pytorch":
            with torch.inference_mode():
                out_tensor = model(rgb_tensor)[0]
        else:
            ort_inputs = {model.get_inputs()[0].name: rgb_tensor.cpu().numpy()}
            out_tensor = torch.from_numpy(model.run(None, ort_inputs)[0][0])
    out_img = Image.fromarray(
        (out_tensor.permute(1, 2, 0).cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
    )
    # Advanced alpha handling
    if has_alpha:
        if alpha_handling == "upscale":
            alpha_tensor = (
                torch.from_numpy(np.array(alpha))
                .unsqueeze(0)
                .unsqueeze(0)
                .float()
                .div(255.0)
            )
            alpha_tensor = to_device_safe(alpha_tensor, device)
            if tile_size is not None:
                alpha_tiles = tile_image(alpha_tensor, tile_size, overlap, scale)
                upscaled_alpha_tiles = []
                for y, x, tile in alpha_tiles:
                    if model_type == "pytorch":
                        with torch.inference_mode():
                            out_tile = model(tile.repeat(1, 3, 1, 1))
                    else:
                        ort_inputs = {
                            model.get_inputs()[0]
                            .name: tile.repeat(1, 3, 1, 1)
                            .cpu()
                            .numpy()
                        }
                        out_tile = torch.from_numpy(model.run(None, ort_inputs)[0])
                    upscaled_alpha_tiles.append((y, x, out_tile[:, 0:1, :, :]))
                out_shape = (
                    1,
                    alpha_tensor.shape[2] * scale,
                    alpha_tensor.shape[3] * scale,
                )
                upscaled_alpha = merge_tiles(
                    upscaled_alpha_tiles, out_shape, tile_size, overlap, scale
                )
                upscaled_alpha_img = Image.fromarray(
                    (upscaled_alpha[0].cpu().numpy() * 255)
                    .clip(0, 255)
                    .astype(np.uint8)
                )
            else:
                with torch.inference_mode():
                    upscaled_alpha = model(alpha_tensor.repeat(1, 3, 1, 1))[0, 0]
                upscaled_alpha_img = Image.fromarray(
                    (upscaled_alpha.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
                )
            out_img.putalpha(upscaled_alpha_img)
        elif alpha_handling == "resize":
            alpha_img = alpha.resize(out_img.size, Image.LANCZOS)
            if gamma_correction:
                # Optionally apply gamma correction here
                pass
            out_img.putalpha(alpha_img)
        # else: discard alpha
    out_img.save(output_path, output_format.upper())
    return output_path


# ===================== BATCH UPSCALING =====================
def batch_upscale(
    input_dir,
    output_dir,
    model,
    model_type="pytorch",
    tile_size=None,
    overlap=16,
    alpha_handling="resize",
    gamma_correction=False,
    device="cuda",
    precision="auto",
    output_format="png",
    progress_bar=True,
):
    """
    Batch upscaling for all images in a directory.
    """
    image_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(input_dir)
        for file in files
        if file.lower().endswith(SUPPORTED_FORMATS)
    ]
    os.makedirs(output_dir, exist_ok=True)
    total = len(image_files)
    results = []
    with (
        tqdm(total=total, desc="Batch Upscaling", unit="img")
        if progress_bar
        else DummyContext()
    ) as pbar:
        for i, input_path in enumerate(image_files):
            rel_path = os.path.relpath(input_path, input_dir)
            out_path = os.path.join(
                output_dir, os.path.splitext(rel_path)[0] + f".{output_format}"
            )
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            try:
                upscale_single_image(
                    input_path,
                    out_path,
                    model,
                    model_type=model_type,
                    tile_size=tile_size,
                    overlap=overlap,
                    alpha_handling=alpha_handling,
                    gamma_correction=gamma_correction,
                    device=device,
                    precision=precision,
                    output_format=output_format,
                )
                results.append((input_path, out_path, True))
    except Exception as e:
                print_error(f"Error upscaling {input_path}: {e}")
        traceback.print_exc()
                results.append((input_path, out_path, False))
            if progress_bar:
                pbar.update(1)
    return results


class DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def update(self, *a, **k):
        pass


# ===================== CLI ENTRY POINT =====================
def main():
    parser = argparse.ArgumentParser(description="Image Upscaling Tool")
    parser.add_argument("--input", required=True, help="Input image file or directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--model", required=True, help="Path to the model file")
    parser.add_argument(
        "--config",
        required=False,
        help="Path to config.ini (default: ./configs/config.ini or ./config.ini)",
    )
    parser.add_argument(
        "--tile_size",
        type=int,
        default=None,
        help="Tile size for tiling (default: None)",
    )
    parser.add_argument(
        "--overlap", type=int, default=16, help="Tile overlap (default: 16)"
    )
    parser.add_argument(
        "--alpha_handling",
        type=str,
        default="resize",
        choices=["resize", "upscale", "discard"],
        help="Alpha handling mode",
    )
    parser.add_argument(
        "--gamma_correction",
        action="store_true",
        help="Enable gamma correction for alpha resize",
    )
    parser.add_argument(
        "--device", type=str, default="cuda", help="Device to use (cuda or cpu)"
    )
    parser.add_argument(
        "--precision",
        type=str,
        default="auto",
        choices=["auto", "fp32", "fp16", "bf16"],
        help="Precision mode",
    )
    parser.add_argument(
        "--output_format", type=str, default="png", help="Output image format"
    )
    parser.add_argument("--onnx", action="store_true", help="Force ONNX model usage")
    args = parser.parse_args()

    config_path = get_config_path(args)
    config = load_config(config_path)
    # Optionally override config with CLI args
    tile_size = args.tile_size or config["Processing"].getint("TileSize", fallback=None)
    overlap = args.overlap or config["Processing"].getint("Overlap", fallback=16)
    alpha_handling = args.alpha_handling or config["Processing"].get(
        "AlphaHandling", fallback="resize"
    )
    gamma_correction = args.gamma_correction or config["Processing"].getboolean(
        "GammaCorrection", fallback=False
    )
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    precision = args.precision or config["Processing"].get("Precision", fallback="auto")
    output_format = args.output_format or config["Processing"].get(
        "OutputFormat", fallback="png"
    )
    use_onnx = args.onnx or args.model.lower().endswith(".onnx")

    if not os.path.exists(args.input):
        print_error(f"Error: Input path not found: {args.input}")
        return
    if not os.path.exists(args.output):
        print_info(f"Creating output directory: {args.output}")
        os.makedirs(args.output)
    if not os.path.exists(args.model):
        print_error(f"Error: Model file not found: {args.model}")
        return
    try:
        print_info("Loading model...")
        model = load_model(args.model, device=device, use_onnx=use_onnx)
        print_success("Model loaded successfully.")
        if os.path.isfile(args.input):
            print_info(f"Processing single file: {args.input}")
            out_path = os.path.join(
                args.output,
                os.path.splitext(os.path.basename(args.input))[0] + f".{output_format}",
            )
            upscale_single_image(
                args.input,
                out_path,
                model,
                model_type="onnx" if use_onnx else "pytorch",
                tile_size=tile_size,
                overlap=overlap,
                alpha_handling=alpha_handling,
                gamma_correction=gamma_correction,
                device=device,
                precision=precision,
                output_format=output_format,
            )
        else:
            print_info(f"Processing directory: {args.input}")
            batch_upscale(
                args.input,
                args.output,
                model,
                model_type="onnx" if use_onnx else "pytorch",
                tile_size=tile_size,
                overlap=overlap,
                alpha_handling=alpha_handling,
                gamma_correction=gamma_correction,
                device=device,
                precision=precision,
                output_format=output_format,
                progress_bar=True,
            )
        print_success("All processing completed.")
    except Exception as e:
        print_error(f"Error: {str(e)}")
        traceback.print_exc()
    finally:
        clear_memory()
        print_info("Cleanup completed.")


if __name__ == "__main__":
    main()
    print_success("Script execution finished.")
