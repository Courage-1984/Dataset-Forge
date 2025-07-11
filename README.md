<h3 align="center">
  Dataset Forge
</h3>
<p align="center">
  <img src="https://pomf2.lain.la/f/2ulflln.png" width="300" alt="Dataset Forge Thumbnail"/>
  <!-- <img src="https://files.catbox.moe/9jaag6.png" width="300" alt="Dataset Forge Thumbnail Backup"/> -->
</p>
<div align="center">
  <img src="https://pomf2.lain.la/f/oyxcxpr.png" width="600" alt="Separator"/>
  <!-- <img src="https://files.catbox.moe/0fyb8o.png" width="600" alt="Separator Backup"/> -->
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
   git clone https://github.com/Courage-1984/Dataset-Forge.git
   cd Dataset-Forge
   ```

2. **Set up the environment:**

   ```bash
   # Create virtual environment with Python 3.12
   py -3.12 -m venv venv

   # Activate virtual environment
   venv\Scripts\activate

   # Install PyTorch with CUDA 12.1 support
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

   # Install other dependencies
   pip install -r requirements.txt
   ```

3. **Run the application:**

   You have two options:

   ```bash
   # Option 1: Run directly with Python
   py main.py
   ```

   ```bash
   # Option 2: Use the Windows batch file
   ./run.bat
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
- **Sketch/Line Art Extraction**: Find and extract sketches, drawings, and line art from images using a deep learning model ([Sketch-126-DomainNet](https://huggingface.co/prithivMLmods/Sketch-126-DomainNet)). Supports single folder or HQ/LQ pairs, with copy/move options and confidence threshold.

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
- **Parallel Processing**: High-performance multiprocessing and multithreading

### 🖥️ **Beautiful CLI Interface**

- **Catppuccin Mocha Theme**: Beautiful ANSI color scheme
- **Hierarchical Menus**: Intuitive 7-category main menu with logical sub-menus
- **Progress Tracking**: Progress bars, error handling, memory management
- **Smart Input**: Path history, favorites, and intelligent defaults
- **Parallel Processing**: Multiprocessing and multithreading for speed improvements

---

## 🎨 **Advanced Features**

### **AI-Powered Image Analysis**

#### **Sketch Extraction with Deep Learning**

- **Model**: [Sketch-126-DomainNet](https://huggingface.co/prithivMLmods/Sketch-126-DomainNet) from Hugging Face
- **Capabilities**: Detect and extract sketches, drawings, and line art from images
- **Features**: Configurable confidence thresholds, support for single folders and HQ/LQ pairs
- **Operations**: Copy or move detected sketches to separate directories
- **Performance**: GPU-accelerated inference with automatic memory management

#### **BHI Filtering - Multi-Metric Quality Assessment**

- **Blockiness Detection**: Identify compression artifacts using DCT analysis
- **HyperIQA**: Perceptual quality assessment using deep learning
- **IC9600**: Neural quality assessment with ICNet architecture
- **Preset Thresholds**: Pre-configured moderate, strict, and lenient filtering options
- **Custom Thresholds**: Adjustable parameters for fine-tuned quality control
- **Batch Processing**: Efficient GPU-accelerated processing of large datasets

#### **Advanced Tiling with AI Complexity Analysis**

- **IC9600 Complexity**: Neural network-based complexity assessment using ICNet
- **Laplacian Complexity**: Traditional complexity measure for comparison
- **BestTile Algorithm**: Dynamic tile selection based on image complexity
- **Adaptive Tiling**: Automatically adjust tile count based on image characteristics
- **Dual Strategy Support**: Choose between traditional and AI-powered tiling
- **Memory Optimization**: Efficient processing with automatic CUDA memory management

### **Advanced Processing & Transformation**

#### **Batch Operations Pipeline**

- **Dataset Splitting**: Split by count, percentage, or random selection
- **Dimension Filtering**: Remove images based on width/height thresholds
- **File Type Filtering**: Filter by specific image formats
- **Advanced Color Adjustments**: Precise control over brightness, contrast, saturation
- **Format Conversion**: PNG optimization, WebP conversion with quality control
- **HDR to SDR Conversion**: Multiple tone mapping algorithms (Hable, Reinhard, etc.)

#### **Upscaling with Advanced Model Support**

- **Spandrel Integration**: Support for various upscaling models and architectures
- **Chainner-ext Processing**: Advanced image processing with high-quality filters
- **Tile-Based Upscaling**: Configurable tile sizes for memory-efficient processing
- **Alpha Channel Handling**: Upscale, resize, or discard alpha channels
- **Precision Control**: FP32, FP16, and BF16 precision options
- **GPU Memory Management**: Automatic memory optimization for large images

#### **Image Sanitization & Security**

- **Steganography Detection**: Use steghide and zsteg to detect hidden data
- **ICC Profile Conversion**: Convert to sRGB for consistent color reproduction
- **Alpha Channel Removal**: Optional transparency channel removal
- **Metadata Scrubbing**: Comprehensive EXIF data removal
- **Dry Run Mode**: Preview changes before applying modifications
- **Security Analysis**: Comprehensive image security assessment

### **Memory & Performance Optimization**

#### **Advanced Memory Management**

- **CUDA Memory Management**: Automatic GPU memory cleanup and optimization
- **Context Managers**: Memory-safe operations for intensive processing
- **Safe Tensor Operations**: Device-agnostic tensor handling
- **Memory Monitoring**: Real-time memory usage tracking and optimization
- **Automatic Cleanup**: Memory cleanup after large operations
- **Memory Recommendations**: Intelligent suggestions for optimal settings

#### **Smart Parallel Processing**

- **Processing Type Selection**: Automatic choice between thread/process/sequential
- **Batch Processing**: Memory-efficient processing of large datasets
- **GPU Memory Fraction Control**: Configurable GPU memory allocation
- **Timeout Handling**: Graceful handling of long-running operations
- **Progress Tracking**: Real-time progress with memory usage monitoring
- **Error Recovery**: Robust error handling with automatic retry mechanisms

### **Advanced Configuration & Integration**

#### **External Tool Integration**

- **WTP Dataset Destroyer**: Full integration with advanced dataset processing
- **traiNNer-redux**: Seamless training pipeline integration
- **VapourSynth**: Required for getnative functionality
- **ExifTool**: Advanced metadata handling and manipulation
- **FFmpeg**: Video processing and HDR conversion capabilities

#### **Configuration Management**

- **HCL File Support**: WTP Dataset Destroyer configuration format
- **YAML Configuration**: traiNNer-redux training configurations
- **JSON Configuration**: Flexible project and model configurations
- **User Profile System**: Personalized settings, favorites, and presets
- **Community Links**: Curated resource collections and external tools
- **Configuration Validation**: Automatic validation of configuration files

### **Rich Reporting & Analysis**

#### **Advanced Reporting System**

- **HTML Report Templates**: Interactive reports with embedded visualizations
- **Quality Score Histograms**: Multi-metric quality assessment visualization
- **Class Balance Analysis**: Dataset composition and distribution analysis
- **Sample Image Generation**: Automatic sample selection for reports
- **Dimension Analysis**: Comprehensive size and aspect ratio reporting
- **Scale Relationship Detection**: HQ/LQ scale analysis and validation

#### **Advanced Analysis Features**

- **Native Resolution Detection**: Automatic detection of original image resolutions
- **Extreme Dimension Analysis**: Identification of unusually sized images
- **Aspect Ratio Testing**: Comprehensive aspect ratio validation
- **Scale Relationship Detection**: Automatic HQ/LQ scale factor detection
- **Outlier Detection**: Statistical analysis for anomalous images
- **Corruption Detection**: Comprehensive image integrity checking

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
- `bhi_filtering_actions.py` - Multi-metric quality assessment
- `tiling_actions.py` - Advanced AI-powered tiling
- `sketch_extraction_actions.py` - Deep learning sketch detection
- `sanitize_images_actions.py` - Image security and sanitization
- `operations_actions.py` - Advanced batch operations
- `imagededup_actions.py` - Advanced duplicate detection
- And more...

### **utils/** - Utilities

Reusable helper modules:

- `file_utils.py` - File operations and image type checks
- `input_utils.py` - Input handling and path management
- `printing.py` - Colorful output and formatting
- `color.py` - Catppuccin Mocha color constants
- `menu.py` - Menu rendering helpers
- `path_history.py` - Path history management
- `memory_utils.py` - Advanced memory management
- `parallel_utils.py` - Smart parallel processing
- `upscale_script.py` - Advanced upscaling utilities
- `ic9600_tiling.py` - AI-powered tiling utilities
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
    │   ├── sanitize_images_actions.py # Image sanitization
    │   ├── sketch_extraction_actions.py # Sketch detection
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
    │   ├── sanitize_images_menu.py  # Image sanitization
    │   ├── bhi_filtering_menu.py    # BHI filtering
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
    │   ├── memory_utils.py          # Memory management
    │   ├── parallel_utils.py        # Parallel processing
    │   ├── progress_utils.py        # Progress tracking
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
  - Find Native Resolution

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
- **Advanced Features**
  - Sketch/Line Art Extraction (AI-powered)
  - Image Sanitization & Security

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
- **Advanced Tools**
  - Image Sanitization
  - BHI Filtering
  - Community Links

#### ⚙️ System & Settings

- **Application Settings & Information**
  - Set Working Directories (HQ/LQ Folders)
  - User Profile Management
  - View Change/History Log
  - Links (Community & Personal)
- **Memory Management**
  - View Memory Information
  - Clear Memory & CUDA Cache
  - Memory Optimization Recommendations
- **Parallel Processing Configuration**
  - Configure Processing Type
  - Set GPU Memory Fraction
  - Adjust Batch Sizes

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

### Advanced Configuration Examples

#### HCL Configuration (WTP Dataset Destroyer)

```hcl
input = "./datasets/input"
output = "./datasets/output"
scale = 4
quality = 85
format = "jpg"
```

#### YAML Configuration (traiNNer-redux)

```yaml
name: my_model
scale: 4
datasets:
  train:
    name: DIV2K
    mode: LQGT
    dataroot_GT: ./datasets/GT
    dataroot_LQ: ./datasets/LQ
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
transformers  # For sketch extraction (Hugging Face models)
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

# Parallel processing
psutil
joblib

# Custom packages
pipeline
pepeline
pepedpid
```

### Advanced Dependencies

- **Spandrel & Chainner-ext**: Advanced model loading and image processing
- **Transformers**: Hugging Face models for sketch detection
- **VapourSynth**: Required for getnative functionality
- **ExifTool**: Advanced metadata handling
- **Steghide & zsteg**: Steganography detection

### Optional Dependencies

- **ExifTool**: For EXIF metadata handling
- **FFmpeg**: For video processing and HDR conversion
- **CUDA Toolkit**: For GPU acceleration
- **VapourSynth**: For getnative functionality

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

#### AI-Powered Dataset Curation

1. **Sketch Extraction**: Use deep learning to extract sketches and line art
2. **BHI Filtering**: Apply multi-metric quality assessment
3. **Advanced Tiling**: Use AI-powered complexity analysis for optimal tiling
4. **Image Sanitization**: Remove metadata and detect hidden content
5. **Advanced Deduplication**: Use ImageDedup with multiple hash methods

#### Advanced Processing Pipeline

1. **Batch Operations**: Split datasets by count or percentage
2. **Format Conversion**: Optimize PNG files and convert to WebP
3. **HDR Processing**: Convert HDR images to SDR with tone mapping
4. **Memory Optimization**: Use GPU memory management for large datasets
5. **Parallel Processing**: Leverage smart processing type selection

---

## 🔧 Advanced Features

### DPID (Degradation Process for Image Downscaling)

Multiple implementations for realistic image degradation:

- **BasicSR DPID**: Industry-standard implementation
- **OpenMMLab DPID**: Research-focused implementation
- **Phhofm DPID**: Custom implementation

### BHI Filtering

Quality assessment using multiple metrics:

- **Blockiness**: Detect compression artifacts using DCT analysis
- **HyperIQA**: Perceptual quality assessment using deep learning
- **IC9600**: Neural quality assessment with ICNet architecture
- **Preset Thresholds**: Pre-configured moderate, strict, and lenient filtering options
- **Custom Thresholds**: Adjustable parameters for fine-tuned quality control

### Advanced Tiling

Intelligent image tiling with complexity analysis:

- **Laplacian Complexity**: Traditional complexity measure
- **IC9600 Complexity**: Neural complexity assessment using ICNet
- **BestTile Algorithm**: Optimal tile selection based on image complexity
- **Dynamic Tiling**: Automatic adjustment of tile count based on complexity
- **Memory Optimization**: Efficient processing with automatic CUDA memory management

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
- **Debug Features**: Directory content analysis and troubleshooting

### Memory Management System

Professional-grade memory optimization:

- **CUDA Memory Management**: Automatic GPU memory cleanup and optimization
- **Context Managers**: Memory-safe operations for intensive processing
- **Safe Tensor Operations**: Device-agnostic tensor handling
- **Memory Monitoring**: Real-time memory usage tracking
- **Automatic Cleanup**: Memory cleanup after large operations
- **Optimization Recommendations**: Intelligent suggestions for optimal settings

### Parallel Processing System

Smart parallel processing with automatic optimization:

- **Processing Type Selection**: Automatic choice between thread/process/sequential
- **Batch Processing**: Memory-efficient processing of large datasets
- **GPU Memory Fraction Control**: Configurable GPU memory allocation
- **Timeout Handling**: Graceful handling of long-running operations
- **Progress Tracking**: Real-time progress with memory usage monitoring
- **Error Recovery**: Robust error handling with automatic retry mechanisms

---

## 🐛 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**

   - Reduce batch sizes in settings
   - Use CPU-only mode for large datasets
   - Process images in smaller batches
   - Enable memory optimization features

2. **Missing Dependencies**

   - Run `pip install -r requirements.txt`
   - Install PyTorch with correct CUDA version
   - Install ExifTool for metadata features
   - Install VapourSynth for getnative functionality

3. **Path Issues**

   - Use absolute paths for large datasets
   - Check file permissions
   - Ensure paths don't contain special characters

4. **Performance Issues**
   - Use SSD storage for better I/O
   - Increase RAM if available
   - Use GPU acceleration when possible
   - Configure parallel processing settings
   - Enable memory optimization features

### Getting Help

- Check the operation logs in the System & Settings menu
- Review the comprehensive validation reports
- Use the built-in help system in each menu
- Check memory management recommendations
- Review parallel processing configuration

---

## 🤝 Contributing

Dataset Forge is designed with a modular architecture for easy contribution:

1. **Add new actions**: Create new files in `dataset_forge/actions/`
2. **Add new menus**: Create new files in `dataset_forge/menus/`
3. **Add new utilities**: Create new files in `dataset_forge/utils/`
4. **Follow coding standards**: Use the established patterns and conventions
5. **Test thoroughly**: Ensure all features work with memory management and parallel processing
6. **Document features**: Add comprehensive documentation for new capabilities

### Development Guidelines

- Follow the modular architecture patterns
- Use centralized memory management utilities
- Implement parallel processing for performance
- Follow the Catppuccin Mocha color scheme
- Include comprehensive error handling
- Add progress tracking for long operations
- Document all public functions with Google-style docstrings
