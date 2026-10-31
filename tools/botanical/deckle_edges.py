"""Fixed-thickness deckle edge masks that tile along the edge (periodic noise), intersected in CSS.
Each mask is mostly opaque with a torn edge on one side, so deckle thickness never stretches."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
OUT='/home/claude/site5/botanical/img'
TL, LONG = 600, 2400   # tile length along the edge, extent into the card
D = 9                   # deckle depth (px at 1x)
S = 2
def periodic1d(n, seed, scales=(30,10,3.5,1.3), weights=(.45,.3,.17,.08)):
    r=np.random.default_rng(seed); acc=np.zeros(n)
    for s,w in zip(scales,weights):
        v=ndi.gaussian_filter1d(r.standard_normal(n), s, mode='wrap'); v/=np.abs(v).max(); acc+=w*v
    return acc
def edge(seed):
    n=TL*S; h=40*S
    off=(D*1.1+periodic1d(n,seed)*D)*S          # torn line position (px from outer edge)
    yy=np.arange(h)[:,None].astype(float)
    r=np.random.default_rng(seed+7)
    hair=ndi.gaussian_filter(r.standard_normal((h,n)),1.0,mode='wrap'); hair=(hair-hair.min())/(hair.max()-hair.min())
    d=yy-off[None,:]+D*S*0.5*(hair-0.5)
    a=np.clip(d/(D*S*0.32),0,1)
    thin=np.clip((yy-off[None,:])/(D*S*1.4),0,1); a*= (0.84+0.16*thin)
    a[:3*S,:]=0
    return Image.fromarray((a*255).astype(np.uint8),'L').resize((TL,40),Image.LANCZOS)
def save(strip, name, rot):
    full=Image.new('L',(TL,LONG),255); full.paste(strip,(0,0))
    full=full.rotate(rot,expand=True)
    rgba=Image.merge('RGBA',[Image.new('L',full.size,0)]*3+[full]); rgba.save(f'{OUT}/{name}.webp',lossless=True)
save(edge(11),'deckle-t',0); save(edge(12),'deckle-b',180); save(edge(13),'deckle-l',90); save(edge(14),'deckle-r',-90)
import os
for n in 'tblr': print(n, os.path.getsize(f'{OUT}/deckle-{n}.webp'), Image.open(f'{OUT}/deckle-{n}.webp').size)
