import os
import shutil
import cv2
import concurrent.futures
import numpy as np
from typing import List, Tuple, Optional, Literal


class MisalignmentDetector:
    """
    Detects misaligned image pairs between two folders (HQ/LQ),
    moves or copies them to a destination, and saves overlays for visual inspection.
    """

    def __init__(self, threshold: float = 0.7, num_workers: int = 8):
        self.threshold = threshold
        self.num_workers = num_workers

    @staticmethod
    def overlay_images(img1_path: str, img2_path: str, dest_path: str):
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        if img1 is None or img2 is None:
            return False
        if img1.shape != img2.shape:
            # Resize img2 to img1's shape for overlay
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        overlay = cv2.addWeighted(img1, 0.5, img2, 0.5, 0)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        cv2.imwrite(dest_path, overlay)
        return True

    @staticmethod
    def compare_images(img1_path: str, img2_path: str) -> Optional[float]:
        img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
        if img1 is None or img2 is None or img1.shape != img2.shape:
            return None
        try:
            _, shift = cv2.phaseCorrelate(np.float32(img1), np.float32(img2))
            score = np.linalg.norm(shift)
            return score
        except Exception:
            return None

    def find_common_files(self, hq_folder: str, lq_folder: str) -> List[str]:
        hq_files = {
            os.path.relpath(os.path.join(root, file), hq_folder)
            for root, _, files in os.walk(hq_folder)
            for file in files
        }
        lq_files = {
            os.path.relpath(os.path.join(root, file), lq_folder)
            for root, _, files in os.walk(lq_folder)
            for file in files
        }
        return sorted(hq_files & lq_files)

    def process_pair(
        self,
        filename: str,
        hq_folder: str,
        lq_folder: str,
        dest_folder: str,
        op: Literal["move", "copy"] = "move",
    ) -> Optional[str]:
        hq_path = os.path.join(hq_folder, filename)
        lq_path = os.path.join(lq_folder, filename)
        if not (os.path.isfile(hq_path) and os.path.isfile(lq_path)):
            return None
        score = self.compare_images(hq_path, lq_path)
        if score is None or score >= self.threshold:
            return None
        # Prepare destination paths
        dest_hq = os.path.join(dest_folder, "hq", filename)
        dest_lq = os.path.join(dest_folder, "lq", filename)
        overlay_path = os.path.join(dest_folder, "overlays", filename)
        os.makedirs(os.path.dirname(dest_hq), exist_ok=True)
        os.makedirs(os.path.dirname(dest_lq), exist_ok=True)
        os.makedirs(os.path.dirname(overlay_path), exist_ok=True)
        # Move or copy
        if op == "move":
            shutil.move(hq_path, dest_hq)
            shutil.move(lq_path, dest_lq)
        else:
            shutil.copy2(hq_path, dest_hq)
            shutil.copy2(lq_path, dest_lq)
        self.overlay_images(dest_hq, dest_lq, overlay_path)
        return filename

    def scan_and_process(
        self,
        hq_folder: str,
        lq_folder: str,
        dest_folder: str,
        op: Literal["move", "copy"] = "move",
    ) -> List[str]:
        common_files = self.find_common_files(hq_folder, lq_folder)
        moved = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.num_workers
        ) as executor:
            futures = [
                executor.submit(
                    self.process_pair, f, hq_folder, lq_folder, dest_folder, op
                )
                for f in common_files
            ]
            for fut in concurrent.futures.as_completed(futures):
                result = fut.result()
                if result:
                    moved.append(result)
        return moved
