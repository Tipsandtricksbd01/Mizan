---
name: stickman-visual-short
description: Make a vertical 9:16 stickman cartoon "visual gag" short (8-30 s, no talking needed) like the rain-umbrella / desert-water reference - two round-head stickmen in colored shirts, a setup scene, a time-skip, a role-reversal payoff. Covers idea, video script, visual plan, audio script, and a FREE-only Python pipeline (FLUX/Qwen-Image -> Wan2.2/LTX-Video -> Chatterbox/Kokoro, Stable Audio/MMAudio, ACE-Step -> ffmpeg) with ready scripts. Use for "stickman video", "cartoon visual short", "like this video", "who laughs last" style reels, or when /visual-short is run.
---

# Stickman Visual Short

Make short, silent-comedy cartoon reels that tell a story **with pictures only**: one smart character, one mocking character, a time-skip, and a payoff where the tables turn. The viewer gets it with the sound off; sound only makes it funnier.

Reference: `references/reference-contact-sheet.jpg` (20 frames across the 11 s source).

## 1. What the reference video is (copy this formula)

| Item | Reference |
|---|---|
| Format | 720 x 1280 (9:16), 30 fps, 11.1 s, 2 shots, hard cut at ~2.8 s |
| Shot 1 SETUP (0-2.8 s) | Grey storm, heavy rain, wet street with puddles. **Green** stickman holds a red umbrella **upside down**, catching rain, looks annoyed. **Blue** stickman with a normal yellow umbrella **laughs and points** at him. Both walk left-to-right in place. |
| Shot 2 PAYOFF (2.8-11.1 s) | Hot sun, cracked desert, dunes. Green guy's upturned umbrella is now a **water tank with a tap**; he fills a metal mug, drinks, smiles. Blue guy sweats, tongue out, cries, drops to his knees, then **collapses flat** at the end. |
| Story rule | Setup: A does something that looks stupid -> B mocks. Payoff: the stupid thing was smart -> B suffers. No words needed. |
| Ending | The loser's state gets worse beat by beat (sweat -> tongue -> tears -> kneel -> fall). Final pose = the punchline frame, hold ~1 s. |
| Audio | No dialogue. Rain + thunder + mocking laugh in shot 1; hot-wind, tap pouring, gulp, "ahh", sad groan, body thud in shot 2; light comic music. |

### Visual style lock (put this in every image prompt)

- 2D cartoon, **thick clean black outlines**, flat bright colors, soft shading only on the background.
- Characters: **pure white round head**, simple face (dot or curved eyes, big expressive mouth), **black stick arms and legs**, black mitten hands, a **solid-color T-shirt** that is the character's only identity (Hero = green #3E9B3A, Rival = blue #2F5FC8). No hair, no nose, no clothes other than the shirt.
- Side view, full body, both characters on the same ground line, at about 45-55 % of frame height, filling the middle of the frame. Large sky at top (sun/clouds/rain live there), ground texture at bottom (puddles, cracked earth).
- Camera: locked, eye level, no cuts inside a shot. Characters "walk in place" (background still) - this is what AI video does best and keeps them on-model.
- One prop is the hero of the story (the umbrella). It must look the same in both shots except the one changed detail (the tap).
- Saturated, high contrast, readable on a phone at thumbnail size.

## 2. Workflow

1. **Idea** -> one-line gag: "A does ___ (looks dumb), B mocks; LATER ___, A wins, B ___." Good themes: weather/season flip (rain->drought, summer->winter), saving vs spending, studying vs partying, planting a tree, building a roof, charging a phone, packing food. Keep it universal and wordless.
2. **Script** (§3) -> 2-4 shots, 8-30 s, every beat with a time and an action you can SEE.
3. **Visual plan** (§4) -> character sheet, one keyframe image per shot, one motion prompt per shot.
4. **Generate images** (§6 models, `make_images.py`) -> character sheet first, then keyframes using the sheet as reference so faces/shirts/prop stay identical.
5. **Image-to-video** (`make_video.py`) -> each keyframe into a 5-10 s clip. Generate 3-4 takes per shot, keep the best.
6. **Audio** (§5, `make_audio.py`) -> SFX cue sheet + music bed (+ optional voice line / caption).
7. **Assemble** (§7, `assemble.py`) -> cut, add audio, optional caption hook, export 1080x1920 MP4.
8. **QA** (§8).

Use the `/visual-short <idea>` command to produce steps 1-3 + the audio script in one file.

## 3. Video script template

```
TITLE: <hook title, 3-6 words>          LENGTH: <s>     FORMAT: 1080x1920, 30 fps
LOGLINE: <A> does <x>, <B> laughs. Later <twist>; <A> wins, <B> <fate>.

SHOT 1  SETUP   0.0-3.0 s   <location, weather, time>
  0.0  <what we see first - instant read, both characters already in frame>
  0.8  <A's "dumb" action is clear>
  1.5  <B mocks: laugh + point>
  2.8  hard cut  (optional on-screen card: "3 MONTHS LATER")
SHOT 2  PAYOFF  3.0-11.0 s  <same characters, opposite conditions>
  3.0  <reveal: A's prop is now useful>
  5.0  <A enjoys the result>
  6.5  <B suffers, stage 1>   8.0 <stage 2>   9.5 <stage 3 - fall>
  10.0-11.0 hold on punchline frame
```

Rules: the gag must be clear in the first 1 s of each shot; never more than one new idea per beat; the payoff shot is 2-3x longer than the setup; end on the loser's worst moment (loop-friendly).

## 4. Visual plan template (prompts)

**Character sheet prompt (generate once, reuse):**
```
2D cartoon character sheet, two stickman characters side by side, front and side view,
pure white round heads with simple expressive faces, thick clean black outlines, black stick arms
and legs, black mitten hands, character 1 wears a plain green t-shirt, character 2 wears a plain
blue t-shirt, flat bright colors, white background, consistent proportions, vector-like clean lineart
```

**Keyframe prompt pattern (one per shot):**
```
Vertical 9:16 2D cartoon illustration, thick clean black outlines, flat bright colors.
[SCENE: stormy grey sky with heavy rain, wet street with puddles and reflections].
Left: stickman with white round head and green t-shirt [ACTION + PROP + EXPRESSION].
Right: stickman with white round head and blue t-shirt [ACTION + PROP + EXPRESSION].
Side view, full body, both standing on the same ground line in the middle of the frame,
large sky above, detailed ground below. Funny, expressive, high contrast.
Negative: realistic, 3D, photo, extra limbs, hair, nose, text, watermark, blurry, cropped feet
```

**Image-to-video motion prompt pattern:**
```
Static camera. Both stickmen walk in place to the right with a bouncy cartoon walk cycle.
[A: specific motion, e.g. "raises the mug to his mouth and drinks, then smiles"].
[B: specific motion, e.g. "sweats, tongue hangs out, tears fall, he drops to his knees and falls flat"].
[Environment motion: "heavy rain falls, ripples in puddles" / "heat haze shimmers"].
Smooth 2D cartoon animation, consistent characters, no camera movement, no new objects.
```

Keep motion prompts to 1-3 actions per clip. For a long payoff (8 s+), make 2 clips: first clip's last frame -> second clip's start image (`make_video.py` does this chaining automatically for long shots).

## 5. Audio script template

```
MUSIC: <genre, mood, tempo, instruments>, e.g. "playful cartoon pizzicato + ukulele, 120 BPM,
       switches to sad trombone wah-wah at the fall". Bed at -20 to -24 LUFS, ducks under SFX.
VOICE (optional): none | one hook line | short laughs/grunts only (no language barrier = global reach)

SFX CUE SHEET
 time   | sound                              | source / prompt
 0.0    | rain loop heavy + distant thunder  | Stable Audio Open / MMAudio or CC0 file
 1.5    | mocking cartoon laugh "ha-ha-ha!"  | Chatterbox (exaggeration 0.9) or CC0 file
 2.8    | whoosh / time-skip swoosh          | library
 3.0    | desert wind, cicadas, heat         | MMAudio prompt
 3.5    | water tap pouring into metal mug   | MMAudio from the clip
 5.0    | gulp gulp + "ahhh" satisfied        | voice or library
 8.0    | dry groan, crying whimper           | voice
 9.8    | body thud on dirt + sad trombone    | library
```
Put every SFX on the exact frame its action happens (1 frame after the picture is fine). Loudness: final mix about -14 LUFS, true peak -1 dBTP.

## 6. Free models (open source, GitHub + Python) - FREE ONLY, no paid tools

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

## 7. Run the pipeline (Python)

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

## 8. QA checklist

- [ ] Sound OFF: is the joke clear? (If not, fix the picture, not the audio.)
- [ ] Frame 0 already shows both characters and the conflict (scroll-stopping thumbnail).
- [ ] Same shirt colors, same prop design, same head shape in every shot; no extra fingers/limbs, no melted faces.
- [ ] No camera drift unless planned; feet on the ground line.
- [ ] Each SFX lands on its action; music ducks under key SFX; final -14 LUFS.
- [ ] Ends on the punchline pose; 8-30 s; 1080x1920 H.264 MP4.
- [ ] Original idea and characters (do not copy a named show's characters or another creator's exact video).
