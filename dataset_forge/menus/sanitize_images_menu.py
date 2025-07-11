import os
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import (
    print_info,
    print_success,
    print_warning,
    print_error,
    print_prompt,
)
from dataset_forge.utils.color import Mocha
from dataset_forge.actions import sanitize_images_actions
from dataset_forge.menus import session_state
import subprocess


def sanitize_images_menu():
    """Menu for sanitizing images: metadata removal, renaming, normalization, ICC to sRGB, steganography checks."""
    while True:
        print_info("\n=== Sanitize Images ===")
        print_info("1. Single folder")
        print_info("2. HQ/LQ paired folders")
        print_info("0. Back")
        mode = input("Select mode [1-2, 0]: ").strip()
        if mode == "0":
            break
        if mode not in ("1", "2"):
            print_warning("Invalid selection.")
            continue
        if mode == "1":
            folder = input("Enter folder path: ").strip()
            if not folder or not os.path.isdir(folder):
                print_error("Folder does not exist.")
                continue
            input_path = folder
        else:
            hq = input("Enter HQ folder path: ").strip()
            lq = input("Enter LQ folder path: ").strip()
            if not os.path.isdir(hq) or not os.path.isdir(lq):
                print_error("Both HQ and LQ folders must exist.")
                continue
            # Use parent directory as input_path
            input_path = os.path.dirname(hq.rstrip("/\\"))
        output_folder = input(
            "Enter output folder (will be created if missing): "
        ).strip()
        if not output_folder:
            print_error("Output folder is required.")
            continue
        if os.path.abspath(output_folder) == os.path.abspath(input_path):
            print_error("Output folder must be different from input folder.")
            continue
        remove_alpha = (
            input("Remove transparency (alpha channel)? [y/N]: ").strip().lower() == "y"
        )
        icc_to_srgb = (
            input("Run ICC to sRGB conversion? [Y/n]: ").strip().lower() != "n"
        )
        run_steg = (
            input("Run steganography checks (steghide/zsteg)? [y/N]: ").strip().lower()
            == "y"
        )
        steg_tools = (False, False)
        if run_steg:
            steghide = input("Use steghide? [Y/n]: ").strip().lower() != "n"
            zsteg = input("Use zsteg? [Y/n]: ").strip().lower() != "n"
            steg_tools = (steghide, zsteg)
        dry_run = input("Dry run (no changes)? [y/N]: ").strip().lower() == "y"
        print_info("\n=== Environment Diagnostics: PATH and zsteg ===")
        try:
            result = subprocess.run(["python", "-u", "print_zsteg_env.py"], check=False)
            if result.returncode != 0:
                print_info("[Diagnostics] print_zsteg_env.py did not run successfully.")
        except FileNotFoundError:
            print_info("[Diagnostics] print_zsteg_env.py not found in project root.")
        except Exception as e:
            print_warning(f"Could not run print_zsteg_env.py: {e}")
        print_info("=== End Diagnostics ===\n")
        zsteg_results_file = sanitize_images_actions.sanitize_images(
            input_path,
            output_folder,
            remove_alpha=remove_alpha,
            icc_to_srgb=icc_to_srgb,
            run_steg=run_steg,
            steg_tools=steg_tools,
            dry_run=dry_run,
        )
        if zsteg_results_file:
            print_prompt("\nView detailed zsteg results? [Y/n]: ")
            resp = input().strip().lower()
            if resp in ("", "y", "yes"):
                try:
                    import sys, subprocess

                    if sys.platform.startswith("win"):
                        os.startfile(zsteg_results_file)
                    elif sys.platform.startswith("darwin"):
                        subprocess.run(["open", zsteg_results_file], check=False)
                    else:
                        subprocess.run(["xdg-open", zsteg_results_file], check=False)
                except Exception as e:
                    print_warning(f"Could not open zsteg results file: {e}")
            else:
                print_info(f"zsteg results saved to: {zsteg_results_file}")
        print_prompt("\nPress Enter to return to the menu...")
        input()
