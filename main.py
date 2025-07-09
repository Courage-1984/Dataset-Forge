import logging
from dataset_forge.menus.main_menu import main_menu
from dataset_forge.menus.links_menu import links_menu  # NEW
from dataset_forge.menus.correct_hq_lq_pairing_menu import (
    correct_hq_lq_pairing_menu,
)  # NEW: Correct/Create HQ LQ Pairing

# from dataset_forge.menus.compress_menu import compress_menu  # (To be implemented)

# Path history is now integrated: all path entry points support history, HQ/LQ selection, and progress bars where relevant.

if __name__ == "__main__":
    # Minimal global logging to console. Functions can add specific file handlers.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main_menu()
