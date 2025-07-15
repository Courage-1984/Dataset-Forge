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
- See [requirements](advanced.md#requirements) and [PyTorch docs](https://pytorch.org/get-started/locally/).

---

## 2. VapourSynth & getnative (for getnative functionality)

**VapourSynth must be installed _before_ getnative.**

**Steps (Windows):**

1. Download and install [VapourSynth](http://www.vapoursynth.com/) (includes imwri plugin).
2. Open a terminal and run:

```bat
vsrepo.py install descale
vsrepo.py install ffms2
vsrepo.py install lsmas
```

3. Activate your virtual environment:

```bat
venv312\Scripts\activate
```

4. Install getnative:

```bat
pip install getnative
```

- See [Getnative Recommended Windows Installation](https://github.com/Infiziert90/getnative?tab=readme-ov-file#recommended-windows-installation) for more details.

**Troubleshooting:**

- If getnative fails to import, check that VapourSynth is installed and on your PATH.
- Install VapourSynth _before_ getnative or any requirements that depend on it.

---

## 3. python-magic (for directory utilities)

**Windows users:** You must install both the Python packages and the required DLLs.

**Steps:**

1. Install the packages:

```bat
pip install python-magic python-magic-bin libmagic
```

2. Copy the following files from `assets/libmagicwin64-master.zip` to `C:/Windows/System32/`:

   - `libgnurx-0.dll`
   - `magic.mgc`
   - `magic1.dll`

   (These are prebuilt for 64-bit Windows. See [libmagicwin64](https://github.com/pidydx/libmagicwin64) for details.)

3. When using python-magic, specify the magic file path if needed:

```python
import magic
file_magic = magic.Magic(magic_file="C:/Windows/System32/magic.mgc")
```

**Troubleshooting:**

- If you get import errors, ensure the DLLs are in `System32` and you are using the correct magic file path.
- See [python-magic docs](https://github.com/ahupp/python-magic) and [libmagicwin64](https://github.com/pidydx/libmagicwin64).

---

## Installing and Using resdet for Native Resolution Detection

### Windows (MSYS2 MINGW64 Shell)

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
   make clean
   ./configure --prefix=/mingw64
   make
   ```
6. Add `resdet.exe` to a folder in your PATH, or add its folder to your PATH.

### Windows (WSL - Recommended for CLI Integration)

1. Clone the repository:
   ```sh
   git clone https://github.com/0x09/resdet.git
   cd resdet
   ```
2. Build resdet:
   ```sh
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

### Linux

1. Clone the repository:
   ```sh
   git clone https://github.com/0x09/resdet.git
   cd resdet
   ```
2. Install dependencies (see resdet README for your distro).
3. Build and install:
   ```sh
   ./configure
   make
   sudo make install
   ```

### Usage in Dataset Forge

- The CLI will detect your platform and use the appropriate resdet binary.
- On Windows, if WSL is available and resdet is installed in WSL, it will be used automatically.
- If resdet is not found, you will receive a clear error message with installation instructions.

---

## Summary Table

| Dependency   | Install Order | Windows Notes                                     | Docs/Links                                            |
| ------------ | ------------- | ------------------------------------------------- | ----------------------------------------------------- |
| torch (CUDA) | 1             | Use correct CUDA version, install before all else | [PyTorch](https://pytorch.org/get-started/locally/)   |
| VapourSynth  | 2             | Install before getnative, add to PATH             | [VapourSynth](http://www.vapoursynth.com/)            |
| getnative    | 3             | Only after VapourSynth                            | [getnative](https://github.com/Infiziert90/getnative) |
| python-magic | 4             | Install DLLs to System32                          | [python-magic](https://github.com/ahupp/python-magic) |

---

For more details, see the [main README](../README.md) and [troubleshooting guide](troubleshooting.md).
