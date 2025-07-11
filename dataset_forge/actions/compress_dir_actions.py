# compress_dir_actions.py - Business logic for directory/folder compression
import os
import shutil
from dataset_forge.utils.progress_utils import tqdm


def compress_directory(
    src_hq=None,
    src_lq=None,
    single_folder=None,
    archive_format="zip",
    compression_level=5,
):
    """
    Compress directories (archive as .zip, .tar, .tar.gz).
    - src_hq, src_lq: HQ/LQ parent paths (if both provided, archive both)
    - single_folder: single folder path (if provided, archive it)
    - archive_format: 'zip', 'tar', 'gztar'
    - compression_level: 1-9 (where supported)
    """
    folders = []
    if single_folder:
        folders.append(single_folder)
    elif src_hq and src_lq:
        folders.extend([src_hq, src_lq])
    else:
        print("No valid input folder(s) provided.")
        return

    for folder in folders:
        if not os.path.isdir(folder):
            print(f"Not a directory: {folder}")
            continue
        base_name = os.path.abspath(folder)
        out_name = base_name + (
            ".zip"
            if archive_format == "zip"
            else ".tar.gz" if archive_format == "gztar" else ".tar"
        )
        # Count files for progress bar
        file_list = []
        for root, _, files in os.walk(folder):
            for f in files:
                file_list.append(os.path.join(root, f))
        print(f"Archiving {folder} to {out_name} ({len(file_list)} files)...")
        # Use tqdm for progress
        with tqdm(
            total=len(file_list), desc=f"Archiving {os.path.basename(folder)}", ncols=80
        ) as pbar:

            def _progress_filter(tarinfo):
                pbar.update(1)
                return tarinfo

            if archive_format == "zip":
                # shutil.make_archive does not support progress, so do it manually
                import zipfile

                compression = zipfile.ZIP_DEFLATED
                with zipfile.ZipFile(
                    out_name, "w", compression, compresslevel=compression_level
                ) as zf:
                    for file in file_list:
                        arcname = os.path.relpath(file, folder)
                        zf.write(file, arcname)
                        pbar.update(1)
            elif archive_format == "gztar":
                import tarfile

                with tarfile.open(
                    out_name, "w:gz", compresslevel=compression_level
                ) as tf:
                    for file in file_list:
                        arcname = os.path.relpath(file, folder)
                        tf.add(file, arcname=arcname, filter=_progress_filter)
            elif archive_format == "tar":
                import tarfile

                with tarfile.open(out_name, "w") as tf:
                    for file in file_list:
                        arcname = os.path.relpath(file, folder)
                        tf.add(file, arcname=arcname, filter=_progress_filter)
            else:
                print(f"Unsupported archive format: {archive_format}")
                return
        print(f"Archive created: {out_name}")
