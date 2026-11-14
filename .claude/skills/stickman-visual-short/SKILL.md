---
name: stickman-visual-short
description: Claude makes a complete vertical 9:16 stickman cartoon "visual gag" short (8-30 s, MP4 with sound) by itself - no AI image/video models, no GPU, no paid tools, nothing to install on the user's computer. Two round-head stickmen in colored shirts, a setup, a time-skip, a role-reversal payoff (like the rain-umbrella / desert-water reference). Claude writes the script, visual plan and audio plan, draws and animates the characters with code (SVG + GSAP in HyperFrames), synthesizes all sound effects and music with Python, renders the MP4 in its cloud container, and checks it. Use for "stickman video", "cartoon visual short", "like this video", "who laughs last" style reels, or when /visual-short is run.
---

# Stickman Visual Short (made 100% by Claude)

Silent-comedy cartoon reels that tell a story **with pictures only**: one smart character, one mocking character, a time-skip, a payoff where the tables turn. The joke works with the sound off; sound makes it funnier.

**The person only needs Claude.** Claude does every step in its own cloud container: the art is drawn with code (flat cartoon style, which is exactly this genre's look), animated with a joint rig, the sound is synthesized, and HyperFrames renders the MP4 (~1 min for 12 s on CPU). No image/video AI model, no GPU, no downloads of models, no paid service.

- Reference look: `references/reference-contact-sheet.jpg` (20 frames of the original 11 s video).
- Working template: `template/` (a finished example film: "Who Laughs Last", rain -> desert). Copy it for every new video.
- Optional AI-model route for people with a GPU: `references/gpu-pipeline.md` (not needed).

## 1. The formula (from the reference video)

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

## 2. How Claude makes a video (follow in order)

1. **Idea** - one wordless gag: "A does ___ (looks dumb), B mocks; LATER ___, A wins, B ___." (`/visual-short` with no idea = 10 ideas first.)
2. **Write the plan** in `shorts/<slug>/PLAN.md`: video script (§3), visual plan (§4), audio script (§5). Show it to the person and wait for OK unless they said "just make it".
3. **Copy the template:** `mkdir -p shorts/<slug> && cp -r .claude/skills/stickman-visual-short/template/. shorts/<slug>/`
4. **Edit `tools/build.py`** (the film): keep `JS`, `Scene`, `write_index`; rewrite `shot1()`, `shot2()` ... and the `S1, S2` lengths, positions and `cue()` calls from your plan. Add new props/backgrounds/faces to `tools/rig.py` when the story needs them (§6). New sound names go in `tools/sound.py` `SOUNDS`.
5. **Build:** `cd shorts/<slug> && python3 tools/build.py && python3 tools/sound.py` (needs `pip install numpy scipy soundfile`).
6. **Check:** `npx --yes hyperframes@0.9.38 check --json` -> fix every error (a gauge/pivot warning on a falling body is OK).
7. **Look:** `npx --yes hyperframes@0.9.38 snapshot --at 0.5,<each beat>,<end-0.1> --no-end -o <scratchpad>/snap` and READ the contact sheet. Fix anything that does not read at phone size: overlapping characters, props floating off hands, faces wrong, empty frame. Repeat 5-7 until it is right.
8. **Render:** `npx --yes hyperframes@0.9.38 render -o renders/<slug>.mp4 --quality delivery --quiet` (1080x1920, 30 fps, H.264 + AAC).
9. **Verify the file:** `ffprobe` (size, fps, duration) + a tiled frame sheet from the MP4 (`ffmpeg -i renders/<slug>.mp4 -vf "fps=12/<dur>,scale=240:-1,tile=6x2" -frames:v 1 sheet.jpg`) and look at it; loudness with `ffmpeg -af ebur128` (aim -14 to -12 LUFS).
10. **Deliver:** send the MP4 to the person (SendUserFile), commit + push `shorts/<slug>/` (not `.hyperframes/`, `node_modules/`).

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

## 4. Visual plan template

For each shot write what Claude will DRAW and ANIMATE (it maps 1:1 to `build.py`):

```
SHOT 2  PAYOFF  3.0-11.5 s   background: sky_sunny + sun + clouds + desert + dead_tree
  HERO  (green, x 290, facing right)  props: umbrella_bowl with tap (behind), mug in back hand (back_arm_front)
        0.35 fill: stream grows, mug water rises      1.8 raise mug -> face drink -> gulps -> lower -> bliss
        whole shot: walk(…, 0.62 s period)
  RIVAL (blue, x 800, facing left = toward hero)      pose: torso lean 16, arms hanging, face thirsty, sweat on
        3.0 face cry   4.7 kneel (thighs -60, knees 105, body down 104)   6.3 fall (body rotate 72) -> face out
  SOUND CUES  pour 3.35, gulp x3, ahh, whimper 6.0, thud_small 8.1, thud 9.8, trombone 9.95, desert loop from 3.0
```
Make sure every story beat is a visible change in pose, face or prop. Keep 1-3 actions per character per beat.

## 5. Audio script template

```
MUSIC: bpm, mood per shot, where it stops (sound.py music(): pizzicato melody A -> melody B + shaker at the cut,
       cuts dead at the punchline). Keep it under the effects.
VOICE: none. Only wordless sounds (laughs, gulps, "ahh", whimpers) = no language barrier, works worldwide.

 SFX CUE SHEET  (name = function in tools/sound.py; new name = write a new function)
 time   | what we hear                       | sound.py name
 0.0    | heavy rain loop + distant thunder  | rain, thunder
 0.3    | mocking cartoon laugh "ha-ha-ha!"  | laugh  (x3)
 2.8    | time-skip swoosh                   | whoosh
 3.0    | desert wind, cicadas               | desert (loop)
 3.35   | water pouring into metal mug       | pour
 5.2    | gulp gulp gulp + "ahhh"            | gulp x3, ahh
 6.0    | crying whimper                     | whimper
 9.8    | body thud + sad trombone           | thud, trombone
```
Put every SFX on the exact frame its action happens (1 frame after the picture is fine). Loudness: final mix about -14 LUFS, true peak -1 dBTP.

## 6. The toolkit (template/tools)

**`rig.py` - art + rig.** Canvas 1080x1920. Everything returns SVG strings.
- `character(pid, x, y, shirt, scale, facing, pose, face, faces, hand_f, hand_b, behind, back_arm_front)` - feet at (x,y). `facing=-1` mirrors (to face the other character). Joints with ids `pid-thL/thR` (hips), `pid-shL/shR` (knees), `pid-arF/arB` (shoulders), `pid-faF/faB` (elbows), `pid-torso`, `pid-head`, whole body `pid`. Angle 0 = limb hanging down; negative = forward. Default scale 1.2 (about 700 px tall), ground y ~1400.
- `fk(shoulder_x, upper, fore_rel)` -> hand position, to put props exactly in a hand (pole of an umbrella, rope, sign). Props that move with the hand go in `hand_f`/`hand_b` (forearm space, hand at 0,0).
- Faces (only one visible at a time, switch with `face()`): neutral, smile, bliss, laugh, annoyed, worried, thirsty, cry, shock, drink, out. Sweat drops: `#pid-sweat`. Add a face = add an entry to `FACES`.
- Props: `umbrella_up`, `umbrella_bowl` (with water level + tap), `pole`, `mug` (with water level). Backgrounds: `sky_rain`, `storm_clouds`, `rain` (looping), `wet_street` (puddle ripples), `sky_sunny`, `sun` (spinning rays), `cloud`, `desert` (Voronoi cracked earth), `dead_tree`. New scene types (snow, city, classroom, kitchen, night) = new functions in the same flat style: thick `#1E1B24` outlines (5-7 px), flat fills, one soft shadow.

**`build.py` - JS animation helpers** (all deterministic, HyperFrames-safe):
- `walk(pid, t0, t1, period, amp, arm, armAmp, armBase)` - walk in place (legs, knee bend, body bob, optional arm swing).
- `rotT(id, from, to, t, dur, ease)` - rotate one joint. `body(pid, x0,y0,r0, x1,y1,r1, t, d)` - move/rotate the whole body (kneel, jump, fall: rotate about the feet).
- `face(pid, from, to, t)`, `show/hide/fade`, `grow(id, attrsFrom, attrsTo, t, d)` (water levels, streams, bars), `drift(id, ...)` (rain, sweat; finite repeats).
- `cue(t, "sound", gain)` in Python registers a sound at time t -> `tools/cues.json`.

**`sound.py` - sound with numpy only.** Effects: rain, thunder, laugh, whoosh, desert (wind + cicadas), pour, gulp, ahh, whimper, thud, thud_small, trombone (sad "wah-wah"). Loops (`rain`, `desert`) run until the next loop starts. Music: Karplus-Strong pizzicato + bass, bouncy major melody, switches melody + shaker at the first `mood_change`, stops dead at `"stop"` so the punchline sound lands alone. New effect = small function (noise + filters + envelope, or `vowel()` for voice-like grunts/laughs) added to `SOUNDS`.

**Rules that keep it looking like the genre:** static camera; side-view walk in place; characters 45-55 % of frame height, standing on one ground line in the middle; big sky with weather on top; textured ground below; hard cut between shots; the prop that is the joke is drawn the same in both shots except the one changed detail; the loser gets worse in 3-4 visible stages and the last pose holds 1 s+.

## 7. QA checklist

- [ ] Sound OFF: is the joke clear? (If not, fix the picture, not the audio.)
- [ ] Frame 0 already shows both characters and the conflict (scroll-stopping thumbnail).
- [ ] Same shirt colors, same prop design in every shot; props sit in the hands; characters do not overlap at the end pose.
- [ ] No camera drift unless planned; feet on the ground line.
- [ ] Each SFX lands on its action (cue = picture time); music stops for the punchline; final -14 to -12 LUFS.
- [ ] `hyperframes check` passes; you LOOKED at the snapshot sheet and at frames from the rendered MP4.
- [ ] Ends on the punchline pose; 8-30 s; 1080x1920 H.264 MP4.
- [ ] Original idea and characters (do not copy a named show's characters or another creator's exact video).
