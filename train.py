"""
YOLOv8 Training Pipeline for Garbage Detection.

Trains YOLOv8n (nano, fastest) on the TACO dataset remapped to
  Class 0: Recyclable
  Class 1: Non-Recyclable

Prerequisites:
  1. Run download.py      → download images
  2. Run map_classes.py   → create annotations_remapped.json
  3. Run split_dataset.py → create train.json / val.json / test.json
  4. Run convert_to_yolo.py → create yolo_dataset/

Usage:
    python train.py
    python train.py --model yolov8s.pt --epochs 100 --imgsz 640 --batch 16
    python train.py --resume                          # resume from last checkpoint
    python train.py --tune --epochs 30 --iterations 30  # run hyperparameter tuner
"""

import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser(description="Train YOLOv8 on TACO garbage dataset")
parser.add_argument("--model",   default="yolov8n.pt",
                    help="YOLOv8 model variant: yolov8n/s/m/l/x.pt (default: yolov8n.pt)")
parser.add_argument("--data",    default="yolo_dataset/dataset.yaml",
                    help="Path to dataset.yaml")
parser.add_argument("--epochs",  type=int, default=100,
                    help="Number of training epochs (default: 100)")
parser.add_argument("--imgsz",   type=int, default=640,
                    help="Input image size (default: 640)")
parser.add_argument("--batch",   type=int, default=8,
                    help="Batch size (default: 8; reduce to 4 if memory errors)")
parser.add_argument("--workers", type=int, default=0,
                    help="DataLoader workers — set 0 on Windows (default: 0)")
parser.add_argument("--device",  default="",
                    help="Device: '' (auto), '0' (GPU 0), 'cpu' (default: auto)")
parser.add_argument("--project", default="runs/detect",
                    help="Output project directory")
parser.add_argument("--name",    default="taco_recycling",
                    help="Experiment name")
parser.add_argument("--resume",  action="store_true",
                    help="Resume training from last checkpoint")
                    
# Advanced / Tuning Options
parser.add_argument("--optimizer", default="auto", choices=["auto", "SGD", "Adam", "AdamW", "RMSProp"],
                    help="Optimizer to use (default: auto, try AdamW for better convergence)")
parser.add_argument("--lr0",     type=float, default=0.01,
                    help="Initial learning rate (default: 0.01, try 0.001 if loss plateaus)")
parser.add_argument("--close_mosaic", type=int, default=10,
                    help="Disable mosaic augmentation for final N epochs (default: 10)")
parser.add_argument("--tune",    action="store_true",
                    help="Run YOLOv8 hyperparameter tuner instead of standard training")
parser.add_argument("--iterations", type=int, default=30,
                    help="Number of tuning iterations if --tune is set (default: 30)")
args = parser.parse_args()

# ─── Validate dataset exists ───────────────────────────────────────────────────
if not os.path.isfile(args.data):
    print(f"[ERR] dataset.yaml not found at: {args.data}")
    print("   → Run convert_to_yolo.py first.")
    raise SystemExit(1)

# ─── Import & train ───────────────────────────────────────────────────────────
try:
    from ultralytics import YOLO
except ImportError:
    print("[ERR] ultralytics not installed. Run: pip install ultralytics")
    raise

print("\n" + "=" * 60)
if args.tune:
    print("[RUN] YOLOv8 Hyperparameter Tuning")
else:
    print("[RUN] YOLOv8 Garbage Detection Training")
print("=" * 60)
print(f"  Model       : {args.model}")
print(f"  Dataset     : {args.data}")
print(f"  Epochs      : {args.epochs}")
print(f"  Image size  : {args.imgsz}")
print(f"  Batch size  : {args.batch}")
print(f"  Optimizer   : {args.optimizer}")
print(f"  Learning Rt : {args.lr0}")
print(f"  Device      : {'auto' if args.device == '' else args.device}")
print(f"  Output      : {args.project}/{args.name}")
if args.tune:
    print(f"  Tune Iters  : {args.iterations}")
print("=" * 60 + "\n")

if args.resume:
    # Resume from last checkpoint
    last_ckpt = Path(args.project) / args.name / "weights" / "last.pt"
    if not last_ckpt.exists():
        print(f"[ERR] No checkpoint found at {last_ckpt}. Cannot resume.")
        raise SystemExit(1)
    model = YOLO(str(last_ckpt))
    print(f"[>>] Resuming from: {last_ckpt}")
else:
    model = YOLO(args.model)
    print(f"[>>] Initializing from pretrained: {args.model}")

if args.tune:
    # Run Hyperparameter Tuner
    model.tune(
        data      = args.data,
        epochs    = args.epochs,
        iterations= args.iterations,
        optimizer = args.optimizer,
        imgsz     = args.imgsz,
        batch     = args.batch,
        device    = args.device if args.device else None,
        project   = args.project,
        name      = args.name + "_tune",
    )
    print("\n[OK] Tuning complete! Best hyperparameters saved to:")
    print(f"     {args.project}/{args.name}_tune/tune/best_hyperparameters.yaml")
    sys.exit(0)

results = model.train(
    data      = args.data,
    epochs    = args.epochs,
    imgsz     = args.imgsz,
    batch     = args.batch,
    workers   = args.workers,
    device    = args.device if args.device else None,
    project   = args.project,
    name      = args.name,
    resume    = args.resume,
    optimizer = args.optimizer,
    lr0       = args.lr0,
    # Augmentation settings (good for small datasets)
    close_mosaic = args.close_mosaic,
    hsv_h     = 0.015,
    hsv_s     = 0.7,
    hsv_v     = 0.4,
    degrees   = 10.0,
    translate = 0.1,
    scale     = 0.5,
    flipud    = 0.05,
    fliplr    = 0.5,
    mosaic    = 1.0,
    mixup     = 0.1,
    # Verbose
    verbose   = True,
)

# ─── Print best weights path ───────────────────────────────────────────────────
best_pt = Path(results.save_dir) / "weights" / "best.pt"
print("\n" + "=" * 60)
print("[OK] Training complete!")
print(f"   Best model saved to : {best_pt}")
print(f"   Results / plots     : {results.save_dir}")
print("\n   To run inference:")
print(f"   python detect.py --source <image_or_0_for_webcam> --weights {best_pt}")
print("=" * 60)
