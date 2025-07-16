import pytest
from dataset_forge.actions import sanitize_images_actions
import os


@pytest.fixture
def dummy_image(tmp_path):
    path = tmp_path / "test.png"
    with open(path, "wb") as f:
        f.write(b"fakepngdata")
    return str(path)


def test_remove_metadata(monkeypatch, dummy_image, tmp_path):
    def fake_run(cmd, check, capture_output):
        return None

    monkeypatch.setattr("subprocess.run", fake_run)
    out_path = tmp_path / "out.png"
    result = sanitize_images_actions.remove_metadata(dummy_image, str(out_path))
    assert result is True


def test_convert_to_png(monkeypatch, dummy_image, tmp_path):
    class DummyImg:
        def save(self, path, format=None):
            assert format == "PNG"

    class DummyOpen:
        def __enter__(self):
            return DummyImg()

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr("PIL.Image.open", lambda path: DummyOpen())
    out_path = tmp_path / "out.png"
    result = sanitize_images_actions.convert_to_png(dummy_image, str(out_path))
    assert result is True


def test_remove_alpha(monkeypatch, dummy_image, tmp_path):
    class DummyImg:
        mode = "RGBA"
        size = (10, 10)

        def split(self):
            from PIL import Image

            return [Image.new("L", (10, 10))] * 4

        def save(self, path, format=None):
            assert format == "PNG"

        def paste(self, img, box=None, **kwargs):
            pass  # No-op for test

    class DummyOpen:
        def __enter__(self):
            return DummyImg()

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr("PIL.Image.open", lambda path: DummyOpen())
    monkeypatch.setattr("PIL.Image.new", lambda mode, size, color=None: DummyImg())
    out_path = tmp_path / "out.png"
    result = sanitize_images_actions.remove_alpha(dummy_image, str(out_path))
    assert result is True


def test_run_steghide_check(monkeypatch, dummy_image):
    def fake_run(cmd, capture_output, check, text):
        class Result:
            stdout = "No hidden data found"

        return Result()

    monkeypatch.setattr("subprocess.run", fake_run)
    result = sanitize_images_actions.run_steghide_check(dummy_image)
    assert result["result"] == "No hidden data found"


def test_run_zsteg_check(monkeypatch, dummy_image):
    def fake_run(cmd, capture_output, check, text):
        class Result:
            stdout = "No stego data found"

        return Result()

    monkeypatch.setattr("subprocess.run", fake_run)
    result = sanitize_images_actions.run_zsteg_check(dummy_image)
    assert result["result"] == "No stego data found"
