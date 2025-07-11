import time
import sys

start_time = time.time()
print(f"Time 0: {time.time() - start_time:.2f} seconds")

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

print(f"Before importing main_menu: {time.time() - start_time:.2f} seconds")

from dataset_forge.menus.main_menu import main_menu

print(f"After importing main_menu: {time.time() - start_time:.2f} seconds")
print("Startup test completed!")
