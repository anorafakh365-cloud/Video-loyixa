"""Kichik 3D renderer: ellipsoidlar (uzum g'ujumi, pomidor, bodring, shaftoli),
yorug'lik (diffuz + spekulyar + Frenel + qobiq "bloom"), soyalar, molekulalar."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from core import *

LIGHT = np.array([-0.55, -0.65, 0.52], np.float32); LIGHT /= np.linalg.norm(LIGHT)
RIM = np.array([0.7, 0.2, -0.3], np.float32); RIM /= np.linalg.norm(RIM)

class Ell:
    """Ellipsoid. cx,cy,cz piksel; rx,ry,rz piksel; rot — ekrandagi burchak (rad)."""
    def __init__(s, cx, cy, cz, rx, ry, rz, color, spec=0.5, shin=40, sheen=0.0, sheen_col=(0.75, 0.75, 0.85),
                 rim=0.3, rot=0.0, tex=None, seed=0, sss=0.0, rough=0.0):
        s.__dict__.update(locals()); del s.__dict__['s']

def shade_ell(e, canvas, alpha, light=LIGHT, rim_col=(1.0, 0.95, 0.85), env=0.25, shadow=True):
    """canvas: float32 (h,w,3) 0..1, alpha: float32 (h,w). Joyida chiziladi (painter)."""
    h, w = alpha.shape
    R = max(e.rx, e.ry) * 1.02
    x0, x1 = int(max(0, e.cx - R - 2)), int(min(w, e.cx + R + 3))
    y0, y1 = int(max(0, e.cy - R - 2)), int(min(h, e.cy + R + 3))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xx - e.cx, yy - e.cy
    c, s_ = math.cos(e.rot), math.sin(e.rot)
    lx = (dx * c + dy * s_) / e.rx; ly = (-dx * s_ + dy * c) / e.ry
    r2 = lx * lx + ly * ly
    inside = r2 < 1.0
    if not inside.any(): return
    # kontakt soya (orqadagi narsalarga)
    if shadow:
        sx = (dx + e.rx * 0.18) / (e.rx * 1.05); sy = (dy - e.ry * 0.10 * 0) / (e.ry * 1.05)
        sd = np.clip(1 - (sx * sx + sy * sy), 0, 1) ** 1.5 * 0.45
        canvas[y0:y1, x0:x1] *= (1 - sd * alpha[y0:y1, x0:x1])[..., None]
    lz = np.sqrt(np.clip(1 - r2, 0, 1))
    nx, ny, nz = lx / e.rx, ly / e.ry, lz / e.rz
    if e.rough:
        nn = e.tex_noise if hasattr(e, 'tex_noise') else None
    # orqaga burish (ekran)
    nX = nx * c - ny * s_; nY = nx * s_ + ny * c; nZ = nz
    if e.rough:
        rng = np.random.default_rng(e.seed)
        bump = rng.standard_normal(nX.shape).astype(np.float32)
        bump = blur_np(bump, max(0.6, e.rx * 0.02))
        nX = nX + bump * e.rough / e.rx * 3; nY = nY + np.roll(bump, 3, 0) * e.rough / e.rx * 3
    nl = np.sqrt(nX * nX + nY * nY + nZ * nZ) + 1e-6
    nX, nY, nZ = nX / nl, nY / nl, nZ / nl
    ndl = nX * light[0] + nY * light[1] + nZ * light[2]
    wrap = 0.25 + e.sss
    diff = np.clip((ndl + wrap) / (1 + wrap), 0, 1)
    hx, hy, hz = light[0], light[1], light[2] + 1
    hn = math.sqrt(hx * hx + hy * hy + hz * hz)
    ndh = np.clip((nX * hx + nY * hy + nZ * hz) / hn, 0, 1)
    spec = ndh ** e.shin * e.spec
    fres = (1 - np.clip(nZ, 0, 1)) ** 3
    rimv = np.clip(nX * RIM[0] + nY * RIM[1] + nZ * RIM[2] + 0.35, 0, 1) ** 2 * fres * e.rim
    col = np.array(e.color, np.float32)[None, None, :] * np.ones_like(diff)[..., None]
    mask_extra = None
    if e.tex is not None:
        col, spec, mask_extra = e.tex(e, lx, ly, lz, col, spec)
    ao = 0.55 + 0.45 * np.clip(lz, 0, 1) ** 0.5
    rgb = col * (diff * 0.92 + env * 0.35)[..., None] * ao[..., None]
    if e.sheen:
        rgb += np.array(e.sheen_col, np.float32) * (fres * e.sheen)[..., None]
    rgb += (spec[..., None] * np.array([1, 0.98, 0.94], np.float32))
    rgb += rimv[..., None] * np.array(rim_col, np.float32)
    # chekka antialias
    edge = np.clip((1 - np.sqrt(r2)) * min(e.rx, e.ry) / 1.3, 0, 1)
    a = edge * inside
    if mask_extra is not None: a = a * mask_extra
    sub = canvas[y0:y1, x0:x1]
    sub[:] = sub * (1 - a[..., None]) + rgb * a[..., None]
    alpha[y0:y1, x0:x1] = alpha[y0:y1, x0:x1] * (1 - a) + a

def render(items, w, h, bg=None, light=LIGHT, rim_col=(1.0, 0.95, 0.85), env=0.25, shadow=True, pre=None):
    canvas = np.zeros((h, w, 3), np.float32) if bg is None else bg.copy()
    alpha = np.zeros((h, w), np.float32)
    if pre: pre(canvas, alpha)
    for e in sorted(items, key=lambda e: e.cz):
        if callable(e):
            e(canvas, alpha); continue
        shade_ell(e, canvas, alpha, light, rim_col, env, shadow)
    return canvas, alpha

def to_rgba(canvas, alpha):
    return rgba_from(canvas, alpha)

# ---------------------------------------------------------------- textures
def tex_grape(state):
    """state: dict(rot=0..1, crack=0..1, powder=0..1, wet=0..1)"""
    def f(e, lx, ly, lz, col, spec):
        rng = np.random.default_rng(e.seed)
        rot = state.get('rot', 0) * e.rotk
        if rot > 0:
            brown = np.array([0.30, 0.17, 0.08], np.float32)
            nz = np.sin(lx * 5 + ly * 3 + e.seed) * 0.5 + np.sin(ly * 7 - lx * 2 + e.seed * 0.3) * 0.5
            col = col * (1 - rot) + brown * rot * (0.75 + 0.25 * nz[..., None])
            spec = spec * (1 - 0.8 * rot)
        cr = state.get('crack', 0) * e.crackk
        if cr > 0:
            ph = e.seed * 1.7
            along = ly * math.cos(ph) - lx * math.sin(ph)
            across = lx * math.cos(ph) + ly * math.sin(ph) + 0.06 * np.sin(along * 13 + ph) + 0.03 * np.sin(along * 29)
            wdt = (0.015 + 0.07 * cr) * np.clip(1 - np.abs(along) / (0.15 + 0.55 * cr), 0, 1)
            m = npsmooth(wdt, wdt * 0.4, np.abs(across)) * (lz > 0.15)
            col = col * (1 - m[..., None]) + np.array([0.10, 0.02, 0.03], np.float32) * m[..., None]
            spec = spec * (1 - 0.7 * m)
        pw = state.get('powder', 0) * e.powk
        if pw > 0:
            key = ('pownoise', e.seed, lx.shape)
            n = G.get(key)
            if n is None:
                n = blur_np(np.random.default_rng(e.seed + 5).random(lx.shape).astype(np.float32), max(1.5, e.rx * 0.12))
                n = (n - n.min()) / (n.max() - n.min() + 1e-6)
                G[key] = n
            m = (npsmooth(1 - pw, 1.2 - pw * 0.8, n) * 0.55 + 0.15 * pw)[..., None]
            col = col * (1 - m) + np.array([0.80, 0.80, 0.82], np.float32) * m
            spec = spec * (1 - 0.8 * m[..., 0])
        return col, spec, None
    return f

def grape_cluster(cx, cy, size, t_rot=0.0, seed=3, color=(0.30, 0.07, 0.20), state=None, n=70, tilt=0.0, depth=0.0):
    """Uzum shingili. cx, cy, size — piksel. t_rot — vertikal o'q atrofida burilish (rad)."""
    rng = random.Random(seed)
    items = []
    R = size * 0.42
    st = state or {}
    tex = tex_grape(st)
    berries = []
    for i in range(n):
        v = rng.random() ** 0.9
        rad = R * (1 - v) ** 0.75 * (0.55 + 0.45 * rng.random()) + R * 0.08
        ang = rng.uniform(0, 2 * math.pi)
        berries.append((v, rad, ang, rng.uniform(0.85, 1.12), rng.random(), rng.random(), rng.random()))
    br0 = size * 0.085
    # shingil bandi (rachis)
    def stems(canvas, alpha):
        im = Image.new('L', (canvas.shape[1], canvas.shape[0]), 0)
        d = ImageDraw.Draw(im)
        top = (cx, cy - size * 0.55)
        d.line((top[0], top[1] - size * 0.15, cx, cy + size * 0.2), fill=255, width=max(2, int(size * 0.025)))
        m = np.asarray(im.filter(ImageFilter.GaussianBlur(1)), np.float32) / 255
        col = np.array([0.32, 0.36, 0.12], np.float32)
        canvas[:] = canvas * (1 - m[..., None]) + col * m[..., None]
        alpha[:] = np.maximum(alpha, m)
    stems.cz = -1e9
    items.append(stems)
    for j, (v, rad, ang, sc, r1, r2, r3) in enumerate(berries):
        a = ang + t_rot
        x = cx + rad * math.cos(a)
        z = rad * math.sin(a) + depth
        y = cy - size * 0.45 + v * size * 1.05 + tilt * x * 0.0
        r = br0 * sc * (1 - 0.15 * st.get('rot', 0) * (r1 > 0.4))
        c = tuple(np.clip(np.array(color) * (0.85 + 0.3 * r2), 0, 1))
        e = Ell(x, y, z, r, r * 1.12, r, c, spec=0.55, shin=60, sheen=0.35, sheen_col=(0.55, 0.52, 0.65),
                rim=0.35, rot=0.0, tex=tex, seed=seed * 1000 + j, sss=0.15)
        e.rotk = 1.0 if r1 < st.get('rot_frac', 0.7) else 0.25
        e.crackk = 1.0 if r3 < st.get('crack_frac', 0.35) else 0.0
        e.powk = 0.6 + 0.4 * r2
        items.append(e)
    return items

# ---------------------------------------------------------------- fruits
def tex_spots(spots_fn):
    """spots_fn(e) -> list of (u, v, radius, kind); u,v in [-1,1] (ekrandagi lokal)."""
    def f(e, lx, ly, lz, col, spec):
        for (u, v, r, kind, amt) in spots_fn(e):
            if amt <= 0: continue
            d = np.sqrt((lx - u) ** 2 + (ly - v) ** 2) / (r * amt + 1e-4)
            core = npsmooth(1.0, 0.75, d)
            halo = npsmooth(1.6, 1.0, d) * (1 - core)
            if kind == 'black':
                cc = np.array([0.06, 0.05, 0.03], np.float32); hc = np.array([0.35, 0.28, 0.08], np.float32)
            elif kind == 'brown':
                cc = np.array([0.28, 0.16, 0.06], np.float32); hc = np.array([0.75, 0.62, 0.15], np.float32)
            else:  # yellow oily
                cc = np.array([0.80, 0.72, 0.20], np.float32); hc = np.array([0.6, 0.65, 0.2], np.float32)
            ring = np.abs(np.sin(d * 9)) * 0.25 * core
            col = col * (1 - core[..., None]) + (cc * (0.8 + ring[..., None])) * core[..., None]
            col = col * (1 - 0.5 * halo[..., None]) + hc * 0.5 * halo[..., None]
            spec = spec * (1 - 0.8 * core)
        return col, spec, None
    return f

def tomato(cx, cy, r, seed=1, spots=None):
    items = [Ell(cx, cy, 0, r * 1.06, r * 0.92, r, (0.80, 0.10, 0.05), spec=0.9, shin=90, rim=0.4, sss=0.2, seed=seed,
                 tex=tex_spots(spots) if spots else None)]
    def calyx(canvas, alpha):
        im = Image.new('L', (canvas.shape[1], canvas.shape[0]), 0); d = ImageDraw.Draw(im)
        top = (cx, cy - r * 0.78)
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            pts = [(top[0] + math.cos(a + 0.35) * r * 0.08, top[1] + math.sin(a + 0.35) * r * 0.05),
                   (top[0] + math.cos(a) * r * 0.42, top[1] + math.sin(a) * r * 0.16 + r * 0.05),
                   (top[0] + math.cos(a - 0.35) * r * 0.08, top[1] + math.sin(a - 0.35) * r * 0.05)]
            d.polygon(pts, fill=255)
        d.line((top[0], top[1], top[0] + r * 0.05, top[1] - r * 0.22), fill=255, width=max(2, int(r * 0.07)))
        m = np.asarray(im.filter(ImageFilter.GaussianBlur(max(1, r * 0.01))), np.float32) / 255
        canvas[:] = canvas * (1 - m[..., None]) + np.array([0.18, 0.40, 0.10], np.float32) * m[..., None]
        alpha[:] = np.maximum(alpha, m)
    calyx.cz = 1e9
    return items + [calyx]

def cucumber(cx, cy, r, seed=2, rot=0.5, spots=None):
    def tex(e, lx, ly, lz, col, spec):
        stripe = 0.5 + 0.5 * np.sin(ly * 3 + np.sin(lx * 2))
        col = col * (0.75 + 0.35 * stripe[..., None])
        rng = np.random.default_rng(seed)
        if spots:
            col, spec, _ = tex_spots(spots)(e, lx, ly, lz, col, spec)
        return col, spec, None
    return [Ell(cx, cy, 0, r * 2.6, r * 0.62, r * 0.62, (0.10, 0.30, 0.08), spec=0.5, shin=50, rim=0.35, rot=rot,
                rough=1.2, seed=seed, tex=tex)]

def peach(cx, cy, r, seed=3, spots=None):
    def tex(e, lx, ly, lz, col, spec):
        g = np.clip(0.5 + 0.6 * (lx * 0.7 - ly * 0.7), 0, 1)[..., None]
        base = np.array([0.95, 0.62, 0.18], np.float32) * (1 - g) + np.array([0.82, 0.18, 0.12], np.float32) * g
        crease = np.exp(-((lx + 0.12 * ly ** 2) / 0.05) ** 2) * (ly < 0.4)
        base = base * (1 - 0.35 * crease[..., None])
        if spots:
            base, spec, _ = tex_spots(spots)(e, lx, ly, lz, base, spec)
        return base, spec, None
    return [Ell(cx, cy, 0, r, r * 0.98, r, (1, 1, 1), spec=0.15, shin=12, sheen=0.45, sheen_col=(1.0, 0.8, 0.7), rim=0.5,
                sss=0.3, seed=seed, tex=tex)]

# ---------------------------------------------------------------- molecules
def _ring(cx, cy, n, r, start=0.0):
    return [(cx + r * math.cos(start + 2 * math.pi * i / n), cy + r * math.sin(start + 2 * math.pi * i / n)) for i in range(n)]

def azoxystrobin():
    """Azoksistrobin (C22H17N3O5) — sxematik 3D tuzilishi."""
    atoms, bonds = [], []
    def add(x, y, z, el):
        atoms.append((x, y, z, el)); return len(atoms) - 1
    def ring(cx, cy, z, n, r, els, st=0.0):
        ids = [add(x, y, z + 0.15 * math.sin(i * 2.1), el) for i, ((x, y), el) in enumerate(zip(_ring(cx, cy, n, r, st), els))]
        for i in range(n): bonds.append((ids[i], ids[(i + 1) % n]))
        return ids
    A_ = ring(-2.6, 0.6, 0.2, 6, 0.7, 'CCCCCC', 0.5)
    cn = add(-3.3, 1.9, 0.4, 'C'); n1 = add(-3.8, 2.8, 0.5, 'N'); bonds += [(A_[1], cn), (cn, n1)]
    o1 = add(-1.5, 1.2, 0.0, 'O'); bonds.append((A_[0], o1))
    B = ring(-0.3, 0.6, -0.2, 6, 0.7, 'CNCNCC', 0.5); bonds.append((o1, B[2]))
    o2 = add(0.9, 1.3, -0.1, 'O'); bonds.append((B[0], o2))
    C = ring(2.1, 0.6, 0.3, 6, 0.7, 'CCCCCC', 0.5); bonds.append((o2, C[2]))
    c1 = add(2.6, -0.8, 0.6, 'C'); bonds.append((C[4], c1))
    c2 = add(1.9, -1.8, 0.9, 'C'); bonds.append((c1, c2))
    o3 = add(2.3, -3.0, 1.1, 'O'); bonds.append((c2, o3)); c3 = add(1.4, -3.8, 1.3, 'C'); bonds.append((o3, c3))
    c4 = add(3.9, -1.0, 0.2, 'C'); bonds.append((c1, c4))
    o4 = add(4.6, -0.1, 0.0, 'O'); o5 = add(4.4, -2.1, 0.1, 'O'); bonds += [(c4, o4), (c4, o5)]
    c5 = add(5.7, -2.3, -0.1, 'C'); bonds.append((o5, c5))
    return atoms, bonds

def difenoconazole():
    """Difenokonazol (C19H17Cl2N3O3) — sxematik 3D tuzilishi."""
    atoms, bonds = [], []
    def add(x, y, z, el):
        atoms.append((x, y, z, el)); return len(atoms) - 1
    def ring(cx, cy, z, n, r, els, st=0.0):
        ids = [add(x, y, z + 0.15 * math.sin(i * 2.1), el) for i, ((x, y), el) in enumerate(zip(_ring(cx, cy, n, r, st), els))]
        for i in range(n): bonds.append((ids[i], ids[(i + 1) % n]))
        return ids
    T = ring(-3.4, -1.2, 0.3, 5, 0.6, 'NNCNC', 0.3)
    ch2 = add(-2.2, -0.6, 0.0, 'C'); bonds.append((T[0], ch2))
    D = ring(-1.0, -1.1, -0.3, 5, 0.6, 'COCCO', 1.0); bonds.append((ch2, D[0]))
    me = add(-0.6, -2.5, -0.6, 'C'); bonds.append((D[3], me))
    P1 = ring(0.4, 0.2, 0.2, 6, 0.7, 'CCCCCC', 0.0); bonds.append((D[0], P1[3]))
    cl1 = add(0.0, 1.6, 0.5, 'Cl'); bonds.append((P1[2], cl1))
    o = add(1.8, -0.4, 0.0, 'O'); bonds.append((P1[5], o))
    P2 = ring(3.1, 0.2, -0.2, 6, 0.7, 'CCCCCC', 0.0); bonds.append((o, P2[3]))
    cl2 = add(4.5, 0.6, -0.4, 'Cl'); bonds.append((P2[0], cl2))
    return atoms, bonds

EL = {'C': ((0.30, 0.32, 0.34), 0.42), 'N': ((0.20, 0.35, 0.95), 0.40), 'O': ((0.92, 0.15, 0.12), 0.40),
      'Cl': ((0.25, 0.85, 0.25), 0.50), 'H': ((0.9, 0.9, 0.9), 0.25)}

def molecule_items(mol, cx, cy, scale, ax, ay, az=0.0, glow=None):
    atoms, bonds = mol
    P = np.array([[a[0], a[1], a[2]] for a in atoms], np.float32)
    P -= P.mean(0)
    def rot(P, ax, ay, az):
        ca, sa = math.cos(ax), math.sin(ax); cb, sb = math.cos(ay), math.sin(ay); cc, sc = math.cos(az), math.sin(az)
        Rx = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]]); Ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
        Rz = np.array([[cc, -sc, 0], [sc, cc, 0], [0, 0, 1]])
        return P @ (Rz @ Ry @ Rx).T
    Q = rot(P, ax, ay, az)
    persp = 1 / (1 - Q[:, 2] * 0.06)
    X = cx + Q[:, 0] * scale * persp; Y = cy + Q[:, 1] * scale * persp; Z = Q[:, 2] * scale
    items = []
    for i, (x, y, z, el) in enumerate(atoms):
        col, rr = EL[el]
        r = rr * scale * 0.95 * persp[i]
        items.append(Ell(X[i], Y[i], Z[i], r, r, r, col, spec=0.8, shin=70, rim=0.5, sss=0.1, seed=i))
    for (a, b) in bonds:
        za = (Z[a] + Z[b]) / 2
        def bond(canvas, alpha, a=a, b=b):
            im = Image.new('L', (canvas.shape[1], canvas.shape[0]), 0); d = ImageDraw.Draw(im)
            wdt = max(2, int(scale * 0.16))
            d.line((X[a], Y[a], X[b], Y[b]), fill=255, width=wdt)
            hl = Image.new('L', im.size, 0); ImageDraw.Draw(hl).line((X[a] - wdt * 0.2, Y[a] - wdt * 0.25, X[b] - wdt * 0.2, Y[b] - wdt * 0.25), fill=255, width=max(1, wdt // 3))
            m = np.asarray(im, np.float32) / 255; h = np.asarray(hl.filter(ImageFilter.GaussianBlur(max(1, wdt * 0.2))), np.float32) / 255
            col = np.array([0.62, 0.66, 0.70], np.float32)
            canvas[:] = canvas * (1 - m[..., None]) + (col * 0.55 + h[..., None] * 0.6) * m[..., None]
            alpha[:] = np.maximum(alpha, m)
        bond.cz = za - scale * 0.3
        items.append(bond)
    return items
