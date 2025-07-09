import os
import logging
import random
from dataset_forge.utils.file_utils import is_image_file

# Setup logging for better error reporting in background tasks
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
