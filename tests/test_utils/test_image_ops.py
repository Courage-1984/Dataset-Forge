from dataset_forge.utils.image_ops import get_image_size
from PIL import Image
import tempfile
import os


def test_get_image_size():
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    try:
        img = Image.new("RGB", (32, 16))
        img.save(tmp.name)
        tmp.close()  # Ensure file is closed before deletion
        size = get_image_size(tmp.name)
        assert size == (32, 16)
    finally:
        os.unlink(tmp.name)
