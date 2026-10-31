# Generates SVG sources for the Temple of Two Souls art layers (rendered to PNG by render_svg.js).
import math, random
random.seed(21)
OUT = '/home/claude/tools5/temple/out/'

NOISE = '''<filter id="stone" x="0" y="0" width="100%" height="100%">
 <feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="4" seed="{seed}" result="n"/>
 <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 {amt} 0" result="g"/>
 <feComposite in="g" in2="SourceAlpha" operator="in" result="gm"/>
 <feBlend in="SourceGraphic" in2="gm" mode="overlay"/>
</filter>'''

def palm(x, y, s, flip=1, col='#2b1f3a'):
    out = []
    tx = x + 46 * s * flip; ty = y - 430 * s
    out.append(f'<path d="M{x-7*s},{y} Q{x+6*s*flip},{y-240*s} {tx-3*s},{ty} L{tx+5*s},{ty+2*s} Q{x+20*s*flip},{y-240*s} {x+9*s},{y} Z" fill="{col}"/>')
    for k in range(13):
        a = -math.pi / 2 + (k - 6) * 0.27 + random.uniform(-.06, .06)
        L = (165 + random.uniform(-25, 25)) * s
        droop = (0.42 + abs(k - 6) * 0.12) * L
        ex = tx + math.cos(a) * L * 1.2; ey = ty + math.sin(a) * L * 0.55 + droop
        cx_ = tx + math.cos(a) * L * 0.6; cy_ = ty + math.sin(a) * L * 0.75 - 10 * s
        n = 22
        top, bot = [], []
        for i in range(n + 1):
            t = i / n
            px = (1-t)**2*tx + 2*(1-t)*t*cx_ + t*t*ex; py = (1-t)**2*ty + 2*(1-t)*t*cy_ + t*t*ey
            w = 30 * s * math.sin(math.pi * min(1, t * 1.15)) ** 0.7 * (1 - t * 0.4)
            # leaflets: comb-like hanging strokes
            hang = w * (1.0 if i % 2 else 0.55)
            top.append((px, py - w * 0.18)); bot.append((px + hang * 0.2 * flip, py + hang))
        d = 'M' + ' L'.join(f'{a_:.1f},{b_:.1f}' for a_, b_ in top) + ' L' + ' L'.join(f'{a_:.1f},{b_:.1f}' for a_, b_ in reversed(bot)) + ' Z'
        out.append(f'<path d="{d}" fill="{col}"/>')
    return '\n'.join(out)

def kudu(cx, y, w, h, fill, stroke):
    # horseshoe arch motif (kudu / gavaksha)
    r = w / 2
    return (f'<path d="M{cx-r},{y} L{cx-r},{y-h+r} A{r},{r} 0 1 1 {cx+r},{y-h+r} L{cx+r},{y} Z" fill="{fill}"/>'
            f'<path d="M{cx-r*0.55},{y} L{cx-r*0.55},{y-h+r} A{r*0.55},{r*0.55} 0 1 1 {cx+r*0.55},{y-h+r} L{cx+r*0.55},{y} Z" fill="{stroke}"/>'
            f'<path d="M{cx},{y-h-r*0.15} l{-r*0.18},{-r*0.35} l{r*0.18},{-r*0.25} l{r*0.18},{r*0.25} Z" fill="{fill}"/>')

def temple():
    W, H = 2400, 1800
    cx = 1200
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="3200" height="2100" viewBox="-400 -300 3200 2100">')
    s.append('<defs>')
    s.append(NOISE.format(bf='0.9', seed=3, amt='0.55'))
    s.append('''
<linearGradient id="litStone" gradientUnits="userSpaceOnUse" x1="0" y1="1090" x2="0" y2="200">
  <stop offset="0" stop-color="#f0b46f"/><stop offset=".25" stop-color="#cf9264"/><stop offset=".55" stop-color="#9c6a63"/><stop offset=".85" stop-color="#6c4d68"/><stop offset="1" stop-color="#4f3a62"/>
</linearGradient>
<linearGradient id="wallG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6a4a55"/><stop offset=".6" stop-color="#4a3340"/><stop offset="1" stop-color="#2b1e28"/></linearGradient><radialGradient id="wallLight" cx="1200" cy="1080" r="700" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#f3a865" stop-opacity=".6"/><stop offset="1" stop-color="#f3a865" stop-opacity="0"/></radialGradient>
<radialGradient id="gateGlow" cx="1200" cy="1000" r="560" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#ffcf8a" stop-opacity=".95"/><stop offset=".35" stop-color="#f19a55" stop-opacity=".45"/><stop offset="1" stop-color="#f19a55" stop-opacity="0"/>
</radialGradient>
<linearGradient id="cornice" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6c891" stop-opacity=".9"/><stop offset=".45" stop-color="#b47a5c" stop-opacity=".2"/><stop offset="1" stop-color="#1e1222" stop-opacity=".75"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff0b8"/><stop offset=".4" stop-color="#e2b04f"/><stop offset=".75" stop-color="#9a6a1f"/><stop offset="1" stop-color="#f5d27a"/></linearGradient>
<linearGradient id="sideFade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset=".3" stop-color="#000" stop-opacity="0"/><stop offset=".7" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient>
<linearGradient id="doorG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a1f17"/><stop offset="1" stop-color="#5a2e1b"/></linearGradient>
<linearGradient id="recess" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c1018"/><stop offset="1" stop-color="#5a3328"/></linearGradient>
<filter id="soft"><feGaussianBlur stdDeviation="2.2"/></filter>
<filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter>
''')
    s.append('</defs>')
    # far palms (two depths)
    s.append('<g opacity=".9">')
    for (x, sc, fl) in [(-300, 1.3, 1), (-60, 0.85, -1), (140, 1.15, 1), (420, 0.9, -1), (650, 0.68, 1), (1760, 0.72, -1), (2000, 0.95, 1), (2280, 1.2, -1), (300, 0.58, 1), (2140, 0.6, -1), (2560, 0.9, 1), (2720, 1.35, -1)]:
        s.append(palm(x, 1000, sc, fl, '#2a1d36'))
    s.append('</g>')
    # compound wall
    s.append(f'<g filter="url(#stone)"><rect x="-400" y="905" width="3200" height="185" fill="url(#wallG)"/>')
    # coping & mouldings
    s.append(f'<rect x="-400" y="895" width="3200" height="16" fill="#9a6f6a"/><rect x="-400" y="911" width="3200" height="6" fill="#2a1c26"/>')
    s.append(f'<rect x="-400" y="1040" width="3200" height="10" fill="#8a6362"/><rect x="-400" y="1050" width="3200" height="6" fill="#2a1c26"/>')
    # small lamp niches on wall
    for x in range(-340, W + 400, 120):
        if abs(x - cx) < 330: continue
        s.append(f'<path d="M{x-14},990 L{x-14},962 A14,14 0 0 1 {x+14},962 L{x+14},990 Z" fill="#1d1219"/>')
    s.append(f'<rect x="-400" y="895" width="3200" height="195" fill="url(#wallLight)"/>')
    s.append('</g>')
    # gate glow behind tower
    s.append('<ellipse cx="1200" cy="760" rx="520" ry="480" fill="url(#gateGlow)" opacity=".55" filter="url(#blur8)"/>')
    # ---- GOPURAM ----
    g = []
    clip = []
    # base storey
    bx0, bx1, by0, by1 = 880, 1520, 700, 1088
    clip.append(f'M{bx0},{by1} L{bx0+6},{by0} L{bx1-6},{by0} L{bx1},{by1} Z')
    g.append(f'<path d="{clip[-1]}" fill="url(#litStone)"/>')
    # base pilasters & niches
    for i in range(9):
        x = bx0 + 20 + i * (bx1 - bx0 - 40) / 8
        if abs(x - cx) < 110: continue
        g.append(f'<rect x="{x-9}" y="{by0+40}" width="18" height="{by1-by0-90}" fill="#f2bb83" opacity=".55"/>')
        g.append(f'<rect x="{x-3}" y="{by0+40}" width="6" height="{by1-by0-90}" fill="#3a2430" opacity=".35"/>')
    for i in range(2):
        for side in (-1, 1):
            x = cx + side * (170 + i * 80)
            for (ny, nh) in ((by0 + 92, 104), (by0 + 238, 88)):
                # carved niche (devakoshta, left empty): frame, pilasters, recess, kudu crown
                g.append(f'<rect x="{x-30}" y="{ny-8}" width="60" height="{nh+16}" fill="#f2c28c" opacity=".35"/>')
                g.append(f'<rect x="{x-27}" y="{ny}" width="7" height="{nh}" fill="#f7cf98" opacity=".7"/><rect x="{x+20}" y="{ny}" width="7" height="{nh}" fill="#b07a5c" opacity=".8"/>')
                g.append(f'<rect x="{x-19}" y="{ny+6}" width="38" height="{nh-6}" fill="url(#recess)"/>')
                g.append(kudu(x, ny + 2, 34, 26, '#e3ac7c', '#2a1824'))
                g.append(f'<rect x="{x-32}" y="{ny+nh}" width="64" height="6" fill="#f5c890"/><rect x="{x-32}" y="{ny+nh+6}" width="64" height="3" fill="#2a1824" opacity=".7"/>')
    # plinth mouldings
    for yy, hh, c in [(by1-40, 10, '#f3c48d'), (by1-30, 8, '#3a2430'), (by1-60, 6, '#d9a274'), (by0+30, 12, '#f8d09a'), (by0+42, 7, '#2e1c28')]:
        g.append(f'<rect x="{bx0}" y="{yy}" width="{bx1-bx0}" height="{hh}" fill="{c}" opacity=".8"/>')
    for i in range(int((bx1 - bx0) / 16)):
        px = bx0 + 8 + i * 16
        g.append(f'<path d="M{px-7},{by1-62} Q{px},{by1-80} {px+7},{by1-62} Z" fill="#f1c08a" opacity=".55"/>')
    for i in range(int((bx1 - bx0) / 22)):
        px = bx0 + 11 + i * 22
        g.append(f'<rect x="{px-6}" y="{by1-28}" width="12" height="18" fill="#2e1c28" opacity=".45"/>')
    # doorway: tall rectangle with stepped frame
    dx0, dx1, dy0 = 1108, 1292, 818
    for k, c in enumerate(['#f6cf98', '#a46b52', '#e9b47e', '#5a3530']):
        o = (3 - k) * 14
        g.append(f'<rect x="{dx0-o}" y="{dy0-o}" width="{dx1-dx0+2*o}" height="{by1-dy0+o}" fill="{c}"/>')
    g.append(f'<rect x="{dx0}" y="{dy0}" width="{dx1-dx0}" height="{by1-dy0}" fill="url(#doorG)"/>')
    # door leaf seam and studs (tiny, far away)
    g.append(f'<rect x="{cx-1.5}" y="{dy0}" width="3" height="{by1-dy0}" fill="#1a0c08"/>')
    for r in range(9):
        for c_ in range(6):
            xx = dx0 + 16 + c_ * (dx1 - dx0 - 32) / 5; yy = dy0 + 20 + r * 28
            g.append(f'<circle cx="{xx}" cy="{yy}" r="2.6" fill="#e8b85c"/>')
    # light spilling under door
    g.append(f'<rect x="{dx0}" y="{by1-6}" width="{dx1-dx0}" height="6" fill="#ffd79a"/>')
    # lintel band with kudus over door
    g.append(f'<rect x="{dx0-70}" y="{dy0-80}" width="{dx1-dx0+140}" height="26" fill="url(#cornice)"/>')
    # ---- TIERS ----
    tiers = 7
    top_y = 250
    y = by0
    w0, w1 = 620, 270
    th = (by0 - top_y) / tiers
    for t in range(tiers):
        wb = w0 + (w1 - w0) * t / tiers
        wt = w0 + (w1 - w0) * (t + 1) / tiers
        yb, yt = y, y - th
        xl_b, xr_b = cx - wb / 2, cx + wb / 2
        xl_t, xr_t = cx - wt / 2, cx + wt / 2
        # body
        body=f'M{xl_b},{yb} L{xl_t+8},{yt+th*0.38} L{xr_t-8},{yt+th*0.38} L{xr_b},{yb} Z'
        clip.append(body)
        g.append(f'<path d="{body}" fill="url(#litStone)"/>')
        # cornice (kapota) projecting band
        cy0 = yt + th * 0.18; cy1 = yt + th * 0.42
        g.append(f'<path d="M{xl_t-14},{cy1} Q{xl_t-20},{cy0} {xl_t-4},{cy0} L{xr_t+4},{cy0} Q{xr_t+20},{cy0} {xr_t+14},{cy1} Z" fill="#c48d68"/>')
        g.append(f'<path d="M{xl_t-14},{cy1} Q{xl_t-20},{cy0} {xl_t-4},{cy0} L{xr_t+4},{cy0} Q{xr_t+20},{cy0} {xr_t+14},{cy1} Z" fill="url(#cornice)"/>')
        g.append(f'<rect x="{xl_t-14}" y="{cy1}" width="{wt+28}" height="5" fill="#1e1220" opacity=".8"/>')
        # top parapet with mini shrine roofs (kutas & shalas) along cornice
        n = max(3, int(wt / 46))
        for i in range(n):
            px = xl_t + (i + 0.5) * wt / n
            isCorner = i in (0, n - 1)
            ww = 30 if isCorner else 24
            hh = th * 0.30
            if isCorner:
                g.append(f'<rect x="{px-ww/2}" y="{cy0-hh*0.6}" width="{ww}" height="{hh*0.6}" fill="#b98466"/>')
                g.append(f'<path d="M{px-ww/2-3},{cy0-hh*0.6} Q{px},{cy0-hh*1.45} {px+ww/2+3},{cy0-hh*0.6} Z" fill="#d9a477"/>')
                g.append(f'<circle cx="{px}" cy="{cy0-hh*1.25}" r="3" fill="url(#gold)"/>')
            else:
                g.append(f'<rect x="{px-ww/2}" y="{cy0-hh*0.55}" width="{ww}" height="{hh*0.55}" fill="#a87560"/>')
                g.append(f'<path d="M{px-ww/2-2},{cy0-hh*0.55} L{px-ww/2+3},{cy0-hh} L{px+ww/2-3},{cy0-hh} L{px+ww/2+2},{cy0-hh*0.55} Z" fill="#c99272"/>')
                g.append(f'<rect x="{px-ww/2+3}" y="{cy0-hh-3}" width="{ww-6}" height="3" fill="#f0c088"/>')
        # body: pilasters and niches with kudu arches
        nb = max(3, int(wb / 52))
        for i in range(nb):
            px = xl_b + (i + 0.5) * wb / nb
            # taper position to follow trapezoid
            frac = (px - cx) / (wb / 2)
            if abs(px - cx) < 30 and t < 3:
                # central opening (window) on each tier
                g.append(f'<rect x="{px-14}" y="{cy1+10}" width="28" height="{yb-cy1-22}" fill="#170c14"/>')
                g.append(f'<rect x="{px-14}" y="{yb-12}" width="28" height="4" fill="#ffcf8f" opacity=".6"/>')
                continue
            nh = (yb - cy1) * 0.62
            g.append(f'<rect x="{px-10}" y="{yb-nh-8}" width="20" height="{nh}" fill="#2a1824" opacity=".62"/>')
            g.append(kudu(px, yb - nh - 8, 22, 16, '#d8a172', '#2a1824'))
            g.append(f'<rect x="{px+wb/nb/2-3}" y="{cy1+6}" width="6" height="{yb-cy1-10}" fill="#f6c690" opacity=".35"/>')
        # base moulding of tier
        g.append(f'<rect x="{xl_b}" y="{yb-6}" width="{wb}" height="6" fill="#f1c08b" opacity=".75"/>')
        y = yt + th * 0.18
    # crown: barrel vault (shala)
    ry0 = y
    sw = 300
    g.append(f'<rect x="{cx-sw/2}" y="{ry0-40}" width="{sw}" height="40" fill="url(#litStone)"/>')
    g.append(f'<path d="M{cx-sw/2-18},{ry0-38} Q{cx},{ry0-150} {cx+sw/2+18},{ry0-38} Z" fill="#c38c6c"/>')
    g.append(f'<path d="M{cx-sw/2-18},{ry0-38} Q{cx},{ry0-150} {cx+sw/2+18},{ry0-38} Z" fill="url(#cornice)" opacity=".8"/>')
    # gable horseshoe ends (mahanasi)
    for side in (-1, 1):
        ex = cx + side * (sw / 2 - 4)
        g.append(f'<path d="M{ex-34},{ry0-30} A34,40 0 1 1 {ex+34},{ry0-30} Z" fill="#d7a173"/>')
        g.append(f'<path d="M{ex-20},{ry0-30} A20,26 0 1 1 {ex+20},{ry0-30} Z" fill="#2a1824"/>')
        g.append(f'<path d="M{ex},{ry0-108} l-8,-16 l8,-10 l8,10 Z" fill="#e2b06c"/>')
    # central kudu on vault
    g.append(kudu(cx, ry0 - 20, 70, 74, '#e0ab7b', '#1d1019'))
    # kalasams along ridge
    ridge = ry0 - 98
    for i in range(7):
        kx = cx - 120 + i * 40
        ky = ridge - (8 if i in (0, 6) else 0) + (abs(i - 3) ** 2) * 1.5 + 6
        g.append(f'<g transform="translate({kx},{ky})">'
                 f'<ellipse cx="0" cy="0" rx="9" ry="4" fill="#8a5d1c"/>'
                 f'<path d="M-8,-2 Q-13,-14 -4,-20 Q-6,-26 -2,-30 L0,-44 L2,-30 Q6,-26 4,-20 Q13,-14 8,-2 Z" fill="url(#gold)"/>'
                 f'<circle cx="0" cy="-46" r="2.5" fill="#fff1c0"/></g>')
    s.append('<g filter="url(#stone)">' + '\n'.join(g) + '</g>')
    # global warm light from lamps below + cool from sky above, side shading
    cp = ' '.join(clip) + f' M{cx-170},{ry0} L{cx-170},{ry0-140} L{cx+170},{ry0-140} L{cx+170},{ry0} Z'
    s.append(f'<clipPath id="towerClip"><path d="{cp}"/></clipPath>')
    s.append(f'<rect x="{bx0-60}" y="150" width="{bx1-bx0+120}" height="950" fill="url(#sideFade)" clip-path="url(#towerClip)"/>')
    # central bay highlight (protruding bay catches more lamp light)
    s.append(f'<rect x="{cx-120}" y="300" width="240" height="800" fill="#ffcf8f" opacity=".10" clip-path="url(#towerClip)"/>')
    # rim light on silhouette edges (sky glow)
    s.append('</svg>')
    open(OUT + 'temple.svg', 'w').write('\n'.join(s))

def deepam():
    # brass kundi lamp on short stand, 200x240; flame drawn live in canvas
    s = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="240" viewBox="0 0 200 240">
<defs>
<linearGradient id="b" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5e3b0f"/><stop offset=".22" stop-color="#c58a2c"/><stop offset=".42" stop-color="#ffe3a0"/><stop offset=".58" stop-color="#d9a040"/><stop offset="1" stop-color="#4a2c0a"/></linearGradient>
<linearGradient id="bv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe7a8"/><stop offset=".5" stop-color="#c88c2e"/><stop offset="1" stop-color="#3f250a"/></linearGradient>
<radialGradient id="oil" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd27a"/><stop offset="1" stop-color="#7a4a10"/></radialGradient>
</defs>
<ellipse cx="100" cy="226" rx="56" ry="10" fill="#000" opacity=".35"/>
<path d="M58,226 Q60,206 84,200 L116,200 Q140,206 142,226 Z" fill="url(#b)"/>
<ellipse cx="100" cy="200" rx="18" ry="5" fill="url(#bv)"/>
<path d="M90,200 Q94,170 92,150 L108,150 Q106,170 110,200 Z" fill="url(#b)"/>
<ellipse cx="100" cy="166" rx="13" ry="5" fill="url(#bv)"/>
<ellipse cx="100" cy="150" rx="11" ry="4" fill="url(#bv)"/>
<path d="M44,112 Q46,148 100,150 Q154,148 156,112 Z" fill="url(#b)"/>
<path d="M156,112 Q168,108 178,100 Q172,116 152,122 Z" fill="url(#b)"/>
<ellipse cx="100" cy="112" rx="56" ry="11" fill="url(#bv)"/>
<ellipse cx="100" cy="113" rx="48" ry="8" fill="url(#oil)"/>
<path d="M166,104 Q172,98 176,96" stroke="#3a2306" stroke-width="3" fill="none"/>
</svg>'''
    open(OUT + 'deepam.svg', 'w').write(s)

def pillar():
    # foreground carved stone pillar, backlit; 360x1800, inner edge on the right
    W, H = 360, 1800
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>',
         NOISE.format(bf='0.7', seed=8, amt='0.7'),
         '<linearGradient id="p" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#150d16"/><stop offset=".72" stop-color="#2d1d26"/><stop offset=".93" stop-color="#8c5a45"/><stop offset="1" stop-color="#f0b071"/></linearGradient>',
         '<linearGradient id="v" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".2"/><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient>',
         '</defs><g filter="url(#stone)">']
    def band(y, h, inset):
        return f'<rect x="0" y="{y}" width="{W-inset}" height="{h}" fill="url(#p)"/>'
    # capital bracket at top (potika)
    s.append(f'<path d="M0,0 L{W},0 L{W},70 Q{W-10},110 {W-60},120 L{W-60},150 L0,150 Z" fill="url(#p)"/>')
    # shaft segments: square - octagonal - square with lotus bands
    y = 150
    segs = [(110, 70), (40, 50), (260, 70), (34, 46), (60, 40), (300, 70), (34, 46), (260, 70), (40, 50), (420, 66)]
    for h, inset in segs:
        s.append(band(y, h, inset))
        if h < 50:
            # lotus petal band
            n = 6
            for i in range(n):
                px = (W - inset) * (i + .5) / n
                s.append(f'<path d="M{px-18},{y+h} Q{px},{y-6} {px+18},{y+h} Z" fill="#000" opacity=".25"/>')
        else:
            # carved medallion
            mx = (W - inset) * .58; my = y + h / 2
            r = min(h, W - inset) * .28
            s.append(f'<circle cx="{mx}" cy="{my}" r="{r}" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="6"/>')
            s.append(f'<circle cx="{mx}" cy="{my}" r="{r*0.55}" fill="none" stroke="#e7a56a" stroke-opacity=".25" stroke-width="3"/>')
        y += h
    s.append(f'<rect x="0" y="{y}" width="{W-40}" height="{H-y}" fill="url(#p)"/>')
    s.append('</g>')
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#v)" style="mix-blend-mode:multiply"/>')
    s.append('</svg>')
    open(OUT + 'pillar.svg', 'w').write('\n'.join(s))

def garland():
    # jasmine strings hanging from top across full width with marigold accents, 1600x420 (tiled/stretched horizontally)
    W, H = 1600, 520
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>',
         '<radialGradient id="j" cx=".45" cy=".4" r=".6"><stop offset="0" stop-color="#fffdf4"/><stop offset=".7" stop-color="#efe6cf"/><stop offset="1" stop-color="#b9a98a"/></radialGradient>',
         '<radialGradient id="m" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#ffd25a"/><stop offset=".7" stop-color="#ef8a12"/><stop offset="1" stop-color="#a24a05"/></radialGradient>',
         '<radialGradient id="r" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#e84a4a"/><stop offset="1" stop-color="#7a0f1c"/></radialGradient>',
         '<filter id="sh"><feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#1a0a10" flood-opacity=".55"/></filter>',
         '</defs><g filter="url(#sh)">']
    # top swag (thick jasmine rope)
    def bud(x, y, r, rot):
        return f'<ellipse cx="{x}" cy="{y}" rx="{r*0.62}" ry="{r}" transform="rotate({rot} {x} {y})" fill="url(#j)"/>'
    for i in range(0, W + 1, 9):
        y = 22 + 26 * math.sin(i / W * math.pi * 4) ** 2
        s.append(bud(i, y + random.uniform(-6, 6), 9 + random.uniform(-2, 2), random.uniform(-40, 40)))
    # hanging strands
    x = 30
    while x < W:
        L = random.uniform(140, 470)
        top = 22 + 26 * math.sin(x / W * math.pi * 4) ** 2
        yy = top + 10
        sway = random.uniform(-6, 6)
        while yy < top + L:
            t = (yy - top) / L
            s.append(bud(x + sway * t + random.uniform(-2, 2), yy, 7.5 * (1 - t * .25), random.uniform(-30, 30)))
            yy += 10.5
        # end tassel: marigold or rose
        end = 'url(#m)' if random.random() < .6 else 'url(#r)'
        s.append(f'<circle cx="{x+sway}" cy="{yy+8}" r="11" fill="{end}"/>')
        x += random.uniform(36, 62)
    s.append('</g></svg>')
    open(OUT + 'garland.svg', 'w').write('\n'.join(s))

def bell():
    s = '''<svg xmlns="http://www.w3.org/2000/svg" width="260" height="720" viewBox="0 0 260 720"><defs>
<linearGradient id="b" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a1708"/><stop offset=".25" stop-color="#7a4d16"/><stop offset=".45" stop-color="#f3cf7e"/><stop offset=".6" stop-color="#b37a28"/><stop offset="1" stop-color="#241306"/></linearGradient>
<linearGradient id="c" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3a220a"/><stop offset=".5" stop-color="#d6a650"/><stop offset="1" stop-color="#3a220a"/></linearGradient></defs>'''
    # chain
    y = 0
    i = 0
    while y < 470:
        if i % 2 == 0:
            s += f'<ellipse cx="130" cy="{y+14}" rx="9" ry="16" fill="none" stroke="url(#c)" stroke-width="5"/>'
        else:
            s += f'<rect x="127" y="{y+2}" width="6" height="26" rx="3" fill="url(#c)"/>'
        y += 24; i += 1
    s += '<path d="M112,470 Q130,452 148,470 L146,486 L114,486 Z" fill="url(#b)"/>'
    s += '<path d="M118,486 Q76,500 70,580 Q66,640 34,672 L226,672 Q194,640 190,580 Q184,500 142,486 Z" fill="url(#b)"/>'
    s += '<path d="M28,668 Q130,700 232,668 L232,680 Q130,712 28,680 Z" fill="url(#c)"/>'
    s += '<path d="M76,560 Q130,575 184,560" stroke="#2a1708" stroke-width="3" fill="none" opacity=".6"/>'
    s += '<path d="M72,600 Q130,616 188,600" stroke="#ffe2a0" stroke-width="2" fill="none" opacity=".5"/>'
    s += '<circle cx="130" cy="700" r="12" fill="url(#b)"/>'
    s += '</svg>'
    open(OUT + 'bell.svg', 'w').write(s)

def door(side):
    # one leaf of the temple door: 700x1500. Teak panels, brass studs grid, brass edge straps.
    W, H = 700, 1500
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>',
         '''<filter id="wood" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.006 0.16" numOctaves="4" seed="''' + ('5' if side == 'l' else '9') + '''" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.9 0" result="g"/>
  <feComposite in="g" in2="SourceAlpha" operator="in" result="gm"/>
  <feBlend in="SourceGraphic" in2="gm" mode="overlay"/></filter>''',
         '<linearGradient id="teak" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6a3a1e"/><stop offset=".5" stop-color="#4b2614"/><stop offset="1" stop-color="#2f170c"/></linearGradient>',
         '<linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c0d06" stop-opacity=".7"/><stop offset=".08" stop-color="#000" stop-opacity="0"/><stop offset=".92" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#f0b070" stop-opacity=".35"/></linearGradient>',
         '<radialGradient id="stud" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#fff4c4"/><stop offset=".3" stop-color="#e8b44f"/><stop offset=".75" stop-color="#8a5a16"/><stop offset="1" stop-color="#3a2206"/></radialGradient>',
         '<linearGradient id="strap" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f8dc94"/><stop offset=".5" stop-color="#b8822e"/><stop offset="1" stop-color="#5a3a10"/></linearGradient>',
         '<filter id="ds"><feDropShadow dx="2" dy="4" stdDeviation="2" flood-color="#000" flood-opacity=".6"/></filter>',
         '</defs>']
    s.append(f'<g filter="url(#wood)"><rect width="{W}" height="{H}" fill="url(#teak)"/></g>')
    # raised panels: 3 x 5
    pw, ph = 170, 210
    for r in range(5):
        for c in range(3):
            x = 60 + c * (pw + 30); y = 90 + r * (ph + 50)
            s.append(f'<rect x="{x}" y="{y}" width="{pw}" height="{ph}" fill="#000" opacity=".22"/>')
            s.append(f'<rect x="{x}" y="{y}" width="{pw}" height="{ph}" fill="url(#panel)"/>')
            s.append(f'<rect x="{x+16}" y="{y+16}" width="{pw-32}" height="{ph-32}" fill="none" stroke="#f0b070" stroke-opacity=".18" stroke-width="2"/>')
            # carved lotus rosette in centre of panel
            cx_, cy_ = x + pw / 2, y + ph / 2
            for k in range(8):
                a = k * math.pi / 4
                s.append(f'<ellipse cx="{cx_+math.cos(a)*22}" cy="{cy_+math.sin(a)*22}" rx="20" ry="9" transform="rotate({k*45} {cx_+math.cos(a)*22} {cy_+math.sin(a)*22})" fill="#000" opacity=".28"/>')
            s.append(f'<circle cx="{cx_}" cy="{cy_}" r="13" fill="url(#stud)" filter="url(#ds)"/>')
    # stud grid on rails
    g = ['<g filter="url(#ds)">']
    for r in range(6):
        y = 65 + r * 260
        for c in range(13):
            x = 40 + c * 52
            g.append(f'<circle cx="{x}" cy="{y}" r="9" fill="url(#stud)"/>')
    for c in range(4):
        x = 38 + c * 200
        for r in range(28):
            y = 90 + r * 50
            g.append(f'<circle cx="{x}" cy="{y}" r="7" fill="url(#stud)"/>')
    g.append('</g>')
    s += g
    # brass straps top/bottom
    for y in (20, H - 46):
        s.append(f'<rect x="0" y="{y}" width="{W}" height="26" fill="url(#strap)" filter="url(#ds)"/>')
    # ring handle near inner edge
    hx = W - 70 if side == 'l' else 70
    s.append(f'<circle cx="{hx}" cy="{H/2}" r="22" fill="url(#stud)" filter="url(#ds)"/>')
    s.append(f'<circle cx="{hx}" cy="{H/2+48}" r="40" fill="none" stroke="url(#strap)" stroke-width="10" filter="url(#ds)"/>')
    # inner edge shadow / outer edge light
    edge = f'<linearGradient id="e" x1="{1 if side=="l" else 0}" y1="0" x2="{0 if side=="l" else 1}" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset=".12" stop-color="#000" stop-opacity="0"/></linearGradient>'
    s.insert(1, '<defs>' + edge + '</defs>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#e)"/>')
    s.append('</svg>')
    open(OUT + f'door_{side}.svg', 'w').write('\n'.join(s))

def arch():
    # carved stone arch frame (torana) 900x1200 with transparent arch opening. Opening: x 150..750, top arch from y 180.
    W, H = 900, 1200
    ox0, ox1, oy_spring, oy_bot = 150, 750, 470, 1110
    r = (ox1 - ox0) / 2
    cx = W / 2
    # cusped (multi-foil) arch path
    cusps = 7
    path_open = f'M{ox0},{oy_bot} L{ox0},{oy_spring} '
    for i in range(cusps):
        a0 = math.pi + i * math.pi / cusps; a1 = math.pi + (i + 1) * math.pi / cusps
        x1 = cx + r * math.cos(a1); y1 = oy_spring + r * 1.0 * math.sin(a1)
        path_open += f'A{r/cusps*1.7},{r/cusps*1.7} 0 0 1 {x1},{y1} '
    path_open += f'L{ox1},{oy_bot} Z'
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>',
         NOISE.format(bf='0.8', seed=17, amt='0.6'),
         '<linearGradient id="st" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6cfa6"/><stop offset=".5" stop-color="#cdb08a"/><stop offset="1" stop-color="#a98a68"/></linearGradient>',
         '<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff0b8"/><stop offset=".4" stop-color="#d9a441"/><stop offset=".75" stop-color="#8a5c18"/><stop offset="1" stop-color="#f0cb72"/></linearGradient>',
         f'<mask id="hole"><rect width="{W}" height="{H}" fill="#fff"/><path d="{path_open}" fill="#000"/></mask>',
         '<filter id="ds"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#2a1608" flood-opacity=".55"/></filter>',
         '<filter id="inner"><feGaussianBlur stdDeviation="10"/></filter>',
         '</defs>']
    s.append(f'<g mask="url(#hole)" filter="url(#ds)"><g filter="url(#stone)">')
    s.append(f'<path d="M40,{H} L40,{oy_spring} Q40,40 {cx},40 Q{W-40},40 {W-40},{oy_spring} L{W-40},{H} Z" fill="url(#st)"/>')
    s.append('</g>')
    # carved bands following the arch
    for k, (off, col, sw) in enumerate([(60, '#8c6a4c', 3), (78, '#fff3d8', 2), (96, '#7a5a40', 4)]):
        rr = r + off
        s.append(f'<path d="M{cx-rr},{H} L{cx-rr},{oy_spring} A{rr},{rr*1.02} 0 0 1 {cx+rr},{oy_spring} L{cx+rr},{H}" fill="none" stroke="{col}" stroke-width="{sw}" opacity=".7"/>')
    # bead & lotus motif along the arch
    for i in range(29):
        a = math.pi + i * math.pi / 28
        x = cx + (r + 38) * math.cos(a); y = oy_spring + (r + 38) * math.sin(a)
        s.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#b89470" stroke="#6f5038" stroke-width="1.5"/>')
    # pilasters on sides
    for x in (70, W - 130):
        s.append(f'<rect x="{x}" y="{oy_spring}" width="60" height="{H-oy_spring-20}" fill="#000" opacity=".08"/>')
        for yy in range(oy_spring + 30, H - 40, 110):
            s.append(f'<path d="M{x+6},{yy} L{x+54},{yy} L{x+30},{yy+40} Z" fill="#6f5038" opacity=".35"/>')
    # kirtimukha-free crown: lotus bud finial and two parrots? keep abstract: lotus finial
    s.append(f'<g transform="translate({cx},70)"><path d="M-46,30 Q0,-40 46,30 Z" fill="url(#gold)"/><path d="M-26,30 Q0,-62 26,30 Z" fill="#f6dc95"/><circle cx="0" cy="-48" r="7" fill="url(#gold)"/></g>')
    s.append('</g>')
    # inner rim shading to give depth around opening
    s.append(f'<path d="{path_open}" fill="none" stroke="#3a2412" stroke-width="18" opacity=".55" filter="url(#inner)"/>')
    s.append(f'<path d="{path_open}" fill="none" stroke="url(#gold)" stroke-width="6"/>')
    s.append('</svg>')
    open(OUT + 'arch.svg', 'w').write('\n'.join(s))
    open(OUT + 'arch_path.txt', 'w').write(path_open)

if __name__ == '__main__':
    temple(); deepam(); pillar(); garland(); bell(); door('l'); door('r'); arch()
    print('svgs written')
