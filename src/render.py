#!/usr/bin/env python3
"""AZDIF 45% S.C. — 68 soniyalik reklama roligi.
Format: vertikal 9:16, Ultra HD 2160x3840, 25 fps.

Barcha koordinatalar "mantiqiy" 1080x1920 o'lchamda yozilgan va K marta
kattalashtiriladi (K=2 -> 2160x3840). Tezkor sinov uchun: K=1.

Ishga tushirish:  python3 src/render.py                 (video, ovozsiz)
                  python3 src/render.py --stills 8 27   (nazorat kadrlari)
                  python3 src/audio.py && bash src/build.sh   (yakuniy mp4)
"""
import math, os, sys, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda *p: os.path.join(ROOT, 'assets', *p)
OUT = os.path.join(ROOT, 'out')
K = float(os.environ.get('K', '2'))           # 2 -> 2160x3840 (UHD 9:16)
LW, LH = 1080, 1920                            # mantiqiy o'lcham
W, H = int(LW * K), int(LH * K)
FPS = 25
DUR = 68.05
NFR = int(round(DUR * FPS))

def k(v): return v * K
def ki(v): return int(round(v * K))

# Sahnalar chegaralari — ovozdagi pauzalarga moslangan (soniya)
SCENES = [
    ('intro',    0.0,  3.1),
    ('problem',  3.1, 12.4),
    ('reveal',  12.4, 21.0),
    ('formula', 21.0, 31.2),
    ('crops',   31.2, 44.6),
    ('protect', 44.6, 57.2),
    ('pack',    57.2, DUR),
]
XF = 0.5  # sahnalararo crossfade (s)

# ---------------------------------------------------------------- utils
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in_out(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)

def font(wt, size): return ImageFont.truetype(A('fonts', f'Montserrat-{wt}.ttf'), size)
def np2im(a): return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a))); return im

def paste(base, layer, xy, alpha=1.0):
    """xy — PIKSEL koordinatasi (chap-yuqori)."""
    if alpha <= 0.002: return
    layer = with_alpha(layer, alpha)
    x, y = int(round(xy[0])), int(round(xy[1]))
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(layer.width, base.width - x), min(layer.height, base.height - y)
    if ex <= sx or ey <= sy: return
    if sx or sy or ex < layer.width or ey < layer.height:
        layer = layer.crop((sx, sy, ex, ey))
    base.alpha_composite(layer, (x + sx, y + sy))

def place(base, layer, cx, cy, alpha=1.0):
    """Markaz bo'yicha joylash, cx/cy — MANTIQIY koordinata."""
    paste(base, layer, (k(cx) - layer.width / 2, k(cy) - layer.height / 2), alpha)

def radial(w, h, cx, cy, r, color, power=2.0):
    yy, xx = np.ogrid[0:h, 0:w]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2).astype(np.float32) / r
    g = np.clip(1 - d, 0, 1) ** power
    return g[..., None] * np.array(color, np.float32)[None, None, :]

def vgrad(h, w, stops):
    ys = np.linspace(0, 1, h); out = np.zeros((h, 3), np.float32)
    ps = [s[0] for s in stops]
    for c in range(3): out[:, c] = np.interp(ys, ps, [s[1][c] for s in stops])
    return np.repeat(out[:, None, :], w, axis=1)

def fbm(w, h, octaves=5, seed=0, base=4):
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        n = base * 2 ** o
        small = rng.random((int(n * h / max(w, h)) + 2, int(n * w / max(w, h)) + 2)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        tot += amp; amp *= 0.5
    return acc / tot

def pill(w, h, color, alpha=255, radius=None):
    """w,h — PIKSEL."""
    S = 3; r = radius if radius is not None else h // 2
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * S - 1, h * S - 1), r * S, fill=color + (alpha,))
    return im.resize((w, h), Image.LANCZOS)

def check_badge(d):
    """Yashil doira ichida belgi, d — PIKSEL diametr."""
    key = ('check', d)
    if key in G: return G[key]
    im = pill(d, d, (60, 190, 80))
    dd = ImageDraw.Draw(im)
    dd.line((d * 0.27, d * 0.52, d * 0.44, d * 0.69, d * 0.75, d * 0.34), fill=(255, 255, 255, 255), width=max(2, int(d * 0.12)), joint='curve')
    G[key] = im
    return im

G = {}

# ------------------------------------------------------------- text
def text_layer(txt, wt, size, color, shadow, track, glow):
    key = ('txt', txt, wt, size, color, shadow, track, glow)
    if key in G: return G[key]
    px = ki(size); f = font(wt, px); tr = k(track)
    if tr:
        widths = [f.getlength(ch) + tr for ch in txt]; tw = int(sum(widths) - tr)
    else:
        tw = int(f.getlength(txt))
    asc, desc = f.getmetrics(); th = asc + desc
    pad = ki(40)
    im = Image.new('RGBA', (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    m = Image.new('L', im.size, 0); d = ImageDraw.Draw(m)
    if tr:
        x = pad
        for ch, wd in zip(txt, widths): d.text((x, pad), ch, font=f, fill=255); x += wd
    else:
        d.text((pad, pad), txt, font=f, fill=255)
    if shadow:
        sh = ImageChops.offset(m.filter(ImageFilter.GaussianBlur(px * 0.08)), 0, int(px * 0.05))
        sl = Image.new('RGBA', im.size, (0, 0, 0, 0)); sl.putalpha(sh.point(lambda v: int(v * 0.8)))
        im.alpha_composite(sl)
    if glow:
        gl = m.filter(ImageFilter.GaussianBlur(px * 0.25))
        gi = Image.new('RGBA', im.size, glow + (0,)); gi.putalpha(gl.point(lambda v: min(255, int(v * 1.2))))
        im.alpha_composite(gi)
    fill = Image.new('RGBA', im.size, color + (0,)); fill.putalpha(m)
    im.alpha_composite(fill)
    G[key] = (im, pad)
    return im, pad

def draw_text(base, txt, wt, size, x, y, t_in, t, color=(255, 255, 255), anchor='l', dur=0.6,
              t_out=None, slide=40, track=0, glow=None, shadow=True):
    """Mantiqiy koordinatalar. y — matn qutisining yuqori qirrasi."""
    a = ease_out(prog(t, t_in, t_in + dur))
    if t_out is not None: a *= 1 - ease_in_out(prog(t, t_out, t_out + 0.4))
    if a <= 0.003: return
    im, pad = text_layer(txt, wt, size, color, shadow, track, glow)
    tw = im.width - 2 * pad
    px = k(x)
    if anchor == 'c': px -= tw / 2
    elif anchor == 'r': px -= tw
    paste(base, im, (px - pad, k(y) - pad + k((1 - a) * slide)), a)

# ------------------------------------------------------------- assets
def bottle_img(height):
    key = ('bottle', height)
    if key not in G:
        b = Image.open(A('bottle.png')).convert('RGBA')
        hp = ki(height); w = int(b.width * hp / b.height)
        b = b.resize((w, hp), Image.LANCZOS)
        if hp > 1637: b = b.filter(ImageFilter.UnsharpMask(2, 50, 2))
        G[key] = b
    return G[key]

def bottle_comp(height, sweep=None):
    """Flakon + kontakt soya + pol aksi. Qaytaradi: (rasm, flakon_x_offset)."""
    key = ('bcomp', height)
    if key not in G:
        b = bottle_img(height); w, h = b.size
        refl_h = int(h * 0.30); ox = ki(100)
        canvas = Image.new('RGBA', (w + 2 * ox, h + refl_h + ki(60)), (0, 0, 0, 0))
        sh = Image.new('L', canvas.size, 0)
        ImageDraw.Draw(sh).ellipse((ox - ki(30), h - ki(22), ox + w + ki(30), h + ki(26)), fill=170)
        sh = sh.filter(ImageFilter.GaussianBlur(k(18)))
        sl = Image.new('RGBA', canvas.size, (0, 15, 5, 0)); sl.putalpha(sh); canvas.alpha_composite(sl)
        refl = b.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, w, refl_h))
        grad = np.linspace(0.30, 0, refl_h, dtype=np.float32)[:, None]
        refl.putalpha(Image.fromarray((np.asarray(refl.getchannel('A'), np.float32) * grad).astype(np.uint8)))
        canvas.alpha_composite(refl.filter(ImageFilter.GaussianBlur(k(2))), (ox, h + 2))
        G[key] = (canvas, ox)
    canvas, ox = G[key]
    b = bottle_img(height)
    if sweep is not None and 0 < sweep < 1: b = light_sweep(b, sweep)
    out = canvas.copy(); out.alpha_composite(b, (ox, 0))
    return out

def light_sweep(b, p, width=0.22, strength=0.8):
    w, h = b.size
    key = ('sweepgrid', w, h)
    if key not in G:
        yy, xx = np.ogrid[0:h, 0:w]
        G[key] = ((xx / w) + (yy / h) * 0.45).astype(np.float32)
    u = G[key]; c = -0.3 + p * 1.9
    band = np.exp(-((u - c) / (width * 0.5)) ** 2) * strength
    arr = np.asarray(b, np.float32).copy()
    al = arr[..., 3] / 255
    arr[..., :3] = np.minimum(255, arr[..., :3] + (band * al * 230)[..., None])
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')

def vignette():
    if 'vig' not in G:
        yy, xx = np.ogrid[0:H, 0:W]
        d = np.sqrt(((xx - W / 2) / (W * 0.70)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2).astype(np.float32)
        G['vig'] = np.clip(1 - 0.9 * np.clip(d - 0.55, 0, 1) ** 1.4, 0.35, 1)[..., None]
    return G['vig']

def grain(i):
    if 'grain' not in G:
        rng = np.random.default_rng(7)
        G['grain'] = [np.asarray(Image.fromarray(((rng.random((H // 2, W // 2)) - 0.5) * 16 + 128).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.int16) - 128
                      for _ in range(4)]
    return G['grain'][i % 4]

def rays(angle, scale=1.0, color=(255, 240, 190)):
    """Aylanuvchi nur dastasi (kichik o'lchamda aylantirib, keyin kattalashtiriladi)."""
    key = ('rays', color)
    if key not in G:
        S = 1400; rng = random.Random(3)
        m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m); c = S / 2
        for i in range(14):
            a0 = rng.uniform(0, 2 * math.pi); wd = rng.uniform(0.04, 0.12)
            d.polygon([(c, c), (c + S * math.cos(a0), c + S * math.sin(a0)), (c + S * math.cos(a0 + wd), c + S * math.sin(a0 + wd))], fill=rng.randint(50, 110))
        m = m.filter(ImageFilter.GaussianBlur(10))
        yy, xx = np.ogrid[0:S, 0:S]
        fall = np.clip(1 - np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / (S * 0.5), 0, 1) ** 1.3
        im = Image.new('RGBA', (S, S), color + (0,)); im.putalpha(Image.fromarray((np.asarray(m, np.float32) * fall).astype(np.uint8)))
        G[key] = im
    r = G[key].rotate(angle, resample=Image.BILINEAR)
    s = ki(2200 * scale)
    return r.resize((s, s), Image.BILINEAR)

def bokeh_sprites():
    if 'bokeh' in G: return G['bokeh']
    spr = []
    for r0 in (18, 30, 46, 70):
        r = ki(r0); S = r * 2 + ki(40); o = ki(20)
        m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m)
        d.ellipse((o, o, o + 2 * r, o + 2 * r), fill=120)
        d.ellipse((o + ki(3), o + ki(3), o + 2 * r - ki(3), o + 2 * r - ki(3)), fill=80)
        spr.append(m.filter(ImageFilter.GaussianBlur(r * 0.12 + 1)))
    G['bokeh'] = spr
    return spr

def draw_bokeh(base, t, seed, n=26, color=(255, 230, 160), alpha=0.6, area=(0, 0, LW, LH)):
    rng = random.Random(seed); spr = bokeh_sprites()
    for i in range(n):
        m = spr[rng.randrange(4)]
        x0 = rng.uniform(area[0], area[2]); y0 = rng.uniform(area[1], area[3])
        vx = rng.uniform(-14, 14); vy = rng.uniform(-22, -6); ph = rng.uniform(0, 6.28)
        x = x0 + vx * t + 20 * math.sin(t * 0.6 + ph); y = y0 + vy * t
        y = (y - area[1]) % (area[3] - area[1] + 200) + area[1] - 100
        a = alpha * (0.5 + 0.5 * math.sin(t * 1.1 + ph))
        col = tuple(int(c * rng.uniform(0.85, 1.0)) for c in color)
        im = Image.new('RGBA', m.size, col + (0,)); im.putalpha(m.point(lambda v: int(v * a)))
        place(base, im, x, y)

# ---------------------------------------------------- landscape
def landscape():
    """Quyosh chiqishidagi uzumzor (vertikal, mantiqiy 1200x2000)."""
    if 'land' in G: return G['land']
    QW, QH = ki(1200), ki(2000)
    s = K
    hz = int(QH * 0.40)
    sky = vgrad(QH, QW, [(0, (34, 70, 132)), (0.22, (110, 145, 190)), (0.36, (250, 200, 150)), (0.40, (255, 225, 170)), (1, (255, 225, 170))])
    sun = (QW * 0.66, hz - 20 * s)
    sky += radial(QW, QH, *sun, 700 * s, (255, 200, 120), 2.2) * 0.9
    sky += radial(QW, QH, *sun, 90 * s, (255, 250, 230), 1.5)
    img = np2im(sky).convert('RGBA')
    rng = np.random.default_rng(2)
    for li, (by, amp, col) in enumerate([(hz - 26 * s, 40 * s, (150, 160, 170)), (hz - 5 * s, 30 * s, (110, 135, 125)), (hz + 12 * s, 20 * s, (78, 112, 82))]):
        xs = np.arange(0, QW + 10, 8)
        ph = rng.uniform(0, 6, 3)
        ys = by - amp * (0.6 * np.sin(xs / (200 * s) + ph[0]) + 0.3 * np.sin(xs / (80 * s) + ph[1]) + 0.1 * np.sin(xs / (30 * s) + ph[2]))
        poly = [(0, QH)] + list(zip(xs.tolist(), ys.tolist())) + [(QW, QH)]
        layer = Image.new('RGBA', (QW, QH), (0, 0, 0, 0)); ImageDraw.Draw(layer).polygon(poly, fill=col + (255,))
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur((3 - li) * s)))
    gh = QH - hz - int(8 * s)
    ground = vgrad(gh, QW, [(0, (96, 120, 60)), (1, (70, 62, 40))]) * (0.8 + 0.4 * fbm(QW, gh, 5, seed=4, base=6)[..., None])
    img.alpha_composite(np2im(ground).convert('RGBA'), (0, QH - gh))
    vpx, vpy = QW * 0.52, hz + 6 * s
    rows = Image.new('RGBA', (QW, QH), (0, 0, 0, 0)); dr = ImageDraw.Draw(rows)
    rr = random.Random(5)
    greens = [(52, 96, 38), (66, 118, 44), (84, 138, 52), (40, 80, 32), (98, 150, 60), (120, 160, 70)]
    xs_bottom = np.linspace(-3200 * s, 4400 * s, 17)
    blobs = []
    bottom = QH + 200 * s
    for xb in xs_bottom:
        for kk in range(600):
            f = (kk / 600) ** 1.9
            x = vpx + (xb - vpx) * f; y = vpy + (bottom - vpy) * f
            if y > QH + 100 * s or x < -200 * s or x > QW + 200 * s: continue
            r = (1.5 + 110 * f) * s; hgt = (1 + 380 * f) * s
            for j in range(2):
                jx = rr.uniform(-0.6, 0.6) * r; jy = -rr.uniform(0.0, 1.0) * hgt
                col = rr.choice(greens); lit = 1 + 0.25 * (-(jy / max(hgt, 1)))
                blobs.append((y, x + jx, y + jy, r * rr.uniform(0.5, 1.0), tuple(min(255, int(c * lit)) for c in col)))
    blobs.sort(key=lambda b: b[0])
    for _, x, y, r, col in blobs:
        dr.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=col + (255,))
    for i in range(220):
        f = rr.uniform(0.5, 1.0); xb = rr.choice(xs_bottom)
        x = vpx + (xb - vpx) * f + rr.uniform(-30, 30) * f * s; y = vpy + (bottom - vpy) * f - rr.uniform(0.2, 0.7) * 380 * f * s
        if not (-50 * s < x < QW + 50 * s and y < QH): continue
        rg = (7 * f + 2) * s; col = rr.choice([(92, 40, 82), (120, 50, 100), (190, 200, 90), (70, 30, 60)])
        for gy in range(7):
            nrow = max(1, 5 - gy * 4 // 6)
            for gx in range(nrow):
                cx = x + (gx - (nrow - 1) / 2) * rg * 1.55 + rr.uniform(-0.3, 0.3) * rg
                cy = y + gy * rg * 1.35 + rr.uniform(-0.3, 0.3) * rg
                rb = rg * rr.uniform(0.85, 1.1)
                shade = tuple(int(c * rr.uniform(0.8, 1.1)) for c in col)
                dr.ellipse((cx - rb, cy - rb, cx + rb, cy + rb), fill=shade + (255,))
                dr.ellipse((cx - rb * 0.5, cy - rb * 0.55, cx - rb * 0.1, cy - rb * 0.15), fill=(255, 255, 255, 80))
    far = rows.crop((0, 0, QW, hz + int(160 * s))).filter(ImageFilter.GaussianBlur(1.5 * s))
    rows.paste(far, (0, 0))
    img.alpha_composite(rows)
    arr = np.asarray(img.convert('RGB'), np.float32)
    arr += radial(QW, QH, *sun, 900 * s, (90, 60, 20), 1.6)
    G['land'] = np2im(arr)
    return G['land']

def land_view(t, z0, z1, T, cx=0.52, cy=0.5, small=False):
    L = landscape(); z = z0 + (z1 - z0) * ease_in_out(t / T)
    cw = L.width / z; ch = cw * H / W
    if ch > L.height: ch = L.height; cw = ch * W / H
    px, py = cx * L.width, cy * L.height
    px = min(max(px, cw / 2), L.width - cw / 2); py = min(max(py, ch / 2), L.height - ch / 2)
    box = (px - cw / 2, py - ch / 2, px + cw / 2, py + ch / 2)
    size = (W // 8, H // 8) if small else (W, H)
    return L.resize(size, Image.BICUBIC, box=box)

# ------------------------------------------------------------- leaf
LEAF = 1000  # mantiqiy o'lcham

def make_leaf(seed=1):
    key = ('leaf', seed)
    if key in G: return G[key]
    S = ki(LEAF)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    cx, cy = S * 0.5, S * 0.62
    dx, dy = xx - cx, yy - cy
    th = np.arctan2(dx, -dy); rr = np.hypot(dx, dy)
    lobes = 0.70 + 0.22 * np.cos(th * 2.5) ** 2
    lobes *= 1 - 0.38 * np.clip(np.abs(th) / math.pi - 0.72, 0, 1) * 3.2
    ser = 1 + 0.035 * np.sin(th * 34) + 0.02 * np.sin(th * 61 + 1)
    R = S * 0.43 * lobes * ser
    inside = np.clip((R - rr) / (2.5 * K), 0, 1)
    n1 = fbm(S, S, 6, seed=seed + 10, base=5); n2 = fbm(S, S, 4, seed=seed + 20, base=24)
    base = np.stack([40 + 30 * n1, 120 + 50 * n1, 35 + 20 * n1], -1)
    light = np.clip(1.05 - 0.45 * ((dx + dy) / (S * 0.6)), 0.55, 1.3)
    edge = np.clip(rr / np.maximum(R, 1), 0, 1)
    base *= (light * (0.95 + 0.1 * n2) * (1 - 0.18 * edge ** 3))[..., None]
    vm = Image.new('L', (S, S), 0); d = ImageDraw.Draw(vm)
    sc = S / 1300
    for ang, ln, wd in [(0, 0.42, 14), (-1.05, 0.40, 11), (1.05, 0.40, 11), (-2.05, 0.30, 9), (2.05, 0.30, 9)]:
        x2 = cx + math.sin(ang) * S * ln; y2 = cy - math.cos(ang) * S * ln
        d.line((cx, cy, x2, y2), fill=255, width=max(2, int(wd * sc)))
        for kk in range(1, 7):
            f = kk / 7; px = cx + (x2 - cx) * f; py = cy + (y2 - cy) * f
            for sgn in (-1, 1):
                a2 = ang + sgn * 0.75; l2 = S * 0.11 * (1 - f * 0.6)
                d.line((px, py, px + math.sin(a2) * l2, py - math.cos(a2) * l2), fill=150, width=max(2, int(wd * sc / 3)))
    vm = vm.filter(ImageFilter.GaussianBlur(1.6 * sc))
    v = np.asarray(vm, np.float32)[..., None] / 255
    base = base * (1 - 0.25 * v) + np.array([170, 205, 120]) * v * 0.55
    stem = ((np.abs(dx) < 9 * sc) & (dy > 0) & (dy < S * 0.36)).astype(np.float32)
    stem = np.asarray(Image.fromarray((stem * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2 * sc)), np.float32) / 255
    alpha = np.maximum(inside, stem)
    rgb = base * (1 - stem[..., None]) + np.array([110, 150, 60]) * stem[..., None]
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8), 'RGBA')
    yel = (0.38 * 1.4 * fbm(S, S, 3, seed=31, base=3))[..., None].astype(np.float32)
    G[key] = (im, inside.astype(np.float32), yel)
    return G[key]

def spots_list(seed=4, n=26):
    key = ('spots', seed)
    if key in G: return G[key]
    rng = random.Random(seed); out = []
    S = ki(LEAF); _, inside, _ = make_leaf()
    while len(out) < n:
        x = rng.uniform(S * 0.15, S * 0.85); y = rng.uniform(S * 0.2, S * 0.8)
        if inside[int(y), int(x)] < 1: continue
        out.append((x, y, rng.uniform(17, 54) * K, rng.uniform(0, 0.7)))
    G[key] = out
    return out

def spot_sprite(r):
    r = max(3, int(r)); key = ('spot', r)
    if key in G: return G[key]
    S = int(r * 3.2) + 4; c = S / 2
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    rng = np.random.default_rng(r)
    th = np.arctan2(yy - c, xx - c)
    d = np.hypot(xx - c, yy - c) / (r * (1 + 0.05 * np.sin(th * 3 + r) + 0.03 * np.sin(th * 7)))
    core = np.clip((1 - d) * 4, 0, 1)
    ring = np.clip(1 - np.abs(d - 0.85) * 5, 0, 1)
    halo = np.clip((1.55 - d) * 1.6, 0, 1) * (1 - core)
    nz = np.asarray(Image.fromarray((rng.random((S, S)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    rgb = (core[..., None] * (np.array([92, 62, 34]) * (0.75 + 0.5 * nz[..., None])) + ring[..., None] * np.array([60, 38, 20]) * 0.6
           + halo[..., None] * np.array([196, 178, 60]))
    a = np.clip(core + ring * 0.8 + halo * 0.75, 0, 1)
    rgb = np.where(a[..., None] > 0, rgb / np.maximum(core + ring * 0.6 + halo, 1e-3)[..., None], 0)
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA')
    G[key] = im
    return im

def mildew():
    if 'mildew' in G: return G['mildew']
    S = ki(LEAF)
    n = fbm(S, S, 6, seed=8, base=6)
    m = np.clip((n - 0.52) * 4.5, 0, 1) * (0.55 + 0.45 * np.random.default_rng(8).random((S, S)).astype(np.float32))
    im = Image.new('RGBA', (S, S), (235, 235, 225, 0))
    im.putalpha(Image.fromarray((m * 200).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2 * K)))
    G['mildew'] = im
    return im

def diseased_leaf(sick, heal_boost=0.0):
    leaf, inside, yel = make_leaf()
    if sick <= 0.001 and heal_boost <= 0: return leaf
    arr = np.asarray(leaf, np.float32).copy()
    if sick > 0.001:
        kk = yel * sick
        arr[..., :3] = arr[..., :3] * (1 - kk) + np.array([150, 140, 50], np.float32) * kk
    if heal_boost > 0:
        arr[..., :3] = np.minimum(255, arr[..., :3] * (1 + 0.18 * heal_boost))
    lf = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    if sick <= 0.001: return lf
    S = leaf.width
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    for (x, y, r, delay) in spots_list():
        g = clamp((sick - delay * 0.6) / 0.5)
        if g <= 0.02: continue
        sp = spot_sprite(max(3, r * ease_out(g)))
        lay.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
    lay.alpha_composite(with_alpha(mildew(), clamp(sick * 1.2 - 0.25)))
    la = np.asarray(lay.getchannel('A'), np.float32) * inside
    lay.putalpha(Image.fromarray(la.astype(np.uint8)))
    lf.alpha_composite(lay)
    return lf

def leaf_draw(img, lf, cx, cy, size, rot):
    """Bargni soyasi bilan chizish (mantiqiy cx, cy, size)."""
    s = ki(size)
    lfi = lf.resize((s, s), Image.BILINEAR).rotate(rot, resample=Image.BICUBIC)
    small = lfi.getchannel('A').resize((s // 8, s // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4))
    shd = small.resize((s, s), Image.BILINEAR).point(lambda v: int(v * 0.5))
    sl = Image.new('RGBA', (s, s), (0, 0, 0, 0)); sl.putalpha(shd)
    place(img, sl, cx + 25, cy + 35)
    place(img, lfi, cx, cy)
    return s

def leaf_bg(warm=False):
    key = ('leafbg', warm)
    if key not in G:
        w8, h8 = W // 4, H // 4
        if warm: g = vgrad(h8, w8, [(0, (30, 50, 25)), (0.6, (60, 80, 35)), (1, (25, 35, 18))])
        else: g = vgrad(h8, w8, [(0, (16, 46, 26)), (0.5, (34, 86, 44)), (1, (10, 30, 18))])
        g = g * (0.7 + 0.6 * fbm(w8, h8, 4, seed=12, base=3)[..., None])
        g += radial(w8, h8, w8 * 0.8, h8 * 0.15, w8 * 0.9, (90, 80, 30), 2)
        G[key] = np2im(g).resize((W, H), Image.BICUBIC).convert('RGBA')
    return G[key].copy()

# ------------------------------------------------------------- droplets / sparkles
def droplet_sprite(r0):
    r = ki(r0); key = ('drop', r)
    if key in G: return G[key]
    S = int(r * 2.6) + 4; c = S / 2
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.hypot((xx - c) / r, (yy - c) / (r * 1.15))
    a = np.clip((1 - d) * r * 0.6, 0, 1)
    rim = np.clip(d * 1.3, 0, 1) ** 3
    hl = np.clip(1 - np.hypot((xx - c + r * 0.35) / (r * 0.28), (yy - c + r * 0.4) / (r * 0.22)), 0, 1)
    rgb = np.zeros((S, S, 3), np.float32) + np.array([200, 230, 245]) * (0.55 + 0.45 * rim[..., None])
    rgb = rgb * (1 - hl[..., None]) + 255 * hl[..., None]
    al = a * (0.35 + 0.5 * rim + 0.6 * hl)
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(al, 0, 1) * 255]).astype(np.uint8), 'RGBA')
    G[key] = im
    return im

def mist(t, base, alpha, src, seed=11):
    if alpha <= 0.01: return
    rng = random.Random(seed)
    for i in range(150):
        life = rng.uniform(1.2, 2.4); off = rng.uniform(0, life)
        p = ((t + off) % life) / life
        ang = math.radians(rng.uniform(100, 140)); sp = rng.uniform(900, 1500)
        x = src[0] + math.cos(ang) * sp * p * life * 0.6 + rng.uniform(-60, 60)
        y = src[1] + math.sin(ang) * sp * p * life * 0.6 + rng.uniform(-60, 60)
        a = alpha * math.sin(p * math.pi) * 0.85
        place(base, droplet_sprite(rng.choice([4, 6, 8, 11])), x, y, a)

def sparkle_sprite(r0):
    r = ki(r0); key = ('spk', r)
    if key in G: return G[key]
    S = r * 4; m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m); c = S / 2; q = r * 0.12
    d.polygon([(c, 0), (c + q, c - q), (S, c), (c + q, c + q), (c, S), (c - q, c + q), (0, c), (c - q, c - q)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(K))
    g = Image.new('L', (S, S), 0); ImageDraw.Draw(g).ellipse((c - r * 0.5, c - r * 0.5, c + r * 0.5, c + r * 0.5), fill=200)
    m = ImageChops.lighter(m, g.filter(ImageFilter.GaussianBlur(r * 0.25)))
    im = Image.new('RGBA', (S, S), (255, 250, 220, 0)); im.putalpha(m)
    G[key] = im
    return im

def sparkles(base, t, seed, n, area, alpha=1.0):
    if alpha <= 0.01: return
    rng = random.Random(seed)
    for i in range(n):
        x = rng.uniform(area[0], area[2]); y = rng.uniform(area[1], area[3])
        per = rng.uniform(1.0, 2.2); ph = rng.uniform(0, per)
        p = ((t + ph) % per) / per
        place(base, sparkle_sprite(rng.choice([10, 14, 20])), x, y, alpha * max(0, math.sin(p * math.pi)) ** 2)

# ------------------------------------------------------------- molecule / orb
def molecule(size, color=(255, 255, 255)):
    key = ('mol', size)
    if key in G: return G[key]
    px = ki(size); S = px * 3
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def hexa(cx, cy, r):
        return [(cx + r * math.cos(math.radians(60 * j + 30)), cy + r * math.sin(math.radians(60 * j + 30))) for j in range(6)]
    r = S * 0.16
    centers = [(S * 0.38, S * 0.45), (S * 0.38 + r * 1.732, S * 0.45), (S * 0.38 + r * 0.866, S * 0.45 + r * 1.5)]
    lw = max(3, S // 60)
    for c in centers:
        pts = hexa(*c, r); d.line(pts + [pts[0]], fill=color + (255,), width=lw, joint='curve')
        for p in pts: d.ellipse((p[0] - lw * 1.6, p[1] - lw * 1.6, p[0] + lw * 1.6, p[1] + lw * 1.6), fill=(255, 255, 255, 255))
    p = hexa(*centers[0], r)[3]; d.line((p[0], p[1], p[0] - r, p[1] - r * 0.6), fill=color + (255,), width=lw)
    d.ellipse((p[0] - r - lw * 3, p[1] - r * 0.6 - lw * 3, p[0] - r + lw * 3, p[1] - r * 0.6 + lw * 3), fill=(255, 90, 80, 255))
    G[key] = im.resize((px, px), Image.LANCZOS)
    return G[key]

def orb(size, color):
    key = ('orb', size, color)
    if key in G: return G[key]
    S = ki(size); c = S / 2
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.hypot(xx - c, yy - c) / (S * 0.5)
    body = np.clip((1 - d) * 40, 0, 1); glow = np.clip(1 - d, 0, 1) ** 0.6; edge = np.clip(d, 0, 1) ** 6
    hl = np.clip(1 - np.hypot((xx - c * 0.7) / (S * 0.22), (yy - c * 0.55) / (S * 0.12)), 0, 1) ** 1.5
    col = np.array(color, np.float32)
    rgb = col * (0.35 + 0.4 * glow[..., None]) + 255 * edge[..., None] * 0.6 + 255 * hl[..., None] * 0.6
    a = body * (0.45 + 0.5 * edge + 0.5 * hl)
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 1) * 255]).astype(np.uint8), 'RGBA')
    g = Image.new('L', (int(S * 1.6), int(S * 1.6)), 0)
    ImageDraw.Draw(g).ellipse((S * 0.3, S * 0.3, S * 1.3, S * 1.3), fill=120)
    out = Image.new('RGBA', g.size, color + (0,)); out.putalpha(g.filter(ImageFilter.GaussianBlur(S * 0.1)))
    out.alpha_composite(im, (int(S * 0.3), int(S * 0.3)))
    G[key] = out
    return out

# ------------------------------------------------------------- crop cards
def card(name, w, h, zoom):
    """w,h — PIKSEL."""
    key = ('cardsrc', name, w, h)
    if key not in G:
        im = Image.open(A(f'crop_{name}.png')).convert('RGB')
        sc = max(w / im.width, h / im.height) * 1.15
        big = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2 * K, 60, 2))
        G[key] = big
    big = G[key]
    cw, ch = w / zoom * 1.15, h / zoom * 1.15
    bw, bh = big.size
    box = ((bw - cw * bw / (w * 1.15)) / 2, (bh - ch * bh / (h * 1.15)) / 2, 0, 0)
    fw = w * bw / (w * 1.15) / zoom * 1.0; fh = h * bh / (h * 1.15) / zoom
    fw = min(fw, bw); fh = min(fh, bh)
    box = ((bw - fw) / 2, (bh - fh) / 2, (bw + fw) / 2, (bh + fh) / 2)
    ph = big.resize((w, h), Image.BICUBIC, box=box).convert('RGBA')
    mk = ('cardmask', w, h)
    if mk not in G: G[mk] = pill(w, h, (255, 255, 255), 255, radius=ki(28)).getchannel('A')
    ph.putalpha(G[mk])
    return ph

def card_frame(w, h):
    key = ('cframe', w, h)
    if key in G: return G[key]
    pad = ki(40)
    im = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((pad, pad + ki(14), pad + w, pad + h + ki(14)), ki(30), fill=150)
    s = Image.new('RGBA', im.size, (0, 0, 0, 0)); s.putalpha(sh.filter(ImageFilter.GaussianBlur(k(16)))); im.alpha_composite(s)
    S = 2; br = Image.new('RGBA', (im.width * S, im.height * S), (0, 0, 0, 0))
    b5 = ki(5)
    ImageDraw.Draw(br).rounded_rectangle(((pad - b5) * S, (pad - b5) * S, (pad + w + b5) * S, (pad + h + b5) * S), (ki(28) + b5) * S, fill=(255, 255, 255, 255))
    im.alpha_composite(br.resize(im.size, Image.LANCZOS))
    G[key] = (im, pad)
    return G[key]

def bg_grad(stops, glow=None):
    key = ('bg', tuple(stops), glow)
    if key not in G:
        w4, h4 = W // 4, H // 4
        g = vgrad(h4, w4, stops)
        if glow: g += radial(w4, h4, w4 * glow[0], h4 * glow[1], w4 * glow[2], glow[3], 1.6)
        G[key] = np2im(g).resize((W, H), Image.BICUBIC).convert('RGBA')
    return G[key].copy()

# ================================================================ SCENES
GOLD = (255, 205, 80); RED = (225, 60, 45); WHITE = (255, 255, 255)
CX = LW / 2

def sc_intro(t, T):
    img = land_view(t, 1.0, 1.12, T + 0.6, cx=0.6, cy=0.45).convert('RGBA')
    place(img, rays(t * 2.5), 0.66 * 1200 * (LW / 1200), 0.40 * LH - 40, 0.35)
    draw_bokeh(img, t, 1, 18, alpha=0.45, area=(0, 0, LW, LH * 0.6))
    if 'introshade' not in G:
        g = np.zeros((H, 1), np.float32); ys = np.linspace(0, 1, H)
        g[:, 0] = np.clip(1 - ys / 0.42, 0, 1) ** 1.3 * 150
        sh = Image.new('RGBA', (W, H), (5, 20, 40, 0)); sh.putalpha(np2im(np.repeat(g, W, 1)).convert('L'))
        G['introshade'] = sh
    img.alpha_composite(G['introshade'])
    draw_text(img, "SOG'LOM BOG' —", 800, 64, CX, 300, 0.4, t, anchor='c', track=6)
    draw_text(img, "MO'L HOSIL", 900, 110, CX, 390, 0.7, t, anchor='c', color=GOLD, track=4, glow=(255, 180, 60))
    draw_text(img, "GAROVI", 900, 110, CX, 520, 0.9, t, anchor='c', color=GOLD, track=4, glow=(255, 180, 60))
    return img, ease_out(prog(t, 0, 1.2))

def sc_problem(t, T):
    img = leaf_bg(warm=True)
    sick = ease_in_out(prog(t, 0.3, T - 1.2))
    lf = diseased_leaf(sick)
    leaf_draw(img, lf, CX + 40, 1330 + 12 * math.sin(t * 0.8), 1000 * (0.95 + 0.08 * ease_in_out(t / T)), -8 + 4 * math.sin(t * 0.5))
    if sick > 0.01:
        arr = np.asarray(img.convert('RGB'), np.float32); kk = 0.16 * sick
        arr *= (1 - kk) + np.array([1.25, 0.8, 0.7], np.float32) * kk
        img = np2im(arr).convert('RGBA')
    draw_text(img, "ZAMBURUG'", 900, 96, 80, 190, 0.4, t, track=3)
    draw_text(img, "KASALLIKLARI", 900, 96, 80, 300, 0.6, t, track=3)
    draw_text(img, "hosilingizni yo'q qiladi", 700, 54, 80, 425, 0.9, t, color=(255, 210, 190))
    for i, (lb, ti) in enumerate([("Un shudring", 3.0), ("Barg dog'lanishi", 4.6), ("Mildyu, chirish", 6.2)]):
        y = 560 + i * 82
        a = ease_out(prog(t, ti, ti + 0.5))
        if a > 0: place(img, pill(ki(20), ki(20), RED), 92, y + 36 + (1 - a) * 30, a)
        draw_text(img, lb, 700, 46, 124, y, ti, t)
    return img, 1.0

def sc_reveal(t, T):
    img = bg_grad([(0, (8, 38, 20)), (0.55, (22, 92, 44)), (1, (6, 26, 14))], (0.5, 0.48, 0.9, (60, 140, 60)))
    place(img, rays(t * 6, 1.3), CX, 900, 0.55 * ease_out(prog(t, 0.2, 1.5)))
    draw_bokeh(img, t, 3, 34, color=(200, 255, 170), alpha=0.5)
    p = ease_back(prog(t, 0.2, 1.6))
    comp = bottle_comp(1000, prog(t, 1.4, 2.6))
    z = 0.92 + 0.08 * p + 0.03 * ease_in_out(t / T)
    comp = comp.resize((int(comp.width * z), int(comp.height * z)), Image.BICUBIC)
    paste(img, comp, (k(CX) - comp.width / 2, k(360) + k((1 - p) * 600) - k(1000) * (z - 1) * 0.5), clamp(p * 1.4))
    sparkles(img, t, 9, 12, (CX - 330, 380, CX + 330, 1350), alpha=ease_out(prog(t, 1.6, 2.2)))
    draw_text(img, "YANGI FUNGITSID", 800, 52, CX, 160, 2.2, t, anchor='c', color=GOLD, track=10)
    draw_text(img, "AZDIF 45% S.C.", 900, 112, CX, 1450, 2.9, t, anchor='c', track=2)
    draw_text(img, "Hosilingiz ishonchli", 700, 54, CX, 1640, 3.8, t, anchor='c', color=(230, 255, 220))
    draw_text(img, "himoyada", 700, 54, CX, 1712, 4.0, t, anchor='c', color=(230, 255, 220))
    fl = 1 - ease_out(prog(t, 0.0, 0.6))
    if fl > 0:
        arr = np.asarray(img.convert('RGB'), np.float32) + 255 * fl * 0.6
        img = np2im(arr).convert('RGBA')
    return img, 1.0

def sc_formula(t, T):
    img = bg_grad([(0, (6, 30, 22)), (1, (14, 64, 40))], (0.5, 0.3, 0.9, (50, 120, 60)))
    gr = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(gr)
    off = k((t * 20) % 90); step = ki(90)
    for x in range(-step, W + step, step): d.line((x + off, 0, x + off, H), fill=(140, 220, 160, 18), width=max(1, ki(1)))
    for y in range(-step, H + step, step): d.line((0, y + off, W, y + off), fill=(140, 220, 160, 18), width=max(1, ki(1)))
    img.alpha_composite(gr)
    p = ease_out(prog(t, 0, 1.0))
    comp = bottle_comp(640)
    place(img, comp, CX, 120 + comp.height / K / 2 + 6 * math.sin(t * 0.9) - (1 - p) * 200, p)
    items = [("AZOKSISTROBIN", "250 g/l", (60, 170, 255), 1.0, 1000),
             ("DIFENOKONAZOL", "200 g/l", (255, 170, 50), 2.2, 1300)]
    for name, dose, col, ti, y in items:
        a = ease_back(prog(t, ti, ti + 0.8))
        if a <= 0: continue
        o = orb(200, col); s = max(1, int(o.width * clamp(a, 0, 1.2)))
        ox, oy = 190, y + 8 * math.sin(t * 1.3 + ti)
        place(img, o.resize((s, s), Image.BICUBIC), ox, oy, clamp(a))
        mol = molecule(140).rotate(t * 20 * (1 if ti < 2 else -1), resample=Image.BICUBIC)
        ms = max(1, int(mol.width * clamp(a))); place(img, mol.resize((ms, ms), Image.BICUBIC), ox, oy, clamp(a))
        draw_text(img, name, 900, 60, 330, y - 75, ti + 0.3, t, track=2)
        draw_text(img, dose, 800, 56, 330, y + 5, ti + 0.5, t, color=col)
    draw_text(img, "+", 900, 80, 190, 1100, 2.0, t, anchor='c')
    draw_text(img, "Ikki faol modda —", 800, 52, CX, 1520, 4.2, t, anchor='c', color=GOLD)
    draw_text(img, "ikki tomonlama kuchli himoya", 800, 52, CX, 1590, 4.4, t, anchor='c', color=GOLD)
    draw_text(img, "Preparat shakli: suspenziya konsentrati", 600, 36, CX, 1720, 5.0, t, anchor='c', color=(210, 240, 220))
    return img, 1.0

def sc_crops(t, T):
    L = land_view(t, 1.2, 1.32, T, cx=0.5, cy=0.7, small=True)
    img = L.filter(ImageFilter.GaussianBlur(2.5)).resize((W, H), Image.BICUBIC).convert('RGBA')
    img.alpha_composite(Image.new('RGBA', (W, H), (0, 25, 10, 120)))
    draw_bokeh(img, t, 5, 20, alpha=0.35)
    draw_text(img, "QAYSI EKINLAR", 900, 76, CX, 130, 0.2, t, anchor='c', track=4)
    draw_text(img, "UCHUN?", 900, 76, CX, 225, 0.35, t, anchor='c', track=4, color=GOLD)
    names = [('grapes', 'Uzum'), ('tomato', 'Pomidor'), ('peach', 'Shaftoli'), ('beans', 'Loviya')]
    cw, ch, gap = 440, 520, 40
    x0 = (LW - (2 * cw + gap)) / 2
    for i, (key, lb) in enumerate(names):
        ti = 0.6 + i * 1.6
        a = ease_back(prog(t, ti, ti + 0.8))
        if a <= 0: continue
        aa = clamp(a)
        x = x0 + (i % 2) * (cw + gap); y = 400 + (i // 2) * (ch + 70) + (1 - aa) * 200
        fr, pad = card_frame(ki(cw), ki(ch))
        paste(img, fr, (k(x) - pad, k(y) - pad), aa)
        paste(img, card(key, ki(cw), ki(ch), 1.0 + 0.12 * prog(t, ti, T)), (k(x), k(y)), aa)
        paste(img, pill(ki(cw - 100), ki(76), (30, 120, 50), 240), (k(x + 50), k(y + ch - 40)), aa)
        draw_text(img, lb, 800, 42, x + cw / 2, y + ch - 39, ti + 0.3, t, anchor='c', slide=0)
        ca = ease_back(prog(t, ti + 0.6, ti + 1.0))
        if ca > 0:
            ck = check_badge(ki(72)); s = max(1, int(ck.width * ca))
            place(img, ck.resize((s, s), Image.BICUBIC), x + cw - 30, y + 30, clamp(ca))
    draw_text(img, "Uzumzor, bog' va", 700, 50, CX, 1600, 7.6, t, anchor='c', color=(235, 255, 225))
    draw_text(img, "sabzavot ekinlari uchun", 700, 50, CX, 1670, 7.8, t, anchor='c', color=(235, 255, 225))
    return img, 1.0

def sc_protect(t, T):
    img = leaf_bg()
    heal = ease_in_out(prog(t, 2.2, 8.5))
    lf = diseased_leaf(1 - heal, heal)
    cx, cy = CX, 640 + 8 * math.sin(t * 0.8)
    size = 920 * (0.95 + 0.06 * ease_in_out(t / T))
    leaf_draw(img, lf, cx, cy, size, 6 + 3 * math.sin(t * 0.5))
    mist(t, img, ease_out(prog(t, 0.3, 1.0)) * (1 - ease_in_out(prog(t, 7.5, 9.0))), src=(1000, -120))
    rng = random.Random(21)
    for i in range(34):
        ti = rng.uniform(0.8, 5.0)
        a = ease_out(prog(t, ti, ti + 0.3))
        x = cx + rng.uniform(-0.33, 0.33) * size; y = cy + rng.uniform(-0.3, 0.25) * size
        r = rng.choice([6, 8, 10, 13])
        if a > 0: place(img, droplet_sprite(r), x, y, a * 0.9)
    if heal > 0.3:
        sparkles(img, t, 13, 16, (cx - size * 0.35, cy - size * 0.35, cx + size * 0.35, cy + size * 0.3), alpha=clamp((heal - 0.3) * 2))
    draw_text(img, "TEZ TA'SIR", 900, 72, CX, 1150, 1.0, t, anchor='c', track=2)
    draw_text(img, "UZOQ MUDDATLI HIMOYA", 900, 60, CX, 1240, 1.6, t, anchor='c', color=GOLD, track=2)
    for i, it in enumerate(["Kasallikni to'xtatadi", "Bargni sog'lom saqlaydi", "Hosil sifatini oshiradi"]):
        ti = 3.4 + i * 1.7; y = 1400 + i * 100
        a = ease_back(prog(t, ti, ti + 0.6))
        if a > 0:
            ck = check_badge(ki(58)); s = max(1, int(ck.width * a))
            place(img, ck.resize((s, s), Image.BICUBIC), 180, y + 38, clamp(a))
        draw_text(img, it, 700, 50, 236, y, ti, t)
    return img, 1.0

def sc_pack(t, T):
    img = bg_grad([(0, (10, 46, 24)), (0.5, (34, 110, 50)), (0.52, (24, 80, 38)), (1, (8, 30, 16))], (0.5, 0.35, 0.95, (70, 150, 60)))
    place(img, rays(t * 4, 1.3), CX, 640, 0.45)
    draw_bokeh(img, t, 8, 30, color=(220, 255, 180), alpha=0.45)
    p = ease_out(prog(t, 0, 1.0))
    comp = bottle_comp(860, prog(t, 1.0, 2.2))
    z = 1.0 + 0.04 * ease_in_out(t / T)
    comp = comp.resize((int(comp.width * z), int(comp.height * z)), Image.BICUBIC)
    paste(img, comp, (k(CX) - comp.width / 2, k(200) - k(860) * (z - 1) * 0.5 + k((1 - p) * 150)), p)
    sparkles(img, t, 17, 9, (CX - 300, 220, CX + 300, 1050), alpha=0.8 * ease_out(prog(t, 1.5, 2.5)))
    draw_text(img, "FUNGITSID", 800, 44, CX, 90, 0.4, t, anchor='c', color=GOLD, track=14)
    draw_text(img, "AZDIF", 900, 170, CX, 1150, 0.6, t, anchor='c', glow=(140, 255, 120), track=6)
    draw_text(img, "45% S.C.", 900, 84, CX, 1350, 0.9, t, anchor='c', color=GOLD, track=4)
    draw_text(img, "Azoksistrobin 250 g/l + Difenokonazol 200 g/l", 600, 34, CX, 1475, 1.3, t, anchor='c', color=(220, 245, 225))
    a = ease_back(prog(t, 1.8, 2.4))
    if a > 0:
        place(img, pill(ki(340), ki(90), (255, 205, 80)), CX, 1600 + (1 - clamp(a)) * 40, clamp(a))
        draw_text(img, "HAJMI: 500 ml", 900, 42, CX, 1572, 1.8, t, anchor='c', color=(30, 60, 20), shadow=False, slide=40)
    draw_text(img, "Sog'lom hosil — farovon hayot!", 800, 50, CX, 1690, 2.8, t, anchor='c')
    sa = ease_out(prog(t, 3.2, 3.8))
    if sa > 0:
        paste(img, Image.new('RGBA', (W, ki(120)), (0, 0, 0, 150)), (0, H - ki(120)), sa)
        draw_text(img, "Bolalar qo'li yetmaydigan joyda saqlang.", 600, 32, CX, 1806, 3.2, t, anchor='c', color=(235, 235, 235), slide=0)
        draw_text(img, "Qo'llashdan oldin yo'riqnomani o'qing.", 600, 32, CX, 1856, 3.3, t, anchor='c', color=(235, 235, 235), slide=0)
    return img, 1 - ease_in_out(prog(t, T - 0.8, T))

SCENE_FN = {'intro': sc_intro, 'problem': sc_problem, 'reveal': sc_reveal, 'formula': sc_formula,
            'crops': sc_crops, 'protect': sc_protect, 'pack': sc_pack}

def frame(i):
    t = i / FPS
    out = None
    for idx, (n, a, b) in enumerate(SCENES):
        s0 = a - (XF / 2 if idx > 0 else 0)
        s1 = b + (XF / 2 if idx < len(SCENES) - 1 else 1)
        if not (s0 <= t < s1): continue
        img, fade = SCENE_FN[n](max(0.0, t - a) if idx > 0 else t, b - a)
        img = img.convert('RGB')
        if fade < 1: img = Image.blend(Image.new('RGB', img.size), img, fade)
        w = prog(t, a - XF / 2, a + XF / 2) if idx > 0 else 1.0
        out = img if out is None else Image.blend(out, img, ease_in_out(w))
    arr = np.asarray(out, np.float32) * vignette()
    arr += grain(i)[..., None]
    arr = (arr - 128) * 1.04 + 128
    return np.clip(arr, 0, 255).astype(np.uint8)

def render_chunk(args):
    ci, f0, f1 = args
    path = os.path.join(OUT, f'_chunk{ci:02d}.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(f0, f1):
        p.stdin.write(frame(i).tobytes())
        if (i - f0) % 25 == 0: print(f'  bo\'lak {ci}: {i - f0}/{f1 - f0}', flush=True)
    p.stdin.close(); p.wait()
    return path

def main():
    os.makedirs(OUT, exist_ok=True)
    if '--stills' in sys.argv:
        times = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1:]] or [1.5, 8, 15.5, 27, 40, 52, 63]
        for tt in times:
            Image.fromarray(frame(int(tt * FPS))).save(os.path.join(OUT, f'still_{tt:05.1f}.jpg'), quality=90)
            print('kadr', tt, flush=True)
        return
    nproc = int(os.environ.get('JOBS', os.cpu_count() or 4))
    nch = nproc * 4
    bounds = np.linspace(0, NFR, nch + 1).astype(int)
    jobs = [(c, bounds[c], bounds[c + 1]) for c in range(nch)]
    with Pool(nproc) as pool:
        parts = pool.map(render_chunk, jobs, chunksize=1)
    lst = os.path.join(OUT, '_list.txt')
    with open(lst, 'w') as f:
        for p in parts: f.write(f"file '{p}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    os.path.join(OUT, '_video.mp4')], check=True)
    for p in parts: os.remove(p)
    os.remove(lst)
    print('video tayyor')

if __name__ == '__main__':
    main()
