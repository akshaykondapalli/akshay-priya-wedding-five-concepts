// Renders SVG files to transparent PNGs at native size via Chromium. usage: node render_svg.js name1 name2 ...
const { chromium } = require('playwright'); const fs = require('fs');
const OUT = '/home/claude/tools5/temple/out/';
(async () => {
  const b = await chromium.launch();
  for (const n of process.argv.slice(2)) {
    const svg = fs.readFileSync(OUT + n + '.svg', 'utf8');
    const w = +svg.match(/width="(\d+)"/)[1], h = +svg.match(/height="(\d+)"/)[1];
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await p.waitForTimeout(200);
    await p.screenshot({ path: OUT + n + '.png', omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
    await p.close(); console.log('rendered', n, w, h);
  }
  await b.close();
})();
