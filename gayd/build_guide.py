#!/usr/bin/env python3
"""Kunlik ovqatlanish qo'llanmasi (3 sahifali A4 PDF). Ishlatish: python3 build_guide.py <kun>"""
import base64, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, '..', 'assets', 'fonts')
def b64(p): return base64.b64encode(open(p, 'rb').read()).decode()
IMG = b64(os.path.join(HERE, '1-kun.jpg'))

MEALS = [
    dict(time="08:00", name="Nonushta", kcal=320, p=16, f=11, c=36,
         items=[("Tuxum, qaynatilgan", "2 dona"), ("Pomidor", "100 g"), ("Bodring", "100 g"), ("Donli non", "1–2 bo‘lak (40–60 g)")],
         note="Kunni oqsil va kletchatka bilan boshlash uzoq vaqt to‘qlik beradi."),
    dict(time="11:00", name="Tamaddi", kcal=180, p=3, f=10, c=22,
         items=[("Olma", "1 dona (150 g)"), ("Yong‘oq", "5–6 dona (15 g)")],
         note="Meva va foydali yog‘lar qonda qand darajasini barqaror ushlaydi."),
    dict(time="13:30", name="Tushlik", kcal=430, p=24, f=14, c=50,
         items=[("Mol go‘shtli mastava", "1 kosa (350 ml)"), ("Ko‘katli salat", "150 g, 1 choy qoshiq moy")],
         note="Kunning eng to‘yimli ovqati — energiya va oqsil manbai."),
    dict(time="16:30", name="Tamaddi", kcal=120, p=8, f=4, c=11,
         items=[("Kefir, 1–2,5%", "1 piyola (250 ml)")],
         note="Kefir ichak mikroflorasini qo‘llab-quvvatlaydi."),
    dict(time="19:00", name="Kechki ovqat", kcal=400, p=38, f=12, c=32,
         items=[("Baliq, duxovkada", "150 g"), ("Grechka, pishgan", "120 g"), ("Brokkoli", "150 g")],
         note="Yengil, ammo oqsilga boy kechki ovqat — uyqudan 3 soat oldin."),
]
PLACEHOLDER_TOT = None
_TOTLINE = dict(kcal=sum(m['kcal'] for m in MEALS), p=sum(m['p'] for m in MEALS), f=sum(m['f'] for m in MEALS), c=sum(m['c'] for m in MEALS))

PREP = [
    ("Tuxum", "Qaynab turgan suvga solib, 8–9 daqiqa pishiring, so‘ng sovuq suvga oling."),
    ("Mastava", "Yog‘siz mol go‘shtidan foydalaning, guruchni kamroq, sabzavotni ko‘proq soling."),
    ("Baliq", "180°C da 20–25 daqiqa pishiring. Limon, sarimsoq va ziravor yetarli — moy kam."),
    ("Grechka", "1 o‘lchov grechkaga 2 o‘lchov suv, past olovda 15–20 daqiqa."),
    ("Brokkoli", "Bug‘da 5–7 daqiqa — rangi yashil, o‘zi qarsildoq qolsin."),
]
RULES = [
    "Kun davomida 2–2,5 litr toza suv iching.",
    "Choy va qahvani shakarsiz iching.",
    "Ovqatni sekin, yaxshilab chaynab yeng.",
    "Qovurilgan, shirin va oq undan tayyorlangan mahsulotlarni cheklang.",
    "Ovqatlar orasida 2,5–3 soat tanaffus qiling.",
    "Kechki ovqatni uyqudan kamida 3 soat oldin tugating.",
]
SHOP = [
    ("Oqsil", ["Tuxum — 2 dona", "Mol go‘shti (yog‘siz) — 100 g", "Baliq — 150 g", "Kefir — 250 ml"]),
    ("Sabzavot va meva", ["Pomidor, bodring", "Brokkoli — 150 g", "Ko‘katlar (ukrop, kashnich)", "Olma — 1 dona", "Mastava uchun sabzavotlar", "Limon"]),
    ("Don va boshqalar", ["Donli non", "Grechka — 50 g (quruq)", "Guruch — 30 g", "Yong‘oq — 15 g", "Zaytun moyi"]),
]

DAY = int(sys.argv[1]) if len(sys.argv) > 1 else 1
if DAY != 1:
    import importlib
    _d = importlib.import_module(f'day{DAY}')
    MEALS, PREP, SHOP = _d.MEALS, _d.PREP, _d.SHOP
    RULES = getattr(_d, 'RULES', RULES)
    IMG = b64(os.path.join(HERE, f'{DAY}-kun.jpg'))
PLATE_LABEL, PLATE = 'Nonushta namunasi', ('pomidor, bodring, brokkoli, salat', 'tuxum, baliq, go‘sht, kefir', 'donli non, grechka')
if DAY != 1:
    PLATE_LABEL = getattr(_d, 'PLATE_LABEL', 'Taom namunasi'); PLATE = getattr(_d, 'PLATE', PLATE)
TOT = dict(kcal=sum(m['kcal'] for m in MEALS), p=sum(m['p'] for m in MEALS), f=sum(m['f'] for m in MEALS), c=sum(m['c'] for m in MEALS))

def page_cover():
    return f"""
<section class="page cover">
  <div class="cover-img" style="background-image:url(data:image/jpeg;base64,{IMG})"></div>
  <div class="cover-shade"></div>
  <div class="cover-in">
    <div class="brandline"><span class="leaf"></span>Shaxsiy ovqatlanish dasturi</div>
    <div class="cover-main">
      <div class="kicker">Sog‘lom vazn va energiya uchun</div>
      <h1>Ovqatlanish<br>rejasi</h1>
      <div class="daybig">{DAY}-kun</div>
    </div>
    <div class="cover-meta">
      <div><span>Mijoz</span><i></i></div>
      <div><span>Sana</span><i></i></div>
      <div><span>Kunlik me’yor</span><b>≈ {TOT['kcal']:,} kkal</b></div>
    </div>
  </div>
</section>""".replace(f"{TOT['kcal']:,}", f"{TOT['kcal']:,}".replace(',', ' '))

def macro_bar():
    pk, fk, ck = TOT['p'] * 4, TOT['f'] * 9, TOT['c'] * 4
    s = pk + fk + ck
    return f"""<div class="mbar"><i style="width:{pk/s*100:.1f}%" class="mp"></i><i style="width:{fk/s*100:.1f}%" class="mf"></i><i style="width:{ck/s*100:.1f}%" class="mc"></i></div>
<div class="mlegend"><span><b class="mp"></b>Oqsil {pk/s*100:.0f}%</span><span><b class="mf"></b>Yog‘ {fk/s*100:.0f}%</span><span><b class="mc"></b>Uglevod {ck/s*100:.0f}%</span></div>"""

def page_plan():
    rows = ""
    for m in MEALS:
        items = "".join(f"<li><span>{a}</span><em>{b}</em></li>" for a, b in m['items'])
        rows += f"""
<div class="meal">
  <div class="mtime">{m['time']}</div>
  <div class="mbody">
    <div class="mhead"><h3>{m['name']}</h3><div class="kc">{m['kcal']} <small>kkal</small></div></div>
    <ul>{items}</ul>
    <div class="mfoot"><span class="chip">O {m['p']} g</span><span class="chip">Y {m['f']} g</span><span class="chip">U {m['c']} g</span><span class="why">{m['note']}</span></div>
  </div>
</div>"""
    return f"""
<section class="page plan">
  <header class="ph"><div><div class="eyebrow">{DAY}-kun · Kunlik menyu</div><h2>Bugungi ovqatlanish</h2></div><div class="pn">02</div></header>
  <div class="totals">
    <div class="tot"><b>{TOT['kcal']}</b><span>kkal</span></div>
    <div class="tot"><b>{TOT['p']} g</b><span>oqsil</span></div>
    <div class="tot"><b>{TOT['f']} g</b><span>yog‘</span></div>
    <div class="tot"><b>{TOT['c']} g</b><span>uglevod</span></div>
    <div class="tot wide">{macro_bar()}</div>
  </div>
  <div class="timeline">{rows}</div>
  <div class="plate">
    <div class="pimg" style="background-image:url(data:image/jpeg;base64,{IMG})"><span>{PLATE_LABEL}</span></div>
    <div class="ptxt">
      <h5 class="sec">Likopcha qoidasi</h5>
      <div class="prow"><b class="pc1"></b><div><strong>½ — sabzavot va ko‘kat</strong><span>{PLATE[0]}</span></div></div>
      <div class="prow"><b class="pc2"></b><div><strong>¼ — oqsil</strong><span>{PLATE[1]}</span></div></div>
      <div class="prow"><b class="pc3"></b><div><strong>¼ — murakkab uglevod</strong><span>{PLATE[2]}</span></div></div>
    </div>
  </div>
  <div class="disc">Kaloriya va makronutrientlar taxminiy, porsiya hajmi va mahsulotga qarab farq qiladi. O — oqsil, Y — yog‘, U — uglevod.</div>
</section>"""

def page_tips():
    prep = "".join(f"<div class='prep'><h4>{a}</h4><p>{b}</p></div>" for a, b in PREP)
    rules = "".join(f"<li>{r}</li>" for r in RULES)
    shop = "".join(f"<div class='shopcol'><h4>{h}</h4>" + "".join(f"<label><i></i>{x}</label>" for x in xs) + "</div>" for h, xs in SHOP)
    water = "".join("<i></i>" for _ in range(8))
    return f"""
<section class="page tips">
  <header class="ph"><div><div class="eyebrow">{DAY}-kun · Amaliy tavsiyalar</div><h2>Tayyorlash va qoidalar</h2></div><div class="pn">03</div></header>
  <div class="grid2">
    <div>
      <h5 class="sec">Qanday tayyorlash kerak</h5>
      {prep}
    </div>
    <div>
      <h5 class="sec">Kun qoidalari</h5>
      <ol class="rules">{rules}</ol>
      <div class="water"><h5 class="sec">Suv nazorati <small>har bir stakan — 250 ml</small></h5><div class="cups">{water}</div></div>
    </div>
  </div>
  <div class="shop"><h5 class="sec">Xarid ro‘yxati — {DAY}-kun</h5><div class="shopgrid">{shop}</div></div>
  <div class="sign"><div>Dastur shaxsiy maqsad va sog‘liq holatiga moslashtiriladi. Surunkali kasallik, homiladorlik yoki allergiya bo‘lsa, shifokor bilan maslahatlashing.</div></div>
</section>"""

CSS = f"""
@font-face{{font-family:Disp;font-weight:600;src:url(data:font/ttf;base64,{b64(os.path.join(FD,'Fraunces-600.ttf'))})}}
@font-face{{font-family:Disp;font-weight:800;src:url(data:font/ttf;base64,{b64(os.path.join(FD,'Fraunces-800.ttf'))})}}
@font-face{{font-family:Body;font-weight:500;src:url(data:font/ttf;base64,{b64(os.path.join(FD,'Montserrat-500.ttf'))})}}
@font-face{{font-family:Body;font-weight:700;src:url(data:font/ttf;base64,{b64(os.path.join(FD,'Montserrat-700.ttf'))})}}
@font-face{{font-family:Body;font-weight:800;src:url(data:font/ttf;base64,{b64(os.path.join(FD,'Montserrat-800.ttf'))})}}
:root{{--ink:#1f2b22;--green:#1f5136;--sage:#dfe7d6;--paper:#fbfaf6;--saffron:#d99a2b;--tomato:#c8553d;--line:#e4e0d4;--muted:#6c7469}}
@page{{size:A4;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Body,sans-serif;color:var(--ink);background:var(--paper);-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page{{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;background:var(--paper)}}
/* cover */
.cover-img{{position:absolute;inset:0;background-size:cover;background-position:62% 55%}}
.cover-shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,40,26,.55) 0%,rgba(18,40,26,.15) 35%,rgba(18,40,26,.35) 55%,rgba(14,32,21,.94) 82%)}}
.cover-in{{position:absolute;inset:0;padding:18mm 18mm 16mm;display:flex;flex-direction:column;color:#fff}}
.brandline{{display:flex;align-items:center;gap:3mm;font-weight:700;font-size:9.5pt;letter-spacing:.2em;text-transform:uppercase}}
.leaf{{width:6mm;height:6mm;border-radius:0 6mm 0 6mm;background:var(--saffron)}}
.cover-main{{margin-top:auto}}
.kicker{{font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:10pt;color:#f3d79c}}
h1{{font-family:Disp;font-weight:800;font-size:54pt;line-height:.98;margin-top:4mm;letter-spacing:-.01em}}
.daybig{{display:inline-block;margin-top:6mm;font-family:Disp;font-weight:600;font-size:22pt;padding:2mm 7mm;border:1.5px solid rgba(255,255,255,.7);border-radius:20mm}}
.cover-meta{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8mm;margin-top:14mm;padding-top:6mm;border-top:1px solid rgba(255,255,255,.35)}}
.cover-meta span{{display:block;font-size:8pt;letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.7);font-weight:700}}
.cover-meta i{{display:block;height:7mm;border-bottom:1px solid rgba(255,255,255,.6)}}
.cover-meta b{{display:block;margin-top:1.5mm;font-family:Disp;font-weight:600;font-size:15pt}}
/* inner pages */
.plan,.tips{{padding:16mm 16mm 12mm;display:flex;flex-direction:column}}
.ph{{display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:4mm;border-bottom:1.5px solid var(--green)}}
.eyebrow{{font-weight:700;font-size:8.5pt;letter-spacing:.18em;text-transform:uppercase;color:var(--saffron)}}
h2{{font-family:Disp;font-weight:800;font-size:26pt;color:var(--green);margin-top:1.5mm}}
.pn{{font-family:Disp;font-weight:600;font-size:13pt;color:var(--muted)}}
.totals{{display:grid;grid-template-columns:repeat(4,1fr) 2.2fr;gap:3mm;margin:6mm 0 5mm;background:var(--green);color:#fff;border-radius:4mm;padding:4.5mm 5mm;align-items:center}}
.tot b{{display:block;font-family:Disp;font-weight:800;font-size:17pt;line-height:1}}
.tot span{{font-size:8pt;letter-spacing:.12em;text-transform:uppercase;color:#cfe0c9;font-weight:700}}
.mbar{{display:flex;height:3mm;border-radius:2mm;overflow:hidden;background:rgba(255,255,255,.2)}}
.mbar i{{display:block;height:100%}}
.mp{{background:#f0c065}} .mf{{background:#e98b6d}} .mc{{background:#a9d38a}}
.mlegend{{display:flex;gap:3mm;margin-top:2mm;font-size:7.3pt;font-weight:700;color:#e5eee0;white-space:nowrap}}
.mlegend b{{display:inline-block;width:2.4mm;height:2.4mm;border-radius:50%;margin-right:1mm;vertical-align:-.2mm}}
.timeline{{display:flex;flex-direction:column}}
.meal{{display:grid;grid-template-columns:17mm 1fr;gap:5mm;padding:3.6mm 0;border-bottom:1px solid var(--line);position:relative}}
.meal:last-child{{border-bottom:0}}
.mtime{{font-family:Disp;font-weight:600;font-size:13pt;color:var(--green);padding-top:.5mm}}
.mhead{{display:flex;justify-content:space-between;align-items:baseline}}
h3{{font-weight:800;font-size:12.5pt;letter-spacing:.01em}}
.kc{{font-family:Disp;font-weight:800;font-size:14pt;color:var(--tomato)}} .kc small{{font-family:Body;font-size:8pt;font-weight:700;color:var(--muted)}}
ul{{list-style:none;margin-top:1.8mm;display:grid;grid-template-columns:1fr 1fr;column-gap:8mm;row-gap:1mm}}
li{{display:flex;justify-content:space-between;gap:3mm;font-size:9.6pt;font-weight:500;border-bottom:1px dotted #cfcabb;padding-bottom:.8mm}}
li em{{font-style:normal;font-weight:700;color:var(--green);white-space:nowrap}}
.mfoot{{display:flex;align-items:center;gap:1.6mm;margin-top:2mm;flex-wrap:wrap}}
.chip{{font-size:7.5pt;font-weight:800;background:var(--sage);color:var(--green);padding:.7mm 2.2mm;border-radius:3mm}}
.why{{font-size:8.6pt;color:var(--muted);margin-left:2mm;font-weight:500}}
.plate{{display:grid;grid-template-columns:62mm 1fr;gap:7mm;margin-top:4mm;background:#f4f1e8;border-radius:4mm;padding:4mm;align-items:center}}
.pimg{{height:44mm;border-radius:3mm;background-size:cover;background-position:60% 55%;position:relative}}
.pimg span{{position:absolute;left:2.5mm;bottom:2.5mm;background:rgba(20,40,26,.82);color:#fff;font-size:7.5pt;font-weight:700;padding:.8mm 2.4mm;border-radius:2mm}}
.prow{{display:flex;gap:3mm;align-items:center;padding:1.6mm 0}}
.prow b{{width:7mm;height:7mm;border-radius:50%;flex:none}}
.pc1{{background:conic-gradient(var(--green) 0 50%,#e4e0d4 0)}} .pc2{{background:conic-gradient(var(--saffron) 0 25%,#e4e0d4 0)}} .pc3{{background:conic-gradient(var(--tomato) 0 25%,#e4e0d4 0)}}
.prow strong{{display:block;font-size:10pt;font-weight:800}} .prow span{{font-size:8.6pt;color:var(--muted)}}
.disc{{margin-top:auto;font-size:7.8pt;color:var(--muted)}}
.grid2{{display:grid;grid-template-columns:1.05fr 1fr;gap:9mm;margin-top:6mm}}
.sec{{font-weight:800;font-size:9pt;letter-spacing:.16em;text-transform:uppercase;color:var(--green);margin-bottom:3mm}}
.sec small{{font-weight:500;letter-spacing:0;text-transform:none;color:var(--muted);font-size:8pt;margin-left:2mm}}
.prep{{padding:2.6mm 0 2.6mm 4mm;border-left:2.5px solid var(--saffron);margin-bottom:2.4mm;background:#f4f1e8;border-radius:0 2mm 2mm 0;padding-right:3mm}}
.prep h4{{font-family:Disp;font-weight:600;font-size:12pt;color:var(--ink)}}
.prep p{{font-size:9pt;line-height:1.45;margin-top:.6mm}}
.rules{{list-style:none;counter-reset:r}}
.rules li{{counter-increment:r;display:block;border:0;font-size:9.6pt;line-height:1.4;padding:1.6mm 0 1.6mm 9mm;position:relative;border-bottom:1px solid var(--line)}}
.rules li::before{{content:counter(r);position:absolute;left:0;top:1.4mm;width:6mm;height:6mm;border-radius:50%;background:var(--green);color:#fff;font-weight:800;font-size:8pt;display:flex;align-items:center;justify-content:center}}
.water{{margin-top:6mm}}
.cups{{display:flex;gap:2.6mm}}
.cups i{{width:8.5mm;height:11mm;border:1.6px solid var(--green);border-top:none;border-radius:0 0 2mm 2mm;position:relative}}
.cups i::after{{content:"";position:absolute;left:1.2mm;right:1.2mm;bottom:1.2mm;height:5mm;background:#cfe3ee;border-radius:0 0 1mm 1mm}}
.shop{{margin-top:7mm;background:var(--sage);border-radius:4mm;padding:5mm 6mm}}
.shopgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:6mm}}
.shopcol h4{{font-family:Disp;font-weight:600;font-size:11.5pt;color:var(--green);margin-bottom:2mm}}
.shopcol label{{display:flex;align-items:center;gap:2mm;font-size:9pt;font-weight:500;padding:.9mm 0}}
.shopcol label i{{width:3.6mm;height:3.6mm;border:1.4px solid var(--green);border-radius:1mm;flex:none;background:#fff}}
.sign{{margin-top:auto;font-size:8pt;color:var(--muted);border-top:1px solid var(--line);padding-top:3mm}}
"""

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{page_cover()}{page_plan()}{page_tips()}</body></html>"
open(os.path.join(HERE, f'{DAY}-kun_qollanma.html'), 'w').write(html)
print('html tayyor')
