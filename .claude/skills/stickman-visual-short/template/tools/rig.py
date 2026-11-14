"""Stickman cartoon art + rig for vertical (1080x1920) HyperFrames shorts. No AI models, no GPU.

Every function returns an SVG string. A character is a poseable rig:

  <g transform="translate(X,Y) scale(S*dir,S)">          placement (never animated)
    <g id="P" transform="translate(0,0) rotate(0)">        whole body: drop / fall      -> attr tween
      legs:  P-thL / P-thR (hip)   -> P-shL / P-shR (knee)
      <g transform="translate(0,-HIP)"><g id="P-torso" transform="rotate(0)">     lean
         P-arF / P-arB (shoulder) -> P-faF / P-faB (elbow) -> hand + optional prop
         head  P-head (rotate) with faces P-f-<name> (only one has opacity 1)

All joints are animated with GSAP *attribute* tweens of `transform="rotate(a)"`
(see JS helpers in build.py), so the pivot is always the joint. Angles are degrees,
SVG-clockwise; a limb drawn pointing DOWN, rotate(-90) points it FORWARD (the way the character faces).
Feet stand at y=0 of the character. Use fk() to know where a hand ends up (to place props).
"""

import math
import random

INK = "#1E1B24"
WHITE = "#FFFFFF"
GREEN, BLUE, RED_SHIRT, ORANGE, PURPLE = "#3E9B3A", "#2F5FC8", "#D63A3A", "#F08A24", "#7A4CC2"

# body sizes (character units, feet at 0)
HIP = 230          # hip height
THIGH = SHIN = 115
SHOULDER_Y = -385  # absolute (from feet)
UPPER, FORE = 95, 90
HEAD_Y, HEAD_R = -492, 74
LW = 13            # limb line width
OW = 7             # outline width

STROKE = f'stroke="{INK}" stroke-width="{OW}" stroke-linejoin="round" stroke-linecap="round"'


def _dir(a):
    r = math.radians(a)
    return -math.sin(r), math.cos(r)


def fk(shoulder_x, upper_a, fore_rel_a, lean=0.0):
    """Hand position (character units, feet = 0) for an arm pose. fore_rel_a is relative to the upper arm."""
    sx, sy = shoulder_x, SHOULDER_Y + HIP  # shoulder relative to hip pivot
    ux, uy = _dir(upper_a)
    ex, ey = sx + ux * UPPER, sy + uy * UPPER
    fx, fy = _dir(upper_a + fore_rel_a)
    hx, hy = ex + fx * FORE, ey + fy * FORE
    if lean:  # torso lean rotates around the hip
        r = math.radians(lean)
        hx, hy = hx * math.cos(r) - hy * math.sin(r), hx * math.sin(r) + hy * math.cos(r)
    return round(hx, 1), round(hy - HIP, 1)


def limb(length, width=LW):
    return f'<line x1="0" y1="0" x2="0" y2="{length}" stroke="{INK}" stroke-width="{width}" stroke-linecap="round"/>'


def rot(gid, a, inner):
    return f'<g id="{gid}" transform="rotate({a})">{inner}</g>'


def at(x, y, inner):
    return f'<g transform="translate({x},{y})">{inner}</g>'


# ---------------------------------------------------------------- faces
def _eyes_open(dx=26, y=-8):
    return (f'<ellipse cx="{-dx}" cy="{y}" rx="8" ry="12" fill="{INK}"/>'
            f'<ellipse cx="{dx}" cy="{y}" rx="8" ry="12" fill="{INK}"/>'
            f'<circle cx="{-dx + 3}" cy="{y - 4}" r="2.6" fill="#fff"/><circle cx="{dx + 3}" cy="{y - 4}" r="2.6" fill="#fff"/>')


def _arc_eyes(up=True, dx=26, y=-8):
    q = -12 if up else 10
    return (f'<path d="M{-dx - 13} {y + 4} Q{-dx} {y + q} {-dx + 13} {y + 4}" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M{dx - 13} {y + 4} Q{dx} {y + q} {dx + 13} {y + 4}" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')


def _lid_eyes(dx=26, y=-6, droop=False):
    tilt = 6 if droop else 0
    return (f'<path d="M{-dx - 14} {y - tilt} L{-dx + 14} {y + tilt}" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M{-dx - 12} {y} A12 12 0 0 0 {-dx + 12} {y}" fill="{INK}"/>'
            f'<path d="M{dx - 14} {y + tilt} L{dx + 14} {y - tilt}" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M{dx - 12} {y} A12 12 0 0 0 {dx + 12} {y}" fill="{INK}"/>')


def _brows_sad(dx=26, y=-30):
    return (f'<path d="M{-dx - 14} {y + 2} L{-dx + 12} {y - 8}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M{dx + 14} {y + 2} L{dx - 12} {y - 8}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')


def _brows_angry(dx=26, y=-30):
    return (f'<path d="M{-dx - 14} {y - 8} L{-dx + 12} {y + 2}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M{dx + 14} {y - 8} L{dx - 12} {y + 2}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')


FACES = {
    "neutral": lambda: _eyes_open() + f'<path d="M-16 30 L16 30" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
    "smile": lambda: _eyes_open() + f'<path d="M-26 22 Q0 46 26 22" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
    "bliss": lambda: _arc_eyes(True) + f'<path d="M-24 22 Q0 44 24 22" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
             + '<ellipse cx="-46" cy="18" rx="12" ry="7" fill="#F59AA0" opacity="0.8"/><ellipse cx="46" cy="18" rx="12" ry="7" fill="#F59AA0" opacity="0.8"/>',
    "laugh": lambda: _arc_eyes(True) + f'<path d="M-34 14 Q0 18 34 14 Q30 58 0 60 Q-30 58 -34 14 Z" fill="{INK}"/>'
             + '<path d="M-18 46 Q0 36 18 46 Q10 58 0 58 Q-10 58 -18 46 Z" fill="#E8505B"/>'
             + '<rect x="-24" y="15" width="48" height="9" rx="3" fill="#fff"/>',
    "annoyed": lambda: _lid_eyes() + _brows_angry() + f'<path d="M-20 34 Q0 24 20 34" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
    "worried": lambda: _eyes_open() + _brows_sad() + f'<path d="M-22 36 Q0 22 22 36" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
    "thirsty": lambda: _lid_eyes(droop=True) + _brows_sad()
               + f'<path d="M-26 22 Q0 30 26 22 Q22 44 0 44 Q-22 44 -26 22 Z" fill="{INK}"/>'
               + f'<path d="M-12 34 L12 34 L13 70 Q0 84 -13 70 Z" fill="#F07C8A" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
               + f'<path d="M0 38 L0 66" stroke="#C94F60" stroke-width="3"/>',
    "cry": lambda: _lid_eyes(droop=True) + _brows_sad()
           + f'<path d="M-26 22 Q0 30 26 22 Q22 44 0 44 Q-22 44 -26 22 Z" fill="{INK}"/>'
           + f'<path d="M-12 34 L12 34 L13 70 Q0 84 -13 70 Z" fill="#F07C8A" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
           + '<path d="M-30 4 Q-36 22 -32 40" stroke="#5BB8F0" stroke-width="7" fill="none" stroke-linecap="round"/>'
           + '<path d="M30 4 Q36 22 32 40" stroke="#5BB8F0" stroke-width="7" fill="none" stroke-linecap="round"/>',
    "shock": lambda: _eyes_open() + f'<ellipse cx="0" cy="34" rx="14" ry="18" fill="{INK}"/>',
    "drink": lambda: _arc_eyes(True),
    "out": lambda: f'<path d="M-36 -18 L-16 2 M-16 -18 L-36 2 M16 -18 L36 2 M36 -18 L16 2" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
           + f'<path d="M-20 34 Q0 24 20 34" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
}


def head(pid, faces, start_face):
    out = [f'<circle cx="0" cy="0" r="{HEAD_R}" fill="{WHITE}" {STROKE}/>']
    for f in faces:
        op = 1 if f == start_face else 0
        out.append(f'<g id="{pid}-f-{f}" opacity="{op}">{FACES[f]()}</g>')
    # sweat drops live on the head, hidden until shown
    out.append(f'<g id="{pid}-sweat" opacity="0">'
               f'<path d="M58 -40 Q66 -26 58 -18 Q50 -26 58 -40 Z" fill="#7CC8F5" stroke="{INK}" stroke-width="3"/>'
               f'<path d="M-62 -30 Q-55 -18 -62 -11 Q-69 -18 -62 -30 Z" fill="#7CC8F5" stroke="{INK}" stroke-width="3"/></g>')
    return out


# ---------------------------------------------------------------- character
def character(pid, x, y, shirt, scale=1.0, facing=1, pose=None, face="neutral",
              faces=("neutral", "smile"), hand_f="", hand_b="", behind="", back_arm_front=False):
    """pose: dict of start angles: thL thR shL shR arF faF arB faB torso head.
    hand_f / hand_b: SVG drawn at the front / back hand, in FOREARM space (hand at 0,0; forearm points down).
    back_arm_front: draw the back arm over the head/shirt (use when it lifts a cup/phone to the face).
    behind: SVG drawn behind the body in character space (e.g. an umbrella pole)."""
    p = dict(thL=8, thR=-8, shL=0, shR=0, arF=-12, faF=-10, arB=14, faB=-10, torso=0, head=0)
    p.update(pose or {})
    faces = list(dict.fromkeys(list(faces) + [face]))

    def leg(side, sign):
        shoe = (f'<ellipse cx="14" cy="{SHIN + 2}" rx="27" ry="13" fill="{INK}"/>')
        shin = rot(f"{pid}-sh{side}", p["sh" + side], limb(SHIN) + shoe)
        return at(sign * 10, -HIP, rot(f"{pid}-th{side}", p["th" + side], limb(THIGH) + at(0, THIGH, shin)))

    def arm(side, sx, prop):
        hand = f'<circle cx="0" cy="{FORE}" r="15" fill="{INK}"/>'
        fore = rot(f"{pid}-fa{side}", p["fa" + side], limb(FORE) + at(0, FORE, prop) + hand)
        return at(sx, SHOULDER_Y + HIP, rot(f"{pid}-ar{side}", p["ar" + side], limb(UPPER) + at(0, UPPER, fore)))

    shirt_path = (f'<path d="M-46 {SHOULDER_Y + HIP - 14} Q0 {SHOULDER_Y + HIP - 30} 46 {SHOULDER_Y + HIP - 14} '
                  f'L56 -6 Q0 8 -56 -6 Z" fill="{shirt}" {STROKE}/>'
                  f'<path d="M-46 {SHOULDER_Y + HIP - 14} L-68 {SHOULDER_Y + HIP + 40} L-40 {SHOULDER_Y + HIP + 52} Z" fill="{shirt}" {STROKE}/>'
                  f'<path d="M46 {SHOULDER_Y + HIP - 14} L68 {SHOULDER_Y + HIP + 40} L40 {SHOULDER_Y + HIP + 52} Z" fill="{shirt}" {STROKE}/>')
    neck = f'<line x1="0" y1="{SHOULDER_Y + HIP - 20}" x2="0" y2="{HEAD_Y + HIP + HEAD_R - 6}" stroke="{INK}" stroke-width="{LW}"/>'
    hd = at(0, HEAD_Y + HIP + 40, rot(f"{pid}-head", p["head"], at(0, -40, "".join(head(pid, faces, face)))))
    torso = rot(f"{pid}-torso", p["torso"],
                ("" if back_arm_front else arm("B", 22, hand_b)) + neck + shirt_path + hd
                + (arm("B", 22, hand_b) if back_arm_front else "") + arm("F", 34, hand_f))
    shadow = f'<ellipse cx="0" cy="4" rx="95" ry="14" fill="{INK}" opacity="0.18"/>'
    body = behind + leg("R", -1) + at(0, -HIP, torso) + leg("L", 1)
    return (f'<g transform="translate({x},{y}) scale({facing * scale},{scale})">{shadow}'
            f'<g id="{pid}" transform="translate(0,0) rotate(0)">{body}</g></g>')


# ---------------------------------------------------------------- props
def umbrella_up(cid, cx, top, w, color, rib="#00000033"):
    """Canopy upright (normal umbrella), centred at cx, apex at y=top. Character space."""
    h = w * 0.42
    base = top + h
    scallops = "".join(f' Q{cx - w / 2 + w / 8 * (2 * i + 1)} {base - 26} {cx - w / 2 + w / 4 * (i + 1)} {base}' for i in range(4))
    ribs = "".join(f'<path d="M{cx} {top} Q{cx - w / 2 + w / 4 * i - (w / 4 * i - w / 2) * 0.1} {top + h * 0.5} {cx - w / 2 + w / 4 * i} {base}" '
                   f'stroke="{rib}" stroke-width="4" fill="none"/>' for i in (1, 2, 3))
    return (f'<g id="{cid}"><path d="M{cx - w / 2} {base} Q{cx - w / 2} {top} {cx} {top} Q{cx + w / 2} {top} {cx + w / 2} {base}{scallops} Z" '
            f'fill="{color}" {STROKE}/>{ribs}<circle cx="{cx}" cy="{top - 8}" r="8" fill="{INK}"/></g>')


def umbrella_bowl(cid, cx, rim_y, w, color, water_id=None, tap=None):
    """Upside-down umbrella used as a bowl: rim (open side) at rim_y, belly hangs below.
    water_id: id of a water rect clipped to the bowl (animate attr y/height to fill).
    tap: (x, y) adds a metal tap under the belly at that point."""
    h = w * 0.36
    bottom = rim_y + h
    belly = f'M{cx - w / 2} {rim_y} Q{cx - w / 2 + 10} {bottom} {cx} {bottom} Q{cx + w / 2 - 10} {bottom} {cx + w / 2} {rim_y}'
    clip = f'<clipPath id="{cid}-clip"><path d="{belly} Z"/></clipPath>'
    water = ""
    if water_id:
        water = (f'<g clip-path="url(#{cid}-clip)"><rect id="{water_id}" x="{cx - w / 2}" y="{bottom}" width="{w}" height="{h + 4}" '
                 f'fill="#5DB7EE"/></g>')
    ribs = "".join(f'<path d="M{cx} {bottom} L{cx - w / 2 + w / 4 * i} {rim_y + (6 if i in (1, 3) else 0)}" stroke="#00000030" stroke-width="4"/>'
                   for i in (1, 2, 3))
    points = "".join(f'<circle cx="{cx - w / 2 + w / 4 * i}" cy="{rim_y}" r="6" fill="{INK}"/>' for i in range(5))
    rim = f'<ellipse cx="{cx}" cy="{rim_y}" rx="{w / 2}" ry="16" fill="{color}" {STROKE}/>'
    rim_inner = f'<ellipse id="{cid}-surf" cx="{cx}" cy="{rim_y + 1}" rx="{w / 2 - 12}" ry="9" fill="#3E8FD0" opacity="0"/>'
    tp = ""
    if tap:
        tx, ty = tap
        tp = (f'<g id="{cid}-tap"><rect x="{tx - 12}" y="{ty - 10}" width="24" height="30" rx="4" fill="#B8C0C8" {STROKE}/>'
              f'<path d="M{tx - 4} {ty + 18} L{tx - 4} {ty + 30} Q{tx - 4} {ty + 40} {tx + 6} {ty + 40} L{tx + 22} {ty + 40} L{tx + 22} {ty + 50}" '
              f'fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>'
              f'<path d="M{tx - 4} {ty + 18} L{tx - 4} {ty + 30} Q{tx - 4} {ty + 40} {tx + 6} {ty + 40} L{tx + 22} {ty + 40} L{tx + 22} {ty + 50}" '
              f'fill="none" stroke="#C9D1D8" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
              f'<rect x="{tx - 20}" y="{ty - 22}" width="40" height="12" rx="6" fill="#E04848" {STROKE}/></g>')
    return (f'<g id="{cid}">{clip}<path d="{belly} Z" fill="{color}" {STROKE}/>{water}{ribs}{tp}{rim}{rim_inner}{points}</g>')


def pole(x, y1, y2, hook=True):
    h = f' Q{x} {y2 + 30} {x - 22} {y2 + 30}' if hook else ""
    return (f'<path d="M{x} {y1} L{x} {y2}{h}" fill="none" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M{x} {y1} L{x} {y2}{h}" fill="none" stroke="#9AA3AC" stroke-width="5" stroke-linecap="round"/>')


def mug(mid, water_id=None, upright_rel=0):
    """Metal mug sitting on the hand (0,0) in forearm space. upright_rel = angle that makes it vertical
    when the forearm's total world angle is -upright_rel (e.g. 120 for a forearm at -120)."""
    water = ""
    if water_id:
        water = (f'<clipPath id="{mid}-clip"><rect x="-26" y="-66" width="52" height="56" rx="6"/></clipPath>'
                 f'<g clip-path="url(#{mid}-clip)"><rect id="{water_id}" x="-26" y="-10" width="52" height="0" fill="#5DB7EE"/></g>')
    return (f'<g transform="rotate({upright_rel})"><g id="{mid}">'
            f'<rect x="-30" y="-70" width="60" height="66" rx="8" fill="#AEB7C0" {STROKE}/>{water}'
            f'<path d="M30 -56 Q56 -56 56 -36 Q56 -18 30 -18" fill="none" stroke="{INK}" stroke-width="16"/>'
            f'<path d="M30 -56 Q56 -56 56 -36 Q56 -18 30 -18" fill="none" stroke="#AEB7C0" stroke-width="6"/>'
            f'<rect x="-22" y="-64" width="10" height="52" rx="4" fill="#fff" opacity="0.45"/></g></g>')


# ---------------------------------------------------------------- backgrounds (1080 x 1920)
W, H = 1080, 1920


def sky_rain(pid):
    return (f'<defs><linearGradient id="{pid}-sky" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#3B4656"/><stop offset="0.65" stop-color="#5F6E80"/><stop offset="1" stop-color="#6E7D8E"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#{pid}-sky)"/>')


def storm_clouds(pid, y=60, seed=3):
    rnd = random.Random(seed)
    blobs = []
    for row, (yy, col) in enumerate([(y, "#2B3340"), (y + 90, "#343D4B"), (y + 170, "#3D4756")]):
        x = -120 + row * 40
        while x < W + 120:
            r = rnd.uniform(90, 150)
            blobs.append(f'<circle cx="{x:.0f}" cy="{yy + rnd.uniform(-20, 20):.0f}" r="{r:.0f}" fill="{col}"/>')
            x += r * 1.2
    return f'<g id="{pid}-clouds">{"".join(blobs)}</g>'


def rain(pid, seed=7, n=260, period=320, top=-340, bottom=H + 40):
    """Rain drops on a vertical tile of `period` px; tween the group attr transform
    translate(0,0) -> translate(-60,period) with ease none and a finite repeat to loop seamlessly."""
    rnd = random.Random(seed)
    drops = []
    for _ in range(n):
        x = rnd.uniform(-40, W + 120)
        y0 = rnd.uniform(0, period)
        ln = rnd.uniform(34, 62)
        op = rnd.uniform(0.35, 0.8)
        y = top + y0
        while y < bottom:
            drops.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - ln * 0.18:.0f}" y2="{y + ln:.0f}" stroke="#C9DDF2" '
                         f'stroke-width="3" stroke-linecap="round" opacity="{op:.2f}"/>')
            y += period
    return f'<g id="{pid}-rain" transform="translate(0,0)">{"".join(drops)}</g>'


def wet_street(pid, ground_y, seed=5):
    rnd = random.Random(seed)
    out = [f'<rect x="0" y="{ground_y}" width="{W}" height="{H - ground_y}" fill="#59636F"/>',
           f'<rect x="0" y="{ground_y}" width="{W}" height="10" fill="#4A535E"/>']
    puddles = [(170, ground_y + 150, 130), (620, ground_y + 120, 160), (930, ground_y + 260, 120), (320, ground_y + 380, 180),
               (800, ground_y + 470, 150)]
    for i, (x, y, r) in enumerate(puddles):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.22:.0f}" fill="#8FB4D6" opacity="0.75"/>')
        out.append(f'<ellipse id="{pid}-rip{i}" cx="{x}" cy="{y}" rx="{r * 0.4:.0f}" ry="{r * 0.09:.0f}" fill="none" stroke="#DDEBF7" stroke-width="3" opacity="0"/>')
    for _ in range(40):
        x, y = rnd.uniform(0, W), rnd.uniform(ground_y + 40, H)
        out.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rnd.uniform(8, 20):.0f}" ry="3" fill="none" stroke="#9AA8B6" stroke-width="2" opacity="0.6"/>')
    return "".join(out)


def sky_sunny(pid):
    return (f'<defs><linearGradient id="{pid}-sky" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#4B9BE0"/><stop offset="0.7" stop-color="#9FD0F2"/><stop offset="1" stop-color="#CFE7F6"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#{pid}-sky)"/>')


def sun(sid, cx, cy, r=95):
    """Rays group <sid>-rays is centred on 0,0 inside a translate(cx,cy) so rotate() spins it in place."""
    rays = "".join(
        f'<path d="M{math.cos(math.radians(a)) * (r + 18):.0f} {math.sin(math.radians(a)) * (r + 18):.0f} '
        f'L{math.cos(math.radians(a + 6)) * (r + 70):.0f} {math.sin(math.radians(a + 6)) * (r + 70):.0f} '
        f'L{math.cos(math.radians(a + 12)) * (r + 18):.0f} {math.sin(math.radians(a + 12)) * (r + 18):.0f} Z" '
        f'fill="#FFC21A" stroke="#F29A00" stroke-width="3" stroke-linejoin="round"/>' for a in range(0, 360, 24))
    return (f'<g transform="translate({cx},{cy})"><g id="{sid}-rays" transform="rotate(0)">{rays}</g>'
            f'<circle cx="0" cy="0" r="{r}" fill="#FFE04A" stroke="#F29A00" stroke-width="6"/>'
            f'<circle cx="0" cy="0" r="{r - 22}" fill="#FFEA75"/></g>')


def cloud(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})" opacity="0.95">'
            '<ellipse cx="0" cy="0" rx="70" ry="30" fill="#fff"/><circle cx="-30" cy="-18" r="32" fill="#fff"/>'
            '<circle cx="18" cy="-26" r="38" fill="#fff"/><circle cx="52" cy="-6" r="26" fill="#fff"/></g>')


def desert(pid, ground_y, seed=9):
    rnd = random.Random(seed)
    out = [f'<path d="M0 {ground_y - 70} Q180 {ground_y - 150} 380 {ground_y - 80} Q560 {ground_y - 20} 760 {ground_y - 110} '
           f'Q930 {ground_y - 170} {W} {ground_y - 90} L{W} {ground_y} L0 {ground_y} Z" fill="#E2B37A"/>',
           f'<path d="M0 {ground_y - 30} Q260 {ground_y - 80} 520 {ground_y - 30} Q800 {ground_y + 10} {W} {ground_y - 40} L{W} {ground_y} L0 {ground_y} Z" fill="#D8A262"/>',
           f'<rect x="0" y="{ground_y}" width="{W}" height="{H - ground_y}" fill="#D99A55"/>']
    # cracked earth: Voronoi cells, squashed toward the horizon for perspective
    from scipy.spatial import Voronoi
    pts = []
    for _ in range(170):
        u, v = rnd.uniform(-0.1, 1.1), rnd.uniform(0, 1) ** 0.8
        pts.append((u * W, ground_y - 60 + v * (H - ground_y + 120)))
    vor = Voronoi(pts)
    for ri, reg in enumerate(vor.regions):
        if not reg or -1 in reg:
            continue
        poly = [vor.vertices[i] for i in reg]
        if any(y < ground_y - 400 or x < -300 or x > W + 300 for x, y in poly):
            continue
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        poly = [(cx + (x - cx) * 0.94, cy + (y - cy) * 0.94) for x, y in poly]   # gap = crack
        d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in poly) + " Z"
        shade = rnd.choice(["#E3AA68", "#DDA15E", "#E6B274"])
        out.append(f'<path d="{d}" fill="{shade}" stroke="#B9783E" stroke-width="2" stroke-linejoin="round"/>')
    out.insert(3, f'<rect x="0" y="{ground_y}" width="{W}" height="{H - ground_y}" fill="#A86A35"/>')
    out.insert(3, f'<clipPath id="{pid}-gclip"><rect x="0" y="{ground_y}" width="{W}" height="{H - ground_y}"/></clipPath><g clip-path="url(#{pid}-gclip)">')
    out.append('</g>')
    for _ in range(9):
        x, y = rnd.uniform(40, W - 40), rnd.uniform(ground_y + 30, H - 60)
        s = 0.6 + (y - ground_y) / (H - ground_y)
        out.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{22 * s:.0f}" ry="{12 * s:.0f}" fill="#8A7F78" stroke="{INK}" stroke-width="3"/>')
    return "".join(out)


def dead_tree(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M0 0 L4 -90 M4 -60 L-22 -96 M3 -78 L26 -110 M-10 -86 L-18 -112" '
            f'stroke="#6B4A33" stroke-width="7" stroke-linecap="round" fill="none"/></g>')
