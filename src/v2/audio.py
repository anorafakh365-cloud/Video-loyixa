#!/usr/bin/env python3
"""Saundtrek v2: musiqa + ovoz effektlari, diktor matniga moslangan. -> out/_v2_music.wav (48 kHz stereo)"""
import os, numpy as np, wave
from scipy.signal import butter, sosfilt, fftconvolve

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SR = 48000; DUR = 70.0; N = int(SR * DUR)
rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N)
FX_L = np.zeros(N); FX_R = np.zeros(N)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, f1, f2, o=2): return sosfilt(butter(o, [f1, f2], 'band', fs=SR, output='sos'), x)
def add(buf_l, buf_r, t0, sig, pan=0.0, gain=1.0):
    s0 = int(t0 * SR)
    if s0 >= N: return
    if s0 < 0: sig = sig[-s0:]; s0 = 0
    n = min(len(sig), N - s0)
    buf_l[s0:s0 + n] += sig[:n] * gain * (1 - max(0, pan)); buf_r[s0:s0 + n] += sig[:n] * gain * (1 + min(0, pan))
def env(n, a, r, curve=2.0):
    e = np.ones(n); na = min(n, int(a * SR)); nr = min(n - na, int(r * SR))
    if na: e[:na] = np.linspace(0, 1, na) ** curve
    if nr: e[n - nr:] *= np.linspace(1, 0, nr) ** curve
    return e
def tt(d): return np.arange(int(d * SR)) / SR
def saw(f, t, det=0.0):
    out = np.zeros_like(t)
    for d in (-det, 0, det):
        ph = (f * (1 + d) * t + rng.random()) % 1.0
        out += 2 * ph - 1
    return out / 3

# ======================================================= 1-QISM: tahdid (0 – 29.2)
# past dron (re minor)
d = tt(29.3)
drone = (np.sin(2 * np.pi * hz(38) * d) * 0.5 + lp(saw(hz(50), d, 0.004), 400) * 0.5)
drone *= env(len(d), 1.5, 0.3) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.11 * d))
grow = np.interp(d, [0, 6, 20, 25.4, 29.2], [0.5, 0.7, 0.9, 1.0, 1.3])
add(L, R, 0, drone * grow, gain=0.32)
# torlilar tremolosi (yuqori)
for m, pan in [(62, -0.4), (65, 0.4), (69, -0.1)]:
    s = lp(saw(hz(m), d, 0.006), 2500) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * d))
    s *= env(len(d), 3, 0.3) * np.interp(d, [0, 3, 12, 20, 29.2], [0, 0.4, 0.6, 0.8, 1.0])
    add(L, R, 0, s, pan, 0.05)
# past pulsatsiya (yurak urishi ritmi) 6.1 dan
for k_ in range(40):
    t0 = 6.1 + k_ * 0.857
    if t0 > 25.3: break
    p = tt(0.4); s = np.sin(2 * np.pi * (45 + 30 * np.exp(-p * 25)) * p) * np.exp(-p * 9)
    add(L, R, t0, s, 0, 0.28)
# soat chiqillashi — kun hisoblagichi
for k_ in range(14):
    t0 = 6.35 + k_ * 0.14
    if t0 > 8.2: break
    c = hp(rng.standard_normal(int(0.02 * SR)), 3000) * np.exp(-tt(0.02) * 300)
    add(FX_L, FX_R, t0, c, 0.2 * (-1) ** k_, 0.25)
# yorilish ovozlari (g'ujumlar yoriladi)
for t0 in [9.95, 10.18, 10.32, 10.6, 10.75]:
    c = bp(rng.standard_normal(int(0.08 * SR)), 900, 5000) * np.exp(-tt(0.08) * 60)
    add(FX_L, FX_R, t0, c, rng.uniform(-0.5, 0.5), 0.35)
# yomg'ir (20.8 – 25.4)
r = tt(5.0); rain = lp(hp(rng.standard_normal(len(r)), 1500), 7000) * env(len(r), 0.6, 0.8)
add(FX_L, FX_R, 20.7, rain, -0.2, 0.07); add(FX_L, FX_R, 20.7, np.roll(rain, 999), 0.2, 0.07)
for k_ in range(60):
    t0 = 20.8 + rng.uniform(0, 4.5); c = bp(rng.standard_normal(int(0.03 * SR)), 2000, 6000) * np.exp(-tt(0.03) * 150)
    add(FX_L, FX_R, t0, c, rng.uniform(-0.8, 0.8), 0.06)
# yurak urishi (25.4 – 29.1)
for k_ in range(6):
    t0 = 25.5 + k_ * 0.72
    for dd, g in [(0, 1.0), (0.18, 0.7)]:
        p = tt(0.25); s = lp(np.sin(2 * np.pi * 52 * p) * np.exp(-p * 18), 200)
        add(FX_L, FX_R, t0 + dd, s, 0, 0.55 * g)
# ko'tariluvchi (riser) 27.4 – 29.2
p = tt(1.8); rs = bp(rng.standard_normal(len(p)), 300, 6000) * (p / 1.8) ** 2.5
rs += np.sin(2 * np.pi * (200 + 900 * (p / 1.8) ** 2) * p) * (p / 1.8) ** 2 * 0.3
add(FX_L, FX_R, 27.4, rs, 0, 0.22)

# ======================================================= TO'XTANG! (29.22) — zarba
p = tt(3.0)
boom = np.sin(2 * np.pi * (35 + 80 * np.exp(-p * 12)) * p) * np.exp(-p * 1.6)
boom += lp(rng.standard_normal(len(p)), 2500) * np.exp(-p * 8) * 0.5
add(FX_L, FX_R, 29.2, boom, 0, 0.9)

# ======================================================= 2-QISM: yechim (30.0 – 70)
BPM = 110; beat = 60 / BPM; T0 = 30.0
prog_ = [(50, [62, 66, 69, 74]), (45, [61, 64, 69, 73]), (47, [62, 66, 71, 74]), (43, [62, 67, 71, 74])]   # D A Bm G
bar = 4 * beat
nb = int((DUR - T0) / bar) + 1
for b in range(nb):
    t0 = T0 + b * bar
    root, notes = prog_[b % 4]
    inten = np.interp(t0, [30, 31.3, 44.6, 51.8, 61.7, 66, 70], [0.6, 0.8, 0.85, 1.0, 1.0, 0.8, 0.5])
    # pad
    d_ = tt(bar + 0.3)
    pad = sum(lp(saw(hz(m), d_, 0.005), 1800) for m in notes) / 4
    add(L, R, t0, pad * env(len(d_), 0.3, 0.5), -0.2, 0.10 * inten)
    add(L, R, t0, np.roll(pad, 300) * env(len(d_), 0.3, 0.5), 0.2, 0.10 * inten)
    # bas
    for q in range(4):
        d_ = tt(beat * 0.95)
        bs = lp(saw(hz(root - 12), d_), 300) * np.exp(-d_ * 2.5)
        add(L, R, t0 + q * beat, bs, 0, 0.30 * inten)
    # pianino-arpedjio
    arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12, notes[2] + 12, notes[1] + 12, notes[3] + 12, notes[2] + 12]
    for q in range(8):
        d_ = tt(1.2); f = hz(arp[q])
        pl = (np.sin(2 * np.pi * f * d_) + 0.4 * np.sin(4 * np.pi * f * d_) + 0.15 * np.sin(6 * np.pi * f * d_)) * np.exp(-d_ * 4.5)
        add(L, R, t0 + q * beat / 2, pl, 0.4 * np.sin(q), 0.06 * inten)
    # baraban 31.3 dan
    if t0 >= 31.2:
        for q in range(4):
            d_ = tt(0.4); kick = np.sin(2 * np.pi * (48 + 110 * np.exp(-d_ * 35)) * d_) * np.exp(-d_ * 8)
            add(L, R, t0 + q * beat, kick, 0, 0.55 * inten)
            if q % 2 == 1:
                d_ = tt(0.25); clap = bp(rng.standard_normal(len(d_)), 900, 6000) * np.exp(-d_ * 22)
                add(L, R, t0 + q * beat, clap, 0, 0.18 * inten)
            for h in (0.5,):
                d_ = tt(0.06); hat = hp(rng.standard_normal(len(d_)), 7000) * np.exp(-d_ * 80)
                add(L, R, t0 + (q + h) * beat, hat, 0.3, 0.07 * inten)

# yaltirash (shimmer)
def shimmer(t0, g=0.08):
    for j, m in enumerate([86, 90, 93, 98, 102]):
        d_ = tt(2.0); s = np.sin(2 * np.pi * hz(m) * d_) * np.exp(-d_ * 2.2)
        add(FX_L, FX_R, t0 + j * 0.06, s, 0.6 * (-1) ** j, g)
for t0 in [30.02, 31.45, 54.7, 61.9, 64.6]: shimmer(t0)

# zarbali urg'ular (matn chiqishi)
def hit(t0, g=0.6, low=40):
    d_ = tt(1.6); s = np.sin(2 * np.pi * (low + 60 * np.exp(-d_ * 15)) * d_) * np.exp(-d_ * 3)
    s += lp(rng.standard_normal(len(d_)), 3000) * np.exp(-d_ * 18) * 0.4
    add(FX_L, FX_R, t0, s, 0, g)
for t0, g in [(4.72, 0.6), (12.9, 0.4), (23.6, 0.45), (31.42, 0.6), (61.86, 0.55), (64.57, 0.45)]: hit(t0, g)

# whoosh — sahna almashishlari
def whoosh(tc, dur=0.55, g=0.25):
    n = int(dur * SR); x = rng.standard_normal(n)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    lo = bp(x, 300, 1500); hi = bp(x, 1500, 7000)
    mix = np.linspace(0, 1, n)
    s = (lo * (1 - mix) + hi * mix) * e
    add(FX_L, FX_R, tc - dur * 0.6, s / (np.abs(s).max() + 1e-9), 0, g)
for tc in [3.0, 6.1, 9.75, 12.4, 16.2, 20.8, 25.4, 31.3, 34.2, 38.45, 44.6, 51.8, 57.2, 58.5, 59.8, 61.7, 64.45]:
    whoosh(tc)

# himoya: zarrachalar ovozi
for t0 in [38.6, 41.0]:
    d_ = tt(1.5); s = hp(rng.standard_normal(len(d_)), 5000) * env(len(d_), 0.2, 1.0) * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * d_))
    add(FX_L, FX_R, t0, s, 0, 0.05)

# ======================================================= reverb + mix
def reverb(x, secs=2.2, wet=0.25):
    n = int(secs * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 3.2)
    ir = lp(ir, 6000); ir /= np.sqrt((ir ** 2).sum())
    return x + fftconvolve(x, ir)[:len(x)] * wet
L = reverb(L, 2.5, 0.35); R = reverb(R, 2.5, 0.35)
FX_L = reverb(FX_L, 1.5, 0.2); FX_R = reverb(FX_R, 1.5, 0.2)
ML = L + FX_L; MR = R + FX_R
t = np.arange(N) / SR
fade = np.clip((DUR - t) / 1.2, 0, 1) * np.clip(t / 0.3, 0, 1)
ML *= fade; MR *= fade
pk = max(np.abs(ML).max(), np.abs(MR).max()); ML /= pk / 0.9; MR /= pk / 0.9
os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
with wave.open(os.path.join(ROOT, 'out', '_v2_music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([ML, MR], 1) * 32767).astype(np.int16).tobytes())
print('saundtrek tayyor')
