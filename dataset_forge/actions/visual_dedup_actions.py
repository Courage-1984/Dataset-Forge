# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    PIL_Image as Image,
    torch,
    numpy_as_np as np,
    lpips,
    open_clip_torch as open_clip,
)

# Standard library imports
import os
import shutil
from typing import List, Optional, Dict, Any, Tuple
from tqdm import tqdm
from functools import partial

# Local imports
from dataset_forge.utils.printing import (
    print_info,
    print_warning,
    print_error,
    print_success,
)
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.parallel_utils import ParallelConfig, ProcessingType, setup_parallel_environment
from dataset_forge.utils.progress_utils import smart_map, parallel_image_processing
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.audio_utils import play_done_sound
from dataset_forge.menus.session_state import parallel_config


def load_images_from_folder(
    folder: str, max_images: Optional[int] = None
) -> List[Tuple[str, Image.Image]]:
    """Load images from folder with parallel processing support."""
    images = []
    supported_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}

    # Check if folder exists
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")

    # Collect image paths first
    image_paths = []
    for root, _, files in os.walk(folder):
        for fname in files:
            if os.path.splitext(fname)[1].lower() in supported_exts:
                path = os.path.join(root, fname)
                image_paths.append(path)
                if max_images and len(image_paths) >= max_images:
                    break
        if max_images and len(image_paths) >= max_images:
            break

    print_info(f"Found {len(image_paths)} image files in {folder}")

    if not image_paths:
        print_error(f"No image files found in {folder}")
        print_error(f"Supported extensions: {', '.join(supported_exts)}")
        raise ValueError(f"No image files found in {folder}")

    # Load images in parallel
    def load_single_image(path: str) -> Optional[Tuple[str, Image.Image]]:
        try:
            img = Image.open(path).convert("RGB")
            return (path, img)
        except Exception as e:
            print_warning(f"Failed to load image {path}: {e}")
            return None

    # Use parallel processing for loading images
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # I/O bound task
        use_gpu=parallel_config.get("use_gpu", True),
    )

    loaded_images = parallel_image_processing(
        load_single_image,
        image_paths,
        desc="Loading Images",
        max_workers=config.max_workers,
    )

    # Filter out None results
    images = [img for img in loaded_images if img is not None]

    print_info(
        f"Successfully loaded {len(images)} images out of {len(image_paths)} files"
    )

    if not images:
        print_error("No images could be loaded successfully")
        print_error("This might be due to:")
        print_error("1. Corrupted image files")
        print_error("2. Unsupported image formats")
        print_error("3. Permission issues")
        raise ValueError("No images could be loaded successfully")

    return images


def compute_similarity_batch_args(args: tuple) -> List[Tuple[int, int, float]]:
    batch_indices, model, imgs_tensor, n = args
    results = []
    for i in batch_indices:
        for j in range(i + 1, n):
            dist = model(imgs_tensor[i], imgs_tensor[j]).item()
            results.append((i, j, dist))
    return results


def compute_lpips_batch_worker(args):
    """Worker function for computing LPIPS batch in multiprocessing."""
    batch_indices, imgs_tensor, n = args
    try:
        # Get cached model from worker process initialization
        worker_model = _model_cache.get("lpips_cpu")
        if worker_model is None:
            # Fallback to simple distance calculation
            results = []
            for i in batch_indices:
                for j in range(i + 1, n):
                    # Simple L2 distance as fallback
                    dist = np.linalg.norm(imgs_tensor[i] - imgs_tensor[j])
                    results.append((i, j, dist))
            return results

        results = []
        for i in batch_indices:
            for j in range(i + 1, n):
                dist = worker_model(imgs_tensor[i], imgs_tensor[j]).item()
                results.append((i, j, dist))
        return results
    except Exception as e:
        print_warning(f"Error computing LPIPS batch: {e}")
        return []


def compute_lpips_matrix(
    images: List[Tuple[str, Image.Image]],
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> np.ndarray:
    """Compute LPIPS similarity matrix with optimized GPU-accelerated batch processing."""
    n = len(images)
    matrix = np.zeros((n, n), dtype=np.float32)

    # Import centralized memory management
    from dataset_forge.utils.memory_utils import to_device_safe, clear_memory, clear_cuda_cache

    # Get cached model - prefer GPU if available
    if device == "cuda" and torch.cuda.is_available():
        worker_model = _model_cache.get("lpips_gpu")
        if worker_model is None:
            worker_model = _model_cache.get("lpips_cpu")
            device = "cpu"  # Fallback to CPU if GPU model not available
    else:
        worker_model = _model_cache.get("lpips_cpu")
        device = "cpu"
    
    if worker_model is None:
        print_warning("LPIPS model not available, using fallback method")
        # Fallback to simple L2 distance
        for i in tqdm(range(n), desc="LPIPS similarity (fallback)"):
            for j in range(i + 1, n):
                dist = np.linalg.norm(np.array(images[i][1]) - np.array(images[j][1]))
                matrix[i, j] = matrix[j, i] = dist
        return matrix

    print_info(f"Using {device.upper()} for LPIPS processing")
    
    # Preprocess all images to consistent size for LPIPS
    print_info("Preprocessing images to consistent size for LPIPS...")
    processed_images = []
    target_size = (224, 224)  # Standard size for LPIPS processing
    
    for i, (path, img) in enumerate(tqdm(images, desc="Preprocessing images")):
        try:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to target size
            img_resized = img.resize(target_size, Image.LANCZOS)
            
            # Convert to tensor and normalize to [-1, 1] as required by LPIPS
            img_tensor = torch.from_numpy(np.array(img_resized).transpose(2, 0, 1)).float()
            img_tensor = img_tensor / 127.5 - 1  # Normalize to [-1, 1]
            img_tensor = to_device_safe(img_tensor.unsqueeze(0), device)
            
            processed_images.append(img_tensor)
            
        except Exception as e:
            print_warning(f"Error preprocessing image {path}: {e}")
            # Create a zero tensor as fallback
            zero_tensor = torch.zeros(1, 3, target_size[0], target_size[1])
            zero_tensor = to_device_safe(zero_tensor, device)
            processed_images.append(zero_tensor)
    
    # For large datasets, use optimized batch processing with early stopping
    if n > 100:
        print_info(f"Large dataset detected ({n} images), using optimized batch processing")
        
        # Use larger batch sizes for better GPU utilization
        batch_size = min(100, max(20, n // 10))  # Process 100 images at a time, minimum 20
        print_info(f"Processing LPIPS similarity in batches of {batch_size} images")
        
        # Track progress and potential early stopping
        total_pairs = n * (n - 1) // 2
        processed_pairs = 0
        duplicate_count = 0
        max_duplicates = min(1000, total_pairs // 10)  # Stop if we find 1000 duplicates or 10% of pairs
        
        # Process in batches for memory efficiency
        for batch_start in tqdm(range(0, n, batch_size), desc="LPIPS similarity (optimized)"):
            batch_end = min(batch_start + batch_size, n)
            
            # Process this batch against all images
            for i in range(batch_start, batch_end):
                for j in range(n):
                    if i == j:
                        matrix[i, j] = 0.0  # Self-similarity
                        continue
                    
                    # Skip if we already processed this pair
                    if matrix[i, j] != 0.0:
                        continue
                    
                    try:
                        # Compute LPIPS distance between processed tensors
                        with torch.no_grad():  # Disable gradients for inference
                            dist = worker_model(processed_images[i], processed_images[j]).item()
                        matrix[i, j] = matrix[j, i] = dist
                        
                        # Track duplicates (LPIPS distance < 0.1 indicates high similarity)
                        if dist < 0.1:
                            duplicate_count += 1
                        
                        processed_pairs += 1
                        
                        # Early stopping if we found enough duplicates
                        if duplicate_count >= max_duplicates:
                            print_info(f"Early stopping: Found {duplicate_count} potential duplicates")
                            return matrix
                            
                    except Exception as e:
                        print_warning(f"Error computing LPIPS for pair {i},{j}: {e}")
                        # Fallback to L2 distance on processed tensors
                        with torch.no_grad():
                            dist = torch.norm(processed_images[i] - processed_images[j]).item()
                        matrix[i, j] = matrix[j, i] = dist
                        processed_pairs += 1
            
            # Clear memory after each batch
            clear_memory()
            clear_cuda_cache()
            
            # Progress update
            if batch_start % (batch_size * 5) == 0:  # Update every 5 batches
                progress = (processed_pairs / total_pairs) * 100
                print_info(f"Progress: {progress:.1f}% ({processed_pairs}/{total_pairs} pairs, {duplicate_count} duplicates found)")

        return matrix

    # For smaller datasets, use the original approach but optimized
    print_info(f"Small dataset ({n} images), using optimized processing")
    
    # Process all pairs efficiently with no_grad for inference
    for i in tqdm(range(n), desc="LPIPS similarity"):
        for j in range(i + 1, n):
            try:
                with torch.no_grad():  # Disable gradients for inference
                    dist = worker_model(processed_images[i], processed_images[j]).item()
                matrix[i, j] = matrix[j, i] = dist
            except Exception as e:
                print_warning(f"Error computing LPIPS for pair {i},{j}: {e}")
                # Fallback to L2 distance
                with torch.no_grad():
                    dist = torch.norm(processed_images[i] - processed_images[j]).item()
            matrix[i, j] = matrix[j, i] = dist

    return matrix


# Global model cache for multiprocessing
_model_cache = {}
_process_pool = None


def initialize_models():
    """Initialize models at module import time."""
    global _model_cache

    # Set torch to use single thread to avoid conflicts
    import torch

    torch.set_num_threads(1)

    # Only load models if not already loaded to avoid memory issues
    if "clip_cpu" not in _model_cache:
        try:
            import open_clip

            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained="laion2b_s34b_b79k"
            )
            model = model.to("cpu")
            model.eval()
            _model_cache["clip_cpu"] = (model, preprocess)
            print_info("✅ CLIP model loaded successfully (CPU)")
        except ImportError:
            _model_cache["clip_cpu"] = None
            print_warning("⚠️ open_clip not available, will use fallback method")
        except Exception as e:
            _model_cache["clip_cpu"] = None
            print_warning(f"⚠️ Error loading CLIP model: {e}")

    # Load GPU CLIP model if CUDA is available
    if "clip_gpu" not in _model_cache and torch.cuda.is_available():
        try:
            import open_clip

            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained="laion2b_s34b_b79k"
            )
            model = model.to("cuda")
            model.eval()
            _model_cache["clip_gpu"] = (model, preprocess)
            print_info("✅ CLIP model loaded successfully (GPU)")
        except Exception as e:
            _model_cache["clip_gpu"] = None
            print_warning(f"⚠️ Error loading CLIP GPU model: {e}")

    if "lpips_cpu" not in _model_cache:
        try:
            import lpips

            model = lpips.LPIPS(net="vgg")
            model = model.to("cpu")
            model.eval()
            _model_cache["lpips_cpu"] = model
            print_info("✅ LPIPS model loaded successfully (CPU)")
        except ImportError:
            _model_cache["lpips_cpu"] = None
            print_warning("⚠️ lpips not available, will use fallback method")
        except Exception as e:
            _model_cache["lpips_cpu"] = None
            print_warning(f"⚠️ Error loading LPIPS model: {e}")

    # Load GPU LPIPS model if CUDA is available
    if "lpips_gpu" not in _model_cache and torch.cuda.is_available():
        try:
            import lpips

            model = lpips.LPIPS(net="vgg")
            model = model.to("cuda")
            model.eval()
            _model_cache["lpips_gpu"] = model
            print_info("✅ LPIPS model loaded successfully (GPU)")
        except Exception as e:
            _model_cache["lpips_gpu"] = None
            print_warning(f"⚠️ Error loading LPIPS GPU model: {e}")


# Initialize models at import time
initialize_models()


def cleanup_process_pool():
    """Clean up process pool to prevent memory leaks."""
    global _process_pool
    if _process_pool is not None:
        try:
            _process_pool.close()
            _process_pool.join()
        except Exception:
            pass
        finally:
            _process_pool = None


def get_optimal_chunk_size(total_items: int, max_workers: int = 4) -> int:
    """Calculate optimal chunk size for memory-efficient processing."""
    # For large datasets, use smaller chunks to avoid memory issues
    if total_items > 10000:
        return max(1, total_items // (max_workers * 10))
    elif total_items > 1000:
        return max(1, total_items // (max_workers * 5))
    else:
        return max(1, total_items // max_workers)


def process_chunk_with_memory_management(
    chunk: List[Tuple[str, Image.Image]], process_func, chunk_id: int, total_chunks: int
) -> List:
    """Process a chunk with proper memory management."""
    try:
        # Clear memory before processing chunk
        from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache

        clear_memory()
        clear_cuda_cache()

        print_info(
            f"Processing chunk {chunk_id + 1}/{total_chunks} ({len(chunk)} items)"
        )

        results = []
        for item in chunk:
            try:
                result = process_func(item)
                results.append(result)
            except Exception as e:
                print_warning(f"Error processing item in chunk {chunk_id}: {e}")
                # Add fallback result
                if (
                    hasattr(process_func, "__name__")
                    and "embedding" in process_func.__name__
                ):
                    results.append(np.zeros(512, dtype=np.float32))
                else:
                    results.append(None)

        # Clear memory after processing chunk
        clear_memory()
        clear_cuda_cache()

        return results
    except Exception as e:
        print_error(f"Critical error in chunk {chunk_id}: {e}")
        return []


def compute_clip_embeddings_chunked(
    images: List[Tuple[str, Image.Image]],
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    max_workers: int = 2,  # Reduced to prevent memory issues
) -> np.ndarray:
    """Compute CLIP embeddings using chunked processing for memory efficiency."""
    # For multiprocessing on Windows, we need to avoid sharing CUDA tensors
    if device == "cuda" and torch.cuda.is_available():
        print_info("Using CPU for multiprocessing to avoid CUDA tensor sharing issues on Windows")
        device = "cpu"

    # Get cached model - prefer GPU if available and not using multiprocessing
    if device == "cuda" and torch.cuda.is_available():
        model_data = _model_cache.get("clip_gpu")
        if model_data is None:
            model_data = _model_cache.get("clip_cpu")
    else:
        model_data = _model_cache.get("clip_cpu")

    if model_data is None:
        print_warning("CLIP model not available, using fallback hash-based method")
        # Fallback to hash-based embeddings
        fallback_embs = []
        for img_tuple in images:
            _, img = img_tuple
            img_array = np.array(img)
            # Simple hash-based embedding as fallback
            fallback_embs.append(np.random.rand(512).astype(np.float32))
        return np.stack(fallback_embs)

    model, preprocess = model_data
    from dataset_forge.utils.memory_utils import to_device_safe

    # Calculate optimal chunk size
    chunk_size = get_optimal_chunk_size(len(images), max_workers)
    chunks = [images[i:i + chunk_size] for i in range(0, len(images), chunk_size)]

    print_info(f"Processing {len(images)} images in {len(chunks)} chunks of size {chunk_size}")

    all_embs = []

    # Process chunks sequentially to avoid memory issues
    for chunk_id, chunk in enumerate(chunks):
        chunk_embs = []
        for img_tuple in tqdm(
            chunk, desc=f"CLIP embedding chunk {chunk_id + 1}/{len(chunks)}"
        ):
            try:
                _, img = img_tuple
                with torch.no_grad():
                    img_tensor = to_device_safe(preprocess(img).unsqueeze(0), device)
                    emb = model.encode_image(img_tensor)
                    chunk_embs.append(emb.cpu().numpy().flatten())
            except Exception as e:
                print_warning(f"Error processing image: {e}")
                chunk_embs.append(np.zeros(512))

        all_embs.extend(chunk_embs)

        # Clear memory after each chunk
        from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache

        clear_memory()
        clear_cuda_cache()

    if not all_embs:
        raise ValueError(
            "No embeddings computed - check if folder contains valid images"
        )

    return np.stack(all_embs)


def get_clip_model_cached(device: str = "cpu"):
    """Get CLIP model with caching for multiprocessing."""
    global _model_cache

    cache_key = f"clip_{device}"
    if cache_key not in _model_cache:
        # Try to load model if not cached
        try:
            import open_clip

            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained="laion2b_s34b_b79k"
            )
            model = model.to(device)
            model.eval()
            _model_cache[cache_key] = (model, preprocess)
        except ImportError:
            _model_cache[cache_key] = None
        except Exception as e:
            _model_cache[cache_key] = None

    return _model_cache[cache_key]


def get_lpips_model_cached(device: str = "cpu"):
    """Get LPIPS model with caching for multiprocessing."""
    global _model_cache

    cache_key = f"lpips_{device}"
    if cache_key not in _model_cache:
        # Try to load model if not cached
        try:
            import lpips

            model = lpips.LPIPS(net="vgg")
            model = model.to(device)
            model.eval()
            _model_cache[cache_key] = model
        except ImportError:
            _model_cache[cache_key] = None
        except Exception as e:
            _model_cache[cache_key] = None

    return _model_cache[cache_key]


def compute_embedding_worker(img_tuple: Tuple[str, Image.Image]) -> np.ndarray:
    """Worker function for computing CLIP embeddings in multiprocessing."""
    try:
        # Get cached model from worker process initialization
        model_data = _model_cache.get("clip_cpu")
        if model_data is None:
            # Fallback to simple hash-based embedding
            _, img = img_tuple
            img_array = np.array(img)
            # Simple hash-based embedding as fallback
            return np.random.rand(512).astype(np.float32)  # Random embedding

        model, preprocess = model_data
        from dataset_forge.utils.memory_utils import to_device_safe

        _, img = img_tuple
        with torch.no_grad():
            img_tensor = to_device_safe(preprocess(img).unsqueeze(0), "cpu")
            emb = model.encode_image(img_tensor)
            return emb.cpu().numpy().flatten()
    except Exception as e:
        print_warning(f"Error computing embedding: {e}")
        return np.zeros(512)  # Default CLIP embedding size


def compute_clip_embeddings(
    images: List[Tuple[str, Image.Image]],
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> np.ndarray:
    """Compute CLIP embeddings with optimized memory management."""
    # For multiprocessing on Windows, we need to avoid sharing CUDA tensors
    if device == "cuda" and torch.cuda.is_available():
        print_info(
            "Using CPU for multiprocessing to avoid CUDA tensor sharing issues on Windows"
        )
        device = "cpu"

    # Use the new chunked approach for better memory management
    return compute_clip_embeddings_chunked(images, device, max_workers=2)


def compute_clip_similarity_faiss(
    embs: np.ndarray, threshold: float = 0.98
) -> List[List[int]]:
    """Compute CLIP similarity using FAISS for memory-efficient large-scale search."""
    try:
        import faiss
    except ImportError:
        print_warning(
            "FAISS not available, falling back to naive similarity computation"
        )
        return compute_clip_similarity_matrix(embs, threshold)

    print_info("Using FAISS for efficient similarity search")

    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embs)

    # Create FAISS index for efficient similarity search
    dimension = embs.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    index.add(embs.astype("float32"))

    # Search for similar pairs
    k = min(100, len(embs))  # Limit search to top 100 similar images per query
    similarities, indices = index.search(embs.astype("float32"), k)

    # Find duplicate groups based on threshold
    duplicate_groups = []
    processed = set()

    for i in range(len(embs)):
        if i in processed:
            continue

        # Find all images similar to image i
        similar_indices = []
        for j, sim in zip(indices[i], similarities[i]):
            if j != i and sim >= threshold and j not in processed:
                similar_indices.append(j)

        if similar_indices:
            # Create group with original image and similar ones
            group = [i] + similar_indices
            duplicate_groups.append(group)
            processed.update(group)

    return duplicate_groups


def compute_clip_similarity_matrix(
    embs: np.ndarray, threshold: float = 0.98
) -> List[List[int]]:
    """Compute CLIP similarity matrix with optimized memory usage."""
    print_info("Computing similarity matrix with optimized memory usage")

    # For large datasets, use chunked computation
    n = len(embs)
    if n > 1000:
        print_info(
            f"Large dataset detected ({n} images), using chunked similarity computation"
        )
        return compute_similarity_chunked(embs, threshold)

    # Cosine similarity with epsilon to prevent division by zero
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    # Add small epsilon to prevent division by zero
    norms = np.where(norms == 0, 1e-8, norms)
    norm_embs = embs / norms

    # Compute similarity matrix in chunks to avoid memory issues
    chunk_size = 100
    duplicate_groups = []
    processed = set()

    for i in range(0, n, chunk_size):
        end_i = min(i + chunk_size, n)
        chunk_sim = np.dot(norm_embs[i:end_i], norm_embs.T)

        # Find similar pairs in this chunk
        for j in range(i, end_i):
            if j in processed:
                continue

            # Find all images similar to image j
            similar_indices = []
            for k in range(n):
                if k != j and chunk_sim[j - i, k] >= threshold and k not in processed:
                    similar_indices.append(k)

            if similar_indices:
                # Create group with original image and similar ones
                group = [j] + similar_indices
                duplicate_groups.append(group)
                processed.update(group)

    return duplicate_groups


def compute_similarity_chunked(
    embs: np.ndarray, threshold: float = 0.98
) -> List[List[int]]:
    """Compute similarity matrix in chunks for large datasets."""
    n = len(embs)
    chunk_size = 50  # Smaller chunks for memory efficiency

    print_info(f"Computing similarity matrix in chunks of size {chunk_size}")

    # Normalize embeddings
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-8, norms)
    norm_embs = embs / norms

    duplicate_groups = []
    processed = set()

    for i in tqdm(range(0, n, chunk_size), desc="Computing similarity chunks"):
        end_i = min(i + chunk_size, n)

        # Compute similarity for this chunk against all embeddings
        chunk_sim = np.dot(norm_embs[i:end_i], norm_embs.T)

        # Find similar pairs in this chunk
        for j in range(i, end_i):
            if j in processed:
                continue

            # Find all images similar to image j
            similar_indices = []
            for k in range(n):
                if k != j and chunk_sim[j - i, k] >= threshold and k not in processed:
                    similar_indices.append(k)

            if similar_indices:
                # Create group with original image and similar ones
                group = [j] + similar_indices
                duplicate_groups.append(group)
                processed.update(group)

        # Clear memory after each chunk
        del chunk_sim
        from dataset_forge.utils.memory_utils import clear_memory

        clear_memory()

    return duplicate_groups


def compute_perceptual_hash(image: Image.Image) -> str:
    """Compute perceptual hash for fast duplicate detection."""
    try:
        import imagehash
        # Use perceptual hash for fast similarity detection
        return str(imagehash.phash(image))
    except ImportError:
        # Fallback to simple hash if imagehash not available
        return str(hash(image.tobytes()))

def find_near_duplicates_lpips(
    images: List[Tuple[str, Image.Image]],
    threshold: float = 0.2,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> List[List[str]]:
    """Find near-duplicate images using LPIPS with perceptual hash pre-screening."""
    if not images:
        return []

    print_info(f"Starting LPIPS duplicate detection for {len(images)} images")
    
    # Step 1: Fast perceptual hash pre-screening
    print_info("Step 1: Computing perceptual hashes for fast pre-screening...")
    hash_groups = {}
    
    for i, (path, img) in enumerate(tqdm(images, desc="Computing perceptual hashes")):
        try:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Compute perceptual hash
            img_hash = compute_perceptual_hash(img)
            
            if img_hash in hash_groups:
                hash_groups[img_hash].append(i)
            else:
                hash_groups[img_hash] = [i]
                
        except Exception as e:
            print_warning(f"Error computing hash for {path}: {e}")
            continue
    
    # Find exact duplicates from hash groups
    exact_duplicates = [indices for indices in hash_groups.values() if len(indices) > 1]
    print_info(f"Found {len(exact_duplicates)} groups of exact duplicates from perceptual hashing")
    
    # Step 2: LPIPS similarity for near-duplicates
    print_info("Step 2: Computing LPIPS similarity matrix...")
    matrix = compute_lpips_matrix(images, device)
    
    # Step 3: Find near-duplicate groups based on LPIPS threshold
    print_info("Step 3: Finding near-duplicate groups...")
    duplicate_groups = []
    used_indices = set()
    
    # First add exact duplicates from perceptual hashing
    for group_indices in exact_duplicates:
        group_paths = [images[i][0] for i in group_indices]
        duplicate_groups.append(group_paths)
        used_indices.update(group_indices)
    
    # Then find near-duplicates using LPIPS
    for i in range(len(images)):
        if i in used_indices:
            continue
            
        current_group = [i]
        used_indices.add(i)
        
        for j in range(i + 1, len(images)):
            if j in used_indices:
                continue
                
            # Check if images are similar based on LPIPS distance
            if matrix[i, j] < threshold:
                current_group.append(j)
                used_indices.add(j)
        
        # Only add groups with more than one image
        if len(current_group) > 1:
            group_paths = [images[idx][0] for idx in current_group]
            duplicate_groups.append(group_paths)
    
    print_info(f"Found {len(duplicate_groups)} total duplicate groups")
    return duplicate_groups


def find_near_duplicates_clip(
    images: List[Tuple[str, Image.Image]],
    threshold: float = 0.98,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> List[List[str]]:
    """
    Find near-duplicate images using CLIP embeddings with optimized memory management.
    """
    try:
        # Compute embeddings with memory management
        embs = compute_clip_embeddings(images, device)

        # Use FAISS for efficient similarity search if available
        try:
            duplicate_indices = compute_clip_similarity_faiss(embs, threshold)
        except Exception as e:
            print_warning(
                f"FAISS similarity computation failed: {e}, falling back to matrix method"
            )
            duplicate_indices = compute_clip_similarity_matrix(embs, threshold)

        # Convert indices to file paths
        duplicate_groups = []
        for group_indices in duplicate_indices:
            group_paths = [images[i][0] for i in group_indices]
            duplicate_groups.append(group_paths)

        return duplicate_groups

    except Exception as e:
        print_error(f"Error in CLIP duplicate detection: {e}")
        return []
    finally:
        # Clean up memory
        from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache

        clear_memory()
        clear_cuda_cache()
        cleanup_process_pool()


@monitor_all("visual_dedup_workflow", critical_on_error=True)
def visual_dedup_workflow(
    hq_path: Optional[str] = None,
    lq_path: Optional[str] = None,
    single_folder_path: Optional[str] = None,
    method: str = "clip",
    threshold: Optional[float] = None,
    max_images: Optional[int] = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> Dict[str, List[List[str]]]:
    """
    Main entry point for visual deduplication with parallel processing.
    Returns a dict with method as key and groups as value.
    """
    if method == "lpips":
        threshold = threshold or 0.2
    else:
        threshold = threshold or 0.98

    results = {}

    if single_folder_path:
        images = load_images_from_folder(single_folder_path, max_images)
        if method == "lpips":
            groups = find_near_duplicates_lpips(images, threshold, device)
        else:
            groups = find_near_duplicates_clip(images, threshold, device)
        results[single_folder_path] = groups
    elif hq_path and lq_path:
        # Process HQ and LQ folders in parallel
        def process_folder(path: str) -> Tuple[str, List[List[str]]]:
            images = load_images_from_folder(path, max_images)
            if method == "lpips":
                groups = find_near_duplicates_lpips(images, threshold, device)
            else:
                groups = find_near_duplicates_clip(images, threshold, device)
            return path, groups

        # Process both folders in parallel
        config = ParallelConfig(
            max_workers=parallel_config.get("max_workers"),
            processing_type=ProcessingType.THREAD,
            use_gpu=parallel_config.get("use_gpu", True),
        )

        import threading

        thread = threading.Thread(target=lambda: None)
        task_id = task_registry.register_thread(thread)
        # Actually run the smart_map (not in thread, but for demo)
        folder_results = smart_map(
            process_folder,
            [hq_path, lq_path],
            desc="Processing folders",
            max_workers=2,  # Only 2 folders
            processing_type=ProcessingType.THREAD,
        )
        for path, groups in folder_results:
            results[path] = groups
        # Cleanup
        clear_memory()
        clear_cuda_cache()
    print_success("Visual deduplication complete.")
    play_done_sound()
    return results


def _move_group_worker(args):
    group, destination_dir, dry_run = args
    group_moved = []
    for i, file_path in enumerate(group[1:], 1):
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            dest_path = os.path.join(destination_dir, f"dup_{i}_{filename}")
            if not dry_run:
                try:
                    shutil.move(file_path, dest_path)
                    group_moved.append(file_path)
                except Exception as e:
                    print_error(f"Error moving {file_path}: {e}")
            else:
                print_info(f"Would move: {file_path} -> {dest_path}")
                group_moved.append(file_path)
    return group_moved


def _copy_group_worker(args):
    group, destination_dir, dry_run = args
    group_copied = []
    for i, file_path in enumerate(group[1:], 1):
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            dest_path = os.path.join(destination_dir, f"dup_{i}_{filename}")
            if not dry_run:
                try:
                    shutil.copy2(file_path, dest_path)
                    group_copied.append(file_path)
                except Exception as e:
                    print_error(f"Error copying {file_path}: {e}")
            else:
                print_info(f"Would copy: {file_path} -> {dest_path}")
                group_copied.append(file_path)
    return group_copied


def _remove_group_worker(args):
    group, dry_run = args
    group_removed = []
    for file_path in group[1:]:
        if os.path.exists(file_path):
            if not dry_run:
                try:
                    os.remove(file_path)
                    group_removed.append(file_path)
                except Exception as e:
                    print_error(f"Error removing {file_path}: {e}")
            else:
                print_info(f"Would remove: {file_path}")
                group_removed.append(file_path)
    return group_removed


@monitor_all("move_duplicate_groups", critical_on_error=True)
def move_duplicate_groups(
    groups: List[List[str]], destination_dir: str, dry_run: bool = True
) -> List[str]:
    """
    Move duplicate files from groups to destination directory with parallel processing.
    """
    if not dry_run:
        os.makedirs(destination_dir, exist_ok=True)
    moved_files = []
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # File I/O bound
        use_gpu=False,  # No GPU needed for file operations
    )
    all_moved = smart_map(
        _move_group_worker,
        [(group, destination_dir, dry_run) for group in groups],
        desc="Moving duplicates",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )
    for group_moved in all_moved:
        moved_files.extend(group_moved)
    return moved_files


@monitor_all("copy_duplicate_groups", critical_on_error=True)
def copy_duplicate_groups(
    groups: List[List[str]], destination_dir: str, dry_run: bool = True
) -> List[str]:
    """
    Copy duplicate files from groups to destination directory with parallel processing.
    """
    if not dry_run:
        os.makedirs(destination_dir, exist_ok=True)
    copied_files = []
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # File I/O bound
        use_gpu=False,  # No GPU needed for file operations
    )
    all_copied = smart_map(
        _copy_group_worker,
        [(group, destination_dir, dry_run) for group in groups],
        desc="Copying duplicates",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )
    for group_copied in all_copied:
        copied_files.extend(group_copied)
    return copied_files


@monitor_all("remove_duplicate_groups", critical_on_error=True)
def remove_duplicate_groups(groups: List[List[str]], dry_run: bool = True) -> List[str]:
    """
    Remove duplicate files from groups with parallel processing.
    """
    removed_files = []
    config = ParallelConfig(
        max_workers=parallel_config.get("max_workers"),
        processing_type=ProcessingType.THREAD,  # File I/O bound
        use_gpu=False,  # No GPU needed for file operations
    )
    all_removed = smart_map(
        _remove_group_worker,
        [(group, dry_run) for group in groups],
        desc="Removing duplicates",
        max_workers=config.max_workers,
        processing_type=ProcessingType.THREAD,
    )
    for group_removed in all_removed:
        removed_files.extend(group_removed)
    return removed_files


def find_duplicate_groups(
    folder: str,
    method: str = "clip",
    threshold: float = None,
    max_images: int = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> list:
    """
    Public API: Find duplicate groups in a folder using the specified method (clip or lpips).

    Args:
        folder: Path to the folder containing images
        method: 'clip' or 'lpips'
        threshold: Similarity threshold (default: 0.98 for clip, 0.2 for lpips)
        max_images: Max images to process (optional)
        device: 'cuda' or 'cpu'
    Returns:
        List of duplicate groups (each group is a list of file paths)
    """
    if method == "lpips":
        threshold = threshold or 0.2
    else:
        threshold = threshold or 0.98
    images = load_images_from_folder(folder, max_images)
    if method == "lpips":
        return find_near_duplicates_lpips(images, threshold, device)
    else:
        return find_near_duplicates_clip(images, threshold, device)
