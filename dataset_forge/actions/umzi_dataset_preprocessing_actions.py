"""
Actions for Umzi's Dataset_Preprocessing integration.
Mirrors the Dataset_Preprocessing_consolidated_script.py features for use in Dataset Forge.
"""

import os
import shutil
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map, thread_map
from enum import Enum
from typing import Optional
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.progress_utils import tqdm as forge_tqdm
from dataset_forge.utils.input_utils import (
    get_folder_path,
    ask_int,
    ask_float,
    ask_choice,
    get_input,
    ask_yes_no,
)
from dataset_forge.menus import session_state

from abc import ABC, abstractmethod
from torchvision.transforms import transforms
from pyiqa import create_metric

# ========== ENUMS ==========


class ProcessType(Enum):
    PROCESS = 0
    THREAD = 1
    FOR = 2


class EmbeddedModel(Enum):
    ConvNextS = 0
    ConvNextL = 1
    VITS = 2
    VITB = 3
    VITL = 4
    VITG = 5


# ========== UTILS ==========


def cosine_dist(emb1: torch.Tensor, emb2: torch.Tensor):
    emb1_norm = F.normalize(emb1, dim=-1)
    emb2_norm = F.normalize(emb2, dim=-1)
    return 1 - F.cosine_similarity(emb1_norm, emb2_norm).item()


def euclid_dist(emb1: torch.Tensor, emb2: torch.Tensor):
    return torch.cdist(emb1, emb2).item()


# ========== EMBEDDING MODELS ==========
# (ConvNeXt and DINO)
# NOTE: Requires timm, torch, and internet for model weights
from timm.layers.weight_init import trunc_normal_
from timm.layers.drop import DropPath


class LayerNorm(nn.Module):
    def __init__(self, normalized_shape, eps=1e-6, data_format="channels_last"):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(normalized_shape))
        self.bias = nn.Parameter(torch.zeros(normalized_shape))
        self.eps = eps
        self.data_format = data_format
        if self.data_format not in ["channels_last", "channels_first"]:
            raise NotImplementedError
        self.normalized_shape = (normalized_shape,)

    def forward(self, x):
        if self.data_format == "channels_last":
            return F.layer_norm(
                x, self.normalized_shape, self.weight, self.bias, self.eps
            )
        elif self.data_format == "channels_first":
            u = x.mean(1, keepdim=True)
            s = (x - u).pow(2).mean(1, keepdim=True)
            x = (x - u) / torch.sqrt(s + self.eps)
            x = self.weight[:, None, None] * x + self.bias[:, None, None]
            return x


class Block(nn.Module):
    def __init__(self, dim, drop_path=0.0, layer_scale_init_value=1e-6):
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, kernel_size=7, padding=3, groups=dim)
        self.norm = LayerNorm(dim, eps=1e-6)
        self.pwconv1 = nn.Linear(dim, 4 * dim)
        self.act = nn.GELU()
        self.pwconv2 = nn.Linear(4 * dim, dim)
        self.gamma = (
            nn.Parameter(layer_scale_init_value * torch.ones((dim)), requires_grad=True)
            if layer_scale_init_value > 0
            else None
        )
        self.drop_path = DropPath(drop_path) if drop_path > 0.0 else nn.Identity()

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


class ConvNeXt(nn.Module):
    def __init__(
        self,
        in_chans=3,
        num_classes=1000,
        depths=[3, 3, 9, 3],
        dims=[96, 192, 384, 768],
        drop_path_rate=0.0,
        layer_scale_init_value=1e-6,
        head_init_scale=1.0,
    ):
        super().__init__()
        self.downsample_layers = nn.ModuleList()
        stem = nn.Sequential(
            nn.Conv2d(in_chans, dims[0], kernel_size=4, stride=4),
            LayerNorm(dims[0], eps=1e-6, data_format="channels_first"),
        )
        self.downsample_layers.append(stem)
        for i in range(3):
            downsample_layer = nn.Sequential(
                LayerNorm(dims[i], eps=1e-6, data_format="channels_first"),
                nn.Conv2d(dims[i], dims[i + 1], kernel_size=2, stride=2),
            )
            self.downsample_layers.append(downsample_layer)
        self.stages = nn.ModuleList()
        dp_rates = [x.item() for x in torch.linspace(0, drop_path_rate, sum(depths))]
        cur = 0
        for i in range(4):
            stage = nn.Sequential(
                *[
                    Block(
                        dim=dims[i],
                        drop_path=dp_rates[cur + j],
                        layer_scale_init_value=layer_scale_init_value,
                    )
                    for j in range(depths[i])
                ]
            )
            self.stages.append(stage)
            cur += depths[i]
        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, (nn.Conv2d, nn.Linear)):
            trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)

    def forward_features(self, x):
        for i in range(4):
            x = self.downsample_layers[i](x)
            x = self.stages[i](x)
        return x.mean([-2, -1])

    def forward(self, x):
        x = self.forward_features(x)
        return x


def convnext_small():
    state = torch.hub.load_state_dict_from_url(
        url="https://github.com/umzi2/Dataset_Preprocessing/releases/download/SPARK_model_duplication/convnextS_1kpretrained_official_style.pth",
        map_location="cpu",
        weights_only=True,
    )
    model = ConvNeXt(depths=[3, 3, 27, 3], dims=[96, 192, 384, 768])
    model.load_state_dict(state)
    return model.eval()


def convnext_large():
    state = torch.hub.load_state_dict_from_url(
        url="https://github.com/umzi2/Dataset_Preprocessing/releases/download/SPARK_model_duplication/convnextL_384_1kpretrained_official_style.pth",
        map_location="cpu",
        weights_only=True,
    )
    model = ConvNeXt(depths=[3, 3, 27, 3], dims=[192, 384, 768, 1536])
    model.load_state_dict(state)
    return model.eval()


def enum_to_model(enum: EmbeddedModel):
    if enum == EmbeddedModel.ConvNextS:
        return convnext_small()
    elif enum == EmbeddedModel.ConvNextL:
        return convnext_large()
    elif enum == EmbeddedModel.VITS:
        return torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").eval()
    elif enum == EmbeddedModel.VITB:
        return torch.hub.load("facebookresearch/dinov2", "dinov2_vitb14").eval()
    elif enum == EmbeddedModel.VITL:
        return torch.hub.load("facebookresearch/dinov2", "dinov2_vitl14").eval()
    elif enum == EmbeddedModel.VITG:
        return torch.hub.load("facebookresearch/dinov2", "dinov2_vitg14").eval()
    else:
        raise ValueError("Unknown EmbeddedModel")


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
        self.model = enum_to_model(model).to(self.device)
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
        if self.vit:
            return self.check_img_size(
                torch.tensor(x.transpose((2, 0, 1)))[None, :, :, :].to(self.device)
            )
        return torch.tensor(x.transpose((2, 0, 1)))[None, :, :, :].to(self.device)

    @torch.inference_mode()
    def __call__(self, x):
        if self.scale > 1:
            h, w = x.shape[:2]
            x = cv2.resize(
                x, (w // self.scale, h // self.scale), interpolation=cv2.INTER_CUBIC
            )
        if self.device.type == "cuda" and self.amp:
            with torch.cuda.amp.autocast():
                x = self.img_to_tensor(x)
                return self.model(x)
        else:
            x = self.img_to_tensor(x)
            return self.model(x)


# ========== UTILITY CLASSES ==========


class ImageDataset(Dataset):
    def __init__(self, image_dir, device, transform=None):
        self.image_dir = image_dir
        self.transform = transform
        self.image_files = os.listdir(image_dir)
        self.device = device

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_path = os.path.join(self.image_dir, self.image_files[idx])
        image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise FileNotFoundError(f"Image not found: {img_path}")
        if image.ndim == 2:
            image = np.stack([image] * 3, axis=-1)
        image = image.astype(np.float32) / 255.0
        image = torch.tensor(image, dtype=torch.float32, device=self.device).permute(
            2, 0, 1
        )
        if self.transform:
            image = self.transform(image).to(self.device)
        return image, self.image_files[idx]


# ========== IQA THREADS AND COMPLEXITY CLASSES ==========

class Thread:
    def __init__(self, name, thread):
        self.name = name
        self.thread = thread
    def __repr__(self):
        return f"Thread(Name = {self.name}, Thread = {self.thread}\n)"

class ThreadList:
    def __init__(self):
        self.mass = []
    def append(self, thread):
        self.mass.append(thread)
    def extend(self, thread_list):
        self.mass.extend(thread_list)
    def sort(self, reverse: bool = False):
        self.mass.sort(key=lambda item: item.thread, reverse=reverse)
    def __iter__(self):
        return iter(self.mass)
    def __getitem__(self, index):
        return self.mass[index]
    def __len__(self):
        return len(self.mass)

class IQANode:
    def __init__(
        self,
        img_dir,
        batch_size: int = 8,
        thread: float = 0.5,
        median_thread=0,
        move_folder: Optional[str] = None,
        transform=None,
        reverse=False,
    ):
        self.device = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
        dataset = ImageDataset(img_dir, self.device, transform)
        self.data_loader = DataLoader(dataset, batch_size=batch_size)
        self.img_dir: str = img_dir
        self.thread = thread
        self.reverse = reverse
        self.move_folder = move_folder
        if move_folder is not None:
            os.makedirs(move_folder, exist_ok=True)
        if median_thread:
            self.median_thread = median_thread
            self.thread_list = ThreadList()
        else:
            self.thread_list = None
    def forward(self, images):
        raise NotImplementedError("The forward method must be implemented in a subclass")
    @torch.inference_mode()
    def __call__(self):
        for images, filenames in tqdm(self.data_loader):
            iqa = self.forward(images)
            for index in range(iqa.shape[0]):
                file_name = filenames[index]
                iqa_value = iqa[index]
                if self.thread_list is None:
                    if iqa[index] > self.thread and self.move_folder:
                        shutil.move(
                            os.path.join(self.img_dir, file_name),
                            os.path.join(self.move_folder, file_name),
                        )
                    elif iqa[index] < self.thread and not self.move_folder:
                        os.remove(os.path.join(self.img_dir, file_name))
                else:
                    if (iqa[index] > self.thread and not self.reverse) or (
                        iqa[index] < self.thread and self.reverse
                    ):
                        self.thread_list.append(
                            Thread(name=file_name, thread=float(iqa_value))
                        )
                    else:
                        if not self.move_folder:
                            os.remove(os.path.join(self.img_dir, file_name))
        if self.thread_list:
            self.thread_list.sort(self.reverse)
            clip_index = int(len(self.thread_list) * self.median_thread)
            if self.move_folder:
                for thread in self.thread_list[-clip_index:]:
                    file_name = thread.name
                    shutil.move(
                        os.path.join(self.img_dir, file_name),
                        os.path.join(self.move_folder, file_name),
                    )
            else:
                for thread in self.thread_list[:-clip_index]:
                    file_name = thread.name
                    shutil.move(
                        os.path.join(self.img_dir, file_name),
                        os.path.join(self.move_folder, file_name),
                    )

class AnIQAThread(IQANode):
    def __init__(
        self,
        img_dir,
        batch_size: int = 8,
        thread: float = 0.5,
        median_thread=0,
        move_folder: Optional[str] = None,
    ):
        compose = transforms.Compose([
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        super().__init__(img_dir, batch_size, thread, median_thread, move_folder, compose)
        self.model = torch.hub.load(
            repo_or_dir="miccunifi/ARNIQA",
            source="github",
            model="ARNIQA",
            regressor_dataset="kadid10k",
        )
        self.model.eval().to(self.device)
    def forward(self, images):
        _, _, h, w = images.size()
        images_ds = transforms.Resize((h // 2, w // 2)).to(images)(images)
        with torch.inference_mode():
            iqa = self.model(images, images_ds, return_embedding=False, scale_score=True)
        return iqa

class BlockinessThread(IQANode):
    def __init__(
        self,
        img_dir,
        batch_size: int = 8,
        thread: float = 0.5,
        median_thread=0,
        move_folder: Optional[str] = None,
    ):
        super().__init__(img_dir, batch_size, thread, median_thread, move_folder, None, reverse=True)
        self.model = lambda images: torch.zeros(images.shape[0])  # Dummy placeholder
    def forward(self, images):
        return self.model(images)

class HyperThread(IQANode):
    def __init__(
        self,
        img_dir,
        batch_size: int = 8,
        thread: float = 0.5,
        median_thread=0,
        move_folder: Optional[str] = None,
    ):
        super().__init__(img_dir, batch_size, thread, median_thread, move_folder, None)
        self.model = create_metric("hyperiqa", device=self.device)
    def forward(self, images):
        return self.model(images)

class TopIQThread(IQANode):
    def __init__(
        self,
        img_dir,
        batch_size: int = 8,
        thread: float = 0.5,
        median_thread=0,
        move_folder: Optional[str] = None,
    ):
        super().__init__(img_dir, batch_size, thread, median_thread, move_folder, None)
        self.model = create_metric("topiq_nr", device=self.device)
    def forward(self, images):
        return self.model(images)

class IC9600Thread(IQANode):
    def __init__(
        self,
        img_dir,
        batch_size: int = 8,
        thread: float = 0.5,
        median_thread=0,
        move_folder: Optional[str] = None,
    ):
        super().__init__(img_dir, batch_size, thread, median_thread, move_folder, None)
        self.model = lambda images: torch.zeros(images.shape[0])  # Dummy placeholder
    def forward(self, images):
        return self.model(images)

class BaseComplexity(ABC):
    @staticmethod
    @abstractmethod
    def type() -> str: ...
    @abstractmethod
    def get_tile_comp_score(self, image, complexity, y: int, x: int, tile_size: int): ...
    @abstractmethod
    def __call__(self, img: np.ndarray): ...

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
        elif self.median_blur <= 5:
            image = cv2.medianBlur(image, self.median_blur)
        else:
            image = (
                cv2.medianBlur((image * 255).astype(np.uint8), self.median_blur).astype(np.float32) / 255
            )
        return image
    @staticmethod
    def type():
        return "Laplacian"
    @staticmethod
    def get_tile_comp_score(image, complexity, y, x, tile_size):
        img_tile = image[y : y + tile_size, x : x + tile_size]
        score = np.mean(complexity[y : y + tile_size, x : x + tile_size])
        complexity[y : y + tile_size, x : x + tile_size] = -1.0
        return img_tile, complexity, score
    def __call__(self, img):
        img = self.image_to_gray(img)
        img = self.median_laplacian(img)
        return np.abs(cv2.Laplacian(img, -1))

def ic9600():
    raise NotImplementedError("ic9600 model loading not implemented in this stub.")

class IC9600Complexity(BaseComplexity):
    def __init__(self, device: str = "cuda"):
        super().__init__()
        self.device = torch.device(device)
        self.arch = ic9600()
    @staticmethod
    def image_to_tensor(image: np.ndarray):
        image = image.squeeze()
        if image.ndim == 2:
            return torch.tensor(cv2.cvtColor(image, cv2.COLOR_GRAY2RGB).transpose((2, 0, 1)))[None, :, :, :]
        return torch.tensor(image.transpose((2, 0, 1)))[None, :, :, :]
    @staticmethod
    def type():
        return "IC9600"
    @torch.inference_mode()
    def get_tile_comp_score(self, image, complexity, y, x, tile_size):
        img_tile = image[y * 8 : y * 8 + tile_size, x * 8 : x * 8 + tile_size]
        score = 0.0  # Dummy placeholder
        complexity[0][y : y + tile_size // 8, x : x + tile_size // 8] = -1.0
        return img_tile, complexity, score
    @torch.inference_mode()
    def __call__(self, img):
        img = self.image_to_tensor(img).to(self.device)
        x_cat, cly_map = torch.zeros(1), torch.zeros(1)  # Dummy placeholder
        return cly_map.detach().cpu().squeeze().numpy(), x_cat

class ResizeFilter:
    Nearest = 0
    Linear = 1
    Cubic = 2
    CubicCatrom = 3
    Lanczos = 4

def resize(image, size, filter_type=ResizeFilter.Linear, preserve_range=False):
    interpolation_map = {
        ResizeFilter.Nearest: cv2.INTER_NEAREST,
        ResizeFilter.Linear: cv2.INTER_LINEAR,
        ResizeFilter.Cubic: cv2.INTER_CUBIC,
        ResizeFilter.CubicCatrom: cv2.INTER_CUBIC,
        ResizeFilter.Lanczos: cv2.INTER_LANCZOS4,
    }
    interpolation = interpolation_map.get(filter_type, cv2.INTER_LINEAR)
    resized = cv2.resize(image, size, interpolation=interpolation)
    if preserve_range:
        return resized
    return resized.astype(np.float32) / 255.0 if resized.dtype == np.uint8 else resized

def best_tile(complexity, tile_size):
    max_score = -np.inf
    best_coords = (0, 0)
    h, w = complexity.shape
    for y in range(0, h - tile_size + 1):
        for x in range(0, w - tile_size + 1):
            score = np.mean(complexity[y : y + tile_size, x : x + tile_size])
            if score > max_score:
                max_score = score
                best_coords = (y, x)
    return best_coords

def save(img, path):
    if isinstance(img, torch.Tensor):
        img = img.detach().cpu().numpy()
    if img.dtype in [np.float32, np.float64]:
        img = np.clip(img * 255, 0, 255).astype(np.uint8)
    cv2.imwrite(
        path,
        (
            cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            if img.ndim == 3 and img.shape[2] == 3
            else img
        ),
    )

def read(path, color_mode=0, img_format=None):
    if color_mode == 1:  # GRAY
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    else:
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if img is None:
        raise FileNotFoundError(f"Image not found: {path}")
    img = img.astype(np.float32) / 255.0
    return img

class ImgColor:
    GRAY = 1
    RGB = 0

class ImgFormat:
    F32 = 0

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
            left_up_cord = best_tile(complexity[0], self.tile_size // 8)
        elif self.scale > 1:
            img_shape = complexity.shape
            complexity_r = resize(
                complexity,
                (img_shape[1] // self.scale, img_shape[0] // self.scale),
                ResizeFilter.Linear,
                False,
            ).squeeze()
            left_up_cord = best_tile(complexity_r, self.tile_size // self.scale)
            left_up_cord = [index * self.scale for index in left_up_cord]
        else:
            left_up_cord = best_tile(complexity, self.tile_size)
        img, laplacian, score = self.func.get_tile_comp_score(
            img, complexity, left_up_cord[0], left_up_cord[1], self.tile_size
        )
        return img, laplacian, score
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
            img_shape = img.shape
            if img_shape[0] < self.tile_size or img_shape[1] < self.tile_size:
                return
            result_name = ".".join(img_name.split(".")[:-1]) + ".png"
            if img_shape[0] == self.tile_size and img_shape[1] == self.tile_size:
                self.save_result(img, result_name)
                return
            complexity = self.func(img)
            if (
                img_shape[0] * img_shape[1] > self.tile_size**2 * 4
                and self.dynamic_n_tiles
            ):
                for i in range(
                    (img_shape[0] * img_shape[1]) // (self.tile_size**2 * 2)
                ):
                    tile, laplacian_abs, score = self.get_tile(img, complexity)
                    if self.laplacian_thread:
                        if score < self.laplacian_thread:
                            break
                    self.save_result(
                        tile, ".".join(img_name.split(".")[:-1]) + f"_{i}" + ".png"
                    )
            else:
                tile, laplacian_abs, score = self.get_tile(img, complexity)
                if self.laplacian_thread:
                    if score < self.laplacian_thread:
                        return
                self.save_result(tile, result_name)
        except Exception as e:
            print(img_name, "\n", e)
    def run(self):
        if self.process_type == ProcessType.THREAD:
            thread_map(self.process, self.all_images)
        elif self.process_type == ProcessType.PROCESS:
            process_map(self.process, self.all_images)
        else:
            for img_name in tqdm(self.all_images):
                self.process(img_name)

class VideoToFrame:
    def __init__(
        self,
        embedder: ImgToEmbedding = ImgToEmbedding(),
        thread: float = 0.3,
        distance_fn=euclid_dist,
    ):
        self.embedder = embedder
        self.thread = thread
        self.distance_func = distance_fn
    def __call__(self, video_path, out_path):
        os.makedirs(out_path, exist_ok=True)
        capture = cv2.VideoCapture(video_path)
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        ref = None
        n = 0
        with tqdm(total=total_frames) as pbar:
            while capture.isOpened():
                ret, frame = capture.read()
                if not ret:
                    break
                if ref is None:
                    ref = self.embedder(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                    )
                else:
                    temp_embedd = self.embedder(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                    )
                    if self.distance_func(ref, temp_embedd) > self.thread:
                        cv2.imwrite(os.path.join(out_path, f"frame_{n}.png"), frame)
                        ref = temp_embedd
                n += 1
                pbar.update(1)
        capture.release()

def create_embedd(
    img_folder: str,
    embedd_pth: str = "embedd.pth",
    embedder: ImgToEmbedding = ImgToEmbedding(),
):
    embedded = {}
    for img_name in os.listdir(img_folder):
        img = read(os.path.join(img_folder, img_name), ImgColor.RGB, ImgFormat.F32)
        embedded[img_name] = embedder(img).detach().cpu()
    torch.save(embedded, embedd_pth)

def duplicate_list(embedd_pth: str = "embedd.pth", dist_fn=euclid_dist, threshold=1):
    embeddings = torch.load(embedd_pth)
    names = list(embeddings.keys())
    used = set()
    clusters = []
    for i, name in enumerate(names):
        if name in used:
            continue
        cluster = [name]
        used.add(name)
        base_vec = embeddings[name]
        for j in range(i + 1, len(names)):
            other_name = names[j]
            if other_name in used:
                continue
            other_vec = embeddings[other_name]
            dist = dist_fn(base_vec, other_vec)
            if dist < threshold:
                cluster.append(other_name)
                used.add(other_name)
        if len(cluster) > 1:
            clusters.append(cluster)
    return clusters


# ========== MENU ACTIONS ==========


def best_tile_extraction_action():
    """Run Best Tile Extraction workflow (ported from consolidated script)."""
    print_info("[Umzi] Best Tile Extraction action")
    try:
        in_folder = get_folder_path("Input folder")
        out_folder = get_folder_path("Output folder")
        tile_size = ask_int(
            "Tile size",
            default=session_state.user_preferences.get("default_tile_size", 512),
            min_value=32,
        )
        process_type = ask_choice(
            "Process type", ["THREAD", "PROCESS", "FOR"], default=0
        )
        scale = ask_int("Scale", default=1, min_value=1)
        dynamic_n_tiles = ask_yes_no("Dynamic n tiles?", default=True)
        laplacian_thread = ask_float("Laplacian threshold", default=0)
        image_gray = ask_yes_no("Use grayscale?", default=False)
        complexity_type = ask_choice(
            "Complexity function", ["Laplacian", "IC9600"], default=0
        )
        if complexity_type == "Laplacian":
            median_blur = ask_int("Median blur (odd int)", default=1, min_value=1)
            func = LaplacianComplexity(median_blur)
        else:
            device = get_input("Device (cuda/cpu)", default="cuda")
            func = IC9600Complexity(device)
        pt_map = {
            "THREAD": ProcessType.THREAD,
            "PROCESS": ProcessType.PROCESS,
            "FOR": ProcessType.FOR,
        }
        best_tile = BestTile(
            in_folder,
            out_folder,
            tile_size,
            pt_map[process_type],
            scale,
            dynamic_n_tiles,
            laplacian_thread,
            image_gray,
            func,
        )
        best_tile.run()
        print_success("Best Tile Extraction complete.")
    except Exception as e:
        print_error(f"Error: {e}")
    clear_memory()
    clear_cuda_cache()


def video_frame_extraction_action():
    """Run Video Frame Extraction workflow (ported from consolidated script)."""
    print_info("[Umzi] Video Frame Extraction action")
    try:
        embed_model = ask_choice(
            "Embedding model",
            ["ConvNextS", "ConvNextL", "VITS", "VITB", "VITL", "VITG"],
            default=0,
        )
        amp = ask_yes_no("Use AMP?", default=True)
        scale = ask_int("Scale", default=4, min_value=1)
        device = get_input("Device (cuda/cpu)", default="cuda")
        embedder = ImgToEmbedding(EmbeddedModel[embed_model], amp, scale, device)
        thread = ask_float("Distance threshold", default=0.3)
        dist_fn_name = ask_choice("Distance function", ["euclid", "cosine"], default=0)
        dist_fn = euclid_dist if dist_fn_name == "euclid" else cosine_dist
        video_path = get_input("Video path", default="video.mp4")
        out_path = get_folder_path("Output folder")
        v2f = VideoToFrame(embedder, thread, dist_fn)
        v2f(video_path, out_path)
        print_success("Video Frame Extraction complete.")
    except Exception as e:
        print_error(f"Error: {e}")
    clear_memory()
    clear_cuda_cache()


def image_deduplication_create_embeddings_action():
    """Run Image Deduplication (create embeddings) workflow (ported from consolidated script)."""
    print_info("[Umzi] Image Deduplication (create embeddings) action")
    try:
        img_folder = get_folder_path("Image folder")
        embedd_pth = get_input("Embeddings path", default="embedd.pth")
        embed_model = ask_choice(
            "Embedding model",
            ["ConvNextS", "ConvNextL", "VITS", "VITB", "VITL", "VITG"],
            default=0,
        )
        amp = ask_yes_no("Use AMP?", default=True)
        scale = ask_int("Scale", default=4, min_value=1)
        device = get_input("Device (cuda/cpu)", default="cuda")
        embedder = ImgToEmbedding(EmbeddedModel[embed_model], amp, scale, device)
        create_embedd(img_folder, embedd_pth, embedder)
        print_success(f"Embeddings saved to {embedd_pth}")
    except Exception as e:
        print_error(f"Error: {e}")
    clear_memory()
    clear_cuda_cache()


def image_deduplication_find_duplicates_action():
    """Run Image Deduplication (find duplicates) workflow (ported from consolidated script)."""
    print_info("[Umzi] Image Deduplication (find duplicates) action")
    try:
        embedd_pth = get_input("Embeddings path", default="embedd.pth")
        dist_fn_name = ask_choice("Distance function", ["euclid", "cosine"], default=0)
        dist_fn = euclid_dist if dist_fn_name == "euclid" else cosine_dist
        threshold = ask_float("Distance threshold", default=1.0)
        clusters = duplicate_list(embedd_pth, dist_fn, threshold)
        print_info("Duplicate clusters:")
        for cluster in clusters:
            print_info(str(cluster))
        print_success("Duplicate finding complete.")
    except Exception as e:
        print_error(f"Error: {e}")
    clear_memory()
    clear_cuda_cache()


def iqa_filtering_action():
    """Run IQA Filtering workflow (ported from consolidated script)."""
    print_info("[Umzi] IQA Filtering action")
    try:
        iqa_alg = ask_choice(
            "IQA Algorithm",
            ["HyperIQA", "AnIQA", "TopIQ", "Blockiness", "IC9600"],
            default=0,
        )
        img_dir = get_folder_path("Input folder")
        batch_size = ask_int(
            "Batch size",
            default=session_state.user_preferences.get("default_batch_size", 8),
            min_value=1,
        )
        thread = ask_float("Score threshold", default=0.5)
        median_thread = ask_float("Median thread (0 for off)", default=0)
        move_folder = get_input("Move folder (empty for none)", default="") or None
        alg_map = {
            "HyperIQA": HyperThread,
            "AnIQA": AnIQAThread,
            "TopIQ": TopIQThread,
            "Blockiness": BlockinessThread,
            "IC9600": IC9600Thread,
        }
        alg = alg_map[iqa_alg](img_dir, batch_size, thread, median_thread, move_folder)
        alg()
        print_success("IQA Filtering complete.")
    except Exception as e:
        print_error(f"Error: {e}")
    clear_memory()
    clear_cuda_cache()


def embedding_extraction_action():
    """Run Embedding Extraction (single image) workflow (ported from consolidated script)."""
    print_info("[Umzi] Embedding Extraction (single image) action")
    try:
        img_path = get_input("Image path", default="image.png")
        embed_model = ask_choice(
            "Embedding model",
            ["ConvNextS", "ConvNextL", "VITS", "VITB", "VITL", "VITG"],
            default=0,
        )
        amp = ask_yes_no("Use AMP?", default=True)
        scale = ask_int("Scale", default=4, min_value=1)
        device = get_input("Device (cuda/cpu)", default="cuda")
        embedder = ImgToEmbedding(EmbeddedModel[embed_model], amp, scale, device)
        img = read(img_path, ImgColor.RGB, ImgFormat.F32)
        emb = embedder(img)
        print_info(f"Embedding shape: {emb.shape}")
        print_success("Embedding extraction complete.")
    except Exception as e:
        print_error(f"Error: {e}")
    clear_memory()
    clear_cuda_cache()


__all__ = [
    "BestTile",
    "ProcessType",
    "LaplacianComplexity",
    "ImgToEmbedding",
    "EmbeddedModel",
    "VideoToFrame",
    "create_embedd",
    "duplicate_list",
    "euclid_dist",
    "ImgColor",
    "ImgFormat",
    "read",
]
