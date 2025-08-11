"""Comprehensive help system for Dataset Forge CLI."""

from typing import Dict, Any, Optional, List
from .printing import (
    print_header,
    print_info,
    print_success,
    print_warning,
    print_error,
)
from .color import Mocha


class HelpSystem:
    """Centralized help system for Dataset Forge."""

    # Menu-specific help content with enhanced descriptions
    MENU_HELP = {
        "Main Menu": {
            "description": "Main navigation hub for all Dataset Forge features - your command center for image dataset management",
            "categories": [
                "📂 Dataset Management - Create, organize, and manage your image datasets from scratch",
                "✨ Image Processing & Augmentation - Transform, enhance, and augment images for machine learning",
                "🔍 Analysis & Validation - Assess dataset quality, find issues, and validate your data",
                "🛠️ Utilities - Helper tools for comparison, compression, deduplication, and more",
                "🚀 Training & Inference - ML model training and inference workflows",
                "⚙️ System & Settings - Configure system settings, paths, and preferences",
                "🔗 Links - External resources, documentation, and community links",
                "🩺 System Monitoring & Health - Monitor system performance and resource usage",
                "🗂️ Enhanced Metadata Management - Advanced metadata handling and manipulation",
                "🚀 Performance Optimization - Optimize processing performance and efficiency",
            ],
            "tips": [
                "🎯 Start with Dataset Management to build your first dataset from existing images",
                "✨ Use Image Processing for common transformations and augmentations",
                "🔍 Run Analysis & Validation to check dataset quality before processing",
                "🛠️ Explore Utilities for helpful tools like deduplication and compression",
                "⚙️ Configure Settings to set up paths and preferences for your workflow",
            ],
            "workflows": [
                "🆕 New User: 1 → 4 → 6 → 8 (Create dataset → Clean → Analyze → Monitor)",
                "🔄 Regular Workflow: 1 → 2 → 3 → 4 (Manage → Process → Analyze → Utilities)",
                "⚡ Quick Processing: 2 → 4 → 8 (Process → Utilities → Monitor)",
                "🔧 Setup: 6 → 8 → 9 (Settings → Monitor → Metadata)",
            ],
        },
        "Dataset Management": {
            "description": "Comprehensive dataset creation, organization, and management tools - build and maintain your image datasets",
            "categories": [
                "📁 Dataset Creation - Build datasets from various sources (folders, videos, images)",
                "🔄 Dataset Operations - Combine multiple datasets or split existing ones into subsets",
                "🔗 HQ/LQ Management - Handle high-quality and low-quality image pairs for super-resolution",
                "🧹 Dataset Cleanup - Remove duplicates, organize files, and maintain dataset hygiene",
                "🎯 Image Alignment - Batch projective alignment for image pairs and sequences",
                "📊 Dataset Analysis - Assess dataset quality, health, and characteristics",
                "⚡ Advanced Preprocessing - Umzi's specialized preprocessing tools for ML workflows",
            ],
            "tips": [
                "🎯 Start with Dataset Creation to build your first dataset from existing images",
                "🔄 Use Dataset Operations to merge multiple datasets or create training/validation splits",
                "🔗 HQ/LQ Management is essential for super-resolution and image restoration tasks",
                "🧹 Always run Dataset Cleanup to remove duplicates and organize your data",
                "🎯 Image Alignment helps ensure consistent positioning across image pairs",
                "📊 Use Dataset Analysis to identify quality issues before training models",
                "⚡ Advanced Preprocessing provides specialized tools for specific ML tasks",
            ],
            "workflows": [
                "🆕 New Dataset: 1 → 4 → 6 (Create → Clean → Analyze)",
                "🔄 Merge Datasets: 2 → 4 → 6 (Combine → Clean → Analyze)",
                "🔗 HQ/LQ Setup: 3 → 5 → 6 (Create pairs → Align → Analyze)",
                "⚡ Advanced: 7 → 6 → 4 (Preprocess → Analyze → Clean)",
            ],
            "examples": [
                "📁 New dataset: 1 → Create from folder → Select source → Choose output location",
                "🔄 Merge datasets: 2 → Combine datasets → Select folders → Choose merge strategy",
                "🔗 HQ/LQ pairs: 3 → Create pairs → Set HQ folder → Set LQ folder → Validate pairs",
                "🧹 Clean dataset: 4 → Remove duplicates → Choose method → Review results",
                "🎯 Align images: 5 → Select pairs → Choose alignment method → Process batch",
                "📊 Analyze quality: 6 → Run health check → Review metrics → Fix issues",
            ],
        },
        "Image Processing & Augmentation": {
            "description": "Transform, enhance, and augment images for machine learning training and preprocessing",
            "categories": [
                "🔄 Geometric Transformations - Resize, crop, rotate, and apply geometric operations",
                "🎨 Color & Tone Adjustments - Modify brightness, contrast, saturation, and color balance",
                "✨ Image Augmentation - Generate augmented training data with various transformations",
                "📋 Metadata Management - Handle EXIF data, ICC profiles, and image metadata",
                "✏️ Sketch Extraction - Extract sketches and line art from images",
            ],
            "tips": [
                "🔄 Start with Geometric Transformations to ensure consistent image dimensions",
                "🎨 Use Color Adjustments to improve model robustness and training stability",
                "✨ Augmentation helps increase your training dataset size and variety",
                "📋 Metadata Management ensures clean, standardized image files",
                "✏️ Sketch Extraction is useful for specialized ML tasks and artistic applications",
            ],
            "workflows": [
                "🆕 Basic Processing: 1 → 2 → 4 (Transform → Color → Metadata)",
                "✨ Augmentation Workflow: 3 → 1 → 2 (Augment → Transform → Color)",
                "🎨 Color Focus: 2 → 4 → 1 (Color → Metadata → Transform)",
                "✏️ Sketch Workflow: 5 → 1 → 4 (Extract → Transform → Metadata)",
            ],
        },
        "Utilities": {
            "description": "Helper tools and utilities for dataset management and analysis - essential tools for maintaining and optimizing your datasets",
            "categories": [
                "🔍 Comparison Tools - Compare folders and analyze differences between datasets",
                "🖼️ Visual Comparisons - Create side-by-side comparison images for quality assessment",
                "🎬 GIF Comparisons - Generate animated comparison GIFs for dynamic analysis",
                "🔍 Consolidated De-duplication - Comprehensive duplicate detection and removal",
                "🗜️ Consolidated Compression - Compress individual images and directories",
                "🧹 Sanitization Tools - Clean and sanitize image files",
                "🌳 Directory Tools - Enhanced directory tree visualization",
                "📁 File Filtering - Filter and manage non-image files",
            ],
            "tips": [
                "🔍 Comparison tools help identify differences between datasets",
                "🖼️ Visual comparisons are great for quality assessment",
                "🔍 Consolidated De-duplication combines all duplicate detection methods",
                "🗜️ Consolidated Compression handles both individual and batch compression",
                "🧹 Sanitization tools ensure image file integrity",
                "🌳 Directory tools provide detailed folder structure analysis",
            ],
            "workflows": [
                "🔍 Quality Check: 1 → 2 → 3 (Compare → Visual → GIF)",
                "🧹 Cleanup: 4 → 5 → 6 (Dedupe → Compress → Sanitize)",
                "📁 Organization: 7 → 8 → 1 (Directory → Filter → Compare)",
                "⚡ Quick Analysis: 2 → 4 → 5 (Visual → Dedupe → Compress)",
            ],
        },
    }

    # Enhanced feature-specific help content
    FEATURE_HELP = {
        "help": {
            "description": "Show context-aware help information for the current menu or feature",
            "usage": "Type 'help', 'h', or '?' in any menu",
            "examples": [
                "help - Show full help for current menu",
                "h - Short form of help",
                "? - Alternative help command",
                "help feature - Show help for specific feature",
            ],
            "notes": [
                "Help is context-aware and shows information relevant to your current menu",
                "Use help anytime you're unsure about what an option does",
                "Help includes examples, tips, and workflow guidance",
            ],
        },
        "quit": {
            "description": "Exit Dataset Forge completely with proper cleanup and resource management",
            "usage": "Type 'quit', 'exit', or 'q' in any menu",
            "examples": [
                "quit - Exit with cleanup",
                "exit - Alternative exit command",
                "q - Short form of quit",
                "Ctrl+C - Emergency exit with cleanup",
            ],
            "notes": [
                "Always use quit to ensure proper cleanup of resources",
                "Ctrl+C works as emergency exit from any operation",
                "Your work is automatically saved before exit",
            ],
        },
        "deduplication": {
            "description": "Find and remove duplicate images using multiple advanced algorithms",
            "usage": "Navigate to Utilities → Consolidated De-duplication",
            "examples": [
                "🔍 Fuzzy Matching - Multi-algorithm fuzzy matching with configurable thresholds",
                "👁️ Visual Detection - CLIP/LPIPS based semantic duplicate detection",
                "🔐 File Hash - Perceptual hash based exact/near-duplicate detection",
                "🔍 ImageDedup Pro - Professional duplicate detection with advanced features",
            ],
            "tips": [
                "Start with Fuzzy Matching for comprehensive duplicate detection",
                "Use Visual Detection for semantic similarity (content-based)",
                "Use File Hash for fast exact/near-duplicate detection",
                "Always test with dry run before destructive operations",
                "Configure thresholds based on your dataset characteristics",
            ],
            "workflows": [
                "🔍 Conservative: Fuzzy (90%) → Visual (0.98) → File Hash (95%)",
                "⚡ Fast: File Hash (90%) → Fuzzy (85%) → Review results",
                "🎯 Accurate: Visual (0.95) → Fuzzy (95%) → ImageDedup Pro",
                "🧹 Cleanup: Show → Copy → Review → Move/Delete",
            ],
        },
        "compression": {
            "description": "Compress images and directories to reduce file sizes while maintaining quality",
            "usage": "Navigate to Utilities → Consolidated Compression",
            "examples": [
                "🖼️ Individual Image Compression - Compress individual images with format options",
                "📁 Directory Compression - Compress entire directories and folders",
                "⚙️ Compression Settings - Configure quality, format, and advanced options",
            ],
            "tips": [
                "Individual compression is best for selective image optimization",
                "Directory compression processes entire folders efficiently",
                "PNG offers lossless compression with Oxipng support",
                "JPEG and WebP provide lossy compression with quality control",
                "Always backup original files before compression",
                "Use appropriate quality settings for your use case",
            ],
            "workflows": [
                "🖼️ Selective: Individual → Choose files → Set quality → Compress",
                "📁 Batch: Directory → Select folder → Set format → Process all",
                "⚙️ Optimized: Settings → Configure → Individual/Directory → Execute",
                "🔄 Format Conversion: Individual → Choose format → Set quality → Convert",
            ],
        },
    }

    # Troubleshooting guide
    TROUBLESHOOTING = {
        "common_issues": {
            "Memory Errors": {
                "symptoms": ["Out of memory", "CUDA memory error", "Process killed"],
                "solutions": [
                    "Reduce batch size in settings",
                    "Use CPU processing instead of GPU",
                    "Process smaller chunks of data",
                    "Clear system memory before processing",
                ],
            },
            "File Not Found": {
                "symptoms": [
                    "File not found",
                    "Path does not exist",
                    "Permission denied",
                ],
                "solutions": [
                    "Check file paths are correct",
                    "Ensure files exist in specified locations",
                    "Verify file permissions",
                    "Use absolute paths if needed",
                ],
            },
            "Slow Processing": {
                "symptoms": [
                    "Very slow operations",
                    "Hanging processes",
                    "No progress",
                ],
                "solutions": [
                    "Reduce batch size or chunk size",
                    "Use fewer parallel workers",
                    "Check system resources",
                    "Use CPU instead of GPU for large datasets",
                ],
            },
            "Quality Issues": {
                "symptoms": [
                    "Poor image quality",
                    "Compression artifacts",
                    "Blurry results",
                ],
                "solutions": [
                    "Increase quality settings",
                    "Use lossless compression",
                    "Check source image quality",
                    "Adjust processing parameters",
                ],
            },
        },
        "error_codes": {
            "E001": "File not found - Check file path and permissions",
            "E002": "Memory error - Reduce batch size or use CPU processing",
            "E003": "Invalid format - Check file format and try different format",
            "E004": "Permission denied - Check file permissions and access rights",
            "E005": "Network error - Check internet connection and try again",
        },
    }

    @classmethod
    def show_menu_help(
        cls,
        menu_name: str,
        menu_context: Optional[Dict[str, Any]] = None,
        pause: bool = True,
    ) -> None:
        """Show context-aware help for a specific menu.

        Args:
            menu_name: Name of the menu to show help for
            menu_context: Optional context information
            pause: If True, prompt for Enter at the end
        """
        print_header(f"🎯 Help: {menu_name}", char="=", color=Mocha.mauve)

        # Get menu-specific help
        menu_help = cls.MENU_HELP.get(menu_name, {})

        if menu_help:
            print_info(
                f"📝 {menu_help.get('description', 'Menu description not available')}"
            )

            if "categories" in menu_help:
                print_info(f"\n📋 Available Options:")
                for category in menu_help["categories"]:
                    print_info(f"  {Mocha.blue}•{Mocha.reset} {category}")

            if "tips" in menu_help:
                print_info(f"\n💡 Tips:")
                for tip in menu_help["tips"]:
                    print_info(f"  {Mocha.green}•{Mocha.reset} {tip}")

            if "workflows" in menu_help:
                print_info(f"\n🔄 Common Workflows:")
                for workflow in menu_help["workflows"]:
                    print_info(f"  {Mocha.yellow}•{Mocha.reset} {workflow}")

            if "examples" in menu_help:
                print_info(f"\n📝 Usage Examples:")
                for example in menu_help["examples"]:
                    print_info(f"  {Mocha.mauve}•{Mocha.reset} {example}")

        # Show menu context if provided
        if menu_context:
            print_info(f"\n📍 Menu Context:")
            for key, value in menu_context.items():
                if isinstance(value, list):
                    print_info(f"  {Mocha.yellow}{key}{Mocha.reset}:")
                    for item in value:
                        print_info(f"    • {item}")
                else:
                    print_info(f"  {Mocha.yellow}{key}{Mocha.reset}: {value}")

        # Show global commands
        cls._show_global_commands()

        # Show quick troubleshooting
        cls._show_quick_troubleshooting()

        print_success(f"\n✨ Ready to use {menu_name}!")
        if pause:
            input(f"\n{Mocha.lavender}Press Enter to continue...{Mocha.reset}")

    @classmethod
    def show_feature_help(cls, feature_name: str, pause: bool = True) -> None:
        """Show help for a specific feature.

        Args:
            feature_name: Name of the feature to show help for
            pause: If True, prompt for Enter at the end
        """
        print_header(
            f"🎯 Feature Help: {feature_name.title()}", char="=", color=Mocha.mauve
        )

        feature_help = cls.FEATURE_HELP.get(feature_name.lower(), {})

        if feature_help:
            print_info(
                f"📝 {feature_help.get('description', 'Feature description not available')}"
            )

            if "usage" in feature_help:
                print_info(f"\n🔧 Usage: {feature_help['usage']}")

            if "examples" in feature_help:
                print_info(f"\n📝 Examples:")
                for example in feature_help["examples"]:
                    print_info(f"  {Mocha.blue}•{Mocha.reset} {example}")

            if "tips" in feature_help:
                print_info(f"\n💡 Tips:")
                for tip in feature_help["tips"]:
                    print_info(f"  {Mocha.green}•{Mocha.reset} {tip}")

            if "workflows" in feature_help:
                print_info(f"\n🔄 Workflows:")
                for workflow in feature_help["workflows"]:
                    print_info(f"  {Mocha.yellow}•{Mocha.reset} {workflow}")

            if "notes" in feature_help:
                print_info(f"\n📋 Notes:")
                for note in feature_help["notes"]:
                    print_info(f"  {Mocha.mauve}•{Mocha.reset} {note}")
        else:
            print_warning(f"No help available for feature: {feature_name}")

        if pause:
            input(f"\n{Mocha.lavender}Press Enter to continue...{Mocha.reset}")

    @classmethod
    def show_troubleshooting_help(
        cls, issue_type: str = "general", pause: bool = True
    ) -> None:
        """Show troubleshooting help for common issues.

        Args:
            issue_type: Type of issue ("general", "memory", "files", "performance", "quality")
            pause: If True, prompt for Enter at the end
        """
        print_header("🔧 Troubleshooting Guide", char="=", color=Mocha.mauve)

        if issue_type == "general":
            print_info("🚨 Common Issues and Solutions:")

            for issue, details in cls.TROUBLESHOOTING["common_issues"].items():
                print_info(f"\n{Mocha.red}• {issue}{Mocha.reset}")
                print_info(f"  Symptoms: {', '.join(details['symptoms'])}")
                print_info(f"  Solutions:")
                for solution in details["solutions"]:
                    print_info(f"    - {solution}")

            print_info(f"\n{Mocha.yellow}Error Codes:{Mocha.reset}")
            for code, description in cls.TROUBLESHOOTING["error_codes"].items():
                print_info(f"  {code}: {description}")

        elif issue_type in cls.TROUBLESHOOTING["common_issues"]:
            details = cls.TROUBLESHOOTING["common_issues"][issue_type]
            print_info(f"\n{Mocha.red}Issue: {issue_type}{Mocha.reset}")
            print_info(f"Symptoms: {', '.join(details['symptoms'])}")
            print_info(f"Solutions:")
            for solution in details["solutions"]:
                print_info(f"  • {solution}")

        print_info(f"\n💡 Need more help?")
        print_info("  • Check the documentation at docs/")
        print_info("  • Review error logs in logs/")
        print_info("  • Use System Monitoring to check resources")

        if pause:
            input(f"\n{Mocha.lavender}Press Enter to continue...{Mocha.reset}")

    @classmethod
    def show_quick_reference(cls, pause: bool = True) -> None:
        """Show a quick reference guide for common commands."""
        print_header("📚 Quick Reference Guide", char="=", color=Mocha.mauve)

        print_info("🚀 Essential Commands:")
        print_info(f"  {Mocha.green}help{Mocha.reset}     - Show help for current menu")
        print_info(f"  {Mocha.green}quit{Mocha.reset}     - Exit Dataset Forge")
        print_info(f"  {Mocha.green}0{Mocha.reset}        - Go back to previous menu")
        print_info(f"  {Mocha.green}Ctrl+C{Mocha.reset}   - Emergency exit")

        print_info(f"\n🎯 Navigation:")
        print_info("  • Use number keys (1, 2, 3...) to select options")
        print_info("  • Use '0' to go back to previous menu")
        print_info("  • Use 'help' anytime for context-aware assistance")

        print_info(f"\n💡 Pro Tips:")
        print_info("  • Commands are case-insensitive")
        print_info("  • You can use 'help' in any menu")
        print_info("  • 'quit' works from any menu level")
        print_info("  • Use Ctrl+C for emergency exit with cleanup")

        print_info(f"\n🔄 Common Workflows:")
        print_info("  • New dataset: Dataset Management → Create → Clean → Analyze")
        print_info(
            "  • Image processing: Image Processing → Transform → Augment → Metadata"
        )
        print_info(
            "  • Quality check: Utilities → Comparison → Deduplication → Compression"
        )

        print_success(f"\n✨ Happy dataset processing!")
        if pause:
            input(f"\n{Mocha.lavender}Press Enter to continue...{Mocha.reset}")

    @classmethod
    def _show_global_commands(cls) -> None:
        """Show global commands that work in any menu."""
        print_info(f"\n🌐 Global Commands:")
        print_info(f"  {Mocha.green}help{Mocha.reset}     - Show this help information")
        print_info(
            f"  {Mocha.green}quit{Mocha.reset}     - Exit Dataset Forge completely"
        )
        print_info(f"  {Mocha.green}0{Mocha.reset}        - Go back to previous menu")
        print_info(
            f"  {Mocha.green}Ctrl+C{Mocha.reset}   - Emergency exit with cleanup"
        )

    @classmethod
    def _show_quick_troubleshooting(cls) -> None:
        """Show quick troubleshooting tips."""
        print_info(f"\n🔧 Quick Troubleshooting:")
        print_info("  • Memory issues? Reduce batch size or use CPU processing")
        print_info("  • File not found? Check paths and permissions")
        print_info("  • Slow processing? Reduce workers or chunk size")
        print_info("  • Need more help? Type 'help troubleshooting'")


def show_help(help_type: str = "general", pause: bool = True, **kwargs) -> None:
    """Show help information based on type.

    Args:
        help_type: Type of help to show ("general", "menu", "feature", "troubleshooting")
        pause: If True, prompt for Enter at the end
        **kwargs: Additional arguments for specific help types
    """
    if help_type == "menu":
        menu_name = kwargs.get("menu_name", "Unknown Menu")
        menu_context = kwargs.get("menu_context")
        HelpSystem.show_menu_help(menu_name, menu_context, pause)
    elif help_type == "feature":
        feature_name = kwargs.get("feature_name", "Unknown Feature")
        HelpSystem.show_feature_help(feature_name, pause)
    elif help_type == "troubleshooting":
        issue_type = kwargs.get("issue_type", "general")
        HelpSystem.show_troubleshooting_help(issue_type, pause)
    else:
        HelpSystem.show_quick_reference(pause)
