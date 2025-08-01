[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Dataset Forge Style Guide

> **Who is this for?**  
> This guide is for contributors and anyone writing code or documentation for Dataset Forge. For user-facing features, see [features.md](features.md) and [usage.md](usage.md).

---

## Critical UI/UX Rule: Catppuccin Mocha Color Scheme

- All user-facing CLI output **must** use the Catppuccin Mocha color scheme.
- Always use `from dataset_forge.utils.color import Mocha` and the centralized printing utilities.
- No raw print statements in user-facing code.
- All menus, prompts, progress bars, and workflow headings must be Mocha-styled.
- All new code and PRs must be reviewed for color consistency.

### Enforcement Checklist

- [ ] All new/modified CLI output uses Mocha colors via centralized utilities.
- [ ] No raw print statements in user-facing code.
- [ ] All code examples in docs use Mocha color utilities.
- [ ] Reviewer confirms color consistency before merging.

---

## General Principles

- **Python 3.12+**. Use modern Python features.
- **PEP 8** style, 4-space indentation, 88-char line length (Black standard).
- **Google-style docstrings** for all public functions/classes.
- **Type hints** for all function parameters and return values.
- **Absolute imports** for all `dataset_forge` modules.
- **Modular design**: UI (menus/), business logic (actions/), utilities (utils/), DPID (dpid/).
- **Consistent use of Catppuccin Mocha color scheme for all CLI output.**

---

## Project Architecture & Modularity

- Keep UI, logic, and utilities separate.
- Thin UI layers (menus), business logic in actions, helpers in utils.
- Use lazy imports to keep CLI menu responsive and fast.

---

## Coding Standards

- Use type hints everywhere.
- Google-style docstrings for all public functions/classes.
- Import order: standard library, third-party, local, relative (only within same module).
- Always use absolute imports for `dataset_forge` modules.

<details>
<summary><strong>Example: Google-style docstring</strong></summary>

```python
def process_images(image_paths: List[str], output_dir: str) -> List[str]:
    """
    Process a list of images and save results to output directory.
    Args:
        image_paths: List of input image file paths
        output_dir: Directory to save processed images
    Returns:
        List of output image file paths
    Raises:
        FileNotFoundError: If input files don't exist
        PermissionError: If output directory is not writable
    Example:
        >>> paths = process_images(['img1.jpg', 'img2.png'], 'output/')
        >>> print(f"Processed {len(paths)} images")
    """
```

</details>

---

## Memory, Parallelism, Progress, and Color/UI

- Use centralized memory management: `from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache`
- Use context managers and decorators for memory and monitoring.
- Use centralized parallel system: `from dataset_forge.utils.parallel_utils import parallel_map, ProcessingType`
- Use `smart_map`, `image_map`, `batch_map` for optimized processing.
- Use `tqdm` and AudioTqdm for progress and audio feedback.
- Use Catppuccin Mocha color scheme and centralized printing utilities for all output.

---

## Menu & Workflow Patterns

- Use hierarchical menu structure and `show_menu()` from `dataset_forge.utils.menu`.
- Include emojis in menu options with context-aware validation.
- Use the robust menu loop pattern (see code example below).
- All interactive workflows must print a clear, Mocha-styled heading before input/output prompts and progress bars using the centralized printing utilities and Mocha colors.

<details>
<summary><strong>Robust Menu Loop Example</strong></summary>

```python
from dataset_forge.utils.printing import print_header
from dataset_forge.utils.color import Mocha

while True:
    choice = show_menu("Menu Title", options, ...)
    if choice is None or choice == "0":
        break
    action = options[choice][1]
    if callable(action):
        print_header("Selected Action", color=Mocha.lavender)
        action()
```

</details>

---

## Error Handling & Logging

- Use centralized logging: `from dataset_forge.utils.history_log import log_operation`
- Log all major operations with timestamps.
- Use try-except with meaningful error messages.
- All user-facing errors must trigger the error sound via the centralized print_error utility.
- Use centralized emoji utilities for safe emoji handling: `from dataset_forge.utils.emoji_utils import normalize_unicode, sanitize_emoji, is_valid_emoji`

---

## Testing & Validation

- All features must provide public, non-interactive APIs for programmatic access and testing.
- Use pytest, fixtures, monkeypatching, and dummy objects.
- Multiprocessing tests must use module-level worker functions.
- All new features and bugfixes must include robust tests.

---

## Caching & Performance

- Use centralized caching utilities: `from dataset_forge.utils.cache_utils import in_memory_cache, disk_cache, model_cache, smart_cache`
- Choose appropriate cache type and document cache usage in function docstrings.
- Monitor cache statistics and implement cache warmup for critical data.

---

## Documentation Requirements

- Google-style docstrings for all public functions/classes.
- Include parameter types, return values, exceptions, and usage examples.

---

## Dependency & Security

- Add new dependencies to `requirements.txt` and use version constraints.
- Validate all user inputs and sanitize file paths.

---

## Emoji System Guidelines

### Emoji Usage in Menus and UI

- **Always validate emojis** before using them in user-facing text
- **Use context-aware validation** for appropriate emoji selection in different contexts
- **Include emojis in menu options** for better user experience and readability
- **Use smart emoji suggestions** for contextually appropriate emoji selection
- **Validate menu emojis** during development using the emoji usage checker

### Emoji Best Practices

```python
from dataset_forge.utils.emoji_utils import (
    suggest_appropriate_emojis,
    validate_emoji_appropriateness,
    get_emoji_description_from_mapping
)

# Good: Context-appropriate emojis
def create_menu_options():
    success_emojis = suggest_appropriate_emojis("success completion")
    error_emojis = suggest_appropriate_emojis("error problem")

    return {
        "1": (f"{success_emojis[0]} Process Complete", process_complete_action),
        "2": (f"{error_emojis[0]} Error Report", error_report_action),
        "0": ("🚪 Exit", None),
    }

# Good: Context-aware validation
def validate_menu_emojis(menu_options):
    for key, (description, action) in menu_options.items():
        emojis = extract_emojis(description)
        for emoji in emojis:
            validation = validate_emoji_appropriateness(emoji, "menu interface")
            if validation['warnings']:
                print(f"Warning: Menu option {key} has inappropriate emoji")

# Avoid: Too many emojis or inappropriate context
bad_menu = {
    "1": ("🎉 🍕 🎊 Process Complete! 🎈 🎪", process_action),  # Too many emojis
    "2": ("😀 😍 😊 😄 😁 😆 😅 😂 😇 😉 Error Report", error_action),  # All same category
}
```

### Emoji Accessibility

- **Provide emoji descriptions** for accessibility when needed
- **Use consistent emoji categories** across related menus
- **Test emoji display** on different platforms and terminals
- **Handle Unicode encoding issues** gracefully with fallbacks

### Emoji Performance

- **Use caching** for repeated emoji operations
- **Lazy load emoji mapping** only when needed
- **Monitor emoji usage patterns** for insights and recommendations
- **Use the emoji usage checker** before submitting PRs

## MCP Integration Requirements (MANDATORY)

### MCP Tool Usage Priority

When implementing solutions, **ALWAYS** use MCP tools in this priority order:

1. **Brave Search Tools** (Primary Research)

   - Use `mcp_brave-search_brave_web_search` for general web research, latest libraries, best practices
   - Use `mcp_brave-search_brave_news_search` for recent developments and updates
   - Use `mcp_brave-search_brave_local_search` for location-specific information
   - Use `mcp_brave-search_brave_video_search` for tutorials and demonstrations
   - Use `mcp_brave-search_brave_image_search` for visual references

2. **Firecrawl Tools** (Deep Web Scraping)

   - Use `mcp_firecrawl_firecrawl_search` for comprehensive web search with content extraction
   - Use `mcp_firecrawl_firecrawl_scrape` for detailed content extraction from specific URLs
   - Use `mcp_firecrawl_firecrawl_map` for discovering website structure
   - Use `mcp_firecrawl_firecrawl_extract` for structured data extraction
   - Use `mcp_firecrawl_firecrawl_deep_research` for complex research questions

3. **Filesystem Tools** (Project Analysis)

   - Use `mcp_filesystem_read_text_file` to read and analyze project files
   - Use `mcp_filesystem_list_directory` to understand project structure
   - Use `mcp_filesystem_search_files` to find specific files or patterns
   - Use `mcp_filesystem_get_file_info` for detailed file metadata analysis
   - Use `mcp_filesystem_directory_tree` for comprehensive project structure visualization

4. **GitHub Integration Tools** (Code Examples)
   - Use `mcp_gitmcp-docs_fetch_generic_documentation` for GitHub repository documentation
   - Use `mcp_gitmcp-docs_search_generic_code` for finding code examples in repositories
   - Use `mcp_gitmcp-docs_search_generic_documentation` for documentation searches
   - Use `mcp_gitmcp-docs_match_common_libs_owner_repo_mapping` for library-to-repo mapping

### MCP Tool Usage Patterns

#### Before Implementing Any Solution:

1. **Research Phase**: Use Brave Search to find latest libraries, best practices, and solutions
2. **Deep Dive**: Use Firecrawl to extract detailed content from relevant sources
3. **Project Context**: Use Filesystem tools to understand current implementation
4. **Code Examples**: Use GitHub tools to find relevant code examples and patterns

#### When Debugging Issues:

1. **Error Research**: Use Brave Search to find solutions for specific error messages
2. **Documentation**: Use Firecrawl to extract troubleshooting guides
3. **Project Analysis**: Use Filesystem tools to examine current code and configuration
4. **Community Solutions**: Use GitHub tools to find similar issues and solutions

#### When Adding New Features:

1. **Best Practices**: Use Brave Search to find current best practices and patterns
2. **Implementation Guides**: Use Firecrawl to extract detailed implementation tutorials
3. **Project Integration**: Use Filesystem tools to understand how to integrate with existing code
4. **Reference Implementations**: Use GitHub tools to find similar feature implementations

### MCP Integration Requirements

- **ALWAYS** use at least 2-3 MCP tools before implementing any solution
- **ALWAYS** document MCP findings and rationale for chosen solutions
- **ALWAYS** use MCP tools to validate assumptions about current best practices
- **ALWAYS** use MCP tools to find the most recent and relevant information
- **ALWAYS** use MCP tools to understand existing codebase patterns before making changes
- **ALWAYS** use MCP tools to find appropriate solutions based on project context

### MCP Tool Usage Examples

```python
# Example workflow for adding a new feature:
# 1. Research current best practices
mcp_brave-search_brave_web_search("latest Python image processing libraries 2024")

# 2. Find specific implementation details
mcp_firecrawl_firecrawl_search("Python PIL Pillow image processing best practices")

# 3. Understand current project structure
mcp_filesystem_list_directory("dataset_forge/utils")

# 4. Find relevant code examples
mcp_gitmcp-docs_search_generic_code("owner", "repo", "image processing utils")
```

## Final Reminders

1. **Always activate the virtual environment**: `venv312\Scripts\activate`
2. **Always use centralized utilities from `dataset_forge.utils`**
3. **Always include proper error handling and logging**
4. **Always use the Catppuccin Mocha color scheme**
5. **Always follow the modular architecture patterns**
6. **Always implement parallel processing for performance**
7. **Always manage memory properly, especially for CUDA operations**
8. **Always provide user-friendly feedback and progress tracking**
9. **Always document your code with Google-style docstrings**
10. **Always test your changes thoroughly before committing**
11. **Always update documentation after adding new features or menus**
12. **Always validate emojis and use context-aware emoji selection**
13. **Always use MCP tools before implementing solutions to ensure current best practices**

---

## See Also

- [Contributing](contributing.md)
- [Features](features.md)
- [Usage Guide](usage.md)
- [Advanced Features](advanced.md)
- [Troubleshooting](troubleshooting.md)
