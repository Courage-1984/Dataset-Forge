"""
OpenModelDB Model Browser Menu
Allows browsing, searching, filtering, and downloading models from OpenModelDB.
Integrates with project utilities for progress, color, and input.
"""

import importlib
import os
import webbrowser
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.input_utils import get_input
from dataset_forge.utils import monitoring

CACHE_DIR = os.path.join("OpenModelDB", "cache")
MODELS_DIR = os.path.join("OpenModelDB", "models")


def lazy_action(module_path, func_name):
    def _action(*args, **kwargs):
        return monitoring.time_and_record_menu_load(
            func_name,
            lambda: getattr(importlib.import_module(module_path), func_name)(
                *args, **kwargs
            ),
        )

    return _action


def openmodeldb_model_browser_menu():
    print_info("\nUpdating OpenModelDB model cache...")
    from dataset_forge.actions.openmodeldb_actions import (
        update_model_cache,
        get_cached_models,
    )

    update_model_cache(CACHE_DIR)
    models = get_cached_models(CACHE_DIR)
    filtered_models = models
    while True:
        options = {
            "1": (
                "🔍 Search/Filter Models",
                lazy_action(__name__, "search_filter_menu"),
            ),
            "2": ("📄 List All Models", lazy_action(__name__, "list_models_menu")),
            "3": (
                "📥 List Downloaded Models",
                lazy_action(__name__, "list_downloaded_models_menu"),
            ),
            "0": ("⬅️  Back to Previous Menu", None),
        }
        key = show_menu(
            "OpenModelDB Model Browser",
            options,
            Mocha.lavender,
        )
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action(models)


def search_filter_menu(models):
    """
    Presents a sub-menu for how to search/filter models (by tag, architecture, scale, free text, or advanced).
    Each option prompts for the relevant input(s) and displays filtered results.
    """
    from dataset_forge.utils.menu import show_menu
    from dataset_forge.utils.color import Mocha
    from dataset_forge.actions.openmodeldb_actions import filter_models

    while True:
        options = {
            "1": ("🔖 Filter by Tag", lambda: filter_by_tag(models)),
            "2": ("🏛️ Filter by Architecture", lambda: filter_by_architecture(models)),
            "3": ("🔢 Filter by Scale", lambda: filter_by_scale(models)),
            "4": ("🔎 Free Text Search", lambda: filter_by_text(models)),
            "5": ("🧩 Advanced/Combined Filter", lambda: filter_advanced(models)),
            "0": ("⬅️  Back", None),
        }
        # Define menu context for help system
        menu_context = {
            "Purpose": "Search and filter models by various criteria",
            "Options": "5 filter operations",
            "Navigation": "Use numbers 1-5 to select, 0 to go back",
        }

        key = show_menu(
            "Search/Filter Models",
            options,
            Mocha.lavender,
            current_menu="Search/Filter Models",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            return
        options[key][1]()


def filter_by_tag(models):
    tag = get_input("Enter tag (e.g. anime, faces, restoration)")
    from dataset_forge.actions.openmodeldb_actions import filter_models

    filtered = filter_models(models, tag=tag)
    if not filtered:
        print_warning("No models found with that tag.")
        return
    list_models_menu(filtered)


def filter_by_architecture(models):
    architecture = get_input("Enter architecture (e.g. ESRGAN, SwinIR)")
    from dataset_forge.actions.openmodeldb_actions import filter_models

    filtered = filter_models(models, architecture=architecture)
    if not filtered:
        print_warning("No models found with that architecture.")
        return
    list_models_menu(filtered)


def filter_by_scale(models):
    scale = get_input("Enter scale (e.g. 1, 2, 4, 8, 16)")
    try:
        scale = int(scale)
    except Exception:
        print_warning("Invalid scale. Please enter a number.")
        return
    from dataset_forge.actions.openmodeldb_actions import filter_models

    filtered = filter_models(models, scale=scale)
    if not filtered:
        print_warning("No models found with that scale.")
        return
    list_models_menu(filtered)


def filter_by_text(models):
    text = get_input("Enter free text to search")
    from dataset_forge.actions.openmodeldb_actions import filter_models

    filtered = filter_models(models, text=text)
    if not filtered:
        print_warning("No models found matching that text.")
        return
    list_models_menu(filtered)


def filter_advanced(models):
    print_info("Enter filter criteria (leave blank to skip):")
    tag = get_input("Tag (e.g. anime, faces, restoration): ", default=None)
    architecture = get_input("Architecture (e.g. ESRGAN, SwinIR): ", default=None)
    scale = get_input("Scale (e.g. 1, 2, 4, 8, 16): ", default=None)
    if scale:
        try:
            scale = int(scale)
        except Exception:
            print_warning("Invalid scale. Ignoring.")
            scale = None
    text = get_input("Free text search: ", default=None)
    from dataset_forge.actions.openmodeldb_actions import filter_models

    filtered = filter_models(
        models, tag=tag, architecture=architecture, scale=scale, text=text
    )
    if not filtered:
        print_warning("No models found matching criteria.")
        return
    list_models_menu(filtered)


def list_models_menu(models):
    """
    Lists all models and allows user to select one for details/download/test.
    """
    model_names = list(models.keys())
    options = {
        str(i + 1): (models[name]["name"], name) for i, name in enumerate(model_names)
    }
    options["0"] = ("Back", None)
    # Define menu context for help system
    menu_context = {
        "Purpose": "Select a model from the filtered list",
        "Options": f"{len(model_names)} models available",
        "Navigation": "Use numbers 1-{len(model_names)} to select, 0 to go back",
    }

    while True:
        key = show_menu(
            "Select a Model",
            options,
            Mocha.lavender,
            current_menu="Select a Model",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            return
        model_key = options[key][1]
        model_details_menu(models, model_key)


def list_downloaded_models_menu(models):
    """
    Lists all files in OpenModelDB/models/ and allows user to select one for test/metadata.
    If a file matches a model in the cache, show model info; otherwise, show as Unknown/Unregistered Model.
    """
    import os
    from dataset_forge.actions.openmodeldb_actions import (
        get_resource_filename,
        test_model,
    )

    model_files = [
        f for f in os.listdir(MODELS_DIR) if os.path.isfile(os.path.join(MODELS_DIR, f))
    ]
    if not model_files:
        print_warning("No models have been downloaded yet.")
        return
    # Build mapping: filename -> (model_key, model_details) or None
    file_to_model = {}
    for f in model_files:
        found = False
        for key, model in models.items():
            for resource in model.get("resources", []):
                filename = get_resource_filename(resource, model)
                if filename == f:
                    file_to_model[f] = (key, model)
                    found = True
                    break
            if found:
                break
        if not found:
            file_to_model[f] = None
    # Build menu options
    options = {}
    for i, f in enumerate(model_files):
        if file_to_model[f]:
            key, model = file_to_model[f]
            label = f"{model.get('name', key)} ({f})"
        else:
            label = f"Unknown/Unregistered Model: {f}"
        options[str(i + 1)] = (label, f)
    options["0"] = ("Back", None)
    # Define menu context for help system
    menu_context = {
        "Purpose": "Select a downloaded model file for testing or management",
        "Options": f"{len(model_files)} model files available",
        "Navigation": "Use numbers 1-{len(model_files)} to select, 0 to go back",
    }

    while True:
        key = show_menu(
            "Select a Downloaded Model File",
            options,
            Mocha.lavender,
            current_menu="Select a Downloaded Model File",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            return
        selected_file = options[key][1]
        model_info = file_to_model[selected_file]
        downloaded_model_menu(selected_file, model_info)


def downloaded_model_menu(filename, model_info):
    """
    Menu for a downloaded model file. If model_info is not None, show metadata and open page; always allow test.
    """
    import os

    model_path = os.path.join(MODELS_DIR, filename)
    options = {}
    if model_info:
        key, model = model_info
        print_info(f"Model: {model.get('name', key)}\nFile: {filename}")
        print_info(f"Author: {model.get('author', '-')}")
        print_info(f"Architecture: {model.get('architecture', '-')}")
        print_info(f"Scale: {model.get('scale', '-')}")
        print_info(f"Tags: {', '.join(model.get('tags', []))}")
        print_info(f"Description: {model.get('description', '-')}")
        options["1"] = (
            "🧪 Test This Model",
            lambda: test_model(model, MODELS_DIR, prompt_image_path()),
        )
        options["2"] = (
            "🌐 Open Model Page in Browser",
            lambda: open_model_page_in_browser(key),
        )
    else:
        print_warning(f"Unknown/Unregistered Model File: {filename}")
        options["1"] = (
            "🧪 Test This Model (as raw file)",
            lambda: test_unknown_model(model_path),
        )
    options["0"] = ("Back", None)
    # Define menu context for help system
    menu_context = {
        "Purpose": f"Manage downloaded model: {filename}",
        "Options": f"{len(options)-1} operations available",
        "Navigation": "Use numbers 1-{len(options)-1} to select, 0 to go back",
    }

    while True:
        key = show_menu(
            f"Downloaded Model: {filename}",
            options,
            Mocha.lavender,
            current_menu="Downloaded Model",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            return
        options[key][1]()


def prompt_image_path():
    from dataset_forge.utils.input_utils import get_path_with_history

    image_path = get_path_with_history("Enter path to image to test: ")
    if not image_path or not os.path.exists(image_path):
        print_error("Image path does not exist.")
        return None
    return image_path


def test_unknown_model(model_path):
    image_path = prompt_image_path()
    if not image_path:
        return
    # Try to use the upscaling script directly
    try:
        from dataset_forge.utils.upscale_script import upscale_image

        output_path = image_path + ".upscaled.png"
        print_info(f"Testing unknown model file: {model_path}")
        upscale_image(model_path, image_path, output_path)
        print_success(f"Upscaled image saved to: {output_path}")
    except Exception as e:
        print_error(f"Could not test unknown model: {e}")


def model_details_menu(models, model_key):
    """
    Shows details for a selected model and allows download/test/open page.
    """
    from dataset_forge.utils.color import Mocha

    details = get_model_details(models, model_key)
    print_header("Model Details", char="#", color=Mocha.lavender)
    print_info(
        f"{Mocha.lavender}Model: {Mocha.rosewater}{details['name']}{Mocha.reset}"
    )
    print_info(
        f"{Mocha.blue}Author:{Mocha.text} {details.get('author', '-')}{Mocha.reset}"
    )
    print_info(
        f"{Mocha.yellow}Tags:{Mocha.text} {', '.join(details.get('tags', []))}{Mocha.reset}"
    )
    print_info(
        f"{Mocha.mauve}Architecture:{Mocha.text} {details.get('architecture', '-')}{Mocha.reset}"
    )
    print_info(
        f"{Mocha.green}Scale:{Mocha.text} {details.get('scale', '-')}{Mocha.reset}"
    )
    print_info(
        f"{Mocha.peach}License:{Mocha.text} {details.get('license', '-')}{Mocha.reset}"
    )
    print_info(
        f"{Mocha.sapphire}Date:{Mocha.text} {details.get('date', '-')}{Mocha.reset}"
    )
    print_info(
        f"{Mocha.text}Description:{Mocha.reset}\n  {details.get('description', '-')}\n"
    )
    # Show resources
    print_info(f"{Mocha.flamingo}Resources:{Mocha.reset}")
    for i, res in enumerate(details.get("resources", []), 1):
        print_info(
            f"  {Mocha.text}[{i}] Platform: {res.get('platform', '-')}, Type: {res.get('type', '-')}, Size: {res.get('size', '-')}, SHA256: {res.get('sha256', '-')}{Mocha.reset}"
        )
        for url in res.get("urls", []):
            print_info(f"    {Mocha.blue}URL:{Mocha.text} {url}{Mocha.reset}")
    # Show images if present
    if details.get("images"):
        print_info(f"\n{Mocha.pink}Sample Images:{Mocha.reset}")
        for img in details["images"]:
            print_info(
                f"  {Mocha.text}LR: {img.get('LR', '-')}, SR: {img.get('SR', '-')}{Mocha.reset}"
            )
    print_header("", char="#", color=Mocha.lavender)
    options = {
        "1": ("⬇️ Download Model", lambda: download_model(details, MODELS_DIR)),
        "2": (
            "🧪 Test This Model",
            lambda: test_model_interactive(details, MODELS_DIR),
        ),
        "3": (
            "🌐 Open Model Page in Browser",
            lambda: open_model_page_in_browser(model_key),
        ),
        "0": ("Back", None),
    }
    # Define menu context for help system
    menu_context = {
        "Purpose": f"Manage model: {details['name']}",
        "Options": "3 operations available",
        "Navigation": "Use numbers 1-3 to select, 0 to go back",
    }

    while True:
        key = show_menu(
            f"Model: {details['name']}",
            options,
            Mocha.lavender,
            current_menu="Model Details",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            return
        options[key][1]()


def test_model_interactive(model_details, models_dir):
    """
    Prompts user for an image and runs test upscaling with the selected model.
    """
    from dataset_forge.utils.input_utils import get_path_with_history

    image_path = get_path_with_history("Enter path to image to test: ")
    if not image_path or not os.path.exists(image_path):
        print_error("Image path does not exist.")
        return
    test_model(model_details, models_dir, image_path)


def open_model_page_in_browser(model_key):
    url = f"https://openmodeldb.info/models/{model_key}"
    print_info(f"Opening: {url}")
    webbrowser.open(url)


def openmodeldb_model_browser_cli_interactive():
    """
    CLI-interactive OpenModelDB Model Browser using questionary.
    Shows a searchable, scrollable list of models. After selection, allows details, download, test, open in browser.
    """
    try:
        import questionary
    except ImportError:
        print_error(
            "The 'questionary' package is required for CLI-interactive mode.\n    Install it with: pip install questionary"
        )
        return
    from dataset_forge.actions.openmodeldb_actions import (
        get_cached_models,
        update_model_cache,
        download_model,
        test_model,
    )
    import os
    import sys
    import webbrowser

    CACHE_DIR = os.path.join("OpenModelDB", "cache")
    MODELS_DIR = os.path.join("OpenModelDB", "models")
    print_info("\nUpdating OpenModelDB model cache...")
    update_model_cache(CACHE_DIR)
    models = get_cached_models(CACHE_DIR)
    model_keys = list(models.keys())
    model_names = [f"{models[k]['name']} ({k})" for k in model_keys]
    if not model_names:
        print_info("No models found in cache.")
        return
    while True:
        answer = questionary.autocomplete(
            "Select a model (type to search):",
            choices=model_names,
            validate=lambda x: x in model_names,
            style=questionary.Style(
                [("qmark", "fg:#ff9d00 bold"), ("answer", "fg:#00ff00 bold")]
            ),
            qmark="🧠",
        ).ask()
        if not answer:
            print_info("No selection made. Returning to previous menu.")
            return
        idx = model_names.index(answer)
        key = model_keys[idx]
        model = models[key]
        # Model action menu
        while True:
            action = questionary.select(
                f"Model: {model['name']} ({key})",
                choices=[
                    "View Details",
                    "⬇️ Download Model",
                    "🧪 Test This Model",
                    "🌐 Open Model Page in Browser",
                    "Back to Model List",
                ],
                style=questionary.Style(
                    [("qmark", "fg:#ff9d00 bold"), ("answer", "fg:#00ff00 bold")]
                ),
                qmark="🧠",
            ).ask()
            if action == "View Details":
                print_header("Model Details", char="#", color=Mocha.lavender)
                print_info(f"Model: {model['name']}")
                print_info(f"Key: {key}")
                print_info(f"Author: {model.get('author', '-')}")
                print_info(f"Tags: {', '.join(model.get('tags', []))}")
                print_info(f"Architecture: {model.get('architecture', '-')}")
                print_info(f"Scale: {model.get('scale', '-')}")
                print_info(f"License: {model.get('license', '-')}")
                print_info(f"Date: {model.get('date', '-')}")
                print_info(f"Description: {model.get('description', '-')}")
                print_info("Resources:")
                for i, res in enumerate(model.get("resources", []), 1):
                    print_info(
                        f"  [{i}] Platform: {res.get('platform', '-')}, Type: {res.get('type', '-')}, Size: {res.get('size', '-')}, SHA256: {res.get('sha256', '-')}"
                    )
                    for url in res.get("urls", []):
                        print_info(f"    URL: {url}")
                if model.get("images"):
                    print_info("Sample Images:")
                    for img in model["images"]:
                        print_info(f"  LR: {img.get('LR', '-')}, SR: {img.get('SR', '-')}")
                print_header("", char="#", color=Mocha.lavender)
            elif action == "⬇️ Download Model":
                download_model(model, MODELS_DIR)
            elif action == "🧪 Test This Model":
                image_path = questionary.path("Enter path to image to test:").ask()
                if not image_path or not os.path.exists(image_path):
                    print_error("Image path does not exist.")
                else:
                    test_model(model, MODELS_DIR, image_path)
            elif action == "🌐 Open Model Page in Browser":
                url = f"https://openmodeldb.info/models/{key}"
                print_info(f"Opening: {url}")
                webbrowser.open(url)
            elif action == "Back to Model List":
                break
        # After returning from model action menu, ask if user wants to select another model
        again = questionary.confirm("Select another model?", default=True).ask()
        if not again:
            break
