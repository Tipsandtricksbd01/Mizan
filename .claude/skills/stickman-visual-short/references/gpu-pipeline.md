# Optional: AI-model pipeline (only for a computer with an NVIDIA GPU)

Not needed when Claude makes the video itself (SKILL.md). Use this only if the person has a strong GPU or a free Kaggle/Colab GPU and wants painted, AI-generated looks. Scripts: `scripts/`.

## Free models (open source, GitHub + Python) - FREE ONLY, no paid tools

Every step runs from Python with the scripts in `scripts/`. All weights download free from Hugging Face.

| Step | Model (GitHub) | Python | Licence (for monetised videos) | VRAM |
|---|---|---|---|---|
| Keyframe images | **FLUX.1-schnell** (black-forest-labs/flux) | diffusers `FluxPipeline` | Apache-2.0 - commercial OK | ~12 GB w/ offload |
| Keyframe images (better) | **Qwen-Image** (QwenLM/Qwen-Image) | diffusers `QwenImagePipeline` | Apache-2.0 | 24 GB+ w/ offload, 64 GB RAM |
| Same characters in shot 2 | **Qwen-Image-Edit-2509** | diffusers `QwenImageEditPlusPipeline` | Apache-2.0 | 24 GB+ w/ offload |
| Image -> video (default) | **Wan2.2-TI2V-5B** (Wan-Video/Wan2.2) | diffusers `WanImageToVideoPipeline` | Apache-2.0 | 24 GB (less with offload, slower) |
| Image -> video (best) | **Wan2.2-I2V-A14B** | same | Apache-2.0 | 48-80 GB |
| Image -> video (fast / small GPU) | **LTX-Video 2B** (Lightricks/LTX-Video) | diffusers `LTXImageToVideoPipeline` | LTX open licence (free) | 12-16 GB |
| Image -> video (6 GB GPU, long) | **FramePack** (lllyasviel/FramePack) | its own Gradio app | Apache-2.0 | 6 GB |
| Voice / laughs / cries | **Chatterbox** (resemble-ai/chatterbox) | `pip install chatterbox-tts` | MIT | GPU (CPU slow) |
| Short voice lines | **Kokoro-82M** (hexgrad/kokoro) | `pip install kokoro` | Apache-2.0 | **CPU is fine** |
| Sound effects from text | **Stable Audio Open 1.0** | diffusers `StableAudioPipeline` | Stability Community (free < $1M/yr), needs free HF login | 8 GB |
| Sound effects synced to video | **MMAudio** (hkchengrex/MMAudio) | `demo.py` | code MIT, **weights non-commercial** | 6-8 GB |
| Music | **ACE-Step 1.5** (ace-step/ACE-Step-1.5) | `acestep` Python API | MIT - commercial OK | 4-8 GB |
| Upscale (optional) | **Real-ESRGAN** `realesr-animevideov3` | `realesrgan` / ncnn binary | BSD-3 | any |
| Smoother motion (optional) | **Practical-RIFE** (hzwer/Practical-RIFE) | `inference_video.py` | MIT | any |
| Cut, mix, export | **ffmpeg** | `scripts/assemble.py` | free | CPU |
| Titles / captions (optional) | **HyperFrames** (heygen-com/hyperframes, in this repo) | `npx hyperframes` | Apache-2.0 | CPU |

If you will earn money from the videos, use the "commercial OK" rows (FLUX-schnell, Qwen, Wan2.2, Chatterbox, Kokoro, ACE-Step) and make SFX with Stable Audio Open or free CC0 sound files (put `"file": "x.wav"` in the plan). Avoid MMAudio and MusicGen weights for monetised work (non-commercial).

### What you need (all free)

1. **An NVIDIA GPU.** Options:
   - Your own PC: RTX 3060 12 GB = LTX + FLUX-schnell + audio; RTX 3090/4090 24 GB = everything with Wan2.2-5B.
   - **Kaggle Notebooks** (free, 2x T4 16 GB, ~30 GPU h/week, 29 GB RAM) - best free option. Use `--model ltx` or `--model wan5b --offload sequential --dtype fp16`, FLUX-schnell images.
   - **Google Colab free** (T4 16 GB, 12 GB RAM) - works for LTX, FLUX-schnell (`--offload sequential`), Kokoro, Chatterbox, ACE-Step, Stable Audio. Too little RAM for Qwen-Image and Wan 14B.
   - No GPU at all: only Kokoro voice and assemble.py run on CPU; image/video generation is not practical.
2. **Python 3.10-3.12**, **ffmpeg**, `git`, ~60-100 GB free disk for model downloads (Kaggle/Colab: use one video model per session).
3. **A free Hugging Face account** + `huggingface-cli login` (needed for Stable Audio Open; speeds up downloads).
4. Install: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124` then `pip install -r scripts/requirements.txt`; `apt install ffmpeg espeak-ng`; clone ACE-Step-1.5 (music) and optionally MMAudio.

## Run the pipeline (Python)

The whole video is described in one JSON file - copy `scripts/shots.example.json` (it is the rain/desert reference video) to `shorts/<slug>/plan.json` and edit it. `{hero}` / `{rival}` in prompts are replaced from `characters`. Output goes to `shorts/<slug>/build/`.

```bash
cd .claude/skills/stickman-visual-short/scripts
P=../../../../shorts/<slug>/plan.json

python make_images.py $P --takes 3                 # FLUX-schnell keyframes -> build/images/s1_take1..3.png
python make_images.py $P --model qwen --edit       # (24 GB+) shot 2 edited from shot 1 = same characters
#   look at the takes, copy the best one to build/images/<shot>.png
python make_video.py  $P --takes 2                 # Wan2.2-5B clips  (--model ltx on T4 / 12 GB)
#   watch build/clips/*_take*.mp4, copy the best to build/clips/<shot>.mp4
python make_audio.py  $P voice                     # Kokoro / Chatterbox lines
python make_audio.py  $P sfx                       # Stable Audio Open SFX   (or: --mmaudio ~/MMAudio)
python make_audio.py  $P music --ace ~/ACE-Step-1.5
python assemble.py    $P --card "3 MONTHS LATER" --card-at 2.8   # -> build/final.mp4 1080x1920 30fps -14 LUFS
```

Tips: low VRAM -> `--offload sequential`; T4/older GPU -> `--dtype fp16` (if frames come out black, use `--dtype fp32` for the VAE-heavy step or switch to LTX); faster drafts -> `--steps 20`. A shot longer than one clip (Wan-5B: 5 s, LTX: 6.7 s, Wan-14B: 5 s) is chained automatically from the previous segment's last frame. FramePack (6 GB GPUs) is a separate app: load `build/images/<shot>.png`, paste the motion prompt, save the mp4 as `build/clips/<shot>.mp4`, then continue with the audio steps.

