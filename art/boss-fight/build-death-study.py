#!/usr/bin/env python3
"""Isolated boss death staging study, 20 fps, using generated art assets.
Not runtime, collision, projectile clearing or final art certification.
Run from repo root: python art/boss-fight/build-death-study.py
"""
from PIL import Image, ImageDraw
from pathlib import Path
import math, json
P=Path('art/boss-fight'); E=P/'exports'; D=E/'death-study'; D.mkdir(parents=True,exist_ok=True)
L={n:Image.open(E/'boss-layers'/f'{n}.png').convert('RGBA') for n in ('hull','pod_left','pod_right','core','cannon')}
T={f'{s}_{p}':Image.open(E/'turret-pivot-tests'/f'{s}-{p}.png').convert('RGBA') for s in ('left','right') for p in ('base','head')}
F={n:Image.open(E/'cinematic'/f'{n}.png').convert('RGBA') for n in ('turret_blast','pod_fire','arc','main_blast','debris','smoke')}
F['shockwave']=Image.open(E/'effects/shockwave.png').convert('RGBA')
bg=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGB').resize((480,700),Image.Resampling.LANCZOS).convert('RGBA')
player=Image.open('art/launch-real-size/exports/ships/PLAYER-10001.png').convert('RGBA')
def put(dst,img,x,y,scale=1,angle=0,opacity=1):
 if opacity<=0:return
 if scale!=1:img=img.resize((max(1,round(img.width*scale)),max(1,round(img.height*scale))),Image.Resampling.LANCZOS)
 if angle:img=img.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if opacity<1:
  img=img.copy();img.putalpha(img.getchannel('A').point(lambda a:round(a*opacity)))
 dst.alpha_composite(img,(round(x-img.width/2),round(y-img.height/2)))
def local(dst,img,cx,cy):
 # layer center is (256,256), translated to intended hull location
 dst.alpha_composite(img,(cx-256,cy-256))
# 0.00–0.65 left turret blast; 0.65–1.30 right pod burn;
# 1.30–1.90 body arc; 1.90–2.20 white flash (0.30 s);
# 2.20–3.30 detonation, shock wave and four fragments; 3.30–4.30 smoke.
fps=20;duration=4.3; frames=[]
for i in range(round(fps*duration)):
 t=i/fps; im=bg.copy(); boss=Image.new('RGBA',(512,512))
 if t<2.75:
  for name in ('hull','pod_left','pod_right','core','cannon'):
   if name=='pod_right' and t>=1.30:continue
   boss.alpha_composite(L[name])
  for side,cx in [('left',144),('right',368)]:
   if side=='left' and t>=.65:continue
   local(boss,T[side+'_base'],cx,210);local(boss,T[side+'_head'],cx,210)
  put(im,boss,240,190,.62,opacity=1 if t<2.2 else max(0,1-(t-2.2)/.55))
 if t<.95:put(im,F['turret_blast'],171,160,.40+t*.16,opacity=min(1,(.95-t)*2))
 if .65<=t<1.9:put(im,F['pod_fire'],356,179,.42,opacity=.7+.2*math.sin(t*18))
 if 1.30<=t<2.2:put(im,F['arc'],240,185,.76,opacity=.65+.25*math.sin(t*23))
 if 1.9<=t<2.2:
  # Six exact 50ms frames, no accessibility claim.
  im=Image.alpha_composite(im,Image.new('RGBA',im.size,(255,255,255,255)))
 if 2.2<=t<3.3:
  a=t-2.2;put(im,F['main_blast'],240,190,.7+a*.7,opacity=max(0,1-a*.75));put(im,F['shockwave'],240,190,.45+a*1.9,opacity=max(0,1-a*.8))
  for j in range(4):
   theta=math.tau*j/4+.4;dist=a*(110+(j%2)*45)
   put(im,F['debris'],240+dist*math.cos(theta),190+dist*math.sin(theta),.16,angle=a*(70+j*15),opacity=max(0,1-a*.7))
 if 2.9<=t<4.3:
  a=max(0,t-3.3)
  fade=min(1,(t-2.9)/.4)*max(0,1-a)
  for j in range(3):put(im,F['smoke'],205+j*35+15*a,175-30*a,.4+.1*a,opacity=fade*.7)
 if not 1.9<=t<2.2:put(im,player,240,565,.14)
 frames.append(im.convert('RGB'))
small=[f.resize((240,350),Image.Resampling.LANCZOS).quantize(colors=64,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for f in frames]
small[0].save(D/'death-study.gif',save_all=True,append_images=small[1:],duration=50,loop=0,disposal=2,optimize=True)
board=Image.new('RGB',(480*4,700*2))
for j,idx in enumerate([0,13,28,38,44,48,54,72]):board.paste(frames[idx],((j%4)*480,(j//4)*700))
board.resize((1200,875),Image.Resampling.LANCZOS).save(D/'death-study-sheet.jpg',quality=90)
meta={'status':'STUDY_NOT_RUNTIME_OR_FINAL_QA','fps':fps,'frames':len(frames),'duration_s':duration,'flash_frames':[38,39,40,41,42,43],'flash_duration_s':.3,'fragments':4,'smoke_only_s':1.0,'segments_s':{'turret':[0,.65],'pod':[.65,1.3],'arc':[1.3,1.9],'flash':[1.9,2.2],'explosion':[2.2,3.3],'smoke':[3.3,4.3]},'limitations':['Projectile clearing is not simulated.','Full-frame white flash needs accessibility review.','Sequence staging and layer alignment require visual review; not gameplay QA.']}
(D/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
print(meta)
