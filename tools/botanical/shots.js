const { chromium } = require('playwright');
const base = 'http://127.0.0.1:8857/botanical/index.html', out = '/home/claude/qa5/botanical/';
(async () => {
  const b = await chromium.launch(); const errs = [];
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  p.on('console', m => m.type() === 'error' && errs.push(m.text())); p.on('pageerror', e => errs.push(e.message));
  p.on('response', r => r.status() >= 400 && errs.push(r.status() + ' ' + r.url()));
  await p.goto(base, { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  await p.screenshot({ path: out + 'm-01-arrival.png' });
  await p.click('#seal'); await p.waitForTimeout(2600);
  await p.screenshot({ path: out + 'm-02-opened.png' });
  for (const id of ['story', 'invitation', 'details', 'moment', 'blessing']) {
    await p.evaluate(id => document.getElementById(id).scrollIntoView({ behavior: 'instant' }), id); await p.waitForTimeout(1300);
    await p.screenshot({ path: out + `m-${id}.png` });
    if (id === 'invitation') { await p.click('#unfoldBtn'); await p.waitForTimeout(1700); await p.screenshot({ path: out + 'm-invitation-open.png' }); }
  }
  console.log('errors', errs);
  await b.close();
})();
