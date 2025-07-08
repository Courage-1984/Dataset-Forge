from dataset_forge.utils.printing import (
    print_section,
    print_info,
    print_success,
    print_prompt,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.actions.settings_actions import settings_menu_action
from dataset_forge.menus import session_state

# Assume hq_folder, lq_folder, and get_folder_path are available in the global scope for now


def settings_menu():
    hq, lq = session_state.hq_folder, session_state.lq_folder
    hq, lq = settings_menu_action(hq, lq)
    session_state.hq_folder, session_state.lq_folder = hq, lq
