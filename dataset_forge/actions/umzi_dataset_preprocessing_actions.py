# Umzi's Dataset_Preprocessing actions - now direct wrappers for pepedp
"""
Actions for Umzi's Dataset_Preprocessing integration using pepedp.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.input_utils import (
    ask_choice,
    ask_float,
    ask_int,
    ask_yes_no,
    get_folder_path,
    get_input,
)
from dataset_forge.utils.lazy_imports import (
    pepedp_best_tile,
    pepedp_cosine_dist,
    pepedp_create_embedd,
    pepedp_euclid_dist,
    pepedp_filtered_pairs,
    pepedp_ic9600_complexity,
    pepedp_img_to_embedding as ImgToEmbedding,
    pepedp_laplacian_complexity,
    pepedp_move_duplicate_files,
    pepedp_threshold_alg,
    pepedp_video_to_frame,
    pepedp_enum,
)
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import (
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)
from dataset_forge.utils.progress_utils import smart_map
from tqdm import tqdm


def clear_corrupted_model_cache(
    model_name: str = "convnextL_384_1kpretrained_official_style.pth",
) -> None:
    """Clear corrupted model cache files to fix download issues.

    Args:
        model_name: Name of the corrupted model file to remove
    """
    try:
        # Common cache locations
        cache_locations = [
            os.path.expanduser("~/.cache/torch/hub/checkpoints/"),
            os.path.expanduser("~/.cache/torch/hub/"),
            os.path.join(os.getcwd(), ".cache", "torch", "hub", "checkpoints"),
        ]

        for cache_dir in cache_locations:
            if os.path.exists(cache_dir):
                model_path = os.path.join(cache_dir, model_name)
                if os.path.exists(model_path):
                    print_warning(f"Removing corrupted model cache: {model_path}")
                    try:
                        os.remove(model_path)
                        print_success(f"✅ Removed corrupted cache file: {model_path}")
                    except Exception as e:
                        print_warning(f"Could not remove {model_path}: {e}")

        # Also clear any temporary download files
        temp_dir = tempfile.gettempdir()
        temp_patterns = [f"*{model_name}*", "*convnext*", "*torch_hub*"]

        for pattern in temp_patterns:
            import glob

            temp_files = glob.glob(os.path.join(temp_dir, pattern))
            for temp_file in temp_files:
                try:
                    if os.path.isfile(temp_file):
                        os.remove(temp_file)
                        print_info(f"Cleared temporary file: {temp_file}")
                except Exception:
                    pass

    except Exception as e:
        print_warning(f"Error clearing cache: {e}")


def safe_model_initialization(
    model_enum, amp: bool, scale: int, max_retries: int = 3
) -> any:
    """Safely initialize embedding model with retry logic and fallback options.

    Args:
        model_enum: Model enum to initialize
        amp: Whether to use AMP
        scale: Scale factor
        max_retries: Maximum number of retry attempts

    Returns:
        Initialized embedder model

    Raises:
        RuntimeError: If all retry attempts fail
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            print_info(
                f"Attempting to initialize model (attempt {attempt + 1}/{max_retries})"
            )

            # Clear memory before each attempt
            clear_memory()
            clear_cuda_cache()

            embedder = ImgToEmbedding(
                model=model_enum,
                amp=amp,
                scale=scale,
            )

            print_success("✅ Model initialized successfully")
            return embedder

        except RuntimeError as e:
            error_msg = str(e)
            last_error = e

            if "PytorchStreamReader failed reading zip archive" in error_msg:
                print_warning(
                    f"⚠️  Corrupted model download detected (attempt {attempt + 1})"
                )
                print_info("Clearing corrupted cache files...")

                # Clear corrupted cache
                clear_corrupted_model_cache()

                if attempt < max_retries - 1:
                    print_info("Retrying model download...")
                    continue
                else:
                    print_error("❌ All retry attempts failed")
                    break

            elif "out of memory" in error_msg.lower():
                print_warning(f"⚠️  CUDA memory error (attempt {attempt + 1})")
                print_info("Clearing CUDA cache and retrying...")
                clear_cuda_cache()
                continue

            else:
                print_error(f"❌ Unexpected error: {error_msg}")
                break

        except Exception as e:
            last_error = e
            print_error(f"❌ Error initializing model: {e}")
            break

    # If all attempts failed, try fallback to CPU
    print_warning("⚠️  Attempting fallback to CPU processing...")
    try:
        embedder = ImgToEmbedding(
            model=model_enum,
            amp=False,  # Disable AMP for CPU
            scale=scale,
        )
        print_success("✅ Model initialized on CPU successfully")
        return embedder
    except Exception as e:
        print_error(f"❌ CPU fallback also failed: {e}")
        raise RuntimeError(
            f"Failed to initialize model after {max_retries} attempts and CPU fallback. Last error: {last_error}"
        )


def create_embedd_with_progress(img_folder: str, embedder):
    """Enhanced version of create_embedd with progress tracking."""
    import os
    from pepeline import read, ImgColor, ImgFormat

    # Get list of image files
    image_files = [
        f
        for f in os.listdir(img_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))
    ]

    if not image_files:
        print_warning("No image files found in the specified folder")
        return {}

    embedded = {}

    # Create progress bar for embedding creation
    with tqdm(total=len(image_files), desc="Creating embeddings", unit="img") as pbar:
        for img_name in image_files:
            try:
                img_path = os.path.join(img_folder, img_name)
                img = read(img_path, ImgColor.RGB, ImgFormat.F32)
                embedded[img_name] = embedder(img).detach().cpu()
                pbar.update(1)
            except Exception as e:
                print_warning(f"Failed to process {img_name}: {e}")
                pbar.update(1)
                continue

    return embedded


def filtered_pairs_with_progress(
    embeddings, dist_func, threshold: float = 1.5, device_str: str = None
):
    """Enhanced version of filtered_pairs with progress tracking."""
    import torch

    names = list(embeddings.keys())
    if not names:
        return {"names": [], "filtered_pairs": []}

    tensor_list = [embeddings[name] for name in names]
    E = torch.stack(tensor_list, dim=0)
    E = E.view(E.size(0), -1)

    device = (
        torch.device(device_str)
        if device_str
        else (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
    )
    E = E.to(device)

    N = E.size(0)
    filtered_pairs = []

    # Create progress bar for duplicate detection
    with tqdm(total=N, desc="Finding duplicates", unit="img") as pbar:
        for i in range(N):
            anchor = E[i].unsqueeze(0)  # [1, D]
            compare_to = E[i + 1 :]  # [N - i - 1, D]
            if compare_to.size(0) == 0:
                pbar.update(1)
                continue

            dists = dist_func(anchor, compare_to).squeeze(0)  # [N - i - 1]
            mask = dists < threshold
            j_indices = torch.nonzero(mask).squeeze(1) + (i + 1)

            for idx, dist_val in zip(j_indices.tolist(), dists[mask].tolist()):
                filtered_pairs.append((i, idx, dist_val))

            pbar.update(1)

    return {
        "names": names,
        "filtered_pairs": filtered_pairs,
    }


def move_duplicate_files_with_progress(
    duplicates_dict, src_dir: str = "", dst_dir: str = ""
):
    """Enhanced version of move_duplicate_files with progress tracking."""
    import os
    import shutil

    os.makedirs(dst_dir, exist_ok=True)

    names = duplicates_dict["names"]
    duplicates = duplicates_dict["filtered_pairs"]

    if not duplicates:
        print_info("No duplicates to move")
        return

    seen_indices = set()
    for i, j, _ in duplicates:
        seen_indices.add(i)
        seen_indices.add(j)

    # Create progress bar for file moving
    with tqdm(total=len(seen_indices), desc="Moving duplicates", unit="file") as pbar:
        moved_count = 0
        for idx in seen_indices:
            filename = names[idx]
            src_path = os.path.join(src_dir, filename)
            dst_path = os.path.join(dst_dir, filename)

            if not os.path.exists(src_path):
                print_warning(f"File not found: {src_path}")
                pbar.update(1)
                continue

            if os.path.exists(dst_path):
                pbar.update(1)
                continue

            try:
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.move(src_path, dst_path)
                moved_count += 1
            except Exception as e:
                print_warning(f"Failed to move {filename}: {e}")

            pbar.update(1)

    print_success(f"✅ Moved {moved_count} duplicate files to: {dst_dir}")


def get_embedded_model_enum(model_name: str):
    """Helper function to map string names to PepeDP EmbeddedModel enum values."""
    # Import here to avoid hanging at module load time
    from pepedp.embedding.enum import EmbeddedModel

    model_mapping = {
        "ConvNextS": EmbeddedModel.ConvNextS,
        "ConvNextL": EmbeddedModel.ConvNextL,
        "VITS": EmbeddedModel.VITS,
        "VITB": EmbeddedModel.VITB,
        "VITL": EmbeddedModel.VITL,
        "VITG": EmbeddedModel.VITG,
    }
    return model_mapping.get(model_name, EmbeddedModel.ConvNextS)


def get_threshold_alg_enum(alg_name: str):
    """Helper function to map string names to PepeDP ThresholdAlg enum values."""
    # Import here to avoid hanging at module load time
    from pepedp.torch_enum import ThresholdAlg

    alg_mapping = {
        "HIPERIQA": ThresholdAlg.HIPERIQA,
        "ANIIQA": ThresholdAlg.ANIIQA,
        "TOPIQ": ThresholdAlg.TOPIQ,
        "BLOCKINESS": ThresholdAlg.BLOCKINESS,
        "IC9600": ThresholdAlg.IC9600,
    }
    return alg_mapping.get(alg_name, ThresholdAlg.HIPERIQA)


# --- 1. Best Tile Extraction ---
def best_tile_extraction_action(
    in_folder: str = None,
    out_folder: str = None,
    tile_size: int = None,
    process_type: str = None,
    scale: int = None,
    dynamic_n_tiles: bool = None,
    threshold: float = None,
    image_gray: bool = None,
    func_type: str = None,  # 'Laplacian' or 'IC9600'
    median_blur: int = None,
):
    print_info("DEBUG: best_tile_extraction_action called with:")
    print_info(f"  in_folder={in_folder}")
    print_info(f"  out_folder={out_folder}")
    print_info(f"  tile_size={tile_size}")
    print_info(f"  process_type={process_type}")
    print_info(f"  scale={scale}")
    print_info(f"  dynamic_n_tiles={dynamic_n_tiles}")
    print_info(f"  threshold={threshold}")
    print_info(f"  image_gray={image_gray}")
    print_info(f"  func_type={func_type}")
    print_info(f"  median_blur={median_blur}")
    print_info("[pepedp] Best Tile Extraction")
    try:
        if in_folder is None:
            print_info("DEBUG: in_folder missing, prompting user...")
            from dataset_forge.utils.color import Mocha

            print_header(
                "🧩 Best Tile Extraction (PepeDP) - Input/Output Selection",
                color=Mocha.pink,
            )
            in_folder = get_folder_path("Input folder")
        if out_folder is None:
            print_info("DEBUG: out_folder missing, prompting user...")
            out_folder = get_folder_path("Output folder")
        if tile_size is None:
            print_info("DEBUG: tile_size missing, prompting user...")
            tile_size = ask_int("Tile size", default=512, min_value=32)
        if process_type is None:
            print_info("DEBUG: process_type missing, prompting user...")
            process_type = ask_choice("Process type", ["FOR", "THREAD"], default=1)
        if scale is None:
            print_info("DEBUG: scale missing, prompting user...")
            scale = ask_int("Scale", default=1, min_value=1)
        if dynamic_n_tiles is None:
            print_info("DEBUG: dynamic_n_tiles missing, prompting user...")
            dynamic_n_tiles = ask_yes_no("Dynamic n_tiles?", default=True)
        if threshold is None:
            print_info("DEBUG: threshold missing, prompting user...")
            threshold = ask_float("Threshold", default=0.0)
        if image_gray is None:
            print_info("DEBUG: image_gray missing, prompting user...")
            image_gray = ask_yes_no("Convert to grayscale?", default=True)
        if func_type is None:
            print_info("DEBUG: func_type missing, prompting user...")
            func_type = ask_choice(
                "Complexity function", ["Laplacian", "IC9600"], default=0
            )
        # Build the complexity function object
        if func_type == "Laplacian":
            if median_blur is None:
                print_info("DEBUG: median_blur missing, prompting user...")
                median_blur = ask_int("Median blur", default=5, min_value=1)
            func = pepedp_laplacian_complexity(median_blur=median_blur)
        else:
            func = pepedp_ic9600_complexity()

        print_info(f"DEBUG: Instantiating BestTile with func={func}")

        # Initialize BestTile with progress tracking
        print_header("🔧 Initializing Best Tile Extraction")
        print_info(f"Input folder: {in_folder}")
        print_info(f"Output folder: {out_folder}")
        print_info(f"Tile size: {tile_size}, Scale: {scale}")
        print_info(f"Complexity function: {func_type}")

        bt = pepedp_best_tile(
            in_folder=in_folder,
            out_folder=out_folder,
            tile_size=tile_size,
            process_type=getattr(pepedp_enum.ProcessType, process_type),
            scale=scale,
            dynamic_n_tiles=dynamic_n_tiles,
            threshold=threshold,
            image_gray=image_gray,
            func=func,
        )

        # --- Print heading before processing ---
        print_header("🧩 Processing Best Tiles")
        print_info("Extracting best tiles from images...")

        print_info("DEBUG: Running BestTile.run()...")
        try:
            bt.run()
        except Exception as e:
            print_error(f"Error during Best Tile Extraction: {e}")
            print_info("This may be due to file access conflicts. Try:")
            print_info("1. Close any applications that might be accessing the images")
            print_info(
                "2. Ensure the output folder is not being accessed by other programs"
            )
            print_info(
                "3. Try running with a smaller batch or different output location"
            )
            # Assuming log_operation is defined elsewhere or will be added.
            # For now, we'll just print the error and return.
            return

        print_info("DEBUG: BestTile.run() complete.")
        print_success("Best tile extraction complete.")
        play_done_sound()

    except Exception as e:
        print_error(f"Error in best_tile_extraction_action: {e}")
        raise


# --- 2. Video Frame Extraction with Embedding-Based Deduplication ---
def video_frame_extraction_action(
    video_path: str = None,
    out_folder: str = None,
    embed_model: str = None,
    amp: bool = None,
    scale: int = None,
    threshold: float = None,
    dist_fn_name: str = None,
):
    print_info("DEBUG: video_frame_extraction_action called with:")
    print_info(f"  video_path={video_path}")
    print_info(f"  out_folder={out_folder}")
    print_info(f"  embed_model={embed_model}")
    print_info(f"  amp={amp}")
    print_info(f"  scale={scale}")
    print_info(f"  threshold={threshold}")
    print_info(f"  dist_fn_name={dist_fn_name}")
    print_info("[pepedp] Video Frame Extraction")

    try:
        if embed_model is None:
            print_info("DEBUG: embed_model missing, prompting user...")
            # Use correct PepeDP enum attribute names
            embed_model = ask_choice(
                "Embedding model",
                [
                    "ConvNeXt_Small",
                    "ConvNeXt_Large",
                    "ViT_Small",
                    "ViT_Base",
                    "ViT_Large",
                    "ViT_Giant",
                ],
                default=0,
            )
        if amp is None:
            print_info("DEBUG: amp missing, prompting user...")
            amp = ask_yes_no("Use AMP? (float16)", default=True)
        if scale is None:
            print_info("DEBUG: scale missing, prompting user...")
            scale = ask_int("Downscale factor for embedding", default=4, min_value=1)
        if threshold is None:
            print_info("DEBUG: threshold missing, prompting user...")
            threshold = ask_float("Distance threshold (0.3-0.5 typical)", default=0.4)
        if dist_fn_name is None:
            print_info("DEBUG: dist_fn_name missing, prompting user...")
        dist_fn_name = ask_choice("Distance function", ["euclid", "cosine"], default=0)
    except Exception as e:
        print_error(f"Error in video_frame_extraction_action parameter setup: {e}")
        raise

    dist_fn = pepedp_euclid_dist if dist_fn_name == "euclid" else pepedp_cosine_dist

    # --- Print heading before input/output prompts ---
    from dataset_forge.utils.color import Mocha

    print_header(
        "🎬 Video Frame Extraction (PepeDP) - Input/Output Selection",
        color=Mocha.yellow,
    )
    if video_path is None:
        print_info("DEBUG: video_path missing, prompting user...")
        video_path = get_input("Video path", default="video.mp4")
    if out_folder is None:
        print_info("DEBUG: out_folder missing, prompting user...")
        out_folder = get_folder_path("Output folder")

    try:

        # Initialize embedder with progress tracking and error handling
        print_header("🔧 Initializing Embedding Model")
        try:
            embedder = safe_model_initialization(
                model_enum=get_embedded_model_enum(embed_model),
                amp=amp,
                scale=scale,
                max_retries=3,
            )
        except Exception as e:
            print_error(f"❌ Failed to initialize embedding model: {e}")
            print_info("💡 Troubleshooting tips:")
            print_info("1. Check your internet connection")
            print_info(
                "2. Try using a different model (ConvNextS instead of ConvNextL)"
            )
            print_info("3. Clear your browser cache and try again")
            print_info("4. Check available disk space")
            log_operation("duplicate_detection", f"Model initialization failed: {e}")
            return

        print_info(
            f"DEBUG: Instantiating VideoToFrame with embedder={embedder}, threshold={threshold}, dist_fn={dist_fn}"
        )
        vtf = pepedp_video_to_frame(
            embedder=embedder,
            threshold=threshold,
            distance_fn=dist_fn,
        )

        # --- Print heading before processing ---
        print_header("🎬 Processing Video Frames")
        print_info(f"Processing video: {video_path}")
        print_info(f"Output folder: {out_folder}")
        print_info(f"Using threshold: {threshold}, Distance function: {dist_fn_name}")

        print_info("DEBUG: Calling VideoToFrame(video_path, out_folder)...")
        try:
            vtf(video_path, out_folder)
        except Exception as e:
            print_error(f"Error during Video Frame Extraction: {e}")
            print_info("This may be due to file access conflicts. Try:")
            print_info("1. Close any applications that might be accessing the video")
            print_info(
                "2. Ensure the output folder is not being accessed by other programs"
            )
            print_info("3. Try running with a different output location")
            log_operation("video_frame_extraction", f"Failed: {e}")
            return

        print_info("DEBUG: VideoToFrame call complete.")
        print_success("Video frame extraction complete.")
        play_done_sound()

    except Exception as e:
        print_error(f"Error in video_frame_extraction_action: {e}")
        raise


# --- 3. Duplicate Image Detection and Removal ---
def duplicate_image_detection_action(
    in_folder: str = None,
    out_folder: str = None,
    embed_model: str = None,
    amp: bool = None,
    scale: int = None,
    threshold: float = None,
    dist_fn_name: str = None,
):
    print_info("DEBUG: duplicate_image_detection_action called with:")
    print_info(f"  in_folder={in_folder}")
    print_info(f"  out_folder={out_folder}")
    print_info(f"  embed_model={embed_model}")
    print_info(f"  amp={amp}")
    print_info(f"  scale={scale}")
    print_info(f"  threshold={threshold}")
    print_info(f"  dist_fn_name={dist_fn_name}")
    print_info("[pepedp] Duplicate Image Detection and Removal")

    try:
        if embed_model is None:
            print_info("DEBUG: embed_model missing, prompting user...")
            # Fix: Access enum values directly based on actual PepeDP enum attributes
            embed_model = ask_choice(
                "Embedding model",
                ["ConvNextS", "ConvNextL", "VITS", "VITB", "VITL", "VITG"],
                default=0,
            )
        if amp is None:
            print_info("DEBUG: amp missing, prompting user...")
            amp = ask_yes_no("Use AMP? (float16)", default=True)
        if scale is None:
            print_info("DEBUG: scale missing, prompting user...")
            scale = ask_int("Downscale factor for embedding", default=4, min_value=1)
        if threshold is None:
            print_info("DEBUG: threshold missing, prompting user...")
            threshold = ask_float("Distance threshold for duplicates", default=1.5)
        if dist_fn_name is None:
            print_info("DEBUG: dist_fn_name missing, prompting user...")
            dist_fn_name = ask_choice(
                "Distance function", ["euclid", "cosine"], default=0
            )
        dist_fn = pepedp_euclid_dist if dist_fn_name == "euclid" else pepedp_cosine_dist
        if in_folder is None:
            print_info("DEBUG: in_folder missing, prompting user...")
            in_folder = get_folder_path("Input folder")
        if out_folder is None:
            print_info("DEBUG: out_folder missing, prompting user...")
            out_folder = get_folder_path("Output folder")

        # Initialize embedder with progress tracking and error handling
        print_header("🔧 Initializing Embedding Model")
        try:
            embedder = safe_model_initialization(
                model_enum=get_embedded_model_enum(embed_model),
                amp=amp,
                scale=scale,
                max_retries=3,
            )
        except Exception as e:
            print_error(f"❌ Failed to initialize embedding model: {e}")
            print_info("💡 Troubleshooting tips:")
            print_info("1. Check your internet connection")
            print_info(
                "2. Try using a different model (ConvNextS instead of ConvNextL)"
            )
            print_info("3. Clear your browser cache and try again")
            print_info("4. Check available disk space")
            log_operation("video_frame_extraction", f"Model initialization failed: {e}")
            return

        # Create embeddings with progress tracking
        print_header("📊 Creating Image Embeddings")
        print_info(f"Processing images from: {in_folder}")
        try:
            embedded = create_embedd_with_progress(
                img_folder=in_folder,
                embedder=embedder,
            )

            # Show embedding completion
            num_images = len(embedded)
            print_success(f"✅ Created embeddings for {num_images} images")

            # Find duplicate pairs with progress tracking
            print_header("🔍 Finding Duplicate Pairs")
            print_info(
                f"Using threshold: {threshold}, Distance function: {dist_fn_name}"
            )

            paired = filtered_pairs_with_progress(
                embeddings=embedded,
                dist_func=dist_fn,
                threshold=threshold,
            )

            # Show duplicate detection completion
            num_duplicates = len(paired.get("filtered_pairs", []))
            print_success(f"✅ Found {num_duplicates} duplicate pairs")

            # Move duplicate files with progress tracking
            if num_duplicates > 0:
                print_header("📁 Moving Duplicate Files")
                print_info(f"Moving duplicates to: {out_folder}")

                move_duplicate_files_with_progress(
                    duplicates_dict=paired,
                    src_dir=in_folder,
                    dst_dir=out_folder,
                )

                print_success(f"✅ Successfully moved {num_duplicates} duplicate files")
            else:
                print_success("✅ No duplicates found - no files to move")

        except Exception as e:
            print_error(f"Error during Duplicate Detection: {e}")
            print_info("This may be due to file access conflicts. Try:")
            print_info("1. Close any applications that might be accessing the images")
            print_info(
                "2. Ensure the output folder is not being accessed by other programs"
            )
            print_info("3. Try running with a different output location")
            log_operation("duplicate_detection", f"Failed: {e}")
            return

        print_success("Duplicate image detection and removal complete.")
        play_done_sound()

    except Exception as e:
        print_error(f"Error in duplicate_image_detection_action: {e}")
        raise


# --- 4. Threshold-Based Image Filtering (IQA) ---
def iqa_filtering_action(
    in_folder: str = None,
    out_folder: str = None,
    iqa_model: str = None,
    batch_size: int = None,
    threshold: float = None,
    median_threshold: float = None,
):
    print_info("DEBUG: iqa_filtering_action called with:")
    print_info(f"  in_folder={in_folder}")
    print_info(f"  out_folder={out_folder}")
    print_info(f"  iqa_model={iqa_model}")
    print_info(f"  batch_size={batch_size}")
    print_info(f"  threshold={threshold}")
    print_info(f"  median_threshold={median_threshold}")
    print_info("[pepedp] IQA Filtering")
    try:
        if iqa_model is None:
            print_info("DEBUG: iqa_model missing, prompting user...")
            # Fix: Access enum values directly based on PepeDP documentation
            iqa_model = ask_choice(
                "IQA model",
                ["HIPERIQA", "ANIIQA", "TOPIQ", "BLOCKINESS", "IC9600"],
                default=0,
            )
        if batch_size is None:
            print_info("DEBUG: batch_size missing, prompting user...")
            batch_size = ask_int("Batch size", default=1, min_value=1)
            print_info(
                "Note: Using batch size 1 to avoid tensor size mismatch errors with different image dimensions"
            )
        if threshold is None:
            print_info("DEBUG: threshold missing, prompting user...")
            threshold = ask_float("IQA threshold (0-1 typical)", default=0.5)
        if median_threshold is None:
            print_info("DEBUG: median_threshold missing, prompting user...")
            median_threshold = ask_float("Median threshold (0-1, 0=off)", default=0.5)
        if in_folder is None:
            print_info("DEBUG: in_folder missing, prompting user...")
            in_folder = get_folder_path("Input folder")

        # Prompt for output folder with options
        if out_folder is None:
            print_info("DEBUG: out_folder missing, prompting user...")
            print_info("What would you like to do with low-quality images?")
            print_info("1. Move to output folder")
            print_info("2. Delete them (no output folder)")

            choice = input("Enter choice (1-2, default: 1): ").strip() or "1"

            if choice == "1":
                out_folder = get_folder_path("Output folder for low-quality images")
                if not out_folder:
                    print_warning(
                        "No output folder specified. Low-quality images will be deleted."
                    )
                    out_folder = None
            else:
                print_warning("Low-quality images will be deleted.")
                out_folder = None

        # Initialize IQA algorithm with progress tracking
        print_header("🔧 Initializing IQA Filtering")
        print_info(f"Input folder: {in_folder}")
        print_info(
            f"Output folder: {out_folder if out_folder else 'DELETE (no output folder specified)'}"
        )
        print_info(f"IQA model: {iqa_model}")
        print_info(f"Batch size: {batch_size}, Threshold: {threshold}")

        alg_enum = getattr(pepedp_threshold_alg.ThresholdAlg, iqa_model)
        print_info(f"DEBUG: Instantiating {iqa_model}.value(...) for IQA filtering")
        alg = alg_enum.value(
            img_dir=in_folder,
            batch_size=batch_size,
            threshold=threshold,
            median_threshold=median_threshold,
            move_folder=out_folder,
        )

        # --- Print heading before processing ---
        print_header("🧪 Processing IQA Filtering")
        print_info("Filtering images based on quality scores...")

        print_info("DEBUG: Running IQA filtering algorithm...")
        try:
            alg()
        except Exception as e:
            error_msg = str(e)
            if "stack expects each tensor to be equal size" in error_msg:
                print_error(f"Tensor size mismatch error: {e}")
                print_info(
                    "This error occurs when processing images of different sizes in the same batch."
                )
                print_info("Attempting to retry with batch size 1...")

                # Retry with batch size 1
                try:
                    alg_retry = alg_enum.value(
                        img_dir=in_folder,
                        batch_size=1,  # Force batch size 1
                        threshold=threshold,
                        median_threshold=median_threshold,
                        move_folder=out_folder,
                    )
                    print_info("Retrying with batch size 1...")
                    alg_retry()
                except Exception as e2:
                    print_error(f"Error during IQA Filtering (batch size 1): {e2}")
                    print_info("Troubleshooting tips:")
                    print_info("1. Ensure all images are valid and not corrupted")
                    print_info("2. Try processing a smaller subset of images")
                    print_info("3. Check available GPU memory")
                    print_info("4. Close other applications using GPU")
                    log_operation("iqa_filtering", f"Failed with batch size 1: {e2}")
                    return
            else:
                print_error(f"Error during IQA Filtering: {e}")
                print_info("This may be due to file access conflicts. Try:")
                print_info(
                    "1. Close any applications that might be accessing the images"
                )
                print_info(
                    "2. Ensure the output folder is not being accessed by other programs"
                )
                print_info("3. Try running with a different output location")
                log_operation("iqa_filtering", f"Failed: {e}")
                return

        print_info("DEBUG: IQA filtering complete.")
        print_success("IQA filtering complete.")
        play_done_sound()

    except Exception as e:
        print_error(f"Error in iqa_filtering_action: {e}")
        raise


def manual_cache_clear_action():
    """Manual action to clear corrupted model cache files."""
    print_header("🧹 Manual Model Cache Clear")
    print_info(
        "This will clear corrupted model cache files that may be causing download issues."
    )

    try:
        # Clear all common model cache locations
        cache_locations = [
            os.path.expanduser("~/.cache/torch/hub/checkpoints/"),
            os.path.expanduser("~/.cache/torch/hub/"),
            os.path.join(os.getcwd(), ".cache", "torch", "hub", "checkpoints"),
        ]

        cleared_files = []
        for cache_dir in cache_locations:
            if os.path.exists(cache_dir):
                print_info(f"Checking cache directory: {cache_dir}")
                for file in os.listdir(cache_dir):
                    if file.endswith(".pth") or "convnext" in file.lower():
                        file_path = os.path.join(cache_dir, file)
                        try:
                            os.remove(file_path)
                            cleared_files.append(file_path)
                            print_info(f"✅ Removed: {file}")
                        except Exception as e:
                            print_warning(f"Could not remove {file}: {e}")

        if cleared_files:
            print_success(f"✅ Successfully cleared {len(cleared_files)} cache files")
            print_info("You can now retry the model download.")
        else:
            print_info("No cache files found to clear.")

    except Exception as e:
        print_error(f"Error clearing cache: {e}")

    play_done_sound()


# Only export the new wrappers
__all__ = [
    "best_tile_extraction_action",
    "video_frame_extraction_action",
    "duplicate_image_detection_action",
    "iqa_filtering_action",
]
