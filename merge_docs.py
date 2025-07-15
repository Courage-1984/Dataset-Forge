import os

DOCS_DIR = "docs"
OUTPUT_FILE = os.path.join(DOCS_DIR, "README_full.md")

# Order of files to merge (edit as needed)
DOC_ORDER = [
    "features.md",
    "usage.md",
    "advanced.md",
    "architecture.md",
    "troubleshooting.md",
    "style_guide.md",
    "changelog.md",
    "contributing.md",
    "faq.md",
    "license.md",
]

NAV_LINKS = (
    "[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | "
    "[Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | "
    "[Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)\n"
)

TOC = (
    "# Table of Contents\n\n"
    "- [Features](features.md)\n"
    "- [Usage Guide](usage.md)\n"
    "- [Advanced Features & Configuration](advanced.md)\n"
    "- [Project Architecture](architecture.md)\n"
    "- [Troubleshooting](troubleshooting.md)\n"
    "- [Style Guide](style_guide.md)\n"
    "- [Changelog](changelog.md)\n"
    "- [Contributing](contributing.md)\n"
    "- [FAQ](faq.md)\n"
    "- [License](license.md)\n"
)


def strip_nav_links(content):
    """Remove the navigation links from the top of a doc file."""
    lines = content.splitlines()
    # Remove the first line if it matches the nav links pattern
    if lines and lines[0].startswith("[← Main README]"):
        return "\n".join(lines[1:]).lstrip()
    return content


def main():
    merged = []
    merged.append(NAV_LINKS)
    merged.append("\n# Dataset Forge Full Documentation\n\n---\n")
    merged.append(TOC)
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

    print(f"README_full.md updated with merged documentation.")


if __name__ == "__main__":
    main()
