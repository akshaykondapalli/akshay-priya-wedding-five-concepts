// Generates the courtyard scene layers as SVG, rasterises them with Chromium, and records
// the positions of every flame and jasmine strand so the page can light/animate them.
// Wide canvas 2400x1800; phone-safe zone x 784–1616.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const TEX = 'file://' + path.join(__dirname, 'tex') + '/';
const OUT = path.join(__dirname, 'render'); fs.mkdirSync(OUT, { recursive: true });
let seed = 2111;
const R = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
const rr = (a, b) => a + R() * (b - a);
const f = n => Math.round(n * 10) / 10;
const META = { flames: [], strands: [] };

const defs = () => `
<defs>
  <pattern id="lime" patternUnits="userSpaceOnUse" width="2400" height="1800"><image href="${TEX}limewash.png" width="2400" height="1800"/></pattern>
  <pattern id="facade" patternUnits="userSpaceOnUse" width="2400" height="1800"><image href="${TEX}limewash-facade.png" width="2400" height="1800"/></pattern>
  <pattern id="teak" patternUnits="userSpaceOnUse" width="512" height="2048"><image href="${TEX}teak.png" width="512" height="2048"/></pattern>
  <pattern id="teakH" patternUnits="userSpaceOnUse" width="2048" height="512" patternTransform="rotate(90)"><image href="${TEX}teak.png" width="512" height="2048"/></pattern>
  <pattern id="oxide" patternUnits="userSpaceOnUse" width="2400" height="900"><image href="${TEX}redoxide.png" width="2400" height="900"/></pattern>
  <pattern id="granite" patternUnits="userSpaceOnUse" width="2400" height="400"><image href="${TEX}granite.png" width="2400" height="400"/></pattern>
  <pattern id="terra" patternUnits="userSpaceOnUse" width="1200" height="400"><image href="${TEX}terracotta.png" width="1200" height="400"/></pattern>
  <pattern id="brassT" patternUnits="userSpaceOnUse" width="512" height="512"><image href="${TEX}brass.png" width="512" height="512"/></pattern>
  <linearGradient id="cyl" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset=".32" stop-color="#fff" stop-opacity=".10"/><stop offset=".45" stop-color="#ffd9a0" stop-opacity=".22"/><stop offset=".75" stop-color="#000" stop-opacity=".25"/><stop offset="1" stop-color="#000" stop-opacity=".65"/></linearGradient>
  <linearGradient id="brassCyl" x1="0" x2="1"><stop offset="0" stop-color="#5a3608"/><stop offset=".25" stop-color="#c58f35"/><stop offset=".42" stop-color="#ffe2a0"/><stop offset=".55" stop-color="#d9a64a"/><stop offset=".85" stop-color="#7a4c12"/><stop offset="1" stop-color="#3f2606"/></linearGradient>
  <radialGradient id="bud" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fffef8"/><stop offset=".6" stop-color="#f3ecd8"/><stop offset="1" stop-color="#c9bf9f"/></radialGradient>
  <radialGradient id="budDim" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#f4ead6"/><stop offset=".6" stop-color="#d9cdb0"/><stop offset="1" stop-color="#9c8f72"/></radialGradient>
  <linearGradient id="leaf" x1="0" x2="1"><stop offset="0" stop-color="#1f4a1c"/><stop offset=".5" stop-color="#3f7a2c"/><stop offset="1" stop-color="#2a5a20"/></linearGradient>
  <linearGradient id="banana" x1="0" x2="1"><stop offset="0" stop-color="#2e5e22"/><stop offset=".5" stop-color="#5f9a3a"/><stop offset="1" stop-color="#3b6e27"/></linearGradient>
  <radialGradient id="marigold" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#ffc23a"/><stop offset=".6" stop-color="#f08a12"/><stop offset="1" stop-color="#a84c06"/></radialGradient>
  <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffb35a" stop-opacity=".55"/><stop offset="1" stop-color="#ffb35a" stop-opacity="0"/></radialGradient>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="blur30" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="6" dy="10" stdDeviation="10" flood-color="#1a0d05" flood-opacity=".55"/></filter>
  <filter id="shadowS" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="2" dy="4" stdDeviation="3" flood-color="#1a0d05" flood-opacity=".5"/></filter>
  <filter id="carve" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur in="SourceAlpha" stdDeviation="1.6" result="b"/><feSpecularLighting in="b" surfaceScale="3" specularConstant=".7" specularExponent="18" lighting-color="#ffd7a0" result="s"><feDistantLight azimuth="235" elevation="38"/></feSpecularLighting><feComposite in="s" in2="SourceAlpha" operator="in" result="s2"/><feComposite in="SourceGraphic" in2="s2" operator="arithmetic" k1="0" k2="1" k3=".6" k4="0"/></filter>
</defs>`;

// ---------- motifs ----------
function jasmineStrand(x, y0, len, opts = {}) {
  const dim = opts.dim, sway = opts.sway || 0, g = dim ? 'budDim' : 'bud';
  let s = `<path d="M${x} ${y0} Q ${x + sway} ${y0 + len / 2} ${x + sway * 0.4} ${y0 + len}" stroke="#6a5a3a" stroke-width="1.4" fill="none" opacity=".55"/>`;
  const n = Math.floor(len / 6.5);
  for (let i = 0; i < n; i++) {
    const t = i / n, cx = x + sway * 2 * t * (1 - t) * 2 + sway * 0.4 * t * t, cy = y0 + t * len;
    if (R() < 0.07) {
      let p = ''; for (let k = 0; k < 6; k++) { const a = k * 60 + rr(-8, 8); p += `<ellipse cx="${f(cx)}" cy="${f(cy - 6.5)}" rx="3.6" ry="7.5" transform="rotate(${f(a)} ${f(cx)} ${f(cy)})" fill="url(#${g})"/>`; }
      s += `<g filter="url(#shadowS)">${p}<circle cx="${f(cx)}" cy="${f(cy)}" r="2" fill="#e2cf86"/></g>`; continue;
    }
    const side = (i % 3) - 1;
    const ang = side * rr(35, 65) + rr(-10, 10), ox = side * 3.2;
    s += `<g filter="url(#shadowS)"><ellipse cx="${f(cx + ox)}" cy="${f(cy)}" rx="4.1" ry="8.6" transform="rotate(${f(ang)} ${f(cx + ox)} ${f(cy)})" fill="url(#${g})"/><circle cx="${f(cx + ox * .3)}" cy="${f(cy + 5)}" r="1.6" fill="#7a8a4a" opacity=".8"/></g>`;
    if (opts.marigold && i % 30 === 15) s += marigold(cx, cy, 9);
  }
  return s;
}
function marigold(x, y, r) {
  let s = `<g filter="url(#shadowS)"><circle cx="${f(x)}" cy="${f(y)}" r="${r}" fill="url(#marigold)"/>`;
  for (let k = 0; k < 16; k++) { const a = rr(0, 6.28), d = rr(0, r * 0.75); s += `<circle cx="${f(x + Math.cos(a) * d)}" cy="${f(y + Math.sin(a) * d)}" r="${f(rr(r * .18, r * .32))}" fill="${R() < .5 ? '#ffb020' : '#e5760c'}" opacity=".9"/>`; }
  return s + '</g>';
}
function mangoLeaf(x, y, ang, len) {
  const w = len * 0.2;
  return `<g transform="translate(${f(x)} ${f(y)}) rotate(${f(ang)})" filter="url(#shadowS)">
   <path d="M0 0 C ${f(w)} ${f(len * .25)} ${f(w * .9)} ${f(len * .7)} 0 ${f(len)} C ${f(-w * .9)} ${f(len * .7)} ${f(-w)} ${f(len * .25)} 0 0Z" fill="url(#leaf)"/>
   <path d="M0 2 L0 ${f(len * .96)}" stroke="#a9c27a" stroke-width="1.4" opacity=".6"/>
   <path d="M${f(-w * .25)} ${f(len * .2)} Q ${f(-w * .1)} ${f(len * .45)} ${f(-w * .2)} ${f(len * .75)}" stroke="#d8f0a8" stroke-width="3" opacity=".18" fill="none"/></g>`;
}
function bananaPlant(x, base, h, dir) {
  let s = `<g filter="url(#shadow)">`;
  const top = base - h;
  // pseudostem with layered sheaths
  s += `<path d="M${x - 38} ${base} C ${x - 36} ${base - h * .5} ${x - 26} ${base - h * .85} ${x - 22} ${top} L ${x + 24} ${top} C ${x + 28} ${base - h * .85} ${x + 38} ${base - h * .5} ${x + 40} ${base}Z" fill="#7d9447"/>`;
  for (let i = 0; i < 9; i++) { const ox = -34 + i * 8.5; s += `<path d="M${x + ox} ${base} Q ${x + ox * .8} ${base - h * .55} ${x + ox * .62} ${top + 10}" stroke="${i % 2 ? '#5f7a34' : '#a3b56a'}" stroke-width="${rr(1.5, 4)}" fill="none" opacity=".55"/>`; }
  s += `<path d="M${x - 38} ${base} C ${x - 36} ${base - h * .5} ${x - 26} ${base - h * .85} ${x - 22} ${top} L ${x + 24} ${top} C ${x + 28} ${base - h * .85} ${x + 38} ${base - h * .5} ${x + 40} ${base}Z" fill="url(#cyl)"/>`;
  s += `<path d="M${x + 30} ${base - 20} Q ${x + 52} ${base - h * .3} ${x + 34} ${base - h * .55}" stroke="#9a7a44" stroke-width="10" fill="none" opacity=".7"/>`;
  const leaves = [[-82, 1.0, 1], [-52, 1.08, 1], [-22, .98, 0], [6, 1.0, 1], [26, .8, 1], [-108, .85, 1], [48, .62, 1]];
  leaves.forEach(([a, sc, droop], li) => {
    const ang = (a * dir + rr(-5, 5)) * Math.PI / 180, L = 560 * sc, W = L * .2;
    const ux = Math.sin(ang), uy = -Math.cos(ang);
    const p0 = [x, top], p1 = [x + ux * L * .45, top + uy * L * .55], p2 = [x + ux * L * .85, top + uy * L * .5 + (droop ? L * .15 : 0)], p3 = [x + ux * L * 1.02, top + uy * L * .2 + (droop ? L * .45 : L * .1)];
    const P = t => { const m = 1 - t; return [m*m*m*p0[0] + 3*m*m*t*p1[0] + 3*m*t*t*p2[0] + t*t*t*p3[0], m*m*m*p0[1] + 3*m*m*t*p1[1] + 3*m*t*t*p2[1] + t*t*t*p3[1]]; };
    const N = 44, pts = []; for (let i = 0; i <= N; i++) pts.push(P(i / N));
    const tears = new Set(); for (let k = 0; k < 3; k++) tears.add(Math.floor(rr(14, N - 4)));
    [-1, 1].forEach(side => {
      for (let i = 4; i < N; i++) {
        if (tears.has(i) && side === 1) continue;
        const [ax, ay] = pts[i], [bx, by] = pts[i + 1];
        const dx = bx - ax, dy = by - ay, d = Math.hypot(dx, dy) || 1, nx = -dy / d * side, ny = dx / d * side;
        const t = i / N, w = W * Math.sin(Math.PI * Math.min(1, t * 1.1)) ** .7 * (side > 0 ? 1 : .92);
        const sl = .28 * W; // veins run toward the tip
        const c = side > 0 ? (li % 2 ? '#5a9638' : '#4e8832') : (li % 2 ? '#3d7629' : '#356a25');
        s += `<path d="M${f(ax)} ${f(ay)} L ${f(bx)} ${f(by)} L ${f(bx + nx * w + dx / d * sl)} ${f(by + ny * w + dy / d * sl)} L ${f(ax + nx * w * .98 + dx / d * sl)} ${f(ay + ny * w * .98 + dy / d * sl)}Z" fill="${c}" stroke="${c}" stroke-width="1.6"/>`;
        if (i % 4 === 0) s += `<path d="M${f(ax)} ${f(ay)} L ${f(ax + nx * w + dx / d * sl)} ${f(ay + ny * w + dy / d * sl)}" stroke="#1f4416" stroke-width="1" opacity=".35"/>`;
      }
    });
    let mr = `M${f(pts[0][0])} ${f(pts[0][1])}`; pts.forEach(p => mr += ` L ${f(p[0])} ${f(p[1])}`);
    s += `<path d="${mr}" stroke="#d4e09a" stroke-width="4.5" fill="none" opacity=".75"/>`;
    if (li === 5 || li === 6) s += `<path d="${mr}" stroke="#9a7a3a" stroke-width="2" fill="none" opacity=".5"/>`;
  });
  return s + '</g>';
}
function pillar(x, top, bottom, w, opts = {}) {
  const hw = w / 2; let s = `<g filter="url(#shadow)">`;
  // plinth
  s += `<rect x="${x - hw * 1.55}" y="${bottom - 150}" width="${w * 1.55}" height="150" fill="url(#granite)"/><rect x="${x - hw * 1.55}" y="${bottom - 150}" width="${w * 1.55}" height="150" fill="url(#cyl)"/>`;
  s += `<rect x="${x - hw * 1.8}" y="${bottom - 160}" width="${w * 1.8}" height="16" fill="#8d857c"/><rect x="${x - hw * 1.8}" y="${bottom - 160}" width="${w * 1.8}" height="16" fill="url(#cyl)"/>`;
  // shaft
  s += `<rect x="${x - hw}" y="${top + 80}" width="${w}" height="${bottom - top - 240}" fill="url(#teak)"/>`;
  // carved bands
  const bands = opts.bands || [0.18, 0.5, 0.82];
  bands.forEach(t => {
    const by = top + 80 + (bottom - top - 240) * t;
    s += `<rect x="${x - hw * 1.18}" y="${by - 26}" width="${w * 1.18}" height="52" rx="8" fill="url(#teak)" filter="url(#carve)"/>`;
    for (let k = -2; k <= 2; k++) s += `<rect x="${x - hw * 1.18}" y="${by + k * 9 - 2}" width="${w * 1.18}" height="3" fill="#2a1408" opacity=".55"/>`;
    s += `<ellipse cx="${x}" cy="${by}" rx="${hw * .5}" ry="12" fill="#b07a3a" opacity=".35" filter="url(#carve)"/>`;
  });
  // lotus base flare
  s += `<path d="M${x - hw} ${bottom - 160} Q ${x - hw * 1.5} ${bottom - 200} ${x - hw * 1.05} ${bottom - 240} L ${x + hw * 1.05} ${bottom - 240} Q ${x + hw * 1.5} ${bottom - 200} ${x + hw} ${bottom - 160}Z" fill="url(#teak)" filter="url(#carve)"/>`;
  // capital + brackets
  s += `<path d="M${x - hw} ${top + 80} Q ${x - hw * 1.6} ${top + 50} ${x - hw * 1.3} ${top + 20} L ${x + hw * 1.3} ${top + 20} Q ${x + hw * 1.6} ${top + 50} ${x + hw} ${top + 80}Z" fill="url(#teak)" filter="url(#carve)"/>`;
  s += `<path d="M${x - hw * 1.3} ${top} h ${w * 2.6 / 2 * 2} v 24 h -${w * 2.6 / 2 * 2}Z" fill="url(#teak)"/>`;
  [-1, 1].forEach(d => {
    const bx = x + d * hw * 1.2;
    s += `<path d="M${bx} ${top + 4} q ${d * 60} 0 ${d * 92} 22 q ${d * 6} 18 ${-d * 10} 26 q ${-d * 30} 6 ${-d * 46} 30 q ${-d * 10} 12 ${-d * 36} 6Z" fill="url(#teak)" filter="url(#carve)"/>`;
  });
  s += `<rect x="${x - hw}" y="${top + 80}" width="${w}" height="${bottom - top - 240}" fill="url(#cyl)"/>`;
  return s + '</g>';
}
function kundulu(x, base, h, id) {
  // tall standing brass lamp with a five-wick cup
  let s = `<g filter="url(#shadow)">`;
  s += `<ellipse cx="${x}" cy="${base}" rx="${h * .22}" ry="${h * .045}" fill="#1c1006" opacity=".45" filter="url(#blur8)"/>`;
  s += `<path d="M${x - h * .2} ${base} Q ${x - h * .2} ${base - h * .1} ${x - h * .05} ${base - h * .14} L ${x + h * .05} ${base - h * .14} Q ${x + h * .2} ${base - h * .1} ${x + h * .2} ${base}Z" fill="url(#brassCyl)"/>`;
  s += `<rect x="${x - h * .022}" y="${base - h * .86}" width="${h * .044}" height="${h * .74}" fill="url(#brassCyl)"/>`;
  [.25, .45, .62, .78].forEach((t, i) => { const yy = base - h * t, rx = h * (i % 2 ? .05 : .065); s += `<ellipse cx="${x}" cy="${f(yy)}" rx="${f(rx)}" ry="${f(rx * .55)}" fill="url(#brassCyl)"/>`; });
  // cup
  const cy = base - h * .9, cw = h * .2;
  s += `<path d="M${x - cw} ${cy} Q ${x - cw * .8} ${cy + h * .07} ${x} ${cy + h * .075} Q ${x + cw * .8} ${cy + h * .07} ${x + cw} ${cy}Z" fill="url(#brassCyl)"/>`;
  s += `<ellipse cx="${x}" cy="${cy}" rx="${cw}" ry="${h * .022}" fill="#e8c27a"/><ellipse cx="${x}" cy="${cy}" rx="${cw * .9}" ry="${h * .016}" fill="#6b4a1a"/>`;
  // finial (a stylised swan-less lotus bud)
  s += `<path d="M${x} ${cy - h * .16} q ${h * .05} ${h * .07} 0 ${h * .12} q ${-h * .05} ${-h * .05} 0 ${-h * .12}Z" fill="url(#brassCyl)"/><rect x="${x - 3}" y="${cy - h * .05}" width="6" height="${h * .05}" fill="url(#brassCyl)"/>`;
  [-0.85, -0.45, 0.45, 0.85].forEach(t => { META.flames.push({ id, x: x + cw * t, y: cy - 2, s: h / 330 }); s += `<path d="M${f(x + cw * t)} ${cy} l 0 -6" stroke="#2a1a0a" stroke-width="2"/>`; });
  return s + '</g>';
}
function diya(x, y, sc, id) {
  META.flames.push({ id, x, y: y - 9 * sc, s: sc * 0.62 });
  return `<g filter="url(#shadowS)"><ellipse cx="${x}" cy="${y + 6 * sc}" rx="${26 * sc}" ry="${6 * sc}" fill="#120804" opacity=".5" filter="url(#soft)"/>
  <path d="M${x - 24 * sc} ${y - 4 * sc} Q ${x - 18 * sc} ${y + 10 * sc} ${x} ${y + 10 * sc} Q ${x + 22 * sc} ${y + 10 * sc} ${x + 30 * sc} ${y - 6 * sc} L ${x + 12 * sc} ${y - 3 * sc}Z" fill="url(#brassCyl)"/>
  <ellipse cx="${x - 2 * sc}" cy="${y - 4 * sc}" rx="${22 * sc}" ry="${5 * sc}" fill="#e7bd6f"/><ellipse cx="${x - 2 * sc}" cy="${y - 4 * sc}" rx="${18 * sc}" ry="${3.6 * sc}" fill="#5a3a10"/>
  <path d="M${x} ${y - 4 * sc} l 0 ${-5 * sc}" stroke="#2a1a0a" stroke-width="${2 * sc}"/></g>`;
}
function tiles(y, x0, x1, h, dark) {
  let s = `<rect x="${x0}" y="${y}" width="${x1 - x0}" height="${h}" fill="url(#terra)"/>`;
  for (let r = 0; r < 4; r++) { const yy = y + r * h / 4; s += `<rect x="${x0}" y="${yy}" width="${x1 - x0}" height="3" fill="#3a1608" opacity=".35"/>`; }
  for (let xx = x0; xx < x1; xx += 34) {
    s += `<path d="M${xx} ${y + h} a 17 12 0 0 0 34 0 v -${h} h -34Z" fill="url(#terra)"/><path d="M${xx} ${y + h} a 17 12 0 0 0 34 0" fill="none" stroke="#3a1608" stroke-width="2" opacity=".55"/><rect x="${xx + 22}" y="${y}" width="10" height="${h}" fill="#fff" opacity=".07"/><rect x="${xx}" y="${y}" width="5" height="${h}" fill="#000" opacity=".18"/>`;
  }
  if (dark) s += `<rect x="${x0}" y="${y}" width="${x1 - x0}" height="${h + 14}" fill="#2a1430" opacity="${dark}"/>`;
  return s;
}
function muggu(cx, cy, rx, ry) {
  // a lotus muggu in perspective: dot grid + petals + border loops, rice-flour white with turmeric/kumkum fills
  let s = `<g transform="translate(${cx} ${cy}) scale(1 ${ry / rx})">`;
  s += `<circle r="${rx}" fill="none" stroke="#f4ecd8" stroke-width="5" opacity=".85"/><circle r="${rx * .93}" fill="none" stroke="#f4ecd8" stroke-width="2.5" opacity=".8"/>`;
  for (let k = 0; k < 36; k++) { const a = k / 36 * 6.283, x = Math.cos(a) * rx * .965, y = Math.sin(a) * rx * .965; s += `<circle cx="${f(x)}" cy="${f(y)}" r="7" fill="${k % 2 ? '#c8261c' : '#e8a92a'}"/>`; }
  [[.8, 16, '#e8a92a'], [.6, 12, '#c8261c'], [.42, 8, '#4f8a3a']].forEach(([rf, n, col]) => {
    const r = rx * rf;
    for (let k = 0; k < n; k++) {
      const a = k / n * 360;
      s += `<path d="M0 0 Q ${f(r * .28)} ${f(-r * .5)} 0 ${f(-r)} Q ${f(-r * .28)} ${f(-r * .5)} 0 0Z" transform="rotate(${f(a)})" fill="${col}" stroke="#f6eedb" stroke-width="3.5" opacity=".92"/>`;
    }
  });
  for (let i = -4; i <= 4; i++) for (let j = -4; j <= 4; j++) { if (i * i + j * j > 18) continue; s += `<circle cx="${i * rx * .05}" cy="${j * rx * .05}" r="3.5" fill="#fbf6ea"/>`; }
  s += `<circle r="${rx * .12}" fill="#c8261c" stroke="#f6eedb" stroke-width="4"/>`;
  for (let k = 0; k < 24; k++) { const a = k / 24 * 6.283, x = Math.cos(a) * rx * .87, y = Math.sin(a) * rx * .87; s += `<circle cx="${f(x)}" cy="${f(y)}" r="${rx * .045}" fill="none" stroke="#f4ecd8" stroke-width="3"/>`; }
  return s + `</g>`;
}
function kalasam(x, base, sc) {
  let s = `<g filter="url(#shadow)" transform="translate(${x} ${base}) scale(${sc})">`;
  s += `<ellipse cx="0" cy="0" rx="90" ry="18" fill="#140a04" opacity=".5" filter="url(#blur8)"/>`;
  s += `<path d="M-70 -10 Q -95 -80 -55 -120 L -40 -135 L 40 -135 L 55 -120 Q 95 -80 70 -10 Q 0 6 -70 -10Z" fill="url(#brassCyl)"/>`;
  s += `<rect x="-46" y="-150" width="92" height="18" rx="6" fill="url(#brassCyl)"/>`;
  s += `<path d="M-70 -60 Q 0 -45 70 -60" stroke="#7a1a12" stroke-width="9" fill="none" opacity=".8"/>`;
  for (let k = 0; k < 9; k++) { s += mangoLeaf(0, -150, -100 + k * 25, 92); }
  s += `<ellipse cx="0" cy="-205" rx="46" ry="52" fill="#7a5530"/><ellipse cx="0" cy="-205" rx="46" ry="52" fill="url(#cyl)"/>`;
  for (let k = 0; k < 14; k++) s += `<path d="M${-40 + k * 6} -250 q ${rr(-4, 4)} 40 ${rr(-2, 2)} 90" stroke="#4a3018" stroke-width="2" opacity=".5" fill="none"/>`;
  s += `<path d="M-46 -205 Q 0 -190 46 -205" stroke="#e8a92a" stroke-width="6" fill="none"/><circle cx="0" cy="-198" r="7" fill="#c8261c"/>`;
  return s + '</g>';
}
function urli(x, y, sc) {
  let s = `<g filter="url(#shadow)" transform="translate(${x} ${y}) scale(${sc})"><ellipse rx="150" ry="40" cy="10" fill="#140a04" opacity=".5" filter="url(#blur8)"/>
  <path d="M-140 -10 Q -120 50 0 52 Q 120 50 140 -10Z" fill="url(#brassCyl)"/><ellipse rx="140" ry="34" cy="-10" fill="#e3b866"/><ellipse rx="128" ry="28" cy="-10" fill="#3a2a1a"/>`;
  for (let k = 0; k < 14; k++) { const a = rr(0, 6.28), d = rr(10, 100); const px = Math.cos(a) * d, py = -10 + Math.sin(a) * d * .22; s += k % 3 ? marigold(px, py, 11) : `<g>${[0, 72, 144, 216, 288].map(r => `<ellipse cx="${f(px)}" cy="${f(py - 6)}" rx="5" ry="10" transform="rotate(${r} ${f(px)} ${f(py)})" fill="url(#bud)"/>`).join('')}</g>`; }
  return s + '</g>';
}
function tulasiKota(x, base) {
  const w = 230; let s = `<g filter="url(#shadow)">`;
  s += `<ellipse cx="${x}" cy="${base}" rx="${w * .8}" ry="26" fill="#140a04" opacity=".45" filter="url(#blur8)"/>`;
  // stepped base
  s += `<rect x="${x - w * .62}" y="${base - 40}" width="${w * 1.24}" height="40" fill="url(#lime)"/><rect x="${x - w * .62}" y="${base - 40}" width="${w * 1.24}" height="40" fill="url(#cyl)"/>`;
  s += `<rect x="${x - w * .54}" y="${base - 72}" width="${w * 1.08}" height="34" fill="url(#lime)"/><rect x="${x - w * .54}" y="${base - 72}" width="${w * 1.08}" height="10" fill="#c8261c" opacity=".85"/>`;
  // body
  s += `<path d="M${x - w * .42} ${base - 72} L ${x - w * .36} ${base - 300} L ${x + w * .36} ${base - 300} L ${x + w * .42} ${base - 72}Z" fill="url(#lime)"/>`;
  s += `<path d="M${x - w * .42} ${base - 72} L ${x - w * .36} ${base - 300} L ${x + w * .36} ${base - 300} L ${x + w * .42} ${base - 72}Z" fill="url(#cyl)" opacity=".8"/>`;
  s += `<path d="M${x - w * .38} ${base - 92} L ${x + w * .38} ${base - 92}" stroke="#e8a92a" stroke-width="12"/><path d="M${x - w * .37} ${base - 280} L ${x + w * .37} ${base - 280}" stroke="#e8a92a" stroke-width="10"/>`;
  // niche (for a lamp)
  s += `<path d="M${x - 34} ${base - 112} L ${x - 34} ${base - 190} Q ${x} ${base - 236} ${x + 34} ${base - 190} L ${x + 34} ${base - 112}Z" fill="#3a1d10"/>`;
  s += `<path d="M${x - 44} ${base - 106} L ${x - 44} ${base - 192} Q ${x} ${base - 250} ${x + 44} ${base - 192} L ${x + 44} ${base - 106}" fill="none" stroke="#c8261c" stroke-width="7"/>`;
  META.flames.push({ id: 'kota', x, y: base - 140, s: 0.55 });
  s += `<ellipse cx="${x}" cy="${base - 128}" rx="16" ry="5" fill="url(#brassCyl)"/>`;
  // kumkum and turmeric dots on body
  for (let i = 0; i < 2; i++) { const px = x + (i ? 1 : -1) * w * .26; s += `<circle cx="${px}" cy="${base - 210}" r="10" fill="#e8a92a"/><circle cx="${px}" cy="${base - 210}" r="5" fill="#c8261c"/>`; }
  // top rim
  s += `<rect x="${x - w * .46}" y="${base - 322}" width="${w * .92}" height="26" rx="4" fill="url(#lime)"/><rect x="${x - w * .46}" y="${base - 322}" width="${w * .92}" height="26" rx="4" fill="url(#cyl)" opacity=".7"/><rect x="${x - w * .46}" y="${base - 300}" width="${w * .92}" height="5" fill="#c8261c"/>`;
  // tulasi plant: clustered small leaves on fine stems
  const top = base - 322;
  for (let k = 0; k < 13; k++) {
    const sx = x + rr(-60, 60), ex = sx + rr(-70, 70), ey = top - rr(60, 165);
    s += `<path d="M${f(sx)} ${top} Q ${f((sx + ex) / 2 + rr(-15, 15))} ${f((top + ey) / 2)} ${f(ex)} ${f(ey)}" stroke="#4a3a20" stroke-width="2.5" fill="none"/>`;
    for (let j = 0; j < 10; j++) {
      const t = j / 10 * 0.8 + 0.2, px = sx + (ex - sx) * t, py = top + (ey - top) * t;
      [-1, 1].forEach(d => { const a = d * rr(30, 70); s += `<ellipse cx="${f(px + d * 7)}" cy="${f(py)}" rx="5" ry="10" transform="rotate(${f(a)} ${f(px + d * 7)} ${f(py)})" fill="${R() < .5 ? '#3d6b2a' : '#2f5a22'}"/>`; });
    }
    for (let j = 0; j < 4; j++) s += `<circle cx="${f(ex + rr(-4, 4))}" cy="${f(ey - j * 6)}" r="3.4" fill="#6b4a6a"/>`; // purple flower spikes (krishna tulasi tinge)
  }
  return s + '</g>';
}

// ---------- layers ----------
function layerC() {
  let s = '';
  // sky
  s += `<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#231f3d"/><stop offset=".45" stop-color="#5a3d5a"/><stop offset=".8" stop-color="#c8784e"/><stop offset="1" stop-color="#f0ae68"/></linearGradient>`;
  s += `<rect width="2400" height="600" fill="url(#sky)"/>`;
  for (let i = 0; i < 9; i++) s += `<ellipse cx="${rr(0, 2400)}" cy="${rr(120, 360)}" rx="${rr(140, 380)}" ry="${rr(14, 34)}" fill="#f2a27a" opacity="${rr(.08, .2)}" filter="url(#blur30)"/>`;
  s += `<circle cx="1640" cy="170" r="22" fill="#fbe7c0" opacity=".9"/><circle cx="1652" cy="162" r="20" fill="#3a2c4c"/>`; // crescent moon
  // palm silhouettes beyond the far roof (fronds with leaflets)
  [[420, 1.1], [1500, .95], [2080, 1.2], [930, .8], [1760, .7]].forEach(([px, sc]) => {
    const col = '#2b1f2e';
    s += `<g opacity=".9"><path d="M${px} 520 Q ${px + 24 * sc} 380 ${px + 12 * sc} ${520 - 270 * sc}" stroke="${col}" stroke-width="${f(11 * sc)}" fill="none"/>`;
    const tx = px + 12 * sc, ty = 520 - 270 * sc;
    for (let k = 0; k < 12; k++) {
      const a = -175 + k * 15.5 + rr(-6, 6), L = rr(120, 175) * sc, rad = a * Math.PI / 180;
      const ex = tx + Math.cos(rad) * L, ey = ty + Math.sin(rad) * L * .55 + L * .42, mx = (tx + ex) / 2, my = ty + (ey - ty) * .05 - 26 * sc;
      s += `<path d="M${f(tx)} ${f(ty)} Q ${f(mx)} ${f(my)} ${f(ex)} ${f(ey)}" stroke="${col}" stroke-width="${f(3.2 * sc)}" fill="none"/>`;
      for (let j = 2; j < 14; j++) { const t = j / 14, qx = (1 - t) ** 2 * tx + 2 * (1 - t) * t * mx + t * t * ex, qy = (1 - t) ** 2 * ty + 2 * (1 - t) * t * my + t * t * ey; const ll = (1 - t * .6) * 38 * sc; [-1, 1].forEach(d => s += `<path d="M${f(qx)} ${f(qy)} q ${f(d * ll * .4)} ${f(ll * .3)} ${f(d * ll * .25)} ${f(ll)}" stroke="${col}" stroke-width="${f(2 * sc)}" fill="none"/>`); }
    }
    s += `</g>`;
  });
  // far roof
  s += tiles(430, 0, 2400, 80, .32);
  s += `<rect y="520" width="2400" height="70" fill="#2e1a10"/>`;
  for (let x = 10; x < 2400; x += 60) s += `<rect x="${x}" y="520" width="22" height="34" fill="url(#teak)"/><rect x="${x}" y="520" width="22" height="34" fill="#000" opacity=".35"/>`;
  s += `<rect y="570" width="2400" height="26" fill="url(#teakH)"/><rect y="570" width="2400" height="26" fill="#000" opacity=".25"/>`;
  // back wall
  s += `<rect y="596" width="2400" height="740" fill="url(#lime)"/>`;
  s += `<linearGradient id="wallShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a160a" stop-opacity=".55"/><stop offset=".25" stop-color="#2a160a" stop-opacity=".12"/><stop offset="1" stop-color="#2a160a" stop-opacity=".18"/></linearGradient><rect y="596" width="2400" height="740" fill="url(#wallShade)"/>`;
  // kaavi dado
  s += `<rect y="1196" width="2400" height="140" fill="#a8432a"/><rect y="1196" width="2400" height="140" fill="url(#lime)" opacity=".18" style="mix-blend-mode:multiply"/><rect y="1190" width="2400" height="8" fill="#f2e6cc"/><rect y="1206" width="2400" height="4" fill="#f2e6cc" opacity=".7"/>`;
  for (let x = 20; x < 2400; x += 40) s += `<circle cx="${x}" cy="1222" r="4" fill="#f2e6cc" opacity=".8"/>`;
  // side doors
  [430, 1970].forEach(dx => {
    s += `<rect x="${dx - 110}" y="780" width="220" height="420" fill="#1a0d06"/><linearGradient id="dd${dx}" x1="0" x2="1"><stop offset="0" stop-color="#4a2410" stop-opacity=".6"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient><rect x="${dx - 100}" y="790" width="200" height="410" fill="url(#dd${dx})"/>`;
    s += `<rect x="${dx - 132}" y="760" width="26" height="440" fill="url(#teak)" filter="url(#carve)"/><rect x="${dx + 106}" y="760" width="26" height="440" fill="url(#teak)" filter="url(#carve)"/><rect x="${dx - 146}" y="740" width="292" height="40" fill="url(#teakH)" filter="url(#carve)"/>`;
    for (let k = 0; k < 9; k++) s += mangoLeaf(dx - 120 + k * 30, 780, rr(-10, 10), 54);
  });
  // wall niches with lamps (desktop)
  [700, 1700].forEach((nx, i) => {
    s += `<path d="M${nx - 36} 1010 L ${nx - 36} 940 Q ${nx} 895 ${nx + 36} 940 L ${nx + 36} 1010Z" fill="#3a1d10"/><path d="M${nx - 44} 1014 L ${nx - 44} 938 Q ${nx} 884 ${nx + 44} 938 L ${nx + 44} 1014" fill="none" stroke="#e8a92a" stroke-width="5"/>`;
    s += diya(nx, 1000, .8, 'niche');
  });
  // far pillars
  [130, 640, 1760, 2270].forEach(px => s += pillar(px, 596, 1340, 58, { bands: [.25, .7] }));
  // portrait frame (photo window is cut by the page: x1030-1370, y763-1047)
  s += `<path d="M1200 672 L 1020 728 M1200 672 L 1380 728" stroke="#5a4020" stroke-width="2.5"/><circle cx="1200" cy="672" r="7" fill="url(#brassCyl)"/>`;
  s += `<g filter="url(#shadow)"><path d="M990 725 h420 v360 h-420Z M1030 763 v284 h340 v-284Z" fill-rule="evenodd" fill="url(#teak)" filter="url(#carve)"/></g>`;
  s += `<path d="M1006 741 h388 v328 h-388Z" fill="none" stroke="#2a1408" stroke-width="3" opacity=".6"/><path d="M1022 755 h356 v300 h-356Z" fill="none" stroke="#d9a64a" stroke-width="4"/>`;
  for (let k = 0; k < 4; k++) { const cx = k % 2 ? 1390 : 1010, cy = k > 1 ? 1065 : 745; s += `<circle cx="${cx}" cy="${cy}" r="11" fill="url(#brassCyl)"/>`; }
  s += `<rect x="1030" y="763" width="340" height="284" fill="#2a1a10"/>`;
  // garland: across the top edge, down both sides outside the frame, swag under the frame
  s += jasmineStrand(992, 716, 0) ;
  s += `<g>`;
  for (let i = 0; i <= 50; i++) { const t = i / 50, x = 994 + t * 412, y = 718 + Math.sin(t * Math.PI) * 10; s += `<ellipse cx="${f(x)}" cy="${f(y)}" rx="4" ry="8" transform="rotate(${i % 2 ? 60 : -60} ${f(x)} ${f(y)})" fill="url(#bud)" filter="url(#shadowS)"/>`; if (i % 10 === 5) s += marigold(x, y + 2, 10); }
  s += jasmineStrand(980, 726, 360, { sway: -6, marigold: true });
  s += jasmineStrand(1420, 726, 360, { sway: 6, marigold: true });
  for (let i = 0; i <= 60; i++) { const t = i / 60, x = 982 + t * 436, y = 1088 + Math.sin(t * Math.PI) * 52; s += `<ellipse cx="${f(x)}" cy="${f(y)}" rx="4" ry="8" transform="rotate(${i % 2 ? 50 : -50} ${f(x)} ${f(y)})" fill="url(#bud)" filter="url(#shadowS)"/>`; if (i % 12 === 6) s += marigold(x, y + 3, 11); }
  s += jasmineStrand(982, 1090, 110, { sway: 3 }) + jasmineStrand(1418, 1090, 110, { sway: -3 });
  s += `</g>`;
  // kundulu either side of the portrait
  s += kundulu(930, 1336, 330, 'kundulu');
  s += kundulu(1470, 1336, 330, 'kundulu');
  // verandah floor, step, courtyard floor
  s += `<rect y="1336" width="2400" height="70" fill="url(#oxide)"/><linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd2a0" stop-opacity=".25"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></linearGradient><rect y="1336" width="2400" height="70" fill="url(#sheen)"/>`;
  s += `<rect y="1404" width="2400" height="40" fill="url(#granite)"/><rect y="1404" width="2400" height="6" fill="#d8cfc2" opacity=".6"/><rect y="1440" width="2400" height="8" fill="#000" opacity=".35"/>`;
  s += `<rect y="1446" width="2400" height="360" fill="url(#granite)"/><rect y="1446" width="2400" height="360" fill="#7a5a48" opacity=".35" style="mix-blend-mode:multiply"/>`;
  for (let k = -14; k <= 14; k++) s += `<path d="M${1200 + k * 60} 1446 L ${1200 + k * 230} 1800" stroke="#3a3028" stroke-width="2" opacity=".35"/>`;
  [1500, 1580, 1680].forEach(y => s += `<path d="M0 ${y} H2400" stroke="#3a3028" stroke-width="2" opacity=".3"/>`);
  s += `<linearGradient id="floorShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a0e08" stop-opacity=".5"/><stop offset="1" stop-color="#1a0e08" stop-opacity=".1"/></linearGradient><rect y="1446" width="2400" height="360" fill="url(#floorShade)"/>`;
  s += muggu(1200, 1712, 470, 96);
  s += tulasiKota(1200, 1660);
  [[1000, 1688], [1090, 1716], [1310, 1716], [1400, 1688], [1200, 1748]].forEach(([x, y]) => s += diya(x, y, 1.05, 'courtyard'));
  // ambient dusk dim
  s += `<radialGradient id="vig" cx=".5" cy=".55" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#0a0405" stop-opacity=".55"/></radialGradient><rect width="2400" height="1800" fill="url(#vig)"/>`;
  return s;
}
function layerB() {
  let s = '';
  // near ceiling / eave seen from inside
  s += `<rect width="2400" height="210" fill="url(#teakH)"/><rect width="2400" height="210" fill="#120804" opacity=".45"/>`;
  for (let x = -40; x < 2440; x += 110) s += `<path d="M${x} 0 L ${x + 30} 0 L ${1200 + (x - 1200) * 1.06 + 30} 196 L ${1200 + (x - 1200) * 1.06} 196Z" fill="url(#teak)"/><path d="M${x} 0 L ${x + 8} 0 L ${1200 + (x - 1200) * 1.06 + 8} 196 L ${1200 + (x - 1200) * 1.06} 196Z" fill="#000" opacity=".4"/>`;
  s += `<g filter="url(#shadow)"><rect y="190" width="2400" height="62" fill="url(#teakH)" filter="url(#carve)"/>`;
  for (let k = 0; k < 4; k++) s += `<rect y="${200 + k * 13}" width="2400" height="3" fill="#2a1408" opacity=".55"/>`;
  for (let x = 60; x < 2400; x += 120) s += `<path d="M${x - 12} 252 h24 l -4 30 q -8 18 -16 0Z" fill="url(#teak)" filter="url(#carve)"/><circle cx="${x}" cy="292" r="6" fill="url(#brassCyl)"/>`;
  s += `</g>`;
  // baked jasmine strands (the page adds a few live, swaying ones on top)
  for (let x = 40; x < 2400; x += 52) { if (x > 860 && x < 1540 && R() < .35) continue; s += jasmineStrand(x + rr(-10, 10), 250, rr(90, 230), { sway: rr(-5, 5), marigold: R() < .3 }); }
  // near pillars
  [300, 820, 1580, 2100].forEach(px => s += pillar(px, 196, 1880, 104));
  // near verandah floor edge
  s += `<path d="M0 1690 H2400 V1800 H0Z" fill="url(#oxide)"/><rect y="1690" width="2400" height="110" fill="url(#sheen)"/><rect y="1676" width="2400" height="22" fill="url(#granite)"/><rect y="1676" width="2400" height="4" fill="#e2d8cc" opacity=".6"/>`;
  s += `<linearGradient id="floorB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".1"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient><rect y="1690" width="2400" height="110" fill="url(#floorB)"/>`;
  s += kalasam(960, 1752, .78);
  s += urli(1452, 1748, .62);
  return s;
}
function layerA() {
  let s = '';
  // facade with door opening x900–1500, y300–1720
  s += `<path d="M0 0 H2400 V1800 H0Z M900 300 V1720 H1500 V300Z" fill-rule="evenodd" fill="url(#facade)"/>`;
  s += `<path d="M0 0 H2400 V1800 H0Z M900 300 V1720 H1500 V300Z" fill-rule="evenodd" fill="#3a1e24" opacity=".42"/>`;
  s += `<radialGradient id="porch" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="#ffb060" stop-opacity=".18"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></radialGradient><path d="M0 0 H2400 V1800 H0Z M900 300 V1720 H1500 V300Z" fill-rule="evenodd" fill="url(#porch)"/>`;
  // eave of the front roof
  s += tiles(0, 0, 2400, 96, .25);
  s += `<rect y="96" width="2400" height="40" fill="#24140c"/>`;
  for (let x = 14; x < 2400; x += 64) s += `<rect x="${x}" y="96" width="22" height="30" fill="url(#teak)"/><rect x="${x}" y="96" width="22" height="30" fill="#000" opacity=".3"/>`;
  s += `<linearGradient id="eaveShadow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#150a10" stop-opacity=".75"/><stop offset="1" stop-color="#150a10" stop-opacity="0"/></linearGradient><rect y="136" width="2400" height="220" fill="url(#eaveShadow)"/>`;
  // arugu: raised sitting platforms either side of the door
  [[0, 800], [1600, 2400]].forEach(([x0, x1]) => {
    s += `<rect x="${x0}" y="1488" width="${x1 - x0}" height="40" fill="url(#oxide)"/><rect x="${x0}" y="1488" width="${x1 - x0}" height="40" fill="url(#sheen)"/>`;
    s += `<rect x="${x0}" y="1526" width="${x1 - x0}" height="14" fill="url(#granite)"/>`;
    s += `<rect x="${x0}" y="1540" width="${x1 - x0}" height="200" fill="url(#facade)"/><rect x="${x0}" y="1540" width="${x1 - x0}" height="200" fill="#1c1030" opacity=".3"/>`;
    s += `<rect x="${x0}" y="1640" width="${x1 - x0}" height="100" fill="#9a3c26"/><rect x="${x0}" y="1636" width="${x1 - x0}" height="6" fill="#efe2c6"/>`;
    for (let x = x0 + 20; x < x1; x += 46) s += `<circle cx="${x}" cy="1590" r="9" fill="#e3a62a"/><circle cx="${x}" cy="1590" r="4" fill="#c01e16"/>`;
    s += `<rect x="${x0}" y="1540" width="${x1 - x0}" height="200" fill="#000" opacity=".22"/>`;
  });
  // hanging brass lamps on chains (wider screens)
  [640, 1760].forEach(hx => {
    s += `<path d="M${hx} 136 V 860" stroke="#8a6a2a" stroke-width="4" stroke-dasharray="10 5"/>`;
    s += `<g filter="url(#shadow)"><path d="M${hx - 60} 880 Q ${hx} 960 ${hx + 60} 880Z" fill="url(#brassCyl)"/><ellipse cx="${hx}" cy="880" rx="60" ry="12" fill="#e8c27a"/><ellipse cx="${hx}" cy="880" rx="52" ry="8" fill="#5a3a10"/><path d="M${hx} 960 v 40" stroke="url(#brassCyl)" stroke-width="8"/><circle cx="${hx}" cy="1008" r="10" fill="url(#brassCyl)"/></g>`;
    [-40, 0, 40].forEach(o => META.flames.push({ id: 'door', x: hx + o, y: 874, s: .62 }));
  });
  // frame and lintel
  s += `<g filter="url(#shadow)"><rect x="828" y="226" width="72" height="1500" fill="url(#teak)" filter="url(#carve)"/><rect x="1500" y="226" width="72" height="1500" fill="url(#teak)" filter="url(#carve)"/>`;
  s += `<rect x="790" y="196" width="820" height="112" fill="url(#teakH)" filter="url(#carve)"/>`;
  for (let k = 0; k < 3; k++) { s += `<rect x="790" y="${210 + k * 30}" width="820" height="3" fill="#2a1408" opacity=".5"/>`; }
  for (let x = 840; x < 1580; x += 70) s += `<circle cx="${x}" cy="252" r="14" fill="#8a5428" filter="url(#carve)"/><circle cx="${x}" cy="252" r="5" fill="url(#brassCyl)"/>`;
  s += `<g transform="translate(1200 252)"><ellipse rx="70" ry="44" fill="#7a4522" filter="url(#carve)"/>${[0, 45, 90, 135, 180, 225, 270, 315].map(a => `<ellipse cx="0" cy="-22" rx="11" ry="22" transform="rotate(${a})" fill="#a8693a" filter="url(#carve)"/>`).join('')}<circle r="12" fill="url(#brassCyl)"/></g>`;
  for (let y = 360; y < 1700; y += 180) { s += `<rect x="842" y="${y}" width="44" height="120" rx="6" fill="none" stroke="#2a1408" stroke-width="3" opacity=".5"/><rect x="1514" y="${y}" width="44" height="120" rx="6" fill="none" stroke="#2a1408" stroke-width="3" opacity=".5"/>`; }
  s += `</g>`;
  // turmeric and kumkum on the frame base (gadapa) and threshold
  s += `<rect x="828" y="1600" width="72" height="120" fill="#e3a62a" opacity=".9"/><rect x="1500" y="1600" width="72" height="120" fill="#e3a62a" opacity=".9"/>`;
  [864, 1536].forEach(x => { [1630, 1690].forEach(y => s += `<circle cx="${x}" cy="${y}" r="9" fill="#c01e16"/>`); });
  s += `<rect x="800" y="1716" width="800" height="90" fill="url(#granite)"/><rect x="800" y="1716" width="800" height="90" fill="#e8ad2c" opacity=".88"/><rect x="800" y="1716" width="800" height="10" fill="#fff4d0" opacity=".5"/>`;
  for (let x = 840; x < 1580; x += 52) s += `<circle cx="${x}" cy="1762" r="10" fill="#c01e16"/>`;
  s += diya(870, 1735, 1.0, 'door') + diya(1530, 1735, 1.0, 'door');
  // thoranam: mango leaves with marigolds on a cord across the lintel
  s += `<path d="M880 310 Q 1200 330 1520 310" stroke="#5a4020" stroke-width="3" fill="none"/>`;
  for (let i = 0; i < 23; i++) { const t = i / 22, x = 880 + t * 640, y = 310 + Math.sin(t * Math.PI) * 18; s += mangoLeaf(x, y, rr(-8, 8) + (t - .5) * 10, rr(118, 150)); }
  for (let i = 0; i < 12; i++) { const t = (i + .5) / 12, x = 880 + t * 640, y = 312 + Math.sin(t * Math.PI) * 18; s += marigold(x, y, 13); }
  // banana plants
  s += bananaPlant(760, 1770, 560, 1) + bananaPlant(1640, 1770, 560, -1);
  return s;
}
function door(side) {
  // a single carved teak door leaf, 300 x 1420
  const W = 300, H = 1420; let s = `<rect width="${W}" height="${H}" fill="url(#teak)"/>`;
  s += `<rect width="${W}" height="${H}" fill="#140804" opacity=".25"/>`;
  const rows = [[30, 230], [290, 330], [650, 330], [1010, 380]];
  rows.forEach(([y, h], ri) => {
    s += `<rect x="28" y="${y}" width="${W - 56}" height="${h}" rx="4" fill="url(#teak)" filter="url(#carve)"/>`;
    s += `<rect x="46" y="${y + 18}" width="${W - 92}" height="${h - 36}" rx="3" fill="#000" opacity=".22"/><rect x="52" y="${y + 24}" width="${W - 104}" height="${h - 48}" rx="3" fill="url(#teak)" filter="url(#carve)"/>`;
    const cx = W / 2, cy = y + h / 2;
    if (ri === 0) s += `<path d="M60 ${y + h - 30} Q ${cx} ${y + 20} ${W - 60} ${y + h - 30}" fill="none" stroke="#c99a52" stroke-width="5" opacity=".75"/>`;
    s += `<g transform="translate(${cx} ${cy})" filter="url(#carve)">${[0, 45, 90, 135, 180, 225, 270, 315].map(a => `<ellipse cx="0" cy="-26" rx="12" ry="26" transform="rotate(${a})" fill="#8f5a2c"/>`).join('')}<circle r="14" fill="url(#brassCyl)"/></g>`;
  });
  for (let y = 60; y < H; y += 120) [14, W - 14].forEach(x => s += `<circle cx="${x}" cy="${y}" r="7" fill="url(#brassCyl)" filter="url(#shadowS)"/>`);
  const kx = side === 'l' ? W - 50 : 50;
  s += `<g filter="url(#shadow)"><circle cx="${kx}" cy="760" r="16" fill="url(#brassCyl)"/><circle cx="${kx}" cy="808" r="34" fill="none" stroke="url(#brassCyl)" stroke-width="9"/></g>`;
  s += `<rect width="${W}" height="${H}" fill="url(#cyl)" opacity=".35"/>`;
  if (side === 'r') s = `<g transform="translate(${W} 0) scale(-1 1)">${s}</g>`;
  return { s, W, H };
}

async function render(page, name, w, h, body, transparent) {
  const html = `<!doctype html><html><head><style>html,body{margin:0;background:transparent}svg{display:block}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${defs()}${body}</svg></body></html>`;
  const file = path.join(OUT, name + '.html'); fs.writeFileSync(file, html);
  await page.setViewportSize({ width: w, height: h });
  await page.goto('file://' + file, { waitUntil: 'load' });
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(OUT, name + '.png'), omitBackground: transparent, clip: { x: 0, y: 0, width: w, height: h } });
  console.log('rendered', name);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const only = process.argv[2];
  const C = layerC(), B = layerB(), A = layerA();
  if (!only || only === 'C') await render(page, 'layer-c', 2400, 1800, C, false);
  if (!only || only === 'B') await render(page, 'layer-b', 2400, 1800, B, true);
  if (!only || only === 'A') await render(page, 'layer-a', 2400, 1800, A, true);
  if (!only || only === 'D') {
    const L = door('l'), Rt = door('r');
    await render(page, 'door-l', L.W, L.H, L.s, true);
    await render(page, 'door-r', Rt.W, Rt.H, Rt.s, true);
  }
  // strands for live sway: hang from beam at y 250, inside the door view
  for (let x = 880; x <= 1520; x += 80) META.strands.push({ x: x + Math.round(rr(-14, 14)), y: 250, len: Math.round(rr(150, 260)) });
  fs.writeFileSync(path.join(OUT, 'meta.json'), JSON.stringify(META, null, 1));
  if (!only || only === 'S') {
    // a single jasmine strand image (live sway)
    seed = 77; await render(page, 'strand', 40, 300, jasmineStrand(20, 0, 290, { sway: 2, marigold: true }), true);
  }
  await browser.close();
})();
