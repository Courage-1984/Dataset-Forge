"""
Enhanced Directory Tree Generator

This module provides advanced directory tree generation with emoji categorization,
file type detection, and comprehensive statistics. It includes features like:

- Automatic file type detection using magic numbers
- Emoji categorization for different file types
- File size and modification time tracking
- Comprehensive statistics and reporting
- Multiple output formats (console, markdown, JSON)
- Configurable depth and ignore patterns
- Memory-efficient processing for large directories
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Import emoji utilities for better emoji handling
from ..utils.emoji_utils import (
    normalize_unicode,
    sanitize_emoji,
    is_valid_emoji,
    extract_emojis,
    categorize_emoji
)
from ..utils.memory_utils import auto_cleanup, memory_context
from ..utils.printing import print_info, print_success, print_warning, print_error

# Try to import magic for better file type detection
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None
    print_warning("⚠️  python-magic not available. Using extension-based file type detection.")


def is_image_file(filename: str) -> bool:
    """Check if a file is an image based on its extension."""
    image_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
        '.webp', '.svg', '.ico', '.raw', '.cr2', '.nef', '.arw'
    }
    return Path(filename).suffix.lower() in image_extensions


class EnhancedDirectoryTreeGenerator:
    """Enhanced directory tree generator with emoji categorization and file type detection."""

    def __init__(self):
        """Initialize the directory tree generator with emoji-safe categories."""
        # Enhanced categories with more specific emojis
        self.categories = {
            "directory": "📁",
            "image": "🖼️",
            "image_hq": "🎨",
            "image_lq": "🖼️",
            "video": "🎬",
            "audio": "🎵",
            "document": "📄",
            "document_pdf": "📕",
            "code_python": "🐍",
            "code_js": "📜",
            "code_html": "🌐",
            "data_json": "📊",
            "data_csv": "📈",
            "model": "🤖",
            "config": "⚙️",
            "log": "📝",
            "backup": "💾",
            "temp": "🗑️",
            "archive": "📦",
            "font": "🔤",
            "other": "📄"
        }
        
        # MIME type to category mapping
        self.file_type_mappings = {
            'image/jpeg': 'image',
            'image/png': 'image',
            'image/gif': 'image',
            'image/bmp': 'image',
            'image/tiff': 'image',
            'image/webp': 'image',
            'image/svg+xml': 'image',
            'video/mp4': 'video',
            'video/avi': 'video',
            'video/mov': 'video',
            'video/wmv': 'video',
            'video/flv': 'video',
            'video/webm': 'video',
            'audio/mpeg': 'audio',
            'audio/wav': 'audio',
            'audio/flac': 'audio',
            'audio/ogg': 'audio',
            'audio/aac': 'audio',
            'application/pdf': 'document_pdf',
            'text/plain': 'document',
            'text/html': 'code_html',
            'text/css': 'code_html',
            'application/javascript': 'code_js',
            'text/javascript': 'code_js',
            'application/json': 'data_json',
            'text/csv': 'data_csv',
            'application/x-python-code': 'code_python',
            'text/x-python': 'code_python',
            'application/x-yaml': 'config',
            'text/yaml': 'config',
            'text/xml': 'config',
            'application/xml': 'config',
            'application/zip': 'archive',
            'application/x-rar': 'archive',
            'application/x-tar': 'archive',
            'application/gzip': 'archive',
            'application/x-7z-compressed': 'archive',
            'font/ttf': 'font',
            'font/otf': 'font',
            'font/woff': 'font',
            'font/woff2': 'font',
        }

    def get_file_emoji(self, file_path: str) -> str:
        """
        Get the appropriate emoji for a file based on its type with emoji validation.

        Args:
            file_path: Path to the file

        Returns:
            Emoji string representing the file type
        """
        try:
            if os.path.isdir(file_path):
                return self.categories["directory"]

            # Enhanced detection for specific file types (works without magic)
            filename = os.path.basename(file_path).lower()

            # Check for specific file extensions first
            if filename.endswith((".py", ".pyc", ".pyo")):
                emoji = self.categories["code_python"]
            elif filename.endswith((".js", ".jsx")):
                emoji = self.categories["code_js"]
            elif filename.endswith((".html", ".htm")):
                emoji = self.categories["code_html"]
            elif filename.endswith((".json")):
                emoji = self.categories["data_json"]
            elif filename.endswith((".csv")):
                emoji = self.categories["data_csv"]
            elif filename.endswith((".pth", ".safetensors", ".onnx", ".pb")):
                emoji = self.categories["model"]
            elif filename.endswith((".yml", ".yaml", ".ini", ".cfg", ".conf")):
                emoji = self.categories["config"]
            elif filename.endswith((".log")):
                emoji = self.categories["log"]
            elif filename.endswith((".bak", ".backup")):
                emoji = self.categories["backup"]
            elif filename.endswith((".tmp", ".temp")):
                emoji = self.categories["temp"]
            elif filename.endswith((".pdf")):
                emoji = self.categories["document_pdf"]
            elif filename.endswith((".zip", ".rar", ".tar", ".gz", ".7z")):
                emoji = self.categories["archive"]
            elif filename.endswith((".mp3", ".wav", ".flac", ".ogg", ".aac")):
                emoji = self.categories["audio"]
            elif filename.endswith((".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm")):
                emoji = self.categories["video"]
            elif filename.endswith((".ttf", ".otf", ".woff", ".woff2")):
                emoji = self.categories["font"]
            elif is_image_file(filename):
                # Check if it's HQ or LQ based on size or naming convention
                try:
                    # Use a safer approach to get file size
                    if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                        file_size = os.path.getsize(file_path)
                        if file_size > 1024 * 1024:  # > 1MB
                            emoji = self.categories["image_hq"]
                        else:
                            emoji = self.categories["image_lq"]
                    else:
                        emoji = self.categories["image"]
                except (OSError, PermissionError, FileNotFoundError):
                    emoji = self.categories["image"]
            else:
                emoji = self.categories["other"]

            # Use magic if available for more accurate detection
            if MAGIC_AVAILABLE and magic:
                try:
                    if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                        mime_type = magic.from_file(file_path, mime=True)

                        # Check if it's a known type
                        if mime_type in self.file_type_mappings:
                            category = self.file_type_mappings[mime_type]
                            emoji = self.categories.get(
                                category, self.categories["other"]
                            )

                        # Fallback to MIME type detection
                        elif mime_type.startswith("image"):
                            emoji = self.categories["image"]
                        elif mime_type.startswith("audio"):
                            emoji = self.categories["audio"]
                        elif mime_type.startswith("video"):
                            emoji = self.categories["video"]
                        elif mime_type.startswith("text"):
                            emoji = self.categories["document"]
                        elif mime_type.startswith("application"):
                            emoji = self.categories["other"]
                except Exception:
                    pass  # Silently fall back to extension-based detection

            # Validate and sanitize the emoji
            if is_valid_emoji(emoji):
                return emoji
            else:
                # Fallback to a safe emoji
                return "📄"

        except Exception:
            # Final fallback
            return self.categories["other"]

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing file information
        """
        info = {
            "name": os.path.basename(file_path),
            "path": file_path,
            "is_dir": False,
            "emoji": self.categories["other"],
            "size": 0,
            "modified": None,
            "type": "unknown",
        }

        try:
            # Check if file exists and is accessible
            if not os.path.exists(file_path):
                return info

            info["is_dir"] = os.path.isdir(file_path)
            info["emoji"] = self.get_file_emoji(file_path)

            if not info["is_dir"]:
                # Only try to get file info if it's a file and accessible
                if os.access(file_path, os.R_OK):
                    try:
                        info["size"] = os.path.getsize(file_path)
                    except (OSError, PermissionError):
                        info["size"] = 0

                    try:
                        info["modified"] = datetime.fromtimestamp(
                            os.path.getmtime(file_path)
                        )
                    except (OSError, PermissionError):
                        info["modified"] = None

                    # Get file type
                    if MAGIC_AVAILABLE and magic:
                        try:
                            mime_type = magic.from_file(file_path, mime=True)
                            info["type"] = mime_type
                        except Exception:
                            info["type"] = "unknown"
                    else:
                        # Fallback based on extension
                        filename = os.path.basename(file_path).lower()
                        if filename.endswith(".py"):
                            info["type"] = "text/x-python"
                        elif filename.endswith(".json"):
                            info["type"] = "application/json"
                        elif filename.endswith(".txt"):
                            info["type"] = "text/plain"
                        elif is_image_file(filename):
                            info["type"] = "image"
                        else:
                            info["type"] = "unknown"

        except Exception:
            # Return safe defaults if anything goes wrong
            pass

        return info

    @auto_cleanup
    def generate_tree(
        self,
        root_path: str,
        prefix: str = "",
        ignore_patterns: Optional[List[str]] = None,
        max_depth: int = -1,
        current_depth: int = 0,
        include_stats: bool = True,
        include_file_info: bool = False,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a tree structure starting from the root path.

        Args:
            root_path: Root directory path
            prefix: Prefix for tree lines
            ignore_patterns: Patterns to ignore
            max_depth: Maximum depth to traverse (-1 for unlimited)
            current_depth: Current depth level
            include_stats: Whether to include statistics
            include_file_info: Whether to include detailed file information

        Returns:
            Tuple of (tree_string, statistics_dict)
        """
        print_info(
            f"DEBUG: generate_tree called for {root_path} at depth {current_depth}"
        )
        with memory_context("Directory Tree Generation"):
            if ignore_patterns is None:
                ignore_patterns = [
                    ".git",
                    "__pycache__",
                    "node_modules",
                    ".idea",
                    ".vscode",
                    ".DS_Store",
                    "Thumbs.db",
                    "*.tmp",
                    "*.temp",
                ]

            # Reset statistics
            if include_stats:
                self.stats = {
                    "total_files": 0,
                    "total_dirs": 0,
                    "total_size": 0,
                    "file_types": {},
                    "largest_files": [],
                    "recent_files": [],
                }

            output = []
            root_path = os.path.abspath(root_path)
            print_info(f"DEBUG: About to list directory {root_path}")

            try:
                items = os.listdir(root_path)
                print_info(f"DEBUG: Found {len(items)} items in {root_path}")
            except PermissionError:
                print_info(f"DEBUG: Permission denied for {root_path}")
                return f"{prefix}└── ⛔ Permission Denied\n", self.stats

            # Sort items (directories first, then alphabetically)
            try:
                items.sort(
                    key=lambda x: (
                        not os.path.isdir(os.path.join(root_path, x)),
                        x.lower(),
                    )
                )
                print_info(f"DEBUG: Sorted {len(items)} items")
            except Exception:
                # If sorting fails, just use alphabetical order
                items.sort(key=lambda x: x.lower())
                print_info(f"DEBUG: Used fallback sorting for {len(items)} items")

            # Filter ignored items
            items = [
                item
                for item in items
                if not any(pattern in item for pattern in ignore_patterns)
            ]
            print_info(f"DEBUG: After filtering, {len(items)} items remain")

            # Process items without complex progress tracking
            for index, item in enumerate(items):
                try:
                    print_info(f"DEBUG: Processing item {index+1}/{len(items)}: {item}")
                    item_path = os.path.join(root_path, item)
                    is_last_item = index == len(items) - 1

                    current_prefix = "└── " if is_last_item else "├── "
                    next_prefix = "    " if is_last_item else "│   "

                    # Check if item still exists (it might have been deleted)
                    if not os.path.exists(item_path):
                        print_info(f"DEBUG: Item no longer exists: {item_path}")
                        continue

                    if os.path.isdir(item_path):
                        # Directory
                        print_info(f"DEBUG: Processing directory: {item}")
                        emoji = self.get_file_emoji(item_path)
                        output.append(f"{prefix}{current_prefix}{emoji} {item}\n")

                        if include_stats:
                            self.stats["total_dirs"] += 1

                        # Recursively process subdirectories
                        if max_depth == -1 or current_depth < max_depth:
                            try:
                                print_info(f"DEBUG: Recursing into {item_path}")
                                sub_tree, _ = self.generate_tree(
                                    item_path,
                                    prefix + next_prefix,
                                    ignore_patterns,
                                    max_depth,
                                    current_depth + 1,
                                    include_stats=False,  # Don't double-count
                                    include_file_info=include_file_info,
                                )
                                output.append(sub_tree)
                                print_info(
                                    f"DEBUG: Completed recursion for {item_path}"
                                )
                            except Exception as e:
                                # If subdirectory processing fails, add error indicator
                                print_info(
                                    f"DEBUG: Error in subdirectory {item_path}: {e}"
                                )
                                output.append(
                                    f"{prefix}{next_prefix}└── ⚠️ Error processing subdirectory\n"
                                )
                    else:
                        # File
                        print_info(f"DEBUG: Processing file: {item}")
                        try:
                            file_info = self.get_file_info(item_path)
                            emoji = file_info["emoji"]

                            if include_file_info:
                                size_str = self.format_file_size(file_info["size"])
                                output.append(
                                    f"{prefix}{current_prefix}{emoji} {item} ({size_str})\n"
                                )
                            else:
                                output.append(
                                    f"{prefix}{current_prefix}{emoji} {item}\n"
                                )

                            # Update statistics
                            if include_stats:
                                self.stats["total_files"] += 1
                                self.stats["total_size"] += file_info["size"]

                                # Track file types
                                file_type = file_info["type"]
                                if file_type not in self.stats["file_types"]:
                                    self.stats["file_types"][file_type] = 0
                                self.stats["file_types"][file_type] += 1

                                # Track largest files
                                self.stats["largest_files"].append(
                                    (item_path, file_info["size"])
                                )

                                # Track recent files
                                if file_info["modified"]:
                                    self.stats["recent_files"].append(
                                        (item_path, file_info["modified"])
                                    )
                        except Exception as e:
                            # If file processing fails, add error indicator
                            print_info(f"DEBUG: Error processing file {item_path}: {e}")
                            output.append(
                                f"{prefix}{current_prefix}⚠️ {item} (Error processing)\n"
                            )

                except Exception as e:
                    # Skip this item if there's any error
                    print_info(f"DEBUG: Skipping item {item} due to error: {e}")
                    continue

            print_info(f"DEBUG: Completed processing {root_path}")
            return "".join(output), self.stats

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def generate_statistics_report(self, stats: Dict[str, Any]) -> str:
        """Generate a detailed statistics report."""
        if not stats:
            return "No statistics available."

        report = []
        report.append("📊 Directory Statistics Report")
        report.append("=" * 50)
        report.append(f"📁 Total Directories: {stats['total_dirs']}")
        report.append(f"📄 Total Files: {stats['total_files']}")
        report.append(f"💾 Total Size: {self.format_file_size(stats['total_size'])}")

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
                report.append(
                    f"  {os.path.basename(file_path)}: {modified.strftime('%Y-%m-%d %H:%M')}"
                )

        return "\n".join(report)

    def save_tree_to_markdown(
        self, tree_output: str, stats: Dict[str, Any], output_path: str
    ) -> str:
        """Save tree output to a markdown file with statistics."""
        try:
            with open(output_path, "w", encoding="utf-8") as md_file:
                md_file.write(
                    f"# Directory Tree for: {os.path.abspath(output_path)}\n\n"
                )
                md_file.write(
                    f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
                md_file.write("## Tree Structure\n\n")
                md_file.write("```\n")
                md_file.write(tree_output)
                md_file.write("```\n\n")

                if stats:
                    md_file.write("## Statistics\n\n")
                    md_file.write(self.generate_statistics_report(stats))
                    md_file.write("\n")

            return output_path
        except Exception as e:
            print_error(f"❌ Error saving markdown file: {e}")
            return ""

    def save_tree_to_json(
        self, tree_output: str, stats: Dict[str, Any], output_path: str
    ) -> str:
        """Save tree output and statistics to a JSON file."""
        try:
            data = {
                "generated_at": datetime.now().isoformat(),
                "tree_output": tree_output,
                "statistics": stats,
            }

            with open(output_path, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=2, default=str)

            return output_path
        except Exception as e:
            print_error(f"❌ Error saving JSON file: {e}")
            return ""


def generate_directory_tree(
    root_path: str,
    ignore_patterns: Optional[List[str]] = None,
    max_depth: int = -1,
    include_stats: bool = True,
    include_file_info: bool = False,
    output_format: str = "console",
) -> Tuple[str, Dict[str, Any]]:
    """
    Generate a directory tree with enhanced features.

    Args:
        root_path: Root directory path
        ignore_patterns: Patterns to ignore
        max_depth: Maximum depth to traverse
        include_stats: Whether to include statistics
        include_file_info: Whether to include file information
        output_format: Output format (console, markdown, json)

    Returns:
        Tuple of (output_string, statistics_dict)
    """
    if not os.path.exists(root_path):
        print_error(f"❌ Path does not exist: {root_path}")
        return "", {}

    # Show magic availability status
    if not MAGIC_AVAILABLE:
        print_warning(
            "⚠️ python-magic library not available. Using fallback file type detection."
        )
        print_info(
            "💡 Install with: pip install python-magic python-magic-bin libmagic"
        )

    print_header("🌳 Enhanced Directory Tree Generator", color=Mocha.lavender)

    generator = EnhancedDirectoryTreeGenerator()

    # Generate tree
    tree_output, stats = generator.generate_tree(
        root_path=root_path,
        ignore_patterns=ignore_patterns,
        max_depth=max_depth,
        include_stats=include_stats,
        include_file_info=include_file_info,
    )

    # Format output
    if output_format == "console":
        output = f"Directory Tree for: {os.path.abspath(root_path)}\n\n"
        output += tree_output

        if include_stats and stats:
            output += "\n" + generator.generate_statistics_report(stats)

    elif output_format == "markdown":
        output_path = os.path.join(root_path, "directory_tree.md")
        saved_path = generator.save_tree_to_markdown(tree_output, stats, output_path)
        if saved_path:
            output = f"✅ Directory tree saved to: {saved_path}"
            print_success(output)
        else:
            output = "❌ Failed to save markdown file"

    elif output_format == "json":
        output_path = os.path.join(root_path, "directory_tree.json")
        saved_path = generator.save_tree_to_json(tree_output, stats, output_path)
        if saved_path:
            output = f"✅ Directory tree saved to: {saved_path}"
            print_success(output)
        else:
            output = "❌ Failed to save JSON file"

    else:
        output = "❌ Invalid output format"

    return output, stats


def quick_tree_generation():
    """Quick directory tree generation with default settings."""
    print_info("DEBUG: About to call print_header")
    print_header("🌳 Quick Directory Tree Generation", color=Mocha.sapphire)
    print_info("DEBUG: After print_header")

    # Simple input without complex utilities
    print_info("DEBUG: About to call input")
    root_path = input("📁 Enter directory path: ").strip()
    print_info("DEBUG: After input")
    if not root_path:
        print_warning("❌ No path specified. Operation cancelled.")
        return

    if not os.path.exists(root_path):
        print_error(f"❌ Path does not exist: {root_path}")
        return

    print_info("🔄 Generating directory tree with default settings...")

    try:
        # Generate tree with default settings
        output, stats = generate_directory_tree(
            root_path=root_path,
            output_format="console",
            include_stats=True,
            include_file_info=False,
        )

        print("\n" + output)
        print_success("✅ Quick tree generation completed!")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during tree generation: {e}")
        print_info("💡 Try using a different directory or check file permissions.")
        # Fallback to simple tree generation
        try:
            print_info("🔄 Attempting fallback tree generation...")
            generator = EnhancedDirectoryTreeGenerator()
            tree_output, _ = generator.generate_tree(
                root_path=root_path, include_stats=False, include_file_info=False
            )
            print("\n" + tree_output)
            print_success("✅ Fallback tree generation completed!")
        except Exception as fallback_error:
            print_error(f"❌ Fallback also failed: {fallback_error}")
            print_info("💡 The directory may contain files that cannot be accessed.")


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
        print("1. Console (display only)")
        print("2. Markdown file")
        print("3. JSON file")
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

        # Generate tree
        output, stats = generate_directory_tree(
            root_path=root_path,
            ignore_patterns=ignore_patterns,
            max_depth=max_depth,
            include_stats=include_stats,
            include_file_info=include_file_info,
            output_format=output_format,
        )

        # Display results
        if output_format == "console":
            print("\n" + output)

        print_success("✅ Advanced tree generation completed!")

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
                output, stats = generate_directory_tree(
                    root_path=path,
                    output_format=output_format,
                    include_stats=include_stats,
                    include_file_info=include_file_info,
                )
                successful += 1
                print_success(f"✅ Completed: {path}")
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

        generator = EnhancedDirectoryTreeGenerator()
        tree_output, stats = generator.generate_tree(
            root_path=root_path, include_stats=True, include_file_info=True
        )

        # Display statistics
        print("\n" + generator.generate_statistics_report(stats))
        print_success("✅ Statistics analysis completed!")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during statistics analysis: {e}")


def compare_directories():
    """Compare statistics between multiple directories."""
    print_header("🔍 Directory Comparison", color=Mocha.sapphire)

    try:
        # Get directories to compare
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

        # Analyze each directory
        results = []
        generator = EnhancedDirectoryTreeGenerator()

        for path in paths:
            try:
                tree_output, stats = generator.generate_tree(
                    root_path=path, include_stats=True, include_file_info=False
                )
                results.append((path, stats))
                print_success(f"✅ Analyzed: {path}")
            except Exception as e:
                print_error(f"❌ Failed to analyze {path}: {e}")

        if not results:
            print_error("❌ No directories could be analyzed.")
            return

        # Display comparison
        print("\n" + "=" * 60)
        print("📊 Directory Comparison Results")
        print("=" * 60)

        for path, stats in results:
            print(f"\n📁 {os.path.basename(path)} ({path})")
            print(f"  📄 Files: {stats['total_files']}")
            print(f"  📁 Directories: {stats['total_dirs']}")
            print(f"  💾 Size: {generator.format_file_size(stats['total_size'])}")

            if stats["file_types"]:
                top_types = sorted(
                    stats["file_types"].items(), key=lambda x: x[1], reverse=True
                )[:3]
                print(
                    f"  📋 Top file types: {', '.join([f'{t[0]}({t[1]})' for t in top_types])}"
                )

        print_success("\n✅ Directory comparison completed!")

    except KeyboardInterrupt:
        print_warning("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print_error(f"❌ Error during directory comparison: {e}")
