import os
import shutil
from typing import Optional, Dict, List
from dataset_forge.utils.progress_utils import tqdm

# ===================== Inlined IQA Threads and Dependencies (from src.scripts.iqa and dependencies) =====================
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import (
    print_success,
    print_info,
    print_error,
    print_header,
    print_section,
    print_warning,
)
from dataset_forge.utils.audio_utils import play_done_sound

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    torch,
    torch_nn as nn,
    torch_nn_functional as F,
    torchvision,
    numpy_as_np as np,
    PIL_Image as Image,
    cv2,
)

# Import Dataset and DataLoader from torch.utils.data
from torch.utils.data import Dataset, DataLoader


def collate_fn_resize(batch):
    """Custom collate function that resizes all images to a common size."""
    from torchvision.transforms import functional as F

    # Find the maximum dimensions in the batch
    max_height = max(img.shape[1] for img, _ in batch)
    max_width = max(img.shape[2] for img, _ in batch)

    # Resize all images to the maximum dimensions
    resized_images = []
    filenames = []

    for img, filename in batch:
        # Resize image to max dimensions using bilinear interpolation
        resized_img = F.resize(
            img.unsqueeze(0), [max_height, max_width], antialias=True
        ).squeeze(0)
        resized_images.append(resized_img)
        filenames.append(filename)

    # Stack the resized images
    images = torch.stack(resized_images)
    return images, filenames


def collate_fn_individual(batch):
    """Alternative collate function that processes images individually."""
    # Return the batch as-is, but with batch_size=1 to avoid stacking issues
    return batch


def collate_fn_safe(batch):
    """Safe collate function that handles size mismatches gracefully."""
    try:
        # Try the resize approach first
        return collate_fn_resize(batch)
    except Exception as e:
        print_warning(
            f"Resize collate failed ({e}), falling back to individual processing"
        )
        # Fall back to individual processing
        return collate_fn_individual(batch)


# --- ImageDataset and IQANode (from utils/module.py and utils/objects.py) ---
class ImageDataset(Dataset):
    def __init__(self, image_dir, device, transform=None):
        self.image_dir = image_dir
        self.transform = transform
        # Only include files, not directories, and skip _bhi_filtered folder
        all_items = os.listdir(image_dir)
        self.image_files = []

        # Add progress tracking for file validation
        print_info(f"Validating {len(all_items)} files in {image_dir}...")

        for item in all_items:
            item_path = os.path.join(image_dir, item)
            if os.path.isfile(item_path) and not item.startswith("_bhi_filtered"):
                # Pre-validate that the file can be read
                try:
                    # Use PIL to load and validate the image
                    with Image.open(item_path) as img:
                        img_array = (
                            np.array(img.convert("RGB"), dtype=np.float32) / 255.0
                        )
                        if img_array is not None and len(img_array.shape) == 3:
                            self.image_files.append(item)
                except Exception as e:
                    print_warning(f"Skipping {item} during initialization: {e}")
                    continue

        print_info(f"Found {len(self.image_files)} valid image files")
        self.device = device

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        from dataset_forge.utils.memory_utils import to_device_safe

        img_path = os.path.join(self.image_dir, self.image_files[idx])
        # Use PIL to load the image
        with Image.open(img_path) as img:
            image = np.array(img.convert("RGB"), dtype=np.float32) / 255.0
        image = torch.tensor(image, dtype=torch.float32, device=self.device).permute(
            2, 0, 1
        )
        if self.transform:
            image = to_device_safe(self.transform(image), self.device)
        return image, self.image_files[idx]


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
        move_folder: str | None = None,
        transform=None,
        reverse=False,
        dataset=None,  # Allow passing a pre-created dataset
    ):
        self.img_dir = img_dir
        self.batch_size = batch_size
        self.thread = thread
        self.median_thread = median_thread
        self.move_folder = move_folder
        self.transform = transform
        self.reverse = reverse
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Use shared dataset if provided, otherwise create new one
        if dataset is not None:
            self.dataset = dataset
        else:
            self.dataset = ImageDataset(img_dir, self.device, transform)

        # Optimized DataLoader with pinned memory and multiple workers for better CUDA performance
        # Note: Using num_workers=0 on Windows to avoid CUDA tensor sharing issues
        num_workers = (
            0  # Disable multiprocessing on Windows to avoid CUDA tensor sharing issues
        )

        # Disable pin_memory when using CUDA tensors (pin_memory only works with CPU tensors)
        use_pin_memory = self.device.type == "cpu"

        self.data_loader = DataLoader(
            self.dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=use_pin_memory,  # Only use pin_memory for CPU tensors
            persistent_workers=False,  # Disable persistent workers when num_workers=0
            collate_fn=collate_fn_safe,
            prefetch_factor=None,  # Disable prefetch when num_workers=0
        )

    def forward(self, images):
        raise NotImplementedError(
            "The forward method must be implemented in a subclass"
        )

    @torch.no_grad()
    def __call__(self):
        for batch_data in tqdm(self.data_loader):
            try:
                # Handle both collate function outputs
                if isinstance(batch_data, tuple):
                    images, filenames = batch_data
                else:
                    # Individual processing case
                    images = [batch_data[0][0]]  # Single image
                    filenames = [batch_data[0][1]]  # Single filename

                # Ensure images is a tensor for batch processing
                if not isinstance(images, torch.Tensor):
                    # Convert list of tensors to batch tensor
                    images = torch.stack(images)

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

            except Exception as e:
                print_error(f"Error processing batch: {e}")
                print_info("Continuing with next batch...")
                continue

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


# --- Blockiness metric (from archs/blocklines.py) ---
DEFAULT_BLOCK_SIZE = 8


def dct(x, norm=None):
    x_shape = x.shape
    N = x_shape[-1]
    x = x.contiguous().view(-1, N)
    v = torch.cat([x[:, ::2], x[:, 1::2].flip([1])], dim=1)
    Vc = torch.view_as_real(torch.fft.fft(v, dim=1))
    k = -torch.arange(N, dtype=x.dtype, device=x.device)[None, :] * np.pi / (2 * N)
    width_r = torch.cos(k)
    width_i = torch.sin(k)
    V = Vc[:, :, 0] * width_r - Vc[:, :, 1] * width_i
    if norm == "ortho":
        V[:, 0] /= np.sqrt(N) * 2
        V[:, 1:] /= np.sqrt(N / 2) * 2
    V = 2 * V.view(*x_shape)
    return V


def dct_2d(x, norm=None):
    X1 = dct(x, norm=norm)
    X2 = dct(X1.transpose(-1, -2), norm=norm)
    return X2.transpose(-1, -2)


def calc_margin(height: int, width: int, block_size: int = DEFAULT_BLOCK_SIZE):
    height_margin: int = height % block_size
    width_margin: int = width % block_size
    cal_height: int = height - (
        height_margin if height_margin >= 4 else height_margin + block_size
    )
    cal_width: int = width - (
        width_margin if width_margin >= 4 else width_margin + block_size
    )
    height_margin = (height_margin + block_size) if height_margin < 4 else height_margin
    width_margin = (width_margin + block_size) if width_margin < 4 else width_margin
    return cal_height, cal_width, height_margin, width_margin


def calc_v_torch(
    dct_img: "torch.Tensor",
    height_block_num: int,
    width_block_num: int,
    block_size: int = DEFAULT_BLOCK_SIZE,
):
    if not isinstance(dct_img, torch.Tensor):
        raise TypeError(f"dct_img must be a torch.Tensor, got {type(dct_img)}")
    if dct_img.dim() not in (3, 4):
        raise ValueError(
            f"dct_img must have 3 or 4 dimensions (got {dct_img.dim()}). Expected (B, H, W) or (B, 1, H, W)."
        )
    if block_size <= 0:
        raise ValueError(f"block_size must be positive, got {block_size}")
    if height_block_num <= 2 or width_block_num <= 2:
        raise ValueError(
            f"height_block_num and width_block_num must be greater than 2 (got {height_block_num} and {width_block_num})."
        )
    if dct_img.dim() == 4:
        dct_img = dct_img.squeeze(1)
    batch_size = dct_img.size(0)
    num_h = height_block_num - 3
    num_w = width_block_num - 3
    device = dct_img.device
    h_offsets = (
        block_size + torch.arange(1, height_block_num - 2, device=device) * block_size
    )
    w_offsets = (
        block_size + torch.arange(1, width_block_num - 2, device=device) * block_size
    )
    r = h_offsets.view(num_h, 1, 1, 1) + torch.arange(block_size, device=device).view(
        1, 1, block_size, 1
    )
    c = w_offsets.view(1, num_w, 1, 1) + torch.arange(block_size, device=device).view(
        1, 1, 1, block_size
    )
    r = r.expand(num_h, num_w, block_size, block_size).to(torch.int)
    c = c.expand(num_h, num_w, block_size, block_size).to(torch.int)
    batch_idx = torch.arange(batch_size, device=device).view(batch_size, 1, 1, 1, 1)
    r_exp = r.unsqueeze(0).expand(batch_size, num_h, num_w, block_size, block_size)
    c_exp = c.unsqueeze(0).expand(batch_size, num_h, num_w, block_size, block_size)
    a = dct_img[batch_idx, r_exp, c_exp]
    b_val = dct_img[batch_idx, r_exp, c_exp - block_size]
    c_val = dct_img[batch_idx, r_exp, c_exp + block_size]
    d_val = dct_img[batch_idx, r_exp - block_size, c_exp]
    e_val = dct_img[batch_idx, r_exp + block_size, c_exp]
    V = torch.sqrt((b_val + c_val - 2 * a) ** 2 + (d_val + e_val - 2 * a) ** 2)
    normalization = (height_block_num - 2) * (width_block_num - 2)
    V_average = V.sum(dim=(1, 2)) / normalization
    return V_average


def blockwise_dct(
    gray_imgs: "torch.Tensor",
    height_block_num: int,
    width_block_num: int,
    block_size: int = DEFAULT_BLOCK_SIZE,
):
    assert gray_imgs.dim() == 4, "Input tensor must have shape (B, 1, H, W)."
    batch_size, channel_size, *_ = gray_imgs.shape
    assert channel_size == 1, "Input tensor must have shape (B, 1, H, W)."
    if (
        gray_imgs.shape[-2] < height_block_num * block_size
        or gray_imgs.shape[-1] < width_block_num * block_size
    ):
        raise ValueError(
            f"Invalid image dimensions. Image must be at least {height_block_num * block_size} x {width_block_num * block_size} because of number of blocks and block size."
        )
    blocks = gray_imgs.unfold(-2, block_size, block_size).unfold(
        -1, block_size, block_size
    )
    blocks = blocks.contiguous().view(batch_size, -1, block_size, block_size)
    dct_blocks_flat: torch.Tensor = dct_2d(blocks, norm="ortho")
    dct_blocks = dct_blocks_flat.view(
        batch_size, height_block_num, width_block_num, block_size, block_size
    )
    dct_blocks = dct_blocks.permute(0, 1, 3, 2, 4).contiguous()
    dct_blocks = dct_blocks.view(
        batch_size, height_block_num * block_size, width_block_num * block_size
    )
    return dct_blocks


def rgb_to_grayscale(tensor):
    weights = torch.tensor([0.2989, 0.5870, 0.1140], device=tensor.device).view(
        1, 3, 1, 1
    )
    grayscale = (tensor * weights).sum(dim=1, keepdim=True)
    return grayscale


def calculate_image_blockiness(
    rgb_images: "torch.Tensor", block_size: int = DEFAULT_BLOCK_SIZE
):
    gray_images = rgb_to_grayscale(rgb_images)
    if not isinstance(gray_images, torch.Tensor):
        raise TypeError("gray_images must be a torch.Tensor.")
    if gray_images.dim() != 4:
        raise ValueError("Input tensor must have shape (B, 1, H, W).")
    height, width = gray_images.shape[-2:]
    if height < 4 or width < 4:
        raise ValueError(
            "Image height and width must be at least 4 pixels for offset calculation."
        )
    cal_height, cal_width, _, _ = calc_margin(height=height, width=width)
    height_block_num, width_block_num = (
        cal_height // block_size,
        cal_width // block_size,
    )
    gray_tensor_cut = gray_images[..., :cal_height, :cal_width]
    gray_offset = torch.zeros_like(gray_images)
    gray_offset[..., :-4, :-4] = gray_images[..., 4:, 4:]
    gray_offset = gray_offset[..., :cal_height, :cal_width]
    dct_imgs = blockwise_dct(
        gray_imgs=gray_tensor_cut,
        height_block_num=height_block_num,
        width_block_num=width_block_num,
        block_size=block_size,
    )
    dct_offset_imgs = blockwise_dct(
        gray_imgs=gray_offset,
        height_block_num=height_block_num,
        width_block_num=width_block_num,
        block_size=block_size,
    )
    v_average = calc_v_torch(
        dct_img=dct_imgs,
        height_block_num=height_block_num,
        width_block_num=width_block_num,
        block_size=block_size,
    )
    v_offset_average = calc_v_torch(
        dct_img=dct_offset_imgs,
        height_block_num=height_block_num,
        width_block_num=width_block_num,
        block_size=block_size,
    )
    epsilon = 1e-8
    d = torch.abs(v_offset_average - v_average) / (v_average + epsilon)
    d_sum = torch.sum(d, dim=(1, 2))
    return d_sum


# --- BlockinessThread ---
class BlockinessThread(IQANode):
    def __init__(
        self,
        img_dir,
        batch_size: int = 8,
        thread: float = 0.5,
        median_thread=0,
        move_folder: str | None = None,
        dataset=None,
    ):
        super().__init__(
            img_dir,
            batch_size,
            thread,
            median_thread,
            move_folder,
            None,
            reverse=True,
            dataset=dataset,
        )
        self.model = calculate_image_blockiness

    def forward(self, images):
        return self.model(images)


# --- HyperThread ---
from pyiqa import create_metric


class HyperThread(IQANode):
    def __init__(
        self,
        img_dir,
        batch_size: int = 8,
        thread: float = 0.5,
        median_thread=0,
        move_folder: str | None = None,
        dataset=None,
    ):
        super().__init__(
            img_dir,
            batch_size,
            thread,
            median_thread,
            move_folder,
            None,
            dataset=dataset,
        )
        self.model = create_metric("hyperiqa", device=self.device)

    def forward(self, images):
        return self.model(images)


# --- IC9600Thread and ICNet model (from archs/ICNet.py) ---
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
    def __init__(self, is_pretrain=True, size1=512, size2=256, device=None):
        super(ICNet, self).__init__()
        from torchvision.models import resnet18, ResNet18_Weights

        resnet18Pretrained1 = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        resnet18Pretrained2 = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        self.size1 = size1
        self.size2 = size2
        self.b1_1 = nn.Sequential(*list(resnet18Pretrained1.children())[:5])
        self.b1_1_slam = slam(32)
        self.b1_2 = list(resnet18Pretrained1.children())[5]
        self.b1_2_slam = slam(32)
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
        self.to_map_f = conv_bn_relu(256 * 2, 256 * 2)
        self.to_map_f_slam = slam(32)
        self.to_map = to_map(256 * 2)
        self.to_score_f = conv_bn_relu(256 * 2, 256 * 2)
        self.to_score_f_slam = slam(32)
        self.head = nn.Sequential(
            nn.Linear(256 * 2, 512), nn.ReLU(), nn.Linear(512, 1), nn.Sigmoid()
        )
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.device = device if device is not None else torch.device("cpu")
        self.to(self.device)

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
        # Ensure we return a tensor that can be indexed, not a 0-dim tensor
        if score.dim() == 0:
            score = score.unsqueeze(0)
        return score

    def body_forward(self, x1):
        b, c, h, w = x1.shape
        x1 = F.pad(x1, pad=(32, 32, 32, 32), mode="reflect")
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


def ic9600(device=None):
    try:
        import time

        start_time = time.time()

        # Load model without timeout (timeout parameter not supported in all PyTorch versions)
        state = torch.hub.load_state_dict_from_url(
            url="https://github.com/umzi2/Dataset_Preprocessing/releases/download/IC9600_duplicate/ic9600.pth",
            map_location=device if device is not None else "cpu",
            weights_only=True,
        )

        model = ICNet(device=device).eval()
        model.load_state_dict(state)

        load_time = time.time() - start_time
        print_success(f"IC9600 model loaded successfully in {load_time:.2f}s")
        return model
    except Exception as e:
        print_warning(f"Failed to load IC9600 model: {e}")
        print_warning("IC9600 scoring will be skipped.")
        return None


class IC9600Thread(IQANode):
    def __init__(
        self,
        img_dir,
        batch_size: int = 8,
        thread: float = 0.5,
        median_thread=0,
        move_folder: str | None = None,
        dataset=None,
    ):
        super().__init__(
            img_dir,
            batch_size,
            thread,
            median_thread,
            move_folder,
            None,
            dataset=dataset,
        )
        # Load IC9600 model with progress indication
        try:
            self.model = ic9600(device=self.device)
            if self.model is not None:
                from dataset_forge.utils.memory_utils import to_device_safe

                self.model = to_device_safe(self.model, self.device)
            else:
                self.model = None
        except Exception as e:
            print_warning(f"Failed to load IC9600 model: {e}")
            self.model = None

    def forward(self, images):
        if self.model is None:
            # Return placeholder scores if model failed to load
            return torch.ones(images.shape[0], device=self.device) * 0.5

        try:
            # Try GPU processing with mixed precision for better memory efficiency
            with torch.amp.autocast("cuda", enabled=True):
                scores = self.model.get_onlu_score(images)
                # Ensure we have a proper batch dimension
                if scores.dim() == 0:
                    scores = scores.unsqueeze(0)
                elif scores.dim() == 1 and scores.shape[0] != images.shape[0]:
                    # If we got a single score for a batch, repeat it
                    scores = scores.repeat(images.shape[0])
                return scores

        except RuntimeError as e:
            if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
                # CUDA memory error - fallback to CPU processing
                print_warning(
                    f"CUDA memory error in IC9600, falling back to CPU processing..."
                )
                try:
                    from dataset_forge.utils.memory_utils import clear_cuda_cache

                    clear_cuda_cache()

                    # Move model and images to CPU
                    cpu_model = self.model.cpu()
                    cpu_images = images.cpu()

                    # Process on CPU
                    with torch.no_grad():
                        scores = cpu_model.get_onlu_score(cpu_images)

                    # Move back to original device
                    cpu_model.to(self.device)

                    # Ensure we have a proper batch dimension
                    if scores.dim() == 0:
                        scores = scores.unsqueeze(0)
                    elif scores.dim() == 1 and scores.shape[0] != images.shape[0]:
                        scores = scores.repeat(images.shape[0])

                    # Move scores to original device
                    scores = scores.to(self.device)
                    return scores

                except Exception as cpu_error:
                    print_error(f"CPU fallback also failed: {cpu_error}")
                    # Return placeholder scores on error
                    return torch.ones(images.shape[0], device=self.device) * 0.5
            else:
                # Other runtime error
                print_warning(f"Error in IC9600 forward pass: {e}")
                return torch.ones(images.shape[0], device=self.device) * 0.5

        except Exception as e:
            print_warning(f"Error in IC9600 forward pass: {e}")
            # Return placeholder scores on error
            return torch.ones(images.shape[0], device=self.device) * 0.5


# ===================== End Inlined IQA Threads and Dependencies =====================


def get_optimal_batch_size(base_batch_size: int, device: str = "cuda") -> int:
    """Dynamically determine optimal batch size based on available GPU memory."""
    if device != "cuda" or not torch.cuda.is_available():
        return base_batch_size

    try:
        # Get GPU memory info
        total_memory = torch.cuda.get_device_properties(0).total_memory
        allocated_memory = torch.cuda.memory_allocated(0)
        free_memory = total_memory - allocated_memory

        # Convert to GB for easier calculation
        free_memory_gb = free_memory / (1024**3)

        # Adjust batch size based on available memory
        if free_memory_gb > 8:
            return min(base_batch_size, 16)  # Large memory: up to 16
        elif free_memory_gb > 4:
            return min(base_batch_size, 8)  # Medium memory: up to 8
        elif free_memory_gb > 2:
            return min(base_batch_size, 4)  # Low memory: up to 4
        else:
            return min(base_batch_size, 2)  # Very low memory: up to 2

    except Exception as e:
        print_warning(f"Could not determine optimal batch size: {e}")
        return min(base_batch_size, 4)  # Conservative fallback


# Helper for paired folder logic
def paired_filenames(hq_folder: str, lq_folder: str) -> List[str]:
    """Return list of filenames present in both HQ and LQ folders."""
    hq_files = set(os.listdir(hq_folder))
    lq_files = set(os.listdir(lq_folder))
    return sorted(list(hq_files & lq_files))


def safe_tensor_to_float(tensor):
    """Safely convert a tensor to float, handling both 0-dim and 1-dim tensors."""
    if hasattr(tensor, "item"):
        return float(tensor.item())
    elif hasattr(tensor, "__len__") and len(tensor) == 1:
        return float(tensor[0].item())
    else:
        return float(tensor)


def get_default_bhi_thresholds():
    """Get default BHI filtering thresholds from session state."""
    try:
        from dataset_forge.menus import session_state

        return {
            "blockiness": session_state.user_preferences["bhi_blockiness_threshold"],
            "hyperiqa": session_state.user_preferences["bhi_hyperiqa_threshold"],
            "ic9600": session_state.user_preferences["bhi_ic9600_threshold"],
        }
    except (ImportError, KeyError):
        # Fallback to hardcoded defaults if session state is not available
        return {
            "blockiness": 0.5,
            "hyperiqa": 0.5,
            "ic9600": 0.5,
        }


def get_bhi_preset_thresholds(preset_name: str = "moderate"):
    """Get BHI filtering thresholds for a specific preset."""
    try:
        from dataset_forge.menus import session_state

        presets = session_state.user_preferences["bhi_suggested_thresholds"]
        if preset_name in presets:
            return presets[preset_name]
        else:
            return presets["moderate"]  # Default to moderate if preset not found
    except (ImportError, KeyError):
        # Fallback presets if session state is not available
        fallback_presets = {
            "conservative": {"blockiness": 0.3, "hyperiqa": 0.3, "ic9600": 0.3},
            "moderate": {"blockiness": 0.5, "hyperiqa": 0.5, "ic9600": 0.5},
            "aggressive": {"blockiness": 0.7, "hyperiqa": 0.7, "ic9600": 0.7},
        }
        return fallback_presets.get(preset_name, fallback_presets["moderate"])


def run_bhi_filtering_with_preset(
    input_path: str,
    preset_name: str = "moderate",
    action: str = "move",
    batch_size: int = 8,
    paired: bool = False,
    lq_folder: Optional[str] = None,
    move_folder: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = True,
):
    """
    Run BHI filtering with a preset configuration.

    Args:
        input_path: Path to input folder
        preset_name: One of 'conservative', 'moderate', 'aggressive'
        action: 'move', 'delete', or 'report'
        batch_size: Batch size for processing
        paired: Whether processing paired HQ/LQ folders
        lq_folder: Path to LQ folder (if paired)
        move_folder: Destination for moved files
        dry_run: Whether to perform a dry run
        verbose: Whether to print progress

    Returns:
        Results dictionary from BHI filtering
    """
    thresholds = get_bhi_preset_thresholds(preset_name)
    return run_bhi_filtering(
        input_path=input_path,
        thresholds=thresholds,
        action=action,
        batch_size=batch_size,
        paired=paired,
        lq_folder=lq_folder,
        move_folder=move_folder,
        dry_run=dry_run,
        verbose=verbose,
    )


def run_bhi_filtering_with_defaults(
    input_path: str,
    action: str = "move",
    batch_size: int = 8,
    paired: bool = False,
    lq_folder: Optional[str] = None,
    move_folder: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = True,
):
    """
    Run BHI filtering with default thresholds from user preferences.

    Args:
        input_path: Path to input folder
        action: 'move', 'delete', or 'report'
        batch_size: Batch size for processing
        paired: Whether processing paired HQ/LQ folders
        lq_folder: Path to LQ folder (if paired)
        move_folder: Destination for moved files
        dry_run: Whether to perform a dry run
        verbose: Whether to print progress

    Returns:
        Results dictionary from BHI filtering
    """
    return run_bhi_filtering(
        input_path=input_path,
        thresholds=None,  # Will use defaults
        action=action,
        batch_size=batch_size,
        paired=paired,
        lq_folder=lq_folder,
        move_folder=move_folder,
        dry_run=dry_run,
        verbose=verbose,
    )


@monitor_all("run_bhi_filtering", critical_on_error=True)
def run_bhi_filtering(
    input_path: str,
    thresholds: Optional[Dict[str, float]] = None,
    action: str = "move",  # 'move', 'copy', 'delete', or 'report'
    output_folder: Optional[str] = None,
    batch_size: int = 8,
    paired: bool = False,
    lq_folder: Optional[str] = None,
    move_folder: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = True,
):
    """
    Run BHI filtering (Blockiness, HyperIQA, IC9600) on a folder or paired HQ/LQ folders.
    - input_path: single folder or HQ folder if paired=True
    - thresholds: dict with keys 'blockiness', 'hyperiqa', 'ic9600' (uses defaults if None)
    - action: 'move', 'copy', 'delete', or 'report'
    - output_folder: where to move/copy files (if action=='move' or 'copy')
    - batch_size: batch size for IQA threads
    - paired: if True, expects HQ/LQ folders
    - lq_folder: path to LQ folder (if paired)
    - move_folder: destination for moved/copied files (if action=='move' or 'copy')
    - dry_run: if True, only report what would happen
    - verbose: print progress
    """
    assert action in ("move", "copy", "delete", "report"), "Invalid action."

    # Use default thresholds if none provided
    if thresholds is None:
        thresholds = get_default_bhi_thresholds()
        if verbose:
            print_info(f"Using default thresholds: {thresholds}")

    assert all(
        k in thresholds for k in ("blockiness", "hyperiqa", "ic9600")
    ), "Thresholds must include all metrics."

    if paired:
        assert lq_folder is not None, "lq_folder required for paired mode."
        if verbose:
            print_info("Scanning paired folders for files...")
        files = paired_filenames(input_path, lq_folder)
        hq_folder = input_path
    else:
        # Only include files, not directories, and skip _bhi_filtered folder
        if verbose:
            print_info("Scanning input folder for files...")
        all_items = os.listdir(input_path)
        files = []
        for item in all_items:
            item_path = os.path.join(input_path, item)
            if os.path.isfile(item_path) and not item.startswith("_bhi_filtered"):
                files.append(item)
        files = sorted(files)
        hq_folder = input_path

    if verbose:
        print_info(f"Found {len(files)} files to process")

    # Prepare move/copy folders if needed
    if action in ("move", "copy"):
        # Use output_folder if provided, otherwise use move_folder, otherwise create timestamped folder
        if output_folder:
            move_folder = output_folder
        elif not move_folder:
            # Create a unique folder name to avoid conflicts
            import time

            timestamp = int(time.time())
            move_folder = os.path.join(hq_folder, f"_bhi_filtered_{timestamp}")

        os.makedirs(move_folder, exist_ok=True)
        if paired:
            lq_move_folder = os.path.join(lq_folder, f"_bhi_filtered_{timestamp}")
            os.makedirs(lq_move_folder, exist_ok=True)
        else:
            lq_move_folder = None
    else:
        move_folder = None
        lq_move_folder = None

    # Create shared dataset to avoid multiple file validations
    if verbose:
        print_info("Creating shared dataset...")
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    shared_dataset = ImageDataset(hq_folder, device)

    # Get optimal batch sizes based on available memory
    optimal_batch_size = get_optimal_batch_size(
        batch_size, "cuda" if torch.cuda.is_available() else "cpu"
    )
    ic9600_batch_size = min(optimal_batch_size, 4)  # Cap at 4 for IC9600

    if verbose:
        print_info(
            f"Using batch size: {optimal_batch_size} (IC9600: {ic9600_batch_size})"
        )
        if torch.cuda.is_available():
            total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            allocated_memory = torch.cuda.memory_allocated(0) / (1024**3)
            print_info(
                f"GPU Memory: {allocated_memory:.1f}GB used / {total_memory:.1f}GB total"
            )

    # Prepare IQA threads with shared dataset
    if verbose:
        print_info("Initializing IQA models...")

    ic9600_thread = IC9600Thread(
        hq_folder,
        batch_size=ic9600_batch_size,
        thread=thresholds["ic9600"],
        dataset=shared_dataset,
    )
    if verbose:
        print_success("✓ IC9600 model initialized")

    blockiness_thread = BlockinessThread(
        hq_folder,
        batch_size=optimal_batch_size,
        thread=thresholds["blockiness"],
        dataset=shared_dataset,
    )
    if verbose:
        print_success("✓ Blockiness model initialized")

    hyper_thread = HyperThread(
        hq_folder,
        batch_size=optimal_batch_size,
        thread=thresholds["hyperiqa"],
        dataset=shared_dataset,
    )
    if verbose:
        print_success("✓ HyperIQA model initialized")

    # Collect scores for all files
    results = {}
    metrics_and_threads = [
        ("ic9600", ic9600_thread),
        ("blockiness", blockiness_thread),
        ("hyperiqa", hyper_thread),
    ]

    if verbose:
        print_info(f"Processing order: IC9600 → Blockiness → HyperIQA")
        print_info(f"Using thresholds: {thresholds}")

    for metric, thread in metrics_and_threads:
        if verbose:
            print_info(f"Scoring with {metric}...")

        # Skip IC9600 if model failed to load
        if metric == "ic9600" and hasattr(thread, "model") and thread.model is None:
            if verbose:
                print_warning("Skipping IC9600 scoring (model failed to load)")
            for fname in files:
                if fname not in results:
                    results[fname] = {}
                results[fname][metric] = None
            continue

        scores = {}
        # Calculate total batches for proper progress tracking
        total_batches = len(thread.data_loader)
        if verbose:
            print_info(f"Processing {total_batches} batches for {metric}...")

        for batch_idx, (images, filenames) in enumerate(
            tqdm(
                thread.data_loader,
                disable=not verbose,
                desc=f"{metric} scoring",
                total=total_batches,
                unit="batch",
            )
        ):
            try:
                iqa = thread.forward(images)
                for idx, fname in enumerate(filenames):
                    scores[fname] = safe_tensor_to_float(iqa[idx])

                # Clear memory after each batch to prevent accumulation
                if (
                    metric == "ic9600" and batch_idx % 10 == 0
                ):  # Every 10 batches for IC9600
                    from dataset_forge.utils.memory_utils import (
                        clear_memory,
                        clear_cuda_cache,
                    )

                    clear_memory()
                    clear_cuda_cache()

            except Exception as e:
                if verbose:
                    print_error(f"Error processing batch {batch_idx} for {metric}: {e}")
                # Clear memory on error
                try:
                    from dataset_forge.utils.memory_utils import (
                        clear_memory,
                        clear_cuda_cache,
                    )

                    clear_memory()
                    clear_cuda_cache()
                except:
                    pass
                continue

        for fname in files:
            if fname not in results:
                results[fname] = {}
            results[fname][metric] = scores.get(fname, None)

    # Decide which files to filter
    to_filter = []
    for fname in files:
        s = results[fname]
        # If any metric is below threshold, filter
        # Only consider metrics that have valid scores (not None)
        should_filter = False
        if s["blockiness"] is not None and s["blockiness"] < thresholds["blockiness"]:
            should_filter = True
        if s["hyperiqa"] is not None and s["hyperiqa"] < thresholds["hyperiqa"]:
            should_filter = True
        if s["ic9600"] is not None and s["ic9600"] < thresholds["ic9600"]:
            should_filter = True

        if should_filter:
            to_filter.append(fname)

    # Perform action
    if verbose:
        # Fix action text for better display
        action_text = {
            "move": "moved",
            "copy": "copied",
            "delete": "deleted",
            "report": "reported",
        }.get(action, f"{action}d")
        print_info(f"{len(to_filter)} files will be {action_text}.")
    if action == "report" or dry_run:
        for fname in to_filter:
            print_info(f"Would {action} {fname} (scores: {results[fname]})")
        return results

    # Add progress tracking for file operations
    if verbose and len(to_filter) > 0:
        print_info(f"Performing {action} operations...")
        # Fix action text for progress bar
        action_ing = {"move": "moving", "copy": "copying", "delete": "deleting"}.get(
            action, f"{action}ing"
        )
        for fname in tqdm(to_filter, desc=f"{action_ing} files", unit="file"):
            src_hq = os.path.join(hq_folder, fname)
            if paired:
                src_lq = os.path.join(lq_folder, fname)
            try:
                if action == "move":
                    dst_hq = os.path.join(move_folder, fname)
                    shutil.move(src_hq, dst_hq)
                    if paired:
                        dst_lq = os.path.join(lq_move_folder, fname)
                        shutil.move(src_lq, dst_lq)
                elif action == "copy":
                    dst_hq = os.path.join(move_folder, fname)
                    shutil.copy2(src_hq, dst_hq)
                    if paired:
                        dst_lq = os.path.join(lq_move_folder, fname)
                        shutil.copy2(src_lq, dst_lq)
                elif action == "delete":
                    os.remove(src_hq)
                    if paired:
                        os.remove(src_lq)
            except Exception as e:
                if verbose:
                    print_error(f"Error processing {fname}: {e}")
                continue
    else:
        # Non-verbose processing
        for fname in to_filter:
            src_hq = os.path.join(hq_folder, fname)
            if paired:
                src_lq = os.path.join(lq_folder, fname)
            try:
                if action == "move":
                    dst_hq = os.path.join(move_folder, fname)
                    shutil.move(src_hq, dst_hq)
                    if paired:
                        dst_lq = os.path.join(lq_move_folder, fname)
                        shutil.move(src_lq, dst_lq)
                elif action == "copy":
                    dst_hq = os.path.join(move_folder, fname)
                    shutil.copy2(src_hq, dst_hq)
                    if paired:
                        dst_lq = os.path.join(lq_move_folder, fname)
                        shutil.copy2(src_lq, dst_lq)
                elif action == "delete":
                    os.remove(src_hq)
                    if paired:
                        os.remove(src_lq)
            except Exception as e:
                if verbose:
                    print_error(f"Error processing {fname}: {e}")
                continue

    if verbose:
        print_success(
            f"\nBHI filtering completed. Processed {len(files)} files, filtered {len(to_filter)} files."
        )
        if len(to_filter) > 0:
            print_info(
                f"Filtered files: {len(to_filter)}/{len(files)} ({len(to_filter)/len(files)*100:.1f}%)"
            )
        else:
            print_info("No files were filtered (all passed quality thresholds)")

    return results
