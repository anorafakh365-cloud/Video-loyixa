#!/usr/bin/env python3
"""Ovoz faylidan (ElevenLabs) har bir gapning boshlanish/tugash vaqtini topadi -> zina/out/timing.json
  python3 zina/src/sync.py zina/assets/ovoz.mp3
Usul: jimlik oraliqlari bo'yicha nutq bo'laklari topiladi, so'ng ular gaplarga
so'z soniga mutanosib qilib, uzun pauzalarda bo'linadigan tarzda (dinamik dasturlash) taqsimlanadi."""
import os, sys, re, json, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
voice = sys.argv[1]; sys.argv = [sys.argv[0]]
import render as R

out = subprocess.run(['ffmpeg', '-hide_banner', '-i', voice, '-af', 'silencedetect=n=-38dB:d=0.12', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', voice], capture_output=True, text=True).stdout)
ss = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]
se = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
# nutq bo'laklari
segs = []; cur = 0.0
for a, b in zip(ss, se + [dur] * (len(ss) - len(se))):
    if a - cur > 0.05: segs.append((cur, a))
    cur = b
if dur - cur > 0.05: segs.append((cur, dur))
m = len(segs); K = len(R.S)
words = np.array([len(s.split()) for s, _, _ in R.S], float)
print('nutq bo\'laklari:', m, ' gaplar:', K)
if m < K: sys.exit('Bo\'laklar gaplardan kam — ElevenLabs\'da gaplar orasidagi pauzani oshiring.')
total_w = words.sum(); total_t = sum(b - a for a, b in segs)
gap_before = [0.0] + [segs[j][0] - segs[j - 1][1] for j in range(1, m)]
INF = 1e18
cost = np.full((K + 1, m + 1), INF); back = np.zeros((K + 1, m + 1), int); cost[0, 0] = 0
for k in range(1, K + 1):
    for j in range(k, m - (K - k) + 1):
        for i in range(k - 1, j):
            if cost[k - 1, i] >= INF: continue
            speech = sum(b - a for a, b in segs[i:j])
            c = (speech / total_t - words[k - 1] / total_w) ** 2 * 400 - gap_before[i] * 1.5
            if cost[k - 1, i] + c < cost[k, j]: cost[k, j] = cost[k - 1, i] + c; back[k, j] = i
res = []; j = m
for k in range(K, 0, -1):
    i = back[k, j]; res.append((segs[i][0], segs[j - 1][1])); j = i
res = res[::-1]
LEAD = 1.0   # video boshida 1 s tasvir, so'ng ovoz
json.dump([[round(a + LEAD, 3), round(b + LEAD, 3)] for a, b in res], open(os.path.join(R.OUT, 'timing.json'), 'w'), indent=0)
for (a, b), (s, _, _) in zip(res, R.S): print(f'{a + LEAD:7.2f}–{b + LEAD:7.2f}  {s}')
print('timing.json yozildi. Ovoz', LEAD, 's kechikish bilan qo\'yiladi.')
