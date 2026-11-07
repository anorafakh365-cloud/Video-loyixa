"""Umumiy yordamchilar: o'lcham, easing, kompozitsiya, matn, post-ishlov."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def A(*p): return os.path.join(ROOT, 'assets', *p)
OUT = os.path.join(ROOT, 'out')

K = float(os.environ.get('K', '2'))     # 2 -> 2160x3840
LW, LH = 1080, 1920
W, H = int(LW * K), int(LH * K)
FPS = 25
CX, CY = LW / 2, LH / 2

def k(v): return v * K
def ki(v): return int(round(v * K))

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def sstep(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x ** 3
def ease_io(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def ease_expo(x): x = clamp(x); return 1 if x >= 1 else 1 - 2 ** (-10 * x)
def ease_back(x, s=1.70158):
    x = clamp(x); c3 = s + 1
    return 1 + c3 * (x - 1) ** 3 + s * (x - 1) ** 2
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def lerp(a, b, x): return a + (b - a) * x

def npsmooth(e0, e1, x):
    x = np.clip((x - e0) / (e1 - e0), 0, 1); return x * x * (3 - 2 * x)

# ---------------------------------------------------------------- cache
G = {}
def cached(key, fn):
    if key not in G: G[key] = fn()
    return G[key]

# ---------------------------------------------------------------- arrays
def np2im(a, mode=None):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), mode) if mode else Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def rgba_from(rgb01, a01):
    return Image.fromarray(np.dstack([np.clip(rgb01, 0, 1) * 255, np.clip(a01, 0, 1) * 255]).astype(np.uint8), 'RGBA')

def vgrad(h, w, stops):
    ys = np.linspace(0, 1, h); out = np.zeros((h, 3), np.float32)
    ps = [s[0] for s in stops]
    for c in range(3): out[:, c] = np.interp(ys, ps, [s[1][c] for s in stops])
    return np.repeat(out[:, None, :], w, axis=1)

def radial(w, h, cx, cy, r, color, power=2.0):
    yy, xx = np.ogrid[0:h, 0:w]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2).astype(np.float32) / r
    g = np.clip(1 - d, 0, 1) ** power
    return g[..., None] * np.array(color, np.float32)[None, None, :]

def fbm(w, h, octaves=5, seed=0, base=4, persist=0.5):
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    m = max(w, h)
    for o in range(octaves):
        n = base * 2 ** o
        small = rng.random((int(n * h / m) + 3, int(n * w / m) + 3)).astype(np.float32)
        im = Image.fromarray(small, 'F').resize((w, h), Image.BICUBIC)
        acc += amp * np.asarray(im, np.float32); tot += amp; amp *= persist
    return acc / tot

def blur_np(a, r):
    """Tez gauss xiralashtirish (float massiv, 2D yoki 3D)."""
    if r <= 0.3: return a
    from scipy.ndimage import gaussian_filter
    if a.ndim == 2: return gaussian_filter(a.astype(np.float32), r, mode='nearest')
    return gaussian_filter(a.astype(np.float32), (r, r, 0), mode='nearest')

def fast_blur_img(im, r):
    """Katta radiusli blur: kichraytirib-kattalashtirish orqali."""
    if r < 6: return im.filter(ImageFilter.GaussianBlur(r))
    f = max(1, int(r / 4))
    small = im.resize((max(1, im.width // f), max(1, im.height // f)), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(r / f))
    return small.resize(im.size, Image.BILINEAR)

# ---------------------------------------------------------------- compositing
def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a))); return im

def paste(base, layer, xy, alpha=1.0):
    if alpha <= 0.002 or layer is None: return
    layer = with_alpha(layer, alpha)
    x, y = int(round(xy[0])), int(round(xy[1]))
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(layer.width, base.width - x), min(layer.height, base.height - y)
    if ex <= sx or ey <= sy: return
    if sx or sy or ex < layer.width or ey < layer.height:
        layer = layer.crop((sx, sy, ex, ey))
    base.alpha_composite(layer, (x + sx, y + sy))

def place(base, layer, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    """cx, cy — mantiqiy koordinata (markaz)."""
    if alpha <= 0.002: return
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.BICUBIC)
    if rot: layer = layer.rotate(rot, resample=Image.BICUBIC, expand=True)
    paste(base, layer, (k(cx) - layer.width / 2, k(cy) - layer.height / 2), alpha)

def shadow_of(layer, blur, opacity=0.6, color=(0, 0, 0)):
    a = layer.getchannel('A')
    a = fast_blur_img(a, blur).point(lambda v: int(v * opacity))
    s = Image.new('RGBA', layer.size, color + (0,)); s.putalpha(a); return s

def view(src, cx, cy, zoom, out_size=None, angle=0.0):
    """src rasmidan kamera ko'rinishi: (cx, cy) — src piksellarida markaz, zoom — 1 = src kengligi kadrga teng."""
    ow, oh = out_size or (W, H)
    cw = src.width / zoom; ch = cw * oh / ow
    if angle:
        big = src.rotate(angle, resample=Image.BICUBIC, center=(cx, cy))
        src = big
    if cw > src.width: cw = src.width; ch = cw * oh / ow
    if ch > src.height: ch = src.height; cw = ch * ow / oh
    cx = min(max(cx, cw / 2), src.width - cw / 2); cy = min(max(cy, ch / 2), src.height - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return src.resize((ow, oh), Image.BICUBIC, box=box)

# ---------------------------------------------------------------- text
def font(wt, px): return ImageFont.truetype(A('fonts', f'Montserrat-{wt}.ttf'), px)

def text_img(txt, wt, size, color=(255, 255, 255), track=0, shadow=0.75, glow=None, stroke=0):
    key = ('txt', txt, wt, size, color, track, shadow, glow, stroke)
    if key in G: return G[key]
    px = ki(size); f = font(wt, px); tr = k(track)
    widths = [f.getlength(ch) + tr for ch in txt]
    tw = int(sum(widths) - tr) if txt else 1
    asc, desc = f.getmetrics()
    pad = ki(40) + ki(stroke)
    im = Image.new('RGBA', (tw + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    m = Image.new('L', im.size, 0); d = ImageDraw.Draw(m)
    x = pad
    for ch, wd in zip(txt, widths):
        d.text((x, pad), ch, font=f, fill=255, stroke_width=ki(stroke), stroke_fill=255); x += wd
    if shadow:
        sh = ImageChops.offset(m.filter(ImageFilter.GaussianBlur(px * 0.07)), 0, int(px * 0.05))
        sl = Image.new('RGBA', im.size, (0, 0, 0, 0)); sl.putalpha(sh.point(lambda v: int(v * shadow)))
        im.alpha_composite(sl)
    if glow:
        gl = m.filter(ImageFilter.GaussianBlur(px * 0.3))
        gi = Image.new('RGBA', im.size, glow + (0,)); gi.putalpha(gl.point(lambda v: min(255, int(v * 1.1))))
        im.alpha_composite(gi)
    fill = Image.new('RGBA', im.size, color + (0,)); fill.putalpha(m)
    im.alpha_composite(fill)
    G[key] = (im, pad, tw, asc + desc)
    return G[key]

def text_w(txt, wt, size, track=0):
    return text_img(txt, wt, size, track=track)[2] / K

def draw_text(base, txt, wt, size, x, y, t, t_in, color=(255, 255, 255), anchor='l', dur=0.5, t_out=None,
              mode='rise', track=0, glow=None, shadow=0.75, alpha=1.0, scale=1.0):
    """Kinetik matn. mode: rise | mask (pastdan kesib chiqadi) | slam (kattadan tushadi) | fade | type."""
    p = prog(t, t_in, t_in + dur)
    if p <= 0: return
    out = 1.0
    if t_out is not None: out = 1 - ease_io(prog(t, t_out, t_out + 0.35))
    if out <= 0: return
    im, pad, tw, th = text_img(txt, wt, size, color, track, shadow, glow)
    px = k(x)
    if anchor == 'c': px -= tw / 2
    elif anchor == 'r': px -= tw
    py = k(y)
    if mode == 'rise':
        a = ease_out(p); paste(base, im, (px - pad, py - pad + k(30) * (1 - a)), a * out * alpha)
    elif mode == 'fade':
        paste(base, im, (px - pad, py - pad), ease_io(p) * out * alpha)
    elif mode == 'mask':
        a = ease_expo(p)
        off = int((1 - a) * (th + ki(10)))
        crop = im.crop((0, 0, im.width, pad + th + ki(6)))
        layer = Image.new('RGBA', crop.size, (0, 0, 0, 0))
        layer.alpha_composite(crop, (0, off))
        paste(base, layer, (px - pad, py - pad), out * alpha)
    elif mode == 'slam':
        a = ease_out(p); s = (1.6 - 0.6 * a) * scale
        im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
        cxp = px + tw / 2; cyp = py + th / 2
        paste(base, im2, (cxp - im2.width / 2, cyp - im2.height / 2), clamp(p * 3) * out * alpha)
    elif mode == 'type':
        n = int(len(txt) * clamp(p * 1.0001))
        if n <= 0: return
        sub = text_img(txt[:n], wt, size, color, track, shadow, glow)
        paste(base, sub[0], (px - pad, py - pad), out * alpha)

def pill(w, h, color, alpha=255, radius=None):
    key = ('pill', w, h, color, alpha, radius)
    if key in G: return G[key]
    S = 3; r = radius if radius is not None else h // 2
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * S - 1, h * S - 1), r * S, fill=color + (alpha,))
    G[key] = im.resize((w, h), Image.LANCZOS)
    return G[key]

def bar_sweep(base, x, y, w, h, t, t_in, color, dur=0.35, anchor='l', alpha=1.0):
    """Matn ortidagi rangli plashka chapdan o'ngga yoyiladi (mantiqiy)."""
    p = ease_expo(prog(t, t_in, t_in + dur))
    if p <= 0: return
    ww = max(1, ki(w * p))
    b = pill(ww, ki(h), color, 255, radius=ki(8))
    px = k(x) if anchor == 'l' else k(x) - ki(w) / 2
    paste(base, b, (px, k(y)), alpha)

# ---------------------------------------------------------------- post
def bloom(rgb, thresh=200, strength=0.35, radius=40):
    """rgb: float32 (H,W,3) 0..255"""
    lum = rgb.max(axis=2)
    m = np.clip((lum - thresh) / (255 - thresh), 0, 1)[..., None]
    br = (rgb * m).astype(np.float32)
    f = 8
    small = Image.fromarray(np.clip(br, 0, 255).astype(np.uint8)).resize((W // f, H // f), Image.BILINEAR)
    b1 = np.asarray(small.filter(ImageFilter.GaussianBlur(radius * K / f)), np.float32)
    b2 = np.asarray(small.filter(ImageFilter.GaussianBlur(radius * K / f * 3)), np.float32)
    up = np.asarray(Image.fromarray(np.clip(b1 * 0.6 + b2 * 0.6, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
    return rgb + up * strength

def vignette_mask(strength=0.55):
    key = ('vig', strength)
    if key not in G:
        yy, xx = np.ogrid[0:H, 0:W]
        d = np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.60)) ** 2).astype(np.float32)
        G[key] = np.clip(1 - strength * np.clip(d - 0.45, 0, 1) ** 1.6, 0, 1)[..., None]
    return G[key]

def grain(i, amt=7):
    if 'grain' not in G:
        rng = np.random.default_rng(7)
        G['grain'] = [(rng.standard_normal((H // 2, W // 2)).astype(np.float32)) for _ in range(5)]
    g = G['grain'][i % 5]
    g = np.asarray(Image.fromarray(g, 'F').resize((W, H), Image.BILINEAR), np.float32)
    return g * amt

def grade(rgb, lift=(0, 0, 0), gain=(1, 1, 1), sat=1.0, contrast=1.0, temp=0.0):
    """Oddiy rang korreksiyasi. temp>0 iliq, <0 sovuq."""
    if sat != 1.0:
        l = (rgb * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
        rgb = l + (rgb - l) * sat
    if temp:
        rgb = rgb * np.array([1 + 0.08 * temp, 1 + 0.01 * temp, 1 - 0.10 * temp], np.float32)
    rgb = rgb * np.array(gain, np.float32) + np.array(lift, np.float32)
    if contrast != 1.0:
        rgb = (rgb - 118) * contrast + 118
    return rgb

def chroma_ab(rgb, amt=1.5):
    """Kadr chetlarida yengil xromatik aberratsiya."""
    if amt <= 0: return rgb
    s = int(round(amt * K))
    if s < 1: return rgb
    out = rgb.copy()
    out[..., 0] = np.roll(rgb[..., 0], s, axis=1)
    out[..., 2] = np.roll(rgb[..., 2], -s, axis=1)
    # faqat chetlarda
    m = 1 - vignette_mask(1.0)
    return rgb * (1 - m) + out * m

def dir_blur(im, dx, dy, n=9):
    """Yo'nalishli harakat xiralanishi (whip-pan uchun)."""
    arr = np.asarray(im, np.float32); acc = np.zeros_like(arr)
    for i in range(n):
        f = (i / (n - 1) - 0.5)
        acc += np.roll(arr, (int(dy * f), int(dx * f)), axis=(0, 1))
    return np2im(acc / n)
