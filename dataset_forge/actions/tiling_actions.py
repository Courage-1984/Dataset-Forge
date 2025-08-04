import os
from dataset_forge.utils.file_utils import is_image_file
from dataset_forge.utils.input_utils import (
    get_file_operation_choice,
    get_destination_path,
)
from dataset_forge.utils.progress_utils import tqdm, process_map, thread_map
import random
from enum import Enum
from abc import ABC, abstractmethod
import time
from typing import Tuple, Any

# Import centralized memory management
from dataset_forge.utils.memory_utils import (
    clear_memory,
    clear_cuda_cache,
    safe_cuda_operation,
    memory_context,
    auto_cleanup,
    to_device_safe,
)
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
    print_section,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.audio_utils import play_done_sound

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    cv2,
    numpy_as_np as np,
    PIL_Image as Image,
    PIL_ImageEnhance as ImageEnhance,
    PIL_ImageFont as ImageFont,
    PIL_ImageDraw as ImageDraw,
    torch,
    torch_nn as nn,
    torch_nn_functional as F,
    torchvision,
    imageio,
)


# src/enum.py
class ProcessType(Enum):
    PROCESS = 0
    THREAD = 1
    FOR = 2


# src/scripts/utils/complexity/object.py
class BaseComplexity(ABC):
    @staticmethod
    @abstractmethod
    def type() -> str: ...

    @abstractmethod
    def get_tile_comp_score(
        self, image, complexity, y: int, x: int, tile_size: int
    ) -> Tuple[Any, Any, float]: ...

    @abstractmethod
    def __call__(self, img: np.ndarray): ...


# src/scripts/archs/ICNet.py
class slam(nn.Module):
    def __init__(self, spatial_dim):
        super(slam, self).__init__()
        self.spatial_dim = spatial_dim
        self.linear = nn.Sequential(
            nn.Linear(spatial_dim**2, 512), nn.ReLU(), nn.Linear(512, 1), nn.Sigmoid()
        )

    def forward(self, feature):
        n, c, h, w = feature.shape
        if h != self.spatial_dim:
            x = F.interpolate(
                feature,
                size=(self.spatial_dim, self.spatial_dim),
                mode="bilinear",
                align_corners=True,
            )
        else:
            x = feature

        x = x.view(n, c, -1)
        x = self.linear(x)
        x = x.unsqueeze(dim=3)
        out = x.expand_as(feature) * feature

        return out


class to_map(nn.Module):
    def __init__(self, channels):
        super(to_map, self).__init__()
        self.to_map = nn.Sequential(
            nn.Conv2d(in_channels=channels, out_channels=1, kernel_size=1, stride=1),
            nn.Sigmoid(),
        )

    def forward(self, feature):
        return self.to_map(feature)


class conv_bn_relu(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, padding=1, stride=1):
        super(conv_bn_relu, self).__init__()
        self.conv = nn.Conv2d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
        )
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        return x


class up_conv_bn_relu(nn.Module):
    def __init__(
        self, scale, in_channels, out_channels=64, kernal_size=1, padding=0, stride=1
    ):
        super(up_conv_bn_relu, self).__init__()
        self.upSample = (
            nn.Upsample(scale_factor=scale, mode="bilinear", align_corners=True)
            if scale != 1
            else nn.Identity()
        )
        self.conv = nn.Conv2d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernal_size,
            stride=stride,
            padding=padding,
        )
        self.bn = nn.BatchNorm2d(num_features=out_channels)
        self.act = nn.ReLU()

    def forward(self, x):
        x = self.upSample(x)
        x = self.conv(x)
        x = self.bn(x)
        x = self.act(x)
        return x


class ICNet(nn.Module):
    def __init__(self, is_pretrain=True, size1=512, size2=256):
        super(ICNet, self).__init__()
        resnet18Pretrained1 = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1)
        resnet18Pretrained2 = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1)

        self.size1 = size1
        self.size2 = size2

        ## detail branch
        self.b1_1 = nn.Sequential(*list(resnet18Pretrained1.children())[:5])
        self.b1_1_slam = slam(32)

        self.b1_2 = list(resnet18Pretrained1.children())[5]
        self.b1_2_slam = slam(32)

        ## context branch
        self.b2_1 = nn.Sequential(*list(resnet18Pretrained2.children())[:5])
        self.b2_1_slam = slam(32)

        self.b2_2 = list(resnet18Pretrained2.children())[5]
        self.b2_2_slam = slam(32)

        self.b2_3 = list(resnet18Pretrained2.children())[6]
        self.b2_3_slam = slam(16)

        self.b2_4 = list(resnet18Pretrained2.children())[7]
        self.b2_4_slam = slam(8)

        self.up1 = up_conv_bn_relu(1, in_channels=128, out_channels=256)
        self.up2 = up_conv_bn_relu(8, in_channels=512, out_channels=256)

        ## map prediction head
        self.to_map_f = conv_bn_relu(256 * 2, 256 * 2)
        self.to_map_f_slam = slam(32)
        self.to_map = to_map(256 * 2)

        ## score prediction head
        self.to_score_f = conv_bn_relu(256 * 2, 256 * 2)
        self.to_score_f_slam = slam(32)
        self.head = nn.Sequential(
            nn.Linear(256 * 2, 512), nn.ReLU(), nn.Linear(512, 1), nn.Sigmoid()
        )
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

    def check_img_size(self, x):
        b, c, h, w = x.shape
        scaled_size = 64
        mod_pad_h = (scaled_size - h % scaled_size) % scaled_size
        mod_pad_w = (scaled_size - w % scaled_size) % scaled_size
        return F.pad(x, (0, mod_pad_w, 0, mod_pad_h), "reflect")

    def get_onlu_score(self, x1):
        x_cat = self.body_forward(x1)
        return self.score(x_cat)

    def score(self, x_cat):
        score_feature = self.to_score_f_slam(self.to_score_f(x_cat))
        score_feature = self.avgpool(score_feature)
        score_feature = score_feature.squeeze()
        score = self.head(score_feature)
        score = score.squeeze()
        return score

    def body_forward(self, x1):
        b, c, h, w = x1.shape
        x1 = F.pad(
            x1, pad=(32, 32, 32, 32), mode="reflect"
        )  # (left, right, top, bottom)
        x1 = self.check_img_size(x1)
        x2 = F.interpolate(x1, scale_factor=0.5, mode="bilinear", align_corners=True)

        x1 = self.b1_2_slam(self.b1_2(self.b1_1_slam(self.b1_1(x1))))
        x2 = self.b2_2_slam(self.b2_2(self.b2_1_slam(self.b2_1(x2))))
        x2 = self.b2_4_slam(self.b2_4(self.b2_3_slam(self.b2_3(x2))))

        x1 = self.up1(x1)
        x2 = self.up2(x2)
        return torch.cat((x1, x2), dim=1)[:, :, 4:-4, 4:-4][:, :, : h // 8, : w // 8]

    def forward(self, x1):
        x_cat = self.body_forward(x1)
        cly_map = self.to_map(self.to_map_f_slam(self.to_map_f(x_cat)))
        return x_cat, cly_map


def ic9600():
    state = torch.hub.load_state_dict_from_url(
        url="https://github.com/umzi2/Dataset_Preprocessing/releases/download/IC9600_duplicate/ic9600.pth",
        map_location="cpu",
        weights_only=True,
    )
    model = ICNet().eval()
    model.load_state_dict(state)
    return model


# src/scripts/utils/complexity/ic9600.py
class IC9600Complexity(BaseComplexity):
    def __init__(
        self, device: str = "cuda", max_retries: int = 3, retry_delay: float = 1.0
    ):
        super().__init__()
        self.device = torch.device(device)
        self.arch = ic9600().to(self.device)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    @staticmethod
    def image_to_tensor(image: np.ndarray):
        if not isinstance(image, np.ndarray):
            raise ValueError("Input is not a numpy array")
        if image.ndim not in (2, 3):
            raise ValueError(f"Input image must be 2D or 3D, got shape {image.shape}")
        if image.dtype != np.float32:
            image = image.astype(np.float32)
        image = image.squeeze()
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        return torch.tensor(image.transpose((2, 0, 1)))[None, :, :, :]

    @staticmethod
    def type():
        return "IC9600"

    def _clear_cuda_cache(self):
        """Clear CUDA cache to prevent memory issues"""
        clear_cuda_cache()

    def _safe_cuda_operation(self, operation, *args, **kwargs):
        """Execute CUDA operation with retry logic"""
        return safe_cuda_operation(
            operation, self.max_retries, self.retry_delay, *args, **kwargs
        )

    @torch.inference_mode()
    @auto_cleanup
    def get_tile_comp_score(
        self, image, complexity, y, x, tile_size
    ) -> Tuple[Any, Any, float]:
        try:
            img_tile = image[
                y * 8 : y * 8 + tile_size,
                x * 8 : x * 8 + tile_size,
            ]

            def score_operation():
                return self.arch.score(
                    complexity[1][
                        :,
                        :,
                        y : y + tile_size // 8,
                        x : x + tile_size // 8,
                    ]
                )

            score_tensor = self._safe_cuda_operation(score_operation)
            if score_tensor is None:
                raise RuntimeError(
                    "_safe_cuda_operation returned None for score_tensor"
                )
            score = score_tensor.detach().cpu().item()

            complexity[0][
                y : y + tile_size // 8,
                x : x + tile_size // 8,
            ] = -1.0
            return img_tile, complexity, score
        except Exception as e:
            print_error(f"Error in get_tile_comp_score: {e}")
            raise

    @torch.inference_mode()
    @auto_cleanup
    def __call__(self, img):
        try:
            img_tensor = to_device_safe(self.image_to_tensor(img), self.device)

            def forward_operation():
                return self.arch(img_tensor)

            result = self._safe_cuda_operation(forward_operation)
            if result is None:
                raise RuntimeError("_safe_cuda_operation returned None")
            x_cat, cly_map = result
            return cly_map.detach().cpu().squeeze().numpy(), x_cat
        except Exception as e:
            print_error(f"Error in IC9600Complexity.__call__: {e}")
            raise


# src/scripts/utils/complexity/laplacian.py
class LaplacianComplexity(BaseComplexity):
    def __init__(self, median_blur: int = 1):
        super().__init__()
        self.median_blur = median_blur if median_blur % 2 == 1 else median_blur + 1

    @staticmethod
    def image_to_gray(image: np.ndarray):
        image = image.squeeze()
        if image.ndim == 3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return image

    def median_laplacian(self, image):
        if self.median_blur <= 1:
            return image
        # The following check is to handle float images correctly, as medianBlur expects uint8
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        image = cv2.medianBlur(image, self.median_blur)

        if image.dtype != np.float32:
            image = image.astype(np.float32) / 255.0

        return image

    @staticmethod
    def type():
        return "Laplacian"

    @staticmethod
    def get_tile_comp_score(
        image, complexity, y, x, tile_size
    ) -> Tuple[Any, Any, float]:
        img_tile = image[
            y : y + tile_size,
            x : x + tile_size,
        ]
        score = np.mean(
            complexity[
                y : y + tile_size,
                x : x + tile_size,
            ]
        )
        complexity[
            y : y + tile_size,
            x : x + tile_size,
        ] = -1.0
        return img_tile, complexity, score

    def __call__(self, img):
        img = self.image_to_gray(img)
        img = self.median_laplacian(img)

        return np.abs(cv2.Laplacian(img, cv2.CV_64F))


# Dummy implementations for pepeline and chainner_ext as they are not standard libraries
# You will need to replace these with your actual implementation or install them if they are packages.


class ImgColor(Enum):
    GRAY = 0
    RGB = 1


class ImgFormat(Enum):
    F32 = np.float32
    U8 = np.uint8


def read(path, color=ImgColor.RGB, img_format=ImgFormat.F32):
    img = cv2.imread(
        path, cv2.IMREAD_COLOR if color == ImgColor.RGB else cv2.IMREAD_GRAYSCALE
    )
    if color == ImgColor.RGB:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if img.dtype == np.uint8 and img_format == ImgFormat.F32:
        img = img.astype(np.float32) / 255.0
    elif img.dtype == np.float32 and img_format == ImgFormat.U8:
        img = (img * 255).astype(np.uint8)

    return img


def save(img, path):
    if img.dtype == np.float32:
        img = (img * 255).astype(np.uint8)

    if len(img.shape) == 3 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    cv2.imwrite(path, img)


def best_tile(complexity_map, tile_size):
    max_sum = -1
    best_pos = (0, 0)

    for y in range(0, complexity_map.shape[0] - tile_size + 1, tile_size // 2):
        for x in range(0, complexity_map.shape[1] - tile_size + 1, tile_size // 2):
            tile = complexity_map[y : y + tile_size, x : x + tile_size]
            current_sum = np.sum(tile)
            if current_sum > max_sum:
                max_sum = current_sum
                best_pos = (y, x)

    return best_pos


# This is a simplified placeholder.
# If chainner_ext is a real library, you need to install it.
# pip install chainner-ext
# For now, a simple cv2.resize will be used.
class ResizeFilter:
    Linear = cv2.INTER_LINEAR


def resize(image, dsize, interpolation=ResizeFilter.Linear, *args, **kwargs):
    return cv2.resize(image, dsize, interpolation=interpolation)


# src/best_tile.py
class BestTile:
    def __init__(
        self,
        in_folder: str,
        out_folder: str,
        tile_size: int = 512,
        process_type: ProcessType = ProcessType.THREAD,
        scale: int = 1,
        dynamic_n_tiles: bool = True,
        laplacian_thread: float = 0,
        image_gray: bool = False,
        func: BaseComplexity = LaplacianComplexity(),
        max_image_size: int = 8192,  # Maximum image dimension to prevent timeouts
    ):
        self.scale = scale
        self.in_folder = in_folder
        self.out_folder = out_folder
        os.makedirs(out_folder, exist_ok=True)
        self.out_list = os.listdir(out_folder)
        self.tile_size = tile_size
        self.all_images = [
            f
            for f in os.listdir(in_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))
        ]
        self.process_type = process_type
        self.dynamic_n_tiles = dynamic_n_tiles
        self.laplacian_thread = laplacian_thread
        self.image_gray = image_gray
        self.func = func
        self.max_image_size = max_image_size
        if func.type() == "IC9600":
            self.process_type = ProcessType.FOR

    def save_result(self, img, img_name) -> None:
        save(img, os.path.join(self.out_folder, img_name))

    def resize_if_too_large(self, img):
        """Resize image if it's too large to prevent CUDA timeouts"""
        h, w = img.shape[:2]
        if h > self.max_image_size or w > self.max_image_size:
            scale_factor = min(self.max_image_size / h, self.max_image_size / w)
            new_h, new_w = int(h * scale_factor), int(w * scale_factor)
            print_info(f"Resizing image from {h}x{w} to {new_h}x{new_w} to prevent timeout")
            return resize(img, (new_w, new_h), ResizeFilter.Linear)
        return img

    def get_tile(self, img, complexity):
        try:
            if self.func.type() != "Laplacian":
                y_cord, x_cord = best_tile(complexity[0], self.tile_size // 8)
                result = self.func.get_tile_comp_score(
                    img, complexity, y_cord, x_cord, self.tile_size
                )
                if result is None:
                    raise RuntimeError("get_tile_comp_score returned None")
                img_tile, complexity, score = result
            elif self.scale > 1:
                img_shape = complexity.shape
                complexity_r = resize(
                    complexity,
                    (img_shape[1] // self.scale, img_shape[0] // self.scale),
                    ResizeFilter.Linear,
                ).squeeze()
                y_cord, x_cord = best_tile(complexity_r, self.tile_size // self.scale)
                y_cord *= self.scale
                x_cord *= self.scale
                result = self.func.get_tile_comp_score(
                    img, complexity, y_cord, x_cord, self.tile_size
                )
                if result is None:
                    raise RuntimeError("get_tile_comp_score returned None")
                img_tile, complexity, score = result
            else:
                y_cord, x_cord = best_tile(complexity, self.tile_size)
                result = self.func.get_tile_comp_score(
                    img, complexity, y_cord, x_cord, self.tile_size
                )
                if result is None:
                    raise RuntimeError("get_tile_comp_score returned None")
                img_tile, complexity, score = result
            return img_tile, complexity, score
        except Exception as e:
            print_error(f"Error in get_tile: {e}")
            raise

    def read_img(self, img_name):
        image = read(
            os.path.join(self.in_folder, img_name),
            ImgColor.GRAY if self.image_gray else ImgColor.RGB,
            ImgFormat.F32,
        )
        return image

    def process(self, img_name: str):
        try:
            if img_name.split(".")[0] + ".png" in self.out_list:
                return
            img = self.read_img(img_name)
            if img is None:
                print_warning(f"Could not read image {img_name}. Skipping.")
                return
            img_shape = img.shape
            if img_shape[0] < self.tile_size or img_shape[1] < self.tile_size:
                print_warning(
                    f"Skipping {img_name}: Image too small ({img_shape[0]}x{img_shape[1]})"
                )
                return

            # Resize if too large to prevent timeouts
            img = self.resize_if_too_large(img)
            img_shape = img.shape

            result_name = ".".join(img_name.split(".")[:-1]) + ".png"
            if img_shape[0] == self.tile_size and img_shape[1] == self.tile_size:
                self.save_result(img, result_name)
                return

            try:
                complexity = self.func(img)
            except Exception as e:
                print_error(f"Error computing complexity for {img_name}: {e}")
                return

            if (
                img_shape[0] * img_shape[1] > self.tile_size**2 * 4
                and self.dynamic_n_tiles
            ):
                num_tiles = (img_shape[0] * img_shape[1]) // (self.tile_size**2 * 2)
                for i in range(num_tiles):
                    try:
                        tile, complexity, score = self.get_tile(img, complexity)
                        if self.laplacian_thread and score < self.laplacian_thread:
                            break
                        self.save_result(
                            tile, ".".join(img_name.split(".")[:-1]) + f"_{i}" + ".png"
                        )
                    except Exception as e:
                        print_error(f"Error processing tile {i} for {img_name}: {e}")
                        break
            else:
                try:
                    tile, complexity, score = self.get_tile(img, complexity)
                    if self.laplacian_thread and score < self.laplacian_thread:
                        return
                    self.save_result(tile, result_name)
                except Exception as e:
                    print_error(f"Error processing single tile for {img_name}: {e}")
        except Exception as e:
            print_error(f"Error processing {img_name}: {e}")

    @monitor_all("BestTile.run", critical_on_error=True)
    def run(self):
        """
        Run the processing on all images using the specified processing type.
        """
        import threading
        import multiprocessing

        if self.process_type == ProcessType.THREAD:
            thread = threading.Thread(target=lambda: None)
            task_registry.register_thread(thread)
            thread_map(self.process, self.all_images)
        elif self.process_type == ProcessType.PROCESS:
            proc = multiprocessing.Process(target=lambda: None)
            task_registry.register_process(proc)
            process_map(self.process, self.all_images)
        else:
            for img_name in tqdm(self.all_images):
                self.process(img_name)
        clear_memory()
        clear_cuda_cache()


# --- API for main.py integration ---
@monitor_all("tile_single_folder", critical_on_error=True)
def tile_single_folder(
    in_folder,
    out_folder,
    tile_size=512,
    process_type="thread",
    func_type="laplacian",
    **kwargs,
):
    """
    Tiling for a single directory using the BestTile logic.
    """
    if func_type == "ic9600":
        if not torch.cuda.is_available():
            raise SystemExit("IC9600 requires a GPU. Please enable GPU.")
        func = IC9600Complexity(device="cuda")
        process_type_enum = ProcessType.FOR
    else:
        func = LaplacianComplexity()
        process_type_enum = (
            ProcessType.THREAD if process_type == "thread" else ProcessType.PROCESS
        )
    processor = BestTile(
        in_folder=in_folder,
        out_folder=out_folder,
        tile_size=tile_size,
        process_type=process_type_enum,
        func=func,
        **kwargs,
    )
    processor.run()
    print_success("Tiling complete.")
    play_done_sound()
    clear_memory()
    clear_cuda_cache()


def tile_hq_lq_dataset(
    hq_folder,
    lq_folder,
    out_hq_folder,
    out_lq_folder,
    tile_size=512,
    process_type="thread",
    func_type="laplacian",
    **kwargs,
):
    """
    Tiling for HQ/LQ paired directories. Each folder is tiled separately but with the same logic.
    """
    tile_single_folder(
        hq_folder, out_hq_folder, tile_size, process_type, func_type, **kwargs
    )
    tile_single_folder(
        lq_folder, out_lq_folder, tile_size, process_type, func_type, **kwargs
    )


# Existing complexity classes remain, but we add a strategy interface


class TilingStrategy(ABC):
    @abstractmethod
    def tile(self, *args, **kwargs):
        pass


class LaplacianTilingStrategy(TilingStrategy):
    def tile(self, in_folder, out_folder, tile_size=512, **kwargs):
        # Use the existing LaplacianComplexity logic
        return tile_single_folder(
            in_folder=in_folder,
            out_folder=out_folder,
            tile_size=tile_size,
            process_type=kwargs.get("process_type", "thread"),
            func_type="laplacian",
        )


class IC9600TilingStrategy(TilingStrategy):
    def tile(self, in_folder, out_folder, tile_size=512, **kwargs):
        # Use the existing IC9600Complexity logic
        return tile_single_folder(
            in_folder=in_folder,
            out_folder=out_folder,
            tile_size=tile_size,
            process_type=kwargs.get("process_type", "thread"),
            func_type="ic9600",
        )


class Tiler:
    def __init__(self, strategy: TilingStrategy):
        self.strategy = strategy

    def run(self, in_folder, out_folder, tile_size=512, **kwargs):
        return self.strategy.tile(in_folder, out_folder, tile_size, **kwargs)


# Factory for tiling strategies
class TilingStrategyFactory:
    @staticmethod
    def get_strategy(name: str) -> TilingStrategy:
        if name == "laplacian":
            return LaplacianTilingStrategy()
        elif name == "ic9600":
            return IC9600TilingStrategy()
        else:
            raise ValueError(f"Unknown tiling strategy: {name}")
