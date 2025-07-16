from dataset_forge.utils.image_ops import get_image_size
from PIL import Image
import tempfile
import os


def test_get_image_size():
    """Test get_image_size returns correct size for a valid image."""
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    try:
        img = Image.new("RGB", (32, 16))
        img.save(tmp.name)
        tmp.close()  # Ensure file is closed before deletion
        size = get_image_size(tmp.name)
        assert size == (32, 16)
    finally:
        os.unlink(tmp.name)


def test_get_image_size_non_image():
    """Test get_image_size raises for a non-image file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
    try:
        tmp.write(b"not an image")
        tmp.close()
        import pytest

        with pytest.raises(Exception):
            get_image_size(tmp.name)
    finally:
        os.unlink(tmp.name)
