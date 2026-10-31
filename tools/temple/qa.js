// QA + screenshots for the temple concept. usage: node qa.js [baseURL]
const { chromium } = require('playwright'); const fs = require('fs');
const base = process.argv[2] || 'http://127.0.0.1:8851/site5/temple/index.html';
const OUT = '/home/claude/qa5/temple/';
const FORBIDDEN = /pellikoduku|lunch|morning|reception|haldi|sangeet|mehendi/i;
(async () => {
  const b = await chromium.launch();
  const rep = { errors: [], failed: [], checks: {} };
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  p.on('console', m => { if (m.type() === 'error') rep.errors.push(m.text()); });
  p.on('pageerror', e => rep.errors.push('pageerror ' + e.message));
  p.on('requestfailed', r => rep.failed.push(r.url()));
  p.on('response', r => { if (r.status() >= 400) rep.failed.push(r.status() + ' ' + r.url()); });
  await p.goto(base, { waitUntil: 'networkidle' }); await p.waitForTimeout(1200);
  await p.screenshot({ path: OUT + 'm-01-arrival.png' });
  // walk the pilgrimage at several progress points
  const H = await p.evaluate(() => { const e = document.getElementById('pilgrimage'); return { top: e.offsetTop, h: e.offsetHeight, vh: innerHeight }; });
  const pts = [0.18, 0.4, 0.62, 0.85, 1.0];
  for (let i = 0; i < pts.length; i++) {
    await p.evaluate(y => window.scrollTo(0, y), H.top + (H.h - H.vh) * pts[i]);
    await p.waitForTimeout(1300);
    await p.screenshot({ path: OUT + `m-02-walk-${Math.round(pts[i] * 100)}.png` });
  }
  for (const id of ['invitation', 'details', 'blessing']) {
    await p.evaluate(id => document.getElementById(id).scrollIntoView({ behavior: 'instant' }), id);
    await p.waitForTimeout(id === 'invitation' ? 3400 : 900);
    await p.screenshot({ path: OUT + `m-03-${id}.png` });
  }
  await p.evaluate(() => document.getElementById('details').scrollIntoView({ behavior: 'instant' }));
  await p.evaluate(() => window.scrollBy(0, 560)); await p.waitForTimeout(400);
  await p.screenshot({ path: OUT + 'm-04-details-2.png' });
  await p.evaluate(() => document.getElementById('blessing').scrollIntoView({ behavior: 'instant' }));
  await p.evaluate(() => window.scrollBy(0, 600)); await p.waitForTimeout(400);
  await p.screenshot({ path: OUT + 'm-04-blessing-2.png' });
  const txt = await p.evaluate(() => document.body.innerText);
  rep.checks.forbidden = (txt.match(FORBIDDEN) || [null])[0];
  for (const f of ['Akshay', 'Priya', 'Saturday, 21 November 2026', '8:00 PM IST', '9:55 PM IST', 'Priyanka Convention', 'Nallajerla, Andhra Pradesh, India']) rep.checks['has: ' + f] = txt.includes(f);
  rep.checks.chapters = await p.evaluate(() => [...document.querySelectorAll('[data-chapter]')].map(e => e.dataset.chapter));
  rep.checks.backHref = await p.evaluate(() => document.querySelector('.back').getAttribute('href'));
  // menu
  await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(300);
  await p.click('#menuBtn'); await p.waitForTimeout(300);
  rep.checks.menuOpens = await p.evaluate(() => !document.getElementById('menu').hidden);
  await p.screenshot({ path: OUT + 'm-05-menu.png' });
  await p.keyboard.press('Escape'); rep.checks.menuEscCloses = await p.evaluate(() => document.getElementById('menu').hidden);
  // music toggle
  await p.click('#musicBtn'); await p.waitForTimeout(500);
  rep.checks.musicOn = await p.evaluate(() => document.getElementById('musicBtn').getAttribute('aria-pressed'));
  await p.click('#musicBtn'); rep.checks.musicOff = await p.evaluate(() => document.getElementById('musicBtn').getAttribute('aria-pressed'));
  // links
  rep.checks.links = await p.evaluate(() => [...document.querySelectorAll('a[href^="http"]')].map(a => a.href));
  // ics
  const [dl] = await Promise.all([p.waitForEvent('download', { timeout: 5000 }).catch(() => null), p.evaluate(() => document.getElementById('icsBtn').click())]);
  if (dl) { const path = OUT + 'test.ics'; await dl.saveAs(path); rep.checks.ics = fs.readFileSync(path, 'utf8').split('\r\n').filter(l => /DTSTART|DTEND|SUMMARY|LOCATION/.test(l)); } else rep.checks.ics = 'no download';
  await ctx.close();
  // other viewports
  for (const [w, h, n] of [[412, 915, 'android'], [820, 1180, 'tablet'], [1440, 900, 'desktop'], [360, 740, 'small']]) {
    const c = await b.newContext({ viewport: { width: w, height: h } }); const q = await c.newPage();
    q.on('pageerror', e => rep.errors.push(n + ' pageerror ' + e.message));
    await q.goto(base, { waitUntil: 'networkidle' }); await q.waitForTimeout(900);
    await q.screenshot({ path: OUT + `v-${n}-arrival.png` });
    const H2 = await q.evaluate(() => { const e = document.getElementById('pilgrimage'); return { top: e.offsetTop, h: e.offsetHeight, vh: innerHeight }; });
    await q.evaluate(y => window.scrollTo(0, y), H2.top + (H2.h - H2.vh) * 0.7); await q.waitForTimeout(1200);
    await q.screenshot({ path: OUT + `v-${n}-walk70.png` });
    if (n === 'desktop') { for (const id of ['invitation', 'details', 'blessing']) { await q.evaluate(id => document.getElementById(id).scrollIntoView({ behavior: 'instant' }), id); await q.waitForTimeout(id === 'invitation' ? 3400 : 700); await q.screenshot({ path: OUT + `v-desktop-${id}.png` }); } }
    rep.checks['overflow-' + n] = await q.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    await c.close();
  }
  // reduced motion
  const rc = await b.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce', deviceScaleFactor: 1 });
  const r = await rc.newPage(); r.on('pageerror', e => rep.errors.push('reduced pageerror ' + e.message));
  await r.goto(base, { waitUntil: 'networkidle' }); await r.waitForTimeout(600);
  await r.screenshot({ path: OUT + 'r-arrival.png' });
  await r.evaluate(() => document.getElementById('invitation').scrollIntoView({ behavior: 'instant' })); await r.waitForTimeout(300);
  await r.screenshot({ path: OUT + 'r-invitation.png' });
  rep.checks.reducedDoorsOpen = await r.evaluate(() => document.getElementById('doors').classList.contains('open'));
  await rc.close();
  // no-JS
  const nc = await b.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false });
  const nj = await nc.newPage(); await nj.goto(base, { waitUntil: 'networkidle' });
  await nj.evaluate ? null : null;
  await nj.screenshot({ path: OUT + 'nojs-full.png', fullPage: true });
  await nc.close();
  await b.close();
  fs.writeFileSync(OUT + 'qa-report.json', JSON.stringify(rep, null, 2));
  console.log(JSON.stringify(rep, null, 2));
})();
