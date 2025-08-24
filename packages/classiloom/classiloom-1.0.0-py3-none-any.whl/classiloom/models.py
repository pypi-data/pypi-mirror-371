from __future__ import annotations
import tensorflow as tf
from typing import Tuple, Optional

# ---- optim, loss, schedules ----

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
    schedule = (schedule or "constant").lower()
    if schedule == "cosine":
        return tf.keras.optimizers.schedules.CosineDecayRestarts(
            initial_learning_rate=lr,
            first_decay_steps=max(epochs // 3, 5)
        )
    return lr

# ---- blocks: Squeeze-and-Excitation + Depthwise Separable with residual ----

def _se_block(x, ratio: int = 8, name: str | None = None):
    L = tf.keras.layers
    in_channels = x.shape[-1]
    se = L.GlobalAveragePooling2D(name=None if name is None else name + "_gap")(x)
    se = L.Dense(max(in_channels // ratio, 8), activation="relu", name=None if name is None else name + "_fc1")(se)
    se = L.Dense(in_channels, activation="sigmoid", name=None if name is None else name + "_fc2")(se)
    se = L.Reshape((1, 1, in_channels))(se)
    return L.Multiply(name=None if name is None else name + "_scale")([x, se])

def _ds_res_block(x, out_ch: int, stride: int = 1, drop_rate: float = 0.0, name: str | None = None):
    """
    Depthwise-separable conv block with BN, Swish, SE, and residual proj when shape changes.
    """
    L = tf.keras.layers
    shortcut = x

    y = L.DepthwiseConv2D(3, strides=stride, padding="same", use_bias=False, name=None if name is None else name + "_dw")(x)
    y = L.BatchNormalization(name=None if name is None else name + "_bn1")(y)
    y = L.Activation("swish")(y)

    y = L.Conv2D(out_ch, 1, padding="same", use_bias=False, name=None if name is None else name + "_pw")(y)
    y = L.BatchNormalization(name=None if name is None else name + "_bn2")(y)

    y = _se_block(y, ratio=12, name=None if name is None else name + "_se")
    if drop_rate and drop_rate > 0:
        y = L.Dropout(drop_rate, name=None if name is None else name + "_drop")(y)

    # project shortcut if channels/stride differ
    if shortcut.shape[-1] != out_ch or stride != 1:
        shortcut = L.Conv2D(out_ch, 1, strides=stride, padding="same", use_bias=False, name=None if name is None else name + "_proj")(shortcut)
        shortcut = L.BatchNormalization(name=None if name is None else name + "_proj_bn")(shortcut)

    out = L.Add(name=None if name is None else name + "_add")([shortcut, y])
    out = L.Activation("swish", name=None if name is None else name + "_act")(out)
    return out

# ---- stronger default CNN (replaces the previous "small_cnn") ----
# Architecture: stem → DS-Res stages (like MobileNet/MBConv with SE) → head.
# Depth scalable via widths list.

def small_cnn(num_classes: int,
              img_h: int,
              img_w: int,
              lr,
              drop: float,
              dense: int,
              label_smoothing: float = 0.0,
              schedule: str = "constant",
              epochs: int = 12,
              weight_decay: float = 0.0,
              optimizer: str = "adam") -> tf.keras.Model:
    """
    Improved small_cnn:
    - Depthwise-separable residual blocks with SE.
    - Progressive downsampling.
    - Swish activations, strong regularization.
    - Outperforms the previous plain CNN on typical small/medium datasets.
    """
    L = tf.keras.layers
    inputs = L.Input(shape=(img_h, img_w, 3))

    # Stem
    x = L.Conv2D(48, 3, strides=2, padding="same", use_bias=False, name="stem_conv")(inputs)
    x = L.BatchNormalization(name="stem_bn")(x)
    x = L.Activation("swish", name="stem_act")(x)

    # Stages: (channels, blocks, stride)
    # Choose moderate width for stability on CPU/GPU/Colab
    stages = [
        (64,  2, 1),
        (96,  2, 2),
        (160, 3, 2),
        (224, 3, 2),
    ]

    for si, (ch, n, stride) in enumerate(stages):
        # first block may downsample
        x = _ds_res_block(x, ch, stride=stride, drop_rate=drop * 0.5, name=f"s{si}_b0")
        for bi in range(1, n):
            x = _ds_res_block(x, ch, stride=1, drop_rate=drop * 0.5, name=f"s{si}_b{bi}")

    # Head
    x = L.Conv2D(max(dense, 128), 1, padding="same", use_bias=False, name="head_conv")(x)
    x = L.BatchNormalization(name="head_bn")(x)
    x = L.Activation("swish", name="head_act")(x)
    x = L.GlobalAveragePooling2D(name="gap")(x)
    x = L.Dropout(0.25 + 0.25 * min(1.0, drop / 0.6), name="head_drop")(x)
    x = L.Dense(dense, activation="swish", name="head_fc")(x)
    x = L.Dropout(0.25, name="head_fc_drop")(x)
    outputs = L.Dense(num_classes, activation="softmax", name="pred")(x)

    m = tf.keras.Model(inputs, outputs, name="dsres_se_cnn")
    lr_or_sched = _maybe_schedule(lr, schedule, epochs)
    m.compile(
        optimizer=_optimizer(optimizer, lr_or_sched, weight_decay),
        loss=_loss(label_smoothing),
        metrics=["accuracy"]
    )
    return m

# ---- pretrained backbones ----

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
    x = L.Dense(dense, activation="swish")(x)
    x = L.Dropout(0.25)(x)
    outputs = L.Dense(num_classes, activation="softmax")(x)

    m = tf.keras.Model(inputs, outputs, name=f"{n}_head")
    lr_or_sched = _maybe_schedule(lr, schedule, epochs)
    m.compile(
        optimizer=_optimizer(optimizer, lr_or_sched, weight_decay),
        loss=_loss(label_smoothing),
        metrics=["accuracy"]
    )
    return m, base