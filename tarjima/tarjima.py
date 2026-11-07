#!/usr/bin/env python3
"""Ruscha videodagi yozuvlarni o'zbekcha yozuvlarga almashtirish (19 LAB reklamasi).
Ruscha yozuv joyida xira shaffof plashka, ustida o'zbekcha matn (so'zma-so'z chiqadi)."""
import cv2, numpy as np, subprocess, os, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'asl_video_ru.mp4')
FONT = os.path.join(HERE, '..', 'assets', 'fonts', 'Montserrat-900.ttf')

# (boshlanish, tugash, o'zbekcha matn) — ruscha nutq vaqtlariga mos
SEGS = [
    (0.10, 3.20, "Xo'sh, yana mendan qutulmoqchimisan?"),
    (3.20, 3.60, "Ha!"),
    (4.30, 5.30, "Qani, urinib ko'r."),
    (7.30, 8.35, "Ha-ha!"),
    (8.35, 10.40, "Shunchaki yo'qolib qolaman deb o'ylaysanmi?"),
    (11.30, 12.45, "Voy, muncha sovuq!"),
    (13.80, 16.25, "Xo'sh, nima bo'pti? Men hali ham shu yerdaman."),
    (17.80, 20.00, "Nima, g'oyalaring tugadimi?"),
    (20.00, 21.30, "Men hech qayerga ketmadim."),
    (22.15, 23.75, "Bu yana nima?"),
    (25.95, 27.70, "Hoy, to'xtanglar!"),
    (27.70, 29.90, "Nega teri bunchalik namlanib ketyapti?"),
    (30.15, 32.25, "Men — 19 LAB zardob-flyuidiman."),
    (32.25, 33.70, "Tarkibimda bakuchiol bor."),
    (33.70, 35.70, "U ajinlarni kamroq sezilarli qiladi"),
    (35.70, 36.90, "va teri teksturasini yaxshilaydi."),
    (36.95, 38.70, "Tarkibimda yana skvalan bor."),
    (38.80, 40.00, "U namlikni ushlab turadi,"),
    (40.00, 40.85, "terini yumshatadi"),
    (40.85, 42.35, "va himoya to'sig'ini saqlaydi."),
    (42.35, 44.00, "Natijada teri parvarishlangan ko'rinadi."),
    (44.00, 44.85, "Senga ham shunday kerakmi?"),
    (44.85, 46.20, "Havola va artikul tavsifda."),
]

def groups(text, t0, t1, maxchars=13):
    """Matnni 1–2 so'zli bo'laklarga bo'lib, vaqtni harf soniga qarab taqsimlaydi."""
    words = text.split(); gs = []; cur = ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > maxchars:
            gs.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur: gs.append(cur)
    tot = sum(len(g) + 3 for g in gs); out = []; t = t0
    for g in gs:
        d = (t1 - t0) * (len(g) + 3) / tot
        out.append((t, t + d, g)); t += d
    return out

def caption_bbox(f):
    y0, y1 = 800, 1000
    band = f[y0:y1]
    white = (band.min(2) > 215).astype(np.uint8)
    dark = (band.max(2) < 70).astype(np.uint8)
    m = white & cv2.dilate(dark, np.ones((9, 9), np.uint8))
    if m.sum() < 60: return None
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n <= 1: return None
    idx = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 40]
    if not idx: return None
    xs0 = min(st[i, 0] for i in idx); ys0 = min(st[i, 1] for i in idx)
    xs1 = max(st[i, 0] + st[i, 2] for i in idx); ys1 = max(st[i, 1] + st[i, 3] for i in idx)
    if xs1 - xs0 < 20: return None
    return (xs0, ys0 + y0, xs1, ys1 + y0)

_fcache = {}
def word_img(txt, size=66):
    key = (txt, size)
    if key in _fcache: return _fcache[key]
    f = ImageFont.truetype(FONT, size)
    sw = 7
    w = int(f.getlength(txt)) + 2 * sw + 20; h = size + 2 * sw + 30
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((sw + 10, sw + 6), txt, font=f, fill=(255, 255, 255, 255), stroke_width=sw, stroke_fill=(0, 0, 0, 255))
    _fcache[key] = im
    return im

def main():
    cap = cv2.VideoCapture(SRC)
    fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames_bbox = []
    while True:
        ok, f = cap.read()
        if not ok: break
        frames_bbox.append(caption_bbox(f))
    n = len(frames_bbox)
    # har bir segment uchun doimiy plashka (ruscha yozuvlar birlashmasi)
    seg_box = []
    for (a, b, txt) in SEGS:
        bxs = [frames_bbox[i] for i in range(int(a * fps), min(n, int(b * fps) + 1)) if frames_bbox[i]]
        gw = max(word_img(g)[0].width if False else word_img(g).width for _, _, g in groups(txt, a, b))
        if bxs:
            x0 = min(bb[0] for bb in bxs); x1 = max(bb[2] for bb in bxs); y0 = min(bb[1] for bb in bxs); y1 = max(bb[3] for bb in bxs)
        else:
            x0, x1, y0, y1 = W // 2 - 100, W // 2 + 100, 870, 940
        cx = W // 2
        half = max(cx - x0, x1 - cx, gw // 2) + 26
        seg_box.append((max(8, cx - half), max(780, y0 - 22), min(W - 8, cx + half), min(1010, y1 + 22)))
    caps = []
    for si, (a, b, txt) in enumerate(SEGS):
        for (g0, g1, g) in groups(txt, a, b): caps.append((g0, g1, g, si))
    cap.release(); cap = cv2.VideoCapture(SRC)
    tmp = os.path.join(HERE, '_uz_video.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(n):
        ok, f = cap.read()
        if not ok: break
        t = i / fps
        box = None; si_act = None
        for si, (a, b, _) in enumerate(SEGS):
            if a - 0.05 <= t < b + 0.05: box = seg_box[si]; si_act = si; break
        bb = frames_bbox[i]
        if bb is not None:
            ex = (bb[0] - 26, bb[1] - 22, bb[2] + 26, bb[3] + 22)
            box = ex if box is None else (min(box[0], ex[0]), min(box[1], ex[1]), max(box[2], ex[2]), max(box[3], ex[3]))
        if box is not None:
            x0, y0, x1, y1 = [int(v) for v in box]
            x0 = max(0, x0); x1 = min(W, x1)
            pad = 40
            X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
            region = f[Y0:Y1, X0:X1]
            # yozuvni olib tashlab, xira oyna effekti
            m = np.zeros(region.shape[:2], np.uint8)
            if bb is not None:
                m[max(0, bb[1] - 14 - Y0):bb[3] + 14 - Y0, max(0, bb[0] - 14 - X0):bb[2] + 14 - X0] = 255
                region = cv2.inpaint(region, m, 9, cv2.INPAINT_TELEA)
            bl = cv2.GaussianBlur(region, (0, 0), 22)
            bl = (bl.astype(np.float32) * 0.62).astype(np.float32)
            mk = Image.new('L', ((X1 - X0) * 3, (Y1 - Y0) * 3), 0)
            ImageDraw.Draw(mk).rounded_rectangle(((x0 - X0) * 3, (y0 - Y0) * 3, (x1 - X0) * 3, (y1 - Y0) * 3), 34 * 3, fill=255)
            mk = np.asarray(mk.resize((X1 - X0, Y1 - Y0), Image.LANCZOS), np.float32)[..., None] / 255
            # kirish/chiqish silliqligi
            fa = 1.0
            if bb is None and si_act is not None:
                a, b, _ = SEGS[si_act]; fa = min(1, (t - (a - 0.05)) / 0.12, ((b + 0.05) - t) / 0.12)
            mk = mk * max(0, fa)
            out = f[Y0:Y1, X0:X1].astype(np.float32) * (1 - mk) + bl * mk
            f[Y0:Y1, X0:X1] = np.clip(out, 0, 255).astype(np.uint8)
        # o'zbekcha matn
        for (g0, g1, g, si) in caps:
            if g0 <= t < g1:
                im = word_img(g)
                pop = min(1, (t - g0) / 0.12); s = 0.8 + 0.2 * (1 - (1 - pop) ** 3)
                if s != 1: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
                bx = seg_box[si]; cy = (bx[1] + bx[3]) / 2
                x = int(W / 2 - im.width / 2); y = int(cy - im.height / 2 + 2)
                fr = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert('RGBA')
                fr.alpha_composite(im, (max(0, x), max(0, y)))
                f = cv2.cvtColor(np.asarray(fr.convert('RGB')), cv2.COLOR_RGB2BGR)
                break
        p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close(); p.wait()
    out = os.path.join(HERE, '19LAB_uzbekcha_yozuv.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', SRC, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy',
                    '-movflags', '+faststart', '-shortest', out], check=True)
    os.remove(tmp)
    print('tayyor:', out)

if __name__ == '__main__':
    main()
