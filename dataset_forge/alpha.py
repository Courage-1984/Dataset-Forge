import os
from dataset_forge.io_utils import is_image_file
from PIL import Image
import shutil
from tqdm import tqdm
from dataset_forge.common import get_file_operation_choice, get_destination_path, get_unique_filename

def find_alpha_channels(hq_folder, lq_folder):
    """Find images with alpha channels in HQ/LQ folders."""
    print("\n" + "=" * 30)
    print("  Finding Images with Alpha Channels")
    print("=" * 30)

    def check_alpha_in_folder(folder_path, folder_name):
        images_with_alpha = []
        errors = []

        image_files = [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
        ]

        for filename in tqdm(image_files, desc=f"Checking {folder_name}"):
            file_path = os.path.join(folder_path, filename)
            try:
                with Image.open(file_path) as img:
                    if img.mode in ("RGBA", "LA") or (
                        img.mode == "P" and "transparency" in img.info
                    ):
                        images_with_alpha.append(filename)
            except Exception as e:
                errors.append((filename, str(e)))

        return images_with_alpha, errors

    hq_alpha_images, hq_errors = check_alpha_in_folder(hq_folder, "HQ")
    lq_alpha_images, lq_errors = check_alpha_in_folder(lq_folder, "LQ")

    print("\n" + "-" * 30)
    print("  Alpha Channel Analysis Summary")
    print("-" * 30)

    print(f"\nHQ Folder Results:")
    print(f"Found {len(hq_alpha_images)} images with alpha channels")
    if hq_alpha_images:
        print("\nExample HQ files with alpha:")
        for f in hq_alpha_images[:5]:
            print(f"  - {f}")
        if len(hq_alpha_images) > 5:
            print(f"  ... and {len(hq_alpha_images) - 5} more")

    print(f"\nLQ Folder Results:")
    print(f"Found {len(lq_alpha_images)} images with alpha channels")
    if lq_alpha_images:
        print("\nExample LQ files with alpha:")
        for f in lq_alpha_images[:5]:
            print(f"  - {f}")
        if len(lq_alpha_images) > 5:
            print(f"  ... and {len(lq_alpha_images) - 5} more")

    if hq_errors or lq_errors:
        print("\nErrors encountered:")
        for filename, error in (hq_errors + lq_errors)[:5]:
            print(f"  - {filename}: {error}")
        if len(hq_errors) + len(lq_errors) > 5:
            print(f"  ... and {len(hq_errors) + len(lq_errors) - 5} more errors")

    print("-" * 30)
    print("=" * 30)

    return {
        "hq_alpha": hq_alpha_images,
        "lq_alpha": lq_alpha_images,
        "hq_errors": hq_errors,
        "lq_errors": lq_errors,
    }


def remove_alpha_channels(hq_folder, lq_folder):
    """Remove alpha channels from images in HQ/LQ folders."""
    print("\n" + "=" * 30)
    print("  Removing Alpha Channels")
    print("=" * 30)

    alpha_results = find_alpha_channels(hq_folder, lq_folder)
    if not (alpha_results["hq_alpha"] or alpha_results["lq_alpha"]):
        print("\nNo images with alpha channels found to process.")
        return

    operation = get_file_operation_choice()
    destination = ""
    if operation != "inplace":
        destination = get_destination_path()
        if not destination:
            print(
                f"Operation aborted as no destination path was provided for {operation}."
            )
            return
        os.makedirs(os.path.join(destination, "hq"), exist_ok=True)
        os.makedirs(os.path.join(destination, "lq"), exist_ok=True)

    def remove_alpha(image_path, output_path):
        try:
            with Image.open(image_path) as img:
                if img.mode in ("RGBA", "LA"):
                    background = Image.new(
                        "RGB" if img.mode == "RGBA" else "L", img.size, "white"
                    )
                    if img.mode == "RGBA":
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img.convert("L"))
                    background.save(output_path, quality=95)
                    return True
                elif img.mode == "P" and "transparency" in img.info:
                    converted = img.convert("RGBA")
                    background = Image.new("RGB", img.size, "white")
                    background.paste(converted, mask=converted.split()[3])
                    background.save(output_path, quality=95)
                    return True
                else:
                    if operation == "copy":
                        shutil.copy2(image_path, output_path)
                    elif operation == "move":
                        shutil.move(image_path, output_path)
                    return True
        except Exception as e:
            return False, str(e)

    processed_count = 0
    errors = []

    for filename in tqdm(alpha_results["hq_alpha"], desc="Processing HQ Images"):
        src_path = os.path.join(hq_folder, filename)
        dest_path = (
            src_path
            if operation == "inplace"
            else os.path.join(
                destination,
                "hq",
                get_unique_filename(os.path.join(destination, "hq"), filename),
            )
        )

        try:
            if remove_alpha(src_path, dest_path):
                processed_count += 1
            else:
                errors.append(f"Failed to process HQ: {filename}")
        except Exception as e:
            errors.append(f"Error processing HQ {filename}: {e}")

    for filename in tqdm(alpha_results["lq_alpha"], desc="Processing LQ Images"):
        src_path = os.path.join(lq_folder, filename)
        dest_path = (
            src_path
            if operation == "inplace"
            else os.path.join(
                destination,
                "lq",
                get_unique_filename(os.path.join(destination, "lq"), filename),
            )
        )

        try:
            if remove_alpha(src_path, dest_path):
                processed_count += 1
            else:
                errors.append(f"Failed to process LQ: {filename}")
        except Exception as e:
            errors.append(f"Error processing LQ {filename}: {e}")

    print("\n" + "-" * 30)
    print("  Remove Alpha Channels Summary")
    print("-" * 30)
    print(f"Successfully processed: {processed_count} images")
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    print("-" * 30)
    print("=" * 30)
