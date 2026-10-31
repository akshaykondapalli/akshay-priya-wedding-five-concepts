"""Letters Across Continents v2 — light keepsake-box redesign. Original procedural artwork.
Run: python3 gen2.py   (ONLY=fn1,fn2 to regenerate parts)
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, distance_transform_edt, zoom
import gen as g

OUT = '/home/claude/site5/letters/img'
os.makedirs(OUT, exist_ok=True)
F, fnoise, to_img, save, paper = g.F, g.fnoise, g.to_img, g.save, g.paper
rng = np.random.default_rng(2026)

IVORY = (246, 241, 231)


# ------------------------------------------------------------ helpers
def wrapnoise(h, w, sigma, seed):
    r = np.random.default_rng(seed)
    n = gaussian_filter(r.standard_normal((h, w)), sigma, mode='wrap')
    return n / (n.std() + 1e-9)


def weave(h, w, p, seed, tile=False, slub=1.0):
    """Plain-weave linen luminance (mean ~1)."""
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    nx, ny = int(math.ceil(w / p)) + 1, int(math.ceil(h / p)) + 1
    colv = 1 + r.normal(0, 0.06, nx)
    rowv = 1 + r.normal(0, 0.06, ny)
    mode = 'wrap' if tile else 'reflect'
    sl_w = gaussian_filter(r.standard_normal((h, nx)), (14, 0), mode=mode); sl_w /= sl_w.std() + 1e-9
    sl_h = gaussian_filter(r.standard_normal((ny, w)), (0, 14), mode=mode); sl_h /= sl_h.std() + 1e-9
    i = (xx // p).astype(int); j = (yy // p).astype(int)
    fx = (xx % p) / p; fy = (yy % p) / p
    warp = (0.78 + 0.22 * np.sin(math.pi * fx)) * colv[i] * (1 + 0.07 * slub * sl_w[yy.astype(int), i])
    weft = (0.78 + 0.22 * np.sin(math.pi * fy)) * rowv[j] * (1 + 0.07 * slub * sl_h[j, xx.astype(int)])
    over = ((i + j) % 2) == 0
    v = np.where(over, warp * (0.92 + 0.08 * np.sin(math.pi * fy)), weft * (0.92 + 0.08 * np.sin(math.pi * fx)))
    v = gaussian_filter(v, 0.45, mode=mode)
    v += r.normal(0, 0.02, v.shape)
    return v / v.mean()


def shade_light(h, w, strength=0.08):
    gy, gx = np.mgrid[0:h, 0:w].astype(float)
    return 1 + strength * (0.5 - (gx / w * 0.45 + gy / h * 0.55))


def foil(mask, seed=1, base=(200, 168, 104)):
    h, w = mask.shape
    hm = gaussian_filter(mask.astype(float), 1.1)
    nx = -np.gradient(hm, axis=1) * 3; ny = -np.gradient(hm, axis=0) * 3
    edge = np.clip(-nx * 0.6 - ny * 0.8, -1, 1)
    gy, gx = np.mgrid[0:h, 0:w].astype(float)
    n = fnoise(h, w, base=max(8, min(h, w) // 6), octaves=3, seed=seed)
    band = 0.5 + 0.5 * np.sin((gx * 0.7 + gy) / (max(h, w) * 0.22) * 2 * math.pi + n * 3)
    b = np.array(base, float)
    col = b * (0.84 + 0.36 * band)[..., None]
    col += (band ** 8)[..., None] * np.array([255, 246, 220.]) * 0.45
    col *= (1 + 0.35 * edge)[..., None]
    col += (fnoise(h, w, base=3, octaves=1, seed=seed + 3) - 0.5)[..., None] * 14
    return np.clip(col, 0, 255)


def put(base_rgb, base_a, col, a, x0, y0):
    g.composite(base_rgb, base_a, col, a, int(x0), int(y0))


def text_mask(w, h, items):
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    for (xy, s, font, size, anchor) in items:
        d.text(xy, s, font=F(font, size), fill=255, anchor=anchor)
    return np.asarray(m) / 255.0


def drop(rgb, a, off=(10, 16), blur=14, op=0.35):
    sh = np.roll(np.roll(gaussian_filter(a, blur), off[1], 0), off[0], 1) * op
    return sh


# ------------------------------------------------------------ backgrounds
def linen_bg():
    T = 600
    v = weave(T, T, 6, 7, tile=True)
    col = np.array([238, 231, 219.]) * (1 + (v[..., None] - 1) * 0.42)
    col += wrapnoise(T, T, 40, 9)[..., None] * 1.6
    save(to_img(col), 'linen.webp', 80)
    # window light: soft panes + leaf dapple, as a white light map with alpha
    W, H = 1000, 1400
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    # skewed window panes
    u = gx + gy * 0.42 - 120; vv = gy * 0.92 - gx * 0.18
    panes = ((u % 360) > 40) & ((vv % 460) > 46) & (u > 0) & (u < 1100) & (vv > -60) & (vv < 1000)
    light = gaussian_filter(panes.astype(float), 34)
    leaf = fnoise(H, W, base=90, octaves=4, seed=31)
    leaf = np.clip((leaf - 0.45) * 4, 0, 1)
    light = light * (0.55 + 0.45 * gaussian_filter(leaf, 10))
    glow = np.exp(-(((gx - W * 0.25) / (W * 0.8)) ** 2 + ((gy - H * 0.05) / (H * 0.7)) ** 2))
    a = np.clip(light * 0.75 + glow * 0.35, 0, 1)
    col = np.zeros((H, W, 3)) + np.array([255, 244, 222.])
    save(to_img(col, a), 'window-light.webp', 70)


# ------------------------------------------------------------ satin ribbon
RIB = (214, 172, 164)  # dusty blush satin


def satin_band(L, Wd, seed, color=RIB):
    r = np.random.default_rng(seed)
    u = np.arange(L, dtype=float)[None, :] * np.ones((Wd, 1))
    v = (np.arange(Wd, dtype=float)[:, None] / (Wd - 1)) * 2 - 1 + 0 * u
    c = 0.22 * np.sin(u / 210 + seed) + 0.15 * np.sin(u / 63 + 2 * seed)
    hi = np.exp(-((v - c) / 0.2) ** 2) * 0.42 + np.exp(-((v + c * 0.6 + 0.55) / 0.12) ** 2) * 0.15
    stri = gaussian_filter(r.standard_normal((Wd, L)), (0.5, 40)); stri /= stri.std()
    base = 0.80 + 0.12 * np.cos(v * math.pi / 2) + 0.02 * stri
    selv = np.exp(-((np.abs(v) - 0.93) / 0.03) ** 2) * 0.10
    lum = base + hi - selv
    col = np.array(color, float)[None, None, :] * lum[..., None] + (hi ** 2)[..., None] * 60
    return np.clip(col, 0, 255)


def shape_satin(mask, center, seed, color=RIB, streak=7, inner=None):
    h, w = mask.shape
    gy, gx = np.mgrid[0:h, 0:w].astype(float)
    th = np.arctan2(gy - center[1], gx - center[0]); rr = np.hypot(gx - center[0], gy - center[1])
    dist = distance_transform_edt(mask > 0.5)
    t = np.clip(dist / 26.0, 0, 1)
    n = fnoise(h, w, base=40, octaves=2, seed=seed)
    sh = 0.5 + 0.5 * np.cos(th * streak + rr / 34 + n * 4)
    lum = 0.66 + 0.24 * np.sqrt(t) + 0.22 * sh ** 3
    col = np.array(color, float) * lum[..., None] + ((sh ** 10) * t)[..., None] * 70
    if inner is not None:
        col *= (1 - inner[..., None] * 0.32)
    return np.clip(col, 0, 255)


def poly_mask(w, h, pts, blur=0.8):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    return gaussian_filter(np.asarray(m) / 255.0, blur)


def teardrop(k, tip, width, bend=0.25, n=60):
    kx, ky = k; tx, ty = tip
    dx, dy = tx - kx, ty - ky; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; px, py = -uy, ux
    up, dn = [], []
    for i in range(n + 1):
        s = i / n
        hw = width * math.sin(math.pi * s) ** 0.75 * (0.35 + 0.65 * s) + 3
        cx = kx + dx * s + px * bend * L * math.sin(math.pi * s) * 0.4
        cy = ky + dy * s + py * bend * L * math.sin(math.pi * s) * 0.4
        up.append((cx + px * hw, cy + py * hw)); dn.append((cx - px * hw, cy - py * hw))
    return up + dn[::-1]


def bow(W=460, H=380, color=RIB, seed=5):
    can = np.zeros((H, W, 3)); al = np.zeros((H, W))
    K = (W / 2, H * 0.40)
    layers = []
    # tails
    for sgn in (-1, 1):
        x1 = K[0] + sgn * W * 0.30; y1 = H * 0.97
        pts = [(K[0] - 18, K[1]), (K[0] + 18, K[1]), (x1 + 30, y1 - 6), (x1, y1 - 34), (x1 - 30, y1 - 2)]
        pts = [(K[0] + sgn * (x - K[0]) if False else x, y) for (x, y) in pts]
        m = poly_mask(W, H, pts)
        layers.append((m, None, 5))
    # loops
    for sgn in (-1, 1):
        tip = (K[0] + sgn * W * 0.47, K[1] - H * 0.10)
        m = poly_mask(W, H, teardrop(K, tip, 84, bend=-0.18 * sgn))
        cx = K[0] + sgn * W * 0.30; cy = K[1] - H * 0.07
        inner = poly_mask(W, H, teardrop((K[0] + sgn * 50, K[1] - 4), (cx + sgn * 50, cy - 6), 30, bend=-0.18 * sgn), 4)
        layers.append((m, inner, 6))
    # knot
    kn = Image.new('L', (W, H), 0); ImageDraw.Draw(kn).rounded_rectangle((K[0] - 34, K[1] - 34, K[0] + 34, K[1] + 32), 18, fill=255)
    layers.append((gaussian_filter(np.asarray(kn) / 255.0, 0.8), None, 3))
    for k, (m, inner, st) in enumerate(layers):
        sh = drop(None, m, (4, 8), 7, 0.35)
        can *= (1 - (sh * al)[..., None] * 0.6)
        col = shape_satin(m, K, seed + k, color, st, inner)
        put(can, al, col, m, 0, 0)
    return to_img(can, al)


def ribbons():
    v = satin_band(1240, 92, 3).transpose(1, 0, 2)
    a = np.ones(v.shape[:2]); a[:, :2] = 0.4; a[:, -2:] = 0.4
    save(to_img(v, a), 'ribbon-v.webp', 82)
    hband = satin_band(1000, 92, 4)
    a = np.ones(hband.shape[:2]); a[:2] = 0.4; a[-2:] = 0.4
    save(to_img(hband, a), 'ribbon-h.webp', 82)
    save(bow(), 'bow.webp', 84)
    # champagne ribbon for invitation & vellum sleeve
    C = (216, 196, 156)
    v = satin_band(760, 70, 8, C).transpose(1, 0, 2)
    save(to_img(v, np.ones(v.shape[:2])), 'ribbon-champ-v.webp', 82)
    hb = satin_band(1000, 56, 9, C)
    save(to_img(hb, np.ones(hb.shape[:2])), 'ribbon-champ-h.webp', 82)
    save(bow(380, 300, C, 11), 'bow-champ.webp', 84)


# ------------------------------------------------------------ keepsake box
BW, BH = 1000, 1240


def box():
    gy, gx = np.mgrid[0:BH, 0:BW].astype(float)
    # lid: fine ivory linen with bevel shading
    v = weave(BH, BW, 4, 17)
    lid = np.array([242, 235, 221.]) * (1 + (v[..., None] - 1) * 0.5) * shade_light(BH, BW, 0.1)[..., None]
    d = np.minimum.reduce([gx, gy, BW - 1 - gx, BH - 1 - gy])
    bev = np.exp(-d / 10.0)
    tl = ((gx < gy * BW / BH) == (gx + gy < BW)).astype(float)  # rough side selector
    side = np.where((gx / BW + gy / BH) < 1, 1.0, -1.0)
    lid *= (1 + bev[..., None] * 0.10 * side[..., None])
    lid *= (1 - np.exp(-d / 3.0)[..., None] * 0.12)
    # gold foil monogram
    mono = text_mask(BW, BH, [((BW / 2, BH * 0.235), 'A & P', 'saint', 190, 'mm')])
    ring = Image.new('L', (BW, BH), 0); dr = ImageDraw.Draw(ring)
    cx, cy, R = BW / 2, BH * 0.235, 118
    dr.ellipse((cx - R, cy - R, cx + R, cy + R), outline=255, width=3)
    dr.ellipse((cx - R - 12, cy - R - 12, cx + R + 12, cy + R + 12), outline=255, width=1)
    m = np.clip(mono + np.asarray(ring) / 255.0, 0, 1)
    fc = foil(m, 3)
    deb = gaussian_filter(m, 2)
    lid *= (1 - (np.gradient(deb, axis=0) + np.gradient(deb, axis=1))[..., None] * 1.2)
    lid = lid * (1 - m[..., None]) + fc * m[..., None]
    t = text_mask(BW, BH, [((BW / 2, BH * 0.37), 'G A T H E R E D', 'bodoni', 24, 'mm'), ((BW / 2, BH * 0.397), 'A C R O S S   C O N T I N E N T S', 'bodoni', 24, 'mm')])
    lid = lid * (1 - t[..., None] * 0.8) + np.array([156, 128, 84.]) * t[..., None] * 0.8
    save(to_img(lid), 'box-lid.webp', 80)

    # base interior: rim, walls, blush silk floor
    rim = 30; wall = 70
    v2 = weave(BH, BW, 4, 19)
    base = np.array([236, 230, 216.]) * v2[..., None]
    silk = np.array([238, 220, 212.]) * (0.93 + 0.07 * fnoise(BH, BW, base=300, octaves=3, seed=4))[..., None]
    silk += (np.sin((gx * 0.5 + gy) / 260.0 + fnoise(BH, BW, base=300, octaves=2, seed=6) * 2) ** 6)[..., None] * 6
    x0, y0, x1, y1 = rim + wall, rim + wall, BW - rim - wall, BH - rim - wall
    floor = (gx >= x0) & (gx <= x1) & (gy >= y0) & (gy <= y1)
    out = base.copy()
    # walls (trapezoids): top/left in shade, bottom/right lit
    inside = (gx >= rim) & (gx <= BW - rim) & (gy >= rim) & (gy <= BH - rim)
    tw = inside & ~floor & (gy < y0) & (gy - rim <= (gx - rim) * 99) & ((gy - rim) <= (gx - rim)) & ((gy - rim) <= (BW - rim - gx))
    bw_ = inside & ~floor & ((BH - rim - gy) <= (gx - rim)) & ((BH - rim - gy) <= (BW - rim - gx))
    lw = inside & ~floor & ~tw & ~bw_ & (gx < BW / 2)
    rw = inside & ~floor & ~tw & ~bw_ & (gx >= BW / 2)
    wallcol = np.array([226, 214, 200.]) * v2[..., None]
    out = np.where(tw[..., None], wallcol * 0.70, out)
    out = np.where(lw[..., None], wallcol * 0.78, out)
    out = np.where(rw[..., None], wallcol * 1.0, out)
    out = np.where(bw_[..., None], wallcol * 1.04, out)
    fl = silk.copy()
    # cast shadow on floor from top-left walls
    sd = np.clip(1 - np.minimum((gx - x0) / 140.0, (gy - y0) / 140.0), 0, 1)
    fl *= (1 - (sd ** 1.6 * 0.30))[..., None]
    out = np.where(floor[..., None], fl, out)
    out = gaussian_filter(out, (0.7, 0.7, 0))
    save(to_img(out), 'box-in.webp', 80)

    # tissue halves
    for side_, seed in (('l', 41), ('r', 42)):
        tw2 = BW // 2 + 40 - rim - wall + 10
        th2 = BH - 2 * (rim + wall) + 20
        n1 = fnoise(th2, tw2, base=60, octaves=4, seed=seed)
        crink = np.abs(gaussian_filter(np.random.default_rng(seed).standard_normal((th2, tw2)), (3, 18)))
        crink = crink / crink.max()
        lum = 0.93 + 0.05 * (n1 - 0.5) - crink * 0.07 + gaussian_filter(np.random.default_rng(seed + 1).standard_normal((th2, tw2)), (14, 2)) * 0.02
        col = np.array([252, 250, 246.]) * lum[..., None]
        gy2, gx2 = np.mgrid[0:th2, 0:tw2].astype(float)
        edgex = gx2 if side_ == 'r' else (tw2 - 1 - gx2)
        jag = 6 + 5 * fnoise(th2, 1, base=6, octaves=2, seed=seed + 5)[:, 0][:, None]
        a = np.clip((edgex - jag) / 2, 0, 1) * 0.94
        a *= np.clip(np.minimum(gy2, th2 - 1 - gy2) / 3, 0, 1)
        col *= (1 - np.exp(-np.maximum(edgex - jag, 0) / 8)[..., None] * 0.05)
        save(to_img(col, a), f'tissue-{side_}.webp', 78)


# ------------------------------------------------------------ wax seal
def seals():
    rgb, a = g.seal(440, 7)
    # warm the oxblood slightly
    rgb = np.clip(rgb * np.array([1.05, 1.0, 0.98]), 0, 255)
    save(to_img(rgb, a), 'seal.webp', 86)
    # champagne-gold wax for the invitation (recolour by luminance)
    lum = rgb.mean(axis=2) / 255.0
    lum = lum / np.percentile(lum[a > 0.5], 92)
    gold = np.array([196, 160, 104.])
    g2 = gold[None, None, :] * np.clip(lum, 0, 1.6)[..., None] ** 0.85
    spec = np.clip(lum - 1.1, 0, 1)[..., None] * 140
    g2 = np.clip(g2 + spec, 0, 255)
    save(to_img(g2, a), 'seal-gold.webp', 86)
    # split halves for gold seal
    S = 440
    r = np.random.default_rng(4)
    ys = np.linspace(0, S, 22); xs = S * 0.52 + np.cumsum(r.normal(0, 7, 22)) + (ys - S / 2) * 0.28
    left = Image.new('L', (S, S), 0)
    ImageDraw.Draw(left).polygon([(0, 0)] + [(float(xs[i]), float(ys[i])) for i in range(22)] + [(0, S)], fill=255)
    lm = gaussian_filter(np.asarray(left) / 255.0, 0.6)
    gimg = Image.new('L', (S, S), 0); ImageDraw.Draw(gimg).line([(float(xs[i]), float(ys[i])) for i in range(22)], fill=255, width=4)
    gm = gaussian_filter(np.asarray(gimg) / 255.0, 0.8)
    save(to_img(g2, a * lm * (1 - gm)), 'seal-gold-l.webp', 86)
    save(to_img(g2, a * (1 - lm) * (1 - gm)), 'seal-gold-r.webp', 86)


# ------------------------------------------------------------ airmail envelope (light, open)
def airmail():
    W, H = 1000, 680
    STR = 24
    cream = np.array(paper(W, H, (246, 240, 228), seed=31, age=0.2, fib=0.7)).astype(float)[..., :3]
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    rim = np.minimum.reduce([gx, gy, W - 1 - gx, H - 1 - gy])

    def band(h, w):
        yy, xx = np.mgrid[0:h, 0:w]
        k = ((xx + yy) // 30) % 4
        c = np.zeros((h, w, 3)) + np.array([246, 240, 228.])
        c[k == 0] = [176, 82, 74]; c[k == 2] = [104, 128, 166]
        return c

    def border(img, m):
        b = band(*m.shape)
        return img * (1 - m[..., None] * 0.85) + b * m[..., None] * 0.85
    # liner: dusty blue tissue with fine pattern
    lin = np.array(paper(W, H, (196, 208, 222), seed=21, age=0.1, fib=0.3)).astype(float)[..., :3]
    cell = 46
    u = (gx % cell) - cell / 2; v = ((gy + (gx // cell % 2) * cell / 2) % cell) - cell / 2
    dd = np.hypot(u, v); th = np.arctan2(v, u)
    pet = gaussian_filter((dd < 7 * (0.35 + 0.65 * np.abs(np.cos(2.5 * th)) ** 0.6)).astype(float), 0.7)
    lin = lin * (1 - pet[..., None] * 0.35) + np.array([246, 242, 234.]) * pet[..., None] * 0.35
    interior = lin * (0.62 + 0.38 * np.clip(1 - gy / (H * 0.8), 0, 1))[..., None]
    L = poly_mask(W, H, [(0, 0), (W * 0.54, H * 0.56), (0, H)])
    R = poly_mask(W, H, [(W, 0), (W * 0.46, H * 0.56), (W, H)])
    B = poly_mask(W, H, [(0, H), (W * 0.06, H * 0.40), (W * 0.5, H * 0.36), (W * 0.94, H * 0.40), (W, H)])
    pocket_a = np.clip(L + R + B, 0, 1)
    pocket = cream * (1 - 0.03 * L[..., None])
    bsh = np.clip(gaussian_filter(B, 8) - B, 0, 1)
    pocket *= (1 - bsh[..., None] * 0.22)
    pocket = border(pocket, (rim < STR).astype(float))
    body = interior * (1 - pocket_a[..., None]) + pocket * pocket_a[..., None]
    # opened flap above (inner side visible = liner)
    FH = int(H * 0.60)
    fm = poly_mask(W, FH, [(0, FH), (W, FH), (W * 0.56, 18), (W * 0.5, 0), (W * 0.44, 18)])
    fy, fx = np.mgrid[0:FH, 0:W].astype(float)
    flin = np.array(paper(W, FH, (196, 208, 222), seed=23, age=0.1, fib=0.3)).astype(float)[..., :3]
    fdist = distance_transform_edt(fm > 0.5)
    flin = np.where((fdist < 9)[..., None], np.array([244, 238, 226.]), flin)
    full = np.zeros((H + FH, W, 3)); fa = np.zeros((H + FH, W))
    full[:FH] = flin; fa[:FH] = fm
    full[FH:] = body; fa[FH:] = 1
    img = to_img(full, fa)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, FH + H - 160, 300, FH + H - 92), radius=3, outline=(104, 128, 166, 230), width=3)
    d.text((185, FH + H - 126), 'PAR AVION', font=F('bodoni', 30), fill=(104, 128, 166, 235), anchor='mm')
    save(img, 'airmail-open.webp', 80)
    # closed version (for the box) with seal
    fo = np.array(paper(W, FH, (247, 242, 231), seed=33, age=0.2, fib=0.7)).astype(float)[..., :3]
    fm2 = poly_mask(W, FH, [(0, 0), (W, 0), (W * 0.56, FH - 18), (W * 0.5, FH), (W * 0.44, FH - 18)])
    fd2 = distance_transform_edt(fm2 > 0.5)
    fo = border(fo, ((fd2 < STR) & (fm2 > 0.5)).astype(float))
    closed = pocket.copy()
    sh = np.zeros((H, W)); sh[:FH] = gaussian_filter(fm2, 7)
    closed *= (1 - np.clip(np.roll(sh, 6, 0) - np.pad(fm2, ((0, H - FH), (0, 0))), 0, 1)[..., None] * 0.25)
    closed[:FH] = closed[:FH] * (1 - fm2[..., None]) + fo * fm2[..., None]
    closed = border(closed, (rim < STR).astype(float) * (1 - np.pad(fm2, ((0, H - FH), (0, 0)))) + 0)
    cimg = to_img(closed)
    s_rgb = Image.open(OUT + '/seal.webp').convert('RGBA').resize((210, 210), Image.LANCZOS)
    cimg = cimg.convert('RGBA'); cimg.alpha_composite(s_rgb, (W // 2 - 105, FH - 120))
    save(cimg, 'airmail-closed.webp', 80)


# ------------------------------------------------------------ map: Canada · Germany · India
def miller(lon, lat):
    lon = np.asarray(lon, float); lat = np.asarray(lat, float)
    x = np.radians(lon)
    y = -1.25 * np.log(np.tan(math.pi / 4 + 0.4 * np.radians(lat)))
    return x, y, np.ones_like(x)


laea = miller


def map_frag():
    geo = json.load(open(os.path.dirname(os.path.abspath(__file__)) + '/geo.json'))
    # frame
    sx, sy, _ = laea(np.array([-128, 99]), np.array([71, 4]))
    x0, x1 = sx.min(), sx.max()
    y0, y1 = sy.min(), sy.max()
    W = 1400; H = int(W * (y1 - y0) / (x1 - x0))
    SS = 2
    def P(lon, lat):
        x, y, cc = laea(np.array(lon), np.array(lat))
        return (x - x0) / (x1 - x0) * W * SS, (y - y0) / (y1 - y0) * H * SS, cc
    def polys(geom):
        if geom['type'] == 'Polygon':
            return [geom['coordinates']]
        return geom['coordinates']
    def draw_mask(geoms):
        m = Image.new('L', (W * SS, H * SS), 0); d = ImageDraw.Draw(m)
        for geom in geoms:
            for poly in polys(geom):
                for ri, ring in enumerate(poly):
                    a = np.array(ring, float)
                    if a[:, 1].min() < -80:
                        continue
                    if np.abs(np.diff(a[:, 0])).max() > 180:
                        if (a[:, 0] > 0).mean() > 0.5:
                            a[:, 0] = np.where(a[:, 0] < -150, a[:, 0] + 360, a[:, 0])
                        else:
                            a[:, 0] = np.where(a[:, 0] > 150, a[:, 0] - 360, a[:, 0])
                    px, py, cc = P(a[:, 0], a[:, 1])
                    if (cc < -0.1).any():
                        continue
                    d.polygon(list(zip(px.tolist(), py.tolist())), fill=0 if ri else 255)
        return np.asarray(m.resize((W, H), Image.LANCZOS)) / 255.0
    land = draw_mask([f['geometry'] for f in geo['land']['features']])
    cmask = {f['properties']['name']: draw_mask([f['geometry']]) for f in geo['countries']}
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    pap = np.array(paper(W, H, (242, 235, 220), seed=88, age=0.35, fib=0.6, deckle=12)).astype(float)
    rgb = pap[..., :3]; alpha = pap[..., 3] / 255.0
    sea_d = distance_transform_edt(land < 0.5)
    ink = np.array([92, 74, 56.])
    # coastal ripple lines
    rip = np.zeros((H, W))
    for k, dd in enumerate((7, 14, 22, 32)):
        rip += np.exp(-((sea_d - dd) / 0.9) ** 2) * (0.45 - k * 0.09)
    rgb = rgb * (1 - rip[..., None] * 0.35) + ink * rip[..., None] * 0.35
    # sea tint very light blue
    sea = (land < 0.5).astype(float)
    rgb = rgb * (1 - sea[..., None] * 0.06) + np.array([170, 190, 205.]) * sea[..., None] * 0.06
    # land: warm cream with stipple
    stip = (np.random.default_rng(3).random((H, W)) > 0.965).astype(float)
    stip = gaussian_filter(stip, 0.5) * land
    rgb = rgb * (1 - land[..., None] * 0.05) + np.array([236, 224, 198.]) * land[..., None] * 0.05 - stip[..., None] * 46
    # washes
    # Soft circular watercolour washes centred on each country. No national border shapes are drawn,
    # so no boundary (including India's northern boundary) is depicted on this symbolic map.
    rng_w = np.random.default_rng(17)
    for (lon, lat), col, rad in (((-100, 57), (150, 168, 134), 150), ((10.4, 51.2), (110, 138, 178), 62), ((79.5, 21.5), (214, 150, 140), 120)):
        px, py, _ = P(lon, lat); cx, cy = float(px) / SS, float(py) / SS
        noise = gaussian_filter(rng_w.random((H, W)), 14); noise = (noise - noise.mean()) / (noise.std() + 1e-6)
        dist = np.hypot(gx - cx, gy - cy) / rad + noise * 0.12
        m = np.clip(1 - dist, 0, 1) ** 1.1 * 0.78
        rgb = rgb * (1 - m[..., None]) + np.array(col, float) * m[..., None]
    # graticule
    gm = Image.new('L', (W * SS, H * SS), 0); d = ImageDraw.Draw(gm)
    for lon in range(-180, 181, 20):
        lat = np.linspace(-10, 85, 200); px, py, cc = P(np.full_like(lat, lon), lat)
        d.line(list(zip(px.tolist(), py.tolist())), fill=255, width=2)
    for lat0 in range(0, 90, 20):
        lon = np.linspace(-180, 180, 600); px, py, cc = P(lon, np.full_like(lon, lat0))
        ok = cc > -0.1
        d.line(list(zip(px[ok].tolist(), py[ok].tolist())), fill=255, width=2)
    gmm = np.asarray(gm.resize((W, H), Image.LANCZOS)) / 255.0 * 0.22
    rgb = rgb * (1 - gmm[..., None]) + ink * gmm[..., None]
    # coastline
    coast = np.clip(np.abs(np.gradient(gaussian_filter(land, 0.7), axis=0)) + np.abs(np.gradient(gaussian_filter(land, 0.7), axis=1)), 0, 1)
    coast = np.clip(coast * 3.2, 0, 1)
    rgb = rgb * (1 - coast[..., None] * 0.85) + ink * coast[..., None] * 0.85
    img = to_img(rgb, alpha)
    d = ImageDraw.Draw(img)
    pts = {}
    for name, (lon, lat) in {'CANADA': (-104, 58), 'GERMANY': (10.4, 51.2), 'INDIA': (81.6, 16.9)}.items():
        px, py, _ = P(lon, lat); pts[name] = (float(px) / SS, float(py) / SS)
    lab = {'CANADA': (60, 30), 'GERMANY': (42, 4), 'INDIA': (-130, 4)}
    f = F('bodoni', 30)
    for name, (x, y) in pts.items():
        dx, dy = lab[name]
        s = ' '.join(name)
        d.text((x + dx, y + dy), s, font=f, fill=(88, 70, 52, 235), anchor='lm' if name == 'GERMANY' else 'mm')
    # compass rose (small, lower left ocean)
    cx, cy, R = 560, H - 110, 54
    for i in range(8):
        a = i * math.pi / 4 - math.pi / 2
        L = R if i % 2 == 0 else R * 0.55
        tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
        l1 = (cx + math.cos(a + 1.57) * 8, cy + math.sin(a + 1.57) * 8)
        l2 = (cx + math.cos(a - 1.57) * 8, cy + math.sin(a - 1.57) * 8)
        d.polygon([tip, l1, (cx, cy)], fill=(120, 100, 78, 200)); d.polygon([tip, l2, (cx, cy)], fill=(196, 176, 140, 200))
    d.ellipse((cx - R * 0.72, cy - R * 0.72, cx + R * 0.72, cy + R * 0.72), outline=(120, 100, 78, 160), width=2)
    d.text((cx, cy - R - 18), 'N', font=F('bodoni', 26), fill=(100, 82, 62, 220), anchor='mm')
    save(img, 'map.webp', 80)
    json.dump({'W': W, 'H': H, 'pts': pts}, open(os.path.dirname(os.path.abspath(__file__)) + '/map-points.json', 'w'))
    print(W, H, pts)


# ------------------------------------------------------------ pressed botanicals
def pressed_maple(S=520, seed=1):
    gy, gx = np.mgrid[0:S, 0:S].astype(float)
    cx, cy = S / 2, S * 0.56
    x = gx - cx; y = gy - cy
    phi = np.degrees(np.arctan2(x, -y))  # 0 = up
    rr = np.hypot(x, y)
    R = S * 0.42
    lobes = [(0, 1.0, 13), (-50, 0.92, 12), (50, 0.92, 12), (-102, 0.55, 11), (102, 0.55, 11)]
    prof = 0.22 + sum(a * np.exp(-np.abs(phi - p) / w) for p, a, w in lobes)
    teeth = 0.035 * np.abs(np.sin(np.radians(phi) * 22)) ** 1.5
    prof = prof + teeth
    m = (rr < R * prof) & (np.abs(phi) < 160)
    m = gaussian_filter(m.astype(float), 0.8)
    # stem
    st = Image.new('L', (S, S), 0); ImageDraw.Draw(st).line([(cx, cy), (cx + 10, S * 0.98)], fill=255, width=7)
    stm = gaussian_filter(np.asarray(st) / 255.0, 0.8)
    n = fnoise(S, S, base=50, octaves=4, seed=seed)
    t = np.clip(rr / R, 0, 1)
    col = np.array([196, 92, 52.]) * (1 - t[..., None] * 0.25) + np.array([214, 150, 70.]) * (n[..., None] - 0.4) * 0.6
    col = col * (0.92 + 0.12 * n[..., None])
    # veins
    vm = Image.new('L', (S, S), 0); d = ImageDraw.Draw(vm)
    for p, a, w in lobes:
        ang = math.radians(p); L = R * a
        d.line([(cx, cy), (cx + math.sin(ang) * L * 0.95, cy - math.cos(ang) * L * 0.95)], fill=255, width=3)
        for s in np.linspace(0.25, 0.8, 4):
            bx, by = cx + math.sin(ang) * L * s, cy - math.cos(ang) * L * s
            for sg in (-1, 1):
                a2 = ang + sg * 0.7
                d.line([(bx, by), (bx + math.sin(a2) * L * 0.18, by - math.cos(a2) * L * 0.18)], fill=180, width=1)
    vmm = gaussian_filter(np.asarray(vm) / 255.0, 0.7)
    col = col * (1 + vmm[..., None] * 0.22)
    edge = np.clip(1 - distance_transform_edt(m > 0.5) / 10, 0, 1)
    col *= (1 - edge[..., None] * 0.18)
    a = np.clip(m * 0.94 + stm * 0.95, 0, 1)
    col = np.where(stm[..., None] > m[..., None], np.array([150, 84, 50.]), col)
    return to_img(col, a)


def pressed_cornflower(S=420, seed=2):
    can = np.zeros((S, S, 3)); al = np.zeros((S, S))
    r = np.random.default_rng(seed)
    cx = cy = S / 2
    # stem
    st = Image.new('L', (S, S), 0); ImageDraw.Draw(st).line([(cx, cy), (cx - 40, S)], fill=255, width=5)
    stm = gaussian_filter(np.asarray(st) / 255.0, 0.8)
    put(can, al, np.full((S, S, 3), [112, 128, 88.]), stm * 0.9, 0, 0)
    for k in range(11):
        ang = k / 11 * 2 * math.pi + r.normal(0, 0.08)
        L = S * r.uniform(0.34, 0.42); w0 = 10; w1 = 34
        ux, uy = math.cos(ang), math.sin(ang); px, py = -uy, ux
        base = (cx + ux * 20, cy + uy * 20)
        tipc = (cx + ux * L, cy + uy * L)
        pts = [(base[0] + px * w0, base[1] + py * w0)]
        # toothed end
        for t in range(6):
            s = -1 + t * 0.4
            depth = L * (1.0 if t % 2 == 0 else 0.9)
            pts.append((cx + ux * depth + px * w1 * s, cy + uy * depth + py * w1 * s))
        pts.append((base[0] - px * w0, base[1] - py * w0))
        pts = pts[:1] + pts[1:-1][::-1] + pts[-1:]
        m = poly_mask(S, S, pts)
        gy, gx = np.mgrid[0:S, 0:S].astype(float)
        dl = ((gx - cx) * ux + (gy - cy) * uy) / L
        col = np.array([92, 112, 172.]) * (0.82 + 0.28 * dl)[..., None] + np.array([30, 24, 10.]) * (dl ** 3)[..., None]
        col = col * (0.9 + 0.15 * fnoise(S, S, base=20, octaves=2, seed=seed + k)[..., None])
        put(can, al, col, gaussian_filter(m, 1.2) * 0.86, 0, 0)
    gy, gx = np.mgrid[0:S, 0:S].astype(float)
    c = gaussian_filter((np.hypot(gx - cx, gy - cy) < 30).astype(float), 1.2)
    put(can, al, np.full((S, S, 3), [70, 52, 104.]) * (0.8 + 0.4 * fnoise(S, S, base=4, octaves=2, seed=9))[..., None], c, 0, 0)
    return to_img(can, al)


def pressed_lotus(W=300, H=520, seed=3):
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    s = gy / H  # 0 tip .. 1 base
    hw = W * 0.46 * np.sin(np.clip(s, 0, 1) * math.pi) ** 0.6 * (0.55 + 0.45 * s)
    hw = np.where(s > 0.85, hw * (1 - (s - 0.85) / 0.15 * 0.7), hw)
    m = gaussian_filter((np.abs(gx - W / 2) < hw).astype(float) * (s > 0.03), 0.9)
    tcol = np.array([214, 120, 142.]); bcol = np.array([246, 230, 222.])
    k = np.clip((s - 0.1) / 0.8, 0, 1) ** 1.3
    col = tcol * (1 - k[..., None]) + bcol * k[..., None]
    vx = (gx - W / 2) / (hw + 1e-6)
    veins = (np.cos(vx * 9 * math.pi / 2) ** 40) * (s > 0.1)
    col *= (1 - veins[..., None] * 0.08)
    col *= (0.94 + 0.08 * fnoise(H, W, base=30, octaves=3, seed=seed))[..., None]
    edge = np.clip(1 - distance_transform_edt(m > 0.5) / 8, 0, 1)
    col *= (1 - edge[..., None] * 0.08)
    return to_img(col, m * 0.9)


# ------------------------------------------------------------ stamps (original designs)
def maple_mask(S):
    im = np.asarray(pressed_maple(S, 5))[..., 3] / 255.0
    return im


def stamp2(kind, w=300, h=360, seed=1):
    pap = np.array(paper(w, h, (248, 244, 234), seed=seed + 40, age=0.2, fib=0.4)).astype(float)[..., :3]
    m = 22; aw, ah = w - 2 * m, h - 2 * m - 44
    yy, xx = np.mgrid[0:ah, 0:aw].astype(float)
    if kind == 'canada':
        art = np.array([236, 226, 210.]) + 0 * yy[..., None]
        mm = np.asarray(pressed_maple(int(ah * 0.95), 6))[..., 3] / 255.0
        S = mm.shape[0]; ox, oy = (aw - S) // 2, (ah - S) // 2 + 4
        lm = np.zeros((ah, aw)); lm[max(0, oy):oy + S, max(0, ox):ox + S] = mm[max(0, -oy):ah - oy, max(0, -ox):aw - ox][:lm[max(0, oy):oy + S, max(0, ox):ox + S].shape[0], :lm[max(0, oy):oy + S, max(0, ox):ox + S].shape[1]]
        art = art * (1 - lm[..., None]) + np.array([170, 66, 58.]) * lm[..., None]
        label, val, tint = 'CANADA', '21', (170, 66, 58)
    elif kind == 'de':
        art = np.array([226, 232, 238.]) * (0.96 + 0.04 * (yy / ah))[..., None]
        cf = np.asarray(pressed_cornflower(int(ah * 0.9), 4)).astype(float)
        S = cf.shape[0]; ox, oy = (aw - S) // 2, (ah - S) // 2
        sub = cf[:min(S, ah - oy), :min(S, aw - ox)]
        a = sub[..., 3:] / 255.0
        art[oy:oy + sub.shape[0], ox:ox + sub.shape[1]] = art[oy:oy + sub.shape[0], ox:ox + sub.shape[1]] * (1 - a) + sub[..., :3] * a
        label, val, tint = 'DEUTSCHLAND', '11', (84, 106, 150)
    else:
        art = np.array([244, 230, 222.]) * (0.97 + 0.03 * (yy / ah))[..., None]
        img = to_img(art).convert('RGBA')
        pet = pressed_lotus(150, 260, 7)
        cx, cy = aw / 2, ah * 0.70
        for ang, sc in [(-62, .62), (62, .62), (-38, .8), (38, .8), (-16, .92), (16, .92), (0, 1.0)]:
            p = pet.resize((int(64 * sc), int(112 * sc)), Image.LANCZOS)
            pad = Image.new('RGBA', (240, 240), (0, 0, 0, 0)); pad.alpha_composite(p, (120 - p.width // 2, 120 - p.height))
            pr = pad.rotate(-ang, resample=Image.BICUBIC, center=(120, 120))
            img.alpha_composite(pr, (int(cx - 120), int(cy - 120)))
        d = ImageDraw.Draw(img)
        d.line([(cx - aw * 0.36, cy + 6), (cx + aw * 0.36, cy + 6)], fill=(132, 150, 118), width=3)
        img = img.convert('RGB')
        art = np.asarray(img).astype(float)
        label, val, tint = 'INDIA', '26', (186, 98, 116)
    art = g.engrave(art, 3.2, 0.08, 0.5)
    pap[m:m + ah, m:m + aw] = art
    img = to_img(pap); d = ImageDraw.Draw(img)
    d.rectangle((m - 1, m - 1, m + aw, m + ah), outline=tint, width=2)
    d.text((m + 12, m + 8), val, font=F('bodonis', 40), fill=tint)
    d.text((w / 2, h - m - 20), label, font=F('bodoni', 24 if len(label) < 8 else 20), fill=(70, 60, 50), anchor='mm')
    alpha = g.perforated(w, h)
    return Image.fromarray(np.dstack([np.asarray(img), (alpha * 255).astype(np.uint8)]), 'RGBA')


# ------------------------------------------------------------ luggage tag
def tag(W=300, H=620):
    pap = np.array(paper(W, H, (247, 242, 231), seed=61, age=0.25, fib=0.6)).astype(float)
    rgb = pap[..., :3]
    m = poly_mask(W, H, [(48, 0), (W - 48, 0), (W, 60), (W, H), (0, H), (0, 60)])
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    hole = np.hypot(gx - W / 2, gy - 70)
    eyelet = (hole < 34) & (hole > 20)
    ey = np.clip(1 - np.abs(hole - 27) / 7, 0, 1)
    rgb = np.where(eyelet[..., None], foil(eyelet.astype(float), 5, (186, 156, 104)) * (0.8 + 0.4 * ey[..., None]), rgb)
    m = m * (hole > 20)
    img = to_img(rgb, m)
    d = ImageDraw.Draw(img)
    d.line([(36, 150), (W - 36, 150)], fill=(176, 82, 74), width=3)
    d.text((W / 2, 196), 'DESTINATION', font=F('bodoni', 24), fill=(110, 92, 72), anchor='mm')
    d.text((W / 2, 280), 'Nallajerla', font=F('bodonii', 58), fill=(52, 64, 98), anchor='mm')
    d.line([(60, 330), (W - 60, 330)], fill=(184, 160, 116), width=1)
    d.text((W / 2, 372), 'ANDHRA PRADESH', font=F('bodoni', 20), fill=(110, 92, 72), anchor='mm')
    d.text((W / 2, 404), 'INDIA', font=F('bodoni', 20), fill=(110, 92, 72), anchor='mm')
    d.text((W / 2, 520), '21 · XI · 2026', font=F('bodoni', 26), fill=(176, 82, 74), anchor='mm')
    # string
    out = Image.new('RGBA', (W, H + 140), (0, 0, 0, 0))
    sd = ImageDraw.Draw(out)
    for k, off in enumerate((-3, 0, 3)):
        sd.line([(W / 2 + off, 0), (W / 2 + off * 0.5 + 6, 140 + 70)], fill=(206, 186, 146, 255 - k * 30), width=3)
    out.alpha_composite(img, (0, 140))
    sd = ImageDraw.Draw(out)
    sd.line([(W / 2 + 4, 140 + 70), (W / 2 + 30, 140 + 40)], fill=(206, 186, 146, 255), width=4)
    return out


# ------------------------------------------------------------ photo print + vellum
def photo_print():
    src = Image.open('/home/claude/shared5/couple-crop-full.png').convert('RGB')
    PW = 860; ph = int(src.height * PW / src.width)
    photo = np.asarray(src.resize((PW, ph), Image.LANCZOS)).astype(float)
    B = 34
    W, H = PW + 2 * B, ph + 2 * B + 30
    card = np.array(paper(W, H, (250, 248, 243), seed=77, age=0.1, fib=0.3)).astype(float)[..., :3]
    card[B:B + ph, B:B + PW] = photo
    card[B - 1:B, B:B + PW] *= 0.88
    save(to_img(card), 'photo-print.webp', 86)


def vellum(W=1000, H=420):
    n = fnoise(H, W, base=50, octaves=4, seed=12)
    fib = g.fibres(H, W, int(W * H / 700), 13) / 255.0
    col = np.array([250, 249, 246.]) * (0.97 + 0.03 * n + fib * 0.4)[..., None]
    a = 0.62 + 0.10 * (n - 0.5) + fib * 0.6
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    a = np.where(gy < 5, 0.85, a)  # top edge catches light
    col = np.where((gy < 5)[..., None], np.array([255, 255, 255.]), col)
    a *= np.clip(np.minimum(gx, W - 1 - gx) / 2, 0, 1)
    save(to_img(col, np.clip(a, 0, 1)), 'vellum.webp', 82)


# ------------------------------------------------------------ invitation envelope (ivory + foil liner)
def jaali(w, h, cell=64):
    gy, gx = np.mgrid[0:h, 0:w].astype(float)
    u = (gx % cell) / cell * 2 * math.pi; v = (gy % cell) / cell * 2 * math.pi
    ogee = np.abs(np.sin(u / 2) - 0.5 * (1 + np.cos(v))) < 0.07
    ogee2 = np.abs(np.sin(u / 2 + math.pi / 2) ** 2 - 0.5 * (1 - np.cos(v))) < 0.05
    cx = (gx % cell) - cell / 2; cy = (gy % cell) - cell / 2
    d = np.hypot(cx, cy); th = np.arctan2(cy, cx)
    flower = d < 6 * (0.5 + 0.5 * np.abs(np.cos(2 * th)))
    m = (ogee | ogee2 | flower).astype(float)
    return gaussian_filter(m, 0.7)


def invite_envelope():
    W, H = 1000, 700
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    ivory = np.array(paper(W, H, IVORY, seed=131, age=0.15, fib=0.8)).astype(float)[..., :3]
    linbase = np.array([244, 236, 226.])
    jm = jaali(W, H)
    liner = linbase * (0.98 + 0.03 * fnoise(H, W, base=80, octaves=2, seed=3))[..., None]
    fc = foil(jm, 7)
    liner = liner * (1 - jm[..., None]) + fc * jm[..., None]
    interior = liner * (0.80 + 0.20 * np.clip(1 - gy / (H * 0.85), 0, 1))[..., None]
    rim = np.minimum.reduce([gx, gy, W - 1 - gx, H - 1 - gy])
    interior = np.where((rim < 14)[..., None], ivory * 0.92, interior)
    save(to_img(interior), 'inv-interior.webp', 78)
    L = poly_mask(W, H, [(0, 0), (W * 0.55, H * 0.55), (0, H)])
    R = poly_mask(W, H, [(W, 0), (W * 0.45, H * 0.55), (W, H)])
    B = poly_mask(W, H, [(0, H), (W * 0.04, H * 0.42), (W * 0.5, H * 0.34), (W * 0.96, H * 0.42), (W, H)])
    al = np.clip(L + R + B, 0, 1)
    pocket = ivory * (1 - 0.03 * L[..., None]) * (1 - 0.015 * R[..., None])
    bsh = np.clip(gaussian_filter(B, 9) - B, 0, 1)
    pocket *= (1 - bsh[..., None] * 0.20)
    for M in (L, R):
        sh = np.clip(gaussian_filter(M, 7) - M, 0, 1)
        pocket *= (1 - sh[..., None] * 0.16 * (1 - B[..., None]))
    save(to_img(pocket, al), 'inv-pocket.webp', 80)
    FH = int(H * 0.62)
    n = fnoise(FH, W, base=8, octaves=2, seed=5)
    fm = poly_mask(W, FH, [(0, 0), (W, 0), (W * 0.5, FH)])
    fd = distance_transform_edt(fm > 0.5)
    deck = np.clip((fd - (2 + 7 * n)) / 1.4, 0, 1) * (fm > 0.01)
    top = np.zeros_like(fd); top[:3] = 1
    fa = np.clip(deck + top * fm, 0, 1)
    fo = np.array(paper(W, FH, (248, 244, 235), seed=133, age=0.1, fib=0.8)).astype(float)[..., :3]
    fo *= (1 + 0.03 * (1 - np.mgrid[0:FH, 0:W][0] / FH))[..., None]
    save(to_img(fo, fa), 'inv-flap.webp', 82)
    fl = liner[:FH].copy()
    fl = np.where((fd < 14)[..., None], np.array([246, 241, 232.]), fl)
    save(to_img(fl, fa), 'inv-flap-in.webp', 80)


# ------------------------------------------------------------ stationery papers
def frame_mask(w, h, inset=48, corners=True, gold=True):
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    d.rectangle((inset, inset, w - inset, h - inset), outline=255, width=2)
    d.rectangle((inset + 10, inset + 10, w - inset - 10, h - inset - 10), outline=255, width=1)
    if corners:
        for (cx, cy, sx, sy) in ((inset, inset, 1, 1), (w - inset, inset, -1, 1), (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)):
            for k in range(3):
                a0 = k * 0.5
                pts = [(cx + sx * (10 + 34 * math.cos(t) * (1 - k * 0.2)), cy + sy * (10 + 34 * math.sin(t) * (1 - k * 0.2))) for t in np.linspace(0.05, 1.52, 20)]
            d.ellipse((cx + sx * 4 - 5, cy + sy * 4 - 5, cx + sx * 4 + 5, cy + sy * 4 + 5), fill=255)
            d.arc((cx - 30, cy - 30, cx + 30, cy + 30), 0, 360, fill=255, width=1)
    return np.asarray(m) / 255.0


def lotus_ornament(w, h, cx, cy, s=1.0):
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    for ang in (-56, -28, 0, 28, 56):
        a = math.radians(ang); L = 46 * s * (1 if ang == 0 else 0.82 if abs(ang) < 40 else 0.62)
        tip = (cx + math.sin(a) * L, cy - math.cos(a) * L)
        lft = (cx + math.sin(a - 0.42) * L * 0.42, cy - math.cos(a - 0.42) * L * 0.42)
        rgt = (cx + math.sin(a + 0.42) * L * 0.42, cy - math.cos(a + 0.42) * L * 0.42)
        d.line([(cx, cy), lft, tip, rgt, (cx, cy)], fill=255, width=2)
    d.line([(cx - 120 * s, cy + 6), (cx - 30 * s, cy + 6)], fill=255, width=1)
    d.line([(cx + 30 * s, cy + 6), (cx + 120 * s, cy + 6)], fill=255, width=1)
    d.ellipse((cx - 4, cy + 2, cx + 4, cy + 10), fill=255)
    return np.asarray(m) / 255.0


def papers():
    CW, CH = 900, 1300
    # letter: deckled cotton with debossed monogram
    mono = text_mask(CW, CH, [((CW / 2, 120), 'A & P', 'saint', 90, 'mm')])
    save(paper(CW, CH, (249, 246, 238), seed=201, age=0.12, fib=0.9, deckle=12, emboss=mono * 1.0), 'paper-cotton.webp', 76)
    # route sheet: smooth fine paper, hairline foil frame
    RW, RH = 900, 1300
    p = np.array(paper(RW, RH, (250, 247, 240), seed=202, age=0.1, fib=0.5, deckle=8)).astype(float)
    fm = frame_mask(RW, RH, 34, corners=False)
    fc = foil(fm, 2)
    p[..., :3] = p[..., :3] * (1 - fm[..., None]) + fc * fm[..., None]
    save(to_img(p[..., :3], p[..., 3] / 255), 'paper-route.webp', 76)
    # invitation card: heavy cotton, letterpress border, foil lotus + frame
    IW, IH = 900, 1300
    fr = frame_mask(IW, IH, 46)
    lot = lotus_ornament(IW, IH, IW / 2, 150, 1.0)
    fmk = np.clip(fr + lot, 0, 1)
    deb = np.zeros((IH, IW)); dd = Image.new('L', (IW, IH), 0); ImageDraw.Draw(dd).rectangle((70, 70, IW - 70, IH - 70), outline=255, width=6)
    deb = np.asarray(dd) / 255.0
    p = np.array(paper(IW, IH, (250, 247, 239), seed=203, age=0.1, fib=0.9, deckle=13, emboss=deb * 1.2)).astype(float)
    fc = foil(fmk, 9)
    p[..., :3] = p[..., :3] * (1 - fmk[..., None]) + fc * fmk[..., None]
    save(to_img(p[..., :3], p[..., 3] / 255), 'paper-invite.webp', 78)
    # stub used inside the envelope animation (same card, smaller)
    Image.open(OUT + '/paper-invite.webp').resize((450, 650), Image.LANCZOS).save(OUT + '/paper-invite-stub.webp', 'WEBP', quality=74)
    # enclosure (details): blush-tinted cotton
    p = np.array(paper(900, 1400, (248, 240, 234), seed=204, age=0.1, fib=0.7, deckle=10)).astype(float)
    lot = lotus_ornament(900, 1400, 450, 96, 0.7)
    fc = foil(lot, 4)
    p[..., :3] = p[..., :3] * (1 - lot[..., None]) + fc * lot[..., None]
    save(to_img(p[..., :3], p[..., 3] / 255), 'paper-enclosure.webp', 76)
    # blessing: ivory with foil frame
    p = np.array(paper(900, 1300, (250, 246, 236), seed=205, age=0.1, fib=0.7, deckle=12)).astype(float)
    fr = frame_mask(900, 1300, 40, corners=False)
    fc = foil(fr, 6)
    p[..., :3] = p[..., :3] * (1 - fr[..., None]) + fc * fr[..., None]
    save(to_img(p[..., :3], p[..., 3] / 255), 'paper-blessing.webp', 76)


def botanicals():
    save(pressed_maple(), 'pressed-maple.webp', 82)
    save(pressed_cornflower(), 'pressed-cornflower.webp', 82)
    save(pressed_lotus(), 'pressed-lotus.webp', 82)
    for i, k in enumerate(['canada', 'de', 'india']):
        save(stamp2(k, seed=20 + i), f'stamp-{k}.webp', 84)
    save(tag(), 'tag.webp', 84)


def main():
    only = os.environ.get('ONLY')
    fns = only.split(',') if only else ['linen_bg', 'ribbons', 'box', 'seals', 'airmail', 'map_frag', 'botanicals', 'photo_print', 'vellum', 'invite_envelope', 'papers']
    for fn in fns:
        globals()[fn]()


if __name__ == '__main__':
    main()
