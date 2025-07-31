# 🌀 pepedpid

**pepedpid** is a Rust implementation of Rapid, Detail-Preserving Image Downscaling (DPID), designed to be used as a Python library via rust-py bindings. It combines high performance with ease of use in Python projects, such as machine learning pipelines or image processing tasks.

# 🚀 Quick Start

Installation:
```bash
pip install pepeline pepedpid
```

Usage example:
```py
from pepeline import read, save, ImgFormat
from pepedpid import dpid_resize,cubic_resize

# Load an image in f32 format (normalized [0,1])
img = read("test.png", format=ImgFormat.F32)

# Apply DPID resizing
img_dpid = dpid_resize(img, 512, 512, 0.5)
img_matlab_bicubic = cubic_resize(img,512,512)
# Save the result
save(img_dpid, "img_dpid.png")
save(img_matlab_bicubic, "img_matlab_bicubic.png")
```

# ⚙️ Arguments for `dpid_resize`
```py
dpid_resize(input: np.ndarray, h: int, w: int, l: float) -> np.ndarray
```

## Parameters:

- `input` (`np.ndarray`) — input image of type `float32`, normalized in the range [0.0, 1.0]. Expected shape: `(H, W, C)`, where `C = 1` (grayscale) or `3` (RGB).

- `h` (`int`) — target height of the image.

- `w` (`int`) — target width of the image.

- `l` (`float`) — the λ coefficient, controlling the trade-off between smoothing and detail preservation:

    - `λ ≈ 0.0` — maximum smoothing, the image will be soft.

    - `λ ≈ 1.0` — maximum detail preservation, resulting in a sharp image.

    - **Recommended value**: `0.5` — balance between smoothness and sharpness.

## Returns:

- `np.ndarray` — the downscaled image (`float32`, range [0.0, 1.0], shape `(h, w, C)`).

