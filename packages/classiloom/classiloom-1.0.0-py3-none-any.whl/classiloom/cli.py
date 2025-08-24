from __future__ import annotations
import os, json, typer, importlib.metadata
from rich import print as rprint

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")

from .config import load_env, set_key
from .data import scan_image_folders, quick_metadata, realize_split
from .gemini import suggest, propose_split
from .trainer import train_and_eval
from .metrics import evaluate_and_report, plot_curves
from .utils import timestamped_dir, save_json, seed_everything

app = typer.Typer(add_completion=False, no_args_is_help=True)

@app.command("set")
def set_cmd(key: str, value: str):
    key_map = {"gemini_api": "GEMINI_API_KEY", "gemini_model": "GEMINI_MODEL"}
    if key not in key_map:
        raise typer.Exit(code=2)
    set_key(key_map[key], value)
    rprint({key: "set"})

@app.command("version")
def version_cmd():
    v = importlib.metadata.version("classiloom")
    rprint({"classiloom_version": v})

@app.command("scan")
def scan(dataset_dir: str, out: str = "runs", seed: int = 13):
    seed_everything(seed)
    classes, files_by_class = scan_image_folders(dataset_dir)
    if len(classes) < 2:
        raise typer.Exit(code=2)
    meta = quick_metadata(files_by_class)
    d = timestamped_dir(out, "scan")
    save_json(os.path.join(d, "scan.json"), {"summary": meta, "counts": {k: len(v) for k, v in files_by_class.items()}})
    rprint({"scan_dir": d, "class_count": len(classes), "total_images": meta["total_images"]})

@app.command("suggest")
def suggest_cmd(scan_json: str, trials: int = 8, out: str = "runs"):
    env = load_env()
    with open(scan_json, "r", encoding="utf-8") as f:
        payload = json.load(f)
    summary = payload["summary"]
    cfgs = suggest(summary, trials=trials, api_key=env.get("GEMINI_API_KEY",""), model_name=env.get("GEMINI_MODEL","gemini-2.0-flash"))
    d = timestamped_dir(out, "suggest")
    save_json(os.path.join(d, "configs.json"), {"configs": cfgs, "summary": summary, "counts": payload.get("counts", {})})
    rprint({"suggest_dir": d, "trials": len(cfgs)})

@app.command("split")
def split_cmd(dataset_dir: str, scan_json: str, out: str = "runs", seed: int = 13):
    """
    Decide per-class test counts via Gemini and materialize a test split (list of file paths).
    Training/validation will exclude these test files.
    """
    seed_everything(seed)
    env = load_env()
    with open(scan_json, "r", encoding="utf-8") as f:
        payload = json.load(f)
    summary = payload["summary"]
    proposal = propose_split(summary, api_key=env.get("GEMINI_API_KEY",""), model_name=env.get("GEMINI_MODEL","gemini-2.0-flash"))
    per = proposal.get("per_class", [])
    want = {it["name"]: int(it["test"]) for it in per}
    classes, files_by_class = scan_image_folders(dataset_dir)
    split = realize_split(files_by_class, want, seed=seed)
    d = timestamped_dir(out, "split")
    data = {"proposal": proposal, "split": split}
    save_json(os.path.join(d, "split.json"), data)
    rprint({"split_dir": d, "notes": proposal.get("notes", ""), "per_class": proposal.get("per_class", [])})

@app.command("train")
def train(
    dataset_dir: str,
    configs_json: str,
    idx: int = 0,
    out: str = "runs",
    seed: int = 13,
    split_json: str = typer.Option("", help="Optional split file produced by `classiloom split`"),
    mixed_precision: bool = typer.Option(False, help="Enable mixed-float16 if supported"),
    fine_tune: bool = typer.Option(False, help="Unfreeze backbone for a short second stage"),
    log_verbose: bool = typer.Option(True, help="Per-epoch logs"),
):
    seed_everything(seed)
    with open(configs_json, "r", encoding="utf-8") as f:
        payload = json.load(f)
    cfg = payload["configs"][idx]
    counts = payload.get("counts", {})

    suggested = int(cfg.get("epochs", 12))
    try:
        new_epochs = typer.prompt(f"Epochs (AI suggested {suggested})", default=suggested, type=int)
    except typer.Abort:
        new_epochs = suggested
    cfg["epochs"] = int(new_epochs)

    split_payload = None
    if split_json:
        with open(split_json, "r", encoding="utf-8") as f:
            sj = json.load(f)
        split_payload = sj.get("split", None)

    run_dir = timestamped_dir(out, "train")
    rprint({
        "run_dir": run_dir,
        "backbone": cfg["backbone"],
        "img_size": cfg["img_size"],
        "batch": cfg["batch"],
        "epochs": cfg["epochs"],
        "using_split": bool(split_payload is not None),
    })

    model, history, class_names, y_true, y_pred = train_and_eval(
        dataset_dir,
        cfg,
        counts,
        out_dir=run_dir,
        mixed_precision=mixed_precision,
        fine_tune=fine_tune,
        verbose=1 if log_verbose else 0,
        split_json=split_payload,
    )

    model_path = os.path.join(run_dir, "model.keras")
    labels_path = os.path.join(run_dir, "labels.json")
    model.save(model_path)
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump({"class_names": class_names}, f, ensure_ascii=False, indent=2)

    metrics = evaluate_and_report(y_true, y_pred, class_names, run_dir)
    curves_path = plot_curves(history, run_dir)
    top_confusions = [m for m in metrics["a_to_b_mapping"] if m["true"] != m["pred"]][:25]

    result = {
        "run_dir": run_dir,
        "val_accuracy": metrics["accuracy"],
        "model_path": model_path,
        "labels_path": labels_path,
        "config": cfg,
        "curves_png": curves_path,
        "confusion_matrix_png": metrics["confusion_matrix_png"],
        "top_confusions": top_confusions,
        "classes": class_names,
    }
    save_json(os.path.join(run_dir, "result.json"), result)
    rprint({"val_accuracy": metrics["accuracy"], "model": model_path})

@app.command("predict")
def predict(image_path: str, model_dir: str):
    import numpy as np
    import tensorflow as tf
    from PIL import Image
    with open(os.path.join(model_dir, "labels.json"), "r", encoding="utf-8") as f:
        class_names = json.load(f)["class_names"]
    model = tf.keras.models.load_model(os.path.join(model_dir, "model.keras"), compile=False)
    try:
        in_shape = model.inputs[0].shape
        H, W = int(in_shape[1]), int(in_shape[2])
    except Exception:
        H = W = 224
    im = Image.open(image_path).convert("RGB").resize((W, H))
    arr = (np.asarray(im, dtype=np.float32) / 255.0)[None, ...]
    preds = model.predict(arr, verbose=0)[0]
    idx = int(np.argmax(preds))
    rprint({"class_index": idx, "class_name": class_names[idx] if 0 <= idx < len(class_names) else None, "confidence": float(np.max(preds))})

if __name__ == "__main__":
    app()