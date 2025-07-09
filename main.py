import logging
from dataset_forge.menus.main_menu import (
    main_menu,
    progressive_validation_menu,
    rich_reports_menu,  # NEW: Rich Reports
)
from dataset_forge.menus.links_menu import links_menu  # NEW
from dataset_forge.menus.correct_hq_lq_pairing_menu import (
    correct_hq_lq_pairing_menu,
    fuzzy_hq_lq_pairing_menu,  # NEW: Fuzzy HQ/LQ Pairing
)  # NEW: Correct/Create HQ LQ Pairing
from dataset_forge.menus.history_log_menu import history_log_menu  # NEW
from dataset_forge.menus.outlier_detection_menu import outlier_detection_menu  # NEW
from dataset_forge.menus.quality_scoring_menu import (
    quality_scoring_menu,
)  # NEW: Automated Dataset Quality Scoring
from dataset_forge.menus.visual_dedup_menu import visual_dedup_menu  # NEW: Visual Deduplication

# from dataset_forge.menus.compress_menu import compress_menu  # (To be implemented)

# Path history is now integrated: all path entry points support history, HQ/LQ selection, and progress bars where relevant.

# NEW: 'Test Aspect Ratio' is now available in the Analysis menu (option 12)

if __name__ == "__main__":
    # Minimal global logging to console. Functions can add specific file handlers.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main_menu()
