const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  const F = 'file:///home/claude/site5/courtyard/fonts/';
  const html = (`<html><head><meta charset="utf-8"><style>
  @font-face{font-family:M;src:url(${F}marcellus-latin-400-normal.woff2)}@font-face{font-family:A;src:url(${F}alegreya-latin-400-italic.woff2)}
  @font-face{font-family:T;src:url(${F}ramabhadra-telugu-400-normal.woff2)}
  body{margin:0;width:1200px;height:630px;overflow:hidden;background:#1d0f08}
  .bg{position:absolute;left:420px;top:-60px;width:960px;height:720px;background:url(file:///home/claude/tools5/courtyard/render/composite-closed.jpg) 50% 40%/960px auto}
  .door{position:absolute;inset:0;background:url(file:///home/claude/tools5/courtyard/render/layer-a.png) 50% 46%/1500px auto}
  .shade{position:absolute;inset:0;background:linear-gradient(90deg,#1d0f08 0,#1d0f08 36%,#1d0f08c0 46%,#1d0f0800 60%)}
  .t{position:absolute;left:70px;top:150px;color:#f1e7d0;width:520px}
  .te{font:30px T;color:#e3a62a;margin:0 0 10px}.h{font:62px/1.04 M;margin:0;letter-spacing:.02em}
  .n{font:38px A;color:#ecc77e;margin:22px 0 6px}.d{font:20px M;letter-spacing:.2em;text-transform:uppercase;color:#f1e7d0cc;margin:0}
  </style></head><body><div class="bg"></div><div class="shade"></div>
  <div class="t"><p class="te">శుభ వివాహం</p><h1 class="h">The Courtyard<br>of Blessings</h1><p class="n">Akshay &amp; Priya</p><p class="d">21 November 2026 · Nallajerla</p></div></body></html>`);
  require('fs').writeFileSync('/home/claude/tools5/courtyard/render/og.html', html); await p.goto('file:///home/claude/tools5/courtyard/render/og.html', { waitUntil: 'load' });
  await p.waitForTimeout(800);
  await p.screenshot({ path: '/home/claude/site5/courtyard/og.jpg', type: 'jpeg', quality: 82 });
  await b.close();
})();
