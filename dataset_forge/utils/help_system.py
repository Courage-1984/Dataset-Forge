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

    # Menu-specific help content
    MENU_HELP = {
        "Main Menu": {
            "description": "Main navigation hub for all Dataset Forge features",
            "categories": [
                "📂 Dataset Management - Create, organize, and manage datasets",
                "🔍 Analysis & Validation - Analyze dataset quality and validate pairs",
                "✨ Image Processing & Augmentation - Transform and enhance images",
                "🚀 Training & Inference - ML model training and inference",
                "🛠️ Utilities - Various utility functions and tools",
                "⚙️ System & Settings - Configure system settings and preferences",
                "🔗 Links - External resources and documentation",
                "🩺 System Monitoring & Health - Monitor system performance",
                "🗂️ Enhanced Metadata Management - Advanced metadata handling",
                "🚀 Performance Optimization - Optimize processing performance",
            ],
            "tips": [
                "Start with Dataset Management if you're new to Dataset Forge",
                "Use Analysis & Validation to check your dataset quality",
                "System Monitoring helps track resource usage during processing",
            ],
        },
        "Dataset Management": {
            "description": "Comprehensive dataset creation, organization, and management tools",
            "categories": [
                "🎯 Create Dataset from Source - Build datasets from various sources",
                "🔗 Combine or Split Datasets - Merge or separate existing datasets",
                "🔗 Manage HQ/LQ Pairs - Handle high/low quality image pairs",
                "🧹 Clean & Organize - Remove duplicates and organize files",
                "🧭 Align Images - Batch projective alignment for image pairs",
                "🩺 Dataset Health Scoring - Assess dataset quality metrics",
                "🐸 Umzi's Dataset Preprocessing - Advanced preprocessing tools",
            ],
            "tips": [
                "Use Create Dataset for building new datasets from scratch",
                "Clean & Organize is essential for removing duplicates",
                "Dataset Health Scoring helps identify quality issues",
            ],
        },
        "Analysis & Validation": {
            "description": "Analyze dataset quality and validate image pairs",
            "categories": [
                "📊 Dataset Analysis - Comprehensive dataset statistics",
                "✅ Pair Validation - Validate HQ/LQ image pairs",
                "🔍 Quality Assessment - Assess image quality metrics",
                "📈 Performance Metrics - Calculate processing performance",
            ],
            "tips": [
                "Run analysis before processing to understand your dataset",
                "Pair validation ensures your HQ/LQ pairs are correctly matched",
                "Quality assessment helps identify problematic images",
            ],
        },
        "Image Processing & Augmentation": {
            "description": "Transform, enhance, and augment images for ML training",
            "categories": [
                "🔄 Image Transformations - Apply various image transformations",
                "✨ Augmentation - Generate augmented training data",
                "🎨 Color Adjustments - Modify color properties",
                "📐 Geometric Operations - Resize, crop, and align images",
            ],
            "tips": [
                "Augmentation helps increase your training dataset size",
                "Color adjustments can improve model robustness",
                "Geometric operations ensure consistent image dimensions",
            ],
        },
    }

    # Feature-specific help content
    FEATURE_HELP = {
        "help": {
            "description": "Show context-aware help information",
            "usage": "Type 'help', 'h', or '?' in any menu",
            "examples": [
                "help - Show full help for current menu",
                "h - Short form of help",
                "? - Alternative help command",
            ],
        },
        "quit": {
            "description": "Exit Dataset Forge completely with cleanup",
            "usage": "Type 'quit', 'exit', or 'q' in any menu",
            "examples": [
                "quit - Exit with cleanup",
                "exit - Alternative exit command",
                "q - Short form of quit",
            ],
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

        # Show menu context if provided
        if menu_context:
            print_info(f"\n📍 Menu Context:")
            for key, value in menu_context.items():
                print_info(f"  {Mocha.yellow}{key}{Mocha.reset}: {value}")

        # Show global commands
        cls._show_global_commands()

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

            if "notes" in feature_help:
                print_info(f"\n💡 Notes:")
                for note in feature_help["notes"]:
                    print_info(f"  {Mocha.green}•{Mocha.reset} {note}")
        else:
            print_warning(f"No help available for feature: {feature_name}")

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

        print_success(f"\n✨ Happy dataset processing!")
        if pause:
            input(f"\n{Mocha.lavender}Press Enter to continue...{Mocha.reset}")

    @classmethod
    def _show_global_commands(cls) -> None:
        """Show global commands that work in any menu."""
        print_info(f"\n🌐 Global Commands:")
        print_info(f"  {Mocha.green}help{Mocha.reset}     - Show this help information")
        print_info(f"  {Mocha.green}quit{Mocha.reset}     - Exit Dataset Forge completely")
        print_info(f"  {Mocha.green}0{Mocha.reset}        - Go back to previous menu")
        print_info(f"  {Mocha.green}Ctrl+C{Mocha.reset}   - Emergency exit with cleanup")


def show_help(help_type: str = "general", pause: bool = True, **kwargs) -> None:
    """Show help information based on type.

    Args:
        help_type: Type of help to show ("general", "menu", "feature")
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
    else:
        HelpSystem.show_quick_reference(pause)
