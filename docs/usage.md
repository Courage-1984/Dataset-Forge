[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Advanced Features](advanced.md)

# Usage Guide

(Include the full "Usage Examples" and "Menu Structure" sections from the original README here, preserving formatting and navigation.)

## Using the OpenModelDB Model Browser

The OpenModelDB Model Browser is available from the Training & Inference menu:

1. Select '🧠 OpenModelDB Model Browser'.
2. Choose between:
   - **Basic Menu (classic):** Hierarchical, emoji-rich menu system
   - **CLI-interactive (modern):** Arrow keys, live search, and dynamic actions (requires `questionary`)

### Features

- Browse, search, and filter models by tag, architecture, scale, or free text
- View model details, resources, and sample images
- Download models (with SHA256 verification, Google Drive/OneDrive/manual fallback)
- Test models on your images (with Spandrel/ONNX support)
- List and manage already downloaded models
- Open model page in your browser

### Downloading from OneDrive

If a model is hosted on OneDrive, you will be prompted to download it manually. The browser will open the link for you, and you should place the file in the indicated models directory.

### CLI-interactive Mode

- Use arrow keys and type to search models
- After selecting a model, choose actions: View Details, Download, Test, Open in Browser, or go back
- Requires `questionary` (install with `pip install questionary`)
