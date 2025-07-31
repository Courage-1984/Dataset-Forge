


### CBIR (Semantic Duplicate Detection)

1. Go to Dataset Management > Clean & Organize > CBIR.
2. Select your workflow: single-folder or HQ/LQ pair.
3. Choose the embedding model (CLIP recommended).
4. Set the similarity threshold (default: 0.92 for cosine similarity).
5. Choose an action: Find, Remove, Move, or Copy duplicates.
6. Review the summary of affected files after each operation.




## Native Resolution Detection (getnative & resdet)

The 'Find Native Resolution' feature allows you to estimate the original resolution of an image using two methods:

- **getnative** (Python, VapourSynth): Works natively on Windows and Linux. Requires VapourSynth and Python dependencies.
- **resdet** (C binary): Fast, supports PNG/JPEG. On Windows, the CLI will use WSL to run resdet if available. On Linux, resdet is run natively.

### How to Use
1. From the main menu, navigate to:
   - `Analysis & Validation` → `Analyze Properties` → `Find Native Resolution`
2. Choose whether to analyze a folder (HQ/LQ) or a single image.
3. Select your preferred method:
   - **getnative**: Requires VapourSynth and Python dependencies.
   - **resdet**: Requires resdet to be installed and available in your PATH (or in WSL PATH on Windows).

### Windows Users
- If you select resdet, the CLI will automatically use WSL if available.
- You must install resdet in your WSL environment and ensure it is in the WSL PATH.
- See [special_installation.md](special_installation.md) for detailed instructions.

### Linux Users
- Install resdet natively and ensure it is in your PATH.

### Troubleshooting
- If resdet is not found, you will receive a clear error message with installation instructions.




## Extending Dataset Forge

- **Add new menu actions**: Use the lazy import pattern (see [style_guide.md](style_guide.md)).
- **Add new analytics or monitoring hooks**: Decorate long-running or user-facing functions with the provided decorators.
- **Add new CBIR models**: Extend the CBIR system by adding new embedding models in the actions layer.



## Implementation Patterns (for Developers)

- **Robust Menu Loop**: All menus and submenus must use the robust menu loop pattern. See [style_guide.md](style_guide.md) for the required code snippet and rationale.
- **Timing & Profiling**: Use the centralized timing utility (`time_and_record_menu_load` in `utils/monitoring.py`) to wrap menu and submenu loads. Timing prints are shown to the user and aggregated for analytics. See [style_guide.md](style_guide.md) for best practices.
- **Lazy Imports**: Use `lazy_action()` and `lazy_menu()` helpers to defer heavy imports until needed. This keeps the CLI fast and memory-efficient.

## Advanced CBIR (Content-Based Image Retrieval)

- **Add new embedding models**: Extend `cbir_actions.py` with new model support.
- **Optimize similarity search**: Use ANN indexing for large datasets.
- **Batch actions**: Implement new batch actions (remove, move, copy) in the CBIR workflow.




## CBIR (Content-Based Image Retrieval) for Duplicates

- **Semantic Duplicate Detection**: Uses deep learning embeddings (CLIP, ResNet, VGG) to find images that are conceptually similar, even if visually transformed.
- **Feature Extraction**: Extracts high-dimensional feature vectors for each image using a pre-trained CNN (CLIP preferred, fallback to ResNet/VGG).
- **Similarity Search**: Computes cosine similarity or Euclidean distance between embeddings to identify near-duplicates.
- **ANN Indexing**: Uses approximate nearest neighbor (ANN) indexing for efficient search in large datasets.
- **Grouping & Actions**: Clusters images by semantic similarity and provides user options to find, remove, move, or copy duplicate groups.
- **GPU Acceleration**: Leverages GPU for fast embedding extraction and search.
- **Menu Integration**: Accessible from the Clean & Organize submenu under Dataset Management.




## 🧑‍💻 Static Analysis & Code Quality

Dataset Forge includes a comprehensive static analysis tool for maintainers and contributors:

- **Location:** `tools/find_code_issues/find_code_issues.py`
- **Checks:**
  - Unused (dead) code, functions, classes, and methods
  - Untested code (missing test coverage)
  - Functions/classes defined but never called
  - Test/code mapping (tests without code, code without tests)
  - Missing docstrings in public functions/classes/methods
  - Unused imports/variables, and more
- **How to run:**
  ```sh
  python tools/find_code_issues/find_code_issues.py [options]
  # Run with no options to perform all checks
  ```
- **Output:**
  - Overwrites files in `tools/find_code_issues/` on each run:
    - `find_code_issues.log` (raw output)
    - `find_code_issues_report.txt` (actionable summary)
    - `find_code_issues_view.txt` (detailed results)
- **Requirements:**
  - `pip install vulture pytest pytest-cov coverage pyan3 pyflakes`

See [docs/usage.md](docs/usage.md) and [docs/features.md](docs/features.md) for details.

---

## 🧩 Umzi's Dataset_Preprocessing (PepeDP-powered, July 2025)

Dataset Forge now features robust, testable integration with [PepeDP](https://github.com/umzi2/PepeDP) for Umzi's Dataset_Preprocessing workflows:

- **Best Tile Extraction**
- **Video Frame Extraction (Embedding Deduplication)**
- **Duplicate Image Detection and Removal**
- **Threshold-Based Image Filtering (IQA)**

All workflows are modular, testable, and use the latest PepeDP API. See [Features](docs/features.md#🧩-umzis-dataset_preprocessing-pepedp-powered-july-2025) and [Usage Guide](docs/usage.md#using-umzis-datasetpreprocessing-pepedp-powered) for details and examples.




## 🧪 Comprehensive Test Suite

Dataset Forge now includes a robust, cross-platform test suite covering all major features:

- Enhanced caching system (in-memory, disk, model, smart caching)
- DPID implementations (BasicSR, OpenMMLab, Phhofm)
- CBIR and deduplication workflows
- Report generation
- Audio feedback, memory, parallel, and progress utilities
- Session state, config, and error handling

**Run all tests:**

```sh
venv312\Scripts\activate
venv312\Scripts\python -m pytest --maxfail=5 --disable-warnings -v tests/
```

All new features and bugfixes must include appropriate tests. See [docs/features.md](docs/features.md) and [docs/usage.md](docs/usage.md) for details.


- Extract, view, edit, filter, and anonymize image metadata (EXIF, IPTC, XMP) with the Enhanced Metadata Management menu ([see docs](docs/features.md#🗂️-enhanced-metadata-management-new-july-2025)).
- Align images from two folders (flat or recursive) using projective transformation (SIFT+FLANN) with the '🧭 Align Images' menu option ([see docs](docs/features.md#🧭-align-images-batch-projective-alignment)).


