import os
import shutil
import numpy as np
import torch
import cv2
import pytest
import time
from dataset_forge.actions.umzi_dataset_preprocessing_actions import (
    BestTile,
    ProcessType,
    LaplacianComplexity,
    ImgToEmbedding,
    EmbeddedModel,
    VideoToFrame,
    create_embedd,
    duplicate_list,
    euclid_dist,
    ImgColor,
    ImgFormat,
    read,
)


def make_dummy_image(path, size=(256, 256, 3), color=128):
    img = np.full(size, color, dtype=np.uint8)
    cv2.imwrite(path, img)


@pytest.fixture(scope="function")
def cleanup_test_dirs():
    yield
    # Ensure all OpenCV windows and handles are released
    cv2.destroyAllWindows()
    time.sleep(0.1)
    for folder in ["test_input", "test_output", "test_frames", "test_dedup_input"]:
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


def test_best_tile(cleanup_test_dirs):
    in_folder = "test_input"
    out_folder = "test_output"
    setup_dummy_folder(in_folder, n=3)
    best_tile = BestTile(
        in_folder,
        out_folder,
        tile_size=128,
        process_type=ProcessType.FOR,
        scale=1,
        dynamic_n_tiles=False,
        laplacian_thread=0,
        image_gray=False,
        func=LaplacianComplexity(1),
    )
    best_tile.run()
    assert len(os.listdir(out_folder)) > 0


def test_video_to_frame_extraction(cleanup_test_dirs):
    video_path = "test_video.avi"
    out_folder = "test_frames"
    h, w = 256, 256
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_path, fourcc, 5.0, (w, h))
    # Make each frame a different color to ensure embedding difference
    colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (0, 255, 255),  # Cyan
    ]
    for i in range(5):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:] = colors[i % len(colors)]
        out.write(frame)
    out.release()
    time.sleep(0.1)  # Ensure file is closed
    embedder = ImgToEmbedding(EmbeddedModel.ConvNextS, scale=4, device="cpu")
    v2f = VideoToFrame(embedder, thread=0.001, distance_fn=euclid_dist)
    v2f(video_path, out_folder)
    assert len(os.listdir(out_folder)) > 0


def test_deduplication_workflow(cleanup_test_dirs):
    img_folder = "test_dedup_input"
    setup_dummy_folder(img_folder, n=3)
    embedd_pth = "test_embedd.pth"
    embedder = ImgToEmbedding(EmbeddedModel.ConvNextS, scale=4, device="cpu")
    create_embedd(img_folder, embedd_pth, embedder)
    clusters = duplicate_list(embedd_pth, euclid_dist, threshold=100)
    assert isinstance(clusters, list)


def test_embedding_extraction(cleanup_test_dirs):
    img_path = "test_single.png"
    make_dummy_image(img_path, size=(256, 256, 3))
    embedder = ImgToEmbedding(EmbeddedModel.ConvNextS, scale=4, device="cpu")
    img = read(img_path, ImgColor.RGB, ImgFormat.F32)
    emb = embedder(img)
    assert hasattr(emb, "shape")
