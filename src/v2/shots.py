"""Sahnalar. Har bir funksiya global vaqt t ni oladi va RGB float32 (H,W,3) 0..255 qaytaradi.
Vaqtlar diktor matniga moslangan (assets/script.txt, src/v2/README)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from core import *
import r3d
from assets_gen import *

WHITE = (255, 255, 255); GOLD = (255, 200, 70); RED = (230, 45, 40); GREEN = (110, 210, 70); DARK = (12, 22, 14)

# ================================================================ umumiy qismlar
def leaf_data():
    return cached('leaf', lambda: make_leaf(ki(1000), seed=1))

def leaf_rgba(powder=0.0, mildew=0.0, necro=0.0, heal=0.0, light=(-0.5, -0.6, 0.62), back=0.55, sat=1.0):
    L = leaf_data()
    rgb, a = compose_leaf(L, powder, mildew, necro, heal, light, back, sat)
    return rgba_from(rgb, a)

def bokeh_bg(theme='warm'):
    """Xira bog' foni (bokeh) — oldindan tayyorlanadi, kamera bilan suriladi."""
    def make():
        w, h = int(W * 1.3), int(H * 1.3)
        w4, h4 = w // 4, h // 4
        if theme == 'warm':
            g = vgrad(h4, w4, [(0, (40, 62, 30)), (0.45, (95, 110, 45)), (1, (20, 36, 16))])
            g += radial(w4, h4, w4 * 0.7, h4 * 0.18, w4 * 0.9, (150, 120, 50), 1.8)
            cols = [(255, 225, 150), (220, 240, 150), (255, 200, 120)]
        elif theme == 'cold':
            g = vgrad(h4, w4, [(0, (24, 34, 36)), (0.5, (44, 58, 54)), (1, (12, 18, 18))])
            cols = [(170, 200, 210), (150, 180, 170)]
        elif theme == 'dark':
            g = vgrad(h4, w4, [(0, (14, 14, 12)), (0.5, (30, 28, 22)), (1, (8, 8, 6))])
            cols = [(160, 120, 80)]
        else:  # green studio
            g = vgrad(h4, w4, [(0, (8, 30, 16)), (0.55, (24, 84, 40)), (1, (6, 22, 12))])
            g += radial(w4, h4, w4 * 0.5, h4 * 0.42, w4 * 0.8, (50, 120, 50), 1.6)
            cols = [(200, 255, 170), (255, 235, 160)]
        g = g * (0.85 + 0.3 * fbm(w4, h4, 3, seed=5, base=3)[..., None])
        im = np2im(g).resize((w, h), Image.BICUBIC)
        lay = Image.new('L', (w // 2, h // 2), 0)
        rng = random.Random(len(theme))
        cl = Image.new('RGB', (w // 2, h // 2))
        for i in range(70):
            x, y = rng.uniform(0, w / 2), rng.uniform(0, h / 2); r = rng.uniform(12, 70) * K / 2
            c = rng.choice(cols); a = rng.randint(25, 80)
            m = Image.new('L', lay.size, 0); ImageDraw.Draw(m).ellipse((x - r, y - r, x + r, y + r), fill=a)
            ImageDraw.Draw(m).ellipse((x - r * 0.9, y - r * 0.9, x + r * 0.9, y + r * 0.9), fill=int(a * 0.7))
            cl.paste(Image.new('RGB', lay.size, c), (0, 0), m.filter(ImageFilter.GaussianBlur(r * 0.05 + 1)))
            lay = Image.fromarray(np.maximum(np.asarray(lay), np.asarray(m)))
        lay = lay.filter(ImageFilter.GaussianBlur(2 * K)).resize((w, h), Image.BILINEAR)
        cl = cl.filter(ImageFilter.GaussianBlur(2 * K)).resize((w, h), Image.BILINEAR)
        arr = np.asarray(im, np.float32) + np.asarray(cl, np.float32) * (np.asarray(lay, np.float32)[..., None] / 255) * 1.2
        return np2im(arr)
    return cached(('bokeh', theme, W), make)

def bg_view(theme, t, drift=(0.02, 0.01), zoom=1.0):
    src = bokeh_bg(theme)
    cx = src.width / 2 + math.sin(t * 0.21) * src.width * drift[0]
    cy = src.height / 2 + math.cos(t * 0.17) * src.height * drift[1]
    return view(src, cx, cy, src.width / W * zoom).convert('RGBA')

def bottle(height):
    def mk():
        b = Image.open(A('bottle.png')).convert('RGBA')
        hp = ki(height); w = int(b.width * hp / b.height)
        b = b.resize((w, hp), Image.LANCZOS)
        if hp > 1500: b = b.filter(ImageFilter.UnsharpMask(1.5 * K, 40, 2))
        return b
    return cached(('bottle', height, K), mk)

def bottle_hero(height, sweep=None, refl=True):
    """Flakon + soya + pol aksi; sweep 0..1 — yorug'lik o'tishi."""
    b = bottle(height)
    if sweep is not None and 0 < sweep < 1:
        w, h = b.size
        u = cached(('sw', w, h), lambda: ((np.arange(w)[None, :] / w) + (np.arange(h)[:, None] / h) * 0.45).astype(np.float32))
        c = -0.3 + sweep * 1.9
        band = np.exp(-((u - c) / 0.11) ** 2) * 0.85
        arr = np.asarray(b, np.float32).copy()
        arr[..., :3] = np.minimum(255, arr[..., :3] + (band * arr[..., 3] / 255 * 220)[..., None])
        b = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    def base():
        bb = bottle(height); w, h = bb.size
        rh = int(h * 0.28) if refl else 0; ox = ki(120)
        cv = Image.new('RGBA', (w + 2 * ox, h + rh + ki(80)), (0, 0, 0, 0))
        sh = Image.new('L', cv.size, 0)
        ImageDraw.Draw(sh).ellipse((ox - ki(40), h - ki(26), ox + w + ki(40), h + ki(30)), fill=200)
        s = Image.new('RGBA', cv.size, (0, 10, 4, 0)); s.putalpha(fast_blur_img(sh, k(20))); cv.alpha_composite(s)
        if refl:
            r = bb.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, w, rh))
            gr = np.linspace(0.28, 0, rh, dtype=np.float32)[:, None]
            r.putalpha(Image.fromarray((np.asarray(r.getchannel('A'), np.float32) * gr).astype(np.uint8)))
            cv.alpha_composite(fast_blur_img(r, k(2)), (ox, h + 2))
        return cv, ox
    cv, ox = cached(('bhero', height, refl, K), base)
    out = cv.copy(); out.alpha_composite(b, (ox, 0))
    return out

def flare(base, cx, cy, size, alpha=1.0, color=(255, 220, 160)):
    """Anamorf linza nuri (mantiqiy koordinata)."""
    def mk():
        s = ki(size); w = s * 4
        yy, xx = np.ogrid[0:s, 0:w]
        d = np.sqrt(((xx - w / 2) / (w * 0.5)) ** 2 + ((yy - s / 2) / (s * 0.02 + 2)) ** 2)
        streak = np.clip(1 - d, 0, 1) ** 3
        d2 = np.sqrt(((xx - w / 2) / (s * 0.25)) ** 2 + ((yy - s / 2) / (s * 0.25)) ** 2)
        glow = np.clip(1 - d2, 0, 1) ** 2
        a = np.clip(streak * 0.8 + glow * 0.9, 0, 1)
        im = Image.new('RGBA', (w, s), color + (0,)); im.putalpha(np2im(a * 255).convert('L'))
        return im
    im = cached(('flare', size, color, K), mk)
    place(base, im, cx, cy, alpha)

def particles(base, t, seed, n, area, color=(255, 255, 255), size=(2, 6), vel=(0, -20), alpha=0.6, twinkle=True):
    rng = random.Random(seed)
    for i in range(n):
        x = rng.uniform(area[0], area[2]); y = rng.uniform(area[1], area[3]); r = rng.uniform(*size)
        ph = rng.uniform(0, 6.28); vx = vel[0] * rng.uniform(0.5, 1.5); vy = vel[1] * rng.uniform(0.5, 1.5)
        xx = area[0] + (x - area[0] + vx * t + 10 * math.sin(t + ph)) % (area[2] - area[0])
        yy = area[1] + (y - area[1] + vy * t) % (area[3] - area[1])
        a = alpha * (0.5 + 0.5 * math.sin(t * 2 + ph)) if twinkle else alpha
        dot = dot_sprite(r, color)
        place(base, dot, xx, yy, a)

def dot_sprite(r, color):
    def mk():
        s = max(4, ki(r * 4)); m = Image.new('L', (s, s), 0)
        ImageDraw.Draw(m).ellipse((s * 0.3, s * 0.3, s * 0.7, s * 0.7), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(s * 0.12))
        im = Image.new('RGBA', (s, s), color + (0,)); im.putalpha(m); return im
    return cached(('dot', round(r, 1), color, K), mk)

def canvas_from(im):
    return np.asarray(im.convert('RGB'), np.float32)

def render_items_layer(items, w=None, h=None, light=r3d.LIGHT, rim_col=(1.0, 0.95, 0.85), env=0.25):
    w = w or W; h = h or H
    c, a = r3d.render(items, w, h, light=light, rim_col=rim_col, env=env)
    return rgba_from(c, a)

def cam_shake(t, amp=4, freq=1.0):
    return (amp * (math.sin(t * 2.1 * freq) * 0.6 + math.sin(t * 5.3 * freq + 1) * 0.4),
            amp * (math.cos(t * 1.7 * freq) * 0.6 + math.sin(t * 4.1 * freq + 2) * 0.4))

def place_leaf(img, lf, cx, cy, size, rot, shadow=True, blur=0):
    s = ki(size)
    li = lf.resize((s, s), Image.BICUBIC)
    if rot: li = li.rotate(rot, resample=Image.BICUBIC)
    if blur: li = fast_blur_img(li, k(blur))
    if shadow:
        sh = shadow_of(li, k(30), 0.55)
        place(img, sh, cx + 30, cy + 45)
    place(img, li, cx, cy)

def headline(base, t, lines, x=CX, y=300, anchor='c'):
    """lines: [(matn, vazn, o'lcham, rang, t_in, mode, extra)]"""
    for (txt, wt, sz, col, tin, mode, dy, kw) in lines:
        draw_text(base, txt, wt, sz, x, y + dy, t, tin, color=col, anchor=anchor, mode=mode, **kw)

# ================================================================ S1  0.0 – 3.0  oq g'ubor savoli
def s1(t):
    T0 = 0.0; lt = t - T0
    img = bg_view('warm', t, zoom=1.0 + 0.04 * lt)
    flare(img, 860, 260, 520, 0.55)
    cover = 0.0 + 0.10 * ease_io(lt / 3.0)
    lf = leaf_rgba(powder=cover, back=0.75, light=(-0.4, -0.7, 0.6))
    z = 1.0 + 0.10 * ease_io(lt / 3.0)
    sx, sy = cam_shake(t, 3)
    place_leaf(img, lf, CX + 20 + sx, 860 + sy, 1180 * z, -12 + 3 * math.sin(lt * 0.6))
    particles(img, t, 3, 26, (0, 0, LW, LH), (255, 240, 200), (1.5, 4), (6, -14), 0.5)
    bar_sweep(img, 110, 1335, 560, 78, t, 0.25, (20, 70, 30), anchor='l', alpha=0.85)
    draw_text(img, "UZUMINGIZ BARGIDA", 800, 52, 136, 1343, t, 0.3, mode='mask')
    draw_text(img, "OQ G'UBOR", 900, 128, 110, 1440, t, 1.25, mode='mask', color=WHITE, track=2)
    draw_text(img, "PAYDO BO'LDIMI?", 900, 76, 116, 1600, t, 1.7, mode='mask', color=GOLD)
    return canvas_from(img), dict(temp=0.6, sat=1.05)

# ================================================================ S2  3.0 – 6.1  oidium makro
def s2(t):
    lt = t - 3.0
    L = leaf_data()
    rgb, a = compose_leaf(L, powder=0.35 + 0.15 * lt / 3, back=0.6, light=(-0.4, -0.7, 0.6))
    src = rgba_from(rgb, a)
    # kuchli yaqinlashtirish — g'ubor o'chog'iga
    z = 3.2 + 1.6 * ease_io(lt / 3.1)
    S = src.width
    bgc = Image.new('RGBA', src.size, (30, 50, 25, 255)); bgc.alpha_composite(src)
    v = view(bgc, S * 0.43, S * 0.40, z / 1.0 * (W / S) * (S / W))
    img = v.convert('RGBA')
    # gifalar (3 chuqurlik qatlami)
    for i, (dep, bl, al, sc) in enumerate([(0.6, 2.5, 0.45, 1.0), (1.0, 0, 0.85, 1.4), (1.6, 6, 0.6, 2.2)]):
        hy = cached(('hyph', i, K), lambda i=i, sc=sc: hyphae_layer(int(W * 1.4), int(H * 1.4), 50 + i, n=int(60 / sc) + 10, thick=sc * 1.6))
        zz = 1.0 + (0.25 + 0.2 * i) * ease_io(lt / 3.1)
        hv = view(hy, hy.width / 2 + i * 40, hy.height / 2, hy.width / W * zz)
        if bl: hv = fast_blur_img(hv, k(bl))
        paste(img, hv, (0, 0), al * ease_out(prog(lt, 0.0, 0.6)))
    # mikroskop vinyetkasi
    img.alpha_composite(cached(('scope', K), lambda: scope_mask()))
    bar_sweep(img, CX, 360, 720, 100, t, 3.05, (10, 20, 12), anchor='c', alpha=0.85)
    draw_text(img, "BU ODDIY CHANG EMAS", 800, 58, CX, 376, t, 3.11, mode='mask', anchor='c')
    if t >= 4.72:
        draw_text(img, "OIDIUM", 900, 190, CX, 1240, t, 4.72, mode='slam', anchor='c', color=WHITE, glow=(255, 60, 40), track=6)
        bar_sweep(img, CX, 1490, 520, 10, t, 4.9, RED, anchor='c')
        draw_text(img, "Erysiphe necator — un shudring", 600, 38, CX, 1520, t, 5.1, mode='rise', anchor='c', color=(235, 235, 235))
    return canvas_from(img), dict(temp=-0.4, sat=0.9, contrast=1.08)

def scope_mask():
    yy, xx = np.ogrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.42)) ** 2).astype(np.float32)
    a = npsmooth(0.85, 1.12, d) * 0.88
    im = Image.new('RGBA', (W, H), (4, 10, 6, 0)); im.putalpha(np2im(a * 255).convert('L')); return im

# ================================================================ S3  6.1 – 12.4  bir haftada / quriydi / yoriladi / chiriydi
def s3(t):
    if t < 9.75: return s3_leaf(t)
    return s3_grapes(t)

def s3_leaf(t):
    lt = t - 6.1
    cover = 0.3 + 0.75 * ease_io(prog(t, 6.3, 8.2))
    necro = ease_io(prog(t, 8.45, 9.5))
    img = bg_view('cold' if t > 8.4 else 'warm', t, zoom=1.05)
    lf = leaf_rgba(powder=cover * (1 - 0.75 * necro), necro=necro, back=0.55 * (1 - necro * 0.7), sat=1 - 0.35 * necro)
    z = 1.0 - 0.12 * ease_io(lt / 3.6)
    sx, sy = cam_shake(t, 2)
    place_leaf(img, lf, CX + sx, 900 + sy, 1150 * z, 8 * math.sin(lt * 0.4) + 6 * necro)
    # kun hisoblagichi
    if t < 8.45:
        day = 1 + int(6 * ease_io(prog(t, 6.4, 8.1)))
        a = ease_out(prog(t, 6.3, 6.6)) * (1 - prog(t, 8.2, 8.45))
        paste(img, pill(ki(300), ki(96), (0, 0, 0), 150), (k(CX - 150), k(150)), a)
        draw_text(img, f"{day}-KUN", 900, 60, CX, 160, t, 6.3, mode='fade', anchor='c', color=GOLD, alpha=a / max(a, 1e-3) if a > 0 else 0)
        draw_text(img, "BIR HAFTADA", 800, 60, CX, 1440, t, 6.34, mode='mask', anchor='c', t_out=8.2)
        draw_text(img, "BUTUN TOKNI QOPLAYDI", 900, 72, CX, 1520, t, 6.9, mode='mask', anchor='c', color=GOLD, t_out=8.2)
    else:
        bar_sweep(img, CX, 1470, 760, 100, t, 8.55, (120, 30, 20), anchor='c', alpha=0.9)
        draw_text(img, "BARGLAR QURIYDI", 900, 76, CX, 1478, t, 8.6, mode='mask', anchor='c')
    return canvas_from(img), dict(temp=0.3 - 0.9 * necro, sat=1 - 0.3 * necro, contrast=1.05)

def s3_grapes(t):
    lt = t - 9.75
    rot = ease_io(prog(t, 11.3, 12.3))
    crack = ease_out(prog(t, 9.9, 10.9))
    img = bg_view('dark' if rot > 0.3 else 'cold', t, zoom=1.1)
    st = dict(powder=0.75, crack=crack, rot=rot, crack_frac=0.4, rot_frac=0.75)
    size = ki(1000) * (1.0 + 0.10 * ease_io(lt / 2.6))
    sx, sy = cam_shake(t, 3)
    items = r3d.grape_cluster(k(CX + sx), k(820 + sy), size, 0.15 * lt + 0.5, seed=7,
                              color=(0.24 + 0.1 * rot, 0.05 + 0.05 * rot, 0.14 - 0.06 * rot), state=st, n=95)
    lay = render_items_layer(items, light=r3d.LIGHT)
    paste(img, shadow_of(lay, k(40), 0.5), (k(30), k(50)))
    paste(img, lay, (0, 0))
    if t < 11.25:
        bar_sweep(img, CX, 1470, 840, 100, t, 9.9, (120, 30, 20), anchor='c', alpha=0.9)
        draw_text(img, "G'UJUMLAR YORILADI", 900, 72, CX, 1480, t, 9.95, mode='mask', anchor='c')
    else:
        bar_sweep(img, CX, 1470, 700, 100, t, 11.3, (70, 40, 20), anchor='c', alpha=0.9)
        draw_text(img, "HOSIL CHIRIYDI", 900, 76, CX, 1478, t, 11.33, mode='mask', anchor='c')
    return canvas_from(img), dict(temp=-0.3 - 0.4 * rot, sat=0.95 - 0.35 * rot, contrast=1.1)

# ================================================================ S4 12.4 – 16.2 mildyu
def s4(t):
    lt = t - 12.4
    m = 0.15 + 0.85 * ease_io(prog(t, 12.6, 15.6))
    img = bg_view('cold', t, zoom=1.08)
    lf = leaf_rgba(mildew=m, back=0.35, light=(0.3, -0.7, 0.6), sat=0.85)
    z = 1.05 + 0.12 * ease_io(lt / 3.8)
    sx, sy = cam_shake(t, 2)
    place_leaf(img, lf, CX - 30 + sx, 820 + sy, 1180 * z, 160 + 4 * math.sin(lt * 0.5))
    draw_text(img, "ORTIDAN", 800, 56, 110, 1290, t, 12.64, mode='mask')
    draw_text(img, "MILDYU", 900, 170, 100, 1350, t, 12.9, mode='mask', color=(240, 225, 90), glow=(200, 160, 30), track=4)
    bar_sweep(img, 110, 1585, 700, 76, t, 14.24, (60, 50, 10), alpha=0.85)
    draw_text(img, "sarg'ish moyli dog'lar", 700, 52, 134, 1594, t, 14.3, mode='mask')
    return canvas_from(img), dict(temp=-0.2, sat=0.95, contrast=1.06)

# ================================================================ S5 16.2 – 20.8 pomidor, bodring, shaftoli
def s5(t):
    lt = t - 16.2
    img = bg_view('dark', t, zoom=1.05)
    sp = ease_io(prog(t, 17.6, 20.2)); blk = ease_io(prog(t, 18.9, 20.5))
    kind = 'black' if blk > 0.5 else 'brown'
    def tsp(e): return [(0.25, -0.1, 0.20, kind, sp), (-0.35, 0.25, 0.14, kind, sp * 0.8), (0.0, 0.45, 0.10, 'brown', sp * 0.7), (-0.15, -0.4, 0.12, kind, sp * 0.6)]
    def csp(e): return [(0.4, 0.0, 0.10, kind, sp), (-0.2, 0.1, 0.07, kind, sp * 0.9), (-0.6, -0.1, 0.08, 'brown', sp * 0.8), (0.05, -0.2, 0.06, kind, sp * 0.7)]
    def psp(e): return [(0.3, 0.25, 0.22, 'brown', sp), (-0.3, -0.2, 0.12, kind, sp * 0.8), (0.0, -0.5, 0.08, kind, sp * 0.6)]
    items = []
    ap = [ease_back(prog(t, ta, ta + 0.45)) for ta in (16.44, 16.85, 17.25)]
    float_ = lambda i: 10 * math.sin(lt * 1.2 + i)
    if ap[0] > 0: items += r3d.tomato(k(330), k(540 + float_(0) + (1 - ap[0]) * 300), k(290), spots=tsp)
    if ap[1] > 0: items += r3d.cucumber(k(700), k(930 + float_(1) + (1 - ap[1]) * 300), k(140), rot=-0.5, spots=csp)
    if ap[2] > 0: items += r3d.peach(k(340), k(1270 + float_(2) + (1 - ap[2]) * 300), k(250), spots=psp)
    if items:
        lay = render_items_layer(items)
        paste(img, shadow_of(lay, k(40), 0.6), (k(25), k(45)))
        paste(img, lay, (0, 0))
    draw_text(img, "Pomidor", 800, 60, 660, 470, t, 16.44, mode='mask')
    draw_text(img, "Bodring", 800, 60, 560, 1120, t, 16.85, mode='mask')
    draw_text(img, "Shaftoli", 800, 60, 640, 1300, t, 17.25, mode='mask')
    bar_sweep(img, CX, 1560, 900, 170, t, 17.9, (0, 0, 0), anchor='c', alpha=0.55)
    draw_text(img, "DOG'LANISH", 900, 76, CX, 1568, t, 17.95, mode='mask', anchor='c', color=(250, 190, 70))
    draw_text(img, "VA QORAYISH", 900, 64, CX, 1648, t, 18.9, mode='mask', anchor='c')
    return canvas_from(img), dict(temp=0.1, sat=1.0, contrast=1.08)

# ================================================================ S6 20.8 – 25.4 nam havo, bog'ga tarqaladi
def s6(t):
    lt = t - 20.8
    def mk():
        rgb, can = aerial_vineyard(int(W * 1.25), int(H * 1.25), seed=4)
        return rgb, can
    rgb, can = cached(('aerial', K), mk)
    sp = ease_io(prog(t, 21.6, 25.0))
    # infeksiya tarqalishi
    inf_f = cached(('aer_inf', K), lambda: aerial_field(rgb.shape[1], rgb.shape[0]))
    thr = -0.05 + sp * 1.05
    m = npsmooth(thr, thr - 0.07, inf_f) * can
    sick = np.array([0.62, 0.60, 0.48], np.float32)
    out = rgb * (1 - m[..., None] * 0.75) + sick * (rgb.mean(2, keepdims=True) * 1.6) * (m[..., None] * 0.75)
    src = np2im(out * 255)
    z = 1.0 + 0.18 * ease_io(lt / 4.6)
    sp_ = 0.75
    ow = int(W * (1 + 2 * sp_))
    v = view(src, src.width / 2, src.height / 2 + lt * k(10), src.width / ow * z * 0.9, out_size=(ow, H))
    # dron kamerasi: perspektiva (yuqori qism uzoqda)
    v = v.transform((W, H), Image.QUAD, (0, 0, W * sp_, H, W * (1 + sp_), H, ow, 0), Image.BICUBIC)
    img = v.convert('RGBA')
    haze = cached(('haze', K), lambda: rgba_from(np.ones((H, W, 3), np.float32) * np.array([0.72, 0.78, 0.80], np.float32),
                                                 np.repeat(np.clip(1 - np.linspace(0, 1, H) / 0.45, 0, 1)[:, None] ** 1.5, W, 1) * 0.85))
    img.alpha_composite(haze)
    # tuman va yomg'ir
    fog = cached(('fog', K), lambda: fog_layer())
    off = int((t * 40 * K) % (W * 0.5))
    fv = fog.crop((off, 0, off + W, H))
    paste(img, fv, (0, 0), 0.75)
    rain = cached(('rain', K), lambda: rain_layer())
    ro = int((t * 2200 * K) % rain.height)
    rv = Image.new('RGBA', (W, H)); rv.alpha_composite(rain.crop((0, ro, W, min(rain.height, ro + H))))
    if ro + H > rain.height: rv.alpha_composite(rain.crop((0, 0, W, ro + H - rain.height)), (0, rain.height - ro))
    paste(img, rv, (0, 0), 0.55)
    bar_sweep(img, CX, 300, 700, 96, t, 21.0, (10, 40, 60), anchor='c', alpha=0.85)
    draw_text(img, "HAVO NAM BO'LSA", 900, 66, CX, 310, t, 21.08, mode='mask', anchor='c')
    draw_text(img, "KASALLIK BUTUN BOG'GA", 900, 66, CX, 1400, t, 22.6, mode='mask', anchor='c')
    draw_text(img, "TARQALADI", 900, 120, CX, 1480, t, 23.6, mode='slam', anchor='c', color=(255, 90, 70))
    return canvas_from(img), dict(temp=-0.7, sat=0.8, contrast=1.05)

def aerial_field(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    seeds = [(0.30, 0.35), (0.70, 0.62), (0.45, 0.80)]
    d = np.ones((h, w), np.float32) * 9
    for (u, v) in seeds: d = np.minimum(d, np.hypot(xx / w - u, yy / h - v))
    return d * 1.4 + (fbm(w, h, 5, seed=21, base=5) - 0.5) * 0.5

def fog_layer():
    w, h = int(W * 1.5), H
    n = fbm(w // 4, h // 4, 5, seed=30, base=3)
    a = np.clip((n - 0.35) * 1.6, 0, 1) * 150
    im = Image.new('RGBA', (w // 4, h // 4), (200, 215, 220, 0)); im.putalpha(np2im(a).convert('L'))
    return im.resize((w, h), Image.BICUBIC)

def rain_layer():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rng = random.Random(9)
    for i in range(900):
        x = rng.uniform(0, W); y = rng.uniform(0, H); l = rng.uniform(40, 110) * K
        d.line((x, y, x - l * 0.12, y + l), fill=(210, 225, 235, rng.randint(40, 120)), width=max(1, ki(1.2)))
    return im.filter(ImageFilter.GaussianBlur(0.6 * K))

# ================================================================ S7 25.4 – 29.1 bir yillik mehnat
def s7(t):
    lt = t - 25.4
    img = bg_view('dark', t, zoom=1.15 + 0.05 * lt / 3.7)
    items = []
    sw = math.sin(lt * 0.9) * 0.08
    items += r3d.grape_cluster(k(260), k(520), ki(700), 0.3 + sw, seed=11, color=(0.34, 0.22, 0.10), state=dict(rot=1.0, rot_frac=1.0, powder=0.5), n=70)
    lay_far = render_items_layer(items)
    paste(img, fast_blur_img(lay_far, k(10)), (0, 0), 0.8)
    near = r3d.grape_cluster(k(640), k(820), ki(1100), 0.2 - sw, seed=12, color=(0.36, 0.22, 0.10), state=dict(rot=1.0, rot_frac=0.95, powder=0.4, crack=0.6), n=95)
    lay = render_items_layer(near, rim_col=(1.4, 0.95, 0.55), env=0.45)
    paste(img, shadow_of(lay, k(40), 0.6), (k(30), k(50)))
    paste(img, lay, (0, 0))
    draw_text(img, "BIR YILLIK", 800, 66, CX, 1330, t, 25.58, mode='mask', anchor='c', color=(230, 220, 200))
    draw_text(img, "MEHNATINGIZ", 900, 96, CX, 1410, t, 25.9, mode='mask', anchor='c', color=WHITE)
    bar_sweep(img, CX, 1560, 820, 92, t, 26.9, (110, 20, 15), anchor='c', alpha=0.92)
    draw_text(img, "BIR NECHA KUNDA", 900, 62, CX, 1570, t, 26.95, mode='mask', anchor='c')
    draw_text(img, "yo'qqa chiqishi mumkin", 700, 50, CX, 1680, t, 27.7, mode='mask', anchor='c', color=(220, 210, 200))
    return canvas_from(img), dict(temp=0.25, sat=0.6, contrast=1.1)

# ================================================================ S8 29.1 – 31.3 To'xtang! Endi yechim bor
def s8(t):
    if t < 30.0:
        base, gp = s7(29.1)                    # muzlatilgan kadr
        l = base.mean(2, keepdims=True); base = l + (base - l) * 0.15
        base = base * 0.6
        img = np2im(base).convert('RGBA')
        sx, sy = cam_shake(t * 8, 14) if t < 29.6 else (0, 0)
        draw_text(img, "TO'XTANG!", 900, 150, CX + sx, 780 + sy, t, 29.22, mode='slam', anchor='c', color=(255, 60, 50), glow=(255, 40, 20), track=4, dur=0.25)
        return canvas_from(img), dict(contrast=1.15)
    lt = t - 30.0
    img = bg_view('green', t, zoom=1.0)
    burst = ease_out(prog(t, 30.0, 30.5))
    r = cached(('rays_big', K), lambda: rays_img())
    rr = r.rotate(lt * 12, resample=Image.BILINEAR)
    place(img, rr, CX, 900, 0.6 * burst, scale=0.6 + 0.6 * burst)
    flare(img, CX, 900, 900, 0.9 * burst)
    draw_text(img, "ENDI", 800, 70, CX, 1300, t, 30.02, mode='mask', anchor='c')
    draw_text(img, "YECHIM BOR", 900, 128, CX, 1390, t, 30.25, mode='slam', anchor='c', color=GOLD, glow=(255, 200, 60), dur=0.3)
    white = 1 - ease_out(prog(t, 30.0, 30.35))
    arr = canvas_from(img) + 255 * white * 0.9
    return arr, dict(temp=0.3, sat=1.1)

def rays_img():
    S = 1600; rng = random.Random(3)
    m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m); c = S / 2
    for i in range(18):
        a0 = rng.uniform(0, 2 * math.pi); wd = rng.uniform(0.03, 0.10)
        d.polygon([(c, c), (c + S * math.cos(a0), c + S * math.sin(a0)), (c + S * math.cos(a0 + wd), c + S * math.sin(a0 + wd))], fill=rng.randint(60, 120))
    m = m.filter(ImageFilter.GaussianBlur(8))
    yy, xx = np.ogrid[0:S, 0:S]
    fall = np.clip(1 - np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / (S * 0.5), 0, 1) ** 1.2
    im = Image.new('RGBA', (S, S), (255, 245, 200, 0)); im.putalpha(np2im(np.asarray(m, np.float32) * fall).convert('L'))
    return im.resize((ki(2400), ki(2400)), Image.BILINEAR)

# ================================================================ S9 31.3 – 34.2 AZDIF — keng ta'sirli fungitsid
def s9(t):
    lt = t - 31.3
    img = bg_view('green', t, zoom=1.0 + 0.03 * lt)
    r = cached(('rays_big', K), lambda: rays_img())
    place(img, r.rotate(lt * 8, resample=Image.BILINEAR), CX, 820, 0.4)
    # katta "AZDIF" flakon ortida
    a = ease_out(prog(t, 31.42, 31.8))
    if a > 0:
        im, pad, tw, th = text_img("AZDIF", 900, 330, (255, 255, 255), 6, 0.0)
        s = (1.25 - 0.25 * a) * (1 + 0.02 * lt)
        place(img, im, CX, 760, 0.22 * a, scale=s)
    p = ease_out(prog(t, 31.3, 31.9))
    bh = bottle_hero(1060, prog(t, 31.8, 32.9))
    z = 0.9 + 0.1 * p + 0.03 * lt
    place(img, bh, CX, 360 + bh.height / K / 2 * z + (1 - p) * 300, p, scale=z)
    flare(img, CX + 260, 330, 600, 0.5 * ease_out(prog(t, 32.0, 32.6)))
    particles(img, t, 9, 30, (0, 0, LW, LH), (220, 255, 190), (1.5, 4), (0, -25), 0.5)
    draw_text(img, "AZDIF", 900, 150, CX, 1440, t, 31.42, mode='slam', anchor='c', glow=(150, 255, 120), track=6, dur=0.3)
    bar_sweep(img, CX, 1640, 900, 84, t, 32.2, (255, 200, 70), anchor='c')
    draw_text(img, "TA'SIR DOIRASI KENG FUNGITSID", 900, 44, CX, 1658, t, 32.3, mode='mask', anchor='c', color=(25, 50, 20), shadow=0)
    return canvas_from(img), dict(temp=0.2, sat=1.08, contrast=1.05)

# ================================================================ S10 34.2 – 38.45 ikki kuchli modda
def s10(t):
    lt = t - 34.2
    img = bg_view('green', t, zoom=1.12)
    dark = Image.new('RGBA', (W, H), (0, 15, 8, 110)); img.alpha_composite(dark)
    draw_text(img, "UNDA IKKI KUCHLI", 800, 60, CX, 120, t, 34.37, mode='mask', anchor='c')
    draw_text(img, "MODDA BOR", 900, 96, CX, 190, t, 34.75, mode='mask', anchor='c', color=GOLD)
    for (mol, cy, tin, name, dose, col) in [(r3d.azoxystrobin(), 650, 36.22, "AZOKSISTROBIN", "250 g/l", (90, 180, 255)),
                                            (r3d.difenoconazole(), 1220, 37.25, "DIFENOKONAZOL", "200 g/l", (255, 175, 60))]:
        a = ease_back(prog(t, tin - 0.15, tin + 0.5))
        if a <= 0: continue
        glow = cached(('mglow', col, K), lambda col=col: glow_disc(560, col))
        place(img, glow, CX, cy, 0.55 * clamp(a))
        items = r3d.molecule_items(mol, k(CX), k(cy), k(88) * clamp(a, 0, 1.2), 0.5 + 0.35 * t, 0.8 * t + tin, 0.15)
        lay = render_items_layer(items, rim_col=tuple(c / 255 for c in col))
        paste(img, lay, (0, 0))
        draw_text(img, name, 900, 64, CX, cy + 240, t, tin, mode='mask', anchor='c')
        draw_text(img, dose, 800, 54, CX, cy + 320, t, tin + 0.2, mode='mask', anchor='c', color=col)
    draw_text(img, "+", 900, 90, CX, 1010, t, 37.1, mode='fade', anchor='c')
    return canvas_from(img), dict(temp=0.0, sat=1.05, contrast=1.06)

def glow_disc(size, col):
    s = ki(size); yy, xx = np.ogrid[0:s, 0:s]
    d = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / (s / 2)
    a = np.clip(1 - d, 0, 1) ** 2 * 200
    im = Image.new('RGBA', (s, s), col + (0,)); im.putalpha(np2im(a).convert('L')); return im

# ================================================================ S11 38.45 – 44.6 tashqaridan / ichkaridan (barg kesimi)
def s11(t):
    lt = t - 38.45
    base = cached(('xsec', K), lambda: xsection_base())
    img = base.copy()
    z = 1.0 + 0.06 * ease_io(lt / 6)
    # gifalar: yuzada va ichkarida
    surf_kill = ease_io(prog(t, 39.4, 40.6)); in_kill = ease_io(prog(t, 42.0, 43.8))
    hy_s = cached(('xs_hs', K), lambda: xs_hyphae('surface'))
    hy_i = cached(('xs_hi', K), lambda: xs_hyphae('inside'))
    paste(img, tint(hy_s, surf_kill), (0, 0), 1 - 0.85 * surf_kill)
    paste(img, tint(hy_i, in_kill), (0, 0), 1 - 0.85 * in_kill)
    # ko'k zarrachalar — tashqi himoya qatlami
    rng = random.Random(4)
    pa = prog(t, 38.57, 39.6)
    for i in range(120):
        x = rng.uniform(40, LW - 40); d0 = rng.uniform(0, 0.6)
        p = ease_io(clamp((pa - d0 * 0.6) / 0.5))
        if p <= 0: continue
        y = lerp(80, 655 + rng.uniform(-6, 6), p)
        place(img, dot_sprite(rng.uniform(4, 8), (90, 190, 255)), x, y, 0.9)
    film = ease_out(prog(t, 39.3, 40.0))
    if film > 0:
        f = cached(('xs_film', K), lambda: film_layer())
        paste(img, f, (0, 0), film * (0.85 + 0.15 * math.sin(t * 6)))
    # to'q sariq zarrachalar — ichkariga kiradi
    pb = prog(t, 40.96, 43.6)
    rng = random.Random(8)
    for i in range(90):
        x0 = rng.uniform(60, LW - 60); d0 = rng.uniform(0, 0.5)
        p = clamp((pb - d0 * 0.7) / 0.6)
        if p <= 0: continue
        y = lerp(80, rng.uniform(740, 1420), ease_io(p)); x = x0 + 25 * math.sin(p * 6 + i)
        place(img, dot_sprite(rng.uniform(4, 7), (255, 160, 40)), x, y, 0.95 * (1 - 0.5 * prog(p, 0.9, 1)))
    if pb > 0.3:
        gl = cached(('xs_glow', K), lambda: inner_glow())
        paste(img, gl, (0, 0), 0.5 * ease_io(prog(t, 41.6, 42.6)) * (0.8 + 0.2 * math.sin(t * 5)))
    # yorliqlar
    draw_text(img, "TASHQARIDAN", 900, 64, CX, 190, t, 38.57, mode='mask', anchor='c', color=(120, 200, 255))
    draw_text(img, "HIMOYA QILADI", 800, 50, CX, 270, t, 38.9, mode='mask', anchor='c')
    draw_text(img, "ICHKARIDAN", 900, 64, CX, 1520, t, 40.96, mode='mask', anchor='c', color=(255, 175, 60))
    draw_text(img, "KASALLIKNI TO'XTATADI", 800, 50, CX, 1600, t, 41.5, mode='mask', anchor='c')
    draw_text(img, "barg kesimi", 600, 30, 70, 600, t, 38.6, mode='fade', color=(200, 220, 200))
    if z != 1.0:
        arr = canvas_from(img)
        return arr, dict(temp=0.0, sat=1.05)
    return canvas_from(img), dict(temp=0.0, sat=1.05)

def tint(im, kill):
    if kill <= 0.01: return im
    arr = np.asarray(im, np.float32).copy()
    arr[..., :3] = arr[..., :3] * (1 - kill) + np.array([120, 90, 60], np.float32) * kill
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')

def xsection_base():
    """Barg kesimi: kutikula, epiderma, ustunsimon va g'ovak to'qima."""
    img = np2im(vgrad(H, W, [(0, (10, 30, 40)), (0.30, (24, 60, 70)), (0.33, (10, 25, 15)), (1, (6, 18, 10))])).convert('RGBA')
    d = ImageDraw.Draw(img)
    rng = random.Random(2)
    top = k(660)
    def cell(x0, y0, x1, y1, col, rad):
        S = 2
        w, h = int(x1 - x0), int(y1 - y0)
        if w < 4 or h < 4: return
        m = Image.new('L', (w * S, h * S), 0)
        ImageDraw.Draw(m).rounded_rectangle((2, 2, w * S - 3, h * S - 3), rad * S, fill=255)
        m = m.resize((w, h), Image.LANCZOS)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        g = 1 - 0.35 * (np.hypot((xx - w * 0.4) / w, (yy - h * 0.35) / h))
        c = np.array(col, np.float32) * g[..., None]
        rim = np.asarray(m.filter(ImageFilter.FIND_EDGES), np.float32)[..., None] / 255
        c = c * (1 - rim * 0.5) + np.array([200, 255, 180], np.float32) * rim * 0.4
        ci = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8)).convert('RGBA'); ci.putalpha(m)
        img.alpha_composite(ci, (int(x0), int(y0)))
        return ci
    # kutikula
    d.rectangle((0, top - k(8), W, top + k(4)), fill=(190, 230, 170, 255))
    # yuqori epiderma
    x = -k(20)
    while x < W:
        w = k(rng.uniform(80, 120)); cell(x + k(3), top + k(6), x + w - k(3), top + k(90), (120, 170, 90), ki(16)); x += w
    # ustunsimon to'qima
    x = -k(10)
    y0 = top + k(98)
    while x < W:
        w = k(rng.uniform(48, 62))
        cell(x + k(3), y0, x + w - k(3), y0 + k(330), (60, 140, 50), ki(22))
        for j in range(9):
            cx = x + w / 2 + rng.uniform(-w * 0.25, w * 0.25); cy = y0 + k(30) + j * k(34) + rng.uniform(-8, 8) * K
            r = k(rng.uniform(8, 12))
            d.ellipse((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), fill=(30, 110, 30, 255))
        x += w
    # g'ovak to'qima
    for i in range(80):
        cx = rng.uniform(0, W); cy = y0 + k(345) + rng.uniform(0, k(330))
        rw = k(rng.uniform(45, 85)); rh = k(rng.uniform(35, 60))
        cell(cx - rw, cy - rh, cx + rw, cy + rh, (70, 130, 60), ki(30))
    # pastki epiderma
    yb = y0 + k(700)
    x = -k(30)
    while x < W:
        w = k(rng.uniform(80, 120)); cell(x + k(3), yb, x + w - k(3), yb + k(70), (110, 160, 85), ki(14)); x += w
    shade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = np.zeros((H, W), np.float32); sd[int(yb + k(80)):, :] = 200
    shade.putalpha(np2im(sd).convert('L')); img.alpha_composite(shade)
    return img

def xs_hyphae(kind):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rng = random.Random(5 if kind == 'surface' else 6)
    col = (235, 240, 235)
    if kind == 'surface':
        for i in range(14):
            x = rng.uniform(0, W); y = k(640)
            pts = [(x, y)]
            for j in range(30):
                x += k(rng.uniform(8, 16)) * rng.choice([-1, 1]) * 0.6 + k(6); y = k(640) + k(6) * math.sin(j * 0.7 + i) - k(4)
                pts.append((x, y))
            d.line(pts, fill=col + (230,), width=ki(5), joint='curve')
            # konidiya zanjiri
            bx = pts[len(pts) // 2][0]
            for s in range(5):
                cy = k(620) - s * k(22); d.ellipse((bx - k(9), cy - k(10), bx + k(9), cy + k(10)), fill=col + (220,))
            # haustoriya — epiderma ichiga
            hx = pts[8][0]; d.line((hx, k(650), hx, k(700)), fill=col + (230,), width=ki(4))
            d.ellipse((hx - k(14), k(700), hx + k(14), k(730)), fill=col + (210,))
    else:
        for i in range(10):
            x = rng.uniform(0, W); y = k(rng.uniform(1100, 1400)); a = rng.uniform(0, 6.28)
            pts = [(x, y)]
            for j in range(40):
                a += rng.uniform(-0.5, 0.5); x += math.cos(a) * k(14); y += math.sin(a) * k(10)
                y = min(max(y, k(780)), k(1450)); pts.append((x, y))
            d.line(pts, fill=(220, 225, 210, 210), width=ki(5), joint='curve')
    return im.filter(ImageFilter.GaussianBlur(0.8 * K))

def film_layer():
    a = np.zeros((H, W), np.float32)
    y = int(k(650)); a[y - ki(14):y + ki(6), :] = 1
    a = blur_np(a, k(8)) * 220
    im = Image.new('RGBA', (W, H), (90, 190, 255, 0)); im.putalpha(np2im(a).convert('L')); return im

def inner_glow():
    a = np.zeros((H, W), np.float32); a[int(k(760)):int(k(1450)), :] = 1
    a = blur_np(a, k(40)) * 120
    im = Image.new('RGBA', (W, H), (255, 150, 40, 0)); im.putalpha(np2im(a).convert('L')); return im

# ================================================================ S12 44.6 – 51.8 kasalliklar ro'yxati — bitta preparat
DISEASES = [("Oidium", 44.84), ("Mildyu", 45.5), ("Soxta un shudring", 46.36), ("Dog'lanish", 47.65), ("Qorayish", 48.3)]

def disease_thumb(i):
    def mk():
        s = ki(260)
        L = leaf_data(); S = L['S']
        if i == 0: rgb, a = compose_leaf(L, powder=0.8); src = rgb[int(S * .3):int(S * .55), int(S * .3):int(S * .55)]
        elif i == 1: rgb, a = compose_leaf(L, mildew=0.9); src = rgb[int(S * .25):int(S * .5), int(S * .3):int(S * .55)]
        elif i == 2:
            rgb, a = compose_leaf(L, mildew=0.9, powder=0.5); src = rgb[int(S * .35):int(S * .6), int(S * .4):int(S * .65)]
            src = src * np.array([0.85, 0.82, 0.92], np.float32)
        elif i == 3:
            c, al = r3d.render(r3d.tomato(s / 2, s / 2, s * 0.62, spots=lambda e: [(0.2, 0.0, 0.25, 'brown', 1), (-0.3, -0.3, 0.15, 'black', 1), (-0.1, 0.4, 0.12, 'brown', 1)]), s, s)
            src = c * al[..., None] + np.array([0.1, 0.12, 0.08]) * (1 - al[..., None])
        else:
            items = r3d.grape_cluster(s / 2, s / 2 + s * 0.05, s * 1.6, 0.4, seed=3, color=(0.12, 0.08, 0.05), state=dict(rot=1, rot_frac=1), n=60)
            c, al = r3d.render(items, s, s)
            src = c * al[..., None] + np.array([0.08, 0.08, 0.06]) * (1 - al[..., None])
        im = np2im(np.asarray(src) * 255).resize((s, s), Image.LANCZOS).convert('RGBA')
        m = Image.new('L', (s * 2, s * 2), 0); ImageDraw.Draw(m).ellipse((0, 0, s * 2 - 1, s * 2 - 1), fill=255)
        im.putalpha(m.resize((s, s), Image.LANCZOS))
        ring = Image.new('RGBA', (s + ki(16), s + ki(16)), (0, 0, 0, 0))
        rm = Image.new('L', (ring.width * 2, ring.height * 2), 0); ImageDraw.Draw(rm).ellipse((0, 0, ring.width * 2 - 1, ring.height * 2 - 1), fill=255)
        ring.putalpha(rm.resize(ring.size, Image.LANCZOS)); ring.alpha_composite(im, (ki(8), ki(8)))
        return ring
    return cached(('dthumb', i, K), mk)

DPOS = [(250, 470), (830, 470), (540, 800), (250, 1130), (830, 1130)]

def s12(t):
    lt = t - 44.6
    img = bg_view('cold' if t < 49.2 else 'green', t, zoom=1.1)
    dk = Image.new('RGBA', (W, H), (0, 0, 0, 90)); img.alpha_composite(dk)
    bt = ease_out(prog(t, 49.26, 49.9))
    for i, (name, tin) in enumerate(DISEASES):
        a = ease_back(prog(t, tin, tin + 0.45))
        if a <= 0: continue
        x, y = DPOS[i]
        if bt > 0:   # preparat chiqqanda qayta joylashadi
            nx_, ny_ = [(190, 330), (890, 330), (540, 250), (190, 820), (890, 820)][i]
            x = lerp(x, nx_, bt); y = lerp(y, ny_, bt)
        th = disease_thumb(i)
        place(img, shadow_of(th, k(20), 0.6), x + 10, y + 16, clamp(a))
        place(img, th, x, y, clamp(a), scale=0.6 + 0.4 * clamp(a, 0, 1.1))
        draw_text(img, name, 800, 40 if len(name) < 12 else 34, x, y + 150, t, tin + 0.1, mode='mask', anchor='c')
        # qizil chiziq — yengildi
        xa = ease_out(prog(t, 49.7 + i * 0.22, 49.95 + i * 0.22))
        if xa > 0:
            ln = Image.new('RGBA', (ki(300), ki(300)), (0, 0, 0, 0)); dd = ImageDraw.Draw(ln)
            L = ki(300) * xa
            dd.line((ki(20), ki(20), ki(20) + (L - ki(40)) * 1.0, ki(20) + (L - ki(40)) * 1.0), fill=(240, 50, 40, 255), width=ki(16))
            place(img, ln, x, y)
    if bt > 0:
        bh = bottle_hero(760, prog(t, 49.7, 50.7), refl=False)
        place(img, bh, CX, 1180 + bh.height / K / 2 * 0 + (1 - bt) * 600 - 80, bt)
    draw_text(img, "BITTA PREPARAT", 900, 70, CX, 1530, t, 49.4, mode='mask', anchor='c', color=GOLD)
    draw_text(img, "BARCHASIGA QARSHI", 900, 70, CX, 1615, t, 50.2, mode='mask', anchor='c')
    return canvas_from(img), dict(temp=-0.2 + 0.4 * bt, sat=1.0, contrast=1.05)

# ================================================================ S13 51.8 – 57.2 ekinlar — bog' va poliz himoyada
def s13(t):
    lt = t - 51.8
    img = bg_view('warm', t, zoom=1.05)
    tins = [52.03, 52.6, 53.2, 53.8]
    names = ["Uzum", "Pomidor", "Bodring", "Shaftoli"]
    pos = [(300, 560), (790, 560), (300, 1080), (790, 1080)]
    items = []
    for i, (tin, (x, y)) in enumerate(zip(tins, pos)):
        a = ease_back(prog(t, tin, tin + 0.4))
        if a <= 0: continue
        fy = y + 8 * math.sin(lt * 1.3 + i) + (1 - clamp(a)) * 250
        if i == 0: items += r3d.grape_cluster(k(x), k(fy), ki(420), 0.3 * lt, seed=21, color=(0.30, 0.06, 0.20), state={}, n=75)
        if i == 1: items += r3d.tomato(k(x), k(fy), k(160))
        if i == 2: items += r3d.cucumber(k(x), k(fy), k(80), rot=-0.6)
        if i == 3: items += r3d.peach(k(x), k(fy), k(150))
    if items:
        lay = render_items_layer(items, rim_col=(1.0, 0.92, 0.7))
        paste(img, shadow_of(lay, k(35), 0.5), (k(20), k(40)))
        paste(img, lay, (0, 0))
    for i, (tin, (x, y)) in enumerate(zip(tins, pos)):
        draw_text(img, names[i], 800, 48, x, y + 230, t, tin + 0.05, mode='mask', anchor='c')
    sh = ease_out(prog(t, 54.7, 55.4))
    if sh > 0:
        dome = cached(('dome', K), lambda: dome_img())
        place(img, dome, CX, 820, sh * (0.75 + 0.25 * math.sin(t * 4)), scale=0.9 + 0.1 * sh)
    bar_sweep(img, CX, 1480, 940, 190, t, 54.7, (20, 90, 40), anchor='c', alpha=0.9)
    draw_text(img, "BOG'INGIZ HAM, POLIZINGIZ HAM", 900, 46, CX, 1500, t, 54.75, mode='mask', anchor='c')
    draw_text(img, "HIMOYADA", 900, 84, CX, 1565, t, 55.5, mode='mask', anchor='c', color=GOLD)
    return canvas_from(img), dict(temp=0.5, sat=1.12, contrast=1.04)

def dome_img():
    s = ki(1100); yy, xx = np.ogrid[0:s, 0:s]
    d = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / (s / 2)
    ring = np.exp(-((d - 0.96) / 0.03) ** 2) * 230 + np.clip(d, 0, 1) ** 6 * 90 * (d < 1)
    hexa = (np.sin(xx * 0.06 / K) * np.sin(yy * 0.06 / K) > 0.85) * 40 * (d < 0.97)
    im = Image.new('RGBA', (s, s), (140, 230, 255, 0)); im.putalpha(np2im(ring + hexa).convert('L'))
    return im.filter(ImageFilter.GaussianBlur(1.5 * K))

# ================================================================ S14 57.2 – 61.7 sog'lom natija
def s14(t):
    if t < 58.5:
        lt = t - 57.2
        img = bg_view('warm', t, zoom=1.0)
        flare(img, 820, 260, 600, 0.6)
        lf = leaf_rgba(heal=0.25, back=0.85, light=(-0.4, -0.7, 0.6))
        place_leaf(img, lf, CX, 860, 1250 * (1 + 0.06 * lt), -6 + 3 * lt)
        drops(img, t, 860, 1250 * (1 + 0.06 * lt))
        draw_text(img, "BARGLAR YASHIL", 900, 80, CX, 1480, t, 57.36, mode='mask', anchor='c')
        return canvas_from(img), dict(temp=0.6, sat=1.15)
    if t < 59.8:
        lt = t - 58.5
        img = bg_view('warm', t, zoom=1.15)
        items = r3d.grape_cluster(k(CX), k(760), ki(1250) * (1 + 0.05 * lt), 0.25 * lt + 1.0, seed=31, color=(0.30, 0.06, 0.20), state={}, n=100)
        lay = render_items_layer(items, rim_col=(1.0, 0.9, 0.7))
        paste(img, shadow_of(lay, k(40), 0.5), (k(25), k(45))); paste(img, lay, (0, 0))
        particles(img, t, 4, 20, (200, 200, 880, 1300), (255, 255, 255), (2, 4), (0, 0), 0.8)
        draw_text(img, "G'UJUMLAR BUTUN", 900, 78, CX, 1480, t, 58.54, mode='mask', anchor='c')
        return canvas_from(img), dict(temp=0.6, sat=1.15)
    lt = t - 59.8
    img = bg_view('warm', t, zoom=1.0 + 0.04 * lt)
    flare(img, 760, 220, 700, 0.7)
    for (x, y, s, sd, col, bl) in [(220, 520, 620, 41, (0.62, 0.70, 0.22), 8), (860, 560, 640, 42, (0.30, 0.06, 0.20), 8),
                                   (540, 820, 1000, 43, (0.26, 0.05, 0.18), 0)]:
        items = r3d.grape_cluster(k(x), k(y), ki(s), 0.2 * lt + sd, seed=sd, color=col, state={}, n=85)
        lay = render_items_layer(items, rim_col=(1.0, 0.9, 0.7))
        if bl: lay = fast_blur_img(lay, k(bl))
        else: paste(img, shadow_of(lay, k(40), 0.5), (k(25), k(45)))
        paste(img, lay, (0, 0))
    bar_sweep(img, CX, 1470, 860, 110, t, 59.82, (255, 200, 70), anchor='c')
    draw_text(img, "HOSIL TOZA VA MO'L", 900, 70, CX, 1486, t, 59.9, mode='mask', anchor='c', color=(25, 50, 20), shadow=0)
    return canvas_from(img), dict(temp=0.7, sat=1.15)

def drops(img, t, cy, size):
    rng = random.Random(5)
    for i in range(26):
        x = CX + rng.uniform(-0.3, 0.3) * size; y = cy + rng.uniform(-0.28, 0.2) * size
        r = rng.uniform(6, 16)
        place(img, drop_sprite(r), x, y, 0.95)

def drop_sprite(r):
    def mk():
        rr = ki(r); S = int(rr * 2.6) + 4; c = S / 2
        yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
        d = np.hypot((xx - c) / rr, (yy - c) / (rr * 0.9))
        a = np.clip((1 - d) * rr * 0.5, 0, 1)
        rim = np.clip(d, 0, 1) ** 4
        hl = np.clip(1 - np.hypot((xx - c + rr * 0.35) / (rr * 0.25), (yy - c + rr * 0.35) / (rr * 0.18)), 0, 1)
        lo = np.clip(1 - np.hypot((xx - c - rr * 0.2) / (rr * 0.5), (yy - c - rr * 0.45) / (rr * 0.25)), 0, 1)
        rgb = np.zeros((S, S, 3), np.float32) + np.array([0.75, 0.9, 0.6]) * (0.4 + 0.5 * rim[..., None]) + hl[..., None] + lo[..., None] * np.array([0.6, 0.9, 0.4]) * 0.6
        al = a * (0.25 + 0.6 * rim + hl + 0.4 * lo)
        sh = np.clip(1 - np.hypot((xx - c - rr * 0.25) / rr, (yy - c - rr * 0.3) / (rr * 0.9)), 0, 1) * 0.0
        return rgba_from(rgb, np.clip(al, 0, 1))
    return cached(('drop', round(r, 1), K), mk)

# ================================================================ S15 61.7 – 64.45 AZDIF — Aziya Agro do'konlarida
def packshot(t, lt, end=False):
    img = bg_view('green', t, zoom=1.0 + 0.02 * lt)
    r = cached(('rays_big', K), lambda: rays_img())
    place(img, r.rotate(t * 6, resample=Image.BILINEAR), CX, 640, 0.35)
    # yon tomonlarda xira uzum shingillari
    side = cached(('side_grapes', K), lambda: side_grapes())
    paste(img, side, (0, 0), 0.9)
    return img

def side_grapes():
    items = r3d.grape_cluster(k(80), k(420), ki(700), 0.6, seed=51, color=(0.30, 0.06, 0.20), state={}, n=80)
    items += r3d.grape_cluster(k(1010), k(520), ki(640), 1.2, seed=52, color=(0.62, 0.70, 0.22), state={}, n=80)
    lay = render_items_layer(items, rim_col=(1.0, 0.9, 0.7))
    return fast_blur_img(lay, k(14))

def s15(t):
    lt = t - 61.7
    img = packshot(t, lt)
    p = ease_out(prog(t, 61.7, 62.2))
    bh = bottle_hero(1000, prog(t, 61.9, 63.0))
    place(img, bh, CX, 240 + bh.height / K / 2 + (1 - p) * 150, p, scale=1 + 0.02 * lt)
    flare(img, CX + 250, 230, 600, 0.45)
    draw_text(img, "AZDIF", 900, 150, CX, 1330, t, 61.86, mode='slam', anchor='c', glow=(150, 255, 120), track=6, dur=0.3)
    pin = cached(('pin', K), lambda: pin_icon())
    a = ease_back(prog(t, 62.7, 63.1))
    if a > 0: place(img, pin, 150, 1585, clamp(a), scale=clamp(a, 0, 1.2))
    draw_text(img, "AZIYA AGRO", 900, 72, 210, 1530, t, 62.71, mode='mask', color=GOLD)
    draw_text(img, "DO'KONLARIDA", 900, 72, 210, 1610, t, 63.0, mode='mask')
    return canvas_from(img), dict(temp=0.2, sat=1.08)

def pin_icon():
    s = ki(110); S = 3
    m = Image.new('L', (s * S, int(s * 1.3) * S), 0); d = ImageDraw.Draw(m)
    w = s * S
    d.ellipse((w * 0.1, 0, w * 0.9, w * 0.8), fill=255)
    d.polygon([(w * 0.18, w * 0.55), (w * 0.82, w * 0.55), (w * 0.5, w * 1.25)], fill=255)
    d.ellipse((w * 0.35, w * 0.25, w * 0.65, w * 0.55), fill=0)
    m = m.resize((s, int(s * 1.3)), Image.LANCZOS)
    im = Image.new('RGBA', m.size, GOLD + (0,)); im.putalpha(m); return im

# ================================================================ S16 64.45 – 70.0 brend yakuni
def s16(t):
    lt = t - 64.45
    img = packshot(t, lt + 3)
    dk = Image.new('RGBA', (W, H), (0, 20, 8, int(90 * ease_io(prog(t, 64.45, 65.0))))); img.alpha_composite(dk)
    bh = bottle_hero(760)
    place(img, bh, CX, 1270, 1.0, scale=1.0)
    logo = cached(('logo', K), lambda: brand_logo())
    a = ease_back(prog(t, 64.57, 65.1))
    if a > 0: place(img, logo, CX, 360, clamp(a), scale=0.85 + 0.15 * clamp(a, 0, 1.1))
    draw_text(img, "Minglab dehqonlarning", 700, 52, CX, 560, t, 65.65, mode='mask', anchor='c')
    draw_text(img, "ishonchini oqlagan", 800, 52, CX, 630, t, 66.1, mode='mask', anchor='c', color=GOLD)
    draw_text(img, "AZDIF 45% S.C.  •  500 ml", 800, 40, CX, 1620, t, 66.3, mode='rise', anchor='c')
    sa = ease_out(prog(t, 66.6, 67.1))
    if sa > 0:
        paste(img, Image.new('RGBA', (W, ki(130)), (0, 0, 0, 150)), (0, H - ki(130)), sa)
        draw_text(img, "Bolalar qo'li yetmaydigan joyda saqlang.", 600, 30, CX, 1808, t, 66.6, mode='fade', anchor='c', color=(230, 230, 230))
        draw_text(img, "Qo'llashdan oldin yo'riqnomani o'qing.", 600, 30, CX, 1856, t, 66.7, mode='fade', anchor='c', color=(230, 230, 230))
    arr = canvas_from(img)
    fade = 1 - ease_io(prog(t, 69.2, 70.0))
    return arr * fade, dict(temp=0.2, sat=1.08)

def brand_logo():
    """AZIYA AGRO — matnli belgi (kompaniya logotipi berilsa, almashtiriladi)."""
    tw = text_img("AZIYA AGRO", 900, 96, WHITE, 3, 0.0)[2] / K
    w, h = int(tw + 260), 190
    im = Image.new('RGBA', (ki(w), ki(h)), (0, 0, 0, 0))
    bg = pill(ki(w), ki(h), (24, 110, 46), 245, radius=ki(36)); im.alpha_composite(bg)
    # barg belgisi
    S = 3; s = ki(120)
    m = Image.new('L', (s * S, s * S), 0); d = ImageDraw.Draw(m); ww = s * S
    d.ellipse((ww * 0.05, ww * 0.25, ww * 0.62, ww * 0.95), fill=255); d.ellipse((ww * 0.38, ww * 0.05, ww * 0.95, ww * 0.75), fill=255)
    d.line((ww * 0.2, ww * 0.85, ww * 0.8, ww * 0.2), fill=0, width=int(ww * 0.05))
    m = m.resize((s, s), Image.LANCZOS)
    leaf = Image.new('RGBA', (s, s), GOLD + (0,)); leaf.putalpha(m)
    im.alpha_composite(leaf, (ki(40), (ki(h) - s) // 2))
    ti, pad, tw2, th2 = text_img("AZIYA AGRO", 900, 96, WHITE, 3, 0.0)
    im.alpha_composite(ti, (ki(190) - pad, (ki(h) - th2) // 2 - pad))
    return im

# ================================================================ jadval
SHOTS = [
    (0.0, 3.0, s1, 'cut'), (3.0, 6.1, s2, 'zoom'), (6.1, 12.4, s3, 'cut'), (12.4, 16.2, s4, 'whip'),
    (16.2, 20.8, s5, 'cut'), (20.8, 25.4, s6, 'whip'), (25.4, 29.1, s7, 'fade'), (29.1, 31.3, s8, 'cut'),
    (31.3, 34.2, s9, 'flash'), (34.2, 38.45, s10, 'whip'), (38.45, 44.6, s11, 'fade'), (44.6, 51.8, s12, 'whip'),
    (51.8, 57.2, s13, 'flash'), (57.2, 61.7, s14, 'fade'), (61.7, 64.45, s15, 'flash'), (64.45, 70.0, s16, 'fade'),
]
DUR = 70.0
