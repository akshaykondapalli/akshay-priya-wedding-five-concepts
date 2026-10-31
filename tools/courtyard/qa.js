const { chromium } = require('playwright');
const URL = 'http://127.0.0.1:8741/courtyard/index.html', out = '/home/claude/qa5/courtyard';
(async () => {
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }); const R = {};
  const watch = (p, tag) => { R[tag] = []; p.on('console', m => m.type() === 'error' && R[tag].push(m.text())); p.on('pageerror', e => R[tag].push(e.message)); p.on('response', r => r.status() >= 400 && R[tag].push(r.status() + ' ' + r.url())); p.on('requestfailed', r => R[tag].push('FAIL ' + r.url())); };
  for (const [w, h, name, mobile] of [[412, 915, 'android', true], [820, 1180, 'tablet', true], [1440, 900, 'desktop', false]]) {
    const c = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: mobile ? 2 : 1, isMobile: mobile, hasTouch: mobile });
    const p = await c.newPage(); watch(p, name); await p.goto(URL, { waitUntil: 'networkidle' }); await p.waitForTimeout(700);
    await p.screenshot({ path: `${out}/first-${name}.png` });
    if (name !== 'android') { const H = await p.evaluate(() => { const w = document.querySelector('.walk'); return w.offsetTop + (w.offsetHeight - innerHeight) * 0.6; }); await p.evaluate(y => scrollTo(0, y), H); await p.waitForTimeout(700); await p.screenshot({ path: `${out}/walk60-${name}.png` }); }
    await c.close();
  }
  // 360 overflow + menu + music + share + links
  const c = await b.newContext({ viewport: { width: 360, height: 740 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await c.newPage(); watch(p, 'w360'); await p.goto(URL, { waitUntil: 'networkidle' });
  const ov = []; for (const f of [0, .3, .6, .9, 1]) { await p.evaluate(f => scrollTo(0, (document.documentElement.scrollHeight - innerHeight) * f), f); await p.waitForTimeout(250); ov.push(await p.evaluate(() => document.documentElement.scrollWidth - innerWidth)); }
  R.overflow360 = ov;
  await p.evaluate(() => scrollTo(0, 0));
  await p.click('[data-menu-open]'); R.menuOpen = await p.isVisible('#menu'); await p.keyboard.press('Escape'); R.menuClosedEsc = !(await p.isVisible('#menu'));
  await p.click('[data-music]'); await p.waitForTimeout(1500); R.musicPressed = await p.getAttribute('[data-music]', 'aria-pressed'); R.audioState = await p.evaluate(() => 'ok');
  await p.click('[data-music]'); R.musicAfter = await p.getAttribute('[data-music]', 'aria-pressed');
  R.links = await p.evaluate(() => [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter((v, i, s) => s.indexOf(v) === i));
  const txt = await p.evaluate(() => document.documentElement.outerHTML);
  R.forbidden = (txt.match(/pellikoduku|lunch|morning|reception|haldi|sangeet|mehendi/gi) || []);
  R.facts = ['Akshay', 'Priya', 'Saturday, 21 November 2026', '8:00 PM', '9:55 PM', 'Priyanka Convention', 'Nallajerla, Andhra Pradesh, India'].map(f => [f, txt.includes(f)]);
  R.chapters = await p.evaluate(() => [...document.querySelectorAll('[data-chapter]')].map(e => e.dataset.chapter));
  await c.close();
  // reduced motion
  const rc = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, reducedMotion: 'reduce', isMobile: true });
  const rp = await rc.newPage(); watch(rp, 'reduced'); await rp.goto(URL, { waitUntil: 'networkidle' });
  for (const f of [0.15, 0.5, 0.9]) { const H = await rp.evaluate(f => { const w = document.querySelector('.walk'); return w.offsetTop + (w.offsetHeight - innerHeight) * f; }, f); await rp.evaluate(y => scrollTo(0, y), H); await rp.waitForTimeout(400); await rp.screenshot({ path: `${out}/reduced-${String(f).replace('.', '')}.png` }); }
  R.reducedTransform = await rp.evaluate(() => getComputedStyle(document.querySelector('.lc')).transform);
  await rc.close();
  // no-JS
  const nc = await b.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false });
  const np = await nc.newPage(); await np.goto(URL, { waitUntil: 'networkidle' });
  await np.screenshot({ path: `${out}/nojs-first.png` });
  R.nojsInviteVisible = await np.isVisible('#invitation .inv-names');
  await nc.close(); await b.close();
  console.log(JSON.stringify(R, null, 1));
})();
