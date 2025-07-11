<h3 align="center">
  Dataset Forge
</h3>
<p align="center">
  <img src="Dataset_Forge_thumb.png" width="300" alt="Dataset Forge Thumbnail"/>
</p>
<div align="center">
  <img src="https://pomf2.lain.la/f/oyxcxpr.png" width="600"/>
</div>

<p align="center"><i>The all-in-one, modular image dataset utility for ML, with a focus on HQ/LQ image pairs for SISR and general computer vision. CLI-first, highly extensible, and packed with advanced tools for dataset curation, analysis, transformation, and validation.</i></p>

---

## ✨ TL;DR

> **Dataset Forge** is a comprehensive Python CLI utility for managing, analyzing, and transforming image datasets—especially High-Quality (HQ) and Low-Quality (LQ) pairs for super-resolution and related ML tasks. It features a beautiful Catppuccin Mocha-themed interface, deep validation, and 40+ powerful operations organized in an intuitive hierarchical menu system.

---

## 🚀 Quick Start

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd Dataset-Forge
   ```

2. **Windows (Recommended):**

   ```bash
   # Run the automated installer
   install.bat
   ```

3. **Manual Installation:**

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate

   # Install PyTorch with CUDA support (if available)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

   # Install other dependencies
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   # Windows:
   run.bat
   # Or manually:
   python main.py
   ```

---

## 🪄 Features

### 🎯 **Core & Configuration**

- **Multi-format config support**: JSON, YAML, HCL
- **External tool integration**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer), [traiNNer-redux](https://github.com/the-database/traiNNer-redux)
- **Model management**: List, select, and run upscaling with trained models
- **Validation tools**: Validate HQ/LQ and validation datasets from config
- **Built-in config editors** for .hcl and .yml files
- **User profiles**: Save favorites, presets, and quick access paths

### 📂 **Dataset Management**

- **Dataset Creation**: Multiscale dataset generation (DPID), video frame extraction, image tiling
- **Dataset Operations**: Combine, split, extract random pairs, shuffle datasets
- **HQ/LQ Pair Management**: Manual pairing, fuzzy matching, scale correction
- **Clean & Organize**: Visual deduplication, hash-based deduplication, ImageDedup advanced duplicate detection, batch renaming
- **Orientation Organization**: Sort by landscape/portrait/square
- **Size Filtering**: Remove small/invalid image pairs

### 🔍 **Analysis & Validation**

- **Comprehensive Validation**: Progressive dataset validation suite
- **Rich Reporting**: HTML/Markdown reports with plots and sample images
- **Quality Scoring**: Automated dataset quality assessment (NIQE, etc.)
- **Issue Detection**: Corruption detection, misalignment detection, outlier detection
- **Property Analysis**: Consistency checks, aspect ratio testing, dimension reporting
- **BHI Filtering**: Blockiness, HyperIQA, IC9600 quality assessment
- **Scale Detection**: Find and test HQ/LQ scale relationships

### ✨ **Image Processing & Augmentation**

- **Basic Transformations**: Downsampling (DPID, OpenCV, PIL), HDR to SDR conversion, grayscale conversion, alpha channel removal
- **Color & Tone Adjustments**: Brightness, contrast, hue, saturation adjustments
- **Metadata Tools**: EXIF scrubbing, ICC to sRGB conversion
- **Augmentation Pipeline**: Custom transformation recipes, data augmentation
- **Advanced Tiling**: BestTile with Laplacian/IC9600 complexity analysis

### 🚀 **Training & Inference**

- **Config Management**: Add, load, edit, and validate configuration files
- **Model Integration**: Run traiNNer-redux, list/run upscaling models
- **Dataset Validation**: Validate training and validation datasets from config
- **External Tools**: Integration with WTP Dataset Destroyer

### 🛠️ **Utilities**

- **Visual Comparison**: Side-by-side comparisons, animated GIF comparisons
- **Folder Comparison**: Find missing files between folders
- **Compression Tools**: Image compression, directory archiving
- **Path History**: Smart path management with history and favorites

### 🖥️ **Beautiful CLI Interface**

- **Catppuccin Mocha Theme**: Beautiful ANSI color scheme
- **Hierarchical Menus**: Intuitive 7-category main menu with logical sub-menus
- **Progress Tracking**: Progress bars, error handling, memory management
- **Smart Input**: Path history, favorites, and intelligent defaults

---

## 🏗️ Modular Architecture

Dataset Forge uses a clean, modular architecture for maintainability and extensibility:

### **menus/** - UI Layer

Thin UI layers for each menu category. Only handles user interaction and delegates to actions.

### **actions/** - Business Logic

Core business logic grouped by domain:

- `analysis_actions.py` - Dataset analysis and validation
- `dataset_actions.py` - Dataset operations and management
- `transform_actions.py` - Image transformations and processing
- `config_actions.py` - Configuration management
- `comparison_actions.py` - Visual comparison tools
- `metadata_actions.py` - EXIF and ICC tools
- `report_actions.py` - Rich reporting functionality
- `user_profile_actions.py` - User profile management
- And more...

### **utils/** - Utilities

Reusable helper modules:

- `file_utils.py` - File operations and image type checks
- `input_utils.py` - Input handling and path management
- `printing.py` - Colorful output and formatting
- `color.py` - Catppuccin Mocha color constants
- `menu.py` - Menu rendering helpers
- `path_history.py` - Path history management
- And more...

### **dpid/** - DPID Implementations

Multiple DPID (Degradation Process for Image Downscaling) implementations:

- `basicsr_dpid.py` - BasicSR DPID implementation
- `openmmlab_dpid.py` - OpenMMLab DPID implementation
- `phhofm_dpid.py` - Phhofm's DPID implementation

---

## 📚 Project Structure

```text
Dataset-Forge/
├── main.py                           # Main CLI entry point
├── run.py                            # Runner script
├── install.py                        # Installation script
├── install.bat                       # Windows installer
├── run.bat                          # Windows runner
├── requirements.txt                  # Python dependencies
├── README.md                        # This file
├── MENU_RESTRUCTURE_SUMMARY.md      # Menu organization details
├── LICENSE                          # Creative Commons CC-BY-SA-4.0
├── Dataset_Forge_thumb.png          # Project thumbnail
├── configs/                         # Configuration files
│   ├── _example_config.json         # Example configuration
│   ├── _example_user_profile.json   # Example user profile
│   ├── _example_community_links.json # Example community links
│   └── ...                          # User configs (gitignored)
├── reports/                         # Report templates
│   └── templates/
│       ├── report_template.html.jinja
│       └── report_template.md.jinja
└── dataset_forge/                   # Core modules
    ├── __init__.py
    ├── actions/                     # Business logic (25+ files)
    │   ├── __init__.py
    │   ├── analysis_actions.py      # Dataset analysis & validation
    │   ├── dataset_actions.py       # Dataset operations
    │   ├── transform_actions.py     # Image transformations
    │   ├── config_actions.py        # Configuration management
    │   ├── comparison_actions.py    # Visual comparison tools
    │   ├── metadata_actions.py      # EXIF & ICC tools
    │   ├── report_actions.py        # Rich reporting
    │   ├── user_profile_actions.py  # User profile management
    │   ├── bhi_filtering_actions.py # Quality assessment
    │   ├── tiling_actions.py        # Advanced tiling
    │   ├── frames_actions.py        # Video frame extraction
    │   ├── augmentation_actions.py  # Data augmentation
    │   ├── visual_dedup_actions.py  # Visual deduplication
    │   ├── imagededup_actions.py    # ImageDedup integration
    │   ├── quality_scoring_actions.py # Quality scoring
    │   ├── outlier_detection_actions.py # Outlier detection
    │   ├── alpha_actions.py         # Alpha channel tools
    │   ├── corruption_actions.py    # Corruption detection
    │   ├── de_dupe_actions.py       # Hash-based deduplication
    │   ├── batch_rename_actions.py  # Batch renaming
    │   ├── hue_adjustment_actions.py # Color adjustments
    │   ├── orientation_organizer_actions.py # Orientation organization
    │   ├── ic9600_tiling_actions.py # IC9600 tiling
    │   ├── compress_actions.py      # Image compression
    │   ├── compress_dir_actions.py  # Directory compression
    │   ├── folder_compare_actions.py # Folder comparison
    │   ├── exif_scrubber_actions.py # EXIF scrubbing
    │   ├── operations_actions.py    # Batch operations
    │   ├── correct_hq_lq_pairing_actions.py # HQ/LQ pairing
    │   ├── dataset_ops_actions.py   # Dataset operations
    │   └── settings_actions.py      # Settings management
    ├── menus/                       # UI layer (15+ files)
    │   ├── __init__.py
    │   ├── main_menu.py             # Main menu
    │   ├── dataset_management_menu.py # Dataset management
    │   ├── analysis_validation_menu.py # Analysis & validation
    │   ├── image_processing_menu.py # Image processing
    │   ├── training_inference_menu.py # Training & inference
    │   ├── utilities_menu.py        # Utilities
    │   ├── system_settings_menu.py  # System settings
    │   ├── user_profile_menu.py     # User profile
    │   ├── visual_dedup_menu.py     # Visual deduplication
    │   ├── imagededup_menu.py       # ImageDedup menu
    │   ├── correct_hq_lq_pairing_menu.py # HQ/LQ pairing
    │   ├── compress_menu.py         # Compression
    │   ├── compress_dir_menu.py     # Directory compression
    │   ├── links_menu.py            # Community links
    │   ├── history_log_menu.py      # History logs
    │   └── session_state.py         # Session state
    ├── utils/                       # Utilities (12+ files)
    │   ├── __init__.py
    │   ├── file_utils.py            # File operations
    │   ├── input_utils.py           # Input handling
    │   ├── printing.py              # Output formatting
    │   ├── color.py                 # Color constants
    │   ├── menu.py                  # Menu rendering
    │   ├── path_history.py          # Path history
    │   ├── history_log.py           # Operation logging
    │   ├── image_ops.py             # Image operations
    │   ├── dpid_phhofm.py           # DPID utilities
    │   ├── ic9600_tiling.py         # IC9600 utilities
    │   ├── upscale_script.py        # Upscaling utilities
    │   └── logging_utils.py         # Logging utilities
    └── dpid/                        # DPID implementations
        ├── __init__.py
        ├── basicsr_dpid.py          # BasicSR DPID
        ├── openmmlab_dpid.py        # OpenMMLab DPID
        └── phhofm_dpid.py           # Phhofm DPID
```

---

## 🎮 Menu Structure

The application features an intuitive hierarchical menu system:

### Main Menu (7 Categories)

```
[ 1 ] 📂 Dataset Management     (Create, build, and modify dataset structures)
[ 2 ] 🔍 Analysis & Validation  (Inspect quality, find issues, and generate reports)
[ 3 ] ✨ Image Processing       (Apply transformations and create variations)
[ 4 ] 🚀 Training & Inference   (Manage configs and run models)
[ 5 ] 🛠️ Utilities             (Comparison, compression, and other tools)
[ 6 ] ⚙️ System & Settings     (Application settings, user profiles, and logs)
[ 0 ] 🚪 Exit
```

### Detailed Sub-Menu Structure

#### 📂 Dataset Management

- **Dataset Creation & Modification**
  - Create Multiscale Dataset (DPID)
  - Extract Frames from Video
  - Image Tiling (BestTile, IC9600)
- **Combine or Split Datasets**
  - Combine Multiple Datasets
  - Split and Adjust Dataset
- **Manage HQ/LQ Pairs**
  - Create/Correct Manual Pairings
  - Find Pairs with Fuzzy Matching
  - Extract Random Pairs
  - Shuffle Image Pairs
- **Clean & Organize**
  - Visual De-duplication (CLIP/LPIPS)
  - De-Duplicate (File Hash)
  - ImageDedup - Advanced Duplicate Detection
  - Batch Rename
  - Remove Image Pairs by Size
  - Organize by Orientation

#### 🔍 Analysis & Validation

- **Dataset Analysis & Reporting**
  - Run Comprehensive Validation Suite
  - Generate Detailed Report (HTML/Markdown)
  - Automated Dataset Quality Scoring
- **Find & Fix Issues**
  - Verify & Fix Image Corruption
  - Find Misaligned Image Pairs
  - Find Outliers & Anomalies
  - Find Images with Alpha Channel
- **Analyze Properties**
  - Check Dataset Consistency
  - Check/Test Aspect Ratios
  - Find & Test HQ/LQ Scale
  - Report Image Dimensions
  - BHI Filtering Analysis

#### ✨ Image Processing & Augmentation

- **Basic Transformations**
  - Downsample Images (DPID, OpenCV, PIL)
  - Convert HDR to SDR
  - Convert to Grayscale
  - Remove Alpha Channel
- **Color & Tone Adjustments**
  - General Color/Tone Adjustments
  - Hue/Brightness/Contrast
- **Metadata**
  - Scrub EXIF Data
  - Convert ICC Profile to sRGB
- **Augmentation**
  - Run Augmentation Pipeline/Recipes
  - Apply Custom Transformations

#### 🚀 Training & Inference

- **Manage Config Files (.hcl, .yml)**
  - Add/Load Config File
  - Edit Config File
  - View Config Info
- **Validate Dataset from Config**
  - Validate Training HQ/LQ Dataset
  - Validate Validation HQ/LQ Dataset
- **Run Training / Models**
  - Run traiNNer-redux
  - List/Run Upscale with Model
  - Run wtp_dataset_destroyer

#### 🛠️ Utilities

- **Compare Images / Folders**
  - Create Comparison Images (Side-by-side)
  - Create GIF Comparison
  - Compare Folder Contents
- **Compress Images / Directory**
  - Compress Images
  - Compress Directory

#### ⚙️ System & Settings

- **Application Settings & Information**
  - Set Working Directories (HQ/LQ Folders)
  - User Profile Management
  - View Change/History Log
  - Links (Community & Personal)

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

### User Profile Example

```json
{
  "name": "default",
  "favorites": ["Dataset Management", "Analysis & Validation"],
  "presets": [
    {
      "name": "Quick Validation",
      "type": "validation",
      "settings": { "sample_count": 10, "max_quality_images": 50 }
    }
  ],
  "favorite_paths": ["/path/to/datasets", "/path/to/models"],
  "settings": {
    "default_tile_size": 512,
    "default_quality": 85
  }
}
```

---

## 🛠️ Requirements

### System Requirements

- **Python**: 3.8+
- **CUDA**: 12.1+ (for GPU acceleration)
- **RAM**: 8GB+ (16GB+ recommended for large datasets)
- **Storage**: SSD recommended for faster I/O

### Core Dependencies

```txt
# Core image processing
numpy<2
opencv-python
Pillow
tqdm
imageio
pyyaml
ffmpeg

# ML/AI frameworks
torch
torchvision
torchaudio
spandrel
spandrel_extra_arches
chainner-ext

# Quality assessment
pyiqa
timm
lpips
open-clip-torch

# Utilities
imagehash
PyExifTool
matplotlib
seaborn
jinja2
webbrowser
imagededup

# Custom packages
pipeline
pepeline
pepedpid
```

### Optional Dependencies

- **ExifTool**: For EXIF metadata handling
- **FFmpeg**: For video processing and HDR conversion
- **CUDA Toolkit**: For GPU acceleration

---

## 🚀 Usage Examples

### Basic Workflow

1. **Set up your workspace:**

   ```
   System & Settings → Set Working Directories
   ```

2. **Create a dataset:**

   ```
   Dataset Management → Create Dataset from Source → Create Multiscale Dataset
   ```

3. **Validate your dataset:**

   ```
   Analysis & Validation → Run Comprehensive Validation Suite
   ```

4. **Process images:**

   ```
   Image Processing → Basic Transformations → Downsample Images
   ```

5. **Generate a report:**
   ```
   Analysis & Validation → Generate Detailed Report
   ```

### Advanced Workflows

#### Super-Resolution Dataset Preparation

1. Create multiscale dataset with DPID
2. Run comprehensive validation
3. Apply quality filtering (BHI)
4. Generate training/validation splits
5. Create rich HTML report

#### Video Frame Extraction

1. Extract frames using deep embeddings
2. Filter by quality and similarity
3. Organize by orientation
4. Create HQ/LQ pairs
5. Validate alignment and scale

#### Dataset Augmentation

1. Load existing dataset
2. Apply augmentation pipeline
3. Quality assessment
4. Visual deduplication
5. Export augmented dataset

---

## 🔧 Advanced Features

### DPID (Degradation Process for Image Downscaling)

Multiple implementations for realistic image degradation:

- **BasicSR DPID**: Industry-standard implementation
- **OpenMMLab DPID**: Research-focused implementation
- **Phhofm DPID**: Custom implementation

### BHI Filtering

Quality assessment using multiple metrics:

- **Blockiness**: Detect compression artifacts
- **HyperIQA**: Perceptual quality assessment
- **IC9600**: Neural quality assessment

### Advanced Tiling

Intelligent image tiling with complexity analysis:

- **Laplacian Complexity**: Traditional complexity measure
- **IC9600 Complexity**: Neural complexity assessment
- **BestTile Algorithm**: Optimal tile selection

### Visual Deduplication

Deep learning-based duplicate detection:

- **CLIP Embeddings**: Fast semantic similarity
- **LPIPS**: Perceptual similarity
- **Configurable Thresholds**: Adjustable sensitivity

### ImageDedup Integration

Advanced duplicate detection using the imagededup library:

- **Multiple Hash Methods**: PHash, DHash, AHash, WHash
- **Configurable Thresholds**: Adjustable distance thresholds
- **HQ/LQ Pair Support**: Handle paired datasets
- **Visual Reports**: Generate duplicate analysis reports
- **Flexible Operations**: Find, remove, or move duplicates
- **Dry Run Mode**: Preview changes before applying

---

## 🐛 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**

   - Reduce batch sizes in settings
   - Use CPU-only mode for large datasets
   - Process images in smaller batches

2. **Missing Dependencies**

   - Run `pip install -r requirements.txt`
   - Install PyTorch with correct CUDA version
   - Install ExifTool for metadata features

3. **Path Issues**

   - Use absolute paths for large datasets
   - Check file permissions
   - Ensure paths don't contain special characters

4. **Performance Issues**
   - Use SSD storage for better I/O
   - Increase RAM if available
   - Use GPU acceleration when possible

### Getting Help

- Check the operation logs in the System & Settings menu
- Review the comprehensive validation reports
- Use the built-in help system in each menu

---

## 🤝 Contributing

Dataset Forge is designed with a modular architecture for easy contribution:

1. **Add new actions**: Create new files in `dataset_forge/actions/`
2. **Add new menus**: Create new files in `dataset_forge/menus/`
3. **Add new utilities**: Create new files in `dataset_forge/utils/`
4. **Follow the architecture**: Keep UI, business logic, and utilities separate

### Development Setup

```bash
git clone <repository-url>
cd Dataset-Forge
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

---

## 💜 Credits

- Thanks [Kim2091](https://github.com/Kim2091)❤️ for [helpful-scripts](https://github.com/Kim2091/helpful-scripts)
- Thanks [umzi2](https://github.com/umzi2)❤️ for [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer) & [Dataset_Preprocessing](https://github.com/umzi2/Dataset_Preprocessing)
- Thanks [the-database](https://github.com/the-database)❤️ for [traiNNer-redux](https://github.com/the-database/traiNNer-redux)
- Thanks [Phhofm](https://github.com/Phhofm)❤️ for [sisr](https://github.com/Phhofm/sisr)

---

## 📄 License

**Creative Commons Attribution Share Alike 4.0 International (CC-BY-SA-4.0)**

This license allows you to:

- Share: Copy and redistribute the material in any medium or format
- Adapt: Remix, transform, and build upon the material
- Attribution: You must give appropriate credit
- Share Alike: If you remix, transform, or build upon the material, you must distribute your contributions under the same license

---

<p align="center">
  <b>Enjoy your dataset journey! 🚀</b>
</p>
