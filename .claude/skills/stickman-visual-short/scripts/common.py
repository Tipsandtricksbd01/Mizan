"""Shared helpers for the stickman-visual-short pipeline (free, open-source only)."""
import json
import os
import subprocess
from pathlib import Path


def load_plan(path):
    plan = json.loads(Path(path).read_text(encoding="utf-8"))
    chars = plan.get("characters", {})
    for shot in plan["shots"]:
        for key in ("image_prompt", "motion_prompt"):
            if key in shot:
                shot[key] = shot[key].format(**chars)
    return plan


def work_dir(plan_path):
    d = Path(plan_path).resolve().parent / "build"
    for sub in ("images", "clips", "audio"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def pick_dtype(name):
    import torch
    if name == "auto":
        if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
            return torch.bfloat16
        return torch.float16
    return {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[name]


def place_on_gpu(pipe, offload):
    """offload: none | model | sequential  (sequential = lowest VRAM, slowest)."""
    if offload == "model":
        pipe.enable_model_cpu_offload()
    elif offload == "sequential":
        pipe.enable_sequential_cpu_offload()
    else:
        pipe.to("cuda")
    return pipe


def run(cmd, cwd=None):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, cwd=cwd)


def hf_login_hint():
    if not (os.environ.get("HF_TOKEN") or Path.home().joinpath(".cache/huggingface/token").exists()):
        print("Note: gated models (e.g. stable-audio-open-1.0) need a FREE Hugging Face token: "
              "huggingface-cli login")
