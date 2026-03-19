"""
Garbage Detection Inference Script.

Runs the trained YOLOv8 model on:
  - A static image  : python detect.py --source path/to/image.jpg
  - A folder        : python detect.py --source path/to/folder/
  - Webcam (live)   : python detect.py --source 0
  - Video file      : python detect.py --source path/to/video.mp4

Results are displayed in a window and (optionally) saved.

Requirements:
  pip install ultralytics opencv-python
"""

import argparse
import os
import sys
import cv2
import numpy as np
from pathlib import Path

# ─── Colours ──────────────────────────────────────────────────────────────────
CLASS_COLORS = {
    0: (0,  200,  60),    # Recyclable     → Green
    1: (0,   60, 220),    # Non-Recyclable → Red (BGR)
}
CLASS_NAMES = {0: "Recyclable", 1: "Non-Recyclable"}

# ─── Args ─────────────────────────────────────────────────────────────────────
DEFAULT_WEIGHTS = os.path.join("runs", "detect", "taco_recycling", "weights", "best.pt")

parser = argparse.ArgumentParser(description="Garbage detection inference with YOLOv8")
parser.add_argument("--source",  required=True,
                    help="Input: image path | folder | video path | 0 (webcam)")
parser.add_argument("--weights", default=DEFAULT_WEIGHTS,
                    help=f"Path to trained model weights (default: {DEFAULT_WEIGHTS})")
parser.add_argument("--conf",    type=float, default=0.35,
                    help="Confidence threshold (default: 0.35)")
parser.add_argument("--iou",     type=float, default=0.45,
                    help="IoU threshold for NMS (default: 0.45)")
parser.add_argument("--imgsz",   type=int,   default=640,
                    help="Inference image size (default: 640)")
parser.add_argument("--save",    action="store_true",
                    help="Save annotated output alongside task")
parser.add_argument("--no_show", action="store_true",
                    help="Do not display window (useful for headless servers)")
parser.add_argument("--device",  default="",
                    help="Device: '' (auto) | '0' (GPU) | 'cpu'")
args = parser.parse_args()

# ─── Load model ───────────────────────────────────────────────────────────────
try:
    from ultralytics import YOLO
except ImportError:
    print("[ERR] ultralytics not installed. Run: pip install ultralytics")
    sys.exit(1)

if not os.path.isfile(args.weights):
    print(f"[ERR] Weights file not found: {args.weights}")
    print("   → Train the model first with: python train.py")
    sys.exit(1)

print(f"\n[LOAD] Loading model: {args.weights}")
model = YOLO(args.weights)

# ─── Determine if source is webcam / video / image ────────────────────────────
is_webcam = args.source.isdigit()
source    = int(args.source) if is_webcam else args.source

# ─── Helper: draw annotated frame ─────────────────────────────────────────────
def draw_detections(frame, result):
    """Overlay bounding boxes on a BGR frame from a YOLO Result object."""
    boxes = result.boxes
    if boxes is None or len(boxes) == 0:
        return frame

    for box in boxes:
        cls_id = int(box.cls[0])
        conf   = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        color  = CLASS_COLORS.get(cls_id, (200, 200, 200))
        label  = f"{CLASS_NAMES.get(cls_id, cls_id)}  {conf:.0%}"

        # Rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness=2)

        # Label background
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, y1 - th - baseline - 6), (x1 + tw + 4, y1), color, -1)

        # Label text (white)
        cv2.putText(frame, label, (x1 + 2, y1 - baseline - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

    return frame

# ─── Determine save path ──────────────────────────────────────────────────────
output_dir = Path("runs/detect/inference")
output_dir.mkdir(parents=True, exist_ok=True)

# ─── Inference ────────────────────────────────────────────────────────────────
if is_webcam:
    # ── LIVE WEBCAM ──────────────────────────────────────────────────────────
    print(f"\n[CAM] Opening webcam (source={source}) ...  Press 'q' to quit.\n")
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("[ERR] Cannot open webcam.")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Optional video writer
    writer = None
    if args.save:
        fourcc     = cv2.VideoWriter_fourcc(*"mp4v")
        save_path  = str(output_dir / "webcam_output.mp4")
        frame_w    = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer     = cv2.VideoWriter(save_path, fourcc, 20, (frame_w, frame_h))
        print(f"[SAVE] Saving output to: {save_path}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(
            source  = frame,
            conf    = args.conf,
            iou     = args.iou,
            imgsz   = args.imgsz,
            device  = args.device if args.device else None,
            verbose = False,
        )
        annotated = draw_detections(frame, results[0])

        if not args.no_show:
            cv2.imshow("[REC] Garbage Detector  |  q = quit", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if writer:
            writer.write(annotated)

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    print("\n[OK] Webcam session ended.")

else:
    # ── STATIC IMAGE / FOLDER / VIDEO ─────────────────────────────────────────
    print(f"\n[IMG] Running inference on: {source}\n")

    results = model.predict(
        source  = source,
        conf    = args.conf,
        iou     = args.iou,
        imgsz   = args.imgsz,
        device  = args.device if args.device else None,
        stream  = True,   # generator — handles large folders/videos
        verbose = True,
    )

    for i, result in enumerate(results):
        frame = result.orig_img
        annotated = draw_detections(frame, result)

        # Display
        if not args.no_show:
            win_title = f"[REC] Garbage Detector  |  q=quit  n=next"
            cv2.imshow(win_title, annotated)
            key = cv2.waitKey(0 if Path(str(source)).is_file() else 1) & 0xFF
            if key == ord("q"):
                break

        # Save
        if args.save:
            src_path  = Path(result.path) if hasattr(result, "path") else Path(f"frame_{i:04d}.jpg")
            save_path = output_dir / f"pred_{src_path.name}"
            cv2.imwrite(str(save_path), annotated)
            print(f"   [SAVE] Saved: {save_path}")

    cv2.destroyAllWindows()

    # Print detection summary
    if hasattr(results, "__iter__"):
        pass  # results already consumed above
    print("\n[OK] Inference complete!")
    if args.save:
        print(f"   Annotated outputs saved in: {output_dir}")
