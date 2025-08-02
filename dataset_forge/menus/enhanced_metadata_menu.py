from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_header,
    print_section,
    print_success,
    print_warning,
    print_error,
    print_info,
    print_prompt,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.actions.enhanced_metadata_actions import (
    batch_extract_metadata,
    view_edit_metadata,
    filter_by_metadata,
    batch_anonymize_metadata,
)


def enhanced_metadata_menu():
    options = {
        "1": ("📤 Batch Extract Metadata (CSV/SQLite)", batch_extract_metadata),
        "2": ("👁️ View/Edit Metadata (Single Image)", view_edit_metadata),
        "3": ("🔎 Filter Images by Metadata", filter_by_metadata),
        "4": ("🧹 Batch Anonymize Metadata", batch_anonymize_metadata),
        "0": ("⬅️  Back", None),
    }
    
    # Define menu context for help system
    menu_context = {
        "Purpose": "Advanced metadata handling and management",
        "Total Options": "4 metadata operations",
        "Navigation": "Use numbers 1-4 to select, 0 to go back",
        "Key Features": "Batch extraction, metadata editing, filtering, anonymization",
    }
    
    while True:
        key = show_menu(
            "🗂️  Enhanced Metadata Management",
            options,
            header_color=Mocha.yellow,
            char="=",
            current_menu="Enhanced Metadata Management",
            menu_context=menu_context,
        )
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        if callable(action):
            try:
                action()
            except Exception as e:
                print_error(f"Exception in menu action: {e}")
        else:
            print_error(f"Selected action is not callable: {action!r}")
