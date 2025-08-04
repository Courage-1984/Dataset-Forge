#!/usr/bin/env python3
"""
Comprehensive static analysis tool for Dataset Forge codebase.

This tool performs multiple types of analysis:
- Dead code detection (vulture)
- Test coverage analysis (pytest-cov)
- Call graph analysis (pyan3)
- Code quality checks (pyflakes)
- Test/code mapping
- AST-based analysis
- Documentation checks
- Dependency analysis
- Configuration validation
- Import analysis

Usage:
    python tools/find_code_issues.py [options]

Options:
    --all              Run all analyses (default)
    --vulture          Dead code detection
    --coverage         Test coverage analysis
    --callgraph        Call graph analysis
    --pyflakes         Code quality checks
    --test-mapping     Test/code correspondence
    --ast              AST-based analysis
    --docstrings       Documentation checks
    --dependencies     Dependency analysis
    --configs          Configuration validation
    --view             View detailed results after analysis
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import ast
import importlib.util
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataset_forge.utils.printing import print_info, print_success, print_warning, print_error, print_header, print_section


# --- CONFIGURATION ---
CODE_DIR = "dataset_forge"
TESTS_DIR = "tests"
CONFIGS_DIR = "configs"
TOOLS_DIR = "tools"
ANALYSIS_DIRS = [CODE_DIR, TESTS_DIR, CONFIGS_DIR, TOOLS_DIR]

# Ensure logs directory exists
LOGS_DIR = "logs/find_code_issues"
os.makedirs(LOGS_DIR, exist_ok=True)

# --- LOGGING ---
def log(msg: str):
    with open(os.path.join(LOGS_DIR, "find_code_issues.log"), "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def clear_log():
    with open(os.path.join(LOGS_DIR, "find_code_issues.log"), "w", encoding="utf-8") as f:
        f.write(f"# find_code_issues.py log - {datetime.now()}\n\n")


def write_view_output(content: str):
    with open(os.path.join(LOGS_DIR, "find_code_issues_view.txt"), "w", encoding="utf-8") as f:
        f.write(content)


def write_report_output(content: str):
    with open(os.path.join(LOGS_DIR, "find_code_issues_report.txt"), "w", encoding="utf-8") as f:
        f.write(content)


def write_dependencies_output(content: str):
    with open(os.path.join(LOGS_DIR, "dependencies_analysis.txt"), "w", encoding="utf-8") as f:
        f.write(content)


# --- UTILS ---
def print_header(msg: str):
    print_info(f"\n{'='*60}\n{msg}\n{'='*60}")


def run_cmd(cmd, capture=True):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
        log(f"$ {cmd}\n{result.stdout}\n{result.stderr if result.stderr else ''}")
        if result.returncode != 0:
            log(f"[!] Command failed: {cmd}\n{result.stderr}")
        return result.stdout if capture else None
    except Exception as e:
        log(f"[!] Exception running command: {cmd}\n{e}")
        return None


def find_py_files(directory):
    """Find all Python files in directory recursively."""
    if not os.path.exists(directory):
        return []
    return [str(p) for p in Path(directory).rglob("*.py") if p.is_file()]


def find_json_files(directory):
    """Find all JSON files in directory recursively."""
    if not os.path.exists(directory):
        return []
    return [str(p) for p in Path(directory).rglob("*.json") if p.is_file()]


def find_all_files(directory, extensions=None):
    """Find all files with given extensions in directory recursively."""
    if not os.path.exists(directory):
        return []
    if extensions is None:
        extensions = [".py", ".json", ".txt", ".md", ".yaml", ".yml"]
    files = []
    for ext in extensions:
        files.extend([str(p) for p in Path(directory).rglob(f"*{ext}") if p.is_file()])
    return files


# --- ANALYSIS STORAGE ---
class AnalysisResults:
    def __init__(self):
        self.vulture: Optional[str] = None
        self.coverage: Optional[str] = None
        self.pyan3: Optional[str] = None
        self.pyflakes: Optional[str] = None
        self.test_mapping: Optional[str] = None
        self.ast: Optional[str] = None
        self.docstrings: Optional[str] = None
        self.dependencies: Optional[str] = None
        self.configs: Optional[str] = None
        self.import_analysis: Optional[str] = None
        self.issues = []  # List of actionable issues


results = AnalysisResults()


# --- 1. VULTURE: Find unused code ---
def run_vulture(verbose=False):
    if not verbose:
        print_info("Running: VULTURE (dead code analysis)...")

    # Run vulture on all analysis directories
    all_output = []
    for directory in ANALYSIS_DIRS:
        if os.path.exists(directory):
            cmd = f"vulture {directory}/"
            output = run_cmd(cmd)
            if output:
                all_output.append(f"--- {directory.upper()} ---\n{output}")

    results.vulture = "\n".join(all_output) or "No output from vulture."

    # Actionable: parse for unused code
    unused = []
    for line in (results.vulture or "").splitlines():
        if line.strip() and ("unused" in line or ":" in line):
            unused.append(line)
    if unused:
        results.issues.append(
            f"[VULTURE] Unused code detected (dead code):\n"
            + "\n".join(unused[:20])  # Limit to first 20
        )


# --- 2. COVERAGE: Find untested code ---
def run_coverage(verbose=False):
    if not verbose:
        print_info("Running: COVERAGE (untested code)...")
    cov_file = ".coverage"
    if os.path.exists(cov_file):
        os.remove(cov_file)

    # Run coverage on dataset_forge directory
    cmd = f"pytest --cov={CODE_DIR} {TESTS_DIR}/ --cov-report=term-missing --cov-report=html:logs/find_code_issues/coverage_html"
    output = run_cmd(cmd)
    results.coverage = output or "No output from pytest-cov."

    # Actionable: parse for missing coverage
    missing = []
    for line in (output or "").splitlines():
        if "Missed" in line or ("100%" not in line and "%" in line):
            missing.append(line)
    if missing:
        results.issues.append(
            f"[COVERAGE] Untested code detected:\n"
            + "\n".join(missing[:10])  # Limit to first 10
        )


# --- 3. PYAN3: Call graph analysis ---
def run_pyan3(verbose=False):
    if not verbose:
        print_info("Running: PYAN3 (call graph analysis)...")

    # Get all Python files from all directories
    all_py_files = []
    for directory in ANALYSIS_DIRS:
        all_py_files.extend(find_py_files(directory))

    if not all_py_files:
        results.pyan3 = "No Python files found in analysis directories."
        return

    with tempfile.NamedTemporaryFile("w+t", delete=False) as tmp:
        tmp.write("\n".join(all_py_files))
        tmp_path = tmp.name

    cmd = f"pyan3 @{tmp_path} --uses --no-defines --colored --grouped --dot"
    output = run_cmd(cmd)
    results.pyan3 = output or "No output from pyan3."

    # Actionable: suggest user to visualize DOT output for orphaned nodes
    if output:
        results.issues.append(
            "[PYAN3] Review the DOT call graph for orphaned (never-called) functions/classes."
        )

    os.unlink(tmp_path)


# --- 4. PYFLAKES: Unused imports/variables ---
def run_pyflakes(verbose=False):
    if not verbose:
        print_info("Running: PYFLAKES (unused imports/variables)...")

    all_py_files = []
    for directory in ANALYSIS_DIRS:
        all_py_files.extend(find_py_files(directory))

    unused = []
    output_accum = []
    for f in all_py_files:
        output = run_cmd(f"pyflakes {f}")
        if output:
            output_accum.append(f"{f}:\n{output}")
            for line in output.splitlines():
                if (
                    "imported but unused" in line
                    or "assigned to but never used" in line
                ):
                    unused.append(f"{f}: {line}")

    results.pyflakes = "\n".join(output_accum) or "No output from pyflakes."
    if unused:
        results.issues.append(
            f"[PYFLAKES] Unused imports/variables detected:\n"
            + "\n".join(unused[:20])  # Limit to first 20
        )


# --- 5. TEST/CODE MAPPING ---
def test_code_mapping(verbose=False):
    if not verbose:
        print_info("Running: TEST/CODE MAPPING (test/code correspondence)...")

    # Get all Python files from dataset_forge
    code_files = set([Path(f).stem for f in find_py_files(CODE_DIR)])

    # Get all test files from tests directory
    test_files = set(
        [
            Path(f).stem.replace("test_", "")
            for f in find_py_files(TESTS_DIR)
            if Path(f).name.startswith("test_")
        ]
    )

    missing_tests = code_files - test_files
    orphan_tests = test_files - code_files

    results.test_mapping = (
        f"Code files with NO corresponding test: {sorted(missing_tests)}\n"
        f"Test files with NO corresponding code: {sorted(orphan_tests)}"
    )

    if missing_tests:
        results.issues.append(
            f"[TEST MAPPING] Code files with NO corresponding test: {sorted(missing_tests)}"
        )
    if orphan_tests:
        results.issues.append(
            f"[TEST MAPPING] Test files with NO corresponding code: {sorted(orphan_tests)}"
        )


# --- 6. AST: Find defined but never called functions/classes ---
def ast_defined_but_never_called(verbose=False):
    if not verbose:
        print_info("Running: AST (defined but never called)...")

    defined = set()
    called = set()

    all_py_files = []
    for directory in ANALYSIS_DIRS:
        all_py_files.extend(find_py_files(directory))

    for f in all_py_files:
        with open(f, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=f)
            except Exception as e:
                log(f"[!] Could not parse {f}: {e}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    defined.add(node.name)
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        called.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        called.add(node.func.attr)

    never_called = defined - called
    results.ast = f"Functions/classes defined but never called: {sorted(never_called)}"
    if never_called:
        results.issues.append(
            f"[AST] Functions/classes defined but never called: {sorted(never_called)}"
        )


# --- 7. DOCSTRING CHECK: Find missing docstrings ---
def check_missing_docstrings(verbose=False):
    if not verbose:
        print_info("Running: DOCSTRING CHECK (missing docstrings)...")

    missing = []
    all_py_files = []
    for directory in ANALYSIS_DIRS:
        all_py_files.extend(find_py_files(directory))

    for f in all_py_files:
        with open(f, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=f)
            except Exception as e:
                log(f"[!] Could not parse {f}: {e}")
                continue

            # Build parent map
            parent_map = {}
            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    parent_map[child] = node

            for node in ast.walk(tree):
                # Only check public (non-underscore) functions/classes/methods
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    name = node.name
                    if name.startswith("_"):
                        continue
                    doc = ast.get_docstring(node)
                    if not doc:
                        parent = parent_map.get(node)
                        if parent and isinstance(parent, ast.ClassDef):
                            missing.append(
                                f"{f}: class {parent.name} -> method {name} (missing docstring)"
                            )
                        elif isinstance(node, ast.ClassDef):
                            missing.append(f"{f}: class {name} (missing docstring)")
                        else:
                            missing.append(f"{f}: function {name} (missing docstring)")

    results.docstrings = (
        "\n".join(missing)
        if missing
        else "All public functions/classes/methods have docstrings."
    )
    if missing:
        results.issues.append(
            f"[DOCSTRINGS] Missing docstrings detected in public functions/classes/methods:\n"
            + "\n".join(missing[:20])  # Limit to first 20
        )


# --- 8. DEPENDENCIES: Analyze unused dependencies ---
def analyze_dependencies(verbose=False):
    if not verbose:
        print_info("Running: DEPENDENCIES (analyze unused dependencies)...")

    # Read requirements.txt
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        results.dependencies = "requirements.txt not found."
        return

    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements_content = f.read()

    # Extract package names from requirements.txt
    required_packages = set()
    for line in requirements_content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("="):
            # Extract package name (before any version specifiers)
            package = (
                line.split("==")[0]
                .split(">=")[0]
                .split("<=")[0]
                .split("~=")[0]
                .split("[")[0]
                .strip()
            )
            if package:
                required_packages.add(package.lower())

    # Find all import statements in the codebase
    imported_packages = set()
    all_py_files = []
    for directory in ANALYSIS_DIRS:
        all_py_files.extend(find_py_files(directory))

    for f in all_py_files:
        with open(f, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=f)
            except Exception as e:
                log(f"[!] Could not parse {f}: {e}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_packages.add(alias.name.split(".")[0].lower())
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_packages.add(node.module.split(".")[0].lower())

    # Find unused packages
    unused_packages = required_packages - imported_packages
    missing_packages = imported_packages - required_packages

    # Special handling for packages that might be used indirectly
    indirect_usage = {
        "pytest",
        "pytest-cov",
        "coverage",
        "vulture",
        "pyan3",
        "pyflakes",
        "setuptools",
        "wheel",
        "pip",
    }
    unused_packages = unused_packages - indirect_usage

    results.dependencies = (
        f"Required packages: {sorted(required_packages)}\n"
        f"Imported packages: {sorted(imported_packages)}\n"
        f"Potentially unused packages: {sorted(unused_packages)}\n"
        f"Imported but not in requirements: {sorted(missing_packages)}"
    )

    if unused_packages:
        results.issues.append(
            f"[DEPENDENCIES] Potentially unused packages in requirements.txt: {sorted(unused_packages)}"
        )
    if missing_packages:
        results.issues.append(
            f"[DEPENDENCIES] Packages imported but not in requirements.txt: {sorted(missing_packages)}"
        )


# --- 9. CONFIGS: Analyze configuration files ---
def analyze_configs(verbose=False):
    if not verbose:
        print_info("Running: CONFIGS (analyze configuration files)...")

    config_issues = []
    config_files = find_json_files(CONFIGS_DIR)

    for config_file in config_files:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Basic validation - accept both dict and list (for augmentation recipes)
            if not isinstance(config_data, (dict, list)):
                config_issues.append(f"{config_file}: Root is not a dictionary or list")
                continue

            # Check for common issues
            if not config_data:
                config_issues.append(f"{config_file}: Empty configuration")

            # Check for required fields in specific config types
            if "example" in config_file.lower():
                # Example configs should have some content
                if len(config_data) < 2:
                    config_issues.append(
                        f"{config_file}: Example config seems too minimal"
                    )

        except json.JSONDecodeError as e:
            config_issues.append(f"{config_file}: Invalid JSON - {e}")
        except Exception as e:
            config_issues.append(f"{config_file}: Error reading file - {e}")

    # Check for missing config files
    expected_configs = [
        "_example_config.json",
        "_example_user_profile.json",
        "_example_community_links.json",
    ]

    missing_configs = []
    for expected in expected_configs:
        if not os.path.exists(os.path.join(CONFIGS_DIR, expected)):
            missing_configs.append(expected)

    if missing_configs:
        config_issues.append(f"Missing expected config files: {missing_configs}")

    results.configs = (
        "\n".join(config_issues)
        if config_issues
        else "All configuration files are valid."
    )

    if config_issues:
        results.issues.append(
            f"[CONFIGS] Configuration file issues detected:\n"
            + "\n".join(config_issues)
        )


# --- 10. IMPORT ANALYSIS: Cross-directory import analysis ---
def analyze_imports(verbose=False):
    if not verbose:
        print_info("Running: IMPORT ANALYSIS (cross-directory import analysis)...")

    import_map = defaultdict(set)
    all_py_files = []
    for directory in ANALYSIS_DIRS:
        all_py_files.extend(find_py_files(directory))

    for f in all_py_files:
        with open(f, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=f)
            except Exception as e:
                log(f"[!] Could not parse {f}: {e}")
                continue

            file_imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        file_imports.add(node.module)

            if file_imports:
                import_map[f] = file_imports

    # Analyze for potential issues
    issues = []

    # Check for circular imports
    for file1, imports1 in import_map.items():
        for file2, imports2 in import_map.items():
            if file1 != file2:
                file1_module = Path(file1).stem
                file2_module = Path(file2).stem
                if file1_module in imports2 and file2_module in imports1:
                    issues.append(f"Potential circular import: {file1} <-> {file2}")

    # Check for unused imports
    for file_path, imports in import_map.items():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            for imp in imports:
                if imp not in content.replace(f"import {imp}", "").replace(
                    f"from {imp}", ""
                ):
                    issues.append(f"{file_path}: Potentially unused import '{imp}'")

    results.import_analysis = (
        "\n".join(issues) if issues else "No import issues detected."
    )

    if issues:
        results.issues.append(
            f"[IMPORTS] Import analysis issues detected:\n"
            + "\n".join(issues[:10])  # Limit to first 10
        )


# --- REPORT GENERATION ---
def generate_report():
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("[COMPREHENSIVE REPORT] Actionable Insights and Issues")
    report_lines.append("=" * 60)

    if not results.issues:
        report_lines.append("No major issues detected. Your codebase looks clean!\n")
    else:
        for issue in results.issues:
            report_lines.append(f"- {issue}\n")

    report_lines.append("\n[Summary]")
    report_lines.append(
        "- See logs/find_code_issues/find_code_issues.log for full verbose output of all analyses."
    )
    report_lines.append(
        "- See logs/find_code_issues/dependencies_analysis.txt for detailed dependency analysis."
    )
    report_lines.append(
        "- Review the above actionable issues and address them as appropriate."
    )
    report_lines.append(
        "- For call graph (pyan3), consider visualizing the DOT output for deeper insights."
    )
    report_lines.append(
        "- For coverage, see the detailed report for lines/functions missed."
    )
    report_lines.append(
        "- For unused code, consider removing or refactoring as needed."
    )
    report_lines.append(
        "- For test/code mapping, ensure all code is tested and all tests have code."
    )
    report_lines.append(
        "- For unused imports/variables, clean up to improve code quality."
    )
    report_lines.append(
        "- For missing docstrings, add Google-style docstrings to all public functions/classes/methods."
    )
    report_lines.append(
        "- For dependencies, review unused packages and add missing ones to requirements.txt."
    )
    report_lines.append(
        "- For configs, ensure all configuration files are valid and complete."
    )
    report_lines.append("\n[Done] Review the above output for actionable issues.\n")

    report = "\n".join(report_lines)
    print_info(report)
    write_report_output(report)


# --- VIEW DETAILED RESULTS ---
def view_detailed_results():
    view_lines = []
    view_lines.append("=" * 60)
    view_lines.append("[DETAILED RESULTS]")
    view_lines.append("=" * 60)

    for name, value in [
        ("VULTURE", results.vulture),
        ("COVERAGE", results.coverage),
        ("PYAN3", results.pyan3),
        ("PYFLAKES", results.pyflakes),
        ("TEST MAPPING", results.test_mapping),
        ("AST", results.ast),
        ("DOCSTRINGS", results.docstrings),
        ("DEPENDENCIES", results.dependencies),
        ("CONFIGS", results.configs),
        ("IMPORT ANALYSIS", results.import_analysis),
    ]:
        view_lines.append(f"\n--- {name} ---\n")
        view_lines.append(value or "No output.")

    view = "\n".join(view_lines)
    print_info(view)
    write_view_output(view)

    # Write dependencies analysis to separate file
    if results.dependencies:
        write_dependencies_output(results.dependencies)


# --- MAIN CLI ---
def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive code analysis for Dataset Forge"
    )
    parser.add_argument(
        "--vulture", action="store_true", help="Run vulture for dead code"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run pytest-cov for coverage"
    )
    parser.add_argument(
        "--callgraph", action="store_true", help="Run pyan3 for call graph analysis"
    )
    parser.add_argument(
        "--pyflakes",
        action="store_true",
        help="Run pyflakes for unused imports/variables",
    )
    parser.add_argument(
        "--test-mapping", action="store_true", help="Check test/code correspondence"
    )
    parser.add_argument(
        "--ast",
        action="store_true",
        help="AST: Find defined but never called functions/classes",
    )
    parser.add_argument(
        "--docstrings",
        action="store_true",
        help="Check for missing docstrings in public functions/classes/methods",
    )
    parser.add_argument(
        "--dependencies",
        action="store_true",
        help="Analyze unused dependencies in requirements.txt",
    )
    parser.add_argument(
        "--configs",
        action="store_true",
        help="Analyze configuration files",
    )
    parser.add_argument("--all", action="store_true", help="Run all analyses (default)")
    parser.add_argument(
        "--view",
        action="store_true",
        help="View detailed results for each analysis after run",
    )
    args = parser.parse_args()

    clear_log()
    print_header("[find_code_issues.py] Comprehensive Static Analysis Starting...")

    if not any(
        [
            args.vulture,
            args.coverage,
            args.callgraph,
            args.pyflakes,
            args.test_mapping,
            args.ast,
            args.docstrings,
            args.dependencies,
            args.configs,
            args.all,
        ]
    ):
        args.all = True

    if args.all or args.vulture:
        run_vulture()
    if args.all or args.coverage:
        run_coverage()
    if args.all or args.callgraph:
        run_pyan3()
    if args.all or args.pyflakes:
        run_pyflakes()
    if args.all or args.test_mapping:
        test_code_mapping()
    if args.all or args.ast:
        ast_defined_but_never_called()
    if args.all or args.docstrings:
        check_missing_docstrings()
    if args.all or args.dependencies:
        analyze_dependencies()
    if args.all or args.configs:
        analyze_configs()
    if args.all:
        analyze_imports()

    generate_report()

    if args.view:
        view_detailed_results()


if __name__ == "__main__":
    main()
