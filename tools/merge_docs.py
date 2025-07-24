import os
import sys
import re

# Always resolve docs/ relative to the project root (parent of this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
OUTPUT_FILE = os.path.join(DOCS_DIR, "README_full.md")
TOC_FILE = os.path.join(DOCS_DIR, "toc.md")

# Order of files to merge (edit as needed)
DOC_ORDER = [
    "special_installation.md",
    "features.md",
    "usage.md",
    "advanced.md",
    "architecture.md",
    "troubleshooting.md",
    "style_guide.md",
    "contributing.md",
    "faq.md",
    "changelog.md",
    "license.md",
]


NAV_LINKS = (
    "[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | "
    "[Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | "
    "[Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)\n"
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

    print(f"README_full.md and toc.md updated with hierarchical ToC.")


if __name__ == "__main__":
    main()
