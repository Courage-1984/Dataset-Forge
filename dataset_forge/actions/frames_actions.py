import os
import torch
import gc
import cv2
import numpy as np
from dataset_forge.utils.progress_utils import tqdm
from enum import Enum
import torch.nn.functional as F
import timm
import torchvision.transforms as T
import torch.nn as nn
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import (
    clear_memory,
    clear_cuda_cache,
    auto_cleanup,
    to_device_safe,
)
from dataset_forge.utils.printing import (
    print_header,
    print_section,
    print_info,
    print_success,
    print_error,
    print_prompt,
)
from dataset_forge.utils.audio_utils import play_done_sound
import threading
from torch.cuda.amp import autocast


class LayerNorm(torch.nn.Module):
    def __init__(self, normalized_shape, eps=1e-6, data_format="channels_last"):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.ones(normalized_shape))
        self.bias = torch.nn.Parameter(torch.zeros(normalized_shape))
        self.eps = eps
        self.data_format = data_format
        if self.data_format not in ["channels_last", "channels_first"]:
            raise NotImplementedError
        self.normalized_shape = (normalized_shape,)

    def forward(self, x):
        if self.data_format == "channels_last":
            return torch.nn.functional.layer_norm(
                x, self.normalized_shape, self.weight, self.bias, self.eps
            )
        elif self.data_format == "channels_first":
            u = x.mean(1, keepdim=True)
            s = (x - u).pow(2).mean(1, keepdim=True)
            x = (x - u) / torch.sqrt(s + self.eps)
            x = self.weight[:, None, None] * x + self.bias[:, None, None]
            return x


# --- Extract Frames Utility ---
# Import centralized memory management


def release_memory():
    """Legacy function for backward compatibility."""
    clear_memory()


@monitor_all("extract_frames_menu", critical_on_error=True)
def extract_frames_menu():
    print_header("🎬 Extract Frames from Video (Batch/Multi-Model)")
    video_path = input("Enter path to video file: ").strip()
    if not os.path.isfile(video_path):
        print_error("Video file does not exist.")
        print_prompt("Press Enter to return to the menu...")
        input()
        return
    base_out_dir = input("Enter base output directory for frames: ").strip()
    if not base_out_dir:
        print_error("Output directory required.")
        print_prompt("Press Enter to return to the menu...")
        input()
        return
    os.makedirs(base_out_dir, exist_ok=True)

    # Model selection (multi-select)
    model_options = [
        ("ConvNextS", EmbeddedModel.ConvNextS),
        ("ConvNextL", EmbeddedModel.ConvNextL),
        ("VITS", EmbeddedModel.VITS),
        ("VITB", EmbeddedModel.VITB),
        ("VITL", EmbeddedModel.VITL),
        ("VITG", EmbeddedModel.VITG),
    ]
    print_section("Select embedding model(s) (comma separated, e.g. 1,3):")
    for i, (name, _) in enumerate(model_options):
        print_info(f"  {i+1}. {name}")
    while True:
        model_choices = input("Model(s) [1-6, default 1]: ").strip() or "1"
        try:
            model_idxs = [
                int(x.strip()) - 1 for x in model_choices.split(",") if x.strip()
            ]
            if all(0 <= idx < len(model_options) for idx in model_idxs):
                break
        except Exception:
            pass
        print_error("Invalid input. Please enter valid model numbers, e.g. 1,3.")
    selected_models = [model_options[idx] for idx in model_idxs]

    # Distance function selection (multi-select, same count as models or one for all)
    dist_options = [
        ("euclid", "Euclidean Distance"),
        ("cosine", "Cosine Distance"),
    ]
    print_section(
        "Select distance function(s) for each model (comma separated, e.g. 1,2):"
    )
    for i, (_, desc) in enumerate(dist_options):
        print_info(f"  {i+1}. {desc}")
    while True:
        dist_choices = input("Distance(s) [1-2, default 1]: ").strip() or "1"
        try:
            dist_idxs = [
                int(x.strip()) - 1 for x in dist_choices.split(",") if x.strip()
            ]
            if len(dist_idxs) == 1:
                dist_idxs = dist_idxs * len(selected_models)
            if len(dist_idxs) == len(selected_models) and all(
                0 <= idx < len(dist_options) for idx in dist_idxs
            ):
                break
        except Exception:
            pass
        print_error(
            "Invalid input. Please enter valid distance numbers, e.g. 1,2 or just 1."
        )
    selected_dists = [dist_options[idx][0] for idx in dist_idxs]

    # Batch size
    batch_size = input("Batch size (default 5000): ").strip()
    try:
        batch_size = int(batch_size) if batch_size else 5000
    except Exception:
        print_error("Invalid batch size, using 5000.")
        batch_size = 5000

    # Max frames per batch
    max_len = input("Max frames to extract per batch (default 1000): ").strip()
    try:
        max_len = int(max_len) if max_len else 1000
    except Exception:
        print_error("Invalid max, using 1000.")
        max_len = 1000

    # Thresholds (per model)
    thresholds = []
    for i, (model_name, _) in enumerate(selected_models):
        dist = selected_dists[i]
        default_threshold = 2.3 if dist == "euclid" else 0.3
        t = input(
            f"Enter threshold for {model_name} ({dist}) (default {default_threshold}): "
        ).strip()
        try:
            t = float(t) if t else default_threshold
        except Exception:
            print_error(f"Invalid threshold, using default {default_threshold}.")
            t = default_threshold
        thresholds.append(t)

    # Scale (per model, or one for all)
    scale = input("Enter scale factor (default 4): ").strip()
    try:
        scale = int(scale) if scale else 4
    except Exception:
        print_error("Invalid scale, using 4.")
        scale = 4

    # Device
    device = input("Device (cuda/cpu, default cuda): ").strip() or "cuda"

    # Get total frames
    import cv2

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Distance function mapping
    def get_dist_fn(name):
        if name == "euclid":
            return euclid_dist
        else:
            return cosine_dist

    # For each model+distance, process in batches
    for i, ((model_name, model_enum), dist_name) in enumerate(
        zip(selected_models, selected_dists)
    ):
        print_section(f"Processing with {model_name} ({dist_name})...")
        out_dir = os.path.join(base_out_dir, f"frames_{model_name}_{dist_name}")
        os.makedirs(out_dir, exist_ok=True)
        embedder = ImgToEmbedding(
            model=model_enum, amp=True, scale=scale, device=device
        )
        dist_fn = get_dist_fn(dist_name)
        video_to_frame = VideoToFrame(
            embedder,
            thread=thresholds[i],
            distance_fn=dist_fn,
            max_len=max_len,
        )
        for start in range(0, total_frames, batch_size):
            end = min(start + batch_size, total_frames)
            # Check how many frames from this batch already exist
            existing = [
                fname
                for fname in os.listdir(out_dir)
                if fname.startswith("frame_")
                and fname.endswith(".png")
                and start <= int(fname[len("frame_") : -len(".png")]) < end
            ]
            if len(existing) >= max_len:
                print_info(f"Skipping frames {start} to {end} (already processed)")
                continue
            print_info(f"Processing frames {start} to {end} ({model_name})")
            video_to_frame(video_path, out_dir, start_frame=start, end_frame=end)

    print_success("All selected models processed.")
    clear_memory()
    clear_cuda_cache()
    play_done_sound()
    print_prompt("Press Enter to return to the menu...")
    input()


# --- END Extract Frames Utility ---


class EmbeddedModel(Enum):
    ConvNextS = 0
    ConvNextL = 1
    VITS = 2
    VITB = 3
    VITL = 4
    VITG = 5


def euclid_dist(emb1, emb2):
    return torch.cdist(emb1.float(), emb2.float()).item()


def cosine_dist(emb1, emb2):
    emb1_norm = F.normalize(emb1.float(), dim=-1)
    emb2_norm = F.normalize(emb2.float(), dim=-1)
    return 1 - F.cosine_similarity(emb1_norm, emb2_norm).item()


def enum_to_model(enum):
    if enum == EmbeddedModel.ConvNextS:
        model = timm.create_model("convnext_small_384_in22ft1k", pretrained=True)
        model.eval()
        preprocess = T.Compose(
            [
                T.ToTensor(),
                T.Resize((384, 384)),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )
        return model, preprocess
    elif enum == EmbeddedModel.ConvNextL:
        model = timm.create_model("convnext_large_384_in22ft1k", pretrained=True)
        model.eval()
        preprocess = T.Compose(
            [
                T.ToTensor(),
                T.Resize((384, 384)),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )
        return model, preprocess
    elif enum == EmbeddedModel.VITS:
        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14")
        if isinstance(model, nn.Module):
            model = model.eval()
        return model, None
    elif enum == EmbeddedModel.VITB:
        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vitb14")
        if isinstance(model, nn.Module):
            model = model.eval()
        return model, None
    elif enum == EmbeddedModel.VITL:
        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vitl14")
        if isinstance(model, nn.Module):
            model = model.eval()
        return model, None
    elif enum == EmbeddedModel.VITG:
        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vitg14")
        if isinstance(model, nn.Module):
            model = model.eval()
        return model, None
    else:
        raise ValueError(f"Unknown EmbeddedModel: {enum}")


class ImgToEmbedding:
    def __init__(
        self,
        model: EmbeddedModel = EmbeddedModel.ConvNextS,
        amp: bool = True,
        scale: int = 4,
        device: str = "cuda",
    ):
        self.device = torch.device(device)
        self.scale = scale
        self.amp = amp
        model_obj, preprocess = enum_to_model(model)
        if isinstance(model_obj, nn.Module):
            self.model = to_device_safe(model_obj, str(self.device))
        else:
            self.model = model_obj
        self.preprocess = preprocess
        self.vit = model in [
            EmbeddedModel.VITS,
            EmbeddedModel.VITB,
            EmbeddedModel.VITL,
            EmbeddedModel.VITG,
        ]

    @staticmethod
    def check_img_size(x):
        b, c, h, w = x.shape
        mod_pad_h = (14 - h % 14) % 14
        mod_pad_w = (14 - w % 14) % 14
        return F.pad(x, (0, mod_pad_w, 0, mod_pad_h), "reflect")

    def img_to_tensor(self, x):
        if self.preprocess is not None:
            # Use model's preprocess pipeline
            tensor = self.preprocess(T.ToPILImage()(x.astype("uint8"))).unsqueeze(0)
            return to_device_safe(tensor, str(self.device))
        if self.vit:
            tensor = self.check_img_size(
                torch.tensor(x.transpose((2, 0, 1)), dtype=torch.float32)[None, :, :, :]
            )
            return to_device_safe(tensor, str(self.device))
        tensor = torch.tensor(x.transpose((2, 0, 1)), dtype=torch.float32)[
            None, :, :, :
        ]
        return to_device_safe(tensor, str(self.device))

    @torch.inference_mode()
    @auto_cleanup
    def __call__(self, x):
        # Optionally add resizing logic here if needed
        with autocast(enabled=self.amp, dtype=torch.float16):
            x = self.img_to_tensor(x)
            if not callable(self.model):
                raise RuntimeError(
                    "Loaded model is not callable. Check model loading logic."
                )
            return self.model(x)


class VideoToFrame:
    def __init__(
        self,
        embedder: ImgToEmbedding,
        thread: float = 1.5,
        distance_fn=euclid_dist,
        max_len=1000,
    ):
        self.embedder = embedder
        self.thread = thread
        self.distance_fn = distance_fn
        self.max_len = max_len

    def __call__(self, video_path, out_path, start_frame=0, end_frame=None):
        os.makedirs(out_path, exist_ok=True)
        capture = cv2.VideoCapture(video_path)
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if end_frame is None or end_frame > total_frames:
            end_frame = total_frames
        capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        ref = None
        n = start_frame
        n_s = 0
        # Get already saved frames for resume
        existing_frames = set()
        for fname in os.listdir(out_path):
            if fname.startswith("frame_") and fname.endswith(".png"):
                try:
                    idx = int(fname[len("frame_") : -len(".png")])
                    existing_frames.add(idx)
                except ValueError:
                    continue
        with tqdm(total=end_frame - start_frame) as pbar:
            while capture.isOpened() and n < end_frame:
                ret, frame = capture.read()
                if n_s > self.max_len:
                    break
                if not ret:
                    break
                if n in existing_frames:
                    n += 1
                    pbar.update(1)
                    continue
                if ref is None:
                    rgb_normalized = (
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32)
                        / 255.0
                    )
                    ref = self.embedder(rgb_normalized)
                    cv2.imwrite(os.path.join(out_path, f"frame_{n}.png"), frame)
                    n_s += 1
                else:
                    rgb_normalized = (
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32)
                        / 255.0
                    )
                    temp_embedd = self.embedder(rgb_normalized)
                    if self.distance_fn(ref, temp_embedd) > self.thread:
                        cv2.imwrite(os.path.join(out_path, f"frame_{n}.png"), frame)
                        ref = temp_embedd
                        n_s += 1
                n += 1
                pbar.update(1)
        capture.release()
        print(f"\nDone. Extracted up to {n_s} frames to {out_path}.")
        release_memory()
