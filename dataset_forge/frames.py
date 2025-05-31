import os
import torch
import gc


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
def release_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def extract_frames_menu():
    print("\n--- Extract Frames from Video ---")
    video_path = input("Enter path to video file: ").strip()
    if not os.path.isfile(video_path):
        print("Error: Video file does not exist.")
        return
    out_dir = input("Enter output directory for frames: ").strip()
    if not out_dir:
        print("Error: Output directory required.")
        return
    os.makedirs(out_dir, exist_ok=True)

    # Model selection
    model_options = [
        ("ConvNextS", 0),
        ("ConvNextL", 1),
        ("VITS", 2),
        ("VITB", 3),
        ("VITL", 4),
        ("VITG", 5),
    ]
    print("Select embedding model:")
    for i, (name, _) in enumerate(model_options):
        print(f"  {i+1}. {name}")
    while True:
        model_choice = input("Model [1-6, default 1]: ").strip() or "1"
        if model_choice in [str(i + 1) for i in range(6)]:
            model_idx = int(model_choice) - 1
            break
        print("Invalid choice.")
    model_name = model_options[model_idx][0]

    # Distance function
    dist_options = [
        ("euclid", "Euclidean Distance"),
        ("cosine", "Cosine Distance"),
    ]
    print("Select distance function:")
    for i, (_, desc) in enumerate(dist_options):
        print(f"  {i+1}. {desc}")
    while True:
        dist_choice = input("Distance [1-2, default 1]: ").strip() or "1"
        if dist_choice in ["1", "2"]:
            dist_idx = int(dist_choice) - 1
            break
        print("Invalid choice.")
    dist_name = dist_options[dist_idx][0]

    # Threshold
    default_threshold = 2.3 if dist_name == "euclid" else 0.3
    threshold = input(f"Enter threshold (default {default_threshold}): ").strip()
    try:
        threshold = float(threshold) if threshold else default_threshold
    except Exception:
        print("Invalid threshold, using default.")
        threshold = default_threshold

    # Scale
    scale = input("Enter scale factor (default 4): ").strip()
    try:
        scale = int(scale) if scale else 4
    except Exception:
        print("Invalid scale, using 4.")
        scale = 4

    # Max frames
    max_len = input("Max frames to extract (default 1000): ").strip()
    try:
        max_len = int(max_len) if max_len else 1000
    except Exception:
        print("Invalid max, using 1000.")
        max_len = 1000

    # Device
    device = input("Device (cuda/cpu, default cuda): ").strip() or "cuda"

    # --- Inline enum, model, and distance logic ---
    class EmbeddedModel:
        ConvNextS = 0
        ConvNextL = 1
        VITS = 2
        VITB = 3
        VITL = 4
        VITG = 5

    def enum_to_model(enum):
        import torch

        if enum == EmbeddedModel.ConvNextS:
            # convnext_small
            state = torch.hub.load_state_dict_from_url(
                url="https://github.com/umzi2/Dataset_Preprocessing/releases/download/SPARK_model_duplication/convnextS_1kpretrained_official_style.pth",
                map_location="cpu",
                weights_only=True,
            )
            from timm.layers import trunc_normal_, DropPath

            class Block(torch.nn.Module):
                def __init__(self, dim, drop_path=0.0, layer_scale_init_value=1e-6):
                    super().__init__()
                    self.dwconv = torch.nn.Conv2d(
                        dim, dim, kernel_size=7, padding=3, groups=dim
                    )
                    self.norm = LayerNorm(dim, eps=1e-6, data_format="channels_last")
                    self.pwconv1 = torch.nn.Linear(dim, 4 * dim)
                    self.act = torch.nn.GELU()
                    self.pwconv2 = torch.nn.Linear(4 * dim, dim)
                    self.gamma = (
                        torch.nn.Parameter(
                            layer_scale_init_value * torch.ones((dim)),
                            requires_grad=True,
                        )
                        if layer_scale_init_value > 0
                        else None
                    )
                    self.drop_path = (
                        DropPath(drop_path) if drop_path > 0.0 else torch.nn.Identity()
                    )

                def forward(self, x):
                    input = x
                    x = self.dwconv(x)
                    x = x.permute(0, 2, 3, 1)
                    x = self.norm(x)
                    x = self.pwconv1(x)
                    x = self.act(x)
                    x = self.pwconv2(x)
                    if self.gamma is not None:
                        x = self.gamma * x
                    x = x.permute(0, 3, 1, 2)
                    x = input + self.drop_path(x)
                    return x

            class ConvNeXt(torch.nn.Module):
                def __init__(
                    self, in_chans=3, depths=[3, 3, 27, 3], dims=[96, 192, 384, 768]
                ):
                    super().__init__()
                    self.downsample_layers = torch.nn.ModuleList()
                    stem = torch.nn.Sequential(
                        torch.nn.Conv2d(in_chans, dims[0], kernel_size=4, stride=4),
                        LayerNorm(dims[0], eps=1e-6, data_format="channels_first"),
                    )
                    self.downsample_layers.append(stem)
                    for i in range(3):
                        downsample_layer = torch.nn.Sequential(
                            LayerNorm(dims[i], eps=1e-6, data_format="channels_first"),
                            torch.nn.Conv2d(
                                dims[i], dims[i + 1], kernel_size=2, stride=2
                            ),
                        )
                        self.downsample_layers.append(downsample_layer)
                    self.stages = torch.nn.ModuleList()
                    for i in range(4):
                        stage = torch.nn.Sequential(
                            *[Block(dim=dims[i]) for _ in range(depths[i])]
                        )
                        self.stages.append(stage)

                def forward(self, x):
                    for i in range(4):
                        x = self.downsample_layers[i](x)
                        x = self.stages[i](x)
                    return x.mean([-2, -1])

            model = ConvNeXt()
            model.load_state_dict(state)
            return model.eval()
        elif enum == EmbeddedModel.ConvNextL:
            state = torch.hub.load_state_dict_from_url(
                url="https://github.com/umzi2/Dataset_Preprocessing/releases/download/SPARK_model_duplication/convnextL_384_1kpretrained_official_style.pth",
                map_location="cpu",
                weights_only=True,
            )
            # ... (same as above, with different dims)
            # For brevity, use ConvNextS logic but with dims=[192, 384, 768, 1536]
            from timm.layers import trunc_normal_, DropPath

            class Block(torch.nn.Module):
                def __init__(self, dim, drop_path=0.0, layer_scale_init_value=1e-6):
                    super().__init__()
                    self.dwconv = torch.nn.Conv2d(
                        dim, dim, kernel_size=7, padding=3, groups=dim
                    )
                    self.norm = LayerNorm(dim, eps=1e-6, data_format="channels_first")
                    self.pwconv1 = torch.nn.Linear(dim, 4 * dim)
                    self.act = torch.nn.GELU()
                    self.pwconv2 = torch.nn.Linear(4 * dim, dim)
                    self.gamma = (
                        torch.nn.Parameter(
                            layer_scale_init_value * torch.ones((dim)),
                            requires_grad=True,
                        )
                        if layer_scale_init_value > 0
                        else None
                    )
                    self.drop_path = (
                        DropPath(drop_path) if drop_path > 0.0 else torch.nn.Identity()
                    )

                def forward(self, x):
                    input = x
                    x = self.dwconv(x)
                    x = x.permute(0, 2, 3, 1)
                    x = self.norm(x)
                    x = self.pwconv1(x)
                    x = self.act(x)
                    x = self.pwconv2(x)
                    if self.gamma is not None:
                        x = self.gamma * x
                    x = x.permute(0, 3, 1, 2)
                    x = input + self.drop_path(x)
                    return x

            class ConvNeXt(torch.nn.Module):
                def __init__(
                    self, in_chans=3, depths=[3, 3, 27, 3], dims=[192, 384, 768, 1536]
                ):
                    super().__init__()
                    self.downsample_layers = torch.nn.ModuleList()
                    stem = torch.nn.Sequential(
                        torch.nn.Conv2d(in_chans, dims[0], kernel_size=4, stride=4),
                        LayerNorm(dims[0], eps=1e-6, data_format="channels_first"),
                    )
                    self.downsample_layers.append(stem)
                    for i in range(3):
                        downsample_layer = torch.nn.Sequential(
                            LayerNorm(dims[i], eps=1e-6, data_format="channels_first"),
                            torch.nn.Conv2d(
                                dims[i], dims[i + 1], kernel_size=2, stride=2
                            ),
                        )
                        self.downsample_layers.append(downsample_layer)
                    self.stages = torch.nn.ModuleList()
                    for i in range(4):
                        stage = torch.nn.Sequential(
                            *[Block(dim=dims[i]) for _ in range(depths[i])]
                        )
                        self.stages.append(stage)

                def forward(self, x):
                    for i in range(4):
                        x = self.downsample_layers[i](x)
                        x = self.stages[i](x)
                    return x.mean([-2, -1])

            model = ConvNeXt(dims=[192, 384, 768, 1536])
            model.load_state_dict(state)
            return model.eval()
        elif enum == EmbeddedModel.VITS:
            return (
                __import__("torch")
                .hub.load("facebookresearch/dinov2", "dinov2_vits14")
                .eval()
            )
        elif enum == EmbeddedModel.VITB:
            return (
                __import__("torch")
                .hub.load("facebookresearch/dinov2", "dinov2_vitb14")
                .eval()
            )
        elif enum == EmbeddedModel.VITL:
            return (
                __import__("torch")
                .hub.load("facebookresearch/dinov2", "dinov2_vitl14")
                .eval()
            )
        elif enum == EmbeddedModel.VITG:
            return (
                __import__("torch")
                .hub.load("facebookresearch/dinov2", "dinov2_vitg14")
                .eval()
            )

    def cosine_dist(emb1, emb2):
        import torch.nn.functional as F

        emb1_norm = F.normalize(emb1, dim=-1)
        emb2_norm = F.normalize(emb2, dim=-1)
        return 1 - F.cosine_similarity(emb1_norm, emb2_norm).item()

    def euclid_dist(emb1, emb2):
        import torch

        return torch.cdist(emb1, emb2).item()

    # --- Embedding class ---
    class ImgToEmbedding:
        def __init__(
            self, model=EmbeddedModel.ConvNextS, amp=True, scale=4, device="cuda"
        ):
            import torch

            self.device = torch.device(device)
            self.scale = scale
            self.amp = amp
            self.model = enum_to_model(model).to(self.device)
            self.vit = model in [
                EmbeddedModel.VITS,
                EmbeddedModel.VITB,
                EmbeddedModel.VITL,
                EmbeddedModel.VITG,
            ]

        @staticmethod
        def check_img_size(x):
            import torch.nn.functional as F

            b, c, h, w = x.shape
            mod_pad_h = (14 - h % 14) % 14
            mod_pad_w = (14 - w % 14) % 14
            return F.pad(x, (0, mod_pad_w, 0, mod_pad_h), "reflect")

        def img_to_tensor(self, x):
            import torch

            if self.vit:
                return self.check_img_size(
                    torch.tensor(x.transpose((2, 0, 1)))[None, :, :, :].to(self.device)
                )
            return torch.tensor(x.transpose((2, 0, 1)))[None, :, :, :].to(self.device)

        def __call__(self, x):
            import torch

            if self.scale > 1:
                h, w = x.shape[:2]
                # No resize, just use as is (or implement if chainner_ext is available)
            with torch.amp.autocast(self.device.__str__(), torch.float16, self.amp):
                x = self.img_to_tensor(x)
                return self.model(x)

    # Select model enum
    model_enum = [
        EmbeddedModel.ConvNextS,
        EmbeddedModel.ConvNextL,
        EmbeddedModel.VITS,
        EmbeddedModel.VITB,
        EmbeddedModel.VITL,
        EmbeddedModel.VITG,
    ][model_idx]
    embedder = ImgToEmbedding(model=model_enum, amp=True, scale=scale, device=device)
    dist_fn = euclid_dist if dist_name == "euclid" else cosine_dist

    # --- Video to frames logic ---
    import cv2
    import numpy as np
    from tqdm import tqdm

    capture = cv2.VideoCapture(video_path)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    ref = None
    n = 0
    n_s = 0
    with tqdm(total=total_frames) as pbar:
        while capture.isOpened():
            ret, frame = capture.read()
            if n_s > max_len:
                break
            if not ret:
                break
            if ref is None:
                ref = embedder(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                )
            else:
                temp_embedd = embedder(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                )
                if dist_fn(ref, temp_embedd) > threshold:
                    cv2.imwrite(os.path.join(out_dir, f"frame_{n}.png"), frame)
                    ref = temp_embedd
                    n_s += 1
            n += 1
            pbar.update(1)
    capture.release()
    print(f"\nDone. Extracted up to {n_s} frames to {out_dir}.")
    release_memory()


# --- END Extract Frames Utility ---
