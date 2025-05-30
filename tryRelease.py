import subprocess
import sys
import os


def list_gpu_processes():
    print("Listing all processes using the GPU...\n")
    result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
    print(result.stdout)
    # Parse PIDs from nvidia-smi output
    pids = []
    for line in result.stdout.splitlines():
        if " C+" in line or "python.exe" in line or "python" in line:
            parts = line.split()
            for part in parts:
                if part.isdigit():
                    pids.append(part)
                    break
    return list(set(pids))


def kill_process(pid):
    try:
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True)
        print(f"Killed process with PID {pid}")
    except Exception as e:
        print(f"Failed to kill PID {pid}: {e}")


def main():
    pids = list_gpu_processes()
    if not pids:
        print("No GPU-using processes found (other than system/display).")
        print("If you still have memory issues, try rebooting your computer.")
        return

    print("\nFound the following PIDs using the GPU:", pids)
    choice = input("Kill all these processes? (y/n): ").strip().lower()
    if choice == "y":
        for pid in pids:
            kill_process(pid)
        print("\nAll listed processes have been killed.")
    else:
        print("No processes were killed.")

    reboot = (
        input("Do you want to reboot your computer for a 100% clean GPU? (y/n): ")
        .strip()
        .lower()
    )
    if reboot == "y":
        print("Rebooting...")
        os.system("shutdown /r /t 0")


if __name__ == "__main__":
    main()
