import hashlib
import os

import requests
from tqdm import tqdm

# Base URL of the dataset
BASE_URL = "https://zenodo.org/records/7056076/files"

# Directory to save the downloaded files
DATA_DIR = "data/raw/jsrt"

# Checksums provided on the Zenodo page
# Format: {"filename": "checksum"}
# Example: {"example_file.txt": "example_checksum"}
CHECKSUMS = {
    "jpg.zip": "db5ff13ca89f7bea9d5360eb49ab026e",
    "landmarks.zip": "b453217c3d85c305a20937d58c4e2aed",
    "masks.zip": "3e9bb1c4bc1f5b2672ac4bfeabab16f4",
    "points.zip": "599cb1e648a19a66f9ad9f828847b57a",
}


def download_file(url, filename):
    """
    Download a file from a given URL and save it to the specified filename.
    Shows a progress bar while downloading.
    Returns True if download is successful, False otherwise.
    """
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size_in_bytes = int(response.headers.get("content-length", 0))
            block_size = 1024  # 1 Kibibyte
            progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)
            with open(filename, "wb") as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print("ERROR, something went wrong")
                return False
            return True
        else:
            print(f"Failed to download {url}")
            return False
    except Exception as e:
        print(f"An error occurred while downloading {url}: {e}")
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


def main():
    """
    Main function to download and verify files.
    """
    # Create the directory if it does not exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for filename, checksum in CHECKSUMS.items():
        file_path = os.path.join(DATA_DIR, filename)
        file_url = f"{BASE_URL}/{filename}"

        # Download the file
        print(f"Downloading {filename}...")
        if download_file(file_url, file_path):
            # Verify the checksum only if the download was successful
            print(f"Verifying {filename}...")
            if verify_checksum(file_path, checksum):
                print(f"{filename} verified successfully.")
            else:
                print(f"Checksum verification failed for {filename}.")
        else:
            # Skip the file if download was not successful
            print(f"Skipping verification for {filename} due to failed download.")


if __name__ == "__main__":
    main()
