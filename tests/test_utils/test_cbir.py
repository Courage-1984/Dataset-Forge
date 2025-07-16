import pytest
from dataset_forge.actions import cbir_actions


class DummyEmbedder:
    def __call__(self, images, *args, **kwargs):
        # Return a fixed embedding for each image
        import numpy as np

        return np.ones((len(images), 4))


def test_cbir_workflow_grouping(monkeypatch, tmp_path):
    """Test cbir_workflow groups images with identical embeddings."""
    # Create dummy images
    img1 = tmp_path / "a.png"
    img2 = tmp_path / "b.png"
    img1.write_bytes(b"fake")
    img2.write_bytes(b"fake")
    # Patch extract_embeddings to return identical embeddings
    monkeypatch.setattr(
        cbir_actions,
        "extract_embeddings",
        lambda imgs, model, device: [[1, 2, 3, 4]] * len(imgs),
    )
    monkeypatch.setattr(
        cbir_actions,
        "load_images_from_folder",
        lambda folder, max_images: [str(img1), str(img2)],
    )
    monkeypatch.setattr(
        cbir_actions,
        "compute_similarity_matrix",
        lambda embs, metric: [[1.0, 1.0], [1.0, 1.0]],
    )
    monkeypatch.setattr(
        cbir_actions,
        "group_duplicates",
        lambda imgs, sim, threshold, metric: [[str(img1), str(img2)]],
    )
    result = cbir_actions.cbir_workflow(
        folder=str(tmp_path),
        model_name="clip",
        threshold=0.98,
        max_images=2,
        metric="cosine",
        operation="find",
    )
    assert isinstance(result, dict)
    assert str(tmp_path) in result
    assert [str(img1), str(img2)] in result[str(tmp_path)]
