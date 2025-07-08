from abc import ABC, abstractmethod
import os
from PIL import Image
import shutil
import cv2
from tqdm import tqdm
from dataset_forge.common import (
    get_unique_filename,
    get_file_operation_choice,
    get_destination_path,
)


class ImageOperation(ABC):
    @abstractmethod
    def process(self, image_path, **kwargs):
        pass


class AlphaRemover(ImageOperation):
    def process(self, image_path, output_path=None, operation="inplace"):
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
                    save_path = output_path if output_path else image_path
                    background.save(save_path, quality=95)
                    return True, save_path
                elif img.mode == "P" and "transparency" in img.info:
                    converted = img.convert("RGBA")
                    background = Image.new("RGB", img.size, "white")
                    background.paste(converted, mask=converted.split()[3])
                    save_path = output_path if output_path else image_path
                    background.save(save_path, quality=95)
                    return True, save_path
                else:
                    if operation == "copy" and output_path:
                        shutil.copy2(image_path, output_path)
                        return True, output_path
                    elif operation == "move" and output_path:
                        shutil.move(image_path, output_path)
                        return True, output_path
                    return True, image_path
        except Exception as e:
            return False, str(e)


class CorruptionFixer(ImageOperation):
    def __init__(self, grayscale=False):
        self.grayscale = grayscale

    def process(self, image_path, output_path=None, operation="inplace"):
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False, "Failed to read image"
            if self.grayscale:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            save_path = output_path if output_path else image_path
            result = cv2.imwrite(save_path, image)
            if operation == "move" and image_path != save_path:
                os.remove(image_path)
            return result, save_path if result else "Failed to save image"
        except Exception as e:
            return False, str(e)


class ColorAdjuster(ImageOperation):
    def __init__(self, adjustment_type, factor):
        self.adjustment_type = adjustment_type
        self.factor = factor

    def process(self, image_path, output_path=None, operation="inplace"):
        try:
            from PIL import ImageEnhance

            with Image.open(image_path) as img:
                enhancer = None
                if self.adjustment_type == "brightness":
                    enhancer = ImageEnhance.Brightness(img)
                elif self.adjustment_type == "contrast":
                    enhancer = ImageEnhance.Contrast(img)
                elif self.adjustment_type == "color":
                    enhancer = ImageEnhance.Color(img)
                elif self.adjustment_type == "sharpness":
                    enhancer = ImageEnhance.Sharpness(img)
                else:
                    return False, f"Unknown adjustment type: {self.adjustment_type}"
                img_enhanced = enhancer.enhance(self.factor)
                save_path = output_path if output_path else image_path
                img_enhanced.save(save_path, quality=95)
                return True, save_path
        except Exception as e:
            return False, str(e)


class ICCToSRGBConverter(ImageOperation):
    def process(self, input_path, output_path=None, operation="copy"):
        """
        Convert image(s) from ICC profile to sRGB, preserving alpha and directory structure.
        If input_path is a file, output_path is the output file or folder (if operation is 'copy').
        If input_path is a folder, output_path is the output folder.
        operation: 'copy' (default, outputs to output_path), 'inplace' (overwrites input files)
        """
        from PIL import Image, ImageCms
        from io import BytesIO
        import os

        def convert_image(img_path, out_path):
            try:
                img = Image.open(img_path)
                has_alpha = "A" in img.getbands()
                if has_alpha:
                    alpha = img.split()[-1]
                    rgb_img = img.convert("RGB")
                else:
                    rgb_img = img
                if "icc_profile" in img.info:
                    input_profile = ImageCms.ImageCmsProfile(
                        BytesIO(img.info["icc_profile"])
                    )
                    srgb_profile = ImageCms.createProfile("sRGB")
                    rgb_converted = ImageCms.profileToProfile(
                        rgb_img, input_profile, srgb_profile, outputMode="RGB"
                    )
                else:
                    rgb_converted = rgb_img
                if has_alpha:
                    channels = list(rgb_converted.split())
                    channels.append(alpha)
                    final_image = Image.merge("RGBA", channels)
                else:
                    final_image = rgb_converted
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                final_image.save(out_path, "PNG", icc_profile=None)
                return True, out_path
            except Exception as e:
                return False, f"Error processing {img_path}: {str(e)}"

        if os.path.isfile(input_path):
            if operation == "inplace":
                out_path = input_path
            else:
                if output_path and os.path.isdir(output_path):
                    base = os.path.splitext(os.path.basename(input_path))[0] + ".png"
                    out_path = os.path.join(output_path, base)
                else:
                    out_path = output_path or input_path
            return convert_image(input_path, out_path)
        elif os.path.isdir(input_path):
            if not output_path:
                return False, "Output folder must be specified for folder input."
            results = []
            for root, dirs, files in os.walk(input_path):
                for file in files:
                    if file.lower().endswith(
                        (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp")
                    ):
                        in_file = os.path.join(root, file)
                        rel_path = os.path.relpath(in_file, input_path)
                        out_file = os.path.join(
                            output_path, os.path.splitext(rel_path)[0] + ".png"
                        )
                        if operation == "inplace":
                            result = convert_image(in_file, in_file)
                        else:
                            result = convert_image(in_file, out_file)
                        results.append(result)
            return True, results
        else:
            return (
                False,
                f"Invalid input: {input_path} is neither a file nor a directory.",
            )


def get_image_size(image_path):
    """Returns (width, height) of the image at image_path."""
    with Image.open(image_path) as img:
        return img.width, img.height
