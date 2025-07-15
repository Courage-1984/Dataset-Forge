from dataset_forge.utils.input_utils import get_path_with_history
from dataset_forge.utils.printing import print_info, print_success, print_error
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha


def quality_scoring_menu():
    from dataset_forge.actions.quality_scoring_actions import (
        score_images_with_pyiqa,
        plot_quality_histogram,
        filter_images_by_quality,
        score_hq_lq_folders,
    )

    options = quality_scoring_menu.__menu_options__
    while True:
        choice = show_menu(
            "Automated Dataset Quality Scoring",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if choice is None or choice == "0":
            break
        action = options[choice][1]
        if callable(action):
            action()


# Register a static menu for favorites (customize as needed)
quality_scoring_menu.__menu_options__ = {
    "1": (
        "Run Quality Scoring Workflow",
        lazy_action(
            "dataset_forge.actions.quality_scoring_actions",
            "run_quality_scoring_workflow",
        ),
    ),
    "0": ("Back to Main Menu", None),
}
