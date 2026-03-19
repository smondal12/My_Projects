# ♻️ TACO Garbage Detection System — Quick Start

## 📁 Project Structure
```
waste segregation/
├── requirements.txt      # All Python dependencies
├── download.py           # Download images from Flickr/S3
├── map_classes.py        # Remap 60 TACO classes → Recyclable / Non-Recyclable
├── split_dataset.py      # Split into train / val / test sets
├── convert_to_yolo.py    # Convert COCO JSON → YOLO .txt labels
├── train.py              # YOLOv8 training pipeline
└── detect.py             # Inference: image / folder / webcam / video
```

---

## 🔧 Step 0 — Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🔽 Step 1 — Download Images
The `annotations.json` is already in your TACO-master folder.
Run this to download the actual images (~1 500 photos, 2–4 GB, 30–60 min):
```powershell
python download.py
# To download smaller 640px versions (faster, less disk):
python download.py --use_resized
```
> ✅ The script **auto-resumes** if interrupted — just run it again.

---

## 🏷️ Step 2 — Remap Classes
```powershell
python map_classes.py
```
Maps 60 TACO categories → **2 classes** and writes `annotations_remapped.json`:
| Class | ID | Examples |
|---|---|---|
| Recyclable | 0 | Bottles, cans, cardboard, paper, glass |
| Non-Recyclable | 1 | Cigarettes, food waste, styrofoam, straws |

---

## ✂️ Step 3 — Split Dataset
```powershell
python split_dataset.py
```
Writes `train.json` / `val.json` / `test.json` with a **70 / 15 / 15** split.

---

## 🔄 Step 4 — Convert to YOLO Format
```powershell
python convert_to_yolo.py
```
Creates `yolo_dataset/` with `images/` and `labels/` folders + `dataset.yaml`.

---

## 🚀 Step 5 — Train
```powershell
# Default: YOLOv8 Nano, 100 epochs, batch 16
python train.py

# Faster variant with GPU:
python train.py --model yolov8s.pt --epochs 100 --batch 16

# Resume a previous run:
python train.py --resume
```
Best weights saved to `runs/detect/taco_recycling/weights/best.pt`

---

## 🎛️ Step 5b — Tune for Better Performance (Optional)
If your model is not converging well, use the built-in hyperparameter tuner:
```powershell
python train.py --tune --epochs 30 --iterations 30
```
Or manually override hyperparameters for more stable training:
```powershell
python train.py --optimizer AdamW --lr0 0.001 --close_mosaic 10
```

---

## 🎯 Step 6 — Detect
```powershell
# Static image
python detect.py --source path/to/image.jpg

# Entire folder
python detect.py --source path/to/folder/

# Live webcam  (press Q to quit)
python detect.py --source 0

# Save output
python detect.py --source 0 --save
```

---

## 🧪 Run Full Pipeline at Once
```powershell
python run_pipeline.py
```

---

## 📌 Notes
- **Download time**: ~30–60 min for all images on a normal connection.
- **Training time**: ~10–20 min with GPU; several hours on CPU (use `yolov8n.pt`).
- **Accuracy**: Expect moderate accuracy on 2 classes — TACO is a small dataset.
  Adding more data or fine-tuning longer will improve results.
