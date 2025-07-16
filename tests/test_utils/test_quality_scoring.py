import pytest
from dataset_forge.actions import quality_scoring_actions
import os


@pytest.fixture
def dummy_images(tmp_path):
    img = tmp_path / "a.png"
    img.write_bytes(b"fake")
    return [str(img)]


def test_score_image_with_pyiqa(monkeypatch, dummy_images):
    class DummyModel:
        def __call__(self, path):
            return 0.42

    monkeypatch.setattr(
        quality_scoring_actions,
        "pyiqa",
        type("pyiqa", (), {"create_metric": lambda *a, **kw: DummyModel()})(),
    )
    score = quality_scoring_actions.score_image_with_pyiqa(dummy_images[0])
    assert score == 0.42


def test_score_images_with_pyiqa(monkeypatch, dummy_images, tmp_path):
    class DummyModel:
        def __call__(self, path):
            return 0.5

    monkeypatch.setattr(
        quality_scoring_actions,
        "pyiqa",
        type("pyiqa", (), {"create_metric": lambda *a, **kw: DummyModel()})(),
    )
    # Create a dummy image in a folder
    folder = tmp_path / "imgs"
    folder.mkdir()
    img_path = folder / "a.png"
    img_path.write_bytes(b"fake")
    scores = quality_scoring_actions.score_images_with_pyiqa(str(folder))
    assert isinstance(scores, list)
    assert scores[0][1] == 0.5
