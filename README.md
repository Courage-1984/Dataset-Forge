<!-- <p align="center">
  <img src="https://pomf2.lain.la/f/k7pch.png" width="600" alt="Catppuccin Mocha Banner"/>
</p> -->

<h1 align="center">
  Dataset Forge
  </br>
  <img src="https://pomf2.lain.la/f/oyxcxpr.png" width="600"/>  
</h1>
<p align="center"><i>The all-in-one, modular image dataset utility for ML, with a focus on HQ/LQ image pairs for SISR and general computer vision. CLI-first, highly extensible, and packed with advanced tools for dataset curation, analysis, transformation, and validation.</i></p>

---

## ✨ TL;DR

> **Dataset Forge** is a comprehensive Python CLI utility for managing, analyzing, and transforming image datasets—especially High-Quality (HQ) and Low-Quality (LQ) pairs for super-resolution and related ML tasks. It features a beautiful Catppuccin Mocha-themed interface, deep validation, and 30+ powerful operations.

---

## 🪄 Features

### 🎯 **Core & Configuration**

- Multi-format config support: JSON, YAML, HCL
- External tool integration: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer), [traiNNer-redux](https://github.com/the-database/traiNNer-redux)
- Model management: List, select, and run upscaling with trained models
- Validation tools: Validate HQ/LQ and validation datasets from config
- Built-in config editors for .hcl and .yml

### 📊 **Dataset Analysis & Validation**

- Scale detection and testing for HQ/LQ pairs
- Consistency checks: format, mode, metadata
- Dimension reporting and histograms
- Extreme dimension detection
- Corruption and misalignment detection
- Comprehensive HQ/LQ dataset reports
- BHI filtering: Blockiness, HyperIQA, IC9600

### 🔧 **Dataset Operations**

- Remove small/invalid image pairs
- Extract random pairs, shuffle, split/adjust datasets
- Combine/merge datasets safely
- Batch renaming (single/paired)
- De-duplication (exact/near-duplicate detection)
- Orientation-based organization (landscape/portrait/square)
- Move/copy utilities

### 🎨 **Image Processing & Transformation**

- Color/tone/hue/brightness/contrast adjustments
- Grayscale conversion
- Remove/find alpha channels
- Custom transformation pipeline
- Downsampling (DPID, batch/single)
- HDR to SDR conversion

### 🧩 **Advanced Tiling & Multiscale**

- BestTile: Laplacian/IC9600 neural tiling
- Linear, random, overlap tiling (single/paired)
- Multiscale dataset generation (DPID downscale + tiling)
- Batch and parallel processing

### 🎬 **Video & Frame Extraction**

- Extract frames using deep embeddings (ConvNeXt, DINOv2, VIT variants)
- Multi-model, multi-distance support
- Batch and threshold controls

### 🚀 **Upscaling & Enhancement**

- Advanced upscaling with custom models (traiNNer-redux)
- Tiling, alpha handling, gamma correction
- Multi-format support: PNG, JPG, JPEG, WebP, TGA, BMP, TIFF
- Precision control: FP32, FP16, BF16

### 🗂️ **Metadata & ICC Tools**

- EXIF scrubbing (single/paired)
- ICC to sRGB conversion (preserves alpha, batch/folder support)

### 🖼️ **Visualization & Comparison**

- Side-by-side and animated (GIF/WebP) comparisons
- Folder comparison (show missing files)

### 🖥️ **Beautiful CLI Interface**

- Catppuccin Mocha ANSI color theme
- Interactive, logical menu system
- Progress bars, error handling, memory management

---

## 🧩 Project Structure

```text
Dataset-Forge/
├── main.py                    # Main CLI utility with interactive menu
├── requirements.txt           # Python dependencies
├── steps.txt                  # Setup instructions
├── configs/                   # Configuration files
├── dataset_forge/             # Core modules (see below)
│   ├── __init__.py
│   ├── actions/               # Business logic for each menu (see below)
│   │   ├── __init__.py
│   │   ├── analysis_actions.py
│   │   ├── batch_rename_actions.py
│   │   ├── comparison_actions.py
│   │   ├── config_actions.py
│   │   ├── dataset_actions.py
│   │   ├── metadata_actions.py
│   │   ├── settings_actions.py
│   │   ├── transform_actions.py
│   ├── utils/                 # Utility/helper modules (see below)
│   │   ├── __init__.py
│   │   ├── color.py
│   │   ├── file_utils.py
│   │   ├── input_utils.py
│   │   ├── logging_utils.py
│   │   ├── menu.py
│   │   ├── printing.py
│   ├── menus/                 # UI/menu modules (thin UI layer)
│   │   ├── __init__.py
│   │   ├── main_menu.py
│   │   ├── analysis_menu.py
│   │   ├── batch_rename_menu.py
│   │   ├── comparison_menu.py
│   │   ├── config_menu.py
│   │   ├── dataset_menu.py
│   │   ├── metadata_menu.py
│   │   ├── settings_menu.py
│   │   ├── transform_menu.py
│   ├── alpha.py               # Alpha channel utilities
│   ├── analysis.py            # Dataset analysis & validation
│   ├── analysis_ops.py        # Analysis operations
│   ├── batch_rename.py        # Batch renaming (legacy, now in actions)
│   ├── bhi_filtering.py       # BHI filtering (Blockiness, HyperIQA, IC9600)
│   ├── combine.py             # Dataset merging
│   ├── common.py              # (Legacy) Common utilities (now in utils)
│   ├── comparison.py          # Visual comparison tools (legacy, now in actions)
│   ├── config_menu.py         # (Legacy) Config menu logic
│   ├── corruption.py          # Corruption detection & fixing
│   ├── dataset_ops.py         # Dataset operations
│   ├── de_dupe.py             # Duplicate/near-duplicate detection
│   ├── dpid_phhofm.py         # DPID degradation kernels
│   ├── exif_scrubber.py       # EXIF metadata scrubbing (legacy, now in actions)
│   ├── folder_compare.py      # Folder comparison utilities
│   ├── frames.py              # Video frame extraction
│   ├── hue_adjustment.py      # Hue/brightness/contrast adjustment
│   ├── image_ops.py           # Image processing utilities (incl. ICCToSRGBConverter)
│   ├── io_utils.py            # (Legacy) I/O and menu helpers (now in utils)
│   ├── misalignment.py        # Misalignment detection
│   ├── move_copy.py           # Move/copy utilities
│   ├── multiscale.py          # Multiscale dataset generation
│   ├── operations.py          # Batch operations & transformations
│   ├── orientation_organizer.py # Orientation-based organization
│   ├── tiling.py              # Advanced image tiling (BestTile, etc.)
│   ├── tiling_grid.py         # Grid/random/overlap tiling
│   ├── upscale-script.py      # Advanced upscaling script
```

---

## 🏗️ Modular Architecture (NEW)

Dataset Forge now uses a clean, modular architecture for maintainability and extensibility:

- **menus/**: Thin UI layers for each menu (main, dataset, analysis, transform, metadata, comparison, config, settings, batch rename). These only handle user interaction and call into actions.
- **actions/**: Business logic for each menu, grouped by domain (e.g., `analysis_actions.py`, `transform_actions.py`). All core operations are here.
- **utils/**: Reusable utility/helper modules (e.g., file operations, input handling, logging, printing, color, menu rendering).
- **(legacy modules)**: Some older modules remain for backward compatibility or as lower-level helpers, but all new logic should go in actions/ or utils/.

**Benefits:**

- Clear separation of UI, business logic, and helpers/utilities
- Easier to test, maintain, and extend
- No more duplicated helpers or mixed UI/logic code

---

## 📚 Module Deep Dive (Updated)

### `menus/`

- UI entry points for each menu (main, dataset, analysis, transform, metadata, comparison, config, settings, batch rename). Only handles user interaction and delegates to actions.

### `actions/`

- `analysis_actions.py`: All dataset analysis and validation logic (reports, scale, consistency, misalignment, BHI, etc.)
- `transform_actions.py`: Image transformation logic (downsampling, HDR->SDR, color/tone, grayscale, alpha removal, custom transforms)
- `metadata_actions.py`: EXIF scrubbing, ICC to sRGB conversion
- `comparison_actions.py`: Visual comparison tools (side-by-side, GIF, folder compare)
- `batch_rename_actions.py`: Batch renaming logic (single/paired, prefix, padding, dry run)
- `settings_actions.py`: HQ/LQ folder management
- `config_actions.py`: Config file management, validation, model management
- `dataset_actions.py`: Dataset operations (combine, extract, shuffle, split, remove, dedupe, orientation, frames)

### `utils/`

- `file_utils.py`: File operations, image type checks, unique naming, etc.
- `input_utils.py`: Input helpers (folder selection, file operation choice, destination path, pair processing)
- `logging_utils.py`: Logging setup and uncaught exception handling
- `menu.py`: Menu rendering helpers
- `printing.py`: Colorful/sectioned printing helpers
- `color.py`: Catppuccin Mocha color constants

### (Legacy modules)

- Some modules like `common.py`, `io_utils.py`, `comparison.py`, `batch_rename.py`, `exif_scrubber.py` remain for backward compatibility or as low-level helpers, but all new logic is in `actions/` and `utils/`.

---

## ⚙️ Configuration

Dataset Forge supports multiple configuration formats:

### JSON Example

```json
{
  "model_name": "my_model",
  "scale": 2.0,
  "hq_path": "/path/to/hq/images",
  "lq_path": "/path/to/lq/images",
  "yml_path": "/path/to/trainner.yml",
  "hcl_path": "/path/to/wtp.hcl",
  "min_lq_w": 96,
  "min_lq_h": 96
}
```

- **Multi-format**: JSON, YAML, HCL
- **External tool paths**: WTP Dataset Destroyer, traiNNer-redux
- **Validation**: Path validation, pair checking
- **Model management**: Integration with traiNNer-redux experiment directories

---

## 🛠️ Requirements

- **Python**: 3.8+
- **CUDA**: 12.1+ (for GPU acceleration)
- **Core Dependencies**:
  - `numpy`, `opencv-python`, `Pillow`, `tqdm`, `imageio`, `pyyaml`, `ffmpeg`
  - `spandrel`, `spandrel_extra_arches`, `chainner-ext` (for advanced features)
  - `torch`, `torchvision`, `torchaudio` (for GPU/ML features)

---

## 💜 Credits

- Thanks [Kim2091](https://github.com/Kim2091)❤️ for [helpful-scripts](https://github.com/Kim2091/helpful-scripts)
- Thanks [umzi2](https://github.com/umzi2)❤️ for [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer)
- Thanks [the-database](https://github.com/the-database)❤️ for [traiNNer-redux](https://github.com/the-database/traiNNer-redux)
- Thanks [Phhofm](https://github.com/Phhofm)❤️ for [sisr](https://github.com/Phhofm/sisr)

---

<p align="center">
  <b>Enjoy your dataset journey!</b>
</p>

---

# License

**Creative Commons Attribution Share Alike 4.0 International (CC-BY-SA-4.0)**

---
