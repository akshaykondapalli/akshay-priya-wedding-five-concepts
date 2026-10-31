# Adds weathered sandstone texture + dusk tonal falloff to the rendered temple layer.
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import importlib.util, sys
spec = importlib.util.spec_from_file_location('pn', '/home/claude/tools5/temple/paint_numpy.py'); pn = importlib.util.module_from_spec(spec); spec.loader.exec_module(pn)
im = np.asarray(Image.open('out/temple.png').convert('RGBA')).astype(float) / 255
h, w = im.shape[:2]
rgb, a = im[..., :3], im[..., 3]
rng = np.random.default_rng(5)
fine = gaussian_filter(rng.random((h, w)), 0.8)
mid = pn.fbm(h, w, 6, 40, seed=31)
coarse = pn.fbm(h, w, 5, 10, seed=32)
tex = (0.80 + 0.36 * (fine - 0.5) * 2 * 0.5 + 0.0) * (0.86 + 0.26 * mid) * (0.9 + 0.18 * coarse)
# streaks of weathering running down (vertical blur of noise)
streak = gaussian_filter(rng.random((h, w)), (14, 0.8))
tex *= 0.97 + 0.06 * (streak - streak.mean()) / (streak.std() * 3 + 1e-6)
tex = tex / tex.mean()
y = np.linspace(0, 1, h)[:, None]
# dusk falloff: upper tower cooler/darker (stage y 300..1400)
fall = np.clip((y * 2100 - 300) / 1100, 0, 1)
tone = 0.78 + 0.26 * fall ** 0.8
mask = np.clip((a - 0.85) / 0.15, 0, 1)
f = 1 + (tex * tone - 1) * mask
out = rgb * f[..., None]
Image.fromarray((np.dstack([np.clip(out, 0, 1), a]) * 255).astype(np.uint8), 'RGBA').save('out/temple_tex.png')
r0, r1 = map(int, open('out/temple_rows.txt').read().split())
Image.open('out/temple_tex.png').crop((0, r0, 3200, r1)).save('/home/claude/site5/temple/img/temple.webp', quality=80, method=6)
print('ok')
