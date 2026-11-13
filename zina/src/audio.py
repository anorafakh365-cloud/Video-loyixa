#!/usr/bin/env python3
"""«54 zina» saundtreki: dramatik pad + kam notali pianino; zinada yurak urishi; quyosh chiqqach — umidli major.
Vaqtlar render.py dagi START/END dan olinadi. -> zina/out/_music.wav"""
import os, sys, wave
import numpy as np
sys.argv = [sys.argv[0]]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

SR = 48000; DUR = R.DUR; N = int(SR * DUR)
rng = np.random.default_rng(3)
L = np.zeros(N); Rr = np.zeros(N)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR
def filt(x, lo=None, hi=None):
    f = np.fft.rfftfreq(len(x), 1 / SR); g = np.ones_like(f)
    if hi: g /= np.sqrt(1 + (f / hi) ** 4)
    if lo: g /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(np.fft.rfft(x) * g, len(x))
def add(t0, s, pan=0.0, g=1.0):
    a = int(t0 * SR)
    if a >= N: return
    n = min(len(s), N - a); L[a:a + n] += s[:n] * g * (1 - max(0, pan)); Rr[a:a + n] += s[:n] * g * (1 + min(0, pan))
def env(n, a, r):
    e = np.ones(n); na = min(n, int(a * SR)); nr = min(n - na, int(r * SR))
    if na: e[:na] = np.linspace(0, 1, na) ** 2
    if nr: e[n - nr:] *= np.linspace(1, 0, nr) ** 2
    return e
def pad(t0, d, notes, g):
    x = tt(d); s = np.zeros_like(x)
    for m in notes:
        for det in (-0.004, 0.004):
            s += np.sin(2 * np.pi * hz(m) * (1 + det) * x) + 0.3 * np.sin(4 * np.pi * hz(m) * (1 + det) * x)
    s = filt(s / len(notes), hi=1800) * env(len(x), 1.5, 1.5)
    add(t0, s, -0.2, g); add(t0 + 0.02, s, 0.2, g)
def piano(t0, m, g=0.12):
    x = tt(3.0); f = hz(m)
    s = (np.sin(2 * np.pi * f * x) + 0.45 * np.sin(4 * np.pi * f * x) + 0.2 * np.sin(6 * np.pi * f * x)) * np.exp(-x * 1.6)
    add(t0, s, rng.uniform(-0.4, 0.4), g)

HOPE = R.START[36]                     # «Bir kuni tongda yugurdim»
# 1-qism: minor (Am — F — C — G), sekin
MINOR = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]
MAJOR = [[48, 55, 64, 67], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]   # C G Am F
bar = 4.0; t = 0.0; b = 0
while t < DUR:
    hope = t >= HOPE - 0.5
    ch = (MAJOR if hope else MINOR)[b % 4]
    pad(t, bar + 1.5, ch, 0.055 if not hope else 0.07)
    add(t, filt(np.sin(2 * np.pi * hz(ch[0] - 12) * tt(bar)) * env(int(bar * SR), 0.5, 1.0), hi=200), 0, 0.12)
    mel = [ch[-1] + 12, ch[1] + 12, ch[0] + 24, ch[1] + 12] if hope else [ch[-1] + 12, None, ch[1] + 12, None]
    for q, m in enumerate(mel):
        if m: piano(t + q * bar / 4, m, 0.09 if hope else 0.07)
    t += bar; b += 1

# yurak urishi — zina sahnalarida (6, 7)
for i in (6, 7):
    t0, t1 = R.START[i], R.END[i]; t = t0; bpm = 95
    while t < t1:
        for dd, g in ((0, 1.0), (0.17, 0.7)):
            x = tt(0.25); s = filt(np.sin(2 * np.pi * 52 * x) * np.exp(-x * 18), hi=180); add(t + dd, s, 0, 0.5 * g)
        bpm = min(150, bpm + 6); t += 60 / bpm
# zarba: yiqilish (7 oxiri), og'riq (24), quyosh (36), final (46)
def hit(t0, g):
    x = tt(2.0); s = np.sin(2 * np.pi * (38 + 60 * np.exp(-x * 14)) * x) * np.exp(-x * 2.5)
    s += filt(rng.standard_normal(len(x)), hi=2500) * np.exp(-x * 12) * 0.3; add(t0, s, 0, g)
hit(R.END[7] - 0.35, 0.7); hit(R.START[24] + (R.END[24] - R.START[24]) * 0.6, 0.6)
hit(R.START[2] + 0.9, 0.45); hit(R.START[38] + 1.0, 0.4)
# shimmer — umid
for t0 in (HOPE, R.START[38], R.START[46]):
    for j, m in enumerate([84, 88, 91, 96]):
        x = tt(2.5); add(t0 + j * 0.08, np.sin(2 * np.pi * hz(m) * x) * np.exp(-x * 1.8), 0.6 * (-1) ** j, 0.04)
# shamol/xona shovqini fonda
amb = filt(rng.standard_normal(N), 200, 1200) * 0.012; L += amb; Rr += np.roll(amb, 3000)

def reverb(x, secs=2.8, wet=0.35):
    n = int(secs * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 2.6); ir = filt(ir, hi=5000); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n; F_ = 1 << (m - 1).bit_length()
    return x + np.fft.irfft(np.fft.rfft(x, F_) * np.fft.rfft(ir, F_), F_)[:len(x)] * wet
L = reverb(L); Rr = reverb(Rr)
tm = np.arange(N) / SR; fade = np.clip(tm / 1.5, 0, 1) * np.clip((DUR - tm) / 2.0, 0, 1)
L *= fade; Rr *= fade; pk = max(np.abs(L).max(), np.abs(Rr).max()); L /= pk / 0.9; Rr /= pk / 0.9
with wave.open(os.path.join(R.OUT, '_music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([L, Rr], 1) * 32767).astype(np.int16).tobytes())
print('musiqa tayyor', round(DUR, 1))
