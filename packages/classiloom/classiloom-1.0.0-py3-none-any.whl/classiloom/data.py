from __future__ import annotations
import os, random
from typing import Dict, List, Tuple

ALLOWED_IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

def scan_image_folders(root: str) -> Tuple[List[str], Dict[str, List[str]]]:
    classes: List[str] = []
    files: Dict[str, List[str]] = {}
    for dirpath, _, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            continue
        cls = os.path.basename(dirpath)
        bucket = []
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in ALLOWED_IMG_EXTS:
                bucket.append(os.path.join(dirpath, fn))
        if bucket:
            classes.append(cls)
            files[cls] = sorted(bucket)
    classes = sorted(set(classes))
    return classes, files

def quick_metadata(files_by_class: Dict[str, List[str]]) -> Dict:
    counts = {k: len(v) for k, v in files_by_class.items()}
    classes = sorted(files_by_class.keys())
    total = sum(counts.values())
    return {
        "classes": classes,
        "counts": counts,
        "class_count": len(classes),
        "total_images": total,
    }

def realize_split(files_by_class: Dict[str, List[str]], per_class_counts: Dict[str, int], seed: int = 13) -> Dict[str, List[str]]:
    rng = random.Random(seed)
    split = {"test": {}, "trainval": {}}
    for cls, paths in files_by_class.items():
        k = max(0, min(len(paths), int(per_class_counts.get(cls, 0))))
        idx = list(range(len(paths)))
        rng.shuffle(idx)
        test_idx = set(idx[:k])
        test_paths = [paths[i] for i in sorted(test_idx)]
        trainval_paths = [paths[i] for i in range(len(paths)) if i not in test_idx]
        split["test"][cls] = test_paths
        split["trainval"][cls] = trainval_paths
    return split