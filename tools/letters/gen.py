"""Procedural asset generator for 'Letters Across Continents'.
All artwork is original and generated here (numpy/scipy/PIL). Run: python3 -I gen.py
Outputs to /home/claude/site5/letters/img/
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, zoom, map_coordinates

OUT = '/home/claude/site5/letters/img'
T = os.path.dirname(os.path.abspath(__file__)) + '/ttf/'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(2111)


def F(name, size):
    return ImageFont.truetype(T + name + '.ttf', size)


def fnoise(h, w, base=64, octaves=5, seed=None, persist=0.5):
    r = np.random.default_rng(seed) if seed is not None else rng
    out = np.zeros((h, w)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        s = max(1, int(base / 2 ** o))
        sh, sw = h // s + 3, w // s + 3
        small = r.random((sh, sw))
        up = zoom(small, s, order=3)[:h, :w]
        if up.shape != (h, w):
            up = np.pad(up, ((0, h - up.shape[0]), (0, w - up.shape[1])), mode='edge')
        out += amp * up; tot += amp; amp *= persist
    out /= tot
    out = (out - out.min()) / (out.max() - out.min() + 1e-9)
    return out


def to_img(arr, alpha=None):
    a = np.clip(arr, 0, 255).astype(np.uint8)
    if alpha is not None:
        al = np.clip(alpha * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(np.dstack([a, al]), 'RGBA')
    return Image.fromarray(a, 'RGB')


def save(img, name, q=76):
    p = os.path.join(OUT, name)
    if name.endswith('.webp'):
        img.save(p, 'WEBP', quality=q, method=6)
    elif name.endswith('.jpg'):
        img.convert('RGB').save(p, 'JPEG', quality=q, optimize=True, progressive=True)
    else:
        img.save(p)
    print(name, img.size, os.path.getsize(p) // 1024, 'KB')


# ---------------------------------------------------------------- paper
def fibres(h, w, n, seed):
    r = np.random.default_rng(seed)
    lay = Image.new('L', (w, h), 128)
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y = r.random() * w, r.random() * h
        L = r.uniform(6, 34); a = r.uniform(0, math.pi * 2); curv = r.uniform(-0.08, 0.08)
        pts = []
        for k in range(8):
            pts.append((x, y)); a += curv; x += math.cos(a) * L / 8; y += math.sin(a) * L / 8
        v = int(128 + r.choice([-1, 1], p=[0.35, 0.65]) * r.uniform(10, 34))
        d.line(pts, fill=v, width=1)
    arr = np.asarray(lay).astype(float) - 128
    return gaussian_filter(arr, 0.6)


def paper(w, h, base, seed=1, laid=False, fold=False, deckle=0, age=0.5, fib=1.0, emboss=None):
    r = np.random.default_rng(seed)
    base = np.array(base, float)
    mot = fnoise(h, w, base=220, octaves=4, seed=seed) - 0.5
    fine = fnoise(h, w, base=6, octaves=2, seed=seed + 1) - 0.5
    lum = 1 + mot * 0.06 * age + fine * 0.035
    lum += fibres(h, w, int(w * h / 900 * fib), seed + 2) / 255 * 0.9
    lum += r.normal(0, 0.012, (h, w))
    if laid:
        yy = np.arange(h)[:, None]; xx = np.arange(w)[None, :]
        lines = (np.sin(yy * 2 * math.pi / 4.2) * 0.5 + 0.5) * (0.6 + 0.4 * np.sin(xx / 37.0))
        chain = np.exp(-((xx % 92) - 46) ** 2 / 3.0)
        lum += (lines - 0.5) * 0.012 + chain * 0.012
    # light from top-left
    gy, gx = np.mgrid[0:h, 0:w]
    lum *= 1.02 - 0.05 * (gx / w * 0.4 + gy / h * 0.6)
    # aged edges
    dist = np.minimum.reduce([gx, gy, w - 1 - gx, h - 1 - gy]).astype(float)
    edge = np.exp(-dist / (min(w, h) * 0.06))
    rgb = base[None, None, :] * lum[..., None]
    tint = np.array([0.93, 0.86, 0.74])
    rgb = rgb * (1 - edge[..., None] * 0.18 * age) + rgb * tint * edge[..., None] * 0.18 * age
    # foxing
    for _ in range(int(6 * age)):
        cx, cy, rad = r.random() * w, r.random() * h, r.uniform(4, 18)
        m = np.exp(-((gx - cx) ** 2 + (gy - cy) ** 2) / (2 * rad ** 2))
        rgb *= (1 - m[..., None] * np.array([0.04, 0.08, 0.14]) * age)
    if fold:
        for fy in (h / 3, 2 * h / 3):
            wave = fy + 3 * np.sin(gx / 140.0 + fy)
            dd = gy - wave
            crease = -0.07 * np.exp(-dd ** 2 / 2.0) + 0.035 * np.exp(-(dd - 3) ** 2 / 10.0) - 0.025 * np.exp(-(dd + 6) ** 2 / 40.0)
            rgb *= (1 + crease[..., None])
        # slight panel shading
        panel = ((gy // (h / 3)).astype(int) % 2) * 0.012
        rgb *= (1 - panel[..., None])
    if emboss is not None:
        hm = gaussian_filter(emboss.astype(float), 1.6)
        sx = np.gradient(hm, axis=1); sy = np.gradient(hm, axis=0)
        shade = (-sx * 0.55 - sy * 0.75) * 1.4
        rgb *= (1 + shade[..., None])
    alpha = None
    if deckle:
        n = fnoise(h, w, base=10, octaves=3, seed=seed + 9)
        thr = deckle * (0.35 + 0.9 * n)
        alpha = np.clip((dist - thr) / 1.6, 0, 1)
        rim = np.exp(-np.maximum(dist - thr, 0) / 3.0) * (alpha > 0)
        rgb *= (1 - rim[..., None] * 0.07)
    return to_img(rgb, alpha)


# ---------------------------------------------------------------- jasmine
def petal_flower(size, n_petals, rot, squash, seed, bud=False):
    """Returns (rgb float HxWx3, alpha HxW) for one jasmine blossom."""
    r = np.random.default_rng(seed)
    S = size
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    cx = cy = S / 2
    x = (xx - cx); y = (yy - cy)
    ca, sa = math.cos(rot), math.sin(rot)
    u = x * ca + y * sa; v = (-x * sa + y * ca) / squash
    d = np.hypot(u, v); th = np.arctan2(v, u)
    R = S * 0.46
    if bud:
        # elongated bud
        mask = ((u / (R * 0.95)) ** 2 + (v / (R * 0.32)) ** 2) < 1
        mask = gaussian_filter(mask.astype(float), 0.8)
        shade = 0.78 + 0.22 * np.clip(1 - np.abs(v) / (R * 0.32), 0, 1)
        col = np.array([248, 236, 238.]) * shade[..., None]
        col[..., 1] -= np.clip(-u / R, 0, 1) * 30
        col[..., 2] -= np.clip(-u / R, 0, 1) * 18
        return col, mask
    jitter = 1 + 0.06 * np.sin(th * 3 + seed)
    k = np.abs(np.cos(n_petals * th / 2))
    rmax = R * (0.30 + 0.70 * k ** 0.55) * jitter
    mask = gaussian_filter((d < rmax).astype(float), 0.9)
    t = np.clip(d / (rmax + 1e-6), 0, 1)
    shade = 0.80 + 0.20 * t ** 0.6
    shade -= 0.10 * np.exp(-(k ** 2) / 0.02) * (t > 0.25)   # creases between petals
    shade -= 0.05 * (1 - np.clip((u + v) / (R * 1.4) + 0.6, 0, 1))  # side shadow
    col = np.array([252, 249, 240.]) * shade[..., None]
    centre = np.exp(-d ** 2 / (2 * (R * 0.09) ** 2))
    col = col * (1 - centre[..., None]) + np.array([214, 200, 120.]) * centre[..., None]
    return col, mask


def leaf(L, W, ang, seed):
    S = int(L * 1.3)
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    x = xx - S / 2; y = yy - S / 2
    ca, sa = math.cos(ang), math.sin(ang)
    u = (x * ca + y * sa) / L + 0.5; v = (-x * sa + y * ca)
    inside = (u > 0) & (u < 1)
    half = W * np.sin(np.clip(u, 0, 1) * math.pi) ** 0.85 * (1 - 0.25 * u)
    mask = gaussian_filter(((np.abs(v) < half) & inside).astype(float), 0.8)
    t = np.clip(v / (half + 1e-6), -1, 1)
    base = np.array([58, 86, 46.]) * (0.85 + 0.15 * u)[..., None]
    light = 1 + 0.22 * np.clip(-t, 0, 1) - 0.18 * np.clip(t, 0, 1)
    rib = np.exp(-(v ** 2) / 2.2) * inside
    col = base * light[..., None] + rib[..., None] * np.array([40, 40, 20.])
    spec = np.exp(-((t + 0.45) ** 2) / 0.03) * 0.25 * np.sin(u * math.pi)
    col += spec[..., None] * 255
    return col, mask, S


def composite(canvas, alpha, col, m, x0, y0):
    h, w = m.shape
    H, W = alpha.shape
    xs, ys = max(0, x0), max(0, y0)
    xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe <= xs or ye <= ys:
        return
    mm = m[ys - y0:ye - y0, xs - x0:xe - x0][..., None]
    cc = col[ys - y0:ye - y0, xs - x0:xe - x0]
    canvas[ys:ye, xs:xe] = canvas[ys:ye, xs:xe] * (1 - mm) + cc * mm
    alpha[ys:ye, xs:xe] = alpha[ys:ye, xs:xe] * (1 - mm[..., 0]) + mm[..., 0]


def jasmine_sprig(W, H, seed=3, n_flowers=7, n_buds=6, scale=1.0, stem_pts=None):
    r = np.random.default_rng(seed)
    can = np.zeros((H, W, 3)); al = np.zeros((H, W))
    # stem curve
    if stem_pts is None:
        stem_pts = [(W * 0.08, H * 0.95), (W * 0.35, H * 0.62), (W * 0.52, H * 0.38), (W * 0.82, H * 0.08)]
    P = np.array(stem_pts)
    ts = np.linspace(0, 1, 200)
    def bez(t):
        n = len(P) - 1
        return sum(math.comb(n, i) * (1 - t) ** (n - i) * t ** i * P[i] for i in range(n + 1))
    pts = [bez(t) for t in ts]
    st = Image.new('L', (W, H), 0); d = ImageDraw.Draw(st)
    d.line([tuple(p) for p in pts], fill=255, width=int(6 * scale))
    sm = gaussian_filter(np.asarray(st) / 255.0, 0.8)
    composite(can, al, np.full((H, W, 3), [70, 92, 52.]), sm, 0, 0)
    # leaves along stem
    for t in np.linspace(0.04, 0.96, 12):
        p = bez(t); q = bez(min(1, t + 0.01)); ta = math.atan2(q[1] - p[1], q[0] - p[0])
        for side in (-1, 1):
            if r.random() < 0.12:
                continue
            ang = ta + side * r.uniform(0.6, 1.1)
            Ll = r.uniform(100, 150) * scale
            c, m, S = leaf(Ll, Ll * 0.26, ang, int(r.integers(1e6)))
            off = np.array([math.cos(ang), math.sin(ang)]) * Ll * 0.5
            composite(can, al, c, m, int(p[0] + off[0] - S / 2), int(p[1] + off[1] - S / 2))
    # flowers & buds: shadows first
    items = []
    for i in range(n_flowers):
        t = r.uniform(0.15, 1.0); p = bez(t)
        p = p + r.normal(0, 26 * scale, 2)
        items.append(('f', p, r.uniform(92, 128) * scale))
    for i in range(n_buds):
        t = r.uniform(0.3, 1.0); p = bez(t) + r.normal(0, 30 * scale, 2)
        items.append(('b', p, r.uniform(48, 66) * scale))
    shadow = np.zeros((H, W))
    rendered = []
    for kind, p, s in items:
        S = int(s)
        c, m = petal_flower(S, int(r.choice([5, 6, 6, 7])), r.uniform(0, 6.28), r.uniform(0.62, 1.0), int(r.integers(1e6)), bud=(kind == 'b'))
        rendered.append((c, m, int(p[0] - S / 2), int(p[1] - S / 2)))
        tmp = np.zeros((H, W)); tc = np.zeros((H, W, 3))
        composite(tc, tmp, c, m, int(p[0] - S / 2 + 6 * scale), int(p[1] - S / 2 + 9 * scale))
        shadow = np.maximum(shadow, tmp)
    shadow = gaussian_filter(shadow, 6 * scale) * 0.55
    can = can * (1 - shadow[..., None] * (1 - al[..., None])) + 0
    al_sh = np.maximum(al, shadow * (1 - al))
    can = np.where(al[..., None] > 0, can, np.zeros(3) + 20)
    al = al_sh
    for c, m, x, y in rendered:
        composite(can, al, c, m, x, y)
    return can, al


# ---------------------------------------------------------------- desk
def desk(W=2400, H=1600, seed=11):
    r = np.random.default_rng(seed)
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    # anisotropic warp: grain runs horizontally, gentle waves
    warp = gaussian_filter(r.random((H // 8 + 2, W // 8 + 2)), (1.5, 18))
    warp = zoom(warp, 8, order=1)[:H, :W]; warp = (warp - warp.mean()) / warp.std()
    warp2 = gaussian_filter(r.random((H // 4 + 2, W // 4 + 2)), (1.0, 6))
    warp2 = zoom(warp2, 4, order=1)[:H, :W]; warp2 = (warp2 - warp2.mean()) / warp2.std()
    t = gy / H * 70 + warp * 2.2 + warp2 * 0.35
    rings = (np.sin(t * 2 * math.pi) * 0.5 + 0.5) ** 4
    fine = gaussian_filter(r.random((H, W)), (0.5, 30)); fine = (fine - fine.mean()) / fine.std()
    streak = gaussian_filter(r.random((H, W)), (3, 120)); streak = (streak - streak.mean()) / streak.std()
    plank = np.floor(gy / (H / 4.0))
    ptint = np.array([0.1, -0.06, 0.04, -0.1])[plank.astype(int) % 4]
    dark = np.array([40, 23, 15.]); light = np.array([122, 78, 48.])
    v = 0.56 + ptint - rings * 0.22 + fine * 0.03 + streak * 0.06
    rgb = dark + (light - dark) * np.clip(v, 0, 1)[..., None]
    seam = np.abs(gy - (plank + 0.0) * (H / 4.0))
    rgb *= (1 - (np.exp(-(seam ** 2) / 2.5) * 0.6 * (plank > 0))[..., None])
    rgb *= (1 + (np.exp(-((seam - 3) ** 2) / 3.0) * 0.12 * (plank > 0))[..., None])
    cx, cy = W * 0.5, H * 0.42
    rr = ((gx - cx) / (W * 0.55)) ** 2 + ((gy - cy) / (H * 0.62)) ** 2
    light_pool = 0.36 + 0.95 * np.exp(-rr * 1.6)
    rgb = rgb * light_pool[..., None] * np.array([1.08, 1.0, 0.86])
    sheen = np.exp(-((gx - W * 0.62) / (W * 0.22)) ** 2 - ((gy - H * 0.3) / (H * 0.16)) ** 2) * 16
    rgb += sheen[..., None]
    rgb += r.normal(0, 2.0, rgb.shape)
    return to_img(rgb)


# ---------------------------------------------------------------- envelope
EW, EH = 1000, 680
STR = 26  # airmail stripe width


def stripe_band(w, h, phase=0):
    yy, xx = np.mgrid[0:h, 0:w]
    k = ((xx + yy + phase) // 34) % 4
    col = np.zeros((h, w, 3))
    col[k == 0] = [168, 46, 44]
    col[k == 1] = [244, 236, 220]
    col[k == 2] = [46, 70, 128]
    col[k == 3] = [244, 236, 220]
    return col


def airmail_border(img_rgb, mask_edge):
    """mask_edge: HxW float where border stripes go."""
    h, w = mask_edge.shape
    band = stripe_band(w, h)
    wear = fnoise(h, w, base=8, octaves=2, seed=5) * 0.25 + 0.75
    m = (mask_edge * wear)[..., None]
    return img_rgb * (1 - m * 0.92) + band * m * 0.92 * (np.asarray(img_rgb) / 235.0)


def liner(w, h, seed=21):
    base = np.array(paper(w, h, (84, 98, 70), seed=seed, age=0.3, fib=0.4)).astype(float)[..., :3]
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cell = 54
    u = (xx % cell) - cell / 2; v = ((yy + (xx // cell % 2) * cell / 2) % cell) - cell / 2
    d = np.hypot(u, v); th = np.arctan2(v, u)
    petal = d < 9 * (0.35 + 0.65 * np.abs(np.cos(2.5 * th)) ** 0.6)
    lat = (np.abs(u - v) < 0.7) | (np.abs(u + v) < 0.7)
    m = gaussian_filter((petal | (lat & (d > 14))).astype(float), 0.7)
    base = base * (1 - m[..., None] * 0.55) + np.array([214, 196, 150.]) * m[..., None] * 0.55
    return base


def envelope():
    W, H = EW, EH
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    cream = np.array(paper(W, H, (240, 230, 207), seed=31, age=0.7)).astype(float)[..., :3]
    # interior (seen when flap open): liner with deep shadow at bottom of pocket
    lin = liner(W, H)
    shade = 0.45 + 0.55 * np.clip(1 - gy / (H * 0.75), 0, 1)
    interior = lin * shade[..., None]
    rim = np.minimum.reduce([gx, gy, W - 1 - gx, H - 1 - gy])
    interior = np.where((rim < 6)[..., None], cream * 0.9, interior)
    save(to_img(interior), 'env-interior.webp', 74)

    # pocket: side flaps + bottom flap (front of back face)
    mid = (W / 2, H * 0.50)
    left = Image.new('L', (W, H), 0); ImageDraw.Draw(left).polygon([(0, 0), (W * 0.54, H * 0.56), (0, H)], fill=255)
    right = Image.new('L', (W, H), 0); ImageDraw.Draw(right).polygon([(W, 0), (W * 0.46, H * 0.56), (W, H)], fill=255)
    bottom = Image.new('L', (W, H), 0); ImageDraw.Draw(bottom).polygon([(0, H), (W * 0.06, H * 0.40), (W * 0.5, H * 0.36), (W * 0.94, H * 0.40), (W, H)], fill=255)
    L = gaussian_filter(np.asarray(left) / 255.0, 0.7)
    R = gaussian_filter(np.asarray(right) / 255.0, 0.7)
    B = gaussian_filter(np.asarray(bottom) / 255.0, 0.7)
    pocket = cream.copy()
    al = np.clip(L + R + B, 0, 1)
    # shading: side flaps slightly darker, bottom flap casts shadow onto sides
    pocket *= (1 - 0.035 * L[..., None]) * (1 - 0.02 * R[..., None])
    bshadow = gaussian_filter(np.asarray(bottom) / 255.0, 8) - B
    pocket *= (1 - np.clip(bshadow, 0, 1)[..., None] * 0.28)
    pocket *= (1 + 0.03 * B[..., None])
    # side flap edge shadows
    for M in (L, R):
        sh = np.clip(gaussian_filter(M, 6) - M, 0, 1)
        pocket *= (1 - sh[..., None] * 0.22 * (1 - B[..., None]))
    edge = (rim < STR).astype(float)
    pocket = airmail_border(pocket, edge)
    # 'BY AIR MAIL' label bottom-left (blue box)
    img = to_img(pocket, al)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, H - 170, 330, H - 92), radius=4, outline=(46, 70, 128, 230), width=3)
    d.text((200, H - 131), 'BY AIR MAIL', font=F('courierb', 34), fill=(46, 70, 128, 235), anchor='mm')
    d.text((200, H - 104), 'PAR AVION', font=F('courier', 18), fill=(46, 70, 128, 200), anchor='mm')
    save(img, 'env-pocket.webp', 78)

    # top flap (outer)
    FH = int(H * 0.60)
    fl = Image.new('L', (W, FH), 0)
    ImageDraw.Draw(fl).polygon([(0, 0), (W, 0), (W * 0.56, FH - 18), (W * 0.5, FH), (W * 0.44, FH - 18)], fill=255)
    fm = gaussian_filter(np.asarray(fl) / 255.0, 0.8)
    fy, fx = np.mgrid[0:FH, 0:W].astype(float)
    outer = np.array(paper(W, FH, (243, 234, 212), seed=33, age=0.7)).astype(float)[..., :3]
    outer *= (1 + 0.035 * (1 - fy / FH))[..., None]
    # stripe along slanted edges + top
    edgeband = np.clip(gaussian_filter((fm > 0.5).astype(float), 0) - 0, 0, 1)
    inner = gaussian_filter(fm, 1)
    from scipy.ndimage import distance_transform_edt
    dist = distance_transform_edt(fm > 0.5)
    outer = airmail_border(outer, ((dist < STR) & (fm > 0.5)).astype(float))
    save(to_img(outer, fm), 'env-flap.webp', 80)
    lin2 = liner(W, FH, seed=23)
    lin2 = np.where(((dist < 8) & (fm > 0.5))[..., None], np.array([238, 228, 205.]), lin2)
    save(to_img(lin2, fm), 'env-flap-in.webp', 78)


# ---------------------------------------------------------------- wax seal
def seal(S=440, seed=7):
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    cx = cy = S / 2
    x = xx - cx; y = yy - cy
    d = np.hypot(x, y); th = np.arctan2(y, x)
    R0 = S * 0.40
    ang = np.linspace(-math.pi, math.pi, 720)
    prof = np.zeros_like(ang)
    for k in range(2, 14):
        prof += r.normal(0, 1) / k ** 1.3 * np.cos(k * ang + r.uniform(0, 6.28))
    prof = 1 + 0.05 * prof / np.abs(prof).max()
    for _ in range(4):  # drips/blobs
        c = r.uniform(-math.pi, math.pi); wdt = r.uniform(0.12, 0.3)
        prof += r.uniform(0.04, 0.09) * np.exp(-((((ang - c) + math.pi) % (2 * math.pi) - math.pi) ** 2) / (2 * wdt ** 2))
    Rt = R0 * np.interp(th, ang, prof)
    edge = np.clip((Rt - d) / 26.0, 0, 1)
    hmap = np.sin(edge * math.pi / 2) ** 0.8 * 0.9
    rn = d / R0
    rim = np.exp(-((rn - 0.74) / 0.035) ** 2) * 0.22
    inner = 1 / (1 + np.exp((rn - 0.71) / 0.012))
    hmap += rim - inner * 0.16
    # dotted ring
    dots = np.exp(-((rn - 0.66) / 0.012) ** 2) * (np.cos(th * 48) > 0.55) * 0.07
    hmap += dots
    # monogram
    mono = Image.new('L', (S, S), 0); dd = ImageDraw.Draw(mono)
    dd.text((cx - S * 0.095, cy - S * 0.01), 'A', font=F('casloni', int(S * 0.27)), fill=255, anchor='mm')
    dd.text((cx + S * 0.10, cy + S * 0.035), 'P', font=F('casloni', int(S * 0.27)), fill=255, anchor='mm')
    dd.text((cx + S * 0.005, cy + S * 0.15), '&', font=F('casloni', int(S * 0.08)), fill=255, anchor='mm')
    mm = gaussian_filter(np.asarray(mono) / 255.0, 1.4)
    hmap += mm * 0.16 * inner
    hmap += (fnoise(S, S, base=20, octaves=3, seed=seed) - 0.5) * 0.03 * edge
    hmap = gaussian_filter(hmap, 0.9)
    alpha = gaussian_filter((d < Rt).astype(float), 0.9)
    k = 60.0
    nx = -np.gradient(hmap, axis=1) * k; ny = -np.gradient(hmap, axis=0) * k; nz = np.ones_like(hmap)
    n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2); nx /= n; ny /= n; nz /= n
    Lv = np.array([-0.45, -0.6, 0.66]); Lv /= np.linalg.norm(Lv)
    diff = np.clip(nx * Lv[0] + ny * Lv[1] + nz * Lv[2], 0, 1)
    Hv = Lv + np.array([0, 0, 1.0]); Hv /= np.linalg.norm(Hv)
    spec = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1) ** 46
    lap = gaussian_filter(hmap, 2) - hmap
    ao = 1 - np.clip(-lap * 9, 0, 0.35)
    base = np.array([112, 18, 26.])
    rgb = base * (0.32 + 0.95 * diff)[..., None] * ao[..., None]
    rgb += spec[..., None] * np.array([255, 214, 200.]) * 0.75
    rgb += (fnoise(S, S, base=4, octaves=1, seed=seed + 2) - 0.5)[..., None] * 8
    return rgb, alpha


def seal_assets():
    rgb, a = seal()
    save(to_img(rgb, a), 'seal.webp', 86)
    S = rgb.shape[0]
    # crack path
    r = np.random.default_rng(4)
    ys = np.linspace(0, S, 22)
    xs = S * 0.52 + np.cumsum(r.normal(0, 7, 22)) + (ys - S / 2) * 0.28
    left = Image.new('L', (S, S), 0)
    poly = [(0, 0)] + [(float(xs[i]), float(ys[i])) for i in range(22)] + [(0, S)]
    ImageDraw.Draw(left).polygon(poly, fill=255)
    lm = gaussian_filter(np.asarray(left) / 255.0, 0.6)
    gap = np.zeros((S, S)); gimg = Image.new('L', (S, S), 0)
    ImageDraw.Draw(gimg).line([(float(xs[i]), float(ys[i])) for i in range(22)], fill=255, width=4)
    gm = gaussian_filter(np.asarray(gimg) / 255.0, 0.8)
    # bright broken edge
    edge = gaussian_filter(np.asarray(gimg) / 255.0, 3) * 1.0
    rgb2 = rgb + edge[..., None] * np.array([60, 18, 16.])
    save(to_img(rgb2, a * lm * (1 - gm)), 'seal-l.webp', 86)
    save(to_img(rgb2, a * (1 - lm) * (1 - gm)), 'seal-r.webp', 86)
    # small seal for invitation footer
    small = to_img(rgb, a).resize((160, 160), Image.LANCZOS)
    save(small, 'seal-small.webp', 86)


# ---------------------------------------------------------------- stamps
def perforated(w, h, hole=7, step=19, margin=0):
    m = Image.new('L', (w, h), 255); d = ImageDraw.Draw(m)
    for x in np.arange(step / 2, w, step):
        d.ellipse((x - hole, -hole, x + hole, hole), fill=0)
        d.ellipse((x - hole, h - hole, x + hole, h + hole), fill=0)
    for y in np.arange(step / 2, h, step):
        d.ellipse((-hole, y - hole, hole, y + hole), fill=0)
        d.ellipse((w - hole, y - hole, w + hole, y + hole), fill=0)
    return gaussian_filter(np.asarray(m) / 255.0, 0.7)


def engrave(art, spacing=4.0, strength=0.22, angle=0.0):
    h, w, _ = art.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    lum = art.mean(axis=2) / 255
    t = (yy * math.cos(angle) + xx * math.sin(angle)) / spacing
    line = 0.5 + 0.5 * np.cos(t * 2 * math.pi)
    thr = (line < (1 - lum) * 1.1).astype(float)
    thr = gaussian_filter(thr, 0.5)
    return art * (1 - thr[..., None] * strength)


def palm(d, x, y, hgt, lean, col, r):
    pts = []
    for k in range(20):
        t = k / 19
        pts.append((x + lean * t ** 1.6, y - hgt * t))
    d.line(pts, fill=col, width=max(2, int(hgt * 0.045)))
    tx, ty = pts[-1]
    for a in np.linspace(-2.9, -0.2, 9):
        Lf = hgt * r.uniform(0.32, 0.46)
        fpts = []
        for k in range(10):
            t = k / 9
            fpts.append((tx + math.cos(a) * Lf * t, ty + math.sin(a) * Lf * t + (Lf * 0.35) * t ** 2))
        d.line(fpts, fill=col, width=max(2, int(hgt * 0.03)))
        for k in range(2, 10):
            px, py = fpts[k]
            for s in (-1, 1):
                d.line([(px, py), (px + math.cos(a + s * 1.2) * Lf * 0.14, py + math.sin(a + s * 1.2) * Lf * 0.14 + Lf * 0.05)], fill=col, width=1)


def stamp(kind, w=300, h=360, seed=1):
    r = np.random.default_rng(seed)
    pap = np.array(paper(w, h, (246, 241, 228), seed=seed + 40, age=0.4, fib=0.4)).astype(float)[..., :3]
    m = 22
    aw, ah = w - 2 * m, h - 2 * m - 40
    if kind == 'jasmine':
        yy = np.mgrid[0:ah, 0:aw][0] / ah
        art = np.array([148, 124, 70.]) * (1 - yy[..., None]) + np.array([96, 104, 66.]) * yy[..., None]
        c, a = jasmine_sprig(aw, ah, seed=8, n_flowers=4, n_buds=3, scale=0.62,
                             stem_pts=[(aw * 0.1, ah * 1.0), (aw * 0.45, ah * 0.6), (aw * 0.6, ah * 0.3), (aw * 0.9, ah * 0.05)])
        art = art * (1 - a[..., None]) + c * a[..., None]
        art = engrave(art, 3.6, 0.12, 0.3)
        label, denom = 'JASMINE', '21'
    elif kind == 'delta':
        yy, xx = np.mgrid[0:ah, 0:aw].astype(float)
        hz = ah * 0.58
        sky = np.array([238, 170, 128.]) * (1 - yy / hz)[..., None] + np.array([214, 112, 104.]) * (yy / hz)[..., None]
        sun = np.exp(-((xx - aw * 0.62) ** 2 + (yy - hz * 0.78) ** 2) / (2 * 18 ** 2))
        sky += sun[..., None] * np.array([40, 60, 40.])
        sd = np.hypot(xx - aw * 0.62, yy - hz * 0.78) < 22
        sky[sd] = [252, 220, 160]
        water = np.array([170, 98, 102.]) * 0.9 + (np.sin(yy * 1.3) * 6)[..., None]
        art = np.where((yy < hz)[..., None], sky, water)
        refl = (np.abs(xx - aw * 0.62) < 20 - (yy - hz) * 0.12) & (yy > hz) & (np.sin(yy * 1.7) > -0.2)
        art[refl] = [246, 196, 150]
        img = to_img(art); d = ImageDraw.Draw(img)
        d.polygon([(0, hz + 4), (aw * 0.45, hz - 6), (aw, hz + 2), (aw, hz + 10), (0, hz + 14)], fill=(70, 52, 60))
        for (px, ph, ln) in [(aw * 0.18, ah * 0.5, 14), (aw * 0.3, ah * 0.36, -8), (aw * 0.82, ah * 0.44, -16)]:
            palm(d, px, hz + 4, ph, ln, (52, 38, 46), r)
        art = np.asarray(img).astype(float)
        art = engrave(art, 3.4, 0.16, 0.0)
        label, denom = 'DELTA DUSK', '9·55'
    else:  # compass / air mail
        yy, xx = np.mgrid[0:ah, 0:aw].astype(float)
        art = np.array([44, 62, 104.]) * (0.85 + 0.15 * (1 - yy / ah))[..., None]
        img = to_img(art); d = ImageDraw.Draw(img)
        cx, cy = aw / 2, ah / 2
        for rad in (ah * 0.38, ah * 0.36, ah * 0.22):
            d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=(226, 210, 170), width=2)
        for i in range(16):
            a = i * math.pi / 8
            L = ah * (0.42 if i % 4 == 0 else 0.28 if i % 2 == 0 else 0.2)
            wdt = ah * (0.07 if i % 4 == 0 else 0.045)
            tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
            l1 = (cx + math.cos(a + math.pi / 2) * wdt, cy + math.sin(a + math.pi / 2) * wdt)
            l2 = (cx + math.cos(a - math.pi / 2) * wdt, cy + math.sin(a - math.pi / 2) * wdt)
            d.polygon([tip, l1, (cx, cy)], fill=(232, 216, 176))
            d.polygon([tip, l2, (cx, cy)], fill=(176, 150, 104))
        # two dashed routes meeting at centre
        for (sx, sy, col) in [(8, ah - 10, (226, 120, 112)), (aw - 8, 10, (240, 226, 190))]:
            pts = [(sx + (cx - sx) * t + math.sin(t * 6) * 10, sy + (cy - sy) * t) for t in np.linspace(0, 1, 30)]
            for k in range(0, 29, 2):
                d.line([pts[k], pts[k + 1]], fill=col, width=3)
        art = np.asarray(img).astype(float)
        art = engrave(art, 3.2, 0.1, 0.8)
        label, denom = 'AIR MAIL', 'XXI'
    pap[m:m + ah, m:m + aw] = art
    img = to_img(pap)
    d = ImageDraw.Draw(img)
    d.rectangle((m - 1, m - 1, m + aw, m + ah), outline=(80, 66, 50), width=1)
    d.text((m + 10, m + 8), denom, font=F('caslonb', 34), fill=(250, 244, 230))
    d.text((w / 2, h - m - 18), label, font=F('courierb', 22), fill=(64, 52, 40), anchor='mm')
    alpha = perforated(w, h)
    return Image.fromarray(np.dstack([np.asarray(img), (alpha * 255).astype(np.uint8)]), 'RGBA')


def postmark(W=560, H=300, seed=3):
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    cx, cy, R = 150, 150, 118
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=255, width=6)
    d.ellipse((cx - R + 22, cy - R + 22, cx + R - 22, cy + R - 22), outline=255, width=3)
    txt = 'NALLAJERLA  ·  ANDHRA PRADESH  ·  '
    f = F('courierb', 22)
    n = len(txt)
    for i, ch in enumerate(txt):
        a = -math.pi / 2 + i / n * 2 * math.pi
        ci = Image.new('L', (40, 40), 0); ImageDraw.Draw(ci).text((20, 20), ch, font=f, fill=255, anchor='mm')
        ci = ci.rotate(-math.degrees(a) - 90, resample=Image.BICUBIC)
        px, py = cx + math.cos(a) * (R - 12), cy + math.sin(a) * (R - 12)
        im.paste(255, (int(px - 20), int(py - 20)), ci)
    d.text((cx, cy - 18), '21 · XI', font=F('courierb', 40), fill=255, anchor='mm')
    d.text((cx, cy + 26), '2026', font=F('courierb', 36), fill=255, anchor='mm')
    for k in range(5):
        y0 = 70 + k * 40
        pts = [(cx + R + 18 + t, y0 + 9 * math.sin(t / 26.0)) for t in range(0, W - cx - R - 30, 4)]
        d.line(pts, fill=255, width=5)
    m = gaussian_filter(np.asarray(im) / 255.0, 0.9)
    ink = fnoise(H, W, base=14, octaves=3, seed=seed)
    skip = fnoise(H, W, base=60, octaves=2, seed=seed + 1)
    a = m * (0.45 + 0.55 * ink) * np.clip((skip - 0.18) * 3, 0.15, 1) * 0.8
    rgb = np.zeros((H, W, 3)) + np.array([34, 36, 58.])
    return to_img(rgb, a)


# ---------------------------------------------------------------- photo print
def photo_print():
    src = Image.open('/home/claude/shared5/couple-crop-full.png').convert('RGB')
    PW = 820
    ph = int(src.height * PW / src.width)
    photo = src.resize((PW, ph), Image.LANCZOS)
    B = 40
    W, H = PW + 2 * B, ph + 2 * B
    card = np.array(paper(W, H, (247, 244, 236), seed=77, age=0.25, fib=0.5)).astype(float)[..., :3]
    p = np.asarray(photo).astype(float)
    # very light print-surface sheen only (faces unaltered otherwise)
    yy, xx = np.mgrid[0:ph, 0:PW].astype(float)
    sheen = np.exp(-((xx - yy * 0.9 - PW * 0.75) / (PW * 0.18)) ** 2) * 6
    p = p + sheen[..., None]
    card[B:B + ph, B:B + PW] = p
    # thin inner shadow line at photo edge
    card[B - 1, B:B + PW] *= 0.85; card[B + ph, B:B + PW] *= 0.9
    # deckle scallops
    gy, gx = np.mgrid[0:H, 0:W].astype(float)
    dist = np.minimum.reduce([gx, gy, W - 1 - gx, H - 1 - gy])
    along = np.where(np.minimum(gx, W - 1 - gx) < np.minimum(gy, H - 1 - gy), gy, gx)
    sc = 5.5 * (0.5 + 0.5 * np.cos(along / 15.0 * 2 * math.pi))
    alpha = np.clip((dist - sc) / 1.4, 0, 1)
    return to_img(card, alpha)


# ---------------------------------------------------------------- invitation emboss mask
def emboss_border(w, h):
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    for inset, wd in ((46, 3), (58, 1)):
        d.rectangle((inset, inset, w - inset, h - inset), outline=255, width=wd)
    # corner lotus-petal fans
    for (cx, cy, s) in ((70, 70, 1), (w - 70, 70, 1), (70, h - 70, 1), (w - 70, h - 70, 1)):
        for k in range(5):
            a = k * math.pi / 8 + (0 if cx < w / 2 and cy < h / 2 else math.pi / 2 if cx > w / 2 and cy < h / 2 else math.pi if cx > w / 2 else 3 * math.pi / 2)
            ex, ey = cx + math.cos(a) * 30, cy + math.sin(a) * 30
            d.line([(cx, cy), (ex, ey)], fill=255, width=2)
    return np.asarray(m) / 255.0


def main():
    only = os.environ.get('ONLY')
    if only:
        for fn in only.split(','):
            globals()[fn]()
        return
    save(desk(), 'desk.webp', 62)
    small = desk(1200, 1600, seed=12)
    save(small, 'desk-portrait.webp', 60)
    envelope()
    seal_assets()
    for i, k in enumerate(['jasmine', 'delta', 'airmail']):
        save(stamp(k, seed=10 + i), f'stamp-{k}.webp', 84)
    save(postmark(), 'postmark.webp', 80)
    # papers (cards ~ 450x660 css, rendered at 2x)
    CW, CH = 900, 1320
    save(paper(CW, CH, (247, 241, 228), seed=101, laid=True, fold=True, age=0.6), 'paper-letter.webp', 72)
    save(paper(CW, CH, (241, 233, 213), seed=102, age=0.8, fib=1.3), 'paper-postcard.webp', 72)
    save(paper(CW, CH, (250, 246, 236), seed=103, deckle=10, age=0.25, fib=0.7, emboss=emboss_border(CW, CH)), 'paper-invite.webp', 74)
    save(paper(CW, CH, (232, 236, 233), seed=104, age=0.5, fib=0.8), 'paper-itinerary.webp', 72)
    save(paper(CW, CH, (198, 168, 128), seed=105, age=0.9, fib=2.0), 'paper-kraft.webp', 70)
    save(photo_print(), 'photo-print.webp', 84)
    c, a = jasmine_sprig(760, 980, seed=3, n_flowers=10, n_buds=8)
    save(to_img(c, a), 'jasmine.webp', 82)
    c, a = jasmine_sprig(520, 660, seed=19, n_flowers=6, n_buds=5, scale=0.75,
                         stem_pts=[(30, 640), (200, 420), (300, 240), (500, 40)])
    save(to_img(c, a), 'jasmine-small.webp', 82)




def desk_only():
    save(desk(), 'desk.webp', 62); save(desk(1200, 1600, seed=12), 'desk-portrait.webp', 60)

def jas_only():
    c, a = jasmine_sprig(760, 980, seed=3, n_flowers=10, n_buds=8)
    save(to_img(c, a), 'jasmine.webp', 82)
    c, a = jasmine_sprig(520, 660, seed=19, n_flowers=6, n_buds=5, scale=0.75, stem_pts=[(30, 640), (200, 420), (300, 240), (500, 40)])
    save(to_img(c, a), 'jasmine-small.webp', 82)


if __name__ == '__main__':
    main()
