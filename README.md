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
│   ├── alpha.py               # Alpha channel utilities
│   ├── analysis.py            # Dataset analysis & validation
│   ├── analysis_ops.py        # Analysis operations
│   ├── batch_rename.py        # Batch renaming (single/paired)
│   ├── bhi_filtering.py       # BHI filtering (Blockiness, HyperIQA, IC9600)
│   ├── combine.py             # Dataset merging
│   ├── common.py              # Common utilities
│   ├── comparison.py          # Visual comparison tools
│   ├── config_menu.py         # Config menu logic (add/load/view/validate configs, model management)
│   ├── corruption.py          # Corruption detection & fixing
│   ├── dataset_ops.py         # Dataset operations
│   ├── de_dupe.py             # Duplicate/near-duplicate detection
│   ├── dpid_phhofm.py         # DPID degradation kernels
│   ├── exif_scrubber.py       # EXIF metadata scrubbing
│   ├── folder_compare.py      # Folder comparison utilities
│   ├── frames.py              # Video frame extraction
│   ├── hue_adjustment.py      # Hue/brightness/contrast adjustment
│   ├── image_ops.py           # Image processing utilities (incl. ICCToSRGBConverter)
│   ├── io_utils.py            # I/O and menu helpers
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

## 🚀 Quickstart

### 1. Clone & Setup

```sh
git clone https://github.com/yourname/Dataset-Forge.git
cd Dataset-Forge
python -m venv venv

# Activate virtual environment:
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt

# For CUDA support (optional):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. Run the Utility

```sh
python main.py
```

You'll be greeted with an immersive, comprehensive, and interactive menu for all dataset operations!

---

## 📋 Complete Menu Overview

### **Main Menu**

- **1. DATASET**: Creation & management (multiscale, tiling, combine, extract, shuffle, split, remove, dedupe, rename, extract frames, orientation org)
- **2. ANALYSIS**: Reporting & validation (report, scale, consistency, dimensions, extremes, verify, fix, misalignment, alpha, BHI filtering)
- **3. TRANSFORM**: Image transformations (downsample, HDR->SDR, color/tone, hue/brightness/contrast, grayscale, remove alpha, custom transforms)
- **4. METADATA**: EXIF & ICC tools (scrub EXIF, ICC to sRGB)
- **5. COMPARISON**: Visual tools (side-by-side, GIF, folder compare)
- **6. CONFIG**: Configuration & model management (add, load, view, validate configs, run external tools, edit config files, model upscaling)
- **7. SETTINGS**: Set HQ/LQ folders
- **0. EXIT**

#### **CONFIG Menu**

- Add Config File: Create a new configuration interactively via CLI
- Load Config File: Load an existing config
- View Config Info: Display current config
- Validate HQ/LQ Dataset from Config: Validate datasets using config
- Validate Val Dataset HQ/LQ Pair: Validate validation datasets
- Run wtp_dataset_destroyer: Execute WTP Dataset Destroyer
- Edit .hcl config file: Edit HCL configuration files
- Run traiNNer-redux: Execute traiNNer-redux training
- Edit .yml config file: Edit YAML configuration files
- List/Run Upscale with Model: Manage and run upscaling models

#### **Submenus**

- Each main menu option opens a submenu with 10+ advanced operations. See in-app help for details.

---

## 📚 Module Deep Dive

### `alpha.py`

- Find and remove alpha channels in HQ/LQ datasets.
- Bulk processing, preserves alignment.

### `analysis.py` / `analysis_ops.py`

- Scale detection, consistency checks, dimension reporting, misalignment, and full dataset reports.
- Advanced validation and statistics.

### `batch_rename.py`

- Batch renaming for single or paired HQ/LQ folders.
- Supports custom prefixes, zero padding, dry run.

### `bhi_filtering.py`

- Blockiness, HyperIQA, and IC9600-based filtering.
- Move, delete, or report filtered images.

### `combine.py`

- Safely merge multiple HQ/LQ datasets.

### `common.py`

- Utility functions for file naming, etc.

### `comparison.py`

- Create side-by-side and animated (GIF/WebP) HQ/LQ comparisons.
- Custom effects, labels, and transitions.

### `corruption.py`

- Detect and fix corrupted images in bulk.

### `dataset_ops.py`

- Core dataset operations (filtering, extraction, etc).

### `de_dupe.py`

- Detect exact and near-duplicate images using multiple hash types.
- Move, copy, or delete duplicates.

### `dpid_phhofm.py`

- DPID degradation kernels for downsampling.

### `exif_scrubber.py`

- Remove EXIF metadata from images (single/paired).
- Uses ExifTool if available.

### `folder_compare.py`

- Compare two folders and report missing files.

### `frames.py`

- Extract frames from video using deep embeddings (ConvNeXt, DINOv2, VIT).
- Multi-model, multi-distance, batch support.

### `hue_adjustment.py`

- Batch hue, brightness, and contrast adjustment.
- Supports duplicates, real file names, paired folders.

### `image_ops.py`

- Image processing utilities (alpha removal, corruption fixing, color adjustment).
- **ICCToSRGBConverter**: Convert images/folders from ICC profile to sRGB, preserving alpha and structure.

### `io_utils.py`

- I/O helpers, menu utilities, file type checks.

### `misalignment.py`

- Detect misaligned HQ/LQ pairs using phase correlation.

### `move_copy.py`

- Move/copy files (single/paired, by % or extension).

### `multiscale.py`

- Multiscale dataset generation (DPID downscale, tiling, batch support).

### `operations.py`

- Batch operations: filtering, extraction, shuffling, splitting, color/tone, grayscale, optimization, format conversion, custom transforms.

### `orientation_organizer.py`

- Organize images by orientation (landscape, portrait, square).
- Copy/move, single or paired folders.

### `tiling.py`

- Advanced tiling: BestTile (Laplacian/IC9600), single/paired, multi-threaded.

### `tiling_grid.py`

- Grid, random, and overlap tiling (single/paired, batch support).

### `upscale-script.py`

- Advanced upscaling script for custom models (traiNNer-redux), with tiling, alpha, gamma, and precision control.

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

---

<p align="center">
  <b>Enjoy your dataset journey!</b>
</p>

---

# License

**Creative Commons Attribution Share Alike 4.0 International (CC-BY-SA-4.0)**

---
