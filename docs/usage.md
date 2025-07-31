[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Usage Guide

> **UI/UX Note:**  
> All CLI output in Dataset Forge uses the Catppuccin Mocha color scheme for a consistent, visually appealing experience. All prompts, menus, and progress bars are styled using the centralized color utilities.

## Quick Reference

- Clean, organize, and validate image datasets (HQ/LQ pairs, deduplication, quality scoring)
- Run advanced augmentations, transformations, and batch processing
- Analyze datasets and generate reports
- Integrate with external tools and leverage GPU acceleration
- Modular CLI with styled workflows and audio feedback

---

## Global Commands & Menu Navigation

Dataset Forge supports global commands for a seamless CLI experience:

- **help, h, ?** — Show context-aware help for the current menu, including navigation tips and available options.
- **quit, exit, q** — Instantly exit Dataset Forge from any menu, with full memory and resource cleanup.
- **0** — Go back to the previous menu (as before).
- **Ctrl+C** — Emergency exit with cleanup.

**User Experience:**

- After using `help`, the menu is automatically redrawn for clarity.
- All prompts and help screens use the Catppuccin Mocha color scheme.
- No raw print statements—output is always styled and consistent.
- Tests for CLI output are fully non-interactive.

**Example:**

```
Enter your choice: help
# ...help screen appears...
Press Enter to continue...
# Menu is redrawn
Enter your choice:
```

---

## Main Workflows

### 📂 Dataset Management

- **Create, combine, split, and shuffle datasets** from the Dataset Management menu.
- **Deduplicate, batch rename, and filter images** using Clean & Organize.
- **Align images** (Batch Projective Alignment) for HQ/LQ pairs or multi-source datasets.

### 🔍 Analysis & Validation

- **Validate datasets and HQ/LQ pairs** from the Analysis & Validation menu.
- **Run quality scoring and outlier detection** to assess dataset quality.
- **Generate HTML/Markdown reports** with plots and sample images.

### ✨ Augmentation & Processing

- **Apply augmentations, tiling, and batch processing** from the Augmentation and Image Processing menus.
- **Resave images, convert formats, and apply basic transformations** (crop, flip, rotate, grayscale, etc.).
- **Use advanced pipelines and recipes** for complex augmentation workflows.

### 🩺 Monitoring & Utilities

- **Monitor live resource usage, error tracking, and analytics** from the System Monitoring menu.
- **Manage cache** (view stats, clear, optimize) from System Settings → Cache Management.
- **Use utility scripts** in the `tools/` directory for environment setup, static analysis, and troubleshooting.

### 🧪 Testing & Developer Tools

- **Run all tests** with `python tools/run_tests.py` (see [getting_started.md](getting_started.md) for details).
- **Use static analysis tools** for code quality (`tools/find_code_issues/find_code_issues.py`).
- **Audit menu hierarchy** with `python tools/log_current_menu.py` for menu system analysis and improvement recommendations.
- **All major features provide public, non-interactive APIs** for programmatic use and testing.

---

## Example: Running a Workflow

```bash
dataset-forge
# or
py main.py
```

- Select a menu option (e.g., Dataset Management, Analysis & Validation).
- Follow the prompts for input/output folders, options, and confirmation.
- Progress bars and styled prompts guide you through each step.
- Audio feedback signals completion or errors.

---

## Tips & Best Practices

- Use the [Troubleshooting Guide](troubleshooting.md) if you encounter issues.
- For advanced configuration, see [Advanced Features](advanced.md).
- For a full list of CLI commands and options, see [Features](features.md).

---

## See Also

- [Getting Started](getting_started.md)
- [Features](features.md)
- [Advanced Features](advanced.md)
- [Troubleshooting](troubleshooting.md)
- [Style Guide](style_guide.md)

> For technical details, developer patterns, and advanced configuration, see [advanced.md](advanced.md).
