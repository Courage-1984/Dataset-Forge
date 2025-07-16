import pytest
from dataset_forge.actions import dataset_health_scoring_actions as dhs
import os
import tempfile
from PIL import Image


def create_dummy_image(path, size=(256, 256), fmt="PNG"):
    with Image.new("RGB", size, color=(255, 0, 0)) as img:
        img.save(path, fmt)


def test_basic_validation_returns_dict(tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()
    for i in range(12):
        create_dummy_image(str(folder / f"img_{i}.png"))
    result = dhs.basic_validation(str(folder))
    assert isinstance(result, dict)
    assert "passed" in result
    assert "issues" in result
    assert result["passed"] is True


def test_unreadable_files_check(tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()
    create_dummy_image(str(folder / "good.png"))
    # Create a corrupt file
    with open(folder / "bad.png", "wb") as f:
        f.write(b"not an image")
    result = dhs.unreadable_files_check(str(folder))
    assert isinstance(result, dict)
    assert "passed" in result
    assert "unreadable" in result
    assert (not result["passed"]) if result["unreadable"] else result["passed"]


def test_image_format_consistency(tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()
    create_dummy_image(str(folder / "a.png"))
    create_dummy_image(str(folder / "b.jpg"), fmt="JPEG")
    result = dhs.image_format_consistency(str(folder))
    assert isinstance(result, dict)
    assert "passed" in result
    assert "formats" in result
    assert set(result["formats"]) == {".png", ".jpg"}
    assert result["passed"] is True
    # Add a third format
    create_dummy_image(str(folder / "c.bmp"), fmt="BMP")
    result2 = dhs.image_format_consistency(str(folder))
    assert result2["passed"] is False


def test_quality_metrics_returns_dict(tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()
    for i in range(5):
        create_dummy_image(str(folder / f"img_{i}.png"), size=(128, 128))
    result = dhs.quality_metrics(str(folder))
    assert isinstance(result, dict)
    assert "avg_resolution" in result
    assert "passed" in result
    assert result["passed"] is False  # avg resolution is low


def test_aspect_ratio_consistency(tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()
    create_dummy_image(str(folder / "a.png"), size=(256, 256))
    create_dummy_image(str(folder / "b.png"), size=(512, 256))
    result = dhs.aspect_ratio_consistency(str(folder))
    assert isinstance(result, dict)
    assert "passed" in result
    assert "ratios" in result
    assert result["passed"] is True
    # Add a third aspect ratio
    create_dummy_image(str(folder / "c.png"), size=(128, 512))
    result2 = dhs.aspect_ratio_consistency(str(folder))
    assert result2["passed"] is True
    # Add a fourth aspect ratio
    create_dummy_image(str(folder / "d.png"), size=(300, 100))
    result3 = dhs.aspect_ratio_consistency(str(folder))
    assert result3["passed"] is False


def test_file_size_outliers(tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()
    for i in range(10):
        create_dummy_image(str(folder / f"img_{i}.png"))
    result = dhs.file_size_outliers(str(folder))
    assert isinstance(result, dict)
    assert "passed" in result
    assert "outliers" in result


def test_score_dataset_single_folder(tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()
    for i in range(12):
        create_dummy_image(str(folder / f"img_{i}.png"))
    result = dhs.score_dataset(str(folder))
    assert isinstance(result, dict)
    assert "health_score" in result
    assert "score" in result["health_score"]
    assert "breakdown" in result["health_score"]
    assert "status" in result["health_score"]


def test_score_dataset_hq_lq_pair(tmp_path):
    parent = tmp_path / "parent"
    hq = parent / "hq"
    lq = parent / "lq"
    hq.mkdir(parents=True)
    lq.mkdir()
    for i in range(10):
        create_dummy_image(str(hq / f"img_{i}.png"))
        create_dummy_image(str(lq / f"img_{i}.png"))
    result = dhs.score_dataset(str(hq), str(lq))
    assert isinstance(result, dict)
    assert "health_score" in result
    assert "score" in result["health_score"]
    assert "breakdown" in result["health_score"]
    assert "status" in result["health_score"]


def test_suggestions_on_failure(tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()
    # No images, should fail basic validation
    result = dhs.score_dataset(str(folder))
    suggestions = result["health_score"]["suggestions"]
    assert suggestions
