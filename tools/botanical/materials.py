"""Procedural materials for The Royal Botanical Letter.
Outputs into /home/claude/site5/botanical/img/
  paper-cotton.webp   seamless cotton-rag paper tile (fibres, mottling, grain)
  paper-blush.webp    seamless blush liner paper tile
  paper-forest.webp   seamless forest-green envelope paper tile
  linen-table.webp    seamless forest linen tablecloth tile
  deckle-card.webp    alpha mask, 5:7, deckled on all edges
  deckle-flap-l.webp  alpha mask, 5:14, deckled top/bottom/left (outer edge)
  deckle-flap-r.webp  mirror
  deckle-wide.webp    alpha mask, 7:5
  seal.webp           burgundy wax seal with A&P cipher, lit
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi
import os

OUT = '/home/claude/site5/botanical/img'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(21112026)


def periodic_noise(n, sigma, seed=None):
    r = np.random.default_rng(seed)
    w = r.standard_normal((n, n))
    out = ndi.gaussian_filter(w, sigma, mode='wrap')
    out -= out.min(); out /= out.max()
    return out


def fbm(n, sigmas, weights, seed=0):
    acc = np.zeros((n, n))
    for i, (s, wt) in enumerate(zip(sigmas, weights)):
        acc += wt * periodic_noise(n, s, seed + i)
    acc -= acc.min(); acc /= acc.max()
    return acc


def fibres(n, count, seed, length=(10, 60), width=(0.4, 1.3)):
    """Draw short curved fibres, wrapped for tiling. Returns float layer (-1..1 contribution)."""
    r = np.random.default_rng(seed)
    S = 3  # supersample
    img = Image.new('L', (n * S, n * S), 128)
    d = ImageDraw.Draw(img)
    for _ in range(count):
        x, y = r.uniform(0, n), r.uniform(0, n)
        L = r.uniform(*length)
        a = r.uniform(0, np.pi * 2)
        curl = r.normal(0, 0.06)
        tone = 128 + int(r.choice([-1, 1], p=[0.35, 0.65]) * r.uniform(18, 55))
        wdt = max(1, int(r.uniform(*width) * S))
        pts = []
        for k in range(14):
            pts.append((x, y))
            a += curl + r.normal(0, 0.05)
            x += np.cos(a) * L / 14; y += np.sin(a) * L / 14
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                d.line([((px + ox) * S, (py + oy) * S) for px, py in pts], fill=tone, width=wdt)
    img = img.resize((n, n), Image.LANCZOS)
    return (np.asarray(img).astype(float) - 128) / 128


def tile_paper(n, base, dark, light, seed, fibre_count=900, inclusions=0):
    mott = fbm(n, [60, 22, 7], [0.5, 0.35, 0.15], seed)
    grain = periodic_noise(n, 0.7, seed + 9)
    fib = fibres(n, fibre_count, seed + 3)
    base = np.array(base, float); dark = np.array(dark, float); light = np.array(light, float)
    t = (mott - 0.5) * 0.9 + (grain - 0.5) * 0.35
    img = base[None, None, :] + np.where(t[..., None] > 0, (light - base) * t[..., None], (base - dark) * t[..., None])
    img += fib[..., None] * np.where(fib[..., None] > 0, (light - base) * 1.1, (base - dark) * 1.4)
    if inclusions:
        r = np.random.default_rng(seed + 50)
        inc = np.zeros((n, n))
        for _ in range(inclusions):
            x, y = r.integers(0, n, 2)
            rr = r.uniform(0.6, 1.6)
            yy, xx = np.ogrid[-4:5, -4:5]
            blob = np.exp(-(xx ** 2 + yy ** 2) / (2 * rr ** 2))
            for dy in range(9):
                for dx in range(9):
                    inc[(y + dy - 4) % n, (x + dx - 4) % n] += blob[dy, dx]
        img -= inc[..., None] * (base - dark) * 1.6
    return np.clip(img, 0, 255).astype(np.uint8)


def linen(n, seed):
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    r = np.random.default_rng(seed)
    threads = 96  # threads across the tile (must be integer for seamless)
    jitter_x = ndi.gaussian_filter1d(r.standard_normal(n), 3, mode='wrap') * 0.8
    jitter_y = ndi.gaussian_filter1d(r.standard_normal(n), 3, mode='wrap') * 0.8
    warp = np.sin((xx + jitter_y[yy.astype(int)] * 2) / n * threads * 2 * np.pi)
    weft = np.sin((yy + jitter_x[xx.astype(int)] * 2) / n * threads * 2 * np.pi)
    # slubs: thickness variation along threads
    slub_w = ndi.gaussian_filter1d(r.standard_normal(n), 1.2, mode='wrap')
    slub_h = ndi.gaussian_filter1d(r.standard_normal(n), 1.2, mode='wrap')
    checker = (np.sin(xx / n * threads * np.pi) * np.sin(yy / n * threads * np.pi)) > 0
    weave = np.where(checker, warp * (0.8 + 0.3 * slub_w[xx.astype(int)]), weft * (0.8 + 0.3 * slub_h[yy.astype(int)]))
    mott = fbm(n, [50, 15], [0.7, 0.3], seed + 2)
    base = np.array([24, 52, 41], float)
    v = 1 + weave * 0.16 + (mott - 0.5) * 0.24 + (periodic_noise(n, 0.6, seed + 5) - 0.5) * 0.10
    img = base[None, None, :] * v[..., None]
    img[..., 1] += (mott - 0.5) * 6
    return np.clip(img, 0, 255).astype(np.uint8)


def edge_noise(L, seed, amp, scales=(50, 14, 4, 1.5), weights=(0.45, 0.3, 0.17, 0.08)):
    r = np.random.default_rng(seed)
    acc = np.zeros(L)
    for s, w in zip(scales, weights):
        n = ndi.gaussian_filter1d(r.standard_normal(L), s)
        n /= (np.abs(n).max() + 1e-9)
        acc += w * n
    return acc * amp


def deckle_mask(w, h, edges='tblr', seed=1, depth=None):
    """Alpha mask with a torn, fibrous deckle on the given edges."""
    S = 2
    W, H = w * S, h * S
    depth = depth or int(min(w, h) * 0.02) * S
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    d = np.full((H, W), 1e9)
    r = np.random.default_rng(seed)
    if 'l' in edges:
        off = depth * 1.2 + edge_noise(H, seed + 1, depth)
        d = np.minimum(d, xx - off[:, None])
    else:
        d = np.minimum(d, xx + 10)
    if 'r' in edges:
        off = depth * 1.2 + edge_noise(H, seed + 2, depth)
        d = np.minimum(d, (W - 1 - xx) - off[:, None])
    else:
        d = np.minimum(d, (W - 1 - xx) + 10)
    if 't' in edges:
        off = depth * 1.2 + edge_noise(W, seed + 3, depth)
        d = np.minimum(d, yy - off[None, :])
    if 'b' in edges:
        off = depth * 1.2 + edge_noise(W, seed + 4, depth)
        d = np.minimum(d, (H - 1 - yy) - off[None, :])
    # fibrous fringe: thin translucent zone, and fine hair-like noise near the edge
    hair = ndi.gaussian_filter(r.standard_normal((H, W)), 1.0)
    hair = (hair - hair.min()) / (hair.max() - hair.min())
    a = np.clip((d + depth * 0.5 * (hair - 0.5)) / (depth * 0.32), 0, 1)
    # the deckle zone is thinner paper: slightly translucent
    thin = np.clip(d / (depth * 1.6), 0, 1)
    a = a * (0.82 + 0.18 * thin)
    m = Image.fromarray((a * 255).astype(np.uint8), 'L').resize((w, h), Image.LANCZOS)
    rgba = Image.merge('RGBA', [Image.new('L', (w, h), 0)] * 3 + [m])
    return rgba


def seal(size=720, seed=7):
    S = size
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    cx = cy = S / 2
    ang = np.arctan2(yy - cy, xx - cx)
    rad = np.hypot(xx - cx, yy - cy)
    # irregular wax outline: base radius + lobes
    r = np.random.default_rng(seed)
    a_samp = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    prof = np.zeros_like(a_samp)
    for k, amp in [(3, 0.022), (5, 0.018), (8, 0.012), (13, 0.008), (21, 0.006), (34, 0.004)]:
        prof += amp * np.sin(k * a_samp + r.uniform(0, 6.28))
    R0 = S * 0.43 * (1 + np.interp(ang, a_samp, prof, period=2 * np.pi))
    t = rad / R0
    # height: puddle dome with a raised rim and recessed stamp face
    h = np.where(t < 1, np.sqrt(np.clip(1 - t ** 6, 0, 1)), 0) * 0.55
    stampR = 0.70
    face = np.clip((stampR - t) / 0.03, 0, 1)
    h = h - face * 0.26 + np.exp(-((t - stampR - 0.035) / 0.03) ** 2) * 0.10 * (t < 1)
    # stamp ring and dots
    ring = np.exp(-((t - 0.62) / 0.010) ** 2) * face
    h += ring * 0.05
    # monogram (raised in seal since the stamp was engraved)
    mono = Image.new('L', (S, S), 0)
    dm = ImageDraw.Draw(mono)
    f = ImageFont.truetype('/home/claude/tools5/botanical/ttf/pinyon-script-latin-400-normal.ttf', int(S * 0.34))
    fa = ImageFont.truetype('/home/claude/tools5/botanical/ttf/playfair-display-latin-400-italic.ttf', int(S * 0.15))
    parts = [('A', f, 0), ('&', fa, -S * 0.035), ('P', f, 0)]
    widths = [dm.textbbox((0, 0), q, font=ff)[2] - dm.textbbox((0, 0), q, font=ff)[0] for q, ff, _ in parts]
    gap = S * 0.01
    x = (S - sum(widths) - gap * 2) / 2
    for (q, ff, dy), w in zip(parts, widths):
        bb = dm.textbbox((0, 0), q, font=ff)
        hh = bb[3] - bb[1]
        dm.text((x - bb[0], S / 2 - hh / 2 - bb[1] + dy), q, fill=255, font=ff)
        x += w + gap
    # sprig dots around ring (8 small leaves)
    for k in range(16):
        aa = k / 16 * 2 * np.pi
        px, py = cx + np.cos(aa) * S * 0.43 * 0.66 * 0.5 * 2 * 0.5 * 2, cy + np.sin(aa) * S * 0.43 * 0.66
        px = cx + np.cos(aa) * S * 0.43 * 0.665
        dm.ellipse([px - S * 0.006, py - S * 0.006, px + S * 0.006, py + S * 0.006], fill=200)
    mono = np.asarray(mono.filter(ImageFilter.GaussianBlur(S * 0.0035))).astype(float) / 255
    h += mono * 0.13 * face
    # surface ripple
    rip = ndi.gaussian_filter(r.standard_normal((S, S)), S * 0.01)
    h += rip / np.abs(rip).max() * 0.012 * (t < 1)
    h = ndi.gaussian_filter(h, 1.0)
    gy, gx = np.gradient(h * S * 0.35)
    nz = np.ones_like(h)
    nl = np.sqrt(gx ** 2 + gy ** 2 + nz ** 2)
    nx, ny, nz = -gx / nl, -gy / nl, nz / nl
    L = np.array([-0.5, -0.6, 0.62]); L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    H = L + np.array([0, 0, 1]); H /= np.linalg.norm(H)
    spec = np.clip(nx * H[0] + ny * H[1] + nz * H[2], 0, 1) ** 60
    base = np.array([118, 22, 34], float)
    deep = np.array([58, 8, 16], float)
    col = deep + (base - deep) * diff[..., None] ** 0.9
    col = col * (0.92 + 0.16 * (ndi.gaussian_filter(r.random((S, S)), 3)[..., None]))
    col += spec[..., None] * np.array([255, 205, 200]) * 0.75
    # subsurface warmth near thin rim
    col += np.clip(1 - t, 0, 1)[..., None] ** 8 * np.array([40, 0, 0])
    alpha = np.clip((1 - t) * S * 0.43 / 1.5, 0, 1)
    out = np.dstack([np.clip(col, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


if __name__ == '__main__':
    n = 768
    seal().save(f'{OUT}/seal.webp', quality=86)
    import sys
    if 'seal' in sys.argv: raise SystemExit
    Image.fromarray(tile_paper(n, (246, 241, 230), (214, 204, 186), (255, 253, 247), 11, 1400, inclusions=45)).save(f'{OUT}/paper-cotton.webp', quality=80)
    Image.fromarray(tile_paper(512, (241, 216, 210), (214, 180, 172), (252, 236, 230), 31, 700, inclusions=40)).save(f'{OUT}/paper-blush.webp', quality=78)
    Image.fromarray(tile_paper(512, (34, 66, 52), (20, 42, 33), (58, 92, 74), 41, 900, inclusions=30)).save(f'{OUT}/paper-forest.webp', quality=78)
    Image.fromarray(linen(600, 51)).save(f'{OUT}/linen-table.webp', quality=74)
    for f in sorted(os.listdir(OUT)):
        print(f, os.path.getsize(f'{OUT}/{f}') // 1024, 'KB')
