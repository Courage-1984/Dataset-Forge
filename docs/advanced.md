[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

> **Note:** Architecture diagrams in this documentation use Mermaid code blocks. No Python package is required; diagrams are rendered by supported Markdown viewers (e.g., GitHub, VSCode with Mermaid extension).
>
> **Badges:** Standard badges (build, license, Python version, etc.) are included in the README. See the README for their meaning.

# Advanced Features & Configuration

> **Who is this for?**  
> This guide is for advanced users, power users, and contributors who want to customize, extend, or deeply understand Dataset Forge. For user-facing features, see [features.md](features.md).

---

## Advanced Configuration

- Use custom config files (JSON, YAML, HCL) for advanced workflows.
- Integrate with external tools (WTP Dataset Destroyer, traiNNer-redux, getnative, resdet, etc.).
- Tune batch sizes, memory, and parallelism for large datasets.
- Advanced model management and upscaling with OpenModelDB.

---

## Performance & Optimization

- GPU acceleration for image processing (PyTorch, TorchVision).
- Distributed processing with Dask and Ray.
- Advanced caching: in-memory, disk, model, and smart auto-selection.
- JIT compilation (Numba, Cython, PyTorch JIT) for performance-critical code.
- Quality-based sample prioritization and adaptive batching.
- **CLI Optimization**: Comprehensive lazy import system for 50-60% faster startup times.

<details>
<summary><strong>Technical Implementation: Caching System</strong></summary>

- In-memory, disk, and model caches with TTL, compression, and statistics.
- Decorators: `@in_memory_cache`, `@disk_cache`, `@model_cache`, `@smart_cache`.
- Programmatic management: clear, validate, repair, warmup, export cache.
- See code samples in the full file for usage.

</details>

<details>
<summary><strong>Technical Implementation: Performance Suite</strong></summary>

- GPUImageProcessor, distributed_map, multi_gpu_map, prioritize_samples, compile_function, etc.
- See code samples in the full file for usage.

</details>

<details>
<summary><strong>Technical Implementation: CLI Optimization & Lazy Import System</strong></summary>

Dataset Forge implements a comprehensive lazy import system to significantly speed up CLI startup times:

**Performance Improvements:**
- **Before Optimization**: ~3-5 seconds startup time, heavy imports loaded at startup
- **After Optimization**: ~1.5-2 seconds startup time (50-60% improvement), lazy imports loaded only when needed

**Core Components:**
- **LazyImport Class**: Wrapper for deferring heavy library imports
- **Pre-defined Lazy Imports**: torch, cv2, numpy, PIL, matplotlib, pandas, transformers, etc.
- **Performance Monitoring**: Import timing analysis and monitoring decorators

**Implementation Patterns:**
- **Module-Level**: Replace direct imports with lazy imports
- **Function-Level**: Import heavy libraries only when functions are called
- **Class-Level**: Lazy loading in class properties

**Usage Examples:**
```python
# Instead of: import torch, cv2, numpy as np
from dataset_forge.utils.lazy_imports import (
    torch, cv2, numpy_as_np as np
)

# Function-level lazy imports
def process_image(image_path):
    from dataset_forge.utils.lazy_imports import cv2, numpy_as_np as np
    image = cv2.imread(image_path)
    return np.array(image)

# Performance monitoring
from dataset_forge.utils.lazy_imports import monitor_import_performance

@monitor_import_performance
def critical_function():
    # Function with performance monitoring
    pass
```

**Optimization Strategies:**
- **Import Timing Analysis**: Monitor and optimize slow imports (>1s)
- **CLI Startup Optimization**: Lazy menu loading, deferred heavy imports
- **Memory Management**: Lazy memory allocation with automatic cleanup

**Best Practices:**
- Use lazy imports for heavy libraries (PyTorch, OpenCV, matplotlib, transformers)
- Don't use lazy imports for core utilities or frequently used libraries
- Monitor import performance and optimize based on usage patterns

See `docs/cli_optimization.md` for comprehensive details and advanced usage patterns.

</details>

---

## Developer Patterns & Extending

- **Robust menu loop pattern** for all CLI menus.
- Modular integration of new workflows (e.g., Umzi's Dataset_Preprocessing, resave images).
- All business logic in `dataset_forge/actions/`, menus in `dataset_forge/menus/`.
- Lazy imports for fast CLI responsiveness.
- Centralized utilities for printing, memory, error handling, and progress.

### Global Command System Implementation

Dataset Forge features a comprehensive global command system that provides context-aware help and instant quit functionality across all menus:

#### **Core Implementation**

- **Global Commands**: `help`, `h`, `?` for context-aware help; `quit`, `exit`, `q` for instant quit
- **Memory Management**: Automatic cleanup on quit with proper resource management
- **Context-Aware Help**: Menu-specific help information with navigation tips and feature descriptions
- **Menu Redraw**: Automatic menu redraw after help for clarity
- **Error Handling**: Graceful handling of `None` and non-string inputs

#### **Technical Architecture**

- **Core Files**: `dataset_forge/utils/menu.py` and `dataset_forge/utils/help_system.py`
- **Menu Integration**: All menus include `current_menu` and `menu_context` parameters
- **Help Documentation**: Comprehensive help content in `menu_system/comprehensive_help_menu.md` (31,665 bytes)
- **Testing**: 71 tests covering unit tests, integration tests, and edge case testing

#### **Menu Context Structure**

Each menu defines a comprehensive context dictionary:
```python
menu_context = {
    "Purpose": "Clear description of menu functionality",
    "Options": "Number and types of available options", 
    "Navigation": "How to navigate the menu",
    "Key Features": ["Feature 1", "Feature 2"],
    "Tips": ["Helpful tips for using the menu"],
    "Examples": "Usage examples (optional)",
    "Notes": "Additional information (optional)"
}
```

#### **Standardized Menu Pattern**

All menus follow the standardized key-based pattern with global command support:
```python
def my_menu():
    """Menu implementation with global command support."""
    options = {
        "1": ("Option 1", function1),
        "2": ("Option 2", function2),
        "0": ("🚪 Exit", None),
    }
    
    menu_context = {
        "Purpose": "Menu purpose description",
        "Options": "Number of options available",
        "Navigation": "Navigation instructions",
        "Key Features": ["Feature 1", "Feature 2"],
        "Tips": ["Tip 1", "Tip 2"],
    }
    
    while True:
        try:
            key = show_menu(
                "Menu Title", 
                options, 
                Mocha.lavender,
                current_menu="Menu Name",
                menu_context=menu_context
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break
```

<details>
<summary><strong>Static Analysis & Utility Scripts</strong></summary>

- `tools/find_code_issues.py`: comprehensive static analysis including dead code, coverage, docstrings, test mapping, dependency analysis, configuration validation, and import analysis
- `tools/log_current_menu.py`: comprehensive menu hierarchy analysis, path input detection, and improvement recommendations
- `tools/check_mocha_theming.py`: comprehensive Catppuccin Mocha theming consistency checker for CLI menus, printing, and user-facing output
- `tools/merge_docs.py`: merges docs and generates ToC.
- `tools/install.py`: automated environment setup.
- All new scripts must be documented and tested.

</details>

<details>
<summary><strong>Menu Auditing Tool</strong></summary>

The menu auditing tool (`tools/log_current_menu.py`) provides comprehensive analysis of Dataset Forge's menu hierarchy:

**Key Features:**

- **Recursive Exploration**: Automatically discovers and explores all menus and submenus (up to 4 levels deep)
- **Path Input Detection**: Identifies menus requiring user path input using regex patterns
- **AST-Based Analysis**: Uses Python's Abstract Syntax Tree for accurate code parsing with regex fallback
- **Function Resolution**: Handles complex menu function references including `lazy_menu()` calls
- **Comprehensive Reporting**: Generates detailed markdown reports with statistics and recommendations

**Usage:**

```bash
# Activate virtual environment
venv312\Scripts\activate

# Run the menu audit
python tools/log_current_menu.py
```

**Output:** Generates `menu_system/current_menu.md` with:

- Executive summary and statistics
- Hierarchical menu tree structure
- Detailed analysis of each menu
- Actionable recommendations for improvement
- Menu depth, size, and path input metrics

**Configuration:** Customizable settings for output location, maximum depth, and path input detection patterns.

</details>

<details>
<summary><strong>Catppuccin Mocha Theming Consistency Checker</strong></summary>

The theming consistency checker (`tools/check_mocha_theming.py`) ensures consistent use of the Catppuccin Mocha color scheme across the entire codebase:

**Key Features:**

- **Comprehensive Analysis**: Scans all Python, Markdown, and batch files in the codebase
- **Raw Print Detection**: Identifies all `print()` statements that should use centralized utilities
- **Import Validation**: Checks for missing Mocha color imports and centralized printing utilities
- **Menu Pattern Analysis**: Validates proper menu implementation patterns and context parameters
- **Detailed Reporting**: Generates comprehensive markdown reports with actionable recommendations
- **Issue Categorization**: Classifies issues by severity (error, warning, info) and type

**Usage:**

```bash
# Activate virtual environment
venv312\Scripts\activate

# Basic analysis
python tools/check_mocha_theming.py

# Save report to specific location
python tools/check_mocha_theming.py --output reports/theming_report.md

# Verbose output with detailed results
python tools/check_mocha_theming.py --verbose
```

**Output:** Generates comprehensive reports with:

- Real-time analysis progress and summary statistics
- File-by-file detailed analysis with line numbers and code snippets
- Actionable recommendations for fixing theming issues
- Issue categorization by severity and type
- Best practices and usage examples

**Analysis Types:**

- **Raw Print Statements**: Finds `print()` calls that should use `print_info()`, `print_success()`, etc.
- **Missing Imports**: Detects Mocha color usage without proper imports
- **Menu Context**: Identifies missing `current_menu` and `menu_context` parameters
- **Menu Patterns**: Validates standardized key-based menu patterns
- **Documentation**: Checks for theming documentation in markdown files

**Integration:** Fully integrated with Dataset Forge's tools launcher and development workflow, with proper exit codes for CI/CD integration.

</details>

---

## Advanced Testing Patterns

- All features provide public, non-interactive APIs for programmatic use and testing.
- Tests use pytest, fixtures, monkeypatching, and dummy objects.
- Multiprocessing tests require module-level worker functions.
- All new features and bugfixes must include robust tests.

---

## Technical Deep Dives

<details>
<summary><strong>DPID Modular Integration</strong></summary>

- Multiple DPID (degradation) methods: BasicSR, OpenMMLab, Phhofm, Umzi.
- Modular, public APIs for both single-folder and HQ/LQ paired workflows.
- All implementations are robustly tested.

</details>

<details>
<summary><strong>Enhanced Metadata Management</strong></summary>

- Uses exiftool for robust, cross-format metadata extraction, editing, and anonymization.
- Batch extract, view/edit, filter, and anonymize metadata.
- Integration with pandas/SQLite for scalable analysis.

</details>

<details>
<summary><strong>Resave Images Integration</strong></summary>

- Modular, maintainable feature with thread-based parallel processing.
- Supports multiple output formats, grayscale, recursive processing, and unique filenames.
- Fully covered by unit and integration tests.

</details>

---

## MCP Integration & Enhanced Development

Dataset Forge is configured with three powerful MCP (Model Context Protocol) servers that provide enhanced development capabilities:

### **MCP Server Configuration**

The project includes three MCP servers for enhanced development:

- **Filesystem MCP**: Direct access to codebase and datasets
- **Brave Search MCP**: Privacy-focused web research for ML techniques  
- **Firecrawl MCP**: Web scraping for documentation and resource extraction

### **Development Workflow Enhancements**

#### **Code Analysis Workflow**
```bash
# Daily Development Routine
1. Use Filesystem MCP to navigate codebase
2. Use Brave Search to research new techniques
3. Use Firecrawl to extract relevant documentation
4. Implement improvements based on findings
5. Update documentation with new insights
```

#### **Research Integration Workflow**
```bash
# Weekly Research Routine
1. Search for new SISR papers and techniques
2. Extract key findings from research papers
3. Identify potential integrations for Dataset Forge
4. Create implementation proposals
5. Update project roadmap
```

### **Proposed Improvements**

#### **Enhanced Documentation System**
- Add "Research Corner" section with latest ML findings
- Include links to relevant papers and datasets
- Provide integration guides for new tools

#### **Automated Research Updates**
- Create research automation system using MCP servers
- Automatically update research database with new findings
- Generate summary reports for new techniques

#### **Enhanced Dataset Discovery**
- Implement dataset discovery features using MCP servers
- Search for new datasets and extract compatibility information
- Generate compatibility reports for new datasets

#### **Community Integration Hub**
- Create community features section with user-submitted dataset reviews
- Add performance benchmarks and real-world usage statistics
- Implement tool integration requests and voting system

### **Technical Implementation**

#### **MCP Integration Class Example**
```python
class MCPIntegration:
    """Integration class for MCP servers in Dataset Forge."""

    def __init__(self):
        self.filesystem = FilesystemMCP()
        self.search = BraveSearchMCP()
        self.scraper = FirecrawlMCP()

    def research_new_features(self, query):
        """Research new features using MCP servers."""
        results = self.search.search(query)
        extracted_info = []

        for result in results:
            info = self.scraper.scrape(result.url)
            extracted_info.append(info)

        return self.analyze_findings(extracted_info)

    def analyze_codebase(self):
        """Analyze codebase using filesystem MCP."""
        files = self.filesystem.list_files("dataset_forge/")
        return self.generate_analysis_report(files)
```

#### **Automated Research Pipeline**
```python
def automated_research_pipeline():
    """Automated research pipeline using MCP servers."""

    # Define research topics
    topics = [
        "SISR techniques 2024",
        "image dataset management", 
        "GPU acceleration image processing",
        "distributed image processing"
    ]

    # Research each topic
    for topic in topics:
        results = search_mcp.search(topic)
        extracted_info = []

        for result in results[:5]:  # Top 5 results
            info = firecrawl_mcp.scrape(result.url)
            extracted_info.append(info)

        # Generate research summary
        summary = generate_research_summary(topic, extracted_info)
        save_research_summary(topic, summary)

    # Create consolidated report
    create_consolidated_research_report()
```

### **Success Metrics**

- **Development Efficiency**: Code navigation time reduced by 50%, research time reduced by 30%
- **Project Visibility**: Improved search engine ranking and GitHub stars
- **Feature Quality**: Research-based features implemented with improved user satisfaction

## Planned/Future Advanced Features

- Advanced options for Align Images (SIFT/FLANN parameters, etc.).
- Further modularization and extensibility for new workflows.
- More advanced analytics and monitoring.
- AI-powered dataset analysis and recommendations.
- Cloud integration for distributed processing and storage.
- Web interface for dataset management and visualization.
- **Parallel Import Loading**: Load multiple modules in parallel with threading
- **Smart Caching**: Predictive loading of frequently used modules
- **Import Optimization**: Compile-time import analysis and automatic conversion
- **Performance Monitoring**: Real-time metrics and automated regression detection

---

## See Also

- [Features](features.md)
- [Usage Guide](usage.md)
- [Project Architecture](architecture.md)
- [Troubleshooting](troubleshooting.md)
- [Style Guide](style_guide.md)
