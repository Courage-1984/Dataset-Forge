#!/usr/bin/env python3
"""
Emoji Usage Checker for Dataset Forge

This tool analyzes emoji usage throughout the codebase to ensure:
- Proper Unicode encoding
- Valid emoji characters
- Consistent emoji usage patterns
- Integration with the emoji handling system
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataset_forge.utils.emoji_utils import (
    get_emoji_handler,
    normalize_unicode,
    is_valid_emoji,
    extract_emojis,
    sanitize_emoji,
    categorize_emoji,
    get_emoji_description,
)
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_section,
)
from dataset_forge.utils.color import Mocha


class EmojiUsageChecker:
    """Comprehensive emoji usage analysis and validation tool."""

    def __init__(self, project_root: Path):
        """Initialize the emoji checker."""
        self.project_root = project_root
        self.emoji_handler = get_emoji_handler()
        self.results = {
            "files_analyzed": 0,
            "total_emojis_found": 0,
            "valid_emojis": 0,
            "invalid_emojis": 0,
            "encoding_issues": 0,
            "files_with_issues": [],
            "emoji_categories": {},
            "menu_emoji_usage": {},
            "recommendations": [],
        }

        # File patterns to analyze
        self.file_patterns = ["*.py", "*.md", "*.txt", "*.json", "*.yaml", "*.yml"]

        # Directories to exclude
        self.exclude_dirs = {
            "__pycache__",
            ".git",
            "venv312",
            "node_modules",
            ".pytest_cache",
            "logs",
            "reports",
        }

    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the entire codebase for emoji usage."""
        print_info("🔍 Starting emoji usage analysis...")

        # Find all relevant files
        files_to_analyze = self._find_files()
        print_info(f"📁 Found {len(files_to_analyze)} files to analyze")

        # Analyze each file
        for file_path in files_to_analyze:
            self._analyze_file(file_path)

        # Generate recommendations
        self._generate_recommendations()

        return self.results

    def _find_files(self) -> List[Path]:
        """Find all files to analyze."""
        files = []

        for pattern in self.file_patterns:
            for file_path in self.project_root.rglob(pattern):
                # Skip excluded directories
                if any(exclude in file_path.parts for exclude in self.exclude_dirs):
                    continue

                # Skip binary files
                if self._is_binary_file(file_path):
                    continue

                files.append(file_path)

        return sorted(files)

    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary."""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                return b"\x00" in chunk
        except Exception:
            return True

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single file for emoji usage."""
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.results["files_analyzed"] += 1

            # Extract emojis from content
            emojis = extract_emojis(content)

            if not emojis:
                return

            file_issues = []
            file_emoji_count = 0

            # Analyze each emoji
            for emoji_char in emojis:
                self.results["total_emojis_found"] += 1
                file_emoji_count += 1

                # Validate emoji
                if is_valid_emoji(emoji_char):
                    self.results["valid_emojis"] += 1

                    # Categorize emoji
                    category = categorize_emoji(emoji_char)
                    self.results["emoji_categories"][category] = (
                        self.results["emoji_categories"].get(category, 0) + 1
                    )
                else:
                    self.results["invalid_emojis"] += 1
                    file_issues.append(f"Invalid emoji: {emoji_char}")

            # Check for encoding issues
            try:
                normalized = normalize_unicode(content)
                sanitized = sanitize_emoji(normalized)
                if normalized != sanitized:
                    self.results["encoding_issues"] += 1
                    file_issues.append("Unicode normalization issues detected")
            except Exception as e:
                self.results["encoding_issues"] += 1
                file_issues.append(f"Encoding error: {e}")

            # Check for menu emoji usage
            if file_path.suffix == ".py" and "menu" in file_path.name.lower():
                self._analyze_menu_emojis(file_path, content)

            # Record issues
            if file_issues:
                self.results["files_with_issues"].append(
                    {
                        "file": str(file_path.relative_to(self.project_root)),
                        "issues": file_issues,
                        "emoji_count": file_emoji_count,
                    }
                )

        except UnicodeDecodeError as e:
            self.results["encoding_issues"] += 1
            self.results["files_with_issues"].append(
                {
                    "file": str(file_path.relative_to(self.project_root)),
                    "issues": [f"Unicode decode error: {e}"],
                    "emoji_count": 0,
                }
            )
        except Exception as e:
            print_warning(f"⚠️  Error analyzing {file_path}: {e}")

    def _analyze_menu_emojis(self, file_path: Path, content: str) -> None:
        """Analyze emoji usage in menu files."""
        menu_name = file_path.stem

        # Extract menu options pattern
        menu_pattern = r"options\s*=\s*\{([^}]+)\}"
        matches = re.findall(menu_pattern, content, re.DOTALL)

        if matches:
            menu_emojis = extract_emojis(content)
            self.results["menu_emoji_usage"][menu_name] = {
                "emojis": menu_emojis,
                "count": len(menu_emojis),
                "categories": {},
            }

            # Categorize emojis in this menu
            for emoji_char in menu_emojis:
                if is_valid_emoji(emoji_char):
                    category = categorize_emoji(emoji_char)
                    self.results["menu_emoji_usage"][menu_name]["categories"][
                        category
                    ] = (
                        self.results["menu_emoji_usage"][menu_name]["categories"].get(
                            category, 0
                        )
                        + 1
                    )

    def _generate_recommendations(self) -> None:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check for invalid emojis
        if self.results["invalid_emojis"] > 0:
            recommendations.append(
                {
                    "type": "error",
                    "message": f"Found {self.results['invalid_emojis']} invalid emojis. Replace with valid Unicode emojis.",
                    "priority": "high",
                }
            )

        # Check for encoding issues
        if self.results["encoding_issues"] > 0:
            recommendations.append(
                {
                    "type": "warning",
                    "message": f"Found {self.results['encoding_issues']} encoding issues. Ensure proper UTF-8 encoding.",
                    "priority": "high",
                }
            )

        # Check emoji diversity
        if len(self.results["emoji_categories"]) < 3:
            recommendations.append(
                {
                    "type": "info",
                    "message": "Limited emoji diversity. Consider using more varied emoji categories.",
                    "priority": "low",
                }
            )

        # Check menu emoji consistency
        menu_files = [f for f in self.results["menu_emoji_usage"].keys()]
        if len(menu_files) > 1:
            # Check for consistency across menus
            all_menu_emojis = set()
            for menu_data in self.results["menu_emoji_usage"].values():
                all_menu_emojis.update(menu_data["emojis"])

            if len(all_menu_emojis) < len(menu_files) * 2:
                recommendations.append(
                    {
                        "type": "info",
                        "message": "Consider using more diverse emojis across different menus for better visual distinction.",
                        "priority": "medium",
                    }
                )

        self.results["recommendations"] = recommendations

    def print_report(self) -> None:
        """Print a comprehensive analysis report."""
        print_section("📊 Emoji Usage Analysis Report", "=", Mocha.lavender)

        # Summary statistics
        print_section("📈 Summary Statistics", "-", Mocha.sapphire)
        print_info(f"Files analyzed: {self.results['files_analyzed']}")
        print_info(f"Total emojis found: {self.results['total_emojis_found']}")
        print_info(f"Valid emojis: {self.results['valid_emojis']}")
        print_info(f"Invalid emojis: {self.results['invalid_emojis']}")
        print_info(f"Encoding issues: {self.results['encoding_issues']}")

        # Emoji categories
        if self.results["emoji_categories"]:
            print_section("🎨 Emoji Categories", "-", Mocha.sapphire)
            for category, count in sorted(
                self.results["emoji_categories"].items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                print_info(f"  {category.title()}: {count}")

        # Menu emoji usage
        if self.results["menu_emoji_usage"]:
            print_section("📋 Menu Emoji Usage", "-", Mocha.sapphire)
            for menu_name, data in self.results["menu_emoji_usage"].items():
                print_info(f"  {menu_name}: {data['count']} emojis")
                if data["categories"]:
                    categories_str = ", ".join(
                        [f"{cat}({count})" for cat, count in data["categories"].items()]
                    )
                    print_info(f"    Categories: {categories_str}")

        # Issues found
        if self.results["files_with_issues"]:
            print_section("⚠️ Issues Found", "-", Mocha.peach)
            for file_issue in self.results["files_with_issues"]:
                print_warning(f"  {file_issue['file']}:")
                for issue in file_issue["issues"]:
                    print_warning(f"    - {issue}")

        # Recommendations
        if self.results["recommendations"]:
            print_section("💡 Recommendations", "-", Mocha.green)
            for rec in self.results["recommendations"]:
                priority_color = (
                    Mocha.red
                    if rec["priority"] == "high"
                    else Mocha.peach if rec["priority"] == "medium" else Mocha.sky
                )
                print(
                    f"{priority_color}  [{rec['priority'].upper()}] {rec['message']}{Mocha.reset}"
                )

        print()
        print_success("✅ Emoji usage analysis completed!")

    def save_report(self, output_path: Path) -> None:
        """Save the analysis report to a JSON file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print_success(f"📄 Report saved to: {output_path}")
        except Exception as e:
            print_error(f"Failed to save report: {e}")


def main():
    """Main function for the emoji usage checker."""
    parser = argparse.ArgumentParser(
        description="Check emoji usage in Dataset Forge codebase"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="logs/emoji_usage_report.json",
        help="Output file for the report (default: logs/emoji_usage_report.json)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize checker
    checker = EmojiUsageChecker(project_root)

    # Run analysis
    results = checker.analyze_codebase()

    # Print report
    checker.print_report()

    # Save report
    checker.save_report(output_path)

    # Exit with appropriate code
    if results["invalid_emojis"] > 0 or results["encoding_issues"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
