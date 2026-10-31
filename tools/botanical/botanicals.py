"""Procedural botanical engravings (hatched line art, lightly hand-coloured) as SVG.
Each plant is built from parametric organs (petal / leaf / stem / bract) with
form-following contour hatching, cross-hatching on the shadow side and stipple.
Light comes from the upper left. Writes SVG files to /home/claude/tools5/botanical/svg/.
"""
import numpy as np
import os, math

OUTDIR = '/home/claude/tools5/botanical/svg'
os.makedirs(OUTDIR, exist_ok=True)
INK = '#2a2b22'
LIGHT = np.array([-0.6, -0.8])


def f(v):
    return f'{v:.1f}'


def path_d(pts, close=False):
    if len(pts) < 2:
        return ''
    s = 'M' + ' L'.join(f'{f(x)},{f(y)}' for x, y in pts)
    return s + (' Z' if close else '')


def smooth_d(pts, close=False):
    """Catmull-Rom to cubic bezier for smooth outlines."""
    P = list(pts)
    if close:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    s = f'M{f(P[1][0])},{f(P[1][1])}'
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f' C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}'
    return s + (' Z' if close else '')


class Drawing:
    def __init__(self, w, h, seed=1):
        self.w, self.h = w, h
        self.rng = np.random.default_rng(seed)
        self.groups = []
        self.begin()
        self.uid = 0
        self.paper = '#f7f2e7'

    def begin(self):
        g = {'tint': [], 'lines': [], 'dots': []}
        self.groups.append(g)
        self.tint, self.lines, self.dots = g['tint'], g['lines'], g['dots']

    def nid(self):
        self.uid += 1
        return f'c{self.uid}'

    # ---------- organs ----------
    def organ(self, base, tip, width, bend=0.0, shape='leaf', tint=None, tint_op=0.42,
              hatch=10, midrib=True, veins=0, cross=True, outline_w=1.1, roll=0.0, light_bias=0.0):
        """Generic petal/leaf. shape: leaf (pointed both), petal (round tip), lotus (pointed tip, broad),
        lance (narrow long), bract (broad round, cupped)."""
        self.begin()
        B, T = np.array(base, float), np.array(tip, float)
        axis = T - B
        L = np.linalg.norm(axis)
        u = axis / L
        n = np.array([-u[1], u[0]])
        ts = np.linspace(0, 1, 60)
        # centreline with bend (quadratic offset)
        C = B[None, :] + axis[None, :] * ts[:, None] + n[None, :] * (bend * L * 4 * ts * (1 - ts))[:, None]
        if shape == 'leaf':
            wf = np.sin(np.pi * ts) ** 0.9 * (1 - 0.25 * ts)
        elif shape == 'lance':
            wf = np.sin(np.pi * ts ** 0.8) ** 1.2
        elif shape == 'petal':
            wf = np.sin(np.pi * np.clip(ts * 0.92, 0, 1)) ** 0.55 * np.clip((1 - ts) * 12, 0, 1) ** 0.5
        elif shape == 'lotus':
            wf = np.sin(np.pi * ts ** 0.75) ** 0.8
        elif shape == 'bract':
            wf = np.sin(np.pi * np.clip(ts * 0.97, 0, 1)) ** 0.5
        else:
            wf = np.sin(np.pi * ts)
        W = width * wf
        # tangent-based normals along curve
        dC = np.gradient(C, axis=0)
        tn = dC / (np.linalg.norm(dC, axis=1)[:, None] + 1e-9)
        N = np.stack([-tn[:, 1], tn[:, 0]], 1)
        left = C + N * W[:, None]
        right = C - N * W[:, None]
        outline = list(map(tuple, left)) + list(map(tuple, right[::-1]))
        if tint:
            self.tint.append((smooth_d(outline, True), tint, tint_op))
        self.lines.append((smooth_d(outline, True), outline_w, 0.95))
        # which side is shadowed? compare normal with light
        side_shadow = -1 if np.dot(N[30], LIGHT) > 0 else 1  # side away from light
        # contour hatching along the form
        if hatch:
            for k in range(1, hatch + 1):
                s = k / (hatch + 1)
                for sgn in (1, -1):
                    shadowed = (sgn == side_shadow)
                    if not shadowed and s < 0.55 + light_bias:
                        continue  # light side mostly bare near the midrib
                    lo, hi = (0.08, 0.92) if shadowed else (0.18, 0.75)
                    jitter = self.rng.uniform(-0.04, 0.04)
                    sel = (ts > lo + jitter) & (ts < hi + jitter)
                    off = s * (1 + roll * (1 - s))
                    pts = C[sel] + sgn * N[sel] * (W[sel] * off)[:, None]
                    op = 0.75 if shadowed else 0.45
                    wdt = 0.55 if shadowed else 0.4
                    self.lines.append((smooth_d(pts[::3].tolist()), wdt, op))
            if cross:
                # cross hatch: short strokes across the shadowed half near the base
                for j in range(int(hatch * 1.3)):
                    t0 = 0.12 + 0.6 * j / (hatch * 1.3)
                    i0 = int(t0 * 59)
                    a = C[i0] + side_shadow * N[i0] * W[i0] * 0.25
                    b = C[i0] + side_shadow * N[i0] * W[i0] * 0.95 + tn[i0] * W[i0] * 0.35
                    self.lines.append((path_d([tuple(a), tuple(b)]), 0.4, 0.55))
        if midrib:
            self.lines.append((smooth_d(C[2:-3:3].tolist()), outline_w * 0.8, 0.85))
        if veins:
            for k in range(1, veins + 1):
                t0 = 0.08 + 0.84 * k / (veins + 1)
                i0 = int(t0 * 59)
                for sgn in (1, -1):
                    i1 = min(59, i0 + 6)
                    a = C[i0]
                    m = C[min(59, i0 + 3)] + sgn * N[i0] * W[i0] * 0.5
                    b = C[i1] + sgn * N[i1] * W[i1] * 0.93
                    self.lines.append((smooth_d([tuple(a), tuple(m), tuple(b)]), 0.5, 0.7))
        return C, N, W

    def stem(self, pts, width=3.0, tint='#6f8a5a'):
        self.begin()
        P = np.array(pts, float)
        # resample smooth
        t = np.linspace(0, 1, len(P))
        tt = np.linspace(0, 1, 50)
        C = np.stack([np.interp(tt, t, P[:, 0]), np.interp(tt, t, P[:, 1])], 1)
        from scipy.ndimage import gaussian_filter1d
        C = np.stack([gaussian_filter1d(C[:, 0], 2, mode='nearest'), gaussian_filter1d(C[:, 1], 2, mode='nearest')], 1)
        dC = np.gradient(C, axis=0)
        tn = dC / (np.linalg.norm(dC, axis=1)[:, None] + 1e-9)
        N = np.stack([-tn[:, 1], tn[:, 0]], 1)
        Wd = width * (1 - 0.35 * tt)
        left = C + N * Wd[:, None]
        right = C - N * Wd[:, None]
        outline = list(map(tuple, left)) + list(map(tuple, right[::-1]))
        self.tint.append((smooth_d(outline, True), tint, 0.5))
        self.lines.append((smooth_d(left[::2].tolist()), 0.9, 0.9))
        self.lines.append((smooth_d(right[::2].tolist()), 0.9, 0.9))
        shadow = right if np.dot(N[25], LIGHT) > 0 else left
        # short hatching ticks on the shadow edge
        for i in range(2, 48, 2):
            a = C[i] + (shadow[i] - C[i]) * 0.2
            b = shadow[i]
            self.lines.append((path_d([tuple(a), tuple(b)]), 0.4, 0.6))
        return C

    def stipple(self, cx, cy, r, count, op=0.7, size=0.6):
        for _ in range(count):
            a = self.rng.uniform(0, 2 * np.pi)
            rr = r * np.sqrt(self.rng.uniform()) ** 0.8
            self.dots.append((cx + np.cos(a) * rr, cy + np.sin(a) * rr, size * self.rng.uniform(0.6, 1.3), op))

    # ---------- plants ----------
    def lotus(self, cx, cy, s=1.0, rot=0.0, open_=1.0):
        """Open lotus, three-quarter side view, petals cupped upward. cx,cy = base of flower."""
        R = lambda p: rotate(p, (cx, cy), rot)
        pink, pale = '#d4808f', '#e8b0b9'
        def pet(ang, L, W, dy=0.0, bend=0.0, col=pink, op=0.5, hatch=10):
            a = math.radians(ang * open_ - 90)
            b = (cx, cy + dy * s)
            tip = (b[0] + math.cos(a) * L * s, b[1] + math.sin(a) * L * s)
            self.organ(R(b), R(tip), W * s, bend=bend, shape='lotus', tint=col, tint_op=op, hatch=hatch,
                       midrib=False, outline_w=1.05, roll=0.35)
        # outermost, low and spreading (behind everything)
        pet(-78, 96, 30, 6, 0.10, pale, 0.42, 8); pet(78, 96, 30, 6, -0.10, pale, 0.42, 8)
        # back row
        pet(0, 132, 34, 0, 0.0, pale, 0.5)
        pet(-26, 128, 36, 0, 0.06, pink); pet(26, 128, 36, 0, -0.06, pink)
        pet(-52, 116, 36, 2, 0.10, pale); pet(52, 116, 36, 2, -0.10, pale)
        # seed pod glimpse between rows
        self.begin()
        self.tint.append((ellipse_d(cx, cy - 46 * s, 24 * s, 8 * s), '#e2c46c', 0.7))
        self.lines.append((ellipse_d(cx, cy - 46 * s, 24 * s, 8 * s), 0.9, 0.9))
        for k in range(16):
            self.dots.append((cx + self.rng.uniform(-18, 18) * s, cy - 46 * s + self.rng.uniform(-4, 4) * s, 1.0 * s, 0.85))
        # front row (shorter, cupping, drawn outside-in)
        pet(-44, 104, 34, 10, -0.08, pink, 0.55); pet(44, 104, 34, 10, 0.08, pink, 0.55)
        pet(-16, 98, 36, 12, -0.05, pink, 0.6); pet(17, 98, 36, 12, 0.05, pink, 0.6)
        # receptacle
        self.organ(R((cx, cy + 40 * s)), R((cx, cy + 6 * s)), 13 * s, shape='bract', tint='#93a36e', hatch=4, midrib=False)

    def lotus_bud(self, cx, cy, s=1.0, rot=0.0):
        R = lambda p: rotate(p, (cx, cy), rot)
        for dx, ln, b in [(-6, 1.0, 0.05), (6, 1.0, -0.05), (0, 1.05, 0.0)]:
            self.organ(R((cx + dx * s, cy)), R((cx + dx * 0.2 * s, cy - 95 * s * ln)), 26 * s, bend=b, shape='lotus',
                       tint='#d98c9a', tint_op=0.55, hatch=8, midrib=False, roll=0.5)

    def lotus_leaf(self, cx, cy, rx, ry, rot=0.0):
        pts = []
        for k in range(90):
            a = k / 90 * 2 * np.pi
            wob = 1 + 0.04 * math.sin(a * 7 + 1) + 0.025 * math.sin(a * 13)
            if abs(((a - 1.6) + np.pi) % (2 * np.pi) - np.pi) < 0.12:  # notch toward viewer
                wob *= 0.55
            pts.append(rotate((cx + math.cos(a) * rx * wob, cy + math.sin(a) * ry * wob), (cx, cy), rot))
        self.begin()
        d = smooth_d(pts, True)
        self.tint.append((d, '#7d9a62', 0.55))
        self.lines.append((d, 1.1, 0.95))
        # radial veins with hatching between on far side
        for k in range(16):
            a = k / 16 * 2 * np.pi + 0.1
            e = rotate((cx + math.cos(a) * rx * 0.96, cy + math.sin(a) * ry * 0.96), (cx, cy), rot)
            m = rotate((cx + math.cos(a + 0.05) * rx * 0.5, cy + math.sin(a + 0.05) * ry * 0.5), (cx, cy), rot)
            self.lines.append((smooth_d([(cx, cy), m, e]), 0.6, 0.8))
            # concentric hatch arcs on lower (shadow) half
            if math.sin(a) > -0.2:
                for rr in np.linspace(0.3, 0.92, 6):
                    a2 = a + 2 * np.pi / 16 * 0.85
                    arc = [rotate((cx + math.cos(t) * rx * rr, cy + math.sin(t) * ry * rr), (cx, cy), rot)
                           for t in np.linspace(a + 0.04, a2, 5)]
                    self.lines.append((smooth_d(arc), 0.35, 0.55))

    def jasmine_flower(self, cx, cy, s=1.0, rot=0.0, layers=2):
        """Jasminum sambac (malle) face-on: layered rounded petals."""
        for layer in range(layers):
            n = 7 if layer == 0 else 6
            off = 0 if layer == 0 else np.pi / n
            for k in range(n):
                a = rot + off + k / n * 2 * np.pi
                L = (26 if layer == 0 else 19) * s
                tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
                self.organ((cx, cy), tip, (8.5 if layer == 0 else 7.5) * s, bend=0.05, shape='petal',
                           tint='#fbf7ea', tint_op=0.85, hatch=3, midrib=False, cross=False, outline_w=0.85, light_bias=0.2)
        self.tint.append((ellipse_d(cx, cy, 3.2 * s, 3.2 * s), '#e5cf86', 0.9))
        self.stipple(cx, cy, 3.5 * s, 10, 0.8, 0.5 * s)

    def jasmine_bud(self, base, tip, s=1.0):
        self.organ(base, tip, 5.5 * s, bend=0.05, shape='lotus', tint='#f6efdc', tint_op=0.9, hatch=3, midrib=False,
                   cross=False, outline_w=0.8)
        # calyx
        bx, by = base
        tx, ty = tip
        u = np.array([tx - bx, ty - by]); u /= np.linalg.norm(u)
        for sgn in (-1, 1):
            n = np.array([-u[1], u[0]]) * sgn
            self.organ(base, (bx + u[0] * 9 * s + n[0] * 4 * s, by + u[1] * 9 * s + n[1] * 4 * s), 2 * s, shape='lance',
                       tint='#7d9a62', hatch=0, midrib=False, outline_w=0.6)

    def jasmine_sprig(self, pts, s=1.0, flowers=3, buds=4, seed_shift=0):
        C = self.stem(pts, width=2.2 * s)
        n = len(C)
        # opposite leaf pairs
        for i in range(8, n - 6, 9):
            p = C[i]
            d = C[min(n - 1, i + 1)] - C[i]
            d /= np.linalg.norm(d)
            nrm = np.array([-d[1], d[0]])
            for sgn in (1, -1):
                tip = p + (nrm * sgn * 0.8 + d * 0.6) * 58 * s
                self.organ(tuple(p), tuple(tip), 17 * s, bend=0.08 * sgn, shape='leaf', tint='#6f8f58', tint_op=0.5,
                           hatch=6, midrib=True, veins=4, outline_w=0.9)
        end = C[-1]
        d = C[-1] - C[-4]; d /= np.linalg.norm(d)
        # terminal cyme
        spots = [(0, 0), (-44, -18), (40, -26), (-10, -58), (54, 18), (-50, 26)]
        for k in range(min(flowers, len(spots))):
            ox, oy = spots[k]
            fx, fy = end[0] + ox * s + d[0] * 18 * s, end[1] + oy * s + d[1] * 18 * s
            self.lines.append((smooth_d([tuple(end), ((end[0] + fx) / 2, (end[1] + fy) / 2 + 4), (fx, fy)]), 0.7, 0.8))
            self.jasmine_flower(fx, fy, s * 1.35 * (1 - 0.08 * k), rot=k * 0.7)
        for k in range(buds):
            a = -1.9 + k * 0.85 + math.atan2(d[1], d[0])
            b0 = (end[0] + d[0] * 6 * s, end[1] + d[1] * 6 * s)
            tip = (b0[0] + math.cos(a) * 34 * s, b0[1] + math.sin(a) * 34 * s)
            self.jasmine_bud(b0, tip, s * 0.95)

    def mango_leaves(self, cx, cy, s=1.0, count=5, spread=70, base_ang=90, length=170):
        for k in range(count):
            ang = math.radians(base_ang + (k - (count - 1) / 2) * spread / max(1, count - 1))
            L = length * s * (0.9 + 0.2 * self.rng.random())
            tip = (cx + math.cos(ang) * L, cy + math.sin(ang) * L)
            self.organ((cx, cy), tip, 20 * s, bend=0.07 * (1 if k % 2 else -1), shape='lance', tint='#5f8a4e',
                       tint_op=0.55, hatch=7, midrib=True, veins=9, outline_w=1.0)

    def banana_flower(self, cx, cy, s=1.0):
        """Hanging banana blossom (arati puvvu): stalk from top, lifted bract with florets, teardrop cone."""
        top = cy - 120 * s
        self.stem([(cx + 40 * s, cy - 330 * s), (cx + 52 * s, cy - 260 * s), (cx + 26 * s, cy - 180 * s), (cx + 2 * s, top)], width=7 * s, tint='#7b8f5c')
        # lifted bract (behind florets), pale inside
        self.organ((cx - 6 * s, top + 8 * s), (cx - 92 * s, top - 70 * s), 40 * s, bend=-0.15, shape='bract',
                   tint='#b8687f', tint_op=0.5, hatch=9, midrib=False, roll=0.25)
        # florets, a curved row pointing up
        for k in range(8):
            x = cx - 44 * s + k * 11 * s
            y = top + 4 * s - 6 * s * math.sin(k / 7 * math.pi)
            self.organ((x, y), (x - 10 * s + k * 2.4 * s, y - 40 * s), 5.2 * s, bend=0.08, shape='petal', tint='#efcf7e',
                       tint_op=0.85, hatch=2, midrib=False, cross=False, outline_w=0.75)
        # cone of overlapping bracts, back (widest) to front
        for i, (dx, L, w, b, col) in enumerate([(0, 250, 70, 0.0, '#6e2a46'), (-8, 236, 62, 0.05, '#86375a'),
                                                (10, 222, 56, -0.05, '#7a2f4c'), (-4, 204, 50, 0.04, '#933f60'),
                                                (6, 182, 42, -0.03, '#7f3352')]):
            base = (cx + dx * s, top + (6 + i * 10) * s)
            self.organ(base, (cx + dx * 0.4 * s, base[1] + L * s), w * s, bend=b, shape='lotus', tint=col,
                       tint_op=0.62, hatch=12, midrib=False, roll=0.45)

    # ---------- output ----------
    def svg(self, ink=INK, tint=True, extra_defs='', paper_wash=False):
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">']
        out.append('<defs><filter id="wc" x="-5%" y="-5%" width="110%" height="110%">'
                   '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="4" result="n"/>'
                   '<feDisplacementMap in="SourceGraphic" in2="n" scale="7" xChannelSelector="R" yChannelSelector="G" result="d"/>'
                   '<feGaussianBlur in="d" stdDeviation="0.9"/></filter>' + extra_defs + '</defs>')
        for g in self.groups:
            if not (g['tint'] or g['lines'] or g['dots']):
                continue
            out.append('<g>')
            for d, c, op in g['tint']:
                if self.paper and op >= 0:
                    out.append(f'<path d="{d}" fill="{self.paper}"/>')
            if tint and g['tint']:
                out.append('<g filter="url(#wc)">' + ''.join(f'<path d="{d}" fill="{c}" fill-opacity="{abs(op)}"/>' for d, c, op in g['tint']) + '</g>')
            if g['lines']:
                out.append(f'<g fill="none" stroke="{ink}" stroke-linecap="round" stroke-linejoin="round">' +
                           ''.join(f'<path d="{d}" stroke-width="{w}" stroke-opacity="{op}"/>' for d, w, op in g['lines']) + '</g>')
            if g['dots']:
                out.append(f'<g fill="{ink}">' + ''.join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r:.2f}" fill-opacity="{op}"/>' for x, y, r, op in g['dots']) + '</g>')
            out.append('</g>')
        out.append('</svg>')
        return '\n'.join(out)


def rotate(p, c, a):
    if not a:
        return p
    x, y = p[0] - c[0], p[1] - c[1]
    ca, sa = math.cos(a), math.sin(a)
    return (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)


def ellipse_d(cx, cy, rx, ry):
    return f'M{f(cx - rx)},{f(cy)} a{f(rx)},{f(ry)} 0 1,0 {f(2 * rx)},0 a{f(rx)},{f(ry)} 0 1,0 {f(-2 * rx)},0 Z'


def save(name, d, **kw):
    with open(f'{OUTDIR}/{name}.svg', 'w') as fh:
        fh.write(d.svg(**kw))


if __name__ == '__main__':
    # 1. Corner spray for the invitation (lotus + mango leaves + jasmine), 900x900
    d = Drawing(900, 900, seed=3)
    d.lotus_leaf(420, 600, 190, 70, rot=-0.15)
    d.stem([(330, 640), (300, 520), (280, 420), (270, 330)], width=4.0)
    d.lotus(270, 330, s=1.25, rot=-0.15)
    d.stem([(520, 640), (560, 540), (580, 470)], width=3.2)
    d.lotus_bud(582, 468, s=0.95, rot=0.25)
    d.jasmine_sprig([(120, 720), (190, 640), (300, 590), (400, 560)], s=1.0, flowers=3, buds=3)
    d.jasmine_sprig([(700, 760), (640, 690), (600, 640)], s=0.85, flowers=2, buds=2)
    save('spray', d)

    # 2. Banana flower plate, 600x900
    d = Drawing(600, 900, seed=5)
    d.banana_flower(290, 540, s=1.15)
    save('banana', d)

    # 3. Jasmine sprig (single, long) 900x400
    d = Drawing(900, 420, seed=8)
    d.jasmine_sprig([(40, 330), (200, 280), (420, 230), (640, 200), (780, 170)], s=1.1, flowers=5, buds=5)
    save('jasmine', d)

    # 4. Lotus single bloom 700x700
    d = Drawing(700, 700, seed=9)
    d.lotus_leaf(350, 560, 250, 85, rot=0.05)
    d.stem([(350, 600), (345, 470), (350, 390)], width=4.5)
    d.lotus(350, 390, s=1.55)
    save('lotus', d)

    # 5. Mango leaf thoranam strip, 1200x260 (leaves hanging from a cord)
    d = Drawing(1200, 260, seed=12)
    cord = [(0, 30), (300, 40), (600, 44), (900, 40), (1200, 30)]
    d.lines.append((smooth_d(cord), 1.6, 0.9))
    for k in range(13):
        x = 40 + k * 93
        y = 32 + 12 * math.sin(math.pi * x / 1200)
        d.organ((x, y), (x + d.rng.uniform(-8, 8), y + 190), 22, bend=0.04 * (1 if k % 2 else -1), shape='lance',
                tint='#5f8a4e', tint_op=0.55, hatch=6, veins=8)
        if k % 3 == 1:
            d.jasmine_flower(x + 46, y + 8, s=0.55, rot=k)
    save('thoranam', d)

    # 6. Two-journeys plate: jasmine from left, lotus from right, stems entwine and meet, 900x1100
    d = Drawing(900, 1100, seed=21)
    left = [(60, 1080), (140, 900), (260, 760), (400, 640), (470, 520), (450, 400)]
    right = [(840, 1080), (760, 900), (640, 760), (500, 650), (430, 530), (450, 400)]
    d.stem(left, width=3.2)
    d.stem(right, width=3.2, tint='#7b9668')
    for i, (p0, p1) in enumerate(zip(left[1:4], left[2:5])):
        d.organ(p0, (p0[0] - 90 + i * 20, p0[1] - 40), 20, bend=0.1, shape='leaf', tint='#6f8f58', hatch=6, veins=4)
    for i, (p0, p1) in enumerate(zip(right[1:4], right[2:5])):
        d.organ(p0, (p0[0] + 100 - i * 20, p0[1] - 50), 22, bend=-0.1, shape='lance', tint='#5f8a4e', hatch=6, veins=7)
    d.lotus(450, 400, s=1.35)
    for (x, y, s) in [(300, 700, 0.9), (220, 820, 0.8), (380, 590, 0.75)]:
        d.jasmine_flower(x, y, s=s, rot=x * 0.01)
    d.lotus_bud(700, 840, s=0.8, rot=0.35)
    save('journeys', d)

    # 7. Wreath of mango leaves + jasmine buds around a monogram, 800x800 (lines only, used as foil mask)
    d = Drawing(800, 800, seed=31)
    d.paper = None
    for side in (-1, 1):
        for k in range(11):
            a0 = math.pi / 2 + side * (0.35 + k * 0.215)
            a1 = a0 + side * 0.20
            r = 300
            p = (400 + math.cos(a0) * r, 400 + math.sin(a0) * r)
            outwards = (k % 2 == 0)
            rr = r + (58 if outwards else -52)
            tip = (400 + math.cos(a1) * rr, 400 + math.sin(a1) * rr)
            d.organ(p, tip, 13, bend=0.12 * side, shape='lance', hatch=3, veins=4, cross=False, outline_w=1.4)
        arc = [(400 + math.cos(math.pi / 2 + side * t) * 300, 400 + math.sin(math.pi / 2 + side * t) * 300) for t in np.linspace(0.25, 2.65, 30)]
        d.begin(); d.lines.append((smooth_d(arc), 1.8, 1))
    for k in range(5):
        a = math.pi / 2 + (k - 2) * 0.09
        d.jasmine_bud((400 + math.cos(a) * 300, 400 + math.sin(a) * 300), (400 + math.cos(a) * 345, 400 + math.sin(a) * 345), 1.3)
    save('wreath', d, tint=False)

    # 8. Liner tile 480x480: scattered small jasmine and leaves (kept inside margins so it tiles)
    d = Drawing(480, 480, seed=41)
    d.paper = None
    for (x, y, r) in [(120, 110, 0.4), (360, 230, 2.1), (150, 370, 4.0)]:
        d.jasmine_flower(x, y, s=0.9, rot=r)
        d.organ((x + 22, y + 10), (x + 70, y + 40), 12, bend=0.1, shape='leaf', tint='#6f8f58', hatch=4, veins=3)
        d.organ((x - 18, y + 14), (x - 52, y + 60), 11, bend=-0.1, shape='leaf', tint='#6f8f58', hatch=4, veins=3)
    for (x, y, a) in [(300, 80, 0.5), (60, 250, -0.7), (400, 410, 1.2), (250, 300, 2.3)]:
        d.jasmine_bud((x, y), (x + math.cos(a) * 34, y + math.sin(a) * 34), 1.0)
    save('liner', d)
    print('ok', os.listdir(OUTDIR))
