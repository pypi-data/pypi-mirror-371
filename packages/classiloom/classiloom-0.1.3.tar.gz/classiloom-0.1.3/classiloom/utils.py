from __future__ import annotations
import os, json, time, pathlib, random
import numpy as np
from typing import Any, Dict, Tuple

def seed_everything(seed: int = 13) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
    except Exception:
        pass
    os.environ["PYTHONHASHSEED"] = str(seed)

def ensure_dir(p: str) -> str:
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)
    return p

def timestamped_dir(root: str, stem: str) -> str:
    ensure_dir(root)
    d = os.path.join(root, f"{stem}_{int(time.time())}")
    ensure_dir(d)
    return d

def save_json(p: str, obj: Dict[str, Any]) -> None:
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)