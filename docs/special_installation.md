[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Special Installation Instructions

This guide covers special installation requirements for certain dependencies in Dataset Forge. These steps are **critical** for correct operation, especially on Windows. Please read carefully and follow the order for each component.

---

## 1. PyTorch with CUDA (GPU Acceleration)

**You must install the correct CUDA-enabled version of torch/torchvision/torchaudio _before_ installing other requirements.**

**Quick Steps:**

```bat
venv312\Scripts\activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

- Replace `cu121` with your CUDA version if needed. See [PyTorch Get Started](https://pytorch.org/get-started/locally/) for details.
- If you skip this, pip will install the CPU-only version by default.
- Only after this, run `pip install .` or `pip install -r requirements.txt`.

**Troubleshooting:**

- Mismatched CUDA/cuDNN versions will cause import errors or no GPU support.
- See [requirements.txt](../requirements.txt) and [PyTorch docs](https://pytorch.org/get-started/locally/).

---

## 2. VapourSynth & getnative

> (for [getnative](https://github.com/Infiziert90/getnative) functionality/native resolution detection)

### Method 1: Windows (Quick)

1. Extract the following file from `assets/getnative.zip`:

   - `getnative.exe`

2. Add the `getnative.exe` file's path to your PATH.

### Method 2: Windows (Better; but *TRICKY*...)

**VapourSynth must be installed _before_ [getnative](https://github.com/Infiziert90/getnative).**

**Steps (Windows):**

1. Download and install [VapourSynth](http://www.vapoursynth.com/) (includes imwri plugin).
2. Open a terminal and run:

```bat
python vsrepo.py install descale
python vsrepo.py install ffms2
python vsrepo.py install lsmas
```

3. Activate your virtual environment:

```bat
venv312\Scripts\activate
```

4. Install getnative:

```bat
pip install getnative
```

### Method 3: Windows (try building `getnative.exe` yourself)

**Steps (Windows):**

1. Git clone the [getnative repo](https://github.com/Infiziert90/getnative):

```bat
git clone https://github.com/Infiziert90/getnative.git
cd getnative
```

2. Extract the following folder from `assets/vapoursynth_install.zip`:

   - `vapoursynth_install`

3. Copy the contents of the `vapoursynth_install` folder to ./getnative/ repo root and REPLACE existing files.

4. Follow the steps outlined in `env_create.md` which should be in your ./getnative/ repo root.

**Troubleshooting:**

- Install VapourSynth _before_ getnative or any requirements that depend on it.
- If getnative fails to import, check that VapourSynth is installed and on your PATH.
- Also make sure directory containing `vsrepo.py` and the plugin's folder containing the `.dll`s are also on your PATH.
- `./assets/vapoursynth_plugins_dll.zip` contains all 4 of the vapoursynth plugins' dll's (`descale`, `ffms2`, `lsmas` & `imwri`) for whatever its worth.

- See [Getnative Recommended Windows Installation](https://github.com/Infiziert90/getnative?tab=readme-ov-file#recommended-windows-installation) for more details.

---

## 3. python-magic (for `Enhanced Directory Tree`)

**Windows users:** You must install both the Python packages and the required DLLs.

**Steps:**

1. Install the packages:

```bat
venv312\Scripts\activate
pip install python-magic python-magic-bin libmagic
```

2. Copy the following files from `assets/libmagicwin64-master.zip` to `C:/Windows/System32/`:

   - `libgnurx-0.dll`
   - `magic.mgc`
   - `magic1.dll`

   (These are prebuilt for 64-bit Windows. See source: [libmagicwin64](https://github.com/pidydx/libmagicwin64) for details.)

3. When using python-magic, specify the magic file path if needed:

```python
import magic
file_magic = magic.Magic(magic_file="C:/Windows/System32/magic.mgc")
```

**Troubleshooting:**

- If you get import errors, ensure the DLLs are in `System32` and you are using the correct magic file path.
- See [python-magic docs](https://github.com/ahupp/python-magic) and [libmagicwin64](https://github.com/pidydx/libmagicwin64).

---

## 4. Using resdet for Native Resolution Detection

> Using [resdet](https://github.com/0x09/resdet) for Native Resolution Detection

### Method 1: Windows (WSL - Recommended for CLI Integration)

1. Clone the repository:
   ```sh
   git clone https://github.com/0x09/resdet.git
   cd resdet
   ```
2. Build resdet:
   ```sh
   sudo apt update
   sudo apt install build-essential
   sudo apt install pkg-config
   sudo apt install libfftw3-dev libpng-dev mjpegtools libmagickwand-dev
   cd path/to/resdet
   make clean
   ./configure
   make
   ```
3. Install resdet to your WSL PATH:
   ```sh
   sudo cp resdet /usr/local/bin/
   sudo chmod +x /usr/local/bin/resdet
   # Or, to use make install:
   sudo make install
   ```
4. **Note:** The Dataset Forge CLI will automatically use WSL to run resdet on Windows. Ensure resdet is available in your WSL environment's PATH.

### Method 2: Windows (MSYS2 MINGW64 Shell)

1. Clone the repository:
   ```sh
   git clone https://github.com/0x09/resdet.git
   ```
2. Open **MSYS2 MINGW64 Shell**.
3. Install dependencies:
   ```sh
   pacman -S base-devel mingw-w64-x86_64-toolchain mingw-w64-x86_64-libpng mingw-w64-x86_64-libjpeg-turbo mingw-w64-x86_64-fftw mingw-w64-x86_64-pkg-config autoconf automake libtool
   ```
4. Set PKG_CONFIG_PATH:
   ```sh
   export PKG_CONFIG_PATH=/mingw64/lib/pkgconfig
   ```
5. Build resdet:
   ```sh
   cd path/to/resdet
   make clean
   ./configure --prefix=/mingw64
   make
   ```
6. Add `resdet.exe` to a folder in your PATH, or add its folder to your PATH.

### Method 3: Windows (Windows pre-build binary)

1. Extract the following files from `assets/resdet_windows.zip`:

   - `resdet.exe`

   (This is a prebuilt for 64-bit Windows that I compiled.)

2. Add `resdet.exe` to a folder in your PATH, or add its folder to your PATH.

### Usage in Dataset Forge

- The CLI will detect your platform and use the appropriate resdet binary.
- On Windows, if WSL is available and resdet is installed in WSL, it will be used automatically.
- If resdet is not found, you will receive a clear error message with installation instructions.

---

## 5. Advanced Metadata Operations with ExifTool

> (for [exiftool](https://exiftool.org/) integration)

### Method 1.1: Windows (Quick)

1. Extract the following folder from `assets/exiftool-13.32_64.zip`:

   - `exiftool-13.32_64`

2. Add the `exiftool-13.32_64` folder path to your PATH.

### Method 1.2: Windows (Better)

1. Download ExifTool.exe:

   https://exiftool.org/

2. Download the Windows Executable (e.g., `exiftool-12.70.zip`).

3. Extract it and rename `exiftool(-k).exe` to `exiftool.exe` for command-line use.

4. Add `exiftool.exe` to a folder in your PATH, or add its folder to your PATH.

> **IMPORTANT:** Note that if you move the .exe to another folder, you must also move the "exiftool_files" folder to the same location.

### Method 2: Windows (Chocolatey)

1. Download ExifTool.exe:

   ```sh
   choco install exiftool -y
   ```

2. This will install `exiftool.exe` to:

   ```sh
   C:\ProgramData\chocolatey\lib\exiftool\tools\
   ```

3. Add `exiftool.exe` to a folder in your PATH, or add its folder to your PATH.

---

## 6. Metadata Strip + Lossless png compression with Oxipng

> (for [Oxipng](https://github.com/oxipng/oxipng) integration)
> essential for 'Sanitise Image Workflow'

### Method 1.1: Windows (Quick)

1. Extract the following folder from `assets/oxipng-9.1.5-x86_64-pc-windows-msvc.zip`:

   - `oxipng-9.1.5-x86_64-pc-windows-msvc`

2. Add the `oxipng-9.1.5-x86_64-pc-windows-msvc` folder path to your PATH.

### Method 1.2: Windows (Better)

1. Download oxipng.exe:

   https://github.com/oxipng/oxipng/releases

2. Download the appropriate archive (e.g., `oxipng-9.1.5-x86_64-pc-windows-msvc.zip`).

3. Extract the contents.

4. Add `oxipng.exe` to a folder in your PATH, or add its folder to your PATH.

---

## 7. Steganography Integration for zsteg and Steghide

> (for [zsteg](https://github.com/zed-0xff/zsteg) & [Steghide](https://steghide.sourceforge.net/) integration)
> optional for 'Sanitise Image Workflow'

### zsteg installation (Windows)

#### Method 1: Gem Installation (Recommended)

1. Install Ruby (via RubyInstaller for Windows)

- Go to: [https://rubyinstaller.org/](https://rubyinstaller.org/)
- Download the **latest Ruby+Devkit** version (e.g. `Ruby 3.3.0 with Devkit`).
- Run the installer.
- On the final screen, check **"Add Ruby executables to your PATH"**.
- Also allow it to **install MSYS2 and development tools** when prompted.

2. Restart PowerShell/Terminal/Console/CLI

3. Install `zsteg`
   ```sh
   gem install zsteg
   ```

#### Method 2.1: Standalone Executable (Quick)

For users who need a standalone `zsteg.exe` executable:

1. Extract the following files from `assets/zsteg_0.2.13_win.zip`:

   - `zsteg.exe`

   (This is a prebuilt Windows binary built using [Largo/ocran](https://github.com/Largo/ocran) that I compiled.)

2. Add `zsteg.exe` to a folder in your PATH, or add its folder to your PATH.

3. You can now use `zsteg.exe` as a CLI tool.

#### Method 2.2: Standalone Executable (Advanced)

For users who need a standalone `zsteg.exe` executable:

1. Install Ruby (via RubyInstaller for Windows)

- Go to: [https://rubyinstaller.org/](https://rubyinstaller.org/)
- Download the **latest Ruby+Devkit** version (e.g. `Ruby 3.3.0 with Devkit`).
- Run the installer.
- On the final screen, check **"Add Ruby executables to your PATH"**.
- Also allow it to **install MSYS2 and development tools** when prompted.

2. Restart PowerShell/Terminal/Console/CLI

3. Remove old OCRA and install OCRAN

-  Remove the old OCRA then install the newer OCRAN (maintained fork)

```bash
gem uninstall ocra
gem install ocran
```

4. Install `zsteg`

   ```sh
   gem install zsteg
   ```

5. **Create zsteg CLI wrapper**

   Extract the following files from `assets/zsteg_cli_build.zip`:

   - `zsteg_cli.rb`
   - `fiber.so`

6. **Build the executable using OCRAN**

   ```sh
   ocran zsteg_cli.rb --gem-all --add-all-core --output zsteg.exe --verbose
   ```

7. **Test the executable**
   ```sh
   ./zsteg.exe --help
   OR
   ./zsteg.exe --help > output.txt 2>&1
   ```

> **Note**: The OCRAN-built executable includes all necessary dependencies and runs without requiring Ruby to be installed on the target system. This method uses the [Largo/ocran](https://github.com/Largo/ocran) fork which provides better Windows compatibility and dependency handling compared to the original OCRA.

> **Technical Details**: OCRAN properly handles native dependencies like `zlib.so`, `zlib1.dll`, and assembly manifest files that cause side-by-side configuration failures with OCRA.

> **Troubleshooting**: If you encounter side-by-side configuration errors with the original OCRA, use the OCRAN method above which properly handles native dependencies like `zlib.so` and `zlib1.dll`.

### steghide installation

#### Method 1.1: Windows (Quick)

1. Extract the following folder from `assets/steghide-0.5.1-win32.zip`:

   - `steghide`

2. Add the `steghide` folder path to your PATH.

#### Method 1.2: Windows (Better)

1. Download Steghide

   [Steghide Windows package](http://prdownloads.sourceforge.net/steghide/steghide-0.5.1-win32.zip?download)

2. Extract the contents (`steghide` folder).

3. Add the `steghide` folder path to your PATH.

---

## 8. ffmpeg integration

> (for [ffmpeg](https://ffmpeg.org/) integration)

### Method 1.1: Windows (Quick)

1. Extract the following folder from `assets/ffmpeg-2025-07-31-git-119d127d05-full_build.zip`:

   - `ffmpeg-2025-07-31-git-119d127d05-full_build`

 - Note that this^ folder contains a `bin` folder which contains:

   - `ffmpeg.exe`
   - `ffplay.exe`
   - `ffprobe.exe`

2. Add the path to the `bin` folder to your PATH.

### Method 1.2: Windows (Better)

1. Download [`FFmpeg Builds`](https://www.gyan.dev/ffmpeg/builds/) (binaries for Windows):

   ```bash
   winget install ffmpeg
   OR
   choco install ffmpeg-full
   OR
   scoop install ffmpeg
   ```

### Method 1.3: Windows (`Method 1.1` but download first)

1. Download `ffmpeg-git-full.7z`:

   https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z

2. Extract the contents of the downloaded archive.

 - Note that this^ folder should contain a `bin` folder which contains:

   - `ffmpeg.exe`
   - `ffplay.exe`
   - `ffprobe.exe`

3. Add the path to the `bin` folder to your PATH.

---







## 9. Special mass implementation of above^^

> shortcut that implements multiple special installations from above

*might, might not work*

### Step 1: Windows binary dump

1. Extract the following folder from `assets/_win_binary_dump.zip`:

   - `_win_binary_dump`

2. Add the path to the `_win_binary_dump` folder path to your PATH.

**this includes**:
```txt
exiftool.exe
ffmpeg.exe
ffplay.exe
ffprobe.exe
getnative.exe
oxipng.exe
resdet.exe
steghide.exe
zsteg.exe
pyiqa.exe
imagededup.exe
```

### Step 2: Windows dll dump

1. Extract the following folder from `assets/_win_dll_dump.zip`:

   - `_win_dll_dump`

2. Add the path to the `_win_dll_dump` folder path to your PATH.

**this includes ddl's for**:
```txt
VapourSynth's plugins
python-magic's dll's & .mgc magicfile
```

### Step 3: Test the implementations

1. lorem ipsum

---

For more details, see the [main README Quick Start](../README.md#-quick-start) and [troubleshooting guide](troubleshooting.md).


