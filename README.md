<!-- <p align="center">
  <img src="https://pomf2.lain.la/f/k7pch.png" width="600" alt="Catppuccin Mocha Banner"/>
</p> -->

<h1 align="center">
  Dataset Forge
  </br>
  <img src="https://pomf2.lain.la/f/oyxcxpr.png" width="600"/>  
</h1>
<p align="center"><i>Your all-in-one image dataset utility helper for ML, with a focus on hq/lq image pairs intended for SISR.</i></p>

---

## ✨ TL;DR

> Dataset Forge is a comprehensive Python CLI utility designed to help you efficiently manage, analyze, and transform image datasets, particularly High-Quality (HQ) and Low-Quality (LQ) pairs for machine learning tasks like super-resolution. Features an immersive Catppuccin Mocha-themed interface with 28+ powerful operations.

---

## 🪄 Features

### 🎯 **Core & Configuration**

- **Multi-Format Config Support**: JSON, INI, YAML, and HCL configuration files
- **External Tool Integration**: Direct integration with [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer) and [traiNNer-redux](https://github.com/the-database/traiNNer-redux)
- **Model Management**: List and run upscaling with trained models from traiNNer-redux experiments
- **Validation Tools**: Validate HQ/LQ datasets and validation datasets from config files
- **Config Editor**: Built-in editors for .hcl and .yml configuration files

### 📊 **Dataset Analysis & Validation**

- **Scale Detection**: Find and test HQ/LQ scale ratios with tolerance checking
- **Consistency Analysis**: Check image formats, modes, and metadata consistency
- **Dimension Reporting**: Detailed statistics on image dimensions with histograms
- **Extreme Dimension Detection**: Find images with unusual sizes
- **Image Integrity Verification**: Detect and report corrupted images
- **Misalignment Detection**: Use Phase Correlation to find misaligned HQ/LQ pairs
- **Comprehensive Reports**: Generate full HQ/LQ dataset analysis reports

### 🔧 **Dataset Operations**

- **Smart Filtering**: Remove image pairs by size, dimensions, file type, or percentage
- **Random Extraction**: Extract random subsets of image pairs
- **Shuffling**: Randomize dataset order while maintaining pair integrity
- **Transformations**: Rotate, flip, adjust brightness/contrast/sharpness
- **Color Adjustments**: Fine-tune contrast, saturation, and brightness
- **Grayscale Conversion**: Convert datasets to grayscale
- **Advanced Splitting**: Split datasets with custom ratios and adjustments
- **Dataset Combination**: Safely merge multiple HQ/LQ datasets
- **Alpha Channel Tools**: Find and remove alpha channels in bulk
- **Corruption Handling**: Detect and fix corrupted images automatically
- **Format Optimization**: Optimize PNG files and convert to WebP

### 🎨 **Visualization & Comparison**

- **Side-by-Side Comparisons**: Create labeled HQ/LQ comparison images
- **Animated Comparisons**: Generate GIF/WebP animations with smooth transitions
- **Custom Effects**: Apply easing curves and visual effects to comparisons

### 🧩 **Advanced Image Processing**

- **BestTile Tiling**: Intelligent image tiling using Laplacian complexity or IC9600 neural network
- **DPID Degradation**: Apply realistic degradations using BasicSR and OpenMMLab kernels
- **Batch Processing**: Process single images or entire datasets
- **Multi-Strategy Tiling**: Choose between Laplacian complexity and neural network-based tiling

### 🎬 **Video Processing**

- **Frame Extraction**: Extract diverse frames using deep embeddings (ConvNeXt, DINOv2)
- **Multi-Model Support**: Use VITS, VITB, VITL, VITG models for frame selection
- **Distance-Based Selection**: Euclidean and cosine distance functions
- **Batch Processing**: Process videos in configurable batches
- **HDR to SDR**: Tone mapping for HDR video content using ffmpeg

### 🚀 **Upscaling & Enhancement**

- **Advanced Upscaling**: Custom models with tiling, alpha handling, and gamma correction
- **Multi-Format Support**: PNG, JPG, JPEG, WebP, TGA, BMP, TIFF
- **Precision Control**: FP32, FP16, and BF16 precision modes
- **Alpha Channel Handling**: Upscale, resize, or discard alpha channels
- **Gamma Correction**: Proper gamma handling for accurate color reproduction

### 🎨 **Beautiful Interface**

- **Catppuccin Mocha Theme**: Immersive color scheme with ANSI colors
- **Interactive Menu**: 28+ operations organized in logical sections
- **Progress Tracking**: Real-time progress bars and status updates
- **Error Handling**: Graceful error handling with detailed reporting
- **Memory Management**: Automatic GPU memory cleanup and optimization

---

## 🧩 Project Structure

```text
Dataset-Forge/
├── main.py                    # Main CLI utility with interactive menu
├── Best_Tile_EXAMPLE.py       # Standalone BestTile implementation example
├── requirements.txt           # Python dependencies
├── steps.txt                  # Setup instructions
├── configs/                   # Configuration files
│   └── test_config.json      # Example configuration
├── dataset_forge/            # Core modules
│   ├── analysis.py           # Dataset analysis & validation
│   ├── analysis_ops.py       # Analysis operations
│   ├── operations.py         # Batch operations & transformations
│   ├── tiling.py            # Advanced image tiling
│   ├── comparison.py        # Visual comparison tools
│   ├── alpha.py             # Alpha channel utilities
│   ├── combine.py           # Dataset merging
│   ├── corruption.py        # Corruption detection & fixing
│   ├── frames.py            # Video frame extraction
│   ├── upscale-script.py    # Advanced upscaling
│   ├── image_ops.py         # Image processing utilities
│   ├── io_utils.py          # I/O utilities
│   └── common.py            # Common utilities
└── dpid/                    # DPID degradation modules
    ├── BasicSR's_degradations.py    # BasicSR degradation kernels
    └── OpenMMLab's_blur_kernels.py  # OpenMMLab blur kernels
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

You'll be greeted with an immersive, comprehensive and interactive menu for all dataset operations!

  <img src="https://pomf2.lain.la/f/sjazby9a.png" width="600"/>

---

## 📋 Complete Menu Overview

### **Core & Config** (Options 0-00005)

- **0**: Add Config File - Create new configuration files
- **00**: Load Config File - Load existing configurations
- **000**: View Config Info - Display current configuration
- **0000**: Validate HQ/LQ Dataset from Config - Validate datasets using config
- **00000**: Validate Val Dataset HQ/LQ Pair - Validate validation datasets
- **00001**: Run wtp_dataset_destroyer - Execute WTP Dataset Destroyer
- **00002**: Edit .hcl config file - Edit HCL configuration files
- **00003**: Run traiNNer-redux - Execute traiNNer-redux training
- **00004**: Edit .yml config file - Edit YAML configuration files
- **00005**: List/Run Upscale with Model - Manage and run upscaling models

### **Dataset Analysis** (Options 1-8)

- **1**: Find HQ/LQ Scale - Detect scale ratios between HQ/LQ pairs
- **2**: Test HQ/LQ Scale - Test specific scale ratios with tolerance
- **3**: Check Image Consistency - Verify format and metadata consistency
- **4**: Report Image Dimensions - Generate detailed dimension statistics
- **5**: Find Extreme Dimensions - Identify unusually sized images
- **6**: Verify Image Integrity - Detect corrupted images
- **7**: Find Misaligned Images - Use Phase Correlation for alignment detection
- **8**: Generate Full HQ/LQ Dataset REPORT - Comprehensive dataset analysis

### **Dataset Operations** (Options 9-25)

- **9**: Remove Small Image Pairs - Filter by minimum size
- **10**: Extract Random Image Pairs - Create random subsets
- **11**: Shuffle Image Pairs - Randomize dataset order
- **12**: Transform Dataset - Apply rotations, flips, and adjustments
- **13**: Dataset Color Adjustment - Fine-tune color parameters
- **14**: Grayscale Conversion - Convert to grayscale
- **15**: Advanced Split/Adjust Dataset - Complex dataset splitting
- **16**: Combine Multiple Datasets - Merge datasets safely
- **17**: Find Alpha - Detect alpha channels
- **18**: Remove Alpha - Remove alpha channels
- **19**: Comparisons - Create side-by-side comparisons
- **20**: Fix Corrupted Images - Repair damaged images
- **21**: Optimize PNG - Compress PNG files
- **22**: Convert to WebP - Convert to WebP format
- **23**: BestTile Image Tiling - Advanced intelligent tiling
- **24**: Create HQ/LQ Animated gif/webp Comparisons - Animated comparisons
- **25**: Extract Frames - Extract video frames using deep embeddings

### **Image Processing** (Options 27)

- **27**: Downsample Images - Apply DPID degradations

### **Video Processing** (Options 28)

- **28**: HDR to SDR Tone Mapping - Convert HDR video to SDR

---

## ⚙️ Configuration

Dataset Forge supports multiple configuration formats:

### JSON Configuration Example

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

### Supported Configuration Features

- **Multi-format support**: JSON, INI, YAML, HCL
- **External tool paths**: WTP Dataset Destroyer and traiNNer-redux integration
- **Dataset validation**: Automatic path validation and pair checking
- **Model management**: Integration with traiNNer-redux experiment directories

---

## 🛠️ Requirements

- **Python**: 3.8+
- **CUDA**: 12.1+ (for GPU acceleration)
- **Core Dependencies**:
  - `numpy` - Numerical computing
  - `opencv-python` - Computer vision
  - `Pillow` - Image processing
  - `spandrel` & `spandrel_extra_arches` - Model loading
  - `chainner-ext` - Advanced image processing
  - `tqdm` - Progress bars
  - `imageio` - Video/image I/O
  - `pyyaml` - YAML configuration
  - `ffmpeg` - Video processing

---

## 📚 Key Modules Deep Dive

| Module              | Purpose                       | Key Features                                                        |
| ------------------- | ----------------------------- | ------------------------------------------------------------------- |
| `main.py`           | Interactive CLI utility       | 28+ operations, Catppuccin theme, external tool integration         |
| `analysis.py`       | Dataset analysis & validation | Scale detection, misalignment detection, comprehensive reporting    |
| `operations.py`     | Batch operations              | Transformations, filtering, color adjustments, format conversion    |
| `tiling.py`         | Advanced image tiling         | Laplacian complexity, IC9600 neural network, multi-strategy support |
| `comparison.py`     | Visual comparison tools       | Side-by-side, animated GIF/WebP, custom effects                     |
| `alpha.py`          | Alpha channel utilities       | Detection, removal, bulk processing                                 |
| `combine.py`        | Dataset merging               | Safe merging with validation                                        |
| `corruption.py`     | Corruption handling           | Detection and automatic fixing                                      |
| `frames.py`         | Video frame extraction        | Deep embeddings, multi-model support, distance-based selection      |
| `upscale-script.py` | Advanced upscaling            | Custom models, tiling, alpha handling, gamma correction             |
| `dpid/`             | DPID degradation              | BasicSR and OpenMMLab kernels for realistic degradation             |

---

## 🎯 Advanced Features

### **BestTile Tiling System**

- **Laplacian Complexity**: Traditional complexity-based tiling
- **IC9600 Neural Network**: Advanced neural network-based tiling
- **Multi-threading**: Process, thread, and sequential processing modes
- **Dynamic Tile Selection**: Intelligent tile size optimization
- **GPU Acceleration**: CUDA-optimized neural network inference

### **Video Frame Extraction**

- **Deep Embedding Models**: ConvNeXt and DINOv2 variants
- **Distance Functions**: Euclidean and cosine distance metrics
- **Batch Processing**: Configurable batch sizes and frame limits
- **Multi-Model Support**: Process with multiple models simultaneously
- **Threshold Control**: Fine-tune frame selection sensitivity

### **DPID Degradation Pipeline**

- **BasicSR Kernels**: Comprehensive blur and noise kernels
- **OpenMMLab Kernels**: Advanced degradation algorithms
- **Realistic Degradation**: Simulate real-world image degradation
- **Batch Processing**: Process entire datasets efficiently

### **External Tool Integration**

- **WTP Dataset Destroyer**: Direct execution from menu
- **traiNNer-redux**: Training pipeline integration
- **Model Management**: Automatic model discovery and execution
- **Configuration Sync**: Seamless config file management

---

## 💜 Credits

- Thanks [Kim2091](https://github.com/Kim2091)❤️ for [helpful-scripts](https://github.com/Kim2091/helpful-scripts); inspiring many functionality and for all their assistance.
- Thanks [umzi2](https://github.com/umzi2)❤️ for [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer); [Dataset_Preprocessing](https://github.com/umzi2/Dataset_Preprocessing); inspiring many functionality and for all their assistance.
- Thanks [the-database](https://github.com/the-database)❤️ for [traiNNer-redux](https://github.com/the-database/traiNNer-redux); [img-ab](https://github.com/the-database/img-ab); creating awesome software inspiring me to make something neat.

---

<p align="center">
  <b>Enjoy your dataset journey!</b>
</p>

---

# License

**Creative Commons Attribution Share Alike 4.0 International (CC-BY-SA-4.0)**

---
