import pytest
from dataset_forge.actions import imagededup_actions


def test_imagededup_workflow_find(monkeypatch, tmp_path):
    """Test imagededup_workflow 'find' operation with dummy handler."""

    # Patch ImageDedupHandler to return fixed result
    class DummyHandler:
        def find_duplicates(
            self, image_dir, max_distance_threshold, scores=True, outfile=None
        ):
            return {"a.png": ["b.png"]}

    monkeypatch.setattr(
        imagededup_actions, "ImageDedupHandler", lambda method: DummyHandler()
    )
    monkeypatch.setattr(imagededup_actions, "IMAGEDEDUP_AVAILABLE", True)
    result = imagededup_actions.imagededup_workflow(
        str(tmp_path), operation="find", hash_method="phash"
    )
    assert result["operation"] == "find"
    assert "duplicates" in result
    assert result["duplicates"] == {"a.png": ["b.png"]}
