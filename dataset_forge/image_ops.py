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
