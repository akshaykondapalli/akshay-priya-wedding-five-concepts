/* Letters Across Continents — correspondence deck */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');

  const deck = $('#deck');
  const cards = $$('.card', deck);
  const N = cards.length;
  const NAMES = ['The envelope', 'A letter', 'A postcard', 'A photograph', 'The invitation', 'The itinerary', 'A last note'];
  const INVITE = 4;
  const ROT = [0, -1.6, 1.4, 0, -0.6, 1.1, -1.3];
  const envCard = cards[0];
  const env = $('#envelope');
  let i = 0, opened = false, busy = false;

  /* ---------- layout ---------- */
  function place(animate = true) {
    cards.forEach((c, k) => {
      c.classList.toggle('is-active', k === i);
      c.classList.toggle('is-past', k < i);
      const d = k - i;
      let t;
      if (d < 0) {
        t = `translate(calc(-50vw - 70%), -4%) rotate(-14deg)`;
      } else if (d === 0) {
        t = `translate(0,0) rotate(${ROT[k]}deg)`;
      } else {
        const dd = Math.min(d, 3);
        t = `translate(${dd * 3}px, ${dd * 7}px) rotate(${ROT[k] + (k % 2 ? 1.6 : -1.8) * dd}deg) scale(${1 - dd * 0.025})`;
      }
      c.style.setProperty('--t', t);
      c.style.zIndex = d < 0 ? 1 : 100 - d;
      const solo = cards[i].classList.contains('card-arrival') || cards[i].classList.contains('card-print');
      c.classList.toggle('is-hidden', d > 3 || (d > 0 && solo) || (d < 0 && !animate));
      const active = d === 0;
      c.setAttribute('aria-hidden', active ? 'false' : 'true');
      if ('inert' in c) c.inert = !active;
      c.style.filter = d > 0 ? `brightness(${1 - Math.min(d, 3) * 0.12})` : '';
    });
    // past cards fade, then hide so they do not catch focus/paint
    if (animate) setTimeout(() => cards.forEach((c, k) => { if (k < i) c.classList.add('is-hidden'); }), 650);
    $('#prevBtn').disabled = i === 0;
    $('#nextBtn').disabled = i === N - 1;
    $('#ctlNum').textContent = i + 1;
    $('#ctlName').textContent = NAMES[i];
    $('#skip').hidden = i >= INVITE;
    $$('.menu a').forEach((a, k) => a.setAttribute('aria-current', k === i ? 'true' : 'false'));
  }

  function go(n, opts = {}) {
    n = Math.max(0, Math.min(N - 1, n));
    if (n > 0 && !opened) openEnvelope(true);
    if (n === i) { if (opts.focus) focusCard(); return; }
    // reveal the cards involved before animating
    cards.forEach((c, k) => { if (k >= Math.min(n, i) - 1) c.classList.remove('is-hidden'); });
    i = n;
    requestAnimationFrame(() => place(true));
    $('#announce').textContent = `${i + 1} of ${N}: ${NAMES[i]}`;
    try { history.replaceState(null, '', '#' + cards[i].id); } catch (_) {}
    if (opts.focus) setTimeout(focusCard, reduce.matches ? 0 : 380);
    if (i === 5) startCountdown();
  }
  function focusCard() {
    const h = cards[i].querySelector('[tabindex="-1"]');
    if (h) h.focus({ preventScroll: true });
  }

  /* ---------- envelope ---------- */
  function openEnvelope(instant) {
    if (opened) return;
    opened = true;
    if (instant || reduce.matches) {
      env.classList.add('opened');
      envCard.classList.add('opened');
      return;
    }
    env.classList.add('opening');
    requestAnimationFrame(() => { env.classList.add('opened'); envCard.classList.add('opened'); });
    setTimeout(() => env.classList.remove('opening'), 900);
  }
  function openAndAdvance() {
    if (busy) return;
    if (!opened) {
      busy = true;
      openEnvelope(false);
      setTimeout(() => { busy = false; go(1, { focus: true }); }, reduce.matches ? 0 : 1750);
    } else go(1, { focus: true });
  }
  $('#seal').addEventListener('click', openAndAdvance);
  $('#openBtn').addEventListener('click', openAndAdvance);

  /* ---------- drag with inertia ---------- */
  let drag = null;
  deck.addEventListener('pointerdown', e => {
    const c = cards[i];
    if (!c.contains(e.target) || busy) return;
    if (e.target.closest('a,button,input,textarea,select')) return;
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    drag = { id: e.pointerId, x0: e.clientX, y0: e.clientY, dx: 0, locked: null, hist: [[e.timeStamp, e.clientX]] };
  });
  deck.addEventListener('pointermove', e => {
    if (!drag || e.pointerId !== drag.id) return;
    const dx = e.clientX - drag.x0, dy = e.clientY - drag.y0;
    if (drag.locked === null) {
      if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
      drag.locked = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
      if (drag.locked === 'x') { cards[i].setPointerCapture(e.pointerId); cards[i].classList.add('dragging'); }
    }
    if (drag.locked !== 'x') return;
    e.preventDefault();
    drag.dx = dx;
    drag.hist.push([e.timeStamp, e.clientX]);
    if (drag.hist.length > 6) drag.hist.shift();
    let ddx = dx;
    if ((i === 0 && dx > 0) || (i === N - 1 && dx < 0)) ddx = dx * 0.25; // resistance at the ends
    cards[i].style.setProperty('--t', `translate(${ddx}px, ${Math.abs(ddx) * 0.04}px) rotate(${ROT[i] + ddx * 0.045}deg)`);
  }, { passive: false });
  function endDrag(e) {
    if (!drag || e.pointerId !== drag.id) return;
    const d = drag; drag = null;
    const c = cards[i];
    c.classList.remove('dragging');
    if (d.locked !== 'x') return;
    const h = d.hist, a = h[0], b = h[h.length - 1];
    const v = (b[1] - a[1]) / Math.max(1, b[0] - a[0]); // px per ms
    const w = c.offsetWidth;
    const forward = d.dx < -w * 0.22 || v < -0.45;
    const back = d.dx > w * 0.22 || v > 0.45;
    // flight time scales with release speed: a hard flick leaves faster
    const dur = Math.max(0.28, Math.min(0.7, 0.7 - Math.abs(v) * 0.18));
    c.style.transitionDuration = `${dur}s, .45s, .45s`;
    setTimeout(() => { c.style.transitionDuration = ''; }, dur * 1000 + 50);
    if (forward && i === 0) { c.style.transitionTimingFunction = 'cubic-bezier(.22,1.45,.36,1)'; place(false); setTimeout(() => (c.style.transitionTimingFunction = ''), 700); openAndAdvance(); return; }
    if (forward && i < N - 1) { go(i + 1); return; }
    if (back && i > 0) { place(false); go(i - 1); return; }
    // spring back
    c.style.transitionTimingFunction = 'cubic-bezier(.22,1.45,.36,1)';
    place(false);
    setTimeout(() => (c.style.transitionTimingFunction = ''), 700);
  }
  deck.addEventListener('pointerup', endDrag);
  deck.addEventListener('pointercancel', endDrag);

  /* ---------- buttons, keys, menu ---------- */
  $('#prevBtn').addEventListener('click', () => go(i - 1, { focus: false }));
  $('#nextBtn').addEventListener('click', () => (i === 0 ? openAndAdvance() : go(i + 1)));
  $('#againBtn').addEventListener('click', () => go(0, { focus: true }));
  document.addEventListener('click', e => {
    const a = e.target.closest('[data-go]');
    if (!a) return;
    e.preventDefault();
    closeMenu(false);
    go(+a.dataset.go, { focus: true });
  });
  document.addEventListener('keydown', e => {
    if (e.target.closest('input,textarea,select')) return;
    if (!menu.hidden && e.key === 'Escape') { closeMenu(true); return; }
    if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); i === 0 ? openAndAdvance() : go(i + 1); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); go(i - 1); }
    else if (e.key === 'Home') go(0);
    else if (e.key === 'End') go(N - 1);
  });
  const menu = $('#menu'), menuBtn = $('#menuBtn');
  function openMenu() { menu.hidden = false; menuBtn.setAttribute('aria-expanded', 'true'); ($('.menu a[aria-current="true"]') || $('.menu a')).focus(); }
  function closeMenu(ret) { if (menu.hidden) return; menu.hidden = true; menuBtn.setAttribute('aria-expanded', 'false'); if (ret) menuBtn.focus(); }
  menuBtn.addEventListener('click', () => (menu.hidden ? openMenu() : closeMenu(true)));
  $('#menuClose').addEventListener('click', () => closeMenu(true));
  document.addEventListener('pointerdown', e => { if (!menu.hidden && !menu.contains(e.target) && e.target !== menuBtn) closeMenu(false); });

  /* ---------- countdown ---------- */
  const TARGET = Date.parse('2026-11-21T20:00:00+05:30');
  let cdTimer = null;
  function tick() {
    const ms = TARGET - Date.now();
    const el = $('#cdVal');
    if (ms <= 0) { el.textContent = 'The celebration has begun'; $('.cd-label').textContent = '21 November 2026'; clearInterval(cdTimer); return; }
    const d = Math.floor(ms / 864e5), h = Math.floor(ms / 36e5) % 24, m = Math.floor(ms / 6e4) % 60;
    el.textContent = `${d} d · ${String(h).padStart(2, '0')} h · ${String(m).padStart(2, '0')} m`;
  }
  function startCountdown() { if (cdTimer) return; tick(); cdTimer = setInterval(tick, 30000); }
  startCountdown();

  /* ---------- calendar file ---------- */
  $('#icsBtn').addEventListener('click', () => {
    const ics = [
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Akshay and Priya//Wedding Invitation//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
      'BEGIN:VEVENT', 'UID:akshay-priya-wedding-20261121@letters', 'DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+/, ''),
      'DTSTART:20261121T143000Z', 'DTEND:20261121T173000Z',
      'SUMMARY:Wedding of Akshay & Priya',
      'DESCRIPTION:Wedding dinner 8:00 PM IST\\nMuhurtham 9:55 PM IST\\nTimes in India Standard Time (Asia/Kolkata).',
      'LOCATION:Priyanka Convention\\, Nallajerla\\, Andhra Pradesh\\, India',
      'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    const url = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' }));
    const a = Object.assign(document.createElement('a'), { href: url, download: 'akshay-priya-wedding.ics' });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
  });

  /* ---------- share ---------- */
  $('#shareBtn').addEventListener('click', async () => {
    const st = $('#shareStatus');
    const url = location.href.split('#')[0];
    const data = { title: 'Akshay & Priya · Wedding invitation', text: 'Saturday, 21 November 2026 · Priyanka Convention, Nallajerla', url };
    if (navigator.share) {
      try { await navigator.share(data); st.textContent = 'Thank you for sharing.'; return; }
      catch (err) { if (err && err.name === 'AbortError') return; }
    }
    try { await navigator.clipboard.writeText(url); st.textContent = 'Link copied.'; }
    catch (_) {
      const inp = Object.assign(document.createElement('input'), { value: url, readOnly: true });
      inp.setAttribute('aria-label', 'Invitation link');
      inp.style.cssText = 'width:100%;margin-top:6px;font:12px monospace;padding:6px';
      st.textContent = 'Copy this link:'; st.after(inp); inp.select();
    }
  });

  /* ---------- reveal hook for automated capture ---------- */
  window.atlasReveal = () => { openEnvelope(true); };
  window.atlasGo = (chapter) => { const k = cards.findIndex(c => c.dataset.chapter === chapter); if (k >= 0) { openEnvelope(true); i = k; place(false); } };

  /* ---------- start ---------- */
  const start = cards.findIndex(c => '#' + c.id === location.hash);
  if (start > 0) { openEnvelope(true); i = start; }
  place(false);
  addEventListener('hashchange', () => { const k = cards.findIndex(c => '#' + c.id === location.hash); if (k >= 0 && k !== i) go(k, { focus: true }); });
})();

/* scroll affordance for overflowing cards */
(() => {
  const ins = [...document.querySelectorAll('.js .card .card-in')];
  const check = () => ins.forEach(el => {
    const card = el.closest('.card');
    const over = el.scrollHeight > el.clientHeight + 4;
    card.classList.toggle('scrolls', over);
    card.classList.toggle('at-end', el.scrollTop + el.clientHeight >= el.scrollHeight - 4);
  });
  ins.forEach(el => el.addEventListener('scroll', check, { passive: true }));
  addEventListener('resize', check);
  document.fonts && document.fonts.ready.then(check);
  setTimeout(check, 400);
})();
