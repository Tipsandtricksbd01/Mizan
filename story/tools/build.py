"""Writes index.html and compositions/s01..s14.html for the Bridgeville film.

Cue times are absolute seconds in the narration (see words.json); each scene converts them to its
own clock. Run: python3 tools/build.py   (from the project root)
"""

import json
import os
import random

from art import *  # noqa: F401,F403

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1920, 1080
TOTAL = 121.5

TEXT_CSS = """
  .t { position: absolute; left: 0; right: 0; text-align: center; font-family: "Archivo Black", sans-serif;
       color: #ffffff; -webkit-text-stroke: 12px #23202E; paint-order: stroke fill; line-height: 1.05;
       text-shadow: 0 8px 0 #23202E; }
  .t .g { color: #F2B134; }
  .t .r { color: #D7263D; }
"""

JS_HELPERS = """
const tl = gsap.timeline({ paused: true });
const BACK = "back.out(1.7)";
function pop(s, t, d = 0.45, o = "50% 100%") { tl.fromTo(s, { scale: 0, transformOrigin: o }, { scale: 1, duration: d, ease: BACK }, t); }
function popOut(s, t, d = 0.25, o = "50% 100%") { tl.fromTo(s, { scale: 1, transformOrigin: o }, { scale: 0, duration: d, ease: "power3.in", immediateRender: false }, t); }
function show(s, t) { tl.fromTo(s, { opacity: 0 }, { opacity: 1, duration: 0.01 }, t); }
function hide(s, t) { tl.fromTo(s, { opacity: 1 }, { opacity: 0, duration: 0.01, immediateRender: false }, t); }
function fin(s, t, d = 0.3) { tl.fromTo(s, { opacity: 0 }, { opacity: 1, duration: d, ease: "power2.out" }, t); }
function fout(s, t, d = 0.2) { tl.fromTo(s, { opacity: 1 }, { opacity: 0, duration: d, ease: "power3.in", immediateRender: false }, t); }
function txt(s, t) { tl.fromTo(s, { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, t); }
function txtOut(s, t) { tl.fromTo(s, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.16, ease: "power3.in", immediateRender: false }, t); }
function slam(s, t) {
  tl.fromTo(s, { scale: 2.4, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: 0.14, ease: "power4.in" }, t);
  tl.fromTo(s, { scaleX: 1, scaleY: 1 }, { scaleX: 1.07, scaleY: 0.9, duration: 0.05, yoyo: true, repeat: 1, ease: "power1.out", immediateRender: false }, t + 0.14);
}
function blink(s, t) { tl.fromTo(s, { scaleY: 1, transformOrigin: "50% 50%" }, { scaleY: 0.1, duration: 0.05, yoyo: true, repeat: 1, ease: "none", immediateRender: false }, t); }
function face(p, from, to, t) { tl.set("#" + p + "-m-" + from, { opacity: 0 }, t); tl.set("#" + p + "-m-" + to, { opacity: 1 }, t); }
function cam(s, t, d, to, ease = "power2.inOut") { tl.to(s, Object.assign({ duration: d, ease: ease }, to), t); }
function count(sel, t, d, from, to, fmt, ease = "power2.out") {
  const el = document.querySelector(sel); const o = { v: from };
  tl.fromTo(o, { v: from }, { v: to, duration: d, ease: ease, onUpdate: () => { el.textContent = fmt(o.v); } }, t);
}
const money = (v) => "$" + Math.round(v).toLocaleString("en-US");
"""


def focus(px, py, s):
    """Camera x,y (svgOrigin 960 540) that put world point (px,py) at the frame centre at scale s."""
    return round(-s * (px - 960), 1), round(-s * (py - 540), 1)


class Scene:
    def __init__(self, sid, start, end):
        self.id, self.start, self.end = sid, start, end
        self.svg, self.html, self.js, self.css = [], [], [], []

    def L(self, t):
        return round(max(0.0, t - self.start), 3)

    def text(self, tid, content, top, size=110, extra=""):
        self.html.append(f'<div id="{self.id}-{tid}" class="t" style="top:{top}px;font-size:{size}px;{extra}">{content}</div>')
        return f"#{self.id}-{tid}"

    def write(self):
        sid = self.id
        body = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
    #{sid}-svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
{TEXT_CSS.replace('.t', f'#{sid}-root-wrap .t')}
{''.join(self.css)}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
   <div id="{sid}-root-wrap" data-layout-allow-overflow data-layout-allow-overlap>
    <svg id="{sid}-svg" viewBox="0 0 {W} {H}" data-layout-allow-overflow data-layout-allow-occlusion>
      {''.join(self.svg)}
    </svg>
    {''.join(self.html)}
   </div>
  </div>
  <script>
{JS_HELPERS}
{chr(10).join(self.js)}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""
        with open(os.path.join(ROOT, "compositions", f"{sid}.html"), "w") as f:
            f.write(body)


def diorama(p, x_center, top_y, s):
    """The town as a slab of land sitting on a surface whose top edge is top_y."""
    clip = f'<clipPath id="{p}-dclip"><rect x="0" y="300" width="1920" height="740"/></clipPath>'
    slab = (f'<rect x="0" y="1036" width="1920" height="84" fill="#8E5B3A" stroke="{INK}" stroke-width="8"/>'
            f'<rect x="0" y="300" width="1920" height="820" fill="none"/>')
    tx = x_center - 960 * s
    ty = top_y - 1120 * s
    return (f'<g transform="translate({tx:.1f},{ty:.1f}) scale({s})"><g id="{p}-dio">{clip}'
            f'<g clip-path="url(#{p}-dclip)">{town(p, with_mailbox=False, edges=False)}</g>'
                        f'{slab}</g></g>')


# ---------------------------------------------------------------- scenes
def s01():
    sc = Scene("s01", 0.0, 7.95)
    sc.svg.append(sky("s01"))
    sc.svg.append('<g id="s01-cam">')
    sc.svg.append(f'<rect x="-400" y="900" width="2720" height="600" fill="#E2B072" stroke="{INK}" stroke-width="6"/>')
    screen_inner = (
        f'<text x="-500" y="-232" font-family="Archivo Black" font-size="46" fill="{INK}">ENTIRE TOWN · BRIDGEVILLE, CA</text>'
        f'<g id="s01-price"><text x="-500" y="-110" font-family="Archivo Black" font-size="104" fill="{INK}">$1.78 MILLION</text></g>'
        f'<text x="-500" y="-62" font-family="Inter" font-weight="700" font-size="34" fill="#5A5566">Auction ended · 1 winning bid</text>'
    )
    sc.svg.append(phone(900, 940, 1160, 340, iid="s01-phone", inner=screen_inner))
    sc.svg.append(diorama("s01t", 900, 600, 0.52))
    sc.svg.append(buyer("s01b", 1660, 980, 1.3))
    sc.svg.append(poof("s01poof", 1660, 760, 1.6))
    sc.svg.append(stamp("s01sold", "SOLD", 880, 400, 1.45))
    sc.svg.append("</g>")
    L = sc.L
    sc.js += [
        f'tl.set("#s01-cam", {{ svgOrigin: "960 540", x: 0, y: 0, scale: 1 }}, 0);',
        f'slam("#s01sold", {L(0.12)});',
        f'tl.fromTo("#s01b", {{ y: 0 }}, {{ y: -46, duration: 0.18, ease: "power2.out", yoyo: true, repeat: 1 }}, {L(0.32)});',
        f'face("s01b", "happy", "open", {L(0.3)}); face("s01b", "open", "happy", {L(0.75)});',
        f'tl.fromTo("#s01b-armL", {{ rotation: 0, svgOrigin: "-55 -200" }}, {{ rotation: 150, svgOrigin: "-55 -200", duration: 0.3, ease: BACK }}, {L(0.3)});',
        f'tl.fromTo("#s01b-armL", {{ rotation: 150, svgOrigin: "-55 -200" }}, {{ rotation: 0, svgOrigin: "-55 -200", duration: 0.35, ease: "power2.inOut", immediateRender: false }}, {L(1.6)});',
        f'blink("#s01b-eyes", {L(2.2)}); blink("#s01b-eyes", {L(4.4)});',
        f'tl.fromTo("#s01-price", {{ scale: 0.6, opacity: 0, transformOrigin: "0% 100%" }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: BACK }}, {L(3.66)});',
        # Then they vanished
        f'tl.fromTo("#s01b-eyes", {{ x: 0 }}, {{ x: -10, duration: 0.15, ease: "power2.out" }}, {L(5.85)});',
        f'tl.fromTo("#s01b", {{ scaleX: 1, scaleY: 1, transformOrigin: "50% 100%" }}, {{ scaleX: 1.25, scaleY: 0.7, duration: 0.12, ease: "power2.in", immediateRender: false }}, {L(6.52)});',
        f'tl.fromTo("#s01b", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.04, immediateRender: false }}, {L(6.72)});',
        f'tl.fromTo(".s01poof-p", {{ scale: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: 0.28, ease: "back.out(2.2)", stagger: 0.02 }}, {L(6.70)});',
        f'tl.fromTo(".s01poof-p", {{ opacity: 1, scale: 1 }}, {{ opacity: 0, scale: 1.5, duration: 0.45, ease: "power2.in", stagger: 0.03, immediateRender: false }}, {L(7.05)});',
        # Zoom into the town: the diorama becomes the world
        f'cam("#s01-cam", {L(7.5)}, 0.45, {{ scale: 3.4, x: {focus(900, 440, 3.4)[0]}, y: {focus(900, 440, 3.4)[1]} }}, "power3.in");',
    ]
    return sc


def s02():
    sc = Scene("s02", 7.95, 17.05)
    sc.svg.append(sky("s02", "#7FC4E8", "#FBE6C2"))
    sc.svg.append('<g id="s02-cam">')
    # clouds high above the valley
    for i, (x, y, s) in enumerate([(300, -380, 1.2), (1500, -460, 1.0), (980, -220, 0.8), (1700, -120, 0.7)]):
        sc.svg.append(f'<g transform="translate({x},{y}) scale({s})"><path d="M-120 0 A60 60 0 0 1 -40 -60 A80 80 0 0 1 100 -50 A55 55 0 0 1 140 0 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="5"/></g>')
    sc.svg.append(f'<path d="M-200 560 Q 300 380 760 520 T 1500 470 T 2200 520 V1400 H-200 Z" fill="#6FA86A" stroke="{INK}" stroke-width="4"/>')
    for i, xx in enumerate(range(-60, 2000, 70)):
        sc.svg.append(redwood(xx, 600 + (i % 3) * 14, 0.9 + (i % 4) * 0.1, RW2 if i % 2 else RW1))
    sc.svg.append(mist("s02-mist1", 560, 0.6))
    sc.svg.append(f'<path d="M-200 760 Q 960 680 2200 760 V1400 H-200 Z" fill="{MEADOW}" stroke="{INK}" stroke-width="4"/>')
    sc.svg.append(f'<path d="M-100 1080 C 500 900 1100 960 2100 820" fill="none" stroke="{INK}" stroke-width="72"/><path d="M-100 1080 C 500 900 1100 960 2100 820" fill="none" stroke="{ROAD}" stroke-width="62"/>'
                  f'<path d="M-100 1080 C 500 900 1100 960 2100 820" fill="none" stroke="{DASH}" stroke-width="6" stroke-dasharray="30 30"/>')
    for i, (x, y, s) in enumerate([(200, 820, 1.4), (1700, 800, 1.3), (420, 780, 1.0), (1500, 770, 1.0)]):
        sc.svg.append(redwood(x, y, s, RW1 if i % 2 else RW2))
    sc.svg.append(mist("s02-mist2", 760, 0.45))
    # Town sign
    sign = (f'<rect x="-14" y="-220" width="28" height="220" fill="#8E5B3A" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="-300" y="-340" width="600" height="170" rx="22" fill="#8E5B3A" stroke="{INK}" stroke-width="6"/>'
            f'<rect x="-282" y="-322" width="564" height="134" rx="14" fill="none" stroke="#F6E0B5" stroke-width="5"/>'
            f'<text x="0" y="-246" text-anchor="middle" font-family="Archivo Black" font-size="76" fill="#FFF6DF">BRIDGEVILLE</text>'
            f'<text x="0" y="-202" text-anchor="middle" font-family="Archivo Black" font-size="34" fill="#F2B134" letter-spacing="8">CALIFORNIA</text>')
    sc.svg.append(place(820, 1000, 1.0, "s02-sign", shadow(160, 0) + sign))
    hw = (f'<rect x="-10" y="-200" width="20" height="200" fill="#9AA0A6" stroke="{INK}" stroke-width="5"/>'
          f'<rect x="-220" y="-380" width="440" height="200" rx="18" fill="#1F6E43" stroke="{INK}" stroke-width="6"/>'
          f'<rect x="-206" y="-366" width="412" height="172" rx="12" fill="none" stroke="#FFFFFF" stroke-width="5"/>'
          f'<text x="0" y="-306" text-anchor="middle" font-family="Archivo Black" font-size="40" fill="#FFFFFF">SAN FRANCISCO</text>'
          f'<text x="-40" y="-226" text-anchor="middle" font-family="Archivo Black" font-size="64" fill="#FFFFFF">260 MI</text>'
          f'<path d="M120 -270 V-216 M96 -240 L120 -212 L144 -240" fill="none" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
    sc.svg.append(place(1480, 1000, 0.95, "s02-hw", hw))
    sc.svg.append(redwood(-40, 1300, 4.6, RW1) + redwood(1980, 1320, 4.4, RW2))
    sc.svg.append("</g>")
    t2002 = sc.text("year", "2002", 300, 240)
    L = sc.L
    sc.js += [
        f'tl.fromTo("#s02-cam", {{ svgOrigin: "960 540", y: 820, scale: 1.08 }}, {{ y: 820, scale: 1, duration: 0.5, ease: "power3.out" }}, 0);',
        f'txt("{t2002}", {L(8.41)});',
        f'txtOut("{t2002}", {L(9.75)});',
        f'cam("#s02-cam", {L(9.8)}, 1.5, {{ y: 0 }});',
        f'tl.fromTo("#s02-mist1", {{ x: -80 }}, {{ x: 120, duration: 9, ease: "none" }}, 0);',
        f'tl.fromTo("#s02-mist2", {{ x: 60 }}, {{ x: -140, duration: 9, ease: "none" }}, 0);',
        f'pop("#s02-sign", {L(10.7)}, 0.5);',
        f'pop("#s02-hw", {L(13.85)}, 0.5);',
        f'cam("#s02-cam", {L(16.6)}, 0.45, {{ scale: 1.25 }}, "power3.in");',
    ]
    return sc


def town_scene_bits(sc, p):
    sc.svg.append(sky(p))
    sc.svg.append(f'<g id="{p}-cam">')
    sc.svg.append(town(p))
    sc.svg.append("</g>")


def s03():
    sc = Scene("s03", 17.05, 23.45)
    town_scene_bits(sc, "s03")
    # boundary of the 82 acres, drawn over the land (inside the cam group: append before closing)
    sc.svg.insert(-1, f'<path id="s03-bound" d="M120 735 Q 960 650 1820 735 L1860 1050 Q 960 1010 70 1050 Z" fill="#FFFFFF" fill-opacity="0.12" stroke="#FFFFFF" stroke-width="10" stroke-dasharray="34 22" stroke-linejoin="round"/>')
    a = sc.text("acres", '<span class="g">82</span> ACRES', 110, 120)
    h = sc.text("houses", '<span class="g">10</span> HOUSES', 110, 120)
    c = sc.text("cabins", '<span class="g">4</span> CABINS', 110, 120)
    L = sc.L
    mx, my = focus(342, 870, 2.6)
    sc.js += [
        f'tl.fromTo("#s03-cam", {{ svgOrigin: "960 540", scale: 1.12, x: 0, y: 0 }}, {{ scale: 1, duration: 0.6, ease: "power3.out" }}, 0);',
        f'tl.set([{",".join(f"\"#s03-h{i}\"" for i in range(10))}, {",".join(f"\"#s03-c{i}\"" for i in range(4))}], {{ scale: 0, transformOrigin: "50% 100%" }}, 0);',
        f'tl.fromTo("#s03-bound", {{ opacity: 0, scale: 0.94, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: BACK }}, {L(17.24)});',
        f'txt("{a}", {L(17.3)}); txtOut("{a}", {L(18.45)});',
        f'fout("#s03-bound", {L(18.5)}, 0.25);',
    ]
    for i in range(10):
        sc.js.append(f'pop("#s03-h{i}", {L(18.63 + 0.06 * i)}, 0.4);')
    sc.js.append(f'txt("{h}", {L(18.66)}); txtOut("{h}", {L(19.6)});')
    for i in range(4):
        sc.js.append(f'pop("#s03-c{i}", {L(19.77 + 0.08 * i)}, 0.4);')
    sc.js += [
        f'txt("{c}", {L(19.8)}); txtOut("{c}", {L(21.0)});',
        f'cam("#s03-cam", {L(21.2)}, 1.0, {{ scale: 2.6, x: {mx}, y: {my} }});',
        f'tl.fromTo("#s03-mail", {{ rotation: 0, transformOrigin: "50% 100%" }}, {{ rotation: -4, duration: 0.12, yoyo: true, repeat: 1, ease: "power1.inOut" }}, {L(22.4)});',
    ]
    return sc


def s04():
    sc = Scene("s04", 23.45, 32.85)
    sc.svg.append(sky("s04"))
    sc.svg.append('<g id="s04-a">')
    sc.svg.append(f'<path d="M-100 760 Q 960 700 2020 760 V1200 H-100 Z" fill="{MEADOW}" stroke="{INK}" stroke-width="4"/>')
    sc.svg.append(redwood(140, 770, 1.6, RW1) + redwood(1800, 760, 1.5, RW2) + redwood(1620, 760, 1.1, RW1))
    sc.svg.append(house(1300, 900, 2.6, "#F2B134", "#6B2E2E"))
    sc.svg.append(for_sale_sign("s04-sign", 420, 1010, 1.3))
    sc.svg.append(owners("s04o", 820, 1030, 1.3))
    tumble = "".join(f'<circle cx="0" cy="0" r="{r}" fill="none" stroke="#B08A55" stroke-width="7" stroke-dasharray="{d}"/>' for r, d in [(70, "40 18"), (52, "30 14"), (34, "20 12"), (18, "12 8")])
    sc.svg.append(place(2150, 990, 1.0, "s04-tw", f'<g id="s04-twspin">{tumble}<circle r="72" fill="none" stroke="{INK}" stroke-width="3" opacity="0.3"/></g>'))
    sc.svg.append("</g>")
    # Online marketplace
    sc.svg.append('<g id="s04-b">')
    sc.svg.append(f'<rect x="0" y="0" width="1920" height="1080" fill="#F3EDE0"/>')
    sc.svg.append(''.join(f'<rect x="{x}" y="{y}" width="300" height="380" rx="24" fill="#E6DECD"/>' for x in (40, 1580) for y in (60, 600)))
    mower_photo = f'<rect x="-200" y="-560" width="400" height="320" fill="#BFE3B0"/>' + lawnmower(-20, -290, 1.0)
    card_photo = f'<rect x="-200" y="-560" width="400" height="320" fill="#9AD4F0"/>' + baseball_card(0, -268, 1.2)
    sc.svg.append(listing_card("s04-mow", 410, 930, 0.92, title="USED MOWER", sub="$40 · runs ok", photo=mower_photo, w=400, h=560))
    sc.svg.append(listing_card("s04-bb", 1510, 930, 0.92, title="BASEBALL CARDS", sub="$12 · lot of 30", photo=card_photo, w=400, h=560))
    town_photo = f'<g transform="translate(-300,-660) scale(0.32)">{town("s04t", with_mailbox=False, edges=False)}</g>'
    sc.svg.append(listing_card("s04-town", 960, 1000, 1.18, title="ENTIRE TOWN", sub="Bridgeville, CA · 82 acres", photo=town_photo, w=560, h=700))
    sc.svg.append("</g>")
    L = sc.L
    sc.js += [
        f'pop("#s04-sign", {L(23.6)}, 0.5);',
        f'tl.fromTo("#s04o-b-armR", {{ rotation: 0, svgOrigin: "55 -200" }}, {{ rotation: -140, svgOrigin: "55 -200", duration: 0.3, ease: BACK }}, {L(24.3)});',
        f'tl.fromTo("#s04o-b-armR", {{ rotation: -140, svgOrigin: "55 -200" }}, {{ rotation: -110, svgOrigin: "55 -200", duration: 0.2, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }}, {L(24.6)});',
        f'tl.fromTo("#s04o-a-armL", {{ rotation: 0, svgOrigin: "-55 -200" }}, {{ rotation: 120, svgOrigin: "-55 -200", duration: 0.3, ease: BACK }}, {L(24.45)});',
        f'blink("#s04o-a-eyes", {L(25.3)}); blink("#s04o-b-eyes", {L(25.5)});',
        f'tl.fromTo("#s04-tw", {{ x: 0 }}, {{ x: -2500, duration: 2.6, ease: "none" }}, {L(25.9)});',
        f'tl.fromTo("#s04-twspin", {{ rotation: 0, transformOrigin: "50% 50%" }}, {{ rotation: -900, duration: 2.6, ease: "none" }}, {L(25.9)});',
        f'tl.fromTo("#s04-tw", {{ y: 0 }}, {{ y: -40, duration: 0.32, yoyo: true, repeat: 7, ease: "power1.out" }}, {L(25.9)});',
        f'face("s04o-a", "happy", "sad", {L(26.6)}); face("s04o-b", "happy", "sad", {L(26.7)});',
        f'tl.fromTo("#s04o-b-armR", {{ rotation: -140, svgOrigin: "55 -200" }}, {{ rotation: 0, svgOrigin: "55 -200", duration: 0.35, ease: "power2.inOut", immediateRender: false }}, {L(26.55)});',
        f'tl.fromTo("#s04o-a-armL", {{ rotation: 120, svgOrigin: "-55 -200" }}, {{ rotation: 0, svgOrigin: "-55 -200", duration: 0.35, ease: "power2.inOut", immediateRender: false }}, {L(26.6)});',
        # whip to the marketplace
        f'tl.fromTo("#s04-a", {{ x: 0 }}, {{ x: -1920, duration: 0.3, ease: "power3.in", immediateRender: false }}, {L(27.6)});',
        f'tl.fromTo("#s04-b", {{ x: 1920 }}, {{ x: 0, duration: 0.3, ease: "power3.out" }}, {L(27.9)});',
        f'tl.set(["#s04-mow", "#s04-bb"], {{ scale: 0, transformOrigin: "50% 100%" }}, 0);',
        f'tl.fromTo("#s04-town", {{ scale: 0.5, transformOrigin: "50% 100%" }}, {{ scale: 1, duration: 0.5, ease: BACK }}, {L(28.7)});',
        f'tl.fromTo("#s04-town", {{ y: 0 }}, {{ y: -20, duration: 1.1, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }}, {L(29.3)});',
        f'pop("#s04-mow", {L(30.62)}, 0.45);',
        f'pop("#s04-bb", {L(31.55)}, 0.45);',
    ]
    return sc


def s05():
    sc = Scene("s05", 32.85, 38.85)
    sc.svg.append(f'<rect x="0" y="0" width="1920" height="1080" fill="#F3EDE0"/>')
    sc.svg.append('<g id="s05-a">')
    town_photo = f'<g transform="translate(-300,-660) scale(0.32)">{town("s05t", with_mailbox=False, edges=False)}</g>'
    price = (f'<text x="-246" y="-96" font-family="Inter" font-weight="700" font-size="34" fill="#5A5566">Current bid</text>'
             f'<g id="s05-price"><text x="-246" y="-26" font-family="Archivo Black" font-size="66" fill="{INK}">$5,000</text></g>')
    sc.svg.append(listing_card("s05-card", 760, 1000, 1.18, title="ENTIRE TOWN", sub="Bridgeville, CA · 82 acres", photo=town_photo + "", w=560, h=700))
    sc.svg.append(f'<g transform="translate(760,1000) scale(1.18)">{price}</g>')
    sc.svg.append(bid_button("s05-bid", 1440, 640, 1.4))
    sc.svg.append("</g>")
    sc.svg.append('<g id="s05-b">')
    globe = (f'<circle cx="0" cy="0" r="360" fill="#4E8FD1" stroke="{INK}" stroke-width="8"/>'
             f'<path d="M-250 -190 Q-150 -260 -60 -200 Q-20 -120 -110 -60 Q-200 -20 -230 -100 Z" fill="#7BC67E" stroke="{INK}" stroke-width="6"/>'
             f'<path d="M40 -250 Q160 -280 240 -180 Q260 -80 180 -40 Q100 -90 60 -150 Z" fill="#7BC67E" stroke="{INK}" stroke-width="6"/>'
             f'<path d="M-120 40 Q-40 20 -20 120 Q-60 250 -130 220 Q-170 120 -120 40 Z" fill="#7BC67E" stroke="{INK}" stroke-width="6"/>'
             f'<path d="M80 60 Q200 40 260 120 Q230 230 140 200 Q80 140 80 60 Z" fill="#7BC67E" stroke="{INK}" stroke-width="6"/>')
    sc.svg.append(place(960, 600, 1.0, "s05-globe", globe))
    spots = [(-180, -150), (150, -170), (-90, 120), (190, 110), (-260, 10), (40, -40), (250, -20), (-30, 260)]
    for i, (x, y) in enumerate(spots):
        bub = (f'<path d="M0 0 L-14 -30 H-46 A20 20 0 0 1 -66 -50 V-110 A20 20 0 0 1 -46 -130 H46 A20 20 0 0 1 66 -110 V-50 A20 20 0 0 1 46 -30 H14 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="6"/>'
               f'<text x="0" y="-58" text-anchor="middle" font-family="Archivo Black" font-size="66" fill="{RED}">!</text>')
        sc.svg.append(place(960 + x, 600 + y, 0.9, f"s05-ping{i}", bub))
    sc.svg.append("</g>")
    L = sc.L
    sc.js += [
        f'tl.fromTo("#s05-a", {{ scale: 1.12, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: 0.5, ease: "power3.out" }}, 0);',
        f'pop("#s05-bid", {L(33.1)}, 0.45, "50% 50%");',
        f'tl.fromTo("#s05-price", {{ scale: 0.5, opacity: 0, transformOrigin: "0% 100%" }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: BACK }}, {L(34.05)});',
        f'tl.fromTo("#s05-bid-top", {{ y: 0 }}, {{ y: 8, duration: 0.06, yoyo: true, repeat: 1 }}, {L(35.0)});',
        f'tl.fromTo("#s05-a", {{ scale: 1 }}, {{ scale: 0.12, duration: 0.45, ease: "power3.in", immediateRender: false }}, {L(36.15)});',
        f'hide("#s05-a", {L(36.62)});',
        f'tl.fromTo("#s05-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, {L(36.55)});',
        f'tl.fromTo("#s05-globe", {{ scale: 0.12, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: 0.55, ease: BACK }}, {L(36.55)});',
        f'tl.fromTo("#s05-globe", {{ rotation: -4 }}, {{ rotation: 4, duration: 2.3, ease: "none" }}, {L(36.55)});',
    ]
    for i in range(len(spots)):
        sc.js.append(f'pop("#s05-ping{i}", {L(36.95 + 0.17 * i)}, 0.35);')
    return sc


def s06():
    sc = Scene("s06", 38.85, 47.9)
    sc.svg.append(sky("s06"))
    # A: highway
    sc.svg.append('<g id="s06-a">')
    sc.svg.append(f'<path d="M-100 640 Q 600 540 1200 620 T 2100 600 V1200 H-100 Z" fill="{HILL}" stroke="{INK}" stroke-width="4"/>')
    for i, xx in enumerate(range(-40, 2000, 90)):
        sc.svg.append(redwood(xx, 700 + (i % 2) * 10, 1.0 + (i % 3) * 0.12, RW1 if i % 2 else RW2))
    sc.svg.append(f'<rect x="-100" y="780" width="2120" height="240" fill="{ROAD}" stroke="{INK}" stroke-width="6"/>'
                  f'<line x1="-100" y1="900" x2="2020" y2="900" stroke="{DASH}" stroke-width="10" stroke-dasharray="70 50"/>')
    for i, (col, lab, y) in enumerate([("#E4572E", "NEWS 7", 900), ("#4E8FD1", "TV 24", 1000), ("#F2B134", "LIVE", 880)]):
        sc.svg.append(van(f"s06-van{i}", -500, y, 1.25 if i != 2 else 1.0, col, lab))
    sc.svg.append("</g>")
    # B: phones ringing
    sc.svg.append('<g id="s06-b">')
    sc.svg.append(f'<rect x="0" y="0" width="1920" height="1080" fill="#F6D9A8"/>')

    def deskphone(pid, x, y, s, col):
        body = (shadow(170, 4) + f'<path d="M-170 0 L-130 -150 H130 L170 0 Z" fill="{col}" stroke="{INK}" stroke-width="6"/>'
                f'<circle cx="0" cy="-75" r="44" fill="#FFFDF7" stroke="{INK}" stroke-width="5"/>'
                f'<g id="{pid}-hs"><path d="M-190 -170 Q-200 -230 -150 -235 H150 Q200 -230 190 -170 L150 -160 Q140 -190 100 -195 H-100 Q-140 -190 -150 -160 Z" fill="{col}" stroke="{INK}" stroke-width="6"/></g>')
        return place(x, y, s, pid, body)
    sc.svg.append(deskphone("s06-ph0", 620, 820, 1.5, "#E4572E") + deskphone("s06-ph1", 1340, 760, 1.2, "#4E8FD1"))
    sc.svg.append("</g>")
    ring0 = sc.text("ring0", "RING!", 250, 96, "left:380px;right:auto;transform:rotate(-8deg);")
    ring1 = sc.text("ring1", "RING!", 210, 80, "left:1220px;right:auto;transform:rotate(7deg);")
    # C: lost with a map
    sc.svg.append('<g id="s06-c">')
    sc.svg.append(f'<rect x="0" y="0" width="1920" height="1080" fill="#BFE3B0"/>')
    sc.svg.append(person("s06p", 960, 1040, 1.65, shirt="#F2B134", hair="#3B2A20"))
    mp = (f'<rect x="-230" y="-170" width="460" height="300" fill="#F6F1E3" stroke="{INK}" stroke-width="6"/>'
          f'<line x1="-77" y1="-170" x2="-77" y2="130" stroke="{INK}" stroke-width="3" opacity="0.4"/><line x1="77" y1="-170" x2="77" y2="130" stroke="{INK}" stroke-width="3" opacity="0.4"/>'
          f'<g transform="rotate(180)"><path d="M-140 -110 L-60 -120 L60 40 L50 110 L-120 30 Z" fill="#9BCB6E" stroke="{INK}" stroke-width="5"/>'
          f'<text x="0" y="-130" text-anchor="middle" font-family="Archivo Black" font-size="40" fill="{INK}">MAP</text></g>')
    sc.svg.append(place(960, 560, 1.15, "s06-map", mp))
    sc.svg.append("</g>")
    q = sc.text("q", "?", 70, 200, "left:1250px;right:auto;")
    # D: cursor storm
    sc.svg.append('<g id="s06-d">')
    sc.svg.append(f'<rect x="0" y="0" width="1920" height="1080" fill="#F3EDE0"/>')
    sc.svg.append(bid_button("s06-bid", 960, 560, 2.2))
    tick = (f'<rect x="-230" y="-110" width="460" height="220" rx="16" fill="#F2B134" stroke="{INK}" stroke-width="6"/>'
            f'<line x1="120" y1="-110" x2="120" y2="110" stroke="{INK}" stroke-width="4" stroke-dasharray="14 10"/>'
            f'<text x="-50" y="-30" text-anchor="middle" font-family="Archivo Black" font-size="44" fill="{INK}">ADMIT ONE</text>'
            f'<text x="-50" y="30" text-anchor="middle" font-family="Inter" font-weight="700" font-size="30" fill="{INK}">last ticket on Earth</text>'
            f'<text x="175" y="16" text-anchor="middle" font-family="Archivo Black" font-size="40" fill="{RED}">★</text>')
    sc.svg.append(place(960, 900, 1.0, "s06-tick", tick))
    rng = random.Random(7)
    cursors = []
    for i in range(26):
        ang = i / 26 * 6.283 + rng.uniform(-0.1, 0.1)
        import math
        r0 = 1250
        tx, ty = 960 + math.cos(ang) * rng.uniform(250, 420), 560 + math.sin(ang) * rng.uniform(150, 260)
        sx, sy = 960 + math.cos(ang) * r0, 560 + math.sin(ang) * r0
        cursors.append((round(sx - tx), round(sy - ty)))
        sc.svg.append(cursor(f"s06-cur{i}", round(tx), round(ty), 1.2))
    sc.svg.append("</g>")
    L = sc.L
    sc.js += [
        f'show("#s06-a", 0); hide("#s06-a", {L(40.5)});',
        f'tl.set(["#s06-b", "#s06-c", "#s06-d"], {{ opacity: 0 }}, 0);',
        f'tl.set("{ring0}", {{ opacity: 0 }}, 0); tl.set("{ring1}", {{ opacity: 0 }}, 0); tl.set("{q}", {{ opacity: 0 }}, 0);',
    ]
    for i, t0 in enumerate([39.05, 39.4, 39.75]):
        sc.js.append(f'tl.fromTo("#s06-van{i}", {{ x: 0 }}, {{ x: 2900, duration: 1.15, ease: "power1.inOut" }}, {L(t0)});')
        sc.js.append(f'tl.fromTo("#s06-van{i}", {{ y: 0 }}, {{ y: -6, duration: 0.08, yoyo: true, repeat: 13, ease: "none" }}, {L(t0)});')
    sc.js += [
        f'show("#s06-b", {L(40.5)}); hide("#s06-b", {L(42.15)});',
        f'tl.fromTo("#s06-ph0-hs", {{ y: 0, rotation: 0, transformOrigin: "50% 100%" }}, {{ y: -26, rotation: -6, duration: 0.07, yoyo: true, repeat: 13, ease: "none" }}, {L(40.6)});',
        f'tl.fromTo("#s06-ph1-hs", {{ y: 0, rotation: 0, transformOrigin: "50% 100%" }}, {{ y: -22, rotation: 6, duration: 0.07, yoyo: true, repeat: 11, ease: "none" }}, {L(40.95)});',
        f'tl.fromTo("{ring0}", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: BACK }}, {L(40.6)});',
        f'tl.fromTo("{ring1}", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: BACK }}, {L(40.95)});',
        f'hide("{ring0}", {L(42.15)}); hide("{ring1}", {L(42.15)});',
        f'show("#s06-c", {L(42.15)}); hide("#s06-c", {L(44.4)});',
        f'tl.fromTo("#s06-map", {{ y: 0 }}, {{ y: -10, rotation: 3, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {L(42.2)});',
        f'tl.fromTo("#s06p-head", {{ rotation: 0, svgOrigin: "0 -214" }}, {{ rotation: -12, svgOrigin: "0 -214", duration: 0.4, ease: "power2.out" }}, {L(43.0)});',
        f'tl.fromTo("{q}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: BACK }}, {L(43.3)});',
        f'hide("{q}", {L(44.4)});',
        f'show("#s06-d", {L(44.4)});',
        f'tl.set("#s06-tick", {{ scale: 0, transformOrigin: "50% 50%" }}, 0);',
    ]
    for i, (dx, dy) in enumerate(cursors):
        t0 = 44.45 + 0.04 * i
        sc.js.append(f'tl.fromTo("#s06-cur{i}", {{ x: {dx}, y: {dy} }}, {{ x: 0, y: 0, duration: 0.35, ease: "power3.out" }}, {L(t0)});')
        sc.js.append(f'tl.fromTo("#s06-cur{i}", {{ scale: 1, transformOrigin: "0% 0%" }}, {{ scale: 0.8, duration: 0.06, yoyo: true, repeat: 5, ease: "none", immediateRender: false }}, {L(t0 + 0.4)});')
    sc.js += [
        f'tl.fromTo("#s06-bid-top", {{ y: 0 }}, {{ y: 8, duration: 0.06, yoyo: true, repeat: 23, ease: "none" }}, {L(44.9)});',
        f'tl.fromTo("#s06-tick", {{ scale: 0, rotation: -30, transformOrigin: "50% 50%" }}, {{ scale: 1, rotation: -6, duration: 0.45, ease: BACK }}, {L(46.1)});',
    ]
    return sc


def s07():
    sc = Scene("s07", 47.9, 62.85)
    sc.svg.append(f'<rect x="0" y="0" width="1920" height="1080" fill="#F3EDE0"/>')
    town_photo = f'<g transform="translate(-300,-660) scale(0.32)">{town("s07t", with_mailbox=False, edges=False)}</g>'
    sc.svg.append(listing_card("s07-card", 520, 990, 1.12, title="ENTIRE TOWN", sub="Bridgeville, CA · 82 acres", photo=town_photo, w=560, h=700))
    sc.svg.append(calendar("s07-cal", 1340, 640, 1.3, "DAYS", ""))
    sc.svg.append(stamp("s07-sold", "SOLD", 520, 520, 1.5))
    sc.html.append('<div id="s07-days" class="t" style="top:395px;left:1145px;right:auto;width:390px;font-size:140px;color:#23202E;-webkit-text-stroke:0;text-shadow:none;">1</div>')
    bids_lbl = sc.text("bidl", "ALMOST", 160, 56, "left:1000px;right:auto;width:700px;")
    bids = sc.text("bids", "0 BIDS", 240, 150, "left:900px;right:auto;width:900px;")
    clock = sc.text("clock", "00:00:03", 400, 170, "left:900px;right:auto;width:900px;")
    clock_lbl = sc.text("clockl", "AUCTION ENDS IN", 300, 56, "left:900px;right:auto;width:900px;")
    price = sc.text("price", "$0", 340, 140, "left:900px;right:auto;width:960px;color:#F2B134;")
    dbl = sc.text("dbl", 'MORE THAN <span class="g">2×</span><br>THE ASKING PRICE', 600, 76, "left:880px;right:auto;width:1000px;")
    L = sc.L
    sc.js += [
        f'tl.fromTo("#s07-card", {{ scale: 0.12, x: 440, y: -440, transformOrigin: "50% 100%" }}, {{ scale: 1, x: 0, y: 0, duration: 0.6, ease: "power3.out" }}, 0);',
        f'pop("#s07-cal", {L(48.2)}, 0.45); tl.set("#s07-days", {{ opacity: 0 }}, 0); show("#s07-days", {L(48.35)});',
        f'count("#s07-days", {L(48.45)}, 0.8, 1, 30, (v) => String(Math.round(v)), "power1.inOut");',
        f'popOut("#s07-cal", {L(49.45)}, 0.2); hide("#s07-days", {L(49.5)});',
        f'txt("{bids_lbl}", {L(49.6)}); txt("{bids}", {L(49.62)});',
        f'count("{bids}", {L(49.65)}, 1.8, 0, 250, (v) => Math.round(v) + " BIDS", "power2.out");',
        f'txtOut("{bids_lbl}", {L(52.3)}); txtOut("{bids}", {L(52.3)});',
        f'txt("{clock_lbl}", {L(52.5)}); txt("{clock}", {L(52.5)});',
        f'tl.set("{clock}", {{ textContent: "00:00:02" }}, {L(52.75)}); tl.set("{clock}", {{ textContent: "00:00:01" }}, {L(53.0)});',
        f'tl.set("{clock}", {{ textContent: "00:00:00", color: "#D7263D" }}, {L(53.2)});',
        f'tl.fromTo("{clock}", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.08, yoyo: true, repeat: 1 }}, {L(53.2)});',
        f'txtOut("{clock_lbl}", {L(54.6)}); txtOut("{clock}", {L(54.6)});',
        f'txt("{price}", {L(54.95)});',
        f'count("{price}", {L(55.15)}, 4.45, 0, 1777877, money, "power1.inOut");',
        f'tl.set("{price}", {{ textContent: "$1,777,877" }}, {L(59.62)});',
        f'tl.fromTo("{price}", {{ scale: 1 }}, {{ scale: 1.1, duration: 0.08, yoyo: true, repeat: 1 }}, {L(59.62)});',
        f'slam("#s07-sold", {L(59.7)});',
        f'txt("{dbl}", {L(60.85)});',
    ]
    return sc


def driveway(p, with_outline=True):
    out = [sky(p), f'<g id="{p}-cam">',
           f'<path d="M-100 700 Q 960 650 2020 700 V1300 H-100 Z" fill="{MEADOW}" stroke="{INK}" stroke-width="4"/>',
           redwood(1700, 720, 1.5, RW1), redwood(1840, 720, 1.2, RW2), redwood(80, 700, 1.3, RW2),
           house(520, 820, 2.3, "#4E8FD1", "#3C3A4D"),
           f'<path d="M820 820 L1180 820 L1500 1100 L700 1100 Z" fill="#B9B3BF" stroke="{INK}" stroke-width="5"/>',
           mailbox(1560, 980, 1.3, iid=f"{p}-mail")]
    if with_outline:
        out.append(place(1010, 990, 1.35, f"{p}-ghost",
                         f'<path d="M-48 0 V-90 H48 V0 M-48 -80 V-190 A48 48 0 0 1 48 -190 V-80 M0 -214 m-52 0 a52 52 0 1 0 104 0 a52 52 0 1 0 -104 0" fill="none" stroke="{INK}" stroke-width="5" stroke-dasharray="16 12" opacity="0.55"/>'))
    out.append('<path d="M0 0 Q20 -20 40 0 Q20 12 0 0 Z" fill="#C77D3A" transform="translate(1150,960) rotate(20) scale(1.4)"/>')
    out.append("</g>")
    return "".join(out)


def s08():
    sc = Scene("s08", 62.85, 70.3)
    sc.svg.append('<g id="s08-a">')
    sc.svg.append(sky("s08a"))
    sc.svg.append(f'<path d="M-100 760 Q 960 700 2020 760 V1200 H-100 Z" fill="{MEADOW}" stroke="{INK}" stroke-width="4"/>')
    sc.svg.append(redwood(160, 770, 1.6, RW1) + redwood(1760, 770, 1.6, RW2))
    sc.svg.append(owners("s08o", 960, 1020, 1.55))
    rng = random.Random(3)
    conf = []
    for i in range(46):
        x, y = rng.uniform(80, 1840), rng.uniform(-300, -40)
        col = rng.choice(["#E4572E", "#F2B134", "#4E8FD1", "#7BC67E", "#F49AC2"])
        conf.append(f'<rect class="s08-conf" x="{x:.0f}" y="{y:.0f}" width="18" height="30" fill="{col}" stroke="{INK}" stroke-width="3"/>')
    sc.svg.append("".join(conf))
    heads = [("s08-n0", 470, 560, -10, "TOWN SOLD ON EBAY!"), ("s08-n1", 1460, 520, 8, "$1.77M FOR A TOWN"), ("s08-n2", 980, 820, -3, "BRIDGEVILLE SOLD!")]
    for nid, x, y, rot, hl in heads:
        sc.svg.append(newspaper(nid, x, y, 1.15, hl, rot))
    sc.svg.append("</g>")
    sc.svg.append('<g id="s08-b">' + driveway("s08b") + "</g>")
    L = sc.L
    sc.js += [
        f'show("#s08-a", 0); hide("#s08-a", {L(67.33)}); tl.set("#s08-b", {{ opacity: 0 }}, 0); show("#s08-b", {L(67.33)});',
        f'face("s08o-a", "happy", "open", {L(63.9)}); face("s08o-b", "happy", "open", {L(63.95)});',
        f'tl.fromTo("#s08o-a-armL", {{ rotation: 0, svgOrigin: "-55 -200" }}, {{ rotation: 160, svgOrigin: "-55 -200", duration: 0.3, ease: BACK }}, {L(63.85)});',
        f'tl.fromTo("#s08o-a-armR", {{ rotation: 0, svgOrigin: "55 -200" }}, {{ rotation: -160, svgOrigin: "55 -200", duration: 0.3, ease: BACK }}, {L(63.9)});',
        f'tl.fromTo("#s08o-b-armL", {{ rotation: 0, svgOrigin: "-55 -200" }}, {{ rotation: 150, svgOrigin: "-55 -200", duration: 0.3, ease: BACK }}, {L(63.95)});',
        f'tl.fromTo("#s08o-b-armR", {{ rotation: 0, svgOrigin: "55 -200" }}, {{ rotation: -150, svgOrigin: "55 -200", duration: 0.3, ease: BACK }}, {L(64.0)});',
        f'tl.fromTo("#s08o-a", {{ y: 0 }}, {{ y: -70, duration: 0.22, yoyo: true, repeat: 5, ease: "power2.out" }}, {L(63.96)});',
        f'tl.fromTo("#s08o-b", {{ y: 0 }}, {{ y: -60, duration: 0.24, yoyo: true, repeat: 5, ease: "power2.out" }}, {L(64.06)});',
        f'tl.fromTo(".s08-conf", {{ y: 0, rotation: 0, transformOrigin: "50% 50%" }}, {{ y: 1350, rotation: 540, duration: 2.6, ease: "power1.in", stagger: 0.02 }}, {L(63.96)});',
    ]
    for i, t0 in enumerate([65.12, 65.42, 65.72]):
        sc.js.append(f'tl.fromTo("#s08-n{i}", {{ scale: 0, rotation: -540, transformOrigin: "50% 50%" }}, {{ scale: 1, rotation: 0, duration: 0.45, ease: "power3.out" }}, {L(t0)});')
    sc.js += [
        f'tl.fromTo("#s08b-cam", {{ svgOrigin: "960 540", scale: 1, x: 0, y: 0 }}, {{ scale: 1.32, x: {focus(1040, 860, 1.32)[0]}, y: {focus(1040, 860, 1.32)[1]}, duration: 2.8, ease: "power1.inOut" }}, {L(67.45)});',
        f'tl.fromTo("#s08b-ghost", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "power2.out" }}, {L(68.3)});',
    ]
    return sc


def s09():
    sc = Scene("s09", 70.3, 79.05)
    sc.svg.append('<g id="s09-a">')
    sc.svg.append(f'<rect x="0" y="0" width="1920" height="1080" fill="#F3EDE0"/>')
    sc.svg.append(bid_button("s09-bid", 960, 560, 2.6))
    sc.svg.append(cursor("s09-cur", 1010, 590, 2.4))
    sc.svg.append("</g>")
    sc.svg.append('<g id="s09-b">')
    sc.svg.append(sky("s09b"))
    sc.svg.append(f'<path d="M-100 720 Q 960 680 2020 720 V1200 H-100 Z" fill="{MEADOW}" stroke="{INK}" stroke-width="4"/>')
    sc.svg.append(redwood(140, 740, 1.5, RW1) + redwood(1800, 730, 1.4, RW2))
    table = (f'<rect x="-330" y="-180" width="660" height="40" fill="#C99A62" stroke="{INK}" stroke-width="6"/>'
             f'<rect x="-300" y="-140" width="24" height="140" fill="#8E5B3A" stroke="{INK}" stroke-width="5"/><rect x="276" y="-140" width="24" height="140" fill="#8E5B3A" stroke="{INK}" stroke-width="5"/>'
             f'<path d="M-250 -180 V-300 H-200 V-180 Z M-290 -300 L-160 -300 L-200 -370 L-250 -370 Z" fill="#F49AC2" stroke="{INK}" stroke-width="5"/>'
             f'<rect x="-100" y="-290" width="170" height="110" fill="#E9C98B" stroke="{INK}" stroke-width="5"/>'
             f'<text x="-15" y="-226" text-anchor="middle" font-family="Archivo Black" font-size="28" fill="{INK}">TOASTER</text>'
             f'<path d="M150 -180 Q120 -250 170 -300 Q220 -250 190 -180 Z" fill="#7BC67E" stroke="{INK}" stroke-width="5"/>')
    sc.svg.append(place(640, 1000, 1.25, "s09-table", table))
    ys = (f'<rect x="-10" y="-200" width="20" height="200" fill="#8E5B3A" stroke="{INK}" stroke-width="5"/>'
          f'<path d="M-170 -330 L170 -320 L160 -190 L-160 -200 Z" fill="#E9C98B" stroke="{INK}" stroke-width="6"/>'
          f'<text x="0" y="-240" text-anchor="middle" font-family="Archivo Black" font-size="56" fill="{RED}" transform="rotate(2)">YARD SALE</text>')
    sc.svg.append(place(280, 1010, 1.1, None, ys))
    sc.svg.append(buyer("s09p", 1380, 1020, 1.6))
    bub = (f'<path d="M0 0 L40 -60 H-220 A40 40 0 0 1 -260 -100 V-230 A40 40 0 0 1 -220 -270 H260 A40 40 0 0 1 300 -230 V-100 A40 40 0 0 1 260 -60 H90 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="7"/>'
           f'<text x="20" y="-140" text-anchor="middle" font-family="Archivo Black" font-size="72" fill="{INK}">I\'LL TAKE IT!</text>')
    sc.svg.append(place(1270, 520, 1.15, "s09-bub", bub))
    wallet = (f'<g id="s09-wal"><rect x="-70" y="-50" width="140" height="100" rx="14" fill="#6B4A3A" stroke="{INK}" stroke-width="6"/>'
              f'<rect x="-60" y="-40" width="120" height="30" rx="8" fill="#4A3328"/></g>')
    sc.svg.append(place(1500, 830, 1.2, "s09-wallet", wallet))
    moth = (f'<g id="s09-mothw"><path d="M0 0 Q-40 -40 -60 -6 Q-40 20 0 0 Z M0 0 Q40 -40 60 -6 Q40 20 0 0 Z" fill="#D8CDB8" stroke="{INK}" stroke-width="4"/></g>'
            f'<ellipse cx="0" cy="0" rx="8" ry="20" fill="#8C7B66" stroke="{INK}" stroke-width="4"/>')
    sc.svg.append(place(1500, 790, 1.1, "s09-moth", moth))
    sc.svg.append("</g>")
    easy = sc.text("easy", "EASY TO SAY.", 70, 104, "left:0;right:auto;width:1100px;")
    hard = sc.text("hard", 'MUCH HARDER<br>TO <span class="g">PAY.</span>', 60, 104, "left:0;right:auto;width:1100px;")
    L = sc.L
    sc.js += [
        f'show("#s09-a", 0); hide("#s09-a", {L(72.6)}); tl.set("#s09-b", {{ opacity: 0 }}, 0); show("#s09-b", {L(72.6)});',
        f'tl.fromTo("#s09-cur", {{ x: 700, y: 520 }}, {{ x: 0, y: 0, duration: 0.6, ease: "power3.out" }}, {L(70.85)});',
        f'tl.fromTo("#s09-cur", {{ scale: 1, transformOrigin: "0% 0%" }}, {{ scale: 0.85, duration: 0.06, yoyo: true, repeat: 1, immediateRender: false }}, {L(71.55)});',
        f'tl.fromTo("#s09-bid-top", {{ y: 0 }}, {{ y: 8, duration: 0.06, yoyo: true, repeat: 1 }}, {L(71.55)});',
        f'tl.set(["#s09-bub", "#s09-wallet", "#s09-moth"], {{ scale: 0, transformOrigin: "50% 100%" }}, 0);',
        f'tl.fromTo("#s09p-armR", {{ rotation: 0, svgOrigin: "55 -200" }}, {{ rotation: -120, svgOrigin: "55 -200", duration: 0.3, ease: BACK }}, {L(73.45)});',
        f'tl.fromTo("#s09p-bag", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.01 }}, 0);',
        f'face("s09p", "happy", "open", {L(73.6)});',
        f'tl.fromTo("#s09p", {{ scaleY: 1, transformOrigin: "50% 100%" }}, {{ scaleY: 1.06, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }}, {L(73.6)});',
        f'pop("#s09-bub", {L(73.62)}, 0.4, "40% 100%");',
        f'face("s09p", "open", "happy", {L(75.1)});',
        f'txt("{easy}", {L(75.9)}); txtOut("{easy}", {L(77.05)});',
        f'popOut("#s09-bub", {L(76.95)}, 0.2, "40% 100%");',
        f'tl.fromTo("#s09p-armR", {{ rotation: -120, svgOrigin: "55 -200" }}, {{ rotation: -60, svgOrigin: "55 -200", duration: 0.3, ease: "power2.inOut", immediateRender: false }}, {L(77.1)});',
        f'pop("#s09-wallet", {L(77.2)}, 0.35, "50% 50%");',
        f'txt("{hard}", {L(77.66)});',
        f'tl.fromTo("#s09-wal", {{ scaleY: 1, transformOrigin: "50% 100%" }}, {{ scaleY: 1.35, duration: 0.2, ease: BACK }}, {L(77.7)});',
        f'tl.fromTo("#s09-moth", {{ scale: 0, x: 0, y: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: 0.2, ease: BACK }}, {L(77.85)});',
        f'tl.fromTo("#s09-moth", {{ x: 0, y: 0 }}, {{ x: 220, y: -560, duration: 1.1, ease: "power1.inOut", immediateRender: false }}, {L(78.0)});',
        f'tl.fromTo("#s09-mothw", {{ scaleY: 1, transformOrigin: "50% 50%" }}, {{ scaleY: 0.3, duration: 0.07, yoyo: true, repeat: 15, ease: "none" }}, {L(77.9)});',
        f'face("s09p", "happy", "sad", {L(78.0)});',
    ]
    return sc


def s10():
    sc = Scene("s10", 79.05, 86.85)
    sc.svg.append(driveway("s10", with_outline=True))
    sc.svg.insert(-1, owners("s10o", 1250, 1060, 1.25))
    sc.svg.append(f'<rect id="s10-night" x="0" y="0" width="1920" height="1080" fill="#1B2440" opacity="0"/>')
    sc.svg.append(place(1500, 220, 1.0, "s10-moon", f'<circle r="80" fill="#FFF2B0" stroke="{INK}" stroke-width="6"/><circle cx="34" cy="-20" r="70" fill="#1B2440" opacity="0.0"/>'))
    moth = (f'<g id="s10-mothw"><path d="M0 0 Q-40 -40 -60 -6 Q-40 20 0 0 Z M0 0 Q40 -40 60 -6 Q40 20 0 0 Z" fill="#D8CDB8" stroke="{INK}" stroke-width="4"/></g>'
            f'<ellipse cx="0" cy="0" rx="8" ry="20" fill="#8C7B66" stroke="{INK}" stroke-width="4"/>')
    sc.svg.append(place(1575, 760, 1.2, "s10-moth", moth))
    sc.svg.append(calendar("s10-cal", 960, 760, 1.5, "ONE YEAR LATER", "2003"))
    L = sc.L
    sc.js += [
        f'tl.fromTo("#s10-cam", {{ svgOrigin: "960 540", scale: 1.15, x: {focus(1040, 860, 1.15)[0]}, y: {focus(1040, 860, 1.15)[1]} }}, {{ scale: 1, x: 0, y: 0, duration: 1.2, ease: "power2.inOut" }}, 0);',
        f'tl.fromTo("#s10-night", {{ opacity: 0 }}, {{ opacity: 0.6, duration: 0.6, ease: "power2.inOut" }}, {L(80.4)});',
        f'tl.set("#s10-moon", {{ scale: 0, transformOrigin: "50% 50%" }}, 0); pop("#s10-moon", {L(80.7)}, 0.4, "50% 50%");',
        f'blink("#s10o-a-eyes", {L(81.2)}); blink("#s10o-b-eyes", {L(81.5)});',
        f'tl.set("#s10-moth", {{ scale: 0, transformOrigin: "50% 50%" }}, 0);',
        f'tl.fromTo("#s10-mail", {{ rotation: 0, transformOrigin: "50% 100%" }}, {{ rotation: 5, duration: 0.1, yoyo: true, repeat: 1 }}, {L(82.0)});',
        f'tl.fromTo("#s10-moth", {{ scale: 0 }}, {{ scale: 1, duration: 0.2, ease: BACK }}, {L(82.4)});',
        f'tl.fromTo("#s10-moth", {{ x: 0, y: 0 }}, {{ x: -380, y: -520, duration: 1.0, ease: "power1.inOut", immediateRender: false }}, {L(82.55)});',
        f'tl.fromTo("#s10-mothw", {{ scaleY: 1, transformOrigin: "50% 50%" }}, {{ scaleY: 0.3, duration: 0.07, yoyo: true, repeat: 13, ease: "none" }}, {L(82.4)});',
        f'tl.fromTo("#s10-night", {{ opacity: 0.6 }}, {{ opacity: 0, duration: 0.4, ease: "power2.inOut", immediateRender: false }}, {L(83.5)});',
        f'popOut("#s10-moon", {L(83.5)}, 0.2, "50% 50%");',
        f'tl.set("#s10-cal", {{ scale: 0, transformOrigin: "50% 100%" }}, 0); pop("#s10-cal", {L(83.66)}, 0.45);',
        f'popOut("#s10-cal", {L(85.15)}, 0.2);',
        f'face("s10o-a", "happy", "sad", {L(85.4)}); face("s10o-b", "happy", "sad", {L(85.5)});',
        f'tl.fromTo(["#s10o-a-head", "#s10o-b-head"], {{ y: 0 }}, {{ y: 14, duration: 0.4, ease: "power2.inOut", stagger: 0.1 }}, {L(85.45)});',
        f'tl.fromTo("#s10-ghost", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.6, ease: "power2.in", immediateRender: false }}, {L(85.9)});',
    ]
    return sc


def s11():
    sc = Scene("s11", 86.85, 93.6)
    sc.svg.append(sky("s11"))
    sc.svg.append('<g id="s11-cam">' + town("s11", with_mailbox=False) + "</g>")
    sc.svg.append(stamp("s11-sold", "SOLD", 960, 720, 1.4, small="FOR REAL"))
    yr = sc.text("yr", "2004", 70, 200)
    old = sc.text("old", "$1,777,877", 70, 150)
    strike = '<div id="s11-strike" style="position:absolute;left:560px;top:150px;width:800px;height:22px;background:#D7263D;border:5px solid #23202E;border-radius:6px;"></div>'
    sc.html.append(strike)
    less = sc.text("less", 'ABOUT <span class="g">$1 MILLION</span> LESS', 270, 84)
    L = sc.L
    sc.js += [
        f'tl.fromTo("#s11-cam", {{ svgOrigin: "960 540", scale: 1.2, y: 120 }}, {{ scale: 1.05, y: 120, duration: 1.0, ease: "power3.out" }}, 0);',
        f'txt("{yr}", {L(87.14)}); txtOut("{yr}", {L(88.4)});',
        f'tl.set("#s11-sold", {{ opacity: 0 }}, 0); slam("#s11-sold", {L(88.55)});',
        f'tl.fromTo("#s11-sold", {{ scale: 1 }}, {{ scale: 0.7, x: 0, y: 160, duration: 0.5, ease: "power2.inOut", immediateRender: false }}, {L(91.1)});',
        f'txt("{old}", {L(91.3)});',
        f'tl.fromTo("#s11-strike", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.3, ease: "power3.out" }}, {L(91.75)});',
        f'txt("{less}", {L(92.15)});',
    ]
    return sc


def s12():
    sc = Scene("s12", 93.6, 99.95)
    sc.svg.append(sky("s12", "#FFD58A", "#F7A55A"))
    rays = "".join(f'<path d="M0 0 L{1600 * __import__("math").cos(a / 18 * 3.14159):.0f} {1600 * __import__("math").sin(a / 18 * 3.14159):.0f} L{1600 * __import__("math").cos((a + 0.5) / 18 * 3.14159):.0f} {1600 * __import__("math").sin((a + 0.5) / 18 * 3.14159):.0f} Z" fill="#FFE7B0" opacity="0.55"/>' for a in range(0, 36, 1))
    sc.svg.append(f'<g transform="translate(1300,300)"><g id="s12-rays">{rays}</g></g>')
    sc.svg.append(f'<circle cx="1300" cy="300" r="130" fill="#FFF1C9" stroke="{INK}" stroke-width="6"/>')
    sc.svg.append(f'<path d="M-100 800 Q 960 740 2020 800 V1200 H-100 Z" fill="#B7C96A" stroke="{INK}" stroke-width="4"/>')
    sc.svg.append(cabin(1520, 820, 1.8) + redwood(1780, 820, 1.5, RW1) + redwood(120, 830, 1.6, RW2))
    sign = (f'<rect x="-12" y="-260" width="24" height="260" fill="#8E5B3A" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="-250" y="-400" width="500" height="170" rx="20" fill="#C99A62" stroke="{INK}" stroke-width="6"/>'
            f'<text x="0" y="-330" text-anchor="middle" font-family="Archivo Black" font-size="44" fill="{INK}">PEACEFUL</text>'
            f'<text x="0" y="-268" text-anchor="middle" font-family="Archivo Black" font-size="44" fill="{INK}">HEALTH RETREAT</text>')
    sc.svg.append(place(420, 1010, 1.1, "s12-sign", sign))
    sc.svg.append(person("s12p", 960, 1030, 1.5, shirt="#FFFDF7", hair="#B0B0B0", pants="#E9E2D0"))
    sc.svg.append(f'<rect id="s12-grey" x="0" y="0" width="1920" height="1080" fill="#6B6F78" opacity="0"/>')
    rng = random.Random(11)
    bills = []
    for i in range(22):
        x = 960 + rng.uniform(-260, 260)
        y = 1040 - rng.uniform(0, 420) * (1 - abs(x - 960) / 420)
        bills.append((x, y))
        sc.svg.append(bill(f"s12-bill{i}", round(x), round(y), 1.0, rng.uniform(-35, 35), rng.choice(["$4,200", "$12,900", "$800", "$31,000", "$6,450"])))
    sc.svg.append(place(1020, 640, 1.3, "s12-hand", f'<rect x="-14" y="-90" width="28" height="90" rx="12" fill="#FFFDF7" stroke="{INK}" stroke-width="5"/><circle cx="0" cy="-100" r="22" fill="#F1C27D" stroke="{INK}" stroke-width="5"/>'))
    L = sc.L
    sc.js += [
        f'tl.fromTo("#s12-rays", {{ rotation: 0, svgOrigin: "0 0" }}, {{ rotation: 20, svgOrigin: "0 0", duration: 6.4, ease: "none" }}, 0);',
        f'tl.fromTo("#s12p-eyes", {{ scaleY: 1, transformOrigin: "50% 50%" }}, {{ scaleY: 0.15, duration: 0.2 }}, {L(94.2)});',
        f'tl.fromTo("#s12p-armL", {{ rotation: 0, svgOrigin: "-55 -200" }}, {{ rotation: 100, svgOrigin: "-55 -200", duration: 0.5, ease: "power2.out" }}, {L(94.5)});',
        f'tl.fromTo("#s12p-armR", {{ rotation: 0, svgOrigin: "55 -200" }}, {{ rotation: -100, svgOrigin: "55 -200", duration: 0.5, ease: "power2.out" }}, {L(94.55)});',
        f'tl.set("#s12-sign", {{ scale: 0, transformOrigin: "50% 100%" }}, 0); pop("#s12-sign", {L(94.65)}, 0.5);',
        f'tl.fromTo("#s12-grey", {{ opacity: 0 }}, {{ opacity: 0.35, duration: 0.4, ease: "power2.inOut" }}, {L(97.55)});',
        f'tl.fromTo("#s12p-eyes", {{ scaleY: 0.15 }}, {{ scaleY: 1.5, duration: 0.15, ease: BACK, immediateRender: false }}, {L(98.3)});',
        f'face("s12p", "happy", "open", {L(98.32)});',
        f'tl.fromTo("#s12p-armL", {{ rotation: 100, svgOrigin: "-55 -200" }}, {{ rotation: 170, svgOrigin: "-55 -200", duration: 0.25, ease: BACK, immediateRender: false }}, {L(98.4)});',
        f'tl.fromTo("#s12p-armR", {{ rotation: -100, svgOrigin: "55 -200" }}, {{ rotation: -170, svgOrigin: "55 -200", duration: 0.25, ease: BACK, immediateRender: false }}, {L(98.4)});',
        f'tl.set("#s12-hand", {{ opacity: 0 }}, 0);',
    ]
    for i in range(len(bills)):
        sc.js.append(f'tl.fromTo("#s12-bill{i}", {{ y: -1300, opacity: 1 }}, {{ y: 0, duration: 0.5, ease: "power2.in" }}, {L(98.55 + 0.045 * i)});')
    sc.js.append(f'show("#s12-hand", {L(99.6)}); tl.fromTo("#s12-hand", {{ rotation: -10, svgOrigin: "0 0" }}, {{ rotation: 10, svgOrigin: "0 0", duration: 0.12, yoyo: true, repeat: 1 }}, {L(99.6)});')
    return sc


def s13():
    sc = Scene("s13", 99.95, 108.9)
    sc.svg.append(sky("s13"))
    sc.svg.append(f'<rect x="-400" y="900" width="2720" height="600" fill="#E2B072" stroke="{INK}" stroke-width="6"/>')
    inner = (f'<text x="-500" y="-232" font-family="Archivo Black" font-size="46" fill="{INK}">ENTIRE TOWN · BRIDGEVILLE, CA</text>'
             f'<g id="s13-back"><text x="-500" y="-120" font-family="Archivo Black" font-size="96" fill="{RED}">BACK ON SALE</text></g>'
             f'<g id="s13-price"><text x="-500" y="-120" font-family="Archivo Black" font-size="96" fill="{INK}">$1.78 MILLION?</text></g>'
             f'<text x="-500" y="-62" font-family="Inter" font-weight="700" font-size="34" fill="#5A5566">Relisted · 0 bids</text>')
    sc.svg.append(phone(900, 940, 1160, 340, inner=inner))
    sc.svg.append(diorama("s13t", 900, 600, 0.52))
    sc.svg.append(stamp("s13sold", "SOLD", 880, 400, 1.45))
    two = sc.text("two", "TWO YEARS LATER", 60, 96)
    L = sc.L
    sc.js += [
        f'tl.fromTo("#s13t-dio", {{ y: -900 }}, {{ y: 0, duration: 0.55, ease: "power3.out" }}, 0);',
        f'txt("{two}", {L(100.15)}); txtOut("{two}", {L(101.2)});',
        f'tl.set("#s13-price", {{ opacity: 0 }}, 0);',
        f'tl.fromTo("#s13-back", {{ scale: 0.4, opacity: 0, transformOrigin: "0% 100%" }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: BACK }}, {L(102.45)});',
        f'tl.set("#s13sold", {{ opacity: 0 }}, 0); slam("#s13sold", {L(104.45)});',
        f'hide("#s13-back", {L(105.8)}); tl.fromTo("#s13-price", {{ scale: 0.4, opacity: 0, transformOrigin: "0% 100%" }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: BACK, immediateRender: false }}, {L(105.8)});',
        f'tl.fromTo("#s13sold", {{ rotation: 0, transformOrigin: "100% 100%" }}, {{ rotation: 14, duration: 0.35, ease: "power2.out", immediateRender: false }}, {L(107.3)});',
        f'tl.fromTo("#s13sold", {{ y: 0 }}, {{ y: 1100, rotation: 60, duration: 0.6, ease: "power2.in", immediateRender: false }}, {L(107.7)});',
    ]
    return sc


def s14():
    sc = Scene("s14", 108.9, TOTAL)
    town_scene_bits(sc, "s14")
    sc.svg.insert(-1, for_sale_sign("s14-sign", 960, 930, 1.55, "FOR SALE"))
    sc.svg.insert(-1, place(960, 930, 1.0, "s14-dust", "".join(f'<circle class="s14-d" cx="{x}" cy="{y}" r="{r}" fill="#EFE6D6" stroke="{INK}" stroke-width="4"/>' for x, y, r in [(-220, -10, 34), (-150, 6, 26), (160, 4, 30), (230, -12, 24)])))
    yrs = sc.text("yrs", '<span class="g">20+</span> YEARS LATER', 90, 120)
    mkt = sc.text("mkt", "BACK ON THE MARKET", 90, 110)
    money = sc.text("money", 'JUST THIS TIME… <span class="g">BRING THE MONEY.</span>', 70, 84)
    L = sc.L
    mx, my = focus(342, 870, 2.6)
    sc.js += [
        f'tl.fromTo("#s14-cam", {{ svgOrigin: "960 540", scale: 1.2, x: 0, y: 0 }}, {{ scale: 1.05, duration: 1.4, ease: "power3.out" }}, 0);',
        f'txt("{yrs}", {L(110.2)}); txtOut("{yrs}", {L(111.55)});',
        f'txt("{mkt}", {L(111.75)}); txtOut("{mkt}", {L(113.2)});',
        f'cam("#s14-cam", {L(113.35)}, 1.2, {{ scale: 2.6, x: {mx}, y: {my} }});',
        f'tl.fromTo("#s14-mail", {{ rotation: 0, transformOrigin: "50% 100%" }}, {{ rotation: -4, duration: 0.12, yoyo: true, repeat: 1, ease: "power1.inOut" }}, {L(115.25)});',
        f'cam("#s14-cam", {L(116.0)}, 2.4, {{ scale: 0.92, x: 0, y: 30 }});',
        f'tl.set("#s14-sign", {{ y: -1400 }}, 0);',
        f'tl.fromTo("#s14-sign", {{ y: -1400 }}, {{ y: 0, duration: 0.42, ease: "power3.in", immediateRender: false }}, {L(118.71)});',
        f'tl.fromTo("#s14-sign", {{ scaleX: 1, scaleY: 1, transformOrigin: "50% 100%" }}, {{ scaleX: 1.08, scaleY: 0.88, duration: 0.07, yoyo: true, repeat: 1, ease: "power1.out", immediateRender: false }}, {L(119.13)});',
        f'tl.fromTo(".s14-d", {{ scale: 0, opacity: 1, transformOrigin: "50% 50%" }}, {{ scale: 1.4, duration: 0.3, ease: "power2.out" }}, {L(119.13)});',
        f'tl.fromTo(".s14-d", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.4, ease: "power2.in", immediateRender: false }}, {L(119.5)});',
        f'txt("{money}", {L(117.45)});',
    ]
    return sc


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14]


def write_index(scenes):
    hosts = "\n".join(
        f'      <div id="{s.id}" data-composition-id="{s.id}" data-composition-src="compositions/{s.id}.html" '
        f'data-start="{s.start}" data-duration="{round(s.end - s.start, 3)}" data-track-index="1" data-track-kind="graphics" '
        f'data-width="{W}" data-height="{H}"></div>'
        for s in scenes
    )
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #9AD4F0; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
{hosts}
      <audio id="voice" class="clip" src="assets/voice/narration.wav" data-start="0" data-duration="119.719" data-track-index="2" data-volume="1"></audio>
      <audio id="music" class="clip" src="assets/music/music.wav" data-start="0" data-duration="{TOTAL}" data-track-index="3" data-volume="1"></audio>
      <audio id="sfx" class="clip" src="assets/sfx/sfx.wav" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(html)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    built = []
    for fn in SCENES:
        sc = fn()
        sc.write()
        built.append(sc)
    for a, b in zip(built, built[1:]):
        assert abs(a.end - b.start) < 1e-6, (a.id, b.id)
    write_index(built)
    print("wrote", len(built), "scenes")
