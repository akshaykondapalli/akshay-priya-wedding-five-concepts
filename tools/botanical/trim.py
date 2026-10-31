import sys
from PIL import Image
# trim.py in.png out.webp maxw [pad]
im=Image.open(sys.argv[1]).convert('RGBA'); pad=int(sys.argv[4]) if len(sys.argv)>4 else 12
bb=im.split()[3].point(lambda v:255 if v>8 else 0).getbbox()
im=im.crop((max(0,bb[0]-pad),max(0,bb[1]-pad),min(im.width,bb[2]+pad),min(im.height,bb[3]+pad)))
mw=int(sys.argv[3])
if im.width>mw: im=im.resize((mw,round(im.height*mw/im.width)),Image.LANCZOS)
im.save(sys.argv[2],quality=82,method=6); print(sys.argv[2],im.size)
