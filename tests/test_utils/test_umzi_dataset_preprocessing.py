import os
import shutil
import numpy as np
import cv2
import pytest
import time
from unittest.mock import patch
from dataset_forge.actions import umzi_dataset_preprocessing_actions as umzi


def make_dummy_image(path, size=(256, 256, 3), color=128):
    img = np.full(size, color, dtype=np.uint8)
    cv2.imwrite(path, img)


@pytest.fixture(scope="function")
def cleanup_test_dirs():
    yield
    cv2.destroyAllWindows()
    time.sleep(0.1)
    for folder in [
        "test_input",
        "test_output",
        "test_frames",
        "test_dedup_input",
        "test_duplicates",
    ]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    for f in ["test_video.avi", "test_embedd.pth", "test_single.png"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except PermissionError:
                time.sleep(0.2)
                os.remove(f)


def setup_dummy_folder(folder, n=3):
    os.makedirs(folder, exist_ok=True)
    for i in range(n):
        make_dummy_image(os.path.join(folder, f"img_{i}.png"), color=128 + i * 10)


def test_best_tile_extraction_action(cleanup_test_dirs):
    in_folder = "test_input"
    out_folder = "test_output"
    setup_dummy_folder(in_folder, n=3)
    print("DEBUG: Starting best_tile_extraction_action test")
    umzi.best_tile_extraction_action(
        in_folder=in_folder,
        out_folder=out_folder,
        tile_size=128,
        process_type="FOR",
        scale=1,
        dynamic_n_tiles=True,
        threshold=0.0,
        image_gray=True,
        func_type="Laplacian",
        median_blur=5,
    )
    assert os.path.exists(out_folder)
    assert len(os.listdir(out_folder)) > 0


def test_video_frame_extraction_action(cleanup_test_dirs):
    video_path = "test_video.avi"
    out_folder = "test_frames"
    h, w = 256, 256
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_path, fourcc, 5.0, (w, h))
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]
    for i in range(5):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:] = colors[i % len(colors)]
        out.write(frame)
    out.release()
    time.sleep(0.1)
    umzi.video_frame_extraction_action(
        video_path=video_path,
        out_folder=out_folder,
        embed_model="ConvNextS",
        amp=True,
        scale=4,
        threshold=0.4,
        dist_fn_name="euclid",
    )
    assert os.path.exists(out_folder)
    assert len(os.listdir(out_folder)) > 0


def test_duplicate_image_detection_action(cleanup_test_dirs):
    in_folder = "test_dedup_input"
    out_folder = "test_duplicates"
    setup_dummy_folder(in_folder, n=5)
    umzi.duplicate_image_detection_action(
        in_folder=in_folder,
        out_folder=out_folder,
        embed_model="ConvNextS",
        amp=True,
        scale=4,
        threshold=1.5,
        dist_fn_name="euclid",
    )
    assert os.path.exists(out_folder)
    assert len(os.listdir(out_folder)) > 0


def test_iqa_filtering_action(cleanup_test_dirs):
    in_folder = "test_input"
    out_folder = "test_output"
    setup_dummy_folder(in_folder, n=3)
    umzi.iqa_filtering_action(
        in_folder=in_folder,
        out_folder=out_folder,
        iqa_model="HIPERIQA",
        batch_size=8,
        threshold=0.5,
        median_threshold=0.5,
    )
    assert os.path.exists(out_folder)
    assert len(os.listdir(out_folder)) > 0
