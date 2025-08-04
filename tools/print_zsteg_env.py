#!/usr/bin/env python3
"""
Print zsteg environment information for debugging.
"""

import os
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from dataset_forge.utils.printing import print_info

print_info("PYTHON PATH: " + os.environ["PATH"])
print_info("ZSTEG FOUND AT: " + str(shutil.which("zsteg")))
print_info(str(shutil.which("zsteg")))
