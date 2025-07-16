import os
import cv2
import numpy as np
from typing import Optional, List, Tuple
from dataset_forge.utils.input_utils import get_folder_path
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.memory_utils import clear_memory, memory_context
from dataset_forge.utils.file_utils import is_image_file
from dataset_forge.utils.history_log import log_operation


def align_images_workflow(
    folder1: Optional[str] = None,
    folder2: Optional[str] = None,
    output_folder: Optional[str] = None,
    recursive: bool = True,
    dry_run: bool = False,
) -> None:
    """
    Align images from two folders (matching by filename) using SIFT+FLANN projective transformation.
    Supports both flat and recursive (subfolder) batch processing.

    Args:
        folder1: Path to the first folder (source images to align)
        folder2: Path to the second folder (reference images)
        output_folder: Path to save aligned images
        recursive: Whether to process subfolders recursively
        dry_run: If True, only print what would be done

    Returns:
        None

    Raises:
        FileNotFoundError: If any input folder does not exist
        Exception: For unexpected errors during processing

    Example:
        >>> align_images_workflow('folderA', 'folderB', 'output', recursive=True)
    """
    print_info("\n🧭 Align Images Workflow (SIFT+FLANN)")
    try:
        if not folder1:
            folder1 = get_folder_path("Select the first folder (images to align)")
        if not folder2:
            folder2 = get_folder_path("Select the second folder (reference images)")
        if not output_folder:
            output_folder = get_folder_path(
                "Select the output folder for aligned images"
            )
        if not os.path.isdir(folder1) or not os.path.isdir(folder2):
            print_error("One or both input folders do not exist.")
            log_operation(
                "align_images", f"Failed: input folder missing: {folder1}, {folder2}"
            )
            return
        os.makedirs(output_folder, exist_ok=True)
        print_info(f"\nSource folder 1: {folder1}")
        print_info(f"Source folder 2: {folder2}")
        print_info(f"Output folder: {output_folder}")
        print_info(f"Recursive: {'Yes' if recursive else 'No'}")
        print_info(f"Dry run: {'Yes' if dry_run else 'No'}")

        # Gather all image files (flat or recursive)
        def gather_images(folder: str) -> List[str]:
            if recursive:
                files = []
                for root, _, filenames in os.walk(folder):
                    for f in filenames:
                        if is_image_file(f):
                            files.append(os.path.relpath(os.path.join(root, f), folder))
                return files
            else:
                return [f for f in os.listdir(folder) if is_image_file(f)]

        images1 = set(gather_images(folder1))
        images2 = set(gather_images(folder2))
        common = sorted(images1 & images2)
        if not common:
            print_warning("No matching image filenames found in both folders.")
            return
        print_info(f"Found {len(common)} matching image(s) to align.")
        processed, failed = 0, 0
        with memory_context("Align Images"), tqdm(
            common, desc="Aligning", unit="img"
        ) as bar:
            for rel_path in bar:
                src1 = os.path.join(folder1, rel_path)
                src2 = os.path.join(folder2, rel_path)
                out_path = os.path.join(output_folder, rel_path)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                if dry_run:
                    print_info(f"[DRY RUN] Would align: {rel_path}")
                    continue
                try:
                    img1 = cv2.imread(src1, cv2.IMREAD_UNCHANGED)
                    img2 = cv2.imread(src2, cv2.IMREAD_UNCHANGED)
                    if img1 is None or img2 is None:
                        print_warning(f"Could not read one or both images: {rel_path}")
                        failed += 1
                        continue
                    aligned = align_image(img1, img2)
                    if aligned is None:
                        print_warning(f"Alignment failed: {rel_path}")
                        failed += 1
                        continue
                    cv2.imwrite(out_path, aligned)
                    processed += 1
                except Exception as e:
                    print_error(f"Error processing {rel_path}: {e}")
                    log_operation("align_images", f"Failed: {rel_path}: {e}")
                    failed += 1
        print_success(
            f"\nAlignment complete. {processed} images aligned, {failed} failed."
        )
        log_operation(
            "align_images",
            f"Aligned {processed}, failed {failed}, from {folder1} to {output_folder}",
        )
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        log_operation("align_images", f"Unexpected error: {e}")
    finally:
        clear_memory()


def align_image(image1: np.ndarray, image2: np.ndarray) -> Optional[np.ndarray]:
    """
    Align image1 to image2 using SIFT keypoints and FLANN-based matching.
    Returns the aligned image or None if alignment fails.

    Args:
        image1: Source image to align
        image2: Reference image

    Returns:
        Aligned image as np.ndarray, or None if failed
    """
    try:
        size = (image1.shape[1], image1.shape[0])
        image2 = cv2.resize(image2, size)
        image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        sift = cv2.SIFT_create()
        keypoints1, descriptors1 = sift.detectAndCompute(image1_gray, None)
        keypoints2, descriptors2 = sift.detectAndCompute(image2_gray, None)
        if descriptors1 is None or descriptors2 is None:
            return None
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = [m[0] for m in flann.knnMatch(descriptors1, descriptors2, k=2)]
        if len(matches) < 4:
            return None
        matches = sorted(matches, key=lambda x: x.distance)
        n = min(20, len(matches))  # TODO: Expose as advanced option
        src_points = np.float32(
            [keypoints1[m.queryIdx].pt for m in matches[:n]]
        ).reshape(-1, 1, 2)
        dst_points = np.float32(
            [keypoints2[m.trainIdx].pt for m in matches[:n]]
        ).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)
        if M is None:
            return None
        h, w = image1.shape[:2]
        aligned_image = cv2.warpPerspective(image1, M, (w, h))
        return aligned_image
    except Exception:
        return None
