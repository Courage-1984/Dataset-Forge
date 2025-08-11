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

Dataset Forge supports comprehensive global commands for a seamless CLI experience:

### **Available Global Commands**

- **help, h, ?** — Show context-aware help for the current menu, including navigation tips and available options.
- **quit, exit, q** — Instantly exit Dataset Forge from any menu, with full memory and resource cleanup.
- **0** — Go back to the previous menu (as before).
- **Ctrl+C** — Emergency exit with cleanup.

### **User Experience Features**

- **Context-Aware Help**: Each menu provides specific help information with purpose, options, navigation instructions, key features, and helpful tips
- **Automatic Menu Redraw**: After using `help`, the menu is automatically redrawn for clarity
- **Consistent Styling**: All prompts and help screens use the Catppuccin Mocha color scheme
- **Memory Management**: Automatic cleanup on quit with proper resource management
- **Error Handling**: Graceful handling of edge cases and invalid inputs
- **Comprehensive Testing**: 71 tests covering all global command functionality

### **Example Usage**

```
Enter your choice: help
# ...context-aware help screen appears with menu-specific information...
Press Enter to continue...
# Menu is automatically redrawn
Enter your choice: quit
# Dataset Forge exits with full cleanup
```

### **Technical Implementation**

The global command system is built on:
- **Core Files**: `dataset_forge/utils/menu.py` and `dataset_forge/utils/help_system.py`
- **Menu Integration**: All menus include `current_menu` and `menu_context` parameters
- **Help Documentation**: Comprehensive help content in `menu_system/comprehensive_help_menu.md` (31,665 bytes)
- **Testing Coverage**: Unit tests, integration tests, and edge case testing for all functionality

---

## Main Workflows

### 📂 Dataset Management

- **Create, combine, split, and shuffle datasets** from the Dataset Management menu.
- **Deduplicate, batch rename, and filter images** using Clean & Organize and **🔍 Fuzzy Matching De-duplication**.
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
- **Use utility scripts** in the `tools/` directory for environment setup, static analysis, theming consistency, and troubleshooting.

### 🧪 Testing & Developer Tools

- **Run all tests** with `python tools/run_tests.py` (see [getting_started.md](getting_started.md) for details).
- **Use static analysis tools** for code quality (`tools/find_code_issues.py`).
- **Check theming consistency** with `python tools/check_mocha_theming.py` for Catppuccin Mocha color scheme validation.
- **Audit menu hierarchy** with `python tools/log_current_menu.py` for menu system analysis and improvement recommendations.
- **All major features provide public, non-interactive APIs** for programmatic use and testing.

### 🔍 Static Analysis Tool

Dataset Forge includes a comprehensive static analysis tool that provides deep insights into code quality and maintainability:

#### **Quick Start**

```bash
# Run comprehensive analysis (all checks)
python tools/find_code_issues.py

# Run specific analysis types
python tools/find_code_issues.py --dependencies --configs
python tools/find_code_issues.py --vulture --pyflakes
python tools/find_code_issues.py --coverage --test-mapping

# View detailed results
python tools/find_code_issues.py --all --view
```

#### **Analysis Types**

1. **Dead Code Detection** (`--vulture`): Finds unused functions, methods, classes, and variables
2. **Test Coverage** (`--coverage`): Identifies untested code and generates coverage reports
3. **Call Graph Analysis** (`--callgraph`): Analyzes function/class relationships using pyan3
4. **Code Quality** (`--pyflakes`): Detects unused imports, variables, and syntax issues
5. **Test Mapping** (`--test-mapping`): Maps test files to source code and identifies gaps
6. **AST Analysis** (`--ast`): Custom analysis for defined but never called functions/classes
7. **Documentation** (`--docstrings`): Identifies missing docstrings in public APIs
8. **Dependencies** (`--dependencies`): Analyzes package usage vs. requirements.txt
9. **Configs** (`--configs`): Validates configuration files and structure
10. **Import Analysis** (automatic): Detects circular imports and unused imports

#### **Output Files**

All results are saved to `./logs/find_code_issues/`:

- `find_code_issues.log` - Full verbose output of all analyses
- `find_code_issues_view.txt` - Detailed results for each analysis type
- `find_code_issues_report.txt` - Actionable insights and issues summary
- `dependencies_analysis.txt` - Detailed dependency analysis results
- `coverage_html/` - HTML coverage reports (when coverage analysis is run)

#### **Integration with Development**

- **Pre-commit Analysis**: Run before committing code to catch issues early
- **Continuous Integration**: Integrate with CI/CD pipelines for automated quality checks
- **Code Review**: Use analysis results to guide code review discussions
- **Maintenance**: Regular analysis helps maintain code quality and identify technical debt

#### **Requirements**

```bash
pip install vulture pytest pytest-cov coverage pyan3 pyflakes
```

The tool automatically handles missing dependencies and provides helpful error messages for installation.

### 🎨 Catppuccin Mocha Theming Consistency Checker

Dataset Forge includes a comprehensive theming consistency checker that ensures all CLI output follows the Catppuccin Mocha color scheme:

#### **Quick Start**

```bash
# Basic analysis
python tools/check_mocha_theming.py

# Save report to specific location
python tools/check_mocha_theming.py --output reports/theming_report.md

# Verbose output with detailed results
python tools/check_mocha_theming.py --verbose
```

#### **Analysis Types**

1. **Raw Print Detection**: Finds `print()` calls that should use centralized utilities
2. **Import Validation**: Detects Mocha color usage without proper imports
3. **Menu Context**: Identifies missing `current_menu` and `menu_context` parameters
4. **Menu Patterns**: Validates standardized key-based menu patterns
5. **Documentation**: Checks for theming documentation in markdown files

#### **Output**

- **Console Summary**: Real-time analysis progress and summary statistics
- **Detailed Report**: Comprehensive markdown report with file-by-file analysis
- **Actionable Recommendations**: Specific suggestions for fixing theming issues
- **Exit Codes**: Proper exit codes for CI/CD integration (1 for errors, 0 for success)

#### **Integration with Development**

- **Pre-commit Analysis**: Run before committing code to ensure theming consistency
- **Continuous Integration**: Integrate with CI/CD pipelines for automated theming checks
- **Code Review**: Use analysis results to guide theming-related code review discussions
- **Quality Assurance**: Regular analysis prevents theming regressions and maintains user experience standards

#### **Requirements**

No additional dependencies required - uses standard library modules only.

### 🔧 Enhanced Development with MCP Integration

Dataset Forge is configured with three MCP (Model Context Protocol) servers for enhanced development:

- **Filesystem MCP**: Direct access to codebase and datasets for navigation and analysis
- **Brave Search MCP**: Privacy-focused web research for ML techniques and tools
- **Firecrawl MCP**: Web scraping for documentation and resource extraction

**Development Workflow:**
```bash
# Enhanced Development Routine
1. Use Filesystem MCP to navigate and analyze codebase
2. Use Brave Search to research new ML techniques and tools
3. Use Firecrawl to extract relevant documentation and resources
4. Implement improvements based on research findings
5. Update documentation with new insights and techniques
```

See [Advanced Features](advanced.md) for detailed MCP integration information and technical implementation examples.

---

## ⭐ BHI Filtering with Advanced CUDA Optimizations

Dataset Forge includes a comprehensive BHI (Blockiness, HyperIQA, IC9600) filtering system with advanced CUDA optimizations for high-performance image quality assessment.

### **Overview**

BHI filtering analyzes images using three quality metrics:
- **Blockiness**: Detects compression artifacts and blocky patterns
- **HyperIQA**: Perceptual image quality assessment using deep learning
- **IC9600**: Advanced image complexity and quality evaluation

### **Key Features**

#### **🚀 Advanced CUDA Optimizations**
- **Mixed Precision (FP16)**: 30-50% memory reduction with automatic fallback
- **Dynamic Batch Sizing**: Automatic batch size adjustment based on available GPU memory
- **Memory Management**: Comprehensive GPU memory cleanup and CPU fallback
- **Windows Compatibility**: Optimized for Windows CUDA multiprocessing limitations
- **Progress Tracking**: Real-time progress bars with detailed metrics

#### **📁 Flexible File Actions**
- **Move**: Move filtered files to a new folder (default)
- **Copy**: Copy filtered files to a new folder
- **Delete**: Permanently delete filtered files (with confirmation)
- **Report**: Dry run to see what would be filtered

#### **⚙️ Smart Processing Order**
- **IC9600 First**: Most memory-intensive operation runs first when GPU memory is cleanest
- **Optimized Memory**: Automatic memory cleanup between operations
- **Error Recovery**: Graceful handling of CUDA memory errors with CPU fallback

### **Usage Workflow**

1. **Navigate to BHI Filtering**:
   ```
   Main Menu → Analysis & Validation → Analyze Properties → BHI Filtering Analysis
   ```

2. **Select Input Folder**: Choose the folder containing images to filter

3. **Choose Action**: Select move, copy, delete, or report

4. **Set Thresholds** (recommended starting values):
   - **Blockiness**: 0.3 (lower = less blocky = better quality)
   - **HyperIQA**: 0.3 (lower = better quality)
   - **IC9600**: 0.3 (lower = better quality)

5. **Monitor Progress**: Watch real-time progress bars and GPU memory usage

### **Performance Optimizations**

#### **Environment Variables** (automatically set in `run.bat`)
```batch
PYTORCH_NO_CUDA_MEMORY_CACHING=1
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128,expandable_segments:True
CUDA_LAUNCH_BLOCKING=0
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
CUDA_MEMORY_FRACTION=0.9
```

#### **Automatic Optimizations**
- **Batch Size**: Dynamically adjusted based on available GPU memory
- **Memory Cleanup**: Automatic cleanup every 10 batches for IC9600
- **CPU Fallback**: Automatic fallback to CPU if CUDA memory errors occur
- **Mixed Precision**: Automatic FP16 usage for memory efficiency

### **Threshold Guidelines**

#### **Conservative (Strict Filtering)**
- Blockiness: 0.3, HyperIQA: 0.3, IC9600: 0.3
- Filters out ~20-40% of images
- Best for high-quality datasets

#### **Moderate (Balanced)**
- Blockiness: 0.5, HyperIQA: 0.5, IC9600: 0.5
- Filters out ~10-20% of images
- Good for general use

#### **Aggressive (Minimal Filtering)**
- Blockiness: 0.7, HyperIQA: 0.7, IC9600: 0.7
- Filters out ~5-10% of images
- Best for large datasets where you want to keep most images

### **Troubleshooting**

#### **CUDA Memory Errors**
- **Automatic Fix**: System automatically falls back to CPU processing
- **Manual Fix**: Reduce batch size or increase pagefile size
- **Prevention**: Use conservative thresholds and monitor GPU memory

#### **100% Filtering**
- **Cause**: Thresholds too strict (all images filtered)
- **Solution**: Increase thresholds (try 0.3 → 0.5)
- **Test**: Use "report" action first to see filtering results

#### **Performance Issues**
- **Windows**: Multiprocessing disabled for compatibility
- **Memory**: Automatic cleanup and batch size adjustment
- **GPU**: Mixed precision and memory optimization active

### **Example Output**

```
----------------------------------------
         BHI Filtering Progress         
----------------------------------------
Starting BHI filtering with action: move
Destination: C:/path/to/filtered_folder
Found 3259 files to process
Using batch size: 8 (IC9600: 4)
GPU Memory: 0.0GB used / 12.0GB total
Processing order: IC9600 → Blockiness → HyperIQA
Using thresholds: {'blockiness': 0.3, 'hyperiqa': 0.3, 'ic9600': 0.3}

Scoring with ic9600...
ic9600 scoring: 100%|████████████████| 815/815 [03:55<00:00, 3.46batch/s]

Scoring with blockiness...
blockiness scoring: 100%|████████████████| 408/408 [01:46<00:00, 3.84batch/s]

Scoring with hyperiqa...
hyperiqa scoring: 100%|████████████████| 408/408 [03:18<00:00, 2.06batch/s]

3259 files will be moved.
Performing move operations...
moving files: 100%|████████████████| 3259/3259 [00:00<00:00, 6602.06file/s]

BHI filtering completed. Processed 3259 files, filtered 3259 files.
Filtered files: 3259/3259 (100.0%)
```

### **Advanced Configuration**

#### **Custom Thresholds**
```python
from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering

# Custom thresholds
thresholds = {
    "blockiness": 0.25,  # Very strict
    "hyperiqa": 0.35,    # Moderate
    "ic9600": 0.4        # Less strict
}

# Run with custom thresholds
run_bhi_filtering(
    input_path="path/to/images",
    thresholds=thresholds,
    action="move",
    batch_size=8,
    verbose=True
)
```

#### **Preset Thresholds**
```python
from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering_with_preset

# Use conservative preset
run_bhi_filtering_with_preset(
    input_path="path/to/images",
    preset_name="conservative",  # "conservative", "moderate", "aggressive"
    action="move",
    verbose=True
)
```

---

## 🔍 Fuzzy Matching De-duplication

The Fuzzy Matching De-duplication feature provides advanced duplicate detection using multiple perceptual hashing algorithms with configurable similarity thresholds. This feature consolidates all duplicate detection methods into a single, comprehensive menu.

### **Quick Start**

1. **Navigate to the menu**: Main Menu → 🛠️ Utilities → 🔍 Fuzzy Matching De-duplication
2. **Choose operation type**: Single folder or HQ/LQ paired folders
3. **Select hash methods**: Choose from pHash, dHash, aHash, wHash, Color Hash
4. **Configure thresholds**: Set similarity thresholds for each hash method
5. **Choose operation mode**: Show, Copy, Move, or Delete duplicates

### **Hash Algorithms**

- **pHash (Perceptual Hash)**: Detects duplicates based on image content and structure
- **dHash (Difference Hash)**: Detects duplicates based on edge differences
- **aHash (Average Hash)**: Detects duplicates based on average pixel values
- **wHash (Wavelet Hash)**: Detects duplicates based on wavelet transform
- **Color Hash**: Detects duplicates based on color distribution

### **Threshold Guidelines**

#### **Conservative (High Accuracy)**
- pHash: 95%, dHash: 90%, aHash: 85%, wHash: 90%, Color Hash: 80%

#### **Balanced (Recommended)**
- pHash: 90%, dHash: 85%, aHash: 80%, wHash: 85%, Color Hash: 75%

#### **Aggressive (More Duplicates)**
- pHash: 80%, dHash: 75%, aHash: 70%, wHash: 75%, Color Hash: 65%

### **Example Workflow**

```
# Navigate to Fuzzy Matching De-duplication
Main Menu → 🛠️ Utilities → 🔍 Fuzzy Matching De-duplication

# Select operation
1. 📁 Single Folder Fuzzy De-duplication

# Enter folder path
C:/path/to/your/images

# Choose hash methods (comma-separated)
pHash, dHash, aHash

# Set thresholds
pHash: 90
dHash: 85
aHash: 80

# Choose operation mode
1. Show duplicates (preview only)
```

#### **Expected Output**
```
Found 1000 images in C:/path/to/images
Computing perceptual hashes...
Computing hashes: 100%|████████████████| 1000/1000 [00:05<00:00, 200.00it/s]
Finding fuzzy duplicates...
✅ Fuzzy deduplication workflow completed successfully!
📊 Results:
  - Total files processed: 1000
  - Duplicate groups found: 15
  - Total duplicates: 45
🔍 Duplicate groups:
  Group 1:
    - image1.jpg (similarity: 95.2%, method: pHash)
    - image2.jpg (similarity: 94.8%, method: pHash)
    - image3.jpg (similarity: 93.1%, method: dHash)
```

### **Best Practices**

1. **Start with Show Mode**: Always preview duplicates before taking action
2. **Use Conservative Thresholds**: Begin with higher thresholds to avoid false positives
3. **Test with Small Datasets**: Verify results before processing large datasets
4. **Combine Hash Methods**: Use multiple algorithms for better accuracy
5. **Backup Important Data**: Always backup before using delete operations
6. **Monitor Memory Usage**: Use appropriate batch sizes for your system

### **Advanced Configuration**

#### **Custom Hash Combinations**
```python
from dataset_forge.actions.fuzzy_dedup_actions import fuzzy_matching_workflow

# Custom hash methods and thresholds
hash_methods = ["pHash", "dHash", "wHash"]
thresholds = {
    "pHash": 92,
    "dHash": 88,
    "wHash": 85
}

# Run fuzzy deduplication
results = fuzzy_matching_workflow(
    folder="path/to/images",
    hash_methods=hash_methods,
    thresholds=thresholds,
    operation="show"
)
```

#### **HQ/LQ Paired Folders**
```python
# For HQ/LQ paired folders
results = fuzzy_matching_workflow(
    hq_folder="path/to/hq",
    lq_folder="path/to/lq",
    hash_methods=["pHash", "dHash"],
    thresholds={"pHash": 90, "dHash": 85},
    operation="copy",
    dest_dir="path/to/duplicates"
)
```

### **Performance Considerations**

#### **Memory Usage Guidelines**
- **Small Datasets** (< 1,000 images): Use batch size of 100-500
- **Medium Datasets** (1,000-10,000 images): Use batch size of 50-200
- **Large Datasets** (> 10,000 images): Use batch size of 20-100

#### **Processing Speed Characteristics**
- **pHash**: Fastest, good for initial screening
- **dHash**: Fast, good for edge-based detection
- **aHash**: Very fast, good for brightness-based detection
- **wHash**: Slower, good for texture-based detection
- **Color Hash**: Medium speed, good for color-based detection

#### **Accuracy vs Speed Trade-offs**
- **High Accuracy**: Use all hash methods with high thresholds
- **Fast Processing**: Use pHash + dHash only
- **Balanced**: Use pHash + dHash + aHash with medium thresholds

### **Troubleshooting**

#### **Common Issues and Solutions**

**No Duplicates Found**
- **Cause**: Thresholds too high
- **Solution**: Lower the similarity thresholds
- **Alternative**: Try different hash method combinations

**Too Many False Positives**
- **Cause**: Thresholds too low
- **Solution**: Increase the similarity thresholds
- **Alternative**: Use fewer hash methods

**Memory Errors**
- **Cause**: Batch size too large
- **Solution**: Reduce the batch size
- **Alternative**: Process smaller subsets

**Slow Processing**
- **Cause**: Too many hash methods or large batch size
- **Solution**: Use fewer hash methods or smaller batch size
- **Alternative**: Process in smaller chunks

#### **Error Messages**

**"No image files found"**
- **Cause**: Folder doesn't contain supported image files
- **Solution**: Check folder path and file types

**"Invalid threshold value"**
- **Cause**: Threshold not between 0 and 100
- **Solution**: Use values between 0 and 100

**"Operation cancelled"**
- **Cause**: User cancelled the operation
- **Solution**: Re-run the operation

### **Integration with Other Features**

#### **Visual De-duplication**
- Use fuzzy matching for initial screening
- Use visual de-duplication for final verification

#### **File Hash De-duplication**
- Use fuzzy matching for content-based duplicates
- Use file hash for exact duplicates

#### **ImageDedup**
- Use fuzzy matching for perceptual duplicates
- Use ImageDedup for advanced duplicate detection

### **Technical Details**

#### **Hash Computation**
- All hashes are computed using the `imagehash` library
- Hashes are normalized to 64-bit values
- Similarity is calculated using Hamming distance

#### **Memory Management**
- Images are processed in batches to manage memory usage
- Hash values are cached to avoid recomputation
- Memory is cleared after each batch

#### **Error Handling**
- Invalid images are skipped with warnings
- Processing continues even if some images fail
- Comprehensive error reporting and logging

### **Dependencies**

The Fuzzy Matching De-duplication feature requires:
- **imagehash**: For perceptual hash computation
- **PIL/Pillow**: For image processing
- **numpy**: For numerical operations
- **tqdm**: For progress tracking

All dependencies are included in the project's `requirements.txt` file.

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
