"""
Map TACO's 60 original categories into 2 target classes:
  - Class 0: Recyclable
  - Class 1: Non-Recyclable

Reads  : data/annotations.json (original TACO COCO format)
Writes : data/annotations_remapped.json (COCO format, 2 categories)

Usage:
    python map_classes.py
    python map_classes.py --input_ann "c:/path/to/data/annotations.json" --output_ann data/annotations_remapped.json
"""

import json
import argparse
import os
from collections import defaultdict

# ─── Default paths ─────────────────────────────────────────────────────────────
TACO_DATA_DIR = os.path.join(
    os.path.expanduser("~"),
    "Downloads", "TACO-master", "TACO-master", "data"
)

parser = argparse.ArgumentParser(description="Remap TACO categories → Recyclable / Non-Recyclable")
parser.add_argument("--input_ann",  default=os.path.join(TACO_DATA_DIR, "annotations.json"),
                    help="Path to original TACO annotations JSON")
parser.add_argument("--output_ann", default=os.path.join(TACO_DATA_DIR, "annotations_remapped.json"),
                    help="Path for output remapped JSON")
args = parser.parse_args()

# ─── Class mapping ──────────────────────────────────────────────────────────────
#  0 = Recyclable  |  1 = Non-Recyclable
#  Any category not listed here gets mapped to Non-Recyclable by default.

RECYCLABLE_CATEGORIES = {
    # Metals
    "Aerosol",
    "Aluminium foil",
    "Drink can",
    "Food Can",
    "Metal bottle cap",
    "Metal lid",
    "Pop tab",
    "Scrap metal",
    "Six pack rings",
    # Glass
    "Glass bottle",
    "Glass cup",
    "Glass jar",
    "Broken glass",          # Recyclable if taken to glass bank
    # Paper / Cardboard
    "Corrugated carton",
    "Drink carton",
    "Egg carton",
    "Meal carton",
    "Other carton",
    "Pizza box",
    "Toilet tube",
    "Magazine paper",
    "Normal paper",
    "Paper bag",
    "Paper straw",
    "Wrapping paper",
    # Plastics (widely accepted)
    "Clear plastic bottle",
    "Other plastic bottle",
    "Plastic bottle cap",
    "Plastic lid",
    "Plastic film",
    "Produce bag",
}

NON_RECYCLABLE_CATEGORIES = {
    # Hazardous
    "Battery",
    # Contaminated / composite
    "Aluminium blister pack",
    "Carded blister pack",
    "Paper cup",             # Lined with plastic
    "Disposable plastic cup",
    "Foam cup",
    "Other plastic cup",
    "Food waste",
    "Tissues",
    "Plastified paper bag",
    "Garbage bag",
    "Single-use carrier bag",
    "Polypropylene bag",
    "Cereal bag",
    "Bread bag",
    "Crisp packet",
    "Other plastic wrapper",
    "Retort pouch",
    "Spread tub",
    "Tupperware",
    "Disposable food container",
    "Foam food container",
    "Other plastic container",
    "Plastic glooves",
    "Plastic utensils",
    "Rope & strings",
    "Shoe",
    "Squeezable tube",
    "Plastic straw",
    "Styrofoam piece",
    "Unlabeled litter",
    "Other plastic",
    "Cigarette",
}

# ─── Load annotations ───────────────────────────────────────────────────────────
print(f"Loading annotations from: {args.input_ann}")
with open(args.input_ann, "r") as f:
    dataset = json.load(f)

original_cats = {cat["id"]: cat["name"] for cat in dataset["categories"]}
print(f"Found {len(original_cats)} original categories.")

# ─── Build category ID → new class ID mapping ───────────────────────────────────
old_to_new = {}   # original cat id → new class id (0 or 1)
unmatched   = []

for cat_id, cat_name in original_cats.items():
    if cat_name in RECYCLABLE_CATEGORIES:
        old_to_new[cat_id] = 0
    elif cat_name in NON_RECYCLABLE_CATEGORIES:
        old_to_new[cat_id] = 1
    else:
        # Default unmapped categories to Non-Recyclable
        old_to_new[cat_id] = 1
        unmatched.append(cat_name)

if unmatched:
    print(f"\n[WARN] {len(unmatched)} categories not explicitly listed → defaulted to Non-Recyclable:")
    for name in unmatched:
        print(f"    - {name}")

# ─── New categories block ───────────────────────────────────────────────────────
new_categories = [
    {"id": 0, "name": "Recyclable",     "supercategory": "Waste"},
    {"id": 1, "name": "Non-Recyclable", "supercategory": "Waste"},
]

# ─── Remap annotations ─────────────────────────────────────────────────────────
new_annotations = []
skipped_anns = 0
class_counts = defaultdict(int)

for ann in dataset["annotations"]:
    orig_cat_id = ann["category_id"]
    if orig_cat_id not in old_to_new:
        skipped_anns += 1
        continue
    new_ann = dict(ann)
    new_ann["category_id"] = old_to_new[orig_cat_id]
    new_annotations.append(new_ann)
    class_counts[old_to_new[orig_cat_id]] += 1

# ─── Build output dataset ──────────────────────────────────────────────────────
output_dataset = {
    "info":        dataset.get("info", {}),
    "licenses":    dataset.get("licenses", []),
    "images":      dataset["images"],
    "annotations": new_annotations,
    "categories":  new_categories,
}

# ─── Save ──────────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(os.path.abspath(args.output_ann)), exist_ok=True)
with open(args.output_ann, "w") as f:
    json.dump(output_dataset, f)

# ─── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("[OK] Class remapping complete!")
print(f"   Original categories : {len(original_cats)}")
print(f"   New categories      : 2 (Recyclable / Non-Recyclable)")
print(f"   Total images        : {len(dataset['images'])}")
print(f"   Total annotations   : {len(new_annotations)}")
print(f"   Skipped annotations : {skipped_anns}")
print(f"\n   [PKG] Recyclable (0)     : {class_counts[0]} annotations")
print(f"   [BIN] Non-Recyclable (1) : {class_counts[1]} annotations")
print(f"\n   Output saved to: {args.output_ann}")
print("=" * 55)
