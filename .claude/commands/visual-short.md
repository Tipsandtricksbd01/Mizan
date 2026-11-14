---
description: Write the full plan for a stickman visual-gag short - video script, visual plan (image + image-to-video prompts) and audio script (music, SFX cue sheet, optional voice).
argument-hint: [idea or topic | blank for 10 ideas] [length in s, default 12]
---

Use the `stickman-visual-short` skill (`.claude/skills/stickman-visual-short/SKILL.md`). Read it first and follow its style lock, templates and rules.

Input: $ARGUMENTS

1. If the input is empty or only a broad topic, give **10 numbered gag ideas** (one line each: setup -> twist -> payoff, wordless, universal), then stop and ask which one to plan. Otherwise continue with the given idea.
2. Default length 12 s (allowed 8-30 s), 1080x1920, 30 fps. Hero = green shirt, Rival = blue shirt unless the idea needs others.
3. Write the plan to `shorts/<kebab-slug>/PLAN.md` with exactly these sections:

   **A. Concept** - title, hook title for the post, logline, why it is funny with sound off, target length.

   **B. Video script** - shot table (shot no., start-end s, location/weather, beat-by-beat actions with timecodes, on-screen text if any, transition). Follow the SKILL §3 rules.

   **C. Visual plan**
   - Style lock paragraph (copied from SKILL §1, adjusted only for this story).
   - Character sheet prompt.
   - Prop sheet prompt for the hero prop (and its "after" version).
   - Per shot: keyframe image prompt + negative prompt, image-to-video motion prompt, clip length, whether to chain with first-last-frame, number of takes.
   - Recommended model per step from SKILL §6 (free open-source only, with the exact script flags for the user's GPU).

   **D. Audio script**
   - Music prompt (ready to paste into ACE-Step 1.5) with mood change points.
   - SFX cue sheet table: time | sound | prompt for Stable Audio Open / MMAudio (or a free CC0 file).
   - Voice: either "none" or the exact lines/laughs with timecodes, emotion tags, and the engine (kokoro voice id or chatterbox exaggeration).
   - Mix targets (music volume vs SFX, -14 LUFS final).

   **E. plan.json** - also write `shorts/<kebab-slug>/plan.json` in the format of `.claude/skills/stickman-visual-short/scripts/shots.example.json` (style, negative, characters, shots with image_prompt/motion_prompt/duration/seed/edit_from, music, sfx, voice) so the Python scripts can run it directly.

   **F. Production checklist** - the ordered steps (images -> video takes -> audio -> assemble with the exact `make_images.py` / `make_video.py` / `make_audio.py` / `assemble.py` commands from SKILL §7 -> QA §8) with the file names to save into `shorts/<slug>/`.

   **G. Post copy** - caption, 5 hashtags, thumbnail frame time.

4. Reply with a short summary and the path to PLAN.md. Use free tools only - never suggest paid services. Do not generate media unless asked.
