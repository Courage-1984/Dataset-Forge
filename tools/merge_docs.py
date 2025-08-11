#!/usr/bin/env python3
"""
Documentation merger for Dataset Forge.

This script merges all documentation files into a single comprehensive document.
"""

import os
import re
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
import sys

sys.path.insert(0, str(project_root))

from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)

# Configuration
DOCS_DIR = "docs"
OUTPUT_FILE = "docs/README_full.md"
TOC_FILE = "docs/toc.md"

# Documentation files in order
DOC_ORDER = [
    "index.md",
    "getting_started.md",
    "features.md",
    "usage.md",
    "advanced.md",
    "architecture.md",
    "contributing.md",
    "style_guide.md",
    "troubleshooting.md",
    "TODO.md",
    "special_installation.md",
    "changelog.md",
    "license.md",
]

# Navigation links
NAV_LINKS = """[← Back to README](../README.md) | [↑ Table of Contents](#dataset-forge-full-documentation) | [→ Next Section](getting_started.md)

---

"""

# Cursorrules paths
CURSORRULES_SOURCE = ".cursorrules"
CURSORRULES_MDC_SOURCE = "cursorrules.mdc"
CURSORRULES_DEST = ".cursor/rules/.cursorrules"
CURSORRULES_MDC_DEST = ".cursor/rules/cursorrules.mdc"


def anchor_link(text):
    """Convert text to anchor link format."""
    # Remove special characters and convert spaces to hyphens
    anchor = re.sub(r"[^\w\s-]", "", text.lower())
    anchor = re.sub(r"[-\s]+", "-", anchor)
    return anchor.strip("-")


def parse_headings(md_path):
    """Parse markdown file and extract headings."""
    headings = []
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
            for line in lines:
                if line.startswith("#"):
                    level = len(line) - len(line.lstrip("#"))
                    title = line.lstrip("#").strip()
                    if title:
                        headings.append((level, title))
    except Exception as e:
        print_error(f"Error parsing {md_path}: {e}")
    return headings


def build_toc():
    """Build table of contents from all documentation files."""
    toc_lines = []

    for doc in DOC_ORDER:
        path = os.path.join(DOCS_DIR, doc)
        if os.path.exists(path):
            headings = parse_headings(path)
            if headings:
                # Add document title
                doc_title = doc.replace(".md", "").replace("_", " ").title()
                toc_lines.append(f"\n## {doc_title}\n")

                # Add headings
                for level, title in headings:
                    indent = "  " * (level - 1)
                    anchor = anchor_link(title)
                    toc_lines.append(f"{indent}- [{title}](#{anchor})")

    return "\n".join(toc_lines)


def strip_nav_links(content):
    """Remove navigation links from content."""
    # Remove the navigation links pattern
    content = re.sub(r"\[← Back to README\].*?---\s*\n", "", content, flags=re.DOTALL)
    return content


def update_cursorrules_mdc():
    """Update cursorrules.mdc with content from .cursorrules after the YAML block."""
    if not os.path.exists(CURSORRULES_SOURCE):
        print_warning(
            f"{CURSORRULES_SOURCE} not found, skipping cursorrules.mdc update."
        )
        return False

    if not os.path.exists(CURSORRULES_MDC_SOURCE):
        print_warning(
            f"{CURSORRULES_MDC_SOURCE} not found, skipping cursorrules.mdc update."
        )
        return False

    try:
        # Read .cursorrules content
        with open(CURSORRULES_SOURCE, "r", encoding="utf-8") as f:
            cursorrules_content = f.read()

        # Read cursorrules.mdc content
        with open(CURSORRULES_MDC_SOURCE, "r", encoding="utf-8") as f:
            mdc_content = f.read()

        # Find the YAML block end (second occurrence of ---)
        lines = mdc_content.splitlines()
        yaml_end_index = -1
        dash_count = 0

        for i, line in enumerate(lines):
            if line.strip() == "---":
                dash_count += 1
                if dash_count == 2:  # Second occurrence of ---
                    yaml_end_index = i
                    break

        if yaml_end_index == -1:
            print_warning(
                "Could not find YAML block end in cursorrules.mdc, skipping update."
            )
            return False

        # Reconstruct the file with YAML block + .cursorrules content
        yaml_block = lines[: yaml_end_index + 1]  # Include the closing ---
        updated_content = "\n".join(yaml_block) + "\n\n" + cursorrules_content

        # Write back to cursorrules.mdc
        with open(CURSORRULES_MDC_SOURCE, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print_success(f"cursorrules.mdc updated with .cursorrules content")
        return True

    except Exception as e:
        print_error(f"Error updating cursorrules.mdc: {e}")
        return False


def copy_cursorrules():
    """Copy .cursorrules to .cursor/rules/ directory."""
    if not os.path.exists(CURSORRULES_SOURCE):
        print_warning(f"{CURSORRULES_SOURCE} not found, skipping cursorrules copy.")
        return False

    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(CURSORRULES_DEST), exist_ok=True)

    try:
        shutil.copy2(CURSORRULES_SOURCE, CURSORRULES_DEST)
        print_success(f".cursorrules copied to {CURSORRULES_DEST}")
        return True
    except Exception as e:
        print_error(f"Error copying .cursorrules: {e}")
        return False


def copy_cursorrules_mdc():
    """Copy cursorrules.mdc to .cursor/rules/ directory."""
    if not os.path.exists(CURSORRULES_MDC_SOURCE):
        print_warning(
            f"{CURSORRULES_MDC_SOURCE} not found, skipping cursorrules.mdc copy."
        )
        return False

    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(CURSORRULES_MDC_DEST), exist_ok=True)

    try:
        shutil.copy2(CURSORRULES_MDC_SOURCE, CURSORRULES_MDC_DEST)
        print_success(f"cursorrules.mdc copied to {CURSORRULES_MDC_DEST}")
        return True
    except Exception as e:
        print_error(f"Error copying cursorrules.mdc: {e}")
        return False


def main():
    merged = []
    toc = build_toc()
    merged.append(NAV_LINKS)
    merged.append("\n# Dataset Forge Full Documentation\n\n---\n")
    merged.append(toc)
    merged.append("\n---\n")

    for doc in DOC_ORDER:
        path = os.path.join(DOCS_DIR, doc)
        if not os.path.exists(path):
            print_warning(f"{doc} not found, skipping.")
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Strip navigation links
            content = strip_nav_links(content)

            # Add document content
            merged.append(f"\n# {doc.replace('.md', '').replace('_', ' ').title()}\n\n")
            merged.append(content)
            merged.append("\n---\n")

        except Exception as e:
            print_error(f"Error reading {doc}: {e}")
            continue

    # Write merged content
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("".join(merged))

        # Write separate toc.md file
        with open(TOC_FILE, "w", encoding="utf-8") as f:
            f.write("# Dataset Forge Documentation - Table of Contents\n\n")
            f.write(toc)

        print_success(f"README_full.md and toc.md updated with hierarchical ToC.")
    except Exception as e:
        print_error(f"Error writing merged documentation: {e}")
        return 1

    # Update cursorrules files
    update_cursorrules_mdc()
    copy_cursorrules()
    copy_cursorrules_mdc()

    return 0


if __name__ == "__main__":
    exit(main())
