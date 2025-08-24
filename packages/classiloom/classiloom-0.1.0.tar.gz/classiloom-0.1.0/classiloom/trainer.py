from __future__ import annotations
import os
from typing import Dict, Any, Tuple, List
import numpy as np
import tensorflow as tf
from .models import small_cnn, backbone_model

def enable_mixed_precision(flag: bool) -> None:
    if flag:
        try:
            from tensorflow.keras import mixed_precision
            mixed_precision.set_global_policy("mixed_float16")
        except Exception:
            pass

def build_datasets(root: str, img_size: int, batch: int, seed: int = 13, val_split: float = 0.2, aug: bool = True):
    L = tf.keras.layers
    train = tf.keras.utils.image_dataset_from_directory(
        root, validation_split=val_split, subset="training", seed=seed,
        image_size=(img_size, img_size), batch_size=batch, label_mode="categorical", shuffle=True)
    val = tf.keras.utils.image_dataset_from_directory(
        root, validation_split=val_split, subset="validation", seed=seed,
        image_size=(img_size, img_size), batch_size=batch, label_mode="categorical", shuffle=False)

    class_names = train.class_names

    norm = L.Rescaling(1.0/255.0)
    aug_layer = tf.keras.Sequential([
        L.RandomFlip("horizontal"),
        L.RandomRotation(0.05),
        L.RandomZoom(0.12),
    ], name="aug") if aug else tf.keras.Sequential(name="no_aug")

    AUTOTUNE = tf.data.AUTOTUNE
    train = train.map(lambda x,y: (aug_layer(norm(x), training=True), y), num_parallel_calls=AUTOTUNE)\
                 .cache()\
                 .prefetch(AUTOTUNE)
    val   = val.map(lambda x,y: (norm(x), y), num_parallel_calls=AUTOTUNE)\
               .cache()\
               .prefetch(AUTOTUNE)
    return train, val, class_names

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

def train_and_eval(dataset_dir: str, cfg: Dict[str, Any], counts: Dict[str, int], out_dir: str,
                   mixed_precision: bool = False, fine_tune: bool = False):
    enable_mixed_precision(mixed_precision)
    train, val, class_names = build_datasets(dataset_dir, cfg["img_size"], cfg["batch"], aug=cfg["aug"])
    num_classes = len(class_names)

    model, base = build_model_from_cfg(cfg, num_classes)
    cw = class_weights_from_counts(class_names, counts)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=0),
        tf.keras.callbacks.ModelCheckpoint(os.path.join(out_dir, "model.best.keras"), monitor="val_accuracy", save_best_only=True),
        tf.keras.callbacks.CSVLogger(os.path.join(out_dir, "train.csv"))
    ]

    hist = model.fit(train, validation_data=val, epochs=int(cfg["epochs"]), verbose=0, callbacks=callbacks, class_weight=cw)
    # Load best
    try:
        model = tf.keras.models.load_model(os.path.join(out_dir, "model.best.keras"))
    except Exception:
        pass

    # Optional fine-tune: unfreeze backbone after N epochs and continue a few epochs
    if fine_tune and base is not None and cfg.get("fine_tune_after", 0) > 0:
        for layer in base.layers[-80:]:
            layer.trainable = True
        try:
            model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=max(cfg["lr"]*0.1, 1e-5)),
                          loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=cfg["label_smoothing"]),
                          metrics=["accuracy"])
        except Exception:
            pass
        ft_cb = [
            tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint(os.path.join(out_dir, "model.ft.best.keras"), monitor="val_accuracy", save_best_only=True),
        ]
        model.fit(train, validation_data=val, epochs=min(10, max(2, int(cfg["epochs"]*0.3))), verbose=0, callbacks=ft_cb, class_weight=cw)
        try:
            model = tf.keras.models.load_model(os.path.join(out_dir, "model.ft.best.keras"))
        except Exception:
            pass

    # Validation predictions
    y_true, y_pred = [], []
    for x, y in val:
        p = model.predict(x, verbose=0)
        y_pred.extend(np.argmax(p, axis=1).tolist())
        y_true.extend(np.argmax(y.numpy(), axis=1).tolist())

    return model, hist.history, class_names, y_true, y_pred