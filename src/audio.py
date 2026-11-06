#!/usr/bin/env python3
"""Fon musiqasi va effektlar (sintez): out/_music.wav — 48 kHz stereo."""
import numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000; DUR = 68.05; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(1)
L = np.zeros(N); R = np.zeros(N)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def env_adsr(n, a, r):
    e = np.ones(n); na = min(n // 2, int(a * SR)); nr = min(n // 2, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return e

BPM = 100; beat = 60 / BPM
# C - G - Am - F (har biri 2 takt = 8 zarb)
prog = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]
chord_len = 8 * beat

def intensity(x):
    # sahnalar bo'yicha musiqa zichligi
    pts = [(0, 0.5), (3, 0.6), (12.0, 0.6), (12.6, 1.0), (31, 0.9), (44.6, 1.0), (57.2, 1.1), (66, 1.0), (68.05, 0.0)]
    return np.interp(x, [p[0] for p in pts], [p[1] for p in pts])

ci = 0; pos = 0.0
while pos < DUR:
    root, notes = prog[ci % 4]
    n0 = int(pos * SR); n1 = min(N, int((pos + chord_len) * SR)); n = n1 - n0
    if n <= 0: break
    tt = np.arange(n) / SR
    e = env_adsr(n, 0.8, 0.9)
    pad = np.zeros(n)
    for m in notes:
        for det in (-0.08, 0.08):
            f = hz(m + det)
            pad += np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) + 0.25 * np.sin(4 * np.pi * f * tt)
    pad *= e * 0.035 * (1 + 0.15 * np.sin(2 * np.pi * 0.3 * tt))
    L[n0:n1] += pad; R[n0:n1] += np.roll(pad, 240)
    # bas
    for b in range(8):
        s0 = n0 + int(b * beat * SR); s1 = min(N, s0 + int(beat * 0.95 * SR))
        if s0 >= N: break
        bt = np.arange(s1 - s0) / SR
        bass = np.sin(2 * np.pi * hz(root - 12) * bt) * np.exp(-bt * 3) * 0.16
        L[s0:s1] += bass; R[s0:s1] += bass
    # arpedjio (8-lik notalar)
    arp = notes + [notes[1] + 12, notes[2] + 12, notes[1] + 12]
    for j in range(16):
        s0 = n0 + int(j * beat / 2 * SR); s1 = min(N, s0 + int(0.9 * SR))
        if s0 >= N: break
        at = np.arange(s1 - s0) / SR; f = hz(arp[j % len(arp)] + 12)
        pl = (np.sin(2 * np.pi * f * at) + 0.3 * np.sin(4 * np.pi * f * at) + 0.1 * np.sin(6 * np.pi * f * at)) * np.exp(-at * 7) * 0.05
        pan = 0.5 + 0.35 * np.sin(j * 0.9)
        L[s0:s1] += pl * (1 - pan) * 2 * 0.7; R[s0:s1] += pl * pan * 2 * 0.7
    pos += chord_len; ci += 1

# yengil zarb (kick + hi-hat), sahna 3 dan boshlab
for b in range(int(DUR / beat)):
    tb = b * beat
    if tb < 12.4 or tb > 66.5: continue
    s0 = int(tb * SR); s1 = min(N, s0 + int(0.35 * SR)); kt = np.arange(s1 - s0) / SR
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9) * 0.22
    L[s0:s1] += kick; R[s0:s1] += kick
    h0 = int((tb + beat / 2) * SR); h1 = min(N, h0 + int(0.06 * SR))
    if h0 < N:
        hh = np.diff(rng.normal(size=h1 - h0 + 1)) * np.exp(-np.arange(h1 - h0) / SR * 70) * 0.025
        L[h0:h1] += hh; R[h0:h1] += hh * 0.8

L *= intensity(t); R *= intensity(t)

# whoosh — sahnalar almashishida
def whoosh(tc, dur=0.9, amp=0.22):
    s0 = int((tc - dur * 0.6) * SR); n = int(dur * SR)
    if s0 < 0: s0 = 0
    nz = rng.normal(size=n)
    out = np.zeros(n); y = 0.0
    k = np.linspace(0.02, 0.35, n) ** 1.5
    k = np.concatenate([k[: n * 6 // 10], np.linspace(k[n * 6 // 10], 0.02, n - n * 6 // 10)])
    for i in range(n):
        y += k[i] * (nz[i] - y); out[i] = y
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    out = out * e * amp / (np.abs(out).max() + 1e-9)
    s1 = min(N, s0 + n); m = s1 - s0
    L[s0:s1] += out[:m]; R[s0:s1] += out[:m] * 0.9
for tc in [3.1, 12.4, 21.0, 31.2, 44.6, 57.2]:
    whoosh(tc)

# shimmer (yaltirash) — flakon paydo bo'lganda
def shimmer(tc, amp=0.06):
    for j, m in enumerate([84, 88, 91, 96, 100]):
        s0 = int((tc + j * 0.07) * SR); n = int(1.6 * SR); s1 = min(N, s0 + n)
        at = np.arange(s1 - s0) / SR
        tone = np.sin(2 * np.pi * hz(m) * at) * np.exp(-at * 3) * amp
        if j % 2: L[s0:s1] += tone
        else: R[s0:s1] += tone
shimmer(13.6); shimmer(58.3); shimmer(46.8, 0.04)

# oxirida so'nish
fade = np.clip((DUR - t) / 1.5, 0, 1); L *= fade; R *= fade
mx = max(np.abs(L).max(), np.abs(R).max()); L /= mx / 0.9; R /= mx / 0.9
data = (np.stack([L, R], 1) * 32767).astype(np.int16)
os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
with wave.open(os.path.join(ROOT, 'out', '_music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
print('musiqa tayyor')
