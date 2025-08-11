[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# TODO / Planned Features

> **Project Roadmap**  
> This section collects all future feature/functionality ideas, goals, and implementation notes for Dataset Forge. Add new ideas here to keep the roadmap in one place and maintain project inspiration.

---

## 🚀 High Priority Features

### Core System Enhancements

- [ ] **Debug Mode**: Add a comprehensive _Debug Mode_ to the project, which when activated, shows verbose output and debug information throughout the CLI
- [ ] **Packaging & Distribution**:
  - [ ] Compile Dataset-Forge into standalone executable
  - [ ] Create Docker container/containerization
  - [ ] Automated build pipeline for releases
- [ ] **Automated Documentation**: Implement automated documentation generation and maintenance
- [ ] **Batch Scripts**: Save and replay complex multi-step operations/workflows
- [ ] **Global Search Functionality**: Implement comprehensive search across all menus and features
- [ ] **Path Sanitization**: Add robust path validation and sanitization throughout the application

### Advanced Data Processing

- [ ] **Advanced Data Augmentation**: Expand augmentation capabilities with model-aware techniques
  - [ ] Compositional Augmentations: Integrate Albumentations for complex augmentation pipelines
  - [ ] Mixing Augmentations: Implement Mixup and CutMix techniques
  - [ ] GAN-based Augmentations: Integrate with pre-trained StyleGAN for synthetic data generation
- [ ] **Advanced Filtering / AI-Powered Features**:
  - [ ] Semantic Filtering: Filter by image content/semantics
  - [ ] Style-Based Filtering: Filter by artistic style
  - [ ] Quality-Based Filtering: Advanced quality assessment filters
  - [ ] Custom Filter Plugins: User-defined filtering logic
  - [ ] Auto-Labeling: Automatic image labeling and classification
  - [ ] Style Transfer: Apply artistic styles to datasets
  - [ ] Content-Aware Cropping: Intelligent image cropping

### Performance & Optimization

- [ ] **Parallel Import Loading**: Load multiple modules in parallel with threading
- [ ] **Smart Caching**: Predictive loading of frequently used modules
- [ ] **Import Optimization**: Compile-time import analysis and automatic conversion
- [ ] **Performance Monitoring**: Real-time metrics and automated regression detection
- [ ] **Lazy Imports**: Ensure lazy imports everywhere to speed up CLI startup

---

## 🔧 Development & Infrastructure

### Code Quality & Testing

- [ ] **Validate Code from Other Repos**: Review and validate all code imported from external repositories
- [ ] **Improve Unit and Integration Tests**: Enhance test coverage and quality
- [ ] **Test Dataset Improvements**: Enhance test datasets for better coverage
- [ ] **Code Validation**: Implement comprehensive code validation and quality checks

### External Tool Integration

- [ ] **Phhofm's SISR**: Investigate [Phhofm's SISR](https://github.com/Phhofm/sisr) for potential integration
- [ ] **Links .json Customization**: Further customize links with metadata, descriptions, and enhanced information
- [ ] **External Tool Validation**: Validate and improve all external tool integrations

### Documentation & User Experience

- [ ] **Onboarding**: Create comprehensive onboarding documentation and flow
- [ ] **Features TL;DR**: Create a '# Features (tl;dr)' section in `./docs/features.md`
- [ ] **User Experience Enhancements**: Improve overall user experience and workflow

---

## 🎯 Specific Feature Implementations

### Image Processing & Analysis

- [ ] **Advanced Align Images Options**: Add SIFT/FLANN parameters and advanced alignment options
- [ ] **AI-Powered Dataset Analysis**: Implement AI-powered dataset analysis and recommendations
- [ ] **Advanced Analytics**: More advanced analytics and monitoring capabilities

### System Architecture

- [ ] **Modularization**: Further modularization and extensibility for new workflows
- [ ] **Cloud Integration**: Cloud integration for distributed processing and storage
- [ ] **Web Interface**: Web interface for dataset management and visualization
- [ ] **Dataset Versioning**: Implement comprehensive dataset versioning system

### Deduplication Enhancements

- [ ] **Dedicated De-dupe Menu**: Create a comprehensive dedicated deduplication menu
- [ ] **Enhanced Deduplication**: Improve existing deduplication features and workflows

---

## ✅ Completed Features

### Core System Features

- [x] **Dataset Health Scoring**: Comprehensive dataset health scoring workflow and menu option
- [x] **the-database's img-ab**: Successfully forked and improved
- [x] **find_code_issues.py**: Comprehensive static analysis tool implemented and tested
- [x] **create .exe & dll dump**: Successfully created executable and DLL dump

### Critical Bug Fixes

- [x] **Fix Critical Menu System Errors**: Resolved 'str' object is not callable and 'module' object is not callable errors

  - **Problem**: Critical menu system errors causing application crashes
  - **Solution**: Fixed lazy_action vs lazy_menu usage, pepedp lazy imports, and ProcessType enum access
  - **Files**: `dataset_management_menu.py` and related menu files
  - **Result**: Stable menu system with proper error handling

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

### Advanced Features

- [x] **MCP Integration Implementation**: Comprehensive MCP (Model Context Protocol) integration for enhanced development
  - **Status**: ✅ COMPLETED - MCP tools integration fully implemented and documented
  - **MCP Tools Configured**:
    1. **Brave Search Tools** - Primary research for latest libraries, best practices, and solutions
    2. **Firecrawl Tools** - Deep web scraping for documentation and content extraction
    3. **Filesystem Tools** - Project analysis and file management
    4. **GitHub Integration Tools** - Code examples and repository documentation
  - **Files Updated**:
    - `.cursorrules` - Added comprehensive MCP Integration (MANDATORY) section with tool usage patterns
    - `docs/style_guide.md` - Added MCP Integration Requirements section
    - `docs/contributing.md` - Enhanced MCP Integration Development section with mandatory requirements
    - `docs/TODO.md` - Added completion status for MCP Integration
  - **Key Features**:
    - **Mandatory MCP Tool Usage**: All contributors must use MCP tools before implementing solutions
    - **Tool Usage Patterns**: Clear workflows for different development scenarios
    - **Priority Order**: Brave Search → Firecrawl → Filesystem → GitHub Integration
    - **Usage Examples**: Practical code examples for each tool category
    - **Integration Requirements**: Specific requirements for MCP tool usage
  - **Result**: Enhanced development workflow with comprehensive research and analysis capabilities

---

## 📋 Future Considerations

### Long-term Goals

- [ ] **Stable Release**: Release a stable build with comprehensive testing
- [ ] **Community Features**: Enhanced community features and collaboration tools
- [ ] **Enterprise Features**: Enterprise-grade features for large-scale deployments
- [ ] **API Development**: RESTful API for programmatic access
- [ ] **Plugin System**: Extensible plugin system for custom functionality

### Research & Investigation

- [ ] **New Technologies**: Investigate emerging technologies for potential integration
- [ ] **Performance Research**: Research new performance optimization techniques
- [ ] **User Experience Research**: Study user workflows and optimize accordingly
- [ ] **Community Feedback**: Gather and implement community feedback and suggestions

---

## 🔄 Maintenance & Updates

### Regular Tasks

- [ ] **Dependency Updates**: Regular dependency updates and security patches
- [ ] **Documentation Updates**: Keep documentation current with feature changes
- [ ] **Test Maintenance**: Maintain and expand test coverage
- [ ] **Performance Monitoring**: Continuous performance monitoring and optimization
- [ ] **Bug Tracking**: Comprehensive bug tracking and resolution

### Quality Assurance

- [ ] **Code Review**: Implement comprehensive code review processes
- [ ] **Automated Testing**: Expand automated testing coverage
- [ ] **Static Analysis**: Regular static analysis and code quality checks
- [ ] **Security Audits**: Regular security audits and vulnerability assessments

---

> **Note**: This TODO list is a living document that should be updated as features are completed and new ideas are added. All completed features should be moved to the "Completed Features" section with detailed implementation notes.

---

## ❓ Unsorted

- [ ] **pyiqa / IQA-PyTorch**: Implement integration
- [ ] **lorem**: lorem
- [ ] **lorem**: lorem
- [ ] **lorem**: lorem
- [ ] **lorem**: lorem
- [ ] **lorem**: lorem
