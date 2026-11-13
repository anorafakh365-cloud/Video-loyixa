// ssenariy.html -> A4 PDF
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.join(__dirname, 'ssenariy.html'), { waitUntil: 'networkidle' });
  await p.pdf({ path: path.join(__dirname, 'Bayroq_kuni_ssenariy_A4.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close(); console.log('PDF tayyor');
})();
