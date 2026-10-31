"""Procedural material textures for the courtyard scene (lime wash, teak, red oxide, granite, terracotta)."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
import os
OUT = os.path.join(os.path.dirname(__file__), 'tex')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(21112026)

def fbm(h, w, octaves=6, base=4, persist=0.55, seed=None):
    r = np.random.default_rng(seed) if seed is not None else rng
    out = np.zeros((h, w)); amp = 1; tot = 0
    for o in range(octaves):
        f = base * 2 ** o
        gh, gw = max(2, int(h / max(h, w) * f) + 2), max(2, int(w / max(h, w) * f) + 2)
        g = r.random((gh, gw))
        z = zoom(g, (h / gh * 1.02, w / gw * 1.02), order=3)[:h, :w]
        out += amp * z; tot += amp; amp *= persist
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-9)

def save(a, name):
    a = np.clip(a, 0, 255).astype(np.uint8)
    Image.fromarray(a).save(os.path.join(OUT, name))
    print('saved', name, a.shape)

def lerp3(c1, c2, t):
    c1 = np.array(c1, float); c2 = np.array(c2, float)
    return c1 + (c2 - c1) * t[..., None]

# Lime wash: warm off-white, mottled, faint brush streaks, a turmeric blush near the base
def limewash(h, w, name, base=(238, 226, 202), dark=(206, 188, 158), seed=1):
    n1 = fbm(h, w, 7, 3, 0.6, seed)
    n2 = fbm(h, w, 5, 24, 0.5, seed + 1)
    streak = gaussian_filter(np.random.default_rng(seed + 2).random((h, w)), (0.8, 26))
    streak = (streak - streak.min()) / (streak.max() - streak.min())
    t = np.clip(0.55 * n1 + 0.25 * n2 + 0.2 * streak, 0, 1) ** 1.4
    img = lerp3(base, dark, t)
    grain = np.random.default_rng(seed + 3).normal(0, 3.2, (h, w))
    img += grain[..., None]
    save(img, name)

# Teak: vertical grain with growth rings, warm brown
def teak(h, w, name, seed=5):
    y, x = np.mgrid[0:h, 0:w].astype(float)
    warp = fbm(h, w, 5, 3, 0.6, seed) * 60
    fine = fbm(h, w, 4, 40, 0.5, seed + 1)
    rings = np.sin((x + warp) / 7.0 + fine * 3) * 0.5 + 0.5
    rings = rings ** 3
    streaks = gaussian_filter(np.random.default_rng(seed + 2).random((h, w)), (40, 0.7))
    streaks = (streaks - streaks.min()) / (streaks.max() - streaks.min())
    t = np.clip(0.45 * rings + 0.35 * streaks + 0.2 * fbm(h, w, 6, 6, 0.55, seed + 3), 0, 1)
    img = lerp3((128, 76, 40), (62, 32, 16), t)
    img += np.random.default_rng(seed + 4).normal(0, 2.5, (h, w))[..., None]
    save(img, name)

# Red oxide (polished cement floor) with soft sheen variations
def redoxide(h, w, name, seed=9):
    n = fbm(h, w, 7, 5, 0.6, seed)
    m = fbm(h, w, 4, 60, 0.5, seed + 1)
    t = np.clip(0.75 * n + 0.25 * m, 0, 1)
    img = lerp3((150, 52, 36), (98, 28, 20), t)
    img += np.random.default_rng(seed + 2).normal(0, 2.0, (h, w))[..., None]
    save(img, name)

def granite(h, w, name, seed=13):
    n = fbm(h, w, 6, 8, 0.6, seed)
    speck = np.random.default_rng(seed + 1).random((h, w))
    img = lerp3((150, 142, 132), (96, 90, 84), n)
    img[speck > 0.985] *= 0.55
    img[speck < 0.01] = img[speck < 0.01] * 0.4 + 140
    save(img, name)

def terracotta(h, w, name, seed=17):
    n = fbm(h, w, 6, 6, 0.55, seed)
    img = lerp3((176, 86, 52), (112, 48, 30), n)
    img += np.random.default_rng(seed + 1).normal(0, 4, (h, w))[..., None]
    save(img, name)

def brass(h, w, name, seed=21):
    y, x = np.mgrid[0:h, 0:w].astype(float)
    n = fbm(h, w, 5, 8, 0.55, seed)
    band = np.sin(x / w * np.pi * 3 + n * 2) * 0.5 + 0.5
    img = lerp3((120, 78, 22), (238, 196, 110), np.clip(band * 0.8 + n * 0.2, 0, 1))
    save(img, name)

def paper(h, w, name, seed=25):
    n = fbm(h, w, 6, 6, 0.55, seed); f = fbm(h, w, 3, 120, 0.5, seed + 1)
    img = lerp3((246, 238, 220), (226, 212, 186), np.clip(0.7 * n + 0.3 * f, 0, 1) ** 1.3)
    img += np.random.default_rng(seed + 2).normal(0, 2.4, (h, w))[..., None]
    save(img, name)

if __name__ == '__main__':
    limewash(1800, 2400, 'limewash.png')
    limewash(1800, 2400, 'limewash-facade.png', base=(232, 214, 182), dark=(190, 164, 126), seed=40)
    teak(2048, 512, 'teak.png')
    redoxide(900, 2400, 'redoxide.png')
    granite(400, 2400, 'granite.png')
    terracotta(400, 1200, 'terracotta.png')
    brass(512, 512, 'brass.png')
    paper(1400, 1000, 'paper.png')
