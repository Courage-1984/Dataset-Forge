from dataset_forge.utils.progress_utils import smart_map


def double(x):
    return x * 2


def test_smart_map_basic():
    result = smart_map(double, [1, 2, 3], desc="Test", play_audio=False)
    assert result == [2, 4, 6]
