import sys
from PIL import Image
S='/tmp/claude-0/-home-claude/2cf5e8b2-6ab2-523a-8d34-c01756c66623/scratchpad/'
c=Image.open('render/layer-c.png').convert('RGBA'); b=Image.open('render/layer-b.png').convert('RGBA'); a=Image.open('render/layer-a.png').convert('RGBA')
comp=Image.alpha_composite(c,b); open_=comp.copy()
comp=Image.alpha_composite(comp,a)
dl=Image.open('render/door-l.png').convert('RGBA'); dr=Image.open('render/door-r.png').convert('RGBA')
closed=comp.copy(); closed.alpha_composite(dl,(900,300)); closed.alpha_composite(dr,(1200,300))
for name,im in [('cA-closed',closed),('cB-open',comp),('cC-inside',open_),('cD-far',c)]:
  t=im.convert('RGB'); t.thumbnail((1200,900)); t.save(S+name+'.jpg',quality=82)
# phone crop of courtyard view
ph=open_.crop((784,0,1616,1800)).convert('RGB'); ph.thumbnail((500,1100)); ph.save(S+'phone-inside.jpg',quality=82)
