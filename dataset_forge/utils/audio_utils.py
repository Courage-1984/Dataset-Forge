import os
import platform
import subprocess
import threading
from pathlib import Path
from dataset_forge.menus.session_state import user_preferences
import sys

# Check if we're in a test environment
IS_TEST_ENVIRONMENT = "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ

# Try to import audio libraries, with fallbacks
try:
    import pygame

    PYGAME_AVAILABLE = True and not IS_TEST_ENVIRONMENT  # Disable pygame in tests
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import winsound

    WINSOUND_AVAILABLE = True and not IS_TEST_ENVIRONMENT  # Disable winsound in tests
except ImportError:
    WINSOUND_AVAILABLE = False

# try:
#     from playsound import playsound

#     PLAYSOUND_AVAILABLE = True
# except ImportError:
#     PLAYSOUND_AVAILABLE = False


class AudioPlayer:
    """Audio player utility that can play the done.wav sound using various methods."""

    def __init__(self, audio_file_path=None):
        """
        Initialize the audio player.

        Args:
            audio_file_path: Path to the audio file. If None, uses default done.wav
        """
        if audio_file_path is None:
            # Get the path to the assets/done.wav file relative to the project root
            current_dir = Path(__file__).parent  # utils directory
            project_root = current_dir.parent.parent  # project root
            audio_file_path = project_root / "assets" / "done.wav"

        self.audio_file_path = Path(audio_file_path)
        self._pygame_initialized = False
        self._pygame_lock = threading.Lock()  # Thread safety lock for pygame operations

    def _init_pygame(self):
        """Initialize pygame mixer if not already done."""
        if not self._pygame_initialized and PYGAME_AVAILABLE:
            with self._pygame_lock:  # Ensure thread safety
                if not self._pygame_initialized:  # Double-check pattern
                    try:
                        pygame.mixer.init()
                        self._pygame_initialized = True
                    except Exception:
                        pass

    def play_audio(self, block=False):
        """
        Play the audio file using the best available method.

        Args:
            block: If True, block until audio finishes. If False, play asynchronously.
        """
        # Skip audio in test environment to prevent crashes
        if IS_TEST_ENVIRONMENT:
            return
            
        if not self.audio_file_path.exists():
            print(f"Warning: Audio file not found at {self.audio_file_path}")
            return

        if block:
            self._play_audio_sync()
        else:
            # Play asynchronously in a separate thread
            thread = threading.Thread(target=self._play_audio_sync, daemon=True)
            thread.start()

    def _play_audio_sync(self):
        """Play audio synchronously using the best available method."""
        # Skip audio in test environment to prevent crashes
        if IS_TEST_ENVIRONMENT:
            return
            
        system = platform.system().lower()

        # Try pygame first (cross-platform) - with thread safety
        if PYGAME_AVAILABLE:
            try:
                with self._pygame_lock:  # Ensure thread safety for pygame operations
                    self._init_pygame()
                    if self._pygame_initialized:
                        pygame.mixer.music.load(str(self.audio_file_path))
                        pygame.mixer.music.play()
                        # Wait for the audio to finish
                        while pygame.mixer.music.get_busy():
                            pygame.time.wait(100)
                        return
            except Exception as e:
                print(f"Pygame audio failed: {e}")

        # Try winsound on Windows
        if system == "windows" and WINSOUND_AVAILABLE:
            try:
                winsound.PlaySound(str(self.audio_file_path), winsound.SND_FILENAME)
                return
            except Exception as e:
                print(f"Winsound failed: {e}")

        # # Try playsound
        # if PLAYSOUND_AVAILABLE:
        #     try:
        #         playsound(str(self.audio_file_path), block=True)
        #         return
        #     except Exception as e:
        #         print(f"Playsound failed: {e}")

        # Try system-specific commands
        try:
            self._play_with_system_command(system)
            return
        except Exception as e:
            print(f"System command failed: {e}")

        # If all else fails, just print a message
        print(
            "Audio playback not available. Consider installing pygame: pip install pygame"
        )

    def _play_with_system_command(self, system):
        """Play audio using system-specific commands."""
        audio_path = str(self.audio_file_path)

        if system == "windows":
            # Try using PowerShell
            cmd = [
                "powershell",
                "-c",
                f"(New-Object Media.SoundPlayer '{audio_path}').PlaySync()",
            ]
        elif system == "darwin":  # macOS
            cmd = ["afplay", audio_path]
        elif system == "linux":
            # Try various Linux audio players
            for player in ["aplay", "paplay", "ffplay"]:
                try:
                    subprocess.run(
                        [player, audio_path], check=True, capture_output=True
                    )
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            raise Exception("No suitable audio player found on Linux")
        else:
            raise Exception(f"Unsupported operating system: {system}")

        subprocess.run(cmd, check=True, capture_output=True)


# Global audio player instance with thread safety
_audio_player = None
_audio_player_lock = threading.Lock()


def get_audio_player():
    """Get the global audio player instance."""
    global _audio_player
    if _audio_player is None:
        with _audio_player_lock:  # Ensure thread safety for singleton creation
            if _audio_player is None:  # Double-check pattern
                _audio_player = AudioPlayer()
    return _audio_player


def play_done_sound(block=False):
    """
    Play the done sound asynchronously.

    Args:
        block: If True, block until audio finishes. If False, play asynchronously.
    """
    # Skip audio in test environment to prevent crashes
    if IS_TEST_ENVIRONMENT:
        return
        
    player = get_audio_player()
    player.play_audio(block=block)


def play_error_sound(block=False):
    """
    Play the error sound asynchronously.

    Args:
        block: If True, block until audio finishes. If False, play asynchronously.
    """
    # Skip audio in test environment to prevent crashes
    if IS_TEST_ENVIRONMENT:
        return
        
    player = get_audio_player()
    # Override the audio file path for error sound
    error_audio_path = Path(__file__).parent.parent.parent / "assets" / "error.mp3"
    if error_audio_path.exists():
        temp_player = AudioPlayer(error_audio_path)
        temp_player.play_audio(block=block)
    else:
        # Fallback to done sound if error sound not found
        player.play_audio(block=block)


def play_startup_sound(block=False):
    """
    Play the startup sound asynchronously.

    Args:
        block: If True, block until audio finishes. If False, play asynchronously.
    """
    # Skip audio in test environment to prevent crashes
    if IS_TEST_ENVIRONMENT:
        return
        
    player = get_audio_player()
    # Override the audio file path for startup sound
    startup_audio_path = Path(__file__).parent.parent.parent / "assets" / "startup.mp3"
    if startup_audio_path.exists():
        temp_player = AudioPlayer(startup_audio_path)
        temp_player.play_audio(block=block)
    else:
        # Fallback to done sound if startup sound not found
        player.play_audio(block=block)


def play_shutdown_sound(block=False):
    """
    Play the shutdown sound asynchronously.

    Args:
        block: If True, block until audio finishes. If False, play asynchronously.
    """
    # Skip audio in test environment to prevent crashes
    if IS_TEST_ENVIRONMENT:
        return
        
    player = get_audio_player()
    # Override the audio file path for shutdown sound
    shutdown_audio_path = Path(__file__).parent.parent.parent / "assets" / "shutdown.mp3"
    if shutdown_audio_path.exists():
        temp_player = AudioPlayer(shutdown_audio_path)
        temp_player.play_audio(block=block)
    else:
        # Fallback to done sound if shutdown sound not found
        player.play_audio(block=block)
