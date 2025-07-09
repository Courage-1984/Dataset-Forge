import os
from typing import List, Tuple, Optional
from dataset_forge.utils.history_log import log_operation


def compare_folders(
    folder1: str, folder2: str, extensions: Optional[List[str]] = None
) -> Tuple[List[str], List[str]]:
    """
    Compare the contents of two folders and return lists of files missing in each.
    Optionally filter by file extensions.
    Returns (missing_in_folder1, missing_in_folder2)
    """

    def list_files(folder):
        files = set(os.listdir(folder))
        if extensions:
            files = {f for f in files if os.path.splitext(f)[1].lower() in extensions}
        return files

    files1 = list_files(folder1)
    files2 = list_files(folder2)

    missing_in_folder1 = sorted(list(files2 - files1))
    missing_in_folder2 = sorted(list(files1 - files2))
    result = f"Missing in {folder1}: {missing_in_folder1}, Missing in {folder2}: {missing_in_folder2}"
    log_operation("folder_compare", f"Compared {folder1} and {folder2}: {result}")
    return missing_in_folder1, missing_in_folder2


def folders_match(
    folder1: str, folder2: str, extensions: Optional[List[str]] = None
) -> bool:
    """
    Return True if both folders contain the same file names (optionally filtered by extension).
    """

    def list_files(folder):
        files = set(os.listdir(folder))
        if extensions:
            files = {f for f in files if os.path.splitext(f)[1].lower() in extensions}
        return files

    return list_files(folder1) == list_files(folder2)
