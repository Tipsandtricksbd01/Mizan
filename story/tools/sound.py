"""Synthesizes assets/music/music.wav and assets/sfx/sfx.wav for the Bridgeville film.

Run with numpy + scipy + soundfile:  python tools/sound.py
Cue times are absolute seconds (picture time + one frame for effects).
"""

import math
import os
import random

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
TOTAL = 121.5
N = int(SR * TOTAL)
F = 1 / 30
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(sec):
    return np.arange(int(sec * SR)) / SR


def add(buf, x, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N:
        return
    if x.ndim == 1:
        lg, rg = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        x = np.stack([x * lg, x * rg], axis=1) * math.sqrt(2)
    n = min(len(x), N - i)
    buf[i:i + n] += gain * x[:n]


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x, axis=0)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x, axis=0)


rng = np.random.default_rng(5)


def noise(sec):
    return rng.standard_normal(int(sec * SR))


# ------------------------------------------------------------- instruments
def marimba(f, length=0.9):
    t = tt(length)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 6) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)
         + 0.08 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 40))
    s[:96] *= np.linspace(0, 1, 96)
    return s


def pluck_bass(f, length=0.6):
    t = tt(length)
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)) * np.exp(-t * 5.5)
    s[:120] *= np.linspace(0, 1, 120)
    return s


def kick():
    t = tt(0.35)
    fr = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 12)


def shaker(length=0.07):
    x = bp(noise(length), 5000, 11000)
    return x * np.exp(-tt(length) * 60)


def pad_chord(notes, length, bright=2.0):
    t = tt(length)
    out = np.zeros((len(t), 2))
    for j, m in enumerate(notes):
        f = hz(m)
        for side, det in ((0, -0.003), (1, 0.003)):
            s = np.zeros_like(t)
            for k in range(1, 9):
                s += (1 / k) * math.exp(-k / bright) * np.sin(2 * np.pi * f * (1 + det) * k * t + j + k)
            out[:, side] += s
    env = np.minimum(1, np.minimum(t / 0.4, (length - t) / 0.5))
    return out * np.clip(env, 0, 1)[:, None] / len(notes)


def wah(f, length):
    t = tt(length)
    ph = 2 * np.pi * np.cumsum(f * (1 - 0.03 * t)) / SR
    saw = sum(np.sin(k * ph) / k for k in range(1, 14))
    cut = 400 + 1600 * (0.5 - 0.5 * np.cos(2 * np.pi * np.minimum(t / 0.5, 1)))
    # crude time-varying low-pass: blend of two fixed filters by the envelope
    a = lp(saw, 500)
    b = lp(saw, 2200)
    w = (cut - 400) / 1600
    s = a * (1 - w) + b * w
    env = np.minimum(1, np.minimum(t / 0.05, (length - t) / 0.15))
    return s * np.clip(env, 0, 1) * 0.5


# ------------------------------------------------------------- music
PROG_MAJ = [(48, [60, 64, 67, 72]), (45, [57, 60, 64, 69]), (41, [57, 60, 65, 69]), (43, [55, 59, 62, 67])]  # C Am F G
PROG_MIN = [(45, [57, 60, 64]), (41, [57, 60, 65]), (38, [57, 62, 65]), (40, [56, 59, 64])]  # Am F Dm E

# (start, end, style)
SECTIONS = [
    (0.0, 7.95, "full"),
    (7.95, 23.45, "gentle"),
    (23.45, 38.85, "full"),
    (38.85, 59.85, "frenzy"),
    (59.85, 67.33, "triumph"),
    (70.3, 86.85, "minor"),
    (86.85, 93.6, "gentle"),
    (93.6, 97.5, "golden"),
    (99.95, 108.9, "full"),
    (108.9, 121.5, "finale"),
]


def music():
    m = np.zeros((N, 2))
    for s0, s1, style in SECTIONS:
        prog = PROG_MIN if style == "minor" else PROG_MAJ
        nb = int(math.ceil((s1 - s0) / BEAT))
        for b in range(nb):
            t = s0 + b * BEAT
            if t >= s1:
                break
            bar = int(b // 4)
            root, chord = prog[bar % 4]
            beat_in_bar = b % 4
            if style in ("full", "frenzy", "triumph", "finale"):
                if beat_in_bar in (0, 2):
                    add(m, pluck_bass(hz(root)), t, 0.55)
                    add(m, kick(), t, 0.35)
                if beat_in_bar == 3:
                    add(m, pluck_bass(hz(root + 7)), t + BEAT / 2, 0.35)
                for e in range(2):
                    note = chord[(beat_in_bar * 2 + e) % len(chord)] + 12
                    add(m, marimba(hz(note)), t + e * BEAT / 2, 0.22, pan=-0.3 + 0.2 * e)
                hats = 4 if style == "frenzy" else 2
                for h in range(hats):
                    add(m, shaker(), t + h * BEAT / hats, 0.10 if h % 2 else 0.05, pan=0.4)
            elif style == "gentle":
                if beat_in_bar == 0:
                    add(m, pad_chord(chord, BAR + 0.4, 1.6), t, 0.32)
                    add(m, pluck_bass(hz(root)), t, 0.35)
                note = chord[beat_in_bar % len(chord)] + 12
                add(m, marimba(hz(note), 1.2), t, 0.16, pan=-0.2 + 0.13 * beat_in_bar)
            elif style == "minor":
                if beat_in_bar == 0:
                    add(m, pad_chord(chord, BAR + 0.4, 1.3), t, 0.22)
                if beat_in_bar in (0, 2):
                    add(m, pluck_bass(hz(root), 0.9), t, 0.45)
                if beat_in_bar == 1:
                    add(m, marimba(hz(chord[b % len(chord)] + 12), 1.0), t, 0.12, pan=0.3)
                add(m, shaker(0.03), t, 0.04, pan=-0.4)
            elif style == "golden":
                if beat_in_bar == 0:
                    add(m, pad_chord([53, 57, 60, 64], BAR + 1.6, 2.6), t, 0.4)
                add(m, marimba(hz([77, 81, 84, 88][beat_in_bar]), 1.4), t, 0.12, pan=0.2)
        if style == "finale":
            pass
    # riser into the SOLD hit
    r0, r1 = 55.15, 59.85
    t = tt(r1 - r0)
    x = bp(noise(r1 - r0), 1200, 7000) * (t / (r1 - r0)) ** 2.5
    tone = np.sin(2 * np.pi * np.cumsum(220 + 660 * (t / (r1 - r0)) ** 2) / SR) * (t / (r1 - r0)) ** 2
    add(m, 0.12 * x + 0.10 * tone, r0)
    # big chord stabs
    for at, chord in ((59.85, [48, 60, 64, 67, 72]), (119.16, [48, 60, 64, 67, 72, 76])):
        add(m, pad_chord(chord, 2.4, 3.2), at, 0.8)
        add(m, pluck_bass(hz(36), 1.5), at, 0.9)
        cym = hp(noise(2.0), 4000) * np.exp(-tt(2.0) * 2.2)
        add(m, cym, at, 0.18)
    # sad trombone on the repair bills
    for at, note, ln in ((98.3, 55, 0.38), (98.7, 54, 0.38), (99.1, 53, 0.38), (99.5, 52, 1.0)):
        add(m, wah(hz(note), ln), at, 0.55)
    # hard stop on "But" and fade at the end
    i_stop = int(67.33 * SR)
    m[i_stop:int(70.3 * SR)] = 0
    m[i_stop - 240:i_stop] *= np.linspace(1, 0, 240)[:, None]
    t_all = np.arange(N) / SR
    fade = np.where(t_all > 120.0, np.clip(1 - (t_all - 120.0) / 1.45, 0, 1), 1.0)
    m *= fade[:, None]
    m = hp(m, 40)
    return m


# ------------------------------------------------------------- effects
def thud(gain_low=1.0, length=0.5):
    t = tt(length)
    fr = 45 + 120 * np.exp(-t * 25)
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 9) * gain_low
    crack = bp(noise(length), 900, 4000) * np.exp(-t * 45)
    return body + 0.6 * crack


def poof():
    t = tt(0.6)
    x = lp(noise(0.6), 2500) * np.exp(-t * 7) * np.minimum(1, t / 0.01)
    return x * 1.4


def whoosh(length=0.5, lo=300, hi=3000, peak=0.7):
    t = tt(length)
    x = bp(noise(length), lo, hi)
    env = np.where(t < peak * length, (t / (peak * length)) ** 2, np.exp(-(t - peak * length) * 12))
    return x * env


def pop(f=600):
    t = tt(0.18)
    fr = f * (0.6 + 0.8 * np.minimum(t / 0.04, 1))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 28) * np.minimum(1, t / 0.002)


def click():
    t = tt(0.03)
    return bp(noise(0.03), 2000, 8000) * np.exp(-t * 300) + 0.5 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 250)


def tick():
    t = tt(0.025)
    return np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 320)


def buzz(length):
    t = tt(length)
    sq = np.sign(np.sin(2 * np.pi * 160 * t))
    am = (np.sin(2 * np.pi * 18 * t) > 0).astype(float)
    return lp(sq * am, 1500) * 0.35


def cricket():
    t = tt(0.18)
    return np.sin(2 * np.pi * 4600 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 60 * t)) * np.sin(np.pi * t / 0.18)


def rustle(length):
    t = tt(length)
    x = bp(noise(length), 1500, 7000)
    flut = 0.4 + 0.6 * (np.sin(2 * np.pi * 13 * t + np.sin(2 * np.pi * 3 * t)) > 0.2)
    return x * flut * np.minimum(1, np.minimum(t / 0.05, (length - t) / 0.1))


def knock():
    t = tt(0.12)
    return np.sin(2 * np.pi * 420 * t) * np.exp(-t * 50) + 0.3 * bp(noise(0.12), 600, 2000) * np.exp(-t * 60)


def whistle_fall(length):
    t = tt(length)
    fr = 1800 - 1100 * (t / length)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * 0.25 * np.minimum(1, t / 0.05)


def sfx():
    s = np.zeros((N, 2))
    r = random.Random(4)
    # stamps
    for at in (0.26, 59.84, 88.69, 104.59):
        add(s, thud(), at + F, 0.9)
    add(s, poof(), 6.70 + F, 0.8, pan=0.5)
    add(s, whoosh(0.45, 400, 4000, 0.9), 7.5, 0.6)
    add(s, whoosh(1.5, 200, 2000, 0.5), 9.8, 0.35)
    for at in (10.7, 13.85, 23.6, 33.1, 3.66, 34.05, 48.2, 73.62, 77.2, 94.65, 83.66, 80.7):
        add(s, pop(r.choice([520, 600, 680])), at + F, 0.45)
    for i in range(10):
        add(s, pop([700, 780, 860, 740, 820][i % 5]), 18.63 + 0.06 * i + F, 0.32, pan=-0.6 + 0.13 * i)
    for i in range(4):
        add(s, pop([480, 540, 600, 520][i]), 19.77 + 0.08 * i + F, 0.36, pan=-0.5 + 0.33 * i)
    for at in (22.4, 115.25, 82.0):
        add(s, knock(), at + F, 0.5)
    for i in range(6):
        add(s, cricket(), 26.5 + 0.32 * i, 0.12, pan=0.6)
    add(s, whoosh(0.32, 500, 5000, 0.8), 27.55, 0.6)
    add(s, click(), 35.0 + F, 0.6)
    add(s, whoosh(0.45, 300, 3000, 0.9), 36.15, 0.45)
    for i in range(8):
        add(s, pop(900 + 60 * (i % 3)), 36.95 + 0.17 * i + F, 0.25, pan=-0.6 + 0.17 * i)
    for i, t0 in enumerate((39.05, 39.4, 39.75)):
        x = whoosh(1.1, 150, 1800, 0.5)
        add(s, x, t0, 0.55, pan=-0.6 + 0.6 * i)
    add(s, buzz(1.0), 40.6, 0.35, pan=-0.3)
    add(s, buzz(0.85), 40.95, 0.28, pan=0.4)
    for i in range(26):
        base = 44.45 + 0.04 * i + 0.4
        for k in range(3):
            add(s, click(), base + 0.12 * k + r.uniform(0, 0.015), 0.22, pan=r.uniform(-0.8, 0.8))
    add(s, whoosh(0.4, 400, 3000, 0.9), 46.1, 0.4)
    for k in range(30):
        add(s, tick(), 48.45 + 0.8 * (k / 30) ** 1.0, 0.25)
    for k in range(40):
        add(s, tick(), 49.65 + 1.8 * (1 - (1 - k / 40) ** 0.5), 0.2, pan=0.3)
    for at in (52.5, 52.75, 53.0):
        add(s, tick(), at, 0.5)
    add(s, thud(0.6), 53.2 + F, 0.6)
    t = 55.15
    while t < 59.6:
        add(s, tick(), t, 0.16, pan=r.uniform(-0.3, 0.3))
        t += 0.05
    add(s, poof(), 63.96, 0.5)
    for i, t0 in enumerate((65.12, 65.42, 65.72)):
        add(s, whoosh(0.4, 800, 6000, 0.8), t0, 0.35, pan=-0.5 + 0.5 * i)
    add(s, click(), 71.55 + F, 0.9)
    add(s, rustle(1.1), 98.55, 0.45)
    add(s, whoosh(0.6, 300, 3000, 0.9), 107.7, 0.4)
    add(s, whistle_fall(0.42), 118.71, 0.5)
    add(s, thud(1.3, 0.8), 119.13 + F, 1.0)
    add(s, poof(), 119.16, 0.5)
    return s


def reverb(x, seconds=1.6, mix=0.18):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t * 6.9 / seconds)[:, None]
    ir = lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum(axis=0))
    wet = np.stack([fftconvolve(x[:, c], ir[:, c])[:N] for c in range(2)], axis=1)
    return (1 - mix) * x + mix * wet


if __name__ == "__main__":
    m = reverb(music(), 1.8, 0.22)
    m[int(67.33 * SR):int(70.3 * SR)] *= np.linspace(1, 0, int(70.3 * SR) - int(67.33 * SR))[:, None] ** 8
    m /= np.max(np.abs(m)) / 0.9
    x = reverb(sfx(), 0.8, 0.12)
    x /= np.max(np.abs(x)) / 0.9
    os.makedirs(os.path.join(ROOT, "assets", "music"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets", "sfx"), exist_ok=True)
    sf.write(os.path.join(ROOT, "assets/music/music_raw.wav"), m.astype(np.float32), SR, subtype="FLOAT")
    sf.write(os.path.join(ROOT, "assets/sfx/sfx_raw.wav"), x.astype(np.float32), SR, subtype="FLOAT")
    print("ok")
