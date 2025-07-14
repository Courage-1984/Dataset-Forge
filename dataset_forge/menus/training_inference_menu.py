from dataset_forge.menus.model_management_menu import openmodeldb_model_browser_menu
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha


def training_inference_menu():
    while True:
        options = {
            "1": ("📝 Add Training/Inference Config", None),
            "2": ("📂 Load Config", None),
            "3": ("ℹ️ View Config Info", None),
            "4": ("✅ Validate HQ/LQ Dataset", None),
            "5": ("✅ Validate Val Dataset", None),
            "6": ("🛠️ Run wtp_dataset_destroyer", None),
            "7": ("🚀 Run traiNNer-redux", None),
            "8": ("✏️ Edit .hcl Config File", None),
            "9": ("✏️ Edit .yml Config File", None),
            "10": ("📋 List/Upscale with Model", None),
            "11": ("🧠 OpenModelDB Model Browser", openmodeldb_model_browser_menu),
            "0": ("⬅️ Back to Main Menu", None),
        }
        choice = show_menu(
            "🚀 Training & Inference",
            options,
            Mocha.lavender,
        )
        if choice is None or choice == "0":
            break
        action = options[choice][1]
        if action:
            action()
