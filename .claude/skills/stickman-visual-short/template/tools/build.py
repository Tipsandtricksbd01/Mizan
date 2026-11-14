"""Builds the HyperFrames project (index.html + compositions/sN.html) for a stickman short.

EXAMPLE FILM: "Who laughs last" - rain / upside-down umbrella -> desert / umbrella water tank.
To make a new film: keep the helpers (Scene, JS), rewrite the SHOT functions and CUES at the bottom.
Run from the project root:  python3 tools/build.py && python3 tools/sound.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rig import (BLUE, GREEN, INK, H, W, character, cloud, dead_tree, desert, fk, mug, pole,  # noqa: E402
                 rain, sky_rain, sky_sunny, storm_clouds, sun, umbrella_bowl, umbrella_up, wet_street)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30

# --------------------------------------------------------------------------- JS helpers
# All joint motion = attribute tweens of rotate(); whole-body motion = translate()+rotate() string tweens.
JS = r"""
const tl = gsap.timeline({ paused: true });
const R = (a) => `rotate(${a})`;
function rotT(id, a, b, t, d, ease = "sine.inOut") {
  tl.fromTo("#" + id, { attr: { transform: R(a) } }, { attr: { transform: R(b) }, duration: d, ease: ease, immediateRender: false }, t);
}
function body(id, x0, y0, r0, x1, y1, r1, t, d, ease = "power2.inOut") {
  tl.fromTo("#" + id, { attr: { transform: `translate(${x0},${y0}) rotate(${r0})` } },
            { attr: { transform: `translate(${x1},${y1}) rotate(${r1})` }, duration: d, ease: ease, immediateRender: false }, t);
}
function face(p, from, to, t) { tl.set("#" + p + "-f-" + from, { opacity: 0 }, t); tl.set("#" + p + "-f-" + to, { opacity: 1 }, t); }
function show(s, t) { tl.set(s, { opacity: 1 }, t); }
function hide(s, t) { tl.set(s, { opacity: 0 }, t); }
function fade(s, a, b, t, d) { tl.fromTo(s, { opacity: a }, { opacity: b, duration: d, ease: "power1.inOut", immediateRender: false }, t); }
// walk in place: legs swing, shins bend on the back swing, body bobs. arm = "B"/"F"/"" swings that arm.
function walk(p, t0, t1, period = 0.62, amp = 22, arm = "B", armAmp = 18, armBase = 0) {
  const half = period / 2; let s = 1;
  for (let t = t0; t + half <= t1 + 1e-6; t += half, s = -s) {
    rotT(p + "-thL", -amp * s, amp * s, t, half); rotT(p + "-thR", amp * s, -amp * s, t, half);
    tl.fromTo("#" + p + (s > 0 ? "-shL" : "-shR"), { attr: { transform: R(0) } }, { attr: { transform: R(28) }, duration: half / 2, yoyo: true, repeat: 1, ease: "sine.inOut", immediateRender: false }, t);
    tl.fromTo("#" + p, { attr: { transform: "translate(0,0) rotate(0)" } }, { attr: { transform: "translate(0,-9) rotate(0)" }, duration: half / 2, yoyo: true, repeat: 1, ease: "sine.out", immediateRender: false }, t);
    if (arm) rotT(p + "-ar" + arm, armBase + armAmp * s, armBase - armAmp * s, t, half);
  }
}
// loop a translate() between two points (rain, sweat), finite repeats only
function drift(id, x0, y0, x1, y1, t, d, reps) {
  tl.fromTo("#" + id, { attr: { transform: `translate(${x0},${y0})` } }, { attr: { transform: `translate(${x1},${y1})` }, duration: d, ease: "none", repeat: reps, immediateRender: false }, t);
}
function grow(id, attrsFrom, attrsTo, t, d, ease = "power1.inOut") {
  tl.fromTo("#" + id, { attr: attrsFrom }, { attr: attrsTo, duration: d, ease: ease, immediateRender: false }, t);
}
"""


class Scene:
    def __init__(self, sid, start, dur, bg="#000"):
        self.id, self.start, self.dur, self.bg = sid, start, dur, bg
        self.svg, self.js = [], []

    def write(self):
        sid = self.id
        html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {self.bg}; }}
    #{sid}-svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
    <svg id="{sid}-svg" viewBox="0 0 {W} {H}" data-layout-allow-overflow data-layout-allow-occlusion>
      {''.join(self.svg)}
    </svg>
  </div>
  <script>
{JS}
{chr(10).join(self.js)}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""
        os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
        with open(os.path.join(ROOT, "compositions", f"{sid}.html"), "w", encoding="utf-8") as f:
            f.write(html)


def write_index(scenes, title):
    total = round(sum(s.dur for s in scenes), 3)
    hosts = "\n".join(
        f'      <div id="{s.id}" data-composition-id="{s.id}" data-composition-src="compositions/{s.id}.html" '
        f'data-start="{s.start}" data-duration="{s.dur}" data-track-index="1" data-track-kind="graphics" '
        f'data-width="{W}" data-height="{H}"></div>' for s in scenes)
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
{hosts}
      <audio id="music" class="clip" src="assets/music.wav" data-start="0" data-duration="{total}" data-track-index="2" data-volume="1"></audio>
      <audio id="sfx" class="clip" src="assets/sfx.wav" data-start="0" data-duration="{total}" data-track-index="3" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return total


# =========================================================================== THE FILM
GROUND = 1400
HERO_X, RIVAL_X = 290, 800
SC = 1.22                   # character scale
S1, S2 = 3.0, 8.5            # shot lengths (s)
CUES = []                    # (absolute time, sound name, gain) -> tools/cues.json -> sound.py


def cue(t, name, gain=1.0):
    CUES.append([round(t, 3), name, gain])


def shot1():
    sc = Scene("s1", 0.0, S1, "#3B4656")
    a = sc.svg
    a += [sky_rain("s1"), storm_clouds("s1"), wet_street("s1", GROUND)]

    # hero: green, holds a red umbrella UPSIDE DOWN (a bowl) that fills with rain
    fx, fy = fk(34, -40, -110)
    rim = fy - 330
    bowl = umbrella_bowl("s1-bowl", fx, rim, 320, "#E03A3A", water_id="s1-water")
    hero = character("hero", HERO_X, GROUND, GREEN, scale=SC, pose=dict(arF=-40, faF=-110, arB=10, faB=-15),
                     face="annoyed", faces=("annoyed", "worried"),
                     behind=pole(fx, fy + 30, rim + 115, hook=True) + bowl)
    # rival: blue, normal yellow umbrella in the back hand, points and laughs (mirrored to face the hero)
    bx, by = fk(22, -160, 20)
    canopy = umbrella_up("s1-yel", bx, by - 330, 330, "#F7C21B")
    rival = character("rival", RIVAL_X, GROUND, BLUE, scale=SC, facing=-1, pose=dict(arF=-88, faF=-6, arB=-160, faB=20),
                      face="laugh", faces=("laugh", "smile"),
                      behind=pole(bx, by + 30, by - 330 + 138, hook=True) + canopy)
    a += [hero, rival, rain("s1")]
    j = sc.js
    j.append('drift("s1-rain", 0, 0, -60, 320, 0, 0.32, 9);')
    for i in range(5):
        j.append(f'tl.fromTo("#s1-rip{i}", {{opacity: 0.9, attr: {{rx: 10}}}}, {{opacity: 0, attr: {{rx: 70}}, duration: 0.5, ease: "power1.out", repeat: 5, immediateRender: false}}, {0.1 * i});')
    # bowl fills
    bottom = rim + 320 * 0.36
    j.append(f'grow("s1-water", {{y: {bottom + 4}, height: 0}}, {{y: {rim + 8}, height: {bottom - rim}}}, 0, 2.9, "power1.out");')
    j.append('fade("#s1-bowl-surf", 0, 0.9, 1.6, 0.6);')
    j.append('walk("hero", 0, 3.0, 0.62, 20, "B", 16, 10);')
    j.append('walk("rival", 0.1, 3.0, 0.62, 16, "", 0, 0);')
    # rival laughs: head bobs, pointing arm shakes
    for k in range(7):
        t = 0.25 + k * 0.36
        j.append(f'rotT("rival-head", -4, 10, {t:.2f}, 0.18, "power1.out"); rotT("rival-head", 10, -4, {t + 0.18:.2f}, 0.18, "power1.in");')
        j.append(f'rotT("rival-faF", -6, -16, {t:.2f}, 0.18); rotT("rival-faF", -16, -6, {t + 0.18:.2f}, 0.18);')
    j.append('face("hero", "annoyed", "worried", 1.7); face("hero", "worried", "annoyed", 2.5);')
    j.append('rotT("hero-head", 0, -8, 1.6, 0.3);')
    cue(0.0, "rain", 1.0)
    cue(0.25, "thunder", 0.9)
    for k in range(3):
        cue(0.3 + k * 0.9, "laugh", 0.95)
    cue(2.82, "whoosh", 0.9)
    return sc


def shot2():
    sc = Scene("s2", S1, S2, "#4B9BE0")
    a = sc.svg
    a += [sky_sunny("s2"), cloud(150, 230, 1.0), cloud(330, 330, 0.7), sun("s2", 860, 260),
          desert("s2", GROUND - 60), dead_tree(70, GROUND - 80, 0.9)]
    # hero: umbrella is now a water tank with a tap; fills a mug and drinks
    fx, fy = fk(34, -40, -110)
    mx, my = fk(22, -60, -60)            # mug hand in the "fill" pose (forearm world angle -120)
    mug_top = my - 70
    spout_y = mug_top - 110
    tx, ty = mx - 22, spout_y - 50
    bottom = ty - 4
    rim = bottom - 320 * 0.36
    bowl = umbrella_bowl("s2-bowl", fx, rim, 320, "#E03A3A", water_id="s2-tank", tap=(tx, ty))
    stream = (f'<rect id="s2-stream" x="{mx - 7}" y="{spout_y}" width="14" height="0" rx="7" fill="#5DB7EE" opacity="0.95"/>')
    hero = character("hero", HERO_X, GROUND, GREEN, scale=SC, pose=dict(arF=-40, faF=-110, arB=-60, faB=-60),
                     face="smile", faces=("smile", "drink", "bliss"),
                     hand_b=mug("s2-mug", water_id="s2-mugw", upright_rel=120), back_arm_front=True,
                     behind=pole(fx, fy + 30, bottom - 2, hook=True) + bowl + stream)
    rival = character("rival", RIVAL_X, GROUND, BLUE, scale=SC, facing=-1, pose=dict(torso=16, arF=6, faF=4, arB=-4, faB=6, head=8),
                      face="thirsty", faces=("thirsty", "cry", "out"))
    heat = "".join(f'<path id="s2-heat{i}" d="M{x} {GROUND - 90} q12 -20 0 -40 q-12 -20 0 -40" fill="none" stroke="#FFFFFF" '
                   f'stroke-width="4" opacity="0" stroke-linecap="round"/>' for i, x in enumerate((520, 640, 980)))
    a += [heat, hero, rival]
    j = sc.js
    j.append(f'grow("s2-tank", {{y: {rim + 10}, height: {bottom - rim}}}, {{y: {rim + 10}, height: {bottom - rim}}}, 0, 0.01);')
    j.append('rotT("s2-rays", 0, 24, 0, 8.5, "none");')
    for i in range(3):
        j.append(f'tl.fromTo("#s2-heat{i}", {{opacity: 0, y: 0}}, {{opacity: 0.6, y: -40, duration: 0.9, yoyo: true, repeat: 7, ease: "sine.inOut", immediateRender: false}}, {0.3 * i});')
    j.append('walk("hero", 0, 8.5, 0.62, 20, "", 0, 0);')
    j.append('walk("rival", 0, 4.6, 0.8, 12, "", 0, 0);')
    j.append('show("#rival-sweat", 0.3); drift("rival-sweat", 0, 0, 0, 26, 0.3, 0.7, 6);')

    # hero fill -> drink -> fill -> drink (stream + mug water)
    def fill(t, d):
        j.append(f'grow("s2-stream", {{height: 0}}, {{height: 112}}, {t}, 0.18, "power2.in");')
        j.append(f'grow("s2-mugw", {{y: -10, height: 0}}, {{y: -62, height: 52}}, {t + 0.15}, {d - 0.2}, "power1.out");')
        j.append(f'grow("s2-stream", {{y: {spout_y}, height: 112}}, {{y: {spout_y + 112}, height: 0}}, {t + d}, 0.15, "power2.in");')
        cue(S1 + t, "pour", 0.9)

    def drink(t):
        j.append(f'rotT("hero-arB", -60, -100, {t}, 0.4, "back.out(1.4)"); rotT("hero-faB", -60, -100, {t}, 0.4, "back.out(1.4)");')
        j.append(f'face("hero", "smile", "drink", {t + 0.3}); rotT("hero-head", 0, -10, {t + 0.3}, 0.3);')
        j.append(f'grow("s2-mugw", {{y: -62, height: 52}}, {{y: -10, height: 0}}, {t + 0.4}, 1.0, "power1.in");')
        j.append(f'rotT("hero-arB", -100, -60, {t + 1.5}, 0.4); rotT("hero-faB", -100, -60, {t + 1.5}, 0.4);')
        j.append(f'rotT("hero-head", -10, 0, {t + 1.5}, 0.3); face("hero", "drink", "bliss", {t + 1.5}); face("hero", "bliss", "smile", {t + 2.4});')
        for g in range(3):
            cue(S1 + t + 0.45 + g * 0.32, "gulp", 0.9)
        cue(S1 + t + 1.5, "ahh", 0.8)

    fill(0.35, 1.3)
    drink(1.8)
    fill(4.4, 1.1)
    drink(5.65)
    j.append('face("hero", "bliss", "bliss", 7.9);')

    # rival: thirsty -> cry -> kneel -> collapse
    j.append('face("rival", "thirsty", "cry", 3.0);')
    j.append('rotT("rival-torso", 16, 30, 4.4, 0.6); rotT("rival-head", 8, 18, 4.4, 0.6);')
    j.append('rotT("rival-thL", 0, -62, 4.7, 0.45, "power2.in"); rotT("rival-thR", 0, -50, 4.7, 0.45, "power2.in");')
    j.append('rotT("rival-shL", 0, 110, 4.7, 0.45, "power2.in"); rotT("rival-shR", 0, 104, 4.7, 0.45, "power2.in");')
    j.append('body("rival", 0, 0, 0, -40, 104, 0, 4.7, 0.45, "power2.in");')
    j.append('rotT("rival-arF", 6, -40, 4.9, 0.4); rotT("rival-arB", -4, -30, 4.9, 0.4);')
    cue(S1 + 5.12, "thud_small", 0.8)
    cue(S1 + 3.0, "whimper", 0.8)
    j.append('body("rival", -40, 104, 0, -250, 150, 72, 6.3, 0.5, "power3.in");')
    j.append('rotT("rival-torso", 30, 10, 6.3, 0.5); rotT("rival-arF", -40, -150, 6.3, 0.5); rotT("rival-arB", -30, -140, 6.3, 0.5);')
    j.append('body("rival", -250, 150, 72, -250, 142, 74, 6.8, 0.12, "power1.out"); body("rival", -250, 142, 74, -250, 150, 72, 6.92, 0.12, "power1.in");')
    j.append('face("rival", "cry", "out", 6.8); hide("#rival-sweat", 6.8);')
    cue(S1 + 6.8, "thud", 1.0)
    cue(S1 + 6.95, "trombone", 0.85)
    cue(S1, "desert", 1.0)
    return sc


def main():
    scenes = [shot1(), shot2()]
    for s in scenes:
        s.write()
    total = write_index(scenes, "Who Laughs Last")
    with open(os.path.join(ROOT, "tools", "cues.json"), "w") as f:
        json.dump({"total": total, "fps": FPS, "music": {"bpm": 116, "mood_change": [[S1, "desert"], [S1 + 6.8, "stop"]]},
                   "cues": sorted(CUES)}, f, indent=1)
    print(f"wrote index.html + {len(scenes)} scenes, {total}s, {len(CUES)} sound cues")


if __name__ == "__main__":
    main()
