import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet18, ResNet18_Weights
from enum import Enum
from abc import ABC, abstractmethod
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map, thread_map


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# src/enum.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class ProcessType(Enum):
    PROCESS = 0
    THREAD = 1
    FOR = 2


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# src/scripts/utils/complexity/object.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class BaseComplexity(ABC):
    @staticmethod
    @abstractmethod
    def type() -> str: ...

    @abstractmethod
    def get_tile_comp_score(
        self, image, complexity, y: int, x: int, tile_size: int
    ): ...

    @abstractmethod
    def __call__(self, img: np.ndarray): ...


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# src/scripts/archs/ICNet.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
        resnet18Pretrained1 = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        resnet18Pretrained2 = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)

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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# src/scripts/utils/complexity/ic9600.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class IC9600Complexity(BaseComplexity):
    def __init__(self, device: str = "cuda"):
        super().__init__()
        self.device = torch.device(device)
        self.arch = ic9600().to(self.device)

    @staticmethod
    def image_to_tensor(image: np.ndarray):
        image = image.squeeze()
        if image.ndim == 2:
            return torch.tensor(
                cv2.cvtColor(image, cv2.COLOR_GRAY2RGB).transpose((2, 0, 1))
            )[None, :, :, :]
        return torch.tensor(image.transpose((2, 0, 1)))[None, :, :, :]

    @staticmethod
    def type():
        return "IC9600"

    @torch.inference_mode()
    def get_tile_comp_score(self, image, complexity, y, x, tile_size):
        img_tile = image[
            y * 8 : y * 8 + tile_size,
            x * 8 : x * 8 + tile_size,
        ]
        score = (
            self.arch.score(
                complexity[1][
                    :,
                    :,
                    y : y + tile_size // 8,
                    x : x + tile_size // 8,
                ]
            )
            .detach()
            .cpu()
            .item()
        )
        complexity[0][
            y : y + tile_size // 8,
            x : x + tile_size // 8,
        ] = -1.0
        return img_tile, complexity, score

    @torch.inference_mode()
    def __call__(self, img):
        img = self.image_to_tensor(img).to(self.device)
        x_cat, cly_map = self.arch(img)
        return cly_map.detach().cpu().squeeze().numpy(), x_cat


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# src/scripts/utils/complexity/laplacian.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
    def get_tile_comp_score(image, complexity, y, x, tile_size):
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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Dummy implementations for pepeline and chainner_ext as they are not standard libraries
# You will need to replace these with your actual implementation or install them if they are packages.
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# src/best_tile.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
    ):
        self.scale = scale
        self.in_folder = in_folder
        self.out_folder = out_folder
        os.makedirs(out_folder, exist_ok=True)
        self.out_list = os.listdir(out_folder)
        self.tile_size = tile_size
        self.all_images = os.listdir(in_folder)
        self.process_type = process_type
        self.dynamic_n_tiles = dynamic_n_tiles
        self.laplacian_thread = laplacian_thread
        self.image_gray = image_gray
        self.func = func
        if func.type() == "IC9600":
            self.process_type = ProcessType.FOR

    def save_result(self, img, img_name) -> None:
        save(img, os.path.join(self.out_folder, img_name))

    def get_tile(self, img, complexity):
        if self.func.type() != "Laplacian":
            y_cord, x_cord = best_tile(complexity[0], self.tile_size // 8)
            img_tile, complexity, score = self.func.get_tile_comp_score(
                img, complexity, y_cord, x_cord, self.tile_size
            )
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
            img_tile, complexity, score = self.func.get_tile_comp_score(
                img, complexity, y_cord, x_cord, self.tile_size
            )
        else:
            y_cord, x_cord = best_tile(complexity, self.tile_size)
            img_tile, complexity, score = self.func.get_tile_comp_score(
                img, complexity, y_cord, x_cord, self.tile_size
            )
        return img_tile, complexity, score

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
                print(f"Warning: Could not read image {img_name}. Skipping.")
                return
            img_shape = img.shape
            result_name = ".".join(img_name.split(".")[:-1]) + ".png"

            # If the image is smaller than the tile size, save it directly
            if img_shape[0] < self.tile_size or img_shape[1] < self.tile_size:
                self.save_result(img, result_name)
                return

            # If the image is exactly the tile size, save it directly
            if img_shape[0] == self.tile_size and img_shape[1] == self.tile_size:
                self.save_result(img, result_name)
                return

            # For images larger than the tile size, proceed with tile extraction
            complexity = self.func(img)
            if (
                img_shape[0] * img_shape[1] > self.tile_size**2 * 4
                and self.dynamic_n_tiles
            ):
                num_tiles = (img_shape[0] * img_shape[1]) // (self.tile_size**2 * 2)
                for i in range(num_tiles):
                    tile, complexity, score = self.get_tile(img, complexity)
                    if self.laplacian_thread and score < self.laplacian_thread:
                        break
                    self.save_result(
                        tile, ".".join(img_name.split(".")[:-1]) + f"_{i}" + ".png"
                    )
            else:
                tile, complexity, score = self.get_tile(img, complexity)
                if self.laplacian_thread and score < self.laplacian_thread:
                    return
                self.save_result(tile, result_name)
        except Exception as e:
            print(f"Error processing {img_name}: {e}")

    def run(self):
        """
        Run the processing on all images using the specified processing type.
        """
        if self.process_type == ProcessType.THREAD:
            thread_map(self.process, self.all_images)
        elif self.process_type == ProcessType.PROCESS:
            process_map(self.process, self.all_images)
        else:
            for img_name in tqdm(self.all_images):
                self.process(img_name)


if __name__ == "__main__":
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # HOW TO USE IN GOOGLE COLAB
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # 1. Mount your Google Drive
    # from google.colab import drive
    # drive.mount('/content/drive')

    # 2. Define your input and output folders
    #    These folders should exist in your Google Drive.
    #    For example, if you have a folder named 'my_images' in your Drive's root,
    #    the path would be '/content/drive/My Drive/my_images'.
    input_folder = (
        "E:/_dataset/dataset_2x_re-animeV1_RealPLKSR/_1 DragonBall_before/test/og"
    )
    output_folder = (
        "E:/_dataset/dataset_2x_re-animeV1_RealPLKSR/_1 DragonBall_before/test/tiles"
    )

    # 3. Choose your complexity function
    #    Options are LaplacianComplexity() or IC9600Complexity()
    #    - LaplacianComplexity is faster and runs on the CPU.
    #    - IC9600Complexity is more advanced, requires a GPU, and is slower.
    #      If using IC9600, make sure your Colab notebook is set to use a GPU runtime.
    #      (Runtime -> Change runtime type -> Hardware accelerator -> GPU)
    use_ic9600 = True  # Set to True to use IC9600, False for Laplacian

    if use_ic9600:
        # Check for GPU
        if not torch.cuda.is_available():
            raise SystemExit(
                "IC9600 requires a GPU. Please enable GPU in Colab's runtime settings."
            )
        complexity_function = IC9600Complexity(device="cuda")
    else:
        complexity_function = LaplacianComplexity(median_blur=3)

    # 4. Configure the BestTile processor
    #    - tile_size: The size of the square tile to extract (e.g., 512, 1024).
    #    - process_type: How to process multiple images.
    #      - ProcessType.THREAD: Use multiple threads (good for I/O bound tasks).
    #      - ProcessType.PROCESS: Use multiple processes (good for CPU-bound tasks).
    #      - ProcessType.FOR: A simple loop (useful for debugging or when using GPU).
    #    - dynamic_n_tiles: If True, extract multiple tiles from very large images.
    #    - laplacian_thread: A threshold to discard tiles with low complexity.
    processor = BestTile(
        in_folder=input_folder,
        out_folder=output_folder,
        tile_size=1024,
        process_type=ProcessType.FOR if use_ic9600 else ProcessType.THREAD,
        dynamic_n_tiles=True,
        laplacian_thread=0.01,  # Adjust as needed
        func=complexity_function,
    )

    # 5. Run the process
    print(f"Starting processing for images in: {input_folder}")
    print(f"Output will be saved to: {output_folder}")
    processor.run()
    print("Processing complete.")
