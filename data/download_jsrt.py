import hashlib
import json
import os
import zipfile

import requests
from colorama import Fore
from tqdm import tqdm
from utils import get_file_hash

# Initialize colorama for ANSI escape sequences to work on all platforms
Fore.RESET  # Resets the color to default

# Base URL of the dataset
BASE_URL = "https://zenodo.org/records/7056076/files"

# Directory to save the downloaded files
DATA_DIR = "raw/jsrt"

# Checksums provided on the Zenodo page
# Format: {"filename": "checksum"}
# Example: {"example_file.txt": "example_checksum"}
CHECKSUMS = {
    "jpg.zip": "db5ff13ca89f7bea9d5360eb49ab026e",
    "landmarks.zip": "b453217c3d85c305a20937d58c4e2aed",
    "masks.zip": "3e9bb1c4bc1f5b2672ac4bfeabab16f4",
    "points.zip": "599cb1e648a19a66f9ad9f828847b57a",
}

EXPECTED_FILE_CHECKSUMS = {}

# Check if the checksums.json file exists before trying to load it
checksum_file_path = os.path.join(DATA_DIR, "checksums.json")
if os.path.exists(checksum_file_path):
    # Load the checksums from the JSON file
    with open(checksum_file_path, "r") as f:
        EXPECTED_FILE_CHECKSUMS = json.load(f)


def unzip_file(file_path, extract_to):
    """
    Unzips a file to a specified directory and deletes the zip file.
    """
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    # Delete the zip file after extraction
    os.remove(file_path)


def download_file(url, filename):
    """
    Download a file from a given URL and save it to the specified filename.
    Shows a colored progress bar while downloading.
    Returns True if download is successful, False otherwise.
    """
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size_in_bytes = int(response.headers.get("content-length", 0))
            block_size = 1024  # 1 Kibibyte

            with open(filename, "wb") as file:
                with tqdm(
                    total=total_size_in_bytes,
                    unit="iB",
                    unit_scale=True,
                    bar_format=Fore.BLUE + "{l_bar}{bar}" + Fore.RESET + "{r_bar}",
                ) as progress_bar:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        file.write(data)
            return True
        else:
            print(Fore.RED + f"Failed to download {url}")
            return False
    except Exception as e:
        print(Fore.RED + f"An error occurred while downloading {url}: {e}")
        return False


def verify_checksum(filename, expected_checksum):
    """
    Verify the file's MD5 checksum matches the expected checksum.
    """
    md5_hash = hashlib.md5()
    with open(filename, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    calculated_checksum = md5_hash.hexdigest()
    return calculated_checksum == expected_checksum


def verify_folder_contents(folder_path):
    """
    Verify the contents of the folder against expected checksums.
    """
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # Construct the full file path
            file_path = os.path.join(root, filename)

            # Construct the relative path as it appears in the checksums dictionary
            relative_path = os.path.relpath(file_path, start=DATA_DIR)

            expected_checksum = EXPECTED_FILE_CHECKSUMS.get(relative_path)
            if not expected_checksum:
                print(
                    Fore.RED
                    + f"No expected checksum for {relative_path}. Verification failed."
                )
                return False

            if get_file_hash(file_path) != expected_checksum:
                print(
                    Fore.RED
                    + f"Checksum mismatch for {relative_path}. Verification failed."
                )
                return False

    print(Fore.GREEN + f"All files in {folder_path} verified successfully.")
    return True


def generate_checksums_and_save(directory, checksum_file_path):
    """
    Generate a dictionary of file hashes for all files in a given directory and save it as a JSON file.
    """
    checksums = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, start=directory)
            checksums[relative_path] = get_file_hash(file_path)

    with open(checksum_file_path, "w") as f:
        json.dump(checksums, f, indent=4)


def main():
    """
    Main function to download (if not present), verify, unzip, and delete files.
    """
    # Create the data directory if it does not exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for filename, checksum in CHECKSUMS.items():
        file_path = os.path.join(DATA_DIR, filename)
        # Determine the expected directory name after unzipping
        expected_dir = os.path.join(DATA_DIR, filename.replace(".zip", ""))

        # Check if the unzipped directory already exists
        if os.path.exists(expected_dir):
            print(
                Fore.YELLOW
                + f"Directory '{expected_dir}' already exists. Verifying contents..."
            )
            if verify_folder_contents(expected_dir):
                print(
                    Fore.GREEN
                    + f"Contents of '{expected_dir}' verified successfully. Skipping download."
                )
                continue
            else:
                print(
                    Fore.RED
                    + f"Verification of '{expected_dir}' failed. Redownloading..."
                )

        # If the zip file exists, verify it, otherwise download it
        if os.path.exists(file_path):
            print(
                Fore.YELLOW + f"Zip file {filename} already exists. Verifying file..."
            )
            if verify_checksum(file_path, checksum):
                print(Fore.GREEN + f"{filename} verified successfully.")
                print(Fore.BLUE + f"Unzipping {filename}...")
                unzip_file(file_path, DATA_DIR)
                print(Fore.BLUE + f"Deleted {filename} after extraction.")
            else:
                print(Fore.RED + f"Checksum verification failed for {filename}.")
        else:
            # Download, verify, unzip, and delete the zip file
            file_url = f"{BASE_URL}/{filename}"
            print(Fore.BLUE + f"Downloading {filename}...")
            if download_file(file_url, file_path):
                print(Fore.YELLOW + f"Verifying {filename}...")
                if verify_checksum(file_path, checksum):
                    print(Fore.GREEN + f"{filename} verified successfully.")
                    print(Fore.BLUE + f"Unzipping {filename}...")
                    unzip_file(file_path, DATA_DIR)
                    print(Fore.BLUE + f"Deleted {filename} after extraction.")

                    # Generate and save checksums.json after fresh download and extraction
                    checksum_file_path = os.path.join(DATA_DIR, "checksums.json")
                    generate_checksums_and_save(DATA_DIR, checksum_file_path)
                    print(Fore.GREEN + "Checksums file generated and saved.")

                else:
                    print(Fore.RED + f"Checksum verification failed for {filename}.")
            else:
                print(
                    Fore.RED
                    + f"Skipping download and extraction due to failed download for {filename}."
                )


if __name__ == "__main__":
    main()
