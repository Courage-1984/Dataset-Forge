#!/usr/bin/env python3
"""
Documentation merger for Dataset Forge.

This script merges all documentation files into a single comprehensive document.
"""

import os
import re
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

    return 0


if __name__ == "__main__":
    exit(main())
