from __future__ import annotations
import os, json
from typing import Any, Dict, List
import google.generativeai as genai

def _configure(api_key: str):
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True

# ==== Hyperparameter suggestion (existing) ====

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
    ok = _configure(api_key)
    if not ok:
        # Fallback: minimal diverse set
        defaults = [
            {"backbone":"small_cnn","img_size":224,"batch":32,"lr":0.001,"drop":0.3,"dense":512,"epochs":12,"aug":True,"train_backbone":False,"optimizer":"adam","label_smoothing":0.05,"weight_decay":0.0,"lr_schedule":"constant","fine_tune_after":0},
            {"backbone":"mobilenetv2","img_size":224,"batch":64,"lr":0.0005,"drop":0.2,"dense":512,"epochs":30,"aug":True,"train_backbone":True,"optimizer":"adamw","label_smoothing":0.05,"weight_decay":1e-4,"lr_schedule":"cosine","fine_tune_after":10},
            {"backbone":"efficientnetb0","img_size":256,"batch":32,"lr":0.001,"drop":0.15,"dense":768,"epochs":20,"aug":True,"train_backbone":False,"optimizer":"adamw","label_smoothing":0.05,"weight_decay":1e-4,"lr_schedule":"cosine","fine_tune_after":0},
            {"backbone":"resnet50","img_size":320,"batch":32,"lr":0.0002,"drop":0.1,"dense":1024,"epochs":40,"aug":True,"train_backbone":False,"optimizer":"adam","label_smoothing":0.1,"weight_decay":0.0,"lr_schedule":"constant","fine_tune_after":0},
        ]
        return defaults[:trials]
    model = genai.GenerativeModel(model_name)
    text = PROMPT.format(trials=trials, summary=json.dumps(summary, ensure_ascii=False))
    out = model.generate_content(text).text.strip()
    if out.startswith("```"):
        out = out.strip("`")
        out = out.split("\n", 1)[1] if "\n" in out else out
        if out.endswith("```"):
            out = out[:-3]
    try:
        data = json.loads(out)
        return data[:trials] if isinstance(data, list) else []
    except Exception:
        return []

# ==== Test split proposal ====

SPLIT_PROMPT = """System Instruction: Absolute Mode. Same constraints as above.

Task: Decide per-class test counts for an image classification dataset. Prefer 10–20% test per class, but adjust for class imbalance and low counts; guarantee at least 1 test image if class has >= 5 images, else 0.

Input:
{summary}

Output JSON ONLY, schema:
{{
  "per_class": [{{"name": "<class>", "test": <int>}}, ...],
  "notes": "<short justification>"
}}
"""

def propose_split(summary: Dict[str, Any], api_key: str, model_name: str) -> Dict[str, Any]:
    ok = _configure(api_key)
    classes = summary.get("classes", [])
    counts = summary.get("counts", {})
    if not ok:
        per = []
        for c in classes:
            n = int(counts.get(c, 0))
            t = 0 if n < 5 else max(1, min(n//5, 1000000))  # ~20%
            per.append({"name": c, "test": int(t)})
        return {"per_class": per, "notes": "fallback 20% per class with min 1 if >=5"}
    model = genai.GenerativeModel(model_name)
    text = SPLIT_PROMPT.format(summary=json.dumps(summary, ensure_ascii=False))
    out = model.generate_content(text).text.strip()
    if out.startswith("```"):
        out = out.strip("`")
        out = out.split("\n", 1)[1] if "\n" in out else out
        if out.endswith("```"):
            out = out[:-3]
    try:
        data = json.loads(out)
    except Exception:
        data = {}
    per = data.get("per_class", []) if isinstance(data, dict) else []
    # validate
    name_to_test = {}
    for item in per:
        try:
            n = int(item.get("test", 0))
        except Exception:
            n = 0
        name_to_test[str(item.get("name", ""))] = max(0, n)
    fixed = []
    for c in classes:
        n = int(counts.get(c, 0))
        t = name_to_test.get(c, 0)
        if n >= 5:
            t = max(1, min(t if t > 0 else n//10, n-1))  # ensure at least 1, at most n-1
        else:
            t = 0
        fixed.append({"name": c, "test": int(t)})
    return {"per_class": fixed, "notes": data.get("notes", "validated")}