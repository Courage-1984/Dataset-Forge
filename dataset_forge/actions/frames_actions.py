import os
import gc
from dataset_forge.utils.progress_utils import tqdm
from enum import Enum
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

# Use lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    torch,
    torch_nn as nn,
    torch_nn_functional as F,
    torch_cuda_amp,
    cv2,
    numpy_as_np as np,
    timm,
    torchvision_transforms as T,
)

# Import autocast from torch.cuda.amp
autocast = torch_cuda_amp.autocast


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
                selected_models = [model_options[idx][1] for idx in model_idxs]
                break
            else:
                print_error("Invalid model selection. Please try again.")
        except ValueError:
            print_error("Invalid input. Please enter comma-separated numbers.")

    # Distance function selection
    distance_options = [
        ("Euclidean", euclid_dist),
        ("Cosine", cosine_dist),
    ]
    print_section("Select distance function:")
    for i, (name, _) in enumerate(distance_options):
        print_info(f"  {i+1}. {name}")
    while True:
        dist_choice = input("Distance function [1-2, default 1]: ").strip() or "1"
        try:
            dist_idx = int(dist_choice) - 1
            if 0 <= dist_idx < len(distance_options):
                distance_fn = distance_options[dist_idx][1]
                break
            else:
                print_error("Invalid distance function selection.")
        except ValueError:
            print_error("Invalid input. Please enter a number.")

    # Parameters
    thread = float(input("Thread threshold [default 1.5]: ").strip() or "1.5")
    max_len = int(input("Maximum frames [default 1000]: ").strip() or "1000")

    # Process video
    try:
        for model in selected_models:
            print_section(f"Processing with {model.name} model...")
            model_dir = os.path.join(base_out_dir, model.name.lower())
            os.makedirs(model_dir, exist_ok=True)

            # Initialize embedder
            embedder = ImgToEmbedding(model=model, device="cuda")

            # Initialize video processor
            video_processor = VideoToFrame(
                embedder=embedder,
                thread=thread,
                distance_fn=distance_fn,
                max_len=max_len,
            )

            # Process video
            video_processor(video_path, model_dir)

            print_success(f"✅ Completed processing with {model.name} model")

        print_success("🎉 All models completed successfully!")
        play_done_sound()

    except Exception as e:
        print_error(f"❌ Error during processing: {e}")
        play_done_sound()
    finally:
        clear_memory()
        clear_cuda_cache()


def get_dist_fn(name):
    """Get distance function by name."""
    if name.lower() == "euclidean":
        return euclid_dist
    elif name.lower() == "cosine":
        return cosine_dist
    else:
        raise ValueError(f"Unknown distance function: {name}")


class EmbeddedModel(Enum):
    ConvNextS = 0
    ConvNextL = 1
    VITS = 2
    VITB = 3
    VITL = 4
    VITG = 5


def euclid_dist(emb1, emb2):
    """Calculate Euclidean distance between embeddings."""
    return torch.cdist(emb1, emb2, p=2)


def cosine_dist(emb1, emb2):
    """Calculate cosine distance between embeddings."""
    # Normalize embeddings
    emb1_norm = F.normalize(emb1, p=2, dim=1)
    emb2_norm = F.normalize(emb2, p=2, dim=1)
    # Calculate cosine similarity and convert to distance
    similarity = torch.mm(emb1_norm, emb2_norm.t())
    return 1 - similarity


# Cache for models to avoid reloading
_model_cache = {}


def enum_to_model(enum):
    """Convert enum to model name for timm."""
    model_mapping = {
        EmbeddedModel.ConvNextS: "convnext_small",
        EmbeddedModel.ConvNextL: "convnext_large",
        EmbeddedModel.VITS: "vit_small_patch16_224",
        EmbeddedModel.VITB: "vit_base_patch16_224",
        EmbeddedModel.VITL: "vit_large_patch16_224",
        EmbeddedModel.VITG: "vit_giant_patch14_224",
    }
    return model_mapping[enum]


class ImgToEmbedding:
    def __init__(
        self,
        model: EmbeddedModel = EmbeddedModel.ConvNextS,
        amp: bool = True,
        scale: int = 4,
        device: str = "cuda",
    ):
        self.model = model
        self.amp = amp
        self.scale = scale
        self.device = device

        # Get model name
        model_name = enum_to_model(model)

        # Load model from cache or create new
        if model_name in _model_cache:
            self.net = _model_cache[model_name]
        else:
            self.net = timm.create_model(model_name, pretrained=True, num_classes=0)
            self.net = self.net.to(device)
            self.net.eval()
            _model_cache[model_name] = self.net

        # Setup transforms
        self.transform = T.Compose(
            [
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    @staticmethod
    def check_img_size(x):
        """Check if image size is valid."""
        if x.shape[0] < 10 or x.shape[1] < 10:
            return False
        return True

    def img_to_tensor(self, x):
        """Convert image to tensor."""
        if isinstance(x, str):
            # Load image from path
            img = cv2.imread(x)
            if img is None:
                return None
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img = x

        if not self.check_img_size(img):
            return None

        # Apply transforms
        img_tensor = self.transform(img).unsqueeze(0).to(self.device)
        return img_tensor

    @torch.no_grad()
    @auto_cleanup
    def __call__(self, x):
        # Optionally add resizing logic here if needed
        img_tensor = self.img_to_tensor(x)
        if img_tensor is None:
            return None

        with autocast(enabled=self.amp):
            with torch.no_grad():
                embedding = self.net(img_tensor)

        return embedding


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
        """Extract frames from video based on embedding similarity."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        print_info(f"Total frames: {total_frames}, FPS: {fps}")

        if end_frame is None:
            end_frame = total_frames

        # Extract frames
        frame_count = 0
        saved_frames = []
        embeddings = []

        with tqdm(total=end_frame - start_frame, desc="Processing frames") as pbar:
            for frame_idx in range(start_frame, end_frame):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()

                if not ret:
                    break

                # Get embedding for current frame
                embedding = self.embedder(frame)
                if embedding is None:
                    continue

                # Check if frame should be saved
                should_save = True
                if embeddings:
                    # Calculate distance to previous embeddings
                    distances = self.distance_fn(embedding, torch.stack(embeddings))
                    min_distance = torch.min(distances).item()

                    if min_distance < self.thread:
                        should_save = False

                if should_save:
                    # Save frame
                    frame_path = os.path.join(out_path, f"frame_{frame_count:06d}.jpg")
                    cv2.imwrite(frame_path, frame)
                    saved_frames.append(frame_path)
                    embeddings.append(embedding.squeeze(0))
                    frame_count += 1

                    if frame_count >= self.max_len:
                        break

                pbar.update(1)

        cap.release()

        print_success(f"Saved {len(saved_frames)} frames to {out_path}")
        return saved_frames
