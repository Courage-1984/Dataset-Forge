from dataset_forge.utils.progress_utils import tqdm, AudioTqdm
import time


def test_tqdm_progress():
    """Test that tqdm iterates and outputs progress."""
    items = [1, 2, 3]
    out = []
    for i in tqdm(items, desc="Testing"):
        out.append(i)
    assert out == items


def test_audio_tqdm(monkeypatch):
    """Test that AudioTqdm calls play_done_sound (mocked)."""
    called = {}
    monkeypatch.setattr(
        "dataset_forge.utils.progress_utils.play_done_sound",
        lambda: called.setdefault("yes", True),
    )
    with AudioTqdm(range(2), desc="AudioTest", play_audio=True) as bar:
        for _ in bar:
            time.sleep(0.01)
    assert called.get("yes")
