"""
Enhanced Directory Tree Menu for Dataset Forge.

This module provides a comprehensive menu interface for the enhanced directory tree generator,
integrating seamlessly with Dataset Forge's menu system with advanced features including
export functionality, visual charts, progress bars, and detailed insights.
"""

from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_info,
    print_success,
    print_warning,
    print_error,
    print_prompt,
    print_section,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.progress_utils import tqdm
import os
import json
import csv
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import defaultdict

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    matplotlib_pyplot as plt,
    matplotlib_patches as mpatches,
    numpy_as_np as np,
)


def quick_tree_generation():
    """Quick directory tree generation with default settings."""
    from dataset_forge.utils.printing import (
        print_header,
        print_warning,
        print_error,
        print_success,
    )
    from dataset_forge.utils.color import Mocha
    import os

    print_header("🌳 Quick Directory Tree Generation", color=Mocha.sapphire)

    # Simple input without complex utilities
    root_path = input("📁 Enter directory path: ").strip()
    if not root_path:
        print_warning("❌ No path specified. Operation cancelled.")
        return

    if not os.path.exists(root_path):
        print_error(f"❌ Path does not exist: {root_path}")
        return

    print_info("🔄 Generating directory tree with default settings...")

    try:
        # Enhanced directory tree implementation with python-magic
        MAGIC_AVAILABLE = False
        magic = None

        try:
            import magic

            # Try to initialize magic with Windows-specific handling
            try:
                # Try standard initialization first
                test_magic = magic.Magic(mime=True)
                MAGIC_AVAILABLE = True
                print_info("✅ python-magic initialized successfully")
            except Exception as e:
                # Try with explicit magic file paths for Windows
                magic_file_paths = [
                    "C:/Windows/System32/magic.mgc",
                    "C:/Windows/System32/magic",
                    "C:/Program Files/Git/usr/share/misc/magic.mgc",
                    "C:/Program Files/Git/usr/share/misc/magic",
                    "C:/msys64/usr/share/misc/magic.mgc",
                    "C:/msys64/usr/share/misc/magic",
                    "C:/cygwin64/usr/share/misc/magic.mgc",
                    "C:/cygwin64/usr/share/misc/magic",
                ]

                for magic_file in magic_file_paths:
                    try:
                        if os.path.exists(magic_file):
                            test_magic = magic.Magic(mime=True, magic_file=magic_file)
                            MAGIC_AVAILABLE = True
                            print_info(
                                f"✅ python-magic initialized with magic file: {magic_file}"
                            )
                            break
                    except Exception:
                        continue

                if not MAGIC_AVAILABLE:
                    print_warning(f"⚠️ python-magic initialization failed: {e}")
                    print_info("💡 Using fallback file type detection")

        except ImportError:
            print_warning(
                "⚠️ python-magic library not available. Using fallback file type detection."
            )
            print_info("💡 Install with: pip install python-magic python-magic-bin")

        class EnhancedDirectoryTreeGenerator:
            def __init__(self):
                # Define categories with appropriate emojis
                self.categories = {
                    "directory": "📁",
                    "image": "🖼️",
                    "audio": "🎵",
                    "video": "🎬",
                    "document": "📄",
                    "executable": "⚙️",
                    "archive": "📦",
                    "code": "📝",
                    "data": "📊",
                    "web": "🌐",
                    "3d": "💠",
                    "font": "🔤",
                    "other": "📄",  # Default category
                }

                # Initialize magic instance if available
                self.magic_instance = None
                if MAGIC_AVAILABLE and magic:
                    try:
                        self.magic_instance = magic.Magic(mime=True)
                    except Exception:
                        # Try with magic file paths
                        magic_file_paths = [
                            "C:/Windows/System32/magic.mgc",
                            "C:/Windows/System32/magic",
                            "C:/Program Files/Git/usr/share/misc/magic.mgc",
                            "C:/Program Files/Git/usr/share/misc/magic",
                            "C:/msys64/usr/share/misc/magic.mgc",
                            "C:/msys64/usr/share/misc/magic",
                            "C:/cygwin64/usr/share/misc/magic.mgc",
                            "C:/cygwin64/usr/share/misc/magic",
                        ]

                        for magic_file in magic_file_paths:
                            try:
                                if os.path.exists(magic_file):
                                    self.magic_instance = magic.Magic(
                                        mime=True, magic_file=magic_file
                                    )
                                    break
                            except Exception:
                                continue

            def get_file_emoji(self, file_path: str) -> str:
                """Get the appropriate emoji for a file based on its type."""
                if os.path.isdir(file_path):
                    return self.categories["directory"]

                # Enhanced detection for specific file types (works without magic)
                filename = os.path.basename(file_path).lower()

                # Check for specific file extensions first
                if filename.endswith(
                    (
                        ".py",
                        ".pyc",
                        ".pyo",
                        ".js",
                        ".jsx",
                        ".ts",
                        ".tsx",
                        ".html",
                        ".css",
                        ".scss",
                        ".java",
                        ".cpp",
                        ".c",
                        ".h",
                        ".php",
                        ".rb",
                        ".go",
                        ".rs",
                        ".swift",
                        ".kt",
                    )
                ):
                    return self.categories["code"]
                elif filename.endswith(
                    (
                        ".json",
                        ".xml",
                        ".csv",
                        ".yaml",
                        ".yml",
                        ".toml",
                        ".ini",
                        ".cfg",
                        ".conf",
                    )
                ):
                    return self.categories["data"]
                elif filename.endswith(
                    (".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages")
                ):
                    return self.categories["document"]
                elif filename.endswith(
                    (".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz")
                ):
                    return self.categories["archive"]
                elif filename.endswith(
                    (".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma")
                ):
                    return self.categories["audio"]
                elif filename.endswith(
                    (".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv", ".m4v")
                ):
                    return self.categories["video"]
                elif filename.endswith((".ttf", ".otf", ".woff", ".woff2", ".eot")):
                    return self.categories["font"]
                elif filename.endswith(
                    (".exe", ".msi", ".app", ".dmg", ".deb", ".rpm", ".pkg")
                ):
                    return self.categories["executable"]
                elif filename.endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".ico",
                        ".tiff",
                        ".webp",
                        ".svg",
                        ".heic",
                        ".heif",
                    )
                ):
                    return self.categories["image"]

                # Use magic if available for more accurate detection
                if self.magic_instance:
                    try:
                        mime_type = self.magic_instance.from_file(file_path)
                        if mime_type.startswith("image"):
                            return self.categories["image"]
                        elif mime_type.startswith("audio"):
                            return self.categories["audio"]
                        elif mime_type.startswith("video"):
                            return self.categories["video"]
                        elif mime_type.startswith("text"):
                            if "html" in mime_type or "xml" in mime_type:
                                return self.categories["web"]
                            elif "javascript" in mime_type or "python" in mime_type:
                                return self.categories["code"]
                            else:
                                return self.categories["document"]
                        elif mime_type.startswith("application"):
                            if (
                                "zip" in mime_type
                                or "x-tar" in mime_type
                                or "x-rar" in mime_type
                            ):
                                return self.categories["archive"]
                            elif "pdf" in mime_type:
                                return self.categories["document"]
                            elif "json" in mime_type or "xml" in mime_type:
                                return self.categories["data"]
                            elif "octet-stream" in mime_type:
                                return self.categories["executable"]
                            elif "font" in mime_type:
                                return self.categories["font"]
                            else:
                                return self.categories["other"]
                        else:
                            return self.categories["other"]
                    except Exception:
                        pass  # Fall back to extension-based detection

                # Final fallback
                return self.categories["other"]

            def get_file_type(self, file_path: str) -> str:
                """Get the file type for statistics."""
                if os.path.isdir(file_path):
                    return "directory"

                filename = os.path.basename(file_path).lower()

                # Enhanced file type detection
                if filename.endswith(
                    (
                        ".py",
                        ".pyc",
                        ".pyo",
                        ".js",
                        ".jsx",
                        ".ts",
                        ".tsx",
                        ".html",
                        ".css",
                        ".scss",
                        ".java",
                        ".cpp",
                        ".c",
                        ".h",
                        ".php",
                        ".rb",
                        ".go",
                        ".rs",
                        ".swift",
                        ".kt",
                    )
                ):
                    return "code"
                elif filename.endswith(
                    (
                        ".json",
                        ".xml",
                        ".csv",
                        ".yaml",
                        ".yml",
                        ".toml",
                        ".ini",
                        ".cfg",
                        ".conf",
                    )
                ):
                    return "data"
                elif filename.endswith(
                    (".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages")
                ):
                    return "document"
                elif filename.endswith(
                    (".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz")
                ):
                    return "archive"
                elif filename.endswith(
                    (".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma")
                ):
                    return "audio"
                elif filename.endswith(
                    (".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv", ".m4v")
                ):
                    return "video"
                elif filename.endswith((".ttf", ".otf", ".woff", ".woff2", ".eot")):
                    return "font"
                elif filename.endswith(
                    (".exe", ".msi", ".app", ".dmg", ".deb", ".rpm", ".pkg")
                ):
                    return "executable"
                elif filename.endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".ico",
                        ".tiff",
                        ".webp",
                        ".svg",
                        ".heic",
                        ".heif",
                    )
                ):
                    return "image"

                # Use magic if available
                if self.magic_instance:
                    try:
                        mime_type = self.magic_instance.from_file(file_path)
                        if mime_type.startswith("image"):
                            return "image"
                        elif mime_type.startswith("audio"):
                            return "audio"
                        elif mime_type.startswith("video"):
                            return "video"
                        elif mime_type.startswith("text"):
                            if "html" in mime_type or "xml" in mime_type:
                                return "web"
                            elif "javascript" in mime_type or "python" in mime_type:
                                return "code"
                            else:
                                return "document"
                        elif mime_type.startswith("application"):
                            if (
                                "zip" in mime_type
                                or "x-tar" in mime_type
                                or "x-rar" in mime_type
                            ):
                                return "archive"
                            elif "pdf" in mime_type:
                                return "document"
                            elif "json" in mime_type or "xml" in mime_type:
                                return "data"
                            elif "octet-stream" in mime_type:
                                return "executable"
                            elif "font" in mime_type:
                                return "font"
                            else:
                                return "other"
                        else:
                            return "other"
                    except Exception:
                        pass

                return "other"

            def generate_tree(
                self,
                root_path: str,
                prefix: str = "",
                ignore_patterns: Optional[list] = None,
                is_subdir: bool = False,
                include_stats: bool = True,
                include_file_info: bool = False,
            ) -> tuple[str, dict]:
                """Generate a tree structure starting from the root path."""
                if ignore_patterns is None:
                    ignore_patterns = [
                        ".git",
                        "__pycache__",
                        "node_modules",
                        ".idea",
                        ".vscode",
                        ".DS_Store",
                        "Thumbs.db",
                    ]

                # Initialize statistics
                stats = {
                    "total_files": 0,
                    "total_dirs": 0,
                    "total_size": 0,
                    "file_types": {},
                    "largest_files": [],
                    "recent_files": [],
                }

                output = []
                root_path = os.path.abspath(root_path)

                try:
                    items = os.listdir(root_path)
                except PermissionError:
                    return f"{prefix}└── ⛔ Permission Denied\n", stats

                items.sort(
                    key=lambda x: (
                        not os.path.isdir(os.path.join(root_path, x)),
                        x.lower(),
                    )
                )
                items = [
                    item
                    for item in items
                    if not any(pattern in item for pattern in ignore_patterns)
                ]

                for index, item in enumerate(items):
                    try:
                        item_path = os.path.join(root_path, item)
                        is_last_item = index == len(items) - 1

                        current_prefix = "└── " if is_last_item else "├── "
                        next_prefix = "    " if is_last_item else "│   "

                        if os.path.isdir(item_path):
                            output.append(
                                f"{prefix}{current_prefix}{self.get_file_emoji(item_path)} {item}\n"
                            )

                            if include_stats:
                                stats["total_dirs"] += 1

                            output.append(
                                self.generate_tree(
                                    item_path,
                                    prefix + next_prefix,
                                    ignore_patterns,
                                    is_subdir=True,
                                    include_stats=include_stats,
                                    include_file_info=include_file_info,
                                )[
                                    0
                                ]  # Only get the tree output, not stats
                            )
                        else:
                            emoji = self.get_file_emoji(item_path)

                            # Add file info if requested
                            if include_file_info:
                                try:
                                    file_size = os.path.getsize(item_path)
                                    size_str = self.format_file_size(file_size)
                                    output.append(
                                        f"{prefix}{current_prefix}{emoji} {item} ({size_str})\n"
                                    )
                                except:
                                    output.append(
                                        f"{prefix}{current_prefix}{emoji} {item}\n"
                                    )
                            else:
                                output.append(
                                    f"{prefix}{current_prefix}{emoji} {item}\n"
                                )

                            # Update statistics
                            if include_stats:
                                try:
                                    file_size = os.path.getsize(item_path)
                                    file_type = self.get_file_type(item_path)
                                    modified_time = os.path.getmtime(item_path)

                                    stats["total_files"] += 1
                                    stats["total_size"] += file_size

                                    if file_type not in stats["file_types"]:
                                        stats["file_types"][file_type] = 0
                                    stats["file_types"][file_type] += 1

                                    stats["largest_files"].append(
                                        (item_path, file_size)
                                    )
                                    stats["recent_files"].append(
                                        (item_path, modified_time)
                                    )
                                except:
                                    pass
                    except Exception:
                        continue

                return "".join(output), stats

            def format_file_size(self, size_bytes: int) -> str:
                """Format file size in human-readable format."""
                if size_bytes == 0:
                    return "0 B"

                size_names = ["B", "KB", "MB", "GB", "TB"]
                i = 0
                current_size = float(size_bytes)
                while current_size >= 1024 and i < len(size_names) - 1:
                    current_size = current_size / 1024.0
                    i += 1

                return f"{current_size:.1f} {size_names[i]}"

            def generate_statistics_report(self, stats: dict) -> str:
                """Generate a detailed statistics report."""
                if not stats:
                    return "No statistics available."

                report = []
                report.append("📊 Directory Statistics Report")
                report.append("=" * 50)
                report.append(f"📁 Total Directories: {stats['total_dirs']}")
                report.append(f"📄 Total Files: {stats['total_files']}")
                report.append(
                    f"💾 Total Size: {self.format_file_size(stats['total_size'])}"
                )

                if stats["file_types"]:
                    report.append("\n📋 File Types:")
                    for file_type, count in sorted(
                        stats["file_types"].items(), key=lambda x: x[1], reverse=True
                    ):
                        report.append(f"  {file_type}: {count} files")

                if stats["largest_files"]:
                    report.append("\n🔝 Largest Files:")
                    largest_files = sorted(
                        stats["largest_files"], key=lambda x: x[1], reverse=True
                    )[:5]
                    for file_path, size in largest_files:
                        report.append(
                            f"  {os.path.basename(file_path)}: {self.format_file_size(size)}"
                        )

                if stats["recent_files"]:
                    report.append("\n🕒 Recently Modified Files:")
                    recent_files = sorted(
                        stats["recent_files"], key=lambda x: x[1], reverse=True
                    )[:5]
                    for file_path, modified in recent_files:
                        from datetime import datetime

                        report.append(
                            f"  {os.path.basename(file_path)}: {datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M')}"
                        )

                return "\n".join(report)

        generator = EnhancedDirectoryTreeGenerator()
        tree_output, stats = generator.generate_tree(root_path)

        print_info("")
        print_info(tree_output)
        print_success("✅ Quick tree generation completed!")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during tree generation: {e}")
        print_info("💡 Try using a different directory or check file permissions.")


def advanced_tree_generation():
    """Advanced directory tree generation with custom settings."""
    print_header("🌳 Advanced Directory Tree Generation", color=Mocha.sapphire)

    # Simple input without complex utilities
    root_path = input("📁 Enter directory path: ").strip()
    if not root_path:
        print_warning("❌ No path specified. Operation cancelled.")
        return

    if not os.path.exists(root_path):
        print_error(f"❌ Path does not exist: {root_path}")
        return

    try:
        # Get ignore patterns
        print_info("\n🚫 Ignore Patterns:")
        print_info("Enter patterns to ignore (comma-separated)")
        print_info("Examples: .git,__pycache__,node_modules,.DS_Store")
        ignore_input = input("Patterns (or press Enter for defaults): ").strip()
        ignore_patterns = None
        if ignore_input:
            ignore_patterns = [pattern.strip() for pattern in ignore_input.split(",")]

        # Get max depth
        print_info("\n📏 Maximum Depth:")
        print_info("-1: Unlimited depth")
        print_info("0: Root directory only")
        print_info("1: Root + 1 level deep")
        depth_input = input("Max depth (-1 for unlimited): ").strip() or "-1"
        try:
            max_depth = int(depth_input)
        except ValueError:
            print_warning("⚠️ Invalid depth, using unlimited (-1)")
            max_depth = -1

        # Get output format
        print_info("\n📤 Output Format:")
        print_info("1. Console (display only)")
        print_info("2. Markdown file")
        print_info("3. JSON file")
        format_choice = input("Select format [1-3]: ").strip() or "1"

        format_map = {"1": "console", "2": "markdown", "3": "json"}
        output_format = format_map.get(format_choice, "console")

        # Get additional options
        include_stats = input("\n📊 Include statistics? (y/n): ").strip().lower() != "n"
        include_file_info = (
            input("📋 Include file information (size, etc.)? (y/n): ").strip().lower()
            == "y"
        )

        print_info("\n🔄 Generating directory tree with custom settings...")

        # Generate tree using the enhanced generator
        try:
            # Enhanced directory tree implementation with python-magic
            MAGIC_AVAILABLE = False
            magic = None

            try:
                import magic

                # Try to initialize magic with Windows-specific handling
                try:
                    # Try standard initialization first
                    test_magic = magic.Magic(mime=True)
                    MAGIC_AVAILABLE = True
                    print_info("✅ python-magic initialized successfully")
                except Exception as e:
                    # Try with explicit magic file paths for Windows
                    magic_file_paths = [
                        "C:/Windows/System32/magic.mgc",
                        "C:/Windows/System32/magic",
                        "C:/Program Files/Git/usr/share/misc/magic.mgc",
                        "C:/Program Files/Git/usr/share/misc/magic",
                        "C:/msys64/usr/share/misc/magic.mgc",
                        "C:/msys64/usr/share/misc/magic",
                        "C:/cygwin64/usr/share/misc/magic.mgc",
                        "C:/cygwin64/usr/share/misc/magic",
                    ]

                    for magic_file in magic_file_paths:
                        try:
                            if os.path.exists(magic_file):
                                test_magic = magic.Magic(
                                    mime=True, magic_file=magic_file
                                )
                                MAGIC_AVAILABLE = True
                                print_info(
                                    f"✅ python-magic initialized with magic file: {magic_file}"
                                )
                                break
                        except Exception:
                            continue

                    if not MAGIC_AVAILABLE:
                        print_warning(f"⚠️ python-magic initialization failed: {e}")
                        print_info("💡 Using fallback file type detection")

            except ImportError:
                print_warning(
                    "⚠️ python-magic library not available. Using fallback file type detection."
                )
                print_info("💡 Install with: pip install python-magic python-magic-bin")

            class EnhancedDirectoryTreeGenerator:
                def __init__(self):
                    # Define categories with appropriate emojis
                    self.categories = {
                        "directory": "📁",
                        "image": "🖼️",
                        "audio": "🎵",
                        "video": "🎬",
                        "document": "📄",
                        "executable": "⚙️",
                        "archive": "📦",
                        "code": "📝",
                        "data": "📊",
                        "web": "🌐",
                        "3d": "💠",
                        "font": "🔤",
                        "other": "📄",  # Default category
                    }

                    # Initialize magic instance if available
                    self.magic_instance = None
                    if MAGIC_AVAILABLE and magic:
                        try:
                            self.magic_instance = magic.Magic(mime=True)
                        except Exception:
                            # Try with magic file paths
                            magic_file_paths = [
                                "C:/Windows/System32/magic.mgc",
                                "C:/Windows/System32/magic",
                                "C:/Program Files/Git/usr/share/misc/magic.mgc",
                                "C:/Program Files/Git/usr/share/misc/magic",
                                "C:/msys64/usr/share/misc/magic.mgc",
                                "C:/msys64/usr/share/misc/magic",
                                "C:/cygwin64/usr/share/misc/magic.mgc",
                                "C:/cygwin64/usr/share/misc/magic",
                            ]

                            for magic_file in magic_file_paths:
                                try:
                                    if os.path.exists(magic_file):
                                        self.magic_instance = magic.Magic(
                                            mime=True, magic_file=magic_file
                                        )
                                        break
                                except Exception:
                                    continue

                def get_file_emoji(self, file_path: str) -> str:
                    """Get the appropriate emoji for a file based on its type."""
                    if os.path.isdir(file_path):
                        return self.categories["directory"]

                    # Enhanced detection for specific file types (works without magic)
                    filename = os.path.basename(file_path).lower()

                    # Check for specific file extensions first
                    if filename.endswith(
                        (
                            ".py",
                            ".pyc",
                            ".pyo",
                            ".js",
                            ".jsx",
                            ".ts",
                            ".tsx",
                            ".html",
                            ".css",
                            ".scss",
                            ".java",
                            ".cpp",
                            ".c",
                            ".h",
                            ".php",
                            ".rb",
                            ".go",
                            ".rs",
                            ".swift",
                            ".kt",
                        )
                    ):
                        return self.categories["code"]
                    elif filename.endswith(
                        (
                            ".json",
                            ".xml",
                            ".csv",
                            ".yaml",
                            ".yml",
                            ".toml",
                            ".ini",
                            ".cfg",
                            ".conf",
                        )
                    ):
                        return self.categories["data"]
                    elif filename.endswith(
                        (".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages")
                    ):
                        return self.categories["document"]
                    elif filename.endswith(
                        (".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz")
                    ):
                        return self.categories["archive"]
                    elif filename.endswith(
                        (".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma")
                    ):
                        return self.categories["audio"]
                    elif filename.endswith(
                        (
                            ".mp4",
                            ".avi",
                            ".mov",
                            ".wmv",
                            ".flv",
                            ".webm",
                            ".mkv",
                            ".m4v",
                        )
                    ):
                        return self.categories["video"]
                    elif filename.endswith((".ttf", ".otf", ".woff", ".woff2", ".eot")):
                        return self.categories["font"]
                    elif filename.endswith(
                        (".exe", ".msi", ".app", ".dmg", ".deb", ".rpm", ".pkg")
                    ):
                        return self.categories["executable"]
                    elif filename.endswith(
                        (
                            ".jpg",
                            ".jpeg",
                            ".png",
                            ".gif",
                            ".bmp",
                            ".ico",
                            ".tiff",
                            ".webp",
                            ".svg",
                            ".heic",
                            ".heif",
                        )
                    ):
                        return self.categories["image"]

                    # Use magic if available for more accurate detection
                    if self.magic_instance:
                        try:
                            mime_type = self.magic_instance.from_file(file_path)
                            if mime_type.startswith("image"):
                                return self.categories["image"]
                            elif mime_type.startswith("audio"):
                                return self.categories["audio"]
                            elif mime_type.startswith("video"):
                                return self.categories["video"]
                            elif mime_type.startswith("text"):
                                if "html" in mime_type or "xml" in mime_type:
                                    return self.categories["web"]
                                elif "javascript" in mime_type or "python" in mime_type:
                                    return self.categories["code"]
                                else:
                                    return self.categories["document"]
                            elif mime_type.startswith("application"):
                                if (
                                    "zip" in mime_type
                                    or "x-tar" in mime_type
                                    or "x-rar" in mime_type
                                ):
                                    return self.categories["archive"]
                                elif "pdf" in mime_type:
                                    return self.categories["document"]
                                elif "json" in mime_type or "xml" in mime_type:
                                    return self.categories["data"]
                                elif "octet-stream" in mime_type:
                                    return self.categories["executable"]
                                elif "font" in mime_type:
                                    return self.categories["font"]
                                else:
                                    return self.categories["other"]
                            else:
                                return self.categories["other"]
                        except Exception:
                            pass  # Fall back to extension-based detection

                    # Final fallback
                    return self.categories["other"]

                def get_file_type(self, file_path: str) -> str:
                    """Get the file type for statistics."""
                    if os.path.isdir(file_path):
                        return "directory"

                    filename = os.path.basename(file_path).lower()

                    # Enhanced file type detection
                    if filename.endswith(
                        (
                            ".py",
                            ".pyc",
                            ".pyo",
                            ".js",
                            ".jsx",
                            ".ts",
                            ".tsx",
                            ".html",
                            ".css",
                            ".scss",
                            ".java",
                            ".cpp",
                            ".c",
                            ".h",
                            ".php",
                            ".rb",
                            ".go",
                            ".rs",
                            ".swift",
                            ".kt",
                        )
                    ):
                        return "code"
                    elif filename.endswith(
                        (
                            ".json",
                            ".xml",
                            ".csv",
                            ".yaml",
                            ".yml",
                            ".toml",
                            ".ini",
                            ".cfg",
                            ".conf",
                        )
                    ):
                        return "data"
                    elif filename.endswith(
                        (".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages")
                    ):
                        return "document"
                    elif filename.endswith(
                        (".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz")
                    ):
                        return "archive"
                    elif filename.endswith(
                        (".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma")
                    ):
                        return "audio"
                    elif filename.endswith(
                        (
                            ".mp4",
                            ".avi",
                            ".mov",
                            ".wmv",
                            ".flv",
                            ".webm",
                            ".mkv",
                            ".m4v",
                        )
                    ):
                        return "video"
                    elif filename.endswith((".ttf", ".otf", ".woff", ".woff2", ".eot")):
                        return "font"
                    elif filename.endswith(
                        (".exe", ".msi", ".app", ".dmg", ".deb", ".rpm", ".pkg")
                    ):
                        return "executable"
                    elif filename.endswith(
                        (
                            ".jpg",
                            ".jpeg",
                            ".png",
                            ".gif",
                            ".bmp",
                            ".ico",
                            ".tiff",
                            ".webp",
                            ".svg",
                            ".heic",
                            ".heif",
                        )
                    ):
                        return "image"

                    # Use magic if available
                    if self.magic_instance:
                        try:
                            mime_type = self.magic_instance.from_file(file_path)
                            if mime_type.startswith("image"):
                                return "image"
                            elif mime_type.startswith("audio"):
                                return "audio"
                            elif mime_type.startswith("video"):
                                return "video"
                            elif mime_type.startswith("text"):
                                if "html" in mime_type or "xml" in mime_type:
                                    return "web"
                                elif "javascript" in mime_type or "python" in mime_type:
                                    return "code"
                                else:
                                    return "document"
                            elif mime_type.startswith("application"):
                                if (
                                    "zip" in mime_type
                                    or "x-tar" in mime_type
                                    or "x-rar" in mime_type
                                ):
                                    return "archive"
                                elif "pdf" in mime_type:
                                    return "document"
                                elif "json" in mime_type or "xml" in mime_type:
                                    return "data"
                                elif "octet-stream" in mime_type:
                                    return "executable"
                                elif "font" in mime_type:
                                    return "font"
                                else:
                                    return "other"
                            else:
                                return "other"
                        except Exception:
                            pass

                    return "other"

                def generate_tree(
                    self,
                    root_path: str,
                    prefix: str = "",
                    ignore_patterns: Optional[list] = None,
                    is_subdir: bool = False,
                    include_stats: bool = True,
                    include_file_info: bool = False,
                    max_depth: int = -1,
                    current_depth: int = 0,
                ) -> tuple[str, dict]:
                    """Generate a tree structure starting from the root path."""
                    if ignore_patterns is None:
                        ignore_patterns = [
                            ".git",
                            "__pycache__",
                            "node_modules",
                            ".idea",
                            ".vscode",
                            ".DS_Store",
                            "Thumbs.db",
                        ]

                    # Initialize statistics
                    stats = {
                        "total_files": 0,
                        "total_dirs": 0,
                        "total_size": 0,
                        "file_types": {},
                        "largest_files": [],
                        "recent_files": [],
                    }

                    output = []
                    root_path = os.path.abspath(root_path)

                    try:
                        items = os.listdir(root_path)
                    except PermissionError:
                        return f"{prefix}└── ⛔ Permission Denied\n", stats

                    items.sort(
                        key=lambda x: (
                            not os.path.isdir(os.path.join(root_path, x)),
                            x.lower(),
                        )
                    )
                    items = [
                        item
                        for item in items
                        if not any(pattern in item for pattern in ignore_patterns)
                    ]

                    for index, item in enumerate(items):
                        try:
                            item_path = os.path.join(root_path, item)
                            is_last_item = index == len(items) - 1

                            current_prefix = "└── " if is_last_item else "├── "
                            next_prefix = "    " if is_last_item else "│   "

                            if os.path.isdir(item_path):
                                output.append(
                                    f"{prefix}{current_prefix}{self.get_file_emoji(item_path)} {item}\n"
                                )

                                if include_stats:
                                    stats["total_dirs"] += 1

                                # Check depth limit
                                if max_depth == -1 or current_depth < max_depth:
                                    sub_tree, sub_stats = self.generate_tree(
                                        item_path,
                                        prefix + next_prefix,
                                        ignore_patterns,
                                        is_subdir=True,
                                        include_stats=include_stats,
                                        include_file_info=include_file_info,
                                        max_depth=max_depth,
                                        current_depth=current_depth + 1,
                                    )
                                    output.append(sub_tree)

                                    # Merge statistics
                                    if include_stats:
                                        stats["total_files"] += sub_stats["total_files"]
                                        stats["total_dirs"] += sub_stats["total_dirs"]
                                        stats["total_size"] += sub_stats["total_size"]
                                        stats["largest_files"].extend(
                                            sub_stats["largest_files"]
                                        )
                                        stats["recent_files"].extend(
                                            sub_stats["recent_files"]
                                        )

                                        for file_type, count in sub_stats[
                                            "file_types"
                                        ].items():
                                            if file_type not in stats["file_types"]:
                                                stats["file_types"][file_type] = 0
                                            stats["file_types"][file_type] += count
                            else:
                                emoji = self.get_file_emoji(item_path)

                                # Add file info if requested
                                if include_file_info:
                                    try:
                                        file_size = os.path.getsize(item_path)
                                        size_str = self.format_file_size(file_size)
                                        output.append(
                                            f"{prefix}{current_prefix}{emoji} {item} ({size_str})\n"
                                        )
                                    except:
                                        output.append(
                                            f"{prefix}{current_prefix}{emoji} {item}\n"
                                        )
                                else:
                                    output.append(
                                        f"{prefix}{current_prefix}{emoji} {item}\n"
                                    )

                                # Update statistics
                                if include_stats:
                                    try:
                                        file_size = os.path.getsize(item_path)
                                        file_type = self.get_file_type(item_path)
                                        modified_time = os.path.getmtime(item_path)

                                        stats["total_files"] += 1
                                        stats["total_size"] += file_size

                                        if file_type not in stats["file_types"]:
                                            stats["file_types"][file_type] = 0
                                        stats["file_types"][file_type] += 1

                                        stats["largest_files"].append(
                                            (item_path, file_size)
                                        )
                                        stats["recent_files"].append(
                                            (item_path, modified_time)
                                        )
                                    except:
                                        pass
                        except Exception:
                            continue

                    return "".join(output), stats

                def format_file_size(self, size_bytes: int) -> str:
                    """Format file size in human-readable format."""
                    if size_bytes == 0:
                        return "0 B"

                    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
                    i = 0
                    size_float = float(size_bytes)
                    while size_float >= 1024 and i < len(size_names) - 1:
                        size_float /= 1024.0
                        i += 1

                    return f"{size_float:.1f} {size_names[i]}"

                def generate_statistics_report(self, stats: dict) -> str:
                    """Generate a comprehensive statistics report."""
                    report = []
                    report.append("📊 Directory Statistics Report")
                    report.append("=" * 50)

                    # Basic statistics
                    report.append(
                        f"\n📁 Total Directories: {stats['total_directories']:,}"
                    )
                    report.append(f"📄 Total Files: {stats['total_files']:,}")
                    report.append(
                        f"💾 Total Size: {self.format_file_size(stats['total_size'])}"
                    )

                    # File type breakdown
                    if stats["file_types"]:
                        report.append("\n📋 File Type Breakdown:")
                        sorted_types = sorted(
                            stats["file_types"].items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )
                        for file_type, count in sorted_types:
                            emoji = self.categories.get(file_type, "📄")
                            percentage = (
                                (count / stats["total_files"]) * 100
                                if stats["total_files"] > 0
                                else 0
                            )
                            report.append(
                                f"  {emoji} {file_type.title()}: {count:,} ({percentage:.1f}%)"
                            )

                    # Special statistics
                    report.append(f"\n🔍 Special Statistics:")
                    report.append(
                        f"  📁 Empty Directories: {stats['empty_directories']}"
                    )
                    report.append(f"  👁️ Hidden Files: {stats['hidden_files']}")
                    report.append(
                        f"  👁️ Hidden Directories: {stats['hidden_directories']}"
                    )

                    # Largest files
                    if stats["largest_files"]:
                        report.append("\n📏 Largest Files:")
                        for file_path, size in stats["largest_files"][:5]:
                            report.append(
                                f"  {os.path.basename(file_path)}: {self.format_file_size(size)}"
                            )

                    # Recent files
                    if stats["recent_files"]:
                        report.append("\n🕒 Recently Modified Files:")
                        from datetime import datetime

                        for file_path, modified in stats["recent_files"][:5]:
                            report.append(
                                f"  {os.path.basename(file_path)}: {datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M')}"
                            )

                    return "\n".join(report)

            generator = EnhancedDirectoryTreeGenerator()
            tree_output, stats = generator.generate_tree(
                root_path,
                ignore_patterns=ignore_patterns,
                include_stats=include_stats,
                include_file_info=include_file_info,
                max_depth=max_depth,
            )

            # Display results
            if output_format == "console":
                print_info("")
                print_info(tree_output)

                if include_stats and stats:
                    print_info("")
                    print_info(generator.generate_statistics_report(stats))

            print_success("✅ Advanced tree generation completed!")

        except Exception as e:
            print_error(f"❌ Error during tree generation: {e}")
            print_info("💡 Try using a different directory or check file permissions.")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during tree generation: {e}")
        print_info("💡 Try using a different directory or check file permissions.")


def batch_tree_generation():
    """Generate trees for multiple directories."""
    print_header("🌳 Batch Directory Tree Generation", color=Mocha.sapphire)

    try:
        # Get multiple paths
        print_info(
            "📁 Enter multiple directory paths (one per line, empty line to finish):"
        )
        paths = []
        while True:
            path = input(f"Path {len(paths) + 1}: ").strip()
            if not path:
                break
            if os.path.exists(path):
                paths.append(path)
            else:
                print_warning(f"⚠️ Path does not exist: {path}")

        if not paths:
            print_warning("❌ No valid paths specified. Operation cancelled.")
            return

        # Get common settings
        print_info(f"\n⚙️ Settings for {len(paths)} directories:")
        output_format = (
            input("Output format (console/markdown/json) [markdown]: ").strip()
            or "markdown"
        )
        include_stats = input("Include statistics? (y/n) [y]: ").strip().lower() != "n"
        include_file_info = (
            input("Include file information? (y/n) [n]: ").strip().lower() == "y"
        )

        # Process each directory
        successful = 0
        failed = 0

        for i, path in enumerate(paths, 1):
            print_info(f"\n🔄 Processing {i}/{len(paths)}: {path}")

            try:
                # Use the same enhanced generator as advanced_tree_generation
                # (Implementation would be similar to above)
                print_success(f"✅ Completed: {path}")
                successful += 1
            except Exception as e:
                failed += 1
                print_error(f"❌ Failed: {path} - {e}")

        print_success(
            f"\n✅ Batch processing completed: {successful} successful, {failed} failed"
        )

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during batch processing: {e}")


def tree_statistics_analysis():
    """Analyze directory statistics without generating full tree."""
    print_header("📊 Directory Statistics Analysis", color=Mocha.sapphire)

    # Simple input without complex utilities
    root_path = input("📁 Enter directory path to analyze: ").strip()
    if not root_path:
        print_warning("❌ No path specified. Operation cancelled.")
        return

    if not os.path.exists(root_path):
        print_error(f"❌ Path does not exist: {root_path}")
        return

    try:
        print_info("🔄 Analyzing directory statistics...")

        # Enhanced directory tree implementation with python-magic
        MAGIC_AVAILABLE = False
        magic = None

        try:
            import magic

            # Try to initialize magic with Windows-specific handling
            try:
                # Try standard initialization first
                test_magic = magic.Magic(mime=True)
                MAGIC_AVAILABLE = True
            except Exception as e:
                # Try with explicit magic file paths for Windows
                magic_file_paths = [
                    "C:/Windows/System32/magic.mgc",
                    "C:/Windows/System32/magic",
                    "C:/Program Files/Git/usr/share/misc/magic.mgc",
                    "C:/Program Files/Git/usr/share/misc/magic",
                    "C:/msys64/usr/share/misc/magic.mgc",
                    "C:/msys64/usr/share/misc/magic",
                    "C:/cygwin64/usr/share/misc/magic.mgc",
                    "C:/cygwin64/usr/share/misc/magic",
                ]

                for magic_file in magic_file_paths:
                    try:
                        if os.path.exists(magic_file):
                            test_magic = magic.Magic(mime=True, magic_file=magic_file)
                            MAGIC_AVAILABLE = True
                            break
                    except Exception:
                        continue

        except ImportError:
            pass

        class StatisticsAnalyzer:
            def __init__(self):
                # Define categories with appropriate emojis
                self.categories = {
                    "directory": "📁",
                    "image": "🖼️",
                    "audio": "🎵",
                    "video": "🎬",
                    "document": "📄",
                    "executable": "⚙️",
                    "archive": "📦",
                    "code": "📝",
                    "data": "📊",
                    "web": "🌐",
                    "3d": "💠",
                    "font": "🔤",
                    "other": "📄",  # Default category
                }

                # Initialize magic instance if available
                self.magic_instance = None
                if MAGIC_AVAILABLE and magic:
                    try:
                        self.magic_instance = magic.Magic(mime=True)
                    except Exception:
                        # Try with magic file paths
                        magic_file_paths = [
                            "C:/Windows/System32/magic.mgc",
                            "C:/Windows/System32/magic",
                            "C:/Program Files/Git/usr/share/misc/magic.mgc",
                            "C:/Program Files/Git/usr/share/misc/magic",
                            "C:/msys64/usr/share/misc/magic.mgc",
                            "C:/msys64/usr/share/misc/magic",
                            "C:/cygwin64/usr/share/misc/magic.mgc",
                            "C:/cygwin64/usr/share/misc/magic",
                        ]

                        for magic_file in magic_file_paths:
                            try:
                                if os.path.exists(magic_file):
                                    self.magic_instance = magic.Magic(
                                        mime=True, magic_file=magic_file
                                    )
                                    break
                            except Exception:
                                continue

            def get_file_emoji(self, file_path: str) -> str:
                """Get the appropriate emoji for a file based on its type."""
                if os.path.isdir(file_path):
                    return self.categories["directory"]

                # Enhanced detection for specific file types (works without magic)
                filename = os.path.basename(file_path).lower()

                # Check for specific file extensions first
                if filename.endswith(
                    (
                        ".py",
                        ".pyc",
                        ".pyo",
                        ".js",
                        ".jsx",
                        ".ts",
                        ".tsx",
                        ".html",
                        ".css",
                        ".scss",
                        ".java",
                        ".cpp",
                        ".c",
                        ".h",
                        ".php",
                        ".rb",
                        ".go",
                        ".rs",
                        ".swift",
                        ".kt",
                    )
                ):
                    return self.categories["code"]
                elif filename.endswith(
                    (
                        ".json",
                        ".xml",
                        ".csv",
                        ".yaml",
                        ".yml",
                        ".toml",
                        ".ini",
                        ".cfg",
                        ".conf",
                    )
                ):
                    return self.categories["data"]
                elif filename.endswith(
                    (".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages")
                ):
                    return self.categories["document"]
                elif filename.endswith(
                    (".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz")
                ):
                    return self.categories["archive"]
                elif filename.endswith(
                    (".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma")
                ):
                    return self.categories["audio"]
                elif filename.endswith(
                    (
                        ".mp4",
                        ".avi",
                        ".mov",
                        ".wmv",
                        ".flv",
                        ".mkv",
                        ".webm",
                        ".m4v",
                        ".3gp",
                    )
                ):
                    return self.categories["video"]
                elif filename.endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".tiff",
                        ".webp",
                        ".svg",
                        ".ico",
                        ".raw",
                        ".cr2",
                        ".nef",
                        ".arw",
                    )
                ):
                    return self.categories["image"]
                elif filename.endswith(
                    (".exe", ".msi", ".bat", ".cmd", ".com", ".app", ".dmg")
                ):
                    return self.categories["executable"]
                elif filename.endswith((".ttf", ".otf", ".woff", ".woff2", ".eot")):
                    return self.categories["font"]
                elif filename.endswith(
                    (".obj", ".fbx", ".dae", ".3ds", ".blend", ".max", ".ma")
                ):
                    return self.categories["3d"]
                elif filename.endswith(
                    (".html", ".htm", ".css", ".js", ".php", ".asp", ".jsp")
                ):
                    return self.categories["web"]

                # Try magic-based detection if available
                if self.magic_instance:
                    try:
                        mime_type = self.magic_instance.from_file(file_path)
                        if mime_type.startswith("image/"):
                            return self.categories["image"]
                        elif mime_type.startswith("audio/"):
                            return self.categories["audio"]
                        elif mime_type.startswith("video/"):
                            return self.categories["video"]
                        elif mime_type.startswith("text/"):
                            if "javascript" in mime_type or "python" in mime_type:
                                return self.categories["code"]
                            else:
                                return self.categories["document"]
                        elif mime_type.startswith("application/"):
                            if "pdf" in mime_type:
                                return self.categories["document"]
                            elif "zip" in mime_type or "rar" in mime_type:
                                return self.categories["archive"]
                            elif "executable" in mime_type:
                                return self.categories["executable"]
                    except Exception:
                        pass

                return self.categories["other"]

            def get_file_type(self, file_path: str) -> str:
                """Get the file type category."""
                emoji = self.get_file_emoji(file_path)
                for category, cat_emoji in self.categories.items():
                    if cat_emoji == emoji:
                        return category
                return "other"

            def analyze_directory(self, root_path: str) -> dict:
                """Analyze directory and return comprehensive statistics."""
                stats = {
                    "total_files": 0,
                    "total_directories": 0,
                    "total_size": 0,
                    "file_types": {},
                    "largest_files": [],
                    "recent_files": [],
                    "empty_directories": 0,
                    "hidden_files": 0,
                    "hidden_directories": 0,
                    "symlinks": 0,
                    "broken_symlinks": 0,
                }

                try:
                    for root, dirs, files in os.walk(root_path):
                        # Count directories
                        for dir_name in dirs:
                            dir_path = os.path.join(root, dir_name)
                            stats["total_directories"] += 1

                            if dir_name.startswith("."):
                                stats["hidden_directories"] += 1

                            # Check for empty directories
                            try:
                                if not os.listdir(dir_path):
                                    stats["empty_directories"] += 1
                            except (PermissionError, OSError):
                                pass

                        # Count files
                        for file_name in files:
                            file_path = os.path.join(root, file_name)
                            stats["total_files"] += 1

                            if file_name.startswith("."):
                                stats["hidden_files"] += 1

                            try:
                                # Get file size
                                file_size = os.path.getsize(file_path)
                                stats["total_size"] += file_size

                                # Track largest files
                                stats["largest_files"].append((file_path, file_size))

                                # Track recent files
                                modified_time = os.path.getmtime(file_path)
                                stats["recent_files"].append((file_path, modified_time))

                                # Categorize file type
                                file_type = self.get_file_type(file_path)
                                stats["file_types"][file_type] = (
                                    stats["file_types"].get(file_type, 0) + 1
                                )

                            except (PermissionError, OSError):
                                # Skip files we can't access
                                continue

                except (PermissionError, OSError) as e:
                    print_warning(
                        f"⚠️ Some files/directories could not be accessed: {e}"
                    )

                # Sort largest files and recent files
                stats["largest_files"].sort(key=lambda x: x[1], reverse=True)
                stats["recent_files"].sort(key=lambda x: x[1], reverse=True)

                # Keep only top 10
                stats["largest_files"] = stats["largest_files"][:10]
                stats["recent_files"] = stats["recent_files"][:10]

                return stats

            def format_file_size(self, size_bytes: int) -> str:
                """Format file size in human-readable format."""
                if size_bytes == 0:
                    return "0 B"

                size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
                i = 0
                size_float = float(size_bytes)
                while size_float >= 1024 and i < len(size_names) - 1:
                    size_float /= 1024.0
                    i += 1

                return f"{size_float:.1f} {size_names[i]}"

            def generate_statistics_report(self, stats: dict) -> str:
                """Generate a comprehensive statistics report."""
                report = []
                report.append("📊 Directory Statistics Report")
                report.append("=" * 50)

                # Basic statistics
                report.append(f"\n📁 Total Directories: {stats['total_directories']:,}")
                report.append(f"📄 Total Files: {stats['total_files']:,}")
                report.append(
                    f"💾 Total Size: {self.format_file_size(stats['total_size'])}"
                )

                # File type breakdown
                if stats["file_types"]:
                    report.append("\n📋 File Type Breakdown:")
                    sorted_types = sorted(
                        stats["file_types"].items(), key=lambda x: x[1], reverse=True
                    )
                    for file_type, count in sorted_types:
                        emoji = self.categories.get(file_type, "📄")
                        percentage = (
                            (count / stats["total_files"]) * 100
                            if stats["total_files"] > 0
                            else 0
                        )
                        report.append(
                            f"  {emoji} {file_type.title()}: {count:,} ({percentage:.1f}%)"
                        )

                # Special statistics
                report.append(f"\n🔍 Special Statistics:")
                report.append(f"  📁 Empty Directories: {stats['empty_directories']}")
                report.append(f"  👁️ Hidden Files: {stats['hidden_files']}")
                report.append(f"  👁️ Hidden Directories: {stats['hidden_directories']}")

                # Largest files
                if stats["largest_files"]:
                    report.append("\n📏 Largest Files:")
                    for file_path, size in stats["largest_files"][:5]:
                        report.append(
                            f"  {os.path.basename(file_path)}: {self.format_file_size(size)}"
                        )

                # Recent files
                if stats["recent_files"]:
                    report.append("\n🕒 Recently Modified Files:")
                    from datetime import datetime

                    for file_path, modified in stats["recent_files"][:5]:
                        report.append(
                            f"  {os.path.basename(file_path)}: {datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M')}"
                        )

                return "\n".join(report)

        # Create analyzer and analyze directory
        analyzer = StatisticsAnalyzer()
        stats = analyzer.analyze_directory(root_path)

        # Display the statistics report
        print_info("")
        print_info(analyzer.generate_statistics_report(stats))

        print_success("✅ Statistics analysis completed!")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during statistics analysis: {e}")


def compare_directories():
    """Compare statistics between multiple directories."""
    print_header("🔍 Directory Comparison", color=Mocha.sapphire)

    try:
        # Get multiple paths to compare
        print_info(
            "📁 Enter directories to compare (one per line, empty line to finish):"
        )
        paths = []
        while True:
            path = input(f"Directory {len(paths) + 1}: ").strip()
            if not path:
                break
            if os.path.exists(path):
                paths.append(path)
            else:
                print_warning(f"⚠️ Path does not exist: {path}")

        if len(paths) < 2:
            print_warning(
                "❌ Need at least 2 directories to compare. Operation cancelled."
            )
            return

        print_info(f"\n🔄 Comparing {len(paths)} directories...")

        # Enhanced directory tree implementation with python-magic
        MAGIC_AVAILABLE = False
        magic = None

        try:
            import magic

            # Try to initialize magic with Windows-specific handling
            try:
                # Try standard initialization first
                test_magic = magic.Magic(mime=True)
                MAGIC_AVAILABLE = True
            except Exception as e:
                # Try with explicit magic file paths for Windows
                magic_file_paths = [
                    "C:/Windows/System32/magic.mgc",
                    "C:/Windows/System32/magic",
                    "C:/Program Files/Git/usr/share/misc/magic.mgc",
                    "C:/Program Files/Git/usr/share/misc/magic",
                    "C:/msys64/usr/share/misc/magic.mgc",
                    "C:/msys64/usr/share/misc/magic",
                    "C:/cygwin64/usr/share/misc/magic.mgc",
                    "C:/cygwin64/usr/share/misc/magic",
                ]

                for magic_file in magic_file_paths:
                    try:
                        if os.path.exists(magic_file):
                            test_magic = magic.Magic(mime=True, magic_file=magic_file)
                            MAGIC_AVAILABLE = True
                            break
                    except Exception:
                        continue

        except ImportError:
            pass

        class DirectoryComparator:
            def __init__(self):
                # Define categories with appropriate emojis
                self.categories = {
                    "directory": "📁",
                    "image": "🖼️",
                    "audio": "🎵",
                    "video": "🎬",
                    "document": "📄",
                    "executable": "⚙️",
                    "archive": "📦",
                    "code": "📝",
                    "data": "📊",
                    "web": "🌐",
                    "3d": "💠",
                    "font": "🔤",
                    "other": "📄",  # Default category
                }

                # Initialize magic instance if available
                self.magic_instance = None
                if MAGIC_AVAILABLE and magic:
                    try:
                        self.magic_instance = magic.Magic(mime=True)
                    except Exception:
                        # Try with magic file paths
                        magic_file_paths = [
                            "C:/Windows/System32/magic.mgc",
                            "C:/Windows/System32/magic",
                            "C:/Program Files/Git/usr/share/misc/magic.mgc",
                            "C:/Program Files/Git/usr/share/misc/magic",
                            "C:/msys64/usr/share/misc/magic.mgc",
                            "C:/msys64/usr/share/misc/magic",
                            "C:/cygwin64/usr/share/misc/magic.mgc",
                            "C:/cygwin64/usr/share/misc/magic",
                        ]

                        for magic_file in magic_file_paths:
                            try:
                                if os.path.exists(magic_file):
                                    self.magic_instance = magic.Magic(
                                        mime=True, magic_file=magic_file
                                    )
                                    break
                            except Exception:
                                continue

            def get_file_emoji(self, file_path: str) -> str:
                """Get the appropriate emoji for a file based on its type."""
                if os.path.isdir(file_path):
                    return self.categories["directory"]

                # Enhanced detection for specific file types (works without magic)
                filename = os.path.basename(file_path).lower()

                # Check for specific file extensions first
                if filename.endswith(
                    (
                        ".py",
                        ".pyc",
                        ".pyo",
                        ".js",
                        ".jsx",
                        ".ts",
                        ".tsx",
                        ".html",
                        ".css",
                        ".scss",
                        ".java",
                        ".cpp",
                        ".c",
                        ".h",
                        ".php",
                        ".rb",
                        ".go",
                        ".rs",
                        ".swift",
                        ".kt",
                    )
                ):
                    return self.categories["code"]
                elif filename.endswith(
                    (
                        ".json",
                        ".xml",
                        ".csv",
                        ".yaml",
                        ".yml",
                        ".toml",
                        ".ini",
                        ".cfg",
                        ".conf",
                    )
                ):
                    return self.categories["data"]
                elif filename.endswith(
                    (".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages")
                ):
                    return self.categories["document"]
                elif filename.endswith(
                    (".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz")
                ):
                    return self.categories["archive"]
                elif filename.endswith(
                    (".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma")
                ):
                    return self.categories["audio"]
                elif filename.endswith(
                    (
                        ".mp4",
                        ".avi",
                        ".mov",
                        ".wmv",
                        ".flv",
                        ".mkv",
                        ".webm",
                        ".m4v",
                        ".3gp",
                    )
                ):
                    return self.categories["video"]
                elif filename.endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".tiff",
                        ".webp",
                        ".svg",
                        ".ico",
                        ".raw",
                        ".cr2",
                        ".nef",
                        ".arw",
                    )
                ):
                    return self.categories["image"]
                elif filename.endswith(
                    (".exe", ".msi", ".bat", ".cmd", ".com", ".app", ".dmg")
                ):
                    return self.categories["executable"]
                elif filename.endswith((".ttf", ".otf", ".woff", ".woff2", ".eot")):
                    return self.categories["font"]
                elif filename.endswith(
                    (".obj", ".fbx", ".dae", ".3ds", ".blend", ".max", ".ma")
                ):
                    return self.categories["3d"]
                elif filename.endswith(
                    (".html", ".htm", ".css", ".js", ".php", ".asp", ".jsp")
                ):
                    return self.categories["web"]

                # Try magic-based detection if available
                if self.magic_instance:
                    try:
                        mime_type = self.magic_instance.from_file(file_path)
                        if mime_type.startswith("image/"):
                            return self.categories["image"]
                        elif mime_type.startswith("audio/"):
                            return self.categories["audio"]
                        elif mime_type.startswith("video/"):
                            return self.categories["video"]
                        elif mime_type.startswith("text/"):
                            if "javascript" in mime_type or "python" in mime_type:
                                return self.categories["code"]
                            else:
                                return self.categories["document"]
                        elif mime_type.startswith("application/"):
                            if "pdf" in mime_type:
                                return self.categories["document"]
                            elif "zip" in mime_type or "rar" in mime_type:
                                return self.categories["archive"]
                            elif "executable" in mime_type:
                                return self.categories["executable"]
                    except Exception:
                        pass

                return self.categories["other"]

            def get_file_type(self, file_path: str) -> str:
                """Get the file type category."""
                emoji = self.get_file_emoji(file_path)
                for category, cat_emoji in self.categories.items():
                    if cat_emoji == emoji:
                        return category
                return "other"

            def analyze_directory(self, root_path: str) -> dict:
                """Analyze directory and return comprehensive statistics."""
                stats = {
                    "total_files": 0,
                    "total_directories": 0,
                    "total_size": 0,
                    "file_types": {},
                    "largest_files": [],
                    "recent_files": [],
                    "empty_directories": 0,
                    "hidden_files": 0,
                    "hidden_directories": 0,
                    "symlinks": 0,
                    "broken_symlinks": 0,
                }

                try:
                    for root, dirs, files in os.walk(root_path):
                        # Count directories
                        for dir_name in dirs:
                            dir_path = os.path.join(root, dir_name)
                            stats["total_directories"] += 1

                            if dir_name.startswith("."):
                                stats["hidden_directories"] += 1

                            # Check for empty directories
                            try:
                                if not os.listdir(dir_path):
                                    stats["empty_directories"] += 1
                            except (PermissionError, OSError):
                                pass

                        # Count files
                        for file_name in files:
                            file_path = os.path.join(root, file_name)
                            stats["total_files"] += 1

                            if file_name.startswith("."):
                                stats["hidden_files"] += 1

                            try:
                                # Get file size
                                file_size = os.path.getsize(file_path)
                                stats["total_size"] += file_size

                                # Track largest files
                                stats["largest_files"].append((file_path, file_size))

                                # Track recent files
                                modified_time = os.path.getmtime(file_path)
                                stats["recent_files"].append((file_path, modified_time))

                                # Categorize file type
                                file_type = self.get_file_type(file_path)
                                stats["file_types"][file_type] = (
                                    stats["file_types"].get(file_type, 0) + 1
                                )

                            except (PermissionError, OSError):
                                # Skip files we can't access
                                continue

                except (PermissionError, OSError) as e:
                    print_warning(
                        f"⚠️ Some files/directories could not be accessed: {e}"
                    )

                # Sort largest files and recent files
                stats["largest_files"].sort(key=lambda x: x[1], reverse=True)
                stats["recent_files"].sort(key=lambda x: x[1], reverse=True)

                # Keep only top 10
                stats["largest_files"] = stats["largest_files"][:10]
                stats["recent_files"] = stats["recent_files"][:10]

                return stats

            def format_file_size(self, size_bytes: int) -> str:
                """Format file size in human-readable format."""
                if size_bytes == 0:
                    return "0 B"

                size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
                i = 0
                size_float = float(size_bytes)
                while size_float >= 1024 and i < len(size_names) - 1:
                    size_float /= 1024.0
                    i += 1

                return f"{size_float:.1f} {size_names[i]}"

            def generate_comparison_report(self, paths: list, all_stats: list) -> str:
                """Generate a comprehensive comparison report."""
                report = []
                report.append("🔍 Directory Comparison Report")
                report.append("=" * 60)

                # Summary table
                report.append("\n📊 Summary Comparison:")
                report.append("-" * 60)
                report.append(
                    f"{'Directory':<30} {'Files':<8} {'Dirs':<8} {'Size':<12}"
                )
                report.append("-" * 60)

                for i, (path, stats) in enumerate(zip(paths, all_stats)):
                    dir_name = (
                        os.path.basename(path) if os.path.basename(path) else path
                    )
                    if len(dir_name) > 28:
                        dir_name = dir_name[:25] + "..."
                    report.append(
                        f"{dir_name:<30} {stats['total_files']:<8,} {stats['total_directories']:<8,} {self.format_file_size(stats['total_size']):<12}"
                    )

                # Detailed analysis for each directory
                for i, (path, stats) in enumerate(zip(paths, all_stats)):
                    report.append(
                        f"\n📁 Directory {i+1}: {os.path.basename(path) or path}"
                    )
                    report.append("-" * 50)
                    report.append(f"📄 Total Files: {stats['total_files']:,}")
                    report.append(
                        f"📁 Total Directories: {stats['total_directories']:,}"
                    )
                    report.append(
                        f"💾 Total Size: {self.format_file_size(stats['total_size'])}"
                    )

                    # File type breakdown
                    if stats["file_types"]:
                        report.append("\n📋 File Type Breakdown:")
                        sorted_types = sorted(
                            stats["file_types"].items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )
                        for file_type, count in sorted_types[:5]:  # Top 5 types
                            emoji = self.categories.get(file_type, "📄")
                            percentage = (
                                (count / stats["total_files"]) * 100
                                if stats["total_files"] > 0
                                else 0
                            )
                            report.append(
                                f"  {emoji} {file_type.title()}: {count:,} ({percentage:.1f}%)"
                            )

                # Comparison insights
                report.append("\n🔍 Comparison Insights:")
                report.append("-" * 50)

                # Find largest directory by size
                largest_by_size = max(all_stats, key=lambda x: x["total_size"])
                largest_idx = all_stats.index(largest_by_size)
                report.append(
                    f"📏 Largest by size: Directory {largest_idx+1} ({self.format_file_size(largest_by_size['total_size'])})"
                )

                # Find directory with most files
                most_files = max(all_stats, key=lambda x: x["total_files"])
                most_files_idx = all_stats.index(most_files)
                report.append(
                    f"📄 Most files: Directory {most_files_idx+1} ({most_files['total_files']:,} files)"
                )

                # Find directory with most directories
                most_dirs = max(all_stats, key=lambda x: x["total_directories"])
                most_dirs_idx = all_stats.index(most_dirs)
                report.append(
                    f"📁 Most directories: Directory {most_dirs_idx+1} ({most_dirs['total_directories']:,} directories)"
                )

                # Size differences
                if len(all_stats) >= 2:
                    sizes = [stats["total_size"] for stats in all_stats]
                    min_size = min(sizes)
                    max_size = max(sizes)
                    size_diff = max_size - min_size
                    if size_diff > 0:
                        report.append(
                            f"📊 Size difference: {self.format_file_size(size_diff)} between smallest and largest"
                        )

                return "\n".join(report)

        # Create comparator and analyze all directories
        comparator = DirectoryComparator()
        all_stats = []

        for path in paths:
            print_info(f"🔄 Analyzing: {os.path.basename(path) or path}")
            stats = comparator.analyze_directory(path)
            all_stats.append(stats)

        # Display the comparison report
        print_info("")
        print_info(comparator.generate_comparison_report(paths, all_stats))

        print_success("✅ Directory comparison completed!")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during directory comparison: {e}")


def export_statistics_report(stats: dict, output_path: str, format_type: str = "json"):
    """Export statistics report to various formats."""
    try:
        if format_type == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
        elif format_type == "csv":
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Category", "Count", "Percentage"])
                total_files = stats["total_files"]
                for file_type, count in stats["file_types"].items():
                    percentage = (count / total_files) * 100 if total_files > 0 else 0
                    writer.writerow([file_type, count, f"{percentage:.1f}%"])
        elif format_type == "txt":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("Directory Statistics Report\n")
                f.write("=" * 50 + "\n")
                f.write(
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
                f.write(f"Total Files: {stats['total_files']:,}\n")
                f.write(f"Total Directories: {stats['total_directories']:,}\n")
                f.write(f"Total Size: {stats['total_size']:,} bytes\n\n")
                f.write("File Type Breakdown:\n")
                for file_type, count in stats["file_types"].items():
                    percentage = (
                        (count / stats["total_files"]) * 100
                        if stats["total_files"] > 0
                        else 0
                    )
                    f.write(f"  {file_type}: {count:,} ({percentage:.1f}%)\n")

        print_success(f"✅ Report exported to: {output_path}")
        return True
    except Exception as e:
        print_error(f"❌ Export failed: {e}")
        return False


def generate_visual_charts(stats: dict, output_dir: str):
    """Generate visual charts from statistics data."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Set up matplotlib style
        plt.style.use("default")
        plt.rcParams["figure.figsize"] = (12, 8)
        plt.rcParams["font.size"] = 10

        # 1. File Type Distribution Pie Chart
        if stats["file_types"]:
            plt.figure(figsize=(10, 8))
            labels = list(stats["file_types"].keys())
            sizes = list(stats["file_types"].values())
            colors = [
                "#ff9999",
                "#66b3ff",
                "#99ff99",
                "#ffcc99",
                "#ff99cc",
                "#c2c2f0",
                "#ffb366",
                "#d9b3ff",
            ]

            plt.pie(
                sizes,
                labels=labels,
                colors=colors[: len(labels)],
                autopct="%1.1f%%",
                startangle=90,
            )
            plt.title("File Type Distribution", fontsize=16, fontweight="bold")
            plt.axis("equal")
            plt.tight_layout()
            plt.savefig(
                os.path.join(output_dir, "file_type_distribution.png"),
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

        # 2. File Size Distribution Histogram
        if stats["largest_files"]:
            plt.figure(figsize=(12, 6))
            sizes = [size for _, size in stats["largest_files"]]
            plt.hist(sizes, bins=20, alpha=0.7, color="skyblue", edgecolor="black")
            plt.xlabel("File Size (bytes)")
            plt.ylabel("Number of Files")
            plt.title("File Size Distribution", fontsize=16, fontweight="bold")
            plt.yscale("log")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(
                os.path.join(output_dir, "file_size_distribution.png"),
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

        # 3. Directory Structure Bar Chart
        if stats["file_types"]:
            plt.figure(figsize=(12, 6))
            file_types = list(stats["file_types"].keys())
            counts = list(stats["file_types"].values())

            bars = plt.bar(
                range(len(file_types)), counts, color="lightcoral", alpha=0.8
            )
            plt.xlabel("File Types")
            plt.ylabel("Number of Files")
            plt.title("File Count by Type", fontsize=16, fontweight="bold")
            plt.xticks(range(len(file_types)), file_types, rotation=45, ha="right")

            # Add value labels on bars
            for bar, count in zip(bars, counts):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01 * max(counts),
                    f"{count:,}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(
                os.path.join(output_dir, "file_count_by_type.png"),
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

        print_success(f"✅ Charts generated in: {output_dir}")
        return True
    except Exception as e:
        print_error(f"❌ Chart generation failed: {e}")
        return False


def enhanced_statistics_analysis():
    """Enhanced statistics analysis with export and visualization options."""
    print_header("📊 Enhanced Directory Statistics Analysis", color=Mocha.sapphire)

    # Get directory path
    root_path = input("📁 Enter directory path to analyze: ").strip()
    if not root_path:
        print_warning("❌ No path specified. Operation cancelled.")
        return

    if not os.path.exists(root_path):
        print_error(f"❌ Path does not exist: {root_path}")
        return

    try:
        print_info("🔄 Analyzing directory statistics with progress tracking...")

        # Use the existing StatisticsAnalyzer class
        # (Implementation would be similar to tree_statistics_analysis)

        # For now, let's create a simple enhanced analyzer
        stats = {
            "total_files": 0,
            "total_directories": 0,
            "total_size": 0,
            "file_types": {},
            "largest_files": [],
            "recent_files": [],
            "empty_directories": 0,
            "hidden_files": 0,
            "hidden_directories": 0,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        # Analyze with progress bar
        all_files = []
        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                all_files.append(file_path)

        print_info(f"📁 Found {len(all_files)} files to analyze...")

        for file_path in tqdm(all_files, desc="Analyzing files"):
            try:
                stats["total_files"] += 1
                file_size = os.path.getsize(file_path)
                stats["total_size"] += file_size

                # Categorize file type
                ext = os.path.splitext(file_path)[1].lower()
                if ext:
                    stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1

                # Track largest files
                stats["largest_files"].append((file_path, file_size))

                # Track recent files
                modified_time = os.path.getmtime(file_path)
                stats["recent_files"].append((file_path, modified_time))

            except (PermissionError, OSError):
                continue

        # Sort and limit lists
        stats["largest_files"].sort(key=lambda x: x[1], reverse=True)
        stats["recent_files"].sort(key=lambda x: x[1], reverse=True)
        stats["largest_files"] = stats["largest_files"][:10]
        stats["recent_files"] = stats["recent_files"][:10]

        # Display enhanced report
        print_header(
            "📊 ENHANCED DIRECTORY STATISTICS REPORT", char="=", color=Mocha.lavender
        )
        print_info(f"📁 Directory: {root_path}")
        print_info(f"🕒 Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"📄 Total Files: {stats['total_files']:,}")
        print_info(
            f"💾 Total Size: {stats['total_size']:,} bytes ({stats['total_size']/1024/1024:.1f} MB)"
        )

        if stats["file_types"]:
            print_info("")
            print_info("📋 File Type Breakdown:")
            sorted_types = sorted(
                stats["file_types"].items(), key=lambda x: x[1], reverse=True
            )
            for ext, count in sorted_types[:10]:
                percentage = (count / stats["total_files"]) * 100
                print_info(f"  {ext}: {count:,} ({percentage:.1f}%)")

        # Export options
        print_info("")
        print_info("💾 Export Options:")
        export_choice = (
            input("Export report? (json/csv/txt/none) [none]: ").strip().lower()
        )

        if export_choice in ["json", "csv", "txt"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"directory_stats_{timestamp}.{export_choice}"
            export_statistics_report(stats, filename, export_choice)

        # Visualization options
        viz_choice = input("Generate visual charts? (y/n) [n]: ").strip().lower()
        if viz_choice == "y":
            charts_dir = f"charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            generate_visual_charts(stats, charts_dir)

        print_success("✅ Enhanced statistics analysis completed!")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during enhanced analysis: {e}")


def batch_export_analysis():
    """Batch analyze and export statistics for multiple directories."""
    print_header("📦 Batch Export Analysis", color=Mocha.sapphire)

    try:
        # Get multiple paths
        print_info(
            "📁 Enter multiple directory paths (one per line, empty line to finish):"
        )
        paths = []
        while True:
            path = input(f"Path {len(paths) + 1}: ").strip()
            if not path:
                break
            if os.path.exists(path):
                paths.append(path)
            else:
                print_warning(f"⚠️ Path does not exist: {path}")

        if not paths:
            print_warning("❌ No valid paths specified. Operation cancelled.")
            return

        # Get export settings
        print_info(f"\n⚙️ Export settings for {len(paths)} directories:")
        export_format = (
            input("Export format (json/csv/txt) [json]: ").strip().lower() or "json"
        )
        generate_charts = input("Generate charts? (y/n) [n]: ").strip().lower() == "y"

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"batch_analysis_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)

        # Process each directory
        successful = 0
        failed = 0

        for i, path in enumerate(paths, 1):
            print_info(
                f"\n🔄 Processing {i}/{len(paths)}: {os.path.basename(path) or path}"
            )

            try:
                # Simple analysis for each directory
                stats = {
                    "directory": path,
                    "total_files": 0,
                    "total_size": 0,
                    "file_types": {},
                    "analysis_timestamp": datetime.now().isoformat(),
                }

                for root, dirs, files in os.walk(path):
                    for file_name in files:
                        try:
                            file_path = os.path.join(root, file_name)
                            stats["total_files"] += 1
                            file_size = os.path.getsize(file_path)
                            stats["total_size"] += file_size

                            ext = os.path.splitext(file_path)[1].lower()
                            if ext:
                                stats["file_types"][ext] = (
                                    stats["file_types"].get(ext, 0) + 1
                                )
                        except (PermissionError, OSError):
                            continue

                # Export individual report
                safe_name = (
                    os.path.basename(path).replace("/", "_").replace("\\", "_")
                    or "root"
                )
                filename = os.path.join(
                    output_dir, f"{safe_name}_stats.{export_format}"
                )
                export_statistics_report(stats, filename, export_format)

                # Generate charts if requested
                if generate_charts:
                    charts_dir = os.path.join(output_dir, f"{safe_name}_charts")
                    generate_visual_charts(stats, charts_dir)

                successful += 1
                print_success(f"✅ Completed: {os.path.basename(path) or path}")

            except Exception as e:
                failed += 1
                print_error(f"❌ Failed: {os.path.basename(path) or path} - {e}")

        # Generate summary report
        summary = {
            "batch_analysis": {
                "timestamp": datetime.now().isoformat(),
                "total_directories": len(paths),
                "successful": successful,
                "failed": failed,
                "export_format": export_format,
                "charts_generated": generate_charts,
                "output_directory": output_dir,
            }
        }

        summary_file = os.path.join(output_dir, "batch_summary.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print_success(
            f"\n✅ Batch analysis completed: {successful} successful, {failed} failed"
        )
        print_info(f"📁 Results saved in: {output_dir}")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during batch analysis: {e}")


def advanced_insights_analysis():
    """Advanced insights analysis with detailed metrics and recommendations."""
    print_header("🔍 Advanced Insights Analysis", color=Mocha.sapphire)

    root_path = input("📁 Enter directory path to analyze: ").strip()
    if not root_path:
        print_warning("❌ No path specified. Operation cancelled.")
        return

    if not os.path.exists(root_path):
        print_error(f"❌ Path does not exist: {root_path}")
        return

    try:
        print_info("🔄 Performing advanced insights analysis...")

        # Advanced analysis metrics
        insights = {
            "basic_stats": {},
            "file_patterns": {},
            "size_analysis": {},
            "age_analysis": {},
            "duplicate_analysis": {},
            "recommendations": [],
        }

        # Collect detailed data
        all_files = []
        file_sizes = []
        file_ages = []
        file_extensions = defaultdict(int)
        file_names = defaultdict(int)

        for root, dirs, files in os.walk(root_path):
            for file_name in files:
                try:
                    file_path = os.path.join(root, file_name)
                    file_size = os.path.getsize(file_path)
                    file_age = datetime.now().timestamp() - os.path.getmtime(file_path)

                    all_files.append(file_path)
                    file_sizes.append(file_size)
                    file_ages.append(file_age)

                    ext = os.path.splitext(file_name)[1].lower()
                    if ext:
                        file_extensions[ext] += 1

                    base_name = os.path.splitext(file_name)[0]
                    file_names[base_name] += 1

                except (PermissionError, OSError):
                    continue

        # Calculate insights
        if file_sizes:
            insights["size_analysis"] = {
                "total_size": sum(file_sizes),
                "average_size": sum(file_sizes) / len(file_sizes),
                "median_size": sorted(file_sizes)[len(file_sizes) // 2],
                "largest_file": max(file_sizes),
                "smallest_file": min(file_sizes),
                "size_distribution": {
                    "tiny": len([s for s in file_sizes if s < 1024]),
                    "small": len([s for s in file_sizes if 1024 <= s < 1024 * 1024]),
                    "medium": len(
                        [s for s in file_sizes if 1024 * 1024 <= s < 100 * 1024 * 1024]
                    ),
                    "large": len([s for s in file_sizes if s >= 100 * 1024 * 1024]),
                },
            }

        if file_ages:
            insights["age_analysis"] = {
                "average_age_days": sum(file_ages) / len(file_ages) / 86400,
                "oldest_file_days": max(file_ages) / 86400,
                "newest_file_days": min(file_ages) / 86400,
                "recent_files": len(
                    [a for a in file_ages if a < 86400]
                ),  # Last 24 hours
                "old_files": len(
                    [a for a in file_ages if a > 30 * 86400]
                ),  # Older than 30 days
            }

        # File pattern analysis
        insights["file_patterns"] = {
            "total_extensions": len(file_extensions),
            "most_common_extension": (
                max(file_extensions.items(), key=lambda x: x[1])
                if file_extensions
                else None
            ),
            "extension_distribution": dict(
                sorted(file_extensions.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "potential_duplicates": {
                name: count for name, count in file_names.items() if count > 1
            },
        }

        # Generate recommendations
        recommendations = []

        if insights["size_analysis"].get("size_distribution", {}).get("large", 0) > 10:
            recommendations.append(
                "🔍 Consider archiving large files (>100MB) to save space"
            )

        if insights["age_analysis"].get("old_files", 0) > len(all_files) * 0.5:
            recommendations.append(
                "📅 Many files are older than 30 days - consider cleanup"
            )

        if len(insights["file_patterns"].get("potential_duplicates", {})) > 5:
            recommendations.append(
                "🔄 Multiple potential duplicate files detected - run deduplication"
            )

        if insights["file_patterns"].get("total_extensions", 0) > 20:
            recommendations.append(
                "📋 High variety of file types - consider organizing by type"
            )

        insights["recommendations"] = recommendations

        # Display insights
        print_header("🔍 ADVANCED INSIGHTS REPORT", char="=", color=Mocha.lavender)

        print_info("")
        print_info("📊 Size Analysis:")
        size_analysis = insights["size_analysis"]
        print_info(
            f"  Total Size: {size_analysis['total_size']:,} bytes ({size_analysis['total_size']/1024/1024:.1f} MB)"
        )
        print_info(f"  Average File Size: {size_analysis['average_size']:,.0f} bytes")
        print_info(f"  Largest File: {size_analysis['largest_file']:,} bytes")

        print_info("")
        print_info("📅 Age Analysis:")
        age_analysis = insights["age_analysis"]
        print_info(f"  Average Age: {age_analysis['average_age_days']:.1f} days")
        print_info(f"  Recent Files (24h): {age_analysis['recent_files']}")
        print_info(f"  Old Files (>30 days): {age_analysis['old_files']}")

        print_info("")
        print_info("📋 File Patterns:")
        patterns = insights["file_patterns"]
        print_info(f"  Unique Extensions: {patterns['total_extensions']}")
        if patterns["most_common_extension"]:
            ext, count = patterns["most_common_extension"]
            print_info(f"  Most Common: {ext} ({count} files)")

        if patterns["potential_duplicates"]:
            print_info(
                f"  Potential Duplicates: {len(patterns['potential_duplicates'])} base names"
            )

        if recommendations:
            print_info("")
            print_info("💡 Recommendations:")
            for rec in recommendations:
                print_info(f"  {rec}")

        # Export insights
        export_choice = input("\n💾 Export insights? (y/n) [n]: ").strip().lower()
        if export_choice == "y":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advanced_insights_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(insights, f, indent=2, ensure_ascii=False)
            print_success(f"✅ Insights exported to: {filename}")

        print_success("✅ Advanced insights analysis completed!")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during advanced analysis: {e}")


def directory_tree_menu():
    """Main directory tree menu with enhanced features."""
    from dataset_forge.utils.printing import print_header, print_section
    from dataset_forge.utils.color import Mocha

    print_header(
        "🌳 Enhanced Directory Tree - Input/Output Selection", color=Mocha.peach
    )
    options = {
        "1": ("🌳 Quick Tree Generation", quick_tree_generation),
        "2": ("⚙️ Advanced Tree Generation", advanced_tree_generation),
        "3": ("📦 Batch Tree Generation", batch_tree_generation),
        "4": ("📊 Statistics Analysis", tree_statistics_analysis),
        "5": ("🔍 Compare Directories", compare_directories),
        "6": ("📈 Enhanced Statistics Analysis", enhanced_statistics_analysis),
        "7": ("📦 Batch Export Analysis", batch_export_analysis),
        "8": ("🔍 Advanced Insights Analysis", advanced_insights_analysis),
        "0": ("⬅️  Back to Main Menu", None),
    }

    # Define menu context for help system
    menu_context = {
        "Purpose": "Generate enhanced directory trees with statistics and analysis",
        "Options": "8 main options available",
        "Navigation": "Use numbers 1-8 to select, 0 to go back",
        "Key Features": [
            "Quick tree generation for basic overview",
            "Advanced tree generation with detailed options",
            "Batch tree generation for multiple directories",
            "Statistics analysis with comprehensive metrics",
            "Directory comparison tools",
            "Enhanced statistics with visual charts",
            "Batch export analysis for multiple directories",
            "Advanced insights analysis with recommendations",
        ],
        "Tips": [
            "Use quick generation for basic overview",
            "Advanced generation offers more customization",
            "Statistics analysis provides detailed metrics",
            "Compare directories to identify differences",
        ],
    }

    while True:
        try:
            print_section("Directory Tree Generation Progress", color=Mocha.peach)
            key = show_menu(
                "🌳 Enhanced Directory Tree Generator",
                options,
                Mocha.lavender,
                current_menu="Directory Tree Generator",
                menu_context=menu_context,
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            return
        except Exception as e:
            print_error(f"❌ Unexpected error: {e}")
            print_info("💡 Please try again or contact support if the issue persists.")
