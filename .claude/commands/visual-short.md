---
description: Plan (and make) a stickman visual-gag short with Claude only - video script, visual plan, audio script, then the finished 9:16 MP4. No AI models, no GPU, no paid tools.
argument-hint: [idea | blank for 10 ideas] [length in s, default 12] [make = also build the video]
---

Use the `stickman-visual-short` skill (`.claude/skills/stickman-visual-short/SKILL.md`). Read it first and follow its formula, style rules and templates. Everything is made by Claude in this container: art drawn with code (`template/tools/rig.py`), animation with GSAP in HyperFrames (`template/tools/build.py`), sound synthesized with numpy (`template/tools/sound.py`). Never suggest paid tools or AI image/video models.

Input: $ARGUMENTS

1. If the input is empty or only a broad topic: give **10 numbered gag ideas** (one line each: setup -> twist -> payoff, wordless, universal, original), then stop and ask which one to make.
2. Otherwise write `shorts/<kebab-slug>/PLAN.md` with:

   **A. Concept** - title, post hook title, logline, why it is funny with the sound off, length (default 12 s, 8-30 s), 1080x1920 30 fps.

   **B. Video script** - shot table: shot, start-end s, place/weather, beat-by-beat visible actions with timecodes, transition (SKILL §3 rules).

   **C. Visual plan** - per shot in the SKILL §4 format: background functions, each character (shirt colour, x, facing, pose, face, props, hand), every beat as rig moves (`walk`, `rotT`, `body`, `face`, `grow`), and which NEW drawing functions must be added to `rig.py` (new props, backgrounds, faces).

   **D. Audio script** - music (bpm, mood per shot, stop point), SFX cue sheet (time | what we hear | `sound.py` name, marking new ones to write), voice = wordless sounds only.

   **E. Post copy** - caption, 5 hashtags, thumbnail frame time.

3. If the input contains `make` (or the person approves the plan), make the video exactly as SKILL §2 steps 3-10 say: copy the template, write the shots in `build.py`, add needed art/sounds, build, `check`, snapshot and LOOK, fix, render to `shorts/<slug>/renders/<slug>.mp4`, verify the MP4 frames and loudness, send the file to the person, commit and push.
4. Reply briefly: what was made, the path(s), and what the person can ask to change (story beat, colours, timing, sounds).
