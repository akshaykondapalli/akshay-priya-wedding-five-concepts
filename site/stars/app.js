/* Nine Fifty-Five Under the Stars — sky, scroll choreography, dial, countdown, music, actions. */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = t => t * t * (3 - 2 * t);
  const mqReduce = matchMedia('(prefers-reduced-motion: reduce)');
  let reduce = mqReduce.matches;
  mqReduce.addEventListener?.('change', e => { reduce = e.matches; layout(); requestDraw(); });

  /* ------------------------------------------------------------ state */
  const root = document.documentElement;
  const S = { p: 0, minutes: 0, t: 0, sink: 0, w: 0, h: 0, dpr: 1 };
  const secs = {};
  function layout() {
    ['story', 'hour', 'invitation', 'details', 'blessing'].forEach(id => {
      const el = document.getElementById(id);
      secs[id] = { top: el.offsetTop, h: el.offsetHeight };
    });
  }

  /* ------------------------------------------------------------ sky */
  const cv = $('#sky');
  const ctx = cv.getContext('2d', { alpha: false });
  let stars = [], C = { x: 0, y: 0 }, milky = null, sprite = null;
  const milkyImg = new Image();
  milkyImg.decoding = 'async';
  milkyImg.src = 'img/milky.webp';
  milkyImg.onload = () => { milky = milkyImg; requestDraw(); };

  function rand(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

  function makeSprite() {
    const c = document.createElement('canvas'); c.width = c.height = 64;
    const g = c.getContext('2d');
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.12, 'rgba(255,255,255,.85)');
    gr.addColorStop(0.35, 'rgba(200,215,255,.18)');
    gr.addColorStop(1, 'rgba(200,215,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    return c;
  }

  function resize() {
    S.dpr = Math.min(window.devicePixelRatio || 1, S.w > 900 ? 1.5 : 2);
    S.w = window.innerWidth; S.h = window.innerHeight;
    cv.width = Math.round(S.w * S.dpr); cv.height = Math.round(S.h * S.dpr);
    ctx.setTransform(S.dpr, 0, 0, S.dpr, 0, 0);
    C = { x: S.w * 0.5, y: S.h * 1.35 };
    // stars live on a sector around a rotation centre below the horizon, so the field can turn without gaps
    const R = Math.hypot(S.w * 0.75, C.y) + 40, rmin = S.h * 0.3, span = 2.6;
    const visible = S.w * S.h, sector = 0.5 * span * (R * R - rmin * rmin);
    const N = Math.round(clamp(visible / 520, 650, 2300) * sector / visible);
    const r = rand(955);
    const lo = -1.4, hi = 6.5, k = 0.33 * Math.LN10;
    const cdfMax = Math.exp(k * (hi - lo)) - 1;
    stars = new Array(N);
    for (let i = 0; i < N; i++) {
      const rr = Math.sqrt(lerp(rmin * rmin, R * R, r()));
      const a = -Math.PI / 2 + (r() - 0.5) * span;
      const m = lo + Math.log(1 + r() * cdfMax) / k;             // more faint stars than bright, like the real sky
      const q = r();
      const col = q < 0.1 ? '205,218,255' : q < 0.7 ? '242,244,255' : q < 0.9 ? '255,241,218' : '255,216,176';
      const lum = (hi - m) / (hi - lo);
      stars[i] = { r: rr, a, m, col, size: 0.35 + 1.75 * Math.pow(lum, 1.9), base: 0.22 + 0.78 * lum, ph: r() * 6.283, f: 1.2 + r() * 2.6 };
    }
    stars.sort((x, y) => y.m - x.m);
    sprite = sprite || makeSprite();
    layout();
    requestDraw();
  }

  const DUSK = { top: [24, 33, 82], mid: [70, 62, 112], low: [196, 138, 128] };
  const NIGHT = { top: [3, 5, 14], mid: [9, 14, 44], low: [26, 32, 74] };
  const mix = (a, b, t) => a.map((v, i) => Math.round(lerp(v, b[i], t)));
  const rgb = c => `rgb(${c[0]},${c[1]},${c[2]})`;

  let tNow = 0;
  function draw(now) {
    tNow = now / 1000;
    const p = S.p, w = S.w, h = S.h;
    // sky gradient: dusk rose at the horizon fades into deep indigo
    const g = ctx.createLinearGradient(0, 0, 0, h);
    const e = smooth(p);
    g.addColorStop(0, rgb(mix(DUSK.top, NIGHT.top, e)));
    g.addColorStop(0.55, rgb(mix(DUSK.mid, NIGHT.mid, e)));
    g.addColorStop(1, rgb(mix(DUSK.low, NIGHT.low, Math.pow(e, 0.8))));
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);

    // the field turns with the evening: about 15° per hour, as the real sky does
    const drift = reduce ? 0 : tNow * 0.00035;
    const rot = (S.minutes / 60) * (15 * Math.PI / 180) + drift - 0.12;

    // milky band
    if (milky) {
      ctx.save();
      ctx.globalAlpha = clamp(Math.pow(p, 1.6) * 0.42);
      ctx.translate(C.x, C.y); ctx.rotate(rot);
      const s = Math.max(w, h) * 1.5;
      ctx.drawImage(milky, -s * 0.62, -C.y - s * 0.32, s, s);
      ctx.restore();
    }

    // stars
    const lim = 1.6 + 4.9 * p;
    const cr = Math.cos(rot), sr = Math.sin(rot);
    for (let i = 0; i < stars.length; i++) {
      const st = stars[i];
      if (st.m > lim + 0.8) continue;
      const ax = Math.cos(st.a), ay = Math.sin(st.a);
      const x = C.x + st.r * (ax * cr - ay * sr);
      const y = C.y + st.r * (ax * sr + ay * cr);
      if (x < -4 || x > w + 4 || y < -4 || y > h * 0.86) continue;
      let al = st.base * clamp((lim + 0.8 - st.m) / 1.4);
      if (!reduce && st.m < 3.6) {
        const low = 0.5 + 0.9 * (y / h);                       // stars twinkle more near the horizon
        al *= 1 + 0.16 * low * Math.sin(tNow * st.f + st.ph);
      }
      if (al <= 0.01) continue;
      if (st.size < 1) {
        ctx.globalAlpha = al * st.size;
        ctx.fillStyle = `rgb(${st.col})`;
        ctx.fillRect(x, y, 1, 1);
      } else {
        ctx.globalAlpha = clamp(al);
        ctx.fillStyle = `rgb(${st.col})`;
        ctx.beginPath(); ctx.arc(x, y, st.size * 0.62, 0, 6.283); ctx.fill();
        if (st.m < 1.8) {
          const s = 10 + (1.8 - st.m) * 7;
          ctx.globalAlpha = clamp(al * 0.55);
          ctx.drawImage(sprite, x - s / 2, y - s / 2, s, s);
        }
      }
    }
    ctx.globalAlpha = 1;
    // warm haze from the pandal lights rises as the evening deepens
    const hz = ctx.createRadialGradient(w * 0.5, h * 1.02, 0, w * 0.5, h * 1.02, Math.max(w * 0.7, h * 0.55));
    hz.addColorStop(0, `rgba(255,170,90,${0.10 + 0.14 * p})`);
    hz.addColorStop(1, 'rgba(255,170,90,0)');
    ctx.fillStyle = hz; ctx.fillRect(0, 0, w, h);
  }

  let rafId = 0, lastFrame = 0, running = true;
  function loop(now) {
    rafId = 0;
    if (!running) return;
    if (now - lastFrame > 32) { lastFrame = now; draw(now); }
    if (!reduce) rafId = requestAnimationFrame(loop);
  }
  function requestDraw() { if (!rafId) rafId = requestAnimationFrame(loop); }
  document.addEventListener('visibilitychange', () => {
    running = !document.hidden;
    if (running) requestDraw();
  });

  /* ------------------------------------------------------------ dial */
  const ticks = $('#ticks'), dialStars = $('#dialStars');
  const NS = 'http://www.w3.org/2000/svg';
  for (let i = 0; i < 60; i++) {
    const a = i * 6 * Math.PI / 180, major = i % 5 === 0;
    const r1 = major ? 128 : 134, r2 = 141;
    const l = document.createElementNS(NS, 'line');
    l.setAttribute('x1', 160 + r1 * Math.sin(a)); l.setAttribute('y1', 160 - r1 * Math.cos(a));
    l.setAttribute('x2', 160 + r2 * Math.sin(a)); l.setAttribute('y2', 160 - r2 * Math.cos(a));
    l.setAttribute('class', 'tick' + (major ? ' major' : ''));
    l.setAttribute('stroke-width', major ? 1.4 : 0.7);
    ticks.appendChild(l);
  }
  { const r = rand(2155);
    for (let i = 0; i < 46; i++) {
      const rr = Math.sqrt(r()) * 112, a = r() * 6.283;
      const c = document.createElementNS(NS, 'circle');
      c.setAttribute('cx', 160 + rr * Math.cos(a)); c.setAttribute('cy', 160 + rr * Math.sin(a));
      c.setAttribute('r', (0.3 + Math.pow(r(), 3) * 1.3).toFixed(2));
      c.setAttribute('class', 'ds'); c.setAttribute('opacity', (0.25 + r() * 0.6).toFixed(2));
      dialStars.appendChild(c);
    } }
  const hHand = $('#hHand'), mHand = $('#mHand'), arc = $('#arc'), dialTime = $('#dialTime');
  const steps = [...document.querySelectorAll('.hour-steps li')];
  const chipT = $('#eveningTime'), chipL = $('#eveningLabel');
  function polar(deg, r) { const a = deg * Math.PI / 180; return [160 + r * Math.sin(a), 160 - r * Math.cos(a)]; }
  function fmt(mins) { const tot = 8 * 60 + Math.round(mins); const h = Math.floor(tot / 60), m = tot % 60; return `${h > 12 ? h - 12 : h}:${String(m).padStart(2, '0')}`; }
  let lastMin = -1;
  function setDial(mins) {
    const mm = Math.round(mins);
    if (mm === lastMin) return; lastMin = mm;
    const hDeg = (8 + mm / 60) * 30, mDeg = (mm % 60) * 6;
    hHand.setAttribute('transform', `rotate(${hDeg} 160 160)`);
    mHand.setAttribute('transform', `rotate(${mDeg} 160 160)`);
    const [x0, y0] = polar(240, 148), [x1, y1] = polar(hDeg, 148);
    arc.setAttribute('d', mm < 1 ? '' : `M${x0.toFixed(2)} ${y0.toFixed(2)} A148 148 0 0 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`);
    const t = fmt(mm);
    dialTime.textContent = t;
    chipT.textContent = t + ' PM';
    const idx = mm < 38 ? 0 : mm < 108 ? 1 : 2;
    steps.forEach((li, i) => li.classList.toggle('on', i === idx));
    chipL.textContent = mm < 38 ? 'Dinner' : mm < 108 ? 'Night' : 'Muhurtham';
  }

  /* ------------------------------------------------------------ scroll */
  const story = $('#story'), arch = $('.arch');
  function onScroll() {
    const y = window.scrollY, vh = S.h || innerHeight;
    const st = secs.story, hr = secs.hour, inv = secs.invitation, bl = secs.blessing;
    if (!st) return;
    // dusk deepens through the first two chapters, then the hour carries it to full night
    const pre = clamp(y / Math.max(1, hr.top));
    const t = reduce ? 1 : clamp((y - hr.top) / Math.max(1, hr.h - vh));
    S.t = t;
    S.minutes = y < hr.top && !reduce ? 0 : 115 * smooth(t);
    S.p = reduce ? clamp(0.35 + 0.65 * (y >= hr.top ? 1 : pre)) : clamp(0.35 * pre + 0.65 * t);
    setDial(S.minutes);
    // constellation lines draw as the story chapter comes in
    const s = clamp((y - (st.top - vh * 0.7)) / (vh * 0.95));
    story.style.setProperty('--draw', reduce ? 0 : (1 - clamp(s * 1.5)).toFixed(3));
    story.style.setProperty('--draw2', reduce ? 0 : (1 - clamp((s - 0.55) * 2.6)).toFixed(3));
    story.style.setProperty('--glowS', (1 + 0.7 * clamp((s - 0.9) * 10)).toFixed(3));
    // horizon sinks behind the invitation and details, then rises for the blessing
    const a = clamp((y - (inv.top - vh * 0.85)) / (vh * 0.6));
    const b = clamp((y - (bl.top - vh * 0.95)) / (vh * 0.7));
    // during the hour the horizon settles lower so the dial and countdown stay clear
    const inHour = clamp((y - (hr.top - vh * 0.6)) / (vh * 0.6));
    const sink = Math.max(smooth(a) * (1 - smooth(b)), (S.w > 700 ? 0.5 : 0.34) * smooth(inHour) * (1 - smooth(a)));
    root.style.setProperty('--hz', (sink * 58).toFixed(2) + '%');
    root.classList.toggle('past-arrival', y > vh * 0.6);
    root.style.setProperty('--lights', (0.38 + 0.62 * S.p).toFixed(3));
    if (reduce) requestDraw();
  }
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => { ticking = false; onScroll(); if (reduce) requestDraw(); });
  }, { passive: true });
  window.addEventListener('resize', () => { resize(); onScroll(); });
  window.addEventListener('load', () => { layout(); onScroll(); });

  if ('IntersectionObserver' in window && arch) {
    new IntersectionObserver((es, o) => es.forEach(en => { if (en.isIntersecting) { arch.classList.add('in'); o.disconnect(); } }), { threshold: 0.3 }).observe(arch);
  }

  /* ------------------------------------------------------------ countdown */
  const TARGET = Date.UTC(2026, 10, 21, 16, 25, 0);      // 9:55 PM IST = 16:25 UTC
  const cd = { d: $('#cd-d'), h: $('#cd-h'), m: $('#cd-m'), s: $('#cd-s') };
  function tickCountdown() {
    let diff = Math.floor((TARGET - Date.now()) / 1000);
    if (diff <= 0) {
      $('#countdown').hidden = true;
      $('#cdNote').textContent = 'The muhurtham was at 9:55 PM IST on 21 November 2026. Thank you for your blessings.';
      return false;
    }
    const d = Math.floor(diff / 86400); diff -= d * 86400;
    const h = Math.floor(diff / 3600); diff -= h * 3600;
    const m = Math.floor(diff / 60); const s = diff - m * 60;
    cd.d.textContent = d; cd.h.textContent = String(h).padStart(2, '0');
    cd.m.textContent = String(m).padStart(2, '0'); cd.s.textContent = String(s).padStart(2, '0');
    return true;
  }
  if (tickCountdown()) setInterval(tickCountdown, 1000);

  /* ------------------------------------------------------------ menu */
  const menu = $('#menu');
  $('#menuBtn').addEventListener('click', () => { menu.showModal ? menu.showModal() : menu.setAttribute('open', ''); });
  $('#menuClose').addEventListener('click', () => menu.close());
  menu.addEventListener('click', e => {
    if (e.target === menu) menu.close();
    const a = e.target.closest('a[href^="#"]');
    if (a) { e.preventDefault(); menu.close(); const t = document.querySelector(a.getAttribute('href')); t && t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' }); history.replaceState(null, '', a.getAttribute('href')); }
  });

  /* ------------------------------------------------------------ calendar + share */
  $('#ics').addEventListener('click', () => {
    const ics = [
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Akshay and Priya//Nine Fifty-Five//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
      'BEGIN:VEVENT',
      'UID:akshay-priya-wedding-20261121@nine-fifty-five',
      'DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, ''),
      'DTSTART:20261121T143000Z', 'DTEND:20261121T143000Z',
      'SUMMARY:Wedding of Akshay & Priya',
      'DESCRIPTION:Wedding dinner 8:00 PM IST · Muhurtham 9:55 PM IST',
      'LOCATION:Priyanka Convention\\, Nallajerla\\, Andhra Pradesh\\, India',
      'END:VEVENT', 'END:VCALENDAR'
    ].join('\r\n');
    const url = URL.createObjectURL(new Blob([ics], { type: 'text/calendar;charset=utf-8' }));
    const a = Object.assign(document.createElement('a'), { href: url, download: 'akshay-priya-wedding.ics' });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
  });
  const msg = $('#shareMsg');
  $('#share').addEventListener('click', async () => {
    const data = { title: 'Akshay & Priya · 21 November 2026', text: 'Wedding of Akshay & Priya · Saturday, 21 November 2026 · Priyanka Convention, Nallajerla', url: 'https://akshaykondapalli.github.io/akshay-priya-wedding-five-concepts/stars/'};
    if (navigator.share) { try { await navigator.share(data); return; } catch (e) { if (e && e.name === 'AbortError') return; } }
    try { await navigator.clipboard.writeText(data.url); msg.textContent = 'Link copied.'; }
    catch (_) { msg.textContent = 'Copy this link: ' + data.url; }
  });

  /* ------------------------------------------------------------ music: the couple's selected recording */
  // One persistent <audio> element for the whole invitation: off until the guest taps, pause/resume, loop, 40% volume.
  const audio = $('#bgm'), mbtn = $('#musicBtn');
  audio.loop = true; audio.volume = 0.4;
  function setMusicUI(playing) {
    mbtn.setAttribute('aria-pressed', String(playing));
    mbtn.setAttribute('aria-label', playing ? 'Pause music' : 'Play music');
    $('.music-label', mbtn).textContent = playing ? 'Pause Music' : 'Play Music';
  }
  mbtn.addEventListener('click', () => {
    if (audio.paused) { audio.volume = 0.4; const pr = audio.play(); if (pr && pr.catch) pr.catch(() => setMusicUI(!audio.paused)); }
    else audio.pause();
  });
  audio.addEventListener('play', () => setMusicUI(true));
  audio.addEventListener('pause', () => setMusicUI(false));
  audio.addEventListener('error', () => setMusicUI(false));
  document.addEventListener('visibilitychange', () => { if (!document.hidden) setMusicUI(!audio.paused); });
  setMusicUI(false);

  /* music button placement: bottom-right; becomes a compact circle, then lifts, so it never covers
     a control, the dial, the countdown or wedding text */
  function protectedRects() {
    const vh = innerHeight, zoneTop = vh - 260, rects = [];
    const push = r => { if (r.width > 0 && r.height > 0 && r.bottom > zoneTop && r.top < vh) rects.push(r); };
    document.querySelectorAll('main a, main button, .bar a, .bar button, #countdown, .dial, svg[role="img"]:not([aria-labelledby="cst-t"])').forEach(el => {
      if (el.closest('dialog:not([open])')) return; const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity < .1) return; push(el.getBoundingClientRect());
    });
    const walker = document.createTreeWalker(document.querySelector('main') || document.body, NodeFilter.SHOW_TEXT);
    const rg = document.createRange();
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      if (!n.textContent.trim()) continue; const el = n.parentElement; if (!el) continue;
      const er = el.getBoundingClientRect(); if (er.bottom < zoneTop || er.top > vh) continue;
      const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || +cs.opacity < .1) continue;
      rg.selectNodeContents(n); for (const r of rg.getClientRects()) push(r);
    }
    return rects;
  }
  let fabRaf = 0;
  function placeFab() {
    fabRaf = 0; const f = mbtn, vh = innerHeight, obs = protectedRects();
    const hit = () => { const r = f.getBoundingClientRect(), pad = 6; return obs.some(o => r.left < o.right + pad && r.right > o.left - pad && r.top < o.bottom + pad && r.bottom > o.top - pad); };
    const set = (compact, bottom) => { f.classList.toggle('compact', compact); f.style.bottom = `calc(${bottom}px + env(safe-area-inset-bottom, 0px))`; };
    set(false, 12); if (!hit()) return;
    set(true, 12); if (!hit()) return;
    const fr = f.getBoundingClientRect();
    const col = obs.filter(o => o.right > fr.left - 6 && o.left < fr.right + 6).sort((a, b) => b.top - a.top);
    let bottom = 12;
    for (const o of col) { const r = f.getBoundingClientRect(); if (r.top < o.bottom + 6 && r.bottom > o.top - 6) { bottom = vh - o.top + 8; set(true, bottom); } }
    if (bottom > vh * 0.45) set(true, 12);     // never float into the middle of the screen
  }
  const queueFab = () => { if (!fabRaf) fabRaf = requestAnimationFrame(placeFab); };
  addEventListener('scroll', queueFab, { passive: true }); addEventListener('resize', queueFab);
  document.fonts && document.fonts.ready.then(queueFab); queueFab();

  /* ------------------------------------------------------------ capture hook + boot */
  window.atlasReveal = () => { arch && arch.classList.add('in'); layout(); onScroll(); requestDraw(); };
  resize();
  onScroll();
  requestDraw();
})();
