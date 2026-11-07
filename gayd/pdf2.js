const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 2 });
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await p.pdf({ path: process.argv[3], format: 'A4', printBackground: true, preferCSSPageSize: true });
  const secs = await p.$$('section.page');
  for (let i = 0; i < secs.length; i++) {
    await secs[i].screenshot({ path: process.argv[4] + '_' + (i + 1) + '.png' });
  }
  await b.close();
})();
