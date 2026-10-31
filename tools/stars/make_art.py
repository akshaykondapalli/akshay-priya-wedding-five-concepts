"""Procedural artwork for 'Nine Fifty-Five Under the Stars'.
Outputs (in ../../site5/stars/img):
  horizon.webp  - silhouette layer (palms, distant treeline, open-air pandal), transparent sky
  glow.webp     - warm light layer (lanterns, string lights, pandal glow), for screen blending
  milky.webp    - faint milky band texture (alpha), drawn into the sky canvas
Run: python3 -I make_art.py
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

OUT = '/home/claude/site5/stars/img/'
W, H = 2400, 1000           # final
S = 2                        # supersample
rng = random.Random(955)
np.random.seed(955)

def ss(v): return int(v * S)

# ---------------------------------------------------------------- silhouette
def bezier(p0, p1, p2, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0]
        y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]
        pts.append((x, y))
    return pts

def palm(d, x, base, h, lean, color, scale=1.0, fronds=13):
    """Coconut palm: tapered curved trunk + drooping fronds made of leaflets."""
    top = (x + lean * h, base - h)
    ctrl = (x + lean * h * 0.15, base - h * 0.55)
    spine = bezier((x, base), ctrl, top, 60)
    w0, w1 = 15 * scale, 7 * scale
    left, right = [], []
    for i, (px, py) in enumerate(spine):
        t = i / (len(spine) - 1)
        w = w0 + (w1 - w0) * t
        # ring bulges
        w *= 1 + 0.06 * math.sin(i * 1.9)
        left.append((ss(px - w / 2), ss(py)))
        right.append((ss(px + w / 2), ss(py)))
    d.polygon(left + right[::-1], fill=color)
    tx, ty = top
    # coconut cluster
    for k in range(5):
        r = 7 * scale
        d.ellipse([ss(tx - 14*scale + k*6*scale - r), ss(ty + 6*scale - r), ss(tx - 14*scale + k*6*scale + r), ss(ty + 6*scale + r)], fill=color)
    for f in range(fronds):
        ang = -math.pi / 2 + (f / (fronds - 1) - 0.5) * math.pi * 1.75 + rng.uniform(-0.12, 0.12)
        L = h * rng.uniform(0.34, 0.46) * (0.82 if abs(math.cos(ang)) < 0.3 else 1)
        droop = L * rng.uniform(0.55, 0.95)
        ex = tx + math.cos(ang) * L
        ey = ty + math.sin(ang) * L * 0.55 + droop * 0.6
        cx = tx + math.cos(ang) * L * 0.55
        cy = ty + math.sin(ang) * L * 0.6 - L * 0.12
        rib = bezier((tx, ty), (cx, cy), (ex, ey), 46)
        # rib
        d.line([(ss(a), ss(b)) for a, b in rib], fill=color, width=max(2, ss(2.6 * scale)))
        # leaflets
        for i in range(2, len(rib) - 1):
            t = i / len(rib)
            px, py = rib[i]
            qx, qy = rib[i + 1]
            dx, dy = qx - px, qy - py
            n = math.hypot(dx, dy) or 1
            nx, ny = -dy / n, dx / n
            ll = (1 - t) * 0.28 * L * 0.55 + 6 * scale
            for side in (-1, 1):
                hang = 0.55 + 0.35 * t
                lx = px + (nx * side * 0.55 + dx / n * 0.35) * ll
                ly = py + (ny * side * 0.55 + hang) * ll
                d.polygon([(ss(px), ss(py)), (ss(qx), ss(qy)), (ss(lx + dx * 0.2), ss(ly + dy * 0.2))], fill=color)
    return top

def treeline(d, base, amp, color, seed, step=6):
    r = random.Random(seed)
    pts = [(0, ss(H))]
    y = base
    x = 0
    while x <= W + step:
        bump = 0
        for (f, a, ph) in [(0.004, 1.0, 0.3), (0.013, 0.45, 1.7), (0.041, 0.22, 2.2), (0.11, 0.09, 0.9)]:
            bump += a * math.sin(x * f + ph + seed)
        yy = base - amp * (0.6 + 0.4 * bump) - r.random() * amp * 0.12
        pts.append((ss(x), ss(yy)))
        x += step
    pts.append((ss(W), ss(H)))
    d.polygon(pts, fill=color)

def pandal(d, cx, base, w, h, color):
    """Open-air wedding pandal: four slender pillars, a gently peaked canopy with
    scalloped valance and tied-back drapes. Returns interior box for glow."""
    x0, x1 = cx - w / 2, cx + w / 2
    roof_y = base - h
    peak = roof_y - h * 0.22
    # canopy (slightly peaked, with eaves)
    d.polygon([(ss(x0 - 26), ss(roof_y + 6)), (ss(cx), ss(peak)), (ss(x1 + 26), ss(roof_y + 6)),
               (ss(x1 + 26), ss(roof_y + 22)), (ss(x0 - 26), ss(roof_y + 22))], fill=color)
    # finial (kalasam-like silhouette)
    d.ellipse([ss(cx - 9), ss(peak - 18), ss(cx + 9), ss(peak)], fill=color)
    d.polygon([(ss(cx - 3), ss(peak - 16)), (ss(cx), ss(peak - 34)), (ss(cx + 3), ss(peak - 16))], fill=color)
    # scalloped valance
    n = 14
    sw = (w + 52) / n
    for i in range(n):
        sx = x0 - 26 + i * sw
        d.chord([ss(sx), ss(roof_y + 8), ss(sx + sw), ss(roof_y + 46)], 0, 180, fill=color)
    # pillars
    for px in (x0, x0 + w * 0.33, x1 - w * 0.33, x1):
        d.rectangle([ss(px - 5), ss(roof_y + 20), ss(px + 5), ss(base)], fill=color)
        d.rectangle([ss(px - 9), ss(base - 10), ss(px + 9), ss(base)], fill=color)
    # drapes tied back at outer pillars (curved wedges)
    for side in (-1, 1):
        px = x0 if side < 0 else x1
        inner = px - side * w * 0.17
        pts = [(ss(px), ss(roof_y + 22)), (ss(inner), ss(roof_y + 22))]
        pts += [(ss(a), ss(b)) for a, b in bezier((inner, roof_y + 22), (px - side * w * 0.04, base - h * 0.45), (px, base - h * 0.42), 20)]
        pts += [(ss(px), ss(base - h * 0.42 + 4))]
        d.polygon(pts, fill=color)
        # fall of drape below tie
        d.polygon([(ss(px - 6), ss(base - h * 0.42)), (ss(px + 6), ss(base - h * 0.42)),
                   (ss(px + side * 16), ss(base)), (ss(px - side * 4), ss(base))], fill=color)
    # steps / platform
    d.rectangle([ss(x0 - 30), ss(base - 6), ss(x1 + 30), ss(base + 8)], fill=color)
    return (x0, roof_y + 46, x1, base)

def build(cfg, suffix):
    global W
    W = cfg['W']
    sil = Image.new('RGBA', (ss(W), ss(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(sil)
    far = (22, 30, 64, 255)
    mid = (12, 17, 40, 255)
    near = (5, 7, 18, 255)
    ground = 870
    # far treeline (haze)
    treeline(d, ground - 70, 70, far, 1.3, step=5)
    # far palms (small)
    for x in cfg['far']:
        palm(d, x + rng.uniform(-20, 20), ground - 40, rng.uniform(190, 250), rng.uniform(-0.12, 0.12), far, 0.55, 11)
    # mid treeline
    treeline(d, ground - 20, 42, mid, 4.1, step=4)
    for x in cfg['mid']:
        palm(d, x + rng.uniform(-30, 30), ground - 10, rng.uniform(300, 380), rng.uniform(-0.16, 0.16), mid, 0.8, 12)
    # ground
    d.rectangle([0, ss(ground), ss(W), ss(H)], fill=near)
    # pandal
    pc = cfg['pandal']
    # lit back cloth inside the pandal (gets warmed by the glow layer)
    d.rectangle([ss(pc - 205), ss(ground + 6 - 230), ss(pc + 205), ss(ground + 6)], fill=(44, 26, 26, 255))
    inner = (18, 12, 16, 255)
    gb = ground + 6
    # inner backdrop: a cusped arch frame behind the wedding platform
    aw, ah = 150, 170
    d.rectangle([ss(pc - aw/2 - 12), ss(gb - ah), ss(pc - aw/2), ss(gb - 14)], fill=inner)
    d.rectangle([ss(pc + aw/2), ss(gb - ah), ss(pc + aw/2 + 12), ss(gb - 14)], fill=inner)
    d.pieslice([ss(pc - aw/2 - 12), ss(gb - ah - 60), ss(pc + aw/2 + 12), ss(gb - ah + 60)], 180, 360, fill=inner)
    d.pieslice([ss(pc - aw/2), ss(gb - ah - 48), ss(pc + aw/2), ss(gb - ah + 48)], 180, 360, fill=(44, 26, 26, 255))
    # low wedding platform with two seats
    d.rectangle([ss(pc - 110), ss(gb - 22), ss(pc + 110), ss(gb - 8)], fill=inner)
    for sx in (pc - 34, pc + 34):
        d.rectangle([ss(sx - 18), ss(gb - 60), ss(sx + 18), ss(gb - 22)], fill=inner)
        d.ellipse([ss(sx - 18), ss(gb - 72), ss(sx + 18), ss(gb - 48)], fill=inner)
    # brass kalasam with coconut and mango leaves at both ends of the platform
    for kx in (pc - 96, pc + 96):
        d.ellipse([ss(kx - 13), ss(gb - 48), ss(kx + 13), ss(gb - 22)], fill=inner)
        d.rectangle([ss(kx - 6), ss(gb - 54), ss(kx + 6), ss(gb - 44)], fill=inner)
        d.ellipse([ss(kx - 8), ss(gb - 68), ss(kx + 8), ss(gb - 52)], fill=inner)
        for lf in (-1, 1):
            d.polygon([(ss(kx), ss(gb - 56)), (ss(kx + lf * 18), ss(gb - 64)), (ss(kx + lf * 14), ss(gb - 54))], fill=inner)
    box = pandal(d, pc, ground + 6, 420, 250, near)
    # jasmine strands hanging from the valance (dark against the lit cloth)
    for i in range(23):
        sx = pc - 200 + i * (400 / 22)
        ln = 34 + (i % 3) * 10 + (8 if i % 2 else 0)
        top_y = gb - 250 + 46
        d.line([(ss(sx), ss(top_y)), (ss(sx), ss(top_y + ln))], fill=near, width=ss(1.4))
        d.ellipse([ss(sx - 2.6), ss(top_y + ln - 2), ss(sx + 2.6), ss(top_y + ln + 4)], fill=near)
    # near palms framing
    tops = []
    for (px, pb, ph, pl, psc) in cfg['near']:
        tops.append(palm(d, px, pb, ph, pl, near, psc, 15))
    # low shrubs / banana plants near pandal
    for bx in (pc - 270, pc + 270):
        for k in range(7):
            ang = -math.pi / 2 + (k - 3) * 0.33
            L = rng.uniform(90, 130)
            ex, ey = bx + math.cos(ang) * L * 1.2, ground - 30 + math.sin(ang) * L
            pts = bezier((bx, ground - 20), (bx + math.cos(ang) * L * 0.5, ground - 60 + math.sin(ang) * L * 0.9), (ex, ey + 30), 18)
            poly = [(ss(a), ss(b - 7)) for a, b in pts] + [(ss(a), ss(b + 7)) for a, b in pts[::-1]]
            d.polygon(poly, fill=near)
        d.rectangle([ss(bx - 7), ss(ground - 30), ss(bx + 7), ss(ground + 4)], fill=near)
    sil = sil.resize((W, H), Image.LANCZOS)
    sil.save(OUT + 'horizon' + suffix + '.webp', quality=86, method=6)

    # ------------------------------------------------------------ glow layer
    g = np.zeros((H, W, 3), np.float32)
    def add_spot(x, y, r, col, k=1.0):
        yy, xx = np.ogrid[max(0, int(y - r*4)):min(H, int(y + r*4)), max(0, int(x - r*4)):min(W, int(x + r*4))]
        dist2 = (xx - x) ** 2 + (yy - y) ** 2
        v = np.exp(-dist2 / (2 * r * r)) * k
        g[yy, xx] += v[..., None] * np.array(col, np.float32)
    amber = (1.0, 0.66, 0.30)
    warm = (1.0, 0.80, 0.52)
    x0, y0, x1, y1 = box
    # interior wash of the pandal
    m = np.zeros((H, W), np.float32)
    m[int(y0):int(y1), int(x0):int(x1)] = 1
    m = gaussian_filter(m, 26)
    vert = np.linspace(0.35, 1.0, H)[:, None].astype(np.float32)
    sa = np.asarray(sil).astype(np.int16)
    cloth = ((np.abs(sa[..., 0] - 44) + np.abs(sa[..., 1] - 26) + np.abs(sa[..., 2] - 26)) < 22) & (sa[..., 3] > 200)
    cloth = gaussian_filter(cloth.astype(np.float32), 1.2)
    g += (m * vert * (0.08 + 0.72 * cloth))[..., None] * np.array(amber)
    add_spot((x0 + x1) / 2, y1 - 40, 120, amber, 0.22)
    # ground pool of light
    pool = np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    pool = np.exp(-(((xx - (x0 + x1) / 2) / 360) ** 2 + ((yy - (ground + 40)) / 46) ** 2))
    g += (pool * 0.18)[..., None] * np.array(amber)
    # string lights: catenaries from pandal roof to palms
    def catenary(a, b, sag, n):
        pts = []
        for i in range(n + 1):
            t = i / n
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)
            pts.append((x, y))
        return pts
    anchors = [((x0 - 24, y0 - 30), a) for a in cfg['strL']] + [((x1 + 24, y0 - 30), a) for a in cfg['strR']] + [((x0 + 10, y0 - 40), (x1 - 10, y0 - 40))]
    sags = cfg['sags'] + [26]
    for (a, b), sag in zip(anchors, sags):
        pts = catenary(a, b, sag, 26 if sag > 30 else 12)
        for (x, y) in pts:
            add_spot(x, y, 2.2, warm, 1.6)
            add_spot(x, y, 9, amber, 0.22)
    # hanging lanterns inside canopy
    lant = []
    for i in range(5):
        lx = x0 + (i + 0.5) * (x1 - x0) / 5
        ly = y0 + 34 + (i % 2) * 14
        lant.append((lx, ly))
        add_spot(lx, ly, 6, warm, 1.5)
        add_spot(lx, ly, 34, amber, 0.5)
    # deepam row on the platform edge
    for i in range(13):
        lx = x0 - 20 + i * (x1 - x0 + 40) / 12
        add_spot(lx, y1 - 4, 2.4, warm, 1.8)
        add_spot(lx, y1 - 6, 10, amber, 0.3)
    g = 1 - np.exp(-g * 1.15)   # soft tone map
    img = Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8), 'RGB')
    img.save(OUT + 'glow' + suffix + '.webp', quality=82, method=6)

    # lantern shapes drawn into silhouette? (they are lights; draw small frames on top)
    return lant

def milky():
    N = 1400
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    # band along a diagonal
    c = N / 2
    u = ((xx - c) * math.cos(0.6) + (yy - c) * math.sin(0.6))
    v = (-(xx - c) * math.sin(0.6) + (yy - c) * math.cos(0.6))
    band = np.exp(-(v / (N * 0.13)) ** 2) * (0.6 + 0.4 * np.exp(-(u / (N * 0.45)) ** 2))
    noise = np.zeros((N, N), np.float32)
    for s, a in [(80, 1.0), (30, 0.6), (10, 0.4), (3, 0.25)]:
        n = np.random.rand(N // s + 2, N // s + 2).astype(np.float32)
        n = np.array(Image.fromarray((n * 255).astype(np.uint8)).resize((N, N), Image.BICUBIC), np.float32) / 255
        noise += a * n
    noise /= noise.max()
    # dust lane
    lane = np.exp(-((v + N * 0.02 + 30 * np.sin(u / 140)) / (N * 0.025)) ** 2)
    a = band * (0.45 + 0.75 * noise) * (1 - 0.7 * lane)
    # star dust speckle
    speck = (np.random.rand(N, N) ** 60) * band * 2.2
    a = np.clip(a * 0.55 + speck, 0, 1)
    a = gaussian_filter(a, 1.0)
    rgb = np.zeros((N, N, 4), np.uint8)
    rgb[..., 0] = 205; rgb[..., 1] = 212; rgb[..., 2] = 238
    rgb[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(rgb, 'RGBA').resize((1000, 1000), Image.LANCZOS).save(OUT + 'milky.webp', quality=70, method=6)

if __name__ == '__main__':
    DESK = dict(W=2400, far=[140, 330, 610, 1520, 1760, 2050, 2290], mid=[60, 420, 820, 1330, 1960, 2200], pandal=1230,
                near=[(250, H + 20, 620, 0.16, 1.4), (700, 870 + 30, 470, -0.10, 1.1), (1720, 870 + 30, 500, 0.09, 1.15), (2230, H + 20, 650, -0.18, 1.45)],
                strL=[(730, 870 - 380), (330, 870 - 420)], strR=[(1700, 870 - 400), (2130, 870 - 440)], sags=[70, 120, 80, 130])
    MOB = dict(W=1200, far=[90, 260, 930, 1110], mid=[40, 300, 880, 1170], pandal=600,
               near=[(70, H + 40, 820, 0.14, 1.35), (1140, H + 40, 860, -0.15, 1.4)],
               strL=[(150, 870 - 600)], strR=[(1060, 870 - 640)], sags=[110, 120])
    build(DESK, '')
    rng.seed(956)
    build(MOB, '-m')
    milky()
    print('done')
