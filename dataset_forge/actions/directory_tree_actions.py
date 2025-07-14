"""
Enhanced Directory Tree Generator for Dataset Forge.

This module provides advanced directory tree generation with emoji categorization,
file type detection, and integration with Dataset Forge's architecture.
"""

import os
import pathlib
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
import json

# Import Dataset Forge utilities
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_header,
)
from dataset_forge.utils.memory_utils import (
    memory_context,
    auto_cleanup,
    clear_memory,
    clear_cuda_cache,
)
from dataset_forge.utils.file_utils import is_image_file
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.audio_utils import play_done_sound

# Try to import magic, but provide fallback
try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    magic = None
    MAGIC_AVAILABLE = False


class EnhancedDirectoryTreeGenerator:
    """
    Enhanced directory tree generator with advanced features.

    Features:
    - Emoji categorization for different file types
    - Advanced file type detection using python-magic (with fallback)
    - Dataset Forge integration (memory management, progress tracking)
    - Multiple output formats (console, markdown, JSON)
    - Statistics and analysis
    - Customizable ignore patterns
    - File size and metadata information
    """

    def __init__(self):
        """Initialize the directory tree generator with enhanced categories."""
        # Enhanced categories with more specific emojis
        self.categories = {
            "directory": "📁",
            "image": "🖼️",
            "image_hq": "🖼️✨",  # High-quality images
            "image_lq": "🖼️📉",  # Low-quality images
            "audio": "🎵",
            "video": "🎬",
            "document": "📄",
            "document_pdf": "📄📋",
            "executable": "⚙️",
            "archive": "📦",
            "code": "📝",
            "code_python": "🐍",
            "code_js": "📜",
            "code_html": "🌐",
            "data": "📊",
            "data_json": "📊🔧",
            "data_csv": "📊📈",
            "web": "🌐",
            "3d": "💠",
            "font": "🔤",
            "model": "🤖",  # ML models
            "config": "⚙️📋",  # Configuration files
            "log": "📋📝",  # Log files
            "backup": "💾",
            "temp": "🗑️",
            "other": "📄",
        }

        # File type mappings for enhanced detection
        self.file_type_mappings = {
            # Images
            "image/jpeg": "image",
            "image/png": "image",
            "image/gif": "image",
            "image/webp": "image",
            "image/bmp": "image",
            "image/tiff": "image",
            "image/svg+xml": "image",
            # Audio
            "audio/mpeg": "audio",
            "audio/wav": "audio",
            "audio/flac": "audio",
            "audio/ogg": "audio",
            "audio/aac": "audio",
            # Video
            "video/mp4": "video",
            "video/avi": "video",
            "video/mov": "video",
            "video/wmv": "video",
            "video/flv": "video",
            "video/webm": "video",
            # Documents
            "application/pdf": "document_pdf",
            "text/plain": "document",
            "text/markdown": "document",
            "application/msword": "document",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
            # Archives
            "application/zip": "archive",
            "application/x-rar-compressed": "archive",
            "application/x-tar": "archive",
            "application/gzip": "archive",
            "application/x-7z-compressed": "archive",
            # Code
            "text/x-python": "code_python",
            "text/javascript": "code_js",
            "text/html": "code_html",
            "text/css": "code",
            "text/xml": "code",
            "application/json": "data_json",
            "text/csv": "data_csv",
            # Models and ML
            "application/octet-stream": "model",  # Often used for model files
        }

        # Statistics tracking
        self.stats = {
            "total_files": 0,
            "total_dirs": 0,
            "total_size": 0,
            "file_types": {},
            "largest_files": [],
            "recent_files": [],
        }

    def get_file_emoji(self, file_path: str) -> str:
        """
        Get the appropriate emoji for a file based on its type.

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
                return self.categories["code_python"]
            elif filename.endswith((".js", ".jsx")):
                return self.categories["code_js"]
            elif filename.endswith((".html", ".htm")):
                return self.categories["code_html"]
            elif filename.endswith((".json")):
                return self.categories["data_json"]
            elif filename.endswith((".csv")):
                return self.categories["data_csv"]
            elif filename.endswith((".pth", ".safetensors", ".onnx", ".pb")):
                return self.categories["model"]
            elif filename.endswith((".yml", ".yaml", ".ini", ".cfg", ".conf")):
                return self.categories["config"]
            elif filename.endswith((".log")):
                return self.categories["log"]
            elif filename.endswith((".bak", ".backup")):
                return self.categories["backup"]
            elif filename.endswith((".tmp", ".temp")):
                return self.categories["temp"]
            elif filename.endswith((".pdf")):
                return self.categories["document_pdf"]
            elif filename.endswith((".zip", ".rar", ".tar", ".gz", ".7z")):
                return self.categories["archive"]
            elif filename.endswith((".mp3", ".wav", ".flac", ".ogg", ".aac")):
                return self.categories["audio"]
            elif filename.endswith((".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm")):
                return self.categories["video"]
            elif filename.endswith((".ttf", ".otf", ".woff", ".woff2")):
                return self.categories["font"]
            elif is_image_file(filename):
                # Check if it's HQ or LQ based on size or naming convention
                try:
                    # Use a safer approach to get file size
                    if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                        file_size = os.path.getsize(file_path)
                        if file_size > 1024 * 1024:  # > 1MB
                            return self.categories["image_hq"]
                        else:
                            return self.categories["image_lq"]
                    else:
                        return self.categories["image"]
                except (OSError, PermissionError, FileNotFoundError):
                    return self.categories["image"]

            # Use magic if available for more accurate detection
            if MAGIC_AVAILABLE and magic:
                try:
                    if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                        mime_type = magic.from_file(file_path, mime=True)

                        # Check if it's a known type
                        if mime_type in self.file_type_mappings:
                            category = self.file_type_mappings[mime_type]
                            return self.categories.get(
                                category, self.categories["other"]
                            )

                        # Fallback to MIME type detection
                        if mime_type.startswith("image"):
                            return self.categories["image"]
                        elif mime_type.startswith("audio"):
                            return self.categories["audio"]
                        elif mime_type.startswith("video"):
                            return self.categories["video"]
                        elif mime_type.startswith("text"):
                            return self.categories["document"]
                        elif mime_type.startswith("application"):
                            return self.categories["other"]
                except Exception:
                    pass  # Silently fall back to extension-based detection

            # Final fallback
            return self.categories["other"]

        except Exception:
            # Ultimate fallback - return a safe default
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
