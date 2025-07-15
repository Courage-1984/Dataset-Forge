[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

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

- **Augmentation**: Flip, rotate, crop, color jitter, random erasing, and more
- **Tiling**: IC9600 and custom tiling for large images
- **Alpha Channel Handling**: Remove, preserve, or process alpha channels
- **Batch Processing**: Efficient batch operations for large datasets

## CBIR (Content-Based Image Retrieval) for Duplicates

- **Semantic Duplicate Detection**: Uses deep learning embeddings (CLIP, ResNet, VGG) to find images that are conceptually similar, even if visually transformed.
- **Feature Extraction**: Extracts high-dimensional feature vectors for each image using a pre-trained CNN (CLIP preferred, fallback to ResNet/VGG).
- **Similarity Search**: Computes cosine similarity or Euclidean distance between embeddings to identify near-duplicates.
- **ANN Indexing**: Uses approximate nearest neighbor (ANN) indexing for efficient search in large datasets.
- **Grouping & Actions**: Clusters images by semantic similarity and provides user options to find, remove, move, or copy duplicate groups.
- **GPU Acceleration**: Leverages GPU for fast embedding extraction and search.
- **Menu Integration**: Accessible from the Clean & Organize submenu under Dataset Management.

## Monitoring, Analytics & Error Tracking

- **Live Resource Monitoring**: Real-time CPU, GPU (NVIDIA), RAM, and disk usage for all processes/threads
- **Performance Analytics**: Decorator-based analytics for all major operations, with live and persistent session summaries
- **Error Tracking**: Logs errors to file and CLI, with summary granularity and critical error notifications (sound/visual)
- **Audio error feedback**: All user-facing errors trigger an error sound (error.mp3) for immediate notification.
- **Health Checks**: Automated checks for RAM, disk, CUDA, Python version, and permissions, with CLI output and recommendations
- **Background Task Management**: Registry of all subprocesses/threads, with CLI controls for pause/resume/kill and session-only persistence
- **Persistent Logging**: All analytics and errors are logged to ./logs/ for later review
- **Memory & CUDA Cleanup**: Automatic cleanup on exit/errors for all tracked processes/threads
- **Dedicated CLI Menu**: Access all monitoring, analytics, and management features from the System Monitoring menu

## Automated Test Suite

- Covers CLI entry, menu navigation, timing/profiling, error feedback (audio), memory management, parallel processing, and file/image utilities.
- Handles Unicode, subprocess, and Windows-specific edge cases.
- Includes manual/script-style tests for BHI filtering and pepeline (run directly).
- All tests pass as of this integration.

See [usage.md](usage.md#running-tests) for instructions on running tests.

---

For advanced implementation details, code patterns, and developer best practices, see [advanced.md](advanced.md) and [style_guide.md](style_guide.md).

- Dual native resolution detection: Choose between getnative (Python/VapourSynth) and resdet (C binary, fast, WSL integration on Windows). See [special_installation.md](special_installation.md) for install details.
