# src/pipeview/cache.py
import sys
import os

# Define a consistent path for the temporary data cache file
CACHE_FILE_PATH = os.path.join(os.path.expanduser("~"), ".pipeview_cache")

def main():
    """Reads data from stdin and saves it to a cache file."""
    if sys.stdin.isatty():
        print("This script is for capturing piped data.")
        print("Usage: some-command | pipeview-cache")
        sys.exit(1)

    piped_content = sys.stdin.read()
    if not piped_content.strip():
        print("Received empty input. Cache not updated.")
        sys.exit(0)

    try:
        with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(piped_content)
        print(f"Data captured successfully. Now run 'pipeview' to see it.")
    except Exception as e:
        print(f"Error: Could not write cache file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()