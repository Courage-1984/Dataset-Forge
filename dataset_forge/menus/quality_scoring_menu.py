from dataset_forge.utils.input_utils import get_path_with_history
from dataset_forge.utils.printing import print_info, print_success, print_error
from dataset_forge.utils.menu import show_menu, lazy_action
from dataset_forge.utils.color import Mocha


def quality_scoring_menu():
    from dataset_forge.actions.quality_scoring_actions import (
        score_images_with_pyiqa,
        plot_quality_histogram,
        filter_images_by_quality,
        score_hq_lq_folders,
    )
    from dataset_forge.utils.printing import print_error

    options = quality_scoring_menu.__menu_options__
    while True:
        key = show_menu(
            "Automated Dataset Quality Scoring",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


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
