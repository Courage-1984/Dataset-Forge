#!/usr/bin/env python3
"""
Dataset-Forge Beta Release Script

This script automates the process of creating a beta release for Dataset-Forge.
It handles version updates, package building, testing, and release preparation.

Usage:
    python tools/create_beta_release.py [--version VERSION] [--dry-run] [--skip-tests]
"""

import os
import sys
import subprocess
import shutil
import argparse
import re
from pathlib import Path
from typing import Optional, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.color import Mocha


class BetaReleaseManager:
    """Manages the beta release process for Dataset-Forge."""

    def __init__(self, version: str, dry_run: bool = False, skip_tests: bool = False):
        self.version = version
        self.dry_run = dry_run
        self.skip_tests = skip_tests
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"

    def run_command(
        self, command: List[str], cwd: Optional[Path] = None
    ) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, and stderr."""
        if self.dry_run:
            print_info(f"DRY RUN: {' '.join(command)}")
            return 0, "", ""

        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def validate_version(self) -> bool:
        """Validate the version format."""
        # Check if version follows PEP 440 beta format
        beta_pattern = r"^\d+\.\d+\.\d+b\d+$"
        if not re.match(beta_pattern, self.version):
            print_error(f"Invalid beta version format: {self.version}")
            print_info("Expected format: X.Y.ZbN (e.g., 1.0.0b1)")
            return False
        return True

    def update_version_files(self) -> bool:
        """Update version in all relevant files."""
        print_info("📝 Updating version files...")

        # Update setup.py
        setup_py = self.project_root / "setup.py"
        if setup_py.exists():
            content = setup_py.read_text(encoding="utf-8")
            content = re.sub(r'version="[^"]*"', f'version="{self.version}"', content)
            if not self.dry_run:
                setup_py.write_text(content, encoding="utf-8")
            print_success(f"Updated setup.py version to {self.version}")

        # Update __init__.py
        init_py = self.project_root / "dataset_forge" / "__init__.py"
        if init_py.exists():
            content = init_py.read_text(encoding="utf-8")
            if "__version__" in content:
                content = re.sub(
                    r'__version__\s*=\s*"[^"]*"',
                    f'__version__ = "{self.version}"',
                    content,
                )
            else:
                content = f'"""Dataset Forge package root."""\n\n__version__ = "{self.version}"\n'

            if not self.dry_run:
                init_py.write_text(content, encoding="utf-8")
            print_success(f"Updated __init__.py version to {self.version}")

        return True

    def clean_build_directories(self) -> bool:
        """Clean previous build artifacts."""
        print_info("🧹 Cleaning build directories...")

        dirs_to_clean = [self.dist_dir, self.build_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                if not self.dry_run:
                    shutil.rmtree(dir_path)
                print_success(f"Cleaned {dir_path}")

        # Clean egg-info directories
        for egg_info in self.project_root.glob("*.egg-info"):
            if not self.dry_run:
                shutil.rmtree(egg_info)
            print_success(f"Cleaned {egg_info}")

        return True

    def run_tests(self) -> bool:
        """Run the test suite."""
        if self.skip_tests:
            print_warning("⏭️ Skipping tests as requested")
            return True

        print_info("🧪 Running tests...")

        # Run pytest
        exit_code, stdout, stderr = self.run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v"]
        )

        if exit_code != 0:
            print_error("Tests failed!")
            if stderr:
                print_error(f"Error output: {stderr}")
            return False

        print_success("All tests passed!")
        return True

    def build_package(self) -> bool:
        """Build the package distribution."""
        print_info("📦 Building package...")

        # Install build dependencies
        print_info("Installing build dependencies...")
        exit_code, stdout, stderr = self.run_command(
            [sys.executable, "-m", "pip", "install", "wheel", "build"]
        )

        if exit_code != 0:
            print_error("Failed to install build dependencies")
            return False

        # Build source distribution
        print_info("Building source distribution...")
        exit_code, stdout, stderr = self.run_command(
            [sys.executable, "setup.py", "sdist"]
        )

        if exit_code != 0:
            print_error("Failed to build source distribution")
            if stderr:
                print_error(f"Error: {stderr}")
            return False

        # Build wheel distribution
        print_info("Building wheel distribution...")
        exit_code, stdout, stderr = self.run_command(
            [sys.executable, "setup.py", "bdist_wheel"]
        )

        if exit_code != 0:
            print_error("Failed to build wheel distribution")
            if stderr:
                print_error(f"Error: {stderr}")
            return False

        print_success("Package built successfully!")
        return True

    def verify_package(self) -> bool:
        """Verify the built package."""
        print_info("🔍 Verifying package...")

        if not self.dist_dir.exists():
            print_error("Distribution directory not found")
            return False

        # List built packages
        packages = list(self.dist_dir.glob("*"))
        if not packages:
            print_error("No packages found in dist directory")
            return False

        print_success("Built packages:")
        for package in packages:
            print_info(f"  - {package.name}")

        # Test installation
        print_info("Testing package installation...")
        test_env = self.project_root / "test_beta_env"

        if test_env.exists():
            if not self.dry_run:
                shutil.rmtree(test_env)

        # Create test virtual environment
        exit_code, stdout, stderr = self.run_command(
            [sys.executable, "-m", "venv", str(test_env)]
        )

        if exit_code != 0:
            print_error("Failed to create test environment")
            return False

        # Install package in test environment
        if os.name == "nt":  # Windows
            pip_path = test_env / "Scripts" / "pip.exe"
        else:  # Unix/Linux
            pip_path = test_env / "bin" / "pip"

        # Find the source distribution
        sdist_files = list(self.dist_dir.glob("*.tar.gz"))
        if not sdist_files:
            print_error("No source distribution found")
            return False

        sdist_file = sdist_files[0]

        exit_code, stdout, stderr = self.run_command(
            [str(pip_path), "install", str(sdist_file)]
        )

        if exit_code != 0:
            print_error("Failed to install package in test environment")
            if stderr:
                print_error(f"Error: {stderr}")
            return False

        print_success("Package installation test passed!")

        # Clean up test environment
        if not self.dry_run and test_env.exists():
            shutil.rmtree(test_env)

        return True

    def create_git_tag(self) -> bool:
        """Create a git tag for the release."""
        print_info("🏷️ Creating git tag...")

        tag_name = f"v{self.version}"

        # Check if tag already exists
        exit_code, stdout, stderr = self.run_command(["git", "tag", "-l", tag_name])

        if stdout.strip():
            print_warning(f"Tag {tag_name} already exists")
            return True

        # Create tag
        exit_code, stdout, stderr = self.run_command(
            ["git", "tag", "-a", tag_name, "-m", f"Beta release {self.version}"]
        )

        if exit_code != 0:
            print_error("Failed to create git tag")
            if stderr:
                print_error(f"Error: {stderr}")
            return False

        print_success(f"Created git tag: {tag_name}")
        return True

    def generate_release_notes(self) -> bool:
        """Generate release notes template."""
        print_info("📝 Generating release notes template...")

        release_notes = f"""# Dataset-Forge Beta {self.version}

## 🎉 Beta Release Announcement

We're excited to announce the beta release of Dataset-Forge {self.version}! This release includes significant improvements and new features for image dataset management and processing.

## 🚀 What's New

### Major Features
- ✨ [Add major features here]
- 🔍 [Add major features here]
- 🎨 [Add major features here]
- 📊 [Add major features here]

### Improvements
- 🚀 [Add improvements here]
- 🛠️ [Add improvements here]
- 📚 [Add improvements here]
- 🎯 [Add improvements here]

### Bug Fixes
- [Add bug fixes here]
- [Add bug fixes here]
- [Add bug fixes here]

## 📦 Installation

### From Source
```bash
# Download and extract
wget https://github.com/Courage-1984/Dataset-Forge/releases/download/v{self.version}/dataset-forge-{self.version}.tar.gz
tar -xzf dataset-forge-{self.version}.tar.gz
cd dataset-forge-{self.version}

# Install
pip install -e .
```

### Windows Executable
Download `dataset-forge-beta.exe` and run directly.

### Via pip (if on PyPI)
```bash
pip install dataset-forge=={self.version}
```

## 🧪 Testing

Please test the following workflows:
- [ ] Dataset creation from various sources
- [ ] Visual deduplication with different thresholds
- [ ] Color adjustment tools
- [ ] Health scoring system
- [ ] Report generation
- [ ] Performance with large datasets (>1000 images)

## 🐛 Known Issues

- [Add known issues here]
- [Add known issues here]

## 📝 Feedback

Please report any issues or suggestions:
- [GitHub Issues](https://github.com/Courage-1984/Dataset-Forge/issues)
- [Discussion Forum](https://github.com/Courage-1984/Dataset-Forge/discussions)

## 🔄 Next Steps

- Final bug fixes based on beta feedback
- Performance optimizations
- Additional feature implementations
- Release candidate preparation

---

**Thank you for testing Dataset-Forge Beta!**
"""

        release_notes_file = self.project_root / f"RELEASE_NOTES_{self.version}.md"
        if not self.dry_run:
            release_notes_file.write_text(release_notes, encoding="utf-8")

        print_success(f"Release notes template created: {release_notes_file}")
        return True

    def print_next_steps(self):
        """Print next steps for the release process."""
        print_success("\n🎉 Beta release preparation completed!")
        print_info("\n📋 Next steps:")
        print_info("1. 📦 Review the generated files in the 'dist' directory:")
        print_info("   - Source distribution (.tar.gz)")
        print_info("   - Wheel distribution (.whl) - if created")
        print_info("   - Custom source code archives (.zip, .tar.gz)")
        print_info("   - Windows executable (.exe) - if created")
        print_info("")
        print_info("2. 🏷️  Push the git tag: git push origin v{self.version}")
        print_info("")
        print_info("3. 🚀 Create a GitHub release:")
        print_info("   - Go to GitHub repository")
        print_info("   - Click 'Releases' → 'Create a new release'")
        print_info(f"   - Tag: v{self.version}")
        print_info("   - Title: Dataset-Forge Beta {self.version}")
        print_info("   - Upload ALL assets from 'dist' directory:")
        print_info("     • Custom source code archives (recommended)")
        print_info("     • Distribution packages")
        print_info("     • Executables")
        print_info("")
        print_info("4. 📋 Note: GitHub will automatically create:")
        print_info("   - Source code (zip) - from repository")
        print_info("   - Source code (tar.gz) - from repository")
        print_info("   These contain the full repository at the tagged commit")
        print_info("")
        print_info("5. 📢 Announce the beta release")
        print_info("6. 🧪 Monitor feedback and issues")

        if self.dry_run:
            print_warning("\n⚠️ This was a dry run. No files were actually modified.")

    def run(self) -> bool:
        """Run the complete beta release process."""
        print_header(f"🚀 Dataset-Forge Beta Release: {self.version}")

        # Validate version
        if not self.validate_version():
            return False

        # Update version files
        if not self.update_version_files():
            return False

        # Clean build directories
        if not self.clean_build_directories():
            return False

        # Run tests
        if not self.run_tests():
            return False

        # Build package
        if not self.build_package():
            return False

        # Verify package
        if not self.verify_package():
            return False

        # Create source code archives
        if not self.create_source_archives():
            return False

        # Create git tag
        if not self.create_git_tag():
            return False

        # Generate release notes
        if not self.generate_release_notes():
            return False

        # Print next steps
        self.print_next_steps()

        return True

    def create_source_archives(self) -> bool:
        """Create custom source code archives for release assets."""
        print_info("📦 Creating source code archives...")
        
        # Define what to include/exclude
        include_patterns = [
            "dataset_forge/**/*",
            "docs/**/*", 
            "tests/**/*",
            "configs/**/*",
            "tools/**/*",
            "requirements.txt",
            "setup.py",
            "README.md",
            "LICENSE",
            "MANIFEST.in",
            "pytest.ini",
            "main.py",
            "run.bat"
        ]
        
        exclude_patterns = [
            "**/__pycache__/**",
            "**/*.pyc",
            "**/.git/**",
            "**/venv*/**",
            "**/logs/**",
            "**/dist/**",
            "**/build/**",
            "**/*.egg-info/**",
            "**/.pytest_cache/**",
            "**/.coverage",
            "**/htmlcov/**",
            "**/.tox/**",
            "**/.mypy_cache/**",
            "**/.vscode/**",
            "**/.idea/**",
            "**/node_modules/**",
            "**/test_datasets/**",
            "**/store/**",
            "**/reports/**"
        ]
        
        try:
            import zipfile
            import tarfile
            from pathlib import Path
            
            # Create temporary directory for clean source
            temp_dir = self.project_root / "temp_source"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()
            
            # Copy files based on patterns
            for pattern in include_patterns:
                pattern_path = self.project_root / pattern
                if pattern_path.exists():
                    if pattern_path.is_file():
                        # Copy single file
                        dest_path = temp_dir / pattern_path.name
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(pattern_path, dest_path)
                    else:
                        # Copy directory
                        dest_path = temp_dir / pattern_path.name
                        shutil.copytree(pattern_path, dest_path, dirs_exist_ok=True)
            
            # Remove excluded files/directories
            for pattern in exclude_patterns:
                for path in temp_dir.rglob(pattern.replace("**/*", "*")):
                    if path.exists():
                        if path.is_file():
                            path.unlink()
                        elif path.is_dir():
                            shutil.rmtree(path)
            
            # Create zip archive
            zip_path = self.dist_dir / f"Dataset-Forge-{self.version}-source.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
            
            # Create tar.gz archive
            tar_path = self.dist_dir / f"Dataset-Forge-{self.version}-source.tar.gz"
            with tarfile.open(tar_path, 'w:gz') as tarf:
                tarf.add(temp_dir, arcname=f"Dataset-Forge-{self.version}")
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            print_success(f"Created source archives:")
            print_info(f"  📦 {zip_path.name}")
            print_info(f"  📦 {tar_path.name}")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to create source archives: {e}")
            return False

    def create_release_assets(self) -> List[Path]:
        """Create all release assets including source code archives."""
        assets = []
        
        # Create source archives
        if self.create_source_archives():
            assets.extend([
                self.dist_dir / f"Dataset-Forge-{self.version}-source.zip",
                self.dist_dir / f"Dataset-Forge-{self.version}-source.tar.gz"
            ])
        
        # Add existing distribution files
        for pattern in ["*.tar.gz", "*.whl", "*.exe"]:
            assets.extend(self.dist_dir.glob(pattern))
        
        return assets


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Mocha.lavender}{'=' * 60}")
    print(f"{Mocha.lavender}{text:^60}")
    print(f"{Mocha.lavender}{'=' * 60}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a beta release for Dataset-Forge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/create_beta_release.py --version 1.0.0b1
  python tools/create_beta_release.py --version 1.0.0b1 --dry-run
  python tools/create_beta_release.py --version 1.0.0b1 --skip-tests
        """,
    )

    parser.add_argument("--version", required=True, help="Beta version (e.g., 1.0.0b1)")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making changes",
    )

    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")

    args = parser.parse_args()

    # Create release manager
    manager = BetaReleaseManager(
        version=args.version, dry_run=args.dry_run, skip_tests=args.skip_tests
    )

    # Run the release process
    success = manager.run()

    if success:
        print_success("\n✅ Beta release process completed successfully!")
        return 0
    else:
        print_error("\n❌ Beta release process failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
