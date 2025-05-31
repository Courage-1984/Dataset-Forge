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

> Dataset Forge is a Python CLI utility designed to help you efficiently manage, analyze, and transform image datasets, particularly High-Quality (HQ) and Low-Quality (LQ) pairs for machine learning tasks like super-resolution.

---

## 🪄 Features

- **HQ/LQ Dataset Management**: Analyze, validate, and manipulate paired high/low quality image datasets.
- **Powerful CLI Utility**: Interactive menu for all major dataset operations.
- ***[WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer) Integration*: Point to your local WTP path and run the main functionality.
- ***[traiNNer-redux](https://github.com/the-database/traiNNer-redux) Integration*: Point to your local traiNNer-redux path and run the main functionality.
- **Image Analysis**: Scale detection, consistency checks (formats, modes), detailed dimension stats, finding extreme dimensions, image integrity verification, misalignment detection using Phase Correlation, and a comprehensive HQ/LQ dataset report.
- **Batch Operations**: Efficiently process datasets with operations like Remove (by size, dimension, type), Extract Random pairs, Shuffle, Transform (Rotate, Flip, Brightness/Contrast/Sharpness), Color-Adjust (Contrast, Saturation, Brightness), Grayscale conversion, and Advanced Split/Adjust.
- **Corruption Handling**: Detect and *fix corrupted images*.
- **Alpha Channel Tools**: Find and remove alpha channels in bulk.
- **Comparisons & Visualizations**: Generate side-by-side and animated GIF/WebP comparisons.
- **Dataset Combination**: Merge multiple HQ/LQ datasets safely.
- **Upscaling Script**: Run advanced upscaling with custom models, tiling, alpha handling, and gamma correction.
- **External Tool Integration**: Directly run `wtp_dataset_destroyer` and `traiNNer-redux` from the menu when paths are specified in loaded `.hcl` and `.yml` config files respectively.
- **Video Frame Extraction**: Extract diverse frames from videos using deep embeddings (supporting ConvNeXt and DINOv2 models) based on a configurable distance threshold.
- **Configurable**: Supports `.json`, `.ini`, `.yml`, and `.hcl` configs for flexible workflows. Load, view, and use configurations via the interactive menu, including paths for datasets and external tools.

---

## 🧩 Project Structure

```text
Dataset-Forge/
├── main.py                # Main CLI utility
├── create_venv.py         # One-click venv + dependency setup
├── requirements.txt       # Python dependencies
├── configs/               # Example configs (ini, json)
├── dataset_forge/         # Core modules (analysis, tiling, upscaling, etc.)
└── README.md
```

---

## 🚀 Quickstart

### 1. Clone & Setup

```sh
git clone https://github.com/yourname/Dataset-Forge.git
cd Dataset-Forge
python create_venv.py
# Then activate:
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Run the Utility

```sh
python main.py
```

You'll be greeted with an immersive, cpomprehensive and interactive menu for all dataset operations!

---

## ⚙️ Configuration

- **Create a .json confige file** (`configs/model_Name_config.json`):

### Conveniant Menu option to create and populate per-model configuration files.

---

## 🛠️ Requirements

- Python 3.8+
- CUDA 12.1+ (for GPU acceleration)
- [See full list in requirements.txt](./requirements.txt):

---

## 📚 Key Modules

| Module              | Purpose                                      |
| ------------------- | -------------------------------------------- |
| `main.py`           | Interactive CLI utility                      |
| `analysis.py`       | Dataset analysis & validation                |
| `operations.py`     | Batch operations (split, shuffle, transform) |
| `tiling.py`         | Image tiling utilities                       |
| `comparison.py`     | Visual comparison tools                      |
| `alpha.py`          | Alpha channel detection/removal              |
| `combine.py`        | Merge multiple datasets                      |
| `corruption.py`     | Fix corrupted images                         |
| `frames.py`         | Video frame extraction                       |
| `upscale-script.py` | Advanced upscaling script                    |

---

## 💜 Credits

- Thanks [Kim2091](https://github.com/Kim2091)❤️ for [helpful-scripts](https://github.com/Kim2091/helpful-scripts); inspiring many functionality and for all their assistance.
- Thanks [umzi2](https://github.com/umzi2)❤️ for [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer); [Dataset_Preprocessing](https://github.com/umzi2/Dataset_Preprocessing); inspiring many functionality and for all their assistance.
- Thanks [the-database](https://github.com/the-database)❤️ for [traiNNer-redux](https://github.com/the-database/traiNNer-redux); [img-ab](https://github.com/the-database/img-ab); creating awesome software inspiring me to make something neat.

---

<p align="center">
  <img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/palette/mocha.png" width="120"/>
  <br/>
  <b>Enjoy your dataset journey!</b>
</p>

---

# License

**Creative Commons Attribution Share Alike 4.0 International (CC-BY-SA-4.0)**

---
