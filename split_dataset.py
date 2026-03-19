"""
Split the remapped TACO annotations into train / val / test sets.

Reads  : data/annotations_remapped.json (output of map_classes.py)
Writes : data/train.json, data/val.json, data/test.json

Usage:
    python split_dataset.py
    python split_dataset.py --input_ann data/annotations_remapped.json --train 0.70 --val 0.15 --test 0.15
"""

import json
import argparse
import os
import random
import copy
from collections import defaultdict

# ─── Default paths ─────────────────────────────────────────────────────────────
TACO_DATA_DIR = os.path.join(
    os.path.expanduser("~"),
    "Downloads", "TACO-master", "TACO-master", "data"
)

parser = argparse.ArgumentParser(description="Split TACO dataset into train/val/test")
parser.add_argument("--input_ann", default=os.path.join(TACO_DATA_DIR, "annotations_remapped.json"),
                    help="Path to remapped annotations JSON")
parser.add_argument("--output_dir", default=TACO_DATA_DIR,
                    help="Directory to save split JSON files")
parser.add_argument("--train",  type=float, default=0.70, help="Train fraction (default: 0.70)")
parser.add_argument("--val",    type=float, default=0.15, help="Val   fraction (default: 0.15)")
parser.add_argument("--test",   type=float, default=0.15, help="Test  fraction (default: 0.15)")
parser.add_argument("--seed",   type=int,   default=42,   help="Random seed (default: 42)")
args = parser.parse_args()

assert abs(args.train + args.val + args.test - 1.0) < 1e-6, \
    "Train + Val + Test fractions must sum to 1.0"

# ─── Load ──────────────────────────────────────────────────────────────────────
print(f"Loading: {args.input_ann}")
with open(args.input_ann, "r") as f:
    dataset = json.load(f)

images = dataset["images"]
annotations = dataset["annotations"]
random.seed(args.seed)
random.shuffle(images)

n = len(images)
n_test  = max(1, int(n * args.test))
n_val   = max(1, int(n * args.val))
n_train = n - n_test - n_val

print(f"\nTotal images : {n}")
print(f"  Train      : {n_train}  ({n_train/n*100:.1f}%)")
print(f"  Val        : {n_val}    ({n_val/n*100:.1f}%)")
print(f"  Test       : {n_test}   ({n_test/n*100:.1f}%)")

test_imgs  = images[:n_test]
val_imgs   = images[n_test : n_test + n_val]
train_imgs = images[n_test + n_val:]

# ─── Build image-id sets ───────────────────────────────────────────────────────
test_ids  = {img["id"] for img in test_imgs}
val_ids   = {img["id"] for img in val_imgs}
train_ids = {img["id"] for img in train_imgs}

# ─── Split annotations ─────────────────────────────────────────────────────────
split_anns = {"train": [], "val": [], "test": []}
for ann in annotations:
    iid = ann["image_id"]
    if iid in train_ids:
        split_anns["train"].append(ann)
    elif iid in val_ids:
        split_anns["val"].append(ann)
    elif iid in test_ids:
        split_anns["test"].append(ann)

# ─── Write splits ──────────────────────────────────────────────────────────────
os.makedirs(args.output_dir, exist_ok=True)
base = {"info": dataset.get("info", {}),
        "licenses": dataset.get("licenses", []),
        "categories": dataset["categories"]}

for split, imgs, img_ids in [("train", train_imgs, train_ids),
                               ("val",   val_imgs,   val_ids),
                               ("test",  test_imgs,  test_ids)]:
    out = copy.deepcopy(base)
    out["images"]      = imgs
    out["annotations"] = split_anns[split]
    out_path = os.path.join(args.output_dir, f"{split}.json")
    with open(out_path, "w") as f:
        json.dump(out, f)

    ann_counts = defaultdict(int)
    for ann in split_anns[split]:
        ann_counts[ann["category_id"]] += 1
    r = ann_counts.get(0, 0)
    nr = ann_counts.get(1, 0)
    print(f"\n  [{split}] {out_path}")
    print(f"    Images: {len(imgs)}  |  Recyclable: {r}  |  Non-Recyclable: {nr}")

print("\n[OK] Dataset split complete!")
