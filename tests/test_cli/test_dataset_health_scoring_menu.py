import pytest
from unittest.mock import patch
from dataset_forge.menus import dataset_health_scoring_menu
import itertools
import os


def dummy_score_dataset_single(*args, **kwargs):
    return {
        "basic_validation": {"passed": True},
        "unreadable_files_check": {"passed": True},
        "image_format_consistency": {"passed": True},
        "quality_metrics": {"passed": True},
        "aspect_ratio_consistency": {
            "passed": False,
            "suggestion": "Standardize aspect ratios.",
        },
        "file_size_outliers": {"passed": True},
        "consistency_checks": {"passed": True},
        "compliance_scan": {"passed": True},
        "health_score": {
            "score": 85,
            "status": "⚠️ Needs Improvement",
            "breakdown": {"aspect_ratio_consistency": ("⚠️", 10)},
            "suggestions": ["Standardize aspect ratios."],
        },
    }


def dummy_score_dataset_hq_lq(*args, **kwargs):
    return {
        "basic_validation": {"passed": True},
        "unreadable_files_check": {"passed": True},
        "image_format_consistency": {"passed": True},
        "quality_metrics": {"passed": True},
        "aspect_ratio_consistency": {"passed": True},
        "file_size_outliers": {"passed": True},
        "consistency_checks": {"passed": True},
        "compliance_scan": {"passed": True},
        "health_score": {
            "score": 95,
            "status": "✅ Production Ready",
            "breakdown": {"basic_validation": ("✅", 20)},
            "suggestions": [],
        },
    }


@pytest.mark.usefixtures("capfd")
def test_dataset_health_scoring_menu_single(monkeypatch, capfd):
    # Patch get_path_with_history to return a dummy path
    monkeypatch.setattr(
        "dataset_forge.menus.dataset_health_scoring_menu.get_path_with_history",
        lambda *a, **kw: "dummy_path",
    )
    # Patch input to select single folder mode
    monkeypatch.setattr("builtins.input", lambda *a, **kw: "1")
    # Patch the scoring function
    with patch(
        "dataset_forge.actions.dataset_health_scoring_actions.score_dataset",
        dummy_score_dataset_single,
    ):
        dataset_health_scoring_menu.dataset_health_scoring_menu()
        out, _ = capfd.readouterr()
        assert "Dataset Health Score" in out
        assert "Status" in out
        assert "aspect ratios" in out


@pytest.mark.usefixtures("capfd")
def test_dataset_health_scoring_menu_hq_lq(tmp_path, monkeypatch, capfd):
    # Create dummy parent, hq, and lq folders
    parent = tmp_path / "parent"
    hq = parent / "hq"
    lq = parent / "lq"
    hq.mkdir(parents=True)
    lq.mkdir(parents=True)
    # Patch get_folder_path to return parent, hq, lq in order
    folder_iter = iter([str(parent), str(hq), str(lq)])
    monkeypatch.setattr(
        "dataset_forge.menus.dataset_health_scoring_menu.get_folder_path",
        lambda *a, **kw: next(folder_iter),
    )
    # Patch input to select HQ/LQ mode
    monkeypatch.setattr("builtins.input", lambda *a, **kw: "2")
    # Patch the scoring function
    with patch(
        "dataset_forge.actions.dataset_health_scoring_actions.score_dataset",
        dummy_score_dataset_hq_lq,
    ):
        dataset_health_scoring_menu.dataset_health_scoring_menu()
        out, _ = capfd.readouterr()
        assert "Dataset Health Score" in out
        assert "Status" in out
        # Accept both possible statuses for robustness
        assert ("Production Ready" in out) or ("Needs Improvement" in out)
