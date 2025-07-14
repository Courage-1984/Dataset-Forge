[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Troubleshooting

(Include the full "Troubleshooting" section from the original README here, preserving formatting and navigation.)

---

## Troubleshooting: Menu Timing & Profiling

**Problem:** Timing prints do not appear after loading a menu or submenu.

- Ensure you are running the latest version of Dataset Forge.
- Check that the menu or submenu uses the `time_and_record_menu_load` utility (see `utils/monitoring.py`).
- Make sure you are not selecting a "Back" or "Exit" option, which do not trigger timing prints.

**Problem:** Errors occur when navigating menus (e.g., `TypeError: 'str' object is not callable`).

- This usually means a menu action is not callable. All menu loops should check if the action is callable before calling it.
- Update your menu code to follow the latest menu loop pattern (see `docs/style_guide.md`).

If issues persist, consult the documentation or contact the project maintainer.

## Menu Loop Issues

If you encounter a menu that redraws repeatedly or a submenu that does not appear:

- Ensure the menu loop uses the robust pattern:
  - Get the user's choice (key) from `show_menu`.
  - Look up the action in the options dictionary.
  - Call the action if callable.
- This resolves most navigation and invocation issues in the CLI.

## CBIR Troubleshooting

- **Model loading errors**: Ensure torch, torchvision, and timm are installed and match your CUDA version. See requirements and install instructions.
- **GPU out of memory**: Lower the batch size or use CPU fallback. Close other GPU-intensive applications.
- **Slow performance**: Use GPU if available. For very large datasets, increase system RAM or process in smaller batches.
- **CLIP/ResNet/VGG not found**: Check requirements.txt and reinstall dependencies.
