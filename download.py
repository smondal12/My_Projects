"""
Improved TACO image downloader with retry logic, tqdm progress bars, and error handling.
Original script by Pedro F. Proenza, 2019. Enhanced version.

Usage:
    python download.py
    python download.py --dataset_path ./data/annotations.json
    python download.py --dataset_path "c:/Users/suraj/Downloads/TACO-master/TACO-master/data/annotations.json"
"""

import os
import argparse
import json
import time
from io import BytesIO

import requests
from PIL import Image
from tqdm import tqdm

# --- Default path points to the existing TACO-master annotations ---
TACO_DATA_DIR = os.path.join(
    os.path.expanduser("~"),
    "Downloads", "TACO-master", "TACO-master", "data"
)
DEFAULT_ANNOTATIONS = os.path.join(TACO_DATA_DIR, "annotations.json")

parser = argparse.ArgumentParser(description="Download TACO dataset images from Flickr/S3")
parser.add_argument("--dataset_path", required=False,
                    default=DEFAULT_ANNOTATIONS,
                    help="Path to annotations JSON file")
parser.add_argument("--use_resized", action="store_true",
                    help="Download 640px resized images instead of originals (smaller, faster)")
parser.add_argument("--max_retries", type=int, default=3,
                    help="Max download retries per image (default: 3)")
parser.add_argument("--timeout", type=int, default=30,
                    help="Request timeout in seconds (default: 30)")
args = parser.parse_args()

dataset_dir = os.path.dirname(os.path.abspath(args.dataset_path))
print(f"\n[DIR] Dataset directory : {dataset_dir}")
print(f"[FILE] Annotations file  : {args.dataset_path}")
print("[INFO] Resuming from where we left off (existing files are skipped).\n")

# Load annotations
with open(args.dataset_path, "r") as f:
    annotations = json.load(f)

images = annotations["images"]
nr_images = len(images)
skipped = 0
failed = []

print(f"Total images in dataset: {nr_images}\n")

for image in tqdm(images, desc="Downloading images", unit="img"):
    file_name = image["file_name"]
    file_path = os.path.join(dataset_dir, file_name)

    # Skip already-downloaded images
    if os.path.isfile(file_path):
        skipped += 1
        continue

    # Choose URL: resized (smaller) or original
    if args.use_resized and image.get("flickr_640_url"):
        url = image["flickr_640_url"]
    else:
        url = image["flickr_url"]

    # Create subdirectory if needed
    subdir = os.path.dirname(file_path)
    os.makedirs(subdir, exist_ok=True)

    # Download with retries
    success = False
    for attempt in range(1, args.max_retries + 1):
        try:
            response = requests.get(url, timeout=args.timeout)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))

            # Save with EXIF if available
            try:
                exif = img.info.get("exif")
                if exif:
                    img.save(file_path, exif=exif)
                else:
                    img.save(file_path)
            except Exception:
                img.save(file_path)

            success = True
            break
        except Exception as e:
            if attempt < args.max_retries:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                failed.append((file_name, str(e)))

    if not success:
        tqdm.write(f"  [WARN] Failed: {file_name}")

# Summary
print("\n" + "=" * 50)
print(f"[OK] Download complete!")
print(f"   Total images    : {nr_images}")
print(f"   Already existed : {skipped}")
print(f"   Newly downloaded: {nr_images - skipped - len(failed)}")
print(f"   Failed          : {len(failed)}")
if failed:
    print("\n[WARN] Failed images:")
    for name, err in failed:
        print(f"   {name}: {err}")
print("=" * 50)
