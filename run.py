import subprocess
import sys

if __name__ == "__main__":
    try:
        # Run main.py using the current Python interpreter
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user (Ctrl+C). Exiting...")
