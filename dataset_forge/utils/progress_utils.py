from tqdm import tqdm as original_tqdm
from tqdm.contrib.concurrent import process_map as original_process_map
from tqdm.contrib.concurrent import thread_map as original_thread_map
from dataset_forge.utils.audio_utils import play_done_sound
import contextlib
from typing import Callable, List, Any, Optional
from dataset_forge.utils.parallel_utils import (
    parallel_map,
    parallel_submit,
    parallel_image_processing,
    ProcessingType,
    ParallelConfig,
    setup_parallel_environment
)


class AudioTqdm(original_tqdm):
    """Custom tqdm class that plays audio when the progress bar finishes."""

    def __init__(self, *args, **kwargs):
        # Extract audio-related kwargs
        self.play_audio = kwargs.pop("play_audio", True)
        super().__init__(*args, **kwargs)

    def close(self):
        """Override close to play audio when finished."""
        super().close()
        if self.play_audio:
            play_done_sound()

    def __exit__(self, *args, **kwargs):
        """Override __exit__ to play audio when context manager exits."""
        result = super().__exit__(*args, **kwargs)
        if self.play_audio:
            play_done_sound()
        return result


def tqdm(*args, **kwargs):
    """
    Custom tqdm function that plays audio when progress bars finish.

    This is a drop-in replacement for tqdm.tqdm that automatically plays
    the done.wav sound when the progress bar completes.

    Args:
        *args: Arguments to pass to tqdm
        **kwargs: Keyword arguments to pass to tqdm
            play_audio (bool): Whether to play audio when finished (default: True)

    Returns:
        AudioTqdm instance
    """
    return AudioTqdm(*args, **kwargs)


def process_map(*args, **kwargs):
    """
    Enhanced process_map that plays audio when finished and supports advanced configuration.

    This is an enhanced replacement for tqdm.contrib.concurrent.process_map
    that automatically plays the done.wav sound when the process map completes
    and supports advanced parallel processing configuration.
    """
    play_audio = kwargs.pop("play_audio", True)
    max_workers = kwargs.pop("max_workers", None)
    processing_type = kwargs.pop("processing_type", ProcessingType.PROCESS)
    
    # Use new parallel processing if advanced options are specified
    if max_workers is not None or processing_type != ProcessingType.PROCESS:
        config = ParallelConfig(max_workers=max_workers, processing_type=processing_type)
        result = parallel_map(*args, **kwargs, config=config)
    else:
        result = original_process_map(*args, **kwargs)
    
    if play_audio:
        play_done_sound()
    return result


def thread_map(*args, **kwargs):
    """
    Enhanced thread_map that plays audio when finished and supports advanced configuration.

    This is an enhanced replacement for tqdm.contrib.concurrent.thread_map
    that automatically plays the done.wav sound when the thread map completes
    and supports advanced parallel processing configuration.
    """
    play_audio = kwargs.pop("play_audio", True)
    max_workers = kwargs.pop("max_workers", None)
    processing_type = kwargs.pop("processing_type", ProcessingType.THREAD)
    
    # Use new parallel processing if advanced options are specified
    if max_workers is not None or processing_type != ProcessingType.THREAD:
        config = ParallelConfig(max_workers=max_workers, processing_type=processing_type)
        result = parallel_map(*args, **kwargs, config=config)
    else:
        result = original_thread_map(*args, **kwargs)
    
    if play_audio:
        play_done_sound()
    return result


def smart_map(
    func: Callable,
    items: List[Any],
    desc: str = "Processing",
    max_workers: Optional[int] = None,
    processing_type: ProcessingType = ProcessingType.AUTO,
    play_audio: bool = True,
    **kwargs
) -> List[Any]:
    """
    Smart parallel processing that automatically chooses the best method.
    
    Args:
        func: Function to apply to each item
        items: List of items to process
        desc: Description for progress bar
        max_workers: Maximum number of workers
        processing_type: Type of processing to use
        play_audio: Whether to play audio when finished
        **kwargs: Additional arguments to pass to func
        
    Returns:
        List of results
    """
    config = ParallelConfig(max_workers=max_workers, processing_type=processing_type)
    result = parallel_map(func, items, desc, config=config, **kwargs)
    
    if play_audio:
        play_done_sound()
    return result


def image_map(
    func: Callable,
    image_paths: List[str],
    desc: str = "Processing Images",
    max_workers: Optional[int] = None,
    play_audio: bool = True,
    **kwargs
) -> List[Any]:
    """
    Specialized parallel processing for image operations.
    
    Args:
        func: Function to apply to each image
        image_paths: List of image file paths
        desc: Description for progress bar
        max_workers: Maximum number of workers
        play_audio: Whether to play audio when finished
        **kwargs: Additional arguments to pass to func
        
    Returns:
        List of results
    """
    result = parallel_image_processing(func, image_paths, desc, max_workers, **kwargs)
    
    if play_audio:
        play_done_sound()
    return result


def batch_map(
    func: Callable,
    items: List[Any],
    batch_size: int,
    desc: str = "Processing Batches",
    max_workers: Optional[int] = None,
    processing_type: ProcessingType = ProcessingType.AUTO,
    play_audio: bool = True,
    **kwargs
) -> List[Any]:
    """
    Parallel processing with batching for memory efficiency.
    
    Args:
        func: Function to apply to each batch
        items: List of items to process
        batch_size: Size of each batch
        desc: Description for progress bar
        max_workers: Maximum number of workers
        processing_type: Type of processing to use
        play_audio: Whether to play audio when finished
        **kwargs: Additional arguments to pass to func
        
    Returns:
        List of results
    """
    from dataset_forge.utils.parallel_utils import BatchProcessor, ParallelConfig
    
    config = ParallelConfig(max_workers=max_workers, processing_type=processing_type)
    processor = BatchProcessor(config)
    result = processor.process_in_batches(func, items, batch_size, desc, **kwargs)
    
    if play_audio:
        play_done_sound()
    return result


@contextlib.contextmanager
def audio_progress_bar(*args, **kwargs):
    """
    Context manager for progress bars that automatically plays audio when finished.

    Usage:
        with audio_progress_bar(total=100, desc="Processing") as pbar:
            for i in range(100):
                pbar.update(1)
                # do work
        # Audio will play automatically when exiting the context
    """
    play_audio = kwargs.pop("play_audio", True)
    pbar = AudioTqdm(*args, **kwargs)
    try:
        yield pbar
    finally:
        pbar.close()
        if play_audio:
            play_done_sound()


# Export the original tqdm functions as well for cases where audio is not wanted
from tqdm import tqdm as original_tqdm
from tqdm.contrib.concurrent import process_map as original_process_map
from tqdm.contrib.concurrent import thread_map as original_thread_map
