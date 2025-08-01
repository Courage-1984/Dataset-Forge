[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Troubleshooting

> **Who is this for?**  
> This guide is for anyone encountering errors, installation problems, or unexpected behavior in Dataset Forge.

---

## Installation & Environment Issues

- **Python version too low:** Upgrade to Python 3.12+.
- **CUDA/torch install fails:** Check your CUDA version and use the correct index URL for torch.
- **pip install fails:** Check your internet connection and permissions. Try running as administrator.
- **python-magic errors on Windows:** Copy required DLLs to `C:/Windows/System32/`. See [Special Installation Instructions](special_installation.md).
- **VapourSynth/getnative:** Install VapourSynth before getnative. See [Special Installation Instructions](special_installation.md).

---

## Common CLI & Workflow Issues

- **Import errors or menu options not working:** Ensure all dependencies are installed. See [Special Installation Instructions](special_installation.md).
- **Menu redraws or submenus not appearing:** Update your menu code to follow the robust menu loop pattern (see [style_guide.md](style_guide.md)).
- **Timing prints missing:** Ensure you are running the latest version and using the correct utilities.
- **Missing workflow headings:** Update the workflow to match the Style Guide.

---

## Test Suite & Developer Tools

- **Test failures:** Check for function signature mismatches, especially with parallel utilities. Ensure all monkeypatches and fixtures match expected types.
- **Static analysis tool fails:** Ensure all dependencies are installed. Check your virtual environment and directory structure.
- **Menu auditing tool issues:** Check that menu functions end with `_menu` and are in `dataset_forge/menus/`. Import errors for complex function references are normal.
- **Utility scripts not working:** Check dependencies, permissions, and environment variables.

---

## Metadata & Caching Issues

- **exiftool not found:** Ensure exiftool is installed and in your PATH. Restart your terminal after installation.
- **pandas/SQLite errors:** Ensure pandas is installed and your Python includes standard libraries.
- **Cache misses or high memory usage:** Check TTL and maxsize settings. Use cache statistics to analyze performance. Clear caches if needed.

---

## DPID & External Tools

- **pepedpid ImportError:** Ensure pepedpid is installed in the correct environment.
- **DPID workflow errors:** Check input folders for valid images and use the correct menu option.

## Steganography Tools (zsteg, steghide)

### ZSTEG Executable Issues

**Problem**: `zsteg.exe` fails with side-by-side configuration error:
```
14001: The application has failed to start because its side-by-side configuration is incorrect.
Please see the application event log or use the command-line sxstrace.exe tool for more detail.
- C:/Users/anon/AppData/Local/Temp/ocran00074B817894/lib/ruby/3.4.0/x64-mingw-ucrt/zlib.so (LoadError)
```

**Root Cause**: OCRA-built executables have dependency issues with native extensions like `zlib.so` and missing `zlib1.dll`.

**Solution 1: OCRAN-Based Executable (RECOMMENDED)**

Replace OCRA with OCRAN (maintained fork) for better Windows compatibility:

```bash
# Remove old OCRA and install OCRAN
gem uninstall ocra
gem install ocran

# Create zsteg CLI wrapper
# Create file: zsteg_cli.rb
#!/usr/bin/env ruby
puts "Starting zsteg_cli.rb..."
puts "ARGV: #{ARGV.inspect}"
STDOUT.flush
STDERR.flush
require 'zsteg'
require 'zsteg/cli/cli'
ZSteg::CLI::Cli.new.run

# Build executable with OCRAN
ocran zsteg_cli.rb --gem-all --add-all-core --output zsteg.exe --verbose

# Test the executable
.\zsteg.exe --help
```

**Solution 2: PowerShell Wrapper (Alternative)**

Use a PowerShell wrapper that gracefully falls back to gem-installed zsteg:

```powershell
# Create zsteg_wrapper.ps1
# Attempts OCRA executable first, falls back to gem-installed zsteg
powershell -ExecutionPolicy Bypass -File "zsteg_wrapper.ps1" --help
```

**Solution 3: Gem Installation (Simplest)**

Use gem-installed zsteg directly:
```bash
gem install zsteg
zsteg --help
```

### Other Steganography Issues

- **zsteg not found:** Ensure zsteg is installed via `gem install zsteg`
- **steghide not found:** Ensure steghide is installed and the folder is added to your PATH. See [Special Installation Instructions](special_installation.md).

---

## FAQ

See below for frequently asked questions. For more, visit the [Discussion Board](https://github.com/Courage-1984/Dataset-Forge/discussions).

<details>
<summary><strong>Frequently Asked Questions (FAQ)</strong></summary>

- **What is Dataset Forge?**  
  Modular Python CLI tool for managing, analyzing, and transforming image datasets, with a focus on HQ/LQ pairs for super-resolution and ML workflows.

- **What platforms are supported?**  
  Windows (primary), Linux/macOS (not yet tested).

- **What Python version is required?**  
  Python 3.12+ is recommended.

- **How do I install Dataset Forge and its dependencies?**  
  See the [Quick Start](../README.md#-quick-start) and [Special Installation Instructions](special_installation.md).

- **Why do I need to install VapourSynth before getnative?**  
  getnative depends on VapourSynth. See [Special Installation Instructions](special_installation.md).

- **How do I fix python-magic errors on Windows?**  
  Copy required DLLs to `C:/Windows/System32/`. See [Special Installation Instructions](special_installation.md).

- **How do I run the test suite?**  
  Activate the virtual environment and run `pytest`. See [usage.md](usage.md).

- **How do I use the monitoring and analytics features?**  
  Access the System Monitoring menu from the CLI. See [features.md](features.md).

- **What should I do if I get CUDA or GPU errors?**  
  Ensure your CUDA/cuDNN versions match your PyTorch install. Lower batch size or use CPU fallback if needed.

- **What if a menu or feature is missing or crashes?**  
  Make sure you are running the latest version. Check the logs in the `./logs/` directory.

- **How do I analyze the menu system structure?**  
  Use the menu auditing tool: `python tools/log_current_menu.py`. It generates a comprehensive report at `menu_system/current_menu.md`.

- **How do I get help or report a bug?**  
  Open an issue on GitHub or contact the project maintainer.

- **How do I create a standalone zsteg.exe executable?**  
  Use the OCRAN method described in [Special Installation Instructions](special_installation.md). This creates a self-contained executable that doesn't require Ruby to be installed on the target system.

- **Why does my zsteg.exe show side-by-side configuration errors?**  
  This is a common issue with the original OCRA. Use the newer OCRAN tool instead, which properly handles native dependencies like `zlib.so` and `zlib1.dll`.

</details>

---

## See Also

- [Getting Started](getting_started.md)
- [Special Installation Instructions](special_installation.md)
- [Usage Guide](usage.md)
- [Features](features.md)
- [Style Guide](style_guide.md)

If your question is not answered here, check the [usage guide](usage.md), [troubleshooting guide](troubleshooting.md), or open an issue.
