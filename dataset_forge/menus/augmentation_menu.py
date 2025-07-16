import os
from dataset_forge.utils.input_utils import (
    select_folder,
    ask_yes_no,
    ask_int,
    ask_float,
    get_folder_path,
)
from dataset_forge.utils.printing import (
    print_section,
    print_success,
    print_warning,
    print_info,
    print_error,
)
from dataset_forge.utils.menu import show_menu, lazy_action
from dataset_forge.utils.color import Mocha

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
    from dataset_forge.actions import augmentation_actions as aug

    options = augmentation_menu.__menu_options__
    while True:
        choice = show_menu(
            "🚀 Augmentation",
            options,
            header_color=Mocha.sapphire,
            char="-",
        )
        if choice is None or choice == "0":
            break
        action = options[choice][1]
        if callable(action):
            action()


def run_augmentation_pipeline_menu():
    from dataset_forge.actions.augmentation_actions import (
        apply_augmentation_pipeline,
        load_json_augmentation_recipe,
        AUGMENTATION_RECIPES,
    )
    import os
    import json

    RECIPES_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../configs/augmentation_recipes")
    )
    # List both built-in and JSON recipes
    json_recipes = []
    if os.path.isdir(RECIPES_DIR):
        json_recipes = [f for f in os.listdir(RECIPES_DIR) if f.endswith(".json")]
    builtin_recipes = list(AUGMENTATION_RECIPES.keys())
    all_recipes = [(name, "builtin") for name in builtin_recipes] + [
        (name, "json") for name in json_recipes
    ]
    if not all_recipes:
        print_error("No augmentation recipes found.")
        return
    input_dir = get_folder_path("Enter input directory:")
    output_dir = get_folder_path("Enter output directory:")
    print_info("Available augmentation recipes:")
    for idx, (name, kind) in enumerate(all_recipes, 1):
        label = "[builtin]" if kind == "builtin" else "[json]"
        print_info(f"[{idx}] {name} {label}")
    try:
        choice = int(input("Select recipe by number: ").strip())
        if choice < 1 or choice > len(all_recipes):
            print_error("Invalid selection. Please enter a valid number.")
            return
        recipe_name, kind = all_recipes[choice - 1]
        if kind == "json":
            recipe_path = os.path.join(RECIPES_DIR, recipe_name)
            with open(recipe_path, "r", encoding="utf-8") as f:
                recipe_json = json.load(f)
            print_info("\n--- Recipe Preview ---")
            print_info(json.dumps(recipe_json, indent=2))
            print_info("----------------------\n")
            confirm = input("Proceed with this recipe? (y/n): ").strip().lower()
            if confirm != "y":
                print_info("Cancelled. Returning to menu.")
                return
            try:
                custom_recipe = load_json_augmentation_recipe(recipe_name)
            except Exception as e:
                print_error(f"Error loading recipe: {e}")
                return
            print_info(f"Running augmentation pipeline: {recipe_name}")
            apply_augmentation_pipeline(
                input_dir, output_dir, recipe_name, custom_recipe=custom_recipe
            )
        else:
            print_info(f"Running augmentation pipeline: {recipe_name}")
            apply_augmentation_pipeline(input_dir, output_dir, recipe_name)
    except (ValueError, IndexError):
        print_error("Invalid selection. Please enter a valid number.")
        return
    except Exception as e:
        print_error(f"Error reading recipe: {e}")
        return


def list_augmentation_recipes():
    from dataset_forge.actions.augmentation_actions import AUGMENTATION_RECIPES
    import os
    import json

    RECIPES_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../configs/augmentation_recipes")
    )
    print_info(f"[DEBUG] Looking in directory: {RECIPES_DIR}")
    try:
        dir_listing = os.listdir(RECIPES_DIR)
        print_info(f"[DEBUG] Directory contents: {dir_listing}")
    except Exception as e:
        print_error(f"[DEBUG] Could not list directory: {e}")
        dir_listing = []
    json_recipes = []
    if os.path.isdir(RECIPES_DIR):
        json_recipes = [f for f in dir_listing if f.lower().endswith(".json")]
    builtin_recipes = list(AUGMENTATION_RECIPES.keys())
    all_recipes = [(name, "builtin") for name in builtin_recipes] + [
        (name, "json") for name in json_recipes
    ]
    print_info("\nPredefined (builtin) recipes:")
    for idx, (name, kind) in enumerate(all_recipes, 1):
        label = "[builtin]" if kind == "builtin" else "[json]"
        print_info(f"[{idx}] {name} {label}")
    print_info("")
    if not all_recipes:
        input("Press Enter to return to the menu...")
        return
    try:
        choice = input(
            "Enter the number of a recipe to view its contents, or press Enter to return: "
        ).strip()
        if not choice:
            return
        choice = int(choice)
        if choice < 1 or choice > len(all_recipes):
            print_error("Invalid selection. Returning to menu.")
            return
        recipe_name, kind = all_recipes[choice - 1]
        print_info(f"\n--- Recipe: {recipe_name} ---")
        if kind == "json":
            recipe_path = os.path.join(RECIPES_DIR, recipe_name)
            with open(recipe_path, "r", encoding="utf-8") as f:
                recipe_json = json.load(f)
            print_info(json.dumps(recipe_json, indent=2))
        else:
            from pprint import pformat

            steps = AUGMENTATION_RECIPES[recipe_name]
            formatted = []
            for fn, params in steps:
                formatted.append({"operation": fn.__name__, "params": params})
            print_info(json.dumps(formatted, indent=2))
        print_info("-----------------------------\n")
    except Exception as e:
        print_error(f"Error displaying recipe: {e}")
    input("Press Enter to return to the menu...")


def create_augmentation_recipe():
    import os
    import json

    RECIPES_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../configs/augmentation_recipes")
    )
    os.makedirs(RECIPES_DIR, exist_ok=True)
    print_info("Create a new augmentation recipe (.json)")
    recipe_name = input("Enter new recipe filename (e.g. my_recipe.json): ").strip()
    if not recipe_name.endswith(".json"):
        recipe_name += ".json"
    steps = []
    supported_ops = [
        "random_crop",
        "random_flip",
        "random_rotation",
        "random_brightness",
        "random_contrast",
        "random_saturation",
        "random_noise",
        "random_blur",
        "mixup",
    ]
    print_info("Supported operations:")
    for op in supported_ops:
        print_info(f"  - {op}")
    while True:
        op = input("Add operation (or leave blank to finish): ").strip()
        if not op:
            break
        if op not in supported_ops:
            print_error(f"Unsupported operation: {op}")
            continue
        params = {}
        while True:
            param_entry = input(
                f"  Add param for {op} (key=value, leave blank to finish): "
            ).strip()
            if not param_entry:
                break
            if "=" not in param_entry:
                print_error("Invalid format. Use key=value.")
                continue
            key, value = param_entry.split("=", 1)
            key = key.strip()
            value = value.strip()
            # Try to parse value as int, float, list, or keep as string
            try:
                if value.startswith("[") and value.endswith("]"):
                    value = json.loads(value)
                elif "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except Exception:
                pass
            params[key] = value
        steps.append({"operation": op, "params": params})
    if not steps:
        print_warning("No steps added. Recipe not created.")
        return
    out_path = os.path.join(RECIPES_DIR, recipe_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(steps, f, indent=2)
    print_success(f"Recipe saved to {out_path}")
    input("Press Enter to return to the menu...")


def edit_augmentation_recipe():
    import os
    import json
    from dataset_forge.utils.printing import print_info, print_error, print_success

    RECIPES_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../configs/augmentation_recipes")
    )
    # List only .json recipes
    if not os.path.isdir(RECIPES_DIR):
        print_error("No recipe directory found.")
        return
    json_recipes = [f for f in os.listdir(RECIPES_DIR) if f.lower().endswith(".json")]
    if not json_recipes:
        print_error("No .json recipes to edit.")
        return
    print_info("Select a recipe to edit:")
    for idx, name in enumerate(json_recipes, 1):
        print_info(f"  {idx}. {name}")
    try:
        sel = int(input("Enter number: "))
        if not (1 <= sel <= len(json_recipes)):
            print_error("Invalid selection.")
            return
    except Exception:
        print_error("Invalid input.")
        return
    recipe_name = json_recipes[sel - 1]
    recipe_path = os.path.join(RECIPES_DIR, recipe_name)
    try:
        with open(recipe_path, "r", encoding="utf-8") as f:
            recipe = json.load(f)
    except Exception as e:
        print_error(f"Failed to load recipe: {e}")
        return
    while True:
        print_info(f"\nEditing {recipe_name}:")
        for idx, step in enumerate(recipe, 1):
            print_info(f"  {idx}. {step['operation']} {step.get('params', {})}")
        print_info(
            "Options: [a]dd step, [e]dit step, [d]elete step, [s]ave, [q]uit without saving"
        )
        choice = input("Select option: ").strip().lower()
        if choice == "a":
            op = input("Enter operation name: ").strip()
            params = input("Enter params as JSON (or leave blank): ").strip()
            try:
                params_dict = json.loads(params) if params else {}
            except Exception:
                print_error("Invalid params JSON.")
                continue
            recipe.append({"operation": op, "params": params_dict})
        elif choice == "e":
            try:
                idx = int(input("Step number to edit: ")) - 1
                if not (0 <= idx < len(recipe)):
                    print_error("Invalid step number.")
                    continue
            except Exception:
                print_error("Invalid input.")
                continue
            op = input(
                f"Enter new operation name (blank to keep '{recipe[idx]['operation']}'): "
            ).strip()
            params = input(
                f"Enter new params as JSON (blank to keep current): "
            ).strip()
            if op:
                recipe[idx]["operation"] = op
            if params:
                try:
                    recipe[idx]["params"] = json.loads(params)
                except Exception:
                    print_error("Invalid params JSON.")
        elif choice == "d":
            try:
                idx = int(input("Step number to delete: ")) - 1
                if not (0 <= idx < len(recipe)):
                    print_error("Invalid step number.")
                    continue
            except Exception:
                print_error("Invalid input.")
                continue
            del recipe[idx]
        elif choice == "s":
            try:
                with open(recipe_path, "w", encoding="utf-8") as f:
                    json.dump(recipe, f, indent=2)
                print_success("Recipe saved.")
            except Exception as e:
                print_error(f"Failed to save: {e}")
            break
        elif choice == "q":
            print_info("Quit without saving.")
            break
        else:
            print_error("Unknown option.")


def delete_augmentation_recipe():
    import os
    import json
    from dataset_forge.utils.printing import print_info, print_error, print_success

    RECIPES_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../configs/augmentation_recipes")
    )
    # List only .json recipes
    if not os.path.isdir(RECIPES_DIR):
        print_error("No recipe directory found.")
        return
    json_recipes = [f for f in os.listdir(RECIPES_DIR) if f.lower().endswith(".json")]
    if not json_recipes:
        print_error("No .json recipes to delete.")
        return
    print_info("Select a recipe to delete:")
    for idx, name in enumerate(json_recipes, 1):
        print_info(f"  {idx}. {name}")
    try:
        sel = int(input("Enter number: "))
        if not (1 <= sel <= len(json_recipes)):
            print_error("Invalid selection.")
            return
    except Exception:
        print_error("Invalid input.")
        return
    recipe_name = json_recipes[sel - 1]
    recipe_path = os.path.join(RECIPES_DIR, recipe_name)
    confirm = (
        input(f"Are you sure you want to delete '{recipe_name}'? (y/N): ")
        .strip()
        .lower()
    )
    if confirm == "y":
        try:
            os.remove(recipe_path)
            print_success(f"Deleted {recipe_name}.")
        except Exception as e:
            print_error(f"Failed to delete: {e}")
    else:
        print_info("Delete cancelled.")


# Register a static menu for favorites (customize as needed)
augmentation_menu.__menu_options__ = {
    "1": ("📜 List All Recipes", list_augmentation_recipes),
    "2": ("➕ Create Recipe", create_augmentation_recipe),
    "3": ("✏️  Edit Recipe", edit_augmentation_recipe),
    "4": ("🗑️  Delete Recipe", delete_augmentation_recipe),
    "5": ("🚀 Run Augmentation Pipeline", run_augmentation_pipeline_menu),
    "0": ("⬅️  Back", None),
}
