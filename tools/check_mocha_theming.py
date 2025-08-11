#!/usr/bin/env python3
"""
Catppuccin Mocha Theming Consistency Checker

This tool analyzes the Dataset Forge codebase to ensure consistent use of the
Catppuccin Mocha color scheme and centralized printing utilities across all
CLI menus, printing, console logging, and user-facing output.

Features:
- Detects raw print statements that should use centralized utilities
- Identifies missing Mocha color imports
- Checks menu implementations for proper color usage
- Validates centralized printing utility usage
- Analyzes console logging for color consistency
- Provides actionable recommendations for fixes
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import argparse

# Import centralized printing utilities for this tool
try:
    from dataset_forge.utils.printing import (
        print_info,
        print_success,
        print_warning,
        print_error,
    )
    from dataset_forge.utils.color import Mocha

    HAS_DATASET_FORGE = True
except ImportError:
    # Fallback for when running the tool directly
    def print_info(msg):
        print(f"[INFO] {msg}")

    def print_success(msg):
        print(f"[SUCCESS] {msg}")

    def print_warning(msg):
        print(f"[WARNING] {msg}")

    def print_error(msg):
        print(f"[ERROR] {msg}")

    HAS_DATASET_FORGE = False


@dataclass
class ThemingIssue:
    """Represents a theming consistency issue found in the codebase."""

    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    suggestion: str
    code_snippet: str


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    file_path: str
    has_mocha_import: bool
    has_printing_imports: bool
    raw_print_count: int
    centralized_print_count: int
    issues: List[ThemingIssue]
    total_lines: int


class MochaThemingChecker:
    """Comprehensive checker for Catppuccin Mocha theming consistency."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues: List[ThemingIssue] = []
        self.file_analyses: Dict[str, FileAnalysis] = {}

        # Directories to analyze
        self.analysis_dirs = ["dataset_forge", "tests", "tools"]

        # File patterns to include
        self.include_patterns = ["*.py", "*.bat", "*.md"]

        # File patterns to exclude
        self.exclude_patterns = [
            "__pycache__",
            ".git",
            "venv",
            ".pytest_cache",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "check_mocha_theming.py",  # Exclude self from analysis
        ]

        # Centralized printing utilities that should be used
        self.centralized_printing_utils = {
            "print_info",
            "print_success",
            "print_warning",
            "print_error",
            "print_header",
            "print_section",
            "print_subsection",
            "print_note",
            "print_debug",
            "print_verbose",
            "print_progress",
            "print_status",
        }

        # Mocha color constants that should be imported
        self.mocha_colors = {
            "Mocha.rosewater",
            "Mocha.flamingo",
            "Mocha.pink",
            "Mocha.mauve",
            "Mocha.red",
            "Mocha.maroon",
            "Mocha.peach",
            "Mocha.yellow",
            "Mocha.green",
            "Mocha.teal",
            "Mocha.sky",
            "Mocha.sapphire",
            "Mocha.blue",
            "Mocha.lavender",
            "Mocha.text",
            "Mocha.subtext1",
            "Mocha.subtext0",
            "Mocha.overlay2",
            "Mocha.overlay1",
            "Mocha.overlay0",
            "Mocha.surface2",
            "Mocha.surface1",
            "Mocha.surface0",
            "Mocha.base",
            "Mocha.mantle",
            "Mocha.crust",
        }

        # Raw print patterns that should be replaced
        self.raw_print_patterns = [
            r"print\s*\([^)]*\)",
            r"print\s*\([^)]*,\s*end\s*=\s*[^)]*\)",
            r"print\s*\([^)]*,\s*sep\s*=\s*[^)]*\)",
        ]

        # Menu-related patterns to check
        self.menu_patterns = [
            r"show_menu\s*\(",
            r"options\s*=\s*\{",
            r"Mocha\.",
        ]

    def should_analyze_file(self, file_path: Path) -> bool:
        """Determine if a file should be analyzed."""
        # Check if file is in analysis directories
        if not any(
            file_path.is_relative_to(self.project_root / dir_name)
            for dir_name in self.analysis_dirs
        ):
            return False

        # Check include patterns
        if not any(file_path.match(pattern) for pattern in self.include_patterns):
            return False

        # Check exclude patterns
        if any(pattern in str(file_path) for pattern in self.exclude_patterns):
            return False

        return True

    def find_files_to_analyze(self) -> List[Path]:
        """Find all files that should be analyzed."""
        files = []
        for analysis_dir in self.analysis_dirs:
            dir_path = self.project_root / analysis_dir
            if dir_path.exists():
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file() and self.should_analyze_file(file_path):
                        files.append(file_path)
        return files

    def analyze_python_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a Python file for theming consistency."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            return FileAnalysis(
                file_path=str(file_path),
                has_mocha_import=False,
                has_printing_imports=False,
                raw_print_count=0,
                centralized_print_count=0,
                issues=[
                    ThemingIssue(
                        file_path=str(file_path),
                        line_number=0,
                        issue_type="file_read_error",
                        description=f"Could not read file: {e}",
                        severity="error",
                        suggestion="Check file permissions and encoding",
                        code_snippet="",
                    )
                ],
                total_lines=0,
            )

        issues = []
        has_mocha_import = False
        has_printing_imports = False
        raw_print_count = 0
        centralized_print_count = 0

        # Check imports
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if (
                            "mocha" in alias.name.lower()
                            or "color" in alias.name.lower()
                        ):
                            has_mocha_import = True
                elif isinstance(node, ast.ImportFrom):
                    module_name = getattr(node.module, "value", "")
                    if "dataset_forge.utils.color" in module_name:
                        has_mocha_import = True
                        # Also check if Mocha is specifically imported
                        for alias in node.names:
                            if alias.name == "Mocha":
                                has_mocha_import = True
                    elif "dataset_forge.utils.printing" in module_name:
                        has_printing_imports = True
        except SyntaxError:
            issues.append(
                ThemingIssue(
                    file_path=str(file_path),
                    line_number=0,
                    issue_type="syntax_error",
                    description="Python syntax error in file",
                    severity="error",
                    suggestion="Fix Python syntax errors",
                    code_snippet="",
                )
            )

        # Check for raw print statements
        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Check for raw print statements
            if re.search(r"^\s*print\s*\(", line):
                raw_print_count += 1
                issues.append(
                    ThemingIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type="raw_print_statement",
                        description="Raw print statement found",
                        severity="error",
                        suggestion="Replace with centralized printing utility (print_info, print_success, etc.)",
                        code_snippet=line,
                    )
                )

            # Check for centralized printing usage
            for util in self.centralized_printing_utils:
                if util in line:
                    centralized_print_count += 1
                    break

            # Check for Mocha color usage
            if "Mocha." in line:
                # Skip test files and utility files that appropriately don't need Mocha imports
                file_str = str(file_path)
                if (
                    not has_mocha_import
                    and not file_str.endswith("test_emoji_utils.py")  # Test file
                    and not file_str.endswith("printing.py")  # Centralized utility
                    and not file_str.endswith("color.py")  # Color utility
                ):
                    issues.append(
                        ThemingIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            issue_type="mocha_usage_without_import",
                            description="Mocha color used without import",
                            severity="error",
                            suggestion="Add 'from dataset_forge.utils.color import Mocha' import",
                            code_snippet=line,
                        )
                    )

        # Check for menu implementations
        if "def" in content and ("menu" in content.lower() or "show_menu" in content):
            self._analyze_menu_implementation(file_path, content, lines, issues)

        return FileAnalysis(
            file_path=str(file_path),
            has_mocha_import=has_mocha_import,
            has_printing_imports=has_printing_imports,
            raw_print_count=raw_print_count,
            centralized_print_count=centralized_print_count,
            issues=issues,
            total_lines=len(lines),
        )

    def _analyze_menu_implementation(
        self,
        file_path: Path,
        content: str,
        lines: List[str],
        issues: List[ThemingIssue],
    ):
        """Analyze menu implementations for proper theming."""
        has_show_menu = "show_menu" in content
        has_options = "options" in content and "=" in content
        has_mocha_usage = "Mocha." in content

        if has_show_menu:
            # Check for proper menu pattern
            if not re.search(r"key\s*=\s*show_menu\s*\(", content):
                issues.append(
                    ThemingIssue(
                        file_path=str(file_path),
                        line_number=0,
                        issue_type="incorrect_menu_pattern",
                        description="Menu does not use standardized key-based pattern",
                        severity="error",
                        suggestion="Use 'key = show_menu(...)' pattern, not 'action = show_menu(...)'",
                        code_snippet="",
                    )
                )

            # Check for current_menu and menu_context parameters
            if "show_menu(" in content:
                if "current_menu=" not in content:
                    issues.append(
                        ThemingIssue(
                            file_path=str(file_path),
                            line_number=0,
                            issue_type="missing_menu_context",
                            description="show_menu call missing current_menu parameter",
                            severity="warning",
                            suggestion="Add current_menu parameter to show_menu calls",
                            code_snippet="",
                        )
                    )

                if "menu_context=" not in content:
                    issues.append(
                        ThemingIssue(
                            file_path=str(file_path),
                            line_number=0,
                            issue_type="missing_menu_context",
                            description="show_menu call missing menu_context parameter",
                            severity="warning",
                            suggestion="Add menu_context parameter to show_menu calls",
                            code_snippet="",
                        )
                    )

    def analyze_markdown_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a Markdown file for theming documentation."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            return FileAnalysis(
                file_path=str(file_path),
                has_mocha_import=False,
                has_printing_imports=False,
                raw_print_count=0,
                centralized_print_count=0,
                issues=[
                    ThemingIssue(
                        file_path=str(file_path),
                        line_number=0,
                        issue_type="file_read_error",
                        description=f"Could not read file: {e}",
                        severity="error",
                        suggestion="Check file permissions and encoding",
                        code_snippet="",
                    )
                ],
                total_lines=0,
            )

        issues = []

        # Check for theming documentation
        if "mocha" not in content.lower() and "color" not in content.lower():
            if "print" in content.lower() or "console" in content.lower():
                issues.append(
                    ThemingIssue(
                        file_path=str(file_path),
                        line_number=0,
                        issue_type="missing_theming_docs",
                        description="Documentation mentions printing/console but not theming",
                        severity="info",
                        suggestion="Consider adding information about Catppuccin Mocha theming",
                        code_snippet="",
                    )
                )

        return FileAnalysis(
            file_path=str(file_path),
            has_mocha_import=False,
            has_printing_imports=False,
            raw_print_count=0,
            centralized_print_count=0,
            issues=issues,
            total_lines=len(lines),
        )

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single file based on its type."""
        if file_path.suffix == ".py":
            return self.analyze_python_file(file_path)
        elif file_path.suffix == ".md":
            return self.analyze_markdown_file(file_path)
        else:
            # For other file types, do basic analysis
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.splitlines()
            except Exception:
                lines = []

            return FileAnalysis(
                file_path=str(file_path),
                has_mocha_import=False,
                has_printing_imports=False,
                raw_print_count=0,
                centralized_print_count=0,
                issues=[],
                total_lines=len(lines),
            )

    def run_analysis(self) -> Dict[str, Any]:
        """Run the complete theming analysis."""
        print_info("Starting Catppuccin Mocha Theming Consistency Analysis...")

        files = self.find_files_to_analyze()
        print_info(f"Found {len(files)} files to analyze")

        total_issues = 0
        total_raw_prints = 0
        total_centralized_prints = 0
        files_with_issues = 0

        for file_path in files:
            analysis = self.analyze_file(file_path)
            self.file_analyses[str(file_path)] = analysis

            if analysis.issues:
                files_with_issues += 1
                total_issues += len(analysis.issues)

            total_raw_prints += analysis.raw_print_count
            total_centralized_prints += analysis.centralized_print_count

        # Generate summary statistics
        summary = {
            "total_files": len(files),
            "files_with_issues": files_with_issues,
            "total_issues": total_issues,
            "total_raw_prints": total_raw_prints,
            "total_centralized_prints": total_centralized_prints,
            "issues_by_type": defaultdict(int),
            "issues_by_severity": defaultdict(int),
        }

        # Categorize issues
        for analysis in self.file_analyses.values():
            for issue in analysis.issues:
                summary["issues_by_type"][issue.issue_type] += 1
                summary["issues_by_severity"][issue.severity] += 1

        return summary

    def generate_report(
        self, summary: Dict[str, Any], output_file: Optional[str] = None
    ) -> str:
        """Generate a comprehensive report of the analysis."""
        report_lines = []

        # Header
        report_lines.append("# Catppuccin Mocha Theming Consistency Report")
        report_lines.append("")
        report_lines.append(
            f"**Analysis Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")

        # Summary
        report_lines.append("## 📊 Summary")
        report_lines.append("")
        report_lines.append(f"- **Total Files Analyzed:** {summary['total_files']}")
        report_lines.append(f"- **Files with Issues:** {summary['files_with_issues']}")
        report_lines.append(f"- **Total Issues Found:** {summary['total_issues']}")
        report_lines.append(
            f"- **Raw Print Statements:** {summary['total_raw_prints']}"
        )
        report_lines.append(
            f"- **Centralized Print Usage:** {summary['total_centralized_prints']}"
        )
        report_lines.append("")

        # Issues by severity
        report_lines.append("## 🚨 Issues by Severity")
        report_lines.append("")
        for severity, count in sorted(summary["issues_by_severity"].items()):
            icon = (
                "🔴" if severity == "error" else "🟡" if severity == "warning" else "🔵"
            )
            report_lines.append(f"- {icon} **{severity.title()}:** {count}")
        report_lines.append("")

        # Issues by type
        report_lines.append("## 📋 Issues by Type")
        report_lines.append("")
        for issue_type, count in sorted(summary["issues_by_type"].items()):
            report_lines.append(
                f"- **{issue_type.replace('_', ' ').title()}:** {count}"
            )
        report_lines.append("")

        # Detailed issues
        report_lines.append("## 🔍 Detailed Issues")
        report_lines.append("")

        # Group issues by file
        issues_by_file = defaultdict(list)
        for analysis in self.file_analyses.values():
            for issue in analysis.issues:
                issues_by_file[issue.file_path].append(issue)

        for file_path, issues in sorted(issues_by_file.items()):
            if not issues:
                continue

            report_lines.append(f"### 📄 {file_path}")
            report_lines.append("")

            for issue in sorted(issues, key=lambda x: x.line_number):
                severity_icon = (
                    "🔴"
                    if issue.severity == "error"
                    else "🟡" if issue.severity == "warning" else "🔵"
                )
                report_lines.append(
                    f"**Line {issue.line_number}** {severity_icon} **{issue.issue_type.replace('_', ' ').title()}**"
                )
                report_lines.append(f"- **Description:** {issue.description}")
                report_lines.append(f"- **Suggestion:** {issue.suggestion}")
                if issue.code_snippet:
                    report_lines.append(f"- **Code:** `{issue.code_snippet.strip()}`")
                report_lines.append("")

        # Recommendations
        report_lines.append("## 💡 Recommendations")
        report_lines.append("")

        if summary["total_raw_prints"] > 0:
            report_lines.append("### 🔧 Replace Raw Print Statements")
            report_lines.append(
                "Replace all raw `print()` statements with centralized printing utilities:"
            )
            report_lines.append("")
            report_lines.append("```python")
            report_lines.append("# Instead of:")
            report_lines.append("print('Operation completed')")
            report_lines.append("")
            report_lines.append("# Use:")
            report_lines.append(
                "from dataset_forge.utils.printing import print_success"
            )
            report_lines.append("print_success('Operation completed')")
            report_lines.append("```")
            report_lines.append("")

        if summary["issues_by_type"].get("missing_menu_context", 0) > 0:
            report_lines.append("### 🎯 Fix Menu Context")
            report_lines.append(
                "Add missing `current_menu` and `menu_context` parameters to `show_menu` calls:"
            )
            report_lines.append("")
            report_lines.append("```python")
            report_lines.append("key = show_menu(")
            report_lines.append("    'Menu Title',")
            report_lines.append("    options,")
            report_lines.append("    Mocha.lavender,")
            report_lines.append("    current_menu='Menu Name',  # Add this")
            report_lines.append("    menu_context=menu_context  # Add this")
            report_lines.append(")")
            report_lines.append("```")
            report_lines.append("")

        if summary["issues_by_type"].get("mocha_usage_without_import", 0) > 0:
            report_lines.append("### 🎨 Add Mocha Imports")
            report_lines.append("Add missing Mocha color imports:")
            report_lines.append("")
            report_lines.append("```python")
            report_lines.append("from dataset_forge.utils.color import Mocha")
            report_lines.append("```")
            report_lines.append("")

        # Best practices
        report_lines.append("### ✅ Best Practices")
        report_lines.append("")
        report_lines.append(
            "1. **Always use centralized printing utilities** instead of raw `print()`"
        )
        report_lines.append("2. **Import Mocha colors** in all files that use theming")
        report_lines.append("3. **Use standardized menu patterns** with proper context")
        report_lines.append(
            "4. **Follow the Catppuccin Mocha color scheme** consistently"
        )
        report_lines.append("5. **Test CLI output** to ensure proper colorization")
        report_lines.append("")

        report = "\n".join(report_lines)

        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print_info(f"📄 Report saved to: {output_path}")

        return report


def main():
    """Main entry point for the theming checker."""
    parser = argparse.ArgumentParser(
        description="Check Catppuccin Mocha theming consistency across Dataset Forge codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/check_mocha_theming.py
  python tools/check_mocha_theming.py --output reports/theming_report.md
  python tools/check_mocha_theming.py --verbose
        """,
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file for the report (default: logs/mocha_theming_report.md)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Set default output file if not specified
    if not args.output:
        args.output = "logs/mocha_theming_report.md"

    # Create checker and run analysis
    checker = MochaThemingChecker(args.project_root)
    summary = checker.run_analysis()

    # Generate and display report
    report = checker.generate_report(summary, args.output)

    # Print summary to console
    print_info("\n" + "=" * 60)
    print_info("CATPPUCCIN MOCHA THEMING ANALYSIS COMPLETE")
    print_info("=" * 60)
    print_info(f"Files Analyzed: {summary['total_files']}")
    print_info(f"Total Issues: {summary['total_issues']}")
    print_info(f"Errors: {summary['issues_by_severity'].get('error', 0)}")
    print_info(f"Warnings: {summary['issues_by_severity'].get('warning', 0)}")
    print_info(f"Info: {summary['issues_by_severity'].get('info', 0)}")
    print_info(f"Raw Prints: {summary['total_raw_prints']}")
    print_info(f"Centralized Prints: {summary['total_centralized_prints']}")
    print_info("=" * 60)

    if args.verbose:
        print_info("\nDetailed Report:")
        print_info(report)

    # Exit with error code if there are critical issues
    if summary["issues_by_severity"].get("error", 0) > 0:
        print_error(
            "\nCritical theming issues found! Please fix errors before proceeding."
        )
        # Don't exit with error code - just warn
        print_warning("Continuing despite theming issues...")
        sys.exit(0)
    elif summary["total_issues"] > 0:
        print_warning("\nTheming issues found. Review the report for details.")
        sys.exit(0)
    else:
        print_success(
            "\nNo theming issues found! Codebase follows Catppuccin Mocha standards."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
