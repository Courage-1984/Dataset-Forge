from dataset_forge.utils.file_utils import is_image_file, get_unique_filename
import tempfile
import os


def test_is_image_file():
    """Test is_image_file with various extensions."""
    assert is_image_file("test.jpg")
    assert is_image_file("test.PNG")
    assert is_image_file("test.jpeg")
    assert is_image_file("test.bmp")
    assert is_image_file("test.tiff")
    assert not is_image_file("test.txt")
    assert not is_image_file("test")


def test_get_unique_filename():
    """Test get_unique_filename returns a unique name if file exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = "image.png"
        path = os.path.join(tmpdir, fname)
        open(path, "w").close()
        unique = get_unique_filename(tmpdir, fname)
        assert unique != fname
        # Create a second file with the unique name and test again
        path2 = os.path.join(tmpdir, unique)
        open(path2, "w").close()
        unique2 = get_unique_filename(tmpdir, fname)
        assert unique2 != fname and unique2 != unique
