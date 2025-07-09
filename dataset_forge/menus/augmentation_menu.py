import os
from dataset_forge.actions import augmentation_actions as aug
from dataset_forge.utils.input_utils import (
    select_folder,
    ask_yes_no,
    ask_int,
    ask_float,
    ask_choice,
)
from dataset_forge.utils.printing import print_section, print_success, print_warning

# If path history is managed elsewhere, import and use it here
try:
    from dataset_forge.utils.path_history import (
        get_path_from_history,
        add_path_to_history,
    )
except ImportError:

    def get_path_from_history(*args, **kwargs):
        return None

    def add_path_to_history(*args, **kwargs):
        pass


def augmentation_menu():
    print_section("Augmentation Recipes")
    recipes = aug.list_recipes()
    print("Available recipes:")
    for i, r in enumerate(recipes):
        print(f"  [{i}] {r}")
    idx = ask_int(
        "Select a recipe by number", default=0, min_value=0, max_value=len(recipes) - 1
    )
    recipe_name = recipes[idx]
    print(f"Selected: {recipe_name}")
    print("Steps:")
    for fn, params in aug.get_recipe(recipe_name):
        print(f"  {fn.__name__} {params}")
    if ask_yes_no("Customize parameters?", default=False):
        custom_steps = []
        for fn, params in aug.get_recipe(recipe_name):
            new_params = {}
            for k, v in params.items():
                if isinstance(v, float):
                    new_params[k] = ask_float(f"{fn.__name__} param '{k}'", default=v)
                elif isinstance(v, int):
                    new_params[k] = ask_int(f"{fn.__name__} param '{k}'", default=v)
                elif isinstance(v, tuple):
                    tup = tuple(
                        ask_int(f"{fn.__name__} param '{k}'[{i}]", default=vi)
                        for i, vi in enumerate(v)
                    )
                    new_params[k] = tup
                else:
                    new_params[k] = v
            custom_steps.append((fn, new_params))
        custom_recipe = custom_steps
    else:
        custom_recipe = None
    # Path selection
    hq_lq_mode = ask_yes_no("Use HQ/LQ paired folders?", default=False)
    if hq_lq_mode:
        hq_path = select_folder("Select HQ input folder")
        lq_path = select_folder("Select LQ input folder")
        out_hq = select_folder("Select HQ output folder (will be created if not exist)")
        out_lq = select_folder("Select LQ output folder (will be created if not exist)")
        add_path_to_history(hq_path)
        add_path_to_history(lq_path)
        add_path_to_history(out_hq)
        add_path_to_history(out_lq)
        aug.apply_augmentation_pipeline(
            input_dir=hq_path,
            output_dir=out_hq,
            recipe_name=recipe_name,
            hq_lq_mode=True,
            lq_input_dir=lq_path,
            lq_output_dir=out_lq,
            custom_recipe=custom_recipe,
            progress_desc="Augmenting HQ/LQ pairs",
        )
    else:
        in_path = select_folder("Select input folder")
        out_path = select_folder("Select output folder (will be created if not exist)")
        add_path_to_history(in_path)
        add_path_to_history(out_path)
        aug.apply_augmentation_pipeline(
            input_dir=in_path,
            output_dir=out_path,
            recipe_name=recipe_name,
            custom_recipe=custom_recipe,
            progress_desc="Augmenting images",
        )
    print_success("Augmentation complete!")
