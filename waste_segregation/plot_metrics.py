"""
plot_metrics.py — Plot YOLOv8 training metrics from results.csv

Reads   : runs/detect/taco_recycling/results.csv  (auto-saved by ultralytics)
Produces: 4 panels saved as 'training_metrics.png' in the same run folder

Plots:
  1. Train vs Val Losses  (box + cls + dfl)
  2. Precision & Recall   (validation)
  3. mAP@0.5  &  mAP@0.5:0.95
  4. Learning Rate schedule

Usage:
    python plot_metrics.py
    python plot_metrics.py --results_csv runs/detect/taco_recycling/results.csv
    python plot_metrics.py --show         # also open interactive window
"""

import argparse
import os
import sys

import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — safe on Windows
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ─── Args ─────────────────────────────────────────────────────────────────────
DEFAULT_CSV = os.path.join("runs", "detect", "taco_recycling", "results.csv")

parser = argparse.ArgumentParser(description="Plot YOLOv8 training metrics")
parser.add_argument("--results_csv", default=DEFAULT_CSV,
                    help=f"Path to results.csv  (default: auto-discovered from runs/detect/)")
parser.add_argument("--show", action="store_true",
                    help="Also open an interactive matplotlib window")
args = parser.parse_args()

# ─── Auto-discover latest results.csv ──────────────────────────────────────────
# YOLOv8 sometimes creates nested folders like runs/detect/runs/detect.
# This scans the entire runs/ directory recursively for the most recent results.csv.
def find_latest_results_csv():
    """Return path of most recently modified results.csv under runs/."""
    runs_dir = "runs"
    if not os.path.isdir(runs_dir):
        return None
    candidates = []
    for root, dirs, files in os.walk(runs_dir):
        if "results.csv" in files:
            csv_path = os.path.join(root, "results.csv")
            candidates.append((os.path.getmtime(csv_path), csv_path))
    if not candidates:
        return None
    candidates.sort(reverse=True)   # most recent first
    return candidates[0][1]

csv_path = args.results_csv
if not os.path.isfile(csv_path):
    print(f"[WARN] Default path not found: {csv_path}")
    print("       Scanning runs/ directory recursively for the latest results.csv ...")
    csv_path = find_latest_results_csv()
    if csv_path:
        print(f"[OK]  Auto-discovered: {csv_path}\n")
    else:
        print("[ERR] No results.csv found anywhere under runs/.")
        print("      Run training first:  python train.py")
        sys.exit(1)

# ─── Load CSV ─────────────────────────────────────────────────────────────────

df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()          # ultralytics adds leading spaces
epochs = df["epoch"] + 1                     # 0-indexed -> 1-indexed

print(f"[OK] Loaded {len(df)} epochs from: {csv_path}")
print(f"     Columns: {list(df.columns)}\n")

# ─── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#0f0f1a",
    "axes.facecolor":    "#15152a",
    "axes.edgecolor":    "#3a3a5c",
    "axes.labelcolor":   "#c8c8e0",
    "xtick.color":       "#8888aa",
    "ytick.color":       "#8888aa",
    "grid.color":        "#252540",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
    "text.color":        "#e0e0f0",
    "legend.facecolor":  "#1e1e35",
    "legend.edgecolor":  "#3a3a5c",
    "legend.fontsize":   8,
    "font.family":       "sans-serif",
})

PALETTE = {
    "train_box":  "#4fc3f7",
    "val_box":    "#0288d1",
    "train_cls":  "#f48fb1",
    "val_cls":    "#c62828",
    "train_dfl":  "#aed581",
    "val_dfl":    "#558b2f",
    "precision":  "#ffb74d",
    "recall":     "#ff7043",
    "map50":      "#64ffda",
    "map5095":    "#1de9b6",
    "lr0":        "#ce93d8",
    "lr1":        "#9c27b0",
    "lr2":        "#6a1b9a",
}

# ─── Safely fetch a column (returns None if absent) ───────────────────────────
def col(name):
    return df[name] if name in df.columns else None

# ─── Figure layout ────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 12), constrained_layout=True)
fig.suptitle("Garbage Detection — YOLOv8 Training Metrics",
             fontsize=16, fontweight="bold", color="#ffffff", y=1.01)

gs  = gridspec.GridSpec(2, 3, figure=fig)
ax1 = fig.add_subplot(gs[0, :2])   # Losses (wide)
ax2 = fig.add_subplot(gs[0, 2])    # Learning rate
ax3 = fig.add_subplot(gs[1, 0])    # Precision & Recall
ax4 = fig.add_subplot(gs[1, 1])    # mAP
ax5 = fig.add_subplot(gs[1, 2])    # Class balance (bar)

for ax in (ax1, ax2, ax3, ax4, ax5):
    ax.grid(True)
    ax.set_xlabel("Epoch", fontsize=9)

# ── Panel 1: Losses ──────────────────────────────────────────────────────────
ax1.set_title("Train vs Validation Loss", fontweight="bold")
loss_pairs = [
    ("train/box_loss", "val/box_loss",  "Box Loss",  PALETTE["train_box"],  PALETTE["val_box"]),
    ("train/cls_loss", "val/cls_loss",  "Class Loss", PALETTE["train_cls"], PALETTE["val_cls"]),
    ("train/dfl_loss", "val/dfl_loss",  "DFL Loss",  PALETTE["train_dfl"],  PALETTE["val_dfl"]),
]
for (tcol, vcol, label, tc, vc) in loss_pairs:
    t, v = col(tcol), col(vcol)
    if t is not None:
        ax1.plot(epochs, t, color=tc,  lw=2,   label=f"Train {label}")
    if v is not None:
        ax1.plot(epochs, v, color=vc,  lw=2, ls="--", label=f"Val {label}")
ax1.set_ylabel("Loss")
ax1.legend(ncol=2)

# ── Panel 2: Learning Rate ────────────────────────────────────────────────────
ax2.set_title("Learning Rate Schedule", fontweight="bold")
for lr_col, label, c in [("lr/pg0", "LR pg0", PALETTE["lr0"]),
                           ("lr/pg1", "LR pg1", PALETTE["lr1"]),
                           ("lr/pg2", "LR pg2", PALETTE["lr2"])]:
    v = col(lr_col)
    if v is not None:
        ax2.plot(epochs, v, color=c, lw=2, label=label)
ax2.set_ylabel("Learning Rate")
ax2.yaxis.set_major_formatter(plt.FormatStrFormatter("%.2e"))
ax2.legend()

# ── Panel 3: Precision & Recall ───────────────────────────────────────────────
ax3.set_title("Precision & Recall (Val)", fontweight="bold")
for metric_col, label, c in [
    ("metrics/precision(B)", "Precision", PALETTE["precision"]),
    ("metrics/recall(B)",    "Recall",    PALETTE["recall"]),
]:
    v = col(metric_col)
    if v is not None:
        ax3.plot(epochs, v, color=c, lw=2.5, label=label)
ax3.set_ylim(0, 1.05)
ax3.set_ylabel("Score")
ax3.legend()

# ── Panel 4: mAP ─────────────────────────────────────────────────────────────
ax4.set_title("mAP (Val)", fontweight="bold")
for metric_col, label, c in [
    ("metrics/mAP50(B)",      "mAP@0.50",      PALETTE["map50"]),
    ("metrics/mAP50-95(B)",   "mAP@0.50:0.95", PALETTE["map5095"]),
]:
    v = col(metric_col)
    if v is not None:
        ax4.plot(epochs, v, color=c, lw=2.5, label=label)
ax4.set_ylim(0, 1.05)
ax4.set_ylabel("mAP")
ax4.legend()

# ── Panel 5: Best-epoch summary bar ──────────────────────────────────────────
ax5.set_title("Best Epoch Summary", fontweight="bold")
best_row = df.copy()
map_col = "metrics/mAP50(B)" if "metrics/mAP50(B)" in df.columns else None
if map_col:
    best_idx = df[map_col].idxmax()
    best_row = df.loc[best_idx]
    metrics = {
        "Precision": best_row.get("metrics/precision(B)", 0),
        "Recall":    best_row.get("metrics/recall(B)",    0),
        "mAP50":     best_row.get("metrics/mAP50(B)",     0),
        "mAP50-95":  best_row.get("metrics/mAP50-95(B)",  0),
    }
    colors = [PALETTE["precision"], PALETTE["recall"], PALETTE["map50"], PALETTE["map5095"]]
    bars = ax5.bar(list(metrics.keys()), list(metrics.values()), color=colors, edgecolor="#0f0f1a", linewidth=0.8)
    for bar, val in zip(bars, metrics.values()):
        ax5.text(bar.get_x() + bar.get_width() / 2, val + 0.01,
                 f"{val:.3f}", ha="center", va="bottom", fontsize=9, color="#e0e0f0")
    ax5.set_ylim(0, 1.15)
    ax5.set_ylabel("Score")
    ax5.set_title(f"Best Epoch Summary (Epoch {int(best_row['epoch'])+1})", fontweight="bold")
    ax5.tick_params(axis="x", rotation=15)
else:
    ax5.text(0.5, 0.5, "No mAP data yet", ha="center", va="center",
             transform=ax5.transAxes, color="#8888aa")

# ─── Save ─────────────────────────────────────────────────────────────────────
out_dir  = os.path.dirname(os.path.abspath(csv_path))
out_path = os.path.join(out_dir, "training_metrics.png")
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"[OK] Metrics plot saved: {out_path}")

if args.show:
    matplotlib.use("TkAgg")   # switch to interactive for display
    plt.show()
else:
    plt.close()
    print("     Tip: add --show to also open an interactive window.")
