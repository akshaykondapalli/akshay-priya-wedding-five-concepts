// Builds og.jpg (1200x630) from the live scene, plus a mid-door-swing check frame.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.goto('http://127.0.0.1:8851/site5/temple/index.html', { waitUntil: 'networkidle' });
  const H = await p.evaluate(() => { const e = document.getElementById('pilgrimage'); return { top: e.offsetTop, h: e.offsetHeight, vh: innerHeight }; });
  await p.evaluate(y => window.scrollTo(0, y), H.top + (H.h - H.vh) * 0.1); await p.waitForTimeout(1500);
  await p.addStyleTag({ content: '.topbar,.beats,.skip-link{visibility:hidden!important}.og{position:fixed;left:0;right:0;top:30px;text-align:center;z-index:99;color:#fff3dd;font-family:Cinzel,serif;text-shadow:0 2px 20px rgba(10,5,20,.9)}.og h1{margin:0;font-weight:400;font-size:58px;letter-spacing:.04em}.og p{margin:8px 0 0;font-size:17px;letter-spacing:.28em;text-transform:uppercase;color:#f6dc95}' });
  await p.evaluate(() => { const d = document.createElement('div'); d.className = 'og'; d.innerHTML = '<h1>Akshay &amp; Priya</h1><p>Saturday · 21 November 2026 · Nallajerla</p>'; document.body.appendChild(d); });
  await p.waitForTimeout(500);
  await p.screenshot({ path: '/home/claude/site5/temple/og.jpg', type: 'jpeg', quality: 80 });
  // door mid-swing
  const q = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await q.goto('http://127.0.0.1:8851/site5/temple/index.html', { waitUntil: 'networkidle' });
  await q.evaluate(() => document.getElementById('invitation').scrollIntoView({ behavior: 'instant' }));
  await q.waitForTimeout(250);
  await q.screenshot({ path: '/home/claude/qa5/temple/door-closed.png' });
  await q.waitForTimeout(1050);
  await q.screenshot({ path: '/home/claude/qa5/temple/door-mid.png' });
  await b.close();
})();
