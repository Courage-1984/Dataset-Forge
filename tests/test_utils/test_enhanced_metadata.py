import pytest
from dataset_forge.actions import enhanced_metadata_actions
import tempfile
import os


@pytest.fixture
def dummy_image(tmp_path):
    path = tmp_path / "test.jpg"
    with open(path, "wb") as f:
        f.write(b"fakejpegdata")
    return str(path)


def test_extract_metadata(monkeypatch, dummy_image, tmp_path):
    def fake_run(cmd, capture_output, check, text):
        class Result:
            stdout = "SourceFile,EXIF:Make\ntest.jpg,Canon\n"
            returncode = 0

        return Result()

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr(
        "pandas.read_csv",
        lambda path: __import__("pandas").DataFrame(
            {"SourceFile": ["test.jpg"], "EXIF:Make": ["Canon"]}
        ),
    )
    out_csv = tmp_path / "meta.csv"
    count = enhanced_metadata_actions.extract_metadata(dummy_image, str(out_csv))
    assert count == 1
    assert os.path.exists(out_csv)


def test_edit_metadata(monkeypatch, dummy_image):
    def fake_run(cmd, capture_output, check, text):
        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr("subprocess.run", fake_run)
    result = enhanced_metadata_actions.edit_metadata(
        dummy_image, {"EXIF:Make": "Nikon"}
    )
    assert result is True


def test_filter_by_metadata(monkeypatch, tmp_path):
    def fake_run(cmd, capture_output, check, text):
        class Result:
            stdout = "SourceFile,EXIF:Make\ntest.jpg,Canon\n"
            returncode = 0

        return Result()

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr(
        "pandas.read_csv",
        lambda path: __import__("pandas").DataFrame(
            {"SourceFile": ["test.jpg"], "EXIF:Make": ["Canon"]}
        ),
    )
    result = enhanced_metadata_actions.filter_by_metadata(
        str(tmp_path), {"EXIF:Make": "Canon"}
    )
    assert result == ["test.jpg"]


def test_anonymize_metadata(monkeypatch, dummy_image, tmp_path):
    def fake_run(cmd, check, capture_output):
        return None

    monkeypatch.setattr("subprocess.run", fake_run)
    out_dir = tmp_path / "anon"
    out_dir.mkdir()
    count = enhanced_metadata_actions.anonymize_metadata(dummy_image, str(out_dir))
    assert count == 1
