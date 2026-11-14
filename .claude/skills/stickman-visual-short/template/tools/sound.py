"""Synthesizes assets/sfx.wav and assets/music.wav from tools/cues.json (written by build.py).

No downloads, no AI: every sound is made with numpy/scipy. Add a new effect = add a function
to SOUNDS and use its name in build.py's cue(). Run:  python3 tools/sound.py
"""

import json
import math
import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
rng = np.random.default_rng(7)


def t_(sec):
    return np.arange(int(sec * SR)) / SR


def env(n, a=0.005, r=0.1, shape=2.0):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr) ** shape
    return e


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


# ------------------------------------------------------------------ effects
def rain(dur):
    x = bp(noise(dur), 1500, 9000) * 0.5 + lp(noise(dur), 500) * 0.4
    drops = np.zeros_like(x)
    for _ in range(int(dur * 70)):
        i = rng.integers(0, len(x) - 2000)
        drops[i:i + 400] += rng.uniform(0.3, 1) * np.exp(-np.arange(400) / 60) * rng.standard_normal(400)
    x = x + hp(drops, 2500) * 0.8
    return norm(x * env(len(x), 0.05, 0.25, 1), 0.55)


def thunder(_d):
    n = noise(2.4)
    x = lp(n, 160, 4) * np.exp(-t_(2.4) / 0.7) + lp(n, 900) * np.exp(-t_(2.4) / 0.15) * 0.4
    return norm(x * env(len(x), 0.04, 0.6), 0.9)


def vowel(f0, dur, formants=((800, 1200), (1150, 1500)), vib=6, glide=0.0):
    t = t_(dur)
    f = f0 * (1 + glide * t / dur) * (1 + 0.02 * np.sin(2 * math.pi * vib * t))
    ph = 2 * math.pi * np.cumsum(f) / SR
    saw = sum(np.sin(k * ph) / k for k in range(1, 30))
    out = sum(bp(saw, lo, hi) for lo, hi in formants)
    return out


def laugh(_d):
    """'ha-ha-ha-ha' : breathy voiced bursts with falling pitch."""
    parts = []
    for k in range(5):
        f0 = 260 - k * 14
        v = vowel(f0, 0.13, ((650, 1100), (1100, 1700))) + bp(noise(0.13), 1200, 4000) * 0.25
        parts.append(v * env(len(v), 0.012, 0.06))
        parts.append(np.zeros(int(0.05 * SR)))
    return norm(np.concatenate(parts), 0.75)


def whoosh(_d):
    d = 0.45
    n = noise(d)
    t = t_(d)
    cutoff = 300 + 5000 * np.sin(math.pi * t / d) ** 2
    out = np.zeros_like(n)
    for i in range(0, len(n), 512):  # sweeping band
        c = cutoff[i]
        out[i:i + 512] = bp(n[max(0, i - 2048):i + 512], max(100, c * 0.5), min(20000, c * 1.6))[-len(n[i:i + 512]):]
    return norm(out * np.sin(math.pi * t / d) ** 2, 0.7)


def desert(dur):
    wind = lp(noise(dur), 400) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.17 * t_(dur)))
    t = t_(dur)
    cic = np.sin(2 * math.pi * 4800 * t) * (0.5 + 0.5 * np.sign(np.sin(2 * math.pi * 38 * t))) * (0.5 + 0.5 * np.sin(2 * math.pi * 0.6 * t))
    return norm(wind * 0.8 + cic * 0.06, 0.35) * env(int(dur * SR), 0.3, 0.5, 1)


def pour(_d):
    d = 1.2
    t = t_(d)
    x = bp(noise(d), 600, 3500) * (0.7 + 0.3 * np.sin(2 * math.pi * 13 * t))
    # rising pitch "glug" as the mug fills
    x += np.sin(2 * math.pi * np.cumsum(300 + 500 * t / d) / SR) * 0.15 * (rng.random(len(t)) > 0.6)
    return norm(x * env(len(x), 0.04, 0.2), 0.55)


def gulp(_d):
    d = 0.16
    t = t_(d)
    f = 180 + 260 * np.exp(-t / 0.03)
    x = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t / 0.05)
    return norm(lp(x, 900), 0.8)


def ahh(_d):
    v = vowel(190, 0.7, ((700, 1100), (1100, 1500)), glide=-0.25) + bp(noise(0.7), 900, 3000) * 0.15
    return norm(v * env(len(v), 0.05, 0.35), 0.6)


def whimper(_d):
    parts = []
    for k in range(3):
        v = vowel(420 - k * 30, 0.32, ((500, 900), (1500, 2200)), vib=9, glide=-0.3)
        parts += [v * env(len(v), 0.03, 0.15), np.zeros(int(0.18 * SR))]
    return norm(np.concatenate(parts), 0.5)


def thud(_d, small=False):
    d = 0.5
    t = t_(d)
    x = np.sin(2 * math.pi * np.cumsum(90 * np.exp(-t / 0.15) + 45) / SR) * np.exp(-t / 0.12)
    x += lp(noise(d), 1200) * np.exp(-t / 0.04) * 0.6
    return norm(x, 0.6 if small else 1.0)


def thud_small(d):
    return thud(d, small=True)


def trombone(_d):
    """'wah wah wah waaah' : brass-like sawtooth through a wah filter, falling notes."""
    out = []
    for i, (m, d) in enumerate([(58, 0.36), (57, 0.36), (56, 0.36), (55, 1.1)]):
        f0 = 440 * 2 ** ((m - 69) / 12)
        t = t_(d)
        vib = 1 + (0.03 * np.sin(2 * math.pi * 5.5 * t) * (t > 0.3) if i == 3 else 0 * t)
        ph = 2 * math.pi * np.cumsum(f0 * vib) / SR
        saw = sum(np.sin(k * ph) / k for k in range(1, 25))
        wah = np.zeros_like(saw)
        cut = 500 + 1800 * np.sin(math.pi * np.minimum(t / 0.3, 1)) ** 2
        for j in range(0, len(saw), 480):
            seg = saw[max(0, j - 1920):j + 480]
            wah[j:j + 480] = lp(seg, cut[j])[-len(saw[j:j + 480]):]
        out.append(wah * env(len(wah), 0.03, 0.12 if i < 3 else 0.5))
    return norm(np.concatenate(out), 0.7)


SOUNDS = dict(rain=rain, thunder=thunder, laugh=laugh, whoosh=whoosh, desert=desert, pour=pour, gulp=gulp,
              ahh=ahh, whimper=whimper, thud=thud, thud_small=thud_small, trombone=trombone)
LOOPS = {"rain", "desert"}   # these fill until the next shot cut / end


# ------------------------------------------------------------------ music
def pluck(f, d, bright=0.5):
    """Karplus-Strong pizzicato."""
    n = int(d * SR)
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * (0.994 + 0.004 * bright)
    return out * env(n, 0.002, 0.05)


def music(total, bpm, changes):
    beat = 60 / bpm
    stop = next((t for t, k in changes if k == "stop"), total)
    swap = next((t for t, k in changes if k != "stop"), total)
    out = np.zeros(int(total * SR) + SR)
    mel_a = [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 83, 79, 74, 71]   # bouncy, C major
    mel_b = [79, 81, 84, 81, 79, 76, 79, 76, 74, 77, 79, 77, 76, 72, 74, 76]
    bass = [48, 55, 53, 55]
    cache = {}
    step = beat / 2
    k, t = 0, 0.0
    while t < stop - 0.05:
        mel = mel_a if t < swap else mel_b
        m = mel[k % len(mel)]
        key = (m, round(step, 3))
        if key not in cache:
            cache[key] = pluck(440 * 2 ** ((m - 69) / 12), step * 1.8)
        x = cache[key] * (0.5 if k % 2 else 0.65)
        i = int(t * SR)
        out[i:i + len(x)] += x[:len(out) - i]
        if k % 2 == 0:
            b = bass[(k // 4) % len(bass)]
            kb = (b, "bass")
            if kb not in cache:
                cache[kb] = lp(pluck(440 * 2 ** ((b - 69) / 12), beat * 1.5, 0.1), 600)
            out[i:i + len(cache[kb])] += cache[kb][:len(out) - i] * 0.8
        if t >= swap and k % 2 == 1:  # shaker in the desert
            sh = hp(noise(0.06), 5000) * env(int(0.06 * SR), 0.002, 0.05) * 0.12
            out[i:i + len(sh)] += sh[:len(out) - i]
        k += 1
        t += step
    i = int(stop * SR)
    out[i:i + int(0.08 * SR)] *= np.linspace(1, 0, len(out[i:i + int(0.08 * SR)]))
    out[i + int(0.08 * SR):] = 0
    return out[: int(total * SR)]


def place(buf, x, at, gain):
    i = int(at * SR)
    if i >= len(buf):
        return
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n] * gain


def main():
    data = json.load(open(os.path.join(ROOT, "tools", "cues.json")))
    total = data["total"]
    cues = data["cues"]
    sfx = np.zeros(int(total * SR))
    loop_starts = sorted(t for t, n, _ in cues if n in LOOPS)
    for t, name, gain in cues:
        if name in LOOPS:
            nxt = [s for s in loop_starts if s > t]
            dur = (nxt[0] if nxt else total) - t + 0.15
            x = SOUNDS[name](dur)
        else:
            x = SOUNDS[name](0)
        place(sfx, x, t + 1 / data.get("fps", 30), gain)   # one frame after the picture
    sfx = np.clip(sfx, -1, 1) * 0.95
    m = data.get("music", {})
    mus = music(total, m.get("bpm", 112), m.get("mood_change", []))
    mus = norm(mus, 0.35)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    sf.write(os.path.join(ROOT, "assets", "sfx.wav"), np.stack([sfx, sfx], 1), SR)
    sf.write(os.path.join(ROOT, "assets", "music.wav"), np.stack([mus, mus], 1), SR)
    print(f"wrote assets/sfx.wav + assets/music.wav ({total}s, {len(cues)} cues)")


if __name__ == "__main__":
    main()
