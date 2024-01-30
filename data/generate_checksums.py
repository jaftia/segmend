import hashlib
import json
import os
import sys

from utils import get_file_hash


def generate_checksums(directory):
    """
    Generate a dictionary of file hashes for all files in a given directory.
    """
    checksums = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            # Generate relative file path for the dictionary key
            relative_path = os.path.relpath(file_path, start=directory)
            checksums[relative_path] = get_file_hash(file_path)
    return checksums


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_checksums.py path/to/directory")
        sys.exit(1)

    directory = sys.argv[1]
    checksums = generate_checksums(directory)

    with open("checksums.json", "w") as f:
        json.dump(checksums, f, indent=4)


if __name__ == "__main__":
    main()
