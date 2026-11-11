#!/usr/bin/env python3
"""TEZORA v2 saundtreki (mijoz videosi uchun, 30.4 s): yengil, ko'tarinki korporativ musiqa (120 BPM, C–G–Am–F) + whoosh/suv/zarba effektlari.
Faqat numpy kerak. -> tezora/out/_music.wav (48 kHz stereo)"""
import os, wave
import numpy as np

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000; DUR = 30.4; N = int(SR * DUR)
def T(x): return x
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N); FL = np.zeros(N); FR = np.zeros(N)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR
def _mask(n, lo=None, hi=None, order=2):
    f = np.fft.rfftfreq(n, 1 / SR); g = np.ones_like(f)
    if hi: g /= np.sqrt(1 + (f / hi) ** (2 * order))
    if lo: g /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return g
def filt(x, lo=None, hi=None, order=2):
    return np.fft.irfft(np.fft.rfft(x) * _mask(len(x), lo, hi, order), len(x))
def add(bl, br, t0, s, pan=0.0, g=1.0):
    s0 = int(t0 * SR)
    if s0 < 0: s = s[-s0:]; s0 = 0
    n = min(len(s), N - s0)
    if n <= 0: return
    bl[s0:s0 + n] += s[:n] * g * (1 - max(0, pan)); br[s0:s0 + n] += s[:n] * g * (1 + min(0, pan))
def env(n, a, r):
    e = np.ones(n); na = min(n, int(a * SR)); nr = min(n - na, int(r * SR))
    if na: e[:na] = np.linspace(0, 1, na) ** 2
    if nr: e[n - nr:] *= np.linspace(1, 0, nr) ** 2
    return e
def saw(f, t, det=0.0):
    o = np.zeros_like(t)
    for d in (-det, 0, det): o += 2 * ((f * (1 + d) * t + rng.random()) % 1.0) - 1
    return o / 3

BPM = 120; beat = 60 / BPM; bar = 4 * beat
ANCHOR = 12.66 - 6 * bar     # 2-qism (12.66 s) bar boshiga tushadi          # zarbli qism 7.27 da boshlanadi, yakuniy kadr ham bar boshiga tushadi
DRUMS = 5.76; END = 28.66 - 2 * bar   # final akkord 28.66 da
CH = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]  # C G Am F

b = 0
while True:
    t0 = ANCHOR + b * bar
    if t0 > DUR: break
    root, notes = CH[b % 4]
    last = t0 >= END + bar * 2 - 0.01     # final akkord
    if last: root, notes = CH[0]
    inten = float(np.interp(t0, [0, DRUMS, 14, END, DUR], [0.55, 0.85, 1.0, 1.0, 0.8]))
    dl = bar * (2.2 if last else 1.0) + 0.3; d = tt(dl)
    pad = sum(filt(saw(hz(m), d, 0.006), hi=2200) for m in notes) / 4 * env(len(d), 0.25, 0.6 if not last else 2.0)
    add(L, R, t0, pad, -0.25, 0.09 * inten); add(L, R, t0, np.roll(pad, 400), 0.25, 0.09 * inten)
    if last:
        dd = tt(2.5); bs = filt(saw(hz(root - 12), dd), hi=300) * np.exp(-dd * 1.2)
        add(L, R, t0, bs, 0, 0.3); break
    # bas (sakkizlik notalar)
    for q in range(8):
        dd = tt(beat * 0.48); bs = filt(saw(hz(root - 12 if q % 2 == 0 else root), dd), hi=420) * np.exp(-dd * 5)
        add(L, R, t0 + q * beat / 2, bs, 0, (0.22 if t0 >= DRUMS - 0.01 else 0.12) * inten)
    # plak (pluck) arpedjio — o'n oltitalik
    arp = [notes[0] + 12, notes[2] + 12, notes[1] + 12, notes[3] + 12]
    for q in range(16):
        f = hz(arp[q % 4] + (12 if q % 8 == 7 else 0)); dd = tt(0.5)
        pl = (np.sin(2 * np.pi * f * dd) + 0.35 * np.sin(4 * np.pi * f * dd) + 0.12 * np.sin(6 * np.pi * f * dd)) * np.exp(-dd * 9)
        add(L, R, t0 + q * beat / 4, pl, 0.45 * np.sin(q * 1.7), 0.05 * inten)
    if t0 >= DRUMS - 0.01:
        for q in range(4):
            dd = tt(0.35); kick = np.sin(2 * np.pi * (50 + 120 * np.exp(-dd * 40)) * dd) * np.exp(-dd * 9)
            add(L, R, t0 + q * beat, kick, 0, 0.6 * inten)
            if q % 2 == 1:
                dd = tt(0.25); cl = filt(rng.standard_normal(len(dd)), 900, 7000) * np.exp(-dd * 20)
                add(L, R, t0 + q * beat, cl, 0, 0.22 * inten)
            for h in (0.5,):
                dd = tt(0.05); hat = filt(rng.standard_normal(len(dd)), 7500) * np.exp(-dd * 90)
                add(L, R, t0 + (q + h) * beat, hat, 0.35, 0.09 * inten)
            if t0 >= 12.66 - 0.01:     # jarayon qismida qo'shimcha shaker
                for h in (0.25, 0.75):
                    dd = tt(0.04); sh = filt(rng.standard_normal(len(dd)), 6000) * np.exp(-dd * 120)
                    add(L, R, t0 + (q + h) * beat, sh, -0.35, 0.05)
    b += 1

# ---------------------------------------------------------------- effektlar
def whoosh(tc, dur=0.5, g=0.22):
    n = int(dur * SR); x = rng.standard_normal(n); e = np.sin(np.linspace(0, np.pi, n)) ** 2
    lo = filt(x, 250, 1400); hi = filt(x, 1400, 8000); m = np.linspace(0, 1, n)
    s = (lo * (1 - m) + hi * m) * e
    add(FL, FR, tc - dur * 0.6, s / (np.abs(s).max() + 1e-9), 0, g)
def splash(t0, g=0.2):
    d = tt(0.9); s = filt(rng.standard_normal(len(d)), 600, 9000) * np.exp(-d * 5) * (1 - np.exp(-d * 80))
    for _ in range(25):
        k = int(rng.uniform(0, 0.6) * SR); dd = tt(0.03)
        s[k:k + len(dd)] += np.sin(2 * np.pi * rng.uniform(900, 2600) * dd * (1 + dd * 30)) * np.exp(-dd * 140) * 0.5
    add(FL, FR, t0, s / np.abs(s).max(), rng.uniform(-0.3, 0.3), g)
def hit(t0, g=0.55):
    d = tt(1.5); s = np.sin(2 * np.pi * (42 + 70 * np.exp(-d * 16)) * d) * np.exp(-d * 3)
    s += filt(rng.standard_normal(len(d)), hi=3500) * np.exp(-d * 16) * 0.35
    add(FL, FR, t0, s, 0, g)
def shimmer(t0, g=0.06):
    for j, m in enumerate([84, 88, 91, 96, 100]):
        d = tt(1.8); add(FL, FR, t0 + j * 0.05, np.sin(2 * np.pi * hz(m) * d) * np.exp(-d * 2.5), 0.6 * (-1) ** j, g)
def riser(t0, dur):
    d = tt(dur); k = d / dur
    s = filt(rng.standard_normal(len(d)), 400, 7000) * k ** 2.5 + np.sin(2 * np.pi * (300 + 1200 * k ** 2) * d) * k ** 2 * 0.25
    add(FL, FR, t0, s, 0, 0.16)

for tc in [1.33, 3.7, 5.75, 7.63, 10.9, 12.66, 13.45, 14.45, 15.36, 16.7, 18.4, 21.07, 23.0, 24.68, 27.4]: whoosh(tc, g=0.18)
for t0 in [7.63, 12.66, 13.45]: splash(t0, 0.14)
hit(5.12, 0.5); shimmer(5.15)
riser(25.02 - 1.2, 1.2); hit(25.02, 0.55); shimmer(25.1); hit(27.65, 0.35); shimmer(27.65, 0.05)

# ---------------------------------------------------------------- reverb + yakuniy mix
def reverb(x, secs, wet):
    n = int(secs * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 3.5)
    ir = filt(ir, hi=6000); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n; F = 1 << (m - 1).bit_length()
    return x + np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)] * wet
L = reverb(L, 2.0, 0.28); R = reverb(R, 2.0, 0.28); FL = reverb(FL, 1.2, 0.18); FR = reverb(FR, 1.2, 0.18)
ML = L + FL; MR = R + FR
t = np.arange(N) / SR
fade = np.clip((DUR - 0.05 - t) / 1.0, 0, 1) * np.clip(t / 0.4, 0, 1)
ML *= fade; MR *= fade
pk = max(np.abs(ML).max(), np.abs(MR).max()); ML /= pk / 0.9; MR /= pk / 0.9
os.makedirs(os.path.join(PRJ, 'out'), exist_ok=True)
with wave.open(os.path.join(PRJ, 'out', '_v2_music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([ML, MR], 1) * 32767).astype(np.int16).tobytes())
print('saundtrek tayyor')
