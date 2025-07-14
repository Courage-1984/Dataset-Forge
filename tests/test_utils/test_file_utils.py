from dataset_forge.utils.file_utils import is_image_file, get_unique_filename
import tempfile
import os


def test_is_image_file():
    assert is_image_file("test.jpg")
    assert is_image_file("test.PNG")
    assert not is_image_file("test.txt")


def test_get_unique_filename():
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = "image.png"
        path = os.path.join(tmpdir, fname)
        open(path, "w").close()
        unique = get_unique_filename(tmpdir, fname)
        assert unique != fname
