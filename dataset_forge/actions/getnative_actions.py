import subprocess
import sys
import tempfile
import os
import platform

from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound


def find_native_resolution(image_path, lq_path=None, extra_args=None):
    """
    Runs getnative on the given image (and optionally LQ image) and prints the output or error.
    """
    from dataset_forge.utils.printing import print_info, print_error
    from dataset_forge.utils.audio_utils import play_error_sound
    import sys

    print_info("[DEBUG] Running getnative (VapourSynth) native resolution detection...")
    cmd = [sys.executable, "-m", "getnative"]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(image_path)
    if lq_path:
        cmd.append(lq_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            print_info(f"getnative output:\n{result.stdout.strip()}")
        elif result.stderr.strip():
            print_error(f"getnative error: {result.stderr.strip()}")
            play_error_sound()
        else:
            print_error("getnative returned no output and no error message.")
            play_error_sound()
    except Exception as e:
        print_error(f"[getnative] Exception: {e}")
        play_error_sound()
    print_info("[DEBUG] getnative workflow finished.")


def find_native_resolution_resdet(image_path, extra_args=None):
    """
    Runs resdet on the given image and prints the output or error.
    Uses WSL if on Windows, otherwise runs natively.
    """
    import shutil
    import subprocess
    from dataset_forge.utils.printing import print_info, print_error
    from dataset_forge.utils.audio_utils import play_error_sound

    print_info(f"[DEBUG] Running resdet on: {image_path}")
    is_windows = platform.system().lower() == "windows"

    def to_wsl_path(win_path):
        # Convert C:/Users/... to /mnt/c/Users/...
        if win_path[1:3] == ":/" or win_path[1:3] == ":\\":
            drive = win_path[0].lower()
            rest = win_path[2:].replace("\\", "/")
            return f"/mnt/{drive}{rest}"
        return win_path

    if is_windows:
        wsl_exe = shutil.which("wsl")
        if not wsl_exe:
            print_error(
                "WSL is not installed or not in PATH. Please install WSL and resdet in your WSL environment."
            )
            play_error_sound()
            return
        wsl_image_path = to_wsl_path(image_path)
        cmd = ["wsl", "resdet"]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(wsl_image_path)
    else:
        resdet_path = shutil.which("resdet")
        if not resdet_path:
            print_error("resdet not found in PATH.")
            play_error_sound()
            return
        cmd = [resdet_path]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(image_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            print_info(f"resdet output:\n{result.stdout.strip()}")
        elif result.stderr.strip():
            print_error(f"resdet error: {result.stderr.strip()}")
            play_error_sound()
        else:
            print_error("resdet returned no output and no error message.")
            play_error_sound()
    except Exception as e:
        print_error(f"[resdet] Exception: {e}")
        play_error_sound()
    print_info("[DEBUG] resdet workflow finished.")
