import os
from dataset_forge.utils.progress_utils import tqdm
from typing import Optional
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound

# You may need to adjust these imports based on your project structure
# from .run_best_tile_ic9600 import BestTile, IC9600Complexity, ProcessType
# For now, let's assume the relevant classes are copied here or imported correctly

# --- Placeholders for actual implementations (copy from run_best_tile_ic9600.py as needed) ---
# from run_best_tile_ic9600 import BestTile, IC9600Complexity, ProcessType

# For now, let's import from store/run_best_tile_ic9600.py if possible, or copy the classes here
# (You may want to refactor these into a shared utils module in the future)


# --- Main Tiling Functionality ---
def run_ic9600_tiling(
    hq_folder: Optional[str] = None,
    lq_folder: Optional[str] = None,
    single_folder: Optional[str] = None,
    out_hq_folder: Optional[str] = None,
    out_lq_folder: Optional[str] = None,
    out_folder: Optional[str] = None,
    tile_size: int = 1024,
    process_type: str = "for",
    scale: int = 1,
    dynamic_n_tiles: bool = True,
    laplacian_thread: float = 0.01,
    image_gray: bool = False,
    device: str = "cuda",
):
    """
    Run IC9600 tiling on either HQ/LQ paired folders or a single folder.
    Maintains correct image pair alignment for HQ/LQ mode.
    """
    from store.run_best_tile_ic9600 import BestTile, IC9600Complexity, ProcessType

    if hq_folder and lq_folder:
        # HQ/LQ paired mode
        assert (
            out_hq_folder and out_lq_folder
        ), "Output folders for HQ and LQ must be specified."
        os.makedirs(out_hq_folder, exist_ok=True)
        os.makedirs(out_lq_folder, exist_ok=True)
        hq_images = set(os.listdir(hq_folder))
        lq_images = set(os.listdir(lq_folder))
        common_images = sorted(hq_images & lq_images)
        print(f"Found {len(common_images)} aligned HQ/LQ pairs.")
        # Process HQ
        hq_tiler = BestTile(
            in_folder=hq_folder,
            out_folder=out_hq_folder,
            tile_size=tile_size,
            process_type=ProcessType.FOR,
            scale=scale,
            dynamic_n_tiles=dynamic_n_tiles,
            laplacian_thread=laplacian_thread,
            image_gray=image_gray,
            func=IC9600Complexity(device=device),
        )
        # Process LQ
        lq_tiler = BestTile(
            in_folder=lq_folder,
            out_folder=out_lq_folder,
            tile_size=tile_size,
            process_type=ProcessType.FOR,
            scale=scale,
            dynamic_n_tiles=dynamic_n_tiles,
            laplacian_thread=laplacian_thread,
            image_gray=image_gray,
            func=IC9600Complexity(device=device),
        )
        # Only process aligned pairs
        hq_tiler.all_images = common_images
        lq_tiler.all_images = common_images
        print("Processing HQ images...")
        hq_tiler.run()
        print("Processing LQ images...")
        lq_tiler.run()
    elif single_folder:
        assert out_folder, "Output folder must be specified for single-folder mode."
        os.makedirs(out_folder, exist_ok=True)
        tiler = BestTile(
            in_folder=single_folder,
            out_folder=out_folder,
            tile_size=tile_size,
            process_type=ProcessType.FOR,
            scale=scale,
            dynamic_n_tiles=dynamic_n_tiles,
            laplacian_thread=laplacian_thread,
            image_gray=image_gray,
            func=IC9600Complexity(device=device),
        )
        print(f"Processing {len(tiler.all_images)} images in single-folder mode...")
        tiler.run()
    else:
        raise ValueError(
            "You must specify either (hq_folder and lq_folder) or single_folder."
        )
