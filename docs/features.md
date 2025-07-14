[//]: # "Navigation"

[← Back to Main README](../README.md) | [Usage Guide](usage.md) | [Advanced Features](advanced.md)

# Features

## Core & Configuration

- **Multi-format config support**: JSON, YAML, HCL
- **External tool integration**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer), [traiNNer-redux](https://github.com/the-database/traiNNer-redux)
- **Model management**: List, select, and run upscaling with trained models
- **Validation tools**: Validate HQ/LQ and validation datasets from config
- **Built-in config editors** for .hcl and .yml files
- **User profiles**: Save favorites, presets, and quick access paths

## Dataset Management

- **Dataset Creation**: Multiscale dataset generation (DPID), video frame extraction, image tiling
- **Dataset Operations**: Combine, split, extract random pairs, shuffle datasets
- **HQ/LQ Pair Management**: Manual pairing, fuzzy matching, scale correction
- **Clean & Organize**: Visual deduplication, hash-based deduplication, ImageDedup advanced duplicate detection, batch renaming
- **Orientation Organization**: Sort by landscape/portrait/square
- **Size Filtering**: Remove small/invalid image pairs

## Analysis & Validation

- **Comprehensive Validation**: Progressive dataset validation suite
- **Rich Reporting**: HTML/Markdown reports with plots and sample images
- **Quality Scoring**: Automated dataset quality assessment (NIQE, etc.)
- **Issue Detection**: Corruption detection, misalignment detection, outlier detection
- **Property Analysis**: Consistency checks, aspect ratio testing, dimension reporting
- **BHI Filtering**: Blockiness, HyperIQA, IC9600 quality assessment
- **Scale Detection**: Find and test HQ/LQ scale relationships

## Image Processing & Augmentation

- **Basic Transformations**: Downsampling (DPID, OpenCV, PIL), HDR to SDR conversion, grayscale conversion, alpha channel removal
- **Color & Tone Adjustments**: Brightness, contrast, hue, saturation adjustments
- **Metadata Tools**: EXIF scrubbing, ICC to sRGB conversion
- **Augmentation Pipeline**: Custom transformation recipes, data augmentation
- **Advanced Tiling**: BestTile with Laplacian/IC9600 complexity analysis
- **Sketch/Line Art Extraction**: Find and extract sketches, drawings, and line art from images using a deep learning model ([Sketch-126-DomainNet](https://huggingface.co/prithivMLmods/Sketch-126-DomainNet)). Supports single folder or HQ/LQ pairs, with copy/move options and confidence threshold.

## Training & Inference

- **Config Management**: Add, load, edit, and validate configuration files
- **Model Integration**: Run traiNNer-redux, list/run upscaling models
- **Dataset Validation**: Validate training and validation datasets from config
- **External Tools**: Integration with WTP Dataset Destroyer

## Utilities

- **Visual Comparison**: Side-by-side comparisons, animated GIF comparisons
- **Folder Comparison**: Find missing files between folders
- **Compression Tools**: Image compression, directory archiving
- **Enhanced Directory Tree**: AI-powered directory visualization with emoji categorization, statistics, and multiple output formats
- **Path History**: Smart path management with history and favorites
- **Parallel Processing**: High-performance multiprocessing and multithreading

## Beautiful CLI Interface

- **Catppuccin Mocha Theme**: Beautiful ANSI color scheme
- **Hierarchical Menus**: Intuitive 7-category main menu with logical sub-menus
- **Progress Tracking**: Progress bars, error handling, memory management
- **Smart Input**: Path history, favorites, and intelligent defaults
- **Parallel Processing**: Multiprocessing and multithreading for speed improvements

---

# Advanced Features

## AI-Powered Image Analysis

### Sketch Extraction with Deep Learning

- **Model**: [Sketch-126-DomainNet](https://huggingface.co/prithivMLmods/Sketch-126-DomainNet) from Hugging Face
- **Capabilities**: Detect and extract sketches, drawings, and line art from images
- **Features**: Configurable confidence thresholds, support for single folders and HQ/LQ pairs
- **Operations**: Copy or move detected sketches to separate directories
- **Performance**: GPU-accelerated inference with automatic memory management

### BHI Filtering - Multi-Metric Quality Assessment

- **Blockiness Detection**: Identify compression artifacts using DCT analysis
- **HyperIQA**: Perceptual quality assessment using deep learning
- **IC9600**: Neural quality assessment with ICNet architecture
- **Preset Thresholds**: Pre-configured moderate, strict, and lenient filtering options
- **Custom Thresholds**: Adjustable parameters for fine-tuned quality control
- **Batch Processing**: Efficient GPU-accelerated processing of large datasets

### Advanced Tiling with AI Complexity Analysis

- **IC9600 Complexity**: Neural network-based complexity assessment using ICNet
- **Laplacian Complexity**: Traditional complexity measure for comparison
- **BestTile Algorithm**: Dynamic tile selection based on image complexity
- **Adaptive Tiling**: Automatically adjust tile count based on image characteristics
- **Dual Strategy Support**: Choose between traditional and AI-powered tiling
- **Memory Optimization**: Efficient processing with automatic CUDA memory management

## Advanced Processing & Transformation

### Batch Operations Pipeline

- **Dataset Splitting**: Split by count, percentage, or random selection
- **Dimension Filtering**: Remove images based on width/height thresholds
- **File Type Filtering**: Filter by specific image formats
- **Advanced Color Adjustments**: Precise control over brightness, contrast, saturation
- **Format Conversion**: PNG optimization, WebP conversion with quality control
- **HDR to SDR Conversion**: Multiple tone mapping algorithms (Hable, Reinhard, etc.)

### Upscaling with Advanced Model Support

- **Spandrel Integration**: Support for various upscaling models and architectures
- **Chainner-ext Processing**: Advanced image processing with high-quality filters
- **Tile-Based Upscaling**: Configurable tile sizes for memory-efficient processing
- **Alpha Channel Handling**: Upscale, resize, or discard alpha channels
- **Precision Control**: FP32, FP16, and BF16 precision options
- **GPU Memory Management**: Automatic memory optimization for large images

### Image Sanitization & Security

- **Steganography Detection**: Use steghide and zsteg to detect hidden data
- **ICC Profile Conversion**: Convert to sRGB for consistent color reproduction
- **Alpha Channel Removal**: Optional transparency channel removal
- **Metadata Scrubbing**: Comprehensive EXIF data removal
- **Dry Run Mode**: Preview changes before applying modifications
- **Security Analysis**: Comprehensive image security assessment

## Memory & Performance Optimization

### Advanced Memory Management

- **CUDA Memory Management**: Automatic GPU memory cleanup and optimization
- **Context Managers**: Memory-safe operations for intensive processing
- **Safe Tensor Operations**: Device-agnostic tensor handling
- **Memory Monitoring**: Real-time memory usage tracking and optimization
- **Automatic Cleanup**: Memory cleanup after large operations
- **Memory Recommendations**: Intelligent suggestions for optimal settings

### Smart Parallel Processing

- **Processing Type Selection**: Automatic choice between thread/process/sequential
- **Batch Processing**: Memory-efficient processing of large datasets
- **GPU Memory Fraction Control**: Configurable GPU memory allocation
- **Timeout Handling**: Graceful handling of long-running operations
- **Progress Tracking**: Real-time progress with memory usage monitoring
- **Error Recovery**: Robust error handling with automatic retry mechanisms

## Advanced Configuration & Integration

### External Tool Integration

- **WTP Dataset Destroyer**: Full integration with advanced dataset processing
- **traiNNer-redux**: Seamless training pipeline integration
- **VapourSynth**: Required for getnative functionality
- **ExifTool**: Advanced metadata handling and manipulation
- **FFmpeg**: Video processing and HDR conversion capabilities

### Configuration Management

- **HCL File Support**: WTP Dataset Destroyer configuration format
- **YAML Configuration**: traiNNer-redux training configurations
- **JSON Configuration**: Flexible project and model configurations
- **User Profile System**: Personalized settings, favorites, and presets
- **Community Links**: Curated resource collections and external tools
- **Configuration Validation**: Automatic validation of configuration files

## Rich Reporting & Analysis

### Advanced Reporting System

- **HTML Report Templates**: Interactive reports with embedded visualizations
- **Quality Score Histograms**: Multi-metric quality assessment visualization
- **Class Balance Analysis**: Dataset composition and distribution analysis
- **Sample Image Generation**: Automatic sample selection for reports
- **Dimension Analysis**: Comprehensive size and aspect ratio reporting
- **Scale Relationship Detection**: HQ/LQ scale analysis and validation

### Advanced Analysis Features

- **Native Resolution Detection**: Automatic detection of original image resolutions
- **Extreme Dimension Analysis**: Identification of unusually sized images
- **Aspect Ratio Testing**: Comprehensive aspect ratio validation
- **Scale Relationship Detection**: Automatic HQ/LQ scale factor detection
- **Outlier Detection**: Statistical analysis for anomalous images
- **Corruption Detection**: Comprehensive image integrity checking
