"""Step 1 - keyframe images for each shot (free models via diffusers).

  python make_images.py plan.json                      # FLUX.1-schnell (Apache-2.0, 4 steps)
  python make_images.py plan.json --model qwen         # Qwen-Image (Apache-2.0, best text/cartoon, big)
  python make_images.py plan.json --edit               # shots with "edit_from" are made by Qwen-Image-Edit
                                                       # from the earlier shot's image -> same characters
  python make_images.py plan.json --only s2 --takes 4  # 4 variations of one shot, pick the best

Output: build/images/<shot>_take<N>.png ; copy the chosen one to build/images/<shot>.png
(the first take is copied automatically if <shot>.png does not exist yet).
"""
import argparse
import shutil

import torch

from common import load_plan, pick_dtype, place_on_gpu, work_dir

MODELS = {
    "flux": "black-forest-labs/FLUX.1-schnell",
    "qwen": "Qwen/Qwen-Image",
}
EDIT_MODEL = "Qwen/Qwen-Image-Edit-2509"


def text_pipe(model, dtype, offload):
    if model == "flux":
        from diffusers import FluxPipeline
        pipe = FluxPipeline.from_pretrained(MODELS[model], torch_dtype=dtype)
    else:
        from diffusers import QwenImagePipeline
        pipe = QwenImagePipeline.from_pretrained(MODELS[model], torch_dtype=dtype)
    return place_on_gpu(pipe, offload)


def gen_text(pipe, model, prompt, negative, w, h, seed):
    g = torch.Generator("cpu").manual_seed(seed)
    if model == "flux":  # schnell: no CFG / negative prompt, 4 steps
        return pipe(prompt, width=w, height=h, num_inference_steps=4, guidance_scale=0.0,
                    max_sequence_length=256, generator=g).images[0]
    return pipe(prompt, negative_prompt=negative, width=w, height=h, num_inference_steps=40,
                true_cfg_scale=4.0, generator=g).images[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--model", choices=MODELS, default="flux")
    ap.add_argument("--edit", action="store_true", help="use Qwen-Image-Edit for shots with edit_from")
    ap.add_argument("--only", nargs="*", help="shot ids to (re)make")
    ap.add_argument("--takes", type=int, default=2)
    ap.add_argument("--size", default="720x1280", help="WxH, keep 9:16 (multiples of 16)")
    ap.add_argument("--dtype", default="auto", choices=["auto", "bf16", "fp16", "fp32"])
    ap.add_argument("--offload", default="model", choices=["none", "model", "sequential"])
    a = ap.parse_args()

    plan, out = load_plan(a.plan), work_dir(a.plan) / "images"
    w, h = map(int, a.size.split("x"))
    dtype = pick_dtype(a.dtype)
    shots = [s for s in plan["shots"] if not a.only or s["id"] in a.only]
    style, neg = plan["style"], plan.get("negative", "")

    plain = [s for s in shots if not (a.edit and s.get("edit_from"))]
    edits = [s for s in shots if a.edit and s.get("edit_from")]

    if plain:
        pipe = text_pipe(a.model, dtype, a.offload)
        for s in plain:
            prompt = f"{style} {s['image_prompt']}"
            for k in range(a.takes):
                img = gen_text(pipe, a.model, prompt, neg, w, h, s.get("seed", 0) + k)
                p = out / f"{s['id']}_take{k + 1}.png"
                img.save(p)
                print("saved", p)
            if not (out / f"{s['id']}.png").exists():
                shutil.copy(out / f"{s['id']}_take1.png", out / f"{s['id']}.png")
        del pipe
        torch.cuda.empty_cache()

    if edits:
        from diffusers import QwenImageEditPlusPipeline
        from PIL import Image
        pipe = place_on_gpu(QwenImageEditPlusPipeline.from_pretrained(EDIT_MODEL, torch_dtype=dtype), a.offload)
        for s in edits:
            ref = Image.open(out / f"{s['edit_from']}.png").convert("RGB")
            prompt = ("Keep the exact same two stickman characters, same drawing style, same shirt colors "
                      f"and same props. Change the scene: {s['image_prompt']}")
            for k in range(a.takes):
                g = torch.Generator("cpu").manual_seed(s.get("seed", 0) + k)
                img = pipe(image=[ref], prompt=prompt, negative_prompt=neg, true_cfg_scale=4.0,
                           num_inference_steps=40, generator=g).images[0].resize((w, h))
                p = out / f"{s['id']}_take{k + 1}.png"
                img.save(p)
                print("saved", p)
            if not (out / f"{s['id']}.png").exists():
                shutil.copy(out / f"{s['id']}_take1.png", out / f"{s['id']}.png")


if __name__ == "__main__":
    main()
