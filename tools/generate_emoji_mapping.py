import re
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from dataset_forge.utils.printing import print_success

EMOJI_TEST_PATH = "docs/emoji-test.txt"
PYTHON_DICT_PATH = "dataset_forge/utils/emoji_mapping.py"
JSON_PATH = "dataset_forge/utils/emoji_mapping.json"

# Regex to match lines like:
# 1F600 ; fully-qualified     # 😀 E1.0 grinning face
EMOJI_LINE_RE = re.compile(
    r"^([0-9A-F ]+);\s*fully-qualified\s*#\s*(\S+)\s+E[\d.]+\s+(.+)$"
)


def parse_emoji_test(path):
    mapping = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = EMOJI_LINE_RE.match(line)
            if m:
                # codepoints = m.group(1)  # not used here
                emoji = m.group(2)
                description = m.group(3)
                # Use only the first word of the description if possible, else keep as is
                short_desc = description.split()[0].lower() if description else "emoji"
                mapping[emoji] = short_desc
    return mapping


def write_python_dict(mapping, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Auto-generated emoji mapping: {emoji: short_description}\n")
        f.write("EMOJI_TO_DESC = {\n")
        for emoji, desc in mapping.items():
            f.write(f"    {repr(emoji)}: {repr(desc)},\n")
        f.write("}\n")


def write_json(mapping, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def main():
    mapping = parse_emoji_test(EMOJI_TEST_PATH)
    write_python_dict(mapping, PYTHON_DICT_PATH)
    write_json(mapping, JSON_PATH)
    print_success(f"Wrote {len(mapping)} emoji mappings to {PYTHON_DICT_PATH} and {JSON_PATH}")


if __name__ == "__main__":
    main()
