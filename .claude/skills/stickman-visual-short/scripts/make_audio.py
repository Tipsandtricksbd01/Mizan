"""Step 3 - free audio: voice / laughs, sound effects, music.

  python make_audio.py plan.json voice                       # Kokoro (CPU ok) / Chatterbox (emotion)
  python make_audio.py plan.json sfx                         # Stable Audio Open (text -> SFX)
  python make_audio.py plan.json sfx --mmaudio ~/MMAudio     # MMAudio: SFX synced to the real clips
  python make_audio.py plan.json music --ace ~/ACE-Step-1.5  # ACE-Step 1.5 instrumental bed (MIT)

Output in build/audio/: voice_<i>.wav, sfx_<i>.wav, music.wav  (assemble.py places them by time).
Any sfx/voice item may also have "file": "path.wav" to use your own free CC0 sound instead.
"""
import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

from common import hf_login_hint, load_plan, run, work_dir


# ---------- voice ----------
def voice(plan, out):
    kokoro = chatter = None
    for i, v in enumerate(plan.get("voice", [])):
        p = out / f"voice_{i}.wav"
        if v.get("file"):
            shutil.copy(v["file"], p)
            continue
        if v.get("engine", "kokoro") == "chatterbox":
            import torch
            import torchaudio as ta
            from chatterbox.tts import ChatterboxTTS
            if chatter is None:
                chatter = ChatterboxTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
            kw = {"exaggeration": v.get("exaggeration", 0.7), "cfg_weight": v.get("cfg_weight", 0.3)}
            if v.get("ref_wav"):
                kw["audio_prompt_path"] = v["ref_wav"]
            wav = chatter.generate(v["text"], **kw)
            ta.save(str(p), wav, chatter.sr)
        else:
            from kokoro import KPipeline
            if kokoro is None:
                kokoro = KPipeline(lang_code=v.get("lang", "a"))  # a = US English
            parts = [audio for _, _, audio in kokoro(v["text"], voice=v.get("voice", "af_heart"))]
            sf.write(p, np.concatenate(parts), 24000)
        print("saved", p)


# ---------- sfx ----------
def sfx_stable_audio(plan, out, steps):
    import torch
    from diffusers import StableAudioPipeline
    hf_login_hint()
    pipe = StableAudioPipeline.from_pretrained("stabilityai/stable-audio-open-1.0", torch_dtype=torch.float16).to("cuda")
    for i, s in enumerate(plan.get("sfx", [])):
        p = out / f"sfx_{i}.wav"
        if s.get("file"):
            shutil.copy(s["file"], p)
            continue
        g = torch.Generator("cuda").manual_seed(i)
        audio = pipe(s["prompt"], negative_prompt="low quality, music, speech", num_inference_steps=steps,
                     audio_end_in_s=min(47.0, max(1.0, s.get("dur", 2.0))), generator=g).audios[0]
        sf.write(p, audio.T.float().cpu().numpy(), pipe.vae.sampling_rate)
        print("saved", p)


def sfx_mmaudio(plan, out, mm_dir, wd):
    """One synced SFX track per shot from the generated clip (+ the shot's sfx prompts)."""
    t0 = 0.0
    items = []
    for s in plan["shots"]:
        clip = wd / "clips" / f"{s['id']}.mp4"
        t1 = t0 + s["duration"]
        prompt = ", ".join(x["prompt"] for x in plan.get("sfx", []) if t0 <= x["t"] < t1) or s["motion_prompt"]
        tmp = out / f"mm_{s['id']}"
        run([sys.executable, "demo.py", "--video", clip.resolve(), "--prompt", prompt,
             "--negative_prompt", "music, speech", "--duration", s["duration"],
             "--output", tmp.resolve(), "--skip_video_composite"], cwd=mm_dir)
        flac = next(tmp.glob("*.flac"))
        dst = out / f"shot_{s['id']}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", flac, dst])
        items.append({"t": t0, "file": str(dst), "vol": 1.0})
        t0 = t1
    (out / "mmaudio_items.json").write_text(__import__("json").dumps(items, indent=1))
    print("MMAudio tracks ready; assemble.py picks them up automatically.")


# ---------- music ----------
def music_ace(plan, out, ace_dir):
    sys.path.insert(0, str(Path(ace_dir).resolve()))
    from acestep.handler import AceStepHandler
    from acestep.inference import GenerationConfig, GenerationParams, generate_music
    from acestep.llm_inference import LLMHandler

    m = plan["music"]
    dit, llm = AceStepHandler(), LLMHandler()
    dit.initialize_service(project_root=str(Path(ace_dir).resolve()), config_path="acestep-v15-turbo", device="cuda")
    llm.initialize(checkpoint_dir=str(Path(ace_dir).resolve() / "checkpoints"),
                   lm_model_path="acestep-5Hz-lm-0.6B", backend="pt", device="cuda")
    params = GenerationParams(caption=m["prompt"], lyrics="[Instrumental]", instrumental=True,
                              duration=max(10, m.get("duration", 15)), bpm=m.get("bpm"))
    res = generate_music(dit, llm, params, GenerationConfig(batch_size=1, audio_format="wav"),
                         save_dir=str(out / "ace"))
    if not res.success:
        raise SystemExit(f"ACE-Step failed: {res.error}")
    shutil.copy(res.audios[0]["path"], out / "music.wav")
    print("saved", out / "music.wav")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("what", choices=["voice", "sfx", "music", "all"])
    ap.add_argument("--mmaudio", help="path to a cloned hkchengrex/MMAudio repo (uses the clips)")
    ap.add_argument("--ace", help="path to a cloned ace-step/ACE-Step-1.5 repo")
    ap.add_argument("--sfx-steps", type=int, default=100)
    a = ap.parse_args()
    plan, wd = load_plan(a.plan), work_dir(a.plan)
    out = wd / "audio"
    if a.what in ("voice", "all"):
        voice(plan, out)
    if a.what in ("sfx", "all"):
        if a.mmaudio:
            sfx_mmaudio(plan, out, a.mmaudio, wd)
        else:
            sfx_stable_audio(plan, out, a.sfx_steps)
    if a.what in ("music", "all"):
        if not a.ace:
            raise SystemExit("music needs --ace /path/to/ACE-Step-1.5 (git clone https://github.com/ace-step/ACE-Step-1.5)")
        music_ace(plan, out, a.ace)


if __name__ == "__main__":
    main()
