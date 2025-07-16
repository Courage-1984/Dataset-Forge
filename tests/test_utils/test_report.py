import pytest
from dataset_forge.actions import report_actions
from PIL import Image
import numpy as np
import os


def make_dummy_image(path, size=(8, 8)):
    arr = np.random.randint(0, 255, size + (3,), dtype=np.uint8)
    Image.fromarray(arr).save(path)


def test_generate_rich_report(tmp_path, monkeypatch):
    """Test generate_rich_report creates output report file."""
    folder = tmp_path / "images"
    folder.mkdir()
    img = folder / "a.png"
    make_dummy_image(img)
    # Patch compute_quality_scores and plot_quality_histograms to avoid heavy computation
    monkeypatch.setattr(
        report_actions, "compute_quality_scores", lambda path, max_images=100: [0.5]
    )
    monkeypatch.setattr(
        report_actions,
        "plot_quality_histograms",
        lambda scores, outdir, prefix: {
            "dummy_metric": os.path.join(outdir, "hist.png")
        },
    )
    report_actions.generate_rich_report(
        single_folder_path=str(folder),
        output_path=str(tmp_path / "report.html"),
        format="html",
        sample_count=1,
        max_quality_images=1,
    )
    assert (tmp_path / "report.html").exists()
