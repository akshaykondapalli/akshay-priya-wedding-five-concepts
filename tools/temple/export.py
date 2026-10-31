from PIL import Image
import numpy as np
O='out/'; D='/home/claude/site5/temple/img/'
def bbox_rows(im):
    a=np.asarray(im.split()[-1]); rows=np.where(a.max(1)>0)[0]; return rows.min(), rows.max()+1
sky=Image.open(O+'sky_small.png').convert('RGB'); sky.save(D+'sky.webp',quality=74,method=6)
t=Image.open(O+'temple.png'); r0,r1=bbox_rows(t); print('temple rows',r0,r1)
t.crop((0,r0,3200,r1)).save(D+'temple.webp',quality=80,method=6); open(O+'temple_rows.txt','w').write(f'{r0} {r1}')
f=Image.open(O+'floor.png'); f0,f1=bbox_rows(f); print('floor rows',f0,f1)
f.crop((0,f0,3200,f1)).save(D+'floor.webp',quality=72,method=6); open(O+'floor_rows.txt','w').write(f'{f0} {f1}')
Image.open(O+'pillar.png').resize((240,1200),Image.LANCZOS).save(D+'pillar.webp',quality=80,method=6)
Image.open(O+'garland.png').save(D+'garland.webp',quality=80,method=6)
Image.open(O+'bell.png').resize((200,554),Image.LANCZOS).save(D+'bell.webp',quality=82,method=6)
Image.open(O+'deepam.png').resize((160,192),Image.LANCZOS).save(D+'deepam.webp',quality=86,method=6)
for s in 'lr': Image.open(O+f'door_{s}.png').resize((600,1286),Image.LANCZOS).save(D+f'door-{s}.webp',quality=78,method=6)
Image.open(O+'arch.png').resize((720,960),Image.LANCZOS).save(D+'arch.webp',quality=82,method=6)
Image.open(O+'sandstone.png').convert('RGB').save(D+'sandstone.webp',quality=74,method=6)
