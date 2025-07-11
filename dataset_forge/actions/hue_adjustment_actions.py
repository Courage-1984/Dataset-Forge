import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.file_utils import get_unique_filename
from dataset_forge.utils.file_utils import is_image_file


def adjust_image(img, brightness=None, contrast=None, hue=None):
    # img: numpy array (BGR)
    if brightness is not None:
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Brightness(pil_img)
        pil_img = enhancer.enhance(brightness)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    if contrast is not None:
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(contrast)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    if hue is not None:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[..., 0] = (hsv[..., 0].astype(int) + int(hue)) % 180
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img


def process_folder(
    input_folder,
    output_folder,
    brightness=None,
    contrast=None,
    hue=None,
    duplicates=1,
    real_name=False,
    paired_lq_folder=None,
    paired_output_lq_folder=None,
):
    os.makedirs(output_folder, exist_ok=True)
    if paired_lq_folder and paired_output_lq_folder:
        os.makedirs(paired_output_lq_folder, exist_ok=True)
        files = [
            f
            for f in os.listdir(input_folder)
            if is_image_file(f)
            and os.path.isfile(os.path.join(input_folder, f))
            and os.path.isfile(os.path.join(paired_lq_folder, f))
        ]
    else:
        files = [
            f
            for f in os.listdir(input_folder)
            if is_image_file(f) and os.path.isfile(os.path.join(input_folder, f))
        ]
    for filename in tqdm(files, desc="Hue/Brightness/Contrast Adjustment"):
        img_path = os.path.join(input_folder, filename)
        img = cv2.imread(img_path)
        if img is None:
            print(f"Failed to read {img_path}")
            continue
        if paired_lq_folder and paired_output_lq_folder:
            lq_path = os.path.join(paired_lq_folder, filename)
            lq_img = cv2.imread(lq_path)
            if lq_img is None:
                print(f"Failed to read {lq_path}")
                continue
        for i in range(duplicates):
            # Randomize adjustments if duplicates > 1
            b = brightness
            c = contrast
            h = hue
            if duplicates > 1:
                if brightness is not None:
                    b = np.random.uniform(max(0.1, brightness - 0.2), brightness + 0.2)
                if contrast is not None:
                    c = np.random.uniform(max(0.1, contrast - 0.2), contrast + 0.2)
                if hue is not None:
                    h = np.random.randint(max(0, int(hue - 20)), int(hue + 20) + 1)
            adj_img = adjust_image(img, brightness=b, contrast=c, hue=h)
            if paired_lq_folder and paired_output_lq_folder:
                adj_lq_img = adjust_image(lq_img, brightness=b, contrast=c, hue=h)
            base, ext = os.path.splitext(filename)
            if real_name:
                out_name = f"{base}_{i}{ext}" if duplicates > 1 else filename
            else:
                out_name = get_unique_filename(
                    output_folder, f"{base}_{i}{ext}" if duplicates > 1 else filename
                )
            out_path = os.path.join(output_folder, out_name)
            cv2.imwrite(out_path, adj_img)
            if paired_lq_folder and paired_output_lq_folder:
                out_lq_path = os.path.join(paired_output_lq_folder, out_name)
                cv2.imwrite(out_lq_path, adj_lq_img)
