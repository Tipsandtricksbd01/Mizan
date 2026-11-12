"""Synthesizes the intro's music bed, timed to the picture.

Run: python score.py <out.wav>   (needs numpy, scipy, soundfile)

Cues (seconds, absolute), one frame after the picture they answer:
  0.0  - 2.1   low D pad breathes in under the scale being built
  2.16         left weight lands: soft thud + low marimba A3
  3.03         right weight lands: thud + marimba D4 (balance restored)
  3.9  - 4.55  airy swell carries the beam into the title
  4.55         pad blooms to Dmaj9
  5.03 - 5.43  one bell per letter of the name (D E F# A B)
  6.08         tagline: soft high chime on A5
  8.4  - 10.0  fade out
"""

import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
DUR = 10.0
N = int(SR * DUR)
t = np.arange(N) / SR
FRAME = 1 / 30


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env_adsr(n, a, r, total):
    """Linear attack, hold, cosine release, in samples of a `total`-length buffer."""
    e = np.ones(total)
    ai = int(a * SR)
    ri = int(r * SR)
    e[:ai] = np.linspace(0, 1, ai)
    e[n - ri : n] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, ri)))
    e[n:] = 0
    return e


def pad_voice(f, start, end, bright, detune=0.004, seed=0):
    """Additive soft saw with slow brightness, two detuned copies per side."""
    rng = np.random.default_rng(seed)
    out = np.zeros((N, 2))
    s, e = int(start * SR), int(end * SR)
    tt = t[s:e] - start
    for side in range(2):
        for d in (-detune, detune):
            ph = rng.uniform(0, 2 * np.pi)
            ff = f * (1 + d * (1 if side else -1) * 0.7 + d)
            sig = np.zeros_like(tt)
            for k in range(1, 12):
                amp = (1 / k) * np.exp(-k / np.maximum(bright(tt), 0.3))
                sig += amp * np.sin(2 * np.pi * ff * k * tt + ph * k)
            out[s:e, side] += sig
    return out / 4


def place(buf, mono_or_stereo, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    x = mono_or_stereo
    if x.ndim == 1:
        lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        x = np.stack([x * lg, x * rg], axis=1) * np.sqrt(2)
    n = min(len(x), N - i)
    buf[i : i + n] += gain * x[:n]


def marimba(f, length=1.6):
    tt = np.arange(int(length * SR)) / SR
    sig = (
        np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3.5)
        + 0.35 * np.sin(2 * np.pi * f * 4.0 * tt) * np.exp(-tt * 14)
        + 0.12 * np.sin(2 * np.pi * f * 9.2 * tt) * np.exp(-tt * 30)
    )
    sig[: int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR))
    return sig


def bell(f, length=2.5):
    tt = np.arange(int(length * SR)) / SR
    parts = [(1.0, 1.0, 1.6), (2.76, 0.35, 3.5), (5.40, 0.18, 6.0), (8.93, 0.08, 9.0)]
    sig = sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt * d) for r, a, d in parts)
    sig[: int(0.003 * SR)] *= np.linspace(0, 1, int(0.003 * SR))
    return sig


def thud(length=0.6):
    tt = np.arange(int(length * SR)) / SR
    f = 46 + 70 * np.exp(-tt * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt * 9)


def noise_swell(start, end, seed=1):
    rng = np.random.default_rng(seed)
    n = int((end - start) * SR)
    x = rng.standard_normal((n, 2))
    x = sosfilt(butter(2, [700, 5200], btype="band", fs=SR, output="sos"), x, axis=0)
    ramp = np.linspace(0, 1, n) ** 2.2
    ramp[-int(0.06 * SR) :] *= np.linspace(1, 0, int(0.06 * SR))
    return x * ramp[:, None]


def reverb(x, seconds=2.6, mix=0.32, seed=2):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    tt = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-tt * 6.9 / seconds)[:, None]
    ir = sosfilt(butter(1, 5000, fs=SR, output="sos"), ir, axis=0)
    ir /= np.sqrt((ir**2).sum(axis=0))
    wet = np.stack([fftconvolve(x[:, c], ir[:, c])[:N] for c in range(2)], axis=1)
    return (1 - mix) * x + mix * wet


mix = np.zeros((N, 2))

# Pad: D minor-ish root and fifth while unbalanced, blooming to Dmaj9 for the title.
pad = np.zeros((N, 2))
dim = lambda tt: 1.2 + 0.8 * np.clip(tt / 3, 0, 1)
for i, m in enumerate([38, 45, 50]):  # D2 A2 D3
    pad += pad_voice(hz(m), 0.0, DUR, dim, seed=10 + i) * env_adsr(N, 2.0, 1.6, N)[:, None]
bloom = lambda tt: 1.4 + 2.2 * np.clip(tt / 1.2, 0, 1)
for i, m in enumerate([54, 57, 61, 64]):  # F#3 A3 C#4 E4
    v = pad_voice(hz(m), 4.55, DUR, bloom, seed=20 + i)
    v *= env_adsr(N, 0.0, 0.0, N)[:, None]
    ramp = np.clip((t - 4.55) / 0.9, 0, 1) ** 1.5
    pad += 0.55 * v * ramp[:, None]
mix += 0.30 * pad

# Weight impacts
place(mix, thud(), 2.13 + FRAME, gain=0.55, pan=-0.35)
place(mix, marimba(hz(57)), 2.13 + FRAME, gain=0.42, pan=-0.45)  # A3
place(mix, thud(), 3.00 + FRAME, gain=0.55, pan=0.35)
place(mix, marimba(hz(62)), 3.00 + FRAME, gain=0.42, pan=0.45)  # D4

# Swell into the title
place(mix, noise_swell(3.9, 4.58), 3.9, gain=0.06)

# One bell per letter, rising across the stereo field
for i, m in enumerate([74, 76, 78, 81, 83]):  # D5 E5 F#5 A5 B5
    place(mix, bell(hz(m)), 5.0 + 0.1 * i + FRAME, gain=0.16, pan=-0.5 + 0.25 * i)

# Tagline chime
place(mix, bell(hz(81), 3.5), 6.05 + FRAME, gain=0.10, pan=0.1)

mix = reverb(mix)

# Gentle high-pass so the low end doesn't muddy small speakers, then fades
mix = sosfilt(butter(2, 35, btype="high", fs=SR, output="sos"), mix, axis=0)
fade_in = np.clip(t / 0.05, 0, 1)
fade_out = np.where(t > 8.4, 0.5 * (1 + np.cos(np.pi * np.clip((t - 8.4) / 1.6, 0, 1))), 1.0)
mix *= (fade_in * fade_out)[:, None]

mix /= np.max(np.abs(mix)) / 0.89
sf.write(sys.argv[1] if len(sys.argv) > 1 else "score.wav", mix.astype(np.float32), SR, subtype="PCM_24")
