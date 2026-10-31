const { chromium } = require('playwright');
const out = process.argv[2] || '/home/claude/qa5/courtyard';
const URL = 'http://127.0.0.1:8741/courtyard/index.html';
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage(); const errs = [];
  p.on('console', m => m.type() === 'error' && errs.push(m.text())); p.on('pageerror', e => errs.push(e.message));
  p.on('requestfailed', r => errs.push('FAILED ' + r.url())); p.on('response', r => r.status() >= 400 && errs.push(r.status() + ' ' + r.url()));
  await p.goto(URL, { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  const H = await p.evaluate(() => { const w = document.querySelector('.walk'); return { top: w.offsetTop, range: w.offsetHeight - innerHeight }; });
  const ps = (process.env.PS || '0,0.08,0.2,0.32,0.5,0.7,0.85,1').split(',').map(Number);
  for (const v of ps) { await p.evaluate(y => scrollTo(0, y), H.top + H.range * v); await p.waitForTimeout(700); await p.screenshot({ path: `${out}/walk-${String(v).replace('.', '')}.png` }); }
  for (const id of ['invitation', 'details', 'blessing']) { await p.evaluate(id => document.getElementById(id).scrollIntoView(), id); await p.waitForTimeout(600); await p.screenshot({ path: `${out}/${id}.png` }); }
  console.log('errors', JSON.stringify(errs));
  await b.close();
})();
