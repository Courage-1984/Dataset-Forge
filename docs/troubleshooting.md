[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Troubleshooting

This guide provides solutions to common issues in Dataset Forge. For advanced usage and developer troubleshooting, see [advanced.md](advanced.md).

---

## Menu Timing & Profiling Issues

**Problem:** Timing prints do not appear after loading a menu or submenu.

- Ensure you are running the latest version of Dataset Forge.
- Check that the menu or submenu uses the `time_and_record_menu_load` utility.
- "Back" and "Exit" options do not trigger timing prints.

## Menu Loop Issues

**Problem:** Errors occur when navigating menus (e.g., `TypeError: 'str' object is not callable`).

- All menu loops should check if the action is callable before calling it.
- Update your menu code to follow the robust menu loop pattern (see [style_guide.md](style_guide.md)).

**Problem:** Menu redraws repeatedly or submenus do not appear.

- Ensure the menu loop uses the robust pattern:
  - Get the user's choice (key) from `show_menu`.
  - Look up the action in the options dictionary.
  - Call the action if callable.

## CBIR Troubleshooting

- **Model loading errors**: Ensure torch, torchvision, and timm are installed and match your CUDA version.
- **GPU out of memory**: Lower the batch size or use CPU fallback. Close other GPU-intensive applications.
- **Slow performance**: Use GPU if available. For very large datasets, increase system RAM or process in smaller batches.

## Other Issues

- For monitoring/analytics issues, check the logs in the ./logs/ directory.
- If tests fail, ensure your environment matches the requirements and all dependencies are installed.

---

For further help, see [usage.md](usage.md) or contact the project maintainer.
