from setuptools import setup, find_packages, Command
from setuptools.command.install import install
import os
import subprocess
import sys

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    all_requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

# Filter out PyTorch packages from requirements for setup
# These will be installed separately with CUDA support
pytorch_packages = ["torch", "torchvision", "torchaudio"]
filtered_requirements = [
    req
    for req in all_requirements
    if not any(pytorch in req.lower() for pytorch in pytorch_packages)
]


class InstallPyTorchCommand(Command):
    """Custom command to install PyTorch with CUDA support first."""

    description = "Install PyTorch with CUDA support"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Install PyTorch with CUDA support."""
        print("Installing PyTorch with CUDA support...")
        try:
            # Install PyTorch with CUDA 12.1 support
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "torch",
                    "torchvision",
                    "torchaudio",
                    "--index-url",
                    "https://download.pytorch.org/whl/cu121",
                ]
            )
            print("✅ PyTorch with CUDA support installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install PyTorch with CUDA: {e}")
            print(
                "Please install manually: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
            )
            sys.exit(1)


class CustomInstallCommand(install):
    """Custom install command that installs PyTorch first."""

    description = "Install Dataset Forge with proper dependency order"

    def run(self):
        """Run the installation with proper dependency order."""
        # First, upgrade pip, setuptools, and wheel
        print("Upgrading pip, setuptools, and wheel...")
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "pip",
                    "setuptools",
                    "wheel",
                ]
            )
            print("✅ pip, setuptools, and wheel upgraded successfully!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to upgrade pip/setuptools/wheel: {e}")

        # Install PyTorch with CUDA support
        pytorch_cmd = InstallPyTorchCommand(self.distribution)
        pytorch_cmd.run()

        # Now run the normal install
        install.run(self)


setup(
    name="dataset-forge",
    version="1.0.0b1",
    description="Modular CLI utility for image dataset management, analysis, and transformation (HQ/LQ pairs, SISR, ML workflows)",
    long_description=(
        open("README.md", encoding="utf-8").read()
        if os.path.exists("README.md")
        else ""
    ),
    long_description_content_type="text/markdown",
    author="Courage-1984 and contributors",
    url="https://github.com/Courage-1984/Dataset-Forge",
    license="CC-BY-SA-4.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=filtered_requirements,  # Use filtered requirements (no PyTorch)
    python_requires=">=3.12",
    entry_points={"console_scripts": ["dataset-forge=main:main"]},
    cmdclass={
        "install": CustomInstallCommand,
        "install_pytorch": InstallPyTorchCommand,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: Creative Commons Attribution Share Alike 4.0 International License",  # Deprecated
        "Operating System :: Microsoft :: Windows",
        # "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Utilities",
        "Topic :: python",
        "Topic :: image-processing",
        "Topic :: video-processing",
        "Topic :: sisr",
        "Topic :: dataset-preparation",
        "Topic :: dataset-preprocessing",
    ],
    project_urls={
        "Documentation": "https://github.com/Courage-1984/Dataset-Forge/tree/main/docs",
        "Source": "https://github.com/Courage-1984/Dataset-Forge",
        "Tracker": "https://github.com/Courage-1984/Dataset-Forge/issues",
    },
)
