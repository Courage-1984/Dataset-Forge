#!/usr/bin/env python3
"""
Tools Launcher for Dataset Forge

This script provides a menu-driven interface to run various development tools.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dataset_forge.utils.printing import (
        print_info,
        print_success,
        print_warning,
        print_error,
        print_header,
        print_section,
    )
    from dataset_forge.utils.color import Mocha
    from dataset_forge.utils.audio_utils import play_error_sound
    from dataset_forge.utils.menu import show_menu, handle_global_command
except ImportError:
    # Fallback for when running outside Dataset Forge environment
    def print_header(msg: str):
        print(f"\n{'='*60}")
        print(f"  {msg}")
        print(f"{'='*60}")

    def print_info(msg: str):
        print(f"[INFO] {msg}")

    def print_success(msg: str):
        print(f"[SUCCESS] {msg}")

    def print_warning(msg: str):
        print(f"[WARNING] {msg}")

    def print_error(msg: str):
        print(f"[ERROR] {msg}")

    def print_section(msg: str):
        print_info(f"\n--- {msg} ---")

    class Mocha:
        lavender = "\033[95m"
        blue = "\033[94m"
        green = "\033[92m"
        yellow = "\033[93m"
        red = "\033[91m"
        reset = "\033[0m"

    def play_error_sound():
        pass

    def show_menu(title, options, color, current_menu="", menu_context=None):
        print_header(title)
        for key, (description, _) in options.items():
            print_info(f"{key}. {description}")
        return input(f"\nSelect option (0 to exit): ").strip()

    def handle_global_command(command, current_menu="", menu_context=None, pause=True):
        if command and command.lower() in ["help", "h", "?"]:
            print_section("Help")
            print_info("Available commands:")
            print_info("- help, h, ?: Show this help")
            print_info("- quit, exit, q: Exit the launcher")
            print_info("- 0: Go back/exit")
            if pause:
                input("\nPress Enter to continue...")
            return True
        elif command and command.lower() in ["quit", "exit", "q"]:
            print_info("Exiting tools launcher...")
            sys.exit(0)
        return False


class ToolInfo:
    """Information about a development tool."""

    def __init__(self, name: str, path: Path, description: str = ""):
        self.name = name
        self.path = path
        self.description = description
        self._docstring = None

    @property
    def docstring(self) -> str:
        """Get the docstring from the tool file."""
        if self._docstring is None:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extract docstring
                    lines = content.split("\n")
                    doc_lines = []
                    in_docstring = False
                    quote_char = None

                    for line in lines:
                        stripped = line.strip()
                        if not in_docstring:
                            if stripped.startswith('"""') or stripped.startswith("'''"):
                                in_docstring = True
                                quote_char = stripped[:3]
                                doc_content = stripped[3:]
                                if doc_content.endswith(quote_char):
                                    doc_lines.append(doc_content[:-3])
                                    break
                                else:
                                    doc_lines.append(doc_content)
                        else:
                            if stripped.endswith(quote_char):
                                doc_lines.append(stripped[:-3])
                                break
                            else:
                                doc_lines.append(stripped)

                    self._docstring = "\n".join(doc_lines).strip()
            except Exception:
                self._docstring = ""

        return self._docstring

    def get_short_description(self) -> str:
        """Get a short description for the menu."""
        if self.description:
            return self.description

        # Try to extract first line of docstring
        doc = self.docstring
        if doc:
            first_line = doc.split("\n")[0].strip()
            if first_line:
                return first_line[:60] + "..." if len(first_line) > 60 else first_line

        return f"Run {self.name}"


class ToolsLauncher:
    """Main tools launcher class."""

    def __init__(self):
        self.tools_dir = Path(__file__).parent
        self.tools: Dict[str, ToolInfo] = {}
        self.discover_tools()

    def discover_tools(self):
        """Discover all available tools in the tools directory."""
        print_info("Discovering available tools...")

        # Define known tools with descriptions
        known_tools = {
            "find_code_issues.py": "Comprehensive static analysis for code quality and issues",
            "run_tests.py": "Flexible test runner with multiple execution modes",
            "install.py": "Installation and setup script for Dataset Forge",
            "merge_docs.py": "Documentation merging and organization tool",
            "log_current_menu.py": "Menu hierarchy auditing and analysis tool",
            "print_zsteg_env.py": "Environment checker for zsteg tool",
            "check_mocha_theming.py": "Check Catppuccin Mocha theming consistency across codebase",
            "find_alpha_images.py": "Find images with alpha channels in directories",
        }

        for file_path in self.tools_dir.glob("*.py"):
            if file_path.name == "__init__.py" or file_path.name == "launcher.py":
                continue

            tool_name = file_path.stem
            description = known_tools.get(file_path.name, "")

            tool_info = ToolInfo(tool_name, file_path, description)
            self.tools[tool_name] = tool_info

        print_success(f"Discovered {len(self.tools)} tools")

    def run_tool(self, tool_name: str, args: List[str] = None) -> bool:
        """Run a specific tool with optional arguments."""
        if tool_name not in self.tools:
            print_error(f"Tool '{tool_name}' not found")
            return False

        tool_info = self.tools[tool_name]
        tool_path = tool_info.path

        print_section(f"Running {tool_name}")
        print_info(f"Tool: {tool_path}")

        if tool_info.docstring:
            print_info("Description:")
            print_info(f"  {tool_info.docstring}")

        # Prepare command
        cmd = [sys.executable, str(tool_path)]
        if args:
            cmd.extend(args)

        print_info(f"Command: {' '.join(cmd)}")
        print_info("")

        try:
            # Run the tool
            result = subprocess.run(cmd, cwd=project_root)

            if result.returncode == 0:
                print_success(f"Tool '{tool_name}' completed successfully")
                return True
            else:
                print_error(
                    f"Tool '{tool_name}' failed with exit code {result.returncode}"
                )
                play_error_sound()
                return False

        except KeyboardInterrupt:
            print_warning(f"Tool '{tool_name}' was interrupted by user")
            return False
        except Exception as e:
            print_error(f"Failed to run tool '{tool_name}': {e}")
            play_error_sound()
            return False

    def show_tool_details(self, tool_name: str):
        """Show detailed information about a specific tool."""
        if tool_name not in self.tools:
            print_error(f"Tool '{tool_name}' not found")
            return

        tool_info = self.tools[tool_name]

        print_section(f"Tool Details: {tool_name}")
        print_info(f"File: {tool_info.path}")
        print_info(f"Size: {tool_info.path.stat().st_size:,} bytes")

        if tool_info.docstring:
            print_info("Documentation:")
            print_info(f"  {tool_info.docstring}")
        else:
            print_warning("No documentation found")

    def show_main_menu(self):
        """Show the main tools selection menu."""
        options = {}

        # Add tools to options
        for i, (tool_name, tool_info) in enumerate(self.tools.items(), 1):
            options[str(i)] = (f"🔧 {tool_info.get_short_description()}", tool_name)

        # Add utility options
        options["d"] = ("📋 Show tool details", "details")
        options["r"] = ("🔄 Refresh tool list", "refresh")
        options["0"] = ("🚪 Exit", None)

        # Define menu context for help system
        menu_context = {
            "Purpose": "Launch and manage development tools for Dataset Forge",
            "Options": f"{len(self.tools)} tools available",
            "Navigation": "Use numbers to select tools, 'd' for details, 'r' to refresh, 0 to exit",
            "Key Features": [
                "Automatic tool discovery from ./tools/ directory",
                "Direct tool execution with proper environment",
                "Tool documentation and details view",
                "Command-line argument support",
                "Error handling and audio feedback",
            ],
            "Tips": [
                "Use 'd' to see detailed information about tools before running",
                "Tools run in the project root directory",
                "Use Ctrl+C to interrupt running tools",
                "Check tool documentation for usage instructions",
            ],
        }

        while True:
            try:
                key = show_menu(
                    "Dataset Forge Tools Launcher",
                    options,
                    Mocha.lavender,
                    current_menu="Tools Launcher",
                    menu_context=menu_context,
                )

                if key is None or key == "0":
                    print_info("Exiting tools launcher...")
                    break

                if key == "d":
                    self.show_details_menu()
                    continue

                if key == "r":
                    self.discover_tools()
                    print_success("Tool list refreshed")
                    continue

                if key in options:
                    action = options[key][1]
                    if action == "details":
                        self.show_details_menu()
                    elif action == "refresh":
                        self.discover_tools()
                        print_success("Tool list refreshed")
                    elif action is not None:
                        self.run_tool(action)
                        input("\nPress Enter to continue...")
                else:
                    print_error("Invalid selection")

            except (KeyboardInterrupt, EOFError):
                print_info("\nExiting...")
                break

    def show_details_menu(self):
        """Show menu for viewing tool details."""
        options = {}

        for i, (tool_name, tool_info) in enumerate(self.tools.items(), 1):
            options[str(i)] = (f"📋 {tool_name}", tool_name)

        options["0"] = ("⬅️ Back", None)

        menu_context = {
            "Purpose": "View detailed information about development tools",
            "Options": f"{len(self.tools)} tools available",
            "Navigation": "Use numbers to select tools, 0 to go back",
            "Key Features": [
                "View tool file paths and sizes",
                "Display tool documentation and docstrings",
                "Show tool descriptions and usage information",
            ],
            "Tips": [
                "Use this menu to understand what each tool does before running it",
                "Check documentation for usage instructions and requirements",
            ],
        }

        while True:
            try:
                key = show_menu(
                    "Tool Details",
                    options,
                    Mocha.blue,
                    current_menu="Tool Details",
                    menu_context=menu_context,
                )

                if key is None or key == "0":
                    break

                if key in options:
                    action = options[key][1]
                    if action is not None:
                        self.show_tool_details(action)
                        input("\nPress Enter to continue...")
                else:
                    print_error("Invalid selection")

            except (KeyboardInterrupt, EOFError):
                print_info("\nExiting...")
                break


def main():
    """Main entry point for the tools launcher."""
    # Handle command-line arguments
    if len(sys.argv) > 1:
        tool_name = sys.argv[1]
        args = sys.argv[2:] if len(sys.argv) > 2 else []

        launcher = ToolsLauncher()
        if tool_name in launcher.tools:
            success = launcher.run_tool(tool_name, args)
            sys.exit(0 if success else 1)
        else:
            print_error(f"Tool '{tool_name}' not found")
            print_info("Available tools:")
            for tool_name in launcher.tools.keys():
                print_info(f"  - {tool_name}")
            sys.exit(1)

    # Interactive mode
    print_header("Dataset Forge Tools Launcher")
    print_info("Welcome to the Dataset Forge development tools launcher!")
    print_info("This tool helps you discover and run various development utilities.")

    launcher = ToolsLauncher()
    launcher.show_main_menu()


if __name__ == "__main__":
    main()
