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

- Before submitting a PR, you **must** run the static analysis tool (`tools/find_code_issues/find_code_issues.py`) and address all actionable issues (dead code, untested code, missing docstrings, etc.).
- All public functions/classes/methods must have Google-style docstrings.
- The script overwrites its output files in `tools/find_code_issues/` on each run.
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

### MCP Integration Development

Dataset Forge is configured with three MCP (Model Context Protocol) servers for enhanced development:

#### **Available MCP Servers**
- **Filesystem MCP**: Direct access to codebase and datasets for navigation and analysis
- **Brave Search MCP**: Privacy-focused web research for ML techniques and tools
- **Firecrawl MCP**: Web scraping for documentation and resource extraction

#### **Development Workflow with MCP**
```bash
# Enhanced Development Routine
1. Use Filesystem MCP to navigate and analyze codebase
2. Use Brave Search to research new ML techniques and tools
3. Use Firecrawl to extract relevant documentation and resources
4. Implement improvements based on research findings
5. Update documentation with new insights and techniques
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
