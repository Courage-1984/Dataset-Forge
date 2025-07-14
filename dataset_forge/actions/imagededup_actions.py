import os
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
from dataset_forge.utils.progress_utils import tqdm

try:
    from imagededup.methods import PHash, DHash, AHash, WHash
    from imagededup.utils import plot_duplicates

    IMAGEDEDUP_AVAILABLE = True
except ImportError:
    IMAGEDEDUP_AVAILABLE = False

from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.history_log import log_operation


class ImageDedupHandler:
    """Handler for imagededup library operations."""

    def __init__(self, hash_method: str = "phash"):
        """
        Initialize the deduplication handler.

        Args:
            hash_method: One of 'phash', 'dhash', 'ahash', 'whash'
        """
        if not IMAGEDEDUP_AVAILABLE:
            raise ImportError(
                "imagededup library is not available. Please install it with: pip install imagededup"
            )

        self.hash_methods = {
            "phash": PHash,
            "dhash": DHash,
            "ahash": AHash,
            "whash": WHash,
        }

        if hash_method not in self.hash_methods:
            raise ValueError(
                f"Invalid hash method: {hash_method}. Must be one of {list(self.hash_methods.keys())}"
            )

        self.hash_method = hash_method
        self.hasher = self.hash_methods[hash_method]()

    def find_duplicates(
        self,
        image_dir: str,
        max_distance_threshold: int = 10,
        scores: bool = False,
        outfile: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """
        Find duplicate images in a directory.

        Args:
            image_dir: Directory containing images
            max_distance_threshold: Maximum distance for considering images as duplicates
            scores: Whether to return similarity scores
            outfile: Optional file to save results

        Returns:
            Dictionary mapping image paths to lists of duplicate paths
        """
        print_info(f"Finding duplicates using {self.hash_method.upper()}...")

        # Find duplicates
        duplicates = self.hasher.find_duplicates(
            image_dir=image_dir,
            max_distance_threshold=max_distance_threshold,
            scores=scores,
        )

        if outfile:
            # Save results to file
            if scores:
                # Convert to DataFrame for easier handling
                results = []
                for img_path, duplicates_list in duplicates.items():
                    for dup_path, score in duplicates_list:
                        results.append(
                            {
                                "original": img_path,
                                "duplicate": dup_path,
                                "similarity_score": score,
                            }
                        )
                df = pd.DataFrame(results)
                df.to_csv(outfile, index=False)
                print_success(f"Results saved to {outfile}")
            else:
                # Save as simple list
                with open(outfile, "w") as f:
                    for img_path, duplicates_list in duplicates.items():
                        f.write(f"Original: {img_path}\n")
                        for dup_path in duplicates_list:
                            f.write(f"  Duplicate: {dup_path}\n")
                        f.write("\n")
                print_success(f"Results saved to {outfile}")

        return duplicates

    def debug_directory_contents(self, image_dir: str) -> None:
        """
        Debug method to check what files are actually in the directory vs what imagededup finds.

        Args:
            image_dir: Directory to check
        """
        print_info(f"Debugging directory contents: {image_dir}")

        # Get actual files in directory
        actual_files = set()
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
                    rel_path = os.path.relpath(os.path.join(root, file), image_dir)
                    actual_files.add(rel_path)

        print_info(f"Actual files in directory: {len(actual_files)}")

        # Get files that imagededup finds
        duplicates = self.find_duplicates(image_dir, max_distance_threshold=10)
        imagededup_files = set()
        for original, duplicate_list in duplicates.items():
            imagededup_files.add(original)
            imagededup_files.update(duplicate_list)

        print_info(f"Files found by imagededup: {len(imagededup_files)}")

        # Find missing files
        missing_files = imagededup_files - actual_files
        if missing_files:
            print_warning(
                f"Files found by imagededup but not in directory: {len(missing_files)}"
            )
            for file in list(missing_files)[:10]:  # Show first 10
                print_warning(f"  Missing: {file}")
            if len(missing_files) > 10:
                print_warning(f"  ... and {len(missing_files) - 10} more")

    def find_duplicates_to_remove(
        self, image_dir: str, max_distance_threshold: int = 10
    ) -> List[str]:
        """
        Find duplicate images and return list of files to remove.

        Args:
            image_dir: Directory containing images
            max_distance_threshold: Maximum distance for considering images as duplicates

        Returns:
            List of file paths to remove
        """
        duplicates = self.find_duplicates(image_dir, max_distance_threshold)

        files_to_remove = []
        for original, duplicate_list in duplicates.items():
            # Convert relative paths to absolute paths and verify files exist
            for dup_path in duplicate_list:
                abs_path = os.path.join(image_dir, dup_path)
                if os.path.exists(abs_path):
                    files_to_remove.append(abs_path)
                else:
                    print_warning(f"Duplicate file not found in directory: {abs_path}")

        return files_to_remove

    def remove_duplicates(
        self, image_dir: str, max_distance_threshold: int = 10, dry_run: bool = True
    ) -> List[str]:
        """
        Remove duplicate images from directory.

        Args:
            image_dir: Directory containing images
            max_distance_threshold: Maximum distance for considering images as duplicates
            dry_run: If True, only show what would be removed without actually removing

        Returns:
            List of removed file paths
        """
        files_to_remove = self.find_duplicates_to_remove(
            image_dir, max_distance_threshold
        )

        if not files_to_remove:
            print_info("No duplicates found.")
            return []

        print_info(f"Found {len(files_to_remove)} duplicate files to remove.")

        if dry_run:
            print_warning(
                "DRY RUN - No files will be removed. Set dry_run=False to actually remove files."
            )
            for file_path in files_to_remove:
                print_info(f"Would remove: {file_path}")
        else:
            removed_files = []
            for file_path in tqdm(files_to_remove, desc="Removing duplicates"):
                try:
                    # Check if file exists before trying to remove it
                    if not os.path.exists(file_path):
                        print_warning(
                            f"File not found (may have been removed already): {file_path}"
                        )
                        continue

                    os.remove(file_path)
                    removed_files.append(file_path)
                except Exception as e:
                    print_error(f"Error removing {file_path}: {e}")

            print_success(f"Removed {len(removed_files)} duplicate files.")
            if len(removed_files) < len(files_to_remove):
                print_info(
                    f"Note: {len(files_to_remove) - len(removed_files)} files were not removed (may have been removed already or don't exist)"
                )
            return removed_files

        return files_to_remove

    def move_duplicates(
        self,
        image_dir: str,
        destination_dir: str,
        max_distance_threshold: int = 10,
        dry_run: bool = True,
    ) -> List[str]:
        """
        Move duplicate images to a separate directory.

        Args:
            image_dir: Directory containing images
            destination_dir: Directory to move duplicates to
            max_distance_threshold: Maximum distance for considering images as duplicates
            dry_run: If True, only show what would be moved without actually moving

        Returns:
            List of moved file paths
        """
        files_to_move = self.find_duplicates_to_remove(
            image_dir, max_distance_threshold
        )

        if not files_to_move:
            print_info("No duplicates found.")
            return []

        print_info(f"Found {len(files_to_move)} duplicate files to move.")

        if dry_run:
            print_warning(
                "DRY RUN - No files will be moved. Set dry_run=False to actually move files."
            )
            for file_path in files_to_move:
                print_info(f"Would move: {file_path} -> {destination_dir}")
        else:
            # Create destination directory if it doesn't exist
            os.makedirs(destination_dir, exist_ok=True)

            moved_files = []
            for file_path in tqdm(files_to_move, desc="Moving duplicates"):
                try:
                    # Check if file exists before trying to move it
                    if not os.path.exists(file_path):
                        print_warning(
                            f"File not found (may have been moved already): {file_path}"
                        )
                        continue

                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(destination_dir, filename)

                    # Handle filename conflicts
                    counter = 1
                    while os.path.exists(dest_path):
                        name, ext = os.path.splitext(filename)
                        dest_path = os.path.join(
                            destination_dir, f"{name}_{counter}{ext}"
                        )
                        counter += 1

                    shutil.move(file_path, dest_path)
                    moved_files.append(file_path)
                except Exception as e:
                    print_error(f"Error moving {file_path}: {e}")

            print_success(
                f"Moved {len(moved_files)} duplicate files to {destination_dir}."
            )
            if len(moved_files) < len(files_to_move):
                print_info(
                    f"Note: {len(files_to_move) - len(moved_files)} files were not moved (may have been moved already or don't exist)"
                )
            return moved_files

        return files_to_move

    def generate_duplicate_report(
        self,
        image_dir: str,
        output_dir: str,
        max_distance_threshold: int = 10,
        sample_size: int = 10,
    ) -> str:
        """
        Generate a visual report of duplicates.

        Args:
            image_dir: Directory containing images
            output_dir: Directory to save the report
            max_distance_threshold: Maximum distance for considering images as duplicates
            sample_size: Number of duplicate groups to include in the report

        Returns:
            Path to the generated report
        """
        duplicates = self.find_duplicates(image_dir, max_distance_threshold)

        if not duplicates:
            print_info("No duplicates found for report.")
            return ""

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate report for first few duplicate groups
        duplicate_groups = list(duplicates.items())[:sample_size]

        for i, (original, duplicate_list) in enumerate(duplicate_groups):
            if not duplicate_list:
                continue

            # Create a list of all images in this group (original + duplicates)
            all_images = [original] + duplicate_list

            # Generate plot
            plot_filename = f"duplicate_group_{i+1}.png"
            plot_path = os.path.join(output_dir, plot_filename)

            try:
                plot_duplicates(
                    image_dir=image_dir,
                    duplicate_map={original: duplicate_list},
                    filename=plot_filename,
                    out_dir=output_dir,
                )
                print_info(f"Generated plot: {plot_path}")
            except Exception as e:
                print_error(f"Error generating plot for group {i+1}: {e}")

        # Generate summary report
        summary_path = os.path.join(output_dir, "duplicate_summary.txt")
        with open(summary_path, "w") as f:
            f.write(f"Duplicate Detection Report\n")
            f.write(f"========================\n\n")
            f.write(f"Directory: {image_dir}\n")
            f.write(f"Hash method: {self.hash_method.upper()}\n")
            f.write(f"Max distance threshold: {max_distance_threshold}\n")
            f.write(f"Total duplicate groups: {len(duplicates)}\n")
            f.write(
                f"Total duplicate files: {sum(len(dups) for dups in duplicates.values())}\n\n"
            )

            for i, (original, duplicate_list) in enumerate(duplicates.items()):
                f.write(f"Group {i+1}:\n")
                f.write(f"  Original: {original}\n")
                f.write(f"  Duplicates ({len(duplicate_list)}):\n")
                for dup in duplicate_list:
                    f.write(f"    - {dup}\n")
                f.write("\n")

        print_success(f"Duplicate report generated in: {output_dir}")
        return output_dir


def imagededup_workflow(
    image_dir: str,
    operation: str = "find",
    hash_method: str = "phash",
    max_distance_threshold: int = 10,
    destination_dir: Optional[str] = None,
    output_file: Optional[str] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Main workflow for imagededup operations.

    Args:
        image_dir: Directory containing images
        operation: One of 'find', 'remove', 'move', 'report'
        hash_method: Hash method to use
        max_distance_threshold: Maximum distance for duplicates
        destination_dir: Directory for moving duplicates (for 'move' operation)
        output_file: File to save results (for 'find' operation)
        dry_run: Whether to perform actual operations or just show what would be done

    Returns:
        Dictionary with operation results
    """
    if not IMAGEDEDUP_AVAILABLE:
        raise ImportError(
            "imagededup library is not available. Please install it with: pip install imagededup"
        )

    try:
        handler = ImageDedupHandler(hash_method)

        if operation == "find":
            duplicates = handler.find_duplicates(
                image_dir, max_distance_threshold, scores=True, outfile=output_file
            )
            return {"operation": "find", "duplicates": duplicates}

        elif operation == "remove":
            removed_files = handler.remove_duplicates(
                image_dir, max_distance_threshold, dry_run=dry_run
            )
            return {"operation": "remove", "removed_files": removed_files}

        elif operation == "move":
            if not destination_dir:
                raise ValueError("destination_dir is required for 'move' operation")
            moved_files = handler.move_duplicates(
                image_dir, destination_dir, max_distance_threshold, dry_run=dry_run
            )
            return {"operation": "move", "moved_files": moved_files}

        elif operation == "report":
            if not destination_dir:
                destination_dir = os.path.join(image_dir, "duplicate_report")
            report_path = handler.generate_duplicate_report(
                image_dir, destination_dir, max_distance_threshold
            )
            return {"operation": "report", "report_path": report_path}

        else:
            raise ValueError(
                f"Invalid operation: {operation}. Must be one of 'find', 'remove', 'move', 'report'"
            )

    except Exception as e:
        print_error(f"Error in imagededup workflow: {e}")
        raise


def imagededup_hq_lq_workflow(
    hq_dir: str,
    lq_dir: str,
    operation: str = "find",
    hash_method: str = "phash",
    max_distance_threshold: int = 10,
    destination_dir: Optional[str] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Workflow for handling HQ/LQ paired datasets with imagededup.

    Args:
        hq_dir: High-quality images directory
        lq_dir: Low-quality images directory
        operation: One of 'find', 'remove', 'move'
        hash_method: Hash method to use
        max_distance_threshold: Maximum distance for duplicates
        destination_dir: Base directory for moving duplicates
        dry_run: Whether to perform actual operations

    Returns:
        Dictionary with operation results
    """
    if not IMAGEDEDUP_AVAILABLE:
        raise ImportError(
            "imagededup library is not available. Please install it with: pip install imagededup"
        )

    try:
        handler = ImageDedupHandler(hash_method)

        # Find duplicates in HQ directory
        hq_duplicates = handler.find_duplicates(hq_dir, max_distance_threshold)

        if not hq_duplicates:
            print_info("No duplicates found in HQ directory.")
            return {"operation": operation, "hq_duplicates": {}, "lq_duplicates": {}}

        # Find corresponding LQ duplicates
        lq_duplicates = {}
        for hq_original, hq_dups in hq_duplicates.items():
            lq_dups = []
            for hq_dup in hq_dups:
                # Find corresponding LQ file
                hq_filename = os.path.basename(hq_dup)
                lq_path = os.path.join(lq_dir, hq_filename)
                if os.path.exists(lq_path):
                    lq_dups.append(lq_path)

            if lq_dups:
                lq_duplicates[os.path.join(lq_dir, os.path.basename(hq_original))] = (
                    lq_dups
                )

        if operation == "find":
            return {
                "operation": "find",
                "hq_duplicates": hq_duplicates,
                "lq_duplicates": lq_duplicates,
            }

        elif operation == "remove":
            if dry_run:
                print_warning("DRY RUN - No files will be removed.")
                for hq_original, hq_dups in hq_duplicates.items():
                    print_info(f"Would remove HQ duplicates for: {hq_original}")
                    for hq_dup in hq_dups:
                        # Convert relative path to absolute path
                        hq_abs_path = os.path.join(hq_dir, hq_dup)
                        print_info(f"  HQ: {hq_abs_path}")
                        lq_dup = os.path.join(lq_dir, os.path.basename(hq_dup))
                        if os.path.exists(lq_dup):
                            print_info(f"  LQ: {lq_dup}")
            else:
                removed_hq = []
                removed_lq = []

                for hq_original, hq_dups in hq_duplicates.items():
                    for hq_dup in hq_dups:
                        try:
                            # Convert relative path to absolute path
                            hq_abs_path = os.path.join(hq_dir, hq_dup)
                            os.remove(hq_abs_path)
                            removed_hq.append(hq_abs_path)

                            # Remove corresponding LQ file
                            lq_dup = os.path.join(lq_dir, os.path.basename(hq_dup))
                            if os.path.exists(lq_dup):
                                os.remove(lq_dup)
                                removed_lq.append(lq_dup)
                        except Exception as e:
                            print_error(f"Error removing {hq_dup}: {e}")

                print_success(
                    f"Removed {len(removed_hq)} HQ and {len(removed_lq)} LQ duplicate files."
                )
                return {
                    "operation": "remove",
                    "removed_hq": removed_hq,
                    "removed_lq": removed_lq,
                }

        elif operation == "move":
            if not destination_dir:
                raise ValueError("destination_dir is required for 'move' operation")

            hq_dest = os.path.join(destination_dir, "hq_duplicates")
            lq_dest = os.path.join(destination_dir, "lq_duplicates")

            if dry_run:
                print_warning("DRY RUN - No files will be moved.")
                for hq_original, hq_dups in hq_duplicates.items():
                    print_info(f"Would move duplicates for: {hq_original}")
                    for hq_dup in hq_dups:
                        # Convert relative path to absolute path
                        hq_abs_path = os.path.join(hq_dir, hq_dup)
                        print_info(f"  HQ: {hq_abs_path} -> {hq_dest}")
                        lq_dup = os.path.join(lq_dir, os.path.basename(hq_dup))
                        if os.path.exists(lq_dup):
                            print_info(f"  LQ: {lq_dup} -> {lq_dest}")
            else:
                os.makedirs(hq_dest, exist_ok=True)
                os.makedirs(lq_dest, exist_ok=True)

                moved_hq = []
                moved_lq = []

                for hq_original, hq_dups in hq_duplicates.items():
                    for hq_dup in hq_dups:
                        try:
                            # Convert relative path to absolute path
                            hq_abs_path = os.path.join(hq_dir, hq_dup)
                            filename = os.path.basename(hq_dup)
                            dest_path = os.path.join(hq_dest, filename)

                            # Handle filename conflicts
                            counter = 1
                            while os.path.exists(dest_path):
                                name, ext = os.path.splitext(filename)
                                dest_path = os.path.join(
                                    hq_dest, f"{name}_{counter}{ext}"
                                )
                                counter += 1

                            shutil.move(hq_abs_path, dest_path)
                            moved_hq.append(hq_abs_path)

                            # Move corresponding LQ file
                            lq_dup = os.path.join(lq_dir, os.path.basename(hq_dup))
                            if os.path.exists(lq_dup):
                                lq_dest_path = os.path.join(
                                    lq_dest, os.path.basename(lq_dup)
                                )

                                # Handle filename conflicts for LQ
                                counter = 1
                                while os.path.exists(lq_dest_path):
                                    name, ext = os.path.splitext(
                                        os.path.basename(lq_dup)
                                    )
                                    lq_dest_path = os.path.join(
                                        lq_dest, f"{name}_{counter}{ext}"
                                    )
                                    counter += 1

                                shutil.move(lq_dup, lq_dest_path)
                                moved_lq.append(lq_dup)
                        except Exception as e:
                            print_error(f"Error moving {hq_dup}: {e}")

                print_success(
                    f"Moved {len(moved_hq)} HQ and {len(moved_lq)} LQ duplicate files."
                )
                return {"operation": "move", "moved_hq": moved_hq, "moved_lq": moved_lq}

        else:
            raise ValueError(
                f"Invalid operation: {operation}. Must be one of 'find', 'remove', 'move'"
            )

    except Exception as e:
        print_error(f"Error in imagededup HQ/LQ workflow: {e}")
        raise
