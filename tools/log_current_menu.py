#!/usr/bin/env python3
"""
Menu Auditing Tool for Dataset Forge

This tool recursively explores all menus and submenus in Dataset Forge,
logging their structure, options, and hierarchy to a markdown file for
auditing and improvement purposes.

Usage:
    python tools/log_current_menu.py
"""

import os
import sys
import importlib
import inspect
import re
import ast
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime
import subprocess
import time
import threading
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import queue
import signal

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Dataset Forge utilities
from dataset_forge.utils.menu import show_menu, lazy_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)


class MenuAuditor:
    """Comprehensive menu auditing tool for Dataset Forge."""

    def __init__(self):
        self.visited_menus: Set[str] = set()
        self.menu_hierarchy: Dict[str, Any] = {}
        self.path_input_patterns = [
            r"get_folder_path\(",
            r"get_path_with_history\(",
            r"input\(",
            r"raw_input\(",
            r"Enter.*path",
            r"Select.*folder",
            r"Choose.*directory",
        ]
        self.output_file = "logs/current_menu.md"
        self.max_depth = 20
        self.current_depth = 0
        self.menu_stack: List[str] = []
        self.menu_files = []

    def discover_menu_files(self) -> List[str]:
        """Discover all menu files in the dataset_forge/menus directory."""
        menus_dir = project_root / "dataset_forge" / "menus"
        menu_files = []

        if menus_dir.exists():
            for file_path in menus_dir.glob("*.py"):
                if file_path.name != "__init__.py":
                    # Return relative path from project root
                    relative_path = file_path.relative_to(project_root)
                    menu_files.append(str(relative_path))

        return menu_files

    def is_path_input_scenario(self, code: str) -> bool:
        """Check if the code contains path input scenarios."""
        code_lower = code.lower()
        for pattern in self.path_input_patterns:
            if re.search(pattern, code_lower, re.IGNORECASE):
                return True
        return False

    def analyze_menu_function(self, menu_func) -> Dict[str, Any]:
        """Analyze a menu function to extract its structure and options."""
        try:
            # Get the source code of the function
            source = inspect.getsource(menu_func)

            # Extract menu options from the source code (always do this)
            options = self.extract_menu_options_advanced(source)

            # Extract menu title and other metadata (always do this)
            metadata = self.extract_menu_metadata(source)

            # Check if this is a path input scenario
            has_path_input = self.is_path_input_scenario(source)

            return {
                "type": "menu",  # Always treat as menu to allow submenu exploration
                "options": options,
                "metadata": metadata,
                "source": source,
                "function_name": menu_func.__name__,
                "module": menu_func.__module__,
                "has_path_input": has_path_input,  # Flag for path input detection
                "description": (
                    "Menu contains path input scenarios"
                    if has_path_input
                    else "Standard menu"
                ),
            }

        except Exception as e:
            return {
                "type": "error",
                "error": str(e),
                "function_name": getattr(menu_func, "__name__", "unknown"),
                "module": getattr(menu_func, "__module__", "unknown"),
            }

    def extract_menu_options_advanced(self, source: str) -> Dict[str, Tuple[str, Any]]:
        """Extract menu options using AST parsing for better accuracy."""
        options = {}

        try:
            # Parse the source code
            tree = ast.parse(source)

            # Find all dictionary assignments
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "options":
                            if isinstance(node.value, ast.Dict):
                                # Parse the options dictionary
                                for key, value in zip(
                                    node.value.keys, node.value.values
                                ):
                                    if isinstance(key, ast.Constant) and isinstance(
                                        value, ast.Tuple
                                    ):
                                        if len(value.elts) >= 2:
                                            option_text = self.extract_string_literal(
                                                value.elts[0]
                                            )
                                            function_ref = (
                                                self.extract_function_reference(
                                                    value.elts[1]
                                                )
                                            )
                                            if option_text and function_ref:
                                                options[str(key.value)] = (
                                                    option_text,
                                                    function_ref,
                                                )

        except Exception as e:
            print_warning(f"AST parsing failed, falling back to regex: {e}")
            # Fallback to regex parsing
            options = self.extract_menu_options_regex(source)

        return options

    def extract_menu_options_regex(self, source: str) -> Dict[str, Tuple[str, Any]]:
        """Extract menu options using regex patterns."""
        options = {}

        # Look for options dictionary patterns
        options_patterns = [
            r"options\s*=\s*\{([^}]+)\}",
            r"options\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}",
        ]

        for pattern in options_patterns:
            matches = re.finditer(pattern, source, re.DOTALL)
            for match in matches:
                options_text = match.group(1)
                # Parse the options dictionary
                parsed_options = self.parse_options_dict(options_text)
                options.update(parsed_options)

        return options

    def extract_string_literal(self, node) -> Optional[str]:
        """Extract string literal from AST node."""
        if isinstance(node, ast.Constant):
            return str(node.value)
        # Remove deprecated ast.Str handling for Python 3.8+
        return None

    def extract_function_reference(self, node) -> Optional[str]:
        """Extract function reference from AST node."""
        try:
            if isinstance(node, ast.Call):
                # Handle function calls like lazy_menu(...)
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name == "lazy_menu" and len(node.args) >= 2:
                        module_arg = self.extract_string_literal(node.args[0])
                        func_arg = self.extract_string_literal(node.args[1])
                        if module_arg and func_arg:
                            return f"lazy_menu('{module_arg}', '{func_arg}')"
                    elif func_name == "lazy_action" and len(node.args) >= 2:
                        module_arg = self.extract_string_literal(node.args[0])
                        func_arg = self.extract_string_literal(node.args[1])
                        if module_arg and func_arg:
                            return f"lazy_action('{module_arg}', '{func_arg}')"
                    elif func_name == "require_hq_lq" and len(node.args) >= 1:
                        # Handle require_hq_lq(lambda: ...) calls
                        arg_str = self.ast_node_to_string(node.args[0])
                        return f"require_hq_lq({arg_str})"
                # Handle other function calls
                return self.ast_node_to_string(node)
            elif isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                return self.ast_node_to_string(node)
            elif isinstance(node, ast.Lambda):
                return f"<lambda>"
            elif isinstance(node, ast.Constant):
                return str(node.value)
            else:
                return self.ast_node_to_string(node)
        except Exception as e:
            return f"<ast.{type(node).__name__}>"

    def ast_node_to_string(self, node) -> str:
        """Convert AST node to string representation."""
        try:
            if hasattr(ast, "unparse"):
                return ast.unparse(node)
            else:
                # Fallback for older Python versions
                return str(node)
        except Exception:
            return f"<ast.{type(node).__name__}>"

    def parse_options_dict(self, options_text: str) -> Dict[str, Tuple[str, Any]]:
        """Parse options dictionary text into structured format."""
        options = {}

        # Split by lines and parse each option
        lines = options_text.split("\n")
        current_key = None
        current_value = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Look for key-value pairs
            key_match = re.match(r'"(\d+)":\s*\(', line)
            if key_match:
                current_key = key_match.group(1)
                # Extract the option text and function
                value_match = re.search(r"\(([^,]+),\s*([^)]+)\)", line)
                if value_match:
                    option_text = value_match.group(1).strip("\"'")
                    function_ref = value_match.group(2).strip()
                    options[current_key] = (option_text, function_ref)

        return options

    def extract_menu_metadata(self, source: str) -> Dict[str, Any]:
        """Extract menu metadata from source code."""
        metadata = {}

        # Extract menu title
        title_match = re.search(r'show_menu\s*\(\s*["\']([^"\']+)["\']', source)
        if title_match:
            metadata["title"] = title_match.group(1)

        # Extract header color
        color_match = re.search(r"header_color\s*=\s*([^,)]+)", source)
        if color_match:
            metadata["header_color"] = color_match.group(1).strip()

        # Extract character decoration
        char_match = re.search(r'char\s*=\s*["\']([^"\']+)["\']', source)
        if char_match:
            metadata["char"] = char_match.group(1)

        # Extract docstring
        docstring_match = re.search(r'"""(.*?)"""', source, re.DOTALL)
        if docstring_match:
            metadata["docstring"] = docstring_match.group(1).strip()

        return metadata

    def find_menu_functions(self, module_path: str) -> List[Tuple[str, Any]]:
        """Find all menu functions in a module."""
        menu_functions = []

        try:
            module = importlib.import_module(module_path)

            for name in dir(module):
                obj = getattr(module, name)
                if callable(obj) and name.endswith("_menu"):
                    menu_functions.append((name, obj))

        except Exception as e:
            print_warning(f"Could not import module {module_path}: {e}")

        return menu_functions

    def explore_menu_recursively(
        self, menu_func, menu_path: str = "", depth: int = 0
    ) -> Dict[str, Any]:
        """Recursively explore a menu and its submenus."""
        if depth > self.max_depth:
            return {"type": "max_depth_reached", "depth": depth}

        menu_id = f"{menu_func.__module__}.{menu_func.__name__}"
        if menu_id in self.visited_menus:
            return {"type": "already_visited", "menu_id": menu_id}

        self.visited_menus.add(menu_id)
        self.menu_stack.append(menu_id)

        print_info(f"Exploring menu: {menu_id} (depth: {depth})")

        # Analyze the menu function
        menu_info = self.analyze_menu_function(menu_func)

        # Explore submenus
        submenus = {}
        if "options" in menu_info and menu_info["options"]:
            for key, (option_text, function_ref) in menu_info["options"].items():
                if key == "0":  # Skip exit/back options
                    continue

                # Try to resolve the function reference
                submenu_func = self.resolve_function_reference(
                    function_ref, menu_func.__module__
                )
                if submenu_func and callable(submenu_func):
                    submenu_path = f"{menu_path} -> {option_text}"
                    submenu_info = self.explore_menu_recursively(
                        submenu_func, submenu_path, depth + 1
                    )
                    submenus[key] = {
                        "option_text": option_text,
                        "function_ref": function_ref,
                        "submenu": submenu_info,
                    }
                else:
                    # If we can't resolve the function, still record it for analysis
                    submenus[key] = {
                        "option_text": option_text,
                        "function_ref": function_ref,
                        "submenu": {
                            "type": "unresolved_function",
                            "function_ref": function_ref,
                        },
                    }

        menu_info["submenus"] = submenus
        menu_info["menu_path"] = menu_path
        menu_info["depth"] = depth

        self.menu_stack.pop()
        return menu_info

    def resolve_function_reference(
        self, function_ref: str, current_module: str
    ) -> Optional[Any]:
        """Resolve a function reference to the actual function."""
        try:
            # Handle lazy_menu calls
            if "lazy_menu(" in function_ref:
                # Extract module and function from lazy_menu call
                match = re.search(
                    r'lazy_menu\s*\(\s*["\']([^"\']+)["\'],\s*["\']([^"\']+)["\']',
                    function_ref,
                )
                if match:
                    module_path = match.group(1)
                    func_name = match.group(2)

                    # Handle __name__ references
                    if module_path == "__name__":
                        module_path = current_module

                    try:
                        module = importlib.import_module(module_path)
                        func = getattr(module, func_name, None)
                        if func:
                            print_info(
                                f"  ✓ Resolved lazy_menu: {module_path}.{func_name}"
                            )
                            return func
                        else:
                            print_warning(
                                f"  ✗ Function {func_name} not found in {module_path}"
                            )
                    except ImportError as e:
                        print_warning(f"  ✗ Could not import module {module_path}: {e}")
                    except Exception as e:
                        print_warning(
                            f"  ✗ Error resolving lazy_menu {module_path}.{func_name}: {e}"
                        )
                    return None

            # Handle lazy_action calls
            elif "lazy_action(" in function_ref:
                # Extract module and function from lazy_action call
                match = re.search(
                    r'lazy_action\s*\(\s*["\']([^"\']+)["\'],\s*["\']([^"\']+)["\']',
                    function_ref,
                )
                if match:
                    module_path = match.group(1)
                    func_name = match.group(2)

                    # Handle __name__ references
                    if module_path == "__name__":
                        module_path = current_module

                    try:
                        module = importlib.import_module(module_path)
                        func = getattr(module, func_name, None)
                        if func:
                            print_info(
                                f"  ✓ Resolved lazy_action: {module_path}.{func_name}"
                            )
                            return func
                        else:
                            print_warning(
                                f"  ✗ Function {func_name} not found in {module_path}"
                            )
                    except ImportError as e:
                        print_warning(f"  ✗ Could not import module {module_path}: {e}")
                    except Exception as e:
                        print_warning(
                            f"  ✗ Error resolving lazy_action {module_path}.{func_name}: {e}"
                        )
                    return None

            # Handle require_hq_lq calls (these are function wrappers, not module imports)
            elif "require_hq_lq(" in function_ref:
                # Extract the inner lazy_action call
                lazy_action_match = re.search(
                    r'lazy_action\s*\(\s*["\']([^"\']+)["\'],\s*["\']([^"\']+)["\']',
                    function_ref,
                )
                if lazy_action_match:
                    module_path = lazy_action_match.group(1)
                    func_name = lazy_action_match.group(2)

                    # Handle __name__ references
                    if module_path == "__name__":
                        module_path = current_module

                    try:
                        module = importlib.import_module(module_path)
                        func = getattr(module, func_name, None)
                        if func:
                            print_info(
                                f"  ✓ Resolved require_hq_lq: {module_path}.{func_name}"
                            )
                            return func
                        else:
                            print_warning(
                                f"  ✗ Function {func_name} not found in {module_path}"
                            )
                    except ImportError as e:
                        print_warning(f"  ✗ Could not import module {module_path}: {e}")
                    except Exception as e:
                        print_warning(
                            f"  ✗ Error resolving require_hq_lq {module_path}.{func_name}: {e}"
                        )
                    return None

            # Handle direct function references (e.g., "function_name")
            elif re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", function_ref.strip()):
                func_name = function_ref.strip()
                try:
                    # Try current module first
                    module = importlib.import_module(current_module)
                    func = getattr(module, func_name, None)
                    if func:
                        print_info(
                            f"  ✓ Resolved direct reference: {current_module}.{func_name}"
                        )
                        return func

                    # Try common action modules
                    action_modules = [
                        "dataset_forge.actions.transform_actions",
                        "dataset_forge.actions.comparison_actions",
                        "dataset_forge.actions.analysis_actions",
                        "dataset_forge.actions.dataset_actions",
                        "dataset_forge.actions.cleanup_actions",
                        "dataset_forge.actions.quality_scoring_actions",
                        "dataset_forge.actions.metadata_actions",
                        "dataset_forge.actions.augmentation_actions",
                        "dataset_forge.actions.bhi_filtering_actions",
                        "dataset_forge.actions.visual_dedup_actions",
                        "dataset_forge.actions.fuzzy_dedup_actions",
                        "dataset_forge.actions.imagededup_actions",
                        "dataset_forge.actions.exif_scrubber_actions",
                        "dataset_forge.actions.orientation_organizer_actions",
                        "dataset_forge.actions.batch_rename_actions",
                        "dataset_forge.actions.hue_adjustment_actions",
                        "dataset_forge.actions.frames_actions",
                        "dataset_forge.actions.report_actions",
                        "dataset_forge.actions.resave_images_actions",
                        "dataset_forge.actions.umzi_dataset_preprocessing_actions",
                        "dataset_forge.actions.align_images_actions",
                        "dataset_forge.actions.openmodeldb_actions",
                        "dataset_forge.actions.model_management_actions",
                        "dataset_forge.actions.settings_actions",
                        "dataset_forge.actions.user_profile_actions",
                        "dataset_forge.actions.enhanced_metadata_actions",
                        "dataset_forge.actions.performance_optimization_actions",
                        "dataset_forge.actions.cache_utils",
                        "dataset_forge.actions.monitoring",
                        "dataset_forge.actions.history_log",
                        "dataset_forge.actions.session_state",
                        # Add menu modules
                        "dataset_forge.menus.dataset_management_menu",
                        "dataset_forge.menus.analysis_menu",
                        "dataset_forge.menus.image_processing_menu",
                        "dataset_forge.menus.training_inference_menu",
                        "dataset_forge.menus.utilities_menu",
                        "dataset_forge.menus.system_settings_menu",
                        "dataset_forge.menus.links_menu",
                        "dataset_forge.menus.monitoring_menu",
                        "dataset_forge.menus.enhanced_metadata_menu",
                        "dataset_forge.menus.performance_optimization_menu",
                    ]

                    for action_module in action_modules:
                        try:
                            module = importlib.import_module(action_module)
                            func = getattr(module, func_name, None)
                            if func:
                                print_info(
                                    f"  ✓ Resolved in {action_module}: {func_name}"
                                )
                                return func
                        except ImportError:
                            continue
                        except Exception as e:
                            print_warning(f"  ✗ Error checking {action_module}: {e}")
                            continue

                    print_warning(
                        f"  ✗ Could not resolve direct reference: {func_name}"
                    )

                except Exception as e:
                    print_warning(
                        f"  ✗ Error resolving direct reference {func_name}: {e}"
                    )
                return None

            # Handle module.function references (e.g., "dataset_actions.combine_datasets")
            elif "." in function_ref and not function_ref.startswith("lazy_"):
                parts = function_ref.split(".")
                if len(parts) == 2:
                    module_name, func_name = parts
                    try:
                        # Try to import the module
                        module = importlib.import_module(module_name)
                        func = getattr(module, func_name, None)
                        if func:
                            print_info(
                                f"  ✓ Resolved module.function: {module_name}.{func_name}"
                            )
                            return func
                        else:
                            print_warning(
                                f"  ✗ Function {func_name} not found in {module_name}"
                            )
                    except ImportError as e:
                        print_warning(f"  ✗ Could not import module {module_name}: {e}")
                    except Exception as e:
                        print_warning(
                            f"  ✗ Error resolving {module_name}.{func_name}: {e}"
                        )
                    return None

            # Handle lambda functions (these are usually simple wrappers)
            elif function_ref.strip() == "<lambda>":
                print_info("  ℹ Lambda function detected (usually a simple wrapper)")
                return None

            # Handle None references
            elif function_ref.strip() == "None":
                print_info("  ℹ None reference detected (exit option)")
                return None

            else:
                print_warning(
                    f"  ✗ Unhandled function reference pattern: {function_ref}"
                )
                return None

        except Exception as e:
            print_error(f"  ✗ Error in resolve_function_reference: {e}")
            return None

    def generate_markdown_report(self, menu_hierarchy: Dict[str, Any]) -> str:
        """Generate a comprehensive markdown report of the menu hierarchy."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Dataset Forge Menu Hierarchy Audit

**Generated on:** {timestamp}  
**Total Menus Explored:** {len(self.visited_menus)}  
**Max Depth Reached:** {self.get_max_depth(menu_hierarchy)}

## Executive Summary

This report provides a comprehensive audit of the Dataset Forge menu hierarchy, including:
- Menu structure and organization
- Navigation patterns and user flow
- Function references and dependencies
- Path input scenarios and user interaction points
- Potential improvements for hierarchy and organization

## Menu Hierarchy

"""

        # Generate hierarchical menu structure
        report += self.generate_menu_tree(menu_hierarchy)

        # Generate detailed menu analysis
        report += "\n## Detailed Menu Analysis\n\n"
        report += self.generate_detailed_analysis(menu_hierarchy)

        return report

    def generate_menu_tree(self, menu_info: Dict[str, Any], indent: int = 0) -> str:
        """Generate a tree representation of the menu hierarchy."""
        if not menu_info or menu_info.get("type") in [
            "error",
            "max_depth_reached",
            "already_visited",
        ]:
            return ""

        indent_str = "  " * indent
        tree = ""

        if menu_info.get("type") == "unresolved_function":
            tree += f"{indent_str}❓ **Unresolved Function** ({menu_info.get('function_ref', 'Unknown')})\n"
            return tree

        title = menu_info.get("metadata", {}).get(
            "title", menu_info.get("function_name", "Unknown")
        )

        # Add path input indicator if this menu has path input
        path_indicator = " 🔗" if menu_info.get("has_path_input", False) else ""
        tree += f"{indent_str}📋 **{title}**{path_indicator}\n"

        if "options" in menu_info:
            for key, (option_text, function_ref) in menu_info["options"].items():
                tree += f"{indent_str}  {key}. {option_text}\n"

        if "submenus" in menu_info:
            for key, submenu_data in menu_info["submenus"].items():
                if "submenu" in submenu_data:
                    tree += self.generate_menu_tree(submenu_data["submenu"], indent + 1)

        return tree

    def generate_detailed_analysis(self, menu_info: Dict[str, Any]) -> str:
        """Generate detailed analysis of each menu."""
        if not menu_info or menu_info.get("type") in [
            "error",
            "max_depth_reached",
            "already_visited",
        ]:
            return ""

        analysis = ""

        if menu_info.get("type") == "unresolved_function":
            analysis += f"### ❓ Unresolved Function\n\n"
            analysis += f"**Function Reference:** `{menu_info.get('function_ref', 'Unknown')}`\n\n"
            analysis += "**Issue:** This function reference could not be resolved during analysis.\n\n"
            return analysis

        title = menu_info.get("metadata", {}).get(
            "title", menu_info.get("function_name", "Unknown")
        )

        # Add path input indicator if this menu has path input
        path_indicator = " 🔗" if menu_info.get("has_path_input", False) else ""
        analysis += f"### 📋 {title}{path_indicator}\n\n"

        # Menu metadata
        metadata = menu_info.get("metadata", {})
        if metadata:
            analysis += "**Metadata:**\n"
            for key, value in metadata.items():
                analysis += f"- **{key}:** {value}\n"
            analysis += "\n"

        # Show path input status
        if menu_info.get("has_path_input", False):
            analysis += "**Path Input:** This menu contains path input scenarios.\n\n"

        # Menu options
        if "options" in menu_info and menu_info["options"]:
            analysis += "**Options:**\n"
            for key, (option_text, function_ref) in menu_info["options"].items():
                analysis += f"- **{key}:** {option_text} → `{function_ref}`\n"
            analysis += "\n"

        # Recursively analyze submenus
        if "submenus" in menu_info:
            for key, submenu_data in menu_info["submenus"].items():
                if "submenu" in submenu_data:
                    analysis += self.generate_detailed_analysis(submenu_data["submenu"])

        return analysis

    def generate_recommendations(self, menu_hierarchy: Dict[str, Any]) -> str:
        """Generate recommendations for menu improvement."""
        recommendations = []

        # Analyze menu depth
        max_depth = self.get_max_depth(menu_hierarchy)
        if max_depth > 5:
            recommendations.append(
                f"⚠️ **Deep Menu Hierarchy:** Maximum depth of {max_depth} levels detected. "
                "Consider flattening the hierarchy for better user experience."
            )

        # Analyze menu size
        large_menus = self.find_large_menus(menu_hierarchy)
        if large_menus:
            recommendations.append(
                f"📊 **Large Menus:** {len(large_menus)} menus have more than 10 options. "
                "Consider grouping related options into submenus."
            )

        # Analyze path input distribution
        path_inputs = self.count_path_inputs(menu_hierarchy)
        if path_inputs > 0:
            recommendations.append(
                f"🔗 **Path Input Points:** {path_inputs} menus require path input. "
                "Consider implementing path history and validation for better UX."
            )

        # Generate recommendations text
        if recommendations:
            return "\n".join(recommendations)
        else:
            return "✅ **No major issues detected.** The menu hierarchy appears well-organized."

    def generate_statistics(self, menu_hierarchy: Dict[str, Any]) -> str:
        """Generate statistics about the menu hierarchy."""
        stats = []

        total_menus = len(self.visited_menus)
        max_depth = self.get_max_depth(menu_hierarchy)
        path_inputs = self.count_path_inputs(menu_hierarchy)
        large_menus = self.find_large_menus(menu_hierarchy)

        stats.append(f"- **Total Menus:** {total_menus}")
        stats.append(f"- **Maximum Depth:** {max_depth} levels")
        stats.append(f"- **Path Input Points:** {path_inputs}")
        stats.append(f"- **Large Menus (>10 options):** {len(large_menus)}")

        return "\n".join(stats)

    def get_max_depth(self, menu_info: Dict[str, Any]) -> int:
        """Get the maximum depth of the menu hierarchy."""
        if not menu_info:
            return 0

        current_depth = menu_info.get("depth", 0)
        max_depth = current_depth

        if "submenus" in menu_info:
            for submenu_data in menu_info["submenus"].values():
                if "submenu" in submenu_data:
                    sub_depth = self.get_max_depth(submenu_data["submenu"])
                    max_depth = max(max_depth, sub_depth)

        return max_depth

    def find_large_menus(self, menu_info: Dict[str, Any]) -> List[str]:
        """Find menus with more than 10 options."""
        large_menus = []

        if not menu_info:
            return large_menus

        if "options" in menu_info and len(menu_info["options"]) > 10:
            title = menu_info.get("metadata", {}).get(
                "title", menu_info.get("function_name", "Unknown")
            )
            large_menus.append(title)

        if "submenus" in menu_info:
            for submenu_data in menu_info["submenus"].values():
                if "submenu" in submenu_data:
                    large_menus.extend(self.find_large_menus(submenu_data["submenu"]))

        return large_menus

    def count_path_inputs(self, menu_info: Dict[str, Any]) -> int:
        """Count the number of path input scenarios."""
        count = 0

        if not menu_info:
            return count

        if menu_info.get("has_path_input", False):
            count += 1

        if "submenus" in menu_info:
            for submenu_data in menu_info["submenus"].values():
                if "submenu" in submenu_data:
                    count += self.count_path_inputs(submenu_data["submenu"])

        return count

    def run_audit(self) -> None:
        """Run the complete menu audit."""
        print_success("🚀 Starting Dataset Forge Menu Audit...")

        # Discover menu files
        print_info("🔍 Discovering menu files...")
        self.menu_files = self.discover_menu_files()
        print_info(f"Found {len(self.menu_files)} menu files")

        # Explore all menus
        try:
            print_info("🔍 Exploring all menus...")
            all_menus = self.explore_all_menus()

            # Use the main menu hierarchy for the main report
            main_hierarchy = all_menus.get("main_menu", {})

            # Generate the report
            print_info("📝 Generating markdown report...")
            report = self.generate_markdown_report(main_hierarchy)

            # Add comprehensive menu listing BEFORE the recommendations and statistics
            report += "\n## All Discovered Menus\n\n"
            for menu_name, menu_info in all_menus.items():
                if menu_name != "main_menu":
                    report += f"### {menu_name}\n"
                    if menu_info.get("type") == "menu":
                        title = menu_info.get("metadata", {}).get("title", menu_name)
                        report += f"**Title:** {title}\n"
                        if "options" in menu_info:
                            report += f"**Options:** {len(menu_info['options'])}\n"
                    elif menu_info.get("type") == "path_input":
                        report += "**Type:** Path Input\n"
                    report += "\n"

            # Add recommendations and statistics sections
            report += "\n## Recommendations for Improvement\n\n"
            report += self.generate_recommendations(main_hierarchy)

            # Generate statistics
            report += "\n## Menu Statistics\n\n"
            report += self.generate_statistics(main_hierarchy)

            # Write the report to file
            # Ensure the logs directory exists
            output_dir = Path(self.output_file).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(report)

            print_success(
                f"✅ Menu audit completed! Report saved to: {self.output_file}"
            )
            print_info(f"📊 Explored {len(self.visited_menus)} menus")
            print_info(
                f"🔗 Found {self.count_path_inputs(main_hierarchy)} path input scenarios"
            )
            print_info(f"📈 Maximum depth: {self.get_max_depth(main_hierarchy)} levels")
            print_info(f"📁 Analyzed {len(all_menus)} total menu functions")

        except Exception as e:
            print_error(f"❌ Menu audit failed: {e}")
            import traceback

            traceback.print_exc()

    def explore_all_menus(self) -> Dict[str, Any]:
        """Explore all menus in the dataset_forge/menus directory."""
        all_menus = {}

        # Start with the main menu
        try:
            from dataset_forge.menus.main_menu import main_menu

            print_info("🔍 Analyzing main menu...")
            main_hierarchy = self.explore_menu_recursively(main_menu, "Main Menu", 0)
            all_menus["main_menu"] = main_hierarchy
        except Exception as e:
            print_error(f"Failed to analyze main menu: {e}")

        # Discover and analyze all menu files
        print_info("🔍 Discovering and analyzing all menu files...")
        for menu_file in self.menu_files:
            try:
                # Debug: print the actual path we're getting
                print_info(f"Processing menu file: {menu_file}")

                # Convert file path to module path properly
                # Handle both forward slashes and backslashes
                normalized_path = menu_file.replace("\\", "/")

                # Remove the dataset_forge/menus/ prefix and .py extension
                if normalized_path.startswith("dataset_forge/menus/"):
                    module_name = normalized_path[
                        19:-3
                    ]  # Remove "dataset_forge/menus/" and ".py"
                elif normalized_path.startswith("/dataset_forge/menus/"):
                    module_name = normalized_path[
                        20:-3
                    ]  # Remove "/dataset_forge/menus/" and ".py"
                elif normalized_path.startswith("./dataset_forge/menus/"):
                    module_name = normalized_path[
                        21:-3
                    ]  # Remove "./dataset_forge/menus/" and ".py"
                else:
                    module_name = normalized_path.replace("/", ".").replace(".py", "")

                # Remove any leading slash from module_name
                if module_name.startswith("/"):
                    module_name = module_name[1:]

                module_path = f"dataset_forge.menus.{module_name}"
                print_info(f"Module path: {module_path}")

                # Find all menu functions in the module
                menu_functions = self.find_menu_functions(module_path)

                for func_name, func in menu_functions:
                    if func_name not in all_menus:
                        try:
                            print_info(f"🔍 Analyzing {module_path}.{func_name}...")
                            menu_info = self.explore_menu_recursively(
                                func, func_name, 0
                            )
                            all_menus[func_name] = menu_info
                        except Exception as e:
                            print_error(
                                f"Failed to analyze {module_path}.{func_name}: {e}"
                            )
                            all_menus[func_name] = {"type": "error", "error": str(e)}

            except Exception as e:
                print_error(f"Failed to process menu file {menu_file}: {e}")

        # Second pass: look for any missed menus by scanning all discovered menus
        print_info("🔍 Second pass: scanning for missed menus...")
        self.second_pass_exploration(all_menus)

        return all_menus

    def second_pass_exploration(self, all_menus: Dict[str, Any]) -> None:
        """Second pass to ensure all menus are explored."""
        print_info("🔍 Second pass: scanning for missed menus...")

        # Collect all function references from all menus
        all_references = set()

        def collect_references(menu_info: Dict[str, Any]) -> None:
            """Collect all function references from a menu."""
            if not menu_info or menu_info.get("type") in [
                "error",
                "max_depth_reached",
                "already_visited",
            ]:
                return

            if "options" in menu_info:
                for option_data in menu_info["options"].values():
                    if isinstance(option_data, tuple) and len(option_data) > 1:
                        func_ref = str(option_data[1])
                        if func_ref and func_ref != "None":
                            all_references.add(func_ref)

            if "submenus" in menu_info:
                for submenu_data in menu_info["submenus"].values():
                    if "submenu" in submenu_data:
                        collect_references(submenu_data["submenu"])

        # Collect all references
        for menu_info in all_menus.values():
            collect_references(menu_info)

        print_info(f"🔍 Found {len(all_references)} function references to check...")

        # Try to resolve and explore any missed menus
        for func_ref in all_references:
            try:
                # Try to resolve the function reference
                func = self.resolve_function_reference(
                    func_ref, "dataset_forge.menus.main_menu"
                )
                if func and callable(func):
                    # Check if this function is a menu function
                    func_name = func.__name__
                    if (
                        func_name not in all_menus
                        and func_name not in self.visited_menus
                    ):
                        try:
                            print_info(f"🔍 Second pass: analyzing {func_name}...")
                            menu_info = self.explore_menu_recursively(
                                func, func_name, 0
                            )
                            all_menus[func_name] = menu_info
                        except Exception as e:
                            print_warning(
                                f"Failed to analyze {func_name} in second pass: {e}"
                            )
            except Exception as e:
                # Skip if we can't resolve it
                continue

        # Third pass: scan all menu files for any missed menu functions
        print_info("🔍 Third pass: scanning all menu files for missed functions...")
        for menu_file in self.menu_files:
            try:
                # Convert file path to module path
                normalized_path = menu_file.replace("\\", "/")

                if normalized_path.startswith("dataset_forge/menus/"):
                    module_name = normalized_path[19:-3]
                elif normalized_path.startswith("/dataset_forge/menus/"):
                    module_name = normalized_path[20:-3]
                elif normalized_path.startswith("./dataset_forge/menus/"):
                    module_name = normalized_path[21:-3]
                else:
                    module_name = normalized_path.replace("/", ".").replace(".py", "")

                if module_name.startswith("/"):
                    module_name = module_name[1:]

                module_path = f"dataset_forge.menus.{module_name}"

                # Find all menu functions in the module
                menu_functions = self.find_menu_functions(module_path)

                for func_name, func in menu_functions:
                    if (
                        func_name not in all_menus
                        and func_name not in self.visited_menus
                    ):
                        try:
                            print_info(
                                f"🔍 Third pass: analyzing {module_path}.{func_name}..."
                            )
                            menu_info = self.explore_menu_recursively(
                                func, func_name, 0
                            )
                            all_menus[func_name] = menu_info
                        except Exception as e:
                            print_warning(
                                f"Failed to analyze {module_path}.{func_name} in third pass: {e}"
                            )

            except Exception as e:
                print_warning(f"Failed to process {menu_file} in third pass: {e}")
                continue


def main():
    """Main entry point for the menu auditing tool."""
    print_success("🎨 Dataset Forge Menu Auditor")
    print_info("This tool will analyze all menus and generate a comprehensive report.")

    auditor = MenuAuditor()
    auditor.run_audit()


if __name__ == "__main__":
    main()
