// TEZORA logotiplari: SVG -> shaffof PNG (3200x2000) + taqdimot varag'i.
//   node tezora/src/logolar_png.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const DIR = path.join(__dirname, '..', 'logolar');
const META = [
  ['1_tomchi', '1. Tomchi', 'Klassik suv tomchisi — eng universal variant'],
  ['2_gilam_tolqini', "2. Gilam to'lqini", "Gilam + yuvuvchi to'lqin — xizmat darrov tushunarli"],
  ['3_monogramma', '3. Monogramma', "Tomchi ichida suv «T» — premium, oltin rang"],
  ['4_muhr', '4. Muhr', 'Dumaloq nishon — forma, stiker, avatar uchun'],
  ['5_minimal', '5. Minimal', "«o» — sovun pufakchasi, zamonaviy uslub"],
  ['6_samarqand', '6. Samarqand naqshi', 'Girih yulduz, firuza va oltin — milliy brend'],
];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
  for (const f of fs.readdirSync(DIR).filter(f => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(DIR, f), 'utf8');
    await p.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await p.locator('svg').screenshot({ path: path.join(DIR, f.replace('.svg', '.png')), omitBackground: true });
  }
  // taqdimot varag'i
  const card = ([k, t, d]) => `<div class="c"><div class="l"><img src="tezora_logo_${k}_oq_fon.svg"></div>
    <div class="d"><img src="tezora_logo_${k}_toq_fon.svg"></div><h3>${t}</h3><p>${d}</p></div>`;
  const html = `<html><head><style>
    body{margin:0;padding:70px;background:#EEF2F8;font-family:Montserrat,Arial,sans-serif;width:2260px}
    h1{margin:0 0 8px;font-size:64px;color:#0B1F44;letter-spacing:2px} .s{margin:0 0 50px;color:#4A5B7A;font-size:28px}
    .g{display:grid;grid-template-columns:repeat(3,1fr);gap:40px}
    .c{background:#fff;border-radius:28px;overflow:hidden;box-shadow:0 10px 30px rgba(11,31,68,.10)}
    .l{padding:20px 30px} .d{background:#0B1F44;padding:8px 120px} img{width:100%;display:block}
    h3{margin:22px 30px 6px;font-size:34px;color:#0B1F44} p{margin:0 30px 28px;font-size:23px;color:#4A5B7A}
  </style></head><body><h1>TEZORA — logotip variantlari</h1><p class="s">6 ta konsepsiya · har biri oq va to'q fon uchun · SVG (vektor) + PNG</p>
  <div class="g">${META.map(card).join('')}</div></body></html>`;
  fs.writeFileSync(path.join(DIR, '_taqdimot.html'), html);
  const q = await b.newPage({ viewport: { width: 2400, height: 1000 }, deviceScaleFactor: 1 });
  await q.goto('file://' + path.join(DIR, '_taqdimot.html'));
  await q.screenshot({ path: path.join(DIR, 'TEZORA_logotiplar_taqdimot.png'), fullPage: true });
  await b.close();
  console.log('PNG tayyor');
})();
