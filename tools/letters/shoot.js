// QA screenshots for letters. Usage: node shoot.js [tag]
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'http://127.0.0.1:8931/letters/index.html';
const OUT = '/home/claude/qa5/letters/';
const tag = process.argv[2] || 'v';
const CH = ['arrival', 'souls', 'connection', 'moment', 'invitation', 'details', 'blessing'];
(async () => {
  const b = await chromium.launch();
  const errs = [];
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  p.on('pageerror', e => errs.push('pageerror ' + e.message));
  p.on('requestfailed', r => errs.push('failed ' + r.url()));
  p.on('response', r => r.status() >= 400 && errs.push(r.status() + ' ' + r.url()));
  await p.goto(BASE, { waitUntil: 'networkidle' });
  await p.waitForTimeout(800);
  await p.screenshot({ path: `${OUT}${tag}-01-arrival.png` });
  // opening animation mid-frame
  await p.click('#openBtn');
  await p.waitForTimeout(1100);
  await p.screenshot({ path: `${OUT}${tag}-01b-opening.png` });
  await p.waitForTimeout(1300);
  await p.screenshot({ path: `${OUT}${tag}-01c-open.png` });
  await p.waitForTimeout(1500);
  // invitation closed -> opening -> open
  await p.goto(BASE + '#moment', { waitUntil: 'networkidle' });
  await p.waitForTimeout(500);
  await p.click('#nextBtn'); await p.waitForTimeout(1200);
  await p.screenshot({ path: `${OUT}${tag}-05a-env.png` });
  await p.click('#invOpen'); await p.waitForTimeout(1300);
  await p.screenshot({ path: `${OUT}${tag}-05b-opening.png` });
  await p.waitForTimeout(2200);
  for (let k = 1; k < CH.length; k++) {
    await p.evaluate(c => window.atlasGo(c), CH[k]);
    await p.waitForTimeout(2600);
    await p.screenshot({ path: `${OUT}${tag}-0${k + 1}-${CH[k]}.png` });
  }
  const overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  // other viewports, first screen
  for (const [w, h, n] of [[412, 915, 'android'], [820, 1180, 'tablet'], [1440, 900, 'desktop'], [360, 640, 'small'], [320, 568, 'se']]) {
    const c = await b.newContext({ viewport: { width: w, height: h } });
    const q = await c.newPage();
    q.on('pageerror', e => errs.push(n + ' pageerror ' + e.message));
    await q.goto(BASE, { waitUntil: 'networkidle' });
    await q.waitForTimeout(600);
    await q.screenshot({ path: `${OUT}${tag}-vp-${n}.png` });
    if (n === 'small' || n === 'desktop' || n === 'se') {
      for (const c2 of ['connection', 'invitation', 'details', 'blessing']) {
        await q.evaluate(c => window.atlasGo(c), c2);
        await q.waitForTimeout(900);
        await q.screenshot({ path: `${OUT}${tag}-vp-${n}-${c2}.png` });
      }
      const ov = await q.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      if (ov > 0) errs.push(n + ' overflow ' + ov);
    }
    await c.close();
  }
  console.log(JSON.stringify({ errs, overflow }, null, 1));
  await b.close();
})();
