"""Step 2 - animate each keyframe (image -> video) with free models via diffusers.

  python make_video.py plan.json                    # Wan2.2-TI2V-5B (Apache-2.0), 704x1280, 24 fps
  python make_video.py plan.json --model wan14b     # Wan2.2-I2V-A14B, best quality, needs a big GPU
  python make_video.py plan.json --model ltx        # LTX-Video 2B, fastest, fits free T4 GPUs
  python make_video.py plan.json --only s2 --takes 3

Shots longer than one clip are chained automatically: the last frame of a segment
is the start image of the next one, so the characters stay the same.
Output: build/clips/<shot>_take<N>.mp4 ; the first take is copied to build/clips/<shot>.mp4
"""
import argparse
import math
import shutil

import numpy as np
import torch
from PIL import Image

from common import load_plan, pick_dtype, place_on_gpu, work_dir

CFG = {
    #           repo                                   W    H     fps max_frames frame_rule steps guidance
    "wan5b":  ("Wan-AI/Wan2.2-TI2V-5B-Diffusers",     704, 1280, 24, 121, 4, 50, 5.0),
    "wan14b": ("Wan-AI/Wan2.2-I2V-A14B-Diffusers",    480, 832,  16, 81,  4, 40, 3.5),
    "ltx":    ("Lightricks/LTX-Video",                448, 768,  24, 161, 8, 50, 3.0),
}
WAN_NEG = ("bright overexposed, static, blurry details, subtitles, text, worst quality, low quality, "
           "JPEG artifacts, extra fingers, deformed, disfigured, extra limbs, fused fingers, "
           "messy background, walking backwards, camera shake, morphing, flicker")



def load_pipe(name, dtype, offload):
    repo = CFG[name][0]
    if name.startswith("wan"):
        from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
        vae = AutoencoderKLWan.from_pretrained(repo, subfolder="vae", torch_dtype=torch.float32)
        pipe = WanImageToVideoPipeline.from_pretrained(repo, vae=vae, torch_dtype=dtype)
    else:
        from diffusers import LTXImageToVideoPipeline
        pipe = LTXImageToVideoPipeline.from_pretrained(repo, torch_dtype=dtype)
    if hasattr(pipe, "vae") and hasattr(pipe.vae, "enable_tiling"):
        pipe.vae.enable_tiling()
    return place_on_gpu(pipe, offload)


def to_pil(frame):
    arr = np.asarray(frame)
    if arr.dtype != np.uint8:
        arr = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(arr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--model", choices=CFG, default="wan5b")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--takes", type=int, default=1)
    ap.add_argument("--steps", type=int, help="override sampling steps (lower = faster)")
    ap.add_argument("--dtype", default="auto", choices=["auto", "bf16", "fp16", "fp32"])
    ap.add_argument("--offload", default="model", choices=["none", "model", "sequential"])
    a = ap.parse_args()

    from diffusers.utils import export_to_video

    plan, wd = load_plan(a.plan), work_dir(a.plan)
    repo, W, H, fps, cap, rule, steps, cfg = CFG[a.model]
    steps = a.steps or steps
    pipe = load_pipe(a.model, pick_dtype(a.dtype), a.offload)
    neg = f"{plan.get('negative', '')}, {WAN_NEG}"

    for s in plan["shots"]:
        if a.only and s["id"] not in a.only:
            continue
        start = Image.open(wd / "images" / f"{s['id']}.png").convert("RGB").resize((W, H), Image.LANCZOS)
        total = math.ceil(s["duration"] * fps) + 1
        prompt = f"{s['motion_prompt']} 2D cartoon, thick black outlines, flat colors."
        for k in range(a.takes):
            all_frames, img, seg = [], start, 0
            while len(all_frames) < total:
                need = total - len(all_frames) + (1 if seg else 0)  # +1: next segment repeats the join frame
                n = min(cap, (need + rule - 2) // rule * rule + 1)  # round UP to rule*k+1, max one clip
                g = torch.Generator("cpu").manual_seed(s.get("seed", 0) * 100 + k * 10 + seg)
                kw = dict(image=img, prompt=prompt, negative_prompt=neg, width=W, height=H,
                          num_frames=n, num_inference_steps=steps, guidance_scale=cfg, generator=g)
                if a.model == "ltx":
                    kw.update(frame_rate=fps, decode_timestep=0.05, decode_noise_scale=0.025)
                frames = pipe(**kw).frames[0]
                frames = [to_pil(f) for f in frames]
                all_frames += frames if seg == 0 else frames[1:]  # drop duplicated join frame
                img = frames[-1]
                seg += 1
            p =wd / "clips" / f"{s['id']}_take{k + 1}.mp4"
            export_to_video(all_frames, str(p), fps=fps)
            print("saved", p, f"({len(all_frames)} frames @ {fps} fps)")
        if not (wd / "clips" / f"{s['id']}.mp4").exists():
            shutil.copy(wd / "clips" / f"{s['id']}_take1.mp4", wd / "clips" / f"{s['id']}.mp4")


if __name__ == "__main__":
    main()
