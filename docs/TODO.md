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

---
