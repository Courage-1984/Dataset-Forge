import os
import subprocess
import pandas as pd
from PIL import Image, ExifTags
from dataset_forge.utils.printing import (
    print_info,
    print_error,
    print_success,
    print_section,
    print_prompt,
)
from dataset_forge.utils.input_utils import (
    get_folder_path,
    get_path_with_history,
    get_input,
)
from dataset_forge.utils.progress_utils import tqdm
from dataset_forge.utils.memory_utils import memory_context, clear_memory
from dataset_forge.utils.history_log import log_operation
from dataset_forge.utils.file_utils import is_image_file


# --- Helper: Check exiftool ---
def _has_exiftool():
    try:
        subprocess.run(
            ["exiftool", "-ver"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except Exception:
        return False


# --- 1. Batch Extract Metadata ---
def batch_extract_metadata():
    """
    Batch extract EXIF/IPTC/XMP metadata from all images in a folder to CSV or SQLite.
    Uses exiftool for extraction and pandas for CSV/SQLite export.
    """
    print_section("Batch Extract Metadata")
    if not _has_exiftool():
        print_error(
            "ExifTool is not installed or not in PATH. Please install ExifTool."
        )
        print_info("See: https://exiftool.org/")
        return
    folder = get_folder_path("Enter folder to extract metadata from:")
    if not os.path.isdir(folder):
        print_error(f"Folder does not exist: {folder}")
        return
    print_info("Choose output format:")
    print_info("  1. CSV (default)")
    print_info("  2. SQLite")
    fmt = input("Select format [1-2]: ").strip() or "1"
    out_path = get_input(
        "Enter output file path (leave blank for default):", default=""
    )
    if not out_path:
        out_path = os.path.join(
            folder, "metadata.csv" if fmt == "1" else "metadata.sqlite"
        )
    print_info(f"Extracting metadata from all images in {folder}...")
    with memory_context("Batch Extract Metadata"):
        try:
            # Use exiftool to extract all metadata to CSV or JSON
            if fmt == "1":
                # CSV
                cmd = ["exiftool", "-csv", folder]
                result = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding="utf-8",
                )
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(result.stdout)
                print_success(f"Metadata extracted to CSV: {out_path}")
                log_operation(
                    "metadata_extract_csv",
                    f"Extracted metadata from {folder} to {out_path}",
                )
            else:
                # SQLite: extract JSON, load to pandas, save to SQLite
                cmd = ["exiftool", "-j", folder]
                result = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding="utf-8",
                )
                import json

                data = json.loads(result.stdout)
                df = pd.DataFrame(data)
                import sqlite3

                conn = sqlite3.connect(out_path)
                df.to_sql("metadata", conn, if_exists="replace", index=False)
                conn.close()
                print_success(f"Metadata extracted to SQLite: {out_path}")
                log_operation(
                    "metadata_extract_sqlite",
                    f"Extracted metadata from {folder} to {out_path}",
                )
        except Exception as e:
            print_error(f"Error extracting metadata: {e}")
        finally:
            clear_memory()


# --- 2. View/Edit Metadata (Single Image) ---
def view_edit_metadata():
    """
    View and edit metadata for a single image (EXIF/IPTC/XMP).
    Uses Pillow for EXIF and exiftool for advanced editing.
    """
    print_section("View/Edit Metadata")
    image_path = get_path_with_history("Enter image file path:")
    if not os.path.isfile(image_path):
        print_error(f"File does not exist: {image_path}")
        return
    print_info(f"Reading metadata for: {image_path}")
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                print_info("EXIF Metadata:")
                for tag, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    print_info(f"  {tag_name}: {value}")
            else:
                print_warning("No EXIF metadata found.")
    except Exception as e:
        print_error(f"Error reading EXIF: {e}")
    # Advanced: Use exiftool to show all metadata
    if _has_exiftool():
        print_info("\nFull metadata (exiftool):")
        try:
            cmd = ["exiftool", image_path]
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
            )
            print(result.stdout)
        except Exception as e:
            print_error(f"Error running exiftool: {e}")
    # Edit metadata
    print_info("\nEdit metadata:")
    print_info("  1. Set field (exiftool)")
    print_info("  2. Remove field (exiftool)")
    print_info("  0. Cancel")
    choice = input("Select action [1-2,0]: ").strip()
    if choice == "1":
        field = get_input("Enter metadata field name (e.g., Artist, Copyright):")
        value = get_input("Enter new value:")
        try:
            cmd = ["exiftool", f"-{field}={value}", image_path]
            subprocess.run(cmd, check=True)
            print_success(f"Set {field} to '{value}' in {image_path}")
            log_operation("metadata_edit", f"Set {field} in {image_path}")
        except Exception as e:
            print_error(f"Error setting metadata: {e}")
    elif choice == "2":
        field = get_input("Enter metadata field name to remove:")
        try:
            cmd = ["exiftool", f"-{field}=", image_path]
            subprocess.run(cmd, check=True)
            print_success(f"Removed {field} from {image_path}")
            log_operation("metadata_remove", f"Removed {field} from {image_path}")
        except Exception as e:
            print_error(f"Error removing metadata: {e}")
    else:
        print_info("No changes made.")
    clear_memory()


# --- 3. Filter by Metadata ---
def filter_by_metadata():
    """
    Filter images by metadata queries (e.g., ISO > 800, camera model, date).
    Loads extracted metadata (CSV/SQLite) and allows user to query/filter.
    """
    print_section("Filter Images by Metadata")
    print_info("Choose metadata source:")
    print_info("  1. CSV (from batch extract)")
    print_info("  2. SQLite (from batch extract)")
    src = input("Select source [1-2]: ").strip() or "1"
    meta_path = get_path_with_history("Enter path to metadata file:")
    if not os.path.isfile(meta_path):
        print_error(f"File does not exist: {meta_path}")
        return
    try:
        if src == "1":
            df = pd.read_csv(meta_path)
        else:
            import sqlite3

            conn = sqlite3.connect(meta_path)
            df = pd.read_sql_query("SELECT * FROM metadata", conn)
            conn.close()
        print_info(f"Loaded {len(df)} metadata records.")
        print_info(
            "Enter a pandas query string (e.g., 'ISO > 800 and Model == \"Canon\"'):"
        )
        query = get_input("Query:")
        try:
            filtered = df.query(query)
            print_info(f"Found {len(filtered)} matching images.")
            print_info("Show results? (y/n)")
            if input().strip().lower().startswith("y"):
                print(
                    filtered[
                        [
                            c
                            for c in filtered.columns
                            if "File" in c
                            or "SourceFile" in c
                            or "Directory" in c
                            or "FileName" in c
                        ]
                    ]
                )
            print_info("Export filtered list? (y/n)")
            if input().strip().lower().startswith("y"):
                out_path = get_input("Enter output CSV path:")
                filtered.to_csv(out_path, index=False)
                print_success(f"Exported filtered metadata to {out_path}")
        except Exception as e:
            print_error(f"Query error: {e}")
    except Exception as e:
        print_error(f"Error loading metadata: {e}")
    clear_memory()


# --- 4. Batch Anonymize Metadata ---
def batch_anonymize_metadata():
    """
    Batch anonymize (strip) all identifying metadata from a dataset using exiftool.
    Uses parallelization and robust error handling.
    """
    print_section("Batch Anonymize Metadata")
    if not _has_exiftool():
        print_error(
            "ExifTool is not installed or not in PATH. Please install ExifTool."
        )
        print_info("See: https://exiftool.org/")
        return
    folder = get_folder_path("Enter folder to anonymize:")
    if not os.path.isdir(folder):
        print_error(f"Folder does not exist: {folder}")
        return
    print_info(
        "This will irreversibly remove all metadata from all images in the folder!"
    )
    print_info("Are you sure? (y/n)")
    if not input().strip().lower().startswith("y"):
        print_info("Operation cancelled.")
        return
    files = [f for f in os.listdir(folder) if is_image_file(f)]
    if not files:
        print_warning("No image files found in folder.")
        return
    with memory_context("Batch Anonymize Metadata"):
        failed = []
        for fname in tqdm(files, desc="Anonymizing", unit="img"):
            fpath = os.path.join(folder, fname)
            try:
                subprocess.run(
                    ["exiftool", "-all=", "-overwrite_original", fpath],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                log_operation("metadata_anonymize", f"Anonymized {fpath}")
            except Exception as e:
                failed.append(fname)
        if failed:
            print_warning(f"Failed to anonymize {len(failed)} files: {failed}")
        else:
            print_success("All images anonymized successfully.")
        clear_memory()
