"""Protsedural teksturalar: makro uzum bargi (tomirlar to'ri, relyef, yorug'lik),
oq g'ubor (oidium), mildyu dog'lari, quruq nekroz, gifalar, osmondan uzumzor."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter, distance_transform_edt
from core import *

def worley(w, h, n, seed):
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 2)) * [w, h]
    tree = cKDTree(pts)
    yy, xx = np.mgrid[0:h, 0:w]
    q = np.stack([xx.ravel(), yy.ravel()], 1).astype(np.float32)
    d, idx = tree.query(q, k=2, workers=-1)
    f1 = d[:, 0].reshape(h, w).astype(np.float32); f2 = d[:, 1].reshape(h, w).astype(np.float32)
    return f1, f2, idx[:, 0].reshape(h, w)

def leaf_shape(S):
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    cx, cy = S * 0.5, S * 0.60
    dx, dy = xx - cx, yy - cy
    th = np.arctan2(dx, -dy); rr = np.hypot(dx, dy)
    # 5 bo'lakli uzum bargi
    lob = np.zeros_like(th)
    for ang, amp, wd in [(0, 1.0, 0.42), (1.05, 0.88, 0.40), (-1.05, 0.88, 0.40), (2.05, 0.62, 0.38), (-2.05, 0.62, 0.38)]:
        dth = np.angle(np.exp(1j * (th - ang)))
        lob = np.maximum(lob, amp * np.exp(-(dth / wd) ** 2))
    base = 0.50 + 0.42 * lob
    sinus = np.exp(-((np.abs(th) - math.pi) / 0.35) ** 2) * 0.45
    ser = 1 + 0.028 * np.sin(th * 38) + 0.018 * np.sin(th * 71 + 1.3)
    R = S * 0.46 * (base - sinus) * ser
    inside = np.clip((R - rr) / 2.0, 0, 1)
    return inside, (cx, cy), th, rr, R

def make_leaf(S, seed=1):
    """Qaytaradi: dict(albedo(h,w,3), height(h,w), alpha(h,w), veins(h,w), cellid, f1)."""
    inside, (cx, cy), th, rr, R = leaf_shape(S)
    # tomirlar: asosiy + ikkilamchi (chiziqlar), uchlamchi (Worley to'r)
    vm = Image.new('L', (S, S), 0); d = ImageDraw.Draw(vm)
    sc = S / 1000
    rng = random.Random(seed)
    prim = []
    for ang, ln in [(0, 0.44), (1.05, 0.40), (-1.05, 0.40), (2.05, 0.29), (-2.05, 0.29)]:
        pts = []
        for i in range(21):
            f = i / 20
            a2 = ang + 0.05 * math.sin(f * 5 + ang)
            pts.append((cx + math.sin(a2) * S * ln * f, cy - math.cos(a2) * S * ln * f))
        d.line(pts, fill=255, width=max(2, int(11 * sc)))
        prim.append(pts)
        for kk in range(2, 19, 2):
            px, py = pts[kk]
            for sgn in (-1, 1):
                a3 = ang + sgn * (0.72 + rng.uniform(-0.1, 0.1)); l2 = S * 0.13 * (1 - kk / 22)
                q = [(px, py)]
                for j in range(1, 7):
                    f = j / 6
                    q.append((px + math.sin(a3 - sgn * 0.25 * f) * l2 * f, py - math.cos(a3 - sgn * 0.25 * f) * l2 * f))
                d.line(q, fill=190, width=max(2, int(5 * sc)))
    vm = vm.filter(ImageFilter.GaussianBlur(1.3 * sc))
    v12 = np.asarray(vm, np.float32) / 255
    f1, f2, cid = worley(S, S, int(5200 * (S / 1000) ** 0 ), seed)
    cellsz = S / math.sqrt(5200)
    v3 = np.clip(1 - (f2 - f1) / (cellsz * 0.09), 0, 1) ** 1.5
    fine1, fine2, _ = worley(S, S, 26000, seed + 1)
    v4 = np.clip(1 - (fine2 - fine1) / (S / math.sqrt(26000) * 0.12), 0, 1) ** 2
    veins = np.clip(v12 + v3 * 0.28 + v4 * 0.10, 0, 1)
    # balandlik: hujayralar ichi biroz bo'rtgan, tomirlar botiq
    dome = np.clip(f1 / cellsz, 0, 1)
    height = (1 - dome) * 0.10 - v12 * 1.0 - v3 * 0.30 - v4 * 0.06
    n1 = fbm(S, S, 6, seed=seed + 10, base=4)
    height += (n1 - 0.5) * 2.2
    height = gaussian_filter(height, 1.6 * sc)
    # rang
    n2 = fbm(S, S, 5, seed=seed + 20, base=3)
    edge = np.clip(rr / np.maximum(R, 1), 0, 1)
    g0 = np.array([0.10, 0.27, 0.05], np.float32); g1 = np.array([0.24, 0.45, 0.09], np.float32)
    alb = g0 + (g1 - g0) * n2[..., None]
    alb = alb * (1 - 0.2 * edge[..., None] ** 4) + np.array([0.1, 0.08, -0.02]) * edge[..., None] ** 6
    alb = alb * (1 - 0.15 * veins[..., None]) + np.array([0.55, 0.68, 0.32], np.float32) * (v12 * 0.55)[..., None]
    # band
    stem = ((np.abs(xx_(S) - cx) < 8 * sc) & (yy_(S) > cy) & (yy_(S) < cy + S * 0.36)).astype(np.float32)
    stem = gaussian_filter(stem, 1.5 * sc)
    alpha = np.maximum(inside, stem)
    alb = alb * (1 - stem[..., None]) + np.array([0.42, 0.50, 0.18]) * stem[..., None]
    return dict(albedo=alb.astype(np.float32), height=height.astype(np.float32), alpha=alpha.astype(np.float32),
                veins=veins.astype(np.float32), v12=v12, cid=cid, f1=f1, cellsz=cellsz, center=(cx, cy), S=S, edge=edge)

def xx_(S): return np.arange(S, dtype=np.float32)[None, :].repeat(S, 0)
def yy_(S): return np.arange(S, dtype=np.float32)[:, None].repeat(S, 1)

def normals(height, strength=4.0):
    gy, gx = np.gradient(height)
    nx, ny, nz = -gx * strength, -gy * strength, np.ones_like(height)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    return nx / l, ny / l, nz / l

def light_leaf(albedo, height, alpha, veins, light=(-0.5, -0.6, 0.62), back=0.6, spec=0.22, strength=2.5, sun_col=(1.0, 0.95, 0.82)):
    """Barg yuzasini yoritish. back — orqadan nur (translyutsentlik)."""
    nx, ny, nz = normals(height, strength)
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    Hh = L + np.array([0, 0, 1]); Hh /= np.linalg.norm(Hh)
    ndh = np.clip(nx * Hh[0] + ny * Hh[1] + nz * Hh[2], 0, 1)
    sp = ndh ** 60 * spec + ndh ** 8 * spec * 0.15
    trans = back * (1 - veins * 0.8)  # tomirlar orasidan nur o'tadi
    tcol = np.array([0.55, 0.85, 0.15], np.float32)
    rgb = albedo * (0.25 + 0.85 * ndl)[..., None] * np.array(sun_col, np.float32) + (albedo * 0.6 + tcol * 0.4) * trans[..., None] * 0.9
    rgb += sp[..., None] * np.array([0.95, 1.0, 0.9], np.float32)
    return rgb

# ---------------------------------------------------------------- kasallik qatlamlari
def powder_layer(leaf, cover, seed=7, tm=0.0):
    """Oq g'ubor: cover 0..1 — qoplanish darajasi. Qaytaradi (rang, alfa, balandlik qo'shimchasi)."""
    S = leaf['S']
    key = ('powder_src', S, seed)
    if key not in G:
        low = fbm(S, S, 4, seed=seed, base=3)
        rng = np.random.default_rng(seed)
        fib = gaussian_filter(rng.random((S, S)).astype(np.float32), 1.2 * S / 1000) * 0.6 + fbm(S, S, 3, seed=seed + 9, base=60) * 0.4
        fib = (fib - fib.min()) / (fib.max() - fib.min())
        mid = fbm(S, S, 5, seed=seed + 3, base=14)
        # boshlang'ich o'choqlar
        ys, xs = np.mgrid[0:S, 0:S]
        seeds = [(0.42, 0.38), (0.62, 0.55), (0.35, 0.62), (0.55, 0.30), (0.70, 0.40)]
        dist = np.ones((S, S), np.float32) * 9
        for (u, v) in seeds:
            dist = np.minimum(dist, np.hypot(xs / S - u, ys / S - v).astype(np.float32))
        G[key] = (low, fib, mid, dist)
    low, fib, mid, dist = G[key]
    field = dist * 3.5 - low * 0.9 - mid * 0.3
    thr = -0.55 + cover * 2.3
    m = npsmooth(thr, thr - 0.12, field)
    m = m * (0.45 + 0.5 * npsmooth(0.35, 0.7, fib)) * leaf['alpha']
    m = np.clip(m * (1.0 - 0.35 * leaf['v12']), 0, 1)
    col = np.array([0.97, 0.97, 0.95], np.float32)
    return col, m, m * 1.5

def mildew_layer(leaf, amt, seed=11):
    """Mildyu: tomirlar bilan chegaralangan sarg'ish moyli dog'lar."""
    S = leaf['S']
    key = ('mild_src', S, seed)
    if key not in G:
        rng = np.random.default_rng(seed)
        cid = leaf['cid']; ncell = int(cid.max()) + 1
        # yaqin hujayralar guruhlari
        cells = np.zeros(ncell, np.float32)
        centers = [(0.38, 0.32), (0.63, 0.42), (0.45, 0.66), (0.70, 0.62), (0.28, 0.50), (0.55, 0.22)]
        ys, xs = np.mgrid[0:S, 0:S]
        d = np.ones((S, S), np.float32) * 9
        for (u, v) in centers:
            d = np.minimum(d, np.hypot(xs / S - u, ys / S - v).astype(np.float32) / rng.uniform(0.8, 1.2))
        # hujayra bo'yicha o'rtacha masofa
        sums = np.bincount(cid.ravel(), d.ravel(), ncell); cnt = np.bincount(cid.ravel(), None, ncell) + 1e-6
        cd = (sums / cnt)[cid] + fbm(S, S, 3, seed=seed, base=6) * 0.05
        G[key] = cd.astype(np.float32)
    cd = G[key]
    thr = 0.02 + amt * 0.16
    m = npsmooth(thr, thr - 0.03, cd) * leaf['alpha'] * (1 - 0.6 * leaf['v12'])
    core = npsmooth(thr - 0.06, thr - 0.12, cd) * m
    col_oil = np.array([0.74, 0.70, 0.24], np.float32)
    col_core = np.array([0.55, 0.40, 0.12], np.float32)
    return col_oil, col_core, m, core

def necrosis_layer(leaf, amt, seed=13):
    """Barg chetidan quriydi (jigarrang)."""
    edge = leaf['edge']
    n = cached(('necn', leaf['S']), lambda: fbm(leaf['S'], leaf['S'], 5, seed=seed, base=5))
    field = edge + (n - 0.5) * 0.45
    thr = 1.0 - amt * 0.95
    m = npsmooth(thr, thr + 0.08, field) * leaf['alpha']
    return np.array([0.36, 0.22, 0.08], np.float32), m

def compose_leaf(leaf, powder=0.0, mildew=0.0, necro=0.0, heal=0.0, light=(-0.5, -0.6, 0.62), back=0.55, sat=1.0):
    alb = leaf['albedo'].copy(); hgt = leaf['height'].copy()
    if necro > 0:
        nc, nm = necrosis_layer(leaf, necro)
        alb = alb * (1 - nm[..., None]) + nc * nm[..., None] * (0.8 + 0.4 * leaf['veins'][..., None])
        hgt = hgt + nm * fbm(leaf['S'], leaf['S'], 3, seed=99, base=20) * 2 if False else hgt
    if mildew > 0:
        oc, cc, m, core = mildew_layer(leaf, mildew)
        alb = alb * (1 - m[..., None] * 0.6) + oc * (m * 0.6)[..., None]
        alb = alb * (1 - core[..., None] * 0.7) + cc * (core * 0.7)[..., None]
    if heal > 0:
        alb = alb * (1 + 0.25 * heal)
    rgb = light_leaf(alb, hgt, leaf['alpha'], leaf['veins'], light, back * (1 - 0.6 * necro))
    if powder > 0:
        pc, pm, ph = powder_layer(leaf, powder)
        nx, ny, nz = normals(hgt + ph * 3, 4)
        L = np.array(light, np.float32); L /= np.linalg.norm(L)
        sh = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
        prgb = pc * (0.62 + 0.45 * sh)[..., None]
        rgb = rgb * (1 - pm[..., None]) + prgb * pm[..., None]
    if mildew > 0:
        # moyli yaltirash
        rgb += (m * 0.10)[..., None] * np.array([1, 0.9, 0.5], np.float32)
    if sat != 1.0:
        l = rgb.mean(2, keepdims=True); rgb = l + (rgb - l) * sat
    return rgb, leaf['alpha']

# ---------------------------------------------------------------- gifalar (makro)
def hyphae_layer(w, h, seed, n=60, color=(0.95, 0.97, 0.95), spores=True, thick=1.0):
    """Zamburug' gifalari va konidiyalar zanjiri (RGBA)."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    col = tuple(int(c * 255) for c in color)
    for i in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h); a = rng.uniform(0, 2 * math.pi)
        pts = [(x, y)]
        L = rng.randint(30, 90)
        for j in range(L):
            a += rng.uniform(-0.25, 0.25); x += math.cos(a) * w * 0.006; y += math.sin(a) * w * 0.006
            pts.append((x, y))
            if spores and rng.random() < 0.035:
                # konidiyalar zanjiri — yuqoriga tik
                ca = a + rng.choice([-1, 1]) * math.pi / 2; cx, cy = x, y
                ns = rng.randint(4, 8); sr = w * 0.0042 * thick
                for s in range(ns):
                    cx += math.cos(ca) * sr * 2.1; cy += math.sin(ca) * sr * 2.1
                    d.ellipse((cx - sr * 1.1, cy - sr * 0.85, cx + sr * 1.1, cy + sr * 0.85), fill=col + (200,), outline=col + (255,))
        d.line(pts, fill=col + (170,), width=max(1, int(w * 0.0018 * thick)), joint='curve')
    return im

# ---------------------------------------------------------------- osmondan uzumzor
def aerial_vineyard(w, h, seed=4):
    """Yuqoridan qaraganda uzumzor qatorlari (diagonal), soya bilan. Qaytaradi (rgb, canopy_mask)."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = math.radians(28)
    u = xx * math.cos(ang) + yy * math.sin(ang)
    v = -xx * math.sin(ang) + yy * math.cos(ang)
    period = w / 9.0
    ph = (u % period) / period
    clump = fbm(w, h, 6, seed=seed, base=18)
    wob = fbm(w, h, 3, seed=seed + 1, base=6)
    width = 0.30 + 0.12 * (clump - 0.5) + 0.06 * (wob - 0.5)
    can = npsmooth(width, width - 0.08, np.abs(ph - 0.5))
    leaves = fbm(w, h, 6, seed=seed + 2, base=60)
    hgt = can * (0.6 + 0.8 * leaves)
    hgt = gaussian_filter(hgt, w / 1500)
    nx, ny, nz = normals(hgt, w / 180)
    L = np.array([-0.6, -0.5, 0.62]); L /= np.linalg.norm(L)
    sh = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    soil_n = fbm(w, h, 6, seed=seed + 3, base=30)
    soil = np.array([0.42, 0.33, 0.22], np.float32) * (0.75 + 0.5 * soil_n[..., None])
    soil += (fbm(w, h, 4, seed=seed + 5, base=50) > 0.62)[..., None] * np.array([-0.05, 0.08, -0.04], np.float32)
    # qator soyasi tuproqqa
    shift = int(w * 0.012)
    shadow = np.roll(np.roll(can, shift, 1), shift, 0)
    soil = soil * (1 - 0.55 * shadow[..., None])
    gcol = np.array([0.17, 0.36, 0.09], np.float32) * (0.7 + 0.6 * leaves[..., None]) + np.array([0.08, 0.1, 0.0]) * clump[..., None]
    rgb = soil * (1 - can[..., None]) + gcol * (0.35 + 0.9 * sh)[..., None] * can[..., None]
    return rgb.astype(np.float32), can.astype(np.float32)
