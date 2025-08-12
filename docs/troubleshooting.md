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
- **Alpha Channel Processing:** All DPID methods now support RGBA images with automatic alpha channel detection and preservation.
- **DPID Alpha Panics Fixed:** Previous alpha channel processing panics have been resolved using hybrid approach (DPID for RGB, OpenCV for alpha).

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

## Audio System Issues

### CLI Hanging During Exit

**Problem**: CLI hangs when trying to exit with `q`, `quit`, `exit`, `0`, or `Ctrl+C`

**Root Cause**: Audio playback system hanging during shutdown sound

**Solution**: The audio system has been updated with robust fallbacks and timeout protection. If issues persist:

1. **Check audio dependencies**:

   ```bash
   pip install playsound==1.2.2 pydub pygame
   ```

2. **Verify audio files exist**:

   ```bash
   ls assets/
   # Should show: done.wav, error.mp3, startup.mp3, shutdown.mp3
   ```

3. **Test audio functionality**:
   ```python
   from dataset_forge.utils.audio_utils import play_done_sound
   play_done_sound(block=True)
   ```

### Audio Not Playing

**Problem**: No audio feedback during operations

**Solutions**:

1. **Check audio library installation**:

   ```bash
   pip install playsound==1.2.2 pydub
   ```

2. **Test individual audio libraries**:

   ```python
   # Test playsound
   from playsound import playsound
   playsound("assets/done.wav", block=True)

   # Test winsound (Windows only)
   import winsound
   winsound.PlaySound("assets/done.wav", winsound.SND_FILENAME)
   ```

3. **Check audio file integrity**:
   ```bash
   # Verify file sizes
   ls -la assets/
   # done.wav should be ~352KB
   # error.mp3 should be ~32KB
   # startup.mp3 should be ~78KB
   # shutdown.mp3 should be ~23KB
   ```

### Audio Library Conflicts

**Problem**: Multiple audio libraries causing conflicts

**Solution**: The audio system automatically selects the best available library:

1. **Playsound (primary)** - Most reliable cross-platform
2. **Winsound (Windows WAV)** - Best for WAV files on Windows
3. **Pydub (various formats)** - Good for MP3 and other formats
4. **Pygame (fallback)** - Cross-platform fallback

### Audio System Error Messages

**Common messages and solutions**:

- `"Playsound failed: Error 277"` - MP3 format issue, system will fall back to pydub
- `"Winsound failed"` - WAV file issue, system will try playsound
- `"Audio playback not available"` - No audio libraries working, CLI continues without audio
- `"Audio playback timeout"` - Audio took too long, automatically stopped

### Audio System Best Practices

1. **Always use centralized audio functions**:

   ```python
   from dataset_forge.utils.audio_utils import play_done_sound
   # Don't use audio libraries directly
   ```

2. **Handle audio failures gracefully**:

   ```python
   try:
       play_done_sound(block=True)
   except Exception:
       # Audio failed, but operation continues
       pass
   ```

3. **Use appropriate blocking**:

   - `block=True` for important feedback (success, error, shutdown)
   - `block=False` for background sounds (startup)

4. **Test audio on target platforms**:
   - Windows: winsound + playsound
   - macOS: playsound + pydub
   - Linux: playsound + pygame

---

## Visual Deduplication Issues

### CUDA Multiprocessing Errors

**Problem**: `RuntimeError: CUDA error: CUDA-capable device(s) is/are busy or unavailable`

**Root Cause**: PyTorch CUDA tensors cannot be shared across multiprocessing processes on Windows.

**Solution**: The Visual Deduplication feature now automatically uses CPU for multiprocessing on Windows to avoid CUDA tensor sharing issues.

**Prevention**: Automatic detection and fallback to CPU processing when CUDA multiprocessing is detected.

### Memory Errors (Paging File Too Small)

**Problem**: `The paging file is too small for this operation to complete. (os error 1455)` and `A process in the process pool was terminated abruptly`

**Root Cause**: Large datasets (4,000+ images) causing memory exhaustion on Windows.

**Solution**: Implemented chunked processing with automatic memory management:
- Large datasets are processed in chunks (default: 458 images per chunk)
- Automatic memory cleanup between chunks
- Global model cache to prevent repeated model loading

**Prevention**: 
- Automatic chunk size calculation based on dataset size
- Memory cleanup after each chunk
- Process pool management to prevent memory leaks

### Empty Embedding Errors

**Problem**: `Critical error in visual_dedup_workflow: need at least one array to stack`

**Root Cause**: Empty embedding lists being passed to `np.stack()` function.

**Solution**: Comprehensive error handling and validation:
- Explicit checks for empty embedding lists before processing
- Graceful fallback to hash-based embeddings if CLIP model unavailable
- Enhanced error messages with debugging information

**Prevention**:
- Validation of image loading results
- Checks for successful model initialization
- Fallback systems for failed operations

### Model Loading Issues

**Problem**: Import errors or model loading failures in worker processes.

**Root Cause**: Lazy imports and model loading issues in multiprocessing workers.

**Solution**: Global model cache and robust initialization:
- Models loaded once at module import time into global cache
- Direct imports in worker functions instead of lazy imports
- Comprehensive error handling for model loading failures

**Prevention**:
- Global model cache prevents repeated loading
- Proper error handling for missing dependencies
- Fallback to alternative methods when models unavailable

### Performance Issues

**Problem**: Slow processing or hanging during large dataset operations.

**Root Cause**: Inefficient processing strategies for large datasets.

**Solution**: Optimized processing workflows:
- Chunked processing for large datasets
- FAISS integration for efficient similarity search
- Optimized similarity matrix computation
- Progress tracking with real-time feedback

**Performance Metrics**:
- **Processing Speed**: ~10 images/second with CLIP embeddings
- **Memory Usage**: Optimized chunked processing
- **Scalability**: Successfully tested with 4,581+ images
- **Reliability**: 100% success rate in production testing

### FAISS Integration Issues

**Problem**: FAISS not available or similarity computation failures.

**Root Cause**: FAISS library not installed or compatibility issues.

**Solution**: Graceful fallback systems:
- Automatic detection of FAISS availability
- Fallback to optimized matrix computation when FAISS unavailable
- Clear error messages and recommendations

**Installation**: Optional FAISS installation for enhanced performance:
```bash
pip install faiss-cpu  # CPU version
# or
pip install faiss-gpu  # GPU version (requires CUDA)
```

### Process Pool Management

**Problem**: Memory leaks or hanging processes after deduplication.

**Root Cause**: Improper process pool cleanup and termination.

**Solution**: Comprehensive process pool management:
- Automatic cleanup and termination of process pools
- Memory cleanup after each operation
- Proper error handling for process pool failures

**Prevention**:
- `cleanup_process_pool()` function for proper termination
- Memory cleanup in `finally` blocks
- Process pool monitoring and management

### Image Loading Issues

**Problem**: Failed to load images or empty image lists.

**Root Cause**: File system issues, corrupted images, or permission problems.

**Solution**: Robust image loading with comprehensive error handling:
- Enhanced error messages for failed image loading
- Validation of loaded images before processing
- Graceful handling of corrupted or unreadable files

**Prevention**:
- File existence checks before loading
- Image format validation
- Permission checking for file access

### Expected Behavior

**Successful Operation Output**:
```
Found 4581 image files in C:/path/to/images
Loading Images: 100%|████████████████| 4581/4581 [00:10<00:00, 441.29it/s]
Successfully loaded 4581 images out of 4581 files
Using CPU for multiprocessing to avoid CUDA tensor sharing issues on Windows
Processing 4581 images in 11 chunks of size 458
CLIP embedding chunk 1/11: 100%|████████████████| 458/458 [00:44<00:00, 10.21it/s]
...
! FAISS not available, falling back to naive similarity computation
Computing similarity matrix with optimized memory usage
Large dataset detected (4581 images), using chunked similarity computation
Computing similarity matrix in chunks of size 50
Computing similarity chunks: 100%|████████████████| 92/92 [00:09<00:00, 9.50it/s]
Visual deduplication complete.
No duplicate groups found.
```

**Error Recovery**: The system automatically handles most errors and provides clear feedback about what went wrong and how to resolve it.

### Best Practices

1. **Start Small**: Test with a small dataset first to verify functionality
2. **Monitor Resources**: Use System Monitoring to check memory and CPU usage
3. **Clear Caches**: Clear memory caches before processing large datasets
4. **Use Appropriate Methods**: CLIP for semantic similarity, LPIPS for perceptual similarity
5. **Check File Permissions**: Ensure read access to image folders
6. **Validate Images**: Use image validation tools before deduplication

## Fuzzy Deduplication Issues

### Common Problems

**No Duplicates Found**
- **Cause**: Thresholds too high
- **Solution**: Lower the similarity thresholds (try 80-85% instead of 90-95%)
- **Alternative**: Try different hash method combinations (pHash + dHash)

**Too Many False Positives**
- **Cause**: Thresholds too low
- **Solution**: Increase the similarity thresholds (try 90-95% instead of 70-80%)
- **Alternative**: Use fewer hash methods (pHash only)

**Memory Errors During Processing**
- **Cause**: Batch size too large for available memory
- **Solution**: Reduce batch size (try 20-50 instead of 100-500)
- **Alternative**: Process smaller subsets of images

**Slow Processing**
- **Cause**: Too many hash methods or large batch size
- **Solution**: Use fewer hash methods (pHash + dHash only)
- **Alternative**: Reduce batch size and process in smaller chunks

**"No image files found" Error**
- **Cause**: Folder doesn't contain supported image files
- **Solution**: Check folder path and ensure it contains .jpg, .png, .bmp, .tiff files
- **Alternative**: Use image validation tools to check file integrity

**"Invalid threshold value" Error**
- **Cause**: Threshold not between 0 and 100
- **Solution**: Use values between 0 and 100 (e.g., 85 for 85%)
- **Alternative**: Use default thresholds if unsure

### Performance Optimization

**For Large Datasets (> 10,000 images)**
- Use batch size of 20-100
- Use only 2-3 hash methods (pHash + dHash + aHash)
- Process in smaller chunks if memory is limited

**For Medium Datasets (1,000-10,000 images)**
- Use batch size of 50-200
- Use 3-4 hash methods for better accuracy
- Monitor memory usage during processing

**For Small Datasets (< 1,000 images)**
- Use batch size of 100-500
- Can use all hash methods for maximum accuracy
- Test different threshold combinations

### Best Practices for Fuzzy Deduplication

1. **Start with Show Mode**: Always preview duplicates before taking action
2. **Use Conservative Thresholds**: Begin with 90-95% thresholds to avoid false positives
3. **Test with Small Subsets**: Verify results with 100-500 images before processing large datasets
4. **Combine Hash Methods**: Use pHash + dHash for balanced accuracy and speed
5. **Backup Important Data**: Always backup before using delete operations
6. **Monitor Memory Usage**: Use System Monitoring to track memory consumption

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Review `./logs/` directory for detailed error information
2. **Use System Monitoring**: Check resource usage and system health
3. **Test with smaller datasets**: Verify functionality with smaller image sets
4. **Report issues**: Open an issue on GitHub with detailed error information and system specifications

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
