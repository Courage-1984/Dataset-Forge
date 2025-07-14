[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Usage Guide

(Include the full "Usage Examples" and "Menu Structure" sections from the original README here, preserving formatting and navigation.)

## Using the System Monitoring Menu

The System Monitoring menu provides live resource usage, analytics, error tracking, health checks, and background task management:

1. Select '🖥️ System Monitoring' from the main menu.
2. Features available:
   - **Live Resource Usage**: View CPU, GPU, RAM, and disk usage for all processes/threads.
   - **Performance Analytics**: See live and session analytics for all major operations.
   - **Error Summaries**: Review error logs and summaries, with notifications for critical errors.
   - **Health Checks**: Run automated checks for RAM, disk, CUDA, Python version, and permissions.
   - **Background Task Management**: List, pause, resume, or kill subprocesses/threads.
   - **Persistent Logs**: All analytics and errors are saved to ./logs/ for later review.
   - **Notifications**: Critical errors trigger sound/visual notifications.
   - **Audio error feedback**: All user-facing errors trigger an error sound (error.mp3) for immediate notification.

See the [Advanced Features](advanced.md) for more details on configuration and integration.

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

---

## Using Content-Based Image Retrieval (CBIR) for Duplicates

1. Navigate to the main menu, then Dataset Management > Clean & Organize > CBIR (Semantic Duplicate Detection).
2. Choose your workflow: single-folder or HQ/LQ pair.
3. Select the embedding model: CLIP (recommended), ResNet, or VGG.
4. Set the similarity threshold (default: 0.92 for cosine similarity).
5. Choose an action:
   - **Find**: List groups of semantically similar images.
   - **Remove**: Delete all but one image in each group.
   - **Move**: Move duplicates to a specified folder.
   - **Copy**: Copy duplicates to a specified folder.
6. Review the summary of affected files after each operation.

CBIR supports GPU acceleration and is optimized for large datasets. For advanced options, see the advanced features documentation.

## Menu Timing & Profiling

Whenever you load a menu or submenu in Dataset Forge, you will see a timing print in the CLI, such as:

    ⏱️ Loaded dataset_management_menu in 0.123 seconds.

This print uses the Catppuccin Mocha color scheme for clarity and consistency.

All menu load times are recorded. To view a summary of all menu/submenu load timings:

1. Go to the **System Monitoring** menu from the main menu.
2. Select **"⏱️ View Menu Load Times"**.
3. You will see a table of all menu/submenu load times for your session.

This helps you identify slow-loading menus and optimize your workflow.

## Menu Navigation: Robust Pattern Everywhere

All menus and submenus now use a robust, standardized menu loop pattern:

- You select an option; the system looks up the action and calls it if callable.
- This ensures every menu and submenu works as intended, with no redraw bugs or dead options.
- Navigation is now consistent and reliable everywhere in the CLI.

For more details, see [docs/features.md](features.md) and [docs/advanced.md](advanced.md).

## Running Tests

Dataset Forge includes a comprehensive automated test suite. To run all tests:

1. Activate your virtual environment:
   ```sh
   venv312\Scripts\activate
   ```
2. Run all automated tests from the project root:
   ```sh
   pytest
   ```

Manual/script-style tests (for BHI filtering and pepeline) can be run directly:

```sh
python tests/test_bhi_filtering.py
python tests/test_pepeline.py
```

The test suite covers:

- CLI entry and menu navigation
- Menu timing/profiling
- Error feedback (including audio)
- Memory management and parallel processing
- File and image utilities
- Robust handling of Unicode, subprocess, and Windows-specific issues

See the [README.md](../README.md) and [features.md](features.md) for more details on test coverage and philosophy.
