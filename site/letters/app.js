/* Letters Across Continents — keepsake box, one item at a time */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const deck = $('#deck');
  const cards = $$('.card', deck);
  const N = cards.length;
  const NAMES = ['The keepsake box', 'A letter', 'The route', 'A photograph', 'The invitation', 'The enclosure', 'With love'];
  const INV = 4;
  const ROT = [0, 0, 0, 0, 0, 0.6, 0];
  const kbox = $('#kbox'), boxCard = cards[0], invCard = cards[INV];
  let i = 0, boxOpen = false, invOpen = false, busy = false;
  const T = ms => (reduce.matches ? 0 : ms);

  /* ---------- placement ---------- */
  function place() {
    cards.forEach((c, k) => {
      const d = k - i;
      let t, op;
      if (d < 0) { t = 'translate(-14%, -9%) rotate(-5deg) scale(1.05)'; op = 0; }
      else if (d === 0) { t = `rotate(${ROT[k]}deg)`; op = 1; }
      else { t = 'translate(0, 9%) scale(.88)'; op = 0; }
      c.style.setProperty('--t', t);
      c.style.opacity = op;
      c.style.zIndex = d === 0 ? 10 : d < 0 ? 5 : 1;
      c.classList.toggle('is-active', d === 0);
      if (d !== 0) { clearTimeout(c._h); c._h = setTimeout(() => { if (cards.indexOf(c) !== i) c.classList.add('is-hidden'); }, T(700)); }
      else { clearTimeout(c._h); c.classList.remove('is-hidden'); }
      c.setAttribute('aria-hidden', d === 0 ? 'false' : 'true');
      if ('inert' in c) c.inert = d !== 0;
    });
    $('#prevBtn').disabled = i === 0;
    $('#nextBtn').disabled = i === N - 1;
    $('#ctlNum').textContent = i + 1;
    $('#ctlName').textContent = NAMES[i];
    $('#skip').hidden = i >= INV;
    $$('.menu a').forEach((a, k) => a.setAttribute('aria-current', k === i ? 'true' : 'false'));
  }

  function go(n, opts = {}) {
    n = Math.max(0, Math.min(N - 1, n));
    if (n > 0 && !boxOpen) openBox(true);
    if (n > INV && !invOpen) openInvite(true);
    if (n === i) { if (opts.focus) focusCard(); return; }
    cards[n].classList.remove('is-hidden');
    i = n;
    requestAnimationFrame(place);
    $('#announce').textContent = `${i + 1} of ${N}: ${NAMES[i]}`;
    try { history.replaceState(null, '', '#' + cards[i].id); } catch (_) {}
    if (opts.focus) setTimeout(focusCard, T(420));
  }
  function focusCard() {
    let h = cards[i].querySelector('[tabindex="-1"]');
    if (i === INV && !invOpen) h = $('#invOpen');
    if (h) h.focus({ preventScroll: true });
  }
  const forward = () => {
    if (busy) return;
    if (i === 0 && !boxOpen) return openBoxAndAdvance();
    if (i === INV && !invOpen) return openInvite(false);
    go(i + 1);
  };

  /* ---------- the box ---------- */
  function openBox(instant) {
    if (boxOpen) return;
    boxOpen = true;
    if (instant || reduce.matches) { kbox.classList.add('instant'); requestAnimationFrame(() => requestAnimationFrame(() => kbox.classList.remove('instant'))); }
    kbox.classList.add('opened'); boxCard.classList.add('opened');
  }
  function resetBox() {
    boxOpen = false;
    kbox.classList.add('instant');
    kbox.classList.remove('opened'); boxCard.classList.remove('opened');
    requestAnimationFrame(() => requestAnimationFrame(() => kbox.classList.remove('instant')));
  }
  function openBoxAndAdvance() {
    if (busy) return;
    if (boxOpen) return go(1, { focus: true });
    busy = true;
    openBox(false);
    setTimeout(() => { busy = false; go(1, { focus: true }); }, T(3000));
  }
  $('#boxHit').addEventListener('click', openBoxAndAdvance);
  $('#openBtn').addEventListener('click', openBoxAndAdvance);

  /* ---------- the invitation envelope ---------- */
  function openInvite(instant) {
    if (invOpen) return;
    invOpen = true;
    if (instant || reduce.matches) {
      invCard.classList.add('opening', 'open');
      if (cards.indexOf(invCard) === i) setTimeout(focusCard, 30);
      return;
    }
    busy = true;
    invCard.classList.add('opening');
    setTimeout(() => { invCard.classList.add('open'); busy = false; setTimeout(focusCard, 300); }, 2100);
  }
  function resetInvite() { invOpen = false; invCard.classList.remove('opening', 'open'); }
  $('#invOpen').addEventListener('click', () => openInvite(false));

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
      if (drag.locked === 'x') { try { cards[i].setPointerCapture(e.pointerId); } catch (_) {} cards[i].classList.add('dragging'); }
    }
    if (drag.locked !== 'x') return;
    e.preventDefault();
    drag.dx = dx;
    drag.hist.push([e.timeStamp, e.clientX]); if (drag.hist.length > 6) drag.hist.shift();
    let ddx = dx;
    if ((i === 0 && dx > 0) || (i === N - 1 && dx < 0)) ddx = dx * 0.25;
    cards[i].style.setProperty('--t', `translate(${ddx}px, ${-Math.abs(ddx) * 0.05}px) rotate(${ROT[i] + ddx * 0.035}deg) scale(${1 + Math.min(Math.abs(ddx), 200) / 4000})`);
  }, { passive: false });
  function endDrag(e) {
    if (!drag || e.pointerId !== drag.id) return;
    const d = drag; drag = null;
    const c = cards[i];
    c.classList.remove('dragging');
    if (d.locked !== 'x') return;
    const h = d.hist, a = h[0], b = h[h.length - 1];
    const v = (b[1] - a[1]) / Math.max(1, b[0] - a[0]);
    const w = c.offsetWidth;
    const fwd = d.dx < -w * 0.2 || v < -0.45;
    const back = d.dx > w * 0.2 || v > 0.45;
    const dur = Math.max(0.3, Math.min(0.7, 0.7 - Math.abs(v) * 0.18));
    c.style.transitionDuration = `${dur}s, .5s`;
    setTimeout(() => { c.style.transitionDuration = ''; }, dur * 1000 + 60);
    if (fwd && i < N - 1) {
      if ((i === 0 && !boxOpen) || (i === INV && !invOpen)) { spring(c); forward(); return; }
      go(i + 1); return;
    }
    if (back && i > 0) { go(i - 1); return; }
    spring(c);
  }
  function spring(c) { c.style.transitionTimingFunction = 'cubic-bezier(.22,1.35,.36,1)'; place(); setTimeout(() => (c.style.transitionTimingFunction = ''), 750); }
  deck.addEventListener('pointerup', endDrag);
  deck.addEventListener('pointercancel', endDrag);

  /* ---------- buttons, keys, menu ---------- */
  $('#prevBtn').addEventListener('click', () => go(i - 1));
  $('#nextBtn').addEventListener('click', forward);
  $('#againBtn').addEventListener('click', () => {
    go(0, { focus: false });
    setTimeout(() => { resetBox(); resetInvite(); $('#openBtn').focus({ preventScroll: true }); }, T(750));
  });
  document.addEventListener('click', e => {
    const a = e.target.closest('[data-go]');
    if (!a) return;
    e.preventDefault();
    closeMenu(false);
    const n = +a.dataset.go;
    go(n, { focus: true });
    if (a.dataset.open && n === INV) setTimeout(() => openInvite(false), T(650));
  });
  const menu = $('#menu'), menuBtn = $('#menuBtn');
  document.addEventListener('keydown', e => {
    if (e.target.closest('input,textarea,select')) return;
    if (!menu.hidden && e.key === 'Escape') { closeMenu(true); return; }
    if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); forward(); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); go(i - 1); }
    else if (e.key === 'Home') go(0);
    else if (e.key === 'End') go(N - 1);
  });
  function openMenu() { menu.hidden = false; menuBtn.setAttribute('aria-expanded', 'true'); ($('.menu a[aria-current="true"]') || $('.menu a')).focus(); }
  function closeMenu(ret) { if (menu.hidden) return; menu.hidden = true; menuBtn.setAttribute('aria-expanded', 'false'); if (ret) menuBtn.focus(); }
  menuBtn.addEventListener('click', () => (menu.hidden ? openMenu() : closeMenu(true)));
  $('#menuClose').addEventListener('click', () => closeMenu(true));
  document.addEventListener('pointerdown', e => { if (!menu.hidden && !menu.contains(e.target) && e.target !== menuBtn) closeMenu(false); });

  /* ---------- countdown ---------- */
  const TARGET = Date.parse('2026-11-21T20:00:00+05:30');
  let cdTimer = null;
  function tick() {
    const ms = TARGET - Date.now(), el = $('#cdVal');
    if (ms <= 0) { el.textContent = 'The celebration has begun'; clearInterval(cdTimer); return; }
    const d = Math.floor(ms / 864e5), h = Math.floor(ms / 36e5) % 24, m = Math.floor(ms / 6e4) % 60;
    el.textContent = `${d} days · ${h} h · ${String(m).padStart(2, '0')} min`;
  }
  tick(); cdTimer = setInterval(tick, 30000);

  /* ---------- calendar file ---------- */
  $('#icsBtn').addEventListener('click', () => {
    const ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Akshay and Priya//Wedding Invitation//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
      'BEGIN:VEVENT', 'UID:akshay-priya-wedding-20261121@letters', 'DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+/, ''),
      'DTSTART:20261121T143000Z', 'DTEND:20261121T173000Z', 'SUMMARY:Wedding of Akshay & Priya',
      'DESCRIPTION:Wedding dinner 8:00 PM IST\\nMuhurtham 9:55 PM IST\\nTimes in India Standard Time (Asia/Kolkata).',
      'LOCATION:Priyanka Convention\\, Nallajerla\\, Andhra Pradesh\\, India', 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    const url = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' }));
    const a = Object.assign(document.createElement('a'), { href: url, download: 'akshay-priya-wedding.ics' });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
  });

  /* ---------- share ---------- */
  $$('.share-btn').forEach(btn => btn.addEventListener('click', async () => {
    const st = document.getElementById(btn.dataset.status);
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
      inp.style.cssText = 'width:100%;font:12px monospace;padding:6px';
      st.textContent = 'Copy this link:'; st.after(inp); inp.select();
    }
  }));

  /* ---------- scroll affordance inside cards ---------- */
  const ins = $$('.sheet-in,.inv-in');
  const check = () => ins.forEach(el => {
    const over = el.scrollHeight > el.clientHeight + 4;
    el.style.maskImage = el.style.webkitMaskImage = over && el.scrollTop + el.clientHeight < el.scrollHeight - 4 ? 'linear-gradient(#000 85%, transparent)' : '';
  });
  ins.forEach(el => el.addEventListener('scroll', check, { passive: true }));
  addEventListener('resize', check);
  document.fonts && document.fonts.ready.then(check);
  setTimeout(check, 500);

  /* ---------- hooks for automated capture ---------- */
  window.atlasReveal = () => { openBox(true); openInvite(true); };
  window.atlasGo = ch => { const k = cards.findIndex(c => c.dataset.chapter === ch); if (k >= 0) { window.atlasReveal(); i = k; place(); setTimeout(check, 50); } };

  /* ---------- start ---------- */
  const start = cards.findIndex(c => '#' + c.id === location.hash);
  if (start > 0) { openBox(true); if (start >= INV) openInvite(true); i = start; }
  place();
  addEventListener('hashchange', () => { const k = cards.findIndex(c => '#' + c.id === location.hash); if (k >= 0 && k !== i) go(k, { focus: true }); });
})();
