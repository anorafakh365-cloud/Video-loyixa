#!/usr/bin/env python3
"""TEZORA — 6 ta logotip konsepsiyasi (SVG, matn egri chiziqlarga aylantirilgan).
  python3 tezora/src/logolar.py   -> tezora/logolar/*.svg (+ preview.html)
PNG va taqdimot varag'i: node tezora/src/logolar_png.js
"""
import os, math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE); ROOT = os.path.dirname(PRJ)
OUT = os.path.join(PRJ, 'logolar'); os.makedirs(OUT, exist_ok=True)
FONTS = {w: TTFont(os.path.join(ROOT, 'assets', 'fonts', f'Montserrat-{w}.ttf')) for w in (600, 700, 800, 900)}

# ---------------------------------------------------------------- matn -> path
def glyph_info(font, ch):
    gname = font.getBestCmap().get(ord(ch))
    return gname, font['hmtx'][gname][0]

def text_width(text, w, size, track=0):
    f = FONTS[w]; s = size / f['head'].unitsPerEm
    return sum(glyph_info(f, c)[1] * s for c in text) + track * size * (len(text) - 1)

def text_path(text, w, size, x, y, anchor='start', track=0.0):
    """Matnni SVG path 'd' ga aylantiradi. y — tayanch chiziq (baseline). track — harflar orasi (em)."""
    f = FONTS[w]; gs = f.getGlyphSet(); s = size / f['head'].unitsPerEm
    tw = text_width(text, w, size, track)
    if anchor == 'middle': x -= tw / 2
    elif anchor == 'end': x -= tw
    d = []
    for c in text:
        g, adv = glyph_info(f, c)
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        d.append(pen.getCommands())
        x += adv * s + track * size
    return ' '.join(d)

def text_on_circle(text, w, size, cx, cy, r, start_deg, track=0.0):
    """Doira bo'ylab matn (yuqori yoy, soat strelkasi bo'yicha)."""
    f = FONTS[w]; gs = f.getGlyphSet(); s = size / f['head'].unitsPerEm
    d = []; ang = math.radians(start_deg)
    for c in text:
        g, adv = glyph_info(f, c); a = adv * s
        mid = ang + (a / 2) / r
        px, py = cx + r * math.sin(mid), cy - r * math.cos(mid)
        ca, sa = math.cos(mid), math.sin(mid)
        # glif: markazi (a/2, 0) -> (px,py), burilish mid
        T = (s * ca, s * sa, s * sa, -s * ca, px - (a / 2) * ca, py - (a / 2) * sa)
        pen = SVGPathPen(gs); gs[g].draw(TransformPen(pen, T)); d.append(pen.getCommands())
        ang += (a + track * size) / r
    return ' '.join(d), math.degrees(ang)

def arc_text_len(text, w, size, track, r):
    return math.degrees((text_width(text, w, size, track)) / r)

# ---------------------------------------------------------------- ranglar
NAVY = '#0B1F44'; BLUE = '#1062FF'; CYAN = '#22D3EE'; GOLD = '#E3B04B'; TURQ = '#14A6B8'; WHITE = '#FFFFFF'
def pal(dark):
    return dict(ink=WHITE if dark else NAVY, sub='#BFD3F2' if dark else '#4A5B7A', blue='#3D8BFF' if dark else BLUE)

def drop(cx, cy, r):
    """Tomchi shakli: pastki doira + uchli tepa. r — doira radiusi."""
    top = cy - r * 2.05
    k = r * 0.552
    return (f'M{cx},{top} C{cx + r * 0.35},{cy - r * 1.35} {cx + r},{cy - r * 0.75} {cx + r},{cy} '
            f'C{cx + r},{cy + k} {cx + k},{cy + r} {cx},{cy + r} C{cx - k},{cy + r} {cx - r},{cy + k} {cx - r},{cy} '
            f'C{cx - r},{cy - r * 0.75} {cx - r * 0.35},{cy - r * 1.35} {cx},{top} Z')

def sparkle(cx, cy, r, fill):
    return (f'<path d="M{cx},{cy - r} Q{cx + r * 0.12},{cy - r * 0.12} {cx + r},{cy} Q{cx + r * 0.12},{cy + r * 0.12} {cx},{cy + r} '
            f'Q{cx - r * 0.12},{cy + r * 0.12} {cx - r},{cy} Q{cx - r * 0.12},{cy - r * 0.12} {cx},{cy - r} Z" fill="{fill}"/>')

def fit(body, left, top, right, bottom, W=1600, H=1000, m=90):
    """Kompozitsiyani kanvas markaziga joylab, chetlardan m piksel bo'sh joy qoldiradi."""
    sc = min((W - 2 * m) / (right - left), (H - 2 * m) / (bottom - top), 1.0)
    tx = W / 2 - sc * (left + right) / 2; ty = H / 2 - sc * (top + bottom) / 2
    return f'<g transform="translate({tx:.1f},{ty:.1f}) scale({sc:.4f})">{body}</g>'

def svg(body, defs='', w=1600, h=1000):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<defs>{defs}</defs>{body}</svg>')

# ================================================================ 1. TOMCHI — klassik suv tomchisi + yozuv
def logo1(dark=False):
    p = pal(dark)
    defs = (f'<linearGradient id="g1" x1="0" y1="0" x2="0.4" y2="1"><stop offset="0" stop-color="{CYAN}"/>'
            f'<stop offset="1" stop-color="{BLUE}"/></linearGradient>')
    b = f'<path d="{drop(400, 560, 150)}" fill="url(#g1)"/>'
    b += f'<path d="M330,560 A75,75 0 0 0 400,635" fill="none" stroke="#fff" stroke-width="22" stroke-linecap="round" opacity=".85"/>'
    b += sparkle(505, 330, 46, CYAN) + sparkle(545, 410, 22, CYAN)
    b += f'<path d="{text_path("TEZ", 900, 230, 610, 610)}" fill="{p["ink"]}"/>'
    b += f'<path d="{text_path("ORA", 900, 230, 610 + text_width("TEZ", 900, 230), 610)}" fill="{p["blue"]}"/>'
    b += f'<path d="{text_path("GILAM YUVISH XIZMATI", 700, 52, 616, 700, track=0.32)}" fill="{p["sub"]}"/>'
    right = max(610 + text_width("TEZORA", 900, 230), 616 + text_width("GILAM YUVISH XIZMATI", 700, 52, 0.32))
    return svg(fit(b, 250, 250, right, 710), defs)

# ================================================================ 2. GILAM TO'LQINI — gilam + yuvuvchi to'lqin (emblema ustida)
def logo2(dark=False):
    p = pal(dark)
    cx = 800
    defs = (f'<linearGradient id="w2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/>'
            f'<stop offset="1" stop-color="{BLUE}"/></linearGradient>'
            f'<clipPath id="c2"><rect x="{cx - 190}" y="110" width="380" height="380" rx="70"/></clipPath>')
    b = f'<rect x="{cx - 190}" y="110" width="380" height="380" rx="70" fill="{NAVY if not dark else "#13306B"}"/>'
    g = f'<g clip-path="url(#c2)">'
    # gilam
    g += f'<rect x="{cx - 120}" y="235" width="240" height="190" rx="10" fill="#C8283C"/>'
    g += f'<rect x="{cx - 98}" y="257" width="196" height="146" rx="6" fill="none" stroke="{GOLD}" stroke-width="10"/>'
    g += f'<path d="M{cx},282 L{cx + 52},330 L{cx},378 L{cx - 52},330 Z" fill="{GOLD}"/>'
    g += f'<path d="M{cx},304 L{cx + 26},330 L{cx},356 L{cx - 26},330 Z" fill="#C8283C"/>'
    for i in range(11):
        x = cx - 110 + i * 22; g += f'<line x1="{x}" y1="427" x2="{x}" y2="452" stroke="#F1E6D2" stroke-width="7" stroke-linecap="round"/>'
    # to'lqin
    g += (f'<path d="M{cx - 200},250 C{cx - 140},190 {cx - 70},300 {cx},240 C{cx + 70},180 {cx + 140},290 {cx + 200},230 '
          f'L{cx + 200},100 L{cx - 200},100 Z" fill="url(#w2)"/>')
    g += (f'<path d="M{cx - 200},250 C{cx - 140},190 {cx - 70},300 {cx},240 C{cx + 70},180 {cx + 140},290 {cx + 200},230" '
          f'fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round"/>')
    g += '</g>'
    b += g
    for (x, y, r) in [(cx - 120, 175, 16), (cx - 70, 150, 10), (cx + 95, 160, 13), (cx + 140, 185, 8)]:
        b += f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#fff" stroke-width="5" opacity=".9"/>'
    b += f'<path d="{text_path("TEZORA", 900, 190, cx, 730, "middle", track=0.04)}" fill="{p["ink"]}"/>'
    b += f'<path d="{text_path("GILAM YUVISH XIZMATI", 700, 48, cx, 815, "middle", track=0.34)}" fill="{p["blue"]}"/>'
    return svg(b, defs)

# ================================================================ 3. MONOGRAMMA — tomchi ichida "T", premium navy + oltin
def logo3(dark=False):
    p = pal(dark)
    gold = GOLD
    b = f'<path d="{drop(400, 590, 165)}" fill="{NAVY if not dark else "#13306B"}" stroke="{gold}" stroke-width="12"/>'
    # T: ustki qism — to'lqin, oyog'i — suv oqimi
    b += f'<path d="M318,505 C350,488 372,522 400,505 C428,488 450,522 482,505 L482,545 L318,545 Z" fill="{gold}"/>'
    b += f'<path d="M384,545 L416,545 L416,655 C416,690 384,690 384,655 Z" fill="{gold}"/>'
    b += f'<circle cx="400" cy="712" r="11" fill="{gold}"/>'
    b += f'<path d="{text_path("TEZORA", 800, 200, 640, 600, track=0.14)}" fill="{p["ink"]}"/>'
    b += f'<rect x="644" y="640" width="{text_width("TEZORA", 800, 200, 0.14) - 6}" height="5" fill="{gold}"/>'
    b += f'<path d="{text_path("GILAM YUVISH XIZMATI", 600, 46, 644, 715, track=0.42)}" fill="{p["sub"]}"/>'
    right = max(640 + text_width("TEZORA", 800, 200, 0.14), 644 + text_width("GILAM YUVISH XIZMATI", 600, 46, 0.42))
    return svg(fit(b, 229, 245, right, 762))

# ================================================================ 4. MUHR — dumaloq nishon (badge)
def logo4(dark=False):
    p = pal(dark)
    cx, cy = 800, 500
    ring = NAVY if not dark else '#13306B'
    defs = (f'<linearGradient id="g4" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="{CYAN}"/>'
            f'<stop offset="1" stop-color="{BLUE}"/></linearGradient>')
    b = f'<circle cx="{cx}" cy="{cy}" r="430" fill="{ring}"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="320" fill="{"#fff" if not dark else "#0B1F44"}"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="412" fill="none" stroke="{CYAN}" stroke-width="5"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="336" fill="none" stroke="{CYAN}" stroke-width="5"/>'
    # aylana matnlar
    t1 = 'GILAM YUVISH XIZMATI'; size = 56; tr = 0.18; r = 352
    L1 = arc_text_len(t1, 800, size, tr, r)
    d, _ = text_on_circle(t1, 800, size, cx, cy, r, -L1 / 2, tr)
    b += f'<path d="{d}" fill="#fff"/>'
    t2 = 'SAMARQAND'
    L2 = arc_text_len(t2, 800, size, tr, r)
    # pastki yoy: matnni pastdan o'qiladigan qilish uchun 180° ga burilgan doirada chizamiz
    d2, _ = text_on_circle(t2, 800, size, cx, cy, r, -L2 / 2, tr)
    b += f'<g transform="rotate(180 {cx} {cy})"><path d="{d2}" fill="#fff" transform="rotate(0)"/></g>' if False else ''
    # pastki yoy uchun: glif tayanchini doiraning ichki tomoniga qaratamiz
    f = FONTS[800]; gs = f.getGlyphSet(); s = size / f['head'].unitsPerEm
    rr = r + size * 0.72; ang = math.radians(180 + L2 / 2); dd = []
    for c in t2:
        g, adv = glyph_info(f, c); a = adv * s
        mid = ang - (a / 2) / rr
        px, py = cx + rr * math.sin(mid), cy - rr * math.cos(mid)
        th = mid - math.pi; ca, sa = math.cos(th), math.sin(th)
        T = (s * ca, s * sa, s * sa, -s * ca, px - (a / 2) * ca, py - (a / 2) * sa)
        pen = SVGPathPen(gs); gs[g].draw(TransformPen(pen, T)); dd.append(pen.getCommands())
        ang -= (a + tr * size) / rr
    b += f'<path d="{" ".join(dd)}" fill="#fff"/>'
    for a in (-1, 1):
        x = cx + a * 392; b += sparkle(x, cy + 8, 20, CYAN)
    # markaz
    b += f'<path d="{drop(cx, cy - 20, 78)}" fill="url(#g4)"/>'
    b += f'<path d="M{cx - 38},{cy - 20} A38,38 0 0 0 {cx},{cy + 18}" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round"/>'
    b += f'<path d="{text_path("TEZORA", 900, 96, cx, cy + 185, "middle", track=0.03)}" fill="{p["ink"] if dark else NAVY}"/>'
    return svg(b, defs)

# ================================================================ 5. MINIMAL — kichik harflar, "o" — pufakcha, ostida to'lqin
def logo5(dark=False):
    p = pal(dark)
    size = 300; y = 600
    defs = (f'<linearGradient id="g5" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/>'
            f'<stop offset="1" stop-color="{BLUE}"/></linearGradient>')
    pre, post = 'tez', 'ra'
    w_pre = text_width(pre, 800, size); w_o = text_width('o', 800, size); w_post = text_width(post, 800, size)
    total = w_pre + w_o + w_post; x0 = 800 - total / 2
    b = f'<path d="{text_path(pre, 800, size, x0, y)}" fill="{p["ink"]}"/>'
    ox = x0 + w_pre + w_o / 2; oy = y - size * 0.265; orr = size * 0.27
    b += f'<circle cx="{ox}" cy="{oy}" r="{orr}" fill="url(#g5)"/>'
    b += f'<path d="M{ox - orr * 0.55},{oy - orr * 0.1} A{orr * 0.55},{orr * 0.55} 0 0 1 {ox - orr * 0.05},{oy - orr * 0.6}" fill="none" stroke="#fff" stroke-width="13" stroke-linecap="round"/>'
    b += sparkle(ox + orr * 0.95, oy - orr * 1.05, 34, CYAN)
    b += f'<path d="{text_path(post, 800, size, x0 + w_pre + w_o, y)}" fill="{p["ink"]}"/>'
    wy = y + 70
    b += (f'<path d="M{x0 + 10},{wy} C{x0 + total * 0.2},{wy - 38} {x0 + total * 0.33},{wy + 38} {x0 + total * 0.5},{wy} '
          f'C{x0 + total * 0.67},{wy - 38} {x0 + total * 0.8},{wy + 38} {x0 + total - 10},{wy}" fill="none" stroke="url(#g5)" stroke-width="16" stroke-linecap="round"/>')
    b += f'<path d="{text_path("gilam yuvish xizmati", 600, 54, 800, wy + 110, "middle", track=0.2)}" fill="{p["sub"]}"/>'
    return svg(b, defs)

# ================================================================ 6. SAMARQAND NAQSHI — 8 qirrali yulduz (girih) + tomchi, firuza + oltin
def logo6(dark=False):
    p = pal(dark)
    cx, cy, R = 800, 330, 205
    def square(rot):
        pts = []
        for k in range(4):
            a = math.radians(rot + 45 + k * 90); pts.append(f'{cx + R * math.cos(a):.1f},{cy + R * math.sin(a):.1f}')
        return 'M' + ' L'.join(pts) + ' Z'
    star = square(0) + ' ' + square(45)
    b = f'<path d="{square(0)}" fill="{TURQ}"/><path d="{square(45)}" fill="{TURQ}"/>'
    b += f'<path d="{star}" fill="none" stroke="{GOLD}" stroke-width="10" stroke-linejoin="round"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R * 0.7}" fill="none" stroke="{GOLD}" stroke-width="6"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R * 0.6}" fill="{NAVY if not dark else "#0B1F44"}"/>'
    b += f'<path d="{drop(cx, cy + 34, 60)}" fill="#fff"/>'
    b += f'<path d="M{cx - 30},{cy + 34} A30,30 0 0 0 {cx},{cy + 64}" fill="none" stroke="{TURQ}" stroke-width="10" stroke-linecap="round"/>'
    b += f'<path d="{text_path("TEZ", 900, 170, 800 - text_width("TEZORA", 900, 170, 0.04) / 2, 735, track=0.04)}" fill="{p["ink"]}"/>'
    b += f'<path d="{text_path("ORA", 900, 170, 800 - text_width("TEZORA", 900, 170, 0.04) / 2 + text_width("TEZ", 900, 170, 0.04) + 0.04 * 170, 735, track=0.04)}" fill="{TURQ}"/>'
    lw = text_width("GILAM YUVISH XIZMATI · SAMARQAND", 700, 40, 0.24)
    b += f'<path d="{text_path("GILAM YUVISH XIZMATI · SAMARQAND", 700, 40, 800, 815, "middle", track=0.24)}" fill="{GOLD}"/>'
    return svg(b)

LOGOS = [
    ('1_tomchi', 'Tomchi', 'Klassik suv tomchisi — tozalik va suv bilan yuvish. Har qanday joyga mos, eng universal variant.', logo1),
    ('2_gilam_tolqini', "Gilam to'lqini", "Gilam va uni yuvayotgan to'lqin — nima xizmat ekani birinchi qarashda tushunarli.", logo2),
    ('3_monogramma', 'Monogramma', "Tomchi ichida suvdan yasalgan «T» harfi, to'q ko'k va oltin — premium, ishonchli ko'rinish.", logo3),
    ('4_muhr', 'Muhr', "Dumaloq nishon: formalar, mashina eshigi, stiker va Instagram avatari uchun ideal.", logo4),
    ('5_minimal', 'Minimal', "Zamonaviy kichik harflar, «o» — sovun pufakchasi, ostida to'lqin. Yoshlar va ijtimoiy tarmoqlar uchun.", logo5),
    ('6_samarqand', 'Samarqand naqshi', "Sharqona 8 qirrali yulduz (girih), Samarqand gumbazlari firuzasi va oltin — milliy, mahalliy brend.", logo6),
]

if __name__ == '__main__':
    for key, name, desc, fn in LOGOS:
        for dark in (False, True):
            open(os.path.join(OUT, f'tezora_logo_{key}_{"toq_fon" if dark else "oq_fon"}.svg'), 'w').write(fn(dark))
    print('SVG tayyor:', len(LOGOS) * 2)
