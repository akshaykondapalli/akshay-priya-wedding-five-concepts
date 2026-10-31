# Procedural raster layers for The Temple of Two Souls: dusk sky, granite processional floor, sandstone texture.
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter, zoom
rng = np.random.default_rng(955)
OUT = '/home/claude/tools5/temple/out/'
W, H = 3200, 2100
VPX, VPY, K = 1600.0, 1280.0, 820.0

def fbm(h, w, octaves=6, base=4, seed=0, persistence=0.55):
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w)); amp = 1.0; tot = 0
    for o in range(octaves):
        f = base * 2 ** o
        gh, gw = max(2, int(h / max(h, w) * f) + 2), max(2, int(w / max(h, w) * f) + 2)
        g = r.standard_normal((gh, gw))
        up = zoom(g, (h / gh, w / gw), order=3)[:h, :w]
        acc += amp * up; tot += amp; amp *= persistence
    acc /= tot
    return (acc - acc.min()) / (acc.max() - acc.min())

def lerp(a, b, t): return a + (b - a) * t
def hexrgb(h): h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], float) / 255

def save(arr, name, q=80, alpha=None):
    arr = np.clip(arr, 0, 1)
    if alpha is not None:
        img = Image.fromarray((np.dstack([arr, np.clip(alpha, 0, 1)[..., None]]) * 255).astype(np.uint8), 'RGBA')
    else:
        img = Image.fromarray((arr * 255).astype(np.uint8), 'RGB')
    img.save(OUT + name + '.png')
    return img

# ---------- SKY (rendered at half res, soft by nature) ----------
def sky():
    h, w = 1050, 1600
    y = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    x = np.linspace(-1, 1, w)[None, :] * np.ones((h, 1))
    stops = [(0.00, '#1a1434'), (0.25, '#33244d'), (0.45, '#6a385d'), (0.56, '#b05858'), (0.62, '#dc875b'), (0.66, '#f2b26b'), (1.0, '#f6c784')]
    col = np.zeros((h, w, 3))
    for i in range(len(stops) - 1):
        a, ca = stops[i]; b, cb = stops[i + 1]
        m = (y >= a) & (y <= b)
        t = ((y - a) / (b - a))[..., None]
        col = np.where(m[..., None], lerp(hexrgb(ca), hexrgb(cb), t), col)
    # sun glow just below horizon behind gate
    d = np.sqrt((x * 1.3) ** 2 + ((y - 0.655) * 2.4) ** 2)
    glow = np.exp(-d * 3.2)
    col += glow[..., None] * hexrgb('#ffd59a') * 0.55
    # long stratus clouds lit from below
    n = fbm(h, w, 6, 3, seed=11)
    n2 = fbm(h, w, 5, 6, seed=12)
    band = np.exp(-((y - 0.40) / 0.11) ** 2) + 0.7 * np.exp(-((y - 0.54) / 0.06) ** 2) + 0.4 * np.exp(-((y - 0.22) / 0.09) ** 2)
    streak = gaussian_filter(n, (2, 40)) * 0.7 + gaussian_filter(n2, (1, 18)) * 0.3
    cloud = np.clip((streak - 0.52) * 4.0, 0, 1) * band
    cloud_lit = lerp(hexrgb('#4a2d55'), hexrgb('#f0a07a'), np.clip(y * 1.55, 0, 1)[..., None])
    col = lerp(col, cloud_lit, (cloud * 0.75)[..., None])
    # a few faint early stars at top
    st = rng.random((h, w)) > 0.99978
    starmask = gaussian_filter(st.astype(float), 0.6) * 4 * np.clip(1 - y * 3.6, 0, 1) * (0.4 + rng.random((h, w)))
    col += starmask[..., None] * 0.8
    col += (rng.standard_normal((h, w, 1)) * 0.012)
    img = save(col, 'sky_small')
    img.resize((W, H), Image.BICUBIC).save(OUT + 'sky.png')

# ---------- FLOOR ----------
def floor():
    y0 = int(VPY + 95)  # floor starts a touch below gate base line region (gate base ~1080)
    ys = np.arange(y0, H)[:, None].astype(float)
    xs = np.arange(W)[None, :].astype(float)
    z = K / (ys - VPY)
    X = (xs - VPX) * z / K
    # slab grid in world units
    sx, sz = 0.42, 0.62
    u = X / sx; v = z / sz
    # offset alternate rows (running bond)
    row = np.floor(v)
    u2 = u + (row % 2) * 0.5
    fu = u2 - np.floor(u2); fv = v - np.floor(v)
    # mortar width in world units, scaled for AA by pixel footprint
    px = z / K  # world size of a pixel horizontally
    mw = 0.0045
    du = np.minimum(fu, 1 - fu) * sx; dv = np.minimum(fv, 1 - fv) * sz
    mort_u = np.clip((du - mw) / (px * 1.2 + 1e-6), 0, 1)
    mort_v = np.clip((dv - mw) / (px * z * 0.8 + 1e-6), 0, 1)
    mortar = 1 - mort_u * mort_v
    # per-slab tone
    cid = (np.floor(u2).astype(int) * 7349 + row.astype(int) * 9157) % 1000
    tone = ((cid * 0.618) % 1.0) * 0.32 - 0.16
    tone = tone + (fu - 0.5) * 0.05 + (fv - 0.5) * 0.04
    # granite speckle: high-frequency noise in screen space attenuated by distance
    hgt, wid = ys.shape[0], W
    speck = rng.random((hgt, wid))
    speck = gaussian_filter(speck, 0.7)
    fade = np.clip((ys - y0) / (H - y0), 0, 1)
    gran = (speck - 0.5) * (0.9 * fade + 0.1)
    mott = fbm(hgt, wid, 5, 8, seed=21) - 0.5
    base = hexrgb('#5d5658')
    c = base[None, None, :] * (1 + tone[..., None] + gran[..., None] * 0.9 + mott[..., None] * 0.25)
    # warm reflected light from the gate & sky near horizon, cool near camera
    warm = np.exp(-np.abs(X) * 0.6) * np.clip(z / 8.2, 0, 1)
    c = c * (0.40 + 0.22 * fade[..., None]) + warm[..., None] * hexrgb('#e09a5a') * 0.32
    # sheen: polished granite reflection streak down the centre
    sheen = np.exp(-(X / 0.35) ** 2) * (0.5 + 0.5 * np.clip(z / 8, 0, 1))
    c += sheen[..., None] * hexrgb('#f2b979') * 0.10
    c = c * (1 - mortar[..., None] * 0.45)
    # outside the processional (|X| > 1.32) -> darker earth with grass texture fading into night
    edge = np.clip((np.abs(X) - 1.30) / 0.05, 0, 1)
    earth = hexrgb('#231c1f')[None, None, :] * (0.7 + mott[..., None] * 0.7 + (speck[..., None]-0.5)*0.5*fade[..., None])
    c = lerp(c, earth, edge[..., None])
    # stone kerb along edges
    kerb = np.exp(-((np.abs(X) - 1.27) / 0.035) ** 2)
    c = lerp(c, hexrgb('#8a7a6e')[None, None, :] * (0.7 + 0.3 * fade[..., None]), (kerb * 0.8)[..., None])
    # petals: marigold + rose scattered in a central band, size by depth
    petal_layer = np.zeros_like(c); palpha = np.zeros((hgt, W))
    npet = 5200
    pz = 1.05 + rng.random(npet) ** 0.7 * 7.0
    pX = rng.normal(0, 0.28, npet)
    for i in range(npet):
        sy = VPY + K / pz[i]; sx_ = VPX + pX[i] * K / pz[i]
        r = max(0.7, 13.0 / pz[i])
        iy, ix = int(sy) - y0, int(sx_)
        if iy < 0 or iy >= hgt or ix < 0 or ix >= W: continue
        rr = int(r * 1.6) + 2
        ya, yb, xa, xb = max(0, iy - rr), min(hgt, iy + rr), max(0, ix - rr * 2), min(W, ix + rr * 2)
        yy, xx = np.mgrid[ya:yb, xa:xb]
        ang = rng.random() * np.pi
        dx, dy = xx - sx_, (yy + y0) - sy
        ex = dx * np.cos(ang) + dy * np.sin(ang); ey = (-dx * np.sin(ang) + dy * np.cos(ang)) * 1.9
        m = np.clip(1.3 - np.sqrt(ex ** 2 + ey ** 2 * 1.0) / r, 0, 1)
        colr = hexrgb(['#f29a1e', '#e8771a', '#c42c2a', '#f3c13a', '#9c1f2a'][rng.integers(0, 5)]) * (0.75 + 0.35 * rng.random())
        petal_layer[ya:yb, xa:xb] = np.where(m[..., None] > palpha[ya:yb, xa:xb][..., None], colr, petal_layer[ya:yb, xa:xb])
        palpha[ya:yb, xa:xb] = np.maximum(palpha[ya:yb, xa:xb], m)
    dens = np.exp(-(X / 0.5) ** 2)
    c = lerp(c, petal_layer * (0.8 + 0.3 * fade[..., None]), (palpha * 0.97)[..., None])
    # vignette to bottom (camera darkness) and distance haze
    c *= (1 - 0.35 * fade[..., None] ** 2)
    haze = np.clip(1 - (ys - y0) / 160, 0, 1)
    c = lerp(c, hexrgb('#a86a5a'), (haze * 0.55)[..., None])
    full = np.zeros((H, W, 3)); alpha = np.zeros((H, W))
    full[y0:] = c; alpha[y0:] = 1
    # soft top edge
    alpha[y0:y0 + 6] = np.linspace(0, 1, 6)[:, None]
    save(full, 'floor', alpha=alpha)

def sandstone():
    s = 640
    n = fbm(s, s, 7, 6, seed=41); n2 = fbm(s, s, 4, 3, seed=42)
    sp = gaussian_filter(rng.random((s, s)), 0.6)
    c = lerp(hexrgb('#e9d7b6'), hexrgb('#d9bf95'), n[..., None]) * (0.96 + (sp[..., None] - 0.5) * 0.16) * (0.97 + n2[..., None] * 0.06)
    # make tileable via mirrored blend
    img = save(c, 'sand_raw')
    a = np.asarray(img).astype(float) / 255
    t = (a + np.roll(a, s // 2, 0) + np.roll(a, s // 2, 1) + np.roll(np.roll(a, s // 2, 0), s // 2, 1)) / 4
    t = lerp(a, t, 0.5)
    save(t, 'sandstone')

if __name__ == '__main__':
    import sys
    for name in (sys.argv[1:] or ['sky', 'floor', 'sandstone']):
        globals()[name](); print('done', name)
