#!/usr/bin/env python3
"""TEZORA — gilam yuvish reklamasi. 9:16, Ultra HD 2160x3840 (K=2) yoki 1080x1920 (K=1), 30 fps.
Kadrlar PIL'da chiziladi va to'g'ridan-to'g'ri ffmpeg'ga uzatiladi -> tezora/out/_video.mp4
  python3 tezora/src/render.py              # to'liq video
  python3 tezora/src/render.py --stills 3 15 27   # nazorat kadrlari (png)
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(HERE)
ROOT = os.path.dirname(PRJ)
A = os.path.join(PRJ, 'assets'); OUT = os.path.join(PRJ, 'out')
FONTS = os.path.join(ROOT, 'assets', 'fonts')
K = int(os.environ.get('K', '2'))   # 2 -> Ultra HD 2160x3840, 1 -> 1080x1920
W, H, FPS = 1080 * K, 1920 * K, 30
def P(v): return v * K
DUR = 31.0
OFF = 0.4          # diktor ovozi shu soniyadan boshlanadi

PHONE = '66-200-17-00'
CITY = 'Samarqand'

NAVY = (8, 27, 64); BLUE = (16, 98, 255); CYAN = (34, 211, 238); YEL = (255, 204, 0); WHITE = (255, 255, 255)

def font(w, s): return ImageFont.truetype(os.path.join(FONTS, f'Montserrat-{w}.ttf'), int(round(s * K)))

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, t0, d): return clamp((t - t0) / d)

# ---------------------------------------------------------------- manba rasmlar
UP = 2 * K  # oldindan kattalashtirish
def load_src(i):
    im = Image.open(os.path.join(A, f'p{i}.png')).convert('RGB')
    im = ImageEnhance.Contrast(im).enhance(1.07)
    im = ImageEnhance.Color(im).enhance(1.12)
    im = im.resize((im.width * UP, im.height * UP), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2.2 * K, percent=75, threshold=2))
    return im
SRC = {i: load_src(i) for i in range(1, 6)}
SIZE = {i: (SRC[i].width // UP, SRC[i].height // UP) for i in SRC}

# Gapiruvchi boshlovchi: SadTalker kadrlari (25 fps, ovoz bilan sinxron). Bo'lmasa — oddiy surat.
TALK_DIR = os.path.join(OUT, '_talk'); TALK_FPS = 25
TALK_N = len([f for f in os.listdir(TALK_DIR) if f.endswith('.png')]) if os.path.isdir(TALK_DIR) else 0
CUR_T = [0.0]; _talk_cache = {}
def talk_frame(t):
    idx = int(clamp(round((t - OFF) * TALK_FPS), 0, TALK_N - 1)) + 1
    if idx not in _talk_cache:
        _talk_cache.clear()
        im = Image.open(os.path.join(TALK_DIR, f'{idx:05d}.png')).convert('RGB')
        if im.size != SIZE[1]: im = im.resize(SIZE[1], Image.LANCZOS)
        im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.07)).enhance(1.12)
        _talk_cache[idx] = im
    return _talk_cache[idx]

def cam(i, cx, cy, h):
    """9:16 kadr: markaz (cx,cy) va balandlik h — asl rasm piksellarida."""
    sw, sh = SIZE[i]
    h = min(h, sh); w = h * 9 / 16
    if w > sw: w = sw; h = w * 16 / 9
    cx = clamp(cx, w / 2, sw - w / 2); cy = clamp(cy, h / 2, sh - h / 2)
    if i == 1 and TALK_N:
        box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        out = talk_frame(CUR_T[0]).resize((W, H), Image.LANCZOS, box=box)
        return out.filter(ImageFilter.UnsharpMask(radius=1.6 * K, percent=80, threshold=2))
    box = [(cx - w / 2) * UP, (cy - h / 2) * UP, (cx + w / 2) * UP, (cy + h / 2) * UP]
    return SRC[i].transform((W, H), Image.EXTENT, box, Image.BICUBIC)

def lerp(a, b, k): return tuple(x + (y - x) * k for x, y in zip(a, b))

# ---------------------------------------------------------------- doimiy qatlamlar
yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(-1, 1, W)[None, :]
vig = np.clip(((xx ** 2) * 0.6 + ((yy - 0.45) * 2) ** 2 * 0.5) - 0.25, 0, 1) * 150
bot = np.clip((yy - 0.55) / 0.45, 0, 1) ** 1.6 * 175
top = np.clip((0.16 - yy) / 0.16, 0, 1) ** 1.5 * 110
shade = np.clip(vig + bot + top, 0, 215).astype(np.uint8)
SHADE = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8) + np.array([3, 10, 28], np.uint8), shade]), 'RGBA')
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 6, (960, 540)).astype(np.int16) for _ in range(6)]

def finish(img, fi):
    a = np.asarray(img.convert('RGB')).astype(np.int16)
    g = np.kron(GRAIN[fi % 6], np.ones((2 * K, 2 * K), np.int16))[:, :, None]
    return np.clip(a + g, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- ikonkalar
def drop_icon(s, c1=CYAN, c2=BLUE):
    """Suv tomchisi (logotip belgisi)."""
    s = int(round(s * K)); S = s * 4; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m)
    r = S * 0.34; cx, cy = S / 2, S * 0.62
    d.ellipse([cx - r, cy - r, cx + r, cy + r], 255)
    ang = math.radians(42)
    d.polygon([(cx, S * 0.04), (cx - r * math.cos(ang) * 1.0, cy - r * math.sin(ang)), (cx + r * math.cos(ang), cy - r * math.sin(ang))], 255)
    grad = np.zeros((S, S, 4), np.uint8); k = np.linspace(0, 1, S)[:, None]
    for j in range(3): grad[:, :, j] = (c1[j] * (1 - k) + c2[j] * k).astype(np.uint8)
    grad[:, :, 3] = np.asarray(m)
    im = Image.fromarray(grad, 'RGBA')
    hl = Image.new('RGBA', (S, S)); hd = ImageDraw.Draw(hl)
    hd.ellipse([cx - r * 0.55, cy - r * 0.5, cx - r * 0.15, cy - r * 0.05], (255, 255, 255, 170))
    im = Image.alpha_composite(im, hl.filter(ImageFilter.GaussianBlur(S * 0.02)))
    return im.resize((s, s), Image.LANCZOS)

def pin_icon(s, col=WHITE):
    s = int(round(s * K)); S = s * 4; m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m)
    r = S * 0.3; cx, cy = S / 2, S * 0.38
    d.ellipse([cx - r, cy - r, cx + r, cy + r], 255)
    d.polygon([(cx - r * 0.86, cy + r * 0.5), (cx + r * 0.86, cy + r * 0.5), (cx, S * 0.95)], 255)
    r2 = r * 0.42; d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], 0)
    im = Image.new('RGBA', (S, S), col + (0,)); im.putalpha(m)
    return im.resize((s, s), Image.LANCZOS)

def phone_icon(s, col=WHITE):
    """Telefon trubkasi (DejaVu'dagi ✆ belgisi emas — o'zimiz chizamiz)."""
    s = int(round(s * K)); S = s * 4; m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m)
    w = S * 0.17
    # yoy shaklidagi trubka
    d.arc([S * 0.12, S * 0.12, S * 0.88, S * 0.88], 100, 250, 255, int(w))
    for a0 in (100, 250):
        a = math.radians(a0); cx = S / 2 + S * 0.38 * math.cos(a); cy = S / 2 + S * 0.38 * math.sin(a)
        d.ellipse([cx - w * 0.95, cy - w * 0.95, cx + w * 0.95, cy + w * 0.95], 255)
    m = m.rotate(-45, resample=Image.BICUBIC, center=(S / 2, S / 2))
    im = Image.new('RGBA', (S, S), col + (0,)); im.putalpha(m)
    return im.resize((s, s), Image.LANCZOS)

def check_icon(s):
    s = int(round(s * K)); S = s * 4; im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, S - 1, S - 1], CYAN + (255,))
    d.line([(S * 0.27, S * 0.52), (S * 0.44, S * 0.68), (S * 0.74, S * 0.34)], fill=NAVY + (255,), width=int(S * 0.11), joint='curve')
    return im.resize((s, s), Image.LANCZOS)

def star_icon(s, col=YEL):
    s = int(round(s * K)); S = s * 4; im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    pts = []
    for k in range(10):
        r = S * (0.48 if k % 2 == 0 else 0.2); a = -math.pi / 2 + k * math.pi / 5
        pts.append((S / 2 + r * math.cos(a), S / 2 + r * math.sin(a) + S * 0.03))
    d.polygon(pts, col + (255,))
    return im.resize((s, s), Image.LANCZOS)

def shadowed(im, blur=10, op=150, off=(0, 6)):
    blur = blur * K; off = (off[0] * K, off[1] * K)
    pad = blur * 3
    out = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel('A').point(lambda v: v * op // 255))
    out.alpha_composite(sh, (pad + off[0], pad + off[1])); out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (pad, pad))
    return out, pad

# ---------------------------------------------------------------- logotip
def make_logo(h=150, tag=True):
    f = font(900, h); tw = int(f.getlength('TEZORA'))
    ic = drop_icon(h * 1.15); hu = h; h = h * K
    th = int(h * 1.25) + (int(h * 0.55) if tag else 0)
    im = Image.new('RGBA', (ic.width + int(h * 0.18) + tw + P(10), th), (0, 0, 0, 0))
    im.alpha_composite(ic, (0, int(h * 0.02)))
    d = ImageDraw.Draw(im)
    x0 = ic.width + int(h * 0.18)
    d.text((x0, h * 0.12), 'TEZ', font=f, fill=WHITE)
    d.text((x0 + f.getlength('TEZ'), h * 0.12), 'ORA', font=f, fill=CYAN)
    if tag:
        ft = font(700, hu * 0.24); s = 'GILAM YUVISH XIZMATI'
        sp = h * 0.075; tx = x0 + P(4)
        for ch in s:
            d.text((tx, h * 1.3), ch, font=ft, fill=(220, 236, 255)); tx += ft.getlength(ch) + sp
    return im
LOGO_BIG = shadowed(make_logo(150), 18, 170)
LOGO_SMALL = shadowed(make_logo(46, tag=False), 6, 160, (0, 2))

# ---------------------------------------------------------------- pastki doimiy panel: telefon + manzil
BAR_Y = 1470   # Instagram/TikTok pastki yozuvlari bilan to'qnashmasligi uchun biroz yuqorida
def make_bar():
    bw, bh = P(1000), P(150)
    im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], P(34), fill=NAVY + (232,), outline=CYAN + (255,), width=P(4))
    # chap: telefon
    r = P(50); cx = P(22) + r; cy = bh // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE + (255,))
    im.alpha_composite(phone_icon(58), (cx - P(29), cy - P(29)))
    fp = font(800, 64); d.text((cx + r + P(20), cy), PHONE, font=fp, fill=WHITE, anchor='lm')
    xe = cx + r + P(20) + fp.getlength(PHONE)
    # ajratgich
    xs = xe + P(26); d.line([(xs, P(30)), (xs, bh - P(30))], fill=(90, 130, 200, 255), width=P(3))
    # o'ng: manzil
    pi = pin_icon(56, YEL); im.alpha_composite(pi, (int(xs + P(22)), cy - P(30)))
    fc = font(700, 44); d.text((xs + P(22) + P(60), cy + P(1)), CITY, font=fc, fill=WHITE, anchor='lm')
    return im
BAR = make_bar()
BAR_SHADOW, BAR_PAD = shadowed(BAR, 16, 150, (0, 8))

def draw_bar(fr, t):
    k = eout(prog(t, 0.15, 0.6))
    if k <= 0: return
    y = int(P(BAR_Y) + (1 - k) * P(260)); x = (W - BAR.width) // 2
    img = BAR_SHADOW
    if k < 1:
        img = img.copy(); img.putalpha(img.getchannel('A').point(lambda v: int(v * k)))
    fr.alpha_composite(img, (x - BAR_PAD, y - BAR_PAD))
    # yaltirash: har 5 soniyada panel bo'ylab nur o'tadi
    ph = ((t - 1.0) % 5.0) / 0.9
    if t > 1.0 and ph < 1:
        sx = int(P(-200) + ph * (BAR.width + P(400)))
        g = Image.new('RGBA', (BAR.width, BAR.height), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.polygon([(sx, 0), (sx + P(70), 0), (sx + P(20), BAR.height), (sx - P(50), BAR.height)], (255, 255, 255, 70))
        g = g.filter(ImageFilter.GaussianBlur(P(8)))
        mask = Image.new('L', BAR.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, BAR.width - 1, BAR.height - 1], P(34), 255)
        g.putalpha(Image.fromarray(np.minimum(np.asarray(g.getchannel('A')), np.asarray(mask))))
        fr.alpha_composite(g, (x, y))

# ---------------------------------------------------------------- kinetik yozuvlar
class Caption:
    """lines: [[(so'z, ajratilgan?), ...], ...]. So'zlar birma-bir sakrab chiqadi."""
    def __init__(self, t0, t1, lines, size=82, cy=1130, step=0.08, weight=800):
        self.t0, self.t1, self.cy, self.step = t0, t1, cy, step
        cy = P(cy)
        def lw_(sz):
            ff = font(weight, sz)
            return max(sum(ff.getlength(w) / K + (sz * 0.44 if h else 0) for w, h in ln) + sz * 0.28 * (len(ln) - 1) for ln in lines)
        while lw_(size) > 940: size -= 2
        f = font(weight, size); size = size * K; sp = size * 0.28; lh = size * 1.32
        self.items = []
        tot_h = lh * len(lines); y = cy - tot_h / 2
        idx = 0
        for line in lines:
            ws = []
            for word, hi in line:
                tw = f.getlength(word); padx = size * 0.22 if hi else 0
                im = Image.new('RGBA', (int(tw + padx * 2 + P(4)), int(size * 1.3)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                if hi:
                    d.rounded_rectangle([0, size * 0.08, im.width - 1, im.height - 1 - size * 0.04], int(size * 0.18), fill=YEL + (255,))
                    d.text((padx, im.height / 2 + size * 0.02), word, font=f, fill=NAVY, anchor='lm')
                else:
                    d.text((P(2), im.height / 2), word, font=f, fill=WHITE, anchor='lm', stroke_width=0)
                ws.append(shadowed(im, 9, 190, (0, 5)))
            lw = sum(w[0].width - 2 * w[1] for w in ws) + sp * (len(ws) - 1)
            x = (W - lw) / 2
            for img, pad in ws:
                self.items.append((img, pad, x, y + (lh - (img.height - 2 * pad)) / 2, idx)); idx += 1
                x += img.width - 2 * pad + sp
            y += lh

    def draw(self, fr, t):
        if t < self.t0 or t > self.t1 + 0.3: return
        out = clamp((self.t1 + 0.25 - t) / 0.25)
        for img, pad, x, y, i in self.items:
            k = prog(t, self.t0 + i * self.step, 0.32)
            if k <= 0: continue
            s = 0.55 + 0.45 * back(k); a = clamp(k * 2.5) * out
            dy = P((1 - eout(k)) * 40 - (1 - out) * 30)
            im = img
            if abs(s - 1) > 0.01:
                im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            if a < 1:
                im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
            cxp = x - pad + img.width / 2; cyp = y - pad + img.height / 2 + dy
            fr.alpha_composite(im, (int(cxp - im.width / 2), int(cyp - im.height / 2)))

def L(s):
    """'Oddiy *ajratilgan so'z* matn' -> [(so'z, bool)]; *...* ichidagilar sariq fonda."""
    out = []; hi = False; buf = ''
    for part in s.split(' '):
        st = part.startswith('*'); en = part.endswith('*')
        p = part.strip('*')
        if st: hi = True
        out.append((p, hi))
        if en: hi = False
    return out

def T(x): return x + OFF   # diktor vaqtini video vaqtiga o'tkazish

CAPS = [
    Caption(T(0.02), T(1.25), [L('ASSALOMU ALAYKUM!')], size=86, cy=1190),
    Caption(T(1.45), T(3.85), [L('Gilamlaringizga'), L('*haqiqiy* *tozalik* kerakmi?')], size=78, cy=1190, step=0.12),
    Caption(T(4.2), T(5.55), [L('Siz izlagan manzil —')], size=72, cy=1240),
    Caption(T(6.9), T(10.0), [L('*Zamonaviy*'), L('uskunalar')], size=96, cy=1150, step=0.18),
    Caption(T(10.05), T(11.75), [L('Professional'), L('*yuvish* *texnologiyasi*')], size=84, cy=1150, step=0.14),
    Caption(T(11.8), T(13.4), [L('Gilamingiz'), L('*tozalikka* qaytadi')], size=88, cy=1150, step=0.14),
    Caption(T(18.75), T(21.1), [L('Biz uchun har bir'), L('mijozning *ishonchi*'), L('muhim')], size=78, cy=1160, step=0.12),
    Caption(T(21.5), T(23.0), [L('Gilamingizni'), L('*bizga* *topshiring*')], size=88, cy=1150, step=0.14),
    Caption(T(23.17), T(24.95), [L('Tozalikni'), L('*o‘zimizga* qo‘yib'), L('bering!')], size=84, cy=1150, step=0.12),
]

# ---------------------------------------------------------------- jarayon kadrlari (yuvish/chayish/quritish/nazorat)
STEPS = [('01', 'YUVISH', T(13.64)), ('02', 'CHAYISH', T(14.35)), ('03', 'QURITISH', T(15.09)), ('04', 'SIFAT NAZORATI', T(15.95))]
def big_word(n, word):
    f = font(900, 128 if len(word) < 10 else 100); fn = font(800, 54)
    tw = f.getlength(word)
    im = Image.new('RGBA', (int(tw + P(40)), P(260)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    nw = fn.getlength(n)
    d.rounded_rectangle([(im.width - nw) / 2 - P(22), 0, (im.width + nw) / 2 + P(22), P(74)], P(18), fill=CYAN + (255,))
    d.text((im.width / 2, P(38)), n, font=fn, fill=NAVY, anchor='mm')
    d.text((im.width / 2, P(180)), word, font=f, fill=WHITE, anchor='mm')
    return shadowed(im, 14, 200, (0, 8))
STEP_IMG = [big_word(n, w) for n, w, _ in STEPS]
STAR = shadowed(star_icon(84), 8, 160, (0, 4))

def draw_step(fr, t, k_idx, t0, t1):
    img, pad = STEP_IMG[k_idx]
    k = prog(t, t0, 0.28); out = clamp((t1 - t) / 0.12)
    s = 1.25 - 0.25 * eout(k); a = clamp(k * 3) * out
    im = img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
    if a < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(P(1080) - im.height / 2)))

# "Barchasi bir joyda" — ro'yxat paneli
def make_list():
    pw, ph = P(860), P(640)
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], P(40), fill=(8, 27, 64, 215), outline=CYAN + (200,), width=P(3))
    f1 = font(900, 64); d.text((pw / 2, P(78)), 'BARCHASI', font=f1, fill=WHITE, anchor='mm')
    fy = font(900, 64); bw = fy.getlength('BIR JOYDA!') + P(50)
    d.rounded_rectangle([(pw - bw) / 2, P(120), (pw + bw) / 2, P(200)], P(18), fill=YEL)
    d.text((pw / 2, P(161)), 'BIR JOYDA!', font=fy, fill=NAVY, anchor='mm')
    return im
LIST_BG = shadowed(make_list(), 20, 170, (0, 10))
ROWS = []
for name in ['Yuvish', 'Chayish', 'Quritish', 'Sifat nazorati']:
    r = Image.new('RGBA', (P(640), P(84)), (0, 0, 0, 0)); d = ImageDraw.Draw(r)
    r.alpha_composite(check_icon(64), (0, P(10)))
    d.text((P(92), P(42)), name, font=font(800, 54), fill=WHITE, anchor='lm')
    ROWS.append(r)

def draw_list(fr, t, t0, t1):
    k = eout(prog(t, t0, 0.35)); out = clamp((t1 - t) / 0.2)
    img, pad = LIST_BG
    a = k * out
    im = img.resize((int(img.width * (0.85 + 0.15 * k)), int(img.height * (0.85 + 0.15 * k))), Image.BILINEAR)
    im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    y0 = P(760)
    fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(y0 + img.height / 2 - pad - im.height / 2)))
    px = (W - P(860)) // 2
    for j, r in enumerate(ROWS):
        kk = eout(prog(t, t0 + 0.25 + j * 0.16, 0.3)) * out
        if kk <= 0: continue
        rr = r.copy(); rr.putalpha(rr.getchannel('A').point(lambda v: int(v * kk)))
        fr.alpha_composite(rr, (int(px + P(130) - P(1 - kk) * 60), int(y0 + P(240) + P(j * 92))))

# ---------------------------------------------------------------- yakuniy kadr
def softblur(im, r):
    """Katta kadrni tez xiralashtirish: 4x kichraytirib, xiralab, qayta kattalashtirish."""
    sm = im.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r * K / 4))
    return sm.resize((W, H), Image.BICUBIC)
def end_bg(t):
    k = (t - T(24.87)) / 7
    base = softblur(cam(3, 640 - 120 * k, 440, 874), 14).convert('RGBA')
    ov = np.zeros((H, W, 4), np.uint8); ov[..., 0] = NAVY[0]; ov[..., 1] = NAVY[1]; ov[..., 2] = NAVY[2]
    ov[..., 3] = (np.clip(0.72 + 0.2 * (yy - 0.5), 0.55, 0.9) * 255).astype(np.uint8)[:, :]
    return Image.alpha_composite(base, Image.fromarray(ov, 'RGBA'))
END_OV = None

BUB = [(rng.uniform(0, W), rng.uniform(0, H), P(rng.uniform(6, 26)), P(rng.uniform(60, 200))) for _ in range(40)]
def bubbles(fr, t, t0, alpha=1.0):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, r, v in BUB:
        yy_ = (y - (t - t0) * v) % (H + P(100)) - P(50)
        xx_ = x + math.sin((t + x / K) * 1.3) * P(12)
        d.ellipse([xx_ - r, yy_ - r, xx_ + r, yy_ + r], outline=(180, 235, 255, int(120 * alpha)), width=P(2))
        d.ellipse([xx_ - r * 0.5, yy_ - r * 0.6, xx_ - r * 0.1, yy_ - r * 0.2], fill=(255, 255, 255, int(90 * alpha)))
    fr.alpha_composite(lay)

def make_cta():
    f = font(900, 58); s = 'HOZIROQ BUYURTMA BERING!'
    tw = f.getlength(s); im = Image.new('RGBA', (int(tw + P(90)), P(120)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], P(60), fill=YEL)
    d.text((im.width / 2, P(62)), s, font=f, fill=NAVY, anchor='mm')
    return shadowed(im, 16, 170, (0, 8))
CTA = make_cta()
def make_tag():
    f = font(800, 50); s = 'ZAMONAVIY TOZALIK XIZMATI'
    im = Image.new('RGBA', (int(f.getlength(s) + P(20)), P(80)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((P(10), P(40)), s, font=f, fill=WHITE, anchor='lm')
    return shadowed(im, 8, 180, (0, 4))
TAG = make_tag()

def paste_anim(fr, sh, cx, cy, k, a=1.0, s0=0.6):
    img, pad = sh
    s = s0 + (1 - s0) * back(k); al = clamp(k * 2.5) * a
    if al <= 0: return
    im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
    if al < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * al)))
    fr.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------------------------------------------------------------- sahnalar
# (boshlanish, rasm, kamera_bosh(cx,cy,h), kamera_oxir)
SHOTS = [
    (0.0,       1, (690, 450, 874), (692, 395, 700)),    # boshlovchi gapiradi
    (T(6.87),   2, (330, 380, 730), (560, 380, 730)),    # zamonaviy sex
    (T(9.65),   3, (1060, 437, 874), (620, 437, 874)),   # cho'tkali yuvish mashinasi
    (T(13.64),  3, (360, 360, 560), (330, 380, 500)),    # 01 yuvish
    (T(14.35),  4, (520, 420, 810), (720, 420, 740)),    # 02 chayish
    (T(15.09),  5, (260, 437, 874), (420, 437, 800)),    # 03 quritish
    (T(15.95),  2, (640, 450, 640), (660, 440, 600)),    # 04 sifat nazorati
    (T(17.0),   2, (520, 380, 730), (760, 380, 730)),    # barchasi bir joyda
    (T(18.75),  1, (690, 440, 760), (690, 420, 690)),    # boshlovchi: ishonch
    (T(21.5),   5, (300, 437, 874), (980, 437, 874)),    # gilamlar osilgan
    (T(24.87),  0, None, None),                          # yakuniy kadr
    (DUR + 1,   0, None, None),
]
FLASH = [T(13.64), T(14.35), T(15.09), T(15.95), T(24.87)]

def frame(t, fi):
    CUR_T[0] = t
    for n in range(len(SHOTS) - 1):
        if SHOTS[n][0] <= t < SHOTS[n + 1][0]: break
    t0, img, c0, c1 = SHOTS[n]; t1 = SHOTS[n + 1][0]
    if img:
        k = ease((t - t0) / (t1 - t0)) * 0.85 + (t - t0) / (t1 - t0) * 0.15
        cx, cy, h = lerp(c0, c1, k)
        punch = 1 - 0.07 * (1 - eout(prog(t, t0, 0.45))) if n > 0 else 1
        fr = cam(img, cx, cy, h * punch).convert('RGBA')
        if n == 7:   # ro'yxat ostida biroz xiralashtirish
            bk = ease(prog(t, t0, 0.4)); fr = Image.blend(fr, softblur(fr, 8), bk * 0.85)
        fr.alpha_composite(SHADE)
    else:
        fr = end_bg(t)
        bubbles(fr, t, t0, ease(prog(t, t0, 0.6)))

    # boshlanishda qora ekrandan chiqish
    if t < 0.35:
        fr = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), fr, ease(t / 0.35))

    # logotip: 1-sahna (TEZORA so'zi aytilganda)
    if n == 0:
        kl = prog(t, T(5.55), 0.5)
        if kl > 0: paste_anim(fr, LOGO_BIG, W / 2, P(1210), kl, clamp((T(6.85) - t) / 0.2))
    # kichik logotip burchakda (2–9 sahnalar)
    if 1 <= n <= 9:
        a = ease(prog(t, T(6.87), 0.5)) * clamp((T(24.87) - t) / 0.2)
        if a > 0:
            im = LOGO_SMALL[0].copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
            fr.alpha_composite(im, (W - LOGO_SMALL[0].width + LOGO_SMALL[1] - P(50), P(110) - LOGO_SMALL[1]))

    for c in CAPS: c.draw(fr, t)
    for j, (_, _, ts) in enumerate(STEPS):
        te = STEPS[j + 1][2] if j + 1 < len(STEPS) else T(17.0)
        if ts <= t < te: draw_step(fr, t, j, ts, te)
    if T(17.0) <= t < T(18.75): draw_list(fr, t, T(17.0), T(18.75))

    # ishonch: 5 yulduz
    if n == 8:
        for j in range(5):
            kk = prog(t, T(19.6) + j * 0.09, 0.35)
            if kk > 0:
                paste_anim(fr, STAR, W / 2 + P((j - 2) * 100), P(950), kk, clamp((T(21.3) - t) / 0.2), 0.2)

    # yakuniy kadr
    if n == 10:
        paste_anim(fr, LOGO_BIG, W / 2, P(640), prog(t, T(25.27), 0.55), 1, 0.4)
        k2 = eout(prog(t, T(26.07), 0.5))
        if k2 > 0:
            im = TAG[0].copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * k2)))
            fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(P(860 + (1 - k2) * 30) - im.height / 2)))
        k3 = prog(t, T(28.05), 0.45)
        if k3 > 0:
            pulse = 1 + 0.04 * math.sin((t - T(28.05)) * 2 * math.pi * 1.3) * clamp((t - T(28.5)) * 3)
            img, pad = CTA
            s = (0.5 + 0.5 * back(k3)) * pulse; al = clamp(k3 * 2.5)
            im = img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
            if al < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * al)))
            fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(P(1150) - im.height / 2)))

    draw_bar(fr, t)

    # oq chaqnash (tez kesishlarda)
    for tf in FLASH:
        if tf - 0.02 <= t < tf + 0.16:
            a = (1 - (t - tf) / 0.16) * 0.55
            fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 255, 255, 255)), clamp(a))
    # oxirida qoraga so'nish
    if t > DUR - 0.5:
        fr = Image.blend(fr, Image.new('RGBA', (W, H), (0, 0, 0, 255)), ease((t - (DUR - 0.5)) / 0.5))
    return finish(fr, fi)

def main():
    os.makedirs(OUT, exist_ok=True)
    if '--stills' in sys.argv:
        for s in sys.argv[sys.argv.index('--stills') + 1:]:
            t = float(s); Image.fromarray(frame(t, 0)).save(os.path.join(OUT, f'still_{t:05.2f}.png')); print('kadr', t)
        return
    n = int(DUR * FPS); J = int(os.environ.get('JOBS', os.cpu_count() or 4))
    parts = [(j, j * n // J, (j + 1) * n // J) for j in range(J)]
    from multiprocessing import Pool
    with Pool(J) as pool: segs = pool.map(render_part, parts)
    lst = os.path.join(OUT, '_parts.txt')
    open(lst, 'w').write(''.join(f"file '{os.path.basename(x)}'\n" for x in segs))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(OUT, '_video.mp4')], check=True)
    for x in segs: os.remove(x)
    print('video tayyor', f'{W}x{H}')

def render_part(arg):
    j, a, b = arg
    seg = os.path.join(OUT, f'_part{j}.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-threads', '1', '-pix_fmt', 'yuv420p', seg],
                         stdin=subprocess.PIPE)
    for i in range(a, b):
        p.stdin.write(frame(i / FPS, i).tobytes())
        if (i - a) % 60 == 0: print(f'[{j}] {i - a}/{b - a}', flush=True)
    p.stdin.close(); p.wait()
    return seg

if __name__ == '__main__':
    main()
