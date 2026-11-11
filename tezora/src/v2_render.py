#!/usr/bin/env python3
"""TEZORA v2 — mijoz yuborgan video (assets/manba.mov) ustiga animatsiyalar: 4K 2160x3840, 60 fps.
Grafika elementlari render.py dan olinadi (subtitrlar, logotip, telefon/manzil paneli, jarayon yozuvlari, CTA).
  K=2 python3 tezora/src/v2_render.py              # to'liq video -> out/_v2_video.mp4
  K=2 python3 tezora/src/v2_render.py --stills 2 5.3 14 19.5 26 29   # nazorat kadrlari
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from render import (W, H, K, P, Caption, L, clamp, ease, eout, back, prog, paste_anim, draw_bar, draw_step, draw_list,
                    LOGO_BIG, LOGO_SMALL, STEP_IMG, STAR, CTA, TAG, NAVY, finish, bubbles)

SRC = os.path.join(R.PRJ, 'assets', 'manba.mov'); OUT = R.OUT
FPS = 60
SRC_DUR = 27.4          # mijoz videosining davomiyligi
DUR = 30.4              # + 3 s yakuniy kadr (logotip + "Hoziroq buyurtma bering!")

# ---------------------------------------------------------------- nutq vaqtlariga mos yozuvlar
CAPS = [
    Caption(0.36, 1.15, [L('ASSALOMU ALAYKUM!')], size=86, cy=1190),
    Caption(1.41, 3.45, [L('Gilamlaringizga'), L('*haqiqiy* *tozalik* kerakmi?')], size=78, cy=1190, step=0.12),
    Caption(3.60, 5.02, [L('Unda siz izlagan'), L('manzil —')], size=80, cy=1230, step=0.12),
    Caption(5.76, 7.10, [L('Biz *zamonaviy*'), L('uskunalar')], size=92, cy=1150, step=0.14),
    Caption(7.17, 9.06, [L('va *professional*'), L('yuvish texnologiyalari')], size=80, cy=1150, step=0.12),
    Caption(9.33, 10.85, [L('yordamida'), L('gilamlaringizni')], size=86, cy=1150, step=0.14),
    Caption(10.95, 12.20, [L('*tozalikka*'), L('qaytaramiz!')], size=92, cy=1150, step=0.14),
    Caption(18.51, 20.55, [L('Biz uchun har bir'), L('mijozning *ishonchi*'), L('muhim')], size=78, cy=1180, step=0.12),
    Caption(21.03, 22.65, [L('Gilamingizni'), L('*bizga* *topshiring,*')], size=88, cy=1150, step=0.14),
    Caption(23.01, 24.66, [L('tozalikni'), L('*o‘zimizga* qo‘yib'), L('bering!')], size=84, cy=1150, step=0.12),
]
STEPS = [12.66, 13.45, 14.45, 15.36]          # Yuvish, Chayish, Quritish, Sifat nazorati
LIST = (16.70, 18.40)                           # "Barchasi bir joyda!"
FLASH = [12.66, 13.45, 14.45, 15.36, SRC_DUR]
CORNER = (5.76, 25.0)                           # burchakdagi kichik logotip

# ---------------------------------------------------------------- manba kadrlar (ffmpeg: lanczos 4K + nozik sharpen)
VF = f'fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6:5:5:0.0,eq=contrast=1.04:saturation=1.08'
def src_reader(t0, dur):
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', f'{t0:.4f}', '-i', SRC, '-t', f'{dur:.4f}', '-vf', VF,
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield Image.frombuffer('RGB', (W, H), b, 'raw', 'RGB', 0, 1)
    p.wait()

LAST_PNG = os.path.join(OUT, '_v2_last.png')
def last_frame():
    if not os.path.exists(LAST_PNG):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-sseof', '-0.1', '-i', SRC, '-vf', VF, '-frames:v', '1', LAST_PNG], check=True)
    return Image.open(LAST_PNG).convert('RGB')

# yengil soya: pastki qismda panel va yozuvlar o'qilishi uchun
yy = np.linspace(0, 1, H)[:, None]
sh = (np.clip((yy - 0.52) / 0.48, 0, 1) ** 1.5 * 150 + np.clip((0.12 - yy) / 0.12, 0, 1) * 70).astype(np.uint8)
SHADE = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8) + np.array([3, 10, 28], np.uint8), np.repeat(sh, W, 1)]), 'RGBA')

def end_card(base, t):
    """27.4 s dan keyin: oxirgi kadr sekin xiralashadi va to'q ko'k qatlam bilan qoplanadi."""
    k = ease(prog(t, SRC_DUR, 0.7))
    z = 1 + 0.04 * (t - SRC_DUR) / (DUR - SRC_DUR)
    cw, ch = W / z, H / z
    im = base.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
    sm = im.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3.5 * k + 0.01)).resize((W, H), Image.BICUBIC)
    fr = Image.blend(im, sm, k).convert('RGBA')
    ov = Image.new('RGBA', (W, H), NAVY + (int(185 * k),))
    fr.alpha_composite(ov)
    bubbles(fr, t, SRC_DUR, k)
    return fr

def frame(t, fi, base):
    if t < SRC_DUR:
        fr = base.convert('RGBA'); fr.alpha_composite(SHADE)
    else:
        fr = end_card(base, t)

    if t < 0.3: fr = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), fr, ease(t / 0.3))

    # "TEZORA!" aytilganda katta logotip (1-sahna)
    kl = prog(t, 5.10, 0.45)
    if 0 < kl and t < 5.80: paste_anim(fr, LOGO_BIG, W / 2, P(1220), kl, clamp((5.78 - t) / 0.15))
    # burchakdagi kichik logotip
    a = ease(prog(t, CORNER[0], 0.5)) * clamp((CORNER[1] - t) / 0.25)
    if a > 0:
        im = LOGO_SMALL[0].copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
        fr.alpha_composite(im, (W - LOGO_SMALL[0].width + LOGO_SMALL[1] - P(50), P(110) - LOGO_SMALL[1]))

    for c in CAPS: c.draw(fr, t)
    for j, ts in enumerate(STEPS):
        te = STEPS[j + 1] if j + 1 < len(STEPS) else LIST[0]
        if ts <= t < te: draw_step(fr, t, j, ts, te)
    if LIST[0] <= t < LIST[1]: draw_list(fr, t, LIST[0], LIST[1])

    # ishonch: 5 yulduz
    if 18.6 <= t < 20.9:
        for j in range(5):
            kk = prog(t, 18.75 + j * 0.09, 0.35)
            if kk > 0: paste_anim(fr, STAR, W / 2 + P((j - 2) * 100), P(960), kk, clamp((20.75 - t) / 0.2), 0.2)

    # "TEZORA — zamonaviy tozalik xizmati!" (25.0 dan) va yakuniy kadr
    if t >= 25.0:
        ky = ease(prog(t, SRC_DUR, 0.7))
        paste_anim(fr, LOGO_BIG, W / 2, P(560 + 80 * ky), prog(t, 25.02, 0.5), 1, 0.4)
        k2 = eout(prog(t, 25.80, 0.5))
        if k2 > 0:
            im = TAG[0].copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * k2)))
            fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(P(780 + 80 * ky + (1 - k2) * 30) - im.height / 2)))
        k3 = prog(t, SRC_DUR + 0.25, 0.45)
        if k3 > 0:
            pulse = 1 + 0.045 * math.sin((t - SRC_DUR) * 2 * math.pi * 1.3) * clamp((t - SRC_DUR - 0.7) * 3)
            img, pad = CTA
            s = (0.5 + 0.5 * back(k3)) * pulse; al = clamp(k3 * 2.5)
            im = img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
            if al < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * al)))
            fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(P(1150) - im.height / 2)))

    draw_bar(fr, t)

    for tf in FLASH:
        if tf - 0.02 <= t < tf + 0.14:
            fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 255, 255, 255)), clamp((1 - (t - tf) / 0.14) * 0.45))
    if t > DUR - 0.45:
        fr = Image.blend(fr, Image.new('RGBA', (W, H), (0, 0, 0, 255)), ease((t - (DUR - 0.45)) / 0.45))
    return finish(fr, fi)

def render_part(arg):
    j, a, b = arg
    seg = os.path.join(OUT, f'_v2_part{j}.mp4')
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-threads', '1', '-pix_fmt', 'yuv420p', seg],
                           stdin=subprocess.PIPE)
    t0 = a / FPS
    rd = src_reader(t0, max(0.0, min(b / FPS, SRC_DUR) - t0) + 0.5) if t0 < SRC_DUR else iter(())
    last = None
    for i in range(a, b):
        t = i / FPS
        if t < SRC_DUR:
            base = next(rd, None) or last
            if base is None: base = last_frame()
        else:
            base = last_frame() if last is None or t - 1 / FPS < SRC_DUR else last
        last = base
        enc.stdin.write(frame(t, i, base).tobytes())
        if (i - a) % 120 == 0: print(f'[{j}] {i - a}/{b - a}', flush=True)
    enc.stdin.close(); enc.wait()
    return seg

def main():
    os.makedirs(OUT, exist_ok=True)
    if '--stills' in sys.argv:
        for s in sys.argv[sys.argv.index('--stills') + 1:]:
            t = float(s)
            base = next(src_reader(t, 0.1), None) if t < SRC_DUR else last_frame()
            Image.fromarray(frame(t, 0, base)).save(os.path.join(OUT, f'still_v2_{t:05.2f}.png')); print('kadr', t)
        return
    n = int(round(DUR * FPS)); J = int(os.environ.get('JOBS', os.cpu_count() or 4))
    parts = [(j, j * n // J, (j + 1) * n // J) for j in range(J)]
    from multiprocessing import Pool
    with Pool(J) as pool: segs = pool.map(render_part, parts)
    lst = os.path.join(OUT, '_v2_parts.txt')
    open(lst, 'w').write(''.join(f"file '{os.path.basename(x)}'\n" for x in segs))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(OUT, '_v2_video.mp4')], check=True)
    for x in segs: os.remove(x)
    print('video tayyor', f'{W}x{H}@{FPS}')

if __name__ == '__main__':
    main()
