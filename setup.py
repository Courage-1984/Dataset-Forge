from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="dataset-forge",
    version="1.0.0",
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
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={"console_scripts": ["dataset-forge=main:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Creative Commons Attribution Share Alike 4.0 International License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://github.com/Courage-1984/Dataset-Forge/tree/main/docs",
        "Source": "https://github.com/Courage-1984/Dataset-Forge",
        "Tracker": "https://github.com/Courage-1984/Dataset-Forge/issues",
    },
)
