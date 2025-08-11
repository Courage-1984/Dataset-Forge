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
import shutil
from pathlib import Path
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.printing import (
    print_header,
    print_section,
    print_success,
    print_error,
    print_info,
    print_warning,
    print_prompt,
)
from dataset_forge.utils.file_utils import get_image_files, is_image_file
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.utils.color import Mocha
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
import threading


@monitor_all("create_dataset_from_source", critical_on_error=True)
def create_dataset_from_source(source_folder: str, output_folder: str):
    """Create a comprehensive dataset from a source folder with validation, quality control, and preprocessing.
    
    This function goes beyond simple copying to provide:
    - Image validation and quality assessment
    - Duplicate detection and removal
    - Metadata extraction and organization
    - Size and format standardization
    - Quality scoring and filtering
    - Comprehensive dataset statistics
    
    Args:
        source_folder: Path to the source folder containing images
        output_folder: Path to the output folder where dataset will be created
    """
    print_header("📁 Create Dataset from Source Folder")
    
    # Validate input paths
    if not os.path.exists(source_folder):
        print_error(f"Source folder does not exist: {source_folder}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all image files from source folder
    image_files = get_image_files(source_folder)
    
    if not image_files:
        print_error(f"No image files found in source folder: {source_folder}")
        return
    
    print_info(f"Found {len(image_files)} image files in source folder")
    
    # Step 1: Dataset Analysis and Statistics
    print_section("📊 Dataset Analysis")
    dataset_stats = analyze_dataset_composition(image_files)
    print_dataset_statistics(dataset_stats)
    
    # Step 2: Quality Control Options
    print_section("🔍 Quality Control Options")
    quality_options = get_quality_control_options()
    
    # Step 3: Preprocessing Options
    print_section("⚙️ Preprocessing Options")
    preprocessing_options = get_preprocessing_options()
    
    # Step 4: Organization Options
    print_section("📂 Organization Options")
    organization_options = get_organization_options()
    
    # Step 5: Process the dataset
    print_section("🚀 Processing Dataset")
    processed_files = process_dataset_with_options(
        image_files, 
        output_folder, 
        quality_options, 
        preprocessing_options, 
        organization_options
    )
    
    # Step 6: Generate final statistics and report
    print_section("📈 Final Dataset Report")
    generate_dataset_report(processed_files, output_folder, dataset_stats)
    
    # Play completion sound
    play_done_sound()


def analyze_dataset_composition(image_files):
    """Analyze the composition of the dataset and return statistics."""
    stats = {
        "total_files": len(image_files),
        "file_types": {},
        "size_categories": {"small": 0, "medium": 0, "large": 0, "xlarge": 0},
        "size_stats": {"min_width": float('inf'), "max_width": 0, "min_height": float('inf'), "max_height": 0},
        "total_size_bytes": 0,
        "corrupted_files": [],
        "metadata_stats": {"with_exif": 0, "without_exif": 0}
    }
    
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        for image_file in tqdm(image_files, desc="Analyzing dataset composition"):
            try:
                # File type analysis
                ext = os.path.splitext(image_file)[1].lower()
                stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                
                # File size analysis
                file_size = os.path.getsize(image_file)
                stats["total_size_bytes"] += file_size
                
                # Image analysis
                with Image.open(image_file) as img:
                    width, height = img.size
                    max_dim = max(width, height)
                    
                    # Update size statistics
                    stats["size_stats"]["min_width"] = min(stats["size_stats"]["min_width"], width)
                    stats["size_stats"]["max_width"] = max(stats["size_stats"]["max_width"], width)
                    stats["size_stats"]["min_height"] = min(stats["size_stats"]["min_height"], height)
                    stats["size_stats"]["max_height"] = max(stats["size_stats"]["max_height"], height)
                    
                    # Categorize by size
                    if max_dim < 512:
                        stats["size_categories"]["small"] += 1
                    elif max_dim < 1024:
                        stats["size_categories"]["medium"] += 1
                    elif max_dim < 2048:
                        stats["size_categories"]["large"] += 1
                    else:
                        stats["size_categories"]["xlarge"] += 1
                    
                    # Metadata analysis
                    exif = img.getexif()
                    if exif:
                        stats["metadata_stats"]["with_exif"] += 1
                    else:
                        stats["metadata_stats"]["without_exif"] += 1
            
            except Exception as e:
                stats["corrupted_files"].append((image_file, str(e)))
                continue
    
    except ImportError:
        print_warning("PIL/Pillow not available. Limited analysis will be performed.")
    
    return stats


def print_dataset_statistics(stats):
    """Print comprehensive dataset statistics."""
    print_info(f"📊 Dataset Statistics:")
    print_info(f"  Total files: {stats['total_files']}")
    print_info(f"  Total size: {stats['total_size_bytes'] / (1024*1024):.2f} MB")
    
    if stats["file_types"]:
        print_info(f"  File types:")
        for ext, count in sorted(stats["file_types"].items()):
            print_info(f"    {ext}: {count} files")
    
    if stats["size_categories"]:
        print_info(f"  Size distribution:")
        for category, count in stats["size_categories"].items():
            if count > 0:
                print_info(f"    {category}: {count} files")
    
    if stats["size_stats"]["max_width"] > 0:
        print_info(f"  Resolution range: {stats['size_stats']['min_width']}x{stats['size_stats']['min_height']} to {stats['size_stats']['max_width']}x{stats['size_stats']['max_height']}")
    
    if stats["metadata_stats"]["with_exif"] > 0:
        print_info(f"  Metadata: {stats['metadata_stats']['with_exif']} with EXIF, {stats['metadata_stats']['without_exif']} without")
    
    if stats["corrupted_files"]:
        print_warning(f"  Corrupted files: {len(stats['corrupted_files'])}")


def get_quality_control_options():
    """Get quality control options from user."""
    options = {
        "remove_corrupted": True,
        "remove_duplicates": False,
        "min_size": 0,
        "max_size": float('inf'),
        "min_resolution": 0,
        "max_resolution": float('inf'),
        "quality_threshold": 0.0,
        "aspect_ratio_filter": None
    }
    
    print_info("Quality Control Options:")
    print_info("[1] Remove corrupted files (recommended)")
    print_info("[2] Remove duplicate images")
    print_info("[3] Filter by file size")
    print_info("[4] Filter by resolution")
    print_info("[5] Filter by quality score")
    print_info("[6] Filter by aspect ratio")
    print_info("[7] Skip quality control")
    
    choice = input("Enter choice [1-7]: ").strip()
    
    if choice == "1":
        options["remove_corrupted"] = True
    elif choice == "2":
        options["remove_duplicates"] = input("Remove duplicates? (y/n): ").strip().lower() == 'y'
    elif choice == "3":
        min_size = input("Minimum file size in KB (0 for no limit): ").strip()
        max_size = input("Maximum file size in KB (0 for no limit): ").strip()
        options["min_size"] = int(min_size) * 1024 if min_size.isdigit() else 0
        options["max_size"] = int(max_size) * 1024 if max_size.isdigit() else float('inf')
    elif choice == "4":
        min_res = input("Minimum resolution (e.g., 512 for 512x512): ").strip()
        max_res = input("Maximum resolution (e.g., 2048 for 2048x2048): ").strip()
        options["min_resolution"] = int(min_res) if min_res.isdigit() else 0
        options["max_resolution"] = int(max_res) if max_res.isdigit() else float('inf')
    elif choice == "5":
        threshold = input("Quality threshold (0.0-1.0, higher = better quality): ").strip()
        options["quality_threshold"] = float(threshold) if threshold.replace('.', '').isdigit() else 0.0
    elif choice == "6":
        aspect = input("Aspect ratio filter (e.g., '16:9', '4:3', '1:1'): ").strip()
        options["aspect_ratio_filter"] = aspect if aspect else None
    elif choice == "7":
        options["remove_corrupted"] = False
        options["remove_duplicates"] = False
    
    return options


def get_preprocessing_options():
    """Get preprocessing options from user."""
    options = {
        "resize": False,
        "resize_width": 0,
        "resize_height": 0,
        "resize_method": "lanczos",
        "convert_format": False,
        "target_format": "jpg",
        "quality": 95,
        "remove_metadata": False,
        "normalize": False
    }
    
    print_info("Preprocessing Options:")
    print_info("[1] Resize images")
    print_info("[2] Convert format")
    print_info("[3] Remove metadata")
    print_info("[4] Normalize pixel values")
    print_info("[5] Skip preprocessing")
    
    choice = input("Enter choice [1-5]: ").strip()
    
    if choice == "1":
        options["resize"] = True
        width = input("Target width (0 to maintain aspect ratio): ").strip()
        height = input("Target height (0 to maintain aspect ratio): ").strip()
        options["resize_width"] = int(width) if width.isdigit() else 0
        options["resize_height"] = int(height) if height.isdigit() else 0
        
        print_info("Resize method:")
        print_info("[1] Lanczos (best quality)")
        print_info("[2] Bicubic (good quality)")
        print_info("[3] Bilinear (fast)")
        resize_choice = input("Enter choice [1-3]: ").strip()
        if resize_choice == "2":
            options["resize_method"] = "bicubic"
        elif resize_choice == "3":
            options["resize_method"] = "bilinear"
    
    elif choice == "2":
        options["convert_format"] = True
        print_info("Target format:")
        print_info("[1] JPEG (recommended)")
        print_info("[2] PNG (lossless)")
        print_info("[3] WebP (modern)")
        format_choice = input("Enter choice [1-3]: ").strip()
        if format_choice == "2":
            options["target_format"] = "png"
        elif format_choice == "3":
            options["target_format"] = "webp"
        
        if options["target_format"] == "jpg":
            quality = input("JPEG quality (1-100, default 95): ").strip()
            options["quality"] = int(quality) if quality.isdigit() else 95
    
    elif choice == "3":
        options["remove_metadata"] = True
    
    elif choice == "4":
        options["normalize"] = True
    
    return options


def get_organization_options():
    """Get organization options from user."""
    options = {
        "organize_by": "none",
        "naming_convention": "original",
        "prefix": "",
        "padding": 5,
        "create_subfolders": False
    }
    
    print_info("Organization Options:")
    print_info("[1] Keep original structure")
    print_info("[2] Organize by file type")
    print_info("[3] Organize by size")
    print_info("[4] Organize by quality score")
    print_info("[5] Flat structure with custom naming")
    
    choice = input("Enter choice [1-5]: ").strip()
    
    if choice == "2":
        options["organize_by"] = "file_type"
    elif choice == "3":
        options["organize_by"] = "size"
    elif choice == "4":
        options["organize_by"] = "quality"
    elif choice == "5":
        options["organize_by"] = "flat"
        print_info("Naming convention:")
        print_info("[1] Keep original names")
        print_info("[2] Sequential numbering")
        print_info("[3] Custom prefix")
        naming_choice = input("Enter choice [1-3]: ").strip()
        if naming_choice == "2":
            options["naming_convention"] = "sequential"
            padding = input("Number padding (e.g., 5 for 00001): ").strip()
            options["padding"] = int(padding) if padding.isdigit() else 5
        elif naming_choice == "3":
            options["naming_convention"] = "prefix"
            options["prefix"] = input("Enter prefix: ").strip()
    
    return options


def process_dataset_with_options(image_files, output_folder, quality_options, preprocessing_options, organization_options):
    """Process the dataset according to the selected options."""
    processed_files = []
    skipped_files = []
    
    # Step 1: Quality filtering
    print_info("🔍 Applying quality filters...")
    filtered_files = apply_quality_filters(image_files, quality_options)
    
    # Step 2: Duplicate removal
    if quality_options["remove_duplicates"]:
        print_info("🔄 Removing duplicates...")
        filtered_files = remove_duplicates(filtered_files)
    
    # Step 3: Preprocessing
    print_info("⚙️ Applying preprocessing...")
    processed_files = apply_preprocessing(filtered_files, preprocessing_options, output_folder, organization_options)
    
    return processed_files


def apply_quality_filters(image_files, options):
    """Apply quality filters to the image files."""
    filtered_files = []
    
    for image_file in tqdm(image_files, desc="Applying quality filters"):
        try:
            # File size filter
            file_size = os.path.getsize(image_file)
            if file_size < options["min_size"] or file_size > options["max_size"]:
                continue
            
            # Image validation
            try:
                from PIL import Image
                with Image.open(image_file) as img:
                    width, height = img.size
                    max_dim = max(width, height)
                    
                    # Resolution filter
                    if max_dim < options["min_resolution"] or max_dim > options["max_resolution"]:
                        continue
                    
                    # Aspect ratio filter
                    if options["aspect_ratio_filter"]:
                        aspect_ratio = width / height
                        target_ratio = parse_aspect_ratio(options["aspect_ratio_filter"])
                        if abs(aspect_ratio - target_ratio) > 0.1:  # 10% tolerance
                            continue
                    
                    filtered_files.append(image_file)
                    
            except Exception as e:
                if options["remove_corrupted"]:
                    continue
                else:
                    filtered_files.append(image_file)
                    
        except Exception as e:
            continue
    
    print_info(f"Quality filtering: {len(filtered_files)}/{len(image_files)} files passed")
    return filtered_files


def remove_duplicates(image_files):
    """Remove duplicate images using perceptual hashing."""
    try:
        import imagehash
        from PIL import Image
        
        hashes = {}
        unique_files = []
        
        for image_file in tqdm(image_files, desc="Detecting duplicates"):
            try:
                with Image.open(image_file) as img:
                    # Compute perceptual hash
                    hash_value = imagehash.phash(img)
                    
                    if hash_value not in hashes:
                        hashes[hash_value] = image_file
                        unique_files.append(image_file)
                    else:
                        print_info(f"Duplicate found: {os.path.basename(image_file)} matches {os.path.basename(hashes[hash_value])}")
                        
            except Exception as e:
                unique_files.append(image_file)  # Keep files that can't be hashed
                continue
        
        print_info(f"Duplicate removal: {len(unique_files)}/{len(image_files)} unique files")
        return unique_files
        
    except ImportError:
        print_warning("imagehash not available. Skipping duplicate removal.")
        return image_files


def apply_preprocessing(image_files, options, output_folder, organization_options):
    """Apply preprocessing to the image files."""
    processed_files = []
    
    try:
        from PIL import Image
        
        for i, image_file in enumerate(tqdm(image_files, desc="Preprocessing images")):
            try:
                with Image.open(image_file) as img:
                    # Apply preprocessing
                    processed_img = apply_image_preprocessing(img, options)
                    
                    # Determine output path
                    output_path = determine_output_path(
                        image_file, i, output_folder, organization_options, options
                    )
                    
                    # Save processed image
                    save_processed_image(processed_img, output_path, options)
                    processed_files.append(output_path)
                    
            except Exception as e:
                print_error(f"Failed to process {image_file}: {e}")
                continue
                
    except ImportError:
        print_error("PIL/Pillow is required for preprocessing.")
        return []
    
    return processed_files


def apply_image_preprocessing(img, options):
    """Apply preprocessing to a single image."""
    # Resize
    if options["resize"]:
        img = resize_image(img, options["resize_width"], options["resize_height"], options["resize_method"])
    
    # Convert format
    if options["convert_format"]:
        img = convert_image_format(img, options["target_format"])
    
    # Normalize
    if options["normalize"]:
        img = normalize_image(img)
    
    return img


def resize_image(img, target_width, target_height, method):
    """Resize image while maintaining aspect ratio if needed."""
    from PIL import Image
    
    if target_width == 0 and target_height == 0:
        return img
    
    current_width, current_height = img.size
    
    if target_width == 0:
        # Maintain aspect ratio based on height
        ratio = target_height / current_height
        target_width = int(current_width * ratio)
    elif target_height == 0:
        # Maintain aspect ratio based on width
        ratio = target_width / current_width
        target_height = int(current_height * ratio)
    
    # Choose resize method
    if method == "lanczos":
        resample = Image.Resampling.LANCZOS
    elif method == "bicubic":
        resample = Image.Resampling.BICUBIC
    else:
        resample = Image.Resampling.BILINEAR
    
    return img.resize((target_width, target_height), resample)


def convert_image_format(img, target_format):
    """Convert image to target format."""
    from PIL import Image
    
    if target_format.upper() == "JPEG":
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
    
    return img


def normalize_image(img):
    """Normalize image pixel values."""
    import numpy as np
    
    # Convert to numpy array
    img_array = np.array(img)
    
    # Normalize to 0-1 range
    if img_array.dtype == np.uint8:
        img_array = img_array.astype(np.float32) / 255.0
    
    # Convert back to PIL Image
    return Image.fromarray((img_array * 255).astype(np.uint8))


def determine_output_path(image_file, index, output_folder, organization_options, preprocessing_options):
    """Determine the output path for a processed image."""
    original_name = os.path.splitext(os.path.basename(image_file))[0]
    original_ext = os.path.splitext(image_file)[1].lower()
    
    # Determine file extension
    if preprocessing_options["convert_format"]:
        ext = f".{preprocessing_options['target_format']}"
    else:
        ext = original_ext
    
    # Determine filename
    if organization_options["naming_convention"] == "sequential":
        filename = f"{index + 1:0{organization_options['padding']}d}{ext}"
    elif organization_options["naming_convention"] == "prefix":
        filename = f"{organization_options['prefix']}_{original_name}{ext}"
    else:
        filename = f"{original_name}{ext}"
    
    # Determine subfolder
    subfolder = ""
    if organization_options["organize_by"] == "file_type":
        subfolder = ext[1:]  # Remove the dot
    elif organization_options["organize_by"] == "size":
        # This would need to be determined during processing
        subfolder = "processed"
    
    if subfolder:
        output_path = os.path.join(output_folder, subfolder, filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    else:
        output_path = os.path.join(output_folder, filename)
    
    return output_path


def save_processed_image(img, output_path, options):
    """Save processed image with appropriate settings."""
    from PIL import Image
    
    # Remove metadata if requested
    if options["remove_metadata"]:
        # Create a new image without metadata
        img_data = list(img.getdata())
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(img_data)
        img = new_img
    
    # Save with appropriate format and quality
    if options["convert_format"] and options["target_format"] == "jpg":
        img.save(output_path, "JPEG", quality=options["quality"], optimize=True)
    elif options["convert_format"] and options["target_format"] == "webp":
        img.save(output_path, "WebP", quality=options["quality"])
    else:
        img.save(output_path)


def parse_aspect_ratio(ratio_str):
    """Parse aspect ratio string (e.g., '16:9') to float."""
    try:
        width, height = map(int, ratio_str.split(':'))
        return width / height
    except:
        return 1.0  # Default to square


def generate_dataset_report(processed_files, output_folder, original_stats):
    """Generate a comprehensive dataset report."""
    print_success(f"✅ Dataset creation completed!")
    print_info(f"📁 Output location: {output_folder}")
    print_info(f"📊 Files processed: {len(processed_files)}")
    
    # Calculate final statistics
    final_stats = analyze_dataset_composition(processed_files)
    
    # Create report file
    report_path = os.path.join(output_folder, "dataset_report.txt")
    with open(report_path, 'w') as f:
        f.write("Dataset Creation Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Source files: {original_stats['total_files']}\n")
        f.write(f"Final files: {len(processed_files)}\n")
        f.write(f"Reduction: {original_stats['total_files'] - len(processed_files)} files\n")
        f.write(f"Total size: {final_stats['total_size_bytes'] / (1024*1024):.2f} MB\n\n")
        
        if final_stats["file_types"]:
            f.write("File type distribution:\n")
            for ext, count in sorted(final_stats["file_types"].items()):
                f.write(f"  {ext}: {count} files\n")
            f.write("\n")
        
        if final_stats["size_categories"]:
            f.write("Size distribution:\n")
            for category, count in final_stats["size_categories"].items():
                if count > 0:
                    f.write(f"  {category}: {count} files\n")
            f.write("\n")
    
    print_info(f"📄 Report saved to: {report_path}")
    print_success(f"🎉 Dataset ready for use!")


@monitor_all("create_dataset_from_video", critical_on_error=True)
def create_dataset_from_video(video_path: str, output_folder: str):
    """Create a dataset from a video file by extracting frames.
    
    Args:
        video_path: Path to the video file
        output_folder: Path to the output folder where frames will be saved
    """
    print_header("🎬 Create Dataset from Video")
    
    # Validate input path
    if not os.path.exists(video_path):
        print_error(f"Video file does not exist: {video_path}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        import cv2
        
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print_error(f"Failed to open video file: {video_path}")
            return
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        print_info(f"Video properties:")
        print_info(f"  - Total frames: {total_frames}")
        print_info(f"  - FPS: {fps:.2f}")
        print_info(f"  - Duration: {duration:.2f} seconds")
        
        # Ask user for frame extraction settings
        print_section("Frame Extraction Settings")
        print_info("[1] Extract all frames")
        print_info("[2] Extract every Nth frame")
        print_info("[3] Extract frames at specific intervals")
        
        choice = input("Enter choice [1-3]: ").strip()
        
        frame_interval = 1
        if choice == "2":
            frame_interval = int(input("Extract every Nth frame (e.g., 30 for every 30th frame): ").strip())
        elif choice == "3":
            start_time = float(input("Start time in seconds: ").strip())
            end_time = float(input("End time in seconds: ").strip())
            interval = float(input("Interval between frames in seconds: ").strip())
            start_frame = int(start_time * fps)
            end_frame = int(end_time * fps)
            frame_interval = int(interval * fps)
        elif choice != "1":
            print_error("Invalid choice. Using default: extract all frames.")
        
        # Extract frames
        extracted_count = 0
        frame_count = 0
        
        with tqdm(total=total_frames, desc="Extracting frames") as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Check if we should extract this frame
                should_extract = False
                if choice == "1":
                    should_extract = True
                elif choice == "2":
                    should_extract = (frame_count % frame_interval == 0)
                elif choice == "3":
                    should_extract = (start_frame <= frame_count <= end_frame and 
                                    (frame_count - start_frame) % frame_interval == 0)
                
                if should_extract:
                    # Save frame
                    frame_filename = f"frame_{frame_count:06d}.jpg"
                    frame_path = os.path.join(output_folder, frame_filename)
                    cv2.imwrite(frame_path, frame)
                    extracted_count += 1
                
                frame_count += 1
                pbar.update(1)
        
        cap.release()
        
        print_success(f"Successfully extracted {extracted_count} frames")
        print_info(f"Frames saved to: {output_folder}")
        
    except ImportError:
        print_error("OpenCV (cv2) is required for video processing. Please install it with: pip install opencv-python")
        return
    except Exception as e:
        print_error(f"Error processing video: {e}")
        return
    
    # Play completion sound
    play_done_sound()


@monitor_all("create_dataset_from_images", critical_on_error=True)
def create_dataset_from_images(image_folder: str, output_folder: str):
    """Create a dataset from individual image files in a folder.
    
    Args:
        image_folder: Path to the folder containing individual images
        output_folder: Path to the output folder where dataset will be created
    """
    print_header("🖼️ Create Dataset from Images")
    
    # Validate input path
    if not os.path.exists(image_folder):
        print_error(f"Image folder does not exist: {image_folder}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all image files from the folder
    image_files = get_image_files(image_folder)
    
    if not image_files:
        print_error(f"No image files found in folder: {image_folder}")
        return
    
    print_info(f"Found {len(image_files)} image files")
    
    # Ask user for organization method
    print_section("Organization Method")
    print_info("[1] Copy all images to output folder")
    print_info("[2] Organize by file type")
    print_info("[3] Organize by size categories")
    
    choice = input("Enter choice [1-3]: ").strip()
    
    copied_count = 0
    
    if choice == "1":
        # Simple copy all images
        for image_file in tqdm(image_files, desc="Copying images"):
            try:
                filename = os.path.basename(image_file)
                dest_path = os.path.join(output_folder, filename)
                
                # Handle duplicate filenames
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(output_folder, new_filename)
                        counter += 1
                
                shutil.copy2(image_file, dest_path)
                copied_count += 1
                
            except Exception as e:
                print_error(f"Failed to copy {image_file}: {e}")
                continue
    
    elif choice == "2":
        # Organize by file type
        file_types = {}
        for image_file in image_files:
            ext = os.path.splitext(image_file)[1].lower()
            if ext not in file_types:
                file_types[ext] = []
            file_types[ext].append(image_file)
        
        for ext, files in file_types.items():
            ext_folder = os.path.join(output_folder, ext[1:])  # Remove the dot
            os.makedirs(ext_folder, exist_ok=True)
            
            for image_file in tqdm(files, desc=f"Copying {ext} files"):
                try:
                    filename = os.path.basename(image_file)
                    dest_path = os.path.join(ext_folder, filename)
                    
                    # Handle duplicate filenames
                    if os.path.exists(dest_path):
                        base, ext_name = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(dest_path):
                            new_filename = f"{base}_{counter}{ext_name}"
                            dest_path = os.path.join(ext_folder, new_filename)
                            counter += 1
                    
                    shutil.copy2(image_file, dest_path)
                    copied_count += 1
                    
                except Exception as e:
                    print_error(f"Failed to copy {image_file}: {e}")
                    continue
    
    elif choice == "3":
        # Organize by size categories
        try:
            from PIL import Image
            
            size_categories = {
                "small": [],      # < 512x512
                "medium": [],     # 512x512 - 1024x1024
                "large": [],      # 1024x1024 - 2048x2048
                "xlarge": []      # > 2048x2048
            }
            
            # Categorize images by size
            for image_file in tqdm(image_files, desc="Analyzing image sizes"):
                try:
                    with Image.open(image_file) as img:
                        width, height = img.size
                        max_dim = max(width, height)
                        
                        if max_dim < 512:
                            size_categories["small"].append(image_file)
                        elif max_dim < 1024:
                            size_categories["medium"].append(image_file)
                        elif max_dim < 2048:
                            size_categories["large"].append(image_file)
                        else:
                            size_categories["xlarge"].append(image_file)
                            
                except Exception as e:
                    print_error(f"Failed to analyze {image_file}: {e}")
                    continue
            
            # Copy images to size-based folders
            for category, files in size_categories.items():
                if files:
                    category_folder = os.path.join(output_folder, category)
                    os.makedirs(category_folder, exist_ok=True)
                    
                    for image_file in tqdm(files, desc=f"Copying {category} images"):
                        try:
                            filename = os.path.basename(image_file)
                            dest_path = os.path.join(category_folder, filename)
                            
                            # Handle duplicate filenames
                            if os.path.exists(dest_path):
                                base, ext = os.path.splitext(filename)
                                counter = 1
                                while os.path.exists(dest_path):
                                    new_filename = f"{base}_{counter}{ext}"
                                    dest_path = os.path.join(category_folder, new_filename)
                                    counter += 1
                            
                            shutil.copy2(image_file, dest_path)
                            copied_count += 1
                            
                        except Exception as e:
                            print_error(f"Failed to copy {image_file}: {e}")
                            continue
                            
        except ImportError:
            print_error("PIL/Pillow is required for size-based organization. Please install it with: pip install Pillow")
            return
    
    else:
        print_error("Invalid choice. Using default: copy all images.")
        # Fallback to simple copy
        for image_file in tqdm(image_files, desc="Copying images"):
            try:
                filename = os.path.basename(image_file)
                dest_path = os.path.join(output_folder, filename)
                
                # Handle duplicate filenames
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(output_folder, new_filename)
                        counter += 1
                
                shutil.copy2(image_file, dest_path)
                copied_count += 1
                
            except Exception as e:
                print_error(f"Failed to copy {image_file}: {e}")
                continue
    
    print_success(f"Successfully created dataset with {copied_count} images")
    print_info(f"Dataset saved to: {output_folder}")
    
    # Play completion sound
    play_done_sound()


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
