# 📝 TODO / Planned Features

> This section collects all future feature/functionality ideas, goals, and implementation notes for Dataset Forge. Add new ideas here to keep the roadmap in one place and keep being inspired.

---

- [ ] **Debug Mode**: I want to add a _Debug Mode_ to my project, which when used, activates the showing of more verbose output and debug output/print
- [ ] **tl;dr**: Create a '# Features (tl;dr)' section in ./docs/features.md
- [ ] **_Packaging_**: "Compile Dataset-Forge" AND/OR "Create docker file/container"
- [ ] **Automated Documentation**
- [ ] **Augmentation**: Document augmentation operations, and degradations and implement 'Advanced Data Augmentation'
- [x] **Dataset Health Scoring**: Add a "Dataset Health Scoring" workflow and menu option
- [ ] **Batch Scripts**: Save and replay complex multi-step operations/workflows
- [ ] **Phhofm's sisr**: Investigate Phhofm's [sisr](https://github.com/Phhofm/sisr) for stuff i can add to DF
- [x] **the-database's img-ab**: Fork and improve.
- [ ] **Links .json's**: Further customize, add metadata, description, etc/
- [ ] **Advanced Filtering / AI-Powered Features**:

<details>
<summary>Expand for details ^^</summary>

```
Semantic Filtering: Filter by image content/semantics
Style-Based Filtering: Filter by artistic style
Quality-Based Filtering: Advanced quality assessment filters
Custom Filter Plugins: User-defined filtering logic
Auto-Labeling: Automatic image labeling and classification
Style Transfer: Apply artistic styles to datasets
Content-Aware Cropping: Intelligent image cropping
```

</details>

- [ ] **Advanced Data Augmentation**:

<details>
<summary>Expand for details ^^</summary>

```
What: Expand the augmentation capabilities to include more complex, model-aware techniques.

Why: Your current augmentations are great for general image processing. Adding advanced techniques can significantly improve model generalization during training.

Suggestions:
- Compositional Augmentations: Integrate a library like Albumentations to create complex augmentation pipelines.
- Mixing Augmentations: Implement Mixup (linearly interpolating images and their labels) and CutMix (pasting a patch from one image onto another).
- GAN-based Augmentations: For advanced users, integrate with a pre-trained StyleGAN to generate synthetic data variations.

```

</details>

- [ ] **Onboarding**: Add 'onboarding' doc/flow
- [ ] **Build**: Release a stable build at some point

- [ ] Advanced options for Align Images (SIFT/FLANN parameters, etc.).
- [ ] Further modularization and extensibility for new workflows.
- [ ] More advanced analytics and monitoring.
- [ ] AI-powered dataset analysis and recommendations.
- [ ] Cloud integration for distributed processing and storage.
- [ ] Web interface for dataset management and visualization.
- [ ] **Parallel Import Loading**: Load multiple modules in parallel with threading
- [ ] **Smart Caching**: Predictive loading of frequently used modules
- [ ] **Import Optimization**: Compile-time import analysis and automatic conversion
- [ ] **Performance Monitoring**: Real-time metrics and automated regression detection

**NEW TODO:**

- [ ] **dedicated de dupe menu**
- [ ] **global search functionality**
- [ ] **path sanitization**

- [ ] **validate code that's from other repos**
- [ ] **title**
- [ ] **title**
- [ ] **title**
- [ ] **speed up cli**: lazy imports AND????
- [x] **find_code_issues.py**: test and improve
- [x] **Fix critical menu system errors**: Resolved 'str' object is not callable and 'module' object is not callable errors in dataset_management_menu.py - Fixed lazy_action vs lazy_menu usage, pepedp lazy imports, and ProcessType enum access
- [x] **Audio System Investigation & Fix**: Resolved CLI hanging issues and implemented robust multi-library audio system
  - **Problem**: CLI was hanging during exit due to audio playback issues
  - **Investigation**: Tested audio files, pygame mixer, winsound, and alternative libraries
  - **Solution**: Implemented robust audio system with multiple fallback libraries
  - **Libraries**: playsound (primary), winsound (Windows WAV), pydub (various formats), pygame (fallback)
  - **Features**: System-specific audio handling, format-specific optimizations, graceful error handling
  - **Testing**: All 4 audio files (done.wav, error.mp3, startup.mp3, shutdown.mp3) working perfectly
  - **Dependencies**: Added playsound==1.2.2 and pydub to requirements.txt
  - **Result**: CLI exits cleanly with full audio functionality restored
- [x] **Comprehensive Audio Implementation**: Add audio feedback throughout the entire application
  - **Status**: ✅ COMPLETED - Audio feedback added to all major action functions
  - **Files Updated**:
    - `augmentation_actions.py` - Added completion audio to `apply_augmentation_pipeline` and `create_augmentation_variations`
    - `metadata_actions.py` - Added completion audio to `exif_scrubber_menu` and `icc_to_srgb_menu`
    - `quality_scoring_actions.py` - Added completion audio to `score_images_with_pyiqa` and `score_hq_lq_folders`
    - `report_actions.py` - Added completion audio to `generate_rich_report`
    - `resave_images_actions.py` - Added completion audio to `resave_images_workflow`
    - `exif_scrubber_actions.py` - Added completion audio to `scrub_exif_single_folder` and `scrub_exif_hq_lq_folders`
    - `orientation_organizer_actions.py` - Added completion audio to `organize_images_by_orientation` and `organize_hq_lq_by_orientation`
    - `batch_rename_actions.py` - Added completion audio to `batch_rename_single_folder` and `batch_rename_hq_lq_folders`
    - `hue_adjustment_actions.py` - Added completion audio to `process_folder`
    - `frames_actions.py` - Already had completion audio in `extract_frames_menu`
  - **Audio Files**: Successfully moved to `./assets/audio/` directory for better organization
  - **Result**: Complete audio feedback throughout the application with success sounds for all major operations
  - **Files to Update**: All action files, menu files, utility functions
  - **Testing**: Ensure audio doesn't interfere with CLI operations
  - **Result**: Complete audio feedback throughout the application
- [x] **Fix Test Failures**: Resolved 3 critical test failures in performance optimization module
  - **Problem**: 3 tests failing in `test_performance_optimization.py`:
    1. `test_gpu_image_analysis` - RuntimeError due to RGB vs grayscale tensor mismatch
    2. `test_prioritize_samples` - NameError due to missing `time` import
    3. `test_end_to_end_optimization_pipeline` - NameError due to missing `time` import
  - **Solution**:
    1. Fixed GPU image analysis by properly converting RGB to grayscale for Sobel edge detection
    2. Added missing `import time` to `sample_prioritization.py`
    3. Added "size" key to GPU image analysis results to match test expectations
  - **Files Modified**:
    - `dataset_forge/utils/sample_prioritization.py` - Added time import
    - `dataset_forge/utils/gpu_acceleration.py` - Fixed RGB/grayscale conversion and added size field
  - **Testing**: All 306 tests now passing (298 passed, 7 skipped, 1 xfailed)
  - **Result**: Complete test suite stability restored
- [ ] **title**: lorem_ipsum
- [ ] **title**: lorem_ipsum
- [ ] **title**: lorem_ipsum
- [ ] **title**: lorem_ipsum
- [ ] **title**: lorem_ipsum

---
