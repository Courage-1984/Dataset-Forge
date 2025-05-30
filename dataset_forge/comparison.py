import os
from dataset_forge.io_utils import is_image_file
from dataset_forge.common import get_destination_path
from PIL import Image, ImageFont, ImageDraw
import random
import numpy as np
from tqdm import tqdm

def create_comparison_images(hq_folder, lq_folder):
    """Create side-by-side comparison images of HQ/LQ pairs."""
    print("\n" + "=" * 30)
    print("  Creating HQ/LQ Comparison Images")
    print("=" * 30)

    # Get destination path
    output_dir = get_destination_path()
    if not output_dir:
        print("Operation aborted as no destination path was provided.")
        return
    os.makedirs(output_dir, exist_ok=True)

    # Setup text parameters
    lq_label = "LQ"
    hq_label = "HQ"
    label_color = (255, 255, 255)  # White
    stroke_color = (0, 0, 0)  # Black
    stroke_width = 1
    font_size = 15

    # Font setup with better fallback handling
    try:
        # First try Arial
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        try:
            # Try Arial from Windows system font directory
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
        except IOError:
            try:
                # Try DejaVu Sans as another option (common on Linux)
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size
                )
            except IOError:
                print("Warning: Could not load TrueType fonts. Using default PIL font.")
                font = ImageFont.load_default()

    # Get the list of matching pairs
    hq_files = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    available_pairs = [
        f for f in hq_files if os.path.isfile(os.path.join(lq_folder, f))
    ]

    if not available_pairs:
        print("No matching HQ/LQ pairs found.")
        return

    # Get number of pairs to process
    while True:
        try:
            num_pairs_str = input("Enter the number of pairs to compare: ").strip()
            num_pairs = int(num_pairs_str)
            if num_pairs <= 0:
                print("Please enter a positive number.")
            elif num_pairs > len(available_pairs):
                print(
                    f"Only {len(available_pairs)} pairs available. Will use all of them."
                )
                num_pairs = len(available_pairs)
                break
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Randomly select pairs
    selected_pairs = random.sample(available_pairs, num_pairs)
    processed_count = 0
    errors = []

    def draw_text_with_stroke(
        draw, position, text, font, fill, stroke_fill, stroke_width
    ):
        x, y = position
        # Draw stroke
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill)
        # Draw main text
        draw.text((x, y), text, font=font, fill=fill)

    for filename in tqdm(selected_pairs, desc="Creating Comparisons"):
        try:
            lq_path = os.path.join(lq_folder, filename)
            hq_path = os.path.join(hq_folder, filename)
            output_path = os.path.join(output_dir, filename)

            # Open images
            lq_img = Image.open(lq_path).convert("RGB")
            hq_img = Image.open(hq_path).convert("RGB")

            # Resize to match dimensions
            target_size = (
                min(lq_img.size[0], hq_img.size[0]),
                min(lq_img.size[1], hq_img.size[1]),
            )
            lq_img = lq_img.resize(target_size, Image.Resampling.LANCZOS)
            hq_img = hq_img.resize(target_size, Image.Resampling.LANCZOS)

            # Create composite image
            composite_img = Image.new(
                "RGB", (target_size[0], target_size[1]), (255, 255, 255)
            )
            composite_img.paste(lq_img, (0, 0))
            composite_img.paste(
                hq_img,
                (0, 0),
                mask=hq_img.split()[3] if hq_img.mode == "RGBA" else None,
            )

            # Add labels
            draw = ImageDraw.Draw(composite_img)
            text_padding = 5

            # Draw labels with stroke effect
            draw_text_with_stroke(
                draw,
                (text_padding, text_padding),
                lq_label,
                font,
                label_color,
                stroke_color,
                stroke_width,
            )
            draw_text_with_stroke(
                draw,
                (
                    target_size[0] - text_padding - font.getsize(hq_label)[0],
                    text_padding,
                ),
                hq_label,
                font,
                label_color,
                stroke_color,
                stroke_width,
            )

            # Save the composite image
            composite_img.save(output_path, quality=100, subsampling=0)
            processed_count += 1

        except Exception as e:
            errors.append(f"Error processing {filename}: {e}")

    print("\n" + "-" * 30)
    print(" Create Comparisons Summary")
    print("-" * 30)
    print(f"Total pairs to process: {num_pairs}")
    print(f"Successfully created: {processed_count} comparisons")

    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)


def create_gif_comparison(hq_folder, lq_folder):
    """Create animated GIF/WebP comparisons of HQ/LQ pairs with transition effects."""
    print("\n" + "=" * 30)
    print("  Creating HQ/LQ Animated Comparisons")
    print("=" * 30)

    # Get output format
    while True:
        format_choice = input("Select output format (gif/webp): ").strip().lower()
        if format_choice in ["gif", "webp"]:
            break
        print("Invalid format. Please enter 'gif' or 'webp'.")

    # Get destination path
    output_dir = get_destination_path()
    if not output_dir:
        print("Operation aborted as no destination path was provided.")
        return
    os.makedirs(output_dir, exist_ok=True)

    # Get available pairs
    hq_files = sorted(
        [
            f
            for f in os.listdir(hq_folder)
            if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
        ]
    )
    available_pairs = [
        f for f in hq_files if os.path.isfile(os.path.join(lq_folder, f))
    ]

    if not available_pairs:
        print("No matching HQ/LQ pairs found.")
        return

    # Get number of pairs to process
    while True:
        try:
            num_pairs_str = input(
                "Enter the number of pairs to create animations for: "
            )
            num_pairs = int(num_pairs_str)
            if num_pairs <= 0:
                print("Please enter a positive number.")
            elif num_pairs > len(available_pairs):
                print(
                    f"Only {len(available_pairs)} pairs available. Will use all of them."
                )
                num_pairs = len(available_pairs)
                break
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get FPS
    while True:
        try:
            fps = float(
                input("Enter FPS (frames per second, e.g., 30): ").strip() or 30
            )
            if fps > 0:
                break
            print("FPS must be positive.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get transition duration percentage
    while True:
        try:
            transition_percent = float(
                input(
                    "Enter transition duration as percentage of total animation (10-90): "
                ).strip()
                or 50
            )
            if 10 <= transition_percent <= 90:
                break
            print("Percentage must be between 10 and 90.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get transition speed multiplier
    while True:
        try:
            speed_multiplier = float(
                input(
                    "Enter transition speed multiplier (0.5 = slower, 2.0 = faster): "
                ).strip()
                or 1.0
            )
            if speed_multiplier > 0:
                break
            print("Speed multiplier must be positive.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get transition type
    print("\nSelect transition type:")
    print("1. Fade")
    print("2. Slide (Left to Right)")
    print("3. Slide (Right to Left)")
    print("4. Zoom")
    print("5. Cut")
    print("6. Special")
    while True:
        transition = input("Enter choice (1-6): ").strip()
        if transition in ["1", "2", "3", "4", "5", "6"]:
            break
        print("Invalid choice. Please enter 1-6.")

    # Calculate frames based on FPS and transition percentage
    total_duration = 2.0  # Total animation duration in seconds
    transition_duration = (transition_percent / 100.0) * total_duration
    static_duration = (total_duration - transition_duration) / 2

    num_transition_frames = int(fps * transition_duration)
    num_static_frames = int(fps * static_duration)

    # Function to create separator line for slide transitions
    def create_separator(
        img, position, thickness=2, color="white", direction="vertical"
    ):
        """Create separator line with custom settings."""
        separator = img.copy()
        draw = ImageDraw.Draw(separator)

        if color == "white":
            line_color = (255, 255, 255)
            edge_color = (0, 0, 0)
        else:  # black
            line_color = (0, 0, 0)
            edge_color = (255, 255, 255)

        if direction == "vertical":
            x = int(position)
            # Draw thin edge lines
            draw.line([(x - 1, 0), (x - 1, img.height)], fill=edge_color, width=1)
            draw.line(
                [(x + thickness, 0), (x + thickness, img.height)],
                fill=edge_color,
                width=1,
            )
            # Draw main line
            draw.line([(x, 0), (x, img.height)], fill=line_color, width=thickness)

        return separator

    # Randomly select pairs
    selected_pairs = random.sample(available_pairs, num_pairs)
    processed_count = 0
    errors = []

    def apply_easing(progress, mode="ease-in-out"):
        # Simple cubic ease-in-out
        if mode == "ease-in-out":
            if progress < 0.5:
                return 4 * progress * progress * progress
            else:
                return 1 - pow(-2 * progress + 2, 3) / 2
        return progress

    for filename in tqdm(selected_pairs, desc="Creating Animated Comparisons"):
        try:
            lq_path = os.path.join(lq_folder, filename)
            hq_path = os.path.join(hq_folder, filename)
            output_name = f"comparison_{os.path.splitext(filename)[0]}.{format_choice}"
            output_path = os.path.join(output_dir, output_name)

            # Open images
            lq_img = Image.open(lq_path).convert("RGB")
            hq_img = Image.open(hq_path).convert("RGB")

            # Resize to match dimensions
            target_size = (
                min(lq_img.size[0], hq_img.size[0]),
                min(lq_img.size[1], hq_img.size[1]),
            )
            lq_img = lq_img.resize(target_size, Image.Resampling.LANCZOS)
            hq_img = hq_img.resize(target_size, Image.Resampling.LANCZOS)

            frames = []

            # Add static LQ frames
            frames.extend([np.array(lq_img)] * num_static_frames)

            # Add transition frames with easing
            for i in range(num_transition_frames):
                progress = i / (num_transition_frames - 1)
                eased_progress = apply_easing(progress, "ease-in-out")

                if transition == "1":  # Fade
                    frame = Image.blend(lq_img, hq_img, eased_progress)
                    frames.append(np.array(frame))

                elif transition in ["2", "3"]:  # Slide transitions
                    frame = Image.new("RGB", target_size)
                    offset = int(target_size[0] * eased_progress)  # Use eased progress

                    if transition == "2":  # Left to Right
                        frame.paste(lq_img, (0, 0))
                        frame.paste(hq_img.crop((0, 0, offset, target_size[1])), (0, 0))
                        frame = create_separator(frame, offset, 2, "white")
                    else:  # Right to Left
                        reverse_offset = target_size[0] - offset
                        frame.paste(hq_img, (0, 0))
                        frame.paste(
                            lq_img.crop(
                                (reverse_offset, 0, target_size[0], target_size[1])
                            ),
                            (reverse_offset, 0),
                        )
                        frame = create_separator(frame, reverse_offset, 2, "white")
                    frames.append(np.array(frame))

                elif transition == "4":  # Zoom with easing
                    zoom_size = (
                        int(target_size[0] * (1 + 0.2 * (1 - eased_progress))),
                        int(target_size[1] * (1 + 0.2 * (1 - eased_progress))),
                    )
                    zoomed = Image.blend(
                        lq_img.resize(zoom_size, Image.Resampling.LANCZOS),
                        hq_img.resize(zoom_size, Image.Resampling.LANCZOS),
                        eased_progress,
                    )
                    # Center crop
                    left = (zoom_size[0] - target_size[0]) // 2
                    top = (zoom_size[1] - target_size[1]) // 2
                    frame = zoomed.crop(
                        (left, top, left + target_size[0], top + target_size[1])
                    )
                    frames.append(np.array(frame))

                elif transition == "5":  # Dynamic Cut
                    # Calculate dynamic cut timing
                    cut_sequence = []
                    quick_cuts = int(num_transition_frames * 0.3)  # 30% quick cuts
                    rest_frames = num_transition_frames - quick_cuts

                    # Generate dynamic cut sequence
                    current_frame = 0
                    while current_frame < num_transition_frames:
                        if current_frame < quick_cuts:
                            cut_duration = max(
                                2, int(fps * 0.1)
                            )  # Quick cuts (0.1 sec)
                        else:
                            cut_duration = max(
                                5, int(fps * 0.5)
                            )  # Longer cuts (0.5 sec)

                        cut_sequence.extend([current_frame % 2] * cut_duration)
                        current_frame += cut_duration

                    # Add cut transition frames
                    for is_hq in cut_sequence[:num_transition_frames]:
                        frames.append(np.array(hq_img if is_hq else lq_img))

                elif transition == "6":  # Special Creative Transition
                    third = num_transition_frames // 3

                    # Phase 1: Fade with slight zoom (first third)
                    for i in range(third):
                        progress = i / third
                        zoom_progress = apply_easing(progress, "ease-in-out")
                        zoom_size = (
                            int(target_size[0] * (1 + 0.1 * (1 - zoom_progress))),
                            int(target_size[1] * (1 + 0.1 * (1 - zoom_progress))),
                        )

                        zoomed_lq = lq_img.resize(zoom_size, Image.Resampling.LANCZOS)
                        zoomed_hq = hq_img.resize(zoom_size, Image.Resampling.LANCZOS)

                        blended = Image.blend(zoomed_lq, zoomed_hq, zoom_progress * 0.5)

                        # Center crop
                        left = (zoom_size[0] - target_size[0]) // 2
                        top = (zoom_size[1] - target_size[1]) // 2
                        frame = blended.crop(
                            (left, top, left + target_size[0], top + target_size[1])
                        )
                        frames.append(np.array(frame))

                    # Phase 2: Quick cuts with fade (second third)
                    for i in range(third):
                        progress = apply_easing(i / third, "ease-in-out")
                        if i % 3 == 0:  # Quick cut every 3 frames
                            frame = Image.blend(lq_img, hq_img, 0.5 + (progress * 0.5))
                        else:
                            frame = Image.blend(lq_img, hq_img, progress)
                        frames.append(np.array(frame))

                    # Phase 3: Slide with fade (final third)
                    for i in range(third):
                        progress = apply_easing(i / third, "ease-in-out")
                        frame = Image.new("RGB", target_size)
                        offset = int(target_size[0] * progress)

                        # Create base frame with fade
                        base = Image.blend(lq_img, hq_img, progress)
                        frame.paste(base, (0, 0))

                        # Add sliding HQ portion
                        frame.paste(hq_img.crop((0, 0, offset, target_size[1])), (0, 0))
                        frames.append(np.array(frame))

            # Add static HQ frames
            frames.extend([np.array(hq_img)] * num_static_frames)

            # Adjust frame timing based on speed multiplier
            adjusted_duration = (1.0 / fps) / speed_multiplier

            # Save as GIF or WebP
            import imageio

            if format_choice == "gif":
                imageio.mimsave(output_path, frames, duration=adjusted_duration, loop=0)
            else:  # webp
                imageio.mimsave(
                    output_path,
                    frames,
                    duration=adjusted_duration,
                    loop=0,
                    format="WEBP",
                    quality=90,
                )

            processed_count += 1

        except Exception as e:
            errors.append(f"Error processing {filename}: {e}")

    print("\n" + "-" * 30)
    print(" Create Animated Comparison Summary")
    print("-" * 30)
    print(f"Format: {format_choice.upper()}")
    print(f"FPS: {fps}")
    print(f"Transition Duration: {transition_percent}% of total")
    print(f"Speed Multiplier: {speed_multiplier}x")
    print(f"Successfully created: {processed_count} animations")

    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)
