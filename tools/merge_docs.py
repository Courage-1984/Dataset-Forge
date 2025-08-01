# This script merges all documentation files in docs/ into a single README_full.md and generates a hierarchical Table of Contents (toc.md).
# It also copies the .cursorrules file to .cursor/rules/ directory for Cursor IDE integration.
# To add new documentation files, update DOC_ORDER below and ensure navigation links are consistent.

import os
import sys
import re
import shutil

# Always resolve docs/ relative to the project root (parent of this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
OUTPUT_FILE = os.path.join(DOCS_DIR, "README_full.md")
TOC_FILE = os.path.join(DOCS_DIR, "toc.md")
CURSORRULES_SOURCE = os.path.join(PROJECT_ROOT, ".cursorrules")
CURSORRULES_DEST = os.path.join(PROJECT_ROOT, ".cursor", "rules", ".cursorrules")
CURSORRULES_MDC_SOURCE = os.path.join(PROJECT_ROOT, "cursorrules.mdc")
CURSORRULES_MDC_DEST = os.path.join(PROJECT_ROOT, ".cursor", "rules", "cursorrules.mdc")

# Order of files to merge (edit as needed)
DOC_ORDER = [
    "README.md",  # Project landing page
    "index.md",  # Documentation home
    "getting_started.md",  # Install & setup
    "special_installation.md",  # Special installation instructions
    "features.md",  # Features overview
    "TODO.md",  # TODO list
    "usage.md",  # Usage guide
    "advanced.md",  # Advanced features
    "architecture.md",  # Project architecture
    "troubleshooting.md",  # Troubleshooting & FAQ
    "style_guide.md",  # Coding & style guide
    "contributing.md",  # Contributing guide
    "changelog.md",  # Changelog
    "license.md",  # License
]

NAV_LINKS = (
    "[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | "
    "[Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | "
    "[Style Guide](style_guide.md) | [Contributing](contributing.md) | [Changelog](changelog.md) | [ToC](toc.md)\n"
)


# Helper to create anchor links in GitHub style
# (lowercase, spaces to -, remove non-alphanum except -)
def anchor_link(text):
    anchor = text.strip().lower()
    anchor = re.sub(r"[\s]+", "-", anchor)
    anchor = re.sub(r"[^a-z0-9\-]", "", anchor)
    return anchor


# Parse headings from a markdown file, return list of (level, text, anchor)
def parse_headings(md_path):
    headings = []
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^(#+) (.+)", line)
            if m:
                level = len(m.group(1))
                text = m.group(2).strip()
                anchor = anchor_link(text)
                headings.append((level, text, anchor))
    return headings


# Build hierarchical ToC for all docs
def build_toc():
    toc_lines = ["# Table of Contents\n"]
    for doc in DOC_ORDER:
        doc_path = os.path.join(DOCS_DIR, doc)
        if not os.path.exists(doc_path):
            continue
        doc_headings = parse_headings(doc_path)
        if not doc_headings:
            continue
        # Top-level entry for the file
        main_title = (
            doc_headings[0][1]
            if doc_headings[0][0] == 1
            else os.path.splitext(doc)[0].replace("_", " ").title()
        )
        toc_lines.append(f"- [{main_title}]({doc})")
        prev_level = 1
        for level, text, anchor in doc_headings[1:]:
            indent = "  " * (level - 1)
            toc_lines.append(f"{indent}- [{text}]({doc}#{anchor})")
    return "\n".join(toc_lines) + "\n"


def strip_nav_links(content):
    """Remove the navigation links from the top of a doc file."""
    lines = content.splitlines()
    # Remove the first line if it matches the nav links pattern
    if lines and lines[0].startswith("[← Main README]"):
        return "\n".join(lines[1:]).lstrip()
    return content


def update_cursorrules_mdc():
    """Update cursorrules.mdc with content from .cursorrules after the YAML block."""
    if not os.path.exists(CURSORRULES_SOURCE):
        print(f"Warning: {CURSORRULES_SOURCE} not found, skipping cursorrules.mdc update.")
        return False
    
    if not os.path.exists(CURSORRULES_MDC_SOURCE):
        print(f"Warning: {CURSORRULES_MDC_SOURCE} not found, skipping cursorrules.mdc update.")
        return False
    
    try:
        # Read .cursorrules content
        with open(CURSORRULES_SOURCE, 'r', encoding='utf-8') as f:
            cursorrules_content = f.read()
        
        # Read cursorrules.mdc content
        with open(CURSORRULES_MDC_SOURCE, 'r', encoding='utf-8') as f:
            mdc_content = f.read()
        
        # Find the YAML block end (second occurrence of ---)
        lines = mdc_content.splitlines()
        yaml_end_index = -1
        dash_count = 0
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                dash_count += 1
                if dash_count == 2:  # Second occurrence of ---
                    yaml_end_index = i
                    break
        
        if yaml_end_index == -1:
            print("Warning: Could not find YAML block end in cursorrules.mdc, skipping update.")
            return False
        
        # Reconstruct the file with YAML block + .cursorrules content
        yaml_block = lines[:yaml_end_index + 1]  # Include the closing ---
        updated_content = '\n'.join(yaml_block) + '\n\n' + cursorrules_content
        
        # Write back to cursorrules.mdc
        with open(CURSORRULES_MDC_SOURCE, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ cursorrules.mdc updated with .cursorrules content")
        return True
        
    except Exception as e:
        print(f"❌ Error updating cursorrules.mdc: {e}")
        return False


def copy_cursorrules():
    """Copy .cursorrules to .cursor/rules/ directory."""
    if not os.path.exists(CURSORRULES_SOURCE):
        print(f"Warning: {CURSORRULES_SOURCE} not found, skipping cursorrules copy.")
        return False
    
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(CURSORRULES_DEST), exist_ok=True)
    
    try:
        shutil.copy2(CURSORRULES_SOURCE, CURSORRULES_DEST)
        print(f"✅ .cursorrules copied to {CURSORRULES_DEST}")
        return True
    except Exception as e:
        print(f"❌ Error copying .cursorrules: {e}")
        return False


def copy_cursorrules_mdc():
    """Copy cursorrules.mdc to .cursor/rules/ directory."""
    if not os.path.exists(CURSORRULES_MDC_SOURCE):
        print(f"Warning: {CURSORRULES_MDC_SOURCE} not found, skipping cursorrules.mdc copy.")
        return False
    
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(CURSORRULES_MDC_DEST), exist_ok=True)
    
    try:
        shutil.copy2(CURSORRULES_MDC_SOURCE, CURSORRULES_MDC_DEST)
        print(f"✅ cursorrules.mdc copied to {CURSORRULES_MDC_DEST}")
        return True
    except Exception as e:
        print(f"❌ Error copying cursorrules.mdc: {e}")
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
            print(f"Warning: {doc} not found, skipping.")
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()
        content = strip_nav_links(content)
        # Add a section header for clarity
        section_title = os.path.splitext(doc)[0].replace("_", " ").title()
        merged.append(f"\n# {section_title}\n\n")
        merged.append(content)
        merged.append("\n---\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(merged))

    with open(TOC_FILE, "w", encoding="utf-8") as f:
        f.write(toc)

    # Update cursorrules.mdc with .cursorrules content
    update_cursorrules_mdc()
    
    # Copy .cursorrules to .cursor/rules/
    copy_cursorrules()
    
    # Copy cursorrules.mdc to .cursor/rules/
    copy_cursorrules_mdc()

    print(f"README_full.md and toc.md updated with hierarchical ToC.")


if __name__ == "__main__":
    main()
