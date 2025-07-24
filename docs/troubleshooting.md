[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Troubleshooting

This guide provides solutions to common issues in Dataset Forge. For advanced usage and developer troubleshooting, see [advanced.md](advanced.md).

---

## Dependancy & Library Issues

**Problem:** Import errors or menu options not working.

- Please see: [Special Installation Instructions](troubleshooting.md)

## Menu Timing & Profiling Issues

**Problem:** Timing prints do not appear after loading a menu or submenu.

- Ensure you are running the latest version of Dataset Forge.
- Check that the menu or submenu uses the `time_and_record_menu_load` utility.
- "Back" and "Exit" options do not trigger timing prints.

## Menu Loop Issues

**Problem:** Errors occur when navigating menus (e.g., `TypeError: 'str' object is not callable`).

- All menu loops should check if the action is callable before calling it.
- Update your menu code to follow the robust menu loop pattern (see [style_guide.md](style_guide.md)).

**Problem:** Menu redraws repeatedly or submenus do not appear.

- Ensure the menu loop uses the robust pattern:
  - Get the user's choice (key) from `show_menu`.
  - Look up the action in the options dictionary.
  - Call the action if callable.

## Other Issues

- For monitoring/analytics issues, check the logs in the ./logs/ directory.
- If tests fail, ensure your environment matches the requirements and all dependencies are installed.

## Test Failures

- If you encounter a failing test, check for function signature mismatches, especially with parallel utilities that pass extra kwargs (e.g., play_audio).
- Ensure all monkeypatches and fixtures match the expected types and return values.

---

## 🧪 Test Suite Troubleshooting (July 2025)

- **Monkeypatch signature mismatch:** Ensure dummy functions/classes accept all arguments used in the real code (e.g., `color=None`, `**kwargs`).
- **Multiprocessing pickling errors:** Worker functions must be defined at module level, not nested inside other functions.
- **XFAIL tests:** Some tests (e.g., ignore patterns in directory tree) are marked XFAIL by design; see docs for details.

See [Style Guide](style_guide.md#testing-patterns) and [features.md](features.md#comprehensive-test-suite).

---

## Static Analysis Tool Issues

**Problem:** The static analysis script (`tools/find_code_issues/find_code_issues.py`) fails to run, or you get unexpected results.

- Ensure all dependencies are installed: `pip install vulture pytest pytest-cov coverage pyan3 pyflakes`
- If you get import errors, check your virtual environment and Python version.
- If the script reports no files found, check your directory structure and that the codebase is present.
- The script overwrites its output files in `tools/find_code_issues/` on each run.
- Review the log file (`find_code_issues.log`) for detailed error messages.

---

## Metadata Management Issues (NEW July 2025)

**Problem:** exiftool not found or not working.

- Ensure exiftool is installed and in your system PATH. Download from https://exiftool.org/.
- On Windows, you may need to rename exiftool(-k).exe to exiftool.exe and add its folder to PATH.
- Restart your terminal after installation.

**Problem:** pandas or SQLite errors when extracting/filtering metadata.

- Ensure pandas is installed: `pip install pandas`
- SQLite is included with Python, but ensure your Python is not missing standard libraries.
- Check your CSV/SQLite file for corruption or incomplete extraction.

**Problem:** Metadata extraction returns empty or incomplete results.

- Some image formats may not contain metadata, or may be corrupted.
- Try running exiftool manually on a sample file to debug.
- Check file permissions and ensure files are not locked by another process.

---

## Utility Scripts (tools/) Troubleshooting

### find_code_issues.py

- **Problem:** Script fails to run, or you get unexpected results.
  - Ensure all dependencies are installed: `pip install vulture pytest pytest-cov coverage pyan3 pyflakes`
  - If you get import errors, check your virtual environment and Python version.
  - If the script reports no files found, check your directory structure and that the codebase is present.
  - The script overwrites its output files in `tools/find_code_issues/` on each run.
  - Review the log file (`find_code_issues.log`) for detailed error messages.

### merge_docs.py

- **Problem:** Documentation files are missing or not merged.
  - Ensure all documentation files exist and are readable.
  - If you see missing file warnings, check the `DOC_ORDER` list in the script.
  - If output files are not updated, check file permissions in the docs/ directory.

### install.py

- **Problem:** Python version is too low.
  - Upgrade to Python 3.12+.
- **Problem:** CUDA-enabled torch fails to install.
  - Check your CUDA version and use the correct index URL for torch.
- **Problem:** pip install fails.
  - Check your internet connection and permissions.
  - Try running the command as administrator or with sudo (Linux/Mac).

### print_zsteg_env.py

- **Problem:** `zsteg` is not found.
  - Ensure `zsteg` is installed and in your PATH.
  - On Windows, you may need to restart your terminal after adding to PATH.
- **Problem:** PATH is not updated.
  - Double-check your environment variable settings and restart your terminal.

---

---

## Enhanced Caching System Issues (NEW July 2025)

**Problem:** Cache misses or unexpected cache behavior.

- Check TTL settings: cached data may have expired
- Verify cache size limits: in-memory cache may have evicted entries
- Use cache statistics to analyze hit rates and performance
- Clear and rebuild cache if corruption is suspected

**Problem:** High memory usage from caching.

- Monitor cache statistics for memory usage
- Reduce maxsize limits for in-memory caches
- Use TTL to prevent memory leaks
- Clear caches when memory pressure is high
- Enable compression for large objects

**Problem:** Disk cache corruption or missing files.

- Use cache validation tools to detect corruption
- Run cache repair to fix corrupted entries
- Check disk space availability
- Verify file permissions in cache directory

**Problem:** Cache management menu not accessible.

- Ensure you're accessing from System Settings → Cache Management
- Check that cache_management_menu.py is properly integrated
- Verify lazy import pattern is working correctly

**Problem:** Model cache issues with CUDA memory.

- Model cache includes automatic CUDA memory management
- Clear model cache if GPU memory issues occur
- Monitor CUDA memory usage during model operations
- Use appropriate TTL for model caching

**Problem:** Smart cache auto-detection not working.

- Check function names for keywords: "model", "load", "embedding" for model cache
- Check function names for keywords: "extract", "compute", "process" for disk cache
- Verify cache_dir parameter is passed correctly for disk cache
- Use explicit cache type if auto-detection fails

**Debug Tools:**

- Use cache statistics to analyze performance
- Export cache data for offline analysis
- Run cache validation and repair tools
- Monitor cache hit rates and memory usage

For further help, see [usage.md](usage.md) or contact the project maintainer.

## DPID & pepedpid Issues (NEW July 2025)

**Problem:** ImportError or menu option for Umzi's DPID (pepedpid) not working.

- Ensure pepedpid is installed: `pip install pepedpid`
- If you get ImportError, check your virtual environment and that pepedpid is installed in the correct environment.
- If you get errors running DPID workflows, ensure you are using the correct menu option and that your input folders contain valid images.
- All DPID implementations (including Umzi's) are modular and covered by robust, non-interactive tests. If tests fail, check for monkeypatching or signature mismatches in your test environment.
- For further help, see [usage.md](usage.md) or contact the project maintainer.

## Missing Workflow Headings

If you don’t see clear workflow headings before prompts and progress bars, the workflow may be outdated or not following project standards. Please update the workflow to match the Style Guide.
