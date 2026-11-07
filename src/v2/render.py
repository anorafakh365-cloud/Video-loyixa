#!/usr/bin/env python3
"""AZDIF reklama v2 — 9:16 UHD (2160x3840), 25 fps, 70 s.
  K=1 python3 src/v2/render.py --stills 1 4 ...   nazorat kadrlari (1080x1920)
  K=2 python3 src/v2/render.py                    to'liq video -> out/_v2_video.mp4
"""
import os, sys, subprocess
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *
from shots import SHOTS, DUR

NFR = int(round(DUR * FPS))

def shot_at(t):
    for i, (a, b, fn, tr) in enumerate(SHOTS):
        if a <= t < b: return i
    return len(SHOTS) - 1

def post(arr, gp, i):
    arr = grade(arr, lift=gp.get('lift', (0, 0, 0)), sat=gp.get('sat', 1.0), contrast=gp.get('contrast', 1.0), temp=gp.get('temp', 0.0))
    arr = bloom(np.clip(arr, 0, 255), thresh=205, strength=0.30, radius=30)
    arr = arr * vignette_mask(0.6)
    arr = chroma_ab(arr, 1.2)
    arr = arr + grain(i, 4.0)[..., None]
    return np.clip(arr, 0, 255).astype(np.uint8)

def raw(t):
    i = shot_at(t); a, b, fn, tr = SHOTS[i]
    return fn(t)

def frame(i):
    t = i / FPS
    idx = shot_at(t); a, b, fn, tr = SHOTS[idx]
    arr, gp = fn(t)
    # o'tishlar (kirish tomoni)
    if idx > 0:
        pa, pb, pfn, _ = SHOTS[idx - 1]
        d = t - a
        if tr == 'fade' and d < 0.3:
            prev, pg = pfn(min(t, pb - 1e-3))
            w = ease_io(d / 0.3); arr = prev * (1 - w) + arr * w
            gp = {k_: (pg.get(k_, gp.get(k_)) if w < 0.5 else gp.get(k_)) for k_ in set(pg) | set(gp)}
            gp = {k_: v for k_, v in gp.items() if v is not None}
        elif tr == 'flash' and d < 0.25:
            arr = arr + 255 * (1 - ease_out(d / 0.25)) * 0.85
        elif tr == 'whip' and d < 0.14:
            im = np2im(arr); s = (1 - d / 0.14)
            arr = np.asarray(dir_blur(im, int(W * 0.25 * s), 0, 9), np.float32)
        elif tr == 'zoom' and d < 0.35:
            prev, pg = pfn(pb - 1e-3)
            w = ease_io(d / 0.35)
            pim = np2im(prev); z = 1 + 0.6 * w
            pim = view(pim, W / 2, H / 2, z * 1.0)
            arr = np.asarray(pim, np.float32) * (1 - w) + arr * w
    # chiqish tomoni (whip — keyingi kadrga)
    if idx < len(SHOTS) - 1:
        na, nb, nfn, ntr = SHOTS[idx + 1]
        if ntr == 'whip' and na - t < 0.12:
            s = 1 - (na - t) / 0.12
            arr = np.asarray(dir_blur(np2im(arr), int(W * 0.25 * s), 0, 9), np.float32)
    return post(arr, gp, i)

def render_chunk(args):
    ci, f0, f1 = args
    path = os.path.join(OUT, f'_v2chunk{ci:03d}.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(f0, f1):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
    print(f'bo\'lak {ci} tayyor ({f0}-{f1})', flush=True)
    return path

def main():
    os.makedirs(OUT, exist_ok=True)
    if '--stills' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1:]]
        for tt in ts:
            from PIL import Image
            Image.fromarray(frame(int(round(tt * FPS)))).save(os.path.join(OUT, f'v2_{tt:05.2f}.jpg'), quality=88)
            print('kadr', tt, flush=True)
        return
    nproc = int(os.environ.get('JOBS', os.cpu_count() or 4))
    # sahnalar bo'yicha bo'laklar (kesh samarali bo'lishi uchun ketma-ket)
    nch = int(os.environ.get('CHUNKS', 70))
    bounds = np.linspace(0, NFR, nch + 1).astype(int)
    jobs = [(c, bounds[c], bounds[c + 1]) for c in range(nch)]
    with Pool(nproc, maxtasksperchild=6) as pool:
        parts = pool.map(render_chunk, jobs, chunksize=1)
    lst = os.path.join(OUT, '_v2list.txt')
    with open(lst, 'w') as f:
        for p in parts: f.write(f"file '{p}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    os.path.join(OUT, '_v2_video.mp4')], check=True)
    for p in parts: os.remove(p)
    os.remove(lst)
    print('video tayyor', flush=True)

if __name__ == '__main__':
    main()
