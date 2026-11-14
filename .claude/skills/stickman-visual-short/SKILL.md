---
name: stickman-visual-short
description: Make a vertical 9:16 stickman cartoon "visual gag" short (8-30 s, no talking needed) like the rain-umbrella / desert-water reference - two round-head stickmen in colored shirts, a setup scene, a time-skip, a role-reversal payoff. Covers idea, video script, visual plan (image + image-to-video prompts), audio script (SFX, music, optional voice), the open-source GitHub models for each step, and the ffmpeg/HyperFrames assembly. Use for "stickman video", "cartoon visual short", "like this video", "who laughs last" style reels, or when /visual-short is run.
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
4. **Generate images** (§6 models) -> character sheet first, then keyframes using the sheet as reference so faces/shirts/prop stay identical.
5. **Image-to-video** -> each keyframe into a 5-10 s clip. Generate 3-4 takes per shot, keep the best.
6. **Audio** (§5) -> SFX cue sheet + music bed (+ optional voice line / caption).
7. **Assemble** (§7) -> cut, add audio, optional caption hook, export 1080x1920 MP4.
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

Keep motion prompts to 1-3 actions per clip. For a long payoff (8 s+), make 2 clips: first clip's last frame -> second clip's start image (first-last-frame mode in Wan 2.2 / FramePack keeps continuity).

## 5. Audio script template

```
MUSIC: <genre, mood, tempo, instruments>, e.g. "playful cartoon pizzicato + ukulele, 120 BPM,
       switches to sad trombone wah-wah at the fall". Bed at -20 to -24 LUFS, ducks under SFX.
VOICE (optional): none | one hook line | short laughs/grunts only (no language barrier = global reach)

SFX CUE SHEET
 time   | sound                              | source / prompt
 0.0    | rain loop heavy + distant thunder  | MMAudio/Foley or library
 1.5    | mocking cartoon laugh "ha-ha-ha!"  | Chatterbox/ElevenLabs vocal or library
 2.8    | whoosh / time-skip swoosh          | library
 3.0    | desert wind, cicadas, heat         | MMAudio prompt
 3.5    | water tap pouring into metal mug   | MMAudio from the clip
 5.0    | gulp gulp + "ahhh" satisfied        | voice or library
 8.0    | dry groan, crying whimper           | voice
 9.8    | body thud on dirt + sad trombone    | library
```
Put every SFX on the exact frame its action happens (1 frame after the picture is fine). Loudness: final mix about -14 LUFS, true peak -1 dBTP.

## 6. Models & tools (open source on GitHub, checked Nov 2026)

Pick one per row. "GPU" = rough VRAM for 720p-ish output; use ComfyUI to run most of them with a node graph.

| Step | Best open-source pick | Alternatives | Notes |
|---|---|---|---|
| Runner / UI | **Comfy-Org/ComfyUI** (~147k★) | - | Node workflows for all image/video models below. |
| Wan in ComfyUI | **kijai/ComfyUI-WanVideoWrapper** (~6.8k★) | built-in Comfy Wan nodes | I2V, first-last-frame, LoRAs, low-VRAM tricks. |
| Text/image -> image (keyframes, char sheet) | **QwenLM/Qwen-Image** / **Qwen-Image-2.1** | **black-forest-labs/flux** (FLUX.1 / Kontext), flux2 | Qwen-Image-Edit or Flux Kontext = edit a keyframe while keeping the same characters (best for consistency). |
| Image -> video (main) | **Wan-Video/Wan2.2** (~18.6k★) | Wan2.1 | I2V-A14B (best quality, 48-80 GB or offload), TI2V-5B (720p, fits 24 GB). Very good at 2D cartoon motion. |
| Image -> video (fast / with audio) | **Lightricks/LTX-2** (~10k★) | Lightricks/LTX-Video | Fast; LTX-2 can make synced audio too. |
| Image -> video (alt) | **Tencent-Hunyuan/HunyuanVideo-1.5** | HunyuanVideo | Lightweight 8.3B, good motion. |
| Image -> video (low VRAM / long) | **lllyasviel/FramePack** (~17k★) | kijai/ComfyUI-FramePackWrapper | Runs on ~6 GB, long clips, keeps the start frame's look. |
| Video -> SFX (Foley) | **hkchengrex/MMAudio** | **Tencent-Hunyuan/HunyuanVideo-Foley**, kijai/ComfyUI-MMAudio | Feed the finished clip + a text prompt, get synced SFX. |
| Music | **ace-step/ACE-Step-1.5** (~14.7k★) | facebookresearch/audiocraft (MusicGen) | Instrumental bed from a text prompt; set length to the video length. |
| Voice / laughs (optional) | **resemble-ai/chatterbox** (~27.8k★) | SWivid/F5-TTS, hexgrad/kokoro, QwenAudio/CosyVoice | Chatterbox has emotion control (good for laughs/cries). |
| Captions / timing | **m-bain/whisperX** | openai/whisper | Word timestamps if you add a voice line. |
| Upscale | **xinntao/Real-ESRGAN** (anime model `realesr-animevideov3`) | - | 720p -> 1080x1920, crisp outlines. |
| Frame interpolation | **hzwer/Practical-RIFE** | - | 16/24 fps model output -> smooth 30/60 fps. |
| Edit / titles / render | **heygen-com/hyperframes** (installed in this repo: `/hyperframes`) | ffmpeg, CapCut, DaVinci Resolve | HTML -> video, captions, "3 MONTHS LATER" cards, audio mix. |

Paid shortcuts (if no GPU): images - Midjourney, GPT image, Gemini "Nano Banana", Ideogram; image-to-video - Kling, Veo 3, Hailuo/MiniMax, Runway, Sora; voice/SFX - ElevenLabs; music - Suno/Udio. Same prompts work.

Hardware guide: no GPU -> use paid tools or cloud GPU (RunPod/Vast, 24-48 GB). 8-12 GB -> FramePack, Wan2.2 TI2V-5B with offload, LTX. 24 GB -> Wan2.2 TI2V-5B 720p, Qwen-Image fp8, Flux. 48-80 GB -> Wan2.2 A14B full quality.

## 7. Assembly (ffmpeg, no GPU needed)

```bash
# 1) scale every clip to 1080x1920, 30 fps, same codec
for f in shot*.mp4; do ffmpeg -y -i "$f" -vf "scale=1080:1920:flags=lanczos,fps=30,setsar=1" -an -c:v libx264 -crf 18 -pix_fmt yuv420p "n_$f"; done
# 2) join (hard cuts)
printf "file '%s'\n" n_shot*.mp4 > list.txt && ffmpeg -y -f concat -safe 0 -i list.txt -c copy video.mp4
# 3) mix music + sfx (sfx already placed on a timeline in sfx.wav) and normalize
ffmpeg -y -i video.mp4 -i music.wav -i sfx.wav -filter_complex \
 "[1:a]volume=0.35[m];[2:a]volume=1.0[s];[m][s]amix=inputs=2:duration=first,loudnorm=I=-14:TP=-1[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest final.mp4
# place one SFX at 9.8 s:  -filter_complex "[1:a]adelay=9800|9800[x]"
```
For on-screen text cards, captions, or a cleaner mix use HyperFrames (`/hyperframes`, `/media-use`) at 1080x1920.

## 8. QA checklist

- [ ] Sound OFF: is the joke clear? (If not, fix the picture, not the audio.)
- [ ] Frame 0 already shows both characters and the conflict (scroll-stopping thumbnail).
- [ ] Same shirt colors, same prop design, same head shape in every shot; no extra fingers/limbs, no melted faces.
- [ ] No camera drift unless planned; feet on the ground line.
- [ ] Each SFX lands on its action; music ducks under key SFX; final -14 LUFS.
- [ ] Ends on the punchline pose; 8-30 s; 1080x1920 H.264 MP4.
- [ ] Original idea and characters (do not copy a named show's characters or another creator's exact video).
