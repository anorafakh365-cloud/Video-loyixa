#!/usr/bin/env python3
"""«54 zina» — ayol varianti. Bitta foto + grafika: har bir gapga mos kadr.
  python3 zina/src/render.py --stills 1 10 40        # nazorat kadrlari
  python3 zina/src/render.py                         # to'liq video -> zina/out/_video.mp4
Vaqtlar: zina/out/timing.json bo'lsa (ovozdan olingan) — shundan, aks holda so'z soniga qarab taxminiy.
"""
import os, sys, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE); ROOT = os.path.dirname(PRJ)
OUT = os.path.join(PRJ, 'out'); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
def F(w, s): return ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', f'Montserrat-{w}.ttf'), int(s))
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, t0, d): return clamp((t - t0) / d)
RED = (235, 38, 38); AMBER = (255, 196, 92); TEAL = (110, 200, 190); WHITE = (255, 255, 255)

# ================================================================ SSENARIY: (gap, sahna, parametrlar)
# sahnalar: photo(crop), led(qiymat), stairs(zina), dark(katta yozuv), plate, list, quote
S = [
 ("Uydagi tarozi raqam ko'rsatmadi — faqat «Error».", 'led', dict(txt='Err', col=RED, photo='feet')),
 ("Meni omborda, un qoplari tortiladigan tarozida o'lchashdi.", 'photo', dict(a=(480, 700, 1312), b=(520, 660, 1180))),
 ("270 kilo.", 'led', dict(v0=0, v1=270.0, photo='full')),
 ("O'sha kuni lift ishlamas edi.", 'lift', {}),
 ("To'rtinchi qavat. Ellik to'rt zina.", 'stairs', dict(s0=0, s1=0, big='54', sub='zina')),
 ("Besh yoshli qizim qo'limdan tortdi: «Oyijon, men sizga yordam beraman».", 'photo', dict(a=(400, 620, 640), b=(395, 610, 520))),
 ("Yigirmanchi zinada havo yetmay qoldi.", 'stairs', dict(s0=1, s1=20, breath=True)),
 ("O'ttizinchisida cho'kkalab qoldim.", 'stairs', dict(s0=20, s1=30, fall=True)),
 ("Qizim qo'shnilarni chaqirib keldi.", 'dark', dict(big='', sub='', door=True)),
 ("Olti erkak meni gilamga solib pastga tushirdi.", 'carpet', {}),
 ("Kasalxonada tomograf stoli menga torlik qildi.", 'ct', {}),
 ("Shifokor ko'zimga qaramay aytdi: «Apparat sizni ko'tarolmaydi».", 'quote', dict(q='«Apparat sizni\nko\'tarolmaydi»', who='shifokor')),
 ("O'sha kechasi qizim yonimga kelib pichirladi: «Oyi, siz o'lib qolmaysiz-a?»", 'photo', dict(a=(585, 230, 640), b=(590, 215, 520), night=True)),
 ("Boshqa yo'l qolmadi.", 'photo', dict(a=(590, 190, 470), b=(592, 185, 380), night=True)),
 ("Avval — tahlillar: qon, gormonlar, yurak, jigar.", 'list', dict(items=['Qon', 'Gormonlar', 'Yurak', 'Jigar'], title='TAHLILLAR', day=1, w=270)),
 ("Keyin — shifokor bilan reja. Och qolish emas: kuniga ikki yarim ming kaloriya.", 'dark', dict(big='2 500', sub='kkal / kun', day=3, w=270)),
 ("Tovoqning yarmi — ko'kat, chorak — go'sht, chorak — bo'tqa.", 'plate', dict(day=10, w=270)),
 ("Kuniga uch litr suv.", 'dark', dict(big='3', sub='litr suv', day=14, w=269, drops=True)),
 ("Harakat — besh daqiqa. Uyimiz eshigidan ko'cha boshigacha.", 'dark', dict(big='5', sub='daqiqa yurish', day=16, w=268, path=True)),
 ("Tizzalarim og'irlikni ko'tarmasdi. Har hafta bir daqiqa qo'shdim.", 'dark', dict(big='+1', sub='daqiqa / hafta', day=40, w=262)),
 ("Bir yil o'tdi. Tarozida — ikki yuz.", 'led', dict(v0=270.0, v1=200.0, photo='full', day=365, w=200)),
 ("Va men shoshildim.", 'photo', dict(a=(590, 210, 520), b=(590, 205, 470), night=True, day=365, w=200)),
 ("Telefonda «bir oyda minus yigirma» degan parhezni ko'rdim.", 'phone', dict(day=366, w=200)),
 ("Sakkiz yuz kaloriya. Yog'siz. Suvni ham kamaytirdim.", 'dark', dict(big='800', sub='kkal', red=True, day=380, w=192)),
 ("Ikki oydan keyin, yarim tunda, o'ng biqinimga pichoq tiqqandek og'riq turdi.", 'pain', dict(day=425, w=178)),
 ("O't pufagida tosh.", 'dark', dict(big='TOSH', sub="o't pufagida", red=True, day=426, w=178)),
 ("Shifokor: «Vazn tez ketsa, tosh tez yig'iladi». Bir oy kasalxonada yotdim.", 'quote', dict(q="«Vazn tez ketsa,\ntosh tez yig'iladi»", who='shifokor', day=427, w=178)),
 ("O'shandan beri qoidam: och qolish — yo'q. «Mo''jizaviy choy» — yo'q. Siydik haydovchi dori — yo'q.", 'list', dict(items=['Och qolish', "Mo'jizaviy choy", 'Siydik haydovchi'], title='YO\'Q', strike=True, day=460, w=176)),
 ("Haftasiga bir kilo — yetarli.", 'dark', dict(big='0,5–1', sub='kg / hafta', day=520, w=170)),
 ("Ikki yilda — yuz ellik. Uydagi tarozi birinchi marta raqam ko'rsatdi.", 'led', dict(v0=200.0, v1=150.0, photo='feet', day=730, w=150)),
 ("Keyin vazn to'xtadi. Ikki oy — bir gramm ham.", 'led', dict(v0=131.4, v1=131.4, photo='feet', sub='plato — odatiy hol', day=850, w=131)),
 ("Bir kechasi oshxonada, muzlatkich oldida, hammasini yeb qo'ydim.", 'fridge', dict(day=900, w=131)),
 ("Psixolog aytdi: «Bitta kecha — mag'lubiyat emas. Mag'lubiyat — ertasi kuni taslim bo'lish».", 'quote', dict(q="«Bitta kecha —\nmag'lubiyat emas.\nMag'lubiyat — ertasi\nkuni taslim bo'lish»", who='psixolog', day=904, w=131)),
 ("Stress ovqat bilan ketmaydi. Men uni yurish bilan haydadim — har gal o'n daqiqa.", 'dark', dict(big='10', sub='daqiqa — ovqat o\'rniga yurish', day=920, w=129, path=True)),
 ("Shifokor rejani qaytadan hisobladi. Yetti-sakkiz soat uyqu. Tarozi — haftada bir marta.", 'list', dict(items=['1 900 kkal', '7–8 soat uyqu', 'Tarozi — haftada 1'], title='YANGI REJA', day=990, w=124)),
 ("Yuz yigirma. Endi — gantellar: mushaklar ketmasin. Yuz.", 'led', dict(v0=120.0, v1=100.0, photo='feet', day=1210, w=100)),
 ("Bir kuni tongda yugurdim. O'n yilda birinchi marta.", 'sunrise', dict(day=1215, w=99)),
 ("Ha, terim osilib qoldi. Mayli. Bu — bosib o'tgan yo'limning narxi.", 'dark', dict(big='', sub='', warm=True, day=1300, w=90)),
 ("To'rt yil. 80 kilo. Minus bir yuz to'qson.", 'led', dict(v0=100.0, v1=80.0, photo='feet', sub='4 yil · −190 kg', gold=True, day=1460, w=80)),
 ("Bugun lift yana ishlamayapti. Ellik to'rt zina. Qizim to'qqiz yoshda.", 'stairs', dict(s0=0, s1=54, sunny=True)),
 ("U endi «o'lib qolmaysiz-a?» deb so'ramaydi.", 'stairs', dict(s0=54, s1=54, sunny=True, glow=True)),
 ("Sizchi? Sizda ikki yuz yetmish emas. O'n kilo. O'n besh. Yigirma.", 'dark', dict(big='10 · 15 · 20', sub='kilo', warm=True)),
 ("Ular og'ritmaydi. Qo'rqitmaydi. Shuning uchun yillar davomida qolib ketadi.", 'dark', dict(big='', sub='', warm=True, slow=True)),
 ("Mening tanlovim yo'q edi. Sizniki bor. Eng xavfli joyi ham shunda.", 'photo', dict(a=(590, 200, 560), b=(590, 195, 500))),
 ("«To'g'ri payt» hech qachon kelmaydi. Men uni ikki yuz yetmish kilogacha kutdim.", 'led', dict(v0=270.0, v1=270.0, photo='full')),
 ("Sport zal shart emas. Bugun o'n daqiqa yuring. Ertaga — yana.", 'dark', dict(big='10', sub='daqiqa · bugun', warm=True, path=True)),
 ("54 zina. Birinchi zinasi — bugun.", 'final', {}),
]

# ---------------------------------------------------------------- vaqtlar
TIMING = os.path.join(OUT, 'timing.json')
if os.path.exists(TIMING):
    TT = json.load(open(TIMING))           # [[boshlanish, tugash], ...] — har bir gap uchun
    START = [a for a, b in TT]; END = [b for a, b in TT]
    LEAD = 0.0
else:
    LEAD = 1.0; START = []; END = []; t = LEAD
    for s, _, _ in S:
        d = max(1.5, len(s.split()) / 2.2 + 0.3)
        START.append(t); END.append(t + d); t += d + 0.45
DUR = END[-1] + 3.0

# ---------------------------------------------------------------- foto
PH = Image.open(os.path.join(PRJ, 'assets', 'ayol.png')).convert('RGB')
PH = ImageEnhance.Contrast(PH).enhance(1.06)
PW, PHH = PH.size
def cam(cx, cy, h, im=PH):
    w = h * 9 / 16
    sw, sh = im.size
    if w > sw: w = sw; h = w * 16 / 9
    h = min(h, sh); w = h * 9 / 16
    cx = clamp(cx, w / 2, sw - w / 2); cy = clamp(cy, h / 2, sh - h / 2)
    return im.resize((W, H), Image.BICUBIC, box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
CROPS = {'full': ((470, 656, 1312), (480, 640, 1200)), 'feet': ((510, 1120, 520), (515, 1110, 470))}
def grade(im, night=False, warm=False, dark=0.0):
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(2, keepdims=True)
    a = lum + (a - lum) * (0.72 if night else 0.9)            # biroz rangsizroq — drama
    if night: a = a * np.array([0.62, 0.72, 0.95]) * 0.75
    elif warm: a = a * np.array([1.06, 0.98, 0.86])
    else: a = a * np.array([0.93, 1.0, 1.0])
    a *= (1 - dark)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

yy, xx = np.mgrid[0:H, 0:W]
VIG = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8),
                                 (np.clip(np.hypot((xx - W / 2) / W, (yy - H * 0.45) / H) * 1.9 - 0.35, 0, 1) * 220).astype(np.uint8)]), 'RGBA')
BOT = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (np.clip((yy - H * 0.6) / (H * 0.4), 0, 1) ** 1.4 * 200).astype(np.uint8)]), 'RGBA')
rng = np.random.default_rng(5)
GRAIN = [rng.normal(0, 9, (H // 2, W // 2)).astype(np.int16) for _ in range(8)]
DUST = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3.5), rng.uniform(5, 25), rng.uniform(0, 6)) for _ in range(90)]

def dust(fr, t, a=1.0, col=(255, 240, 210)):
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    for x, y, r, v, ph in DUST:
        X = (x + math.sin(t * 0.3 + ph) * 30) % W; Y = (y - t * v) % H
        al = int(110 * a * (0.5 + 0.5 * math.sin(t * 1.5 + ph)))
        d.ellipse([X - r, Y - r, X + r, Y + r], fill=col + (al,))
    fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))

def dark_bg(t, warm=False, red=False):
    top = np.array([30, 22, 16]) if warm else (np.array([40, 6, 8]) if red else np.array([10, 22, 26]))
    bot = np.array([4, 4, 5])
    k = np.clip(np.hypot((xx - W / 2) / W, (yy - H * (0.42 + 0.02 * math.sin(t * 0.4))) / H) * 1.6, 0, 1)[..., None]
    a = top * (1 - k) + bot * k
    return Image.fromarray(a.astype(np.uint8)).convert('RGBA')

# ---------------------------------------------------------------- yozuv yordamchilari
def text_img(s, font, fill=WHITE, stroke=0, spacing=0.12, align='center'):
    lines = s.split('\n'); lh = font.size * (1 + spacing)
    wmax = max(font.getlength(l) for l in lines)
    im = Image.new('RGBA', (int(wmax + 40), int(lh * len(lines) + 30)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = (im.width - font.getlength(l)) / 2 if align == 'center' else 20
        d.text((x, 10 + i * lh), l, font=font, fill=fill)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 0.8))
    out = Image.alpha_composite(sh, im)
    return out
_tc = {}
def T(s, w, size, fill=WHITE, align='center'):
    k = (s, w, size, fill, align)
    if k not in _tc: _tc[k] = text_img(s, F(w, size), fill, align=align)
    return _tc[k]
def put(fr, im, cx, cy, a=1.0, s=1.0):
    if a <= 0: return
    if s != 1: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    fr.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------------------------------------------------------------- subtitr (so'zma-so'z)
SUB_F = F(700, 50)
def wrap(words, font, maxw):
    lines = [[]]
    for w in words:
        test = ' '.join(lines[-1] + [w])
        if font.getlength(test) > maxw and lines[-1]: lines.append([w])
        else: lines[-1].append(w)
    return lines
def subtitle(fr, t, i):
    t0, t1 = START[i], END[i]
    if not (t0 - 0.05 <= t <= t1 + 0.35): return
    words = S[i][0].split(); lines = wrap(words, SUB_F, 900)
    n = len(words); k = 0
    out = clamp((t1 + 0.35 - t) / 0.3)
    lay = Image.new('RGBA', (W, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    lh = 66; y0 = 200 - len(lines) * lh / 2
    for li, ln in enumerate(lines):
        x = (W - SUB_F.getlength(' '.join(ln))) / 2
        for w in ln:
            tw = t0 + (t1 - t0) * 0.92 * k / max(1, n)
            a = clamp((t - tw) / 0.18) * out
            col = (255, 255, 255, int(255 * a)) if a > 0 else None
            if col is None: col = (255, 255, 255, int(70 * out))
            d.text((x, y0 + li * lh), w, font=SUB_F, fill=col)
            x += SUB_F.getlength(w + ' '); k += 1
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel('A').filter(ImageFilter.GaussianBlur(8)).point(lambda v: min(255, v)))
    fr.alpha_composite(sh, (0, 1330)); fr.alpha_composite(lay, (0, 1330))

# ---------------------------------------------------------------- LED tarozi displeyi (7 segment)
SEG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg',
       'E': 'afged', 'r': 'eg', '-': 'g', ' ': ''}
def led(txt, col=RED, h=260):
    w = h * 0.52; th = h * 0.085; gap = h * 0.24
    chars = list(txt); n = sum(1 for c in chars if c != '.')
    im = Image.new('RGBA', (int(n * (w + gap) + 60), int(h + 60)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 30; y = 30
    def seg(s, on):
        c = col + (255,) if on else col + (16,)
        X, Y = x, y; hw = w; hh = h / 2
        P = {'a': [(X + th, Y), (X + hw - th, Y), (X + hw - 2 * th, Y + th), (X + 2 * th, Y + th)],
             'g': [(X + th, Y + hh), (X + 2 * th, Y + hh - th / 2), (X + hw - 2 * th, Y + hh - th / 2), (X + hw - th, Y + hh), (X + hw - 2 * th, Y + hh + th / 2), (X + 2 * th, Y + hh + th / 2)],
             'd': [(X + 2 * th, Y + h - th), (X + hw - 2 * th, Y + h - th), (X + hw - th, Y + h), (X + th, Y + h)],
             'f': [(X, Y + th), (X + th, Y + 2 * th), (X + th, Y + hh - th), (X, Y + hh - th / 2)],
             'b': [(X + hw, Y + th), (X + hw, Y + hh - th / 2), (X + hw - th, Y + hh - th), (X + hw - th, Y + 2 * th)],
             'e': [(X, Y + hh + th / 2), (X + th, Y + hh + th), (X + th, Y + h - 2 * th), (X, Y + h - th)],
             'c': [(X + hw, Y + hh + th / 2), (X + hw, Y + h - th), (X + hw - th, Y + h - 2 * th), (X + hw - th, Y + hh + th)]}
        d.polygon(P[s], fill=c)
    for i, c in enumerate(chars):
        if c == '.':
            d.ellipse([x - gap * 0.5 - th * 0.7, y + h - th * 1.4, x - gap * 0.5 + th * 0.7, y + h], fill=col + (255,)); continue
        for s in 'abcdefg': seg(s, s in SEG.get(c, ''))
        x += w + gap
    glow = im.filter(ImageFilter.GaussianBlur(h * 0.08))
    out = Image.alpha_composite(glow, im); out = Image.alpha_composite(out, im.filter(ImageFilter.GaussianBlur(2)))
    return out
_ledc = {}
def LED(txt, col=RED, h=260):
    k = (txt, col, h)
    if k not in _ledc:
        if len(_ledc) > 60: _ledc.clear()
        _ledc[k] = led(txt, col, h)
    return _ledc[k]
def panel(fr, cx, cy, w, h):
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 28, fill=(14, 14, 16, 235), outline=(70, 70, 76, 255), width=4)
    d.rounded_rectangle([cx - w / 2 + 24, cy - h / 2 + 24, cx + w / 2 - 24, cy + h / 2 - 24], 14, fill=(26, 6, 6, 255))
    fr.alpha_composite(lay)

# ---------------------------------------------------------------- HUD: kun va vazn
def hud(fr, t, i):
    p = S[i][2]
    if 'day' not in p: return
    j = i; day1 = p['day']; w1 = p['w']
    # oldingi qiymatdan silliq o'tish
    prev = next((S[k][2] for k in range(i - 1, -1, -1) if 'day' in S[k][2]), None)
    k = ease(prog(t, START[i], max(0.5, (END[i] - START[i]) * 0.8)))
    day = int(round((prev['day'] if prev else day1) + (day1 - (prev['day'] if prev else day1)) * k))
    wv = (prev['w'] if prev else w1) + (w1 - (prev['w'] if prev else w1)) * k
    first = prev is None
    a = ease(prog(t, START[i], 0.5)) if first else 1.0
    put(fr, T(f'{day}-kun', 700, 40, (230, 230, 230)), 150, 120, a)
    put(fr, T(f'{wv:.0f} kg', 800, 40, (255, 120, 110) if wv > 150 else (AMBER if wv > 100 else (140, 230, 160))), W - 150, 120, a)
    # vazn shkalasi (chap tomonda ingichka chiziq)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay); x = 60; y0, y1 = 220, 1180
    d.line([(x, y0), (x, y1)], fill=(255, 255, 255, int(70 * a)), width=2)
    for v in range(80, 271, 10):
        y = y1 - (v - 80) / 190 * (y1 - y0); d.line([(x, y), (x + (14 if v % 50 == 0 else 7), y)], fill=(255, 255, 255, int(90 * a)), width=2)
    y = y1 - (wv - 80) / 190 * (y1 - y0)
    d.polygon([(x + 4, y), (x + 26, y - 10), (x + 26, y + 10)], fill=(255, 255, 255, int(220 * a)))
    fr.alpha_composite(lay)

# ---------------------------------------------------------------- sahnalar
def sc_photo(t, i, p):
    k = (t - START[i]) / max(0.1, END[i] - START[i] + 0.5)
    cx, cy, h = [a + (b - a) * ease(k) for a, b in zip(p['a'], p['b'])]
    fr = grade(cam(cx, cy, h), night=p.get('night', False)).convert('RGBA')
    fr.alpha_composite(VIG); dust(fr, t, 0.5 if p.get('night') else 0.8)
    return fr

def photo_bg(name, t, i, dark=0.55, blur=0):
    (a, b) = CROPS[name]; k = (t - START[i]) / max(0.1, END[i] - START[i] + 0.5)
    cx, cy, h = [x + (y - x) * ease(k) for x, y in zip(a, b)]
    im = cam(cx, cy, h)
    if blur: im = im.resize((W // 6, H // 6)).filter(ImageFilter.GaussianBlur(blur)).resize((W, H), Image.BICUBIC)
    return grade(im, dark=dark).convert('RGBA')

def sc_led(t, i, p):
    fr = photo_bg(p.get('photo', 'feet'), t, i, dark=0.6, blur=3)
    fr.alpha_composite(VIG)
    k = prog(t, START[i] + 0.15, max(0.6, (END[i] - START[i]) * 0.75))
    if 'txt' in p: txt = p['txt'] if int(t * 6) % 3 else ' ' * len(p['txt']); col = p.get('col', RED)
    else:
        v = p['v0'] + (p['v1'] - p['v0']) * eout(k)
        if p['v0'] == 0: v = p['v1'] * eout(k) + (math.sin(t * 40) * 3 if k < 0.95 else 0)
        txt = f'{max(0, v):5.1f}'; col = (255, 200, 70) if p.get('gold') else (RED if p['v1'] > 140 else ((255, 170, 60) if p['v1'] > 100 else (90, 235, 120)))
    panel(fr, W / 2, 760, 900, 380)
    put(fr, LED(txt, col, 230), W / 2 - 30, 760)
    put(fr, T('kg', 700, 54, col), W / 2 + 395, 845, 0.9)
    if p.get('sub'): put(fr, T(p['sub'], 700, 48, (230, 230, 230)), W / 2, 1040, ease(prog(t, START[i] + 0.6, 0.5)))
    dust(fr, t, 0.6)
    return fr

def stairs_img(step, sunny, fall_k=0.0, glow=0.0):
    """Perspektivali zina: 54 pog'ona, 'step' ga qadar yoritilgan."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top_y, bot_y = 300, 1500; n = 18
    for j in range(n, -1, -1):
        k0 = min(1.0, j / n); k1 = min(1.0, (j + 1) / n)
        y0 = bot_y - (bot_y - top_y) * (1 - (1 - k0) ** 1.6); y1 = bot_y - (bot_y - top_y) * (1 - (1 - k1) ** 1.6)
        w0 = 900 * (1 - 0.72 * (1 - (1 - k0) ** 1.6)); w1_ = 900 * (1 - 0.72 * (1 - (1 - k1) ** 1.6))
        idx = int(j * 54 / n)
        lit = idx < step
        base = (150, 120, 85) if sunny else (70, 80, 78)
        if lit: base = (230, 170, 80) if sunny else (200, 70, 60)
        shade = 0.55 + 0.45 * (1 - k0)
        c_top = tuple(int(c * shade) for c in base); c_front = tuple(int(c * shade * 0.65) for c in base)
        ym = y1 + (y0 - y1) * 0.45
        d.polygon([(W / 2 - w1_ / 2, y1), (W / 2 + w1_ / 2, y1), (W / 2 + w0 / 2, ym), (W / 2 - w0 / 2, ym)], fill=c_top + (255,))
        d.polygon([(W / 2 - w0 / 2, ym), (W / 2 + w0 / 2, ym), (W / 2 + w0 / 2, y0), (W / 2 - w0 / 2, y0)], fill=c_front + (255,))
    # panjara
    for side in (-1, 1):
        pts = [(W / 2 + side * 470, bot_y - 260), (W / 2 + side * 140, top_y - 120)]
        d.line(pts, fill=(110, 70, 40, 255) if sunny else (60, 45, 35, 255), width=18)
        for j in range(12):
            k = j / 11; x = pts[0][0] + (pts[1][0] - pts[0][0]) * k; y = pts[0][1] + (pts[1][1] - pts[0][1]) * k
            d.line([(x, y), (x, y + 260 * (1 - 0.6 * k))], fill=(50, 70, 60, 255), width=int(8 - 4 * k))
    # deraza nuri
    win = Image.new('RGBA', (W, H)); wd = ImageDraw.Draw(win)
    wc = (255, 230, 170) if sunny else (150, 180, 200)
    wd.rectangle([W / 2 - 110, 90, W / 2 + 110, 300], fill=wc + (230,))
    wd.line([(W / 2, 90), (W / 2, 300)], fill=(40, 40, 40, 255), width=8); wd.line([(W / 2 - 110, 190), (W / 2 + 110, 190)], fill=(40, 40, 40, 255), width=8)
    im = Image.alpha_composite(im, win.filter(ImageFilter.GaussianBlur(2)))
    ray = Image.new('RGBA', (W, H)); rd = ImageDraw.Draw(ray)
    rd.polygon([(W / 2 - 110, 300), (W / 2 + 110, 300), (W / 2 + 420, 1500), (W / 2 - 300, 1500)], fill=wc + (int(40 + 60 * glow),))
    im = Image.alpha_composite(im, ray.filter(ImageFilter.GaussianBlur(40)))
    return im

def sc_stairs(t, i, p):
    sunny = p.get('sunny', False)
    fr = dark_bg(t, warm=sunny)
    k = prog(t, START[i], max(0.5, (END[i] - START[i]) * 0.9))
    step = p['s0'] + (p['s1'] - p['s0']) * (k if not p.get('breath') else (1 - (1 - k) ** 2))
    shake = 0
    if p.get('fall') and k > 0.85: shake = (1 - prog(t, START[i] + (END[i] - START[i]) * 0.85 * 0.9, 0.5)) * 18
    st = stairs_img(int(step), sunny, glow=1.0 if p.get('glow') else 0)
    ox = int(math.sin(t * 50) * shake); fr.alpha_composite(st, (ox, 0))
    if p.get('breath'):  # yurak urishi kabi qorayish
        pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 1.6)
        fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(90 * k * pulse))))
    if p.get('fall') and k > 0.85:
        fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(160 * prog(t, END[i] - 0.4, 0.4)))))
    fr.alpha_composite(VIG)
    num = p.get('big') or f'{int(step)}'
    col = (255, 225, 160) if sunny else ((255, 110, 100) if p.get('breath') or p.get('fall') else WHITE)
    put(fr, T(num, 800, 190, col), W / 2 - 40, 560, ease(prog(t, START[i], 0.4)))
    put(fr, T(p.get('sub', '/ 54'), 700, 54, (220, 220, 220)), W / 2 + 170, 620, ease(prog(t, START[i], 0.4)))
    dust(fr, t, 0.9 if sunny else 0.5)
    return fr

def sc_dark(t, i, p):
    fr = dark_bg(t, warm=p.get('warm', False), red=p.get('red', False))
    a = ease(prog(t, START[i], 0.5)); s = 0.92 + 0.08 * eout(prog(t, START[i], 0.8))
    if p.get('big'):
        col = (255, 90, 80) if p.get('red') else ((255, 215, 150) if p.get('warm') else WHITE)
        put(fr, T(p['big'], 800, 230 if len(p['big']) < 6 else 140, col), W / 2, 700, a, s)
        put(fr, T(p['sub'], 600, 56, (215, 215, 215)), W / 2, 880, ease(prog(t, START[i] + 0.3, 0.5)))
    if p.get('drops'):
        lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
        for j in range(3):
            kk = ease(prog(t, START[i] + 0.4 + j * 0.25, 0.4)); x = W / 2 + (j - 1) * 150
            d.rounded_rectangle([x - 45, 1020, x + 45, 1240], 20, outline=(120, 200, 255, int(220 * kk)), width=6)
            d.rectangle([x - 39, 1240 - 210 * kk, x + 39, 1234], fill=(80, 170, 255, int(140 * kk)))
        fr.alpha_composite(lay)
    if p.get('path'):
        lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay); kk = prog(t, START[i] + 0.3, max(0.5, END[i] - START[i] - 0.4))
        for j in range(int(14 * kk)):
            x = 180 + j * 52; y = 1120 + (j % 2) * 34
            d.ellipse([x, y, x + 30, y + 46], fill=(255, 255, 255, 160))
        fr.alpha_composite(lay)
    if p.get('door'):
        lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay); kk = eout(prog(t, START[i], 1.2))
        d.rectangle([W / 2 - 200, 380, W / 2 + 200, 1150], fill=(255, 220, 160, int(200 * kk)))
        d.polygon([(W / 2 - 200, 380), (W / 2 - 200 + 340 * (1 - kk), 420), (W / 2 - 200 + 340 * (1 - kk), 1110), (W / 2 - 200, 1150)], fill=(60, 40, 30, 255))
        fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
        # qizcha silueti yugurib chiqadi
        x = W / 2 + 60 - 300 * ease(prog(t, START[i] + 0.5, 1.2)); y = 1000
        sil = Image.new('RGBA', (W, H)); sd = ImageDraw.Draw(sil)
        sd.ellipse([x - 32, y - 230, x + 32, y - 166], fill=(20, 16, 14, 255)); sd.polygon([(x - 60, y), (x + 60, y), (x + 34, y - 170), (x - 34, y - 170)], fill=(230, 190, 40, 255))
        fr.alpha_composite(sil)
    fr.alpha_composite(VIG); dust(fr, t, 0.5, (255, 220, 190) if p.get('warm') else (200, 230, 255))
    return fr

def sc_quote(t, i, p):
    fr = photo_bg('full', t, i, dark=0.78, blur=4); fr.alpha_composite(VIG)
    a = ease(prog(t, START[i], 0.6))
    put(fr, T('“', 800, 260, (255, 255, 255)), W / 2, 420, a * 0.35)
    put(fr, T(p['q'], 700, 72, WHITE), W / 2, 760, a, 0.96 + 0.04 * a)
    put(fr, T('— ' + p['who'], 600, 44, (190, 190, 190)), W / 2, 1060, ease(prog(t, START[i] + 0.5, 0.5)))
    return fr

def sc_list(t, i, p):
    fr = dark_bg(t); fr.alpha_composite(VIG)
    put(fr, T(p['title'], 800, 70, (255, 120, 110) if p.get('strike') else TEAL), W / 2, 470, ease(prog(t, START[i], 0.4)))
    n = len(p['items']); span = max(0.6, END[i] - START[i] - 0.3)
    for j, it in enumerate(p['items']):
        tj = START[i] + 0.2 + span * j / n; a = ease(prog(t, tj, 0.35))
        y = 640 + j * 120
        put(fr, T(it, 700, 64, WHITE), W / 2, y, a)
        if p.get('strike'):
            ks = prog(t, tj + 0.35, 0.35)
            if ks > 0:
                lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay); half = F(700, 64).getlength(it) / 2 + 20
                d.line([(W / 2 - half, y + 8), (W / 2 - half + 2 * half * ks, y + 8)], fill=(255, 70, 60, 255), width=9); fr.alpha_composite(lay)
        else:
            put(fr, T('✓' if False else '•', 800, 64, TEAL), W / 2 - F(700, 64).getlength(it) / 2 - 50, y, a)
    dust(fr, t, 0.4)
    return fr

def sc_plate(t, i, p):
    fr = dark_bg(t, warm=True); lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    cx, cy, r = W / 2, 760, 330
    d.ellipse([cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40], fill=(235, 232, 225, 255))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(246, 244, 238, 255))
    span = max(0.6, END[i] - START[i] - 0.2)
    parts = [(90, 270, (70, 170, 80), "ko'kat ½", (cx - 420, cy)), (270, 360, (150, 60, 50), "go'sht ¼", (cx + 400, cy - 200)), (0, 90, (190, 140, 80), "bo'tqa ¼", (cx + 400, cy + 200))]
    for j, (a0, a1, col, lab, lp) in enumerate(parts):
        k = eout(prog(t, START[i] + 0.2 + span * j / 3, 0.5))
        if k > 0:
            d.pieslice([cx - r + 30, cy - r + 30, cx + r - 30, cy + r - 30], a0, a0 + (a1 - a0) * k, fill=col + (255,))
    fr.alpha_composite(lay)
    for j, (a0, a1, col, lab, lp) in enumerate(parts):
        put(fr, T(lab, 700, 52, WHITE), lp[0], lp[1] if j else cy + 420, ease(prog(t, START[i] + 0.3 + span * j / 3, 0.4)))
    fr.alpha_composite(VIG)
    return fr

def sc_generic_photo(t, i, kind):
    """lift, hands, carpet, ct, phone, pain, fridge, sunrise — foto + grafik belgilar."""
    if kind == 'lift':
        fr = dark_bg(t); lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
        d.rectangle([W / 2 - 300, 350, W / 2 + 300, 1200], fill=(70, 60, 50, 255)); d.line([(W / 2, 350), (W / 2, 1200)], fill=(30, 25, 20, 255), width=8)
        d.rectangle([W / 2 - 330, 320, W / 2 + 330, 350], fill=(90, 90, 85, 255))
        for k_ in range(2):
            y = 760 + k_ * 40
            for s_ in range(12):
                x = W / 2 - 360 + s_ * 60
                d.polygon([(x, y), (x + 60, y - 10), (x + 60, y + 14), (x, y + 24)], fill=((230, 40, 40) if s_ % 2 else (240, 240, 240)) + (255,))
        fr.alpha_composite(lay); put(fr, T('LIFT ISHLAMAYDI', 800, 46, (255, 210, 120)), W / 2, 1290, ease(prog(t, START[i] + 0.3, 0.4)))
        if int(t * 2.5) % 2: fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 40)))
    elif kind == 'hands':
        fr = photo_bg('full', t, i, dark=0.35); lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
        k = eout(prog(t, START[i] + 0.3, 1.0)); x = -120 + 420 * k; y = 1080
        d.rounded_rectangle([x - 260, y - 40, x, y + 40], 30, fill=(240, 200, 40, 255))   # sariq yeng
        d.ellipse([x - 20, y - 46, x + 70, y + 46], fill=(235, 190, 160, 255))           # kichik qo'l
        fr.alpha_composite(lay)
    elif kind == 'carpet':
        fr = dark_bg(t, warm=True); st = stairs_img(0, False); fr.alpha_composite(st)
        lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay); k = prog(t, START[i], END[i] - START[i] + 0.4)
        y = 520 + 520 * k
        d.rounded_rectangle([W / 2 - 300, y, W / 2 + 300, y + 260], 50, fill=(150, 30, 40, 255))
        for s_ in range(6):
            d.rounded_rectangle([W / 2 - 280 + s_ * 95, y + 30, W / 2 - 220 + s_ * 95, y + 230], 10, outline=(220, 170, 90, 255), width=5)
        for s_ in range(6):
            sx = W / 2 + (-380 if s_ % 2 == 0 else 380); sy = y - 40 + (s_ // 2) * 120
            d.ellipse([sx - 34, sy - 34, sx + 34, sy + 34], fill=(18, 18, 20, 255)); d.rectangle([sx - 40, sy + 30, sx + 40, sy + 170], fill=(18, 18, 20, 255))
        fr.alpha_composite(lay); put(fr, T('6', 800, 150, WHITE), 140, 420, ease(prog(t, START[i], 0.4))); put(fr, T('kishi', 600, 44, (220, 220, 220)), 140, 520, ease(prog(t, START[i], 0.4)))
    elif kind == 'ct':
        fr = dark_bg(t); lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
        d.ellipse([W / 2 - 330, 360, W / 2 + 330, 1020], fill=(230, 232, 235, 255)); d.ellipse([W / 2 - 170, 520, W / 2 + 170, 860], fill=(20, 26, 30, 255))
        d.rectangle([W / 2 - 120, 860, W / 2 + 120, 1180], fill=(205, 210, 215, 255))
        fr.alpha_composite(lay)
        put(fr, T('stol: 200 kg gacha', 700, 52, WHITE), W / 2, 1230, ease(prog(t, START[i] + 0.3, 0.4)))
        put(fr, T('270', 800, 120, RED), W / 2, 260, ease(prog(t, START[i] + 0.8, 0.4)))
    elif kind == 'phone':
        fr = photo_bg('full', t, i, dark=0.8, blur=5); lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle([W / 2 - 260, 330, W / 2 + 260, 1250], 60, fill=(10, 10, 12, 255)); d.rounded_rectangle([W / 2 - 235, 360, W / 2 + 235, 1220], 44, fill=(250, 250, 250, 255))
        fr.alpha_composite(lay)
        put(fr, T('−20 KG\n1 OYDA', 800, 110, (20, 20, 20)), W / 2, 620)
        d2 = Image.new('RGBA', (W, H)); dd = ImageDraw.Draw(d2); dd.ellipse([W / 2 - 90, 880, W / 2 + 90, 1060], fill=(120, 200, 60, 255)); fr.alpha_composite(d2)
        k = prog(t, END[i] - 0.6, 0.4)
        if k > 0:
            l2 = Image.new('RGBA', (W, H)); d3 = ImageDraw.Draw(l2)
            d3.line([(W / 2 - 300, 330), (W / 2 - 300 + 600 * k, 330 + 920 * k)], fill=(235, 40, 40, 255), width=16); fr.alpha_composite(l2)
    elif kind == 'pain':
        fr = photo_bg('full', t, i, dark=0.5); fr = Image.blend(fr, Image.new('RGBA', (W, H), (110, 0, 0, 255)), 0.35 + 0.25 * abs(math.sin(t * 5)))
        if prog(t, START[i] + (END[i] - START[i]) * 0.6, 0.1) > 0 and int(t * 8) % 2:
            fr = Image.blend(fr, Image.new('RGBA', (W, H), (30, 60, 255, 255)), 0.25)
    elif kind == 'fridge':
        fr = dark_bg(t); lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
        d.rectangle([W / 2 - 230, 300, W / 2 + 230, 1250], fill=(210, 230, 245, 235)); fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))
        ray = Image.new('RGBA', (W, H)); rd = ImageDraw.Draw(ray); rd.polygon([(W / 2 - 230, 1250), (W / 2 + 230, 1250), (W + 200, H), (-200, H)], fill=(160, 200, 255, 90)); fr.alpha_composite(ray.filter(ImageFilter.GaussianBlur(40)))
        for s_ in range(4):
            y = 430 + s_ * 200; l2 = Image.new('RGBA', (W, H)); d2 = ImageDraw.Draw(l2); d2.line([(W / 2 - 210, y), (W / 2 + 210, y)], fill=(255, 255, 255, 200), width=6); fr.alpha_composite(l2)
        sil = Image.new('RGBA', (W, H)); sd = ImageDraw.Draw(sil); sd.ellipse([W / 2 - 130, 980, W / 2 + 130, 1240], fill=(8, 8, 10, 255)); sd.ellipse([W / 2 - 330, 1150, W / 2 + 330, 1750], fill=(8, 8, 10, 255)); fr.alpha_composite(sil)
    elif kind == 'sunrise':
        fr = dark_bg(t, warm=True); lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay); k = eout(prog(t, START[i], END[i] - START[i]))
        sy = 980 - 260 * k
        for r_ in range(6, 0, -1): d.ellipse([W / 2 - 60 * r_, sy - 60 * r_, W / 2 + 60 * r_, sy + 60 * r_], fill=(255, 170, 70, 20 + 8 * (6 - r_)))
        d.ellipse([W / 2 - 110, sy - 110, W / 2 + 110, sy + 110], fill=(255, 210, 130, 255))
        d.rectangle([0, 980, W, H], fill=(70, 30, 25, 255))
        for ln in range(6): d.line([(W / 2 - 40 - ln * 80, 980), (W / 2 - 300 - ln * 300, H)], fill=(255, 255, 255, 120), width=4)
        fr.alpha_composite(lay)
    fr.alpha_composite(VIG); dust(fr, t, 0.6)
    return fr

def sc_final(t, i, p):
    fr = dark_bg(t, warm=True); st = stairs_img(1, True, glow=1.0); fr.alpha_composite(st); fr.alpha_composite(VIG)
    put(fr, T('54', 800, 240, (255, 225, 160)), W / 2 - 50, 560, ease(prog(t, START[i], 0.6)))
    put(fr, T('zina', 700, 64, (240, 220, 190)), W / 2 + 160, 630, ease(prog(t, START[i], 0.6)))
    put(fr, T('Birinchi zinasi — bugun.', 700, 64, WHITE), W / 2, 820, ease(prog(t, START[i] + 0.8, 0.6)))
    put(fr, T("Badiiy hikoya · g'oya: @javoxirmarufov", 600, 30, (190, 180, 170)), W / 2, 1760, ease(prog(t, START[i] + 1.5, 0.6)))
    dust(fr, t, 1.0)
    return fr

SCN = {'photo': sc_photo, 'led': sc_led, 'stairs': sc_stairs, 'dark': sc_dark, 'quote': sc_quote, 'list': sc_list, 'plate': sc_plate, 'final': sc_final}

def scene_idx(t):
    for i in range(len(S) - 1, -1, -1):
        if t >= START[i] - (0.25 if i else 99): return i
    return 0

def render_scene(t, i):
    kind = S[i][1]; p = S[i][2]
    if kind in SCN: return SCN[kind](t, i, p)
    return sc_generic_photo(t, i, kind)

def frame(t, fi):
    i = scene_idx(t)
    fr = render_scene(t, i)
    # sahnalar orasida 0.25 s yumshoq o'tish
    if i > 0 and t < START[i] + 0.0 and t >= START[i] - 0.25:
        pass
    tr = START[i] - 0.25
    if i > 0 and tr <= t < START[i] + 0.05:
        prev = render_scene(t, i - 1); k = ease((t - tr) / 0.3); fr = Image.blend(prev, fr, k)
    fr.alpha_composite(BOT)
    hud(fr, t, i)
    subtitle(fr, t, i)
    # sarlavha belgisi
    if t < 4: put(fr, T('Badiiy hikoya. Raqamlar — tibbiy manbalardan.', 600, 30, (200, 200, 200)), W / 2, 70, clamp(min(t / 0.5, (4 - t) / 0.5)))
    if t < 0.6: fr = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), fr, ease(t / 0.6))
    if t > DUR - 1.0: fr = Image.blend(fr, Image.new('RGBA', (W, H), (0, 0, 0, 255)), ease((t - (DUR - 1.0)) / 1.0))
    a = np.asarray(fr.convert('RGB')).astype(np.int16)
    a += np.kron(GRAIN[fi % 8], np.ones((2, 2), np.int16))[:, :, None]
    return np.clip(a, 0, 255).astype(np.uint8)

def render_part(arg):
    j, a, b = arg; seg = os.path.join(OUT, f'_part{j}.mp4')
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-threads', '1', '-pix_fmt', 'yuv420p', seg], stdin=subprocess.PIPE)
    for i in range(a, b):
        enc.stdin.write(frame(i / FPS, i).tobytes())
        if (i - a) % 300 == 0: print(f'[{j}] {i - a}/{b - a}', flush=True)
    enc.stdin.close(); enc.wait(); return seg

def main():
    if '--stills' in sys.argv:
        args = sys.argv[sys.argv.index('--stills') + 1:]
        for s in args:
            # raqam sahna indeksi bo'lsa — o'sha sahnaning o'rtasi
            i = int(s); t = (START[i] + END[i]) / 2
            Image.fromarray(frame(t, 0)).save(os.path.join(OUT, f'still_{i:02d}.png')); print('kadr', i, round(t, 2))
        return
    print('davomiylik', round(DUR, 1), 's')
    n = int(DUR * FPS); J = os.cpu_count() or 4
    from multiprocessing import Pool
    with Pool(J) as pool: segs = pool.map(render_part, [(j, j * n // J, (j + 1) * n // J) for j in range(J)])
    lst = os.path.join(OUT, '_parts.txt'); open(lst, 'w').write(''.join(f"file '{os.path.basename(x)}'\n" for x in segs))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(OUT, '_video.mp4')], check=True)
    for x in segs: os.remove(x)
    json.dump([[a, b] for a, b in zip(START, END)], open(os.path.join(OUT, '_timing_used.json'), 'w'))
    print('video tayyor')

if __name__ == '__main__':
    main()
