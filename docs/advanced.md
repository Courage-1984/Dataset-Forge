[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Advanced Features & Configuration

This document covers advanced usage, configuration, and developer patterns for Dataset Forge. For user-facing features, see [features.md](features.md).

---

## Advanced Configuration

- **Custom config files**: Use JSON, YAML, or HCL for advanced workflows.
- **Integration with external tools**: See [features.md](features.md#core--configuration).
- **Batch processing and memory optimization**: Tune batch sizes and memory settings in the config files for large datasets.
- **OpenModelDB integration**: Advanced model management and upscaling workflows.

## Extending Dataset Forge

- **Add new menu actions**: Use the lazy import pattern (see [style_guide.md](style_guide.md)).
- **Add new analytics or monitoring hooks**: Decorate long-running or user-facing functions with the provided decorators.
- **Add new CBIR models**: Extend the CBIR system by adding new embedding models in the actions layer.

## Implementation Patterns (for Developers)

- **Robust Menu Loop**: All menus and submenus must use the robust menu loop pattern. See [style_guide.md](style_guide.md) for the required code snippet and rationale.
- **Timing & Profiling**: Use the centralized timing utility (`time_and_record_menu_load` in `utils/monitoring.py`) to wrap menu and submenu loads. Timing prints are shown to the user and aggregated for analytics. See [style_guide.md](style_guide.md) for best practices.
- **Lazy Imports**: Use `lazy_action()` and `lazy_menu()` helpers to defer heavy imports until needed. This keeps the CLI fast and memory-efficient.

## Advanced CBIR (Content-Based Image Retrieval)

- **Add new embedding models**: Extend `cbir_actions.py` with new model support.
- **Optimize similarity search**: Use ANN indexing for large datasets.
- **Batch actions**: Implement new batch actions (remove, move, copy) in the CBIR workflow.

## Advanced Monitoring & Analytics

- **Add new analytics hooks**: Decorate new actions with `@monitor_performance` and `@track_errors`.
- **Background task management**: Register new subprocesses/threads for monitoring.
- **Persistent logging**: Ensure all analytics and errors are logged to ./logs/.

---

For user workflows and feature summaries, see [features.md](features.md). For code style and requirements, see [style_guide.md](style_guide.md).
