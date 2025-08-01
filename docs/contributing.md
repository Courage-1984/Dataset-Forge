[ Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Contributing

> **Who is this for?**  
> Anyone who wants to contribute code, documentation, or ideas to Dataset Forge.

---

## How to Contribute

1. **Read the [Style Guide](style_guide.md)**  
   All code must follow the project's coding standards, modular architecture, and documentation requirements.
2. **Fork the repository** and create a new branch for your feature or fix.
3. **Write clear, well-documented code**
   - Use Google-style docstrings and type hints for all public functions/classes.
   - Add or update tests in `tests/` for new features or bugfixes.
   - Update or add documentation in the appropriate `docs/` file(s).
4. **Test your changes**
   - Activate the virtual environment: `venv312\Scripts\activate`
   - Run the test suite: `pytest`
   - Ensure all tests pass on your platform (Windows and/or Linux).
5. **Submit a Pull Request (PR)**
   - Describe your changes clearly in the PR description.
   - Reference any related issues or discussions.
   - If your change affects documentation, mention which files were updated.
   - Be responsive to code review feedback.

---

## Development Guidelines

- **Modular Design:**  
  UI in `menus/`, business logic in `actions/`, helpers in `utils/`. Use lazy imports for menu actions.
- **Memory & Performance:**  
  Use centralized memory and parallel processing utilities. Always clean up memory after large operations.
- **Testing:**  
  Add tests for new features and bugfixes. Use pytest fixtures and monkeypatching as needed.
- **Documentation:**  
  Update relevant docs in `docs/` and regenerate `README_full.md` and `toc.md` using `merge_docs.py` after changes.
- **Commit Messages:**  
  Use clear, descriptive commit messages (e.g., `feat: add CBIR duplicate detection`, `fix: handle VapourSynth import error`).
- **Community Standards:**  
  Be respectful and constructive in all communications. Report bugs or suggest features via GitHub Issues.

---

## Doc Maintenance

- After updating any documentation, always regenerate `docs/README_full.md` and `docs/toc.md` using `merge_docs.py`.
- For major changes, update `docs/changelog.md`.
- For new documentation sections, create a new markdown file in `docs/` and add it to the Table of Contents in `README.md` and `docs/toc.md`.

---

## Static Analysis & Code Quality

- Before submitting a PR, you **must** run the static analysis tool (`tools/find_code_issues.py`) and address all actionable issues (dead code, untested code, missing docstrings, dependency issues, configuration problems, etc.).
- **Theming Consistency**: You **must** run the theming consistency checker (`tools/check_mocha_theming.py`) and address all critical theming issues (raw print statements, missing imports, incorrect menu patterns).
- All public functions/classes/methods must have Google-style docstrings.
- All user-facing output must use centralized printing utilities with Catppuccin Mocha colors.
- The static analysis script saves all output files to `./logs/find_code_issues/` for easy review and analysis.
- The theming checker saves reports to `./logs/mocha_theming_report.md` by default.
- See [usage.md](usage.md) and [features.md](features.md) for details.

## Menu System Development

- **Menu Auditing**: Use the menu auditing tool (`tools/log_current_menu.py`) to analyze menu hierarchy and identify improvement opportunities.
- **Menu Pattern Compliance**: All menus must follow the standardized key-based pattern documented in `.cursorrules`.
- **Menu Testing**: Ensure new menus are testable and follow the established patterns for help/quit functionality.
- **Menu Documentation**: Update menu documentation when adding new menus or changing menu structure.

### Global Command System Development

- **Global Commands**: All menus must support `help`, `h`, `?` for context-aware help and `quit`, `exit`, `q` for instant quit
- **Menu Context**: Define comprehensive `menu_context` dictionaries for each menu with purpose, options, navigation, key features, and tips
- **Testing**: Global command functionality must be covered by unit and integration tests
- **Documentation**: Update help documentation when adding new menus or changing menu structure

### MCP Integration Development (MANDATORY)

Dataset Forge is configured with comprehensive MCP (Model Context Protocol) servers for enhanced development. **ALL contributors MUST use MCP tools before implementing solutions.**

#### **Available MCP Servers**

1. **Brave Search Tools** (Primary Research)

   - `mcp_brave-search_brave_web_search` - General web research, latest libraries, best practices
   - `mcp_brave-search_brave_news_search` - Recent developments and updates
   - `mcp_brave-search_brave_local_search` - Location-specific information
   - `mcp_brave-search_brave_video_search` - Tutorials and demonstrations
   - `mcp_brave-search_brave_image_search` - Visual references

2. **Firecrawl Tools** (Deep Web Scraping)

   - `mcp_firecrawl_firecrawl_search` - Comprehensive web search with content extraction
   - `mcp_firecrawl_firecrawl_scrape` - Detailed content extraction from specific URLs
   - `mcp_firecrawl_firecrawl_map` - Discovering website structure
   - `mcp_firecrawl_firecrawl_extract` - Structured data extraction
   - `mcp_firecrawl_firecrawl_deep_research` - Complex research questions

3. **Filesystem Tools** (Project Analysis)

   - `mcp_filesystem_read_text_file` - Read and analyze project files
   - `mcp_filesystem_list_directory` - Understand project structure
   - `mcp_filesystem_search_files` - Find specific files or patterns
   - `mcp_filesystem_get_file_info` - Detailed file metadata analysis
   - `mcp_filesystem_directory_tree` - Comprehensive project structure visualization

4. **GitHub Integration Tools** (Code Examples)
   - `mcp_gitmcp-docs_fetch_generic_documentation` - GitHub repository documentation
   - `mcp_gitmcp-docs_search_generic_code` - Finding code examples in repositories
   - `mcp_gitmcp-docs_search_generic_documentation` - Documentation searches
   - `mcp_gitmcp-docs_match_common_libs_owner_repo_mapping` - Library-to-repo mapping

#### **MCP Tool Usage Patterns (MANDATORY)**

##### Before Implementing Any Solution:

1. **Research Phase**: Use Brave Search to find latest libraries, best practices, and solutions
2. **Deep Dive**: Use Firecrawl to extract detailed content from relevant sources
3. **Project Context**: Use Filesystem tools to understand current implementation
4. **Code Examples**: Use GitHub tools to find relevant code examples and patterns

##### When Debugging Issues:

1. **Error Research**: Use Brave Search to find solutions for specific error messages
2. **Documentation**: Use Firecrawl to extract troubleshooting guides
3. **Project Analysis**: Use Filesystem tools to examine current code and configuration
4. **Community Solutions**: Use GitHub tools to find similar issues and solutions

##### When Adding New Features:

1. **Best Practices**: Use Brave Search to find current best practices and patterns
2. **Implementation Guides**: Use Firecrawl to extract detailed implementation tutorials
3. **Project Integration**: Use Filesystem tools to understand how to integrate with existing code
4. **Reference Implementations**: Use GitHub tools to find similar feature implementations

#### **MCP Integration Requirements**

- **ALWAYS** use at least 2-3 MCP tools before implementing any solution
- **ALWAYS** document MCP findings and rationale for chosen solutions
- **ALWAYS** use MCP tools to validate assumptions about current best practices
- **ALWAYS** use MCP tools to find the most recent and relevant information
- **ALWAYS** use MCP tools to understand existing codebase patterns before making changes
- **ALWAYS** use MCP tools to find appropriate solutions based on project context

#### **MCP Tool Usage Examples**

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

#### **Research Integration**

- **Automated Research**: Use MCP servers to automatically research new SISR techniques and tools
- **Documentation Extraction**: Extract and analyze documentation from external sources
- **Community Research**: Research community feedback and competitor features
- **Implementation Planning**: Use research findings to plan new features and improvements

#### **Code Quality Enhancement**

- **Pattern Analysis**: Use Filesystem MCP to analyze code patterns and consistency
- **Documentation Coverage**: Use MCP servers to identify missing documentation topics
- **Feature Research**: Research new features and tools for potential integration
- **Performance Analysis**: Analyze performance benchmarks and optimization techniques

### Menu Auditing Workflow

1. **Before Making Changes**: Run `python tools/log_current_menu.py` to understand the current menu structure
2. **After Adding Menus**: Re-run the audit to verify the new menu integrates properly
3. **Review Recommendations**: Check the generated report for suggestions on menu organization
4. **Monitor Statistics**: Track menu depth, size, and path input points over time

### Menu Auditing Features

- **Automatic Discovery**: Finds all menu files in `dataset_forge/menus/`
- **Path Input Detection**: Identifies menus requiring user input to prevent infinite loops
- **AST-Based Analysis**: Uses Python's Abstract Syntax Tree for accurate code parsing
- **Comprehensive Reporting**: Generates detailed analysis with statistics and recommendations
- **Configurable Depth**: Set maximum exploration depth (default: 4 levels)

---

## See Also

- [Style Guide](style_guide.md)
- [Features](features.md)
- [Usage Guide](usage.md)
- [Advanced Features](advanced.md)
- [Troubleshooting](troubleshooting.md)

For questions, open an issue or contact the project maintainer.
