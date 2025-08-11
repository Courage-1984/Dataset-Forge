from dataset_forge.actions.dataset_ops_actions import DatasetCombiner
from dataset_forge.actions.de_dupe_actions import (
    compute_hashes,
    find_duplicates,
    find_near_duplicates,
    align_and_operate_on_pairs,
)
from dataset_forge.actions.batch_rename_actions import (
    batch_rename_single_folder,
    batch_rename_hq_lq_folders,
)
from dataset_forge.actions.orientation_organizer_actions import (
    organize_images_by_orientation,
    organize_hq_lq_by_orientation,
)
from dataset_forge.actions.operations_actions import (
    extract_random_pairs as _extract_random_pairs,
    shuffle_image_pairs as _shuffle_image_pairs,
    split_adjust_dataset as _split_adjust_dataset,
    remove_small_image_pairs as _remove_small_image_pairs,
    split_single_folder_in_sets as _split_single_folder_in_sets,
)
import os
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.printing import (
    print_header,
    print_section,
    print_success,
    print_error,
    print_info,
    print_prompt,
)
from dataset_forge.dpid import (
    run_basicsr_dpid_single_folder,
    run_basicsr_dpid_hq_lq,
    run_openmmlab_dpid_single_folder,
    run_openmmlab_dpid_hq_lq,
    run_phhofm_dpid_single_folder,
    run_phhofm_dpid_hq_lq,
)
from dataset_forge.dpid.umzi_dpid import (
    run_umzi_dpid_single_folder,
    run_umzi_dpid_hq_lq,
)
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.color import Mocha
import threading


def create_multiscale_dataset(*args, **kwargs):
    print_header("🎯 Create Multiscale Dataset (DPID)")
    print_section("Select DPID method:")
    print_info("[1] BasicSR DPID")
    print_info("[2] OpenMMLab DPID")
    print_info("[3] 🌟 Phhofm DPID (Recommended)")
    print_info("[4] 🌟 Umzi DPID (Recommended)")
    method = input("Enter choice [1-4]: ").strip()
    if method not in {"1", "2", "3", "4"}:
        print_error("Invalid method.")
        print_prompt("Press Enter to return to the menu...")
        input()
        return
    print_section("Select mode:")
    print_info("[1] Single folder")
    print_info("[2] HQ/LQ paired folders")
    mode = input("Enter choice [1-2]: ").strip()
    if mode not in {"1", "2"}:
        print_error("Invalid mode.")
        print_prompt("Press Enter to return to the menu...")
        input()
        return
    print_section("Select downscale factor:")
    print_info("[1] 25% (0.25)")
    print_info("[2] 50% (0.5)")
    print_info("[3] 75% (0.75)")
    print_info("[4] 25%, 50% AND 75% (all)")
    scale_choice = input("Enter choice [1-4]: ").strip()
    if scale_choice == "1":
        scales = [0.25]
    elif scale_choice == "2":
        scales = [0.5]
    elif scale_choice == "3":
        scales = [0.75]
    elif scale_choice == "4":
        scales = [0.25, 0.5, 0.75]
    else:
        print_error("Invalid scale choice.")
        print_prompt("Press Enter to return to the menu...")
        input()
        return
    overwrite = input("Overwrite existing files? [y/N]: ").strip().lower() == "y"
    dpid_kwargs = {}
    if method in {"1", "2"}:
        print_section("DPID kernel parameters (press Enter for defaults):")
        kernel_size = input("DPID kernel size [default 21]: ").strip()
        sigma = input("DPID sigma [default 2.0]: ").strip()
        lambd = input("DPID lambda [default 0.5]: ").strip()
        dpid_kwargs["kernel_size"] = int(kernel_size) if kernel_size else 21
        dpid_kwargs["sigma"] = float(sigma) if sigma else 2.0
        dpid_kwargs["lambd"] = float(lambd) if lambd else 0.5
        isotropic = input("Isotropic kernel? [Y/n]: ").strip().lower()
        if isotropic in ("", "y", "yes"):
            dpid_kwargs["isotropic"] = True
        else:
            dpid_kwargs["isotropic"] = False
            sig_x = input("sig_x [default 2.0]: ").strip()
            sig_y = input("sig_y [default 2.0]: ").strip()
            theta = input("theta (radians, default 0.0): ").strip()
            dpid_kwargs["sig_x"] = float(sig_x) if sig_x else 2.0
            dpid_kwargs["sig_y"] = float(sig_y) if sig_y else 2.0
            dpid_kwargs["theta"] = float(theta) if theta else 0.0
    elif method == "3":
        print_section("DPID lambda parameter (press Enter for default 0.5):")
        lambd = input("DPID lambda [default 0.5]: ").strip()
        dpid_kwargs["lambd"] = float(lambd) if lambd else 0.5
    elif method == "4":
        print_section("DPID lambda parameter (press Enter for default 0.5):")
        lambd = input("DPID lambda [default 0.5]: ").strip()
        dpid_kwargs["lambd"] = float(lambd) if lambd else 0.5

    # --- Print heading before input/output folder prompts ---
    from dataset_forge.utils.color import Mocha

    if mode == "1":
        if method == "1":
            print_header("[BasicSR DPID] Input/Output Selection", color=Mocha.blue)
        elif method == "2":
            print_header(
                "[OpenMMLab DPID] Input/Output Selection", color=Mocha.sapphire
            )
        elif method == "3":
            print_header("[Phhofm DPID] Input/Output Selection", color=Mocha.green)
        elif method == "4":
            print_header("[Umzi DPID] Input/Output Selection", color=Mocha.mauve)
        input_folder = input("Enter input folder path: ").strip()
        output_base = input("Enter output base folder path: ").strip()
        # --- Print heading before progress bar ---
        if method == "1":
            print_section("BasicSR DPID Progress", color=Mocha.blue)
            run_basicsr_dpid_single_folder(
                input_folder, output_base, scales, overwrite=overwrite, **dpid_kwargs
            )
        elif method == "2":
            print_section("OpenMMLab DPID Progress", color=Mocha.sapphire)
            run_openmmlab_dpid_single_folder(
                input_folder, output_base, scales, overwrite=overwrite, **dpid_kwargs
            )
        elif method == "3":
            print_section("Phhofm DPID Progress", color=Mocha.green)
            run_phhofm_dpid_single_folder(
                input_folder, output_base, scales, overwrite=overwrite
            )
        elif method == "4":
            print_section("Umzi DPID Progress", color=Mocha.mauve)
            run_umzi_dpid_single_folder(
                input_folder, output_base, scales, overwrite=overwrite, **dpid_kwargs
            )
    else:
        if method == "1":
            print_header(
                "[BasicSR DPID] HQ/LQ Input/Output Selection", color=Mocha.blue
            )
        elif method == "2":
            print_header(
                "[OpenMMLab DPID] HQ/LQ Input/Output Selection", color=Mocha.sapphire
            )
        elif method == "3":
            print_header(
                "[Phhofm DPID] HQ/LQ Input/Output Selection", color=Mocha.green
            )
        elif method == "4":
            print_header("[Umzi DPID] HQ/LQ Input/Output Selection", color=Mocha.mauve)
        hq_folder = input("Enter HQ folder path: ").strip()
        lq_folder = input("Enter LQ folder path: ").strip()
        out_hq_base = input("Enter output HQ base folder path: ").strip()
        out_lq_base = input("Enter output LQ base folder path: ").strip()
        # --- Print heading before progress bar ---
        if method == "1":
            print_section("BasicSR DPID Progress", color=Mocha.blue)
            run_basicsr_dpid_hq_lq(
                hq_folder,
                lq_folder,
                out_hq_base,
                out_lq_base,
                scales,
                overwrite=overwrite,
                **dpid_kwargs,
            )
        elif method == "2":
            print_section("OpenMMLab DPID Progress", color=Mocha.sapphire)
            run_openmmlab_dpid_hq_lq(
                hq_folder,
                lq_folder,
                out_hq_base,
                out_lq_base,
                scales,
                overwrite=overwrite,
                **dpid_kwargs,
            )
        elif method == "3":
            print_section("Phhofm DPID Progress", color=Mocha.green)
            run_phhofm_dpid_hq_lq(
                hq_folder,
                lq_folder,
                out_hq_base,
                out_lq_base,
                scales,
                overwrite=overwrite,
            )
        elif method == "4":
            print_section("Umzi DPID Progress", color=Mocha.mauve)
            run_umzi_dpid_hq_lq(
                hq_folder,
                lq_folder,
                out_hq_base,
                out_lq_base,
                scales,
                overwrite=overwrite,
                **dpid_kwargs,
            )
    print_success("Multiscale dataset creation complete!")
    play_done_sound()
    print_prompt("Press Enter to return to the menu...")
    input()


def combine_datasets():
    """Combine multiple HQ/LQ datasets into one."""
    combiner = DatasetCombiner()
    combiner.run()


def extract_random_pairs(hq_folder, lq_folder):
    """Extract random HQ/LQ image pairs from the dataset."""
    return _extract_random_pairs(hq_folder, lq_folder)


def shuffle_image_pairs(hq_folder, lq_folder):
    """Shuffle HQ/LQ image pairs while maintaining alignment."""
    return _shuffle_image_pairs(hq_folder, lq_folder)


def split_single_folder_in_sets(folder):
    """Split a single folder of images into N sets with progress bar and operation choice."""
    return _split_single_folder_in_sets(folder)


def split_adjust_dataset(hq_folder, lq_folder):
    """Split and adjust the dataset according to user parameters."""
    if not lq_folder:
        return split_single_folder_in_sets(hq_folder)
    return _split_adjust_dataset(hq_folder, lq_folder)


def remove_small_image_pairs(hq_folder, lq_folder):
    """Remove HQ/LQ image pairs that are below a minimum size."""
    return _remove_small_image_pairs(hq_folder, lq_folder)


@monitor_all("de_dupe", critical_on_error=True)
def de_dupe(
    hq_folder,
    lq_folder=None,
    hash_type="phash",
    mode="exact",
    max_dist=5,
    op="move",
    dest_dir=None,
):
    """Detect and handle duplicate or near-duplicate images. If lq_folder is None or blank, only dedupe in hq_folder."""
    hq_hashes = compute_hashes(hq_folder, hash_func=hash_type)
    if not hq_hashes:
        print_info("No images found in HQ folder.")
        return
    if mode == "near":
        groups = find_near_duplicates(hq_hashes, max_distance=max_dist) or []
    else:
        groups = find_duplicates(hq_hashes) or []
    if not groups:
        print_info("No duplicates or near-duplicates found.")
        return
    import threading

    thread = threading.Thread(target=lambda: None)
    task_registry.register_thread(thread)
    if lq_folder:
        # Progress bar for paired deduplication
        for group in tqdm(groups, desc="Processing duplicate groups"):
            align_and_operate_on_pairs(
                [group], hq_folder, lq_folder, op=op, dest_dir=dest_dir
            )
    else:
        # Only operate on HQ folder, with progress bar
        for group in tqdm(groups, desc="Processing duplicate groups"):
            to_operate = list(group)[1:]
            for fname in to_operate:
                hq_path = os.path.join(hq_folder, fname)
                if op == "delete":
                    if os.path.exists(hq_path):
                        os.remove(hq_path)
                        print_info(f"Deleted {hq_path}")
                elif op in ("move", "copy"):
                    if dest_dir and "hq" in dest_dir:
                        dest = os.path.join(dest_dir["hq"], fname)
                        os.makedirs(dest_dir["hq"], exist_ok=True)
                        if op == "move":
                            os.rename(hq_path, dest)
                            print_info(f"Moved {hq_path} -> {dest}")
                        elif op == "copy":
                            import shutil

                            shutil.copy2(hq_path, dest)
                            print_info(f"Copied {hq_path} -> {dest}")
    clear_memory()
    clear_cuda_cache()
    print_success("Deduplication complete.")
    play_done_sound()


def batch_rename(
    input_path, hq_path=None, lq_path=None, prefix="", padding=5, dry_run=True
):
    """Batch rename images in a folder or HQ/LQ pair."""
    if hq_path and lq_path:
        batch_rename_hq_lq_folders(
            hq_path, lq_path, prefix=prefix, padding=padding, dry_run=dry_run
        )
    else:
        batch_rename_single_folder(
            input_path, prefix=prefix, padding=padding, dry_run=dry_run
        )


def images_orientation_organization(*args, **kwargs):
    """Organize images by orientation (landscape, portrait, square)."""
    # This function can call organize_images_by_orientation or organize_hq_lq_by_orientation based on args
    if "hq_folder" in kwargs and "lq_folder" in kwargs:
        return organize_hq_lq_by_orientation(
            kwargs["hq_folder"],
            kwargs["lq_folder"],
            kwargs["output_hq_folder"],
            kwargs["output_lq_folder"],
            kwargs["orientations"],
            kwargs.get("operation", "copy"),
        )
    else:
        return organize_images_by_orientation(
            kwargs["input_folder"],
            kwargs["output_folder"],
            kwargs["orientations"],
            kwargs.get("operation", "copy"),
        )


def filter_non_images(
    folder: str = None,
    hq_folder: str = None,
    lq_folder: str = None,
    operation: str = "move",
    dest_dir: str = None,
    dry_run: bool = False,
):
    """
    Filter non-image files from a folder or HQ/LQ pair.

    Args:
        folder: Single folder path (if provided, process all files in this folder)
        hq_folder: HQ folder path (for paired mode)
        lq_folder: LQ folder path (for paired mode)
        operation: 'copy', 'move', or 'delete'
        dest_dir: Destination directory for copy/move (ignored for delete)
        dry_run: If True, only print what would be done

    Returns:
        Dict with counts of processed and skipped files

    Raises:
        ValueError: If no valid folder(s) provided

    Example:
        >>> filter_non_images(folder="/path/to/folder", operation="delete")
        >>> filter_non_images(hq_folder="/hq", lq_folder="/lq", operation="move", dest_dir="/out")
    """
    import os
    from dataset_forge.utils.file_utils import is_image_file, get_unique_filename
    from dataset_forge.utils.progress_utils import tqdm, image_map
    from dataset_forge.utils.printing import (
        print_info,
        print_success,
        print_warning,
        print_error,
    )
    import shutil

    def _filter_in_folder(src_folder, op, dest=None):
        files = [
            f
            for f in os.listdir(src_folder)
            if os.path.isfile(os.path.join(src_folder, f))
        ]
        non_images = [f for f in files if not is_image_file(f)]
        if not non_images:
            print_info(f"No non-image files found in {src_folder}.")
            return {"processed": 0, "skipped": 0}
        print_info(f"Found {len(non_images)} non-image files in {src_folder}.")
        processed = 0
        skipped = 0
        for fname in tqdm(
            non_images, desc=f"Filtering non-images in {os.path.basename(src_folder)}"
        ):
            src_path = os.path.join(src_folder, fname)
            try:
                if dry_run:
                    print_info(
                        f"[Dry run] Would {op} {src_path}{' to ' + dest if dest else ''}"
                    )
                    continue
                if op == "delete":
                    os.remove(src_path)
                elif op in ("move", "copy"):
                    if not dest:
                        print_error(
                            f"Destination directory required for {op} operation."
                        )
                        skipped += 1
                        continue
                    os.makedirs(dest, exist_ok=True)
                    dest_path = os.path.join(dest, get_unique_filename(dest, fname))
                    if op == "move":
                        shutil.move(src_path, dest_path)
                    else:
                        shutil.copy2(src_path, dest_path)
                processed += 1
            except Exception as e:
                print_warning(f"Failed to {op} {src_path}: {e}")
                skipped += 1
        print_success(f"{op.title()}d {processed} non-image files from {src_folder}.")
        return {"processed": processed, "skipped": skipped}

    results = {}
    if folder:
        results[folder] = _filter_in_folder(folder, operation, dest_dir)
    elif hq_folder and lq_folder:
        dest_hq = (
            os.path.join(dest_dir, "hq")
            if dest_dir and operation in ("move", "copy")
            else None
        )
        dest_lq = (
            os.path.join(dest_dir, "lq")
            if dest_dir and operation in ("move", "copy")
            else None
        )
        results["hq"] = _filter_in_folder(hq_folder, operation, dest_hq)
        results["lq"] = _filter_in_folder(lq_folder, operation, dest_lq)
    else:
        raise ValueError(
            "Must provide either a single folder or both hq_folder and lq_folder."
        )
    return results


dedupe = de_dupe
