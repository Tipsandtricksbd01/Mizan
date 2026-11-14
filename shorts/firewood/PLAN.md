# Firewood - PLAN

## A. Concept
- **Title:** Firewood
- **Post hook title:** "He laughed in July… 🥶"
- **Logline:** In the summer heat Green chops and stacks firewood while Blue laughs at him from a hammock. In the winter snow Green sits warm by his fire; Blue shivers, turns blue and freezes into an ice block.
- **Why it works with the sound off:** the same two places shown hot then cold, and the woodpile is the joke. Every beat is something you can see: the axe, the woodpile growing, the hammock laugh, the fire, the shivering, the blue skin, the ice.
- **Length:** 12.0 s · 1080x1920 · 30 fps · 2 shots, hard cut.

## B. Video script
| Shot | Time | Place | Beats (absolute s) | Out |
|---|---|---|---|---|
| 1 SETUP | 0.0-3.6 | hot summer meadow, big sun, two trees | 0.0 Green raises the axe over a log on a stump, sweating · 0.45 CHOP, the log splits, a half jumps onto the woodpile · 1.25 chop 2 · 2.05 chop 3 (pile grows each time) · 0.3-3.4 Blue lies in a hammock between the trees, laughing and pointing, the hammock swinging · 2.6 Green wipes his forehead, annoyed | whoosh, hard cut |
| 2 PAYOFF | 3.6-12.0 | snowy winter, grey sky, falling snow, same trees bare | 3.6 Green sits on a log by a crackling campfire, the big woodpile behind him, hands to the fire, bliss · 5.0 holds a cocoa mug (steam), drinks, "ahh" · 3.6 Blue stands in the snow hugging himself and shivering, teeth chattering · 5.4 snow cap on his head · 6.6 his skin turns blue, he cries · 7.8 icicle on his nose · 8.8-9.6 an ice block grows from his feet to over his head · 9.7 frozen face, crack + sad trombone · 10.2-12.0 Green toasts a marshmallow, smiles; hold | end |

## C. Visual plan
**Shot 1 (0-3.6 s).** Backgrounds: `sky_summer` (new) + `sun` + `cloud` + `meadow` (new, grass and flowers) + 2× `tree` (new, leafy).
- **GREEN** (x 280, facing right, scale 1.22). Holds an `axe` (new) in the front hand. Pose: wide stance.
  - Each chop is `rotT(arF)` from -170 to -40 over 0.18 s with `back.in`, then `ease out`.
  - The `stump` + `log` (new): the log halves split apart and are swapped by opacity.
  - `woodpile(n)` (new) beside him: logs pop in one at a time (scale back.out).
  - Face: annoyed. Sweat on.
- **BLUE** (lying in the `hammock`, new, between the trees at x 700-1000). Uses `body()` rotated -80 so he lies along the hammock.
  - The hammock group swings: rotate ±4° about the rope point, 1.2 s, 3 repeats.
  - Laugh face, head bobs, front arm pointing at Green.

**Shot 2 (3.6-12 s).** Backgrounds: `sky_winter` (new, grey-blue) + `snow` (new, looping like `rain`, slow drifting flakes) + `snow_ground` (new) + 2× `tree(bare=True)` with snow on the branches + a big `woodpile`.
- **GREEN** (x 260, facing right). Sitting on a log: thighs -85, shins +85, `body` down 110.
  - `campfire` (new, flames flicker with scale yoyo) at x 470.
  - Hands to the fire: `arF` -70.
  - Mug (existing `mug`, `back_arm_front`) with `steam` (new). Drinks at 5.0 (same drink move as the template).
  - Later he toasts a marshmallow on a stick (new `stick` prop in the front hand).
  - Faces: bliss → drink → smile.
- **BLUE** (x 800, facing left, standing).
  - Arms hug his body: `arF`/`arB` cross over the chest.
  - Shiver: new `shiver(pid, t0, t1)` helper, which moves the torso ±3° fast with a 0.06 s yoyo.
  - Faces: `cold` (new, chattering teeth) → `cry` → `frozen` (new: wide eyes, flat mouth, ice-blue).
  - Head and hands colour: a new id `pid-skull` on the head circle, tweened white → #A9D8F5 at 6.6.
  - `snow_cap` (new) pops onto his head at 5.4.
  - `icicle` (new) under his nose at 7.8.
  - `ice_block` (new): a translucent blue box with highlights, whose height grows 8.8-9.6; a frost sparkle at 9.7.

**New in rig.py:** `sky_summer`, `meadow`, `tree(bare)`, `hammock`, `axe`, `stump`, `log_halves`, `woodpile`, `sky_winter`, `snow`, `snow_ground`, `campfire`, `steam`, `stick_marshmallow`, `snow_cap`, `icicle`, `ice_block`. New faces: `cold` and `frozen`, and the head id `pid-skull`.
**New in build.py:** `shiver()`.

## D. Audio script
**Music:** 112 bpm pizzicato. Shot 1 is bright and bouncy. Shot 2 switches to melody B with sleigh-bell shakes, and it stops dead at 9.7 (the freeze) so the crack and the trombone play alone.

| Time | What we hear | sound.py |
|---|---|---|
| 0.0 | summer birds and cicadas (loop) | `summer` **new** |
| 0.45 / 1.25 / 2.05 | axe chop, wood split | `chop` **new** ×3 |
| 0.6 / 1.4 / 2.2 | log clacks onto the pile | `clack` **new** ×3 |
| 0.4, 1.3, 2.2 | mocking laugh | `laugh` ×3 |
| 3.45 | time-skip swoosh | `whoosh` |
| 3.6 | cold wind (loop) | `winter` **new** |
| 3.6 | fire crackle (loop, quieter) | `fire` **new** |
| 3.7-9.0 | teeth chattering | `chatter` **new** ×4 |
| 5.0 | gulp ×2 + "ahh" | `gulp`, `ahh` |
| 6.6 | whimper | `whimper` |
| 8.8 | ice freezing sweep | `freeze` **new** |
| 9.7 | ice crack + sad trombone | `crack` **new**, `trombone` |

**Voice:** wordless sounds only (laughs, ahh, whimper). Target loudness: -14 to -12 LUFS.

## E. Post copy
- **Caption:** "Some people chop wood in summer. Some people laugh at them. 🪓☀️ ➜ ❄️🔥 Who's laughing now?"
- **Hashtags:** #stickman #funnyanimation #cartoonshorts #lifelesson #whoLaughsLast
- **Thumbnail frame:** 10.5 s (Green warm by the fire and Blue frozen in the ice block, both in one frame).
