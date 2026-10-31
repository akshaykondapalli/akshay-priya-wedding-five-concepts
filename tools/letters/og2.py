from PIL import Image, ImageDraw, ImageFont, ImageFilter
I='/home/claude/site5/letters/img/'; T='ttf/'
tile=Image.open(I+'linen.webp').convert('RGBA').resize((300,300),Image.LANCZOS)
og=Image.new('RGBA',(1200,630))
for x in range(0,1200,300):
    for y in range(0,630,300): og.alpha_composite(tile,(x,y))
light=Image.open(I+'window-light.webp').convert('RGBA').resize((1200,1680)).crop((0,200,1200,830))
light.putalpha(light.split()[3].point(lambda v:int(v*.75))); og.alpha_composite(light)
def shadow(im,blur=18,op=95):
    a=im.split()[3].point(lambda v:v*op//255); sh=Image.new('RGBA',im.size,(80,60,40,0)); sh.putalpha(a); return sh.filter(ImageFilter.GaussianBlur(blur))
def place(im,xy,rot=0,off=(10,18)):
    im=im.rotate(rot,resample=Image.BICUBIC,expand=True); og.alpha_composite(shadow(im),(xy[0]+off[0],xy[1]+off[1])); og.alpha_composite(im,xy)
# box lid with ribbons
lid=Image.open(I+'box-lid.webp').convert('RGBA')
rv=Image.open(I+'ribbon-v.webp').convert('RGBA'); rh=Image.open(I+'ribbon-h.webp').convert('RGBA'); bw=Image.open(I+'bow.webp').convert('RGBA')
lid.alpha_composite(rv,(770-46,0)); lid.alpha_composite(rh,(0,int(1240*.66)-46)); lid.alpha_composite(bw,(770-230,int(1240*.66)-160))
lid=lid.resize((380,471),Image.LANCZOS); place(lid,(690,60),4)
env=Image.new('RGBA',(1000,700))
for f in ['inv-interior.webp','inv-pocket.webp']: env.alpha_composite(Image.open(I+f).convert('RGBA'))
env.alpha_composite(Image.open(I+'inv-flap.webp').convert('RGBA'),(0,0))
s=Image.open(I+'seal-gold.webp').convert('RGBA').resize((190,190),Image.LANCZOS); env.alpha_composite(s,(405,int(700*.62)-95))
env=env.resize((470,329),Image.LANCZOS); place(env,(560,330),-7)
mp=Image.open(I+'pressed-maple.webp').convert('RGBA').resize((150,150),Image.LANCZOS); place(mp,(1040,20),20,(4,8))
cf=Image.open(I+'pressed-cornflower.webp').convert('RGBA').resize((120,120),Image.LANCZOS); place(cf,(1080,470),-10,(4,8))
d=ImageDraw.Draw(og)
d.text((72,200),'L E T T E R S   A C R O S S   C O N T I N E N T S',font=ImageFont.truetype(T+'bodoni.ttf',17),fill=(148,118,63,255))
d.text((66,232),'Akshay',font=ImageFont.truetype(T+'bodonii.ttf',92),fill=(56,51,61,255))
d.text((200,330),'&',font=ImageFont.truetype(T+'saint.ttf',80),fill=(168,135,77,255))
d.text((262,326),'Priya',font=ImageFont.truetype(T+'bodonii.ttf',92),fill=(56,51,61,255))
d.text((72,462),'S A T U R D A Y  ·  2 1  N O V E M B E R  2 0 2 6',font=ImageFont.truetype(T+'bodoni.ttf',17),fill=(56,51,61,255))
d.text((72,494),'Priyanka Convention, Nallajerla',font=ImageFont.truetype(T+'casloni.ttf',24),fill=(106,97,112,255))
og.convert('RGB').save('/home/claude/site5/letters/og.jpg',quality=84,optimize=True,progressive=True)
import os;print(os.path.getsize('/home/claude/site5/letters/og.jpg')//1024,'KB')
