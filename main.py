import logging
from dataset_forge.menus.main_menu import main_menu

# All functionality is now organized in the new hierarchical menu structure
# See MENU_RESTRUCTURE_SUMMARY.md for details on the new organization

if __name__ == "__main__":
    # Minimal global logging to console. Functions can add specific file handlers.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main_menu()
