from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import print_info
from dataset_forge.utils.color import Mocha


def main_menu():
    import time

    start_time = time.time()
    print(f"[main_menu] Entered main_menu: {time.time() - start_time:.2f} seconds")

    print(
        f"[main_menu] Before importing dataset_management_menu: {time.time() - start_time:.2f} seconds"
    )
    from dataset_forge.menus.dataset_management_menu import dataset_management_menu

    print(
        f"[main_menu] After importing dataset_management_menu: {time.time() - start_time:.2f} seconds"
    )

    print(
        f"[main_menu] Before importing analysis_validation_menu: {time.time() - start_time:.2f} seconds"
    )
    from dataset_forge.menus.analysis_validation_menu import analysis_validation_menu

    print(
        f"[main_menu] After importing analysis_validation_menu: {time.time() - start_time:.2f} seconds"
    )

    print(
        f"[main_menu] Before importing image_processing_menu: {time.time() - start_time:.2f} seconds"
    )
    from dataset_forge.menus.image_processing_menu import image_processing_menu

    print(
        f"[main_menu] After importing image_processing_menu: {time.time() - start_time:.2f} seconds"
    )

    print(
        f"[main_menu] Before importing training_inference_menu: {time.time() - start_time:.2f} seconds"
    )
    from dataset_forge.menus.training_inference_menu import training_inference_menu

    print(
        f"[main_menu] After importing training_inference_menu: {time.time() - start_time:.2f} seconds"
    )

    print(
        f"[main_menu] Before importing utilities_menu: {time.time() - start_time:.2f} seconds"
    )
    from dataset_forge.menus.utilities_menu import utilities_menu

    print(
        f"[main_menu] After importing utilities_menu: {time.time() - start_time:.2f} seconds"
    )

    print(
        f"[main_menu] Before importing system_settings_menu: {time.time() - start_time:.2f} seconds"
    )
    from dataset_forge.menus.system_settings_menu import system_settings_menu

    print(
        f"[main_menu] After importing system_settings_menu: {time.time() - start_time:.2f} seconds"
    )

    main_options = {
        "1": ("\U0001f4c2 Dataset Management", dataset_management_menu),
        "2": ("\U0001f50d Analysis & Validation", analysis_validation_menu),
        "3": ("\u2728 Image Processing & Augmentation", image_processing_menu),
        "4": ("\U0001f680 Training & Inference", training_inference_menu),
        "5": ("\U0001f6e0\ufe0f Utilities", utilities_menu),
        "6": ("\u2699\ufe0f System & Settings", system_settings_menu),
        "0": ("\U0001f6aa Exit", None),
    }
    while True:
        try:
            action = show_menu(
                "Image Dataset Utility - Main Menu",
                main_options,
                header_color=Mocha.lavender,
            )
            if action is None:
                print_info("Exiting...")
                break
            action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break
