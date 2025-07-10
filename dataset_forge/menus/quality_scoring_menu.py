from dataset_forge.actions.quality_scoring_actions import (
    score_images_with_pyiqa,
    plot_quality_histogram,
    filter_images_by_quality,
    score_hq_lq_folders,
)
from dataset_forge.utils.input_utils import get_path_with_history
from dataset_forge.utils.printing import print_info, print_success, print_error
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha


def quality_scoring_menu():
    options = quality_scoring_menu.__menu_options__
    while True:
        action = show_menu(
            "Automated Dataset Quality Scoring",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if action is None:
            break
        action()


# Register a static menu for favorites (customize as needed)
quality_scoring_menu.__menu_options__ = {
    "1": ("Run Quality Scoring Workflow", lambda: None),
    "0": ("Back to Main Menu", None),
}
