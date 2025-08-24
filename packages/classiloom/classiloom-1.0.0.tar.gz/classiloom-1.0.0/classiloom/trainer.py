from __future__ import annotations
import os, math
from typing import Dict, Any, List, Tuple
import numpy as np
import tensorflow as tf
from .models import small_cnn, backbone_model
from .data import scan_image_folders

def enable_mixed_precision(flag: bool) -> None:
    if flag:
        try:
            from tensorflow.keras import mixed_precision
            mixed_precision.set_global_policy("mixed_float16")
        except Exception:
            pass

def _build_from_file_list(file_label: List[Tuple[str, int]], img_size: int, batch: int, shuffle: bool, augment: bool):
    L = tf.keras.layers
    paths = [p for p, _ in file_label]
    labels = [y for _, y in file_label]
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=max(2048, len(paths)))
    def _load(path, y):
        img = tf.io.read_file(path)
        img = tf.image.decode_image(img, channels=3, expand_animations=False)
        img = tf.image.resize(img, [img_size, img_size], method="bilinear")
        img = tf.cast(img, tf.float32) / 255.0
        return img, tf.one_hot(y, depth=99999)  # placeholder depth; fix below
    ds = ds.map(_load, num_parallel_calls=tf.data.AUTOTUNE)
    return ds

def _one_hot_depth_fix(ds: tf.data.Dataset, num_classes: int):
    def fix(x, y):  # y has "too large" one-hot; remap
        y = tf.argmax(y, axis=-1)
        y = tf.one_hot(y, depth=num_classes)
        return x, y
    return ds.map(fix, num_parallel_calls=tf.data.AUTOTUNE)

def build_datasets_with_optional_split(root: str,
                                       img_size: int,
                                       batch: int,
                                       seed: int,
                                       val_split: float,
                                       aug: bool,
                                       split_json: Dict[str, Any] | None = None):
    classes, files_by_class = scan_image_folders(root)
    if len(classes) < 2:
        raise ValueError("need >=2 classes")
    class_to_idx = {c: i for i, c in enumerate(classes)}

    # remove test files if split_json provided
    test_set = set()
    if split_json:
        for c, arr in split_json.get("test", {}).items():
            for p in arr:
                test_set.add(os.path.abspath(p))

    # compose train/val pool
    pool: List[Tuple[str, int]] = []
    for c, paths in files_by_class.items():
        for p in paths:
            if os.path.abspath(p) not in test_set:
                pool.append((p, class_to_idx[c]))

    # deterministic split
    rng = np.random.RandomState(seed)
    idx = np.arange(len(pool))
    rng.shuffle(idx)
    n_val = int(math.floor(len(idx) * val_split))
    val_idx = set(idx[:n_val].tolist())
    train_list = [pool[i] for i in range(len(pool)) if i not in val_idx]
    val_list   = [pool[i] for i in range(len(pool)) if i in val_idx]

    # build datasets
    train = _build_from_file_list(train_list, img_size, batch, shuffle=True, augment=aug)
    val   = _build_from_file_list(val_list,   img_size, batch, shuffle=False, augment=False)

    # fix one-hot depth now that we know num_classes
    K = len(classes)
    train = _one_hot_depth_fix(train, K)
    val   = _one_hot_depth_fix(val,   K)

    # augment and prefetch
    L = tf.keras.layers
    norm = L.Rescaling(1.0/255.0)  # already normalized, keep identity
    aug_layer = tf.keras.Sequential([
        L.RandomFlip("horizontal"),
        L.RandomRotation(0.05),
        L.RandomZoom(0.12),
    ]) if aug else tf.keras.Sequential()
    AUTOTUNE = tf.data.AUTOTUNE
    train = train.map(lambda x,y: (aug_layer(x, training=True), y), num_parallel_calls=AUTOTUNE)\
                 .batch(batch).prefetch(AUTOTUNE)
    val   = val.batch(batch).prefetch(AUTOTUNE)

    # counts (for class weighting)
    counts = {c: len(files_by_class[c]) for c in classes}
    return train, val, classes, counts, test_set

def class_weights_from_counts(class_names: List[str], counts: Dict[str, int]) -> Dict[int, float]:
    total = sum(counts.get(c, 0) for c in class_names)
    weights = {}
    for i, c in enumerate(class_names):
        n = max(1, counts.get(c, 0))
        weights[i] = total / (len(class_names) * n)
    return weights

def build_model_from_cfg(cfg: Dict[str, Any], num_classes: int):
    if cfg["backbone"] == "small_cnn":
        m = small_cnn(
            num_classes, cfg["img_size"], cfg["img_size"],
            lr=cfg["lr"], drop=cfg["drop"], dense=cfg["dense"],
            label_smoothing=cfg["label_smoothing"], schedule=cfg["lr_schedule"],
            epochs=cfg["epochs"], weight_decay=cfg["weight_decay"], optimizer=cfg["optimizer"]
        )
        return m, None
    m, base = backbone_model(
        cfg["backbone"], num_classes, cfg["img_size"], cfg["img_size"],
        lr=cfg["lr"], drop=cfg["drop"], dense=cfg["dense"],
        label_smoothing=cfg["label_smoothing"], schedule=cfg["lr_schedule"],
        epochs=cfg["epochs"], weight_decay=cfg["weight_decay"], optimizer=cfg["optimizer"],
        train_backbone=bool(cfg["train_backbone"])
    )
    return m, base

def train_and_eval(dataset_dir: str, cfg: Dict[str, Any], counts_hint: Dict[str, int], out_dir: str,
                   mixed_precision: bool = False, fine_tune: bool = False, verbose: int = 1,
                   split_json: Dict[str, Any] | None = None):
    tf.get_logger().setLevel("INFO" if verbose else "WARNING")
    enable_mixed_precision(mixed_precision)

    train, val, class_names, counts_all, _ = build_datasets_with_optional_split(
        dataset_dir, cfg["img_size"], cfg["batch"], seed=13, val_split=0.2, aug=cfg["aug"], split_json=split_json
    )

    num_classes = len(class_names)
    model, base = build_model_from_cfg(cfg, num_classes)
    cw = class_weights_from_counts(class_names, counts_all)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True, verbose=verbose),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=verbose),
        tf.keras.callbacks.ModelCheckpoint(os.path.join(out_dir, "model.best.keras"), monitor="val_accuracy", save_best_only=True, verbose=verbose),
        tf.keras.callbacks.CSVLogger(os.path.join(out_dir, "train.csv"))
    ]

    hist = model.fit(train, validation_data=val, epochs=int(cfg["epochs"]), verbose=verbose, callbacks=callbacks, class_weight=cw)

    try:
        model = tf.keras.models.load_model(os.path.join(out_dir, "model.best.keras"))
    except Exception:
        pass

    # Eval on val set to produce y_true/y_pred
    y_true, y_pred = [], []
    for x, y in val:
        p = model.predict(x, verbose=0)
        y_pred.extend(np.argmax(p, axis=1).tolist())
        y_true.extend(np.argmax(y.numpy(), axis=1).tolist())

    return model, hist.history, class_names, y_true, y_pred