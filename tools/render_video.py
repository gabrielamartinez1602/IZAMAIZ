from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from pathlib import Path
import math, random, subprocess, json, sys
import numpy as np

R=Path(__file__).resolve().parents[1]
D=R/'work/revision-19'; V=R/'work/revision-06'; B=R/'work/revision-03'; O=R/'outputs'; A=R/'source-assets'
W,H,FPS=720,1280,30; C=(W/2,H/2)
INK=(99,23,48); CREAM=(245,237,218); WHITE=(255,249,235); PINK=(202,116,137)
import os, shutil
FF=os.environ.get('FFMPEG_BINARY') or shutil.which('ffmpeg')
if not FF: raise RuntimeError('Instala FFmpeg o define FFMPEG_BINARY.')
D.mkdir(parents=True,exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Georgia.ttf'
BOLD='/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
SANS='/System/Library/Fonts/Helvetica.ttc'
fonts={k:ImageFont.truetype(p,z) for k,p,z in [('title',BOLD,49),('body',SANS,27),('small',SANS,18),('label',SANS,19),('card',BOLD,25),('detail',SANS,22),('brand',FONT,18)]}

def ease(p):p=max(0,min(1,p));return p*p*(3-2*p)
def ramp(p,a,b):return ease((p-a)/(b-a))
def lerp(a,b,p):return a+(b-a)*p

def load(name):
 im=Image.open(A/name).convert('RGBA')
 if im.getchannel('A').getextrema()[0]<255:
  b=im.getchannel('A').getbbox()
  if b:im=im.crop(b)
 return im
names=['maiz1.png','maiz2.png','canasta1.png','canasta2.png','hojasdemaiz2.m.png','semillas2.png','semillas3.png','molde.png','batidora.png','jabon1.png','jabon2.png','producto1.png']
assets={n:load(n) for n in names}
support=Image.open(R/'work/infinite/support-assets.png').convert('RGBA')
for name,box in [('pot',(0,0,700,630)),('bowl',(700,150,1254,625)),('soap',(0,730,667,1140)),('hands',(668,620,1254,1254))]:
 im=support.crop(box);b=im.getchannel('A').getbbox();assets[name]=im.crop(b) if b else im
# Fixed registration: identical visible alpha silhouette, width and 56-pixel top/right margins.
logo=Image.open(B/'logo-original-vector.png').convert('RGBA')
bb=logo.getchannel('A').point(lambda a:255 if a>20 else 0).getbbox();logo=logo.crop(bb)
logo=logo.resize((150,round(150*logo.height/logo.width)),Image.Resampling.LANCZOS)
logo_white=Image.new('RGBA',logo.size,(255,255,255,255));logo_white.putalpha(logo.getchannel('A'))
logo_guinda=Image.new('RGBA',logo.size,INK+(255,));logo_guinda.putalpha(logo.getchannel('A'));logo=logo_guinda
LOGO_X=W-56-logo.width;LOGO_Y=56

# Photo and textile frames have irregular paper edges, not UI panels.
def paper_mask(size,seed=1,margin=0):
 w,h=size;r=random.Random(seed);m=Image.new('L',size,0);d=ImageDraw.Draw(m)
 pts=[(x,margin+r.randint(0,8)) for x in range(0,w,17)]
 pts +=[(w-margin-r.randint(0,7),y) for y in range(0,h,17)]
 pts +=[(x,h-margin-r.randint(0,8)) for x in range(w,0,-17)]
 pts +=[(margin+r.randint(0,7),y) for y in range(h,0,-17)]
 d.polygon(pts,fill=255);return m

def photo(name,size,seed=1,box=None):
 im=Image.open(A/name).convert('RGB')
 if box:im=im.crop(box)
 im=ImageOps.fit(im,size,Image.Resampling.LANCZOS).convert('RGBA');im.putalpha(paper_mask(size,seed));return im
old_sheet=Image.open(R/'work/animation-assets.png').convert('RGBA')
im=old_sheet.crop((840,0,1254,502));box=im.getchannel('A').getbbox();assets['farmerL']=im.crop(box) if box else im
im=Image.open(R/'work/revision-14/recolectora.png').convert('RGBA');assets['farmerL']=im.crop(im.getchannel('A').getbbox())
assets['farmerR']=Image.open(B/'farmer-right.png').convert('RGBA')
assets['batidora.png']=Image.open(B/'mixer-pink.png').convert('RGBA')
assets['basketFilled']=Image.open(B/'basket-filled.png').convert('RGBA')
engraved=Image.open(B/'engravings.png').convert('RGBA')
for name,box in [('inkCorn',(0,0,.5,.54)),('inkLeaf',(.55,0,1,.54)),('inkGrains',(0,.55,.5,1)),('inkSteam',(.57,.54,1,1))]:
 im=engraved.crop(tuple(round(v*(engraved.width if i%2==0 else engraved.height)) for i,v in enumerate(box)));b=im.getchannel('A').getbbox();assets[name]=im.crop(b) if b else im
leaf=assets['inkLeaf'];leaf_box=leaf.getchannel('A').point(lambda a:255 if a>20 else 0).getbbox()
assets['inkLeafClean']=leaf.crop(leaf_box)

assets['clothRed']=photo('textileschiapas2.jpg',(900,410),8)
assets['clothPink']=photo('textileschiapas3.jpeg',(850,410),12)
assets['clothGold']=photo('textilesmichoacan.jpg',(650,650),14)
assets['clothStripe']=photo('textilesoaxaca2.jpg',(950,420),16,box=(160,370,1760,940))
assets['huskWall']=load('huskWall.png')

cache={}
def sticker(c,name,x,y,width=None,height=None,angle=0,alpha=1,flip=False,shadow=False):
 im=assets[name]
 if width is None:width=height*im.width/im.height
 height=width*im.height/im.width;ww=max(1,round(width));hh=max(1,round(height));ang=round(angle,1)
 key=(name,ww,hh,ang,flip)
 if key not in cache:
  v=im.resize((ww,hh),Image.Resampling.LANCZOS)
  if flip:v=ImageOps.mirror(v)
  if ang:v=v.rotate(ang,Image.Resampling.BICUBIC,expand=True)
  if len(cache)>800:cache.clear()
  cache[key]=v
 im=cache[key]
 if alpha<.999:im=im.copy();im.putalpha(im.getchannel('A').point(lambda a:int(a*max(0,alpha))))
 x=round(x-im.width/2);y=round(y-im.height/2)
 if shadow:
  sh=Image.new('RGBA',im.size,(45,17,10,0));sh.putalpha(im.getchannel('A').point(lambda a:int(a*.18)));sh=sh.filter(ImageFilter.GaussianBlur(7));c.alpha_composite(sh,(x+5,y+10))
 c.alpha_composite(im,(x,y))

def solid_paper(size,color=CREAM,seed=0):
 n=Image.effect_noise(size,7).convert('RGB');im=Image.blend(Image.new('RGB',size,color),n,.035).convert('RGBA');return im

def bgphoto(name,tint=None,amount=0):
 if not (A/name).exists():
  fallback={'campo2.png':'fondo_1.png','maizpolvo4.JPG':'fondo_3.png'}
  return Image.open(A/fallback[name]).convert('RGBA')
 im=ImageOps.fit(Image.open(A/name).convert('RGB'),(W,H),Image.Resampling.LANCZOS)
 if tint:im=Image.blend(im,Image.new('RGB',(W,H),tint),amount)
 return im.convert('RGBA')
backgrounds=[bgphoto('maizales.jpg',(21,36,21),.20),bgphoto('campo2.png',(29,35,27),.24),solid_paper((W,H)),bgphoto('maizpolvo4.JPG',CREAM,.64),bgphoto('textilesmichoacan.jpg',CREAM,.10),solid_paper((W,H)),bgphoto('textileschiapas3.jpeg',(92,23,51),.23)]
# Readable upper atmosphere over photographic backgrounds.
for idx in [0,6]:
 ar=np.zeros((H,W,4),dtype=np.uint8);ar[:,:,:3]=[22,19,12]
 for y in range(H):ar[y,:,3]=round(max(0,1-y/620)*135)
 backgrounds[idx].alpha_composite(Image.fromarray(ar))

leaf=Image.open(R/'work/revision-08/hoja-corregida.png').convert('RGBA')
bb=leaf.getchannel('A').point(lambda a:255 if a>20 else 0).getbbox();assets['leafRestored']=leaf.crop(bb)

def vessel_leaf(c,kind,x,y,width,alpha=1):
 scale=width/545
 offset=140 if kind=='pot' else 195
 sticker(c,'leafRestored',x+offset*scale,y-165*scale,height=460*scale,angle=18,alpha=alpha)

def clean_asset(path):
 im=Image.open(path).convert('RGBA');bb=im.getchannel('A').point(lambda a:255 if a>20 else 0).getbbox();return im.crop(bb)
assets['pourBowl']=clean_asset(R/'work/revision-11/pour-bowl.png')
mold_empty=assets['molde.png'];mold_filled=clean_asset(R/'work/revision-11/filled-mold.png').resize(mold_empty.size,Image.Resampling.LANCZOS)
mold_empty=mold_empty.resize((round(900*mold_empty.width/mold_empty.height),900),Image.Resampling.LANCZOS)
mold_filled=mold_filled.resize(mold_empty.size,Image.Resampling.LANCZOS)
SLOTS=[.135,.315,.50,.685,.865]
BANDS=[(.035,.225),(.23,.41),(.42,.60),(.605,.785),(.79,.98)]
def mold_state(amounts):
 if min(amounts)>=.999:return mold_filled
 if max(amounts)<=.001:return mold_empty
 mask=Image.new('L',mold_empty.size,0);md=ImageDraw.Draw(mask);ww,hh=mold_empty.size
 for k,(lo,hi) in enumerate(BANDS):
  p=max(0,min(1,amounts[k]));bottom=round(hi*hh);top=round((hi-(hi-lo)*p)*hh)
  if p>0:md.rectangle((0,top,ww,bottom),fill=255)
 return Image.composite(mold_filled,mold_empty,mask)
def place_mold(c,amounts,x,y,height,angle=0,alpha=1):
 im=mold_state(amounts);im=im.resize((round(height*im.width/im.height),round(height)),Image.Resampling.LANCZOS)
 if angle:im=im.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if alpha<1:im.putalpha(im.getchannel('A').point(lambda a:int(a*alpha)))
 c.alpha_composite(im,(round(x-im.width/2),round(y-im.height/2)))
def cold_label(c,alpha=1):
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer);cx,cy=258,298
 for k in range(6):
  a=k*math.pi/3;x=cx+math.cos(a)*17;y=cy+math.sin(a)*17
  d.line((cx,cy,x,y),fill=INK,width=2)
  for side in [-1,1]:
   px=cx+math.cos(a)*10;py=cy+math.sin(a)*10
   d.line((px,py,px+math.cos(a+side*.85+math.pi)*7,py+math.sin(a+side*.85+math.pi)*7),fill=INK,width=2)
 d.text((286,280),'Refrigeración',font=fonts['body'],fill=INK)
 if alpha<1:layer.putalpha(layer.getchannel('A').point(lambda a:int(a*alpha)))
 c.alpha_composite(layer)
def formulation(c,t):
 # Mix, then lift the mixer away and pour into each cavity, then cool the filled mold.
 leave=ramp(t,1.05,1.65)
 if leave<1:
  sticker(c,'batidora.png',192-370*leave,650-220*leave,height=425,angle=5+math.sin(t*30)*.65*(1-leave),alpha=1-leave)
  vessel_leaf(c,'bowl',195-350*leave,973+200*leave,320,1-leave)
  sticker(c,'bowl',195-350*leave,973+200*leave,width=320,angle=9,alpha=1-leave)
 cooling=ramp(t,4.6,5.65)
 center=ramp(t,.45,1.6)
 mx=lerp(lerp(445,360,center),380,cooling);my=lerp(760,710,cooling);mh=lerp(440,550,cooling);ma=lerp(0,9,center)
 a=max(0,min(1,(t-1.7)/2.8));amounts=[ramp(a*5-k,.12,.8) for k in range(5)]
 place_mold(c,amounts,mx,my,mh,ma)
 if 1.15<t<4.95:
  index=min(4,int(a*5));within=a*5-index
  yy=SLOTS[index]
  if index<4:yy=lerp(yy,SLOTS[index+1],ramp(within,.80,1))
  offset=(yy-.5)*mh;theta=math.radians(ma)
  tx=mx+math.sin(theta)*offset;ty=my+math.cos(theta)*offset
  bx=tx-160;by=ty-140
  bowl_alpha=ramp(t,1.15,1.65)*(1-ramp(t,4.5,4.95))
  sticker(c,'pourBowl',bx,by,width=300,alpha=bowl_alpha)
  flow=ramp(t,1.65,1.8)*(1-ramp(t,4.42,4.6))*(1-ramp(within,.76,.96))
  if t<4.5 and flow>.01:
   bh=300*assets['pourBowl'].height/assets['pourBowl'].width
   sx=bx+300*.435;sy=by+bh*.21
   length=ramp(within,.0,.14);ey=lerp(sy,ty,length);ex=lerp(sx,tx,length)
   pts=[]
   for j in range(35):
    v=j/34;pts.append((lerp(sx,ex,v)+math.sin(v*math.pi)*4,lerp(sy,ey,v)))
   layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
   d.line(pts,fill=(207,135,153,round(255*flow)),width=12,joint='curve')
   d.line([(x-2,y) for x,y in pts],fill=(248,204,210,round(230*flow)),width=5,joint='curve')
   d.ellipse((ex-12,ey-4,ex+12,ey+4),fill=(239,180,193,round(230*flow)))
   c.alpha_composite(layer)


static=[]
for n in range(7):
 c=Image.new('RGBA',(W,H))
 if n==0:
  sticker(c,'inkCorn',630,740,height=570,angle=-16,shadow=True)
 elif n==1:
  sticker(c,'clothStripe',370,1100,width=1040,angle=-9)
  sticker(c,'farmerL',210,594,height=540,angle=4,shadow=True)
  sticker(c,'farmerR',520,610,height=540,angle=-3,shadow=True)
  sticker(c,'basketFilled',360,851,width=520,angle=3,shadow=True)
 elif n==2:
  sticker(c,'clothRed',400,1040,width=1010,angle=-10)
  sticker(c,'inkCorn',100,655,height=420,angle=16)
  vessel_leaf(c,'pot',415,756,545)
  sticker(c,'pot',415,756,width=545,angle=-4,shadow=True)
 elif n==3:
  sticker(c,'clothPink',390,1030,width=1020,angle=-12)
  sticker(c,'inkGrains',360,458,width=190,angle=-9)
  vessel_leaf(c,'bowl',360,752,545)
  sticker(c,'bowl',360,752,width=545,angle=-5,shadow=True)
 elif n==4:
  sticker(c,'clothRed',440,1035,width=1020,angle=10)
 elif n==5:
  sticker(c,'clothPink',-185,630,width=860,angle=70)
  sticker(c,'clothPink',910,670,width=860,angle=70)
  sticker(c,'clothGold',350,650,width=560,angle=-12)
  sticker(c,'soap',370,565,width=470,angle=-16,shadow=True)
 elif n==6:
  sticker(c,'clothStripe',340,1040,width=1020,angle=10)
  sticker(c,'inkCorn',668,698,height=380,angle=-18)
 static.append(c)

FOCUS=[(355,690),(360,750),(415,650),(360,720),(480,650),(380,560),(360,680)]
TITLES=['Todo empieza\nen la tierra','El origen\ntiene rostro','El maíz\nse transforma','Del grano\nal ingrediente','La fórmula\ntoma forma','Lo que aporta\ntu jabón','Del taller\na tus manos']
KICK=['DEL CAMPO A TU PIEL','','NIXTAMALIZACIÓN','OBTENCIÓN DEL INGREDIENTE','ELABORACIÓN DEL JABÓN','INGREDIENTES Y PROPIEDADES','EMPAQUE Y ENTREGA']
BODY=[['Del maizal a tus manos.','Sigue el maíz desde la cosecha','hasta convertirse en jabón.'],['La cosecha comienza con sus manos.','Conoce el maíz y a quienes lo cultivan.','Origen y productoras: por documentar.'],['Sigue cada transformación: del grano','al ingrediente que incorporamos en tu jabón.','Proceso, responsables y lugar: por documentar.'],['Después de su preparación, el maíz','se transforma en un ingrediente de la fórmula.','Método y función: por confirmar.'],['Después de batir, la mezcla rosa','se vierte en los moldes para refrigerar.','Proceso real: por documentar.'],[],['El recorrido continúa contigo. Conoce','cómo protegemos tu jabón y cómo cuidar','su empaque después de abrirlo.']]

# Image-plane camera: separate speeds for the backdrop and the cutout plane.
def transform(im,scale,focus,pan=1,fill=(0,0,0,0)):
 cx,cy=C;fx=lerp(cx,focus[0],pan);fy=lerp(cy,focus[1],pan)
 return im.transform((W,H),Image.Transform.AFFINE,(1/scale,0,fx-cx/scale,0,1/scale,fy-cy/scale),Image.Resampling.BICUBIC,fillcolor=fill)

def artwork(n,t,zoom=1,pan=0):
 focus=FOCUS[n]
 s=1+(zoom-1)*.32 if zoom>=1 else .92+.08*zoom
 # Background remains full bleed even while distant objects approach.
 b=transform(backgrounds[n],max(1,s),focus,pan,fill=(*CREAM,255))
 art=static[n].copy()
 if n==4:
  formulation(art,t)
 elif n==2:
  # Kernels move as individual cutouts; liquid remains a still photograph.
  for k in range(5):
   phase=(t*.46+k*.23)%1
   sticker(art,'semillas2.png',220+k*66,435+phase*220,width=26,angle=k*32+phase*55,alpha=.9)
  sticker(art,'inkSteam',375,485-(t*.24%1)*55,height=145,alpha=.85)
 elif n==3:
  for k in range(4):sticker(art,'semillas2.png',195+k*110,430+math.sin(t*.9+k)*9,width=26,angle=k*47)
 elif n==6:
  q=ramp(t,.5,3.0)
  # The husk slides over the soap, then the wrapped product rests in the hands.
  sticker(art,'hands',360,lerp(1150,815,q),width=530,shadow=True)
  if q<.8:sticker(art,'soap',360,640,width=390,angle=58,alpha=1-ramp(q,.4,.8),shadow=True)
  if q<.9:sticker(art,'hojasdemaiz2.m.png',lerp(-220,380,q),660,width=480,angle=lerp(-25,60,q),alpha=1-ramp(q,.7,1),shadow=True)
  sticker(art,'jabon1.png',360,lerp(600,650,q),height=565,angle=-8,alpha=ramp(q,.35,.75),shadow=True)
 # A second foreground plane adds depth instead of moving the entire page equally.
 b.alpha_composite(transform(art,zoom**.95,focus,pan))
 return b

def left_text(draw,x,y,text,font,fill):
 box=draw.textbbox((0,0),text,font=font)
 draw.text((x-box[0],y-box[1]),text,font=font,fill=fill)

def left_block(draw,x,y,lines,font,fill,gap=11):
 heights=[draw.textbbox((0,0),s,font=font)[3]-draw.textbbox((0,0),s,font=font)[1] for s in lines]
 for s,h in zip(lines,heights):
  left_text(draw,x,y,s,font,fill);y+=h+gap
 return sum(heights)+gap*max(0,len(lines)-1)

def founder_note(c,t):
 alpha=ramp(t,.5,1.2)
 if alpha<=0:return
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
 # Three little hand-cut emphasis rays sit beside Elizabeth's hat.
 grow=ramp(t,.5,1.05)
 rays=[((342,377),(359,351),5),((354,395),(385,386),6),((358,414),(386,424),5)]
 for i,(start,end,width) in enumerate(rays):
  show=ramp(t,.5+i*.12,.85+i*.12)
  if show<=0:continue
  x,y=start;ex=x+(end[0]-x)*show;ey=y+(end[1]-y)*show
  dx=ex-x;dy=ey-y;ln=max(.1,math.hypot(dx,dy));nx=-dy/ln;ny=dx/ln
  pts=[(x,y),(x+dx*.35+nx*width*.7,y+dy*.35+ny*width*.7),(ex+nx*width*.45,ey+ny*width*.45),(ex+dx/ln*2,ey+dy/ln*2),(ex-nx*width*.5,ey-ny*width*.5),(x+dx*.35-nx*width*.55,y+dy*.35-ny*width*.55)]
  d.polygon(pts,fill=(13,65,37,255))
  d.line((x+dx*.2,y+dy*.2,ex,ey),fill=(224,216,164,210),width=1)
 name=ImageFont.truetype(SANS,27,index=1);role=ImageFont.truetype(SANS,20)
 for y,s,font in [(300,'Elizabeth Rueda',name),(324,'Fundadora de Izamaíz',role)]:
  d.text((330,y),s,font=font,fill=WHITE,anchor='ls',stroke_width=1,stroke_fill=(39,48,39,130))
 layer.putalpha(layer.getchannel('A').point(lambda a:int(a*alpha)));c.alpha_composite(layer)

def harvest_overlay(t,alpha=1):
 c=Image.new('RGBA',(W,H));d=ImageDraw.Draw(c)
 small=ImageFont.truetype(FONT,45);large=ImageFont.truetype(BOLD,78)
 def title_line(parts,y):
  x=44
  for text,font in parts:
   d.text((x,y),text,font=font,fill=WHITE,anchor='ls');x+=d.textlength(text,font=font)
 title_line([('El ',small),('Origen',large)],157)
 title_line([('tiene ',small),('Rostro',large)],232)
 p=solid_paper((W+30,385));p.putalpha(paper_mask(p.size,17));p=p.rotate(-1,Image.Resampling.BICUBIC,expand=True)
 c.alpha_composite(p,(-15,929))
 regular=ImageFont.truetype(SANS,31);bold=ImageFont.truetype(SANS,35,index=1)
 lines=[[('Todo comienza en ',False),('Tlaxcala',True),(',',False)],
 [('donde ',False),('artesanas',True),(' expertas se',False)],
 [('encargan de la siembra, el cuidado',False)],
 [('y la cosecha de un maíz',False)]]
 for i,line in enumerate(lines):
  x=44;baseline=990+i*39
  for text,strong in line:
   font=bold if strong else regular
   d.text((x,baseline),text,font=font,fill=INK,anchor='ls');x+=d.textlength(text,font=font)
 emphasis=ImageFont.truetype(SANS,46,index=1)
 d.text((676,1174),'100% orgánico',font=emphasis,fill=INK,anchor='rs')
 d.text((676,1221),'que será la base para tu jabón.',font=regular,fill=INK,anchor='rs')
 founder_note(c,t)
 if alpha<.999:c.putalpha(c.getchannel('A').point(lambda a:int(a*max(0,alpha))))
 return c

# Descriptive typography belongs to the resting scene and clears before the dive.
def text_overlay(n,t,alpha=1):
 if n==1:return harvest_overlay(t,alpha)
 c=Image.new('RGBA',(W,H));d=ImageDraw.Draw(c)
 dark=n in [2,3,4,5];ink=INK if dark else WHITE
 if n==4:
  p=solid_paper((W+80,370));mask=Image.new('L',p.size,0);md=ImageDraw.Draw(mask);rng=random.Random(79)
  edge=[(x,337+round(x*.025)+rng.randint(-10,10)) for x in range(0,W+81,12)]
  md.polygon([(0,0),(W+80,0)]+edge[::-1],fill=255);p.putalpha(mask);c.alpha_composite(p,(-40,-14))
 elif dark and n not in [2,3]:
  p=solid_paper((W,375));c.alpha_composite(p,(0,0))
 left_text(d,44,95,KICK[n],fonts['label'],ink)
 left_block(d,44,150,TITLES[n].split('\n'),fonts['title'],ink,gap=8)
 if n!=5:
  # A paper caption, not a button or a navigation panel.
  p=solid_paper((W+30,225));p.putalpha(paper_mask(p.size,17));p=p.rotate(-1,Image.Resampling.BICUBIC,expand=True)
  c.alpha_composite(p,(-15,1010))
  lines=BODY[n]
  heights=[d.textbbox((0,0),s,font=fonts['body'])[3]-d.textbbox((0,0),s,font=fonts['body'])[1] for s in lines]
  total=sum(heights)+12*(len(lines)-1)+(42 if n==6 else 0)
  y=1125-total/2
  left_block(d,44,y,lines,fonts['body'],INK,gap=12)
  if n==6:left_text(d,44,y+total-18,'Materiales · envío · conservación · disposición',fonts['small'],INK)
 else:
  left_block(d,44,298,['Conoce qué contiene y qué función','cumple cada ingrediente.'],fonts['body'],INK,gap=11)
  cards=[('Ingredientes','Listado completo de la fórmula por validar.'),('Función del ingrediente de maíz','Su papel dentro de la fórmula final.'),('Beneficios comprobados','Se mostrarán según la evidencia del jabón.')]
  for k,(title,detail) in enumerate(cards):
   p=ramp(t,.25+k*.45,1.1+k*.45)
   if p==0:continue
   card=solid_paper((635,88));card.putalpha(paper_mask(card.size,30+k))
   cd=ImageDraw.Draw(card);left_text(cd,23,16,title,fonts['card'],INK);left_text(cd,23,51,detail,fonts['detail'],INK)
   card=card.resize((635,max(1,round(88*p))),Image.Resampling.LANCZOS)
   c.alpha_composite(card,(44,round(805+k*104+16*(1-p))))
  left_text(d,44,1144,'Modo de uso y cuidados: espacio desplegable.',fonts['small'],INK)
 if alpha<.999:c.putalpha(c.getchannel('A').point(lambda a:int(a*max(0,alpha))))
 return c

# One continuous original-photograph cutout with overscan; no split crop edges.
plants=Image.open(R/'work/revision-05/original-maize-cutout.png').convert('RGBA')
plants=ImageOps.fit(plants,(W,H),Image.Resampling.LANCZOS)

def field_exit(p,t=0):
 q=ease(p)
 c=backgrounds[1].copy()
 distant=transform(static[1],lerp(.60,1,q),C,0)
 visible=ramp(p,.30,.66)
 distant.putalpha(distant.getchannel('A').point(lambda a:int(a*visible)))
 c.alpha_composite(distant)
 # This zoom never goes below 1.22: every rectangular source boundary stays outside the viewport.
 z=1.22*(6.0**q)
 foreground=transform(plants,z,(360,970),ramp(p,.12,1))
 if p>.7:foreground=foreground.filter(ImageFilter.GaussianBlur(3*ramp(p,.7,1)))
 opacity=1-ramp(p,.82,1)
 if opacity<.999:foreground.putalpha(foreground.getchannel('A').point(lambda a:int(a*opacity)))
 c.alpha_composite(foreground)
 return c

def transitional(n,p,t):
 q=ease(p);nn=n+1
 if n==0:return field_exit(p,t)
 c=Image.blend(backgrounds[n],backgrounds[nn],q)
 if n==1:
  # Follow the harvested maize into the preparation area. The basket remains full.
  sticker(c,'clothStripe',370-450*q,1100,width=1040,angle=-9,alpha=1-q)
  sticker(c,'clothRed',400,lerp(1370,1040,q),width=1010,angle=-10,alpha=q)
  sticker(c,'farmerL',210-850*q,594+60*q,height=540*(1-.15*q),angle=4-8*q)
  sticker(c,'farmerR',520-850*q,610+60*q,height=540*(1-.15*q),angle=-3)
  sticker(c,'basketFilled',lerp(360,-340,q),lerp(851,1020,q),width=lerp(520,430,q),angle=lerp(3,-15,q))
  sticker(c,'inkCorn',100,655,height=420,angle=16,alpha=ramp(p,.25,.8))
  vessel_leaf(c,'pot',lerp(1100,415,q),lerp(850,756,q),545)
  sticker(c,'pot',lerp(1100,415,q),lerp(850,756,q),width=545,angle=-4,shadow=True)
  for k in range(4):
   g=(p-.14-k*.07)/.52
   if 0<g<1:sticker(c,'inkGrains',lerp(345,415,g),lerp(720,650,g)-math.sin(math.pi*g)*185,width=65,angle=lerp(-25,45,g))
 elif n==2:
  # Prepared maize leads to the ingredient: the vessels keep their real silhouettes.
  sticker(c,'clothRed',400-400*q,1040,width=1010,angle=-10,alpha=1-q)
  sticker(c,'clothPink',390+450*(1-q),1030,width=1020,angle=-12,alpha=q)
  sticker(c,'inkCorn',100-330*q,655,height=420,angle=16,alpha=1-q)
  vessel_leaf(c,'pot',lerp(415,-440,q),lerp(756,1250,q),545)
  sticker(c,'pot',lerp(415,-440,q),lerp(756,1250,q),width=545,angle=lerp(-4,12,q))
  vessel_leaf(c,'bowl',lerp(1100,360,q),752,545)
  sticker(c,'bowl',lerp(1100,360,q),752,width=545,angle=-5,shadow=True)
  sticker(c,'inkGrains',lerp(415,360,q),lerp(600,458,q),width=lerp(90,190,q),angle=-9)
  sticker(c,'inkSteam',375,lerp(480,170,q),height=145,alpha=1-ramp(p,.15,.65))
 elif n==3:
  # The very same bowl moves beside the mixer and the mold.
  sticker(c,'clothPink',390-500*q,1030,width=1020,angle=-12,alpha=1-q)
  sticker(c,'clothRed',440,lerp(1360,1035,q),width=1020,angle=10,alpha=q)
  sticker(c,'inkGrains',lerp(360,370,q),lerp(458,400,q),width=lerp(190,135,q),angle=lerp(-9,20,q),alpha=1-q)
  sticker(c,'batidora.png',lerp(-350,192,q),lerp(530,650,q),height=425,angle=lerp(-15,5,q),shadow=True)
  sticker(c,'molde.png',lerp(1100,500,q),760,height=440,angle=lerp(15,0,q),shadow=True)
  vessel_leaf(c,'bowl',lerp(360,195,q),lerp(752,973,q),lerp(545,320,q))
  sticker(c,'bowl',lerp(360,195,q),lerp(752,973,q),width=lerp(545,320,q),angle=lerp(-5,9,q),shadow=True)
 elif n==4:
  sticker(c,'clothRed',440+500*q,1035,width=1020,angle=10,alpha=1-q)
  sticker(c,'clothPink',-185,630,width=860,angle=70,alpha=q)
  sticker(c,'clothPink',910,670,width=860,angle=70,alpha=q)
  sticker(c,'clothGold',350,650,width=560,angle=-12,alpha=q)

  place_mold(c,[1]*5,lerp(380,1200,q),lerp(710,1390,q),lerp(550,780,q),lerp(9,-25,q),1-ramp(p,.85,1))
  sticker(c,'soap',lerp(380,370,q),lerp(710,565,q),width=lerp(190,470,q),angle=lerp(0,-16,q),alpha=ramp(p,.06,.35),shadow=True)
 elif n==5:
  # Follow the same bar to the hands; the husk wrap happens in the following hold.
  sticker(c,'clothGold',350,650+650*q,width=560,angle=-12,alpha=1-q)
  sticker(c,'clothPink',-185-450*q,630,width=860,angle=70,alpha=1-q)
  sticker(c,'clothPink',910+450*q,670,width=860,angle=70,alpha=1-q)
  sticker(c,'clothStripe',340,lerp(1430,1040,q),width=1020,angle=10,alpha=q)
  sticker(c,'inkCorn',668,698,height=380,angle=-18,alpha=q)
  sticker(c,'hands',360,lerp(1480,1150,q),width=530,shadow=True)
  sticker(c,'soap',lerp(370,360,q),lerp(565,640,q),width=lerp(470,390,q),angle=lerp(-16,58,q),shadow=True)
 # Only a brief settling of the moving layers, never a hole or page-sized wipe.
 if p>.92:c=Image.blend(c,artwork(nn,0,1,0),ramp(p,.92,1))
 return c

HOLDS=[3.5,9.2,5.5,5.0,7.0,8.0,7.0]
TRANSITIONS=[2.8,2.6,2.6,2.6,2.6,2.6,0]
STARTS=[];clock=0
for hold,tr in zip(HOLDS,TRANSITIONS):STARTS.append(clock);clock+=hold+tr
DURATION=clock

logo_center=logo_white.resize((320,round(320*logo_white.height/logo_white.width)),Image.Resampling.LANCZOS)

def translated_overlay(layer,dy,alpha=1):
 if alpha<.999:
  layer=layer.copy();layer.putalpha(layer.getchannel('A').point(lambda a:int(a*max(0,alpha))))
 shifted=Image.new('RGBA',(W,H));shifted.alpha_composite(layer,(0,round(dy)));return shifted

def frame(t):
 n=next((i for i in range(6,-1,-1) if t>=STARTS[i]),0);local=t-STARTS[n];hold=HOLDS[n]
 if n==0:
  p=0 if local<=hold else min(1,(local-hold)/TRANSITIONS[0])
  c=field_exit(p,local)
  # First only the maize field; the original centered brand appears and then fully clears.
  brand_alpha=ramp(t,.16,.50)*(1-ramp(t,3.08,3.48))
  effect=1-ramp(t,3.48,4.05)
  if effect>0:
   c=Image.blend(c,c.filter(ImageFilter.GaussianBlur(3)),effect*.9)
   c.alpha_composite(Image.new('RGBA',(W,H),(0,0,0,round(108*effect))))
  if brand_alpha>0:
   mark=logo_center.copy();mark.putalpha(mark.getchannel('A').point(lambda a:int(a*brand_alpha)))
   c.alpha_composite(mark,((W-mark.width)//2,round(620-mark.height/2)))
  if local>hold:
   enter=ramp(p,.69,1)
   c.alpha_composite(translated_overlay(text_overlay(1,0,1),-46*(1-enter),enter))
  return c.convert('RGB')
 if local<=hold or n==6:
  c=artwork(n,local,1,0);c.alpha_composite(text_overlay(n,local,1))
 else:
  p=min(1,(local-hold)/TRANSITIONS[n]);c=transitional(n,p,local)
  c.alpha_composite(text_overlay(n,local,1-ramp(p,0,.26)))
  c.alpha_composite(text_overlay(n+1,0,ramp(p,.64,.98)))
 if n==4:
  if local<=hold and local>=4.6:cold_label(c,ramp(local,4.6,5.3))
  elif local>hold:cold_label(c,1-ramp((local-hold)/TRANSITIONS[n],0,.25))
 dark=n in [0,1,6]
 if local>hold and n<6:
  nn=n+1;next_dark=nn in [0,1,6];mix=ramp((local-hold)/TRANSITIONS[n],.35,.65)
 else:next_dark=dark;mix=0
 asset=logo_white if (next_dark if next_dark!=dark and mix>=.5 else dark) else logo
 mark=asset.copy()
 if n==1 and local<.35:mark.putalpha(mark.getchannel('A').point(lambda a:int(a*ramp(local,0,.35))))
 c.alpha_composite(mark,(LOGO_X,LOGO_Y))
 return c.convert('RGB')



if '--check' in sys.argv:
 for i,t in enumerate([2.5,5.5,9.5,13.5,19.5,27.5,33.9,34.8,35.8,36.3,37.0,37.8,38.4,39.5,45.5,56]):frame(t).save(D/f'check-{i}.jpg',quality=95)
 sys.exit()
out=D/'video-sin-audio.mp4'
cmd=[FF,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
with open(D/'encode.log','w') as log:
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
 for i in range(round(DURATION*FPS)):
  proc.stdin.write(frame(i/FPS).tobytes())
  if i%300==0:print(f'Rendered {i}/{round(DURATION*FPS)}',flush=True)
 proc.stdin.close();assert proc.wait()==0
print(json.dumps({'video':str(out),'duration':DURATION,'bytes':out.stat().st_size}),flush=True)
