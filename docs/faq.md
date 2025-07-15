[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Frequently Asked Questions (FAQ)

---

### What is Dataset Forge?

Dataset Forge is a modular Python CLI tool for managing, analyzing, and transforming image datasets, with a focus on HQ/LQ pairs for super-resolution and ML workflows.

### What platforms are supported?

- Windows (primary)
- Linux (tested)
- macOS is not officially supported but may work with some features disabled.

### What Python version is required?

Python 3.12+ is recommended. The project supports Python 3.8+ but is tested on 3.12.

### How do I install Dataset Forge and its dependencies?

See the [Quick Start](../README.md#quick-start) and [Special Installation Instructions](special_installation.md). Always install the correct CUDA-enabled torch/torchvision/torchaudio **before** running `pip install .`.

### Why do I need to install VapourSynth before getnative?

getnative depends on VapourSynth. If VapourSynth is not installed first, getnative will fail to import or function. See [special_installation.md](special_installation.md#vapoursynth--getnative-for-getnative-functionality).

### How do I fix python-magic errors on Windows?

You must copy the required DLLs from `assets/libmagicwin64-master.zip` to `C:/Windows/System32/`. See [special_installation.md](special_installation.md#python-magic-for-directory-utilities).

### How do I run the test suite?

Activate the virtual environment and run `pytest`. See [usage.md](usage.md#running-tests).

### What is CBIR for Duplicates?

CBIR (Content-Based Image Retrieval) for Duplicates uses deep learning models (CLIP, ResNet, VGG) to find images that are semantically similar, even if visually transformed. It extracts feature embeddings, computes similarity, and groups duplicates for easy management. See [features.md](features.md#cbir-content-based-image-retrieval-for-duplicates).

### How do I use the monitoring and analytics features?

Access the System Monitoring menu from the CLI to view live resource usage, error tracking, analytics, and health checks. See [features.md](features.md#monitoring-analytics--error-tracking).

### What should I do if I get CUDA or GPU errors?

- Ensure your CUDA and cuDNN versions match your PyTorch install.
- Close other GPU-intensive applications.
- Lower batch size or use CPU fallback if you run out of memory.
- See [troubleshooting.md](troubleshooting.md).

### What if a menu or feature is missing or crashes?

- Make sure you are running the latest version.
- Check the logs in the `./logs/` directory for error details.
- See [troubleshooting.md](troubleshooting.md) for solutions to common issues.

### How do I get help or report a bug?

Open an issue on GitHub or contact the project maintainer.

---

If your question is not answered here, check the [usage guide](usage.md), [troubleshooting guide](troubleshooting.md), or open an issue.
