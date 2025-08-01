# Umzi's Dataset_Preprocessing actions - now direct wrappers for pepedp
"""
Actions for Umzi's Dataset_Preprocessing integration using pepedp.
"""

from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
)
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.input_utils import (
    get_folder_path,
    get_input,
    ask_int,
    ask_float,
    ask_choice,
    ask_yes_no,
)
from dataset_forge.menus import session_state

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    pepedp,
    pepedpid,
    pepedp_enum,
    pepedp_best_tile as BestTile,
    pepedp_laplacian_complexity as LaplacianComplexity,
    pepedp_ic9600_complexity as IC9600Complexity,
    pepedp_img_to_embedding as ImgToEmbedding,
    pepedp_embedded_model as EmbeddedModel,
    pepedp_euclid_dist as euclid_dist,
    pepedp_cosine_dist as cosine_dist,
    pepedp_video_to_frame as VideoToFrame,
    pepedp_create_embedd as create_embedd,
    pepedp_filtered_pairs as filtered_pairs,
    pepedp_move_duplicate_files as move_duplicate_files,
    pepedp_threshold_alg as ThresholdAlg,
)


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
    print("DEBUG: best_tile_extraction_action called with:")
    print(f"  in_folder={in_folder}")
    print(f"  out_folder={out_folder}")
    print(f"  tile_size={tile_size}")
    print(f"  process_type={process_type}")
    print(f"  scale={scale}")
    print(f"  dynamic_n_tiles={dynamic_n_tiles}")
    print(f"  threshold={threshold}")
    print(f"  image_gray={image_gray}")
    print(f"  func_type={func_type}")
    print(f"  median_blur={median_blur}")
    print_info("[pepedp] Best Tile Extraction")
    try:
        if in_folder is None:
            print("DEBUG: in_folder missing, prompting user...")
            from dataset_forge.utils.color import Mocha

            print_header(
                "🧩 Best Tile Extraction (PepeDP) - Input/Output Selection",
                color=Mocha.pink,
            )
            in_folder = get_folder_path("Input folder")
        if out_folder is None:
            print("DEBUG: out_folder missing, prompting user...")
            out_folder = get_folder_path("Output folder")
        if tile_size is None:
            print("DEBUG: tile_size missing, prompting user...")
            tile_size = ask_int("Tile size", default=512, min_value=32)
        if process_type is None:
            print("DEBUG: process_type missing, prompting user...")
            process_type = ask_choice("Process type", ["FOR", "THREAD"], default=1)
        if scale is None:
            print("DEBUG: scale missing, prompting user...")
            scale = ask_int("Scale", default=1, min_value=1)
        if dynamic_n_tiles is None:
            print("DEBUG: dynamic_n_tiles missing, prompting user...")
            dynamic_n_tiles = ask_yes_no("Dynamic n_tiles?", default=True)
        if threshold is None:
            print("DEBUG: threshold missing, prompting user...")
            threshold = ask_float("Threshold", default=0.0)
        if image_gray is None:
            print("DEBUG: image_gray missing, prompting user...")
            image_gray = ask_yes_no("Convert to grayscale?", default=True)
        if func_type is None:
            print("DEBUG: func_type missing, prompting user...")
            func_type = ask_choice(
                "Complexity function", ["Laplacian", "IC9600"], default=0
            )
        # Build the complexity function object
        if func_type == "Laplacian":
            if median_blur is None:
                print("DEBUG: median_blur missing, prompting user...")
                median_blur = ask_int("Median blur", default=5, min_value=1)
            func = LaplacianComplexity(median_blur=median_blur)
        else:
            func = IC9600Complexity()
        print(f"DEBUG: Instantiating BestTile with func={func}")
        bt = BestTile(
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
        # --- Print heading before progress bar ---
        from dataset_forge.utils.color import Mocha

        print_header(
            "🧩 Best Tile Extraction (PepeDP) - Input/Output Selection",
            color=Mocha.pink,
        )
        print("DEBUG: Running BestTile.run()...")
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
        print("DEBUG: BestTile.run() complete.")
        print_success("Best tile extraction complete.")
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
    print("DEBUG: video_frame_extraction_action called with:")
    print(f"  video_path={video_path}")
    print(f"  out_folder={out_folder}")
    print(f"  embed_model={embed_model}")
    print(f"  amp={amp}")
    print(f"  scale={scale}")
    print(f"  threshold={threshold}")
    print(f"  dist_fn_name={dist_fn_name}")
    print_info("[pepedp] Video Frame Extraction")
    try:
        if embed_model is None:
            print("DEBUG: embed_model missing, prompting user...")
            embed_model = ask_choice(
                "Embedding model", [e.name for e in EmbeddedModel], default=0
            )
        if amp is None:
            print("DEBUG: amp missing, prompting user...")
            amp = ask_yes_no("Use AMP? (float16)", default=True)
        if scale is None:
            print("DEBUG: scale missing, prompting user...")
            scale = ask_int("Downscale factor for embedding", default=4, min_value=1)
        if threshold is None:
            print("DEBUG: threshold missing, prompting user...")
            threshold = ask_float("Distance threshold (0.3-0.5 typical)", default=0.4)
        if dist_fn_name is None:
            print("DEBUG: dist_fn_name missing, prompting user...")
            dist_fn_name = ask_choice(
                "Distance function", ["euclid", "cosine"], default=0
            )
        dist_fn = euclid_dist if dist_fn_name == "euclid" else cosine_dist
        # --- Print heading before input/output prompts ---
        from dataset_forge.utils.color import Mocha

        print_header(
            "🎬 Video Frame Extraction (PepeDP) - Input/Output Selection",
            color=Mocha.yellow,
        )
        if video_path is None:
            print("DEBUG: video_path missing, prompting user...")
            video_path = get_input("Video path", default="video.mp4")
        if out_folder is None:
            print("DEBUG: out_folder missing, prompting user...")
            out_folder = get_folder_path("Output folder")
        embedder = ImgToEmbedding(
            model=getattr(EmbeddedModel, embed_model),
            amp=amp,
            scale=scale,
        )
        print(
            f"DEBUG: Instantiating VideoToFrame with embedder={embedder}, threshold={threshold}, dist_fn={dist_fn}"
        )
        vtf = VideoToFrame(
            embedder=embedder,
            threshold=threshold,
            distance_fn=dist_fn,
        )
        # --- Print heading before progress bar ---
        print_header(
            "🎬 Video Frame Extraction (PepeDP) - Input/Output Selection",
            color=Mocha.yellow,
        )
        print("DEBUG: Calling VideoToFrame(video_path, out_folder)...")
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
        print("DEBUG: VideoToFrame call complete.")
        print_success("Video frame extraction complete.")
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
    print("DEBUG: duplicate_image_detection_action called with:")
    print(f"  in_folder={in_folder}")
    print(f"  out_folder={out_folder}")
    print(f"  embed_model={embed_model}")
    print(f"  amp={amp}")
    print(f"  scale={scale}")
    print(f"  threshold={threshold}")
    print(f"  dist_fn_name={dist_fn_name}")
    print_info("[pepedp] Duplicate Image Detection and Removal")
    try:
        if embed_model is None:
            print("DEBUG: embed_model missing, prompting user...")
            embed_model = ask_choice(
                "Embedding model", [e.name for e in EmbeddedModel], default=0
            )
        if amp is None:
            print("DEBUG: amp missing, prompting user...")
            amp = ask_yes_no("Use AMP? (float16)", default=True)
        if scale is None:
            print("DEBUG: scale missing, prompting user...")
            scale = ask_int("Downscale factor for embedding", default=4, min_value=1)
        if threshold is None:
            print("DEBUG: threshold missing, prompting user...")
            threshold = ask_float("Distance threshold for duplicates", default=1.5)
        if dist_fn_name is None:
            print("DEBUG: dist_fn_name missing, prompting user...")
            dist_fn_name = ask_choice(
                "Distance function", ["euclid", "cosine"], default=0
            )
        dist_fn = euclid_dist if dist_fn_name == "euclid" else cosine_dist
        if in_folder is None:
            print("DEBUG: in_folder missing, prompting user...")
            in_folder = get_folder_path("Input folder")
        if out_folder is None:
            print("DEBUG: out_folder missing, prompting user...")
            out_folder = get_folder_path("Output folder")
        embedder = ImgToEmbedding(
            model=getattr(EmbeddedModel, embed_model),
            amp=amp,
            scale=scale,
        )
        print(f"DEBUG: Calling create_embedd for {in_folder}...")
        try:
            embedded = create_embedd(
                img_folder=in_folder,
                embedder=embedder,
            )
            print(
                f"DEBUG: Calling filtered_pairs with threshold={threshold}, dist_fn={dist_fn}..."
            )
            paired = filtered_pairs(
                embeddings=embedded,
                dist_func=dist_fn,
                threshold=threshold,
            )
            print(f"DEBUG: Calling move_duplicate_files to {out_folder}...")
            move_duplicate_files(
                duplicates_dict=paired,
                src_dir=in_folder,
                dst_dir=out_folder,
            )
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
    print("DEBUG: iqa_filtering_action called with:")
    print(f"  in_folder={in_folder}")
    print(f"  out_folder={out_folder}")
    print(f"  iqa_model={iqa_model}")
    print(f"  batch_size={batch_size}")
    print(f"  threshold={threshold}")
    print(f"  median_threshold={median_threshold}")
    print_info("[pepedp] IQA Filtering")
    try:
        if iqa_model is None:
            print("DEBUG: iqa_model missing, prompting user...")
            iqa_model = ask_choice(
                "IQA model", [e.name for e in ThresholdAlg], default=0
            )
        if batch_size is None:
            print("DEBUG: batch_size missing, prompting user...")
            batch_size = ask_int("Batch size", default=8, min_value=1)
        if threshold is None:
            print("DEBUG: threshold missing, prompting user...")
            threshold = ask_float("IQA threshold (0-1 typical)", default=0.5)
        if median_threshold is None:
            print("DEBUG: median_threshold missing, prompting user...")
            median_threshold = ask_float("Median threshold (0-1, 0=off)", default=0.5)
        if in_folder is None:
            print("DEBUG: in_folder missing, prompting user...")
            in_folder = get_folder_path("Input folder")
        # out_folder is optional: if None, low-quality images are deleted
        alg_enum = getattr(ThresholdAlg, iqa_model)
        print(f"DEBUG: Instantiating {iqa_model}.value(...) for IQA filtering")
        alg = alg_enum.value(
            img_dir=in_folder,
            batch_size=batch_size,
            threshold=threshold,
            median_threshold=median_threshold,
            move_folder=out_folder,
        )
        print("DEBUG: Running IQA filtering algorithm...")
        try:
            alg()
        except Exception as e:
            print_error(f"Error during IQA Filtering: {e}")
            print_info("This may be due to file access conflicts. Try:")
            print_info("1. Close any applications that might be accessing the images")
            print_info(
                "2. Ensure the output folder is not being accessed by other programs"
            )
            print_info("3. Try running with a different output location")
            log_operation("iqa_filtering", f"Failed: {e}")
            return
        print("DEBUG: IQA filtering complete.")
        print_success("IQA filtering complete.")
    except Exception as e:
        print_error(f"Error in iqa_filtering_action: {e}")
        raise


# Only export the new wrappers
__all__ = [
    "best_tile_extraction_action",
    "video_frame_extraction_action",
    "duplicate_image_detection_action",
    "iqa_filtering_action",
]
