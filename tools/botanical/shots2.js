const { chromium } = require('playwright');
const base = 'http://127.0.0.1:8857/botanical/index.html', out = '/home/claude/qa5/botanical/';
(async () => {
  const b = await chromium.launch(); const errs = [];
  const watch = p => { p.on('console', m => m.type() === 'error' && errs.push(m.text())); p.on('pageerror', e => errs.push(e.message)); p.on('response', r => r.status() >= 400 && errs.push(r.status() + ' ' + r.url())); };
  // opened envelope + mid unfold on phone
  let ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }); let p = await ctx.newPage(); watch(p);
  await p.goto(base, { waitUntil: 'networkidle' }); await p.click('#openBtn'); await p.waitForTimeout(3600); await p.screenshot({ path: out + 'm-02-opened.png' });
  await p.evaluate(() => document.getElementById('invitation').scrollIntoView({ behavior: 'instant' })); await p.waitForTimeout(800);
  await p.click('#unfoldBtn'); await p.waitForTimeout(550); await p.screenshot({ path: out + 'm-invitation-mid.png' });
  await ctx.close();
  // other viewports
  for (const [w, h, n, mob] of [[412, 915, 'android', true], [820, 1180, 'tablet', true], [1440, 900, 'desktop', false]]) {
    ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: mob ? 2 : 1, isMobile: mob, hasTouch: mob }); p = await ctx.newPage(); watch(p);
    await p.goto(base, { waitUntil: 'networkidle' }); await p.waitForTimeout(600); await p.screenshot({ path: out + `v-${n}.png` });
    if (n === 'desktop') { await p.evaluate(() => { atlasReveal(); document.getElementById('invitation').scrollIntoView({ behavior: 'instant' }); }); await p.waitForTimeout(1600); await p.screenshot({ path: out + 'v-desktop-invitation.png' }); }
    await ctx.close();
  }
  // overflow at 360 + reduced motion + no-js
  ctx = await b.newContext({ viewport: { width: 360, height: 740 }, reducedMotion: 'reduce' }); p = await ctx.newPage(); watch(p);
  await p.goto(base, { waitUntil: 'networkidle' });
  const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await p.click('#openBtn'); await p.waitForTimeout(300); await p.screenshot({ path: out + 'rm-opened.png' });
  const ov2 = await p.evaluate(() => { atlasReveal(); return document.documentElement.scrollWidth - innerWidth; });
  await ctx.close();
  ctx = await b.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false }); p = await ctx.newPage();
  await p.goto(base, { waitUntil: 'networkidle' }); await p.evaluate(() => 0).catch(() => 0);
  await p.screenshot({ path: out + 'nojs-full.png', fullPage: true });
  await ctx.close();
  console.log({ overflow360: ov, overflow360revealed: ov2, errs });
  await b.close();
})();
