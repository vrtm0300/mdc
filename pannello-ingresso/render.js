const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 800, height: 1100 } });
  const svg = require('fs').readFileSync(process.argv[2], 'utf8').replace(/width="400mm" height="550mm"/, 'width="800" height="1100"');
  await p.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  await p.screenshot({ path: process.argv[3] });
  await b.close();
})();
