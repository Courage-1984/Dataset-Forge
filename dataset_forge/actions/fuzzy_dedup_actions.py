"""
fuzzy_dedup_actions.py - Fuzzy Matching De-duplication Actions for Dataset Forge

Provides:
- Fuzzy matching duplicate detection using multiple perceptual hashing algorithms
- Configurable similarity thresholds for different hash methods
- Support for single folder and HQ/LQ paired folders
- Multiple operation modes: copy, move, delete
- Comprehensive analysis and reporting tools
"""

import os
import shutil
import hashlib
from typing import Dict, List, Tuple, Optional, Any, Set
from pathlib import Path
from collections import defaultdict
import imagehash
from PIL import Image
import numpy as np

from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.progress_utils import smart_map
from dataset_forge.utils.file_utils import get_image_files


def fuzzy_matching_workflow(
    folder: Optional[str] = None,
    hq_folder: Optional[str] = None,
    lq_folder: Optional[str] = None,
    hash_methods: List[str] = None,
    thresholds: Dict[str, int] = None,
    operation: str = "show",
    destination_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main fuzzy matching workflow for duplicate detection.
    
    Args:
        folder: Single folder path (if using single folder mode)
        hq_folder: HQ folder path (if using HQ/LQ mode)
        lq_folder: LQ folder path (if using HQ/LQ mode)
        hash_methods: List of hash methods to use
        thresholds: Dictionary of thresholds for each method
        operation: Operation to perform ('copy', 'move', 'delete', 'show')
        destination_dir: Destination directory for copy/move operations
        
    Returns:
        Dictionary with results and statistics
    """
    try:
        # Initialize parameters
        if hash_methods is None:
            hash_methods = ["phash", "dhash", "ahash", "whash", "colorhash"]
        if thresholds is None:
            thresholds = {
                "phash": 90,
                "dhash": 85,
                "ahash": 80,
                "whash": 85,
                "colorhash": 75
            }
        
        # Get image files
        if folder:
            # Single folder mode
            image_files = get_image_files(folder)
            print_info(f"Found {len(image_files)} images in {folder}")
        elif hq_folder and lq_folder:
            # HQ/LQ mode
            hq_files = get_image_files(hq_folder)
            lq_files = get_image_files(lq_folder)
            image_files = hq_files + lq_files
            print_info(f"Found {len(hq_files)} HQ and {len(lq_files)} LQ images")
        else:
            print_error("Invalid folder configuration")
            return None
        
        if not image_files:
            print_warning("No image files found")
            return {"duplicate_groups": [], "total_files_processed": 0, "total_duplicates_found": 0}
        
        # Compute hashes for all images
        print_info("Computing perceptual hashes...")
        hash_results = compute_multiple_hashes(image_files, hash_methods)
        
        # Find fuzzy duplicates
        print_info("Finding fuzzy duplicates...")
        duplicate_groups = find_fuzzy_duplicates(hash_results, thresholds)
        
        # Process results
        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        
        results = {
            "duplicate_groups": duplicate_groups,
            "total_files_processed": len(image_files),
            "total_duplicates_found": total_duplicates,
            "hash_methods_used": hash_methods,
            "thresholds_used": thresholds
        }
        
        # Perform operation if not just showing
        if operation != "show" and duplicate_groups:
            if operation in ["copy", "move"]:
                results["operation_results"] = perform_copy_move_operation(
                    duplicate_groups, destination_dir, operation
                )
            elif operation == "delete":
                results["operation_results"] = perform_delete_operation(duplicate_groups)
        
        return results
        
    except Exception as e:
        print_error(f"Error in fuzzy matching workflow: {e}")
        return None
    finally:
        clear_memory()
        clear_cuda_cache()


def compute_multiple_hashes(
    image_files: List[str], 
    hash_methods: List[str]
) -> Dict[str, Dict[str, Any]]:
    """
    Compute multiple types of perceptual hashes for all images.
    
    Args:
        image_files: List of image file paths
        hash_methods: List of hash methods to use
        
    Returns:
        Dictionary mapping file paths to their hash results
    """
    hash_results = {}
    
    def compute_hashes_for_file(file_path: str) -> Dict[str, Any]:
        """Compute hashes for a single file."""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                file_hashes = {}
                
                for method in hash_methods:
                    try:
                        if method == "phash":
                            file_hashes[method] = imagehash.phash(img)
                        elif method == "dhash":
                            file_hashes[method] = imagehash.dhash(img)
                        elif method == "ahash":
                            file_hashes[method] = imagehash.average_hash(img)
                        elif method == "whash":
                            file_hashes[method] = imagehash.whash(img)
                        elif method == "colorhash":
                            file_hashes[method] = imagehash.colorhash(img)
                    except Exception as e:
                        print_warning(f"Failed to compute {method} hash for {file_path}: {e}")
                        file_hashes[method] = None
                
                return {
                    "path": file_path,
                    "hashes": file_hashes,
                    "size": os.path.getsize(file_path)
                }
                
        except Exception as e:
            print_warning(f"Failed to process {file_path}: {e}")
            return None
    
    # Process files with progress tracking
    results = smart_map(
        compute_hashes_for_file,
        image_files,
        desc="Computing hashes",
        max_workers=4
    )
    
    # Filter out None results and create hash_results
    for result in results:
        if result is not None:
            hash_results[result["path"]] = result
    
    return hash_results


def find_fuzzy_duplicates(
    hash_results: Dict[str, Dict[str, Any]], 
    thresholds: Dict[str, int]
) -> List[List[Dict[str, Any]]]:
    """
    Find fuzzy duplicates using multiple hash methods and thresholds.
    
    Args:
        hash_results: Dictionary of hash results for all images
        thresholds: Dictionary of similarity thresholds for each method
        
    Returns:
        List of duplicate groups
    """
    duplicate_groups = []
    processed_files = set()
    
    # Convert thresholds from percentage to hash distance
    # For 64-bit hashes, max distance is 64
    # We convert percentage similarity to distance: distance = 64 * (1 - similarity/100)
    hash_distances = {}
    for method, threshold in thresholds.items():
        similarity = threshold / 100.0
        distance = int(64 * (1 - similarity))
        hash_distances[method] = distance
    
    # Group files by hash methods
    for file_path, file_data in hash_results.items():
        if file_path in processed_files:
            continue
        
        # Find similar files for this file
        similar_files = [file_data]
        
        for other_path, other_data in hash_results.items():
            if other_path == file_path or other_path in processed_files:
                continue
            
            # Check similarity across all hash methods
            is_similar = False
            best_similarity = 0
            best_method = None
            
            for method in file_data["hashes"].keys():
                if method not in other_data["hashes"]:
                    continue
                
                hash1 = file_data["hashes"][method]
                hash2 = other_data["hashes"][method]
                
                if hash1 is None or hash2 is None:
                    continue
                
                # Calculate hamming distance
                distance = hash1 - hash2
                max_distance = hash_distances.get(method, 10)  # Default threshold
                
                if distance <= max_distance:
                    is_similar = True
                    # Calculate similarity percentage
                    similarity = (1 - distance / 64) * 100
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_method = method
            
            if is_similar:
                similar_files.append({
                    **other_data,
                    "similarity": best_similarity,
                    "method": best_method
                })
        
        # If we found similar files, create a group
        if len(similar_files) > 1:
            duplicate_groups.append(similar_files)
            # Mark all files in this group as processed
            for file_data in similar_files:
                processed_files.add(file_data["path"])
    
    return duplicate_groups


def perform_copy_move_operation(
    duplicate_groups: List[List[Dict[str, Any]]], 
    destination_dir: str, 
    operation: str
) -> Dict[str, Any]:
    """
    Perform copy or move operation on duplicate files.
    
    Args:
        duplicate_groups: List of duplicate groups
        destination_dir: Destination directory
        operation: 'copy' or 'move'
        
    Returns:
        Dictionary with operation results
    """
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    
    moved_files = []
    errors = []
    
    for group_idx, group in enumerate(duplicate_groups, 1):
        # Create subdirectory for this group
        group_dir = os.path.join(destination_dir, f"duplicate_group_{group_idx}")
        os.makedirs(group_dir, exist_ok=True)
        
        # Keep the first file, operate on the rest
        for file_data in group[1:]:  # Skip first file (keep original)
            file_path = file_data["path"]
            filename = os.path.basename(file_path)
            
            # Create unique filename if needed
            dest_path = os.path.join(group_dir, filename)
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(group_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            try:
                if operation == "copy":
                    shutil.copy2(file_path, dest_path)
                else:  # move
                    shutil.move(file_path, dest_path)
                
                moved_files.append({
                    "source": file_path,
                    "destination": dest_path,
                    "operation": operation
                })
                
            except Exception as e:
                errors.append({
                    "file": file_path,
                    "error": str(e)
                })
    
    return {
        "moved_files": moved_files,
        "errors": errors,
        "total_processed": len(moved_files)
    }


def perform_delete_operation(
    duplicate_groups: List[List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Perform delete operation on duplicate files.
    
    Args:
        duplicate_groups: List of duplicate groups
        
    Returns:
        Dictionary with operation results
    """
    deleted_files = []
    errors = []
    
    for group in duplicate_groups:
        # Keep the first file, delete the rest
        for file_data in group[1:]:  # Skip first file (keep original)
            file_path = file_data["path"]
            
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                
            except Exception as e:
                errors.append({
                    "file": file_path,
                    "error": str(e)
                })
    
    return {
        "deleted_files": deleted_files,
        "errors": errors,
        "total_deleted": len(deleted_files)
    }


def duplicate_analysis_workflow(
    folder: str,
    analysis_type: str = "4"
) -> Dict[str, Any]:
    """
    Comprehensive duplicate analysis workflow.
    
    Args:
        folder: Folder to analyze
        analysis_type: Type of analysis to perform
        
    Returns:
        Dictionary with analysis results
    """
    try:
        image_files = get_image_files(folder)
        if not image_files:
            return {"total_files": 0, "potential_duplicates": 0}
        
        results = {
            "total_files": len(image_files),
            "potential_duplicates": 0,
            "space_savings": "0 bytes",
            "breakdown": {}
        }
        
        if analysis_type in ["1", "4"]:  # File size analysis
            size_results = analyze_file_sizes(image_files)
            results["breakdown"]["size_duplicates"] = size_results["duplicates"]
            results["potential_duplicates"] += size_results["duplicates"]
        
        if analysis_type in ["2", "4"]:  # Hash-based analysis
            hash_results = analyze_hash_duplicates(image_files)
            results["breakdown"]["hash_duplicates"] = hash_results["duplicates"]
            results["potential_duplicates"] += hash_results["duplicates"]
        
        if analysis_type in ["3", "4"]:  # Visual similarity analysis
            visual_results = analyze_visual_similarity(image_files)
            results["breakdown"]["visual_duplicates"] = visual_results["duplicates"]
            results["potential_duplicates"] += visual_results["duplicates"]
        
        # Calculate space savings
        total_size = sum(os.path.getsize(f) for f in image_files)
        if results["potential_duplicates"] > 0:
            # Estimate 50% of duplicates could be removed
            estimated_savings = total_size * 0.5 * (results["potential_duplicates"] / len(image_files))
            results["space_savings"] = format_bytes(estimated_savings)
        
        return results
        
    except Exception as e:
        print_error(f"Error in duplicate analysis: {e}")
        return None


def analyze_file_sizes(image_files: List[str]) -> Dict[str, Any]:
    """Analyze files for size-based duplicates."""
    size_groups = defaultdict(list)
    
    for file_path in image_files:
        try:
            size = os.path.getsize(file_path)
            size_groups[size].append(file_path)
        except Exception:
            continue
    
    duplicates = sum(len(files) - 1 for files in size_groups.values() if len(files) > 1)
    
    return {"duplicates": duplicates}


def analyze_hash_duplicates(image_files: List[str]) -> Dict[str, Any]:
    """Analyze files for hash-based duplicates."""
    hash_groups = defaultdict(list)
    
    def compute_hash(file_path: str) -> Tuple[str, str]:
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_path, file_hash
        except Exception:
            return file_path, None
    
    # Compute hashes
    hash_results = smart_map(
        compute_hash,
        image_files,
        desc="Computing file hashes",
        max_workers=4
    )
    
    # Group by hash
    for file_path, file_hash in hash_results:
        if file_hash:
            hash_groups[file_hash].append(file_path)
    
    duplicates = sum(len(files) - 1 for files in hash_groups.values() if len(files) > 1)
    
    return {"duplicates": duplicates}


def analyze_visual_similarity(image_files: List[str]) -> Dict[str, Any]:
    """Analyze files for visual similarity using perceptual hashing."""
    try:
        # Use a simple approach with pHash for quick analysis
        hash_results = compute_multiple_hashes(image_files, ["phash"])
        
        # Group by similar hashes (threshold of 5 bits difference)
        similar_groups = []
        processed = set()
        
        for file_path, file_data in hash_results.items():
            if file_path in processed:
                continue
            
            similar_files = [file_data]
            
            for other_path, other_data in hash_results.items():
                if other_path == file_path or other_path in processed:
                    continue
                
                hash1 = file_data["hashes"]["phash"]
                hash2 = other_data["hashes"]["phash"]
                
                if hash1 and hash2 and (hash1 - hash2) <= 5:
                    similar_files.append(other_data)
            
            if len(similar_files) > 1:
                similar_groups.append(similar_files)
                for file_data in similar_files:
                    processed.add(file_data["path"])
        
        duplicates = sum(len(group) - 1 for group in similar_groups)
        return {"duplicates": duplicates}
        
    except Exception as e:
        print_warning(f"Error in visual similarity analysis: {e}")
        return {"duplicates": 0}


def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"
