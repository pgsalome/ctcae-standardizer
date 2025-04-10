#!/usr/bin/env python3
"""
Download the CTCAE v5.0 Excel file if it doesn't exist locally.
"""
import os
import sys
import requests
from pathlib import Path

# CTCAE v5.0 URL
CTCAE_URL = "https://ctep.cancer.gov/protocoldevelopment/electronic_applications/docs/CTCAE_v5.0.xlsx"
OUTPUT_PATH = Path("data/CTCAE_v5.0.xlsx")


def download_ctcae():
    """Download the CTCAE v5.0 Excel file."""
    # Create data directory if it doesn't exist
    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)

    # Check if file already exists
    if OUTPUT_PATH.exists():
        print(f"CTCAE file already exists at {OUTPUT_PATH}")
        return True

    print(f"Downloading CTCAE v5.0 from {CTCAE_URL}...")
    try:
        response = requests.get(CTCAE_URL, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the file
        with open(OUTPUT_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Successfully downloaded CTCAE v5.0 to {OUTPUT_PATH}")
        return True
    except Exception as e:
        print(f"Error downloading CTCAE file: {e}")
        return False


if __name__ == "__main__":
    success = download_ctcae()
    sys.exit(0 if success else 1)