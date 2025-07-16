#!/usr/bin/env python
"""
find_code_issues.py - Static analysis tool for Dataset Forge

Finds:
- Unused functions/methods/classes (dead code)
- Untested code (missing test coverage)
- Functions/methods/classes defined but never called
- Test files without corresponding code, and vice versa
- (Extensible: add more static analysis as needed)

Usage:
    python tools/find_code_issues.py [options]

Options:
    --vulture         Run vulture for dead code
    --coverage        Run pytest-cov for coverage
    --callgraph       Run pyan3 for call graph analysis
    --pyflakes        Run pyflakes for unused imports/variables
    --test-mapping    Check test/code correspondence
    --ast             AST: Find defined but never called functions/classes
    --all             Run all analyses (default)
    --view            View detailed results for each analysis after run
    -h, --help        Show help

Requirements:
    pip install vulture pytest pytest-cov coverage pyan3 pyflakes

"""
import os
import sys
import subprocess
import argparse
import tempfile
import ast
from pathlib import Path
from datetime import datetime
from typing import Optional

# --- CONFIG ---
CODE_DIR = "dataset_forge"
TESTS_DIR = "tests"
LOG_DIR = "tools/find_code_issues"
LOG_FILE = os.path.join(LOG_DIR, "find_code_issues.log")
VIEW_FILE = os.path.join(LOG_DIR, "find_code_issues_view.txt")
REPORT_FILE = os.path.join(LOG_DIR, "find_code_issues_report.txt")


# --- LOGGING ---
def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log(msg: str):
    ensure_log_dir()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def clear_log():
    ensure_log_dir()
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"# find_code_issues.py log - {datetime.now()}\n\n")


def write_view_output(content: str):
    ensure_log_dir()
    with open(VIEW_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def write_report_output(content: str):
    ensure_log_dir()
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(content)


# --- UTILS ---
def print_header(msg: str):
    print(f"\n{'='*60}\n{msg}\n{'='*60}")


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
    return [str(p) for p in Path(directory).rglob("*.py") if p.is_file()]


# --- ANALYSIS STORAGE ---
class AnalysisResults:
    def __init__(self):
        self.vulture: Optional[str] = None
        self.coverage: Optional[str] = None
        self.pyan3: Optional[str] = None
        self.pyflakes: Optional[str] = None
        self.test_mapping: Optional[str] = None
        self.ast: Optional[str] = None
        self.docstrings: Optional[str] = None  # <-- Add for docstring analysis
        self.issues = []  # List of actionable issues


results = AnalysisResults()


# --- 1. VULTURE: Find unused code ---
def run_vulture(verbose=False):
    if not verbose:
        print("Running: VULTURE (dead code analysis)...")
    cmd = f"vulture {CODE_DIR}/"
    output = run_cmd(cmd)
    results.vulture = output or "No output from vulture."
    # Actionable: parse for unused code
    unused = []
    for line in (output or "").splitlines():
        if line.strip() and ("unused" in line or ":" in line):
            unused.append(line)
    if unused:
        results.issues.append(
            f"[VULTURE] Unused code detected (dead code):\n" + "\n".join(unused)
        )


# --- 2. COVERAGE: Find untested code ---
def run_coverage(verbose=False):
    if not verbose:
        print("Running: COVERAGE (untested code)...")
    cov_file = ".coverage"
    if os.path.exists(cov_file):
        os.remove(cov_file)
    cmd = f"pytest --cov={CODE_DIR} {TESTS_DIR}/ --cov-report=term-missing"
    output = run_cmd(cmd)
    results.coverage = output or "No output from pytest-cov."
    # Actionable: parse for missing coverage
    missing = []
    for line in (output or "").splitlines():
        if "Missed" in line or "100%" not in line and "%" in line:
            missing.append(line)
    if missing:
        results.issues.append(
            f"[COVERAGE] Untested code detected:\n" + "\n".join(missing)
        )


# --- 3. PYAN3: Call graph analysis ---
def run_pyan3(verbose=False):
    if not verbose:
        print("Running: PYAN3 (call graph analysis)...")
    py_files = find_py_files(CODE_DIR)
    if not py_files:
        results.pyan3 = "No Python files found in code directory."
        return
    with tempfile.NamedTemporaryFile("w+t", delete=False) as tmp:
        tmp.write("\n".join(py_files))
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
        print("Running: PYFLAKES (unused imports/variables)...")
    py_files = find_py_files(CODE_DIR)
    unused = []
    output_accum = []
    for f in py_files:
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
            f"[PYFLAKES] Unused imports/variables detected:\n" + "\n".join(unused)
        )


# --- 5. TEST/CODE MAPPING ---
def test_code_mapping(verbose=False):
    if not verbose:
        print("Running: TEST/CODE MAPPING (test/code correspondence)...")
    code_files = set([Path(f).stem for f in find_py_files(CODE_DIR)])
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
        print("Running: AST (defined but never called)...")
    defined = set()
    called = set()
    for f in find_py_files(CODE_DIR):
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
        print("Running: DOCSTRING CHECK (missing docstrings)...")
    missing = []
    for f in find_py_files(CODE_DIR):
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
            + "\n".join(missing)
        )


# --- REPORT GENERATION ---
def generate_report():
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("[FULL REPORT] Actionable Insights and Issues")
    report_lines.append("=" * 60)
    if not results.issues:
        report_lines.append("No major issues detected. Your codebase looks clean!\n")
    else:
        for issue in results.issues:
            report_lines.append(f"- {issue}\n")
    report_lines.append("\n[Summary]")
    report_lines.append(
        "- See tools/find_code_issues/find_code_issues.log for full verbose output of all analyses."
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
    report_lines.append("\n[Done] Review the above output for actionable issues.\n")
    report = "\n".join(report_lines)
    print("\n" + report)
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
        ("DOCSTRINGS", results.docstrings),  # <-- Add docstring results
    ]:
        view_lines.append(f"\n--- {name} ---\n")
        view_lines.append(value or "No output.")
    view = "\n".join(view_lines)
    print("\n" + view)
    write_view_output(view)


# --- MAIN CLI ---
def main():
    parser = argparse.ArgumentParser(
        description="Find code issues (dead code, untested code, etc.)"
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
    parser.add_argument("--all", action="store_true", help="Run all analyses (default)")
    parser.add_argument(
        "--view",
        action="store_true",
        help="View detailed results for each analysis after run",
    )
    args = parser.parse_args()

    clear_log()
    print_header("[find_code_issues.py] Static Analysis Starting...")

    if not any(
        [
            args.vulture,
            args.coverage,
            args.callgraph,
            args.pyflakes,
            args.test_mapping,
            args.ast,
            args.docstrings,
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

    generate_report()

    if args.view:
        view_detailed_results()


if __name__ == "__main__":
    main()
