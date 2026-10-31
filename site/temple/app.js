/* The Temple of Two Souls — interactions.
   Stage camera + lamp canvas driven by scroll; door sanctum; menu; original Web Audio music; calendar; share; countdown. */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  var reduceMQ = window.matchMedia('(prefers-reduced-motion: reduce)');
  var reduced = reduceMQ.matches;
  var revealAll = false; // set by window.atlasReveal for automated capture

  /* ---------------- helpers ---------------- */
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function smooth(a, b, v) { var t = clamp((v - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); }
  function easeInOut(t) { return t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

  /* ---------------- stage geometry ---------------- */
  var SW = 3200, SH = 2100, VPX = 1600, VPY = 1280, K = 820, GATE_Y = 1380;
  var pil = doc.getElementById('pilgrimage');
  var stage = doc.getElementById('stage');
  var sky = doc.getElementById('sky');
  var canvas = doc.getElementById('lamps');
  var veil = doc.getElementById('veil');
  var frame = doc.getElementById('frame');
  var pillarL = frame.querySelector('.pillar.left');
  var pillarR = frame.querySelector('.pillar.right');
  var garland = frame.querySelector('.garland');
  var bell = frame.querySelector('.bell');
  var ctx = canvas.getContext('2d');
  var vw = 0, vh = 0, dpr = 1, bs = 1, gy = 0, gx = 0, ox = 0, oy = 0;
  var sprite = new Image(); sprite.src = 'img/deepam.webp';

  function layout() {
    var wrap = canvas.parentNode;
    vw = wrap.clientWidth; vh = wrap.clientHeight;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(vw * dpr); canvas.height = Math.round(vh * dpr);
    var portrait = vh > vw;
    gy = vh * (portrait ? 0.70 : 0.80);
    bs = Math.max(vw / SW, vh / 2300, (vh - gy) / 820);
    gx = vw / 2;
    ox = gx - VPX * bs; oy = gy - GATE_Y * bs;
    draw(performance.now(), true);
  }

  /* lamps: two rows along the processional edges, lit from the near edges toward the gate */
  var N = 12, lamps = [];
  (function buildLamps() {
    for (var i = 0; i < N; i++) {
      var z = 1.12 + (7.55 - 1.12) * i / (N - 1);
      [-1, 1].forEach(function (side) {
        lamps.push({ X: side * 1.2, z: z, side: side, i: i, t: 0.03 + 0.66 * i / (N - 1) + (side > 0 ? 0.018 : 0), I: 0, seed: Math.random() * 100 });
      });
    }
    lamps.sort(function (a, b) { return b.z - a.z; }); // far first
  })();
  var center = { X: 0, z: 7.95, I: 0, seed: 7 };

  function progress() {
    if (reduced) return 1;
    var r = pil.getBoundingClientRect();
    var span = pil.offsetHeight - vh;
    return span > 0 ? clamp(-r.top / span, 0, 1) : 0;
  }

  var lastT = performance.now();
  function draw(now, force) {
    var p = progress();
    var dt = Math.min(64, now - lastT); lastT = now;
    var k = reduced ? 0 : easeInOut(p);
    var zoom = 1 + 0.9 * k;
    var a = bs * zoom;
    var tx = gx + (ox - gx) * zoom, ty = gy + (oy - gy) * zoom;
    stage.style.transform = 'matrix(' + a + ',0,0,' + a + ',' + tx + ',' + ty + ')';
    sky.style.transform = 'scale(' + (1 + 0.1 * k) + ') translateY(' + (k * 2) + '%)';
    // foreground mandapa frame: we walk past it
    pillarL.style.transform = 'translateX(' + (-k * 85) + '%) scale(' + (1 + 0.3 * k) + ')';
    pillarR.style.transform = 'scaleX(-1) translateX(' + (-k * 85) + '%) scale(' + (1 + 0.3 * k) + ')';
    garland.style.transform = 'translateY(' + (-k * 75) + '%)';
    bell.style.transform = 'translateY(' + (-k * 70) + '%)';
    bell.style.opacity = reduced ? '1' : String(smooth(.02, .09, p) * (1 - smooth(.35, .62, p)));
    veil.style.opacity = reduced ? '0' : String(smooth(.9, 1, p) * 0.92);

    // canvas
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.setTransform(dpr * a, 0, 0, dpr * a, dpr * tx, dpr * ty);
    var t = now / 1000;
    var rate = revealAll || reduced ? 1 : Math.min(1, dt / 260);
    var litCount = 0;
    lamps.forEach(function (L) {
      var target = (reduced || p >= L.t) ? 1 : 0;
      L.I += (target - L.I) * rate;
      if (L.I > .5) litCount++;
    });
    var merge = reduced ? 1 : smooth(.8, .92, p);
    center.I += (merge - center.I) * rate;

    // gate glow grows with the number of lit lamps
    var gateStrength = 0.15 + 0.55 * (litCount / lamps.length) + 0.5 * center.I;
    ctx.globalCompositeOperation = 'lighter';
    radial(VPX, GATE_Y - 120, 520, 'rgba(255,170,90,' + (0.22 * gateStrength) + ')');
    radial(VPX, GATE_Y - 20, 180, 'rgba(255,214,150,' + (0.35 * gateStrength) + ')');
    ctx.globalCompositeOperation = 'source-over';

    lamps.forEach(function (L) { drawLamp(L, t, merge); });
    drawCenter(t);
    if (!force && !visible) return;
  }

  function radial(x, y, r, col) {
    var g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, col); g.addColorStop(1, 'rgba(255,150,60,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
  }
  function poolEllipse(x, y, rx, ry, alpha) {
    ctx.save(); ctx.translate(x, y); ctx.scale(1, ry / rx);
    var g = ctx.createRadialGradient(0, 0, 0, 0, 0, rx);
    g.addColorStop(0, 'rgba(255,170,80,' + alpha + ')'); g.addColorStop(.5, 'rgba(240,120,50,' + alpha * .4 + ')'); g.addColorStop(1, 'rgba(200,90,40,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, rx, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  }
  function flame(x, y, h, I, t, seed, lean) {
    if (I < .02) return;
    var fl = reduced ? 1 : 1 + 0.07 * Math.sin(t * 13 + seed) + 0.04 * Math.sin(t * 29 + seed * 2.3);
    var hh = h * fl * (0.55 + 0.45 * I);
    var sway = reduced ? 0 : h * 0.07 * Math.sin(t * 6.3 + seed);
    var tipX = x + sway + (lean || 0) * h * 0.5, tipY = y - hh;
    var w = h * 0.24;
    // halo
    ctx.globalCompositeOperation = 'lighter';
    var g = ctx.createRadialGradient(x, y - hh * .45, 0, x, y - hh * .45, h * 2.6);
    g.addColorStop(0, 'rgba(255,200,120,' + 0.55 * I + ')'); g.addColorStop(.35, 'rgba(255,140,60,' + 0.18 * I + ')'); g.addColorStop(1, 'rgba(255,120,40,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y - hh * .45, h * 2.6, 0, Math.PI * 2); ctx.fill();
    // body
    ctx.globalCompositeOperation = 'source-over';
    ctx.beginPath();
    ctx.moveTo(x - w, y);
    ctx.bezierCurveTo(x - w * 1.15, y - hh * .45, tipX - w * .2, tipY + hh * .25, tipX, tipY);
    ctx.bezierCurveTo(tipX + w * .2, tipY + hh * .25, x + w * 1.15, y - hh * .45, x + w, y);
    ctx.quadraticCurveTo(x, y + w * .9, x - w, y);
    var fg = ctx.createLinearGradient(x, y, x, tipY);
    fg.addColorStop(0, 'rgba(255,255,240,' + I + ')'); fg.addColorStop(.25, 'rgba(255,236,170,' + I + ')');
    fg.addColorStop(.6, 'rgba(255,170,60,' + .95 * I + ')'); fg.addColorStop(1, 'rgba(230,90,30,' + .2 * I + ')');
    ctx.fillStyle = fg; ctx.fill();
    // blue root
    ctx.beginPath(); ctx.ellipse(x, y - w * .1, w * .55, w * .35, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(120,150,255,' + .35 * I + ')'; ctx.fill();
  }
  function drawLamp(L, t, merge) {
    var sx = VPX + L.X * K / L.z, sy = VPY + K / L.z;
    var h = 250 / L.z, w = h * (160 / 192);
    // floor pool + polished-granite reflection
    if (L.I > .02) {
      ctx.globalCompositeOperation = 'lighter';
      poolEllipse(sx, sy, h * 1.9, h * 0.42, 0.42 * L.I);
      var rg = ctx.createLinearGradient(sx, sy, sx, sy + h * 1.3);
      rg.addColorStop(0, 'rgba(255,190,110,' + .28 * L.I + ')'); rg.addColorStop(1, 'rgba(255,150,70,0)');
      ctx.fillStyle = rg; ctx.fillRect(sx - h * .07, sy, h * .14, h * 1.3);
      ctx.globalCompositeOperation = 'source-over';
    }
    if (sprite.complete && sprite.naturalWidth) {
      ctx.globalAlpha = 0.4 + 0.6 * L.I;
      ctx.drawImage(sprite, sx - w / 2, sy - h, w, h);
      ctx.globalAlpha = 1;
    }
    // the two nearest-the-gate flames lean toward the centre as they merge
    var lean = L.i >= N - 2 ? -L.side * merge * 0.6 : 0;
    flame(sx, sy - h * 0.55, h * 0.42, L.I, t, L.seed, lean);
  }
  function drawCenter(t) {
    if (center.I < .02) return;
    var sx = VPX, sy = VPY + K / center.z + 6;
    var h = 470 / center.z, w = h * (160 / 192);
    ctx.globalCompositeOperation = 'lighter';
    poolEllipse(sx, sy, h * 3.2, h * .7, .55 * center.I);
    radial(sx, sy - h, h * 7, 'rgba(255,200,120,' + .32 * center.I + ')');
    // the moment of union: a brief bloom as the single flame takes hold
    var bloom = Math.sin(Math.PI * clamp((center.I - .35) / .65, 0, 1));
    if (bloom > .01) radial(sx, sy - h * .8, h * 11, 'rgba(255,230,180,' + .22 * bloom + ')');
    ctx.globalCompositeOperation = 'source-over';
    if (sprite.complete && sprite.naturalWidth) ctx.drawImage(sprite, sx - w / 2, sy - h, w, h);
    flame(sx, sy - h * .55, h * .62, center.I, t, center.seed, 0);
  }

  /* render loop only while the pilgrimage is on screen */
  var visible = true, raf = 0;
  function loop(now) { draw(now); raf = (visible && !doc.hidden && !reduced) ? requestAnimationFrame(loop) : 0; }
  function kick() { if (!raf) raf = requestAnimationFrame(loop); }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) kick(); }).observe(pil);
  }
  window.addEventListener('scroll', function () { if (reduced) { draw(performance.now(), true); } else kick(); }, { passive: true });
  window.addEventListener('resize', layout);
  doc.addEventListener('visibilitychange', function () { if (!doc.hidden) kick(); });
  sprite.addEventListener('load', function () { draw(performance.now(), true); });
  reduceMQ.addEventListener && reduceMQ.addEventListener('change', function (e) { reduced = e.matches; layout(); kick(); });
  layout(); kick();

  /* ---------------- doors ---------------- */
  var doors = doc.getElementById('doors');
  var openBtn = doc.getElementById('openDoors');
  var opened = false;
  function openDoors(instant) {
    if (opened) return; opened = true;
    if (instant) { doors.querySelectorAll('.door').forEach(function (d) { d.style.transition = 'none'; }); }
    doors.classList.add('open'); doors.classList.add('gone');
    openBtn.hidden = true;
  }
  openBtn.addEventListener('click', function () { openDoors(false); });
  if (reduced) openDoors(true);
  else if ('IntersectionObserver' in window) {
    var dio = new IntersectionObserver(function (es) {
      if (es[0].intersectionRatio > .55) { setTimeout(function () { openDoors(false); }, 450); dio.disconnect(); }
    }, { threshold: [0, .55, .8] });
    dio.observe(doc.getElementById('doorStage'));
  } else openDoors(true);

  /* ---------------- menu ---------------- */
  var menu = doc.getElementById('menu'), menuBtn = doc.getElementById('menuBtn'), menuClose = doc.getElementById('menuClose');
  function setMenu(open) {
    menu.hidden = !open; menuBtn.setAttribute('aria-expanded', String(open));
    doc.body.style.overflow = open ? 'hidden' : '';
    if (open) menu.querySelector('a').focus(); else menuBtn.focus();
  }
  menuBtn.addEventListener('click', function () { setMenu(menu.hidden); });
  menuClose.addEventListener('click', function () { setMenu(false); });
  menu.addEventListener('click', function (e) { if (e.target.closest('a')) { menu.hidden = true; menuBtn.setAttribute('aria-expanded', 'false'); doc.body.style.overflow = ''; } });
  doc.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !menu.hidden) setMenu(false);
    if (e.key === 'Tab' && !menu.hidden) {
      var f = menu.querySelectorAll('a,button'), first = f[0], last = f[f.length - 1];
      if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  // jumping to the invitation opens the doors
  doc.querySelectorAll('a[href="#invitation"]').forEach(function (a) { a.addEventListener('click', function () { setTimeout(function () { openDoors(false); }, 900); }); });

  /* ---------------- countdown ---------------- */
  var TARGET = Date.UTC(2026, 10, 21, 14, 30, 0); // 8:00 PM IST
  function tick() {
    var diff = TARGET - Date.now();
    var d = doc.getElementById('cdD'), h = doc.getElementById('cdH'), m = doc.getElementById('cdM');
    if (diff <= 0) { doc.querySelector('.cd-label').textContent = 'The celebration has begun'; d.textContent = h.textContent = m.textContent = '0'; return; }
    d.textContent = Math.floor(diff / 864e5);
    h.textContent = String(Math.floor(diff / 36e5) % 24).padStart(2, '0');
    m.textContent = String(Math.floor(diff / 6e4) % 60).padStart(2, '0');
  }
  tick(); setInterval(tick, 30000);

  /* ---------------- calendar file ---------------- */
  doc.getElementById('icsBtn').addEventListener('click', function () {
    var stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
    // End time (11:00 PM IST) is a placeholder to confirm.
    var ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Akshay and Priya//Wedding invitation//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
      'BEGIN:VEVENT', 'UID:akshay-priya-wedding-20261121@temple-of-two-souls', 'DTSTAMP:' + stamp,
      'DTSTART:20261121T143000Z', 'DTEND:20261121T173000Z',
      'SUMMARY:Wedding of Akshay & Priya',
      'DESCRIPTION:Wedding dinner 8:00 PM IST · Muhurtham 9:55 PM IST',
      'LOCATION:Priyanka Convention\\, Nallajerla\\, Andhra Pradesh\\, India',
      'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    var blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = doc.createElement('a'); a.href = url; a.download = 'akshay-priya-wedding.ics';
    doc.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  });

  /* ---------------- share ---------------- */
  var shareBtn = doc.getElementById('shareBtn'), shareStatus = doc.getElementById('shareStatus');
  shareBtn.addEventListener('click', function () {
    var url = location.href.split('#')[0];
    var data = { title: 'Akshay & Priya · Wedding invitation', text: 'Akshay & Priya · Saturday, 21 November 2026 · Priyanka Convention, Nallajerla', url: url };
    if (navigator.share) {
      navigator.share(data).catch(function (e) { if (e && e.name !== 'AbortError') copy(url); });
    } else copy(url);
  });
  function copy(url) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () { shareStatus.textContent = 'Link copied.'; }, function () { shareStatus.textContent = 'Copy this link: ' + url; });
    } else shareStatus.textContent = 'Copy this link: ' + url;
  }

  /* ---------------- original music (Web Audio, synthesised live) ---------------- */
  var musicBtn = doc.getElementById('musicBtn');
  var audio = null, playing = false;
  function makeAudio() {
    var AC = window.AudioContext || window.webkitAudioContext; if (!AC) return null;
    var ac = new AC();
    var master = ac.createGain(); master.gain.value = 0;
    var comp = ac.createDynamicsCompressor(); comp.threshold.value = -24; comp.ratio.value = 4;
    master.connect(comp); comp.connect(ac.destination);
    // simple generated reverb
    var len = ac.sampleRate * 3.2, ir = ac.createBuffer(2, len, ac.sampleRate);
    for (var ch = 0; ch < 2; ch++) { var d = ir.getChannelData(ch); for (var i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3.2); }
    var verb = ac.createConvolver(); verb.buffer = ir;
    var wet = ac.createGain(); wet.gain.value = .45; verb.connect(wet); wet.connect(master);
    var dry = ac.createGain(); dry.gain.value = .7; dry.connect(master);
    var SA = 138.59; // C#3
    function pluck(freq, when, vol) {
      // tanpura-like pluck: two detuned saws through a slowly closing low-pass, long decay
      var g = ac.createGain(); g.gain.setValueAtTime(0, when);
      g.gain.linearRampToValueAtTime(vol, when + .03); g.gain.exponentialRampToValueAtTime(.0008, when + 4.2);
      var f = ac.createBiquadFilter(); f.type = 'lowpass'; f.Q.value = 6;
      f.frequency.setValueAtTime(freq * 9, when); f.frequency.exponentialRampToValueAtTime(freq * 2.2, when + 3.2);
      [0, 4].forEach(function (cents) {
        var o = ac.createOscillator(); o.type = 'sawtooth'; o.frequency.value = freq; o.detune.value = cents;
        o.connect(f); o.start(when); o.stop(when + 4.4);
      });
      f.connect(g); g.connect(dry); g.connect(verb);
    }
    function bellTone(freq, when, vol) {
      var parts = [[1, 1], [2.0, .5], [2.76, .35], [4.07, .18], [5.4, .1]];
      parts.forEach(function (pt) {
        var o = ac.createOscillator(), g = ac.createGain();
        o.type = 'sine'; o.frequency.value = freq * pt[0];
        g.gain.setValueAtTime(0, when); g.gain.linearRampToValueAtTime(vol * pt[1], when + .008);
        g.gain.exponentialRampToValueAtTime(.0005, when + 5.5 / pt[0] + .6);
        o.connect(g); g.connect(verb); g.connect(dry); o.start(when); o.stop(when + 6.5);
      });
    }
    // Mohanam: S R2 G3 P D2 (an original, slowly wandering phrase; no existing melody)
    var scale = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2, 9 / 4, 5 / 2];
    var deg = 2, timer = null, nextPluck = 0, nextBell = 0, step = 0;
    var cycle = [SA * .75, SA, SA, SA * .5]; // Pa, Sa, Sa, low Sa
    function schedule() {
      var now = ac.currentTime;
      while (nextPluck < now + 1.5) { pluck(cycle[step % 4], nextPluck, step % 4 === 3 ? .07 : .05); step++; nextPluck += 1.15; }
      while (nextBell < now + 1.5) {
        deg = clamp(deg + [-2, -1, -1, 0, 1, 1, 2][Math.floor(Math.random() * 7)], 0, scale.length - 1);
        bellTone(SA * 4 * scale[deg], nextBell, .045);
        if (Math.random() < .35) bellTone(SA * 4 * scale[clamp(deg + 1, 0, scale.length - 1)], nextBell + .55, .03);
        nextBell += 3.4 + Math.random() * 3.2;
      }
    }
    return {
      start: function () {
        ac.resume(); var now = ac.currentTime;
        nextPluck = Math.max(nextPluck, now + .1); nextBell = Math.max(nextBell, now + 1.2);
        schedule(); timer = setInterval(schedule, 400);
        master.gain.cancelScheduledValues(now); master.gain.setValueAtTime(master.gain.value, now);
        master.gain.linearRampToValueAtTime(.11, now + 2.5);
      },
      stop: function () {
        var now = ac.currentTime; clearInterval(timer);
        master.gain.cancelScheduledValues(now); master.gain.setValueAtTime(master.gain.value, now);
        master.gain.linearRampToValueAtTime(0, now + 1.2);
        setTimeout(function () { if (!playing) ac.suspend(); }, 1400);
      }
    };
  }
  function setMusic(on) {
    if (on && !audio) audio = makeAudio();
    if (!audio) { musicBtn.disabled = true; musicBtn.querySelector('.label').textContent = 'Music unavailable'; return; }
    playing = on;
    if (on) audio.start(); else audio.stop();
    musicBtn.setAttribute('aria-pressed', String(on));
    musicBtn.querySelector('.label').textContent = on ? 'Pause music' : 'Play music';
    musicBtn.setAttribute('aria-label', on ? 'Pause music' : 'Play music');
  }
  musicBtn.setAttribute('aria-label', 'Play music');
  musicBtn.addEventListener('click', function () { setMusic(!playing); });
  doc.addEventListener('visibilitychange', function () {
    if (!audio || !playing) return;
    if (doc.hidden) audio.stop(); else audio.start();
  });

  /* ---------------- capture hook ---------------- */
  window.atlasReveal = function () { revealAll = true; openDoors(true); draw(performance.now(), true); };
})();
