(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const root = document.documentElement;

  /* ---- envelope ---- */
  const stage = $('#stage'), openBtn = $('#openBtn'), cont = $('#continueBtn'), hint = $('#hint');
  let opened = false;
  function openEnvelope(instant) {
    if (opened) return; opened = true;
    stage.classList.add('opened'); stage.closest('section').classList.add('is-open');
    openBtn.hidden = true; cont.hidden = false; hint.textContent = 'The first card has risen from the envelope';
    if (!instant) { setTimeout(() => { const r = stage.getBoundingClientRect(); scrollBy({ top: r.top - innerHeight * 0.36, behavior: reduce ? 'auto' : 'smooth' }); cont.focus({ preventScroll: true }); }, reduce ? 0 : 1500); }
  }
  $('#seal').addEventListener('click', () => openEnvelope());
  openBtn.addEventListener('click', () => openEnvelope());

  /* ---- gatefold ---- */
  const gate = $('#gate'), unfoldBtn = $('#unfoldBtn');
  const gwrap = gate.parentElement;
  function fitGate() {
    const open = gate.classList.contains('unfolded');
    const wide = matchMedia('(min-width:900px)').matches;
    let s = 1;
    if (open && !wide) {
      const w = gate.offsetWidth, ang = 150 * Math.PI / 180;
      const span = w * (1 + Math.abs(Math.cos(Math.PI - ang)));   // centre + two flaps projected outward
      s = Math.min(1, (document.documentElement.clientWidth - 28) / (span * 1.07));  // 1.07: perspective widens the near edges
    }
    gate.style.setProperty('--gs', s.toFixed(3));
    gwrap.style.setProperty('--gmb', ((s - 1) * gate.offsetHeight).toFixed(1) + 'px');
  }
  addEventListener('resize', fitGate);
  function setGate(open) {
    gate.classList.toggle('unfolded', open); fitGate();
    unfoldBtn.setAttribute('aria-expanded', open);
    unfoldBtn.textContent = open ? 'Fold the card' : 'Unfold the invitation';
  }
  unfoldBtn.addEventListener('click', () => setGate(!gate.classList.contains('unfolded')));
  gate.addEventListener('click', () => { if (!gate.classList.contains('unfolded')) setGate(true); });

  /* skip intro: open everything and jump */
  $$('[data-skip]').forEach(a => a.addEventListener('click', () => { openEnvelope(true); setGate(true); }));

  window.atlasReveal = () => {
    root.classList.add('reveal-all');
    openEnvelope(true); setGate(true);
    $$('.rise').forEach(el => el.classList.add('in'));
    const p = $('#plate'); if (p) p.style.setProperty('--hide', 0);
  };

  /* ---- entrances (start visible-ish, fade up when in view) ---- */
  const io = 'IntersectionObserver' in window ? new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -8% 0px', threshold: 0.05 }) : null;
  $$('.rise').forEach(el => io ? io.observe(el) : el.classList.add('in'));
  // safety: never leave a piece invisible
  setTimeout(() => $$('.rise').forEach(el => {
    const r = el.getBoundingClientRect(); if (r.top < innerHeight) el.classList.add('in');
  }), 2500);

  /* ---- the engraving grows upward with scroll ---- */
  const plate = $('#plate');
  function grow() {
    if (!plate || reduce || root.classList.contains('reveal-all')) return;
    const r = plate.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, (innerHeight * 0.95 - r.top) / (r.height * 0.9)));
    plate.style.setProperty('--hide', (1 - p).toFixed(3));
  }
  addEventListener('scroll', () => requestAnimationFrame(grow), { passive: true });
  grow();

  /* ---- foil + emboss light follows the pointer (and drifts gently on touch) ---- */
  let tx = .5, ty = .35, cx = .5, cy = .35, raf = 0;
  function tick() {
    cx += (tx - cx) * .12; cy += (ty - cy) * .12;
    root.style.setProperty('--mx', cx.toFixed(3)); root.style.setProperty('--my', cy.toFixed(3));
    raf = (Math.abs(tx - cx) > .002 || Math.abs(ty - cy) > .002) ? requestAnimationFrame(tick) : 0;
  }
  const aim = (x, y) => { tx = x; ty = y; if (!raf) raf = requestAnimationFrame(tick); };
  if (!reduce) {
    addEventListener('pointermove', e => aim(e.clientX / innerWidth, e.clientY / innerHeight), { passive: true });
    addEventListener('scroll', () => { if (matchMedia('(hover: none)').matches) aim(.5 + .45 * Math.sin(scrollY / 420), .3 + .2 * Math.cos(scrollY / 600)); }, { passive: true });
  }

  /* ---- countdown to 8:00 PM IST, 21 Nov 2026 ---- */
  const target = Date.parse('2026-11-21T20:00:00+05:30');
  const units = Object.fromEntries($$('#count [data-u]').map(b => [b.dataset.u, b]));
  function count() {
    let ms = Math.max(0, target - Date.now());
    const d = Math.floor(ms / 864e5); ms -= d * 864e5;
    const h = Math.floor(ms / 36e5); ms -= h * 36e5;
    const m = Math.floor(ms / 6e4); ms -= m * 6e4;
    const s = Math.floor(ms / 1e3);
    units.d.textContent = d; units.h.textContent = String(h).padStart(2, '0');
    units.m.textContent = String(m).padStart(2, '0'); units.s.textContent = String(s).padStart(2, '0');
  }
  count(); setInterval(count, 1000);

  /* ---- .ics (times in UTC, equal to 8:00–11:00 PM Asia/Kolkata; end time is a placeholder) ---- */
  $('#ics').addEventListener('click', () => {
    const ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Akshay and Priya//Wedding//EN', 'CALSCALE:GREGORIAN', 'BEGIN:VEVENT',
      'UID:akshay-priya-wedding-20261121@invitation', 'DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z',
      'DTSTART:20261121T143000Z', 'DTEND:20261121T173000Z', 'SUMMARY:Wedding of Akshay & Priya',
      'DESCRIPTION:Wedding dinner 8:00 PM IST · Muhurtham 9:55 PM IST', 'LOCATION:Priyanka Convention\\, Nallajerla\\, Andhra Pradesh\\, India',
      'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    const url = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' }));
    const a = Object.assign(document.createElement('a'), { href: url, download: 'akshay-priya-wedding.ics' });
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 4000);
    say($('#ics').closest('.card'), 'Calendar file prepared. Open it to add the evening to your calendar.');
  });

  /* ---- share ---- */
  function say(scope, msg) { const s = $('.status', scope); if (s) { s.textContent = msg; setTimeout(() => { if (s.textContent === msg) s.textContent = ''; }, 4000); } }
  $$('[data-share]').forEach(b => b.addEventListener('click', async () => {
    const data = { title: 'Akshay & Priya · Wedding', text: 'Akshay & Priya · Saturday, 21 November 2026 · Priyanka Convention, Nallajerla', url: location.href.split('#')[0] };
    const scope = b.closest('.card');
    if (navigator.share) { try { await navigator.share(data); return; } catch (e) { if (e && e.name === 'AbortError') return; } }
    try { await navigator.clipboard.writeText(data.url); say(scope, 'Link copied'); }
    catch (_) { say(scope, 'Copy this link: ' + data.url); }
  }));

  /* ---- contents menu ---- */
  const menu = $('#menu'), mBtn = $('#menuBtn');
  const close = () => { menu.hidden = true; mBtn.setAttribute('aria-expanded', 'false'); mBtn.focus(); };
  mBtn.addEventListener('click', () => { menu.hidden = false; mBtn.setAttribute('aria-expanded', 'true'); $('a', menu).focus(); });
  $('#menuClose').addEventListener('click', close);
  menu.addEventListener('click', e => { if (e.target.closest('a')) { const h = e.target.closest('a').getAttribute('href'); if (h === '#invitation' || h === '#details') { openEnvelope(true); } if (h === '#invitation') setGate(true); menu.hidden = true; mBtn.setAttribute('aria-expanded', 'false'); } else if (e.target === menu) close(); });
  addEventListener('keydown', e => {
    if (menu.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'Tab') { const f = $$('a,button', menu), first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); } }
  });
})();
