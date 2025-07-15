from abc import ABC, abstractmethod
import os
from collections import Counter, defaultdict
from PIL import Image
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.io_utils import is_image_file
from dataset_forge.utils.monitoring import monitor_all, task_registry
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.printing import print_success
from dataset_forge.utils.audio_utils import play_done_sound


class DatasetAnalyzer(ABC):
    @abstractmethod
    def analyze(self, hq_folder, lq_folder, **kwargs):
        pass


class ScaleAnalyzer(DatasetAnalyzer):
    def analyze(self, hq_folder, lq_folder, verbose=True):
        hq_files = sorted(
            [
                f
                for f in os.listdir(hq_folder)
                if os.path.isfile(os.path.join(hq_folder, f)) and is_image_file(f)
            ]
        )
        lq_files = sorted(
            [
                f
                for f in os.listdir(lq_folder)
                if os.path.isfile(os.path.join(lq_folder, f)) and is_image_file(f)
            ]
        )
        scales = []
        inconsistent_scales = []
        missing_lq = []
        missing_hq = []
        for hq_file in tqdm(hq_files, desc="Finding Scale", disable=not verbose):
            if hq_file in lq_files:
                hq_path = os.path.join(hq_folder, hq_file)
                lq_path = os.path.join(lq_folder, hq_file)
                try:
                    with Image.open(hq_path) as hq_img:
                        hq_width, hq_height = hq_img.size
                    with Image.open(lq_path) as lq_img:
                        lq_width, lq_height = lq_img.size
                    if lq_width == 0 or lq_height == 0:
                        inconsistent_scales.append(
                            f"{hq_file}: Division by zero in LQ dimension"
                        )
                        continue
                    width_scale = hq_width / lq_width
                    height_scale = hq_height / lq_height
                    if abs(width_scale - height_scale) < 1e-9:
                        scales.append(round(width_scale, 2))
                    else:
                        inconsistent_scales.append(
                            f"{hq_file}: Inconsistent Scale: Width {width_scale:.2f}, Height {height_scale:.2f}"
                        )
                except Exception as e:
                    inconsistent_scales.append(f"Could not process file {hq_file}: {e}")
            else:
                missing_lq.append(hq_file)
        for lq_file in lq_files:
            if lq_file not in hq_files:
                missing_hq.append(lq_file)
        return {
            "total_hq_files": len(hq_files),
            "total_lq_files": len(lq_files),
            "processed_pairs": len(scales) + len(inconsistent_scales),
            "scales": scales,
            "inconsistent_scales": inconsistent_scales,
            "missing_lq": missing_lq,
            "missing_hq": missing_hq,
        }


class DimensionAnalyzer(DatasetAnalyzer):
    def analyze(self, folder_path, folder_name, verbose=True):
        files = sorted(
            [
                f
                for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
            ]
        )
        dimensions = []
        errors = []
        for file in tqdm(
            files, desc=f"Reporting Dimensions for {folder_name}", disable=not verbose
        ):
            file_path = os.path.join(folder_path, file)
            try:
                with Image.open(file_path) as img:
                    dimensions.append(img.size)
            except Exception as e:
                errors.append(f"{file}: {e}")
        return {
            "total_files": len(files),
            "successfully_processed": len(dimensions),
            "dimensions": dimensions,
            "errors": errors,
        }


class ConsistencyAnalyzer(DatasetAnalyzer):
    def analyze(self, folder_path, folder_name, verbose=True):
        files = sorted(
            [
                f
                for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f)) and is_image_file(f)
            ]
        )
        formats = defaultdict(list)
        modes = defaultdict(list)
        errors = []
        for file in tqdm(files, desc=f"Checking {folder_name}", disable=not verbose):
            file_path = os.path.join(folder_path, file)
            try:
                with Image.open(file_path) as img:
                    formats[img.format].append(file)
                    modes[img.mode].append(file)
            except Exception as e:
                errors.append(f"{file}: {e}")
        return {
            "total_files": len(files),
            "formats": formats,
            "modes": modes,
            "errors": errors,
        }
