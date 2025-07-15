from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.color import Mocha
from dataset_forge.utils.input_utils import get_folder_path
from dataset_forge.utils.printing import print_info, print_success, print_error
from dataset_forge.utils.monitoring import time_and_record_menu_load


# Lazy import pattern for actions
def lazy_blur_action():
    from dataset_forge.actions.degradations_actions import apply_blur_degradation

    return apply_blur_degradation


def lazy_noise_action():
    from dataset_forge.actions.degradations_actions import apply_noise_degradation

    return apply_noise_degradation


def lazy_compress_action():
    from dataset_forge.actions.degradations_actions import apply_compress_degradation

    return apply_compress_degradation


def lazy_pixelate_action():
    from dataset_forge.actions.degradations_actions import apply_pixelate_degradation

    return apply_pixelate_degradation


def lazy_color_action():
    from dataset_forge.actions.degradations_actions import apply_color_degradation

    return apply_color_degradation


def lazy_saturation_action():
    from dataset_forge.actions.degradations_actions import apply_saturation_degradation

    return apply_saturation_degradation


def lazy_dithering_action():
    from dataset_forge.actions.degradations_actions import apply_dithering_degradation

    return apply_dithering_degradation


def lazy_subsampling_action():
    from dataset_forge.actions.degradations_actions import apply_subsampling_degradation

    return apply_subsampling_degradation


def lazy_screentone_action():
    from dataset_forge.actions.degradations_actions import apply_screentone_degradation

    return apply_screentone_degradation


def lazy_halo_action():
    from dataset_forge.actions.degradations_actions import apply_halo_degradation

    return apply_halo_degradation


def lazy_sin_action():
    from dataset_forge.actions.degradations_actions import apply_sin_degradation

    return apply_sin_degradation


def lazy_shift_action():
    from dataset_forge.actions.degradations_actions import apply_shift_degradation

    return apply_shift_degradation


def lazy_canny_action():
    from dataset_forge.actions.degradations_actions import apply_canny_degradation

    return apply_canny_degradation


def lazy_resize_action():
    from dataset_forge.actions.degradations_actions import apply_resize_degradation

    return apply_resize_degradation


# Update options dict
def degradations_menu():
    """
    Degradations menu for applying image degradations (WTP style).
    """
    options = {
        "1": ("🌀 Blur", lambda: blur_menu()),
        "2": ("🎲 Noise", lambda: noise_menu()),
        "3": ("🗜️ Compress", lambda: compress_menu()),
        "4": ("🟪 Pixelate", lambda: pixelate_menu()),
        "5": ("🎨 Color", lambda: color_menu()),
        "6": ("🌈 Saturation", lambda: saturation_menu()),
        "7": ("🟫 Dithering", lambda: dithering_menu()),
        "8": ("🟦 Subsampling", lambda: subsampling_menu()),
        "9": ("🟩 Screentone", lambda: screentone_menu()),
        "10": ("💫 Halo", lambda: halo_menu()),
        "11": ("🌊 Sin", lambda: sin_menu()),
        "12": ("🔀 Shift", lambda: shift_menu()),
        "13": ("🖊️ Canny", lambda: canny_menu()),
        "14": ("📏 Resize", lambda: resize_menu()),
        "0": ("🚪 Back", None),
    }
    while True:
        try:
            with time_and_record_menu_load("Degradations Menu"):
                action = show_menu("Degradations Menu", options, Mocha.lavender)
            if action is None:
                break
            action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting Degradations Menu...")
            break


def blur_menu():
    print_info("\n[Blur Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    # Prompt for in-place/copy
    from questionary import select, text

    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    # Prompt for parameters
    blur_type = select(
        "Select blur type:", choices=["gauss", "box", "median"], default="gauss"
    ).ask()
    kernel_size = int(text("Kernel size (integer, e.g. 3):", default="3").ask())
    probability = float(
        text("Probability to apply blur (0.0-1.0):", default="0.5").ask()
    )
    # Call action
    action = lazy_blur_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            blur_type=blur_type,
            kernel_size=kernel_size,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Blur degradation complete.")


def noise_menu():
    print_info("\n[Noise Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    noise_type = select(
        "Select noise type:",
        choices=["gauss", "uniform", "salt", "pepper"],
        default="gauss",
    ).ask()
    alpha = float(text("Noise intensity (0.0-1.0):", default="0.2").ask())
    probability = float(
        text("Probability to apply noise (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_noise_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            noise_type=noise_type,
            alpha=alpha,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Noise degradation complete.")


def compress_menu():
    print_info("\n[Compress Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    algorithm = select(
        "Select compression algorithm:", choices=["jpeg", "webp"], default="jpeg"
    ).ask()
    quality = int(
        text(
            "Compression quality (1-100, lower = more compression):", default="50"
        ).ask()
    )
    probability = float(
        text("Probability to apply compression (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_compress_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            algorithm=algorithm,
            quality=quality,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Compression degradation complete.")


def pixelate_menu():
    print_info("\n[Pixelate Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    size = int(text("Pixel block size (2-32):", default="8").ask())
    probability = float(
        text("Probability to apply pixelate (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_pixelate_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            size=size,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Pixelate degradation complete.")


def color_menu():
    print_info("\n[Color Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    high = int(text("Max brightness (200-255):", default="255").ask())
    low = int(text("Min darkness (0-50):", default="0").ask())
    gamma = float(text("Gamma correction (0.8-1.2):", default="1.0").ask())
    probability = float(
        text("Probability to apply color degradation (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_color_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            high=high,
            low=low,
            gamma=gamma,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Color degradation complete.")


def saturation_menu():
    print_info("\n[Saturation Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    rand = float(text("Random saturation factor (0.0-1.0):", default="0.7").ask())
    probability = float(
        text("Probability to apply saturation (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_saturation_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            rand=rand,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Saturation degradation complete.")


def dithering_menu():
    print_info("\n[Dithering Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    dithering_type = select(
        "Select dithering type:",
        choices=["quantize", "floydsteinberg", "atkinson", "sierra", "burkes"],
        default="quantize",
    ).ask()
    color_ch = int(text("Number of color channels (2-16):", default="8").ask())
    probability = float(
        text("Probability to apply dithering (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_dithering_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            dithering_type=dithering_type,
            color_ch=color_ch,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Dithering degradation complete.")


def subsampling_menu():
    print_info("\n[Subsampling Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    sampling = select(
        "Select chroma subsampling:",
        choices=["4:4:4", "4:2:2", "4:2:0"],
        default="4:2:0",
    ).ask()
    blur = float(text("Optional blur kernel size (0.0-4.0):", default="0.0").ask())
    probability = float(
        text("Probability to apply subsampling (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_subsampling_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            sampling=sampling,
            blur=blur,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Subsampling degradation complete.")


def screentone_menu():
    print_info("\n[Screentone Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    dot_size = int(text("Dot size (4-16):", default="7").ask())
    dot_type = select(
        "Dot type:", choices=["circle", "diamond", "line"], default="circle"
    ).ask()
    angle = int(text("Pattern angle (-45 to 45):", default="0").ask())
    probability = float(
        text("Probability to apply screentone (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_screentone_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            dot_size=dot_size,
            dot_type=dot_type,
            angle=angle,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Screentone degradation complete.")


def halo_menu():
    print_info("\n[Halo Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    type_halo = select(
        "Halo type:",
        choices=["unsharp_mask", "unsharp_halo", "unsharp_gray"],
        default="unsharp_mask",
    ).ask()
    kernel = int(text("Kernel (0-5):", default="2").ask())
    amount = float(text("Amount (0.0-2.0):", default="1.0").ask())
    threshold = float(text("Threshold (0.0-1.0):", default="0.0").ask())
    probability = float(
        text("Probability to apply halo (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_halo_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            type_halo=type_halo,
            kernel=kernel,
            amount=amount,
            threshold=threshold,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Halo degradation complete.")


def sin_menu():
    print_info("\n[Sin Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    shape = int(text("Shape (100-1000):", default="200").ask())
    alpha = float(text("Alpha (0.1-0.5):", default="0.3").ask())
    bias = float(text("Bias (-1.0-1.0):", default="0.0").ask())
    vertical = float(text("Vertical (0.0-1.0):", default="0.5").ask())
    probability = float(
        text("Probability to apply sin (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_sin_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            shape=shape,
            alpha=alpha,
            bias=bias,
            vertical=vertical,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Sin degradation complete.")


def shift_menu():
    print_info("\n[Shift Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    shift_type = select(
        "Shift type:", choices=["rgb", "yuv", "cmyk"], default="rgb"
    ).ask()
    percent = (
        select("Shift as percent?", choices=["No", "Yes"], default="No").ask() == "Yes"
    )
    amount = int(text("Amount (-10 to 10):", default="2").ask())
    probability = float(
        text("Probability to apply shift (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_shift_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            shift_type=shift_type,
            percent=percent,
            amount=amount,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Shift degradation complete.")


def canny_menu():
    print_info("\n[Canny Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    thread1 = int(text("Thread1 (10-150):", default="100").ask())
    thread2 = int(text("Thread2 (10-100):", default="50").ask())
    aperture_size = int(
        select("Aperture size:", choices=["3", "5", "7"], default="3").ask()
    )
    scale = float(text("Scale (0.0-1.0):", default="0.5").ask())
    white = float(text("White (0.0-1.0):", default="0.0").ask())
    probability = float(
        text("Probability to apply canny (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_canny_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            thread1=thread1,
            thread2=thread2,
            aperture_size=aperture_size,
            scale=scale,
            white=white,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Canny degradation complete.")


def resize_menu():
    print_info("\n[Resize Degradation]")
    input_folder = get_folder_path("Select input folder:")
    in_place = False
    output_folder = None
    in_place_choice = select(
        "Process images in-place or copy to output folder?",
        choices=["In-place (overwrite)", "Copy to output folder"],
        default="Copy to output folder",
    ).ask()
    if in_place_choice == "In-place (overwrite)":
        in_place = True
    else:
        output_folder = get_folder_path("Select output folder:")
    alg_lq = select(
        "Resize algorithm:",
        choices=[
            "box",
            "hermite",
            "linear",
            "lagrange",
            "cubic_catrom",
            "cubic_mitchell",
            "cubic_bspline",
            "lanczos",
            "gauss",
        ],
        default="box",
    ).ask()
    scale = float(text("Scale (0.5-1.0):", default="0.5").ask())
    probability = float(
        text("Probability to apply resize (0.0-1.0):", default="0.5").ask()
    )
    action = lazy_resize_action()
    try:
        action(
            input_folder=input_folder,
            output_folder=output_folder,
            in_place=in_place,
            alg_lq=alg_lq,
            scale=scale,
            probability=probability,
        )
    except Exception as e:
        print_error(f"Error: {e}")
    else:
        print_success("Resize degradation complete.")
