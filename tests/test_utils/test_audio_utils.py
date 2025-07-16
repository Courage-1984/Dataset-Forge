import pytest
from dataset_forge.utils.audio_utils import AudioPlayer
from pathlib import Path


def test_audio_player_init():
    """Test AudioPlayer initializes with default and custom path."""
    player = AudioPlayer()
    assert player.audio_file_path.exists() or isinstance(player.audio_file_path, Path)
    custom = AudioPlayer(audio_file_path="assets/done.wav")
    assert str(custom.audio_file_path).endswith("done.wav")


def test_audio_player_play_audio(monkeypatch):
    """Test play_audio calls _play_audio_sync (mocked)."""
    player = AudioPlayer()
    called = {}
    monkeypatch.setattr(
        player, "_play_audio_sync", lambda: called.setdefault("yes", True)
    )
    player.play_audio(block=True)
    assert called.get("yes")


def test_audio_player_missing_file():
    """Test play_audio with missing file does not raise."""
    player = AudioPlayer(audio_file_path="not_a_real_file.wav")
    # Should not raise
    player.play_audio(block=True)
