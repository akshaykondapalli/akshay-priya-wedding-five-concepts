"""Post-process rendered layers: dusk grade, depth blur, film grain, light maps; export WebP (wide + phone crop)."""
import json, os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
os.chdir(os.path.dirname(os.path.abspath(__file__)))
OUT = '/home/claude/site5/courtyard/img'; os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)
meta = json.load(open('render/meta.json'))
H, W = 1800, 2400

def load(n): return np.asarray(Image.open(f'render/{n}.png').convert('RGBA')).astype(np.float32) / 255

def grain(img, amt=0.035, sigma=0.6):
    h, w = img.shape[:2]
    n = gaussian_filter(rng.normal(0, 1, (h, w)), sigma) * amt
    img[..., :3] = np.clip(img[..., :3] + n[..., None], 0, 1)
    return img

def grade(img, shadows=(0.10, 0.06, 0.12), gain=(1.0, 0.97, 0.92)):
    rgb = img[..., :3]
    lum = rgb.mean(-1, keepdims=True)
    rgb = rgb * np.array(gain) + np.array(shadows) * (1 - lum) ** 2 * 0.5
    img[..., :3] = np.clip(rgb, 0, 1); return img

def vgrad(top, bottom, y0=0, y1=H):
    y = np.clip((np.arange(H) - y0) / (y1 - y0), 0, 1)[:, None, None]
    return top + (bottom - top) * y

def radial(cx, cy, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))

def save(img, name, alpha):
    a = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    mode = 'RGBA' if alpha else 'RGB'
    im = Image.fromarray(a if alpha else a[..., :3], mode)
    q = 74
    im.save(f'{OUT}/{name}-wide.webp', quality=q, method=6)
    im.crop((600, 0, 1800, 1800)).save(f'{OUT}/{name}-tall.webp', quality=q, method=6)
    print(name, os.path.getsize(f'{OUT}/{name}-wide.webp') // 1024, 'KB wide,', os.path.getsize(f'{OUT}/{name}-tall.webp') // 1024, 'KB tall')

# Layer C — far courtyard: dusk interior, slight depth softness
c = load('layer-c')
c[..., :3] = gaussian_filter(c[..., :3], (1.1, 1.1, 0))
dark = vgrad(np.array([1.0, 1.0, 1.0]), np.array([0.62, 0.58, 0.6]), 560, 1000)
dark = np.where((np.arange(H) < 560)[:, None, None], 1.0, dark)
c[..., :3] *= dark * 0.92 + 0.08
c[..., :3] *= (0.55 + 0.45 * radial(1200, 900, 1300, 900))[..., None]
c = grade(c); c = grain(c, 0.03)
save(c, 'c', False)

# Layer B — near verandah: silhouetted against the courtyard, warm rim from below
b = load('layer-b')
b[..., :3] *= 0.62
rim = radial(1200, 1500, 700, 500)[..., None] * np.array([0.35, 0.18, 0.06])
b[..., :3] = np.clip(b[..., :3] + rim * b[..., 3:4] * 0.6, 0, 1)
b = grade(b, gain=(0.98, 0.94, 0.9)); b = grain(b, 0.03)
save(b, 'b', True)

# Layer A — facade at dusk, lamp warmth pooling near the door
a = load('layer-a')
a[..., :3] *= (0.42 + 0.58 * radial(1200, 1250, 1100, 1000))[..., None]
a[..., :3] = np.clip(a[..., :3] + radial(1200, 1700, 900, 300)[..., None] * np.array([.12, .06, .01]), 0, 1)
a = grade(a); a = grain(a, 0.035)
save(a, 'a', True)

# Doors
for side in 'lr':
    d = np.asarray(Image.open(f'render/door-{side}.png').convert('RGBA')).astype(np.float32) / 255
    d[..., :3] *= 0.82
    yy = np.linspace(0, 1, d.shape[0])[:, None, None]
    d[..., :3] *= 0.85 + 0.25 * (yy > 0.55) * np.minimum(1, (yy - .55) * 3)  # warm light from threshold lamps
    rng2 = np.random.default_rng(3); d[..., :3] = np.clip(d[..., :3] + rng2.normal(0, .03, d.shape[:2])[..., None], 0, 1)
    Image.fromarray((d * 255).astype(np.uint8), 'RGBA').save(f'{OUT}/door-{side}.webp', quality=76, method=6)
    print('door', side, os.path.getsize(f'{OUT}/door-{side}.webp') // 1024, 'KB')

# Light maps (screen-blended by the page), quarter resolution
def lightmap(ids, name, spread=1.0, warm=(1.0, 0.62, 0.26)):
    h, w = H // 4, W // 4
    yy, xx = np.mgrid[0:h, 0:w]
    m = np.zeros((h, w))
    for fl in meta['flames']:
        if fl['id'] not in ids: continue
        x, y, s = fl['x'] / 4, fl['y'] / 4, fl['s']
        m += 0.5 * np.exp(-(((xx - x) / (40 * s * spread)) ** 2 + ((yy - y) / (55 * s * spread)) ** 2))
        m += 0.18 * np.exp(-(((xx - x) / (120 * s * spread)) ** 2 + ((yy - y) / (100 * s * spread)) ** 2))
    m = 1 - np.exp(-m * 1.2)
    rgb = (np.clip(m[..., None] * np.array(warm) * 0.42, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(rgb, 'RGB')
    im.save(f'{OUT}/light-{name}-wide.webp', quality=80)
    im.crop((150, 0, 450, 450)).save(f'{OUT}/light-{name}-tall.webp', quality=80)
    print('light', name, os.path.getsize(f'{OUT}/light-{name}-wide.webp') // 1024, 'KB')
lightmap({'courtyard', 'kota'}, 'court', 1.3)
lightmap({'kundulu', 'niche'}, 'hall', 1.2)
lightmap({'door'}, 'door', 1.4)

# Strand
Image.open('render/strand.png').save(f'{OUT}/strand.webp', quality=82)
json.dump(meta, open('/home/claude/tools5/courtyard/render/meta.json', 'w'))
