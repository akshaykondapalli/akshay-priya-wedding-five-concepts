// node render.js in.svg out.png width [bgColor]
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const jobs = JSON.parse(process.argv[2]);
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [inp, out, w, bg] of jobs) {
    const svg = fs.readFileSync(inp, 'utf8');
    const vb = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/); const W = +vb[1], H = +vb[2];
    const h = Math.round(w * H / W);
    await p.setViewportSize({ width: w, height: h });
    await p.setContent(`<html><body style="margin:0;background:${bg || 'transparent'}">${svg.replace(/width="[\d.]+" height="[\d.]+"/, `width="${w}" height="${h}"`)}</body></html>`);
    await p.screenshot({ path: out, omitBackground: !bg, clip: { x: 0, y: 0, width: w, height: h } });
  }
  await b.close();
})();
