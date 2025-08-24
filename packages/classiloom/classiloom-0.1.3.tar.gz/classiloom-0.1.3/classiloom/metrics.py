from __future__ import annotations
import os, json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from sklearn.metrics import confusion_matrix, classification_report

def evaluate_and_report(y_true: np.ndarray, y_pred: np.ndarray, class_names: List[str], out_dir: str) -> Dict:
    os.makedirs(out_dir, exist_ok=True)
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)

    # A→B mapping: flatten confusions
    mapping = []
    for i, tn in enumerate(class_names):
        for j, pn in enumerate(class_names):
            c = int(cm[i, j])
            if c > 0:
                mapping.append({"true": tn, "pred": pn, "count": c})
    mapping = sorted(mapping, key=lambda x: (-x["count"], x["true"], x["pred"]))

    # Confusion matrix figure
    fig = plt.figure(figsize=(max(6, 0.4*len(class_names)), max(5, 0.35*len(class_names))))
    ax = fig.add_subplot(111)
    im = ax.imshow(cm, interpolation="nearest")
    ax.set_title("Confusion Matrix")
    ax.set_xticks(range(len(class_names))); ax.set_xticklabels(class_names, rotation=90)
    ax.set_yticks(range(len(class_names))); ax.set_yticklabels(class_names)
    fig.colorbar(im, ax=ax)
    plt.tight_layout()
    fig_path = os.path.join(out_dir, "confusion_matrix.png")
    fig.savefig(fig_path, dpi=160)
    plt.close(fig)

    # JSON
    out = {
        "accuracy": float(np.trace(cm) / max(1, cm.sum())),
        "per_class": report,
        "confusion_matrix": cm.tolist(),
        "a_to_b_mapping": mapping[:2000],  # cap for size
        "classes": class_names,
        "confusion_matrix_png": fig_path,
    }
    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out

def plot_curves(history: Dict[str, List[float]], out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    fig = plt.figure(figsize=(7,4))
    ax = fig.add_subplot(111)
    if "accuracy" in history:
        ax.plot(history["accuracy"], label="train_acc")
    if "val_accuracy" in history:
        ax.plot(history["val_accuracy"], label="val_acc")
    if "loss" in history:
        ax.plot(history["loss"], label="train_loss")
    if "val_loss" in history:
        ax.plot(history["val_loss"], label="val_loss")
    ax.legend(); ax.set_title("Training Curves"); ax.set_xlabel("epoch"); ax.set_ylabel("value")
    p = os.path.join(out_dir, "curves.png")
    fig.savefig(p, dpi=160); plt.close(fig)
    return p