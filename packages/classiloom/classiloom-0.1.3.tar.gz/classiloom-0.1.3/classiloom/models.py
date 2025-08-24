from __future__ import annotations
import tensorflow as tf
from typing import Tuple, Optional

def _optimizer(name: str, lr, weight_decay: float):
    name = name.lower()
    if name == "adamw" or weight_decay > 0:
        try:
            return tf.keras.optimizers.AdamW(learning_rate=lr, weight_decay=weight_decay)
        except Exception:
            return tf.keras.optimizers.Adam(learning_rate=lr)
    return tf.keras.optimizers.Adam(learning_rate=lr)

def _loss(label_smoothing: float):
    return tf.keras.losses.CategoricalCrossentropy(label_smoothing=label_smoothing)

def _maybe_schedule(lr: float, schedule: str, epochs: int):
    if schedule == "cosine":
        return tf.keras.optimizers.schedules.CosineDecayRestarts(initial_learning_rate=lr, first_decay_steps=max(epochs//3, 5))
    return lr

def small_cnn(num_classes: int, img_h: int, img_w: int, lr, drop: float, dense: int,
              label_smoothing: float = 0.0, schedule: str = "constant", epochs: int = 12, weight_decay: float = 0.0,
              optimizer: str = "adam") -> tf.keras.Model:
    L = tf.keras.layers
    inputs = L.Input(shape=(img_h, img_w, 3))
    x = inputs
    x = L.Conv2D(48, 3, padding="same", activation="relu")(x); x = L.BatchNormalization()(x); x = L.MaxPooling2D()(x)
    x = L.Dropout(drop)(x)
    x = L.Conv2D(96, 3, padding="same", activation="relu")(x); x = L.BatchNormalization()(x)
    x = L.Conv2D(96, 3, padding="same", activation="relu")(x); x = L.BatchNormalization()(x); x = L.MaxPooling2D()(x)
    x = L.Dropout(drop)(x)
    x = L.Conv2D(192, 3, padding="same", activation="relu")(x); x = L.BatchNormalization()(x)
    x = L.Conv2D(192, 3, padding="same", activation="relu")(x); x = L.BatchNormalization()(x); x = L.MaxPooling2D()(x)
    x = L.Dropout(drop)(x)
    x = L.Flatten()(x)
    x = L.Dense(dense, activation="relu")(x); x = L.BatchNormalization()(x); x = L.Dropout(0.5)(x)
    outputs = L.Dense(num_classes, activation="softmax")(x)
    m = tf.keras.Model(inputs, outputs)
    lr_or_sched = _maybe_schedule(lr, schedule, epochs)
    m.compile(optimizer=_optimizer(optimizer, lr_or_sched, weight_decay),
              loss=_loss(label_smoothing), metrics=["accuracy"])
    return m

def backbone_model(name: str, num_classes: int, img_h: int, img_w: int, lr, drop: float, dense: int,
                   label_smoothing: float = 0.0, schedule: str = "constant", epochs: int = 12,
                   weight_decay: float = 0.0, optimizer: str = "adam",
                   train_backbone: bool = False) -> Tuple[tf.keras.Model, Optional[tf.keras.Model]]:
    L = tf.keras.layers
    n = name.lower()
    if n == "mobilenetv2":
        base = tf.keras.applications.MobileNetV2(input_shape=(img_h, img_w, 3), include_top=False, weights="imagenet")
        preprocess = tf.keras.applications.mobilenet_v2.preprocess_input
    elif n == "efficientnetb0":
        base = tf.keras.applications.EfficientNetB0(input_shape=(img_h, img_w, 3), include_top=False, weights="imagenet")
        preprocess = tf.keras.applications.efficientnet.preprocess_input
    elif n == "resnet50":
        base = tf.keras.applications.ResNet50(input_shape=(img_h, img_w, 3), include_top=False, weights="imagenet")
        preprocess = tf.keras.applications.resnet.preprocess_input
    else:
        raise ValueError(f"unsupported backbone: {name}")
    base.trainable = bool(train_backbone)

    inputs = L.Input(shape=(img_h, img_w, 3))
    x = preprocess(inputs)
    x = base(x, training=train_backbone)
    x = L.GlobalAveragePooling2D()(x)
    x = L.Dropout(drop)(x)
    x = L.Dense(dense, activation="relu")(x)
    x = L.Dropout(0.25)(x)
    outputs = L.Dense(num_classes, activation="softmax")(x)
    m = tf.keras.Model(inputs, outputs)
    lr_or_sched = _maybe_schedule(lr, schedule, epochs)
    m.compile(optimizer=_optimizer(optimizer, lr_or_sched, weight_decay),
              loss=_loss(label_smoothing), metrics=["accuracy"])
    return m, base