[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Advanced Features & Configuration

This document covers advanced usage, configuration, and developer patterns for Dataset Forge. For user-facing features, see [features.md](features.md).

---

## Advanced Configuration

- **Custom config files**: Use JSON, YAML, or HCL for advanced workflows.
- **Integration with external tools**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer), [traiNNer-redux](https://github.com/the-database/traiNNer-redux), [getnative](https://github.com/Infiziert90/getnative), [resdet](https://github.com/0x09/resdet)
- **Batch processing and memory optimization**: Tune batch sizes and memory settings in the config files for large datasets.
- **OpenModelDB integration**: Advanced model management and upscaling workflows.

## Advanced Monitoring & Analytics

- **Add new analytics hooks**: Decorate new actions with `@monitor_performance` and `@track_errors`.
- **Background task management**: Register new subprocesses/threads for monitoring.
- **Persistent logging**: Ensure all analytics and errors are logged to ./logs/.

---

For user workflows and feature summaries, see [features.md](features.md). For code style and requirements, see [style_guide.md](style_guide.md).

## Robust Menu Loop Pattern (July 2025)

All Dataset Forge menus now use a robust menu loop pattern to ensure reliability and maintainability. This pattern ensures that:

- The user's menu selection (key) is always used to look up the corresponding action in the options dictionary.
- Only callable actions are executed; if the action is not callable, a clear error is printed.
- Debug prints for both the selected key and resolved action are included for easier debugging.

**Pattern Example:**

```python
while True:
    key = show_menu("Menu Title", options, ...)
    print(f"DEBUG: key={key!r}, type={type(key)}")
    if key is None or key == "0":
        break
    action = options.get(key, (None, None))[1]
    print(f"DEBUG: action={action!r}, type={type(action)}")
    if callable(action):
        action()
    else:
        print_error(f"Selected action is not callable: {action!r} (type={type(action)})")
```

**Why this matters:**

- Prevents menu loops from breaking if the user input is not mapped to a callable.
- Ensures all menu actions are robust to user error and code changes.
- Makes debugging easier by providing clear output for both valid and invalid selections.

**Enforcement:**

- As of July 2025, all menus in Dataset Forge have been updated to use this pattern.
- If you add a new menu, you must use this pattern for consistency and reliability.

## Advanced Testing Patterns

- The test suite uses pytest fixtures and monkeypatching to isolate tests and mock external dependencies (audio, file I/O, heavy computation).
- To add tests for new features, create a new test file in tests/test_utils/ or tests/ as appropriate.
- All new features and bugfixes must include appropriate tests.
