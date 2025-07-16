[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Project Architecture

Dataset Forge is built with a modular, extensible architecture for maintainability and performance.

## Directory Structure

- **dataset_forge/menus/**: UI layer (CLI menus, user interaction)
- **dataset_forge/actions/**: Business logic (core dataset/image operations)
- **dataset_forge/utils/**: Reusable utilities (file ops, memory, parallelism, color, monitoring, etc.)
- **dataset_forge/dpid/**: Multiple DPID (degradation) implementations
- **configs/**: Example and user configuration files
- **reports/**: Report templates for HTML/Markdown output
- **assets/**: Any asset files required
- **docs/**: Project documentation
- **tests/**: Unit & integration tests
- **tools/**: Project tools and developer utilities (e.g., static analysis, documentation merging)
  - **find_code_issues/find_code_issues.py**: Static analysis and code quality tool for maintainers. Checks for dead code, untested code, missing docstrings, test/code mapping, and more. Outputs actionable reports to the same directory.

## Monitoring & Analytics

- Centralized resource monitoring, analytics, error tracking, health checks, and background task registry (see utils/monitoring.py).
- CLI menu for live resource usage, analytics, error summaries, health checks, and background task management (see menus/system_monitoring_menu.py).
- Persistent logging and notifications for all major operations.

## Test Suite Integration

- Comprehensive automated test suite using pytest.
- Covers CLI, menu timing, error feedback, memory, parallelism, and file/image utilities.

### Umzi's Dataset_Preprocessing Integration

The Umzi Dataset_Preprocessing workflows are now fully modularized within Dataset Forge:

- Business logic is in `actions/umzi_dataset_preprocessing_actions.py`.
- UI/menu is in `menus/umzi_dataset_preprocessing_menu.py`.
- Uses lazy imports, robust menu loop, and centralized utilities.
- See `docs/advanced.md` for a detailed discussion of the porting and modularization process.

---

For coding standards and best practices, see [style_guide.md](style_guide.md).
