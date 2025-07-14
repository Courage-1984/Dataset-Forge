from dataset_forge.utils.progress_utils import tqdm


def test_tqdm_progress():
    items = [1, 2, 3]
    out = []
    for i in tqdm(items, desc="Testing"):
        out.append(i)
    assert out == items
