import os
import shutil
from typing import Optional, Tuple
from PIL import Image
import torch
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.input_utils import (
    get_file_operation_choice,
    get_destination_path,
)
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
)
from dataset_forge.utils.memory_utils import (
    clear_memory,
    memory_context,
    clear_cuda_cache,
)
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.audio_utils import play_done_sound

try:
    from transformers import AutoImageProcessor, SiglipForImageClassification
except ImportError:
    print_error(
        "transformers not installed. Please install it to use sketch extraction."
    )
    raise

MODEL_NAME = "prithivMLmods/Sketch-126-DomainNet"
SKETCH_CLASS_IDS = list(range(0, 126))  # 0–125 = sketch classes

# Model and processor are loaded lazily to avoid slow startup
_model = None
_processor = None


def get_model_and_processor():
    global _model, _processor
    if _model is None or _processor is None:
        print_info(
            "Loading Sketch-126-DomainNet model (first time use may take a while)..."
        )
        _processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
        _model = SiglipForImageClassification.from_pretrained(MODEL_NAME)
        _model.eval()
    return _model, _processor


def is_sketch(image_path: str, confidence_threshold: float = 0.5) -> bool:
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print_warning(f"Could not open image: {image_path} — {e}")
        return False
    model, processor = get_model_and_processor()
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        pred_class = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred_class].item()
    return (pred_class in SKETCH_CLASS_IDS) and (confidence >= confidence_threshold)


def extract_sketches_from_folder(
    input_dir: str,
    output_dir: str,
    operation: str = "copy",
    confidence_threshold: float = 0.5,
) -> Tuple[int, int]:
    os.makedirs(output_dir, exist_ok=True)
    supported_exts = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
    found, errors = 0, 0
    image_files = []
    for root, _, files in os.walk(input_dir):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in supported_exts:
                image_files.append(os.path.join(root, fname))
    for input_path in tqdm(image_files, desc=f"Scanning {os.path.basename(input_dir)}"):
        try:
            if is_sketch(input_path, confidence_threshold=confidence_threshold):
                dest_path = os.path.join(output_dir, os.path.basename(input_path))
                if operation == "copy":
                    shutil.copy2(input_path, dest_path)
                elif operation == "move":
                    shutil.move(input_path, dest_path)
                found += 1
        except Exception as e:
            print_warning(f"Error processing {input_path}: {e}")
            errors += 1
    return found, errors


def extract_sketches_workflow(
    hq_folder: Optional[str] = None,
    lq_folder: Optional[str] = None,
    single_folder: Optional[str] = None,
    confidence_threshold: float = 0.5,
    operation: Optional[str] = None,
    output_base: Optional[str] = None,
):
    """
    Main workflow for extracting sketches from single folder or HQ/LQ pairs.
    """
    with memory_context("Sketch Extraction"):
        if not operation:
            operation = get_file_operation_choice()
        if not output_base:
            output_base = get_destination_path(
                "Enter output folder for extracted sketches:"
            )
        if not output_base:
            print_error("No output folder specified. Aborting.")
            return
        if single_folder:
            print_info(f"Extracting sketches from: {single_folder}")
            out_dir = os.path.join(output_base, "sketches")
            found, errors = extract_sketches_from_folder(
                single_folder, out_dir, operation, confidence_threshold
            )
            print_success(
                f"Extracted {found} sketches from {single_folder} (errors: {errors})"
            )
        elif hq_folder and lq_folder:
            print_info(f"Extracting sketches from HQ: {hq_folder}")
            out_hq = os.path.join(output_base, "hq_sketches")
            found_hq, errors_hq = extract_sketches_from_folder(
                hq_folder, out_hq, operation, confidence_threshold
            )
            print_info(f"Extracted {found_hq} sketches from HQ (errors: {errors_hq})")
            print_info(f"Extracting sketches from LQ: {lq_folder}")
            out_lq = os.path.join(output_base, "lq_sketches")
            found_lq, errors_lq = extract_sketches_from_folder(
                lq_folder, out_lq, operation, confidence_threshold
            )
            print_success(
                f"Extracted {found_lq} sketches from LQ (errors: {errors_lq})"
            )
        else:
            print_error(
                "You must specify either a single folder or both HQ and LQ folders."
            )
        clear_memory()
