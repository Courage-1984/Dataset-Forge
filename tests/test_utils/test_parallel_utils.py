from dataset_forge.utils.progress_utils import smart_map

try:
    from dataset_forge.utils.parallel_utils import image_processor, batch_processor
except ImportError:
    image_processor = None
    batch_processor = None


def double(x, **kwargs):
    """Double a value, ignore extra kwargs."""
    return x * 2


def double_batch(batch, **kwargs):
    """Double a batch of values."""
    return [x * 2 for x in batch]


def fail_on_three(x, **kwargs):
    if x == 3:
        raise ValueError("fail")
    return x


def test_smart_map_basic():
    """Test smart_map with a simple function."""
    result = smart_map(double, [1, 2, 3], desc="Test", play_audio=False)
    assert result == [2, 4, 6]


def test_image_map():
    """Test image_processor.process_images with a simple function."""
    if image_processor is None:
        import pytest

        pytest.skip("image_processor not available")
    items = [1, 2, 3]
    result = image_processor.process_images(
        double, items, desc="Test", play_audio=False
    )
    assert result == [2, 4, 6]


def test_batch_map():
    """Test batch_processor.process_in_batches with a batch function."""
    if batch_processor is None:
        import pytest

        pytest.skip("batch_processor not available")
    items = [1, 2, 3, 4]
    result = batch_processor.process_in_batches(
        double_batch, items, batch_size=2, desc="Test"
    )
    assert result == [2, 4, 6, 8]


def test_smart_map_error():
    """Test smart_map propagates errors."""
    import pytest

    with pytest.raises(ValueError):
        smart_map(fail_on_three, [1, 2, 3], desc="Test", play_audio=False)
