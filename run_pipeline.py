"""
run_pipeline.py — Run the full TACO garbage-detection pipeline in one shot.

Steps executed:
  1. map_classes.py        (remap 60 categories -> 2)
  2. split_dataset.py      (70 / 15 / 15 split)
  3. convert_to_yolo.py    (COCO JSON -> YOLO .txt labels)
  4. train.py              (YOLOv8n, N epochs)
  5. plot_metrics.py       (training metrics graphs)

NOTE: download.py is NOT run automatically because it takes 30–60 minutes.
      Run `python download.py` separately BEFORE this script.

Usage:
    python run_pipeline.py
    python run_pipeline.py --epochs 30 --skip_train
    python run_pipeline.py --skip_plot     # skip the metrics plot step
    python run_pipeline.py --show_plot     # show interactive plot window after training
"""

import subprocess
import sys
import argparse
import os

parser = argparse.ArgumentParser(description="Run the full TACO pipeline")
parser.add_argument("--epochs",     type=int,  default=100,       help="Training epochs (default: 100)")
parser.add_argument("--model",      default="yolov8n.pt",         help="YOLOv8 model (default: yolov8n.pt)")
parser.add_argument("--batch",      type=int,  default=16,        help="Batch size (default: 16)")
parser.add_argument("--skip_train", action="store_true",           help="Skip training step")
parser.add_argument("--skip_plot",  action="store_true",           help="Skip metrics plot step")
parser.add_argument("--show_plot",  action="store_true",           help="Open interactive plot window after training")
args = parser.parse_args()

python = sys.executable   # use the same interpreter that launched this script

STEPS = [
    ("Class Mapping",   [python, "map_classes.py"]),
    ("Dataset Split",   [python, "split_dataset.py"]),
    ("YOLO Conversion", [python, "convert_to_yolo.py"]),
]

if not args.skip_train:
    STEPS.append(("Training", [
        python, "train.py",
        "--epochs", str(args.epochs),
        "--model",  args.model,
        "--batch",  str(args.batch),
    ]))

if not args.skip_train and not args.skip_plot:
    plot_cmd = [python, "plot_metrics.py"]
    if args.show_plot:
        plot_cmd.append("--show")
    STEPS.append(("Metrics Plot", plot_cmd))

print("\n" + "=" * 60)
print("[RUN] TACO Garbage Detection — Full Pipeline")
print("=" * 60)

for step_num, (name, cmd) in enumerate(STEPS, 1):
    print(f"\n[{step_num}/{len(STEPS)}] {name} ...")
    print(f"    CMD: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"\n[ERR] Step '{name}' failed (exit code {result.returncode}).")
        print("   Fix the issue and re-run, or continue manually.")
        sys.exit(result.returncode)
    print(f"    [OK] {name} done.")

print("\n" + "=" * 60)
print("[OK] Pipeline complete!")
if not args.skip_train:
    print("   Best weights : runs/detect/taco_recycling/weights/best.pt")
if not args.skip_train and not args.skip_plot:
    print("   Metrics plot : runs/detect/taco_recycling/training_metrics.png")
print("\nNext steps:")
print("   python detect.py --source 0              (live webcam)")
print("   python detect.py --source image.jpg      (static image)")
print("   python plot_metrics.py --show            (re-open metrics window)")
print("=" * 60)
