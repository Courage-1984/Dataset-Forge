from tqdm import tqdm as original_tqdm
from tqdm.contrib.concurrent import process_map as original_process_map
from tqdm.contrib.concurrent import thread_map as original_thread_map
from dataset_forge.utils.audio_utils import play_done_sound
import contextlib


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
    Custom process_map that plays audio when finished.

    This is a drop-in replacement for tqdm.contrib.concurrent.process_map
    that automatically plays the done.wav sound when the process map completes.
    """
    play_audio = kwargs.pop("play_audio", True)
    result = original_process_map(*args, **kwargs)
    if play_audio:
        play_done_sound()
    return result


def thread_map(*args, **kwargs):
    """
    Custom thread_map that plays audio when finished.

    This is a drop-in replacement for tqdm.contrib.concurrent.thread_map
    that automatically plays the done.wav sound when the thread map completes.
    """
    play_audio = kwargs.pop("play_audio", True)
    result = original_thread_map(*args, **kwargs)
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
