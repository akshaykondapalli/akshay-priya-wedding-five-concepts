/* The Courtyard of Blessings — walk-in, lamps, captions, actions and original Web Audio music */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const FLAMES = [["niche",700,993,0.5],["niche",1700,993,0.5],["kundulu",874,1037,1],["kundulu",900,1037,1],["kundulu",960,1037,1],["kundulu",986,1037,1],["kundulu",1414,1037,1],["kundulu",1440,1037,1],["kundulu",1500,1037,1],["kundulu",1526,1037,1],["kota",1200,1520,0.55],["courtyard",1000,1679,0.65],["courtyard",1090,1707,0.65],["courtyard",1310,1707,0.65],["courtyard",1400,1679,0.65],["courtyard",1200,1739,0.65],["door",600,874,0.62],["door",640,874,0.62],["door",680,874,0.62],["door",1720,874,0.62],["door",1760,874,0.62],["door",1800,874,0.62],["door",870,1726,0.62],["door",1530,1726,0.62]];
  const STRANDS = [[880,250,203],[968,250,188],[1053,250,210],[1123,250,181],[1190,250,216],[1284,250,151],[1361,250,219],[1443,250,172],[1520,250,257]];

  /* ---- build flames and strands ---- */
  const groups = {};
  $$('.flames').forEach(box => {
    const want = box.dataset.groups.split(' ');
    FLAMES.filter(f => want.includes(f[0])).forEach(([id, x, y, s], i) => {
      const el = document.createElement('span');
      el.className = 'flame'; el.style.cssText = `--x:${x};--y:${y};--s:${s};--d:${(-Math.random() * 1.8).toFixed(2)}s`;
      box.appendChild(el); (groups[id] = groups[id] || []).push(el);
    });
  });
  (groups.door || []).forEach(f => f.classList.add('lit'));
  const strandBox = $('.strands');
  STRANDS.forEach(([x, y, len]) => {
    const im = new Image(); im.src = 'img/strand.webp'; im.alt = ''; im.className = 'strand'; im.decoding = 'async';
    im.style.cssText = `--x:${x - 20};--y:${y};--len:${len};--d:${(-Math.random() * 5).toFixed(2)}s`;
    strandBox.appendChild(im);
  });
  const scene = $('.scene');
  const setUnit = () => { const cw = innerWidth / innerHeight >= 2 / 3 ? 2400 : 1200; scene.style.setProperty('--u', (scene.offsetWidth / cw).toFixed(4)); };
  setUnit(); addEventListener('resize', setUnit);

  /* ---- walk-in ---- */
  const walk = $('.walk'), la = $('.la'), laL = $('.la-light'), lb = $('.lb'), lc = $('.lc');
  const dl = $('.door-l'), dr = $('.door-r');
  const lights = { court: $('.light-court'), hall: $('.light-hall') };
  const bloom = $('.bloom');
  const caps = $$('.cap').map(el => ({ el, from: +el.dataset.from, to: +el.dataset.to }));
  const courtFl = [...(groups.kota || []), ...(groups.courtyard || [])];
  const hallFl = [...(groups.kundulu || []), ...(groups.niche || [])];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const ease = t => t * t * (3 - 2 * t);
  const span = (p, a, b) => ease(clamp((p - a) / (b - a)));

  function progress() {
    const r = walk.getBoundingClientRect(), range = walk.offsetHeight - innerHeight;
    return range > 0 ? clamp(-r.top / range) : 0;
  }
  function render() {
    const p = progress(), still = reduce.matches;
    const dOpen = span(p, 0.02, 0.17);
    if (still) {
      dl.style.transform = dr.style.transform = '';
      la.style.transform = lb.style.transform = lc.style.transform = '';
      la.style.opacity = 1 - span(p, 0.13, 0.17);
      lb.style.opacity = 1 - span(p, 0.64, 0.68);
    } else {
      dl.style.transform = `rotateY(${dOpen * 100}deg)`;
      dr.style.transform = `rotateY(${-dOpen * 100}deg)`;
      la.style.transform = `scale(${1 + 1.9 * span(p, 0.08, 0.40)})`;
      la.style.opacity = 1 - span(p, 0.30, 0.40);
      lb.style.transform = `scale(${1 + 0.95 * span(p, 0.12, 0.76)})`;
      lb.style.opacity = 1 - span(p, 0.68, 0.80);
      lc.style.transform = `scale(${1 + 0.9 * span(p, 0.14, 0.97)})`;
    }
    laL.style.transform = la.style.transform; laL.style.opacity = la.style.opacity;
    la.style.visibility = laL.style.visibility = +la.style.opacity <= 0.001 ? 'hidden' : '';
    lb.style.visibility = +lb.style.opacity <= 0.001 ? 'hidden' : '';
    let litC = 0, litH = 0;
    courtFl.forEach((f, i) => { const on = still ? p > 0.25 : p > 0.30 + i * 0.035; f.classList.toggle('lit', on); litC += on; });
    hallFl.forEach((f, i) => { const on = still ? p > 0.55 : p > 0.60 + i * 0.022; f.classList.toggle('lit', on); litH += on; });
    lights.court.style.opacity = (litC / courtFl.length).toFixed(3);
    lights.hall.style.opacity = (litH / hallFl.length).toFixed(3);
    bloom.style.opacity = (0.1 + 0.12 * (litC / courtFl.length) + 0.12 * (litH / hallFl.length)).toFixed(3);
    caps.forEach(c => {
      const fade = 0.04;
      const o = c.from === 0 ? 1 - span(p, c.to - fade, c.to) : c.to > 1 ? span(p, c.from, c.from + fade) : Math.min(span(p, c.from, c.from + fade), 1 - span(p, c.to - fade, c.to));
      c.el.style.opacity = o.toFixed(3);
      c.el.style.transform = still ? '' : `translateY(${((1 - o) * 14).toFixed(1)}px)`;
      c.el.classList.toggle('on', o > 0.01);
    });
  }
  let ticking = false;
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { ticking = false; render(); }); } };
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);
  reduce.addEventListener?.('change', render);
  render();

  // "Open the doors" glides you into the courtyard
  $('[data-walk]')?.addEventListener('click', () => {
    const range = walk.offsetHeight - innerHeight;
    scrollTo({ top: walk.offsetTop + range * 0.5, behavior: reduce.matches ? 'auto' : 'smooth' });
  });

  window.atlasReveal = () => { render(); };

  /* ---- menu ---- */
  const menu = $('#menu'), openBtn = $('[data-menu-open]');
  const closeMenu = (focus = true) => { menu.hidden = true; openBtn.setAttribute('aria-expanded', 'false'); if (focus) openBtn.focus(); };
  openBtn.addEventListener('click', () => { menu.hidden = false; openBtn.setAttribute('aria-expanded', 'true'); $('a', menu).focus(); });
  $('[data-menu-close]').addEventListener('click', () => closeMenu());
  menu.addEventListener('click', e => { if (e.target.closest('a')) closeMenu(false); });
  addEventListener('keydown', e => { if (e.key === 'Escape' && !menu.hidden) closeMenu(); });

  /* ---- countdown ---- */
  const cd = $('[data-countdown]');
  if (cd) {
    const target = new Date(cd.dataset.countdown).getTime();
    const u = k => $(`[data-u="${k}"]`, cd);
    const tick = () => {
      let s = Math.max(0, Math.floor((target - Date.now()) / 1000));
      const d = Math.floor(s / 86400); s -= d * 86400; const h = Math.floor(s / 3600); s -= h * 3600; const m = Math.floor(s / 60); s -= m * 60;
      u('d').textContent = d; u('h').textContent = String(h).padStart(2, '0'); u('m').textContent = String(m).padStart(2, '0'); u('s').textContent = String(s).padStart(2, '0');
    };
    tick(); setInterval(tick, 1000);
  }

  /* ---- share / calendar ---- */
  const status = $('.status');
  const say = t => { if (status) { status.textContent = t; clearTimeout(say.t); say.t = setTimeout(() => status.textContent = '', 4000); } };
  $$('[data-share]').forEach(b => b.addEventListener('click', async () => {
    const data = { title: 'Akshay & Priya · Wedding invitation', text: 'Saturday, 21 November 2026 · Priyanka Convention, Nallajerla', url: location.href.split('#')[0] };
    if (navigator.share) { try { await navigator.share(data); return; } catch (e) { if (e.name === 'AbortError') return; } }
    try { await navigator.clipboard.writeText(data.url); b.dataset.label = b.dataset.label || b.textContent; b.textContent = 'Link copied'; setTimeout(() => b.textContent = b.dataset.label, 2200); say('Link copied to your clipboard.'); }
    catch (_) { say('Copy this link: ' + data.url); }
  }));
  $('[data-ics]')?.addEventListener('click', () => {
    // 8:00 PM–11:00 PM IST expressed in UTC; end time is a placeholder to confirm
    const ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Akshay & Priya//Wedding//EN', 'CALSCALE:GREGORIAN', 'BEGIN:VEVENT',
      'UID:akshay-priya-wedding-20261121@invite', 'DTSTAMP:20261031T000000Z', 'DTSTART:20261121T143000Z', 'DTEND:20261121T173000Z',
      'SUMMARY:Wedding of Akshay & Priya', 'DESCRIPTION:Wedding dinner 8:00 PM IST\\nMuhurtham 9:55 PM IST',
      'LOCATION:Priyanka Convention\\, Nallajerla\\, Andhra Pradesh\\, India', 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    const url = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' }));
    const a = Object.assign(document.createElement('a'), { href: url, download: 'akshay-priya-wedding.ics' });
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
    say('Calendar file downloaded.');
  });

  /* ---- original music, synthesised live (off by default) ----
     A tanpura-style drone on D (Pa · Sa · Sa · low Sa) with sparse plucked phrases
     on Mohanam (S R2 G3 P D2). Composed for this page; no recordings or samples. */
  const musicBtn = $('[data-music]');
  let ctx = null, master = null, playing = false, timers = [];
  const SA = 146.83; // D3
  const ratio = { S: 1, R: 9 / 8, G: 5 / 4, P: 3 / 2, D: 5 / 3 };
  function setupAudio() {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    master = ctx.createGain(); master.gain.value = 0;
    const comp = ctx.createDynamicsCompressor(); comp.threshold.value = -24; comp.ratio.value = 3;
    const rev = ctx.createConvolver(); const len = ctx.sampleRate * 3.2, buf = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let c = 0; c < 2; c++) { const d = buf.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3.2); }
    rev.buffer = buf; const wet = ctx.createGain(); wet.gain.value = 0.35;
    master.connect(comp); master.connect(rev); rev.connect(wet); wet.connect(comp); comp.connect(ctx.destination);
  }
  function pluck(freq, t, dur, vol, bright) {
    const o1 = ctx.createOscillator(), o2 = ctx.createOscillator(), g = ctx.createGain(), lp = ctx.createBiquadFilter();
    o1.type = 'sawtooth'; o2.type = 'triangle'; o1.frequency.value = freq; o2.frequency.value = freq * 1.003;
    lp.type = 'lowpass'; lp.Q.value = 2; lp.frequency.setValueAtTime(freq * bright, t); lp.frequency.exponentialRampToValueAtTime(freq * 1.5, t + dur * 0.8);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.015); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o1.connect(lp); o2.connect(lp); lp.connect(g); g.connect(master);
    o1.start(t); o2.start(t); o1.stop(t + dur + 0.05); o2.stop(t + dur + 0.05);
  }
  function bell(freq, t, dur, vol) {
    [1, 2.01, 3.0].forEach((m, i) => {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine'; o.frequency.value = freq * m;
      const v = vol / (1 + i * 2.2);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(v, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + dur / (1 + i * .6));
      o.connect(g); g.connect(master); o.start(t); o.stop(t + dur);
    });
  }
  const drone = [[ratio.P / 2, 0.05], [1, 0.045], [1, 0.045], [0.5, 0.06]];
  const phrases = [ // original phrases: [note, octave, beats]
    [['S', 1, 1], ['D', 0, .5], ['P', 0, .5], ['G', 0, 1.5], ['R', 0, .5], ['S', 0, 2]],
    [['G', 0, .5], ['P', 0, .5], ['D', 0, 1], ['S', 1, 1], ['D', 0, .5], ['P', 0, 2.5]],
    [['P', 0, 1], ['G', 0, .5], ['R', 0, .5], ['G', 0, 1], ['P', 0, .5], ['D', 0, .5], ['P', 0, 2]],
    [['R', 1, .5], ['S', 1, .5], ['D', 0, 1], ['P', 0, .5], ['G', 0, .5], ['R', 0, 1], ['S', 0, 2.5]]
  ];
  let droneStep = 0, nextDrone = 0, nextPhrase = 0, phraseIdx = 0;
  function scheduler() {
    const now = ctx.currentTime;
    while (nextDrone < now + 0.4) {
      const [m, v] = drone[droneStep % 4];
      pluck(SA * m, nextDrone, 3.6, v, 9); droneStep++; nextDrone += 1.15;
    }
    if (nextPhrase < now + 0.4) {
      let t = nextPhrase; const beat = 0.52;
      phrases[phraseIdx % phrases.length].forEach(([n, oct, b]) => { bell(SA * 2 * ratio[n] * (oct ? 2 : 1), t, 2.6, 0.05); t += b * beat; });
      phraseIdx++; nextPhrase = t + 4 + Math.random() * 4;
    }
  }
  function startMusic() {
    if (!ctx) setupAudio();
    ctx.resume();
    const now = ctx.currentTime;
    nextDrone = now + 0.1; nextPhrase = now + 3.5;
    master.gain.cancelScheduledValues(now); master.gain.setValueAtTime(master.gain.value, now); master.gain.linearRampToValueAtTime(0.11, now + 2.5);
    timers.push(setInterval(scheduler, 150));
    playing = true; musicBtn.setAttribute('aria-pressed', 'true'); musicBtn.setAttribute('aria-label', 'Pause music');
  }
  function stopMusic() {
    if (!ctx) return;
    const now = ctx.currentTime;
    master.gain.cancelScheduledValues(now); master.gain.setValueAtTime(master.gain.value, now); master.gain.linearRampToValueAtTime(0, now + 0.8);
    timers.forEach(clearInterval); timers = [];
    setTimeout(() => { if (!playing) ctx.suspend(); }, 900);
    playing = false; musicBtn.setAttribute('aria-pressed', 'false'); musicBtn.setAttribute('aria-label', 'Play music');
  }
  musicBtn?.addEventListener('click', () => (playing ? stopMusic() : startMusic()));
  document.addEventListener('visibilitychange', () => { if (document.hidden && playing) stopMusic(); });
})();
