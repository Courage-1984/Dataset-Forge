import subprocess
import sys

from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound


def find_native_resolution(image_path, extra_args=None):
    """
    Runs getnative on the given image and returns the output.
    """
    cmd = [sys.executable, "-m", "getnative"]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(image_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running getnative: {e.stderr or e.stdout}"
