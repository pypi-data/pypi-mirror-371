import subprocess
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: pyr <filename.py> [args...]")
        sys.exit(1)

    script = sys.argv[1]

    if not os.path.exists(script):
        print(f"Error: File '{script}' not found.")
        sys.exit(1)

    # Forward any extra args to the script
    args = sys.argv[2:]

    # Run script with same Python interpreter
    subprocess.run([sys.executable, script] + args)
