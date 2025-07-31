from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.input_utils import get_folder_path
from dataset_forge.utils.printing import print_info, print_success, print_error
from dataset_forge.utils.monitoring import time_and_record_menu_load


# Lazy import pattern for actions
def lazy_action(module_path, func_name):
    def _action(*args, **kwargs):
        import importlib

        return getattr(importlib.import_module(module_path), func_name)(*args, **kwargs)

    return _action


def degradations_menu():
    options = {
        "1": (
            "🌀 Blur (Gaussian/Box/Median)",
            lazy_action(
                "dataset_forge.actions.degradations_actions", "blur_degradation_menu"
            ),
        ),
        "2": (
            "🎲 Add Noise (Gaussian/Salt)",
            lazy_action(
                "dataset_forge.actions.degradations_actions", "noise_degradation_menu"
            ),
        ),
        "3": (
            "🗜️  Compression (JPEG/WebP)",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "compress_degradation_menu",
            ),
        ),
        "4": (
            "🟫 Pixelate",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "pixelate_degradation_menu",
            ),
        ),
        "5": (
            "🎨 Color Degradation",
            lazy_action(
                "dataset_forge.actions.degradations_actions", "color_degradation_menu"
            ),
        ),
        "6": (
            "🌈 Saturation Degradation",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "saturation_degradation_menu",
            ),
        ),
        "7": (
            "🖼️  Dithering",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "dithering_degradation_menu",
            ),
        ),
        "8": (
            "🧩 Subsampling",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "subsampling_degradation_menu",
            ),
        ),
        "9": (
            "✨ Sharpen",
            lazy_action(
                "dataset_forge.actions.degradations_actions", "sharpen_degradation_menu"
            ),
        ),
        "10": (
            "⬇️  Downscale",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "downscale_degradation_menu",
            ),
        ),
        "11": (
            "🖍️  Posterize",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "posterize_degradation_menu",
            ),
        ),
        "12": (
            "🕳️  Bit Depth Reduction",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "bitdepth_degradation_menu",
            ),
        ),
        "13": (
            "🟪 Banding",
            lazy_action(
                "dataset_forge.actions.degradations_actions", "banding_degradation_menu"
            ),
        ),
        "14": (
            "🏞️  JPEG2000 Compression",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "jpeg2000_degradation_menu",
            ),
        ),
        "15": (
            "📶 Moiré Pattern",
            lazy_action(
                "dataset_forge.actions.degradations_actions", "moire_degradation_menu"
            ),
        ),
        "16": (
            "🌑 Vignetting",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "vignetting_degradation_menu",
            ),
        ),
        "17": (
            "🔄 Lens Distortion",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "lens_distortion_degradation_menu",
            ),
        ),
        "18": (
            "🎭 Color Shift",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "color_shift_degradation_menu",
            ),
        ),
        "19": (
            "🔀 Channel Swap",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "channel_swap_degradation_menu",
            ),
        ),
        "20": (
            "🧊 Block Shuffle",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "block_shuffle_degradation_menu",
            ),
        ),
        "21": (
            "❌ Random Erasing",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "random_erasing_degradation_menu",
            ),
        ),
        "22": (
            "🎚️  Color Jitter",
            lazy_action(
                "dataset_forge.actions.degradations_actions",
                "color_jitter_degradation_menu",
            ),
        ),
        "0": ("⬅️  Back", None),
    }
    while True:
        key = show_menu("🧪 Degradations", options, header_color=Mocha.yellow)
        if key is None or key == "0":
            return
        action = options[key][1]
        if callable(action):
            action()
