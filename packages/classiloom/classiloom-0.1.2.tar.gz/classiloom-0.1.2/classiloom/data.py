from __future__ import annotations
import os, random
from typing import Dict, List, Tuple
from PIL import Image, UnidentifiedImageError

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

def scan_image_folders(root: str) -> Tuple[List[str], Dict[str, List[str]]]:
    classes: List[str] = []
    files_by_class: Dict[str, List[str]] = {}
    for dirpath, _, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            continue
        cls = os.path.basename(dirpath)
        kept: List[str] = []
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in IMG_EXTS:
                continue
            p = os.path.join(dirpath, fn)
            try:
                with Image.open(p) as im:
                    im.verify()
            except (UnidentifiedImageError, OSError, ValueError):
                continue
            kept.append(p)
        if kept:
            classes.append(cls)
            files_by_class[cls] = kept
    classes = sorted(set(classes))
    return classes, files_by_class

def quick_metadata(files_by_class: Dict[str, List[str]], max_per_class: int = 24) -> Dict:
    import numpy as np
    from PIL import Image
    meta = {"classes": [], "counts": {}, "sizes_sample": [], "modes": []}
    for cls, files in files_by_class.items():
        meta["classes"].append(cls)
        meta["counts"][cls] = len(files)
        sample = random.sample(files, k=min(len(files), max_per_class))
        for p in sample:
            try:
                with Image.open(p) as im:
                    w, h = im.size
                    meta["sizes_sample"].append({"w": w, "h": h})
                    meta["modes"].append(im.mode)
            except Exception:
                continue
    if meta["sizes_sample"]:
        ws = [s["w"] for s in meta["sizes_sample"]]
        hs = [s["h"] for s in meta["sizes_sample"]]
        meta["median_w"] = int(np.median(ws)); meta["median_h"] = int(np.median(hs))
    else:
        meta["median_w"] = meta["median_h"] = 224
    meta["class_count"] = len(meta["classes"])
    meta["total_images"] = sum(meta["counts"].values()) if meta["counts"] else 0
    return meta