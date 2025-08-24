from __future__ import annotations
import os, pathlib
from dotenv import dotenv_values

CFG_DIR = pathlib.Path.home() / ".classiloom"
ENV_FILE = CFG_DIR / ".env"

def ensure_cfg_dir() -> None:
    CFG_DIR.mkdir(parents=True, exist_ok=True)

def set_key(key: str, value: str) -> None:
    ensure_cfg_dir()
    # simple .env append/update without a third-party writer
    lines = []
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    out = []
    found = False
    for ln in lines:
        if not ln or ln.strip().startswith("#") or "=" not in ln:
            out.append(ln); continue
        k, v = ln.split("=", 1)
        if k.strip() == key:
            out.append(f"{key}={value}")
            found = True
        else:
            out.append(ln)
    if not found:
        out.append(f"{key}={value}")
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + ("\n" if out and out[-1] != "" else ""))

def load_env() -> dict:
    ensure_cfg_dir()
    env = {}
    if ENV_FILE.exists():
        env.update(dotenv_values(dotenv_path=str(ENV_FILE)))
    # OS env overrides file
    env["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", env.get("GEMINI_API_KEY", ""))
    env["GEMINI_MODEL"] = os.getenv("GEMINI_MODEL", env.get("GEMINI_MODEL", "gemini-2.0-flash"))
    return env