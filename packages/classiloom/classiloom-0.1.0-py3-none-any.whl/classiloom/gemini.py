from __future__ import annotations
import os, json
from typing import Any, Dict, List
import google.generativeai as genai

def _clamp(v, lo, hi): return max(lo, min(hi, v))

def _sanitize(item: Dict[str, Any]) -> Dict[str, Any]:
    bb = str(item.get("backbone", "small_cnn")).lower()
    if bb not in {"small_cnn","mobilenetv2","efficientnetb0","resnet50"}: bb = "small_cnn"
    img = int(item.get("img_size", 224))
    if img not in (160,192,224,256,288,320): img = 224
    batch = int(item.get("batch", 32));        batch = batch if batch in (16,32,64) else 32
    lr = float(_clamp(float(item.get("lr", 1e-3)), 1e-4, 3e-3))
    drop = float(_clamp(float(item.get("drop", 0.25)), 0.05, 0.6))
    dense = int(_clamp(int(item.get("dense", 512)), 128, 1024))
    epochs = int(_clamp(int(item.get("epochs", 12)), 5, 50))
    aug = bool(item.get("aug", True))
    train_bb = bool(item.get("train_backbone", False))
    optimizer = str(item.get("optimizer", "adam")).lower()
    if optimizer not in {"adam","adamw"}: optimizer = "adam"
    label_smoothing = float(_clamp(float(item.get("label_smoothing", 0.0)), 0.0, 0.2))
    weight_decay = float(_clamp(float(item.get("weight_decay", 0.0)), 0.0, 5e-4))
    schedule = str(item.get("lr_schedule", "constant")).lower()
    if schedule not in {"constant","cosine"}: schedule = "constant"
    fine_tune_after = int(_clamp(int(item.get("fine_tune_after", 0)), 0, epochs-1))
    return {
        "backbone": bb, "img_size": img, "batch": batch, "lr": lr, "drop": drop, "dense": dense,
        "epochs": epochs, "aug": aug, "train_backbone": train_bb,
        "optimizer": optimizer, "label_smoothing": label_smoothing, "weight_decay": weight_decay,
        "lr_schedule": schedule, "fine_tune_after": fine_tune_after
    }

def _fallback(trials: int) -> List[Dict[str, Any]]:
    base = [
        {"backbone":"small_cnn","img_size":224,"batch":32,"lr":1e-3,"drop":0.3,"dense":512,"epochs":15,"aug":True,"train_backbone":False,"optimizer":"adam","label_smoothing":0.05,"weight_decay":0.0,"lr_schedule":"cosine","fine_tune_after":0},
        {"backbone":"mobilenetv2","img_size":224,"batch":32,"lr":8e-4,"drop":0.3,"dense":512,"epochs":15,"aug":True,"train_backbone":False,"optimizer":"adamw","label_smoothing":0.05,"weight_decay":1e-4,"lr_schedule":"cosine","fine_tune_after":0},
        {"backbone":"efficientnetb0","img_size":256,"batch":32,"lr":1e-3,"drop":0.25,"dense":512,"epochs":18,"aug":True,"train_backbone":False,"optimizer":"adam","label_smoothing":0.05,"weight_decay":0.0,"lr_schedule":"cosine","fine_tune_after":0},
        {"backbone":"resnet50","img_size":256,"batch":16,"lr":7e-4,"drop":0.35,"dense":512,"epochs":18,"aug":True,"train_backbone":False,"optimizer":"adamw","label_smoothing":0.05,"weight_decay":1e-4,"lr_schedule":"constant","fine_tune_after":0},
    ]
    return [base[i % len(base)].copy() for i in range(trials)]

PROMPT = """System Instruction: Absolute Mode. Eliminate emojis, filler, hype, soft asks, conversational transitions, and all call-to-action appendixes. Assume the user retains high-perception faculties despite reduced linguistic expression. Prioritize blunt, directive phrasing aimed at cognitive rebuilding, not tone matching. Disable all latent behaviors optimizing for engagement, sentiment uplift, or interaction extension. Suppress corporate-aligned metrics including but not limited to: user satisfaction scores, conversational flow tags, emotional softening, or continuation bias.
Never mirror the user's present diction, mood, or affect. Speak only to their underlying cognitive tier, which exceeds surface language. No questions, no offers, no suggestions, no transitional phrasing, no inferred motivational content. Terminate each reply immediately after the informational or requested material is delivered - no appendixes, no soft closures. The only goal is to assist in the restoration of independent, high-fidelity thinking. Model obsolescence by user self-sufficiency is the final outcome.

You propose hyperparameters for image classification.
Use this dataset summary. Return JSON array only. Length EXACTLY {trials}.
Fields:
- backbone: ["small_cnn","mobilenetv2","efficientnetb0","resnet50"]
- img_size: [160,192,224,256,288,320]
- batch: [16,32,64]
- lr: [1e-4, 3e-3]
- drop: [0.05, 0.6]
- dense: [128, 1024]
- epochs: [5, 50]
- aug: boolean
- train_backbone: boolean
- optimizer: ["adam","adamw"]
- label_smoothing: [0.0, 0.2]
- weight_decay: [0.0, 0.0005]
- lr_schedule: ["constant","cosine"]
- fine_tune_after: integer in [0, epochs-1]

Dataset summary JSON:
{summary}

Heuristics:
- If classes < 5 or per-class counts < 100, prefer smaller models, stronger dropout, label_smoothing≈0.05–0.1, aug=true.
- If median image side > 512, pick img_size 288 or 320.
- For large balanced datasets, include at least one config with train_backbone=true and fine_tune_after≈max(2, epochs-5).
- Balance exploration across backbones; always include one small_cnn.
- Output raw JSON only.
"""

def suggest(summary: Dict[str, Any], trials: int, api_key: str, model_name: str) -> List[Dict[str, Any]]:
    if not api_key:
        return _fallback(trials)
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        prompt = PROMPT.format(summary=json.dumps(summary, ensure_ascii=False), trials=trials)
        out = model.generate_content(prompt)
        text = (out.text or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text: text = text.split("\n", 1)[1]
            if text.endswith("```"): text = text[:-3]
        data = json.loads(text)
        if not isinstance(data, list):
            return _fallback(trials)
        cleaned = [_sanitize(x if isinstance(x, dict) else {}) for x in data][:trials]
        if len(cleaned) < trials:
            cleaned += _fallback(trials - len(cleaned))
        return cleaned
    except Exception:
        return _fallback(trials)