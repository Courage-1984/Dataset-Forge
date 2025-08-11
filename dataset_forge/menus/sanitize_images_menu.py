import os
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_prompt,
    print_header,
    print_section,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.menus import session_state
import subprocess
from dataset_forge.utils.input_utils import ask_yes_no, get_folder_path


def sanitize_images_menu():
    from dataset_forge.actions import sanitize_images_actions
    from dataset_forge.utils.printing import print_header, print_section
    from dataset_forge.utils.color import Mocha

    # Define menu context for help system
    menu_context = {
        "Purpose": "Sanitize images by removing metadata and optimizing file formats",
        "Total Options": "2 sanitization modes",
        "Navigation": "Use numbers 1-2 to select, 0 to go back",
        "Key Features": [
            "Single folder sanitization - Process individual folders",
            "HQ/LQ paired folders - Process paired datasets while preserving alignment",
            "Metadata removal - Strip EXIF and other metadata",
            "Format optimization - Convert to optimized formats",
            "Dry run mode - Preview changes without applying them"
        ],
        "Tips": [
            "Use dry run mode first to preview changes",
            "Ensure output folder is different from input folder",
            "HQ/LQ mode preserves file pairing and alignment"
        ]
    }

    options = {
        "1": ("📁 Single Folder Sanitization", lambda: run_single_folder_sanitization()),
        "2": ("🔗 HQ/LQ Paired Folders Sanitization", lambda: run_hq_lq_sanitization()),
        "0": ("⬅️ Back to Utilities Menu", None),
    }

    while True:
        try:
            key = show_menu(
                "🧹 Sanitize Images Workflow",
                options,
                Mocha.lavender,
                current_menu="Sanitize Images",
                menu_context=menu_context
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break
        except Exception as e:
            print_error(f"Menu error: {e}")
            break


def run_single_folder_sanitization():
    """Run single folder sanitization workflow."""
    from dataset_forge.actions import sanitize_images_actions
    
    print_header(
        "🧹 Sanitize Images Workflow - Single Folder", color=Mocha.lavender
    )
    
    input_path = get_folder_path("Select the folder to sanitize")
    if not input_path:
        print_error("No folder selected. Returning to menu.")
        return
        
    output_folder = get_folder_path(
        "Select the output folder (will be created if missing)"
    )
    if not output_folder:
        print_error("Output folder is required.")
        return
    if os.path.abspath(output_folder) == os.path.abspath(input_path):
        print_error("Output folder must be different from input folder.")
        return
        
    print_section("Workflow Options", char="-", color=Mocha.sapphire)
    dry_run = ask_yes_no(
        "Perform a dry run (no changes will be made)?", default=False
    )
    
    print_header("Summary of Selected Options", char="-", color=Mocha.green)
    print_info(f"Input folder: {input_path}")
    print_info(f"Output folder: {output_folder}")
    print_info(f"Dry run: {'Yes' if dry_run else 'No'}")
    
    print_section("Confirm and Run", char="-", color=Mocha.green)
    if not ask_yes_no("Proceed with these settings?", default=True):
        print_warning("Operation cancelled by user. Returning to menu.")
        return
        
    print_section("Environment Diagnostics", char="-", color=Mocha.yellow)
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-u", "tools/print_zsteg_env.py"], check=False
        )
        if result.returncode != 0:
            print_info("[Diagnostics] print_zsteg_env.py did not run successfully.")
    except FileNotFoundError:
        print_info("[Diagnostics] print_zsteg_env.py not found in project root.")
    except Exception as e:
        print_warning(f"Could not run print_zsteg_env.py: {e}")
    print_info("=== End Diagnostics ===\n")
    
    print_section("Sanitize Images Progress", color=Mocha.lavender)
    # --- Run the workflow (all step prompts now handled inside) ---
    summary = sanitize_images_actions.sanitize_images(
        input_path,
        output_folder,
        dry_run=dry_run,
    )
    
    # --- Print visually distinct summary box ---
    print_header(
        "📝 Sanitize Images Workflow Summary 📝", char="=", color=Mocha.green
    )
    for step, status in summary.items():
        if step == "📄 Zsteg results file":
            continue
        color = Mocha.green if ("Run" in status) else Mocha.peach
        print_info(color + f"{step:35} : {status}" + Mocha.reset)
    if "📄 Zsteg results file" in summary:
        print_info(f"📄 Zsteg results file: {summary['📄 Zsteg results file']}")
    print_section("", char="-", color=Mocha.lavender)
    input("Press Enter to return to the Sanitize Images menu...")
    print_header("🧹 Sanitize Images Workflow 🧹", char="=", color=Mocha.lavender)


def run_hq_lq_sanitization():
    """Run HQ/LQ paired folders sanitization workflow."""
    from dataset_forge.actions import sanitize_images_actions
    
    print_header(
        "🧹 Sanitize Images Workflow - HQ/LQ Paired Folders", color=Mocha.lavender
    )
    
    print_section("Select HQ/LQ Folders", char="-", color=Mocha.sapphire)
    hq = get_folder_path("Select the HQ folder")
    lq = get_folder_path("Select the LQ folder")
    if not hq or not lq:
        print_error("Both HQ and LQ folders must be selected.")
        return
    input_path = os.path.dirname(hq.rstrip("/\\"))
    
    output_folder = get_folder_path(
        "Select the output folder (will be created if missing)"
    )
    if not output_folder:
        print_error("Output folder is required.")
        return
    if os.path.abspath(output_folder) == os.path.abspath(input_path):
        print_error("Output folder must be different from input folder.")
        return
        
    print_section("Workflow Options", char="-", color=Mocha.sapphire)
    dry_run = ask_yes_no(
        "Perform a dry run (no changes will be made)?", default=False
    )
    
    print_header("Summary of Selected Options", char="-", color=Mocha.green)
    print_info(f"HQ folder: {hq}")
    print_info(f"LQ folder: {lq}")
    print_info(f"Output folder: {output_folder}")
    print_info(f"Dry run: {'Yes' if dry_run else 'No'}")
    
    print_section("Confirm and Run", char="-", color=Mocha.green)
    if not ask_yes_no("Proceed with these settings?", default=True):
        print_warning("Operation cancelled by user. Returning to menu.")
        return
        
    print_section("Environment Diagnostics", char="-", color=Mocha.yellow)
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-u", "tools/print_zsteg_env.py"], check=False
        )
        if result.returncode != 0:
            print_info("[Diagnostics] print_zsteg_env.py did not run successfully.")
    except FileNotFoundError:
        print_info("[Diagnostics] print_zsteg_env.py not found in project root.")
    except Exception as e:
        print_warning(f"Could not run print_zsteg_env.py: {e}")
    print_info("=== End Diagnostics ===\n")
    
    print_section("Sanitize Images Progress", color=Mocha.lavender)
    # --- Run the workflow (all step prompts now handled inside) ---
    summary = sanitize_images_actions.sanitize_images(
        input_path,
        output_folder,
        dry_run=dry_run,
    )
    
    # --- Print visually distinct summary box ---
    print_header(
        "📝 Sanitize Images Workflow Summary 📝", char="=", color=Mocha.green
    )
    for step, status in summary.items():
        if step == "📄 Zsteg results file":
            continue
        color = Mocha.green if ("Run" in status) else Mocha.peach
        print_info(color + f"{step:35} : {status}" + Mocha.reset)
    if "📄 Zsteg results file" in summary:
        print_info(f"📄 Zsteg results file: {summary['📄 Zsteg results file']}")
    print_section("", char="-", color=Mocha.lavender)
    input("Press Enter to return to the Sanitize Images menu...")
    print_header("🧹 Sanitize Images Workflow 🧹", char="=", color=Mocha.lavender)
